#!/usr/bin/env python3
"""
audit_fidelity_v1_6.py
MediStack Factory v1.6 — B7/B8 **독립 fidelity-audit**(읽기전용·live 무수정).

auto_pass(=family adversarial 권위 통과 source-confirmed)는 reviewer-ready 로 **직행 금지**(B7).
이 모듈이 quote 완전성 · scope 일치 · copy fidelity(Phase A copy-lint) 를 재검해 PASS 한 것만
reviewer-ready 로 승격 가능하다고 판정한다. auto_pass 전수 audit(B8).

승급 가드(전부 hard rule — 위반은 reject/needs_review 격리):
  B1 Al/Mg 제산제 구성 미네랄(Al·Mg)을 standalone nutrient 로 승격 금지.
  B2 임신/태아/이상반응 맥락 엽산을 drug depletion 으로 승격 금지.
  B3 counterpart 가 standalone nutrient 도, 인정 drug-counterpart(al_mg_antacid/acid_reducing_drug)도 아니면 금지.
  B4 mechanism 없으면 금지.
  B5 source 없거나 quote 약하면 needs_review.
  B6 source 보다 강한 문구 금지(Phase A copy-lint 재적용) — copy 과확장이면 reframe 필요.

판정:
  - HARD(B1~B4) 위반 → audit_fail(=false auto_pass 후보) → batch 재검 트리거(B8).
  - B5 weak source → needs_review(승격 보류, false-pass 아님).
  - B6 copy 과확장 → fixable(reframe 적용 후 clean 이면 reviewer-ready, finding 으로 보고).
사용: python3 scripts/audit_fidelity_v1_6.py            # 글로벌 confirmed corpus 전수 audit
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLAN = os.path.join(ROOT, "data", "review", "reviewer_ready_global_plan_v1_4.json")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fix = _load("fix", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))

NUTRIENTS = ["철분", "칼슘", "아연", "마그네슘", "엽산", "비타민D", "비타민B12", "비타민B6",
             "비타민 B12", "비타민 B6", "비타민K", "비타민 K", "지용성 비타민", "칼륨", "나트륨", "구리"]
# 알루미늄은 영양소가 아님 → standalone nutrient 로 승급은 항상 오류. (마그네슘은 정당한 depletion 대상 — 제외.)
ALUMINUM_TOKENS = ["알루미늄", "Al"]
PREGNANCY_CTX = ["임신", "태아", "수유", "기형"]
# 진짜 depletion/길항 기전 근거 — 있으면 B2(임신/ADR 맥락 오승급) escape(정당한 depletion 관계).
DEPLETION_EVIDENCE = ["결핍", "길항", "감소", "저하", "악화", "고갈", "환원효소", "대사길항", "대사이상"]
VALID_DRUG_CAT = ("al_mg_antacid", "acid_reducing_drug")


def promotion_guards(rel, cand):
    """B1~B4 hard guards. 위반 목록 반환(빈 리스트면 통과)."""
    issues = []
    nut = rel.get("nutrient", "") or cand.get("counterpart", "")
    cat = rel.get("counterpart_category") or cand.get("counterpart_category")
    mech = rel.get("mechanism", "")
    action = rel.get("recommended_action", "")
    src_blob = json.dumps(rel.get("source", {}), ensure_ascii=False) + " " + json.dumps(cand, ensure_ascii=False)

    # B1: (a) 알루미늄을 standalone nutrient 로 승격 금지(알루미늄은 영양소가 아님 — 항상 오류).
    #     단 'Al/Mg 함유 제산제(약물)' 처럼 제산제 약물 counterpart 면 정당(separation).
    if cat != "al_mg_antacid" and "제산제" not in nut and any(a == nut for a in ALUMINUM_TOKENS):
        issues.append("B1:aluminum_as_standalone_nutrient")
    # (b) al_mg_antacid 유래 counterpart 를 depletion/monitoring 으로 재분류(separation flip) 금지.
    if cat == "al_mg_antacid" and action != "separation":
        issues.append("B1:al_mg_antacid_miscast_as_depletion")

    # B2: 임신/태아 맥락 엽산을 drug depletion 으로 승격 금지 — 단, source 가 진짜 depletion/길항
    #     기전(폴산결핍 악화·환원효소 길항 등)을 말하면 정당한 관계라 escape(섹션 라벨 오탐 방지).
    if "엽산" in nut and action != "separation":
        has_preg_ctx = any(t in src_blob for t in PREGNANCY_CTX)
        has_depletion_mech = any(t in src_blob for t in DEPLETION_EVIDENCE)
        if has_preg_ctx and not has_depletion_mech:
            issues.append("B2:folate_pregnancy_context_no_depletion_mechanism")

    # B3: counterpart 가 standalone nutrient 도, 인정 drug-counterpart 도 아니면 금지.
    is_nutrient = any(n in nut for n in NUTRIENTS)
    is_valid_drug_cp = (cat in VALID_DRUG_CAT) or ("제산제" in nut and "약물" in nut)
    if not is_nutrient and not is_valid_drug_cp:
        issues.append("B3:counterpart_not_nutrient_or_valid_drug")

    # B4: mechanism 없으면 금지.
    if not mech:
        issues.append("B4:no_mechanism")
    return issues


def quote_completeness(rel):
    """B5: source pointer/quote 가 실재하고 잘리지 않았는지. (ok, reason)."""
    src = rel.get("source", {}) or {}
    pointer = src.get("pointer", "") or ""
    url = src.get("url", "") or ""
    if not pointer:
        return False, "no_source_pointer"
    if "itemSeq" not in pointer and "itemSeq=" not in url and "itemSeq" not in url:
        return False, "no_itemSeq"
    # pointer 안의 인용구(따옴표) 또는 pointer 자체가 충분히 길어야(라벨 문맥 보존).
    if len(pointer) < 20:
        return False, "pointer_too_short"
    # 잘림 검사: pointer 가 '…'/'...' 로 끝나면 quote 잘림 의심.
    if pointer.rstrip().endswith(("…", "...")):
        return False, "quote_truncated"
    return True, "ok"


def copy_fidelity(rel):
    """B6: display/management 가 source 보다 강하지 않은지(Phase A copy-lint). reframe 가능 여부."""
    disp = rel.get("display_text_ko", "") or ""
    mng = rel.get("management_ko", "") or ""
    sq = json.dumps(rel.get("source", {}), ensure_ascii=False)  # source pointer 안에 quote 포함
    disp_v = fix.copy_lint(disp, sq)
    mng_v = fix.copy_lint(mng, sq)
    violations = ["display:" + x for x in disp_v] + ["management:" + x for x in mng_v]
    if not violations:
        return {"clean": True, "violations": [], "reframe_needed": False}
    # reframe 시도(능동단정/수치단정만 fixable).
    action = rel.get("recommended_action", "")
    fixed_disp = fix.reframe_display(disp, "depletion" if action != "separation" else "separation")
    fixed_clean = (fix.copy_lint(fixed_disp, sq) == [])
    return {"clean": False, "violations": violations, "reframe_needed": True,
            "reframe_fixed": fixed_clean, "corrected_display": fixed_disp if fixed_clean else None}


def audit_entry(entry, live_pairs):
    """confirmed projected entry 1건 전수 audit. 판정 dict 반환."""
    rel = entry["projected_live_relation"]
    cand = {"candidate_id": entry["candidate_id"], "family": entry["family"],
            "counterpart": rel.get("nutrient"), "counterpart_category": rel.get("counterpart_category")}
    pair = (rel.get("ingredient"), rel.get("nutrient"))
    already_live = pair in live_pairs

    hard = promotion_guards(rel, cand)
    q_ok, q_reason = quote_completeness(rel)
    cf = copy_fidelity(rel)
    clinical = rel.get("requires_clinical_review", False)
    product = rel.get("product_link_allowed", False)

    # 판정 우선순위: HARD 위반 → false_auto_pass / clinical·product → needs_review /
    #   weak source → needs_review / copy 과확장 fixable → reviewer_ready(corrected) / clean → reviewer_ready.
    if hard:
        verdict = "audit_fail_false_auto_pass"
    elif clinical or product:
        verdict = "needs_review"
    elif not q_ok:
        verdict = "needs_review"
    elif not cf["clean"] and not cf.get("reframe_fixed"):
        verdict = "audit_fail_copy_unfixable"
    elif not cf["clean"] and cf.get("reframe_fixed"):
        verdict = "reviewer_ready_corrected"
    else:
        verdict = "reviewer_ready"

    return {
        "candidate_id": entry["candidate_id"], "family": entry["family"],
        "ingredient": rel.get("ingredient"), "counterpart": rel.get("nutrient"),
        "mechanism": rel.get("mechanism"), "action": rel.get("recommended_action"),
        "display_text_ko": rel.get("display_text_ko", ""), "management_ko": rel.get("management_ko", ""),
        "already_live_on_base": already_live,
        "hard_guard_violations": hard,
        "quote_complete": q_ok, "quote_reason": q_reason,
        "copy_fidelity": cf,
        "verdict": verdict,
        "audit_pass": verdict in ("reviewer_ready", "reviewer_ready_corrected"),
        "source_pointer": (rel.get("source", {}) or {}).get("pointer", "")[:160],
        "evidence_level": rel.get("evidence_level"),
    }


def audit_corpus(plan=None, live_pairs=None):
    """전수 audit(B8). 결과 + 요약 반환."""
    plan = plan or json.load(open(PLAN, encoding="utf-8"))
    live_pairs = live_pairs if live_pairs is not None else set()
    results = [audit_entry(e, live_pairs) for e in plan["combined_projected_entries"]]
    false_pass = [r for r in results if r["verdict"].startswith("audit_fail")]
    corrected = [r for r in results if r["verdict"] == "reviewer_ready_corrected"]
    ready = [r for r in results if r["audit_pass"]]
    needs_review = [r for r in results if r["verdict"] == "needs_review"]
    summary = {
        "total_audited": len(results),
        "audit_pass": len(ready),
        "reviewer_ready_clean": len([r for r in results if r["verdict"] == "reviewer_ready"]),
        "reviewer_ready_corrected": len(corrected),
        "needs_review": len(needs_review),
        "false_auto_pass": len(false_pass),
        "batch_recheck_required": len(false_pass) > 0,  # B8
        "already_live_count": len([r for r in results if r["already_live_on_base"]]),
        "not_live_audit_pass": [r["candidate_id"] for r in ready if not r["already_live_on_base"]],
        "copy_corrections": [{"candidate_id": r["candidate_id"], "violations": r["copy_fidelity"]["violations"],
                              "corrected_display": r["copy_fidelity"].get("corrected_display")}
                             for r in corrected],
    }
    return results, summary


def main():
    exp_path = os.path.join(ROOT, "data", "medistack_v0.2_beta_export.json")
    live_pairs = set()
    if os.path.exists(exp_path):
        exp = json.load(open(exp_path, encoding="utf-8"))
        live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in exp["relations"])
    results, summary = audit_corpus(live_pairs=live_pairs)
    print("=== B7/B8 fidelity-audit (confirmed corpus 전수) ===")
    for r in results:
        if r["verdict"] != "reviewer_ready" or not r["already_live_on_base"]:
            flag = "" if r["audit_pass"] else "  ⚠️"
            print(f"  [{r['verdict']}]{flag} {r['candidate_id']} {r['ingredient']}×{r['counterpart']} "
                  f"live={r['already_live_on_base']} hard={r['hard_guard_violations']} "
                  f"copy_clean={r['copy_fidelity']['clean']}")
    print("-" * 60)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("=" * 60)
    if summary["false_auto_pass"] > 0:
        print(f"RESULT: BATCH-RECHECK — false auto_pass {summary['false_auto_pass']}건(B8 트리거)")
        return 1
    print(f"RESULT: PASS — false auto_pass 0 · audit_pass {summary['audit_pass']}/{summary['total_audited']} "
          f"(corrected {summary['reviewer_ready_corrected']}) · not-live audit_pass {summary['not_live_audit_pass']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
