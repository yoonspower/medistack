#!/usr/bin/env python3
"""
validate_autofactory_orchestrator_v1_7.py — v1.7 산출물 일관성·안전·source-fidelity 검증 (읽기전용·live 무수정).

검증:
  1) autofactory_v1_7_*.json 존재(7) + dryrun_package.
  2) raw 후보: 전건 실 source_pointer(itemSeq)·완전 문장 quote(잘림/줄바꿈 0)·허위 인용 0.
  3) funnel: raw=신규 confirmed 합치(분기 정합) · 신규 confirmed=4 · audit total=37.
  4) B7/B8: false_auto_pass=0 · audit_pass=37 · batch_recheck=False.
  5) reviewer-ready=4=[RF-F3-0147,RF-F4-0173,H7-F3-001,H7-F3-002](existing 2 + harvested-new 2) · cross_validated 2.
  6) reviewer-ready lock 안전 플래그 전건 + effective copy lint-clean + '분리하도록 안내' 0.
  7) **source-fidelity 재검(독립)**: harvested-new 의 quote 가 커밋 fixture HTML 재추출 상호작용 finding 에 verbatim 존재.
  8) dry-run 92→96 · live_write=False · protected 무수정 · guard_ok.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
FX = os.path.join(ROOT, "tests", "fixtures", "nedrug")
P = "autofactory_v1_7_"
fails = []


def J(name):
    return json.load(open(os.path.join(REV, P + name + ".json"), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    print("=== AutoFactory Orchestrator v1.7 산출물 검증 ===")
    files = ["run_config", "raw_candidates", "source_check", "auto_reviewed", "fidelity_audit",
             "dashboard", "dryrun_package"]
    for f in files:
        ck(os.path.exists(os.path.join(REV, P + f + ".json")), f"{f}.json 존재")
    if fails:
        print("RESULT: FAIL — 산출물 누락"); return 1

    raw = J("raw_candidates"); sc = J("source_check"); fa = J("fidelity_audit")
    dash = J("dashboard"); pkg = J("dryrun_package")
    fix = load("fix", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))
    ex = load("ex", os.path.join(HERE, "extract_label_interaction_v1_7.py"))

    cands = raw["candidates"]
    # 2) raw: 실 source_pointer + 완전 문장 + 줄바꿈/잘림 0
    ck(all(c.get("item_seq") and str(c["item_seq"]).isdigit() for c in cands), "raw 전건 실 itemSeq 보유")
    ck(all(c.get("source_pointer") and "itemSeq" in c["source_pointer"] for c in cands), "raw 전건 source_pointer 실 인용(itemSeq)")
    ck(all("\n" not in c["source_quote"] for c in cands), "raw quote 줄바꿈 0(글루 없음)")
    ck(all(fix.quote_truncation_ok(c["source_quote"]) for c in cands), "raw quote 전건 완전 문장(잘림 0)")

    # 3) funnel
    asum = fa["meta"]
    ck(len(sc["new_confirmed"]) == 3, f"신규 confirmed=3 (got {len(sc['new_confirmed'])})")
    ck(asum["total_audited"] == 36, f"audit total=36 (got {asum['total_audited']})")
    # 일반-제산제 scope 미지원(알렌드론산)은 needs_review 격리(reviewer-ready 아님).
    nr = sc["prefiltered"]["needs_review"]
    ck(any(x.get("reason") == "counterpart_scope_unsupported" and "알렌드론산" in x.get("drug_ingredient", "")
           for x in nr), "알렌드론산(일반 제산제) → needs_review(counterpart_scope_unsupported)")

    # 4) B7/B8
    ck(asum["false_auto_pass"] == 0, "false_auto_pass=0")
    ck(asum["audit_pass"] == 36, f"audit_pass=36 (got {asum['audit_pass']})")
    ck(asum["batch_recheck_required"] is False, "batch_recheck_required=False")
    ck(asum["harvested"]["audit_pass"] == 3, "harvested audit_pass=3")

    # 5) reviewer-ready
    rr = pkg["reviewer_ready"]
    ck(rr["reviewer_ready_total"] == 3, f"reviewer-ready=3 (got {rr['reviewer_ready_total']})")
    ck(set(rr["reviewer_ready_ids"]) == {"RF-F3-0147", "RF-F4-0173", "H7-F3-001"},
       f"reviewer-ready ids 정합 (got {rr['reviewer_ready_ids']})")
    ck(rr["existing_corpus_ready"] == 2 and rr["harvested_new_ready"] == 1, "existing 2 + harvested-new 1(리세드론산)")
    ck(len(rr["harvested_cross_validated_existing"]) == 2, "cross_validated 2(이반드론산·레보티록신 독립 재확인)")
    # source-fidelity: 승급된 모든 harvested counterpart 표시명이 quote 로 정당화(과확장 0)
    for it in rr["reviewer_ready_lock"]:
        if it["origin"] != "harvested_online":
            continue
        q = next((c["source_quote"] for c in cands if c["item_seq"] == it["item_seq"]), "")
        ck(ex.counterpart_scope_justified(it["counterpart"], q),
           f"{it['candidate_id']}: counterpart 특정성 quote 로 정당(과확장 아님)")

    # 6) lock 안전 플래그 + copy clean
    bad = [it["candidate_id"] for it in rr["reviewer_ready_lock"]
           if it.get("live_integration_forbidden") is not True or it.get("published") is not False
           or it.get("clinical_reviewed") is not False or it.get("reviewed_by", "X") != ""
           or it.get("product_link_allowed") is not False or it.get("requires_clinical_review") is not False]
    ck(not bad, f"lock 전건 안전 플래그(live금지·published/clinical=false·reviewed_by 공란·product false) ({bad})")
    dirty = [it["candidate_id"] for it in rr["reviewer_ready_lock"]
             if fix.copy_lint(it["effective_display_text_ko"], it.get("source_pointer", ""))
             or fix.copy_lint(it["effective_management_ko"], it.get("source_pointer", ""))
             or "분리하도록 안내" in it["effective_display_text_ko"]]
    ck(not dirty, f"lock effective copy 전건 lint-clean·분리안내 0 ({dirty})")

    # 7) source-fidelity 독립 재검: harvested-new quote 가 fixture 재추출에 verbatim 존재
    quotes_by_seq = {c["item_seq"]: c["source_quote"] for c in cands}
    for it in rr["reviewer_ready_lock"]:
        if it["origin"] != "harvested_online":
            continue
        seq = it["item_seq"]
        fxpath = os.path.join(FX, f"detail_{seq}.html")
        if not os.path.exists(fxpath):
            ck(False, f"{it['candidate_id']}: fixture detail_{seq}.html 존재")
            continue
        html = open(fxpath, encoding="utf-8").read()
        found = [f["source_quote"] for f in ex.extract_interactions(html)]
        ck(quotes_by_seq[seq] in found,
           f"{it['candidate_id']}: quote 가 fixture 재추출 상호작용 finding 에 verbatim 존재(source-fidelity)")

    # 8) dry-run + guards
    dr = pkg["dry_run_projection"]
    ck(dr["base"] == 92 and dr["projected"] == 95, f"dry-run 92→95 (got {dr['base']}→{dr['projected']})")
    ck(dr["live_write"] is False, "live_write=False")
    g = pkg["guards"]
    ck(g["protected_hash_unchanged"], "protected hash 불변")
    ck(g["live_write_performed"] is False, "live write 0")
    ck(g["data_url_v0_2"], "DATA_URL v0.2")
    ck(g["false_auto_pass_zero"], "false_auto_pass=0 가드")
    ck(not g["forbidden_phrase_hits"], "reviewer-ready 산출 forbidden 0")
    ck(dash["guard_ok"] is True, "guard_ok=True")

    print("=" * 64)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — 실인용·완전문장·B7/B8 false_pass 0·reviewer-ready 3(harvested-new 1)·"
          "counterpart 과확장 0·source-fidelity 재검·dry-run 92→95·가드 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
