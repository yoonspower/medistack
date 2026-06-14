#!/usr/bin/env python3
"""
verify_factory_sources_v1_2.py
MediStack relation factory — 후보 75건(data/relation_factory_candidates_v1_2.csv) 중
**source-checkable** 후보의 제안 nutrient 테마가 MFDS nedrug 허가사항(getItemDetail) 원문
상호작용/주의/이상반응 문맥에 실재하는지 **출처 존재 여부만** 확인한다.

설계: verify_source_queue_top10_v1_2.py 의 검증된 패턴(detector + 첨가제 배제 + 방향성)을 승계하되,
factory 후보 전체로 일반화한다. 성분→대표 itemSeq 해결은 collect_nedrug_alias_candidates.py 의
searchDrug 파서를 승계한다.

⚠️ 절대 규칙 (위반 금지):
  - relation / full index / alias / export / src / .github / validator 를 한 줄도 수정하지 않는다(읽기전용 + 네트워크 fetch).
  - relation 을 추가/승격/flip 하지 않는다. relations 는 55 그대로다.
  - 어떤 후보도 source_confirmed 라도 "다음 단계 검토 대상"일 뿐 구현 지시가 아니다(do_not_implement_yet).
  - 제품추천/복용지시/영양제 추천 문구를 생성하지 않는다(허가사항 원문 인용 + 참고정보 톤 safe_user_copy 만).
  - high_risk / hold(항응고·항혈소판·항암·정신건강·허브·CoQ10·칼륨보존이뇨제 상승방향·방향반대·약-약·index트랙)
    후보는 **fetch 하지 않고 분류만** 한다(검토만, 승격 금지).
  - source_confirmed 는 **방향성까지 일치**할 때만(depletion 후보는 저칼륨/저마그네슘 등 고갈 방향 신호 필수).

출력(분석 산출물만): data/relation_factory_source_check_v1_2.csv

사용: python3 scripts/verify_factory_sources_v1_2.py [--no-write] [--limit N]
종료 코드: 0 정상.
"""
import argparse
import csv
import html as htmllib
import http.cookiejar
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
OUT_CSV = os.path.join(DATA, "relation_factory_source_check_v1_2.csv")
CHECKED_AT = "2026-06-14"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"
SEARCH_URL = "https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1={}&page={}"

# 첨가제/조성표(false positive) 배제용 문맥.
EXCIPIENT_CTX = re.compile(r"첨가제|착색|코팅|활택|부형|결합제|붕해|산화마그네슘|스테아르산마그네슘|"
                           r"규산마그네슘|탄산마그네슘|분량|규격|용량단위|밀리그램\)")
ORAL_RE = re.compile(r"(정|캡슐)")
NONORAL_RE = re.compile(r"(점안|점이|점비|주사|연고|크림|로션|겔|외용|흡입|패치|좌제|관장|시럽|현탁|가글|"
                        r"스프레이|에어로졸|틴크|패취|건조시럽|산제|좌약)")
EXPORT_RE = re.compile(r"수출")
ANCHOR_RE = re.compile(r'getItemDetail\?itemSeq=(\d+)"[^>]*>\s*([^<]+?)\s*</a>')


# ----------------- 네트워크 -----------------
def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch_detail(opener, seq):
    url = DETAIL_URL.format(seq)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    last = None
    for _ in range(3):
        try:
            with opener.open(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
            t = re.sub(r"<[^>]+>", " ", raw)
            t = htmllib.unescape(t)
            t = re.sub(r"\s+", " ", t)
            return t, url
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5)
    raise last


def _field(row, label):
    m = re.search(re.escape(f'<span class="s-th">{label}</span>') + r'(.*?)(?=<span class="s-th">|</td>|</tr>)',
                  row, re.S)
    if not m:
        return ""
    txt = re.sub(r"<[^>]+>", " ", m.group(1))
    return " ".join(htmllib.unescape(txt).split()).strip()


