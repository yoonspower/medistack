#!/usr/bin/env python3
"""
integrate_factory_draft_batch_v1_2.py
MediStack — factory draft batch 중 **DF06·DF07(리오티로닌×칼슘/철분)만** 라이브 통합한다.
PM 승인(이번 라운드 프롬프트) = 이 두 건만 do_not_implement_yet 해제. **DF01-DF05(칼륨)는 통합 금지.**

수행(integrate_relation_draft_v1_2.py 패턴 승계):
  1) v0.2 export(라이브 DATA_URL): relations 55 → 57 (DF06·DF07 append, ids 57·58). meta.relation_count 57.
     draft-전용 필드(draft_id/source_batch/source_candidate_id/published/clinical_reviewed/review_required/
     source_required/do_not_implement_yet/live_integration_forbidden/adversarial_verified/note) strip.
     source 는 {type,url,pointer(+확인일)} 로 라이브 스키마 정합(checked_at strip).
  2) full index: 리오티로닌은 인덱스(17,580)에 0건 → **flip 0**. relation_card 1077·name_only 16503 불변.
  3) aliases: flip 0 → verified_item_seqs/alias 무변경(1064/22·717 불변).

⚠️ 절대 가드:
  - DF06·DF07 외 통합 금지(특히 DF01-DF05 칼륨). 칼륨(potassium_safety_card)·depletion 건 들어오면 STOP.
  - 두 건 모두 mechanism=absorption·source itemSeq 보유·draft adversarial_verified=true 여야 함.
  - 기존 relation 55·excluded·disclaimers·DATA_URL·src·published/clinical false 불변.
  - reviewed_by 등 reviewer 크레딧 부여 금지(clinical_reviewed=false 유지·reviewer 미기재).
idempotent: 리오티로닌 relation 이 이미 export 에 있으면 skip.
사용: python3 scripts/integrate_factory_draft_batch_v1_2.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
BATCH = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")

BASELINE_RELATIONS = 55
TARGET_DRAFT_IDS = ["DF06", "DF07"]   # 이번 승격 대상(리오티로닌×칼슘/철분)만
LIVE_KEEP = ["ingredient", "nutrient", "mechanism", "recommended_action", "evidence_level",
             "display_text_ko", "management_ko", "product_link_allowed",
             "potassium_safety_card", "requires_clinical_review"]
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)


def draft_to_live(d, new_id):
    r = {"id": new_id}
    for k in LIVE_KEEP:
        r[k] = d[k]
    src = d["source"]
    pointer = src["pointer"]
    chk = src.get("checked_at")
    if chk and "확인일" not in pointer:
        pointer = f"{pointer} / 확인일 {chk}"
    r["source"] = {"type": src["type"], "url": src["url"], "pointer": pointer}
    return r


def main():
    dry = "--dry-run" in sys.argv
    exp = json.load(open(EXPORT, encoding="utf-8"))
    batch = json.load(open(BATCH, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))

    drafts = {d["draft_id"]: d for d in batch["draft_relations"]}
    targets = [drafts[i] for i in TARGET_DRAFT_IDS if i in drafts]

    # 통합 대상 성분 집합(idempotency 판정)
    target_ings = {d["ingredient"] for d in targets}
    already = any(r.get("ingredient") in target_ings and (r.get("ingredient"), r.get("nutrient")) in
                  {(t["ingredient"], t["nutrient"]) for t in targets} for r in exp["relations"])

    # ---- 가드 ----
    if not already:
        if len(exp["relations"]) != BASELINE_RELATIONS:
            print(f"[STOP] export relations {len(exp['relations'])} != {BASELINE_RELATIONS} baseline")
            return 1
        if len(targets) != 2:
            print(f"[STOP] 대상 draft {len(targets)} != 2 (DF06·DF07)")
            return 1
        existing_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
        for d in targets:
            tag = d["draft_id"]
            if d["draft_id"] not in TARGET_DRAFT_IDS:
                print(f"[STOP] 대상 외 draft: {tag}"); return 1
            if d["nutrient"] == "칼륨" or d.get("potassium_safety_card") is True:
                print(f"[STOP] 칼륨/안전카드 건 통합 금지(DF01-05 보류): {tag}"); return 1
            if d.get("mechanism") != "absorption":
                print(f"[STOP] absorption 아님: {tag} {d.get('mechanism')}"); return 1
            if d.get("adversarial_verified") is not True:
                print(f"[STOP] 적대적 검증 미통과: {tag}"); return 1
            if not re.search(r"itemSeq=\d+", (d.get("source") or {}).get("url", "")):
                print(f"[STOP] source itemSeq 없음: {tag}"); return 1
            if FORBIDDEN_RE.search(d["ingredient"]):
                print(f"[STOP] 금지 성분: {tag} {d['ingredient']}"); return 1
            if (d["ingredient"], d["nutrient"]) in existing_pairs:
                print(f"[STOP] 중복: {tag}"); return 1

    # ---- 1) export append ----
    if already:
        print("[skip] export 이미 통합(리오티로닌 relation 존재)")
        new_rels = [r for r in exp["relations"] if r.get("ingredient") in target_ings]
    else:
        nid = max(r["id"] for r in exp["relations"])
        new_rels = []
        for d in targets:
            nid += 1
            new_rels.append(draft_to_live(d, nid))
        exp["relations"] = exp["relations"] + new_rels
        exp["meta"]["relation_count"] = len(exp["relations"])
        exp["meta"]["note"] = exp["meta"].get("note", "") + \
            (" | factory draft batch DF06·DF07 통합(2026-06-14): 리오티로닌(테트로닌정 단일제)×칼슘·철분 "
             "absorption/separation 2건(ids 57·58, 허가사항 상호작용 출처·적대적 검증 통과). relation 55→57. "
             "DF01-05(칼륨)은 보류.")
        print(f"[export] relations {BASELINE_RELATIONS} → {len(exp['relations'])} "
              f"(meta.relation_count={exp['meta']['relation_count']}) 신규 ids {[r['id'] for r in new_rels]}")

    # ---- 2) full index flip (리오티로닌은 인덱스 0건 → flip 0 검증) ----
    rio_in_index = [e for e in full["entries"]
                    if any(t in (e.get("ingredient_name") or "") for t in target_ings)]
    if rio_in_index:
        print(f"[STOP] 예상과 달리 리오티로닌 인덱스 {len(rio_in_index)}건 존재 — flip 정책 재검토 필요")
        return 1
    rc = sum(1 for e in full["entries"] if e.get("display_mode") == "relation_card")
    no = sum(1 for e in full["entries"] if e.get("display_mode") == "name_only")
    print(f"[full index] flip 0 (리오티로닌 인덱스 부재) → relation_card {rc}·name_only {no}·total {len(full['entries'])} 불변")
    vis_total = sum(len(v) for v in (aliases.get("verified_item_seqs") or {}).values())
    print(f"[aliases] 무변경 — alias_count {aliases['meta'].get('alias_count')}·verified {vis_total}/"
          f"{len(aliases.get('verified_item_seqs') or {})} 불변")

    # 신규 relation 요약
    for r in new_rels:
        print(f"   id{r['id']} {r['ingredient']}×{r['nutrient']} ({r['mechanism']}/{r['recommended_action']}, "
              f"link={r['product_link_allowed']}, kcard={r['potassium_safety_card']})")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        return 0

    # export 만 기록(full index·alias 무변경 → 미기록으로 byte 불변 보장)
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n[write] export 기록(full index·alias 무변경 미기록)")
    print(f"요약: relations {len(exp['relations'])}·relation_card {rc}·name_only {no}·"
          f"alias {aliases['meta'].get('alias_count')}·published {exp['meta'].get('published')}")
    print("INTEGRATE FACTORY DRAFT BATCH (DF06·DF07): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
