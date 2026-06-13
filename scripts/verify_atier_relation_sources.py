#!/usr/bin/env python3
"""
verify_atier_relation_sources.py
MediStack — A티어 Top10 relation 확장 후보(E01–E10)의 제안 nutrient 테마가
MFDS nedrug 허가사항(getItemDetail) 원문에 실재하는지 **출처 존재 여부만** 확인한다.

⚠️ 이 스크립트는 relation/full index/alias/export/src 를 한 줄도 수정하지 않는다(읽기 전용 + 네트워크 fetch).
   relation 을 추가/승격하지 않는다. 출력은 source_confirmed / needs_review / missing / reject 분류와 증거뿐이다.
   제품추천/복용지시/영양제 추천 문구를 생성하지 않는다(허가사항 원문 인용만).

방법:
  - 후보 성분별 대표 품목(단일성분 경구제 우선) 2~3건의 getItemDetail HTML 을 fetch → 태그 제거 → 정규화.
  - 테마별 **특정 신호어**(첨가제·우연 언급과 구분)로 검색하고 증거 스니펫을 캡처한다:
      마그네슘(고갈)      : '저마그네슘'(저마그네슘혈증)            ← 첨가제 '산화마그네슘' 등과 구분
      비타민B12(고갈)     : '시아노코발라민' 또는 'B12'+흡수 문맥
      칼슘/철/Mg(흡수,비스포): '다가 양이온' / '제산제' / 칼슘·흡수 문맥
      철분(흡수, 세팔로)   : '철' + (흡수/병용/적색 대변) 문맥
  - 한 후보의 ≥1 품목에서 해당 테마 신호어가 상호작용/주의 문맥에 잡히면 그 nutrient 를 confirmed.

분류(증거 기반):
  source_confirmed : 신호어가 상호작용/주의 문맥에 명확히 존재 → 다음 relation 승격 검토 대상으로 표시(promote_eligible=true).
  needs_review     : 신호어 일부/문맥 모호 → 사람 검토 필요(promote_eligible=false).
  missing          : fetch 한 어떤 품목에도 신호 없음(promote_eligible=false).
  reject           : 테마가 허가사항 근거와 어긋남(promote_eligible=false).

쓰기(분석 산출물만):
  data/relation_source_verification_atier_v1_1.csv
사용: python3 scripts/verify_atier_relation_sources.py [--no-write]
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
OUT_CSV = os.path.join(DATA, "relation_source_verification_atier_v1_1.csv")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"
CHECKED_AT = "2026-06-13"

# 신호어 정의: (라벨, 정규식). 첨가제/우연 언급과 구분되는 상호작용·주의 신호.
SIG = {
    "mg_depletion": re.compile(r"저마그네슘"),
    "b12_depletion": re.compile(r"시아노코발라민|B\s*12"),
    "polyvalent_absorption": re.compile(r"다가\s*양이온|제산제"),
    "iron_absorption": re.compile(r"철"),
}

# 후보 E01–E10: (candidate_id, rank, ingredient, candidate_type, [seqs], [(nutrient, theme_dir, [signal_keys], confirm_rule)])
# confirm_rule: 신호 매칭 시 status. 'primary'=핵심 nutrient.
CANDIDATES = [
    ("E01", 1, "라베프라졸", "PPI", ["201405854", "201308942", "201206679"],
     [("마그네슘", "depletion", ["mg_depletion"]), ("비타민B12", "depletion", ["b12_depletion"])]),
    ("E02", 2, "판토프라졸", "PPI", ["202107096", "201200590", "200705176"],
     [("마그네슘", "depletion", ["mg_depletion"]), ("비타민B12", "depletion", ["b12_depletion"])]),
    ("E03", 3, "란소프라졸", "PPI", ["201308978", "201308053"],
     [("마그네슘", "depletion", ["mg_depletion"]), ("비타민B12", "depletion", ["b12_depletion"])]),
    ("E05", 5, "덱스란소프라졸", "PPI", ["201802450", "201207343"],
     [("마그네슘", "depletion", ["mg_depletion"]), ("비타민B12", "depletion", ["b12_depletion"])]),
    ("E04", 4, "리세드론산", "비스포스포네이트", ["201903166", "200803148", "200713889"],
     [("칼슘·철·마그네슘(다가양이온)", "absorption", ["polyvalent_absorption"])]),
    ("E06", 6, "이반드론산", "비스포스포네이트", ["201306285", "201306253"],
     [("칼슘·철·마그네슘(다가양이온)", "absorption", ["polyvalent_absorption"])]),
    ("E07", 7, "파모티딘", "H2차단제", ["200109233", "202000553"],
     [("비타민B12", "depletion", ["b12_depletion"])]),
    ("E09", 9, "라푸티딘", "H2차단제", ["201302935", "201908602", "201507415"],
     [("비타민B12", "depletion", ["b12_depletion"])]),
    ("E10", 10, "니자티딘", "H2차단제", ["200102170", "201400834", "200000919"],
     [("비타민B12", "depletion", ["b12_depletion"])]),
    ("E08", 8, "세프디니르", "세팔로스포린", ["200711458", "200712298", "200709156"],
     [("철분", "absorption", ["iron_absorption"])]),
]


def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch_text(opener, seq):
    url = DETAIL_URL.format(seq)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    with opener.open(req, timeout=30) as r:
        raw = r.read().decode("utf-8", "replace")
    text = re.sub(r"<[^>]+>", " ", raw)
    text = htmllib.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text, url


def snippet(text, m, pad=130):
    i = m.start()
    seg = text[max(0, i - pad):i + pad]
    return seg.strip()


# 첨가제 문맥(false positive) 배제용: 신호어 주변에 첨가제/조성 단서가 있으면 제외
EXCIPIENT_CTX = re.compile(r"첨가제|산화마그네슘|스테아르산마그네슘|규산마그네슘|착색|코팅")


def search_signal(text, sigkey):
    """반환: (found, evidence_snippet) — 상호작용/주의 문맥의 신호만. 첨가제 문맥은 배제."""
    rx = SIG[sigkey]
    best = None
    for m in rx.finditer(text):
        seg = snippet(text, m)
        # b12: 흡수/흡수장애 문맥 요구(우연 'B12' 토큰 배제)
        if sigkey == "b12_depletion" and "시아노코발라민" not in seg and "흡수" not in seg:
            continue
        # iron: 흡수/병용/적색/대변 문맥 요구(착색용 산화철 등 배제)
        if sigkey == "iron_absorption":
            if not re.search(r"흡수|병용|적색|대변|함유 제제|제2철|제일철", seg):
                continue
            if EXCIPIENT_CTX.search(seg):
                continue
        # mg/polyvalent: 첨가제 문맥 배제
        if sigkey in ("mg_depletion", "polyvalent_absorption") and EXCIPIENT_CTX.search(seg):
            # 저마그네슘/다가양이온은 첨가제어와 거의 안 겹치지만 안전차원
            if sigkey == "polyvalent_absorption" and "다가" not in seg and "제산제" not in seg:
                continue
        best = (True, seg)
        break
    return best or (False, "")


def verify():
    opener = make_opener()
    # seq -> text 캐시(후보 간 중복 없음이라 단순)
    rows = []
    for cid, rank, ing, ctype, seqs, themes in CANDIDATES:
        # fetch all seqs for this candidate
        texts = []
        for s in seqs:
            try:
                t, url = fetch_text(opener, s)
                texts.append((s, t, url))
                time.sleep(0.8)
            except Exception as e:
                print(f"  [fetch err] {ing} {s}: {type(e).__name__} {e}")
        print(f"{cid} {ing}: fetched {len(texts)}/{len(seqs)} 품목")
        for nutrient, direction, sigkeys in themes:
            found_seqs, evidence, src_url = [], "", ""
            for s, t, url in texts:
                hit = False
                for sk in sigkeys:
                    ok, ev = search_signal(t, sk)
                    if ok:
                        hit = True
                        if not evidence:
                            evidence, src_url = ev[:240], url
                        break
                if hit:
                    found_seqs.append(s)
            n_prod = len(texts)
            n_found = len(found_seqs)
            # 분류
            if n_prod == 0:
                status, note = "needs_review", "허가사항 fetch 실패 — 네트워크 재시도 필요"
            elif n_found == 0:
                status = "missing"
                note = f"fetch {n_prod}품목 어디에도 신호 없음 — 한국 허가사항 미기재(literature only 가능)"
            elif n_found == n_prod:
                status = "source_confirmed"
                note = f"전 품목({n_found}/{n_prod}) 허가사항 상호작용/주의에 신호 존재"
            else:
                status = "source_confirmed"
                note = f"일부 품목({n_found}/{n_prod}) 허가사항에 신호 존재(제조사별 표기 차이) — 대표 출처로 confirmed"
            promote = "true" if status == "source_confirmed" else "false"
            rows.append({
                "candidate_id": cid, "priority_rank": rank, "ingredient": ing,
                "candidate_type": ctype, "nutrient": nutrient, "theme_direction": direction,
                "products_checked": n_prod, "products_with_signal": n_found,
                "found_item_seqs": ";".join(found_seqs),
                "source_status": status, "promote_eligible": promote,
                "evidence_quote": evidence, "source_url": src_url,
                "source_method": "nedrug.getItemDetail", "source_checked_at": CHECKED_AT,
                "note": note,
            })
    return rows


COLS = ["candidate_id", "priority_rank", "ingredient", "candidate_type", "nutrient",
        "theme_direction", "products_checked", "products_with_signal", "found_item_seqs",
        "source_status", "promote_eligible", "evidence_quote", "source_url",
        "source_method", "source_checked_at", "note"]


def main():
    write = "--no-write" not in sys.argv
    rows = verify()
    print("\n=== 검증 결과(후보×nutrient) ===")
    for r in rows:
        print(f"  {r['candidate_id']} {r['ingredient']:8s} × {r['nutrient']:20s} "
              f"[{r['source_status']:16s}] promote={r['promote_eligible']:5s} "
              f"({r['products_with_signal']}/{r['products_checked']})")
    from collections import Counter
    sc = Counter(r["source_status"] for r in rows)
    print("\n  status:", dict(sc))
    cand_confirmed = sorted({r["candidate_id"] for r in rows if r["source_status"] == "source_confirmed"})
    print("  source_confirmed 후보(승격검토 대상):", ", ".join(cand_confirmed) or "없음")
    if write:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)}  ({len(rows)} rows)")
    else:
        print("\n(--no-write)")
    print("\nVERIFY A-TIER RELATION SOURCES: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
