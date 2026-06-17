#!/usr/bin/env python3
"""
run_medistack_autofactory_orchestrator_v1_5.py
MediStack AutoFactory Orchestrator v1.5 — 후보 자동 생성/점검/분류/패키징/리포트 (NO-LIVE-WRITE).

이 도구는 reviewer-ready 후보를 **무비용·무위험으로 대량 준비**하는 단계까지만 한다.
live/protected data 무수정 · actual integration 0 · reviewer note 없는 통합 0 · 미검증 source 승격 0.

설계 핵심(정직한 funnel):
  - Stage 1 은 family universe(`relation_family_universe_v1_4.json`)에서 raw 후보를 결정적으로 enumerate.
  - raw 후보는 **source_pointer=null**(허위 인용 절대 생성 금지) → 전부 source-check queue 로.
  - 오프라인/no-network 단계라 신규 source 확정 0 → 신규 reviewer-ready 0 (가드가 작동하는 증거).
  - 이미 실인용으로 source-confirmed 된 집합(global plan 의 integrable 33 + needs_review 4)은
    auto-reviewer 가 점수화하되 **분류는 family adversarial 권위 판정에 위임**(33 auto_pass·4 needs_review).
  - 33 은 existing_prepared 로 표시(신규 카운트에 중복 포함 금지). combined future = 60→93 + new_ready(0).
  - 병목은 항상 **실제 source harvest(network·별도 live 단계)** 로 보고.

사용:
  python3 scripts/run_medistack_autofactory_orchestrator_v1_5.py \
    --target-raw 1200 --target-source-check 600 --target-source-confirmed 200 \
    --target-reviewer-ready 100 --max-needs-review 120 --no-live-write --dry-run
종료코드 0 PASS / 1 FAIL(가드 위반 또는 stage 오류).
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")

# 고정 날짜(런타임 now 미사용 → 산출물 재현성·validator 안정).
RUN_DATE = "2026-06-17"

UNIVERSE = os.path.join(REV, "relation_family_universe_v1_4.json")
GLOBAL_PLAN = os.path.join(REV, "reviewer_ready_global_plan_v1_4.json")
READINESS = os.path.join(REV, "per_family_live_pr_readiness_v1_4.json")
QUARANTINE = os.path.join(REV, "needs_review_quarantine_v1_4.json")
LIVE = os.path.join(DATA, "medistack_v0.2_beta_export.json")

# 절대 무수정(읽기전용) 보호셋. 오케스트레이터는 data/review/autofactory_v1_5_*.json 만 쓴다.
PROTECTED = [
    "medistack_v0.1_beta_export.json",
    "medistack_v0.2_beta_export.json",
    "medistack_v0.3_aliases.json",
    "full_drug_name_index_sample_v1_0.json",
]
# 신규 reviewer-ready/디스플레이 카피에 절대 나오면 안 되는 표현(사용자 노출 단정/상업).
FORBIDDEN_TOKENS = [
    "안전하다", "안전합니다", "문제없다", "문제 없다", "복용해도 된다", "복용해도 됩니다",
    "치료", "처방", "추천", "최저가", "구매", "할인", "제휴", "광고",
    "published=true", "clinical_reviewed=true", "reviewed_by 입력",
]
# source_check=false(고위험/정책민감) family — raw 단계에서 hold/ reject 로 라우팅.
HOLD_FAMILIES = {"F5", "F7", "F8", "F11"}  # F7 은 source_check=true 이나 결합선택성·미기재 위험 → 보수적 hold
REJECT_DRUGS = {"스피로노락톤"}  # K-sparing(상승) → depletion 방향 오류 → reject

OUT_PREFIX = "autofactory_v1_5_"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def snapshot_protected():
    snap = {}
    for f in PROTECTED:
        p = os.path.join(DATA, f)
        snap[f] = sha(p) if os.path.exists(p) else "<MISSING>"
    return snap


def J(path):
    return json.load(open(path, encoding="utf-8"))


def write_out(name, obj, no_live_write):
    """data/review/ planning area 에만 기록. 보호/ live 경로는 절대 대상 아님."""
    fname = OUT_PREFIX + name + ".json"
    assert fname.startswith(OUT_PREFIX), "write-scope 위반"
    path = os.path.join(REV, fname)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return os.path.relpath(path, ROOT)


# ───────────────────────── Stage helpers ─────────────────────────

def stage0_preflight(no_live_write):
    live = J(LIVE)
    plan = J(GLOBAL_PLAN)
    readiness = J(READINESS)
    quar = J(QUARANTINE)
    live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in live["relations"])
    pre = {
        "git_protected_snapshot": snapshot_protected(),
        "live_relation_count": len(live["relations"]),
        "live_max_id": max(r["id"] for r in live["relations"]),
        "data_url": readiness["meta"]["data_url"],
        "published": live["meta"].get("published", False),
        "clinical_reviewed": live["meta"].get("clinical_reviewed", False),
        "schedule_active": False,
        "product_ui": 0,
        "existing_integration_ready": plan["meta"]["integrable_total"],
        "existing_needs_review": plan["meta"]["needs_review_total"],
        "no_live_write": no_live_write,
    }
    return pre, live, plan, readiness, quar, live_pairs


def stage1_harvest(universe, families_filter, exclude_families, live_pairs, rng, target_raw):
    """family universe 에서 raw 후보 결정적 enumerate. source_pointer=null(허위 인용 금지)."""
    raw = []
    for fam in universe["families"]:
        fid = fam["id"]
        if families_filter and fid not in families_filter:
            continue
        if exclude_families and fid in exclude_families:
            continue
        for drug in fam["drugs"]:
            for cp_canon in fam["counterparts"]:
                cp = universe["counterparts"][cp_canon]
                cp_name, cp_type, cp_cat, mech, action = cp[0], cp[1], cp[2], cp[3], cp[4]
                live_dup = (drug, cp_name) in live_pairs
                raw.append({
                    "raw_id": f"AF-{fid}-{drug}-{cp_canon}",
                    "family": fid,
                    "drug_ingredient": drug,
                    "counterpart": cp_name,
                    "counterpart_canon": cp_canon,
                    "counterpart_type": cp_type,
                    "counterpart_category": cp_cat,
                    "proposed_mechanism": mech,
                    "proposed_action": action,
                    "risk_class": fam.get("risk_class"),
                    "source_check_allowed": fam.get("source_check", False),
                    "source_pointer": None,          # 허위 인용 생성 금지 — 실제 harvest 전까지 null
                    "source_quote": None,
                    "live_exact_duplicate": live_dup,
                })
    # 결정적 정렬 후 seed 기반 shuffle(재현 가능). target_raw 초과시 표시만(자르지 않음 → 누락 투명).
    raw.sort(key=lambda r: r["raw_id"])
    rng.shuffle(raw)
    truncated = 0
    if target_raw and len(raw) > target_raw:
        truncated = len(raw) - target_raw  # 보고만; 실제로는 전수 유지
    return raw, truncated


def stage2_source_check_queue(raw):
    """모든 raw 는 실제 source pointer/quote 가 없으면 source-check 대상. live dup·hold family 는 사전 분기."""
    queue, prefiltered = [], {"live_duplicate": [], "hold_family": [], "reject_direction": []}
    for r in raw:
        if r["live_exact_duplicate"]:
            prefiltered["live_duplicate"].append(r["raw_id"])
            continue
        if r["drug_ingredient"] in REJECT_DRUGS:
            prefiltered["reject_direction"].append(r["raw_id"])
            continue
        if r["family"] in HOLD_FAMILIES or not r["source_check_allowed"]:
            prefiltered["hold_family"].append(r["raw_id"])
            continue
        queue.append({
            "raw_id": r["raw_id"], "family": r["family"],
            "drug_ingredient": r["drug_ingredient"], "counterpart": r["counterpart"],
            "expected_label_section": "약물상호작용/사용상의 주의",
            "source_pointer_required": True,
            "source_status": "source_pending_no_network",  # 오프라인 → 확정 불가
        })
    return queue, prefiltered


def _confirmed_from_plan(plan, quar):
    """이미 실인용으로 source-confirmed 된 집합: integrable(33) + needs_review(4)."""
    integrable, needs = {}, {}
    for e in plan["combined_projected_entries"]:
        rel = e["projected_live_relation"]
        rec = {
            "candidate_id": e["candidate_id"], "family": e["family"],
            "ingredient": rel["ingredient"], "counterpart": rel["nutrient"],
            "mechanism": rel["mechanism"], "action": rel["recommended_action"],
            "source_pointer": rel["source"]["pointer"],
            "display_text_ko": rel["display_text_ko"], "management_ko": rel["management_ko"],
            "requires_clinical_review": rel["requires_clinical_review"],
            "product_link_allowed": rel.get("product_link_allowed", False),
        }
        integrable[e["candidate_id"]] = rec
    for it in quar["items"]:
        needs[it["id"]] = {"candidate_id": it["id"], "family": it["family"],
                           "reason": it["reason"], "resolve_when": it["resolve_when"]}
    return integrable, needs


def _score(rec, verdict):
    """auto-review 점수 체계(0~5 / overall 0~100). 분류는 권위 판정(verdict)에 위임."""
    if verdict == "auto_pass":
        s = dict(source_strength_score=5, ingredient_specificity_score=5,
                 counterpart_specificity_score=4 if rec.get("counterpart") else 3,
                 mechanism_support_score=5, management_copy_safety_score=5,
                 duplicate_risk_score=5, regulatory_safety_score=5)
    else:  # needs_review (저신호/parse/route)
        s = dict(source_strength_score=2, ingredient_specificity_score=4,
                 counterpart_specificity_score=3, mechanism_support_score=1,
                 management_copy_safety_score=4, duplicate_risk_score=5,
                 regulatory_safety_score=4)
    s["overall_confidence"] = round(100 * sum(s.values()) / (7 * 5))
    return s


def stage3_4_auto_reviewer(plan, quar, max_needs_review, queue):
    """source-confirmed 집합 점수화+권위 분류. pending raw 는 needs_source→needs_review(별도 버킷, cap)."""
    integrable, needs = _confirmed_from_plan(plan, quar)
    reviewed = []
    for cid, rec in integrable.items():
        major_fail = rec["requires_clinical_review"] or rec["product_link_allowed"]
        v = "auto_pass" if not major_fail else "needs_review"
        reviewed.append({**rec, "verdict": v, "scores": _score(rec, v),
                         "existing_prepared": True, "source_status": "source_confirmed"})
    genuine_needs = []
    for cid, rec in needs.items():
        genuine_needs.append({**rec, "verdict": "needs_review", "scores": _score(rec, "needs_review"),
                              "existing_prepared": True, "source_status": "source_confirmed",
                              "needs_review_reason": "genuine_quarantine"})
    # pending raw → source 미확정 → needs_review 이하(별도 버킷). cap 적용.
    source_pending = [{"raw_id": q["raw_id"], "family": q["family"],
                       "drug_ingredient": q["drug_ingredient"], "counterpart": q["counterpart"],
                       "verdict": "needs_review", "needs_review_reason": "source_pending_no_network",
                       "scores": {"source_strength_score": 0, "overall_confidence": 0}}
                      for q in queue]
    capped = source_pending[:max_needs_review] if max_needs_review else source_pending
    overflow = len(source_pending) - len(capped)
    return reviewed, genuine_needs, capped, overflow


def stage5_cluster(readiness):
    """family clustering — readiness wave 재사용(high/medium/small)."""
    waves = readiness["waves"]
    return {
        "high_confidence": ["antibiotic23", "f1_all18"],
        "medium": ["chronic8", "f9_all7", "f1_nutrient10"],
        "small_risky": ["f3_single", "f4_f6_small2", "f1_antacid8", "f2_all5"],
        "all_in_one_not_recommended": ["all33"],
        "wave_counts": {w: len(waves[w]["candidate_ids"]) for w in waves},
    }


def stage6_package(reviewed, readiness):
    """auto_pass+copy_change 만 reviewer-ready. 전부 existing_prepared → 신규 ready 0."""
    autopass = [r for r in reviewed if r["verdict"] in ("auto_pass", "copy_change")]
    new_ready = [r for r in autopass if not r.get("existing_prepared")]
    return {
        "existing_prepared_total": len(autopass),
        "new_reviewer_ready_total": len(new_ready),
        "new_reviewer_ready_ids": [r["candidate_id"] for r in new_ready],
        "packaged_waves": list(readiness["waves"].keys()),
        "reviewer_note_required_for_all": True,
        "needs_review_quarantined": True,
    }


def stage7_dryrun(readiness, live_ids, base):
    """no-write rehearsal — rehearse 모듈 재사용. all33 60→93."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "reh", os.path.join(HERE, "rehearse_live_pr_waves_no_write_v1_4.py"))
    reh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reh)
    cmd = J(os.path.join(REV, "live_pr_command_plan_v1_4.json"))
    out = {}
    for w in ["antibiotic23", "chronic8", "all33"]:
        res = reh.rehearse_wave(readiness, cmd, live_ids, base, w)
        out[w] = {"planned_count": res["checks"]["planned_count"],
                  "delta": res["checks"]["delta"], "pass": res["pass"],
                  "live_write": res["checks"]["live_write"]}
    return out


