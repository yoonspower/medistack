#!/usr/bin/env python3
"""test_search_depth_v1_3.py
search_itemseqs 검색 깊이 정책 회귀 테스트(결정적·네트워크 0).

FakeOpener 가 max_pages 에 따라 통제된 SearchRow 를 반환한다(실 NEDRUG 무접촉).
검증:
  1) 프레드니솔론 substring 지배 → 깊은검색 fallback 이 소론도정(199602982) 정확 주성분만 채택.
     - 메틸/메칠프레드니솔론(부분문자열 동명) 오채택 금지.
     - 수출용/원료만 보고 종료 금지.
  2) 미유통(부메타니드 등) → 0건이면 ([], no_domestic...) + 깊은검색 호출 안 함.
  3) 하이드로코르티손 → 외용/비경구만(정확 경구 단일 0) + 접미사형(아세테이트) superset 뿐 →
     깊은검색 미발동(연속명 접두사 지배 아님) + [].
  4) PM-ready 비교군(메틸프레드니솔론·아세타졸아미드·아조세미드) → 얕은검색 정확 주성분 있으면
     기존 itemSeq 유지 + 깊은검색 호출 안 함(불필요한 깊은검색 방지).
  5) 검색깊이 하드닝: 깊은검색은 **다른 약물의 연속 명칭**(접두사 확장, 예: 에스오메프라졸이
     오메프라졸을 지배)에서만 발동. 염/수화물(접미사형 X나트륨)·복합제(Y/X)는 미발동 —
     exact_only deep 로 복구 불가하므로 호출 자체를 피한다(deep 호출 과다 방지).
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
    # 외용/비경구만(정확 경구 단일 없음). 동명은 접미사형 아세테이트(startswith)뿐 → 연속명 접두사
    # 지배 아님 → 깊은검색 미발동(외용 희소 문제는 substring 지배가 아니라 별개).
    shallow = [
        row("100000001", "하이드로코르티손크림", "하이드로코르티손"),                  # nonoral
        row("100000002", "락티손로션(하이드로코르티손아세테이트)", "하이드로코르티손아세테이트"),  # nonoral + 접미사 동명
    ]
    deep = shallow + [row("100000003", "코티솜연고(하이드로코르티손)", "하이드로코르티손")]  # 여전히 nonoral
    op = FakeOpener(shallow, deep)
    picks, reason = vfs.search_itemseqs(op, "하이드로코르티손", max_n=2, max_pages=2, deep_max_pages=20)
    ck(picks == [], f"[하이드로코르티손] 외용만인데 픽 발생: {picks}")
    ck(reason == "no_domestic_single_oral_product", f"[하이드로코르티손] reason != no_domestic ({reason})")
    ck(all(mp <= 2 for mp in op.calls), f"[하이드로코르티손] 접미사형뿐인데 깊은검색 호출(calls={op.calls})")


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


def test_hardening_prefix_only_deep():
    """검색깊이 하드닝: 연속명 접두사(다른 약물)만 깊은검색 발동. 염(접미사)·복합제는 미발동."""
    # (a) 염/수화물(접미사형): X나트륨 경구만 → substring 픽 채택(reason ok) + 깊은검색 미발동.
    salt_shallow = [row("300000001", "파리에트정10밀리그람(라베프라졸나트륨)", "라베프라졸나트륨"),
                    row("300000002", "라비셋정(라베프라졸나트륨)", "라베프라졸나트륨")]
    op = FakeOpener(salt_shallow, salt_shallow + [row("399999999", "딥라베프라졸정", "라베프라졸")])
    picks, reason = vfs.search_itemseqs(op, "라베프라졸", max_n=2, max_pages=2, deep_max_pages=20)
    ck(reason == "ok", f"[라베프라졸 salt] reason != ok ({reason})")
    ck([s for s, _, _ in picks] == ["300000001", "300000002"], f"[라베프라졸 salt] 염 경구 픽 누락: {picks}")
    ck(all(mp <= 2 for mp in op.calls), f"[라베프라졸 salt] 접미사형인데 깊은검색 호출(calls={op.calls})")

    # (b) 복합제(Y/X): '/' 구분 동거성분만 → 단일성분 0 + 깊은검색 미발동([], no_domestic).
    combo_shallow = [row("310000001", "나프록센에스오메프라졸정", "나프록센/에스오메프라졸"),
                     row("310000002", "콤비정(침강탄산칼슘/란소프라졸)", "침강탄산칼슘/란소프라졸")]
    op2 = FakeOpener(combo_shallow, combo_shallow + [row("319999999", "딥란소프라졸정", "란소프라졸")])
    picks2, reason2 = vfs.search_itemseqs(op2, "란소프라졸", max_n=2, max_pages=2, deep_max_pages=20)
    ck(picks2 == [], f"[란소프라졸 combo] 복합제인데 픽 발생: {picks2}")
    ck(reason2 == "no_domestic_single_oral_product", f"[란소프라졸 combo] reason != no_domestic ({reason2})")
    ck(all(mp <= 2 for mp in op2.calls), f"[란소프라졸 combo] '/' 동거성분인데 깊은검색 호출(calls={op2.calls})")

    # (c) 연속명 접두사(다른 약물): 에스오메프라졸이 오메프라졸을 지배 → 깊은검색 발동·정확 base 복구.
    pref_shallow = [row("320000001", "넥시움정(에스오메프라졸마그네슘)", "에스오메프라졸마그네슘"),
                    row("320000002", "에소메정(에스오메프라졸)", "에스오메프라졸")]
    pref_deep = pref_shallow + [row("199202074", "라메졸캡슐20밀리그램(오메프라졸)", "오메프라졸")]
    op3 = FakeOpener(pref_shallow, pref_deep)
    picks3, reason3 = vfs.search_itemseqs(op3, "오메프라졸", max_n=2, max_pages=2, deep_max_pages=20)
    ck(reason3 == "ok_deep_exact", f"[오메프라졸 prefix] reason != ok_deep_exact ({reason3})")
    ck([s for s, _, _ in picks3] == ["199202074"], f"[오메프라졸 prefix] 정확 base 미복구: {picks3}")
    ck(any(mp > 2 for mp in op3.calls), f"[오메프라졸 prefix] 연속명 지배인데 깊은검색 미발동(calls={op3.calls})")


def main():
    test_prednisolone_deep_fallback()
    test_not_marketed_no_deep()
    test_hydrocortisone_topical_only()
    test_pmready_shallow_exact_no_deep()
    test_hardening_prefix_only_deep()
    if fails:
        print("FAIL — search depth 회귀:")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS — search depth 회귀 5종(프레드니솔론 deep fallback·미유통 no-deep·"
          "하이드로코르티손 topical no-deep·PM-ready shallow-exact no-deep·"
          "하드닝 prefix-only deep[salt/combo skip]) 전건 통과.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
