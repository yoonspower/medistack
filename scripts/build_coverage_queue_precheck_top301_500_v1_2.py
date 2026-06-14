#!/usr/bin/env python3
"""
build_coverage_queue_precheck_top301_500_v1_2.py
MediStack coverage-queue **Top301-500 효율 점검 precheck**(라이브 미반영·분석 산출물).

batch3(Top101-200)·batch4(Top201-300) 패턴 승계. 차이:
  - 랭킹 소스를 KPI CSV(Top300 절단)가 아니라 **full index(17,580) 성분별 품목수**에서 직접 재계산해
    ranks 301-500 을 슬라이스(기존 1-300 랭킹과 동일한 prod_count.most_common() tie-break → 연속성 보장).
  - 분류는 analyze_coverage_kpi_v1_2.classify()·SENSITIVE_CLASSES + batch4 EXTRA_SENSITIVE 를 재사용(중복 0).
  - source_check_candidate 는 **명시 후보맵(SOURCE_CHECK_MAP)** 만 채택 — 품목수만으로 후보화 금지·
    계열 일반화 금지·짝이온/복합제 트랩 제외. 맵에 없으면 rejected_precheck.

⚠️ 보호 데이터(relation/full index/alias/export/src) 한 줄도 수정하지 않는다(읽기전용).
출력: data/coverage/coverage_queue_top301_500_precheck_v1_2.csv
사용: python3 scripts/build_coverage_queue_precheck_top301_500_v1_2.py [--no-write]
종료코드: 0.
"""
import argparse
import csv
import importlib.util
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
OUT_CSV = os.path.join(DATA, "coverage", "coverage_queue_top301_500_precheck_v1_2.csv")
BAND_LO, BAND_HI = 301, 500

# analyze_coverage_kpi 의 classify/CLASS_RULES/SENSITIVE_CLASSES 재사용(랭킹·분류 정합).
_spec = importlib.util.spec_from_file_location(
    "kpi", os.path.join(HERE, "analyze_coverage_kpi_v1_2.py"))
kpi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kpi)

# batch4 EXTRA_SENSITIVE 승계 + 301-500 band 신규 민감/고위험군(KPI '기타'로 새는 것 회수).
EXTRA_SENSITIVE = [
    # 항암/면역억제/표적/이식
    "메토트렉세이트", "타목시펜", "이매티닙", "다사티닙", "레날리도마이드", "비칼루타미드",
    "엔잘루타미드", "류프로렐린", "레트로졸", "카페시타빈", "아자티오프린", "타크로리무스",
    "토파시티닙", "테노포비르", "엔테카비르", "카베르골린",
    # 마취/규제·진정·벤조
    "미다졸람", "디아제팜", "로라제팜", "에스조피클론", "로쿠로늄",
    # 정신건강/항정신병/항우울/ADHD
    "할로페리돌", "아미설프리드", "팔리페리돈", "블로난세린", "클로자핀", "부프로피온",
    "둘록세틴", "벤라팍신", "데스벤라팍신", "트라조돈", "독세핀", "클로미프라민",
    # 항전간/기분조절(임상판단·상호작용 민감)
    "카르바마제핀", "옥스카르바제핀", "발프로산", "페람파넬",
    # 항혈전/항혈소판
    "클로피도그렐", "아픽사반", "트리플루살",
    # 호르몬/피임(특수군)
    "디에노게스트", "프로게스테론", "레보노르게스트렐", "티볼론",
]

# source_check_candidate 명시 후보맵(grounded in actual ranks 301-500 ingredients).
# 채택 기준: 국내 단일 경구 완제 가능 + uncovered + 비민감 + 라벨 직접 동거어 **개연**이 있는 known mechanism.
# 값: (proposed_nutrient, mechanism, detector_key, reason)
# ⚠️ 계열 일반화 금지: 세팔로스포린×철 킬레이션은 성분특이(세프디니르 적색복합) — 아래 세파 후보는
#    "라벨 직접 동거어 있으면만 confirmed" 의 fetch 검증 대상이지 자동 confirmed 가 아니다(batch3 reject 선례).
SOURCE_CHECK_MAP = {
    "세푸록심": ("철분", "absorption", "iron_absorption",
              "세푸록심악세틸(경구) 위산의존 흡수. 세팔로스포린×철 계열 일반화 금지 — 라벨 직접 철 동거어만 채택."),
    "세프카펜": ("철분", "absorption", "iron_absorption",
              "세프카펜피복실(경구). 철 킬레이션 가설, 라벨 직접 동거어만 채택(계열 일반화 금지)."),
    "세프디토렌": ("철분", "absorption", "iron_absorption",
               "세프디토렌피복실(경구). 철 직접 동거어만 채택(계열 일반화 금지)."),
}


def is_extra_sensitive(ing):
    return any(k in ing for k in EXTRA_SENSITIVE)


def map_key(ing):
    for k in SOURCE_CHECK_MAP:
        if k in ing:
            return k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    full = json.load(open(FULL, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))
    ents = full["entries"]

    prod = Counter()
    rc = Counter()
    for e in ents:
        ing = e.get("ingredient_name")
        if not ing:
            continue
        prod[ing] += 1
        if e.get("display_mode") == "relation_card":
            rc[ing] += 1
    ranked = prod.most_common()  # 1-300 과 동일 tie-break(연속성)
    band = ranked[BAND_LO - 1:BAND_HI]  # ranks 301..500

    covered_bases = sorted({r["ingredient"] for r in exp["relations"]})

    def covered(ing):
        if rc[ing] > 0:
            return True
        return any(c and (c in ing or ing in c) for c in covered_bases)

    out = []
    for off, (ing, cnt) in enumerate(band):
        rank = BAND_LO + off
        cls = kpi.classify(ing)
        is_combo = "/" in ing
        mk = map_key(ing)
        nutrient = mech = detkey = ""
        ksafe = "false"
        risk = ""
        if covered(ing):
            pc = "already_covered_or_drafted"
            reason = "이미 relation 보유(성분 base 매칭 또는 relation_card 품목 존재) — 재후보화 불필요."
        elif cls in kpi.SENSITIVE_CLASSES or is_extra_sensitive(ing):
            pc = "sensitive_hold"
            reason = ("민감/고위험군(정신건강·항혈전·항암/면역억제·마취/규제·호르몬 특수군) — "
                      "임상판단·출혈/상호작용/이식/규제 위험으로 참고정보 베타 범위 밖(clinical reviewer 트랙 전 hold).")
        elif mk and not is_combo:
            pc = "source_check_candidate"
            nutrient, mech, detkey, reason = SOURCE_CHECK_MAP[mk]
            risk = "low"
        elif is_combo:
            pc = "rejected_precheck"
            reason = ("복합제(2성분 이상) — 단일 성분-영양소 relation 모델 부적합·짝이온/조성 트랩 위험. "
                      "단일 경구 완제 후보 아님(복합제 함유 trap 제외).")
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

    dist = Counter(r["precheck_class"] for r in out)
    print(f"=== Top{BAND_LO}-{BAND_HI} precheck: {len(out)}건 ===")
    print(f"분포: {dict(dist)}")
    print("source_check_candidate:")
    for r in out:
        if r["precheck_class"] == "source_check_candidate":
            print(f"  r{r['rank']} {r['ingredient']} × {r['proposed_nutrient']} ({r['mechanism']}/{r['detector_key']})")

    if not args.no_write:
        cols = ["rank", "ingredient", "product_count", "therapeutic_class", "precheck_class",
                "proposed_nutrient", "mechanism", "detector_key", "potassium_safety", "risk_level",
                "recovery_promoted", "reason"]
        os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
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
