#!/usr/bin/env python3
"""
test_penicillamine_reviewer_note_gate_v1_3.py
MediStack — 페니실라민 FE/ZN subset live 통합 reviewer-note **인터록 회귀 테스트**(읽기전용·네트워크 0).

검증 대상: integrate_penicillamine_subset_v1_3.check_reviewer_note + (temp-copy) 전체 write 경로.
  1) 게이트 단위 — invalid(빈/토큰없음/FE누락/ZN누락/ZN mechanism 누락/grouping 누락/SAMPLE/placeholder/
     clinical=true 요구/제품추천 허용/철분·아연 보충 권유 허용) 거부 + valid 통과.
  2) temp-copy 전체 write — valid 노트로 --pm-approved --reviewer-note 를 **임시 복사본** export 에 실행해 60→62 동작 +
     **실제 live export sha256 불변** 확인.
⚠️ live export 무수정. --pm-approved 전체 경로는 temp 복사본에서만.
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

fails = []


def _load(modfile):
    path = os.path.join(HERE, modfile)
    spec = importlib.util.spec_from_file_location(modfile[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(p):
    with open(p, "rb") as f:
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


VALID = (
    "검수자: RPH-TEST-001  검토일 2026-07-01\n"
    "승인(approved): 페니실라민 subset 2건 TM-CHEL-01-FE, TM-CHEL-01-ZN 을 verified_reference 노출로 승인.\n"
    "mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지"
    "(흡수 추론·confidence moderate·user 카피 영향 없음).\n"
    "grouping 결정: FE/ZN 개별 카드 유지.\n"
    "clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 철분·아연 보충 권유 없음.\n"
)


def test_gate(mod, tmp):
    print("--- 페니실라민 subset 게이트 (check_reviewer_note) ---")
    cn = lambda txt: mod.check_reviewer_note(_note(tmp, txt))

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부",
                  cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    expect_reject("FE 누락 거부", cn(VALID.replace("TM-CHEL-01-FE, ", ""))[1], "candidate_id 미명시")
    expect_reject("ZN 누락 거부", cn(VALID.replace("TM-CHEL-01-ZN", ""))[1], "candidate_id 미명시")
    expect_reject("ZN mechanism 결정 누락 거부",
                  cn(VALID.replace("mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지"
                                   "(흡수 추론·confidence moderate·user 카피 영향 없음).\n", ""))[1], "mechanism")
    expect_reject("grouping 결정 누락 거부",
                  cn(VALID.replace("grouping 결정: FE/ZN 개별 카드 유지.\n", ""))[1], "grouping")
    expect_reject("verified_reference 누락 거부",
                  cn(VALID.replace("verified_reference 노출로", "참고 노출로").replace("verified_reference 천장 유지", "천장 유지"))[1],
                  "verified_reference")
    expect_reject("clinical=true 아님 명시 누락 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ", ""))[1],
                  "clinical_reviewed=true 아님")
    expect_reject("제품 추천 아님 명시 누락 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음. ", ""))[1], "제품 추천 아님")
    expect_reject("철분/아연 보충 권유 아님 명시 누락 거부",
                  cn(VALID.replace(" 철분·아연 보충 권유 없음.", ""))[1], "보충 권유 아님")
    expect_reject("SAMPLE 토큰 거부", cn(VALID + "\nAPPROVED-SAMPLE-NOT-VALID")[1], "SAMPLE")
    expect_reject("placeholder 거부", cn(VALID + "\n검토일 YYYY-MM-DD")[1], "placeholder")
    expect_reject("clinical=true 승격 요구 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ",
                                   "clinical_reviewed=true 로 승격 승인. "))[1], "승격 요구")
    expect_reject("제품 추천 허용 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음.", "제품 추천 허용함."))[1], "제품 추천 허용")
    expect_reject("철분/아연 보충 권유 허용 거부",
                  cn(VALID.replace("철분·아연 보충 권유 없음.", "철분 보충 권장함."))[1], "보충 권유/권장 허용")
    expect_accept("valid 노트 통과(FE/ZN+ZN mechanism+grouping+verified_reference·promo 없음)", cn(VALID)[1])


def temp_write_test(mod, tmp):
    print("--- temp-copy 전체 write (valid 노트 — live 무수정) ---")
    real = mod.EXPORT
    before = _sha(real)
    work = tempfile.mkdtemp(prefix="ms_pen_write_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, VALID)
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note]
        rc = mod.main()
        data = json.load(open(tmp_export, encoding="utf-8"))
        cnt = len(data["relations"])
        new_ids = sorted(r["id"] for r in data["relations"])[-2:]
        new_rels = [r for r in data["relations"] if r["id"] in (62, 63)]
        ok_rc, ok_cnt, ok_meta = rc == 0, cnt == 62, data["meta"].get("relation_count") == 62
        ok_ids = new_ids == [62, 63]
        ok_safe = all(r.get("product_link_allowed") is False and r.get("potassium_safety_card") is False
                      and r.get("requires_clinical_review") is False and "reviewed_by" not in r
                      and "counterpart_category" not in r for r in new_rels)
        for c, n in ((ok_rc, "valid 노트 통합 rc=0"), (ok_cnt, "temp relations 62"),
                     (ok_meta, "temp meta.relation_count 62"), (ok_ids, "신규 id 62,63"),
                     (ok_safe, "신규 2건 product/kcard/clinical=false·reviewed_by/category 부재")):
            print(("  PASS " if c else "  FAIL ") + f"{n}" + ("" if c else f" (rc={rc} cnt={cnt} ids={new_ids})"))
            if not c:
                fails.append(n)
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    ok_live = before == _sha(real)
    print(("  PASS " if ok_live else "  FAIL ") + "live export sha256 불변(무수정)")
    if not ok_live:
        fails.append("live unchanged")


def main():
    mod = _load("integrate_penicillamine_subset_v1_3.py")
    tmp = tempfile.mkdtemp(prefix="ms_pen_gate_")
    try:
        print("=== 페니실라민 subset reviewer-note 게이트 회귀 테스트 (live 무수정) ===")
        test_gate(mod, tmp)
        temp_write_test(mod, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — invalid 전건 거부 + valid 통과 · temp write 60→62 동작 · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
