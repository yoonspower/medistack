#!/usr/bin/env python3
"""
validate_global_reviewer_ready_dryrun_v1_4.py
MediStack — 글로벌 reviewer-ready 37 통합 **계획/조합 시나리오 검증**(읽기전용·no-live-write).
integrate_reviewer_ready_global_batch_v1_4.py(dry-run)의 계획 산출물 + check_global_reviewer_note 게이트 검증 +
결함주입으로 검증기 자체 입증.

검사:
  0) 안전: live export 무변경(relations==60·meta 60·published/clinical=false·sha 불변).
  1) family map: 37 = F1 18 + F2 5 + F3 3 + F4 1 + F6 1 + F9 8 + F10 1. family_reverified=[F1,F2,F3]·pending=[F4,F6,F9,F10].
  2) integrable: F1 18·F2 5·F3 1 = 24 · F3 needs_review 2 · pending 11.
  3) 조합 시나리오: F1 78·F2 65·F3 61·F1+F2 83·F1+F3 79·F2+F3 66·F1+F2+F3 84(disjoint·dedup 0).
  4) dedup_clean=true(교차 family·live 중복 0) · combined v0.2 sim PASS(재실행) · no_live_write=true.
  5) reviewer-note 게이트: pending family 요청 거부·per-family 위임 누락 거부·family 일반화 거부·승인 없음 거부 + valid 통과.
  6) 결함주입 → 전건 검출.
사용: python3 scripts/validate_global_reviewer_ready_dryrun_v1_4.py
종료코드: 0 PASS, 1 FAIL.
"""
import copy
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
PLAN = os.path.join(DATA, "review", "reviewer_ready_global_plan_v1_4.json")
LIVE_RELATIONS = 60
RR_TOTAL = 37
EXPECTED_RR = {"F1": 18, "F2": 5, "F3": 3, "F4": 1, "F6": 1, "F9": 8, "F10": 1}
EXPECTED_COMBOS = {"F1_only": 78, "F2_only": 65, "F3_only": 61, "F1+F2": 83,
                   "F1+F3": 79, "F2+F3": 66, "F1+F2+F3": 84}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = _load("g", "integrate_reviewer_ready_global_batch_v1_4.py")
integ = g.integ


def validate_plan(art, exp):
    bad = []
    meta = art.get("meta", {})
    if meta.get("no_live_write") is not True:
        bad.append("no_live_write != true")
    if meta.get("live_write_performed") is not False:
        bad.append("live_write_performed != false")
    if meta.get("export_sha_after_same") is not True:
        bad.append("export_sha_after_same != true")
    if meta.get("published") is not False or meta.get("clinical_reviewed") is not False:
        bad.append("published/clinical != false")
    if meta.get("reviewer_ready_total") != RR_TOTAL:
        bad.append(f"reviewer_ready_total != {RR_TOTAL}")
    rr = meta.get("reviewer_ready_by_family_adversarial", {})
    if rr != EXPECTED_RR:
        bad.append(f"family map != 기대 ({rr})")
    if sum(rr.values()) != RR_TOTAL:
        bad.append(f"family map 합 != {RR_TOTAL}")
    if meta.get("family_reverified") != ["F1", "F2", "F3"]:
        bad.append("family_reverified != [F1,F2,F3]")
    if sorted(meta.get("family_pending_reverify", [])) != ["F10", "F4", "F6", "F9"]:
        bad.append("family_pending_reverify != [F4,F6,F9,F10]")
    pf = meta.get("per_family", {})
    if pf.get("F1", {}).get("integrable_count") != 18:
        bad.append("F1 integrable != 18")
    if pf.get("F2", {}).get("integrable_count") != 5:
        bad.append("F2 integrable != 5")
    if pf.get("F3", {}).get("integrable_count") != 1:
        bad.append("F3 integrable != 1")
    if sorted(pf.get("F3", {}).get("needs_review_ids", [])) != ["RF-F3-0148", "RF-F3-0149"]:
        bad.append("F3 needs_review != [0148,0149]")
    for fam in ("F4", "F6", "F9", "F10"):
        if pf.get(fam, {}).get("family_reverified") is not False or pf.get(fam, {}).get("integrable_count") != 0:
            bad.append(f"{fam} pending 표기 오류")
    if meta.get("integrable_total") != 24:
        bad.append(f"integrable_total != 24 ({meta.get('integrable_total')})")
    combos = meta.get("combined_scenarios", {})
    for k, v in EXPECTED_COMBOS.items():
        if combos.get(k) != v:
            bad.append(f"combo {k} != {v} ({combos.get(k)})")
    if meta.get("dedup_clean") is not True:
        bad.append("dedup_clean != true")
    ded = meta.get("dedup", {})
    if any(ded.get("vs_live", {}).values()) or any(ded.get("cross_family", {}).values()):
        bad.append("dedup 비어있지 않음(중복 존재)")
    sim = meta.get("v0_2_sim_combined", {})
    if sim.get("combined_count") != 84 or sim.get("sim_passed") is not True:
        bad.append(f"combined v0.2 sim != (84,PASS) ({sim.get('combined_count')},{sim.get('sim_passed')})")
    # combined_projected_entries 24 · disjoint · 모두 통합 가능 family
    ents = art.get("combined_projected_entries", [])
    if len(ents) != 24:
        bad.append(f"combined_projected_entries != 24 ({len(ents)})")
    fams = {e.get("family") for e in ents}
    if not fams <= {"F1", "F2", "F3"}:
        bad.append(f"combined entries 에 통합 불가 family 포함 {fams}")
    pairs = [(e["projected_live_relation"]["ingredient"], e["projected_live_relation"]["nutrient"]) for e in ents]
    if len(set(pairs)) != len(pairs):
        bad.append("combined entries 내 중복 pair")
    return bad


