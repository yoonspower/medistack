#!/usr/bin/env python3
"""
harvest_relation_candidates.py
MediStack relation factory — 후보 제안 목록을 full index 17,580 / popular seed 에 매칭해
counts·impact·risk score 를 붙인 후보 CSV 를 생성한다 (읽기 전용 분석 스크립트).

⚠️ 절대 규칙 (위반 금지):
  - 보호 데이터(relation export / full index / aliases / src / .github / validator)를 한 줄도 쓰지 않는다.
    full index·seed CSV 는 **읽기 매칭만** 한다.
  - source_status 는 후보가 들고온 값(needs_source / candidate_only / source_check_needed)을 그대로 보존한다.
    어떤 후보도 source_confirmed 로 자동 승격하지 않는다.
  - 모든 출력 행 do_not_implement_yet=true.
  - 이 스크립트는 relation 을 만들지 않는다. 후보 큐(CSV)만 만든다. PM 승인 + source 확인 전까지 통합 금지.

입력(읽기):
  data/candidates/relation_factory_candidates_input_v1_2.json  (후보 제안 목록 — 이 프롬프트 JSON)
  data/full_drug_name_index_sample_v1_0.json                   (17,580 = relation_card 1,077 + name_only 16,503)
  data/popular_drug_seed_candidates_v1_1.csv                    (seed 120 — popular-like 인지도 기반)

출력(분석 산출물만):
  data/relation_factory_candidates_v1_2.csv

사용:
  python3 scripts/harvest_relation_candidates.py
  python3 scripts/harvest_relation_candidates.py --in <후보 JSON 경로>
  python3 scripts/harvest_relation_candidates.py --no-write   (계산만, CSV 미기록)
종료 코드: 0 정상, 1 무결성 위반(STOP).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")

DEFAULT_INPUT = os.path.join(DATA, "candidates", "relation_factory_candidates_input_v1_2.json")
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
SEED_CSV = os.path.join(DATA, "popular_drug_seed_candidates_v1_1.csv")
OUT_CSV = os.path.join(DATA, "relation_factory_candidates_v1_2.csv")

# 기준 수치(불변) — 어긋나면 STOP. (full index 무수정 확인용)
EXPECT_INDEX_TOTAL = 17580
EXPECT_RELATION_CARD = 1077
EXPECT_NAME_ONLY = 16503

# 허용된 source_status (이 셋 외 값은 무결성 위반). source_confirmed 자동 승격 금지.
ALLOWED_SOURCE_STATUS = {"needs_source", "candidate_only", "source_check_needed"}

# 매칭 불가(성분이 아니라 분류/일반 서술)인 ingredient_or_class — counts=0 으로 두고 noise 방지.
# 매칭을 일부러 건너뛰는 항목(허브 일반·소아 일반·항암 일반 등 비-성분 라벨).
NON_INGREDIENT_LABELS = {
    "소아 일반(미지정)",
    "경구 항암제 일반(이마티닙/카페시타빈 등)",
}

CSV_COLUMNS = [
    "candidate_id",
    "candidate_theme",
    "drug_class",
    "ingredient_or_class",
    "expected_nutrient",
    "expected_relation_direction",
    "related_existing_relation_ids",
    "candidate_source",
    "estimated_card_impact",
    "matched_item_count",
    "name_only_item_count",
    "popular_seed_match_count",
    "source_status",
    "source_needed",
    "risk_level",
    "caution_flags",
    "user_value_score",
    "impact_score",
    "source_priority",
    "next_action",
    "do_not_implement_yet",
]


def load_candidates(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_index():
    with open(FULL_INDEX, encoding="utf-8") as f:
        d = json.load(f)
    entries = d["entries"]
    # 무결성 확인 — full index 가 기대 수치와 다르면 STOP (변형/오염 방지).
    total = len(entries)
    name_only = sum(1 for e in entries if e.get("display_mode") == "name_only")
    relation_card = sum(1 for e in entries if e.get("display_mode") == "relation_card")
    if (total, relation_card, name_only) != (
        EXPECT_INDEX_TOTAL,
        EXPECT_RELATION_CARD,
        EXPECT_NAME_ONLY,
    ):
        sys.stderr.write(
            "STOP: full index 수치 불일치 "
            f"(total={total} relation_card={relation_card} name_only={name_only}; "
            f"기대 {EXPECT_INDEX_TOTAL}/{EXPECT_RELATION_CARD}/{EXPECT_NAME_ONLY}). 매칭 중단.\n"
        )
        sys.exit(1)
    return entries


def load_seed_names():
    names = []
    with open(SEED_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            q = (row.get("query_name") or "").strip()
            if q:
                names.append(q)
    return names


def count_index_matches(entries, ingredient):
    """ingredient_or_class 를 full index 의 ingredient_name 에 부분문자열 매칭.
    복합제(예: 로수바스타틴/에제티미브)도 잡기 위해 substring 사용.
    returns (matched_item_count, name_only_item_count).
    matched = ingredient_name 에 후보 성분 문자열이 포함된 모든 품목,
    name_only = 그 중 display_mode == name_only (= 아직 relation 미연결, 신규 커버 가능).
    """
    matched = 0
    name_only = 0
    for e in entries:
        ing = e.get("ingredient_name") or ""
        if ingredient and ingredient in ing:
            matched += 1
            if e.get("display_mode") == "name_only":
                name_only += 1
    return matched, name_only


def count_seed_matches(seed_names, ingredient):
    """후보 성분이 seed query_name 과 부분문자열로 겹치는 seed 수.
    양방향 substring (성분이 seed 에 포함되거나 seed 가 성분에 포함)."""
    n = 0
    for s in seed_names:
        if not s or not ingredient:
            continue
        if ingredient in s or s in ingredient:
            n += 1
    return n


def estimate_card_impact(name_only_count):
    """name_only_item_count 기반 추정 등급(데이터 무변경, 휴리스틱).
    name_only = 신규 relation 으로 새로 커버될 잠재 품목 수 (relation_card 는 이미 covered).
    """
    if name_only_count == 0:
        return "none(0)"
    if name_only_count >= 200:
        return f"very_high({name_only_count})"
    if name_only_count >= 50:
        return f"high({name_only_count})"
    if name_only_count >= 10:
        return f"medium({name_only_count})"
    return f"low({name_only_count})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=DEFAULT_INPUT, help="후보 제안 목록 JSON 경로")
    ap.add_argument("--no-write", action="store_true", help="계산만, CSV 미기록")
    args = ap.parse_args()

    candidates = load_candidates(args.inp)
    entries = load_index()
    seed_names = load_seed_names()

    rows = []
    integrity_errors = []
    for c in candidates:
        cid = c.get("candidate_id", "")
        ingredient = (c.get("ingredient_or_class") or "").strip()
        status = c.get("source_status", "")

        # 무결성: source_status 가 허용셋이 아니면 기록(승격 금지).
        if status not in ALLOWED_SOURCE_STATUS:
            integrity_errors.append(f"{cid}: source_status='{status}' 허용셋 밖")

        # 매칭 (비-성분 라벨은 0)
        if ingredient in NON_INGREDIENT_LABELS:
            matched, name_only = 0, 0
        else:
            matched, name_only = count_index_matches(entries, ingredient)
        seed_n = count_seed_matches(seed_names, ingredient)
        card_impact = estimate_card_impact(name_only)

        rel_ids = c.get("related_existing_relation_ids") or []
        rel_ids_str = ";".join(str(x) for x in rel_ids)

        rows.append(
            {
                "candidate_id": cid,
                "candidate_theme": c.get("candidate_theme", ""),
                "drug_class": c.get("drug_class", ""),
                "ingredient_or_class": ingredient,
                "expected_nutrient": c.get("expected_nutrient", ""),
                "expected_relation_direction": c.get("expected_relation_direction", ""),
                "related_existing_relation_ids": rel_ids_str,
                "candidate_source": c.get("candidate_source", ""),
                "estimated_card_impact": card_impact,
                "matched_item_count": matched,
                "name_only_item_count": name_only,
                "popular_seed_match_count": seed_n,
                "source_status": status,
                "source_needed": c.get("source_needed", ""),
                "risk_level": c.get("risk_level", ""),
                "caution_flags": c.get("caution_flags", ""),
                "user_value_score": c.get("user_value_score", ""),
                "impact_score": c.get("impact_score", ""),
                "source_priority": c.get("source_priority", ""),
                "next_action": c.get("next_action", ""),
                # 모든 후보 통합 금지 — 항상 true.
                "do_not_implement_yet": "true",
            }
        )

    # 출력 정렬: source_priority(P2 < P3 < hold) → name_only_item_count desc → candidate_id
    prio_rank = {"P1": 0, "P2": 1, "P3": 2, "hold": 3}
    rows.sort(
        key=lambda r: (
            prio_rank.get(r["source_priority"], 9),
            -int(r["name_only_item_count"]),
            r["candidate_id"],
        )
    )

    # 무결성 게이트 — source_confirmed 자동 승격 0건 확인.
    confirmed = [r for r in rows if r["source_status"] == "source_confirmed"]
    if confirmed:
        integrity_errors.append(
            f"source_confirmed 자동 승격 {len(confirmed)}건 발견 — 금지"
        )
    not_dni = [r for r in rows if r["do_not_implement_yet"] != "true"]
    if not_dni:
        integrity_errors.append(f"do_not_implement_yet != true {len(not_dni)}건")

    # 리포트
    ss = Counter(r["source_status"] for r in rows)
    sp = Counter(r["source_priority"] for r in rows)
    rl = Counter(r["risk_level"] for r in rows)
    print(f"후보 행수: {len(rows)}")
    print(f"source_status: {dict(ss)}")
    print(f"source_priority: {dict(sp)}")
    print(f"risk_level: {dict(rl)}")
    print(f"source_confirmed: {len(confirmed)} (기대 0)")
    print(f"do_not_implement_yet=true: {len(rows) - len(not_dni)}/{len(rows)}")

    if integrity_errors:
        sys.stderr.write("STOP: 무결성 위반:\n  - " + "\n  - ".join(integrity_errors) + "\n")
        sys.exit(1)

    if args.no_write:
        print("(--no-write) CSV 미기록")
        return

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"기록: {OUT_CSV} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
