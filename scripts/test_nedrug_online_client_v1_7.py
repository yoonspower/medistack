#!/usr/bin/env python3
"""
test_nedrug_online_client_v1_7.py — nedrug online client(v1.7) 테스트.

기본: **offline·fixtures** 모드(네트워크 0·결정론적) — search/detail fixture 로 API 계약 검증.
live smoke: 환경변수 NEDRUG_LIVE=1 일 때만 실제 nedrug 도달(검색 200·상세 HTML) 확인.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FX = os.path.join(ROOT, "tests", "fixtures", "nedrug")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    print("=== nedrug_online_client v1.7 (offline·fixtures) ===")
    mod = load("noc", os.path.join(HERE, "nedrug_online_client_v1_7.py"))
    c = mod.NedrugOnlineClient(offline=True, fixtures_dir=FX)

    # 1) search_itemseqs (fixture: search_리세드론산_p1.html)
    seqs = c.search_itemseqs("리세드론산", max_pages=1)
    ck(len(seqs) >= 10, f"search_itemseqs 리세드론산 ≥10건(got {len(seqs)})")
    ck(all(s.isdigit() for s in seqs), "itemSeq 전건 숫자 문자열")
    ck(seqs == sorted(seqs, key=int), "itemSeq 오름차순 정렬")

    # 2) search_rows 표준화 필드
    rows = c.search_rows("리세드론산", max_pages=1)
    ck(rows and all(r.item_name for r in rows), "search_rows item_name 채워짐")
    ck(any(r.ingr_name for r in rows), "search_rows ingr_name 일부 채워짐")

    # 3) fetch_detail raw HTML(태그 보존 — 섹션 마커 존재)
    html = c.fetch_detail("201903166")
    ck(len(html) > 100000, f"fetch_detail raw HTML 수신(got {len(html)} bytes)")
    ck('class="title"' in html or "상호작용" in html, "detail HTML 에 섹션 마커 존재(태그 보존)")
    ck('흡수를 방해' in html, "detail HTML 에 라벨 원문 보존")

    # 4) 설정값(과제 사양): min_interval≥1·timeout 25·재시도 1회(=2 attempts)·UA 고정
    ck(c._c.min_interval >= 1.0, "polite delay ≥1s")
    ck(c._c.timeout == 25, "timeout 25s")
    ck(c._c.max_retries == 2, "재시도 1회(max_retries=2)")
    ck("Mozilla/5.0" in mod.USER_AGENT, "UA 고정(Mozilla/5.0)")

    # 5) offline 은 네트워크 0(fixture/cache 만)
    ck(c.stats["network"] == 0, "offline: network 호출 0")

    # 6) live smoke (옵트인)
    if os.environ.get("NEDRUG_LIVE") == "1":
        print("--- LIVE smoke (NEDRUG_LIVE=1) ---")
        lc = mod.NedrugOnlineClient()
        lseqs = lc.search_itemseqs("리세드론산", max_pages=1)
        ck(len(lseqs) >= 5, f"LIVE search ≥5건(got {len(lseqs)})")
        lh = lc.fetch_detail(lseqs[0]) if lseqs else ""
        ck(len(lh) > 50000, f"LIVE detail HTML(got {len(lh)} bytes)")
    else:
        print("  SKIP live smoke (set NEDRUG_LIVE=1 to enable)")

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — search/detail 계약·설정·offline 네트워크 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
