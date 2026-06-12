#!/usr/bin/env python3
"""
test_validate_combo_ar.py
v0.7 combo approved-ready 검증기(validate_combo_approved_ready.py) 음성/양성 테스트 러너.
라이브 relations export(읽기 전용)에 대해 fixture 들로 검증기를 실행하고 기대 PASS/FAIL +
거부 케이스의 정확한 실패 check 까지 단언한다. 라이브 데이터 미변경.

사용: python3 scripts/test_validate_combo_ar.py
종료 코드: 0 통과, 1 실패
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VALIDATOR = os.path.join(HERE, "validate_combo_approved_ready.py")
RELATIONS = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
REAL_ALIASES = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
FIX = os.path.join(HERE, "fixtures", "v0_7_combo_ar")

CASES = [
    ("P 정상 메트포르민 복합제 PASS", "allow.json", True, set()),
    ("P HCTZ+ARB 복합제 PASS(v0.8 개방·염이름 칼륨 통과)", "allow_hctz_arb.json", True, set()),
    ("P HCTZ+ARB+CCB 3성분 PASS", "allow_hctz_arb_ccb.json", True, set()),
    ("C3 is_combination=false/단일 ingr", "reject_C3_not_combo.json", False, {3}),
    ("C4 relation 성분 2개", "reject_C4_multi_relation.json", False, {4}),
    ("C5 basis != canonical", "reject_C5_basis_ne_canonical.json", False, {5}),
    ("C6 basis allowlist 외(토라세미드)", "reject_C6_basis_blocked.json", False, {6}),
    ("C7 notice_required=false(메트)", "reject_C7_notice_false.json", False, {7}),
    ("C8 동일 item_seq 2건", "reject_C8_dup_itemseq.json", False, {8}),
    ("C9 에스오메프라졸 신호(+substring #4)", "reject_C9_eso.json", False, {4, 9}),
    ("C11 incorporated=true 인데 alias 미반영(옵션A)", "reject_C10_incorporated.json", False, {11}),
    ("C12 칼륨보존이뇨제 파트너(스피로노락톤)", "reject_C12_kspare.json", False, {12}),
    ("C13 HCTZ notice=false(반전고지 트리거 불완전)", "reject_C13_hctz_notice.json", False, {7, 13}),
]

CHECK_RE = re.compile(r"X #(\d+)")


def run(path):
    p = subprocess.run([sys.executable, VALIDATOR, path, RELATIONS, REAL_ALIASES], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    fails = []
    for label, fname, expect_pass, expected in CASES:
        rc, out = run(os.path.join(FIX, fname))
        failing = {int(n) for n in CHECK_RE.findall(out)}
        ok = (rc == 0 and not failing) if expect_pass else (rc == 1 and failing == expected)
        print(f"[{'PASS' if ok else 'FAIL'}] {label}  (rc={rc}, failing={sorted(failing)}, expect={'PASS' if expect_pass else sorted(expected)})")
        if not ok:
            fails.append(label)
            for line in out.splitlines():
                print("  " + line)
    print()
    if fails:
        print(f"TEST SUITE: FAIL ({len(fails)}/{len(CASES)}): {fails}")
        return 1
    print(f"TEST SUITE: PASS ({len(CASES)}/{len(CASES)} 통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
