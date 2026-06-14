#!/usr/bin/env python3
"""
build_coverage_queue_precheck_batch3.py
MediStack relation factory batch3 — coverage KPI Top101-200(precheck 대역, cap 100)을
precheck_class 로 분류해 batch2 와 동일 스키마의 precheck CSV 를 생성한다(라이브 미반영·분석 산출물).

입력(읽기):
  data/coverage_kpi_top_candidates_v1_2.csv      (rank 101-200 대역)
  data/medistack_v0.2_beta_export.json           (covered base/pair)
  <union_json>  (batch3 precheck 발굴 workflow union: source_check_candidate 후보)
출력:
  data/coverage_queue_precheck_batch3_v1_2.csv

분류 규칙(batch2 승계):
  - covered(relation 보유) → already_covered_or_drafted
  - 민감/고위험군(정신건강·항혈전·항암·면역억제[이식]·임신수유소아) → sensitive_hold
  - workflow union 후보 → source_check_candidate(nutrient/mechanism/detector_key/reason 승계)
  - 그 외 → rejected_precheck(라벨 직접근거 개연 없음)
사용: python3 scripts/build_coverage_queue_precheck_batch3.py [--union /tmp/batch3_union.json] [--no-write]
"""
import argparse
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
KPI_CSV = os.path.join(DATA, "coverage_kpi_top_candidates_v1_2.csv")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
OUT_CSV = os.path.join(DATA, "coverage_queue_precheck_batch3_v1_2.csv")
DEFAULT_UNION = "/tmp/batch3_union.json"

# KPI sensitive_hold(정신/항혈전/항암) 외 추가 민감군: 면역억제/이식·항암 TKI/DMARD(기타로 오분류된 것).
EXTRA_SENSITIVE = ["사이클로스포린", "타크로리무스", "이매티닙", "레플루노미드", "토파시티닙",
                   "메토트렉세이트", "타목시펜", "라모트리진", "바레니클린"]
BAND_LO, BAND_HI = 101, 200


def is_extra_sensitive(ing):
    return any(k in ing for k in EXTRA_SENSITIVE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--union", default=DEFAULT_UNION)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(KPI_CSV, encoding="utf-8")))
    band = [r for r in rows if BAND_LO <= int(r["rank"]) <= BAND_HI]

    union = {}
    if os.path.exists(args.union):
        u = json.load(open(args.union, encoding="utf-8"))
        for c in (u.get("union") or u):
            union[int(c["rank"])] = c
    print(f"union source_check_candidate: {len(union)}")

    out = []
    for r in band:
        rank = int(r["rank"])
        ing = r["ingredient_name"]
        cls = r["therapeutic_class"]
        cnt = r["product_count"]
        covered = r["relation_covered"] == "yes"
        sensitive = r["sensitive_hold"] == "yes" or is_extra_sensitive(ing)
        nutrient = mech = detkey = ""
        ksafe = "false"
        risk = ""
        if covered:
            pc = "already_covered_or_drafted"
            reason = f"이미 relation 보유({r['covered_base_ingredient'] or 'relation_card'}) — 재후보화 불필요."
        elif sensitive:
            pc = "sensitive_hold"
            reason = (f"민감/고위험군({cls if r['sensitive_hold']=='yes' else '면역억제/항암/특수군'}) — "
                      "임상판단·출혈/상호작용/이식 위험으로 참고정보 베타 범위 밖(clinical reviewer 트랙 전 hold).")
        elif rank in union:
            c = union[rank]
            pc = "source_check_candidate"
            nutrient = c["nutrient"]
            mech = c["mechanism"]
            detkey = c["detector_key"]
            risk = "low"
            ksafe = "true" if (nutrient == "칼륨" and mech == "depletion") else "false"
            reason = c.get("reason", "")[:200]
        else:
            pc = "rejected_precheck"
            reason = "허가사항에 6대 영양소(철/칼슘/Mg/아연/칼륨) 직접 상호작용/이상반응 동거어 개연 낮음(품목수만으로 후보화 금지)."
        out.append({
            "rank": rank, "ingredient": ing, "product_count": cnt, "therapeutic_class": cls,
            "precheck_class": pc, "proposed_nutrient": nutrient, "mechanism": mech,
            "detector_key": detkey, "potassium_safety": ksafe, "risk_level": risk,
            "recovery_promoted": "false", "reason": reason,
        })

    from collections import Counter
    dist = Counter(r["precheck_class"] for r in out)
    print(f"precheck band {len(out)}건 분포: {dict(dist)}")
    print("source_check_candidate:")
    for r in out:
        if r["precheck_class"] == "source_check_candidate":
            print(f"  r{r['rank']} {r['ingredient']} × {r['proposed_nutrient']} ({r['mechanism']}/{r['detector_key']})")

    if not args.no_write:
        cols = ["rank", "ingredient", "product_count", "therapeutic_class", "precheck_class",
                "proposed_nutrient", "mechanism", "detector_key", "potassium_safety", "risk_level",
                "recovery_promoted", "reason"]
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(out)
        print(f"[write] {os.path.relpath(OUT_CSV, REPO)}")
    else:
        print("(--no-write)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