def search_itemseqs(opener, ingredient, exclude_ingr=None, max_n=3, max_pages=2):
    """성분명 → 국내 완제·경구·정상·단일성분 대표 itemSeq 목록(오름차순). 실패 시 ([], reason)."""
    picked = []
    seen = set()
    for page in range(1, max_pages + 1):
        url = SEARCH_URL.format(urllib.parse.quote(ingredient), page)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
        try:
            with opener.open(req, timeout=25) as r:
                html_text = r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            if page == 1:
                return [], f"network:{type(e).__name__}"
            break
        rows = []
        for chunk in re.split(r"<tr[ >]", html_text):
            if "getItemDetail?itemSeq=" not in chunk:
                continue
            m = ANCHOR_RE.search(chunk)
            if not m:
                continue
            rows.append({
                "item_seq": m.group(1),
                "item_name": htmllib.unescape(m.group(2)).strip(),
                "ingr_name": _field(chunk, "주성분"),
                "finished": _field(chunk, "완제/원료구분"),
                "status_cancel": _field(chunk, "취소/취하구분"),
            })
        if not rows:
            break
        for p in sorted(rows, key=lambda x: int(x["item_seq"])):
            if len(picked) >= max_n:
                break
            name, seq, ingr = p["item_name"], p["item_seq"], p["ingr_name"]
            if seq in seen:
                continue
            # 완제·정상·경구고형·비수출
            if "원료" in p["finished"] or (p["finished"] and "완제" not in p["finished"]):
                continue
            if p["status_cancel"] and p["status_cancel"] != "정상":
                continue
            if EXPORT_RE.search(name) or NONORAL_RE.search(name) or not ORAL_RE.search(name):
                continue
            # 주성분에 성분 포함(보수적). 단일성분(복합제 '/' 제외).
            if not ingr or ingredient not in ingr:
                continue
            if "/" in ingr or "," in ingr:
                continue
            if exclude_ingr and exclude_ingr in ingr:
                continue
            seen.add(seq)
            picked.append((seq, name, ingr))
        if len(picked) >= max_n:
            break
    if not picked:
        return [], "no_domestic_single_oral_product"
    return picked, "ok"


# ----------------- detectors (검증된 패턴 승계) -----------------
def snip(text, i, pad=95):
    return text[max(0, i - pad):i + pad].strip()


def d_potassium(text):
    """저칼륨혈증(전해질 고갈) 방향 신호."""
    for m in re.finditer(r"저칼륨", text):
        return True, snip(text, m.start())
    for m in re.finditer("칼륨", text):
        i = m.start()
        w = text[max(0, i - 50):i + 50]
        if re.search(r"저하|감소|상실|배설|소실|보충|혈증", w):
            return True, snip(text, i)
    return False, ""


def d_mg_depletion(text):
    """저마그네슘혈증(전해질 소실) 방향 신호."""
    for m in re.finditer("저마그네슘", text):
        return True, snip(text, m.start())
    for m in re.finditer("마그네슘", text):
        i = m.start()
        w = text[max(0, i - 50):i + 50]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"저하|감소|상실|배설|소실|혈증|전해질", w):
            return True, snip(text, i)
    return False, ""


def d_iron_absorption(text):
    """철(분) 흡수저해/병용/복합체/간격/다가양이온 문맥(착색용 산화철 등 배제)."""
    for m in re.finditer(r"철분|철염|철\s*함유|철\s*제제|철제|철\s*및|철ㆍ|철·", text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"흡수|병용|복합체|간격|동시|다가\s*양이온|킬레이트", w):
            return True, snip(text, i)
    return False, ""


def d_calcium_absorption(text):
    """칼슘 흡수저해/병용/다가양이온 문맥(B12·조성 배제)."""
    for m in re.finditer("칼슘", text):
        i = m.start()
        w = text[max(0, i - 60):i + 60]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"B\s*12|시아노코발라민", w):
            continue
        if re.search(r"다가\s*양이온|흡수.{0,12}(저해|저하|감소|방해)|"
                     r"(저해|저하|감소|방해).{0,12}흡수|제산제|간격|킬레이트", w):
            return True, snip(text, i)
    return False, ""


def d_zinc_interaction(text):
    """아연 흡수저해/병용/다가양이온 상호작용 문맥(첨가제 아님)."""
    for m in re.finditer("아연", text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"흡수|병용|다가\s*양이온|킬레이트|복합체|간격|동시|제산제|함유.{0,8}제제", w):
            return True, snip(text, i)
    return False, ""


def d_mg_absorption(text):
    """마그네슘 흡수상호작용(다가양이온/제산제/흡수저해) — 고갈 아님."""
    for m in re.finditer("마그네슘", text):
        i = m.start()
        w = text[max(0, i - 70):i + 70]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"다가\s*양이온|제산제|흡수.{0,12}(저해|저하|감소|방해)|"
                     r"(저해|저하|감소|방해).{0,12}흡수|병용.{0,12}흡수|킬레이트", w):
            return True, snip(text, i)
    return False, ""


