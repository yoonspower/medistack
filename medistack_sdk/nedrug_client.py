#!/usr/bin/env python3
"""
nedrug_client.py — 식약처 nedrug 조회 SDK (MediStack 외부 데이터 단일 게이트웨이).

harvester bot / source checker / coverage-queue 스크립트는 nedrug 를 직접 호출하지 않고
**반드시 이 클라이언트를 통해서만** 조회한다.

공개 API:
  NedrugClient.search_drug(ingredient, max_pages=2)  -> list[SearchRow]   (성분 → 후보 품목)
  NedrugClient.get_item_detail(item_seq)             -> ItemDetail        (itemSeq → 표준화 상세)
  NedrugClient.fetch_label(item_seq)                 -> (label_text, url)  (detector 용 라벨 원문)

SDK 가 내부에서 처리하는 것(이 파일 밖으로 새지 않게):
  - retry / timeout / rate limit / cache / raw response 저장 / 호출 logging / schema normalize
  - offline + fixtures 모드(네트워크 0, 결정론적 dry-run/test)

⚠️ 금지(설계 불변):
  - SDK 는 source_confirmed 를 **최종 확정하지 않는다**(found/quote 같은 원자료만 제공, 판정은 게이트가).
  - SDK 는 relation 을 만들지 않고, live export/full index/alias 를 수정하지 않으며, 배포를 수행하지 않는다.
  - SDK 가 쓰는 경로는 cache_dir / raw_dir / log_path 뿐 — 전부 호출자가 지정하는 작업/큐 디렉토리.

종료/예외: 네트워크 실패는 retry 후 빈 결과로 떨어지고(로그에 mode=error 기록), 예외를 호출자에게
전파하지 않는다(파이프라인이 needs_review 로 분류하게). raise 하지 않는 fail-soft.
"""
from __future__ import annotations

import html as htmllib
import http.cookiejar
import json
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict

# ----------------- 엔드포인트 (이 파일이 유일한 정의 지점) -----------------
SEARCH_URL = "https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1={}&page={}"
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"
DEFAULT_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# searchDrug 결과 파싱(verify_factory_sources / collect_nedrug_alias 의 검증된 패턴 승계 — 이제 SDK 가 소유).
_ANCHOR_RE = re.compile(r'getItemDetail\?itemSeq=(\d+)"[^>]*>\s*([^<]+?)\s*</a>')
_TITLE_RE = re.compile(r'<h1[^>]*>\s*([^<]+?)\s*</h1>')
_INGR_RE = re.compile(r'"?ingrName"?\s*[:=]\s*"([^"]+)"')


@dataclass
class SearchRow:
    """searchDrug 결과 1행(표준화)."""
    item_seq: str
    item_name: str
    ingr_name: str = ""
    finished: str = ""        # 완제/원료구분
    status_cancel: str = ""   # 취소/취하구분


@dataclass
class ItemDetail:
    """getItemDetail 표준화 상세."""
    item_seq: str
    title: str
    ingredients: list = field(default_factory=list)  # distinct 주성분
    label_text: str = ""                              # 태그제거·정규화 라벨 원문(detector 입력)
    url: str = ""
    raw_len: int = 0


def _slug(s: str) -> str:
    """파일명 안전 슬러그(한글 보존)."""
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", (s or "").strip()).strip("_") or "x"


def _strip_html(raw: str) -> str:
    # script/style 내용 제거(JS/CSS 가 라벨 본문으로 새지 않게) 후 태그 제거.
    raw = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", raw)
    t = re.sub(r"<[^>]+>", " ", raw)
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def _field(row: str, label: str) -> str:
    """상세/검색 row 에서 <span class="s-th">{label}</span> 값 추출."""
    m = re.search(re.escape(f'<span class="s-th">{label}</span>')
                  + r'(.*?)(?=<span class="s-th">|</td>|</tr>)', row, re.S)
    if not m:
        return ""
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split()).strip()


