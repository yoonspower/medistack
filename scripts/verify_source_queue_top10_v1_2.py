#!/usr/bin/env python3
"""
verify_source_queue_top10_v1_2.py
MediStack — 다음 relation 확장 큐(Q01–Q18) 중 **Top10 우선 후보**의 제안 nutrient 테마가
MFDS nedrug 허가사항(getItemDetail) 원문 상호작용/주의 문맥에 실재하는지 **출처 존재 여부만** 확인한다.

⚠️ 이 스크립트는 relation/full index/alias/export/src 를 한 줄도 수정하지 않는다(읽기 전용 + 네트워크 fetch).
   relation 을 추가/승격/flip 하지 않는다. relations 는 41 그대로다.
   제품추천/복용지시/영양제 추천 문구를 생성하지 않는다(허가사항 원문 인용만).
   여기서 source_confirmed 로 나오더라도 "다음 단계 검토 대상"일 뿐 구현 지시가 아니다(do_not_implement_yet).

방법(verify_atier_relation_sources.py 패턴 승계):
  - 테마별 대표 단일성분 품목 2~3건의 getItemDetail HTML 을 fetch → 태그 제거 → 정규화.
  - 테마별 **특정 신호어**(첨가제·우연 언급과 구분)를 상호작용/주의 문맥에서만 잡고 증거 스니펫 캡처.
  - 첨가제/조성표 문맥(산화마그네슘·스테아르산마그네슘·착색·코팅·분량·규격 등)은 배제.

활성 검증 대상(Top10):
  P1: Q01(에스오메프라졸 B12/Mg, index-track), Q06(FQ×아연), Q07(테트라사이클린×아연)
  P2: Q02(잔여 PPI×B12/Mg=오메프라졸 대표), Q03(잔여 경구 비스포×Ca/Fe/Mg=알렌드론산),
      Q04(비스포×Fe/Mg enrichment=리세/이반/알렌), Q08(레보티록신×Mg), Q10(클로르탈리돈×K/Mg),
      Q11(인다파미드×K/Mg)
  P3: Q05(세팔로스포린/FQ class×Fe/Ca/Mg — 계열 일반화 위험, needs_review 기본)

분류(증거 기반):
  source_confirmed : 신호어가 상호작용/주의 문맥에 명확히 존재(첨가제 아님). 다음 검토 대상.
  needs_review     : 신호 일부/문맥 모호/계열일반화 위험 → 사람 검토 필요.
  missing/reject   : 신호 없음 / 근거 어긋남.
  hold             : 안전정책 선행 또는 영구 보류(여기서 fetch 안 함, 결과표에만 캐리포워드).

사용: python3 scripts/verify_source_queue_top10_v1_2.py [--no-write]
출력: data/source_queue_top10_verification_v1_2.csv (분석 산출물만)
"""
import csv
import html as htmllib
import http.cookiejar
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
OUT_CSV = os.path.join(DATA, "source_queue_top10_verification_v1_2.csv")
CHECKED_AT = "2026-06-14"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

# 첨가제/조성표(false positive) 배제용 문맥.
EXCIPIENT_CTX = re.compile(r"첨가제|착색|코팅|활택|부형|결합제|붕해|산화마그네슘|스테아르산마그네슘|"
                           r"규산마그네슘|탄산마그네슘|분량|규격|용량단위|밀리그램\)")


def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch_text(opener, seq):
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


def snip(text, i, pad=95):
    return text[max(0, i - pad):i + pad].strip()


# ---- 테마별 신호 탐지기. 각 함수는 (found, evidence_snippet) 반환 ----

def sig_zinc_interaction(text):
    """아연이 흡수저해/병용/다가양이온 상호작용 문맥에 등장(첨가제 아님)."""
    for m in re.finditer("아연", text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"흡수|병용|다가\s*양이온|킬레이트|복합체|간격|동시|제산제|함유.{0,8}제제", w):
            return True, snip(text, i)
    return False, ""


def sig_mg_depletion(text):
    """저마그네슘혈증(고갈) — 첨가제 마그네슘과 구분."""
    for m in re.finditer("저마그네슘", text):
        return True, snip(text, m.start())
    return False, ""


