#!/usr/bin/env python3
"""
integrate_coverage_queue_cqf02_v1_2.py
MediStack — coverage-queue draft batch3 중 **CQF02(테고프라잔×철분)만** 라이브 통합한다.
PM 승인(이번 라운드 프롬프트) = CQF02 do_not_implement_yet 해제. batch3 다른 행(CQF03 칼륨)은 승격 금지.

수행(integrate_coverage_queue_draft_batch_v1_2.py = CQF01 패턴 승계):
  1) v0.2 export(라이브 DATA_URL): relations 58 → 59 (CQF02 append, id 60). meta.relation_count 59.
     draft-전용 필드(draft_id/source_batch/source_candidate_id/published/clinical_reviewed/review_required/
     source_required/do_not_implement_yet/live_integration_forbidden/adversarial_verified/risk_level/note) strip.
     source 는 {type,url,pointer(+확인일)} 로 라이브 스키마 정합(checked_at strip).
  2) full index: 테고프라잔 **단일성분** name_only 품목(37건)만 relation_card 로 flip.
     테고프라잔고체분산체(1건, ingredient_name 상이)는 보수적 name_only 유지(CQF01 복합제 패턴 승계 —
     relation ingredient 가 정확히 '테고프라잔'이라 다른 성분명 entry 는 해당 relation 미커버).
     meta.counts 갱신(relation_card 1131→1168·name_only 16449→16412·total 17580 유지).
  3) aliases: verified_item_seqs 에 테고프라잔 키 추가(flip 된 item_seq, pool 진입). alias_count 717 불변.

⚠️ 절대 가드:
  - CQF02 외 통합 금지. 칼륨(potassium_safety_card)·depletion·금지성분 들어오면 STOP.
  - mechanism=absorption·source itemSeq 보유·draft adversarial_verified=true·source_confirmed=true 여야 함.
  - 기존 relation 58·excluded·disclaimers·DATA_URL·src·published/clinical false 불변.
  - reviewed_by 등 reviewer 크레딧 부여 금지(clinical_reviewed=false 유지·reviewer 미기재).
idempotent: 테고프라잔×철분 relation 이 이미 export 에 있으면 export/full/alias 각각 skip.
사용: python3 scripts/integrate_coverage_queue_cqf02_v1_2.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
BATCH = os.path.join(DATA, "coverage_queue_draft_batch3_v1_2.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")

BASELINE_RELATIONS = 58
TARGET_DRAFT_IDS = ["CQF02"]          # 이번 승격 대상(테고프라잔×철분)만
FLIP_INGREDIENT = "테고프라잔"         # 신규 relation 성분(full index 단일성분 flip 대상)
LIVE_KEEP = ["ingredient", "nutrient", "mechanism", "recommended_action", "evidence_level",
             "display_text_ko", "management_ko", "product_link_allowed",
             "potassium_safety_card", "requires_clinical_review"]
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)
VERIFY_METHOD = "nedrug.searchDrug"   # full index source_method 화이트리스트 정합


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


def is_flip_candidate(e):
    if e.get("display_mode") != "name_only":
        return False
    ing = e.get("ingredient_name") or ""
    if "/" in ing or "," in ing:        # 복합제는 보수적 name_only 유지
        return False
    return ing == FLIP_INGREDIENT       # 정확히 '테고프라잔'만(고체분산체 등 변형 성분명 제외)


def main():
    dry = "--dry-run" in sys.argv
    exp = json.load(open(EXPORT, encoding="utf-8"))
    batch = json.load(open(BATCH, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))

    drafts = {d["draft_id"]: d for d in batch["draft_relations"]}
    targets = [drafts[i] for i in TARGET_DRAFT_IDS if i in drafts]
    target_pairs = {(t["ingredient"], t["nutrient"]) for t in targets}

    existing_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    already = bool(target_pairs & existing_pairs)

    # ---- 가드 ----
    if not already:
        if len(exp["relations"]) != BASELINE_RELATIONS:
            print(f"[STOP] export relations {len(exp['relations'])} != {BASELINE_RELATIONS} baseline")
            return 1
        if len(targets) != 1:
            print(f"[STOP] 대상 draft {len(targets)} != 1 (CQF02)")
            return 1
        for d in targets:
            tag = d["draft_id"]
            if d["draft_id"] not in TARGET_DRAFT_IDS:
                print(f"[STOP] 대상 외 draft: {tag}"); return 1
            if d["nutrient"] == "칼륨" or d.get("potassium_safety_card") is True:
                print(f"[STOP] 칼륨/안전카드 건 통합 금지: {tag}"); return 1
            if d.get("mechanism") != "absorption":
                print(f"[STOP] absorption 아님: {tag} {d.get('mechanism')}"); return 1
            if d.get("adversarial_verified") is not True:
                print(f"[STOP] 적대적 검증 미통과: {tag}"); return 1
            if d.get("source_confirmed") is not True:
                print(f"[STOP] source_confirmed 아님: {tag}"); return 1
            if not re.search(r"itemSeq=\d+", (d.get("source") or {}).get("url", "")):
                print(f"[STOP] source itemSeq 없음: {tag}"); return 1
            if FORBIDDEN_RE.search(d["ingredient"]):
                print(f"[STOP] 금지 성분: {tag} {d['ingredient']}"); return 1
            if (d["ingredient"], d["nutrient"]) in existing_pairs:
                print(f"[STOP] 중복: {tag}"); return 1

    # ---- 1) export append ----
    if already:
        print("[skip] export 이미 통합(테고프라잔×철분 relation 존재)")
        new_rels = [r for r in exp["relations"] if (r.get("ingredient"), r.get("nutrient")) in target_pairs]
    else:
        nid = max(r["id"] for r in exp["relations"])
        new_rels = []
        for d in targets:
            nid += 1
            new_rels.append(draft_to_live(d, nid))
        exp["relations"] = exp["relations"] + new_rels
        exp["meta"]["relation_count"] = len(exp["relations"])
        exp["meta"]["note"] = exp["meta"].get("note", "") + \
            (" | coverage-queue draft batch3 CQF02 통합(2026-06-14): 테고프라잔(P-CAB 단일제)×철분 "
             "absorption/separation 1건(id 60, 허가사항 상호작용 출처·적대적 검증 통과). relation 58→59. "
             "테고프라잔 단일성분 37품목 full index relation_card flip.")
        print(f"[export] relations {BASELINE_RELATIONS} → {len(exp['relations'])} "
              f"(meta.relation_count={exp['meta']['relation_count']}) 신규 ids {[r['id'] for r in new_rels]}")

    # ---- 2) full index flip (테고프라잔 단일성분만) ----
    flip = [e for e in full["entries"] if is_flip_candidate(e)]
    for e in flip:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {len(flip)}건(테고프라잔 단일성분) → "
          f"relation_card {len(rc)}·name_only {len(no)}·total {len(full['entries'])}")

    # ---- 3) aliases verified_item_seqs 추가(pool 진입) ----
    vis = aliases.setdefault("verified_item_seqs", {})
    existing = vis.get(FLIP_INGREDIENT, [])
    existing_seqs = {x.get("item_seq") for x in existing}
    added = 0
    for e in flip:
        seq = str(e["item_seq"])
        if seq in existing_seqs:
            continue
        clean_name = re.sub(r"\s+", " ", e["item_name"]).strip()
        existing.append({"item_seq": seq, "item_name": clean_name,
                         "verified_at": "2026-06-14", "method": VERIFY_METHOD})
        existing_seqs.add(seq)
        added += 1
    if existing:
        vis[FLIP_INGREDIENT] = existing
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs +{added} → {vis_total}/{len(vis)}ing "
          f"(alias_count {aliases['meta'].get('alias_count')} 불변)")

    for r in new_rels:
        print(f"   id{r['id']} {r['ingredient']}×{r['nutrient']} ({r['mechanism']}/{r['recommended_action']}, "
              f"evidence={r['evidence_level']}, link={r['product_link_allowed']}, kcard={r['potassium_safety_card']})")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        print(f"\n예상 요약: relations {len(exp['relations'])}·relation_card {len(rc)}·"
              f"name_only {len(no)}·verified {vis_total}/{len(vis)}")
        return 0

    for path, obj in ((EXPORT, exp), (FULL, full), (ALIASES, aliases)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("\n[write] export · full index · aliases 기록 완료")
    print(f"요약: relations {len(exp['relations'])}·relation_card {len(rc)}·name_only {len(no)}·"
          f"total {len(full['entries'])}·verified {vis_total}/{len(vis)}·"
          f"published {exp['meta'].get('published')}")
    print("INTEGRATE COVERAGE-QUEUE DRAFT BATCH3 (CQF02): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
