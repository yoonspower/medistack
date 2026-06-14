#!/usr/bin/env python3
"""
build_coverage_queue_precheck_batch4.py
MediStack relation factory batch4 — coverage KPI Top201-300(precheck 대역, cap 100)을
precheck_class 로 분류해 batch2/batch3 와 동일 스키마의 precheck CSV 를 생성한다(라이브 미반영·분석 산출물).

build_coverage_queue_precheck_batch3.py 패턴 승계. 차이:
  - BAND 201-300
  - EXTRA_SENSITIVE 확장: KPI therapeutic_class 가 '기타'로 분류했으나 항암/면역억제/마취·규제/정신건강/항혈전인
    성분(에베로리무스·엘로티닙·팔보시클립·티카그렐러·에독사반·펜타닐·프로포폴·덱스메데토미딘·메틸페니데이트·
    보티옥세틴·테노포비르·데노수맙 등)을 sensitive_hold 로 회수.
  - 출력: data/coverage_queue_precheck_batch4_v1_2.csv

분류 규칙(batch2/batch3 승계):
  - covered(relation 보유) → already_covered_or_drafted
  - 민감/고위험군(정신건강·항혈전·항암·면역억제[이식]·마취/규제·특수군) → sensitive_hold
  - union 후보 → source_check_candidate(nutrient/mechanism/detector_key/reason 승계)
  - 그 외 → rejected_precheck(라벨 직접근거 개연 없음·품목수만으로 후보화 금지·계열 일반화 금지)
사용: python3 scripts/build_coverage_queue_precheck_batch4.py [--union /tmp/batch4_union.json] [--no-write]
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
OUT_CSV = os.path.join(DATA, "coverage_queue_precheck_batch4_v1_2.csv")
DEFAULT_UNION = "/tmp/batch4_union.json"

# KPI sensitive_hold(정신/항혈전/항암) 외 추가 민감군: 항암/면역억제/이식·마취/규제·정신건강·특수군
# (KPI therapeutic_class='기타'로 새는 것 회수). batch3 목록 + batch4 band 신규.
EXTRA_SENSITIVE = [
    # batch3 승계
    "사이클로스포린", "타크로리무스", "이매티닙", "레플루노미드", "토파시티닙",
    "메토트렉세이트", "타목시펜", "라모트리진", "바레니클린",
    # batch4 band 신규(항암/면역억제/표적)
    "에베로리무스", "엘로티닙", "팔보시클립", "데노수맙", "테노포비르",
    # 마취/규제·진정
    "펜타닐", "프로포폴", "덱스메데토미딘", "레미펜타닐",
    # 정신건강/ADHD
    "메틸페니데이트", "보티옥세틴", "졸피뎀",
    # 항혈전/항혈소판
    "티카그렐러", "에독사반", "클로피도그렐",
]
BAND_LO, BAND_HI = 201, 300


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
            reason = (f"민감/고위험군({cls if r['sensitive_hold']=='yes' else '항암/면역억제/마취·규제/정신건강/항혈전'}) — "
                      "임상판단·출혈/상호작용/이식/규제 위험으로 참고정보 베타 범위 밖(clinical reviewer 트랙 전 hold).")
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
            reason = ("허가사항에 6대 영양소(철/칼슘/Mg/아연/칼륨) 직접 상호작용/이상반응 동거어 개연 낮음 "
                      "(품목수만으로 후보화 금지·계열 일반화 금지·칼슘/칼륨 짝이온염 트랩 제외).")
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