def sig_b12_depletion(text):
    """비타민 B12(시아노코발라민) 흡수장애 문맥."""
    for m in re.finditer(r"시아노코발라민|비타민\s*B\s*12|B\s*12", text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if "흡수" in w or "시아노코발라민" in w or "결핍" in w:
            return True, snip(text, i)
    return False, ""


def sig_polyvalent_absorption(text):
    """다가 양이온(칼슘/철/마그네슘) 흡수저해 간격 권고 문맥."""
    for m in re.finditer(r"다가\s*양이온", text):
        return True, snip(text, m.start())
    return False, ""


def sig_mg_in_polyvalent(text):
    """마그네슘이 다가양이온/제산제 흡수 상호작용 문맥에 등장(흡수저해)."""
    for m in re.finditer("마그네슘", text):
        i = m.start()
        w = text[max(0, i - 70):i + 70]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"다가\s*양이온|제산제|흡수.{0,12}(저해|저하|감소|방해)|"
                     r"(저해|저하|감소|방해).{0,12}흡수|병용.{0,12}흡수", w):
            return True, snip(text, i)
    return False, ""


def sig_iron_absorption(text):
    """철(분)이 흡수저해/병용/복합체 문맥에 등장(착색용 산화철 등 배제)."""
    for m in re.finditer(r"철분|철염|철\s*함유|철\s*제제|철제", text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"흡수|병용|복합체|간격|동시|다가\s*양이온", w):
            return True, snip(text, i)
    return False, ""


def sig_ca_absorption(text):
    """칼슘이 흡수저해/병용/다가양이온 문맥(조성·B12·철 흡수 문맥 배제)."""
    for m in re.finditer("칼슘", text):
        i = m.start()
        w = text[max(0, i - 60):i + 60]
        if EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"B\s*12|시아노코발라민", w):
            continue
        if re.search(r"다가\s*양이온|흡수.{0,12}(저해|저하|감소|방해)|"
                     r"(저해|저하|감소|방해).{0,12}흡수|제산제|간격", w):
            return True, snip(text, i)
    return False, ""


def sig_potassium_depletion(text):
    """저칼륨혈증(전해질 고갈) 문맥."""
    for m in re.finditer(r"저칼륨|칼륨\s*(이|을|의)?\s*(저하|감소|상실|배설)|칼륨\s*소실", text):
        return True, snip(text, m.start())
    for m in re.finditer("칼륨", text):
        i = m.start()
        w = text[max(0, i - 50):i + 50]
        if re.search(r"저하|감소|상실|배설|소실|보충|혈증", w):
            return True, snip(text, i)
    return False, ""


def sig_mg_depletion_loop(text):
    """이뇨제 맥락의 저마그네슘혈증(전해질 소실)."""
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


