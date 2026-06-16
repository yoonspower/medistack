#!/usr/bin/env python3
"""
theme_map_harvest_provider_v1_3.py — harvester 의 **theme map expansion candidate provider**.

harvester(`harvest_relation_bot_v1_3.py`)가 `--include-theme-map-expansion` 플래그로 호출하는
**격리된 읽기 전용 provider**. 프롬프트 8 에서 source-check + 적대검증을 끝낸 신규 theme map
후보(draft 6 + hold 7)를 candidate-only 로 PM review queue 에 편입한다.

⚠️ 안전 불변:
  - **읽기만**: config(`data/config/theme_map_seeds_v1_3.json`) + source_of_truth 아티팩트(draft batch /
    candidates / adversarial ledger)만 읽는다. live/protected 무수정. SDK·네트워크 호출 0(직접 HTTP 없음).
  - **candidate-only**: 모든 행 live_integration_forbidden=true · published=false · clinical_reviewed=false ·
    reviewed_by 공란 · do_not_implement_yet=true. 어떤 행도 live relation·승격을 만들지 않는다.
  - **auto integrate 금지**: provider 는 큐·요약만 만든다. 통합은 PM + clinical reviewer 노트 후 별도.
  - runtime 산출물(`data/harvest_queue/theme_map_*`)은 커밋하지 않는다(.gitignore). 커밋되는 건
    review summary(`data/review/theme_map_harvest_incorporation_v1_3.json`)뿐.

사용:
  # 큐 생성(runtime) + 요약 갱신(committed)
  python3 scripts/theme_map_harvest_provider_v1_3.py --emit --summary-out data/review/theme_map_harvest_incorporation_v1_3.json
  # 요약만 stdout
  python3 scripts/theme_map_harvest_provider_v1_3.py --print-summary
종료코드: 0 정상 / 1 안전 위반(integrity/safety/consistency 실패).
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

CONFIG_PATH = os.path.join(REPO, "data/config/theme_map_seeds_v1_3.json")

# 권위있는 금지어 스캐너 재사용(봇/validator 와 동일).
_spec = importlib.util.spec_from_file_location(
    "vfp", os.path.join(HERE, "validate_forbidden_phrases_v1_2.py"))
vfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfp)

# 사용자 카피 안전 상수(theme map validator/smoke 와 동일 정책).
PRODUCT_PHRASES = ["구매", "구입", "제휴", "할인", "쿠폰", "최저가", "바로가기", "제품 링크", "제품링크"]
ANTICOAGULANT_TERMS = ["와파린", "항응고", "항혈소판", "INR", "혈액응고", "출혈 위험", "프로트롬빈"]
SUPPLEMENT_RECO_PHRASES = ["권장합니다", "권장됩니다", "복용을 권", "보충을 권", "섭취하세요",
                           "섭취하십시오", "드시는 것이 좋", "복용하는 것이 좋습니다", "보충제를 드"]
DRUG_CATEGORIES = {"acid_reducing_drug", "al_mg_antacid"}


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_config(path=CONFIG_PATH):
    return _load_json(path)


def load_artifacts(cfg):
    sot = cfg["meta"]["source_of_truth"]
    return {
        "draft_batch": _load_json(os.path.join(REPO, sot["draft_batch"])),
        "candidates": _load_json(os.path.join(REPO, sot["candidates"])),
        "adversarial": _load_json(os.path.join(REPO, sot["adversarial_ledger"])),
    }


def check_consistency(cfg, art):
    """config 의 confirmed/hold id 가 아티팩트와 1:1 인지(누락·유령 방지)."""
    errs = []
    cfg_confirmed = {s["candidate_id"] for s in cfg["confirmed_seeds"]}
    cfg_hold = {s["candidate_id"] for s in cfg["hold_seeds"]}
    draft_ids = {d["candidate_id"] for d in art["draft_batch"]["drafts"]}
    cand_by_id = {c["candidate_id"]: c for c in art["candidates"]["candidates"]}
    cand_confirmed = {cid for cid, c in cand_by_id.items()
                      if c.get("initial_status") == "source_confirmed_draft_candidate"}
    cand_hold = {cid for cid, c in cand_by_id.items() if c.get("initial_status") == "hold"}
    if cfg_confirmed != draft_ids:
        errs.append(f"config confirmed {sorted(cfg_confirmed)} != draft batch {sorted(draft_ids)}")
    if cfg_confirmed != cand_confirmed:
        errs.append(f"config confirmed != candidates source_confirmed {sorted(cand_confirmed)}")
    if cfg_hold != cand_hold:
        errs.append(f"config hold {sorted(cfg_hold)} != candidates hold {sorted(cand_hold)}")
    return errs


def build_confirmed_rows(cfg, art):
    """draft batch + adversarial ledger 를 PM 큐 행(candidate-only)으로."""
    adv_by_id = {a["candidate_id"]: a for a in art["adversarial"]["candidates"]}
    rows = []
    for d in art["draft_batch"]["drafts"]:
        cid = d["candidate_id"]
        adv = adv_by_id.get(cid, {})
        verdict = (d.get("adversarial_verified") or {}).get("verdict", "")
        rows.append({
            "candidate_id": cid,
            "track": "theme_map_expansion",
            "family": d.get("family", ""),
            "relation": f'{d.get("ingredient","")} × {d.get("nutrient","")}',
            "drug_ingredient": d.get("ingredient", ""),
            "counterpart": d.get("nutrient", ""),
            "counterpart_type": d.get("counterpart_type", ""),
            "counterpart_category": d.get("counterpart_category"),
            "mechanism": d.get("mechanism", ""),
            "recommended_action": d.get("recommended_action", ""),
            "evidence_level": d.get("evidence_level", ""),
            "confidence": d.get("confidence", ""),
            "risk_level": d.get("risk_level", "low"),
            "source_itemseq": str(d.get("source_itemseq", "")),
            "source_section": d.get("source_section", ""),
            "source_quote": d.get("source_quote", ""),
            "source_url": d.get("source_url", ""),
            "display_text_ko_draft": d.get("display_text_ko_draft", ""),
            "management_copy_draft": d.get("management_copy_draft", ""),
            "adversarial_verdict": verdict,
            "adversarial_next_action": adv.get("next_action", ""),
            "final_status": "draft_only (source_confirmed · adversarial_verified)",
            "recommended_pm_action": "PM REVIEW → reviewer note 후에만 live(자동 승격 금지)",
            "reviewer_needed": True,
            "product_link_allowed": d.get("product_link_allowed", False),
            "potassium_safety_card": d.get("potassium_safety_card", False),
            # candidate-only 안전 플래그(전건 고정)
            "do_not_implement_yet": True,
            "live_integration_forbidden": True,
            "published": False,
            "clinical_reviewed": False,
            "reviewed_by": "",
        })
    return rows


def build_hold_rows(cfg, art):
    cand_by_id = {c["candidate_id"]: c for c in art["candidates"]["candidates"]}
    rows = []
    for s in cfg["hold_seeds"]:
        cid = s["candidate_id"]
        c = cand_by_id.get(cid, {})
        rows.append({
            "candidate_id": cid,
            "drug_ingredient": s.get("drug_ingredient", ""),
            "counterpart": s.get("counterpart", ""),
            "family": c.get("family", ""),
            "hold_reason": s.get("hold_reason", ""),
            "required_source": c.get("required_source", ""),
            "final_status": "hold (draft 큐 제외)",
            "live_integration_forbidden": True,
            "published": False,
            "clinical_reviewed": False,
            "reviewed_by": "",
        })
    return rows


# ----- 안전 게이트 -----
def integrity_check(confirmed, holds):
    """어떤 행도 live/published/clinical 로 새지 않음을 기계 검증."""
    bad = []
    for r in confirmed + holds:
        if r.get("live_integration_forbidden") is not True or r.get("published") is not False \
           or r.get("clinical_reviewed") is not False or r.get("reviewed_by", "X") != "":
            bad.append(r.get("candidate_id"))
    for r in confirmed:
        if r.get("do_not_implement_yet") is not True:
            bad.append(r.get("candidate_id") + ":do_not_implement_yet")
    return bad


def safety_scan(confirmed):
    """사용자 카피의 금칙어·보충 권유·항응고 오인·제품 문구·category 오용을 스캔."""
    viol = []
    for r in confirmed:
        cid = r["candidate_id"]
        copy = f'{r.get("display_text_ko_draft","")} {r.get("management_copy_draft","")}'
        for bad in vfp.scan(copy):
            viol.append(f"{cid}:forbidden:{bad}")
        for p in PRODUCT_PHRASES:
            if p in copy:
                viol.append(f"{cid}:product:{p}")
        for p in SUPPLEMENT_RECO_PHRASES:
            if p in copy:
                viol.append(f"{cid}:supplement_reco:{p}")
        nut = r.get("counterpart", "")
        if ("지용성 비타민" in nut) or ("비타민 K" in nut) or ("·K" in nut):
            for t in ANTICOAGULANT_TERMS:
                if t in copy or t in r.get("source_quote", ""):
                    viol.append(f"{cid}:anticoagulant_framing:{t}")
        # counterpart_category 오용
        cat = r.get("counterpart_category")
        ctype = r.get("counterpart_type")
        if ctype == "antacid_drug":
            if cat not in DRUG_CATEGORIES:
                viol.append(f"{cid}:antacid_needs_drug_category:{cat}")
            if cat == "al_mg_antacid":
                viol.append(f"{cid}:acid_reducer_must_not_use_al_mg_antacid")
            if "약물" not in nut:
                viol.append(f"{cid}:antacid_counterpart_must_say_약물")
        if ctype in ("nutrient", "nutrient_group") and cat in DRUG_CATEGORIES:
            viol.append(f"{cid}:nutrient_has_drug_category:{cat}")
        # 라벨 원문이 사용자 카피로 통째 노출되지 않음
        if r.get("source_quote", "") and r["source_quote"] == r.get("display_text_ko_draft", ""):
            viol.append(f"{cid}:user_copy_equals_raw_quote")
    return viol


# ----- 렌더 -----
PM_BANNER = [
    "> **LIVE 아님 / review artifact**. 이 큐의 모든 항목은 candidate-only 다.",
    "> **자동 승격 금지**: live_integration_forbidden=true · published=false · clinical_reviewed=false · reviewed_by 공란.",
    "> **source quote 는 출처(허가사항 원문)**, app copy(display/management)는 그와 분리된 **비지시 참고 문구**다.",
    "> **제품/구매/제휴 UI 없음**. 보충제 추천·복용 지시 없음. live 통합은 PM + clinical reviewer 노트 후 별도 PR.",
]


def build_pm_queue_md(cfg, confirmed, holds, meta):
    L = []
    L.append("# MediStack — Theme Map Expansion PM Review Queue (v1.3, 편입)\n")
    L.append(f"- 생성: {meta['run_at']}  |  provider: theme_map_harvest_provider_v1_3  |  seed: data/config/theme_map_seeds_v1_3.json")
    L.append(f"- live relation 변경: **0** (provider 는 큐만 생성). draft 후보 {len(confirmed)} · hold {len(holds)}.")
    L += PM_BANNER
    L.append("")
    L.append("## A. DRAFT 후보 (source_confirmed · adversarial_verified · live 금지)\n")
    for r in confirmed:
        _pm_block(L, r)
    L.append("## B. HOLD (draft 큐 제외 — 미유통/임상판단/오인위험)\n")
    for r in holds:
        L.append(f"### {r['candidate_id']} — {r['drug_ingredient']} × {r['counterpart']}")
        L.append(f"- final_status: {r['final_status']}")
        L.append(f"- hold 사유: {r['hold_reason']}")
        L.append(f"- **live 금지**: live_integration_forbidden=true · published=false · clinical_reviewed=false\n")
    L.append("## PM 판단사항")
    L.append("1. counterpart_category 채택 확정: **acid_reducing_drug**(세팔로 acid-reducer, id61 al_mg_antacid 와 구분) · **fat_soluble_vitamin** 그룹.")
    L.append("2. TM-CHEL-01-ZN mechanism(absorption vs interaction) reviewer 확정(user 카피 영향 없음 — '효과 감소'로 라벨 충실).")
    L.append("3. 지용성 비타민 group 단일 vs 비타민별 분리 · 페니실라민 FE/ZN 묶음 카드 여부.")
    L.append("4. **live 통합은 clinical reviewer 노트 + 수동 명령 후 별도 PR.** provider/harvester 는 자동 승격하지 않는다.")
    return "\n".join(L) + "\n"


def _pm_block(L, r):
    L.append(f"### {r['candidate_id']} — {r['relation']} ({r['mechanism']}/{r['recommended_action']})")
    L.append(f"- relation 후보: {r['relation']}")
    L.append(f"- counterpart_type: {r['counterpart_type']}  |  counterpart_category: {r['counterpart_category']}")
    L.append(f"- source quote: \"{(r['source_quote'] or '').strip()[:200]}\"")
    L.append(f"- app copy(참고): {r['management_copy_draft']}")
    L.append(f"- itemSeq: {r['source_itemseq']}  |  section: {r['source_section']}")
    L.append(f"- evidence: {r['evidence_level']}  |  confidence: {r['confidence']}  |  risk: {r['risk_level']}")
    L.append(f"- adversarial verdict: **{r['adversarial_verdict']}**  |  next: {r['adversarial_next_action']}")
    L.append(f"- recommended_action: {r['recommended_pm_action']}")
    L.append(f"- **live 금지**: live_integration_forbidden=true · published=false · clinical_reviewed=false · reviewed_by 공란\n")


def build_summary(cfg, confirmed, holds, meta):
    by_verdict = {}
    for r in confirmed:
        by_verdict[r["adversarial_verdict"]] = by_verdict.get(r["adversarial_verdict"], 0) + 1
    return {
        "meta": {
            "name": "theme_map_harvest_incorporation_v1_3",
            "purpose": "harvester theme map expansion 편입(프롬프트 9) 결과 요약. review artifact / live 통합 아님.",
            "generated_via": "scripts/theme_map_harvest_provider_v1_3.py (harvester --include-theme-map-expansion 또는 standalone)",
            "incorporation_mode": "manual flag (default disabled) — config-driven, read-only, candidate-only",
            "live_relations_created": 0,
            "live_integration_forbidden": True,
            "published": False,
            "clinical_reviewed": False,
            "reviewed_by": "",
            "auto_integrate": False,
            "schedule_activation": False,
            "runtime_output_committed": False,
            "run_at": meta["run_at"],
        },
        "counts": {
            "confirmed_draft": len(confirmed),
            "hold": len(holds),
            "by_adversarial_verdict": by_verdict,
        },
        "confirmed_candidates": [
            {"candidate_id": r["candidate_id"], "relation": r["relation"],
             "counterpart_type": r["counterpart_type"], "counterpart_category": r["counterpart_category"],
             "itemSeq": r["source_itemseq"], "adversarial_verdict": r["adversarial_verdict"],
             "final_status": r["final_status"], "reviewer_needed": r["reviewer_needed"]}
            for r in confirmed
        ],
        "hold_candidates": [
            {"candidate_id": r["candidate_id"], "drug_ingredient": r["drug_ingredient"],
             "counterpart": r["counterpart"], "hold_reason": r["hold_reason"]}
            for r in holds
        ],
        "category_decision": cfg["meta"]["counterpart_category_policy"]["notes"],
        "id_disjointness": cfg["meta"]["id_disjointness"],
        "next_pm_actions": [
            "reviewer: acid_reducing_drug category 채택 + TM-CHEL-01-ZN mechanism + 지용성비타민 group-split 확정",
            "live 통합은 clinical reviewer 노트 + 수동 단계 후 별도 PR(자동 승격 금지)",
            "schedule 비활성 유지(프롬프트 6 게이트)",
        ],
    }


def build(cfg=None, art=None):
    """provider 핵심: config+아티팩트 → (confirmed, holds, errors). 호출자(harvester/validator)가 재사용."""
    cfg = cfg or load_config()
    art = art or load_artifacts(cfg)
    errs = check_consistency(cfg, art)
    confirmed = build_confirmed_rows(cfg, art)
    holds = build_hold_rows(cfg, art)
    errs += [f"integrity:{x}" for x in integrity_check(confirmed, holds)]
    errs += [f"safety:{x}" for x in safety_scan(confirmed)]
    return confirmed, holds, errs


def now_iso(stamp):
    return stamp or "(unstamped)"


def emit(queue_dir, summary_out=None, stamp=None):
    """runtime 큐(theme_map_*) + (선택) committed summary 생성. 안전 위반 시 RuntimeError."""
    cfg = load_config()
    art = load_artifacts(cfg)
    confirmed, holds, errs = build(cfg, art)
    if errs:
        raise RuntimeError(f"theme_map provider 안전 위반: {errs}")
    meta = {"run_at": now_iso(stamp)}
    os.makedirs(queue_dir, exist_ok=True)
    prefix = cfg["meta"]["policy"]["runtime_output_prefix"]
    pm_md = build_pm_queue_md(cfg, confirmed, holds, meta)
    with open(os.path.join(queue_dir, f"{prefix}pm_review_queue.md"), "w", encoding="utf-8") as f:
        f.write(pm_md)
    draft_doc = {"meta": {"status": "THEME MAP EXPANSION DRAFT CANDIDATES — NOT LIVE",
                          "do_not_implement_yet": True, "live_integration_forbidden": True,
                          "published": False, "clinical_reviewed": False, "reviewed_by": "",
                          "auto_integrate": False, "live_promotions": 0, "run_at": meta["run_at"]},
                 "draft_candidates": confirmed}
    with open(os.path.join(queue_dir, f"{prefix}draft_candidates.json"), "w", encoding="utf-8") as f:
        json.dump(draft_doc, f, ensure_ascii=False, indent=1)
    with open(os.path.join(queue_dir, f"{prefix}hold_report.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": {"live_integration_forbidden": True, "count": len(holds)},
                   "holds": holds}, f, ensure_ascii=False, indent=1)
    summary = build_summary(cfg, confirmed, holds, meta)
    if summary_out:
        with open(os.path.join(REPO, summary_out) if not os.path.isabs(summary_out) else summary_out,
                  "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="runtime 큐(theme_map_*) 생성")
    ap.add_argument("--queue-dir", default=os.path.join(REPO, "data/harvest_queue"))
    ap.add_argument("--summary-out", default=None, help="committed review summary 경로(data/review/...)")
    ap.add_argument("--stamp", default=None, help="run_at 타임스탬프(결정성 위해 호출자 주입)")
    ap.add_argument("--print-summary", action="store_true")
    args = ap.parse_args()
    try:
        if args.emit:
            summary = emit(args.queue_dir, args.summary_out, args.stamp)
            print(f"[theme_map provider] emit OK — draft {summary['counts']['confirmed_draft']} / "
                  f"hold {summary['counts']['hold']} → {args.queue_dir}/theme_map_*")
            if args.summary_out:
                print(f"  summary → {args.summary_out}")
        else:
            cfg = load_config()
            art = load_artifacts(cfg)
            confirmed, holds, errs = build(cfg, art)
            if errs:
                sys.stderr.write(f"FAIL(안전 위반): {errs}\n")
                return 1
            summary = build_summary(cfg, confirmed, holds, {"run_at": now_iso(args.stamp)})
            if args.print_summary:
                print(json.dumps(summary, ensure_ascii=False, indent=1))
            else:
                print(f"[theme_map provider] build OK — draft {len(confirmed)} / hold {len(holds)} / 안전 위반 0")
        return 0
    except RuntimeError as e:
        sys.stderr.write(f"FAIL: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
