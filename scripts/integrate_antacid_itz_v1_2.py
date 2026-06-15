#!/usr/bin/env python3
"""
integrate_antacid_itz_v1_2.py
MediStack — antacid_interaction 트랙의 **AT-05(이트라코나졸 × Al/Mg 함유 제산제)만** 라이브 통합한다.
**antacid_interaction 첫 live relation.** PM 승인(이번 라운드 프롬프트) = AT-05 라이브 승격.

수행(integrate_coverage_queue_cqf02_v1_2.py 패턴 승계, 단 full index/alias 는 건드리지 않음):
  1) v0.2 export(라이브 DATA_URL): relations 59 → 60 (AT-05 append, id = max+1). meta.relation_count 60.
     draft surface(render_nutrient/render_action) → live(nutrient/recommended_action) 매핑.
     draft-전용 필드(draft_id/harvester_candidate_id/surface/source_basis/copy_risk_level/confidence/
     risk_level/published/clinical_reviewed/reviewed_by/review_required/source_required/
     do_not_implement_yet/live_integration_forbidden/adversarial_verified/adversarial_verification/
     live_candidate_*/online_reconcile/note/label_quote/label_directive_type) strip.
     source 는 {type,url,pointer(+확인일)} 로 라이브 스키마 정합.
     mechanism=absorption(위산중화제가 이트라코나졸 흡수 영향)·evidence_level=high·requires_clinical_review=false 부여.
     counterpart_category=al_mg_antacid 유지(비-영양소 마커 — getFacets 가 영양소 facet 에서 제외).

  ※ full index: 이트라코나졸은 CANONICAL_13 아님 + alias pool 부재 → name_only 유지(flip 불필요·무변경).
  ※ aliases: 변경 없음(이트라코나졸 verified_item_seqs 미추가).

⚠️ 절대 가드:
  - AT-05(이트라코나졸·separation) 외 통합 금지. AT-01(펙소페나딘·avoid_concomitant)·칼륨·금지성분 들어오면 STOP.
  - recommended_action(render_action)=separation 만 허용(avoid_concomitant 는 v0.2 enum 위반·미통합).
  - counterpart_category=al_mg_antacid · adversarial_verified=true · source itemSeq 보유 여야 함.
  - 기존 relation 59·excluded·disclaimers·DATA_URL·full index·aliases·published/clinical false 불변.
  - product_link_allowed=false·potassium_safety_card=false·reviewed_by 미기재(clinical_reviewed=false 유지).
idempotent: 이트라코나졸×al_mg_antacid relation 이 이미 export 에 있으면 skip.
사용: python3 scripts/integrate_antacid_itz_v1_2.py [--dry-run]
종료코드: 0 DONE/skip, 1 STOP(가드 위반).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")

BASELINE_RELATIONS = 59
TARGET_DRAFT_ID = "AT-05"          # 이트라코나졸×Al/Mg 제산제만(separation)
COUNTERPART = "al_mg_antacid"
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)


def draft_to_live(d, new_id):
    surf = d.get("surface", {})
    nutrient = surf.get("render_nutrient")          # "Al/Mg 함유 제산제(약물)"
    action = surf.get("render_action")              # "separation"
    src = d["source"]
    pointer = src["pointer"]
    chk = src.get("checked_at")
    if chk and "확인일" not in pointer:
        pointer = f"{pointer} / 확인일 {chk}"
    return {
        "id": new_id,
        "ingredient": d["ingredient"],
        "nutrient": nutrient,
        "counterpart_category": d["counterpart_category"],   # 비-영양소 마커(영양소 facet 제외)
        "mechanism": "absorption",
        "recommended_action": action,
        "evidence_level": "high",
        "display_text_ko": d["display_text_ko"],
        "management_ko": d.get("management_ko", ""),
        "product_link_allowed": False,
        "potassium_safety_card": False,
        "requires_clinical_review": False,
        "source": {"type": src["type"], "url": src["url"], "pointer": pointer},
    }


def main():
    dry = "--dry-run" in sys.argv
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))

    drafts = {d["draft_id"]: d for d in draft["draft_relations"]}
    if TARGET_DRAFT_ID not in drafts:
        print(f"[STOP] draft {TARGET_DRAFT_ID} 없음"); return 1
    t = drafts[TARGET_DRAFT_ID]

    # idempotency: 이트라코나졸 × al_mg_antacid 이미 존재?
    def is_itz(r):
        return r.get("ingredient") == t["ingredient"] and r.get("counterpart_category") == COUNTERPART
    already = any(is_itz(r) for r in exp["relations"])

    if not already:
        # ---- 가드 ----
        if len(exp["relations"]) != BASELINE_RELATIONS:
            print(f"[STOP] export relations {len(exp['relations'])} != {BASELINE_RELATIONS} baseline"); return 1
        if t.get("counterpart_category") != COUNTERPART:
            print(f"[STOP] counterpart_category != {COUNTERPART}: {t.get('counterpart_category')}"); return 1
        if t.get("label_directive_type") != "separation":
            print(f"[STOP] AT-05 는 separation 만 통합(현 {t.get('label_directive_type')}) — avoid_concomitant 미통합"); return 1
        if (t.get("surface") or {}).get("render_action") != "separation":
            print(f"[STOP] render_action != separation: {(t.get('surface') or {}).get('render_action')}"); return 1
        if t.get("adversarial_verified") is not True:
            print(f"[STOP] adversarial_verified != true: {TARGET_DRAFT_ID}"); return 1
        if t.get("potassium_safety_card") is True or "칼륨" in (t.get("surface") or {}).get("render_nutrient", ""):
            print("[STOP] 칼륨/안전카드 건 통합 금지"); return 1
        if FORBIDDEN_RE.search(t["ingredient"]):
            print(f"[STOP] 금지 성분: {t['ingredient']}"); return 1
        if not re.search(r"itemSeq=\d+", (t.get("source") or {}).get("url", "")):
            print("[STOP] source itemSeq 없음"); return 1
        if "제산제" not in ((t.get("surface") or {}).get("render_nutrient") or ""):
            print("[STOP] render_nutrient 에 '제산제' 명시 없음"); return 1

    if already:
        print("[skip] export 이미 통합(이트라코나졸×al_mg_antacid relation 존재)")
        new = [r for r in exp["relations"] if is_itz(r)]
    else:
        nid = max(r["id"] for r in exp["relations"]) + 1
        rel = draft_to_live(t, nid)
        exp["relations"] = exp["relations"] + [rel]
        exp["meta"]["relation_count"] = len(exp["relations"])
        exp["meta"]["note"] = exp["meta"].get("note", "") + \
            (" | antacid_interaction 첫 live relation 통합(2026-06-15): AT-05 이트라코나졸 × Al/Mg 함유 제산제(약물) "
             "absorption/separation 1건(id %d, 허가사항 출처·적대검증 survives). relation 59→60. "
             "상대=제산제(약물 카테고리·counterpart_category=al_mg_antacid)이며 영양소 relation 아님 "
             "(getFacets 가 영양소 facet 에서 제외). full index/aliases 무변경(이트라코나졸 name_only 유지). "
             "published/clinical_reviewed=false·reviewed_by 미기재 유지." % nid)
        new = [rel]
        print(f"[export] relations {BASELINE_RELATIONS} → {len(exp['relations'])} "
              f"(meta.relation_count={exp['meta']['relation_count']}) 신규 id {[r['id'] for r in new]}")

    for r in new:
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, evidence={r['evidence_level']}, "
              f"counterpart={r.get('counterpart_category')}, link={r['product_link_allowed']}, "
              f"kcard={r['potassium_safety_card']}, clinical_review={r['requires_clinical_review']})")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        print(f"예상: relations {len(exp['relations'])}·meta.relation_count {exp['meta']['relation_count']}·"
              f"published {exp['meta'].get('published')}·clinical_reviewed {exp['meta'].get('clinical_reviewed')}")
        return 0

    if not already:
        with open(EXPORT, "w", encoding="utf-8") as f:
            json.dump(exp, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("\n[write] export 기록 완료(full index/aliases 무변경)")
    print(f"요약: relations {len(exp['relations'])}·published {exp['meta'].get('published')}·"
          f"clinical_reviewed {exp['meta'].get('clinical_reviewed')}")
    print("INTEGRATE ANTACID AT-ITZ: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