# 테마 정의:
# (queue_id, candidate_theme, ingredient_or_class, expected_nutrient, expected_card_impact,
#  [(seq, name)...], [(nutrient_label, detector_fn)...], risk_level, default_decision_if_missing)
ACTIVE = [
    # ----- P1 -----
    ("Q01", "PPI x B12/Mg (esomeprazole index-track)", "에스오메프라졸(esomeprazole)",
     "비타민B12·마그네슘", "index_only(relation16 존재·카드0)",
     [("201405854", "라베프라졸 교차참조 대표(에스오메 단일제 itemSeq 미보유)")],
     [("마그네슘", sig_mg_depletion), ("비타민B12", sig_b12_depletion)],
     "low",
     "needs_review_index_track"),

    ("Q06", "Fluoroquinolone x 아연 (enrichment)", "레보/시프로/오플록사신(fluoroquinolone)",
     "아연", "0(enrichment·기존 covered)",
     [("201207060", "글로비트정(레보플록사신)"),
      ("200403053", "뉴록사신정(시프로플록사신)"),
      ("199602013", "넬슨오플록사신정(오플록사신)")],
     [("아연", sig_zinc_interaction)],
     "low", "missing"),

    ("Q07", "Tetracycline x 아연 (enrichment)", "독시/미노사이클린(tetracycline)",
     "아연", "0(enrichment·기존 covered)",
     [("201403031", "독시정(독시사이클린)"),
      ("198300718", "모노신정(독시사이클린)"),
      ("202500078", "미노젠캡슐(미노사이클린)")],
     [("아연", sig_zinc_interaction)],
     "low", "missing"),

    # ----- P2 -----
    ("Q02", "잔여 PPI x B12/Mg", "오메프라졸 등 잔여 PPI 단일제",
     "비타민B12·마그네슘", "low(name_only 소량)",
     [("199202074", "라메졸캡슐20mg(오메프라졸)"),
      ("200402992", "메프라졸캡슐(오메프라졸)")],
     [("마그네슘", sig_mg_depletion), ("비타민B12", sig_b12_depletion)],
     "low", "missing"),

    ("Q03", "잔여 경구 비스포스포네이트 x Ca/Fe/Mg", "알렌드론산(대표·경구 비스포)",
     "칼슘·철·마그네슘", "low~med(name_only 소량)",
     [("201902246", "라이트알렌드론정70mg"),
      ("200500488", "보나드론정70mg(알렌드론산)")],
     [("다가양이온(칼슘·철·Mg)", sig_polyvalent_absorption),
      ("철", sig_iron_absorption), ("마그네슘", sig_mg_in_polyvalent)],
     "low", "missing"),

    ("Q04", "비스포스포네이트 x 철/Mg enrichment", "리세/이반/알렌드론산(기존 covered)",
     "철·마그네슘", "0(enrichment·기존 covered)",
     [("201903166", "건토넬정35mg(리세드론산)"),
      ("201306285", "경보이반드로네이트정(이반드론산)"),
      ("201902246", "라이트알렌드론정70mg(알렌드론산)")],
     [("철", sig_iron_absorption), ("마그네슘", sig_mg_in_polyvalent),
      ("다가양이온", sig_polyvalent_absorption)],
     "low", "missing"),

    ("Q08", "Levothyroxine x Mg (enrichment)", "레보티록신(기존 covered)",
     "마그네슘", "0(enrichment·기존 covered)",
     [("200401821", "씬지로이드정0.05mg(레보티록신)"),
      ("197400278", "씬지로이드정0.1mg(레보티록신)"),
      ("200301116", "씬지록신정100mcg(레보티록신)")],
     [("마그네슘", sig_mg_in_polyvalent)],
     "low", "missing"),

    ("Q10", "치아지드유사 x 칼륨/Mg", "클로르탈리돈(chlortalidone)",
     "칼륨·마그네슘", "med(name_only 64)·복합 다수",
     [("202500118", "클로베네정25mg(클로르탈리돈)"),
      ("200302309", "하이그로톤정25mg(클로르탈리돈)")],
     [("칼륨", sig_potassium_depletion), ("마그네슘", sig_mg_depletion_loop)],
     "moderate", "missing"),

    ("Q11", "치아지드유사 x 칼륨/Mg", "인다파미드(indapamide)",
     "칼륨·마그네슘", "low~med(name_only 16)",
     [("199900835", "나트릭스서방정(인다파미드)"),
      ("199501023", "다피드정2.5mg(인다파미드)"),
      ("200805114", "후루덱스서방정(인다파미드)")],
     [("칼륨", sig_potassium_depletion), ("마그네슘", sig_mg_depletion_loop)],
     "moderate", "missing"),

    # ----- P3 (계열 일반화 위험) -----
    ("Q05", "세팔로스포린 class x Fe/Ca/Mg", "세파클러·세프포독심 등 경구 세팔로스포린",
     "철·칼슘·마그네슘", "med(name_only 다수)이나 계열일반화 불가",
     [("199700521", "세파클러 대표(name_only)"),  # 대표 후보 — 미보유시 fetch 실패 처리
      ("200707142", "세프디어캡슐(세프디니르·교차참조)")],
     [("철", sig_iron_absorption), ("칼슘", sig_ca_absorption),
      ("다가양이온", sig_polyvalent_absorption)],
     "moderate", "needs_review_class_generalization"),
]


