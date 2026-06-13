#!/usr/bin/env python3
"""
integrate_combo_banner_c_v1_1.py
MediStack — 케이스 C(PPI+침강탄산칼슘 buffer_combo 18건) 복합제 고지 배너 배선 + relation_card flip.

PM 승인(장기 작업 지시 2026-06-14, 작업3 조건 충족) + 안전 게이트:
  - C 18건은 PPI×칼슘 nutrient relation 이 아니라 "PPI 성분 + 침강탄산칼슘 완충/제산 성분" 복합제(buffer_combo).
  - 표시 카드는 기존 PPI 관계(란소프라졸 id36/37 ×B12/×Mg · 라베프라졸 id32/33 ×B12/×Mg)만. 신규 relation 0.
  - 공존 성분(침강탄산칼슘)은 영양 칼슘이 아니라 위산 중화 완충제 → other_label 로 기능 명시
    ("위산 중화 완충 성분(침강탄산칼슘)") → '칼슘 보충/영양 칼슘' 오독 차단.
  - 근거: data/ppi_calcium_combo_review_v1_1.csv(허가사항 PPI×칼슘 흡수신호 0/22·칼슘=완충제 18/18) +
          docs/MediStack_ppi_calcium_combo_reclassification_v1_1.md.

수행(데이터만, 앱 src 무변경 — 배너 렌더는 render.js v0.7 .combobox + v1.1 otherLabel 경로로 이미 라이브):
  대상 = data/ppi_calcium_combo_reclassification_v1_1.csv 의 18 item_seq(권위 목록).
  1) full index: 18건 name_only → relation_card. meta.counts 갱신.
  2) aliases: ① verified_item_seqs[PPI] 에 item_seq 추가(pool 진입·alias #8 충족)
     ② product_aliases 에 18건 추가(is_combination=true·basis=PPI·notice=true·
        source_relation_ids=[36,37]/[32,33]·other_label="위산 중화 완충 성분(침강탄산칼슘)").

불변 보호: export(relations 41)·DATA_URL·src·excluded·potassium 정책·published/clinical false.
금지: 신규 relation / PPI×칼슘 nutrient relation / E(라베+산화Mg) / 칼슘 추천·보충 / 제품·구매.

idempotent: 이미 relation_card 면 skip.
사용: python3 scripts/integrate_combo_banner_c_v1_1.py [--dry-run]
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
CSVF = os.path.join(DATA, "ppi_calcium_combo_reclassification_v1_1.csv")

# PPI base 성분 → 기존 PPI relation id (×B12·×Mg). 신규 relation 0.
PPI_RID = {"란소프라졸": [36, 37], "라베프라졸": [32, 33]}
OTHER_LABEL = "위산 중화 완충 성분(침강탄산칼슘)"
CHECKED = "2026-06-13"  # 허가사항 침강탄산칼슘 완충성분 source 확인일(ppi_calcium_source_verification_v1_1.csv)
VERIFY_METHOD = "nedrug 허가사항 침강탄산칼슘=위산중화 완충성분 확인 (buffer_combo C v1.1)"


def clean(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def load_targets():
    """권위 목록 = 재분류 CSV. (item_seq, ppi_base, source_relation_ids, other_label) 반환 + 정합 assert."""
    rows = list(csv.DictReader(open(CSVF, encoding="utf-8")))
    targets = []
    for r in rows:
        seq = clean(r["item_seq"])
        base = clean(r["ppi_base"])
        rids = json.loads(r["future_source_relation_ids"])
        ol = clean(r["future_combination_other_label"])
        assert base in PPI_RID, f"예상밖 ppi_base: {base}"
        assert rids == PPI_RID[base], f"{seq}: source_relation_ids {rids} != {PPI_RID[base]}"
        assert ol == OTHER_LABEL, f"{seq}: other_label {ol!r} != {OTHER_LABEL!r}"
        targets.append({"item_seq": seq, "base": base, "rids": rids, "other_label": ol})
    return targets


def main():
    dry = "--dry-run" in sys.argv
    targets = load_targets()
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    if len(targets) != 18:
        print(f"[STOP] C 대상 {len(targets)} != 18 (예상 baseline 아님)")
        return 1
    from collections import Counter
    by_base = Counter(t["base"] for t in targets)
    print(f"[scan] C PPI+침강탄산칼슘 buffer_combo: {len(targets)}건 {dict(by_base)}")

    ent = {str(e["item_seq"]): e for e in full["entries"]}
    # 대상 전부 full index 에 존재 + 현재 name_only 확인(idempotent: 이미 relation_card 면 skip)
    flip_targets = []
    for t in targets:
        e = ent.get(t["item_seq"])
        if e is None:
            print(f"[STOP] item_seq {t['item_seq']} full index 미존재")
            return 1
        if e.get("display_mode") == "relation_card":
            continue  # idempotent
        if e.get("display_mode") != "name_only":
            print(f"[STOP] item_seq {t['item_seq']} display_mode={e.get('display_mode')} (name_only 아님)")
            return 1
        flip_targets.append((t, e))

    # --- 1) full index flip ---
    for t, e in flip_targets:
        e["display_mode"] = "relation_card"
        e["covered_by_relation"] = True
        e["no_relation_notice_required"] = False
    rc = [e for e in full["entries"] if e.get("display_mode") == "relation_card"]
    no = [e for e in full["entries"] if e.get("display_mode") == "name_only"]
    full["meta"]["counts"]["relation_card"] = len(rc)
    full["meta"]["counts"]["name_only"] = len(no)
    full["meta"]["counts"]["total"] = len(full["entries"])
    print(f"[full index] flip {len(flip_targets)} → relation_card {len(rc)} · name_only {len(no)} · total {len(full['entries'])}")

    # --- 2a) verified_item_seqs[PPI] += (pool 진입, alias #8 충족) ---
    vis = aliases.setdefault("verified_item_seqs", {})
    added_vis = 0
    for t in targets:
        lst = vis.setdefault(t["base"], [])
        have = {str(x.get("item_seq")) for x in lst}
        if t["item_seq"] in have:
            continue
        e = ent[t["item_seq"]]
        lst.append({"item_seq": t["item_seq"], "item_name": clean(e["item_name"]),
                    "verified_at": CHECKED, "method": VERIFY_METHOD})
        added_vis += 1
    vis_total = sum(len(v) for v in vis.values())
    print(f"[aliases] verified_item_seqs +{added_vis} → {vis_total}/{len(vis)}ing "
          f"(란소프라졸 {len(vis.get('란소프라졸',[]))}·라베프라졸 {len(vis.get('라베프라졸',[]))})")

    # --- 2b) product_aliases += (is_combination 버퍼-콤보 배너 배선) ---
    pa = aliases.setdefault("product_aliases", [])
    existing_alias = {clean(p.get("alias")).lower() for p in pa}
    added_pa = 0
    for t in targets:
        e = ent[t["item_seq"]]
        surf = clean(e["item_name"])
        if surf.lower() in existing_alias:
            continue
        pa.append({
            "alias": surf,
            "canonical_ingredient": t["base"],
            "kind": "product",
            "lang": "ko",
            "item_seq": t["item_seq"],
            "source_relation_ids": t["rids"],
            "is_combination": True,
            "combination_basis_ingredient": t["base"],
            "combination_notice_required": True,
            # 공존 성분 = 위산 중화 완충제(영양 칼슘 아님). other_label 로 기능 명시 → '칼슘 보충' 오독 차단.
            "combination_other_label": t["other_label"],
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
          f"product_aliases {prod_n} · alias_count {aliases['meta']['alias_count']} · buffer_combo banner +{added_pa}")
    print("INTEGRATE COMBO BANNER C v1.1: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