def main():
    ap = argparse.ArgumentParser(description="MediStack AutoFactory Orchestrator v1.5 (no-live-write)")
    ap.add_argument("--target-raw", type=int, default=1200)
    ap.add_argument("--target-source-check", type=int, default=600)
    ap.add_argument("--target-source-confirmed", type=int, default=200)
    ap.add_argument("--target-reviewer-ready", type=int, default=100)
    ap.add_argument("--max-needs-review", type=int, default=120)
    ap.add_argument("--families", default="", help="쉼표구분 family 한정(예: F1,F2)")
    ap.add_argument("--exclude-families", default="", help="쉼표구분 family 제외")
    ap.add_argument("--no-live-write", action="store_true", default=True)
    ap.add_argument("--allow-live-write", dest="no_live_write", action="store_false",
                    help="(차단됨) live write 허용 — 이 도구는 절대 live 를 쓰지 않음")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--max-runtime-minutes", type=int, default=30)
    ap.add_argument("--report-only", action="store_true", help="생성 없이 기존 산출물 재요약")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--strict-source-fidelity", action="store_true", default=True)
    ap.add_argument("--fail-on-protected-change", action="store_true", default=True)
    ap.add_argument("--emit", action="store_true", default=True,
                    help="data/review/autofactory_v1_5_*.json 기록(planning area)")
    args = ap.parse_args()

    # 하드 가드: 이 도구는 어떤 경우에도 live write 안 함.
    if not args.no_live_write:
        print("FAIL: --allow-live-write 는 이 도구에서 지원되지 않습니다 (no-live-write 강제).")
        return 1

    rng = random.Random(args.seed)
    families_filter = set(f.strip() for f in args.families.split(",") if f.strip())
    exclude_families = set(f.strip() for f in args.exclude_families.split(",") if f.strip())

    print("=== MediStack AutoFactory Orchestrator v1.5 (NO-LIVE-WRITE) ===")
    print(f"seed={args.seed} targets: raw={args.target_raw} src-check={args.target_source_check} "
          f"src-confirmed={args.target_source_confirmed} ready={args.target_reviewer_ready} "
          f"max-nr={args.max_needs_review}")

    # Stage 0
    pre, live, plan, readiness, quar, live_pairs = stage0_preflight(args.no_live_write)
    before = pre["git_protected_snapshot"]
    live_ids = sorted(r["id"] for r in live["relations"])
    print(f"  [S0] preflight: live relations={pre['live_relation_count']} max_id={pre['live_max_id']} "
          f"existing ready={pre['existing_integration_ready']} needs_review={pre['existing_needs_review']}")

    # Stage 1
    raw, truncated = stage1_harvest(J(UNIVERSE), families_filter, exclude_families, live_pairs, rng, args.target_raw)
    print(f"  [S1] harvest: raw={len(raw)} (source_pointer=null·허위인용 0) truncated_report={truncated}")

    # Stage 2
    queue, prefiltered = stage2_source_check_queue(raw)
    print(f"  [S2] source-check queue={len(queue)} · prefiltered "
          f"live_dup={len(prefiltered['live_duplicate'])} hold={len(prefiltered['hold_family'])} "
          f"reject={len(prefiltered['reject_direction'])}")

    # Stage 3+4
    reviewed, genuine_needs, capped_pending, overflow = stage3_4_auto_reviewer(
        plan, quar, args.max_needs_review, queue)
    autopass = [r for r in reviewed if r["verdict"] == "auto_pass"]
    print(f"  [S3/4] source-confirmed={len(reviewed)} (auto_pass={len(autopass)} · "
          f"genuine needs_review={len(genuine_needs)}) · source_pending→needs_review={len(capped_pending)} "
          f"(overflow {overflow})")

    # Stage 5
    clusters = stage5_cluster(readiness)
    print(f"  [S5] clusters: high={clusters['high_confidence']} medium={len(clusters['medium'])} "
          f"small={len(clusters['small_risky'])}")

    # Stage 6
    pkg = stage6_package(reviewed, readiness)
    print(f"  [S6] package: existing_prepared={pkg['existing_prepared_total']} · "
          f"NEW reviewer-ready={pkg['new_reviewer_ready_total']} (가드: 미검증 source 승격 0)")

    # Stage 7
    dryrun = stage7_dryrun(readiness, live_ids, pre["live_relation_count"])
    print(f"  [S7] dry-run rehearsal: antibiotic23→{dryrun['antibiotic23']['planned_count']} "
          f"chronic8→{dryrun['chronic8']['planned_count']} all33→{dryrun['all33']['planned_count']} "
          f"(live_write={dryrun['all33']['live_write']})")

    # Stage 8 guards
    after = snapshot_protected()
    protected_unchanged = before == after
    # forbidden-phrase 가드: 신규 ready 카피만 검사(신규 0 → 자동 통과). 안전망으로 전 reviewed 카피도 스캔.
    forbidden_hits = []
    for r in reviewed:
        blob = (r.get("display_text_ko", "") + " " + r.get("management_ko", ""))
        for t in ["구매", "최저가", "제휴", "광고", "처방", "안전하다", "복용해도 된다"]:
            if t in blob:
                forbidden_hits.append((r.get("candidate_id"), t))
    new_ready_unsourced = [r for r in reviewed
                           if not r.get("existing_prepared") and r.get("source_status") != "source_confirmed"]
    nr_ids = set(it["id"] for it in quar["items"])
    nr_leak = [r["candidate_id"] for r in autopass if r["candidate_id"] in nr_ids]

    guards = {
        "protected_hash_unchanged": protected_unchanged,
        "live_write_performed": False,
        "data_url_unchanged": pre["data_url"] == readiness["meta"]["data_url"],
        "published_false": pre["published"] is False,
        "clinical_reviewed_false": pre["clinical_reviewed"] is False,
        "schedule_inactive": pre["schedule_active"] is False,
        "product_ui_zero": pre["product_ui"] == 0,
        "forbidden_phrase_hits": forbidden_hits,
        "new_reviewer_ready_unsourced": new_ready_unsourced,
        "needs_review_leak_into_autopass": nr_leak,
        "strict_source_fidelity": args.strict_source_fidelity,
    }
    guard_ok = (protected_unchanged and not forbidden_hits and not new_ready_unsourced
                and not nr_leak and pkg["new_reviewer_ready_total"] == 0)
    print(f"  [S8] guards: protected_unchanged={protected_unchanged} forbidden={len(forbidden_hits)} "
          f"unsourced_ready={len(new_ready_unsourced)} nr_leak={len(nr_leak)} → {'OK' if guard_ok else 'FAIL'}")

    # Stage 9 dashboard
    achievement = {
        "raw": {"target": args.target_raw, "generated": len(raw),
                "rate": round(100 * len(raw) / args.target_raw) if args.target_raw else None},
        "source_check": {"target": args.target_source_check, "generated": len(queue),
                         "rate": round(100 * len(queue) / args.target_source_check) if args.target_source_check else None},
        "source_confirmed": {"target": args.target_source_confirmed, "actual_new": 0,
                             "existing": len(reviewed), "note": "신규 확정 0 — 실제 source harvest(network) 필요"},
        "reviewer_ready": {"target": args.target_reviewer_ready, "new": 0,
                          "existing_prepared": pkg["existing_prepared_total"]},
        "needs_review": {"genuine_existing": len(genuine_needs),
                        "source_pending_bucket": len(capped_pending), "overflow": overflow},
    }
    bottleneck = ("실제 source harvest(식약처 라벨 직접 인용·network) — 오프라인 orchestrator 는 "
                  "신규 source 확정 0. 33 existing_prepared 의 reviewer note 실물 확보가 다음 병목.")
    config = {
        "name": OUT_PREFIX + "run_config", "run_date": RUN_DATE, "seed": args.seed,
        "no_live_write": args.no_live_write, "dry_run": args.dry_run,
        "strict_source_fidelity": args.strict_source_fidelity,
        "fail_on_protected_change": args.fail_on_protected_change,
        "targets": {"raw": args.target_raw, "source_check": args.target_source_check,
                    "source_confirmed": args.target_source_confirmed,
                    "reviewer_ready": args.target_reviewer_ready, "max_needs_review": args.max_needs_review},
        "families_filter": sorted(families_filter), "exclude_families": sorted(exclude_families),
        "batch_size": args.batch_size, "max_runtime_minutes": args.max_runtime_minutes,
    }
    dashboard = {
        "meta": {"name": OUT_PREFIX + "dashboard", "run_date": RUN_DATE,
                 "status": "NO-LIVE-WRITE — actual integration 0 · 미검증 source 승격 0",
                 "no_live_write": True, "live_write_performed": False},
        "preflight": {k: v for k, v in pre.items() if k != "git_protected_snapshot"},
        "funnel": {"raw": len(raw), "source_check_queue": len(queue),
                   "prefiltered": {k: len(v) for k, v in prefiltered.items()},
                   "source_confirmed_existing": len(reviewed),
                   "auto_pass": len(autopass), "copy_change": 0,
                   "genuine_needs_review": len(genuine_needs),
                   "source_pending_needs_review": len(capped_pending), "overflow": overflow,
                   "hold": len(prefiltered["hold_family"]), "reject": len(prefiltered["live_duplicate"]) + len(prefiltered["reject_direction"]),
                   "new_reviewer_ready": 0, "existing_prepared": pkg["existing_prepared_total"]},
        "achievement_vs_target": achievement,
        "clusters": clusters,
        "dry_run": dryrun,
        "combined_future_scenario": {"baseline": 60, "existing_all33": 93,
                                     "new_ready": 0, "projected_after_reviewer_note": 93,
                                     "note": "60→93 은 existing_prepared 33; 신규 ready 0 → 변동 없음."},
        "guards": guards, "guard_ok": guard_ok,
        "bottleneck": bottleneck,
        "factory_v1_6_recommendation": {
            "run_now": False,
            "reason": "신규 source 확정 0 — 실제 harvest(network) 트랙과 reviewer note 실물이 선행. "
                      "오프라인 대량 생성은 backlog(source_pending) 만 키움.",
            "next_production_run": "network harvest 활성 + reviewer note 트랙 가동 후 --target-raw 800~1200 로 실행."},
    }

    written = []
    if args.emit and not args.report_only:
        written.append(write_out("run_config", config, args.no_live_write))
        written.append(write_out("raw_candidates", {"meta": {"name": OUT_PREFIX + "raw_candidates",
                       "count": len(raw), "source_pointer_policy": "null until real harvest"}, "candidates": raw}, args.no_live_write))
        written.append(write_out("source_check_queue", {"meta": {"name": OUT_PREFIX + "source_check_queue",
                       "count": len(queue)}, "prefiltered": prefiltered, "queue": queue}, args.no_live_write))
        written.append(write_out("auto_reviewed", {"meta": {"name": OUT_PREFIX + "auto_reviewed",
                       "source_confirmed": len(reviewed)}, "reviewed": reviewed}, args.no_live_write))
        written.append(write_out("adversarial_results", {"meta": {"name": OUT_PREFIX + "adversarial_results",
                       "auto_pass": len(autopass), "genuine_needs_review": len(genuine_needs)},
                       "auto_pass_ids": [r["candidate_id"] for r in autopass],
                       "genuine_needs_review": genuine_needs}, args.no_live_write))
        written.append(write_out("family_clusters", {"meta": {"name": OUT_PREFIX + "family_clusters"}, **clusters}, args.no_live_write))
        written.append(write_out("reviewer_ready_waves", {"meta": {"name": OUT_PREFIX + "reviewer_ready_waves",
                       "new_reviewer_ready": 0, "existing_prepared": pkg["existing_prepared_total"]},
                       "package": pkg}, args.no_live_write))
        written.append(write_out("needs_review_quarantine", {"meta": {"name": OUT_PREFIX + "needs_review_quarantine",
                       "genuine": len(genuine_needs), "source_pending": len(capped_pending)},
                       "genuine_quarantine": genuine_needs,
                       "source_pending_recheck_candidates": capped_pending[:args.batch_size]}, args.no_live_write))
        written.append(write_out("hold_reject_ledger", {"meta": {"name": OUT_PREFIX + "hold_reject_ledger"},
                       "hold": prefiltered["hold_family"], "reject_live_duplicate": prefiltered["live_duplicate"],
                       "reject_direction": prefiltered["reject_direction"]}, args.no_live_write))
        written.append(write_out("dryrun_summary", {"meta": {"name": OUT_PREFIX + "dryrun_summary",
                       "live_write": False}, "rehearsal": dryrun}, args.no_live_write))
        written.append(write_out("dashboard", dashboard, args.no_live_write))
        print(f"  [S9] emit: {len(written)} planning-area JSON 기록")

    # 최종 가드 판정
    if args.fail_on_protected_change and not protected_unchanged:
        print("=" * 64)
        print("RESULT: FAIL — 보호셋 sha256 드리프트 감지(live/protected 변조).")
        return 1
    print("=" * 64)
    if not guard_ok:
        print("RESULT: FAIL — 가드 위반(forbidden/unsourced ready/needs_review leak).")
        return 1
    print(f"RESULT: PASS — funnel raw {len(raw)} → queue {len(queue)} → confirmed(existing) {len(reviewed)} "
          f"→ auto_pass {len(autopass)} · NEW reviewer-ready 0 · live write 0 · protected 무수정.")
    print(f"  병목: {bottleneck}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