def classify(qid, n_prod, n_found, default_missing):
    """active 후보 분류. Q01은 index-track, Q05는 계열일반화 위험으로 특수 처리."""
    if n_prod == 0:
        return "needs_review", "허가사항 fetch 0건(대표품목 미확보/네트워크) — 재시도 필요", "low"
    if qid == "Q01":
        # relation16 이미 존재; 신규 relation 불필요. 신호가 있어도 index/alias 트랙.
        if n_found > 0:
            return "needs_review", ("PPI 계열 동거 신호 확인되나 relation16(에스오메x마그네슘) 이미 존재 → "
                                    "신규 relation 불필요. full index/alias 확장 트랙(PM 승인)에서만 다룸"), "low"
        return "needs_review", "에스오메 단일제 itemSeq 미보유(교차참조만) — 인덱스/alias 트랙 별도 확인", "low"
    if qid == "Q05":
        if n_found > 0:
            return "needs_review", ("세프디니르×철은 성분특이(적색 비흡수복합). 세파클러 등 계열 일반화 근거 약함 → "
                                    "계열 일괄확장 금지, 성분별 개별 확인 필요"), "moderate"
        return "reject", ("fetch 품목에 흡수 상호작용 동거어 없음 + 계열 일반화 위험 → 계열 일괄확장 reject"), "moderate"
    # 일반 active 후보
    if n_found == 0:
        return "reject" if default_missing == "missing" else default_missing, \
            f"fetch {n_prod}품목 어디에도 상호작용 문맥 신호 없음 — 한국 허가사항 미기재(literature only 가능)", "low"
    conf = "high" if n_found == n_prod else "moderate"
    return "source_confirmed", \
        f"{n_found}/{n_prod} 품목 허가사항 상호작용/주의 문맥에 신호 존재", conf


# carry-forward 행(재fetch 불필요). decision/이유 고정.
CARRIED = [
    ("Q12", "스타틴 x CoQ10", "로수바스타틴(rosuvastatin)", "코엔자임Q10",
     "large(name_only 472)", "needs_review", "literature_only(예상)",
     "허가사항-우선 gate 미통과 예상(CoQ10 한국 라벨 미기재 관행). source-policy(이차문헌 허용) 입력용. 단독 채택 금지.",
     "moderate"),
    ("Q13", "스타틴 x CoQ10", "아토르바스타틴(atorvastatin)", "코엔자임Q10",
     "large(name_only 267)", "needs_review", "literature_only(예상)",
     "Q12 동일 — 허가사항 미기재 예상. source-policy 결정 전 채택 금지.", "moderate"),
    ("Q14", "스타틴 x CoQ10", "피타바/심바 등 잔여 스타틴", "코엔자임Q10",
     "med(name_only 합 ~205)", "needs_review", "literature_only(예상)",
     "Q12 동일. source-policy 결정 전 채택 금지.", "moderate"),
    ("Q09", "메트포르민 x B12", "메트포르민", "비타민B12",
     "0(headroom 0·이미 covered)", "hold", "허가사항(relation12 라이브)",
     "relation12 라이브 + 메트포르민 인덱스 전건 covered(headroom 0). 신규 작업 없음, 신규 품목 유입 모니터만.",
     "low"),
    ("Q15", "H2 차단제 x B12", "파모티딘/라푸티딘/니자티딘", "비타민B12",
     "med(name_only ~202)", "hold", "literature_only(CHECKED missing)",
     "A티어 확인서에서 허가사항 미기재(missing) 확정(E07/E09/E10). 재fetch 불필요. source-policy 결정 시에만 재검토.",
     "moderate"),
    ("Q16", "항응고/항혈소판 x 비타민K", "와파린·DOAC·항혈소판", "비타민K",
     "N/A(영구 금지)", "hold", "N/A",
     "CLAUDE.md 영구 금지(antagonism·임상판단 행). 후보화/ source 확인 금지.", "high"),
    ("Q17", "항암제 x 영양소", "경구 항암제 일반", "(미지정)",
     "N/A(고위험)", "hold", "N/A",
     "임상판단·개인차 강한 고위험군. 참고정보 베타 톤으로 다룰 수 없음. 후보화 금지.", "high"),
    ("Q18", "임신/소아/정신건강 x 영양소", "임신·피임·소아·SSRI/벤조/항정신병", "(미지정)",
     "N/A(민감군)", "hold", "N/A",
     "민감군·근거 불충분·개인차 큼. clinical reviewer 트랙에서만 별도 검토. 후보화 금지.", "high"),
]

