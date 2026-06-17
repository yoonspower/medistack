#!/usr/bin/env python3
"""
validate_autofactory_orchestrator_v1_5.py
MediStack v1.5 — AutoFactory Orchestrator 산출물 일관성·안전 검증 (읽기전용·live 무수정).

검증:
  1) 11개 autofactory_v1_5_*.json 존재·로드.
  2) funnel 정합: raw ≥ source_check_queue ≥ 0 · confirmed = auto_pass + genuine_needs_review.
  3) 신규 reviewer-ready = 0 · existing_prepared = 33 (미검증 source 승격 0 가드).
  4) needs_review genuine 4건이 auto_pass/신규ready 에 누출 0.
  5) raw 후보 전건 source_pointer=null (허위 인용 생성 0).
  6) hold/reject 분기 ∪ queue ∪ confirmed = raw(누락/중복 없음).
  7) dry-run rehearsal all33 = 60→93 · live_write=False.
  8) guards: protected_unchanged·published/clinical=false·schedule inactive·product UI 0·forbidden 0.
  9) combined_future_scenario: new_ready 0 → 93 변동 없음.
종료코드 0 PASS / 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
P = "autofactory_v1_5_"
fails = []


def J(name):
    return json.load(open(os.path.join(REV, P + name + ".json"), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def main():
    print("=== AutoFactory Orchestrator v1.5 산출물 검증 ===")
    files = ["run_config", "raw_candidates", "source_check_queue", "auto_reviewed",
             "adversarial_results", "family_clusters", "reviewer_ready_waves",
             "needs_review_quarantine", "hold_reject_ledger", "dryrun_summary", "dashboard"]
    for f in files:
        ck(os.path.exists(os.path.join(REV, P + f + ".json")), f"{f}.json 존재")
    if fails:
        print("RESULT: FAIL — 산출물 누락"); return 1

    raw = J("raw_candidates")
    q = J("source_check_queue")
    ar = J("auto_reviewed")
    adv = J("adversarial_results")
    waves = J("reviewer_ready_waves")
    nrq = J("needs_review_quarantine")
    hr = J("hold_reject_ledger")
    dr = J("dryrun_summary")
    dash = J("dashboard")
    fn = dash["funnel"]

    n_raw = len(raw["candidates"])
    n_queue = len(q["queue"])
    reviewed = ar["reviewed"]
    autopass = [r for r in reviewed if r["verdict"] == "auto_pass"]
    genuine = adv["genuine_needs_review"]

    # 2) funnel 정합 (reviewed=integrable 33; genuine 4 는 adversarial 에 별도 추적)
    ck(n_raw >= n_queue >= 0, f"raw({n_raw}) ≥ source_check_queue({n_queue}) ≥ 0")
    ck(len(reviewed) == len(autopass), "auto_reviewed.reviewed = auto_pass(integrable)")
    confirmed_total = len(reviewed) + len(genuine)
    ck(confirmed_total == 37, f"source-confirmed total = integrable 33 + genuine needs_review 4 = {confirmed_total}")
    ck(fn["raw"] == n_raw and fn["source_check_queue"] == n_queue, "dashboard funnel 수치 일치")

    # 3) 신규 ready 0 / existing 33
    ck(waves["package"]["new_reviewer_ready_total"] == 0, "신규 reviewer-ready = 0 (미검증 source 승격 0)")
    ck(waves["package"]["existing_prepared_total"] == 33, "existing_prepared = 33")
    ck(len(autopass) == 33, "auto_pass = 33")
    ck(len(genuine) == 4, "genuine needs_review = 4")

    # 4) needs_review 누출 0
    nr_ids = set(g["candidate_id"] for g in genuine)
    ap_ids = set(r["candidate_id"] for r in autopass)
    ck(not (nr_ids & ap_ids), "genuine needs_review ∩ auto_pass = 0")
    ck(nr_ids == {"RF-F3-0148", "RF-F3-0149", "RF-F9-0245", "RF-F10-0275"}, "genuine needs_review 4건 정확")

    # 5) raw source_pointer=null
    ck(all(c["source_pointer"] is None and c["source_quote"] is None for c in raw["candidates"]),
       "raw 전건 source_pointer/quote=null (허위 인용 0)")

    # 6) 분기 합 = raw
    pf = q["prefiltered"]
    accounted = n_queue + len(pf["live_duplicate"]) + len(pf["hold_family"]) + len(pf["reject_direction"])
    ck(accounted == n_raw, f"queue+hold+reject 분기 합({accounted}) = raw({n_raw}) (누락/중복 0)")

    # 7) dry-run
    ck(dr["rehearsal"]["all33"]["planned_count"] == 93, "dry-run all33 = 60→93")
    ck(dr["rehearsal"]["antibiotic23"]["planned_count"] == 83, "dry-run antibiotic23 = 60→83")
    ck(dr["meta"]["live_write"] is False, "dry-run live_write = False")

    # 8) guards
    g = dash["guards"]
    ck(g["protected_hash_unchanged"], "protected hash 불변")
    ck(g["live_write_performed"] is False, "live write 0")
    ck(dash["preflight"]["published"] is False, "published=false")
    ck(dash["preflight"]["clinical_reviewed"] is False, "clinical_reviewed=false")
    ck(dash["preflight"]["schedule_active"] is False, "schedule 비활성")
    ck(dash["preflight"]["product_ui"] == 0, "product UI 0")
    ck(not g["forbidden_phrase_hits"], "forbidden phrase 0")
    ck(not g["new_reviewer_ready_unsourced"], "unsourced reviewer-ready 0")
    ck(not g["needs_review_leak_into_autopass"], "needs_review leak 0")
    ck(dash["guard_ok"] is True, "guard_ok = True")

    # 9) combined future
    cf = dash["combined_future_scenario"]
    ck(cf["new_ready"] == 0 and cf["projected_after_reviewer_note"] == 93,
       "combined future: new_ready 0 → 93 변동 없음")

    # hold/reject ledger 무모순
    ck(set(hr["reject_direction"]) and all("스피로노락톤" in x for x in hr["reject_direction"]) or not hr["reject_direction"],
       "reject_direction = K-sparing(스피로노락톤) 한정")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — funnel 정합 · 신규ready 0 · needs_review 격리 · 허위인용 0 · dry-run 60→93 · 가드 전부 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
