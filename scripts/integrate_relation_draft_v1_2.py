#!/usr/bin/env python3
"""
integrate_relation_draft_v1_2.py
MediStack — v1.2 source_confirmed draft relation 14건(D01-D14)을 **라이브에 통합**한다.

PM 승인(이번 라운드 프롬프트 = do_not_implement_yet 해제). 수행:
  1) v0.2 export(라이브 DATA_URL): relations 41 → 55 (draft 14건 append, ids 43-56). meta.relation_count 55.
     draft-전용 필드(draft_id/source_queue_id/published/clinical_reviewed/review_required/source_required/
     do_not_implement_yet/note) strip. source 는 {type,url,pointer(+확인일)} 로 라이브 스키마 정합.
     ⚠️ evidence 일관성 조정: D12/D14(치아지드유사 × 마그네슘, depletion)는 draft "high"→**"moderate"**
        (라이브 relation 20 HCTZ×Mg 선례 일치·draft 가 '동일 모델'로 명시·원문보다 강하지 않게).
  2) full index: 신규 성분 **클로르탈리돈·인다파미드 단일성분** name_only 품목만 relation_card 로 flip.
     (FQ/테트라/비스포 6+2성분은 이미 전건 relation_card → flip 0. enrichment only.)
     meta.counts 갱신(relation_card 1072→1077·name_only 16508→16503·total 17580 유지).
     복합제(클로르탈리돈 62·인다파미드 13)는 보수적으로 name_only 유지(v1.1 7성분 패턴 승계).
  3) aliases: verified_item_seqs 에 클로르탈리돈·인다파미드 키 추가(flip 된 item_seq, pool 진입).
     alias_count/product_aliases/ingredient_aliases 불변(verified_item_seqs 는 alias_count 미포함).

불변 보호: 기존 relation 41·excluded_v0_1·disclaimers·DATA_URL·src·published/clinical false·potassium 정책.
금지: 14건 외 relation / 와파린·에스오메프라졸·알렌드론산(reject)·H2(hold) / 제품·구매·영양제 추천.
칼륨 안전: D11/D13(칼륨) product_link_allowed=false·potassium_safety_card=true 승계(v0.2 validator #11 강제).

idempotent: export relations 에 클로르탈리돈 relation 이 이미 있으면 export/full/alias 각각 skip.
사용: python3 scripts/integrate_relation_draft_v1_2.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRAFT = os.path.join(DATA, "relation_expansion_draft_v1_2.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")

BASELINE_RELATIONS = 41
NEW_INGREDIENTS_FLIP = {"클로르탈리돈", "인다파미드"}   # 신규 성분(full index flip 대상)
# draft → live 변환 시 유지할 필드(라이브 relation 스키마와 정합). source/id 는 별도 처리.
LIVE_KEEP = ["ingredient", "nutrient", "mechanism", "recommended_action", "evidence_level",
             "display_text_ko", "management_ko", "product_link_allowed",
             "potassium_safety_card", "requires_clinical_review"]
# evidence 일관성 조정: (ingredient, nutrient) → 강제 evidence (라이브 선례 일치)
EVIDENCE_OVERRIDE = {("클로르탈리돈", "마그네슘"): "moderate", ("인다파미드", "마그네슘"): "moderate"}
# 금지 성분 가드(통합 절대 불가)
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)
FORBIDDEN_INGREDIENTS = {"알렌드론산", "파모티딘", "라푸티딘", "니자티딘"}
VERIFY_METHOD = "nedrug.searchDrug"   # full index source_method 화이트리스트 정합


def draft_to_live(d, new_id):
    r = {"id": new_id}
    for k in LIVE_KEEP:
        r[k] = d[k]
    ev = EVIDENCE_OVERRIDE.get((d["ingredient"], d["nutrient"]))
    if ev:
        r["evidence_level"] = ev
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
    if "/" in ing or "," in ing:        # 단일성분만(복합 제외 — 보수적 name_only 유지)
        return False
    return ing in NEW_INGREDIENTS_FLIP   # exact single ingredient


def main():
    dry = "--dry-run" in sys.argv
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    drafts = draft["draft_relations"]
    already = any(r.get("ingredient") in NEW_INGREDIENTS_FLIP for r in exp["relations"])

    # ---- 가드: source_confirmed 외/금지/중복 ----
    existing_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    if not already:
        if len(exp["relations"]) != BASELINE_RELATIONS:
            print(f"[STOP] export relations {len(exp['relations'])} != {BASELINE_RELATIONS} baseline")
            return 1
        if len(drafts) != 14:
            print(f"[STOP] draft 수 {len(drafts)} != 14")
            return 1
        for d in drafts:
            if FORBIDDEN_RE.search(d["ingredient"]) or d["ingredient"] in FORBIDDEN_INGREDIENTS:
                print(f"[STOP] 금지 성분 draft: {d['draft_id']} {d['ingredient']}")
                return 1
            if (d["ingredient"], d["nutrient"]) in existing_pairs:
                print(f"[STOP] 중복 (ingredient,nutrient): {d['draft_id']} {d['ingredient']}×{d['nutrient']}")
                return 1
            # 칼륨 안전정책 승계 강제
            if d["nutrient"] == "칼륨" and not (d["potassium_safety_card"] is True and d["product_link_allowed"] is False):
                print(f"[STOP] 칼륨 행 안전정책 위반: {d['draft_id']}")
                return 1

    # ---- 1) export append ----
    if already:
        print("[skip] export 이미 통합(신규 성분 relation 존재)")
        new_rels = [r for r in exp["relations"] if r.get("ingredient") in NEW_INGREDIENTS_FLIP
                    or (r.get("nutrient") == "아연")]
    else:
        max_id = max(r["id"] for r in exp["relations"])
        live = []
        nid = max_id
        for d in drafts:
            nid += 1
            live.append(draft_to_live(d, nid))
        exp["relations"] = exp["relations"] + live
        exp["meta"]["relation_count"] = len(exp["relations"])
        exp["meta"]["note"] = exp["meta"].get("note", "") + \
            (" | v1.2 draft relation 통합(2026-06-14): source_confirmed 14건(ids 43-56, 허가사항 출처) 추가. "
             "FQ/테트라×아연·비스포×철/Mg enrichment + 치아지드유사(클로르탈리돈·인다파미드)×칼륨/Mg. relation 41→55.")
        new_rels = live
        print(f"[export] relations {BASELINE_RELATIONS} → {len(exp['relations'])} "
              f"(meta.relation_count={exp['meta']['relation_count']})")
        print("   신규 ids:", [r["id"] for r in live])

    # ---- 2) full index flip (클로르탈리돈·인다파미드 단일성분만) ----
    flip = [e for e in full["entries"] if is_flip_candidate(e)]
    flipped_by_ing = {}
    for e in flip:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
        flipped_by_ing.setdefault(e["ingredient_name"], []).append(e)
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {len(flip)}건 → relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])}")
    print("   성분별:", {k: len(v) for k, v in flipped_by_ing.items()})

    # ---- 3) aliases verified_item_seqs 추가(pool 진입) ----
    vis = aliases.setdefault("verified_item_seqs", {})
    added = 0
    for ing, entries in flipped_by_ing.items():
        existing = vis.get(ing, [])
        existing_seqs = {x.get("item_seq") for x in existing}
        for e in entries:
            seq = str(e["item_seq"])
            if seq in existing_seqs:
                continue
            clean_name = re.sub(r"\s+", " ", e["item_name"]).strip()
            existing.append({"item_seq": seq, "item_name": clean_name,
                             "verified_at": "2026-06-14", "method": VERIFY_METHOD})
            existing_seqs.add(seq)
            added += 1
        vis[ing] = existing
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs +{added} → {vis_total}/{len(vis)}ing "
          f"(alias_count {aliases['meta'].get('alias_count')} 불변)")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        print(f"\n예상 요약: relations {len(exp['relations'])} · relation_card {len(rc)} · "
              f"name_only {len(no)} · verified {vis_total}/{len(vis)}")
        return 0

    for path, obj in ((EXPORT, exp), (FULL, full), (ALIASES, aliases)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("\n[write] export · full index · aliases 기록 완료")
    print(f"요약: relations {len(exp['relations'])} · relation_card {len(rc)} · "
          f"name_only {len(no)} · total {len(full['entries'])} · verified {vis_total}/{len(vis)}")
    print("INTEGRATE RELATION DRAFT v1.2: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
