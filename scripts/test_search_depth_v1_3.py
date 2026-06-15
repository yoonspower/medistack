#!/usr/bin/env python3
"""test_search_depth_v1_3.py
search_itemseqs 검색 깊이 정책 회귀 테스트(결정적·네트워크 0).

FakeOpener 가 max_pages 에 따라 통제된 SearchRow 를 반환한다(실 NEDRUG 무접촉).
검증:
  1) 프레드니솔론 substring 지배 → 깊은검색 fallback 이 소론도정(199602982) 정확 주성분만 채택.
     - 메틸/메칠프레드니솔론(부분문자열 동명) 오채택 금지.
     - 수출용/원료만 보고 종료 금지.
  2) 미유통(부메타니드 등) → 0건이면 ([], no_domestic...) + 깊은검색 호출 안 함.
  3) 하이드로코르티손 → 외용/비경구만이면 깊은검색에도 정확 경구 단일 0 → [].
  4) PM-ready 비교군(메틸프레드니솔론·아세타졸아미드·아조세미드) → 얕은검색 정확 주성분 있으면
     기존 itemSeq 유지 + 깊은검색 호출 안 함(불필요한 깊은검색 방지).
사용: python3 scripts/test_search_depth_v1_3.py · 종료코드 0 PASS / 1 FAIL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from medistack_sdk.nedrug_client import SearchRow
import verify_factory_sources_v1_2 as vfs

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def row(seq, name, ingr, finished="완제의약품", cancel="정상"):
    return SearchRow(item_seq=seq, item_name=name, ingr_name=ingr, finished=finished, status_cancel=cancel)


class FakeOpener:
    """max_pages>2 면 deep, 아니면 shallow 반환. 호출 max_pages 기록(비용 검증)."""
    def __init__(self, shallow, deep=None):
        self.shallow = shallow
        self.deep = shallow if deep is None else deep
        self.calls = []

    def search_drug(self, ingredient, max_pages=2):
        self.calls.append(max_pages)
        return list(self.deep) if max_pages > 2 else list(self.shallow)


def test_prednisolone_deep_fallback():
    # 얕은검색: 메틸프레드니솔론(메틸) 지배 + 수출용 프레드니솔론 + 원료. 정확 경구 단일 0.
    shallow = [
        row("201309846", "니소론엠정(메틸프레드니솔론)", "메틸프레드니솔론"),
        row("201900631", "다솔론정(메틸프레드니솔론)", "메틸프레드니솔론"),
        row("201102314", "대한뉴팜프레드니솔론정5mg(프레드니솔론)(수출용)", "프레드니솔론"),
        row("198501702", "대신프레드니솔론(원료)", "프레드니솔론", finished="원료의약품"),
    ]
    # 깊은검색(p7+): 소론도정(정확 주성분) + 프론드정(메칠프레드니솔론=부분문자열 동명, 함정).
    deep = shallow + [
        row("199602982", "소론도정(프레드니솔론)", "프레드니솔론"),
        row("200500854", "프론드정(메칠프레드니솔론)", "메칠프레드니솔론"),
    ]
    op = FakeOpener(shallow, deep)
    picks, reason = vfs.search_itemseqs(op, "프레드니솔론", exclude_ingr="메틸프레드니솔론",
                                        max_n=2, max_pages=2, deep_max_pages=20)
    seqs = [s for s, _, _ in picks]
    ck(reason == "ok_deep_exact", f"[프레드니솔론] reason != ok_deep_exact ({reason})")
    ck("199602982" in seqs, f"[프레드니솔론] 소론도정(199602982) 미채택: {seqs}")
    ck("200500854" not in seqs, f"[프레드니솔론] 메칠프레드니솔론(프론드정) 오채택(부분문자열 동명): {seqs}")
    ck(all(ingr == "프레드니솔론" for _, _, ingr in picks), f"[프레드니솔론] 정확 주성분 외 채택: {picks}")
    ck("201102314" not in seqs, f"[프레드니솔론] 수출용 채택됨: {seqs}")
    ck("198501702" not in seqs, f"[프레드니솔론] 원료 채택됨: {seqs}")
    ck(any(mp > 2 for mp in op.calls), f"[프레드니솔론] 깊은검색 미수행(calls={op.calls})")


def test_not_marketed_no_deep():
    op = FakeOpener([], [])
    picks, reason = vfs.search_itemseqs(op, "부메타니드", max_n=2, max_pages=2, deep_max_pages=20)
    ck(picks == [], f"[부메타니드] 미유통인데 픽 발생: {picks}")
    ck(reason == "no_domestic_single_oral_product", f"[부메타니드] reason != no_domestic ({reason})")
    ck(all(mp <= 2 for mp in op.calls), f"[부메타니드] 0건인데 깊은검색 호출(calls={op.calls})")


def test_hydrocortisone_topical_only():
    # 외용/비경구만(정확 경구 단일 없음). 부분문자열 동명(아세테이트)이 있으면 깊은검색은 돌되 exact 0.
    shallow = [
        row("100000001", "하이드로코르티손크림", "하이드로코르티손"),                  # nonoral
        row("100000002", "락티손로션(하이드로코르티손아세테이트)", "하이드로코르티손아세테이트"),  # nonoral + 동명
    ]
    deep = shallow + [row("100000003", "코티솜연고(하이드로코르티손)", "하이드로코르티손")]  # 여전히 nonoral
    op = FakeOpener(shallow, deep)
    picks, reason = vfs.search_itemseqs(op, "하이드로코르티손", max_n=2, max_pages=2, deep_max_pages=20)
    ck(picks == [], f"[하이드로코르티손] 외용만인데 픽 발생: {picks}")
    ck(reason == "no_domestic_single_oral_product", f"[하이드로코르티손] reason != no_domestic ({reason})")


def test_pmready_shallow_exact_no_deep():
    cases = {
        "메틸프레드니솔론": [row("199701131", "메드롤정4밀리그람(메틸프레드니솔론)", "메틸프레드니솔론"),
                       row("199800324", "메틴정(메틸프레드니솔론)", "메틸프레드니솔론")],
        "아세타졸아미드": [row("201403403", "다이아막스정(아세타졸아미드)", "아세타졸아미드")],
        "아조세미드": [row("199001306", "유리논정(아조세미드)", "아조세미드")],
    }
    for ing, shallow in cases.items():
        op = FakeOpener(shallow, shallow + [row("999999999", f"가짜{ing}원료", ing, finished="원료의약품")])
        excl = "메틸프레드니솔론" if ing == "프레드니솔론" else None
        picks, reason = vfs.search_itemseqs(op, ing, exclude_ingr=excl, max_n=2, max_pages=2, deep_max_pages=20)
        seqs = [s for s, _, _ in picks]
        ck(reason == "ok", f"[{ing}] reason != ok ({reason})")
        ck(len(picks) >= 1, f"[{ing}] 얕은검색 정확 주성분 미채택: {picks}")
        ck(all(ingr == ing for _, _, ingr in picks), f"[{ing}] 비-정확 주성분 채택: {picks}")
        ck(all(mp <= 2 for mp in op.calls), f"[{ing}] 얕은검색 정확 후보 있는데 깊은검색 호출(calls={op.calls})")
        for s in [r.item_seq for r in shallow]:
            ck(s in seqs, f"[{ing}] 기대 itemSeq {s} 누락: {seqs}")


def main():
    test_prednisolone_deep_fallback()
    test_not_marketed_no_deep()
    test_hydrocortisone_topical_only()
    test_pmready_shallow_exact_no_deep()
    if fails:
        print("FAIL — search depth 회귀:")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS — search depth 회귀 4종(프레드니솔론 deep fallback·미유통 no-deep·"
          "하이드로코르티손 topical·PM-ready shallow-exact no-deep) 전건 통과.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
