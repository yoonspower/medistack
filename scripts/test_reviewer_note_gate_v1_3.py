#!/usr/bin/env python3
"""
test_reviewer_note_gate_v1_3.py
MediStack — reviewer-gated integration 인터록 **회귀 테스트**(읽기전용·네트워크 0).

검증 대상:
  - integrate_potassium_pm_ready_v1_2.check_reviewer_note (칼륨 4건 게이트)
  - integrate_antacid_fex_v1_2.check_reviewer_note      (AT-FEX 게이트)

두 단계로 입증한다.
  1) 게이트 함수 단위 — invalid 노트(빈/토큰없음/draft_id 누락/일부만/SAMPLE/placeholder, AT-FEX 는
     candidate_id·itemSeq·evidence moderate 누락 추가)를 **거부**하고 valid 노트만 **통과**시키는지.
  2) temp-copy 전체 write — valid 노트로 `--pm-approved --reviewer-note` 전체 경로를 **임시 복사본**
     export 에 대해서만 실행해 통합이 동작함을 입증하고, **실제 live export 는 한 바이트도 안 바뀜**(sha256 불변)을 확인.

⚠️ 이 테스트는 live export 를 수정하지 않는다. --pm-approved 전체 경로는 오직 temp 복사본에서만 호출한다.
종료코드: 0 PASS, 1 FAIL.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

fails = []


def _load(modfile):
    """integrate 스크립트를 모듈로 import(모듈 레벨엔 상수/함수만 — main 은 __main__ 가드, side-effect 0)."""
    path = os.path.join(HERE, modfile)
    spec = importlib.util.spec_from_file_location(modfile[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def expect_reject(label, bad, must_contain=None):
    ok = len(bad) > 0 and (must_contain is None or any(must_contain in b for b in bad))
    print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else f"  [bad={bad}]"))
    if not ok:
        fails.append(label)


def expect_accept(label, bad):
    ok = len(bad) == 0
    print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else f"  [bad={bad}]"))
    if not ok:
        fails.append(label)


def _note(tmp, text):
    p = os.path.join(tmp, "note.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def test_potassium_gate(pot, tmp):
    print("--- 칼륨 게이트 (check_reviewer_note, required = DF01·DF04·DF05·DF-PRED-01) ---")
    req = ["DF01", "DF04", "DF05", "DF-PRED-01"]
    cn = lambda txt: pot.check_reviewer_note(_note(tmp, txt), req)

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부", cn("DF01 DF04 DF05 DF-PRED-01 검토만 함")[1], "승인 표기")
    expect_reject("DF-PRED-01 누락 거부", cn("승인(approved): DF01, DF04, DF05")[1], "미명시")
    expect_reject("DF01만 있음 거부", cn("승인: DF01 만 검토")[1], "미명시")
    expect_reject("SAMPLE 토큰 거부(토큰+4건 있어도)",
                  cn("승인(approved) APPROVED-SAMPLE-NOT-VALID DF01 DF04 DF05 DF-PRED-01")[1], "SAMPLE")
    expect_reject("미기입 placeholder 거부", cn("승인(approved) DF01 DF04 DF05 DF-PRED-01\n검토일: YYYY-MM-DD")[1], "placeholder")
    expect_accept("valid 노트 통과(토큰+4건 전건·SAMPLE/placeholder 없음)",
                  cn("검수자: RPH-TEST-001 검토일 2026-07-01\n승인(approved): 칼륨 PM-ready 4건 "
                     "DF01, DF04, DF05, DF-PRED-01 을 verified_reference 노출로 승인.")[1])


def test_fex_gate(fex, tmp):
    print("--- AT-FEX 게이트 (check_reviewer_note, candidate_id+itemSeq 202202380+moderate) ---")
    cn = lambda txt: fex.check_reviewer_note(_note(tmp, txt))

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부", cn("AT-FEX-01 202202380 moderate 검토만")[1], "승인 표기")
    expect_reject("candidate_id 없음 거부", cn("승인(approved) 202202380 moderate")[1], "candidate_id")
    expect_reject("primary itemSeq 없음 거부", cn("승인(approved) AT-FEX-01 evidence moderate")[1], "202202380")
    expect_reject("evidence moderate 없음 거부", cn("승인(approved) AT-FEX-01 202202380")[1], "moderate")
    expect_reject("SAMPLE 토큰 거부(요건 다 있어도)",
                  cn("승인(approved) SAMPLE AT-FEX-01 202202380 moderate")[1], "SAMPLE")
    expect_accept("valid 노트 통과(토큰+candidate+itemSeq+moderate·SAMPLE 없음)",
                  cn("검수자: RPH-TEST-001 검토일 2026-07-01\n승인(approved): AT-FEX 후보 AT-FEX-01"
                     "(펙소페나딘 × Al/Mg 제산제) primary itemSeq 202202380, evidence_level moderate "
                     "로 verified_reference 노출 승인.")[1])


def temp_write_test(label, mod, valid_text, expect_count):
    """valid 노트로 --pm-approved 전체 write 경로를 temp 복사본 export 에 대해서만 실행.
    실 live export 는 sha256 불변이어야 한다."""
    real = mod.EXPORT
    real_before = _sha(real)
    tmp = tempfile.mkdtemp(prefix="ms_note_write_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(tmp, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, valid_text)
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note]
        rc = mod.main()
        data = json.load(open(tmp_export, encoding="utf-8"))
        cnt = len(data["relations"])
        ok_rc = rc == 0
        ok_cnt = cnt == expect_count
        ok_meta = data["meta"].get("relation_count") == expect_count
        print(("  PASS " if ok_rc else "  FAIL ") + f"{label}: valid 노트 통합 rc=0 (rc={rc})")
        print(("  PASS " if ok_cnt else "  FAIL ") + f"{label}: temp export relations {cnt} == {expect_count}")
        print(("  PASS " if ok_meta else "  FAIL ") + f"{label}: temp meta.relation_count == {expect_count}")
        for c, n in ((ok_rc, f"{label} rc"), (ok_cnt, f"{label} count"), (ok_meta, f"{label} meta")):
            if not c:
                fails.append(n)
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(tmp, ignore_errors=True)
    real_after = _sha(real)
    ok_live = real_before == real_after
    print(("  PASS " if ok_live else "  FAIL ") + f"{label}: live export sha256 불변(무수정)")
    if not ok_live:
        fails.append(f"{label} live unchanged")


def main():
    pot = _load("integrate_potassium_pm_ready_v1_2.py")
    fex = _load("integrate_antacid_fex_v1_2.py")
    tmp = tempfile.mkdtemp(prefix="ms_note_gate_")
    try:
        print("=== reviewer-note 게이트 회귀 테스트 (live export 무수정) ===")
        test_potassium_gate(pot, tmp)
        test_fex_gate(fex, tmp)
        print("--- temp-copy 전체 write (valid 노트 — live 무수정 확인) ---")
        temp_write_test(
            "칼륨 4건", pot,
            "검수자: RPH-TEST-001 검토일 2026-07-01\n승인(approved): 칼륨 PM-ready 4건 "
            "DF01, DF04, DF05, DF-PRED-01 을 verified_reference 노출로 승인.", 64)
        temp_write_test(
            "AT-FEX", fex,
            "검수자: RPH-TEST-001 검토일 2026-07-01\n승인(approved): AT-FEX 후보 AT-FEX-01 "
            "primary itemSeq 202202380, evidence_level moderate 로 verified_reference 노출 승인.", 61)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — 게이트가 invalid(빈/토큰없음/누락/SAMPLE/placeholder) 거부 + valid 통과 · "
          "temp write 동작 · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
