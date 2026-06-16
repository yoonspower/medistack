#!/usr/bin/env python3
"""
test_theme_map_reviewer_note_gate_v1_3.py
MediStack — theme map 6건 live 통합 reviewer-note **인터록 회귀 테스트**(읽기전용·네트워크 0).

검증 대상: integrate_theme_map_draft_batch_v1_3.check_reviewer_note + (temp-copy) 전체 write 경로.

두 단계.
  1) 게이트 함수 단위 — invalid 노트(빈/토큰없음/candidate 일부누락/category 누락/grouping 누락/mechanism 누락/
     SAMPLE/placeholder/clinical=true 요구/제품추천 허용)를 **거부**하고 valid 노트만 **통과**.
  2) temp-copy 전체 write — valid 노트로 --pm-approved --reviewer-note 전체 경로를 **임시 복사본** export 에 대해서만
     실행해 60→66 통합이 동작함을 입증하고, **실제 live export 는 sha256 불변**(한 바이트도 안 바뀜)을 확인.

⚠️ live export 무수정. --pm-approved 전체 경로는 오직 temp 복사본에서만 호출한다.
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


VALID = (
    "검수자: RPH-TEST-001  검토일 2026-07-01\n"
    "승인(approved): theme map 6건 TM-LIP-01, TM-LIP-02, TM-CEPH-AC-01, TM-CEPH-AC-02, "
    "TM-CHEL-01-FE, TM-CHEL-01-ZN 을 verified_reference 노출로 승인.\n"
    "category 결정: acid_reducing_drug(세팔로 acid-reducer, al_mg_antacid 와 구분) 채택, "
    "fat_soluble_vitamin 그룹 채택.\n"
    "grouping 결정: 지용성 비타민은 그룹 단일 카드 유지, 페니실라민 FE/ZN 은 개별 카드.\n"
    "mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지(user 카피 영향 없음).\n"
    "clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴·보충제 추천 없음.\n"
)


def test_gate(mod, tmp):
    print("--- theme map 게이트 (check_reviewer_note) ---")
    cn = lambda txt: mod.check_reviewer_note(_note(tmp, txt))

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부",
                  cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    expect_reject("candidate 일부 누락 거부(TM-LIP-01 제거)",
                  cn(VALID.replace("TM-LIP-01, ", ""))[1], "candidate_id 미명시")
    expect_reject("acid_reducing_drug 결정 누락 거부",
                  cn(VALID.replace("acid_reducing_drug(세팔로 acid-reducer, al_mg_antacid 와 구분) 채택, ", ""))[1],
                  "acid_reducing_drug")
    expect_reject("fat_soluble_vitamin 결정 누락 거부",
                  cn(VALID.replace("fat_soluble_vitamin 그룹 채택", "지용성군 채택"))[1], "fat_soluble_vitamin")
    expect_reject("grouping 결정 누락 거부",
                  cn(VALID.replace("grouping 결정: 지용성 비타민은 그룹 단일 카드 유지, 페니실라민 FE/ZN 은 개별 카드.\n", ""))[1],
                  "grouping")
    expect_reject("아연 mechanism 결정 누락 거부",
                  cn(VALID.replace("mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지(user 카피 영향 없음).\n", ""))[1],
                  "mechanism")
    expect_reject("verified_reference 동의 누락 거부",
                  cn(VALID.replace("verified_reference 노출로", "참고 노출로").replace("verified_reference 천장 유지", "천장 유지"))[1],
                  "verified_reference")
    expect_reject("clinical_reviewed=true 아님 명시 누락 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ", ""))[1],
                  "clinical_reviewed=true 아님")
    expect_reject("제품 추천 아님 명시 누락 거부",
                  cn(VALID.replace("제품·구매·제휴·보충제 추천 없음.", "상업 영역 검토함."))[1],
                  "제품/보충 추천 아님")
    expect_reject("SAMPLE 토큰 거부(요건 다 있어도)",
                  cn(VALID + "\nAPPROVED-SAMPLE-NOT-VALID")[1], "SAMPLE")
    expect_reject("placeholder 거부", cn(VALID + "\n검토일: YYYY-MM-DD")[1], "placeholder")
    expect_reject("clinical=true 승격 요구 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ",
                                   "clinical_reviewed=true 로 승격 승인. "))[1],
                  "승격 요구")
    expect_reject("제품 추천 허용 문구 거부",
                  cn(VALID.replace("제품·구매·제휴·보충제 추천 없음.", "보충제 추천 허용함."))[1],
                  "제품/보충 추천 허용")
    expect_accept("valid 노트 통과(6건+category+grouping+mechanism+verified_reference·SAMPLE/promo 없음)", cn(VALID)[1])


def temp_write_test(mod, tmp):
    """valid 노트로 --pm-approved 전체 write 를 temp 복사본 export(60건)에 실행 → 66. 실 live sha 불변."""
    print("--- temp-copy 전체 write (valid 노트 — live 무수정 확인) ---")
    real = mod.EXPORT
    real_before = _sha(real)
    work = tempfile.mkdtemp(prefix="ms_tm_note_write_")
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
        new_ids = sorted(r["id"] for r in data["relations"])[-6:]
        ok_rc, ok_cnt, ok_meta = rc == 0, cnt == 66, data["meta"].get("relation_count") == 66
        ok_ids = new_ids == [62, 63, 64, 65, 66, 67]
        # 통합된 6건 안전 필드
        new_rels = [r for r in data["relations"] if r["id"] in (62, 63, 64, 65, 66, 67)]
        ok_safe = all(r.get("product_link_allowed") is False and r.get("potassium_safety_card") is False
                      and r.get("requires_clinical_review") is False and "reviewed_by" not in r
                      for r in new_rels)
        for c, n in ((ok_rc, "valid 노트 통합 rc=0"), (ok_cnt, "temp relations 66"),
                     (ok_meta, "temp meta.relation_count 66"), (ok_ids, "신규 id 62..67"),
                     (ok_safe, "신규 6건 product/kcard/clinical=false·reviewed_by 부재")):
            print(("  PASS " if c else "  FAIL ") + f"{n}" + ("" if c else f" (rc={rc} cnt={cnt} ids={new_ids})"))
            if not c:
                fails.append(n)
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    ok_live = real_before == _sha(real)
    print(("  PASS " if ok_live else "  FAIL ") + "live export sha256 불변(무수정)")
    if not ok_live:
        fails.append("live unchanged")


def main():
    mod = _load("integrate_theme_map_draft_batch_v1_3.py")
    tmp = tempfile.mkdtemp(prefix="ms_tm_note_gate_")
    try:
        print("=== theme map reviewer-note 게이트 회귀 테스트 (live export 무수정) ===")
        test_gate(mod, tmp)
        temp_write_test(mod, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — 게이트가 invalid 전건 거부 + valid 통과 · temp write 60→66 동작 · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