DETECTORS = {
    "potassium": d_potassium, "mg_depletion": d_mg_depletion,
    "iron_absorption": d_iron_absorption, "calcium_absorption": d_calcium_absorption,
    "zinc": d_zinc_interaction, "mg_absorption": d_mg_absorption,
}


# ----------------- 후보 정의 -----------------
# 성분 단위로 묶어 fetch 1회 후 다중 nutrient detector 적용.
# 각 nutrient 항목: (candidate_id, nutrient, mechanism, action, detector_key, potassium_safety, risk, internal_note)
# class_generalization: 세팔로스포린 철은 성분특이(세프디니르 적색복합) — 계열 일반화 금지, 해당 성분 라벨 직접 hit 만 confirmed.
SEARCH_INGREDIENTS = {
    # ---- 세팔로스포린 × 철분 (per-ingredient, class_generalization_forbidden) ----
    "세파클러": [("F-CEPH-01", "철분", "absorption", "separation", "iron_absorption", False, "low",
                "세팔로스포린 철 킬레이션은 성분특이(세프디니르). 계열 일반화 금지 — 세파클러 라벨 직접 동거어만 채택.")],
    "세푸록심": [("F-CEPH-02", "철분", "absorption", "separation", "iron_absorption", False, "low",
                "세푸록심악세틸. 위산의존 흡수라 제산제 언급 가능성 있으나 철분 직접 동거어만 채택.")],
    "세프포독심": [("F-CEPH-03", "철분", "absorption", "separation", "iron_absorption", False, "low",
                 "세프포독심프록세틸. 철분 직접 동거어만 채택.")],
    "세프프로질": [("F-CEPH-04", "철분", "absorption", "separation", "iron_absorption", False, "low",
                 "철 킬레이션 근거 약함 — 직접 동거어 없으면 reject.")],
    "세픽심": [("F-CEPH-05", "철분", "absorption", "separation", "iron_absorption", False, "low",
              "철분 직접 동거어만 채택.")],
    "세프라딘": [("F-CEPH-06", "철분", "absorption", "separation", "iron_absorption", False, "low",
                "철 킬레이션 근거 약함.")],
    "세프카펜": [("F-CEPH-07", "철분", "absorption", "separation", "iron_absorption", False, "low",
                "세프카펜피복실.")],
    "세프디토렌": [("F-CEPH-08", "철분", "absorption", "separation", "iron_absorption", False, "low",
                 "세프디토렌피복실. 위산의존 흡수.")],
    "세팔렉신": [("F-CEPH-09", "철분", "absorption", "separation", "iron_absorption", False, "low",
                "index 소수(5)·철 킬레이션 약함 — 동거어 없으면 reject.")],
    "세프록사딘": [("F-CEPH-10", "철분", "absorption", "separation", "iron_absorption", False, "low",
                 "index 1품목. 동거어 없으면 reject.")],
    # ---- 코르티코스테로이드 × 칼륨(depletion) / 칼슘(absorption, 약함) ----
    "프레드니솔론": [
        ("D-CORT-01", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
         "스테로이드 미네랄코르티코이드 작용 저칼륨혈증. 장기/고용량 맥락 — 참고정보 톤·monitoring."),
        ("D-CORT-02", "칼슘", "absorption", "monitoring", "calcium_absorption", False, "moderate",
         "장기 골소실은 골다공증 문맥(흡수 직접 문구 약함). 흡수 동거어 없으면 reject(과다해석 금지)."),
    ],
    "메틸프레드니솔론": [
        ("D-CORT-03", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
         "스테로이드 class 저칼륨혈증. D-CORT-01과 동일 톤."),
        ("D-CORT-07", "칼슘", "absorption", "monitoring", "calcium_absorption", False, "moderate",
         "골대사 문맥. 흡수 직접 문구 없으면 reject."),
    ],
    "덱사메타손": [("D-CORT-04", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                 "덱사메타손은 미네랄코르티코이드 작용 약함 — 저칼륨 문구 누락 시 reject/needs_review.")],
    "하이드로코르티손": [("D-CORT-05", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                   "전신(경구) 제형 한정. 국소/외용은 필터 제외. 전신 품목 없으면 needs_review.")],
    "플루드로코르티손": [("D-CORT-06", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                   "강한 미네랄코르티코이드. 국내 유통 적음 — 품목 없으면 needs_review/hold.")],
    # ---- 탄산탈수효소억제제 × 칼륨 ----
    "아세타졸아미드": [("D-CA-01", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                   "탄산탈수효소억제 이뇨작용 저칼륨혈증·대사성산증. 녹내장/고산병 적응증.")],
    # ---- 루프이뇨제 × 칼륨 / 마그네슘 ----
    "부메타니드": [
        ("D-LOOP-01", "칼륨", "depletion", "monitoring", "potassium", True, "moderate", "루프 class 저칼륨(푸로세미드 id17 패턴)."),
        ("D-LOOP-02", "마그네슘", "depletion", "monitoring", "mg_depletion", False, "low", "루프 class 저마그네슘(id18 패턴). Mg는 칼륨카드 불필요."),
    ],
    "피레타니드": [("D-LOOP-03", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                 "국내 유통 확인 우선 — 품목 없으면 needs_review/hold.")],
    "아조세미드": [
        ("D-LOOP-04", "칼륨", "depletion", "monitoring", "potassium", True, "moderate", "국내 유통 루프(유리논 계열). 저칼륨."),
        ("D-LOOP-05", "마그네슘", "depletion", "monitoring", "mg_depletion", False, "low", "루프 class 저마그네슘."),
    ],
    # ---- 치아지드(유사) × 칼륨 / 마그네슘 ----
    "메토라존": [
        ("D-THZ-01", "칼륨", "depletion", "monitoring", "potassium", True, "moderate", "치아지드유사 class 저칼륨(인다파미드/클로르탈리돈 선례)."),
        ("D-THZ-02", "마그네슘", "depletion", "monitoring", "mg_depletion", False, "low", "치아지드유사 class 저마그네슘."),
    ],
    "트리클로르메티아지드": [
        ("D-THZ-03", "칼륨", "depletion", "monitoring", "potassium", True, "moderate", "치아지드 class 저칼륨(HCTZ id19 패턴). 국내 다수 유통."),
        ("D-THZ-04", "마그네슘", "depletion", "monitoring", "mg_depletion", False, "low", "치아지드 class 저마그네슘."),
    ],
    "벤드로플루메티아지드": [("D-THZ-05", "칼륨", "depletion", "monitoring", "potassium", True, "moderate",
                      "국내 단일제 유통 불확실(복합 가능) — 품목 없으면 needs_review/hold.")],
    # ---- 갑상선호르몬 enrichment / T3 ----
    "레보티록신": [
        ("D-THY-01", "아연", "absorption", "separation", "zinc", False, "low",
         "레보티록신×Mg는 Q08 reject 전례(라벨 미기재). 아연도 직접 동거어 없으면 reject."),
        ("F-FQ-02", "마그네슘", "absorption", "separation", "mg_absorption", False, "low",
         "Q08 레보티록신×Mg 미기재 확정 — carry-forward reject 예상. 재확인용."),
    ],
    "리오티로닌": [
        ("D-THY-02", "칼슘", "absorption", "separation", "calcium_absorption", False, "low",
         "T3. 국내 단일제 유통 제한적 — 품목 없으면 hold. class 유추는 source 아님(직접 문구 필수)."),
        ("D-THY-03", "철분", "absorption", "separation", "iron_absorption", False, "low",
         "T3 × 철. 품목 없으면 hold."),
    ],
    # ---- FQ enrichment ----
    "목시플록사신": [("F-FQ-01", "칼슘", "absorption", "separation", "calcium_absorption", False, "low",
                  "목시는 Fe/Mg/Zn 킬레이션 위주 — 칼슘 직접 동거어 불확실. 없으면 reject(이미 id24/25/46 covered).")],
}

