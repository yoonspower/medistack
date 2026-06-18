#!/usr/bin/env python3
"""
nedrug_online_client_v1_7.py — 식약처 nedrug **online** 조회 클라이언트(검증된 직접 HTTP).

v1.6 병목 (a) online fetch 미작동을 해소한다. 사실: 기존 medistack_sdk.NedrugClient 는
online 으로 정상 동작하나(검색 200·상세 302→getItemDetailCache redirect 자동 추종), v1.6
orchestrator 가 SDK 를 harvest 경로에 **배선하지 않고** static universe 만 열거해 신규 0건이었다.
이 클라이언트는 SDK 를 과제 사양 설정으로 래핑해 단순 API 를 제공한다.

검증된 엔드포인트(2026-06-18 curl 확인):
  검색: GET https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1=<성분>&page=N   → HTML, itemSeq 파싱
  상세: GET https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=<seq>          → 302 → Cache(HTML ~300KB)
  data.go.kr DrbEasyDrugInfoService 는 serviceKey 없으면 401 → 의존 금지(이 클라이언트는 미사용).

과제 사양: polite delay ≥1s · timeout 25s · 재시도 1회(=2 attempts) · UA 고정. offline/fixtures 지원(test).

공개 API:
  NedrugOnlineClient(offline=False, fixtures_dir=None, cache_dir=None, ...)
  .search_itemseqs(name, max_pages=2)  -> list[str]      # itemSeq 문자열(오름차순 dedup)
  .search_rows(name, max_pages=2)      -> list[SearchRow]# item_seq/item_name/ingr_name/finished/status_cancel
  .fetch_detail(item_seq)              -> str            # getItemDetail raw HTML(태그 보존·302 추종)
  .stats                               -> dict           # network/cache/fixture/error 카운트
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from medistack_sdk.nedrug_client import NedrugClient, SearchRow  # noqa: E402

# 과제 사양 UA(검증 시 사용한 값과 동일 계열).
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


class NedrugOnlineClient:
    """nedrug online 조회 단순 클라이언트(SDK 래핑 + 과제 사양 설정)."""

    def __init__(self, *, offline=False, fixtures_dir=None, cache_dir=None, raw_dir=None,
                 log_path=None, min_interval=1.0, timeout=25, max_retries=2, clock=None):
        # max_retries=2 → 2 attempts = 재시도 1회. min_interval=1.0 → polite delay ≥1s.
        self._c = NedrugClient(
            offline=offline, fixtures_dir=fixtures_dir, cache_dir=cache_dir, raw_dir=raw_dir,
            log_path=log_path, min_interval=min_interval, timeout=timeout, max_retries=max_retries,
            user_agent=USER_AGENT, clock=clock)

    @property
    def stats(self):
        return self._c.stats

    def search_rows(self, name, *, max_pages=2):
        """성분/품목명 → 표준화 search row(itemSeq 오름차순 dedup). 판정 없음."""
        return self._c.search_drug(name, max_pages=max_pages)

    def search_itemseqs(self, name, *, max_pages=2):
        """성분/품목명 → itemSeq 문자열 목록."""
        return [r.item_seq for r in self.search_rows(name, max_pages=max_pages)]

    def fetch_detail(self, item_seq):
        """itemSeq → getItemDetail raw HTML(태그 보존). 302 자동 추종. 실패 시 ''."""
        return self._c.get_detail_html(item_seq)


# 간단 CLI 진단(직접 실행 시): online 도달 + 1건 상세 길이.
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "리세드론산"
    c = NedrugOnlineClient()
    rows = c.search_rows(name, max_pages=1)
    print(f"search '{name}': {len(rows)} rows")
    for r in rows[:5]:
        print(" ", r.item_seq, r.item_name, "|", r.ingr_name, "|", r.finished, r.status_cancel)
    if rows:
        html = c.fetch_detail(rows[0].item_seq)
        print(f"detail {rows[0].item_seq}: {len(html)} bytes")
    print("stats:", c.stats)
