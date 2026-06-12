#!/usr/bin/env python3
"""
test_validate_v0_3_combo.py
v0.7 복합제(combo) tier 라이브 가드(#14/#15) 테스트 러너.

v0.3 alias validator 를 라이브 relations export(읽기 전용)에 대해 combo fixture 들로 실행하고
기대 PASS/FAIL + (거부 케이스는) 정확히 어떤 check 가 실패했는지까지 단언한다.
라이브 alias/데이터는 변경하지 않는다.

사용:  python3 scripts/test_validate_v0_3_combo.py
종료 코드: 0 = 모든 테스트 통과, 1 = 실패
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VALIDATOR = os.path.join(HERE, "validate_medistack_v0_3_aliases.py")
RELATIONS = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
REAL_ALIASES = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
FIX = os.path.join(HERE, "fixtures", "v0_7_combo")

# (label, alias_path, expect_pass, expected_failing_checks)
CASES = [
    ("P0 현행 라이브 alias(복합제 entry 0건) 전체 PASS", REAL_ALIASES, True, set()),
    ("P1 정상 메트포르민 복합제(고지 메타 정합) PASS", os.path.join(FIX, "allow_combo.json"), True, set()),
    ("C1 HCTZ basis 차단(allowlist 외)", os.path.join(FIX, "reject_C1_hctz_combo.json"), False, {15}),
    ("C2 combination_notice_required 누락", os.path.join(FIX, "reject_C2_missing_notice.json"), False, {14}),
    ("C3 basis != canonical", os.path.join(FIX, "reject_C3_basis_ne_canonical.json"), False, {14}),
    ("C4 is_combination 플래그가 ingredient alias", os.path.join(FIX, "reject_C4_combo_on_ingredient.json"), False, {14}),
    ("C5 orphan 고지필드(is_combination 없음)", os.path.join(FIX, "reject_C5_orphan_notice.json"), False, {14}),
]

CHECK_RE = re.compile(r"X #(\d+)")


def run(alias_path):
    p = subprocess.run([sys.executable, VALIDATOR, alias_path, RELATIONS],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    fails = []
    for label, path, expect_pass, expected_checks in CASES:
        rc, out = run(path)
        failing = {int(n) for n in CHECK_RE.findall(out)}
        if expect_pass:
            ok = (rc == 0 and not failing)
        else:
            ok = (rc == 1 and failing == expected_checks)
        print(f"[{'PASS' if ok else 'FAIL'}] {label}  (rc={rc}, failing_checks={sorted(failing)}, expect={'PASS' if expect_pass else sorted(expected_checks)})")
        if not ok:
            fails.append(label)
            print("  --- validator output ---")
            for line in out.splitlines():
                print("  " + line)
    print()
    if fails:
        print(f"TEST SUITE: FAIL ({len(fails)}/{len(CASES)} 실패): {fails}")
        return 1
    print(f"TEST SUITE: PASS ({len(CASES)}/{len(CASES)} 통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
