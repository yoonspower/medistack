#!/usr/bin/env python3
"""
integrate_penicillamine_subset_v1_3.py
MediStack — theme map 6건 중 **페니실라민 FE/ZN 2건 subset** live 통합 **준비/드라이런** 스크립트.
full-6 integrator(integrate_theme_map_draft_batch_v1_3.py)와 별도 — 두 페니실라민 영양소 relation 만
대상으로 한다(counterpart_category=null=일반 영양소 → **live 선행조건 0**: validator/src/facet/chip 변경 불필요).

대상(seed: theme_map_harvest_provider_v1_3.build · itemSeq 198300142 알타민캡슐250밀리그램(디-페니실라민)):
  TM-CHEL-01-FE  페니실라민 × 철분  (separation · absorption · evidence high · confidence high · '흡수율 저하' 직접근거)
  TM-CHEL-01-ZN  페니실라민 × 아연  (separation · absorption[추론] · evidence high · confidence moderate · '효과 감소'만 라벨 명시)

⚠️ ZN mechanism 결정(docs/MediStack_penicillamine_mechanism_decision_v1_3.md): **Option A 채택** —
  mechanism=absorption(추론·inference_flag) 유지 + confidence moderate. **user 카피는 라벨대로 '효과 감소'**(absorption 단정 안 함).
  Option B(mechanism=interaction)는 v0.2 validator ALLOWED_MECHANISM={absorption,depletion} 밖 → validator 선행 PR 필요라 비채택.

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 필요(별도 PM + clinical
reviewer 전까지 금지·본 세션 호출 안 함). dry-run = 라이브/보호 데이터 무수정 + 예상 산출물
data/review/penicillamine_subset_live_dryrun_v1_3.json(60→62·id 62~63·export sha 불변·live_write 0).

reviewer 노트 인터록(check_reviewer_note) — FE/ZN 2건 전건 + ZN mechanism 결정 + grouping(개별 카드) +
verified_reference 동의 + 철분/아연 보충 권유 아님 강제. SAMPLE/placeholder/clinical=true 승격요구/제품·보충 추천 허용 거부.
템플릿 = docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md §reviewer-note.

draft→live 매핑은 full integrator 와 동일(integ.draft_to_live 재사용·counterpart_category=null → 필드 생략·
draft-전용 필드 strip). id 는 runtime max+1(현재 60→62·id 62~63. full 6 또는 AT-FEX/칼륨 먼저면 자동 조정).
⚠️ full-6 integrator 와 **동시 사용 금지**(같은 후보 중복) — subset 우선 시 full 은 나머지 4건만(별도 결정).

사용:
  python3 scripts/integrate_penicillamine_subset_v1_3.py                                  # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_penicillamine_subset_v1_3.py --pm-approved --reviewer-note X  # live(별도 PM·reviewer 후·본 세션 금지)
종료코드: 0 DONE/skip/dry, 1 STOP(가드/노트 위반).
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
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "penicillamine_subset_live_dryrun_v1_3.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# full integrator(draft_to_live·guard_projected·DRAFT_ONLY 재사용) + provider(단일 진실원).
integ = _load("integ", "integrate_theme_map_draft_batch_v1_3.py")
prov = _load("prov", "theme_map_harvest_provider_v1_3.py")

SUBSET_IDS = ["TM-CHEL-01-FE", "TM-CHEL-01-ZN"]
EXCLUDED_THEME_MAP = ["TM-LIP-01", "TM-LIP-02", "TM-CEPH-AC-01", "TM-CEPH-AC-02"]
BASELINE_RELATIONS = 60
ITEMSEQ = "198300142"
ZN_MECHANISM_DECISION = {
    "option": "A",
    "mechanism": "absorption",
    "inference_flag": True,
    "confidence": "moderate",
    "user_copy_basis": "라벨 '효과 감소' 충실 — absorption 단정 안 함",
    "rationale": "Option B(interaction)는 v0.2 ALLOWED_MECHANISM={absorption,depletion} 밖이라 validator 선행 PR 필요. "
                 "Option A 는 선행조건 0(현행 v0.2 PASS) + user 카피 라벨 충실.",
}

# ── reviewer 노트 인터록(페니실라민 subset 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date")
MECHANISM_MARKERS = ("mechanism", "기전")
GROUPING_MARKERS = ("개별 카드", "grouping 결정", "묶음 카드")
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("철분·아연 보충 권유 없음", "철분/아연 보충 권유 없음", "보충 권유 없음",
                          "보충 권유 아님", "철분·아연 보충 권유 아님")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
# 철분/아연 보충 '권유/권장' 허용 거부(부정 '없/아님/금지' 직후는 통과)
SUPPLEMENT_RECO_RE = re.compile(
    r"(철분|아연|보충제)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")


def check_reviewer_note(reviewer_note):
    """페니실라민 FE/ZN subset live 통합 reviewer 노트 게이트.
    (note_content, violations) 반환 — 빈 리스트 = 통과. main() 과 테스트가 공유."""
    bad = []
    note = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note = f.read()
    if not note.strip():
        bad.append(f"노트 비공란 필요(--reviewer-note PATH). 받은 값: {reviewer_note!r}")
        return note, bad
    up, low = note.upper(), note.lower()
    for s in NOTE_SAMPLE_SENTINELS:
        if s.upper() in up:
            bad.append(f"SAMPLE/예시 토큰 감지('{s}') — 템플릿 그대로 승격 거부")
            break
    for m in NOTE_PLACEHOLDER_MARKERS:
        if m in note:
            bad.append(f"미기입 placeholder 감지('{m}')")
            break
    if not any(t in low or t in note for t in APPROVAL_TOKENS):
        bad.append(f"승인 표기({'/'.join(APPROVAL_TOKENS)}) 없음")
    miss = [c for c in SUBSET_IDS if c not in note]
    if miss:
        bad.append(f"candidate_id 미명시(FE/ZN 2건 전건 필요): {miss}")
    if not any(m in note for m in MECHANISM_MARKERS):
        bad.append("TM-CHEL-01-ZN 아연 mechanism 결정 미명시(absorption 추론 vs interaction)")
    if not any(g in note for g in GROUPING_MARKERS):
        bad.append("grouping 결정(FE/ZN 개별 카드) 미명시")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품 추천 아님 명시 필요")
    if not any(m in note for m in NOT_SUPPLEMENT_MARKERS):
        bad.append("철분/아연 보충 권유 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품 추천 허용 문구 — 금지")
    if SUPPLEMENT_RECO_RE.search(note):
        bad.append("철분/아연 보충 권유/권장 허용 문구 — 금지")
    return note, bad


def build_subset(exp):
    """provider 행 → 페니실라민 FE/ZN 2건 projected entries. live 무수정."""
    confirmed, _holds, errs = prov.build()
    if errs:
        return None, [f"provider:{e}" for e in errs]
    by_id = {r["candidate_id"]: r for r in confirmed}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in SUBSET_IDS:
        if cid not in by_id:
            viol.append(f"{cid}: provider confirmed 에 없음")
            continue
        row = by_id[cid]
        if row.get("counterpart_category") is not None:
            viol.append(f"{cid}: 일반 영양소 subset 인데 counterpart_category 비어있지 않음({row['counterpart_category']})")
        if (row["drug_ingredient"], row["counterpart"]) in existing:
            viol.append(f"{cid}: 이미 live 에 존재(드라이런 전제 위반)")
            continue
        nid += 1
        rel = integ.draft_to_live(row, nid)
        viol += integ.guard_projected(cid, row, rel)
        entries.append({
            "candidate_id": cid,
            "projected_id": nid,
            "counterpart_category": rel.get("counterpart_category"),  # None → 키 없음
            "mechanism": rel["mechanism"],
            "recommended_action": rel["recommended_action"],
            "evidence_level": rel["evidence_level"],
            "confidence": row.get("confidence", ""),
            "adversarial_verdict": row.get("adversarial_verdict", ""),
            "risk_flags": row.get("risk_flags", []),
            "projected_live_relation": rel,
        })
    return entries, viol


def main():
    if "--only" in sys.argv:
        print("[STOP] --only(부분 승인)는 미구현. 현 integrator 는 both-approval 전제(FE/ZN 2건 전건). "
              "부분 승인 시나리오는 dry-run artifact meta.partial_approval_scenarios 문서 참조 — "
              "실제 부분 live 통합은 별도 --only 변형 PR(dry-run 우선) 필요.")
        return 1
    pm_approved = "--pm-approved" in sys.argv
    reviewer_note = None
    if "--reviewer-note" in sys.argv:
        i = sys.argv.index("--reviewer-note")
        if i + 1 < len(sys.argv):
            reviewer_note = sys.argv[i + 1]

    exp = json.load(open(EXPORT, encoding="utf-8"))
    before = len(exp["relations"])
    entries, viol = build_subset(exp)
    if entries is None or viol:
        for b in (viol or ["build 실패"]):
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== 페니실라민 FE/ZN subset 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    for e in entries:
        r = e["projected_live_relation"]
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, evidence={r['evidence_level']}, "
              f"confidence={e['confidence']}, cat={r.get('counterpart_category')}, "
              f"link={r['product_link_allowed']}, clinical={r['requires_clinical_review']})")

    if not pm_approved:
        with open(EXPORT, "rb") as f:
            sha_before = hashlib.sha256(f.read()).hexdigest()
        before_max = max(r["id"] for r in exp["relations"])
        # 부분 승인 시나리오(문서화 전용·id 는 runtime max+1 → 단건 승인 시 그 단건이 id 62 차지. both 일 때만 FE=62·ZN=63).
        single_id = before_max + 1
        partial_scenarios = {
            "recommended": "both",
            "both": {"approved": SUBSET_IDS, "expected_count": after, "expected_ids": ids,
                     "note": "권고 — FE=id 62, ZN=id 63(2건 동시 → 순서대로 62·63)."},
            "FE_only": {"approved": ["TM-CHEL-01-FE"], "expected_count": before + 1, "expected_ids": [single_id],
                        "note": "ZN hold 시. 단건이므로 FE=id 62(max+1). ZN 은 needs_review 유지."},
            "ZN_only": {"approved": ["TM-CHEL-01-ZN"], "expected_count": before + 1, "expected_ids": [single_id],
                        "note": "단건이므로 ZN=id 62(max+1 — both 모드의 '63' 아님). FE 제외 사유 명시 필요 — "
                                "일반적으로 비권장(FE 가 '흡수율 저하' 직접근거로 더 확실, ZN 은 추론). reviewer 가 FE 위험만 보류할 특별 사유가 있을 때만."},
            "neither": {"approved": [], "expected_count": before, "expected_ids": [],
                        "note": "reject subset → live 0."},
            "id_rule": "id 는 runtime max+1. 단건 승인 시 그 단건이 id 62 를 차지. both 일 때만 FE=62·ZN=63.",
            "live_partial_integration": "현 integrator 는 both-approval 전제(SUBSET_IDS 전건 + 게이트가 FE/ZN 2건·grouping 강제). "
                                        "부분 승인이 실제 필요해지면 별도 --only 변형(dry-run 우선)을 추가 — 본 라운드는 시나리오 문서화만(live 0).",
        }
        # v0.2 validator 증거 — 선행조건 0 입증(현행 v0.2 PASS).
        sim = json.loads(json.dumps(exp))
        sim["relations"] += projected
        sim["meta"]["relation_count"] = len(sim["relations"])
        ok2, tail = integ.run_v0_2(sim)

        artifact = {
            "meta": {
                "name": "penicillamine_subset_live_dryrun_v1_3",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "페니실라민 FE/ZN 2건 subset live 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_penicillamine_subset_dryrun_v1_3.py 가 안전·계약을 검증.",
                "baseline_relations": before,
                "baseline_max_id": max(r["id"] for r in exp["relations"]),
                "expected_relation_count_before": before,
                "expected_relation_count_after": after,
                "expected_ids": ids,
                "included_candidate_ids": SUBSET_IDS,
                "excluded_theme_map_candidate_ids": EXCLUDED_THEME_MAP,
                "partial_approval_scenarios": partial_scenarios,
                "itemSeq": ITEMSEQ,
                "live_write_performed": False,
                "live_promotion": 0,
                "published": False,
                "clinical_reviewed": False,
                "reviewed_by": "",
                "data_url": "v0.2 (불변)",
                "export_sha_before": sha_before,
                "export_sha_after_same": True,
                "zn_mechanism_decision": ZN_MECHANISM_DECISION,
                "zn_mechanism_decision_required": True,
                "reviewer_note_required": True,
                "reviewer_note_interlock": {
                    "required": True,
                    "approval_tokens": list(APPROVAL_TOKENS),
                    "candidate_ids_all_of": SUBSET_IDS,
                    "zn_mechanism_decision_required": True,
                    "grouping_decision_required": True,
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id/mechanism/grouping/verified_reference 누락 · "
                               "clinical_reviewed=true·제품추천·철분/아연 보충 권유 허용 문구",
                    "template": "docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md §reviewer-note",
                },
                "guard_checks": {
                    "guard_projected_violations": viol,
                    "all_counterpart_category_null": all("counterpart_category" not in r for r in projected),
                    "all_product_link_false": all(r["product_link_allowed"] is False for r in projected),
                    "all_potassium_card_false": all(r["potassium_safety_card"] is False for r in projected),
                    "all_requires_clinical_review_false": all(r["requires_clinical_review"] is False for r in projected),
                    "no_reviewed_by": all("reviewed_by" not in r for r in projected),
                    "no_draft_only_leak": all(not (integ.DRAFT_ONLY & set(r.keys())) for r in projected),
                    "all_itemseq_198300142": all(ITEMSEQ in r["source"]["url"] for r in projected),
                    "ids_disjoint_from_live": not (set(ids) & {r["id"] for r in exp["relations"]}),
                },
                "live_integration_prerequisites": [],   # ⭐ subset 은 선행조건 0(아래 evidence 참조)
                "v0_2_validator_evidence": {
                    "sim_subset_2_passed": ok2,
                    "sim_subset_2_tail": tail,
                    "interpretation": "counterpart_category=null(일반 영양소)+separation+mechanism=absorption → 현행 v0.2 validator "
                                      "PASS. acid_reducing_drug/avoid_concomitant(#15)·fat_soluble_vitamin(facet) 선행조건 무관.",
                },
                "render_safety_summary": "두 카드 모두 counterpart_category=null → 기존 nutrient relation 과 동일 렌더(영양소 facet 노출·"
                                         "separation chip '복용 간격'). src getFacets/render 변경 불필요. full index/aliases/relation_card 1168·name_only 16412 불변.",
                "validator_result_summary": f"sim v0.2 PASS={ok2} (선행조건 0)",
                "note": "본 산출물은 드라이런 예상치일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 "
                        "의미하지 않는다. live 승격은 --pm-approved + --reviewer-note + 별도 PM + clinical reviewer.",
            },
            "projected_entries": entries,
            "excluded_theme_map": [
                {"candidate_id": "TM-LIP-01", "reason": "fat_soluble_vitamin — facet 선행조건(별도 PR)"},
                {"candidate_id": "TM-LIP-02", "reason": "fat_soluble_vitamin — facet 선행조건(별도 PR)"},
                {"candidate_id": "TM-CEPH-AC-01", "reason": "acid_reducing_drug — chip 선행조건(별도 PR)"},
                {"candidate_id": "TM-CEPH-AC-02", "reason": "acid_reducing_drug+avoid_concomitant — validator #15 선행조건(별도 PR)"},
            ],
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")
        with open(EXPORT, "rb") as f:
            sha_after = hashlib.sha256(f.read()).hexdigest()
        if sha_after != sha_before:
            print("[FATAL] 드라이런인데 live export sha 변경됨 — 중단")
            return 1
        print(f"\n[dry-run] live export sha 불변({sha_before[:8]}). 산출물: {os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print(f"[dry-run] v0.2 validator: subset 2건 sim PASS={ok2} (선행조건 0 — counterpart_category=null·separation).")
        print("[dry-run] live 기록은 --pm-approved + --reviewer-note + 별도 PM/reviewer 필요.")
        return 0

    # ── LIVE 기록(--pm-approved + --reviewer-note): 본 세션 호출 금지. 테스트는 temp 복사본에서만 ──
    _note, note_bad = check_reviewer_note(reviewer_note)
    if note_bad:
        for b in note_bad:
            print(f"[STOP] reviewer 노트: {b}")
        return 1
    exp["relations"] = exp["relations"] + projected
    exp["meta"]["relation_count"] = len(exp["relations"])
    exp["meta"]["note"] = exp["meta"].get("note", "") + \
        (" | 페니실라민 FE/ZN subset live 통합: 페니실라민 × 철분·아연(일반 영양소·separation·absorption[ZN 추론]). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE PENICILLAMINE SUBSET: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
