#!/usr/bin/env python3
"""
test_f2_tetracycline_reviewer_note_gate_v1_4.py
MediStack — F2 테트라사이클린 live 통합 reviewer-note **인터록 회귀 테스트**(읽기전용·네트워크 0).

검증 대상: integrate_f2_tetracycline_batch_v1_4.check_reviewer_note + (temp-copy) 전체 write 경로.
  1) 게이트 단위 — invalid(빈/토큰없음/candidate 일부 누락/scope 불일치/SAMPLE/placeholder/clinical=true 요구/
     제품 추천 허용/금속이온·제산제·우유 복용 권유 허용/al_mg_antacid 미명시(Mg nutrient·antacid 혼동)/overlap 판단 누락/
     pediatric·계열 일반화 허용/verified_reference 없음/reviewer 식별자 없음/grouping·간격 누락) 거부 + valid 통과.
  2) temp-copy 전체 write — valid 노트로 --pm-approved --reviewer-note 를 **임시 복사본** export 에 실행해
     all5 60→65 / nutrient2 60→62 / antacid3 60→63 동작 + **실제 live export sha256 불변** 확인.
  3) idempotency — 같은 scope 재실행 시 이미 존재 → STOP(드라이런 전제 위반 가드).
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


def build_valid(mod, scope_label, scope_ids):
    ids_line = ", ".join(scope_ids)
    grouping = {"all5": "grouping: all5 한 번에 통합", "nutrient2": "grouping: by-counterpart nutrient subset",
               "antacid3": "grouping: by-counterpart al_mg_antacid subset"}[scope_label]
    return (
        f"검수자: RPH-TEST-001 (PM 승인 근거 첨부)  검토일 2026-07-01\n"
        f"승인(approved): F2 테트라사이클린 {scope_label} 후보를 verified_reference 노출로 승인.\n"
        f"scope: {scope_label} 범위. 승인 candidate_id 전건: {ids_line}.\n"
        f"{grouping}.\n"
        f"category 결정: Al/Mg 함유 제산제는 al_mg_antacid(약물 counterpart·id61 선례) — 마그네슘 영양제 아님.\n"
        f"독시/미노 nutrient-overlap 판단: 기존 ×칼슘/철분/마그네슘/아연 영양소 relation 과 정보 중복 아닌 "
        f"제산제 제품 맥락으로 추가 노출 승인.\n"
        f"separation 간격(2~4시간) 카드 노출: 일반 '분리' 안내 유지(구체 시간 비노출).\n"
        f"clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. "
        f"금속이온·제산제·우유·유제품 복용 권유 없음.\n"
    )


def test_gate(mod, tmp):
    print("--- F2 게이트 (check_reviewer_note) ---")
    recs, _s = mod.load_f2()
    ids_all = [r["candidate_id"] for r in recs]
    nutrient, antacid = mod._scope_split(recs)
    VALID = build_valid(mod, "all5", ids_all)
    cn = lambda txt, ids=ids_all: mod.check_reviewer_note(_note(tmp, txt), ids)

    expect_reject("빈 노트 거부", cn("")[1], "비공란")
    expect_reject("승인 토큰 없음 거부",
                  cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    expect_reject("candidate_id 일부 누락 거부", cn(VALID.replace(ids_all[0] + ", ", ""))[1], "candidate_id 미명시")
    expect_reject("reviewer 식별자 없음 거부",
                  cn(VALID.replace("검수자: RPH-TEST-001 (PM 승인 근거 첨부)  ", ""))[1], "reviewer 식별자")
    expect_reject("scope 선언 누락 거부", cn(VALID.replace("scope:", "대상:").replace(" 범위.", "."))[1], "scope 선언")
    expect_reject("grouping 결정 누락 거부",
                  cn(VALID.replace("grouping: all5 한 번에 통합", "통합 방식 미정"))[1], "grouping")
    expect_reject("al_mg_antacid 미명시(Mg nutrient/antacid 혼동) 거부",
                  cn(VALID.replace("al_mg_antacid(약물 counterpart·id61 선례) — 마그네슘 영양제 아님",
                                   "제산제 분류 미정"))[1], "al_mg_antacid")
    expect_reject("독시/미노 nutrient-overlap 판단 누락 거부",
                  cn(VALID.replace("독시/미노 nutrient-overlap 판단: 기존 ×칼슘/철분/마그네슘/아연 영양소 relation 과 정보 중복 아닌 "
                                   "제산제 제품 맥락으로 추가 노출 승인.\n", ""))[1], "overlap")
    expect_reject("separation 간격 결정 누락 거부",
                  cn(VALID.replace("separation 간격(2~4시간) 카드 노출: 일반 '분리' 안내 유지(구체 시간 비노출).\n", ""))[1],
                  "간격")
    expect_reject("verified_reference 누락 거부",
                  cn(VALID.replace("verified_reference 노출로", "참고 노출로").replace("verified_reference 천장 유지", "천장 유지"))[1],
                  "verified_reference")
    expect_reject("clinical=true 아님 명시 누락 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ", ""))[1],
                  "clinical_reviewed=true 아님")
    expect_reject("제품 추천 아님 명시 누락 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음. ", ""))[1], "제품 추천 아님")
    expect_reject("금속이온 복용 권유 아님 명시 누락 거부",
                  cn(VALID.replace(" 금속이온·제산제·우유·유제품 복용 권유 없음.", ""))[1], "복용 권유 아님")
    expect_reject("SAMPLE 토큰 거부", cn(VALID + "\nAPPROVED-SAMPLE-NOT-VALID")[1], "SAMPLE")
    expect_reject("placeholder 거부", cn(VALID + "\n검토일 YYYY-MM-DD")[1], "placeholder")
    expect_reject("clinical=true 승격 요구 거부",
                  cn(VALID.replace("clinical_reviewed=true 아님(verified_reference 천장 유지). ",
                                   "clinical_reviewed=true 로 승격 승인. "))[1], "승격 요구")
    expect_reject("제품 추천 허용 거부",
                  cn(VALID.replace("제품·구매·제휴 추천 없음.", "제품 추천 허용함."))[1], "제품/보충 추천 허용")
    expect_reject("금속이온/제산제/유제품 복용 권유 허용 거부",
                  cn(VALID.replace("금속이온·제산제·우유·유제품 복용 권유 없음.", "철분 보충 권장함."))[1], "복용 권유/권장 허용")
    expect_reject("pediatric/계열 일반화 허용 거부",
                  cn(VALID + "\n소아·골형성 문맥 테트라사이클린 계열 일반화 승인.")[1], "일반화 허용")
    expect_accept("valid 노트(all5) 통과", cn(VALID)[1])
    # scope 불일치 — nutrient2 ids 로 antacid3 scope 검증(antacid ids 누락 감지)
    expect_reject("scope 불일치(nutrient2 노트를 antacid3 scope 로) 거부",
                  mod.check_reviewer_note(_note(tmp, build_valid(mod, "nutrient2", nutrient)), antacid)[1],
                  "candidate_id 미명시")
    expect_accept("valid 노트(nutrient2) 통과",
                  mod.check_reviewer_note(_note(tmp, build_valid(mod, "nutrient2", nutrient)), nutrient)[1])
    expect_accept("valid 노트(antacid3) 통과",
                  mod.check_reviewer_note(_note(tmp, build_valid(mod, "antacid3", antacid)), antacid)[1])


def temp_write(mod, tmp, scope_label, expected_after, expected_ids):
    print(f"--- temp-copy 전체 write (scope={scope_label}, valid 노트 — live 무수정) ---")
    real = mod.EXPORT
    before = _sha(real)
    recs, _s = mod.load_f2()
    nutrient, antacid = mod._scope_split(recs)
    scope_ids = {"all5": [r["candidate_id"] for r in recs], "nutrient2": nutrient, "antacid3": antacid}[scope_label]
    work = tempfile.mkdtemp(prefix="ms_f2_write_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        note = _note(tmp, build_valid(mod, scope_label, scope_ids))
        mod.EXPORT = tmp_export
        argv = ["prog", "--pm-approved", "--reviewer-note", note]
        if scope_label != "all5":
            argv += ["--scope", scope_label]
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
        ok_cat = all(("counterpart_category" in r) == ("제산제" in r.get("nutrient", "")) for r in new_rels)
        for c, n in ((ok_rc, "rc=0"), (ok_cnt, f"temp relations {expected_after}"),
                     (ok_meta, f"meta.relation_count {expected_after}"), (ok_ids, f"신규 id {expected_ids}"),
                     (ok_safe, "신규 product/kcard/clinical=false·reviewed_by 부재"),
                     (ok_cat, "제산제만 al_mg_antacid category·영양소 키 부재")):
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


def test_idempotency(mod, tmp):
    print("--- idempotency (이미 존재 시 STOP) ---")
    real = mod.EXPORT
    before = _sha(real)
    recs, _s = mod.load_f2()
    work = tempfile.mkdtemp(prefix="ms_f2_idem_")
    old_argv = sys.argv
    try:
        tmp_export = os.path.join(work, "export.json")
        shutil.copy(real, tmp_export)
        nutrient, _ = mod._scope_split(recs)
        note = _note(tmp, build_valid(mod, "nutrient2", nutrient))
        mod.EXPORT = tmp_export
        sys.argv = ["prog", "--pm-approved", "--reviewer-note", note, "--scope", "nutrient2"]
        mod.main()  # 1차 통합
        rc2 = mod.main()  # 2차 — 이미 존재 → build_subset viol → STOP(1)
        ok = rc2 == 1
        print(("  PASS " if ok else "  FAIL ") + "nutrient2 재실행 STOP(이미 live)" + ("" if ok else f" rc2={rc2}"))
        if not ok:
            fails.append("idempotency STOP")
    finally:
        mod.EXPORT = real
        sys.argv = old_argv
        shutil.rmtree(work, ignore_errors=True)
    if before != _sha(real):
        fails.append("idempotency live unchanged")


def main():
    mod = _load("integrate_f2_tetracycline_batch_v1_4.py")
    tmp = tempfile.mkdtemp(prefix="ms_f2_gate_")
    try:
        print("=== F2 테트라사이클린 reviewer-note 게이트 회귀 테스트 (live 무수정) ===")
        test_gate(mod, tmp)
        temp_write(mod, tmp, "all5", 65, list(range(62, 67)))
        temp_write(mod, tmp, "nutrient2", 62, list(range(62, 64)))
        temp_write(mod, tmp, "antacid3", 63, list(range(62, 65)))
        test_idempotency(mod, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — invalid 전건 거부 + valid 통과 · temp write all5/nutrient2/antacid3 동작 · "
          "scope 불일치 거부 · idempotency STOP · live export 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
