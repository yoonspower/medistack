#!/usr/bin/env python3
"""
integrate_relation_expansion_v1_1.py
MediStack — source_confirmed 7후보 relation 11건(draft ids 32-42)을 **라이브에 통합**한다.

PM 승인(라이브 통합). 수행:
  1) v0.2 export(라이브 DATA_URL): relations 30 → 41 (draft 11건 append, draft_origin 제거). meta.relation_count 41.
  2) full index: 7성분 **단일성분** name_only 품목 418건을 relation_card 로 flip(covered_by_relation=true·
     no_relation_notice_required=false). meta.counts 갱신(relation_card 558→976·name_only 17,022→16,604·total 17,580 유지).
     ⚠️ 복합제(97건·라베+산화Mg/PPI+칼슘/비스포+비타민D 등 nutrient 혼재)는 카드 혼란 우려로 **이번 라운드 제외**(name_only 유지).
  3) aliases: verified_item_seqs 에 7성분 키 추가(flip 된 418 item_seq, pool 진입). alias_count/ingredient/product_aliases 불변.

불변 보호: 기존 relation 30·excluded_v0_1·disclaimers·DATA_URL·src·published/clinical false·potassium 정책.
금지: 7후보 외 relation / E07·E09·E10(H2×B12) / 에스오메프라졸 / 제품·구매·영양제 추천.

idempotent: export relations 가 이미 41(ids32-42 존재)이면 export/full/alias 단계 각각 skip.
사용: python3 scripts/integrate_relation_expansion_v1_1.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRAFT = os.path.join(DATA, "relation_expansion_draft_v1_1.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")

NEW_IDS = set(range(32, 43))
# 키 매핑은 더 구체적인 것 먼저(덱스란소프라졸 ⊃ 란소프라졸 substring)
SEVEN_ORDERED = ["덱스란소프라졸", "란소프라졸", "라베프라졸", "판토프라졸",
                 "리세드론산", "이반드론산", "세프디니르"]
ESO_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium)", re.IGNORECASE)
FORBIDDEN_ITEMSEQS = {"201600209", "201600209"}
CHECKED = "2026-06-13"
VERIFY_METHOD = "full_index nedrug.searchDrug ingredient_name (relation expansion v1.1)"


def canonical_key(ing_name):
    for s in SEVEN_ORDERED:
        if s in ing_name:
            return s
    return None


def is_flip_candidate(e):
    if e.get("display_mode") != "name_only":
        return False
    ing = e.get("ingredient_name") or ""
    if not ing or "/" in ing or "," in ing:  # 단일성분만(복합 제외)
        return False
    if not any(s in ing for s in SEVEN_ORDERED):
        return False
    if ESO_RE.search(e.get("item_name") or "") or ESO_RE.search(ing):
        return False
    if str(e.get("item_seq")) in FORBIDDEN_ITEMSEQS:
        return False
    return True


def main():
    dry = "--dry-run" in sys.argv
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    exp_ids = {r["id"] for r in exp["relations"]}
    already = NEW_IDS.issubset(exp_ids)

    # --- 1) export: append 11 relations ---
    if already:
        print("[skip] export 이미 통합(ids 32-42 존재)")
    else:
        if len(exp["relations"]) != 30:
            print(f"[STOP] export relations {len(exp['relations'])} != 30 (예상 baseline 아님)")
            return 1
        draft_new = [r for r in draft["relations"] if r["id"] in NEW_IDS]
        if len(draft_new) != 11:
            print(f"[STOP] draft 신규 relation {len(draft_new)} != 11")
            return 1
        # draft_origin 제거(라이브 스키마 정합)
        clean = []
        for r in draft_new:
            r2 = {k: v for k, v in r.items() if k != "draft_origin"}
            clean.append(r2)
        # 금지 성분 가드
        forb = [r["id"] for r in clean if ESO_RE.search(r["ingredient"])
                or r["ingredient"] in ("파모티딘", "라푸티딘", "니자티딘")]
        if forb:
            print(f"[STOP] 금지 성분 relation: {forb}")
            return 1
        exp["relations"] = exp["relations"] + clean
        exp["meta"]["relation_count"] = len(exp["relations"])
        exp["meta"]["note"] = exp["meta"].get("note", "") + \
            " | v1.1 relation 확장 통합(2026-06-13): source_confirmed 7후보 11건(ids 32-42, 허가사항 출처) 추가. relation 30→41."
        print(f"[export] relations 30 → {len(exp['relations'])} (meta.relation_count={exp['meta']['relation_count']})")

    # --- 2) full index: flip 418 single-ingredient ---
    flip = [e for e in full["entries"] if is_flip_candidate(e)]
    key_count = {}
    flipped_by_key = {}
    for e in flip:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
        k = canonical_key(e["ingredient_name"])
        key_count[k] = key_count.get(k, 0) + 1
        flipped_by_key.setdefault(k, []).append(e)
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {len(flip)}건 → relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])}")
    print("   key별:", dict(sorted(key_count.items(), key=lambda x: -x[1])))

    # --- 3) aliases: verified_item_seqs 키 추가(pool 진입) ---
    vis = aliases.setdefault("verified_item_seqs", {})
    added_vis = 0
    for k, entries in flipped_by_key.items():
        existing = vis.get(k, [])
        existing_seqs = {x.get("item_seq") for x in existing}
        for e in entries:
            seq = str(e["item_seq"])
            if seq in existing_seqs:
                continue
            # item_name 표면형 위생: nedrug 공식명 개행/다중공백 → 단일공백(surface_forms validator 호환).
            clean_name = re.sub(r"\s+", " ", e["item_name"]).strip()
            existing.append({"item_seq": seq, "item_name": clean_name,
                             "verified_at": CHECKED, "method": VERIFY_METHOD})
            existing_seqs.add(seq)
            added_vis += 1
        vis[k] = existing
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs +{added_vis} → {vis_total}/{len(vis)}ing (alias_count {aliases['meta'].get('alias_count')} 불변)")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        return 0

    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(FULL, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(ALIASES, "w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n[write] export · full index · aliases 기록 완료")
    print(f"\n요약: relations {len(exp['relations'])} · relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])} · verified {vis_total}/{len(vis)}")
    print("INTEGRATE RELATION EXPANSION v1.1: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
