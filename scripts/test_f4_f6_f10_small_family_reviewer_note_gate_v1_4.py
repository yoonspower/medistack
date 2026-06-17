#!/usr/bin/env python3
"""
test_f4_f6_f10_small_family_reviewer_note_gate_v1_4.py
MediStack — F4/F6/F10 small-family bundle live 통합 reviewer-note **인터록 회귀 테스트**(읽기전용·네트워크 0).

검증 대상: integrate_f4_f6_f10_small_family_batch_v1_4.check_reviewer_note + (temp-copy) 전체 write 경로 + needs_review 차단.
  1) 게이트 단위 — invalid(빈/토큰없음/candidate 누락/scope 불일치/SAMPLE/placeholder/clinical=true 요구/제품 추천 허용/
     B12 보충 권유 허용/검사·처방 지시 허용/category 미명시/영양소 미명시/mechanism 미명시/Al-only ack 누락/0275 ack 누락/
     verified_reference 없음/reviewer 식별자 없음/grouping 누락/소아·골·외용 일반화 허용) 거부 + valid 통과.
  2) temp-copy 전체 write — valid 노트로 integrable(2) 60→62(id 62,63)·family:F4 60→61·family:F6 60→61 + **실제 live export sha256 불변**.
  3) needs_review 차단 — --candidate-ids 로 0275(needs_review) 요청 시 build_subset STOP(통합 거부).
  4) idempotency — 같은 scope 재실행 시 이미 존재 → STOP.
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
    ok = len(bad) > 0 and (must_contain is None or any(must_contain in x for x in bad))
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


def build_valid(scope_label, scope_ids):
    ids_line = ", ".join(scope_ids)
    grouping = {"integrable": "grouping: integrable subset(small-family bundle) 한 번에 통합",
                "family:F4": "grouping: family:F4 개별 통합",
                "family:F6": "grouping: family:F6 개별 통합"}.get(scope_label, "grouping: subset 한 번에 통합")
    return (
        f"검수자: RPH-TEST-001 (PM 승인 근거 첨부)  검토일 2026-07-01\n"
        f"승인(approved): F4/F6/F10 small-family {scope_label} 후보를 verified_reference 노출로 승인.\n"
        f"scope: {scope_label} 범위. 승인 candidate_id 전건: {ids_line}.\n"
        f"{grouping}.\n"
        f"category 결정: 레보티록신×제산제 = al_mg_antacid(알루미늄 함유 제산제). 영양소: 에스오메프라졸×비타민B12(약물 category 없음).\n"
        f"mechanism/action: absorption/separation(F4) · depletion/monitoring(F6). 모니터링 톤(참고정보·정기 확인 문의, "
        f"검사 지시 아님·처방 아님) 유지.\n"
        f"RF-F4-0173: 라벨이 알루미늄 함유 제산제만 명시(Mg 미명시) — Al-only copy_change 인지·display Mg 비단정.\n"
        f"케토코나졸(F10): 국내 외용 전용·수출용 source → route/availability needs_review, 본 승인 대상 아님(통합 제외).\n"
        f"clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. B12 보충 권유 없음.\n"
        f"verified_reference 노출 동의.\n"
    )


def test_gate(mod, tmp):
    print("--- small-family 게이트 (check_reviewer_note) ---")
    recs, _s = mod.load_bundle()
    integ_ids = mod._integrable_ids(recs)
    VALID = build_valid("integrable", integ_ids)
    cn = lambda txt, ids=integ_ids: mod.check_reviewer_note(_note(tmp, txt), ids)

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부",
                  cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    expect_reject("candidate_id 누락 거부", cn(VALID.replace("RF-F4-0173", "RF-F4-XXXX"))[1], "candidate_id 미명시")
    expect_reject("reviewer 식별자 없음 거부",
                  cn(VALID.replace("검수자: RPH-TEST-001 (PM 승인 근거 첨부)  ", ""))[1], "reviewer 식별자")
    expect_reject("scope 선언 누락 거부", cn(VALID.replace("scope:", "대상:").replace(" 범위.", "."))[1], "scope 선언")
    expect_reject("grouping 결정 누락 거부",
                  cn(VALID.replace("grouping: integrable subset(small-family bundle) 한 번에 통합.", "통합 방식 미정."))[1], "grouping")
    expect_reject("category 결정 미명시 거부",
                  cn(VALID.replace("al_mg_antacid(알루미늄 함유 제산제)", "○○").replace("레보티록신×제산제", "레보티록신×○○")
                     .replace("RF-F4-0173: 라벨이 알루미늄 함유 제산제만 명시(Mg 미명시) — Al-only copy_change 인지·display Mg 비단정.\n", ""))[1],
                  "F4 category")
    expect_reject("영양소(B12) 미명시 거부",
                  cn(VALID.replace("비타민B12", "○○").replace("B12 보충 권유 없음", "보충 권유 없음"))[1],
                  "F6 영양소")
    expect_reject("mechanism 미명시 거부",
                  cn(VALID.replace("mechanism/action: absorption/separation(F4) · depletion/monitoring(F6). ", "")
                     .replace("= al_mg_antacid", "= 카테고리"))[1], "mechanism/action 결정")
    expect_reject("Al-only ack 누락 거부",
                  cn(VALID.replace("알루미늄 함유 제산제만 명시(Mg 미명시) — Al-only copy_change 인지·display Mg 비단정", "기록")
                     .replace("al_mg_antacid(알루미늄 함유 제산제)", "al_mg_antacid"))[1], "aluminum-only")
    expect_reject("0275 ack 누락 거부",
                  cn(VALID.replace("케토코나졸(F10): 국내 외용 전용·수출용 source → route/availability needs_review, 본 승인 대상 아님(통합 제외).\n", ""))[1],
                  "RF-F10-0275")
    expect_reject("verified_reference 누락 거부",
                  cn(VALID.replace("verified_reference 노출로", "참고 노출로").replace("verified_reference 천장 유지", "천장 유지")
                     .replace("verified_reference 노출 동의.", "노출 동의."))[1], "verified_reference")
    expect_reject("clinical=true 아님 명시 누락 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ", ""))[1],
                  "clinical_reviewed=true 아님")
    expect_reject("제품 추천 아님 명시 누락 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음. ", ""))[1], "제품 추천 아님")
    expect_reject("보충 권유 아님 명시 누락 거부",
                  cn(VALID.replace("B12 보충 권유 없음", "추가 안내 없음"))[1], "보충/영양제 복용 권유 아님")
    expect_reject("SAMPLE 토큰 거부", cn(VALID + "\nAPPROVED-SAMPLE-NOT-VALID")[1], "SAMPLE")
    expect_reject("placeholder 거부", cn(VALID + "\n검토일 YYYY-MM-DD")[1], "placeholder")
    expect_reject("clinical=true 승격 요구 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ",
                                   "clinical_reviewed=true 로 승격 승인. "))[1], "승격 요구")
    expect_reject("제품 추천 허용 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음.", "제품 추천 허용함."))[1], "제품/보충 추천 허용")
    expect_reject("B12 보충 권유 허용 거부",
                  cn(VALID.replace("B12 보충 권유 없음.", "B12 보충 권장함."))[1], "보충/복용 권유/권장 허용")
    expect_reject("검사/처방 지시 허용 거부",
                  cn(VALID + "\n정기 혈액 검사 지시 문구 허용함.")[1], "검사/처방/투여 지시")
    expect_reject("외용→경구 일반화 허용 거부",
                  cn(VALID + "\n케토코나졸 외용 제품에도 일반화 적용 승인.")[1], "일반화")
    expect_accept("valid 노트(integrable) 통과", cn(VALID)[1])
    # scope 불일치 — needs_review 0275 추가 요구 시 candidate 미명시
    expect_reject("scope 불일치(0275 추가 요구) 거부",
                  mod.check_reviewer_note(_note(tmp, VALID), integ_ids + ["RF-F10-0275"])[1], "candidate_id 미명시")


def temp_write(mod, tmp, scope_label, scope_ids, expected_after, expected_ids):
    print(f"--- temp-copy 전체 write (scope={scope_label}, valid 노트 — live 무수정) ---")
    real = mod.EXPORT
    before = _sha(real)
    work = tempfile.mkdtemp(prefix="ms_sf_write_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid(scope_label, scope_ids))
        mod.EXPORT = tmp_export
        argv = ["prog", "--pm-approved", "--reviewer-note", note]
        if scope_label.startswith("family:"):
            argv += ["--scope", scope_label]
        else:
            argv += ["--scope", "integrable"]
        sys.argv = argv
        rc = mod.main()
        data = json.load(open(tmp_export, encoding="utf-8"))
        cnt = len(data["relations"])
        new_rels = [r for r in data["relations"] if r["id"] in expected_ids]
        new_ids = sorted(r["id"] for r in new_rels)
        ok_rc, ok_cnt = rc == 0, cnt == expected_after
        ok_meta = data["meta"].get("relation_count") == expected_after
        ok_ids = new_ids == expected_ids
        ok_safe = all(r.get("product_link_allowed") is False and r.get("potassium_safety_card") is False
                      and r.get("requires_clinical_review") is False and "reviewed_by" not in r
                      for r in new_rels)

        def shape_ok(r):
            nut = r.get("nutrient", "")
            if "제산제" in nut:
                return (r.get("mechanism") == "absorption" and r.get("recommended_action") == "separation"
                        and r.get("counterpart_category") == "al_mg_antacid" and "마그네슘" not in r.get("display_text_ko", ""))
            if nut == "비타민B12":
                return (r.get("mechanism") == "depletion" and r.get("recommended_action") == "monitoring"
                        and "counterpart_category" not in r)
            return False
        ok_shape = all(shape_ok(r) for r in new_rels)
        for c, n in ((ok_rc, "rc=0"), (ok_cnt, f"temp relations {expected_after}"),
                     (ok_meta, f"meta.relation_count {expected_after}"), (ok_ids, f"신규 id {expected_ids}"),
                     (ok_safe, "신규 product/kcard/clinical=false·reviewed_by 부재"),
                     (ok_shape, "absorption/separation·al_mg·Mg비단정 / depletion/monitoring·B12·category부재")):
            ok = bool(c)
            print(("  PASS " if ok else "  FAIL ") + f"{scope_label}: {n}" + ("" if ok else f" (rc={rc} cnt={cnt} ids={new_ids})"))
            if not ok:
                fails.append(f"{scope_label}:{n}")
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    ok_live = before == _sha(real)
    print(("  PASS " if ok_live else "  FAIL ") + f"{scope_label}: live export sha256 불변(무수정)")
    if not ok_live:
        fails.append(f"{scope_label}:live unchanged")


def test_needs_review_block(mod, tmp):
    print("--- needs_review 통합 차단 (--candidate-ids 0275 STOP) ---")
    real = mod.EXPORT
    before = _sha(real)
    integ_ids = mod._integrable_ids(mod.load_bundle()[0])
    work = tempfile.mkdtemp(prefix="ms_sf_nr_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid("integrable", integ_ids + ["RF-F10-0275"]))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--candidate-ids", "RF-F4-0173,RF-F10-0275"]
        rc = mod.main()
        ok = rc == 1
        print(("  PASS " if ok else "  FAIL ") + "0275(needs_review) 통합 요청 STOP" + ("" if ok else f" rc={rc}"))
        if not ok:
            fails.append("needs_review block")
        ok2 = len(json.load(open(tmp_export, encoding="utf-8"))["relations"]) == 60
        print(("  PASS " if ok2 else "  FAIL ") + "STOP 시 temp export relations 60(미기록)")
        if not ok2:
            fails.append("needs_review block no-write")
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    if before != _sha(real):
        fails.append("needs_review block live unchanged")


def test_idempotency(mod, tmp):
    print("--- idempotency (이미 존재 시 STOP) ---")
    real = mod.EXPORT
    before = _sha(real)
    integ_ids = mod._integrable_ids(mod.load_bundle()[0])
    work = tempfile.mkdtemp(prefix="ms_sf_idem_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid("integrable", integ_ids))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--scope", "integrable"]
        mod.main()
        rc2 = mod.main()
        ok = rc2 == 1
        print(("  PASS " if ok else "  FAIL ") + "integrable 재실행 STOP(이미 live)" + ("" if ok else f" rc2={rc2}"))
        if not ok:
            fails.append("idempotency STOP")
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    if before != _sha(real):
        fails.append("idempotency live unchanged")


def main():
    mod = _load("integrate_f4_f6_f10_small_family_batch_v1_4.py")
    tmp = tempfile.mkdtemp(prefix="ms_sf_gate_")
    try:
        print("=== F4/F6/F10 small-family reviewer-note 게이트 회귀 테스트 (live 무수정) ===")
        test_gate(mod, tmp)
        temp_write(mod, tmp, "integrable", ["RF-F4-0173", "RF-F6-0201"], 62, [62, 63])
        temp_write(mod, tmp, "family:F4", ["RF-F4-0173"], 61, [62])
        temp_write(mod, tmp, "family:F6", ["RF-F6-0201"], 61, [62])
        test_needs_review_block(mod, tmp)
        test_idempotency(mod, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — invalid 전건 거부 + valid 통과 · temp write integrable 60→62(id 62,63)·family:F4/F6 60→61 · "
          "needs_review(0275) 통합 차단 · scope 불일치 거부 · idempotency STOP · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