# carry-forward(허가사항 미기재 확정/방향성/범위 — fetch 없이 분류만). source_status='hold' 또는 'reject'.
# (candidate_id, drug_ingredient, nutrient, relation_type, status, evidence_strength, risk, reason, internal_note)
CARRIED = [
    # CoQ10 스타틴 — 허가사항 미기재 관행, literature_only hold
    ("F-STA-01", "로수바스타틴", "코엔자임Q10", "depletion", "hold", "literature_only", "moderate",
     "한국 허가사항 미기재 예상(CoQ10). source-policy(이차문헌 허용) 결정 전 영구 보류.", "최대 커버리지 레버(name_only 472)이나 라벨 근거 없음 — 임의 통합 금지."),
    ("F-STA-02", "아토르바스타틴", "코엔자임Q10", "depletion", "hold", "literature_only", "moderate",
     "허가사항 미기재 예상. source-policy 결정 전 보류.", "name_only 267."),
    ("F-STA-03", "심바스타틴", "코엔자임Q10", "depletion", "hold", "literature_only", "moderate",
     "허가사항 미기재 예상. 보류.", ""),
    ("F-STA-04", "피타바스타틴", "코엔자임Q10", "depletion", "hold", "literature_only", "moderate",
     "허가사항 미기재 예상. 보류.", ""),
    ("F-STA-05", "프라바스타틴", "코엔자임Q10", "depletion", "hold", "literature_only", "moderate",
     "허가사항 미기재 예상. 보류.", "잔여 스타틴 최저우선."),
    # H2 × B12 — A티어 확인서 missing 확정
    ("F-H2-01", "파모티딘", "비타민B12", "depletion", "hold", "label_missing_confirmed", "moderate",
     "A티어 확인서 미기재(missing) 확정(구 Q15/E07). 재fetch 불필요. source-policy 결정 시에만 재검토.", "위산억제 인접 기전이나 라벨 동거 없음."),
    ("F-H2-02", "라푸티딘", "비타민B12", "depletion", "hold", "label_missing_confirmed", "moderate",
     "missing 확정(구 Q15/E09).", ""),
    ("F-H2-03", "니자티딘", "비타민B12", "depletion", "hold", "label_missing_confirmed", "moderate",
     "missing 확정(구 Q15/E10).", ""),
    # PPI 잔여 단일제(일라프라졸) — low index 2, class 신호 있으나 hold
    ("F-PPI-01", "일라프라졸", "마그네슘", "depletion", "hold", "low_index", "low",
     "index 2품목뿐 — 한계효용 낮음. PPI class 저마그네슘 패턴은 존재하나 우선순위 hold.", "확인 시 id14/16 톤 승계 가능."),
    ("F-PPI-02", "일라프라졸", "비타민B12", "depletion", "hold", "low_index", "low",
     "index 2품목뿐. PPI class B12 패턴 존재하나 hold.", "확인 시 id13/32 톤 승계 가능."),
    ("F-TET-01", "테트라사이클린", "칼슘", "absorption", "hold", "low_index", "low",
     "테트라사이클린 원성분 index 1품목 — near-zero coverage. 독시/미노 톤 존재하나 hold.", ""),
    # 비구아나이드 잔여 — 국내 미유통
    ("D-BIG-01", "부포르민", "비타민B12", "depletion", "hold", "not_marketed_kr", "low",
     "부포르민/펜포르민 국내 미유통 가능성 — 시장 의미 0. 현행 비구아나이드는 메트포르민 단일(id12 라이브).", "class 유추는 source 아님."),
    # 방향 반대(칼슘 retention) — depletion factory 범위 밖
    ("D-THZ-06", "히드로클로로티아지드", "칼슘", "retention", "hold", "wrong_direction", "moderate",
     "치아지드는 칼슘 배설을 '감소'(고칼슘혈증 방향) — depletion 후보 아님. 혼동방지 hold. HCTZ는 K/Mg covered.", "잘못된 depletion 후보화 방지 기록용."),
    # SGLT2 × Mg — 방향성 불명확(상승 우세)
    ("D-SGLT2-01", "다파글리플로진", "마그네슘", "depletion", "hold", "direction_uncertain", "low",
     "SGLT2는 혈청 Mg 상승 보고 우세 — depletion 가정 부적합 가능. 근거 확인 전 채택 금지.", ""),
    ("D-SGLT2-02", "엠파글리플로진", "마그네슘", "depletion", "hold", "direction_uncertain", "low",
     "D-SGLT2-01과 동일 — 상승 보고 우세.", ""),
    # index/alias 트랙(relation 아님)
    ("F-CEPH-IDX-01", "세프디니르", "철분", "absorption", "hold", "relation_exists", "low",
     "id42 이미 라이브. relation 신설 불필요 — index/alias 충실도 트랙(데이터 무변경).", "relation 트랙 아님."),
    # ---- high_risk hold (fetch 금지) ----
    ("F-WAR-01", "와파린", "비타민K", "antagonism", "hold", "high_risk", "high",
     "CLAUDE.md 영구 금지(antagonism·임상판단 행). source 확인 금지.", "안전 정책상 영구 비대상."),
    ("F-DOAC-01", "리바록사반", "비타민K", "antagonism", "hold", "high_risk", "high", "항응고·임상판단·출혈위험. source 확인 금지.", ""),
    ("F-DOAC-02", "아픽사반", "비타민K", "antagonism", "hold", "high_risk", "high", "항응고·임상판단 영역. source 확인 금지.", ""),
    ("F-DOAC-03", "다비가트란", "비타민K", "antagonism", "hold", "high_risk", "high", "항응고·임상판단 영역. source 확인 금지.", ""),
    ("F-DOAC-04", "에독사반", "비타민K", "antagonism", "hold", "high_risk", "high", "항응고·임상판단 영역. source 확인 금지.", ""),
    ("F-APL-01", "아스피린(저용량 항혈소판)", "비타민K", "antagonism", "hold", "high_risk", "high", "항혈소판·출혈·임상판단. source 확인 금지.", ""),
    ("F-APL-02", "클로피도그렐", "비타민K", "antagonism", "hold", "high_risk", "high", "항혈소판·출혈·임상판단. source 확인 금지.", ""),
    ("F-APL-03", "실로스타졸", "비타민K", "antagonism", "hold", "high_risk", "high", "항혈소판·출혈·임상판단. source 확인 금지.", ""),
    ("F-ONC-01", "메토트렉세이트", "엽산", "antagonism", "hold", "high_risk", "high", "항암·엽산길항·임상판단. clinical reviewer 전 대상 아님.", ""),
    ("F-ONC-02", "타목시펜", "비타민D/칼슘", "unknown", "hold", "high_risk", "high", "항암·호르몬요법·임상판단. 대상 아님.", ""),
    ("F-ONC-03", "경구 항암제 일반(이마티닙/카페시타빈 등)", "비타민D", "unknown", "hold", "high_risk", "high", "고위험·seed 미포함.", ""),
    ("F-SSRI-01", "에스시탈로프람", "마그네슘", "unknown", "hold", "high_risk", "high", "정신건강 민감군·근거 불충분. clinical reviewer 트랙에서만.", ""),
    ("F-SSRI-02", "설트랄린", "마그네슘", "unknown", "hold", "high_risk", "high", "정신건강 민감군. clinical reviewer 트랙에서만.", ""),
    ("F-BZD-01", "알프라졸람", "마그네슘", "unknown", "hold", "high_risk", "high", "정신건강 민감군. clinical reviewer 트랙에서만.", ""),
    ("F-BZD-02", "졸피뎀", "마그네슘", "unknown", "hold", "high_risk", "high", "정신건강 민감군. clinical reviewer 트랙에서만.", ""),
    ("F-AP-01", "쿠에티아핀", "비타민D", "unknown", "hold", "high_risk", "high", "정신건강 민감군·근거 불충분. clinical reviewer 트랙에서만.", ""),
    ("F-OC-01", "드로스피레논", "엽산", "unknown", "hold", "high_risk", "high", "여성건강 민감군·근거 불충분. clinical reviewer 트랙에서만.", ""),
    ("F-PED-01", "소아 일반(미지정)", "비타민D", "unknown", "hold", "high_risk", "high", "소아 민감군·체중당용량·근거 불충분. clinical reviewer 트랙에서만.", ""),
    ("F-HERB-01", "세인트존스워트(성요한풀)", "다수 약물(영양소 외)", "unknown", "hold", "out_of_scope", "high",
     "허브-약물 상호작용(CYP3A4/P-gp 유도)·광범위·고위험 — 참고정보 베타 범위 밖.", ""),
    ("F-HERB-02", "밀크씨슬(실리마린)", "CYP 기질 약물", "unknown", "hold", "out_of_scope", "moderate",
     "허브-약물 상호작용·근거 혼재·베타 범위 밖.", ""),
    ("F-HERB-03", "은행잎(징코빌로바)", "항혈소판/항응고 약물", "unknown", "hold", "out_of_scope", "high",
     "허브-약물 상호작용(항혈소판 강화·출혈)·베타 범위 밖.", ""),
    # 칼륨보존이뇨제 — 칼륨 상승(고칼륨혈증) 방향, depletion factory 범위 밖 + PM 정책
    ("H-KSPAR-01", "스피로노락톤", "칼륨", "rise", "hold", "wrong_direction_high_risk", "high",
     "칼륨 상승(고칼륨혈증) 방향 — depletion 반대. 칼륨 보충 병용 금기 방향. PM 정책 결정 전 hold.", "potassium_safety_card 승계 필요(승격 시)."),
    ("H-KSPAR-02", "에플레레논", "칼륨", "rise", "hold", "wrong_direction_high_risk", "high",
     "칼륨 상승 방향. PM 정책 대기.", ""),
    ("H-KSPAR-03", "아밀로라이드", "칼륨", "rise", "hold", "wrong_direction_high_risk", "high",
     "칼륨 상승 방향. 국내 주로 복합제. PM 정책 대기.", ""),
    ("H-KSPAR-04", "트리암테렌", "칼륨", "rise", "hold", "wrong_direction_high_risk", "high",
     "칼륨 상승 방향. 엽산 길항은 별도 트랙. PM 정책 대기.", ""),
    ("H-WARN-01", "스피로노락톤(+ACEi/ARB 병용)", "칼륨", "rise", "hold", "drug_drug_out_of_scope", "high",
     "약-약 상호작용(칼륨 상승) — 약-영양소 고갈 factory 범위 밖. PM 분류.", ""),
]