COLS = ["queue_id", "candidate_theme", "ingredient_or_class", "expected_nutrient",
        "expected_card_impact", "source_status", "source_type", "source_title",
        "source_url_or_note", "source_checked_at", "confidence", "risk_level",
        "decision", "reason", "proposed_next_action", "do_not_implement_yet"]


def run_active():
    opener = make_opener()
    rows = []
    for (qid, theme, ing, exp_nut, impact, seqs, detectors, risk, default_missing) in ACTIVE:
        texts = []
        for s, name in seqs:
            try:
                t, url = fetch_text(opener, s)
                texts.append((s, name, t, url))
                time.sleep(0.8)
            except Exception as e:  # noqa
                print(f"  [fetch err] {qid} {s} {name}: {type(e).__name__} {e}")
        print(f"{qid} {ing}: fetched {len(texts)}/{len(seqs)} 품목")
        # 테마 내 모든 nutrient detector 를 합산해서 후보 단위 판정.
        # nutrient별 증거를 모으되, 후보 status 는 "어느 nutrient든 신호 있으면 confirmed" 규칙.
        per_nut_evidence = []  # (nutlabel, found_seqs, snippet, url)
        for nutlabel, fn in detectors:
            found_seqs, ev, ev_url = [], "", ""
            for s, name, t, url in texts:
                ok, snippet = fn(t)
                if ok:
                    found_seqs.append((s, name))
                    if not ev:
                        ev, ev_url = snippet[:260], url
            per_nut_evidence.append((nutlabel, found_seqs, ev, ev_url))
            tag = f"{len(found_seqs)}/{len(texts)}"
            print(f"    {nutlabel:22s} {tag:6s} {'HIT' if found_seqs else 'no'} {ev[:60]}")

        n_prod = len(texts)
        # 후보 status: detector 중 가장 강한 신호(가장 많은 품목 hit)를 채택
        best = max(per_nut_evidence, key=lambda x: len(x[1])) if per_nut_evidence else ("", [], "", "")
        n_found = len(best[1])
        decision, reason, conf = classify(qid, n_prod, n_found, default_missing)
        # source_status mirrors decision but uses controlled vocab
        ss_map = {"source_confirmed": "source_confirmed", "needs_review": "needs_review",
                  "reject": "reject", "hold": "hold",
                  "needs_review_index_track": "needs_review",
                  "needs_review_class_generalization": "needs_review"}
        source_status = ss_map.get(decision, decision)
        # nutrient별 confirmed 라벨 모으기
        confirmed_nuts = [nl for nl, fs, ev, url in per_nut_evidence if fs]
        # url_or_note: 신호가 잡혔으면(decision 무관) itemSeq+스니펫, 아니면 fetch 메모
        if best[2] and n_found > 0:
            # 어떤 itemSeq에서 잡혔는지 + 스니펫
            hit_seqs = ";".join(s for s, _ in best[1])
            prefix = "" if decision == "source_confirmed" else "[교차참조/index-track 신호] "
            note = (f"{prefix}itemSeq {hit_seqs} (nutrient={best[0]}; 동거 nutrient={','.join(confirmed_nuts)}) | "
                    f"URL {best[3]} | 증거: \"{best[2]}\"")
            source_type = "허가사항"
            source_title = f"식약처 nedrug getItemDetail / {ing}"
        elif n_prod == 0:
            note = "fetch 0건 — 대표품목 미확보 또는 네트워크 오류, 재시도 필요"
            source_type = "허가사항(미확인)"
            source_title = f"식약처 nedrug getItemDetail / {ing}"
        else:
            checked = ";".join(s for s, _, _, _ in texts)
            note = (f"fetch {n_prod}품목(itemSeq {checked}) 상호작용 문맥에 {exp_nut} 동거어 없음 "
                    f"(첨가제 문맥만/미기재). literature only 가능.")
            source_type = "허가사항(미기재)"
            source_title = f"식약처 nedrug getItemDetail / {ing}"

        next_action = {
            "Q01": "신규 relation 금지. full index/alias 확장 트랙(에스오메프라졸 매핑)은 PM 승인 별도 단계.",
            "Q05": "계열 일괄확장 금지. 성분별 허가사항 개별 확인 후에만, 동거어 없으면 reject.",
            "Q02": "오메프라졸은 relation13(B12)·14(Mg) 이미 라이브 → 신규 relation 불필요. 잔여 단일제 인덱스/alias 매핑(PM 승인).",
            "Q04": "리세/이반(relation40/41) 기존 칼슘 relation 에 Fe/Mg enrichment draft 후보(PM·검토). 알렌드론산은 다가양이온 라벨 없음→Fe/Mg 미적용.",
            "Q06": "신규 relation 후보(FQ×아연) — draft 생성(PM·검토 후 별도 단계). 기존 FQ covered 품목에 아연 테마 보강.",
            "Q07": "신규 relation 후보(테트라사이클린×아연) — draft 생성(PM·검토 후 별도 단계).",
            "Q10": "신규 relation 후보(클로르탈리돈×K/Mg) — 승격 시 칼륨 안전정책(product_link_allowed=false·potassium_safety_card=true) 승계 필수.",
            "Q11": "신규 relation 후보(인다파미드×K/Mg) — Q10 동일 칼륨 안전정책 승계 필수.",
        }.get(qid, ("source_confirmed 면 draft relation 후보(PM·검토 후 별도 단계)."
                    if decision == "source_confirmed" else
                    "미기재 — 채택 금지. source-policy(이차문헌) 결정 또는 보류."))

        rows.append({
            "queue_id": qid, "candidate_theme": theme, "ingredient_or_class": ing,
            "expected_nutrient": exp_nut, "expected_card_impact": impact,
            "source_status": source_status, "source_type": source_type,
            "source_title": source_title, "source_url_or_note": note,
            "source_checked_at": CHECKED_AT, "confidence": conf, "risk_level": risk,
            "decision": source_status, "reason": reason,
            "proposed_next_action": next_action, "do_not_implement_yet": "true",
        })
    return rows