def run_v0_2_combined(art, exp):
    sim = copy.deepcopy(exp)
    base_max = max(r["id"] for r in sim["relations"])
    nid = base_max
    for e in art["combined_projected_entries"]:
        rel = dict(e["projected_live_relation"])
        nid += 1
        rel["id"] = nid
        sim["relations"].append(rel)
    sim["meta"]["relation_count"] = len(sim["relations"])
    import shutil
    import subprocess
    tmp = tempfile.mkdtemp(prefix="ms_glob_")
    p = os.path.join(tmp, "sim.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, os.path.join(HERE, "validate_medistack_v0_2_export.py"), p],
                           capture_output=True, text=True)
        return r.returncode == 0, len(sim["relations"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _note(tmp, text):
    p = os.path.join(tmp, "gnote.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def test_gate(tmp):
    print("--- 글로벌 reviewer-note 게이트 ---")
    VALID = ("승인(approved): F1, F2, F3 통합 가능분을 per-family integrator(개별 reviewer-note 위임)로 진행 승인.\n"
             "F4/F6/F9/F10 은 family 재검증 선행 필요(본 글로벌 노트로 통합 불가).\n"
             "글로벌 노트는 family 선택·순서용이며 live write 는 per-family integrator 가 수행.\n")
    cn = lambda txt, sel=("F1", "F2", "F3"), blk=(): g.check_global_reviewer_note(_note(tmp, txt), list(sel), list(blk))

    def er(label, bad, must=None):
        ok = len(bad) > 0 and (must is None or any(must in b for b in bad))
        print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else f"  [bad={bad}]"))
        if not ok:
            fails.append("gate:" + label)

    def ea(label, bad):
        ok = len(bad) == 0
        print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else f"  [bad={bad}]"))
        if not ok:
            fails.append("gate:" + label)

    er("빈 노트 거부", cn("")[1], "비공란")
    er("승인 토큰 없음 거부", cn(VALID.replace("승인", "검토").replace("approved", "review"))[1], "승인 표기")
    er("family 명시 누락 거부", cn(VALID.replace("F1, F2, F3", "F1, F2"))[1], "F3 family 명시 누락")
    er("per-family 위임 누락 거부",
       cn(VALID.replace("per-family integrator(개별 reviewer-note 위임)", "글로벌 일괄").replace(
           "live write 는 per-family integrator 가 수행", "live write 진행"))[1], "per-family")
    er("pending 선행 미명시 거부",
       cn(VALID.replace("F4/F6/F9/F10 은 family 재검증 선행 필요(본 글로벌 노트로 통합 불가).\n", ""))[1], "재검증 선행")
    er("pending family 요청 거부", cn(VALID, sel=("F1", "F9"), blk=("F9",))[1], "pending family")
    er("family 일반화 허용 거부", cn(VALID + "\nfamily 계열 일반화 승인.")[1], "일반화")
    er("clinical=true 승격 거부", cn(VALID + "\nclinical_reviewed=true 승격.")[1], "clinical")
    ea("valid 글로벌 노트 통과", cn(VALID)[1])


