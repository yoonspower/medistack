#!/usr/bin/env python3
"""
integrate_combo_banner_a_v1_1.py
MediStack — 복합제 통합 2순위(A 비스포스포네이트+비타민D3 복합제 43건) 복합제 고지 배너 배선 + relation_card flip.

PM 승인(복합제 검토 v1.1 로드맵 2순위) + 안전 게이트 통과(칼슘 카드가 '별도 칼슘제품'을 명시·D3는 칼슘 아님·
일반 배너 "다른 성분 미포함"으로 충분). 대상 = name_only 복합제 중 base ∈ {리세드론산, 이반드론산} 이고
co-ingredient 이 콜레칼시페롤(비타민D3) 인 43건(리세드론산 42·이반드론산 1).
B·D(라베프라졸)는 이미 통합(별도 스크립트). C(PPI+칼슘)·E(라베+산화Mg)는 제외.

수행(데이터만, 앱 src 무변경 — 배너 렌더는 render.js v0.7 .combobox 로 이미 라이브):
  1) full index: 43건 name_only → relation_card. meta.counts 갱신.
  2) aliases: ① verified_item_seqs[base] 에 item_seq 추가(pool 진입·alias #8 충족)
     ② product_aliases 에 43건 추가(is_combination=true·basis=base·notice=true·source_relation_ids=[40 or 41]).

불변 보호: export(relations 41)·DATA_URL·src·excluded·potassium 정책·published/clinical false.
금지: 신규 relation / E(라베+산화Mg)·C(PPI+칼슘) / 칼슘·비타민D 추천 / 제품·구매.

idempotent: 이미 relation_card 면 skip.
사용: python3 scripts/integrate_combo_banner_a_v1_1.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")

# base 성분 → 칼슘 relation id (source_relation_ids 용)
BASE_RID = {"리세드론산": 40, "이반드론산": 41}
CHECKED = "2026-06-13"
VERIFY_METHOD = "full_index nedrug.searchDrug ingredient_name (combo banner A v1.1)"


def base_of(ing):
    for b in BASE_RID:
        if b in ing:
            return b
    return None


def is_a_combo(e):
    if e.get("display_mode") != "name_only":
        return False
    ing = e.get("ingredient_name") or ""
    if base_of(ing) is None:
        return False
    if "콜레칼시페롤" not in ing:  # 비타민D3 복합제만
        return False
    if not ("/" in ing or "," in ing):
        return False
    return True


def clean(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def main():
    dry = "--dry-run" in sys.argv
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    targets = [e for e in full["entries"] if is_a_combo(e)]
    from collections import Counter
    by_base = Counter(base_of(e["ingredient_name"]) for e in targets)
    print(f"[scan] A 비스포+D3 복합제 name_only 후보: {len(targets)}건 {dict(by_base)}")
    if len(targets) != 43:
        print(f"[STOP] 후보 {len(targets)} != 43 (예상 baseline 아님)")
        return 1

    # --- 1) full index flip ---
    for e in targets:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {len(targets)} → relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])}")

    # --- 2a) verified_item_seqs[base] += (pool 진입, alias #8 충족) ---
    vis = aliases.setdefault("verified_item_seqs", {})
    added_vis = 0
    for e in targets:
        b = base_of(e["ingredient_name"])
        lst = vis.setdefault(b, [])
        have = {str(x.get("item_seq")) for x in lst}
        seq = str(e["item_seq"])
        if seq in have:
            continue
        lst.append({"item_seq": seq, "item_name": clean(e["item_name"]),
                    "verified_at": CHECKED, "method": VERIFY_METHOD})
        added_vis += 1
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs +{added_vis} → {vis_total}/{len(vis)}ing "
          f"(리세드론산 {len(vis.get('리세드론산',[]))}·이반드론산 {len(vis.get('이반드론산',[]))})")

    # --- 2b) product_aliases += (is_combination 배너 배선) ---
    pa = aliases.setdefault("product_aliases", [])
    existing_alias = {clean(p.get("alias")).lower() for p in pa}
    added_pa = 0
    for e in targets:
        b = base_of(e["ingredient_name"])
        surf = clean(e["item_name"])
        if surf.lower() in existing_alias:
            continue
        pa.append({
            "alias": surf,
            "canonical_ingredient": b,
            "kind": "product",
            "lang": "ko",
            "item_seq": str(e["item_seq"]),
            "source_relation_ids": [BASE_RID[b]],
            "is_combination": True,
            "combination_basis_ingredient": b,
            "combination_notice_required": True,
            # v1.1 A: 공존 성분 명시(칼슘 카드 ↔ 제품 속 비타민D 구분 → 오인 차단). 배너 "다른 성분"→"비타민D 성분".
            "combination_other_label": "비타민D",
        })
        existing_alias.add(surf.lower())
        added_pa += 1
    ing_n = len(aliases.get("ingredient_aliases") or [])
    prod_n = len(pa)
    aliases["meta"]["alias_count"] = ing_n + prod_n
    print(f"[aliases] product_aliases +{added_pa} → {prod_n} (ingredient {ing_n}) · alias_count {aliases['meta']['alias_count']}")

    if dry:
        print("\n(--dry-run: 파일 미기록)")
        return 0

    with open(FULL, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(ALIASES, "w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n[write] full index · aliases 기록 완료")
    print(f"요약: relation_card {len(rc)} · name_only {len(no)} · verified {vis_total}/{len(vis)} · "
          f"product_aliases {prod_n} · alias_count {aliases['meta']['alias_count']} · combo banner +{added_pa}")
    print("INTEGRATE COMBO BANNER A v1.1: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