def carried_rows():
    rows = []
    for (qid, theme, ing, nut, impact, decision, srctype, reason, risk) in CARRIED:
        rows.append({
            "queue_id": qid, "candidate_theme": theme, "ingredient_or_class": ing,
            "expected_nutrient": nut, "expected_card_impact": impact,
            "source_status": decision, "source_type": srctype,
            "source_title": "(carry-forward · 재fetch 불필요)",
            "source_url_or_note": "carry-forward: 기존 확정 verdict 승계(재fetch 없음)",
            "source_checked_at": CHECKED_AT, "confidence": "moderate" if decision == "needs_review" else "high",
            "risk_level": risk, "decision": decision, "reason": reason,
            "proposed_next_action": "보류/정책결정 대기. 채택 금지.",
            "do_not_implement_yet": "true",
        })
    return rows


def main():
    write = "--no-write" not in sys.argv
    print("=== Top10 active source 확인 (네트워크 fetch) ===")
    rows = run_active()
    print("\n=== carry-forward (Q09,Q12-Q18) — 재fetch 없음 ===")
    rows += carried_rows()

    from collections import Counter
    tally = Counter(r["decision"] for r in rows)
    print("\n=== verdict tally(전체) ===", dict(tally))
    active_ids = {q[0] for q in ACTIVE}
    atally = Counter(r["decision"] for r in rows if r["queue_id"] in active_ids)
    print("=== Top10 active verdict tally ===", dict(atally))
    confirmed = [r["queue_id"] for r in rows if r["decision"] == "source_confirmed"]
    print("source_confirmed:", ", ".join(confirmed) or "없음")

    if write:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)}  ({len(rows)} rows)")
    else:
        print("\n(--no-write)")
    print("\nVERIFY SOURCE QUEUE TOP10 v1.2: DONE")
    print("relations 는 41 그대로. 어떤 것도 구현하지 않음(do_not_implement_yet=true).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
