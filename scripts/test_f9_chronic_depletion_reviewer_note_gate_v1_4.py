#!/usr/bin/env python3
"""
test_f9_chronic_depletion_reviewer_note_gate_v1_4.py
MediStack — F9 만성복용 depletion live 통합 reviewer-note **인터록 회귀 테스트**(읽기전용·네트워크 0).

검증 대상: integrate_f9_chronic_depletion_batch_v1_4.check_reviewer_note + (temp-copy) 전체 write 경로 + needs_review 통합 차단.
  1) 게이트 단위 — invalid(빈/토큰없음/candidate 누락/scope 불일치/SAMPLE/placeholder/clinical=true 요구/제품 추천 허용/
     엽산·비타민D 보충 권유 허용/검사·처방 지시 허용/영양소 미명시/모니터링톤 미명시/장기framing 미명시/0245 ack 누락/
     verified_reference 없음/reviewer 식별자 없음/grouping 누락/소아·골·계열 일반화 허용) 거부 + valid 통과.
  2) temp-copy 전체 write — valid 노트로 integrable scope(7) 60→67(id 62..68) 동작 + **실제 live export sha256 불변**.
  3) needs_review 차단 — --candidate-ids 로 0245(needs_review) 요청 시 build_subset STOP(통합 거부).
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


def build_valid(scope_label, scope_ids):
    ids_line = ", ".join(scope_ids)
    grouping = {"integrable": "grouping: integrable subset 한 번에 통합",
                "folate": "grouping: by-nutrient 엽산 wave",
                "vitd": "grouping: by-nutrient 비타민D wave"}.get(scope_label, "grouping: subset 한 번에 통합")
    return (
        f"검수자: RPH-TEST-001 (PM 승인 근거 첨부)  검토일 2026-07-01\n"
        f"승인(approved): F9 만성복용 depletion {scope_label} 후보를 verified_reference 노출로 승인.\n"
        f"scope: {scope_label} 범위. 승인 candidate_id 전건: {ids_line}.\n"
        f"{grouping}.\n"
        f"영양소 대상: 엽산·비타민D(영양소 — 약물 category 없음). 모니터링 톤(참고정보·정기 확인 문의, "
        f"검사 지시 아님·처방 아님) 유지.\n"
        f"장기/연용 복용 framing: 라벨 연용 근거와 일치 확인(설파살라진은 '병용투여 시'이나 만성 IBD/RA 약 맥락).\n"
        f"카르바마제핀×엽산(저신호 이상반응 열거)은 needs_review — 본 승인 대상 아님.\n"
        f"clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. "
        f"엽산·비타민D 보충 권유 없음.\n"
        f"verified_reference 노출 동의.\n"
    )


def test_gate(mod, tmp):
    print("--- F9 게이트 (check_reviewer_note) ---")
    recs, _s = mod.load_f9()
    integ_ids = mod._survives_ids(recs)
    VALID = build_valid("integrable", integ_ids)
    cn = lambda txt, ids=integ_ids: mod.check_reviewer_note(_note(tmp, txt), ids)

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부",
                  cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    expect_reject("candidate_id 누락 거부", cn(VALID.replace("RF-F9-0269", "RF-F9-XXXX"))[1], "candidate_id 미명시")
    expect_reject("reviewer 식별자 없음 거부",
                  cn(VALID.replace("검수자: RPH-TEST-001 (PM 승인 근거 첨부)  ", ""))[1], "reviewer 식별자")
    expect_reject("scope 선언 누락 거부", cn(VALID.replace("scope:", "대상:").replace(" 범위.", "."))[1], "scope 선언")
    expect_reject("grouping 결정 누락 거부",
                  cn(VALID.replace("grouping: integrable subset 한 번에 통합", "통합 방식 미정"))[1], "grouping")
    expect_reject("영양소 대상 미명시 거부",
                  cn(VALID.replace("엽산", "○○").replace("비타민D", "○○").replace("비타민 D", "○○"))[1],
                  "영양소 monitoring 대상")
    expect_reject("모니터링 톤 미명시 거부",
                  cn(VALID.replace("모니터링 톤(참고정보·정기 확인 문의, 검사 지시 아님·처방 아님) 유지", "톤 미정"))[1],
                  "모니터링 톤")
    expect_reject("장기 framing 미명시 거부",
                  cn(VALID.replace("장기/연용 복용 framing: 라벨 연용 근거와 일치 확인(설파살라진은 '병용투여 시'이나 만성 IBD/RA 약 맥락).\n", "")
                     .replace("F9 만성복용 depletion", "F9 depletion"))[1], "장기/연용")
    expect_reject("0245 ack 누락 거부",
                  cn(VALID.replace("카르바마제핀×엽산(저신호 이상반응 열거)은 needs_review — 본 승인 대상 아님.\n", ""))[1],
                  "0245")
    expect_reject("verified_reference 누락 거부",
                  cn(VALID.replace("verified_reference 노출로", "참고 노출로").replace("verified_reference 천장 유지", "천장 유지")
                     .replace("verified_reference 노출 동의.", "노출 동의."))[1], "verified_reference")
    expect_reject("clinical=true 아님 명시 누락 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ", ""))[1],
                  "clinical_reviewed=true 아님")
    expect_reject("제품 추천 아님 명시 누락 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음. ", ""))[1], "제품 추천 아님")
    expect_reject("보충 권유 아님 명시 누락 거부",
                  cn(VALID.replace("엽산·비타민D 보충 권유 없음", "추가 안내 없음"))[1], "보충/영양제 복용 권유 아님")
    expect_reject("SAMPLE 토큰 거부", cn(VALID + "\nAPPROVED-SAMPLE-NOT-VALID")[1], "SAMPLE")
    expect_reject("placeholder 거부", cn(VALID + "\n검토일 YYYY-MM-DD")[1], "placeholder")
    expect_reject("clinical=true 승격 요구 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ",
                                   "clinical_reviewed=true 로 승격 승인. "))[1], "승격 요구")
    expect_reject("제품 추천 허용 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음.", "제품 추천 허용함."))[1], "제품/보충 추천 허용")
    expect_reject("엽산/비타민D 보충 권유 허용 거부",
                  cn(VALID.replace("엽산·비타민D 보충 권유 없음.", "엽산 보충 권장함."))[1], "보충/복용 권유/권장 허용")
    expect_reject("검사/처방 지시 허용 거부",
                  cn(VALID + "\n정기 혈액 검사 지시 문구 허용함.")[1], "검사/처방/투여 지시")
    expect_reject("소아/골/계열 일반화 허용 거부",
                  cn(VALID + "\n효소유도제 계열 일반화 승인.")[1], "일반화")
    expect_accept("valid 노트(integrable) 통과", cn(VALID)[1])
    # scope 불일치 — 다른 후보 id 요구(scope_ids 에 없는 needs_review id 요구 시 candidate 미명시)
    expect_reject("scope 불일치(0245 추가 요구) 거부",
                  mod.check_reviewer_note(_note(tmp, VALID), integ_ids + ["RF-F9-0245"])[1], "candidate_id 미명시")


def temp_write(mod, tmp, scope_label, expected_after, expected_ids):
    print(f"--- temp-copy 전체 write (scope={scope_label}, valid 노트 — live 무수정) ---")
    real = mod.EXPORT
    before = _sha(real)
    recs, _s = mod.load_f9()
    integ_ids = mod._survives_ids(recs)
    by_id = {r["candidate_id"]: r for r in recs}
    folate, vitd = mod._scope_split(recs)
    scope_ids = {"integrable": integ_ids, "folate": folate, "vitd": vitd}[scope_label]
    work = tempfile.mkdtemp(prefix="ms_f9_write_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid(scope_label, scope_ids))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--scope", scope_label]
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
        ok_shape = all(r.get("mechanism") == "depletion" and r.get("recommended_action") == "monitoring"
                       and r.get("nutrient") in ("엽산", "비타민D") and "counterpart_category" not in r
                       for r in new_rels)
        for c, n in ((ok_rc, "rc=0"), (ok_cnt, f"temp relations {expected_after}"),
                     (ok_meta, f"meta.relation_count {expected_after}"), (ok_ids, f"신규 id {expected_ids}"),
                     (ok_safe, "신규 product/kcard/clinical=false·reviewed_by 부재"),
                     (ok_shape, "depletion/monitoring·영양소·category 부재")):
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
    print("--- needs_review 통합 차단 (--candidate-ids 0245 STOP) ---")
    real = mod.EXPORT
    before = _sha(real)
    integ_ids = mod._survives_ids(mod.load_f9()[0])
    work = tempfile.mkdtemp(prefix="ms_f9_nr_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        # 0269+0245 명시 요청 — 0245 는 needs_review → build_subset viol → STOP(노트 검사 전 차단)
        note = _note(tmp, build_valid("integrable", integ_ids + ["RF-F9-0245"]))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--candidate-ids", "RF-F9-0269,RF-F9-0245"]
        rc = mod.main()
        ok = rc == 1
        print(("  PASS " if ok else "  FAIL ") + "0245(needs_review) 통합 요청 STOP" + ("" if ok else f" rc={rc}"))
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
    integ_ids = mod._survives_ids(mod.load_f9()[0])
    work = tempfile.mkdtemp(prefix="ms_f9_idem_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid("integrable", integ_ids))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--scope", "integrable"]
        mod.main()  # 1차 통합
        rc2 = mod.main()  # 2차 — 이미 존재 → build_subset viol → STOP(1)
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
    mod = _load("integrate_f9_chronic_depletion_batch_v1_4.py")
    tmp = tempfile.mkdtemp(prefix="ms_f9_gate_")
    try:
        print("=== F9 만성복용 depletion reviewer-note 게이트 회귀 테스트 (live 무수정) ===")
        test_gate(mod, tmp)
        temp_write(mod, tmp, "integrable", 67, [62, 63, 64, 65, 66, 67, 68])
        temp_write(mod, tmp, "folate", 63, [62, 63, 64])
        test_needs_review_block(mod, tmp)
        test_idempotency(mod, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — invalid 전건 거부 + valid 통과 · temp write integrable 60→67(id 62..68)·folate 60→63 · "
          "needs_review(0245) 통합 차단 · scope 불일치 거부 · idempotency STOP · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