def main():
    if not os.path.exists(PLAN):
        print(f"[FATAL] 계획 산출물 없음 — 먼저 integrate_reviewer_ready_global_batch_v1_4.py")
        return 1
    art = json.load(open(PLAN, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))

    ck(len(exp["relations"]) == LIVE_RELATIONS, "라이브 relations != 60")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, "라이브 meta != 60")
    ck(exp["meta"].get("published") is False and exp["meta"].get("clinical_reviewed") is False,
       "라이브 published/clinical != false")

    plan_bad = validate_plan(art, exp)
    ck(not plan_bad, f"plan 계약 위반: {plan_bad}")

    ok, cnt = run_v0_2_combined(art, exp)
    ck(ok, "combined 24 sim v0.2 FAIL")
    ck(cnt == 84, f"combined sim count != 84 ({cnt})")
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 변경됨")

    tmp = tempfile.mkdtemp(prefix="ms_glob_gate_")
    try:
        test_gate(tmp)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    # 결함주입(plan)
    print("--- 결함주입(검출되어야 PASS) ---")
    inj_fail = []

    def inject(label, mutate):
        a = copy.deepcopy(art)
        mutate(a)
        b = validate_plan(a, exp)
        ok2 = len(b) > 0
        print(("  PASS " if ok2 else "  FAIL ") + label + ("" if ok2 else "  [검출 실패]"))
        if not ok2:
            inj_fail.append(label)

    inject("no_live_write=false", lambda a: a["meta"].update(no_live_write=False))
    inject("family map 변조(F3 5)", lambda a: a["meta"]["reviewer_ready_by_family_adversarial"].update(F3=5))
    inject("F3 integrable 위조(3)", lambda a: a["meta"]["per_family"]["F3"].update(integrable_count=3))
    inject("pending family 통합가능 위조(F9 8)",
           lambda a: a["meta"]["per_family"]["F9"].update(family_reverified=True, integrable_count=8))
    inject("combo 위조(F1+F2+F3=90)", lambda a: a["meta"]["combined_scenarios"].update({"F1+F2+F3": 90}))
    inject("integrable_total 위조(37)", lambda a: a["meta"].update(integrable_total=37))
    inject("dedup_clean 위조(중복 주입)",
           lambda a: a["meta"]["dedup"]["cross_family"].update({"F1∩F2": ["x×y"]}))
    inject("combined entries 에 pending family(F9) 주입",
           lambda a: a["combined_projected_entries"].append({"family": "F9", "candidate_id": "RF-F9-0269",
                                                             "projected_live_relation": {"ingredient": "x", "nutrient": "y"}}))
    fails.extend(inj_fail)

    print(f"=== 글로벌 reviewer-ready 37 계획 검증: live relations {len(exp['relations'])}(불변) · "
          f"integrable 24(F1 18·F2 5·F3 1) · pending 11(F4/F6/F9/F10) · F3 needs_review 2 · F1+F2+F3 60→84 ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — family map 37(F1 18/F2 5/F3 3/F4 1/F6 1/F9 8/F10 1) · integrable 24 · pending 11 · "
          "조합 시나리오(78/65/61/83/79/66/84) · dedup_clean · combined v0.2 PASS(60→84) · no_live_write · "
          "게이트(pending/위임/일반화/승인) · 결함주입 검출 · 라이브 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
