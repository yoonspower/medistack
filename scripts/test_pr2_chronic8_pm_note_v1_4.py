#!/usr/bin/env python3
"""
test_pr2_chronic8_pm_note_v1_4.py
check_pr2_chronic8_pm_note_v1_4.check_pm_note 단위 테스트 (읽기전용·live 무수정).
valid note PASS + 금지 mutation 전건 FAIL 확인.
사용: python3 scripts/test_pr2_chronic8_pm_note_v1_4.py   (0 = 전건 통과)
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("chk", os.path.join(HERE, "check_pr2_chronic8_pm_note_v1_4.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

NOTE = os.path.join(ROOT, "data", "review", "pr2_chronic8_pm_reviewed_note_v1_4.md")
LOCK = os.path.join(ROOT, "data", "review", "pr2_chronic8_candidate_lock_v1_4.json")
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
    _results.append((name, good, ok, problems[:2]))
    print(("  PASS " if good else "  FAIL ") + name +
          ("" if good else f"  [ok={ok} expect={expect_ok} {problems[:2]}]"))


def main():
    # 1) valid → PASS
    run("valid_note → PASS", BASE_NOTE, BASE_LOCK, True)

    # 2) PM 토큰 누락 (5)
    for tok in chk.PM_TOKENS:
        run(f"PM 토큰 제거({tok}) → FAIL", BASE_NOTE.replace(tok, "X_REMOVED_X"), BASE_LOCK, False)

    # 3) clinical/published true 요구
    run("clinical_reviewed=true 요구 → FAIL", BASE_NOTE + "\nclinical_reviewed=true 로 승격 요청.", BASE_LOCK, False)
    run("published=true 요구 → FAIL", BASE_NOTE + "\npublished=true 로 전환 승인.", BASE_LOCK, False)
    run("임상 검수 완료 단정 → FAIL", BASE_NOTE + "\n임상 검수 완료 되었음.", BASE_LOCK, False)
    run("식약처 문제없음 단정 → FAIL", BASE_NOTE + "\n식약처 문제없음 확인함.", BASE_LOCK, False)

    # 4) reviewed_by 입력 요구
    run("reviewed_by 입력 요구 → FAIL", BASE_NOTE + "\nreviewed_by 입력 필요.", BASE_LOCK, False)

    # 5) 제품/구매/제휴 허용
    run("제품 추천 허용 → FAIL", BASE_NOTE + "\n제품 추천 허용.", BASE_LOCK, False)
    run("구매 링크 허용 → FAIL", BASE_NOTE + "\n구매 링크 추가 가능.", BASE_LOCK, False)

    # 6) schedule 활성
    run("schedule 활성화 → FAIL", BASE_NOTE + "\nschedule 활성화함.", BASE_LOCK, False)

    # 7) 영양제 복용 권유 허용
    run("엽산 보충 권장 → FAIL", BASE_NOTE + "\n엽산 보충 권장.", BASE_LOCK, False)
    run("비타민D 복용 권유 허용 → FAIL", BASE_NOTE + "\n비타민D 복용 권유 허용.", BASE_LOCK, False)

    # 8) 검사/처방 지시 허용
    run("검사 지시 허용 → FAIL", BASE_NOTE + "\n검사 지시 허용함.", BASE_LOCK, False)

    # 9) 사용자 노출 단정
    run("안전 단정 → FAIL", BASE_NOTE + "\n복용해도 안전하다.", BASE_LOCK, False)

    # 10) needs_review 후보 승인맥락 포함
    run("needs_review(0245) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F9-0245 도 함께 통합 승인.", BASE_LOCK, False)
    # 11) 제외 family(F3) 승인맥락 포함
    run("F3 후보(0148) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F3-0148 통합 승인.", BASE_LOCK, False)
    # 12) PR-1 후보(F1) 승인맥락 포함
    run("PR-1 후보(F1) 승인맥락 → FAIL",
        BASE_NOTE + "\n승인 candidate: RF-F1-0021 통합 승인.", BASE_LOCK, False)

    # 13) candidate 누락 (8건 중 1 제거)
    miss = BASE_NOTE.replace("  - RF-F6-0201", "  - (제거됨)")
    run("candidate 누락(RF-F6-0201) → FAIL", miss, BASE_LOCK, False)

    # 14) delta 불일치
    run("delta 불일치 → FAIL", BASE_NOTE.replace("delta: +8", "delta: +9"), BASE_LOCK, False)

    # 15) before→after 불일치
    run("84→92 불일치 → FAIL", BASE_NOTE.replace("84 → 92", "84 → 99").replace("84→92", "84→99"),
        BASE_LOCK, False)

    # 16) source 없는 후보 (lock 변형)
    lock_nosrc = copy.deepcopy(BASE_LOCK)
    lock_nosrc["candidates"][0]["has_source"] = False
    run("source 없는 후보(lock) → FAIL", BASE_NOTE, lock_nosrc, False)

    # 17) 수치 단정 회피 원칙 제거
    run("수치 단정 회피 ack 제거 → FAIL",
        BASE_NOTE.replace("수치 단정 회피", "XXX").replace("'수치 변화 / 수치가 걱정되면'", "XXX")
                 .replace("엽산·비타민D·B12 '수치 저하'", "XXX"), BASE_LOCK, False)

    # 18) 골질환 alarm 비노출 제거
    run("골질환 alarm 비노출 ack 제거 → FAIL",
        BASE_NOTE.replace("display 에 비노출", "display 에 노출")
                 .replace("골연화증·구루병 등 골질환 alarm phrase 는 사용자", "XXX 는"), BASE_LOCK, False)

    # 19) 빈 노트
    run("빈 노트 → FAIL", "   ", BASE_LOCK, False)
    # 20) SAMPLE 토큰
    run("SAMPLE 토큰 → FAIL", BASE_NOTE + "\nSAMPLE", BASE_LOCK, False)

    print("=" * 60)
    fails = [r for r in _results if not r[1]]
    if fails:
        print(f"RESULT: FAIL — {len(fails)}/{len(_results)} 케이스 불일치")
        return 1
    print(f"RESULT: PASS — {len(_results)}/{len(_results)} 케이스 전건 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
