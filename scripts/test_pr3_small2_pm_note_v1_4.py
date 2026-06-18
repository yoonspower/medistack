#!/usr/bin/env python3
"""
test_pr3_small2_pm_note_v1_4.py
check_pr3_small2_pm_note_v1_4.check_pm_note 단위 테스트 (읽기전용·live 무수정).
valid note PASS + 금지 mutation 전건 FAIL 확인.
"""
import copy
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("chk", os.path.join(HERE, "check_pr3_small2_pm_note_v1_4.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

NOTE = os.path.join(ROOT, "data", "review", "pr3_small2_pm_reviewed_note_v1_4.md")
LOCK = os.path.join(ROOT, "data", "review", "pr3_small2_candidate_lock_v1_4.json")
BASE_NOTE = open(NOTE, encoding="utf-8").read()
BASE_LOCK = json.load(open(LOCK, encoding="utf-8"))

_results = []


def run(name, note_text, lock, expect_ok):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(note_text)
        path = f.name
    try:
        ok, problems = chk.check_pm_note(path, lock)
    finally:
        os.unlink(path)
    good = (ok == expect_ok)
    _results.append((name, good))
    print(("  PASS " if good else "  FAIL ") + name + ("" if good else f"  [ok={ok} expect={expect_ok} {problems[:2]}]"))


def main():
    run("valid_note → PASS", BASE_NOTE, BASE_LOCK, True)
    for tok in chk.PM_TOKENS:
        run(f"PM 토큰 제거({tok}) → FAIL", BASE_NOTE.replace(tok, "X_RM_X"), BASE_LOCK, False)
    run("clinical_reviewed=true 요구 → FAIL", BASE_NOTE + "\nclinical_reviewed=true 로 승격 요청.", BASE_LOCK, False)
    run("published=true 요구 → FAIL", BASE_NOTE + "\npublished=true 로 전환 승인.", BASE_LOCK, False)
    run("임상 검수 완료 단정 → FAIL", BASE_NOTE + "\n임상 검수 완료 되었음.", BASE_LOCK, False)
    run("식약처 문제없음 단정 → FAIL", BASE_NOTE + "\n식약처 문제없음 확인함.", BASE_LOCK, False)
    run("reviewed_by 입력 요구 → FAIL", BASE_NOTE + "\nreviewed_by 입력 필요.", BASE_LOCK, False)
    run("제품 추천 허용 → FAIL", BASE_NOTE + "\n제품 추천 허용.", BASE_LOCK, False)
    run("구매 링크 허용 → FAIL", BASE_NOTE + "\n구매 링크 추가 가능.", BASE_LOCK, False)
    run("schedule 활성화 → FAIL", BASE_NOTE + "\nschedule 활성화함.", BASE_LOCK, False)
    run("검사 지시 허용 → FAIL", BASE_NOTE + "\n검사 지시 허용함.", BASE_LOCK, False)
    run("안전 단정 → FAIL", BASE_NOTE + "\n복용해도 안전하다.", BASE_LOCK, False)
    run("needs_review(0148) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F3-0148 도 함께 통합 승인.", BASE_LOCK, False)
    run("PR-1 후보(F1) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F1-0021 통합 승인.", BASE_LOCK, False)
    run("PR-2 후보(F9) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F9-0269 통합 승인.", BASE_LOCK, False)
    run("candidate 누락(RF-F4-0173) → FAIL",
        BASE_NOTE.replace("RF-F4-0173", "X_RM_X"), BASE_LOCK, False)
    run("delta 불일치 → FAIL", BASE_NOTE.replace("delta: +2", "delta: +3"), BASE_LOCK, False)
    run("92→94 불일치 → FAIL", BASE_NOTE.replace("92 → 94", "92 → 99").replace("92→94", "92→99"), BASE_LOCK, False)
    lock_nosrc = copy.deepcopy(BASE_LOCK)
    lock_nosrc["candidates"][0]["has_source"] = False
    run("source 없는 후보(lock) → FAIL", BASE_NOTE, lock_nosrc, False)
    run("레보티록신 Al-only ack 제거 → FAIL",
        BASE_NOTE.replace("Mg 미명시", "XXX").replace("알루미늄", "XXX"), BASE_LOCK, False)
    run("copy_change/reframe ack 제거 → FAIL",
        BASE_NOTE.replace("copy_change", "XXX").replace("reframe", "XXX"), BASE_LOCK, False)
    run("빈 노트 → FAIL", "   ", BASE_LOCK, False)
    run("SAMPLE 토큰 → FAIL", BASE_NOTE + "\nSAMPLE", BASE_LOCK, False)

    print("=" * 60)
    fails = [r for r in _results if not r[1]]
    if fails:
        print(f"RESULT: FAIL — {len(fails)}/{len(_results)} 불일치")
        return 1
    print(f"RESULT: PASS — {len(_results)}/{len(_results)} 케이스 전건 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
