#!/usr/bin/env python3
"""
test_pr1_antibiotic24_pm_note_v1_4.py
PR-1 antibiotic24 PM-note checker 회귀 테스트 (읽기전용·temp 파일만·live 무수정).

valid note → PASS, 그리고 금지 행동을 요구/누락한 변형 → 전부 FAIL 임을 검증.
"""
import copy
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NOTE = os.path.join(ROOT, "data", "review", "pr1_antibiotic24_pm_reviewed_note_v1_4.md")
LOCK = os.path.join(ROOT, "data", "review", "pr1_antibiotic24_candidate_lock_v1_4.json")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


chk = _load("chk", os.path.join(HERE, "check_pr1_antibiotic24_pm_note_v1_4.py"))


def write_tmp(text):
    fd, p = tempfile.mkstemp(suffix=".md", prefix="pmnote_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def main():
    base = open(NOTE, encoding="utf-8").read()
    lock = json.load(open(LOCK, encoding="utf-8"))
    results = []

    def expect(label, ok, problems, want_pass):
        passed = (ok == want_pass)
        results.append((label, passed, "PASS" if ok else f"FAIL({len(problems)})"))
        if not passed:
            print(f"  [!] {label}: 기대 {'PASS' if want_pass else 'FAIL'} 인데 {'PASS' if ok else 'FAIL'} — {problems[:3]}")

    # 0) valid note → PASS
    p = write_tmp(base)
    ok, pr = chk.check_pm_note(p, lock)
    expect("valid_note", ok, pr, True)
    os.unlink(p)

    # 1) 없는 note → FAIL
    ok, pr = chk.check_pm_note(os.path.join(ROOT, "no_such_note.md"), lock)
    expect("missing_note", ok, pr, False)

    # 2) 빈 note → FAIL
    p = write_tmp("   \n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("empty_note", ok, pr, False)
    os.unlink(p)

    # 3) PM 토큰 각각 누락 → FAIL
    for tok in chk.PM_TOKENS:
        p = write_tmp(base.replace(tok, "TOKEN_REMOVED"))
        ok, pr = chk.check_pm_note(p, lock)
        expect(f"missing_token:{tok}", ok, pr, False)
        os.unlink(p)

    # 4) clinical_reviewed=true 승격 요구 → FAIL
    p = write_tmp(base + "\n추가: clinical_reviewed=true 로 승격 요청.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("clinical_true_demand", ok, pr, False)
    os.unlink(p)

    # 5) published=true 요구 → FAIL
    p = write_tmp(base + "\n추가: published=true 로 전환 요청.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("published_true_demand", ok, pr, False)
    os.unlink(p)

    # 6) reviewed_by 입력 요구 → FAIL
    p = write_tmp(base + "\n추가: reviewed_by 입력 필요.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("reviewed_by_input_demand", ok, pr, False)
    os.unlink(p)

    # 7) 제품 추천 허용 → FAIL
    p = write_tmp(base + "\n추가: 제품 추천 허용.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("product_permission", ok, pr, False)
    os.unlink(p)

    # 7b) 구매 권유 → FAIL
    p = write_tmp(base + "\n추가: 구매 권유 문구 노출.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("purchase_promotion", ok, pr, False)
    os.unlink(p)

    # 8) schedule 활성화 허용 → FAIL
    p = write_tmp(base + "\n추가: schedule 활성화 허용.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("schedule_active", ok, pr, False)
    os.unlink(p)

    # 9) needs_review 후보를 승인 맥락(제외 없는 줄)에 포함 → FAIL
    p = write_tmp(base + "\n승인 추가: RF-F3-0148 도 함께 통합.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("needs_review_in_approval", ok, pr, False)
    os.unlink(p)

    # 10) F4/F6 family 후보를 승인 맥락에 포함 → FAIL
    p = write_tmp(base + "\n승인 추가: RF-F4-0301 통합 승인.\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("excluded_family_in_approval", ok, pr, False)
    os.unlink(p)

    # 11) candidate 누락 → FAIL
    drop = lock["candidate_ids"][0]
    p = write_tmp(base.replace(drop, "RF-DROPPED"))
    ok, pr = chk.check_pm_note(p, lock)
    expect(f"candidate_missing:{drop}", ok, pr, False)
    os.unlink(p)

    # 11b) add-on candidate 누락 → FAIL
    addon = [c["candidate_id"] for c in lock["candidates"] if c.get("origin") == "production_audit_cleanup"][0]
    p = write_tmp(base.replace(addon, "ADDON-DROPPED"))
    ok, pr = chk.check_pm_note(p, lock)
    expect("addon_missing", ok, pr, False)
    os.unlink(p)

    # 12) delta 불일치 → FAIL
    p = write_tmp(base.replace("delta: +24", "delta: +25"))
    ok, pr = chk.check_pm_note(p, lock)
    expect("delta_mismatch", ok, pr, False)
    os.unlink(p)

    # 12b) before→after 불일치 → FAIL
    p = write_tmp(base.replace("60 → 84", "60 → 83"))
    ok, pr = chk.check_pm_note(p, lock)
    expect("count_mismatch", ok, pr, False)
    os.unlink(p)

    # 13) source 없는 add-on (lock 변형) → FAIL
    lock_nosrc = copy.deepcopy(lock)
    for c in lock_nosrc["candidates"]:
        if c.get("origin") == "production_audit_cleanup":
            c["has_source"] = False
    p = write_tmp(base)
    ok, pr = chk.check_pm_note(p, lock_nosrc)
    expect("addon_no_source", ok, pr, False)
    os.unlink(p)

    # 13b) add-on independent_audit != passed → FAIL
    lock_noaudit = copy.deepcopy(lock)
    for c in lock_noaudit["candidates"]:
        if c.get("origin") == "production_audit_cleanup":
            c["independent_audit"] = "pending"
    p = write_tmp(base)
    ok, pr = chk.check_pm_note(p, lock_noaudit)
    expect("addon_audit_not_passed", ok, pr, False)
    os.unlink(p)

    # 14) SAMPLE 토큰 → FAIL
    p = write_tmp(base + "\nSAMPLE\n")
    ok, pr = chk.check_pm_note(p, lock)
    expect("sample_token", ok, pr, False)
    os.unlink(p)

    npass = sum(1 for _, ok, _ in results if ok)
    print(f"\n=== PR-1 antibiotic24 PM-note checker 테스트: {npass}/{len(results)} ===")
    for label, ok, verdict in results:
        print(f"  {'OK ' if ok else 'XX '} {label} ({verdict})")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
