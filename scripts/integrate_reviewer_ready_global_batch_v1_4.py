#!/usr/bin/env python3
"""
integrate_reviewer_ready_global_batch_v1_4.py
MediStack — Relation Factory v1.4 **글로벌 reviewer-ready 37 통합 계획/드라이런**(읽기전용·no-live-write).

목적: factory reviewer-ready 37건(적대검증 survives/copy_change)을 family 별로 매핑하고, family-specific 재검증을 거친
  통합 가능분(F1·F2·F3)의 **조합 시나리오 + 교차 family dedup + v0.2 sim** 을 산출한다. 실제 live 통합은 본 글로벌
  도구가 직접 하지 않고 **per-family integrator(reviewer-note 게이트)** 에 위임한다(no-live-write 영구).

핵심 원칙(품질 저하 방지):
  · family-specific 재검증을 **통과한 family 만 통합 가능**(F1/F2/F3 = 24건). F4/F6/F9/F10(=11건)은 적대검증만 거쳤고
    family 재검증 전 → **통합 불가(pending)**. (교훈: family 재검증이 F1 stray '1'·F2 철→철 토큰·F3 에티드론산 parse 처럼
    광역검증이 놓친 family 특이 결함을 잡음 — F4/F6/F9/F10 도 각자 family integrator/재검증 후에만 live.)
  · 교차 family + live 60 **dedup**: 통합 대상은 (ingredient, counterpart/category) 키로 live·타 family·자기 자신과 중복 금지.
  · 글로벌 도구는 **export 를 절대 쓰지 않음**(planning/dry-run 전용). live 는 per-family `--pm-approved --reviewer-note`.

family map(reviewer-ready 37, 적대검증):
  F1 fluoroquinolone×metal/antacid : 18 (family 재검증 ✅ survives 18 → 통합가능 18)
  F2 tetracycline×metal/antacid     :  5 (family 재검증 ✅ survives 5  → 통합가능 5)
  F3 bisphosphonate×mineral/antacid :  3 (family 재검증 ✅ survives 1·needs_review 2 → 통합가능 1)
  F4 thyroid×mineral/antacid        :  1 (family 재검증 ⏳ pending → 통합 불가)
  F6 acid-reducer×Fe/B12            :  1 (family 재검증 ⏳ pending → 통합 불가)
  F9 chronic-depletion×folate/vitD  :  8 (family 재검증 ⏳ pending → 통합 불가)
  F10 azole×antacid                 :  1 (family 재검증 ⏳ pending → 통합 불가)

조합 시나리오(통합 가능분, 모두 disjoint·dedup 0):
  F1 60→78 · F2 60→65 · F3 60→61 · F1+F2 60→83 · F1+F3 60→79 · F2+F3 60→66 · F1+F2+F3 60→84

사용:
  python3 scripts/integrate_reviewer_ready_global_batch_v1_4.py                 # (기본) dry-run 계획 — 쓰기 0
  python3 scripts/integrate_reviewer_ready_global_batch_v1_4.py --families F1,F3  # 부분 family 시나리오
종료코드: 0 DONE/dry, 1 STOP(불변·dedup·pending 위반).
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
ADVERSARIAL = os.path.join(DATA, "review", "relation_factory_adversarial_verify_v1_4.json")
PLAN_ARTIFACT = os.path.join(DATA, "review", "reviewer_ready_global_plan_v1_4.json")

BASELINE_RELATIONS = 60
CONFIRMED_AT = "2026-06-17"
REVIEWER_READY_TOTAL = 37


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f1 = _load("f1", "integrate_f1_quinolone_batch_v1_4.py")
f2 = _load("f2", "integrate_f2_tetracycline_batch_v1_4.py")
f3 = _load("f3", "integrate_f3_bisphosphonate_batch_v1_4.py")
integ = f1.integ  # 동일 substrate

# family 재검증 완료(통합 가능) family ↔ 모듈.
FAMILY_MODULES = {"F1": f1, "F2": f2, "F3": f3}
# 적대검증 reviewer-ready 지만 family 재검증 전 → 통합 불가.
FAMILY_PENDING_REVERIFY = {"F4", "F6", "F9", "F10"}
FAMILY_NAMES = {
    "F1": "Fluoroquinolone × metal cation / Al·Mg 제산제",
    "F2": "Tetracycline × metal cation / Al·Mg 제산제",
    "F3": "Bisphosphonate × mineral / Al·Mg 제산제",
    "F4": "Thyroid hormone × mineral/antacid",
    "F6": "Acid-reducer (H2/PPI) × Fe/B12/antacid",
    "F9": "Chronic-use depletion × folate/vitD",
    "F10": "Azole antifungal × antacid",
}


def _family_integrable(fam):
    """family 모듈의 survives subset entries(projected). (entries, recs, survives_ids)."""
    mod = FAMILY_MODULES[fam]
    loader = getattr(mod, {"F1": "load_f1", "F2": "load_f2", "F3": "load_f3"}[fam])
    recs, _summary = loader()
    if fam == "F3":
        survives = mod._survives_ids(recs)
    else:
        survives = [r["candidate_id"] for r in recs]  # F1/F2 전건 survives
    exp = json.load(open(EXPORT, encoding="utf-8"))
    entries, viol = mod.build_subset(exp, survives)
    return entries, recs, survives, viol


def _adversarial_family_counts():
    """적대검증 산출물에서 family 별 reviewer-ready 수 집계(family map 의 단일 소스)."""
    d = json.load(open(ADVERSARIAL, encoding="utf-8"))
    counts = {}
    for e in d["entries"]:
        if e.get("final_status") == "reviewer_ready_candidate":
            counts[e["family"]] = counts.get(e["family"], 0) + 1
    return counts


def build_plan(requested_families):
    exp = json.load(open(EXPORT, encoding="utf-8"))
    before = len(exp["relations"])
    base_max = max(r["id"] for r in exp["relations"])
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    rr_counts = _adversarial_family_counts()

    # 통합 가능 family 별 entries.
    per_family = {}
    integrable_pairs = {}
    all_viol = []
    for fam in ("F1", "F2", "F3"):
        entries, recs, survives, viol = _family_integrable(fam)
        all_viol += [f"{fam}:{v}" for v in viol]
        per_family[fam] = {
            "family_name": FAMILY_NAMES[fam],
            "reviewer_ready_adversarial": rr_counts.get(fam, 0),
            "family_reverified": True,
            "integrable_count": len(entries),
            "integrable_ids": [e["candidate_id"] for e in entries],
            "needs_review_ids": sorted(set(r["candidate_id"] for r in recs) - set(survives)),
            "expected_count_standalone": before + len(entries),
        }
        integrable_pairs[fam] = {(e["projected_live_relation"]["ingredient"],
                                  e["projected_live_relation"]["nutrient"]) for e in entries}

    # pending family(통합 불가) — family map 에만 표기.
    for fam in ("F4", "F6", "F9", "F10"):
        per_family[fam] = {
            "family_name": FAMILY_NAMES[fam],
            "reviewer_ready_adversarial": rr_counts.get(fam, 0),
            "family_reverified": False,
            "integrable_count": 0,
            "blocked_reason": "family-specific 재검증 미수행 → 통합 불가(per-family integrator/재검증 선행 필요).",
            "expected_count_standalone": None,
        }

    # 교차 family + live dedup 매트릭스.
    dedup = {"vs_live": {}, "cross_family": {}}
    for fam, pairs in integrable_pairs.items():
        dedup["vs_live"][fam] = sorted(f"{a}×{b}" for (a, b) in (pairs & live_pairs))
    fams = list(integrable_pairs)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            a, b = fams[i], fams[j]
            ov = integrable_pairs[a] & integrable_pairs[b]
            dedup["cross_family"][f"{a}∩{b}"] = sorted(f"{x}×{y}" for (x, y) in ov)
    dedup_clean = (all(not v for v in dedup["vs_live"].values())
                   and all(not v for v in dedup["cross_family"].values()))

    # 조합 시나리오(통합 가능분).
    n = {fam: per_family[fam]["integrable_count"] for fam in ("F1", "F2", "F3")}
    combos = {
        "F1": before + n["F1"], "F2": before + n["F2"], "F3": before + n["F3"],
        "F1+F2": before + n["F1"] + n["F2"], "F1+F3": before + n["F1"] + n["F3"],
        "F2+F3": before + n["F2"] + n["F3"], "F1+F2+F3": before + n["F1"] + n["F2"] + n["F3"],
    }

    # 요청 family 의 통합 가능 entries 합집합 → v0.2 sim(전 통합 가능분 충돌 0 입증).
    sel = [f for f in requested_families if f in ("F1", "F2", "F3")]
    blocked = [f for f in requested_families if f in FAMILY_PENDING_REVERIFY]
    combined_entries, seen = [], set()
    nid = base_max
    for fam in sel:
        entries, _r, _s, _v = _family_integrable(fam)
        for e in entries:
            rel = e["projected_live_relation"]
            key = (rel["ingredient"], rel["nutrient"])
            if key in live_pairs or key in seen:
                all_viol.append(f"dedup: {fam} {key} 중복(live/배치)")
                continue
            seen.add(key)
            nid += 1
            r2 = dict(rel)
            r2["id"] = nid  # 글로벌 순차 id 재배치(시뮬 전용)
            combined_entries.append({"family": fam, "candidate_id": e["candidate_id"],
                                     "projected_live_relation": r2})
    combined_count = before + len(combined_entries)
    sim = integ._sim_with(exp, [e["projected_live_relation"] for e in combined_entries])
    ok_sim, tail = integ.run_v0_2(sim) if combined_entries else (True, "n/a(0건)")

    return {
        "before": before, "base_max": base_max, "rr_counts": rr_counts,
        "per_family": per_family, "dedup": dedup, "dedup_clean": dedup_clean,
        "combos": combos, "requested": requested_families, "selected": sel, "blocked": blocked,
        "combined_entries": combined_entries, "combined_count": combined_count,
        "ok_sim": ok_sim, "sim_tail": tail, "viol": all_viol,
        "total_integrable": sum(n.values()),
    }


# ── 글로벌 reviewer-note 게이트(메타) — live write 는 per-family 위임이지만, 글로벌 승인 노트 형식을 검증/문서화 ──
GLOBAL_APPROVAL = ("approved", "승인")
PENDING_ACK_RE = re.compile(r"F4.{0,4}F6.{0,4}F9.{0,4}F10|F9.{0,4}F10|family[ \t]*재검증[ \t]*선행")
PER_FAMILY_NOTE_RE = re.compile(r"per-family|per_family|family별|개별 (reviewer[- ]?note|노트)")
GENERALIZE_PERMIT_RE = re.compile(r"(family|계열)[^\n]{0,12}(일반화|확대)[ \t]*(승인|허용)|(일반화|확대)[ \t]*(승인|허용)")


def check_global_reviewer_note(reviewer_note, selected, blocked):
    """글로벌 통합 승인 노트 게이트. 실제 write 없음(per-family 위임) — 노트 형식·금지 위반 검증용."""
    bad = []
    note = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note = f.read()
    if not note.strip():
        bad.append("노트 비공란 필요")
        return note, bad
    low = note.lower()
    if not any(t in low or t in note for t in GLOBAL_APPROVAL):
        bad.append("승인 표기 없음")
    for fam in selected:
        if fam not in note:
            bad.append(f"{fam} family 명시 누락(통합 family 전건 명시)")
    if not PER_FAMILY_NOTE_RE.search(note):
        bad.append("per-family reviewer-note 위임 명시 누락(글로벌 노트는 live write 안 함)")
    if not PENDING_ACK_RE.search(note):
        bad.append("F4/F6/F9/F10 family 재검증 선행 미명시(pending family 통합 불가 확인)")
    if blocked:
        bad.append(f"pending family 요청됨(통합 불가): {blocked}")
    if GENERALIZE_PERMIT_RE.search(note):
        bad.append("family/계열 일반화 허용 문구 — 금지")
    if re.search(r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|없음))", note):
        bad.append("clinical_reviewed/published=true 승격 요구 — 금지")
    return note, bad


def main():
    if "--families" in sys.argv:
        i = sys.argv.index("--families")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        requested = [f.strip().upper() for f in raw.split(",") if f.strip()]
    else:
        requested = ["F1", "F2", "F3"]

    with open(EXPORT, "rb") as f:
        sha_before = hashlib.sha256(f.read()).hexdigest()
    plan = build_plan(requested)
    if plan["viol"]:
        for v in plan["viol"]:
            print(f"[STOP] {v}")
        return 1

    before = plan["before"]
    print(f"=== 글로벌 reviewer-ready {REVIEWER_READY_TOTAL} 통합 계획 (DRY-RUN · no-live-write) ===")
    print(f"family map(reviewer-ready 적대검증): {plan['rr_counts']}")
    for fam in ("F1", "F2", "F3", "F4", "F6", "F9", "F10"):
        pf = plan["per_family"][fam]
        tag = "✅재검증·통합가능 %d" % pf["integrable_count"] if pf["family_reverified"] else "⏳pending(통합불가)"
        print(f"   {fam} {pf['family_name']}: reviewer-ready {pf['reviewer_ready_adversarial']} · {tag}")
    print(f"통합 가능 합계(F1+F2+F3): {plan['total_integrable']}건 · 조합: {plan['combos']}")
    print(f"dedup clean(교차 family·live): {plan['dedup_clean']}")
    print(f"요청 family={plan['selected']} · combined 60→{plan['combined_count']} · v0.2 sim PASS={plan['ok_sim']}")
    if plan["blocked"]:
        print(f"   ⚠️ pending family 요청 무시(통합 불가): {plan['blocked']}")

    artifact = {
        "meta": {
            "name": "reviewer_ready_global_plan_v1_4",
            "status": "DRY-RUN PLAN — NOT LIVE / no_live_write=true / live_integration_forbidden=true / "
                      "글로벌 도구는 export 무수정 · live 는 per-family integrator 위임",
            "purpose": "factory reviewer-ready 37 family map + 통합 가능분(F1/F2/F3) 조합 시나리오 + 교차 dedup + v0.2 sim.",
            "confirmed_at": CONFIRMED_AT,
            "reviewer_ready_total": REVIEWER_READY_TOTAL,
            "reviewer_ready_by_family_adversarial": plan["rr_counts"],
            "family_reverified": ["F1", "F2", "F3"],
            "family_pending_reverify": sorted(FAMILY_PENDING_REVERIFY),
            "integrable_total": plan["total_integrable"],
            "pending_total": REVIEWER_READY_TOTAL - plan["total_integrable"]
                             - sum(len(plan["per_family"][f]["needs_review_ids"]) for f in ("F1", "F2", "F3")),
            "f3_needs_review": sum(len(plan["per_family"][f].get("needs_review_ids", [])) for f in ("F1", "F2", "F3")),
            "per_family": plan["per_family"],
            "combined_scenarios": {
                "baseline": before,
                "F1_only": plan["combos"]["F1"], "F2_only": plan["combos"]["F2"], "F3_only": plan["combos"]["F3"],
                "F1+F2": plan["combos"]["F1+F2"], "F1+F3": plan["combos"]["F1+F3"], "F2+F3": plan["combos"]["F2+F3"],
                "F1+F2+F3": plan["combos"]["F1+F2+F3"],
                "note": "통합 가능분 기준. 모든 family ingredient disjoint(록사신/사이클린/드론산)·교차 dedup 0 → 합산 단순.",
            },
            "dedup": plan["dedup"], "dedup_clean": plan["dedup_clean"],
            "duplicate_policy": "통합 대상은 (ingredient, counterpart/category) 키로 live 60·타 family·자기 배치와 중복 금지. "
                                "차후 per-family integrator 가 live 와 build_subset 단계에서 재dedup(이미 통합분 skip).",
            "no_live_write": True, "live_write_performed": False, "live_promotion": 0,
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "data_url": "v0.2 (불변)", "export_sha_before": sha_before, "export_sha_after_same": True,
            "v0_2_sim_combined": {"selected_families": plan["selected"], "combined_count": plan["combined_count"],
                                  "sim_passed": plan["ok_sim"], "sim_tail": plan["sim_tail"]},
            "reviewer_note_gate": {
                "delegation": "글로벌 도구는 live write 안 함 — live 통합은 per-family integrator(F1/F2/F3) 의 "
                              "--pm-approved --reviewer-note(각 family 게이트) 로만. 글로벌 노트는 family 선택·순서·pending 확인용.",
                "requires": "승인 토큰 · 통합 family 전건 명시 · per-family reviewer-note 위임 명시 · "
                            "F4/F6/F9/F10 family 재검증 선행 확인 · family/계열 일반화·clinical=true 금지.",
            },
            "factory_v1_5_recommendation": {
                "run_now": False,
                "reason": "신규 harvest/family 확장은 (a) 통합 가능 24건(F1·F2·F3)의 reviewer note·live PR 미완, "
                          "(b) F4/F6/F9/F10 family 재검증 미수행(품질 게이트 미통과), (c) F9 needs_review 4·F3 needs_review 2 등 "
                          "기존 backlog 정리 우선. 신규 후보 추가는 backlog 부풀림·중복 위험.",
                "preconditions_to_run": ["F1/F2/F3 reviewer note 확보 + live PR(60→84 경로)",
                                         "F4/F6/F9/F10 family 재검증 + per-family integrator",
                                         "F9 needs_review 5·F3 needs_review 2 재검색/정리",
                                         "factory dedup 키(ingredient,counterpart/category) 표준화"],
                "recommended_timing": "위 4 선행조건 중 최소 reviewer note 트랙(F1/F2/F3 live) 가동 후.",
            },
            "note": "본 산출물은 계획/드라이런이며 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 "
                    "의미하지 않는다. live 통합은 per-family integrator + 별도 PM + clinical reviewer note + 별도 PR.",
        },
        "combined_projected_entries": plan["combined_entries"],
    }
    os.makedirs(os.path.dirname(PLAN_ARTIFACT), exist_ok=True)
    with open(PLAN_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=1)
        f.write("\n")

    with open(EXPORT, "rb") as f:
        sha_after = hashlib.sha256(f.read()).hexdigest()
    if sha_after != sha_before:
        print("[FATAL] 글로벌 계획인데 live export sha 변경됨 — 중단")
        return 1
    print(f"[dry-run] live export sha 불변({sha_before[:8]}). 계획 산출물: {os.path.relpath(PLAN_ARTIFACT, REPO)}")
    print("[dry-run] 글로벌 도구는 live 무기록 — live 통합은 per-family integrator(reviewer-note 게이트).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
