#!/usr/bin/env python3
"""
test_nedrug_client_dryrun.py — NedrugClient **dry-run(네트워크 0) 테스트**.

검증: offline+fixtures 표준화 · cache · raw 저장 · 호출 log · retry/timeout fail-soft · 네트워크 미발생.
실 nedrug 에 접속하지 않는다(전부 fixture/주입 opener). CI/smoke 로 실행 가능.

사용: python3 medistack_sdk/test_nedrug_client_dryrun.py
종료코드: 0 PASS / 1 FAIL.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
from medistack_sdk import NedrugClient  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
_fails = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fails.append(name)


def _client(tmp, **kw):
    return NedrugClient(offline=True, fixtures_dir=FIX,
                        cache_dir=os.path.join(tmp, "cache"),
                        raw_dir=os.path.join(tmp, "raw"),
                        log_path=os.path.join(tmp, "calls.jsonl"),
                        clock=lambda: 0.0, **kw)


def test_normalize(tmp):
    print("· normalize(offline+fixtures)")
    c = _client(tmp)
    rows = c.search_drug("프레드니솔론")
    check("search 1행 표준화", len(rows) == 1, str(rows))
    r = rows[0]
    check("search 필드(seq/name/ingr/완제/정상)",
          r.item_seq == "100001" and r.item_name.startswith("프레드니솔론정")
          and r.ingr_name == "프레드니솔론" and r.finished == "완제" and r.status_cancel == "정상")
    d = c.get_item_detail("100001")
    check("detail title 추출", d.title == "프레드니솔론정5밀리그램", d.title)
    check("detail ingredients 추출", d.ingredients == ["프레드니솔론"], str(d.ingredients))
    check("detail label_text 저칼륨혈증 포함", "저칼륨혈증" in d.label_text)
    lbl, url = c.fetch_label("100005")
    check("fetch_label antacid 원문", "제산제" in lbl and "간격" in lbl)
    check("fetch_label url=getItemDetail", "getItemDetail?itemSeq=100005" in url)
    check("미존재 검색 → 빈 결과(offline_miss)", c.search_drug("존재하지않는성분xyz") == [])


def test_cache_raw(tmp):
    print("· cache + raw 저장")
    c = _client(tmp)
    c.get_item_detail("100001")
    n_net0, n_cache0 = c.stats["network"], c.stats["cache"]
    c.get_item_detail("100001")  # 2nd → cache
    check("2회차 동일 조회 = cache hit", c.stats["cache"] == n_cache0 + 1)
    check("offline 에서 network 호출 0", c.stats["network"] == 0)
    check("raw 원문 파일 저장됨(offline namespace)",
          os.path.exists(os.path.join(tmp, "raw", "offline", "detail_100001.html")))
    check("cache 파일 생성됨(offline namespace)",
          os.path.exists(os.path.join(tmp, "cache", "offline", "detail_100001.html")))


def test_log(tmp):
    print("· 호출 log(JSONL)")
    c = _client(tmp)
    c.search_drug("아세타졸아미드")
    c.get_item_detail("100002")
    c.get_item_detail("999999")  # offline_miss
    with open(os.path.join(tmp, "calls.jsonl"), encoding="utf-8") as f:
        recs = [json.loads(x) for x in f if x.strip()]
    modes = [r["mode"] for r in recs]
    check("log 라인 생성", len(recs) >= 3, str(modes))
    check("log mode∈{fixture,cache,offline_miss}", set(modes) <= {"fixture", "cache", "offline_miss"}, str(modes))
    check("log 각 라인 url/kind/ts 포함", all({"url", "kind", "ts", "status"} <= set(r) for r in recs))
    check("offline_miss 기록됨", "offline_miss" in modes)


class _RaisingOpener:
    def __init__(self):
        self.calls = 0

    def open(self, req, timeout=None):
        self.calls += 1
        raise OSError("simulated network down")


def test_retry_failsoft(tmp):
    print("· retry/timeout fail-soft(주입 opener, 네트워크 미발생)")
    c = NedrugClient(offline=False, cache_dir=os.path.join(tmp, "c2"),
                     raw_dir=os.path.join(tmp, "r2"), log_path=os.path.join(tmp, "l2.jsonl"),
                     max_retries=3, backoff=0.0, min_interval=0.0, clock=lambda: 0.0)
    fake = _RaisingOpener()
    c._opener = fake  # 네트워크 대신 실패 주입
    rows = c.search_drug("무엇이든")  # page1 실패 → 빈 결과
    check("network 실패 → 예외 전파 안 함(fail-soft)", rows == [])
    check("max_retries(3)회 시도", fake.calls == 3, f"calls={fake.calls}")
    check("error 통계 증가", c.stats["error"] >= 1)
    with open(os.path.join(tmp, "l2.jsonl"), encoding="utf-8") as f:
        recs = [json.loads(x) for x in f if x.strip()]
    check("error 로그에 attempts/error 기록", any(r["mode"] == "error" and r.get("attempts") == 3 for r in recs))


class _FakeOpener:
    """주입용 가짜 opener — 실 네트워크 대신 고정 본문 반환(실 소켓 0, 네트워크 미발생)."""
    def __init__(self, body):
        self._body = body.encode("utf-8")
        self.calls = 0

    def open(self, req, timeout=None):
        self.calls += 1
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


# fixture(offline)·실데이터(online)를 명확히 구분하려고 detail_100001 키를 양쪽이 재사용한다.
_REAL_HTML_A = ("<html><h1>온라인리얼_프레드니솔론</h1><body>실데이터 라벨 본문 — "
                "상호작용 주의 안내(fixture 아님)</body></html>")
_REAL_HTML_B = "<html><h1>온라인전용_라벨</h1><body>오직 네트워크에서만 온 본문</body></html>"


def test_offline_then_online_no_fixture_contamination(tmp):
    print("· 캐시 오염 방지 ①: offline 후 online 이 fixture cache-hit 안 함")
    base_cache, base_raw = os.path.join(tmp, "cache"), os.path.join(tmp, "raw")
    log = os.path.join(tmp, "calls.jsonl")
    # 1) offline 런: fixture 를 (offline) 캐시 namespace 에 적재
    off = NedrugClient(offline=True, fixtures_dir=FIX, cache_dir=base_cache,
                       raw_dir=base_raw, log_path=log, clock=lambda: 0.0)
    d_off = off.get_item_detail("100001")
    check("offline 결과 = fixture(저칼륨혈증)", "저칼륨혈증" in d_off.label_text, d_off.label_text[:40])
    # 2) online 런: 같은 base cache_dir + 주입 opener 가 다른 '실' 본문 반환(같은 key 100001)
    on = NedrugClient(offline=False, cache_dir=base_cache, raw_dir=base_raw, log_path=log,
                      min_interval=0.0, backoff=0.0, clock=lambda: 0.0)
    on._opener = _FakeOpener(_REAL_HTML_A)
    net0, cache0 = on.stats["network"], on.stats["cache"]
    d_on = on.get_item_detail("100001")
    check("online 이 fixture 를 cache-hit 하지 않음(network 경유)",
          on.stats["network"] == net0 + 1 and on.stats["cache"] == cache0,
          f"net={on.stats['network']} cache={on.stats['cache']}")
    check("online 결과 = 실데이터(fixture 오염 아님)",
          "온라인리얼_프레드니솔론" in d_on.title and "저칼륨혈증" not in d_on.label_text, d_on.title)
    check("offline·online 캐시가 mode 별 dir 분리",
          os.path.exists(os.path.join(base_cache, "offline", "detail_100001.html"))
          and os.path.exists(os.path.join(base_cache, "online", "detail_100001.html")))


def test_online_then_offline_separation(tmp):
    print("· 캐시 오염 방지 ②: online 후 offline 이 real cache 를 읽지 않음")
    base_cache, base_raw = os.path.join(tmp, "cache"), os.path.join(tmp, "raw")
    log = os.path.join(tmp, "calls.jsonl")
    # 1) online 런: 주입 opener 의 '실' 본문을 (online) 캐시 namespace 에 적재
    on = NedrugClient(offline=False, cache_dir=base_cache, raw_dir=base_raw, log_path=log,
                      min_interval=0.0, backoff=0.0, clock=lambda: 0.0)
    on._opener = _FakeOpener(_REAL_HTML_B)
    on.get_item_detail("100001")
    # 2) offline 런: 같은 base cache_dir → online 실캐시 읽지 말고 fixture 사용해야
    off = NedrugClient(offline=True, fixtures_dir=FIX, cache_dir=base_cache,
                       raw_dir=base_raw, log_path=log, clock=lambda: 0.0)
    d_off = off.get_item_detail("100001")
    check("offline 이 online real cache 를 읽지 않음",
          "온라인전용_라벨" not in (d_off.title + d_off.label_text), d_off.title)
    check("offline 결과 = fixture(저칼륨혈증)", "저칼륨혈증" in d_off.label_text)
    check("offline network 0 유지", off.stats["network"] == 0)


def main():
    print("=== NedrugClient dry-run test (네트워크 0) ===")
    with tempfile.TemporaryDirectory() as tmp:
        test_normalize(os.path.join(tmp, "a"))
        test_cache_raw(os.path.join(tmp, "b"))
        test_log(os.path.join(tmp, "c"))
        test_retry_failsoft(os.path.join(tmp, "d"))
        test_offline_then_online_no_fixture_contamination(os.path.join(tmp, "e"))
        test_online_then_offline_separation(os.path.join(tmp, "f"))
    print("=" * 56)
    if _fails:
        print(f"RESULT: FAIL — {len(_fails)}건: {_fails}")
        return 1
    print("RESULT: PASS — SDK dry-run 전부 통과(네트워크 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