class NedrugClient:
    """식약처 nedrug 조회 SDK. 모든 외부 조회의 단일 통로."""

    def __init__(self, *, cache_dir=None, raw_dir=None, log_path=None,
                 timeout=30, max_retries=3, backoff=1.5, min_interval=0.7,
                 offline=False, fixtures_dir=None, user_agent=DEFAULT_UA, clock=None):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.min_interval = min_interval
        self.offline = offline
        self.fixtures_dir = fixtures_dir
        self.user_agent = user_agent
        self._clock = clock or time.time
        self._sleep = (lambda s: None) if (offline or clock) else time.sleep
        self._last_call = 0.0
        self._opener = None  # lazy
        self.cache_dir = cache_dir
        self.raw_dir = raw_dir
        self.log_path = log_path
        for d in (cache_dir, raw_dir):
            if d:
                os.makedirs(d, exist_ok=True)
        if log_path:
            os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        # 호출 통계(호출자 리포트용)
        self.stats = {"network": 0, "cache": 0, "fixture": 0, "offline_miss": 0, "error": 0}

    # ----------------- 공개 API -----------------
    def search_drug(self, ingredient, *, max_pages=2):
        """성분명 → 후보 품목 표준화 목록(itemSeq 오름차순 dedup). 판정 없음."""
        rows, seen = [], set()
        for page in range(1, max_pages + 1):
            url = SEARCH_URL.format(urllib.parse.quote(ingredient), page)
            raw = self._get(url, kind="search", key=f"{_slug(ingredient)}_p{page}")
            if not raw:
                break
            page_rows = self._parse_search(raw)
            if not page_rows:
                break
            for r in page_rows:
                if r.item_seq in seen:
                    continue
                seen.add(r.item_seq)
                rows.append(r)
        rows.sort(key=lambda r: int(r.item_seq) if r.item_seq.isdigit() else 0)
        return rows

    def get_item_detail(self, item_seq):
        """itemSeq → 표준화 상세(title/ingredients/label_text). 판정 없음."""
        url = DETAIL_URL.format(item_seq)
        raw = self._get(url, kind="detail", key=str(item_seq))
        label = _strip_html(raw) if raw else ""
        return ItemDetail(
            item_seq=str(item_seq),
            title=self._parse_title(raw),
            ingredients=self._parse_ingredients(raw),
            label_text=label,
            url=url,
            raw_len=len(raw or ""),
        )

    def fetch_label(self, item_seq):
        """detector 용 라벨 원문 + url. (verify_factory_sources.fetch_detail 호환 시그니처)."""
        d = self.get_item_detail(item_seq)
        return d.label_text, d.url

    # ----------------- 표준화(normalize) -----------------
    def _parse_search(self, html_text):
        rows = []
        for chunk in re.split(r"<tr[ >]", html_text):
            if "getItemDetail?itemSeq=" not in chunk:
                continue
            m = _ANCHOR_RE.search(chunk)
            if not m:
                continue
            rows.append(SearchRow(
                item_seq=m.group(1),
                item_name=htmllib.unescape(m.group(2)).strip(),
                ingr_name=_field(chunk, "주성분"),
                finished=_field(chunk, "완제/원료구분"),
                status_cancel=_field(chunk, "취소/취하구분"),
            ))
        return rows

    @staticmethod
    def _parse_title(raw):
        if not raw:
            return ""
        m = _TITLE_RE.search(raw)
        return htmllib.unescape(m.group(1)).strip() if m else ""

    @staticmethod
    def _parse_ingredients(raw):
        if not raw:
            return []
        out, seen = [], set()
        for m in _INGR_RE.finditer(raw):
            v = htmllib.unescape(m.group(1)).strip()
            if v and v not in seen:
                seen.add(v)
                out.append(v)
        return sorted(out)

    # ----------------- 조회 코어(cache / raw / log / retry / ratelimit / offline) -----------------
    def _get(self, url, *, kind, key):
        """raw HTML 텍스트 반환(실패/미존재 시 '')."""
        cache_file = os.path.join(self.cache_dir, f"{kind}_{key}.html") if self.cache_dir else None
        # 1) cache hit
        if cache_file and os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as f:
                raw = f.read()
            self._log(kind=kind, key=key, url=url, mode="cache", status="ok", nbytes=len(raw), attempts=0, elapsed_ms=0)
            self.stats["cache"] += 1
            return raw
        # 2) offline → fixture only
        if self.offline:
            raw = self._read_fixture(kind, key)
            if raw is not None:
                self._save_raw(kind, key, raw)
                if cache_file:
                    self._write(cache_file, raw)
                self._log(kind=kind, key=key, url=url, mode="fixture", status="ok", nbytes=len(raw), attempts=0, elapsed_ms=0)
                self.stats["fixture"] += 1
                return raw
            self._log(kind=kind, key=key, url=url, mode="offline_miss", status="empty", nbytes=0, attempts=0, elapsed_ms=0)
            self.stats["offline_miss"] += 1
            return ""
        # 3) network (retry + timeout + rate limit)
        raw, attempts, elapsed_ms, err = self._network(url)
        if raw:
            self._save_raw(kind, key, raw)
            if cache_file:
                self._write(cache_file, raw)
            self._log(kind=kind, key=key, url=url, mode="network", status="ok", nbytes=len(raw), attempts=attempts, elapsed_ms=elapsed_ms)
            self.stats["network"] += 1
            return raw
        self._log(kind=kind, key=key, url=url, mode="error", status="error", nbytes=0, attempts=attempts, elapsed_ms=elapsed_ms, error=err)
        self.stats["error"] += 1
        return ""

    def _network(self, url):
        if self._opener is None:
            self._opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        # rate limit
        wait = self.min_interval - (self._clock() - self._last_call)
        if wait > 0:
            self._sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent,
                                                   "Accept-Language": "ko,en;q=0.8"})
        start = self._clock()
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with self._opener.open(req, timeout=self.timeout) as r:
                    raw = r.read().decode("utf-8", "replace")
                self._last_call = self._clock()
                return raw, attempt, int((self._clock() - start) * 1000), None
            except Exception as e:  # noqa: BLE001 — 네트워크/HTTP 모두 fail-soft
                last_err = f"{type(e).__name__}: {e}"
                self._sleep(self.backoff * attempt)
        self._last_call = self._clock()
        return "", self.max_retries, int((self._clock() - start) * 1000), last_err

    # ----------------- 보조 -----------------
    def _read_fixture(self, kind, key):
        if not self.fixtures_dir:
            return None
        path = os.path.join(self.fixtures_dir, f"{kind}_{key}.html")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        return None

    def _save_raw(self, kind, key, raw):
        if self.raw_dir:
            self._write(os.path.join(self.raw_dir, f"{kind}_{key}.html"), raw)

    @staticmethod
    def _write(path, text):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def _log(self, **rec):
        rec.setdefault("ts", round(self._clock(), 3))
        if not self.log_path:
            return
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