# safe_user_copy 템플릿(참고정보 톤 — 복용지시/추천/치료/예방/구매 금지)
def safe_copy(ingredient, nutrient, mechanism, potassium_safety):
    if mechanism == "absorption":
        disp = (f"{ingredient}과(와) {nutrient}이(가) 함유된 제품을 같은 시간에 복용하면 "
                f"{ingredient}의 흡수가 줄어들 가능성이 있습니다.")
        mgmt = "같은 시간대 복용은 피하고 시간 간격을 두는 것이 도움이 될 수 있습니다. 구체적인 간격은 약사 또는 의사와 상담하세요."
    else:  # depletion → monitoring
        disp = (f"{ingredient}을(를) 복용하는 경우 {nutrient} 상태에 영향이 있을 수 있어, "
                f"상태 확인이 필요할 수 있습니다.")
        if potassium_safety:
            mgmt = "칼륨은 임의로 보충하면 위험할 수 있으므로, 보충 여부는 반드시 의사 또는 약사와 상담하세요."
        else:
            mgmt = f"{nutrient} 보충 여부는 의사 또는 약사와 상담하세요."
    return disp + " / " + mgmt


COLS = ["candidate_id", "drug_ingredient", "nutrient", "relation_type", "mechanism",
        "source_status", "source_url_or_basis", "itemseqs_checked", "evidence_snippet",
        "source_checked_at", "evidence_strength", "risk_level", "potassium_safety_card",
        "pass_to_draft", "rejection_or_needs_review_reason", "safe_user_copy", "internal_note"]


