#!/usr/bin/env python3
"""
test_validate_v0_3_typeB.py
validator #8 일반화(유형 B 화이트리스트) 테스트 러너.

v0.3 alias validator 를 라이브 relations export(읽기 전용)에 대해 fixture 들로 실행하고
기대 PASS/FAIL + (거부 케이스는) 정확히 어떤 check 가 실패했는지까지 단언한다.
라이브 alias/데이터는 변경하지 않는다.

사용:  python3 scripts/test_validate_v0_3_typeB.py
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
FIX = os.path.join(HERE, "fixtures", "v0_4_typeB")

# (label, alias_path, expect_pass, expected_failing_checks)
#   expect_pass=True  -> rc 0 (실패 check 없음)
#   expect_pass=False -> rc 1 이고 실패 check 집합 == expected_failing_checks
CASES = [
    ("P1 하위호환: 라이브 62개 alias(화이트리스트 없음)", REAL_ALIASES, True, set()),
    ("P3/P4/P5 유형 B 허용(화이트리스트+제품 alias)", os.path.join(FIX, "allow_typeB.json"), True, set()),
    ("F1 item_seq 가 relation·화이트리스트 모두에 없음", os.path.join(FIX, "reject_F1_itemseq_unknown.json"), False, {8}),
    ("F2 화이트리스트 성분 키 비라이브", os.path.join(FIX, "reject_F2_whitelist_ingredient_not_live.json"), False, {12}),
    ("F6 화이트리스트 에스오메프라졸 키", os.path.join(FIX, "reject_F6_whitelist_esomeprazole.json"), False, {12}),
    ("F7 화이트리스트 엔트리 제품/구매 필드", os.path.join(FIX, "reject_F7_whitelist_link_field.json"), False, {13}),
    ("F9 화이트리스트 item_seq 비숫자형", os.path.join(FIX, "reject_F9_whitelist_bad_itemseq.json"), False, {13}),
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
