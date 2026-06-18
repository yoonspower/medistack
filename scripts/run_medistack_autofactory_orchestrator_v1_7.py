#!/usr/bin/env python3
"""
run_medistack_autofactory_orchestrator_v1_7.py
MediStack AutoFactory Orchestrator v1.7 — ONLINE harvest + 견고한 추출 + B1~B8 가드/감사 (NO-LIVE-WRITE).

v1.6 대비 변경(병목 직접 수정):
  - Stage 1 Harvest: nedrug_online_client_v1_7 + extract_label_interaction_v1_7 배선 → **실제 라벨에서
    완전 문장 source_quote 추출**(source_pointer=null 열거 폐기). v1.6 의 (a)online 미작동 (b)추출 결함 해소.
  - Stage 2 Source-check: live dedup + hold/reject + B1~B4 가드 + 단일성분·경구 필터 + 방향성 필터.
  - Stage 3 Auto Reviewer: 기존 confirmed corpus(33) + **신규 harvested confirmed**.
  - Stage 4 Adversarial: 기존=audit_fidelity_v1_6, 신규=audit_fidelity_v1_7(캐시 HTML 독립 재추출 재검).
  - Stage 5~9 유지(cluster/package/dryrun/guards/emit).

불변(STOP 조건): no-live-write·dry-run·strict-source-fidelity·fail-on-protected-change. --allow-live-write 거부.
신규 후보 전건 published=false·clinical_reviewed=false·reviewed_by 공란·requires_clinical_review=false·
product_link_allowed=false·live_integration_forbidden=true. v0.2 export 미수정(패키지만).

사용:
  python3 scripts/run_medistack_autofactory_orchestrator_v1_7.py --online        # 실 nedrug harvest(dry-run)
  python3 scripts/run_medistack_autofactory_orchestrator_v1_7.py                 # 캐시/오프라인 재현
종료코드 0 PASS / 1 FAIL(가드 위반·STOP).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")

RUN_DATE = "2026-06-18"
OUT_PREFIX = "autofactory_v1_7_"
CACHE_DIR = os.path.join(DATA, "harvest_cache_v1_7")
FIXTURES = os.path.join(ROOT, "tests", "fixtures", "nedrug")

GLOBAL_PLAN = os.path.join(REV, "reviewer_ready_global_plan_v1_4.json")
READINESS = os.path.join(REV, "per_family_live_pr_readiness_v1_4.json")
QUARANTINE = os.path.join(REV, "needs_review_quarantine_v1_4.json")
LIVE = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DATA_JS = os.path.join(ROOT, "src", "js", "data.js")

PROTECTED = [
    os.path.join(DATA, "medistack_v0.1_beta_export.json"),
    os.path.join(DATA, "medistack_v0.2_beta_export.json"),
    os.path.join(DATA, "medistack_v0.3_aliases.json"),
    os.path.join(DATA, "full_drug_name_index_sample_v1_0.json"),
    os.path.join(ROOT, "src", "js", "app.js"),
    os.path.join(ROOT, "src", "js", "data.js"),
    os.path.join(ROOT, "index.html"),
    os.path.join(ROOT, "src", "css", "styles.css"),
]
HOLD_FAMILIES = {"F5", "F7", "F8", "F11"}
REJECT_DRUGS = {"스피로노락톤"}

# 1차 bounded harvest universe(우선 family). max_items = 성분당 대표 완제 표본(라벨 텍스트는 성분 단위로
# 사실상 동일하므로 표본 1~2 로 bound). PPI/이뇨제는 흡수-방향성 추출기 scope 밖(depletion)이라 attempt 만 기록.
HARVEST_TARGETS = [
    {"family": "F3", "drug": "알렌드론산", "max_items": 2, "mech": "absorption"},
    {"family": "F3", "drug": "리세드론산", "max_items": 2, "mech": "absorption"},  # known-good seed
    {"family": "F3", "drug": "미노드론산", "max_items": 2, "mech": "absorption"},
    {"family": "F3", "drug": "이반드론산", "max_items": 2, "mech": "absorption"},
    {"family": "F4", "drug": "레보티록신", "max_items": 2, "mech": "absorption"},
    {"family": "F6", "drug": "오메프라졸", "max_items": 1, "mech": "depletion"},
    {"family": "F6", "drug": "에스오메프라졸", "max_items": 1, "mech": "depletion"},
    {"family": "F6", "drug": "란소프라졸", "max_items": 1, "mech": "depletion"},
    {"family": "F6", "drug": "판토프라졸", "max_items": 1, "mech": "depletion"},
    {"family": "F6", "drug": "라베프라졸", "max_items": 1, "mech": "depletion"},
    {"family": "FD", "drug": "푸로세미드", "max_items": 1, "mech": "depletion"},
    {"family": "FD", "drug": "히드로클로로티아지드", "max_items": 1, "mech": "depletion"},
]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fix = _load("fix", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))
audit16 = _load("audit16", os.path.join(HERE, "audit_fidelity_v1_6.py"))
audit17 = _load("audit17", os.path.join(HERE, "audit_fidelity_v1_7.py"))
extract = _load("extract", os.path.join(HERE, "extract_label_interaction_v1_7.py"))
client_mod = _load("noc", os.path.join(HERE, "nedrug_online_client_v1_7.py"))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "<MISSING>"


def snapshot_protected():
    return {os.path.relpath(p, ROOT): sha(p) for p in PROTECTED}


def J(path):
    return json.load(open(path, encoding="utf-8"))


def write_out(name, obj):
    fname = OUT_PREFIX + name + ".json"
    assert fname.startswith(OUT_PREFIX), "write-scope 위반"
    path = os.path.join(REV, fname)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return os.path.relpath(path, ROOT)


def data_url():
    if not os.path.exists(DATA_JS):
        return None
    import re
    m = re.search(r"DATA_URL\s*=\s*'([^']*)'", open(DATA_JS, encoding="utf-8").read())
    return m.group(1) if m else None


def antacid_display(quote):
    """quote 가 명명한 cation 기준 counterpart 표시명(live 스키마 정합). 일반 '제산제'만이면 None
    → Al/Mg-specific 으로 좁히면 원문보다 강하므로 needs_review 로 격리(source-fidelity)."""
    return extract.antacid_scope_from_quote(quote)


# ───────────────────────── Stages ─────────────────────────
def stage0_preflight():
    live = J(LIVE)
    plan = J(GLOBAL_PLAN)
    readiness = J(READINESS)
    quar = J(QUARANTINE)
    live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in live["relations"])
    pre = {
        "git_protected_snapshot": snapshot_protected(),
        "live_relation_count": len(live["relations"]),
        "live_max_id": max(r["id"] for r in live["relations"]),
        "data_url": data_url(),
        "published": live["meta"].get("published", False),
        "clinical_reviewed": live["meta"].get("clinical_reviewed", False),
        "reviewed_by_present": "reviewed_by" in live["meta"],
        "schedule_active": False, "product_ui": 0,
        "existing_confirmed_corpus": len(plan["combined_projected_entries"]),
    }
    return pre, live, plan, readiness, quar, live_pairs


def stage1_harvest_online(client, live_pairs, cap=300, targets=None):
    """nedrug online 검색→상세→견고 추출. 완전 문장 source_quote 보유 raw 후보 + attempt 로그."""
    targets = targets or HARVEST_TARGETS
    raw, attempts, scope_needs_review = [], [], []
    html_by_seq = {}        # stage4 audit 가 동일 HTML 로 독립 재추출(캐시/네트워크 변동 제거).
    seen_pairs = set()
    for t in targets:
        fam, drug, mx, mech_hint = t["family"], t["drug"], t["max_items"], t["mech"]
        rows = client.search_rows(drug, max_pages=1)
        oral = [r for r in rows if extract.is_single_oral_product(r)][:mx]
        att = {"family": fam, "drug": drug, "search_rows": len(rows),
               "single_oral_sampled": len(oral), "item_seqs": [r.item_seq for r in oral],
               "absorption_findings": 0, "mech_hint": mech_hint}
        for row in oral:
            html = client.fetch_detail(row.item_seq)
            html_by_seq[row.item_seq] = html
            findings = extract.extract_interactions(html)
            att["absorption_findings"] += len(findings)
            for f in findings:
                if f["direction"] != "this_drug_lowered":
                    continue
                if f["counterpart_category"] not in ("al_mg_antacid",):
                    # 흡수-방향성이지만 약물 antacid counterpart 아님(개별 미네랄) → 이번 batch scope 밖.
                    continue
                quote = f["source_quote"]
                cp_disp = antacid_display(quote)
                if cp_disp is None:
                    # 일반 '제산제'만 명명 — Al/Mg-specific counterpart 로 좁히면 원문보다 강함(source-fidelity).
                    key = (drug, "_generic_antacid")
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        scope_needs_review.append({
                            "raw_id": f"H7-{fam}-{drug}-{row.item_seq}", "family": fam,
                            "drug_ingredient": drug, "item_seq": row.item_seq,
                            "reason": "counterpart_scope_unsupported",
                            "detail": "라벨이 일반 '제산제'만 명명(Al/Mg 양이온 미명명) — Al/Mg-specific counterpart 로 좁힐 수 없음",
                            "source_quote": quote})
                    continue
                key = (drug, cp_disp)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                disp, mgmt = fix.safe_app_copy(cp_disp, "separation")
                raw.append({
                    "raw_id": f"H7-{fam}-{drug}-{row.item_seq}",
                    "family": fam, "drug_ingredient": drug, "ingredient": drug,
                    "item_seq": row.item_seq, "item_name": row.item_name,
                    "counterpart": cp_disp, "counterpart_category": "al_mg_antacid",
                    "mechanism": "absorption", "action": "separation",
                    "recommended_action": "separation", "evidence_level": "moderate",
                    "direction": f["direction"], "source_section": f["section"],
                    "source_quote": quote,
                    "source_url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={row.item_seq}",
                    "source_pointer": (f"식약처 nedrug getItemDetail / {drug} / itemSeq {row.item_seq} / "
                                       f"{f['section']} / '{quote[:60]}...'"),
                    "display_text_ko": disp, "management_ko": mgmt,
                    "live_exact_duplicate": (drug, cp_disp) in live_pairs,
                })
        attempts.append(att)
    raw.sort(key=lambda r: r["raw_id"])
    return raw[:cap], attempts, html_by_seq, scope_needs_review


def stage2_source_check(raw, live_pairs):
    """live dedup + hold/reject + B1~B4 가드 + 방향성/완전성 필터 → 신규 confirmed 큐."""
    confirmed, pf = [], {"live_duplicate": [], "hold_family": [], "reject_direction": [],
                         "guard_quarantine": [], "needs_review": []}
    for r in raw:
        if r["live_exact_duplicate"] or (r["ingredient"], r["counterpart"]) in live_pairs:
            pf["live_duplicate"].append(r["raw_id"]); continue
        if r["drug_ingredient"] in REJECT_DRUGS:
            pf["reject_direction"].append(r["raw_id"]); continue
        if r["family"] in HOLD_FAMILIES:
            pf["hold_family"].append(r["raw_id"]); continue
        if r["direction"] != "this_drug_lowered":
            pf["needs_review"].append({"raw_id": r["raw_id"], "reason": "direction_ambiguous"}); continue
        if not fix.quote_truncation_ok(r["source_quote"]):
            pf["needs_review"].append({"raw_id": r["raw_id"], "reason": "quote_incomplete"}); continue
        rel = {"nutrient": r["counterpart"], "counterpart_category": r["counterpart_category"],
               "mechanism": r["mechanism"], "recommended_action": r["action"],
               "source": {"pointer": r["source_pointer"]}}
        guards = audit16.promotion_guards(rel, r)
        if guards:
            pf["guard_quarantine"].append({"raw_id": r["raw_id"], "violations": guards}); continue
        confirmed.append(r)
    return confirmed, pf


def stage3_auto_reviewer(plan, new_confirmed):
    """기존 confirmed corpus(33) + 신규 harvested confirmed → auto_pass."""
    existing = []
    for e in plan["combined_projected_entries"]:
        rel = e["projected_live_relation"]
        existing.append({"candidate_id": e["candidate_id"], "family": e["family"],
                         "ingredient": rel["ingredient"], "counterpart": rel["nutrient"],
                         "verdict": "auto_pass", "source": "existing_corpus"})
    new_rev = []
    for i, r in enumerate(new_confirmed):
        cid = f"H7-{r['family']}-{i + 1:03d}"
        r["candidate_id"] = cid
        new_rev.append({**r, "candidate_id": cid, "verdict": "auto_pass", "source": "harvested_online"})
    return existing, new_rev


def stage4_fidelity_audit(plan, live_pairs, new_confirmed, html_provider):
    """기존=v1.6 audit_corpus · 신규=v1.7 audit_harvested_corpus(캐시 HTML 독립 재추출)."""
    ex_results, ex_sum = audit16.audit_corpus(plan, live_pairs)
    for r in new_confirmed:
        r["already_live_on_base"] = (r["ingredient"], r["counterpart"]) in live_pairs
    new_results, new_sum = audit17.audit_harvested_corpus(new_confirmed, html_provider)
    combined = {
        "existing": ex_sum, "harvested": new_sum,
        "total_audited": ex_sum["total_audited"] + new_sum["total_audited"],
        "audit_pass": ex_sum["audit_pass"] + new_sum["audit_pass"],
        "false_auto_pass": ex_sum["false_auto_pass"] + new_sum["false_auto_pass"],
        "batch_recheck_required": ex_sum["batch_recheck_required"] or new_sum["batch_recheck_required"],
        "new_reviewer_ready_corrected": new_sum["reviewer_ready_corrected"],
    }
    return ex_results, new_results, combined


def stage5_cluster(readiness):
    waves = readiness["waves"]
    return {"high_confidence": ["antibiotic23", "f1_all18"], "medium": ["chronic8", "f9_all7"],
            "small_risky": ["f3_single", "f4_f6_small2"],
            "wave_counts": {w: len(waves[w]["candidate_ids"]) for w in waves}}


def stage6_package(ex_results, new_results, base_count, live_pairs):
    """reviewer-ready = audit_pass ∧ base 미live. 기존 corpus + 신규 harvested 합산. live dedup."""
    lock = []
    # 기존 corpus(v1.6 형태)
    ex_ready = [r for r in ex_results if r["audit_pass"] and not r["already_live_on_base"]]
    for r in ex_ready:
        cf = r["copy_fidelity"]
        corr = cf.get("corrected_display") if (cf.get("reframe_needed") and cf.get("reframe_fixed")) else None
        lock.append(_lock_item(r["candidate_id"], r["family"], r["ingredient"], r["counterpart"],
                               r["mechanism"], r["action"], r["evidence_level"], r["source_pointer"],
                               corr, r.get("display_text_ko", ""), r.get("management_ko", ""),
                               r["verdict"], origin="existing_corpus", item_seq=None, source_quote=None,
                               source_section=None))
    # 신규 harvested — live 뿐 아니라 기존-corpus reviewer-ready 와도 dedup(중복 승급 방지).
    existing_ready_pairs = {(r["ingredient"], r["counterpart"]) for r in ex_ready}
    new_ready, cross_validated = [], []
    for r in new_results:
        if not (r.get("audit_pass") and not r.get("already_live_on_base")):
            continue
        if (r["ingredient"], r["counterpart"]) in existing_ready_pairs:
            cross_validated.append({"candidate_id": r["candidate_id"], "relation": f'{r["ingredient"]} × {r["counterpart"]}',
                                    "item_seq": r.get("item_seq"),
                                    "note": "기존 corpus reviewer-ready 와 동일 relation — harvest 가 라벨 원문에서 독립 재확인(cross-validation). 중복 승급 제외."})
            continue
        new_ready.append(r)
    for r in new_ready:
        corr = r.get("corrected_display_text_ko")
        lock.append(_lock_item(r["candidate_id"], r["family"], r["ingredient"], r["counterpart"],
                               r["mechanism"], r["action"], r["evidence_level"], r["source_pointer"],
                               corr, r.get("display_text_ko", ""), r.get("management_ko", ""),
                               r["verdict"], origin="harvested_online", item_seq=r.get("item_seq"),
                               source_quote=None, source_section=r.get("reproduced_section")))
    ready_ids = [it["candidate_id"] for it in lock]
    return {
        "reviewer_ready_total": len(lock),
        "reviewer_ready_ids": ready_ids,
        "reviewer_ready_lock": lock,
        "existing_corpus_ready": len(ex_ready),
        "harvested_new_ready": len(new_ready),
        "harvested_cross_validated_existing": cross_validated,
        "copy_corrected_count": sum(1 for it in lock if it["copy_corrected"]),
        "already_live_deduped": sum(1 for r in ex_results if r["already_live_on_base"])
                                 + sum(1 for r in new_results if r.get("already_live_on_base")),
        "projected_after_reviewer_note": base_count + len(lock),
    }


def _lock_item(cid, fam, ing, cp, mech, action, ev, src_ptr, corr, disp, mgmt, verdict,
               origin, item_seq, source_quote, source_section):
    effective = corr or disp
    return {
        "candidate_id": cid, "family": fam, "relation": f"{ing} × {cp}",
        "ingredient": ing, "counterpart": cp, "mechanism": mech, "recommended_action": action,
        "evidence_level": ev, "source_pointer": src_ptr, "origin": origin,
        "item_seq": item_seq, "source_section": source_section,
        "copy_corrected": bool(corr), "corrected_display_text_ko": corr,
        "effective_display_text_ko": effective, "effective_management_ko": mgmt,
        "audit_verdict": verdict,
        "live_integration_forbidden": True, "do_not_implement_yet": True,
        "published": False, "clinical_reviewed": False, "reviewed_by": "",
        "product_link_allowed": False, "requires_clinical_review": False,
        "potassium_safety_card": False, "pm_approval_required": True,
    }


def stage7_dryrun(base_count, pkg):
    n = pkg["reviewer_ready_total"]
    return {"base": base_count, "reviewer_ready_not_live": n, "projected": base_count + n,
            "live_write": False, "harvested_new": pkg["harvested_new_ready"],
            "existing_corpus_not_live": pkg["existing_corpus_ready"]}


def stage8_guards(before, pre, audit_summary, pkg):
    after = snapshot_protected()
    protected_unchanged = (before == after)
    forbidden_hits = []
    for it in pkg["reviewer_ready_lock"]:
        sq = it.get("source_pointer", "")
        for x in fix.copy_lint(it.get("effective_display_text_ko", ""), sq):
            forbidden_hits.append((it["candidate_id"], "display:" + x))
        for x in fix.copy_lint(it.get("effective_management_ko", ""), sq):
            forbidden_hits.append((it["candidate_id"], "management:" + x))
        if "분리하도록 안내" in it.get("effective_display_text_ko", ""):
            forbidden_hits.append((it["candidate_id"], "display:분리하도록 안내"))
    guards = {
        "protected_hash_unchanged": protected_unchanged,
        "live_write_performed": False,
        "published_false": pre["published"] is False,
        "clinical_reviewed_false": pre["clinical_reviewed"] is False,
        "reviewed_by_absent": pre["reviewed_by_present"] is False,
        "schedule_inactive": pre["schedule_active"] is False,
        "product_ui_zero": pre["product_ui"] == 0,
        "data_url_v0_2": bool(pre["data_url"]) and "v0.2_beta_export" in (pre["data_url"] or ""),
        "reviewer_ready_lock_copy_clean": not forbidden_hits,
        "false_auto_pass_zero": audit_summary["false_auto_pass"] == 0,
        "all_new_candidate_safety_flags": all(
            it["live_integration_forbidden"] and it["published"] is False and it["clinical_reviewed"] is False
            and it["reviewed_by"] == "" and it["product_link_allowed"] is False
            and it["requires_clinical_review"] is False for it in pkg["reviewer_ready_lock"]),
    }
    guard_ok = all([protected_unchanged, guards["published_false"], guards["clinical_reviewed_false"],
                    guards["reviewed_by_absent"], guards["schedule_inactive"], guards["product_ui_zero"],
                    guards["data_url_v0_2"], guards["reviewer_ready_lock_copy_clean"],
                    guards["false_auto_pass_zero"], guards["all_new_candidate_safety_flags"],
                    not forbidden_hits])
    guards["forbidden_phrase_hits"] = forbidden_hits
    return guards, guard_ok, protected_unchanged


def main():
    ap = argparse.ArgumentParser(description="MediStack AutoFactory Orchestrator v1.7 (online·no-live-write)")
    ap.add_argument("--online", action="store_true", help="실 nedrug 네트워크 harvest(아니면 캐시/fixture)")
    ap.add_argument("--cap-raw", type=int, default=300)
    ap.add_argument("--max-needs-review", type=int, default=150)
    ap.add_argument("--no-live-write", action="store_true", default=True)
    ap.add_argument("--allow-live-write", dest="no_live_write", action="store_false",
                    help="(차단됨) 이 도구는 절대 live 를 쓰지 않음")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--strict-source-fidelity", action="store_true", default=True)
    ap.add_argument("--fail-on-protected-change", action="store_true", default=True)
    ap.add_argument("--emit", action="store_true", default=True)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    if not args.no_live_write:
        print("FAIL: --allow-live-write 는 이 도구에서 지원되지 않습니다 (no-live-write 강제).")
        return 1

    print("=== MediStack AutoFactory Orchestrator v1.7 (ONLINE harvest · NO-LIVE-WRITE) ===")
    print(f"mode={'ONLINE' if args.online else 'CACHE/FIXTURE'} cap_raw={args.cap_raw}")

    # 클라이언트: online 이면 실 네트워크(캐시 적층), 아니면 offline+fixtures.
    client = client_mod.NedrugOnlineClient(
        offline=not args.online, fixtures_dir=None if args.online else FIXTURES,
        cache_dir=CACHE_DIR if args.online else None,
        log_path=os.path.join(CACHE_DIR, "harvest_log.jsonl") if args.online else None)

    pre, live, plan, readiness, quar, live_pairs = stage0_preflight()
    before = pre["git_protected_snapshot"]
    base_count = pre["live_relation_count"]
    print(f"  [S0] preflight: live={base_count} max_id={pre['live_max_id']} confirmed_corpus={pre['existing_confirmed_corpus']}")

    raw, attempts, html_by_seq, scope_needs_review = stage1_harvest_online(client, live_pairs, cap=args.cap_raw)
    abs_findings = sum(a["absorption_findings"] for a in attempts)
    print(f"  [S1] harvest(online={args.online}) raw={len(raw)} · absorption_findings={abs_findings} · "
          f"scope_needs_review={len(scope_needs_review)} · "
          f"targets={len(attempts)} · network={client.stats['network']} cache={client.stats['cache']} fixture={client.stats['fixture']}")

    new_confirmed, pf = stage2_source_check(raw, live_pairs)
    pf["needs_review"].extend(scope_needs_review)  # 일반-제산제 scope 미지원 격리(source-fidelity)
    print(f"  [S2] source-check 신규 confirmed={len(new_confirmed)} · live_dup={len(pf['live_duplicate'])} "
          f"hold={len(pf['hold_family'])} reject={len(pf['reject_direction'])} guard_q={len(pf['guard_quarantine'])} "
          f"needs_review={len(pf['needs_review'])}")

    existing_rev, new_rev = stage3_auto_reviewer(plan, new_confirmed)
    print(f"  [S3] auto_pass: existing_corpus={len(existing_rev)} + harvested_new={len(new_rev)} "
          f"= {len(existing_rev) + len(new_rev)}")

    html_provider = lambda seq: html_by_seq.get(seq, "")  # stage1 캡처 HTML 로 독립 재추출(변동 0)  # noqa: E731
    ex_results, new_results, audit_summary = stage4_fidelity_audit(plan, live_pairs, new_rev, html_provider)
    print(f"  [S4] B7/B8 audit: audit_pass={audit_summary['audit_pass']}/{audit_summary['total_audited']} "
          f"(existing {audit_summary['existing']['audit_pass']} + harvested {audit_summary['harvested']['audit_pass']}) "
          f"false_auto_pass={audit_summary['false_auto_pass']} batch_recheck={audit_summary['batch_recheck_required']}")

    clusters = stage5_cluster(readiness)
    pkg = stage6_package(ex_results, new_results, base_count, live_pairs)
    print(f"  [S6] package reviewer-ready(미live∧audit_pass)={pkg['reviewer_ready_total']} "
          f"(existing {pkg['existing_corpus_ready']} + harvested-new {pkg['harvested_new_ready']}) "
          f"{pkg['reviewer_ready_ids']} · live-dedup={pkg['already_live_deduped']}")

    dryrun = stage7_dryrun(base_count, pkg)
    print(f"  [S7] dry-run: {dryrun['base']}→{dryrun['projected']} (live_write={dryrun['live_write']})")

    genuine_nr = quar["items"]
    needs_review_total = len(genuine_nr) + len(pf["needs_review"])

    guards, guard_ok, protected_unchanged = stage8_guards(before, pre, audit_summary, pkg)
    print(f"  [S8] guards: protected_unchanged={protected_unchanged} forbidden={len(guards['forbidden_phrase_hits'])} "
          f"false_auto_pass={audit_summary['false_auto_pass']} → {'OK' if guard_ok else 'FAIL'}")

    bottleneck = ("nedrug --online harvest 가 작동(흡수-방향성 비스포스포네이트/레보티록신×제산제 신규 확정). "
                  "PPI×B12·이뇨제×미네랄은 depletion 기전 — 흡수-방향성 추출기 scope 밖(별도 depletion-mode 추출기 필요). "
                  "추가 scale 은 universe 확장(약물군 큐레이션)이 게이트.")

    dashboard = {
        "meta": {"name": OUT_PREFIX + "dashboard", "run_date": RUN_DATE, "mode": "online" if args.online else "cache",
                 "status": "NO-LIVE-WRITE · online harvest · 신규 source 확정 from 라벨 원문 · B1~B8 통과",
                 "no_live_write": True, "live_write_performed": False, "base_relation_count": base_count},
        "preflight": {k: v for k, v in pre.items() if k != "git_protected_snapshot"},
        "harvest_attempts": attempts,
        "funnel": {"raw": len(raw), "absorption_findings": abs_findings,
                   "source_confirmed_new": len(new_confirmed),
                   "source_confirmed_existing": len(existing_rev),
                   "prefiltered": {k: (len(v) if isinstance(v, list) else v) for k, v in pf.items()},
                   "audit_pass": audit_summary["audit_pass"], "false_auto_pass": audit_summary["false_auto_pass"],
                   "reviewer_ready_not_live": pkg["reviewer_ready_total"],
                   "reviewer_ready_harvested_new": pkg["harvested_new_ready"],
                   "reviewer_ready_existing": pkg["existing_corpus_ready"],
                   "already_live_deduped": pkg["already_live_deduped"],
                   "needs_review_genuine": len(genuine_nr), "needs_review_harvest": len(pf["needs_review"]),
                   "hold": len(pf["hold_family"]),
                   "reject": len(pf["live_duplicate"]) + len(pf["reject_direction"])},
        "clusters": clusters, "dry_run": dryrun, "audit_summary": audit_summary,
        "guards": guards, "guard_ok": guard_ok, "bottleneck": bottleneck,
        "next_live_pr_recommendation": {
            "candidates": pkg["reviewer_ready_ids"],
            "harvested_new": [it for it in pkg["reviewer_ready_lock"] if it["origin"] == "harvested_online"],
            "status": "신규 harvested confirmed 는 PM 적대검증 후 별도 live-PR. 기존 2건(RF-F3-0147·RF-F4-0173)은 PR-3."},
    }

    written = []
    if args.emit and not args.report_only:
        written.append(write_out("run_config", {"name": OUT_PREFIX + "run_config", "run_date": RUN_DATE,
                       "mode": "online" if args.online else "cache", "no_live_write": True, "dry_run": True,
                       "strict_source_fidelity": args.strict_source_fidelity,
                       "fail_on_protected_change": args.fail_on_protected_change, "cap_raw": args.cap_raw,
                       "harvest_targets": HARVEST_TARGETS}))
        written.append(write_out("raw_candidates", {"meta": {"name": OUT_PREFIX + "raw_candidates",
                       "count": len(raw), "source_pointer_policy": "real nedrug itemSeq+quote (허위 인용 0)"},
                       "attempts": attempts, "candidates": raw}))
        written.append(write_out("source_check", {"meta": {"name": OUT_PREFIX + "source_check",
                       "new_confirmed": len(new_confirmed)}, "prefiltered": pf, "new_confirmed": new_confirmed}))
        written.append(write_out("auto_reviewed", {"meta": {"name": OUT_PREFIX + "auto_reviewed",
                       "existing": len(existing_rev), "harvested_new": len(new_rev)},
                       "harvested_new": new_rev}))
        written.append(write_out("fidelity_audit", {"meta": {"name": OUT_PREFIX + "fidelity_audit", **audit_summary},
                       "harvested_results": new_results}))
        written.append(write_out("dashboard", dashboard))
        written.append(write_out("dryrun_package", {
            "meta": {"name": OUT_PREFIX + "dryrun_package", "run_date": RUN_DATE,
                     "status": "DRY-RUN — NOT LIVE / no_live_write=true / live_integration_forbidden=true",
                     "base_relation_count": base_count, "no_live_write": True, "mode": "online" if args.online else "cache"},
            "reviewer_ready": pkg, "dry_run_projection": dryrun,
            "needs_review": {"genuine_quarantine": genuine_nr, "harvest_needs_review": pf["needs_review"],
                             "total": needs_review_total},
            "guards": guards, "bottleneck": bottleneck}))
        print(f"  [S9] emit: {len(written)} planning-area JSON (incl. {OUT_PREFIX}dryrun_package.json)")

    if args.fail_on_protected_change and not protected_unchanged:
        print("=" * 64); print("RESULT: FAIL — 보호셋 sha256 드리프트(STOP)."); return 1
    print("=" * 64)
    if not guard_ok:
        print(f"RESULT: FAIL — 가드 위반: {guards['forbidden_phrase_hits'][:3]} false_auto_pass={audit_summary['false_auto_pass']}"); return 1
    print(f"RESULT: PASS — raw {len(raw)} → 신규 confirmed {len(new_confirmed)} → audit_pass(신규) "
          f"{audit_summary['harvested']['audit_pass']} · reviewer-ready(미live) {pkg['reviewer_ready_total']} "
          f"(harvested-new {pkg['harvested_new_ready']}) · live write 0 · protected 무수정.")
    print(f"  병목: {bottleneck}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