def classify_active(ingredient, items, fetched, opener):
    """fetched = [(seq,name,ingr,text,url)...]. nutrient별 결과 행 생성."""
    rows = []
    n_prod = len(fetched)
    for (cid, nutrient, mech, action, det_key, ksafe, risk, note) in items:
        det = DETECTORS[det_key]
        hits, ev, ev_url, ev_seq = [], "", "", ""
        for seq, name, ingr, text, url in fetched:
            ok, snippet = det(text)
            if ok:
                hits.append(seq)
                if not ev:
                    ev, ev_url, ev_seq = snippet[:240], url, seq
        n_found = len(hits)
        # carry-forward known reject (레보티록신×Mg = Q08 미기재)
        if cid == "F-FQ-02" and n_found == 0:
            status, strength, reason = "reject", "label_missing", "Q08 레보티록신×Mg 미기재 확정 재확인(상호작용 문맥 동거어 없음)."
        elif n_prod == 0:
            status, strength = "needs_review", "no_product"
            reason = "국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요."
        elif n_found == 0:
            status, strength = "reject", "label_missing"
            reason = (f"fetch {n_prod}품목 상호작용/주의/이상반응 문맥에 {nutrient} 방향성 동거어 없음 — "
                      f"한국 허가사항 미기재(literature only 가능). 계열 유추 채택 금지.")
        else:
            status = "source_confirmed"
            strength = "high" if n_found == n_prod else "moderate"
            reason = f"{n_found}/{n_prod} 품목 허가사항 문맥에 {nutrient} {'고갈' if mech=='depletion' else '흡수'} 방향 신호 존재."
        pass_draft = "true" if status == "source_confirmed" else "false"
        if status == "source_confirmed":
            basis = (f"식약처 nedrug getItemDetail / {ingredient} / itemSeq {';'.join(hits)} / "
                     f"{nutrient} 동거어 / 확인일 {CHECKED_AT} | {ev_url}")
        elif n_prod > 0:
            basis = (f"식약처 nedrug getItemDetail / {ingredient} / 확인 itemSeq "
                     f"{';'.join(s for s,_,_,_,_ in fetched)} / {nutrient} 동거어 없음 / 확인일 {CHECKED_AT}")
        else:
            basis = f"식약처 nedrug searchDrug / {ingredient} / 국내 대표 품목 미확보 / 확인일 {CHECKED_AT}"
        rows.append({
            "candidate_id": cid, "drug_ingredient": ingredient, "nutrient": nutrient,
            "relation_type": action, "mechanism": mech, "source_status": status,
            "source_url_or_basis": basis,
            "itemseqs_checked": ";".join(s for s, _, _, _, _ in fetched),
            "evidence_snippet": ev, "source_checked_at": CHECKED_AT,
            "evidence_strength": strength, "risk_level": risk,
            "potassium_safety_card": "true" if ksafe else "false",
            "pass_to_draft": pass_draft,
            "rejection_or_needs_review_reason": "" if status == "source_confirmed" else reason,
            "safe_user_copy": safe_copy(ingredient, nutrient, mech, ksafe) if status == "source_confirmed" else "",
            "internal_note": note,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="활성 성분 fetch 개수 제한(디버그)")
    args = ap.parse_args()

    opener = make_opener()
    rows = []
    ingredients = list(SEARCH_INGREDIENTS.items())
    if args.limit:
        ingredients = ingredients[:args.limit]

    print("=== 활성 source 확인 (searchDrug → getItemDetail fetch) ===")
    for ingredient, items in ingredients:
        exclude = "메틸프레드니솔론" if ingredient == "프레드니솔론" else None
        seqs, st = search_itemseqs(opener, ingredient, exclude_ingr=exclude)
        if st != "ok":
            print(f"  [품목없음] {ingredient}: {st}")
            rows.extend(classify_active(ingredient, items, [], opener))
            continue
        fetched = []
        for seq, name, ingr in seqs:
            try:
                text, url = fetch_detail(opener, seq)
                fetched.append((seq, name, ingr, text, url))
                time.sleep(0.7)
            except Exception as e:  # noqa
                print(f"    [fetch err] {ingredient} {seq}: {type(e).__name__}")
        got = len(fetched)
        new_rows = classify_active(ingredient, items, fetched, opener)
        for r in new_rows:
            tag = "CONFIRMED" if r["source_status"] == "source_confirmed" else r["source_status"].upper()
            print(f"  {ingredient:12s} {r['candidate_id']:12s} {r['nutrient']:8s} "
                  f"[{got}품목] -> {tag}")
        rows.extend(new_rows)
        time.sleep(0.5)

    # carry-forward (fetch 없음)
    print("\n=== carry-forward (hold/reject — fetch 없음) ===")
    for (cid, ing, nut, rtype, status, strength, risk, reason, note) in CARRIED:
        rows.append({
            "candidate_id": cid, "drug_ingredient": ing, "nutrient": nut,
            "relation_type": rtype, "mechanism": "", "source_status": status,
            "source_url_or_basis": f"carry-forward / 확인일 {CHECKED_AT}", "itemseqs_checked": "",
            "evidence_snippet": "", "source_checked_at": CHECKED_AT,
            "evidence_strength": strength, "risk_level": risk, "potassium_safety_card": "false",
            "pass_to_draft": "false", "rejection_or_needs_review_reason": reason,
            "safe_user_copy": "", "internal_note": note,
        })

    from collections import Counter
    tally = Counter(r["source_status"] for r in rows)
    confirmed = [r["candidate_id"] for r in rows if r["source_status"] == "source_confirmed"]
    print("\n=== 결과 tally ===", dict(tally))
    print(f"총 처리: {len(rows)} | source_confirmed: {len(confirmed)}")
    print("confirmed:", ", ".join(confirmed) or "없음")

    if not args.no_write:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)} ({len(rows)} rows)")
    else:
        print("\n(--no-write)")
    print("\nVERIFY FACTORY SOURCES v1.2: DONE — relations 55 그대로, 구현 0(do_not_implement_yet).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
