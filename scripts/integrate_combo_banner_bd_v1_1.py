#!/usr/bin/env python3
"""
integrate_combo_banner_bd_v1_1.py
MediStack — 복합제 통합 1순위(B·D 라베프라졸 복합제 35건) 복합제 고지 배너 배선 + relation_card flip.

PM 승인(복합제 검토 v1.1 로드맵 1순위). 대상 = name_only 복합제 중 base=라베프라졸 이고
co-ingredient 이 탄산수소나트륨(완충제, 케이스 B 27건) 또는 아스피린(약물, 케이스 D 8건) 인 35건.
A(비스포+비타민D)/C(PPI+칼슘)/E(라베+산화Mg) 는 이번 라운드 제외(로드맵 2·3순위·영구금지).

수행(데이터만, 앱 src 무변경 — 배너 렌더는 render.js v0.7 .combobox 로 이미 라이브):
  1) full index: 35건 name_only → relation_card(covered_by_relation=true·no_relation_notice_required=false).
     meta.counts 갱신(relation_card 976→1011·name_only 16,604→16,569·total 17,580 유지).
  2) aliases: ① verified_item_seqs['라베프라졸'] 에 35 item_seq 추가(pool 진입·alias #8 충족, 174→209)
     ② product_aliases 에 35건 추가(is_combination=true·combination_basis_ingredient='라베프라졸'·
        combination_notice_required=true·source_relation_ids=[32,33]). meta.alias_count 621→656.

불변 보호: export(relations 41)·DATA_URL·src·excluded·potassium 정책·published/clinical false.
금지: 신규 relation / E(라베+산화Mg) flip / A·C / 에스오메프라졸 / 제품·구매·영양제 추천.

idempotent: 이미 35건이 relation_card 면 각 단계 skip.
사용: python3 scripts/integrate_combo_banner_bd_v1_1.py [--dry-run]
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

BASIS = "라베프라졸"
SOURCE_RELATION_IDS = [32, 33]  # 라베프라졸 ×비타민B12(32)·×마그네슘(33)
CHECKED = "2026-06-13"
VERIFY_METHOD = "full_index nedrug.searchDrug ingredient_name (combo banner B/D v1.1)"
# B/D 선택: base=라베프라졸 복합제 중 co-ingredient ∈ {탄산수소나트륨(B), 아스피린(D)}.
# C(침강탄산칼슘)·E(산화마그네슘) 는 제외 토큰으로 구조적으로 배제.
CO_INCLUDE = ("탄산수소나트륨", "아스피린")
CO_EXCLUDE = ("침강탄산칼슘", "탄산칼슘", "산화마그네슘")


def is_bd_combo(e):
    if e.get("display_mode") != "name_only":
        return False
    ing = e.get("ingredient_name") or ""
    if "라베프라졸" not in ing:
        return False
    if not ("/" in ing or "," in ing):  # 복합제만
        return False
    if any(x in ing for x in CO_EXCLUDE):  # C/E 배제
        return False
    if not any(x in ing for x in CO_INCLUDE):  # B/D 만
        return False
    return True


def clean(s):
    # nedrug 공식명 개행/다중공백 → 단일공백(surface_forms validator 호환).
    return re.sub(r"\s+", " ", str(s)).strip()


def main():
    dry = "--dry-run" in sys.argv
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    targets = [e for e in full["entries"] if is_bd_combo(e)]
    print(f"[scan] B/D 라베프라졸 복합제 name_only 후보: {len(targets)}건")
    if len(targets) != 35:
        print(f"[STOP] 후보 {len(targets)} != 35 (예상 baseline 아님)")
        return 1

    # --- 1) full index flip ---
    flipped = 0
    for e in targets:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
        flipped += 1
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {flipped} → relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])}")

    # --- 2a) verified_item_seqs['라베프라졸'] += 35 (pool 진입, alias #8 충족) ---
    vis = aliases.setdefault("verified_item_seqs", {})
    rabe = vis.setdefault(BASIS, [])
    have = {str(x.get("item_seq")) for x in rabe}
    added_vis = 0
    for e in targets:
        seq = str(e["item_seq"])
        if seq in have:
            continue
        rabe.append({"item_seq": seq, "item_name": clean(e["item_name"]),
                     "verified_at": CHECKED, "method": VERIFY_METHOD})
        have.add(seq)
        added_vis += 1
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs['{BASIS}'] +{added_vis} → {len(rabe)} (vis_total {vis_total}/{len(vis)}ing)")

    # --- 2b) product_aliases += 35 (is_combination 배너 배선) ---
    pa = aliases.setdefault("product_aliases", [])
    existing_alias = {clean(p.get("alias")).lower() for p in pa}
    added_pa = 0
    for e in targets:
        surf = clean(e["item_name"])
        if surf.lower() in existing_alias:
            continue
        pa.append({
            "alias": surf,
            "canonical_ingredient": BASIS,
            "kind": "product",
            "lang": "ko",
            "item_seq": str(e["item_seq"]),
            "source_relation_ids": list(SOURCE_RELATION_IDS),
            "is_combination": True,
            "combination_basis_ingredient": BASIS,
            "combination_notice_required": True,
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
    print("INTEGRATE COMBO BANNER B/D v1.1: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
