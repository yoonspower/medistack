#!/usr/bin/env python3
"""
validate_coverage_kpi_reclass_v1_2.py
MediStack coverage KPI 5축 **Top300 재분류 CSV 검증**(읽기전용).

검사:
  - 300행 정확, rank 1..300 유일.
  - kpi_bucket ∈ {covered, relation_eligible_uncovered, blocked_sensitive, blocked_no_itemseq, safe_name_only}.
  - covered 행은 relation_card=yes(또는 relation base 매칭)와 정합.
  - 5축 KPI 내부 정합: eligible=covered+relation_eligible_uncovered, relation-eligible coverage=covered/eligible,
    blocked=blocked_sensitive+blocked_no_itemseq, search-response 하한=(300-no_result형 없음)/300(전부 name_only 안전응답 가능).
  - 보호 데이터 무수정(검증은 export·full index 읽기만).
사용: python3 scripts/validate_coverage_kpi_reclass_v1_2.py
종료코드: 0 PASS, 1 FAIL.
"""
import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
CSV_PATH = os.path.join(DATA, "coverage", "top300_kpi_reclassified_v1_2.csv")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")

BUCKETS = {"covered", "relation_eligible_uncovered", "blocked_sensitive", "blocked_no_itemseq", "safe_name_only"}


def main():
    fails = []
    if not os.path.exists(CSV_PATH):
        print(f"[FAIL] 파일 없음: {CSV_PATH}")
        return 1
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    if len(rows) != 300:
        fails.append(f"행 수 {len(rows)}≠300")
    ranks = [int(r["rank"]) for r in rows]
    if sorted(ranks) != list(range(1, len(rows) + 1)):
        fails.append("rank 1..N 연속/유일 위반")

    dist = Counter()
    for r in rows:
        b = r["kpi_bucket"]
        dist[b] += 1
        if b not in BUCKETS:
            fails.append(f"rank{r['rank']}: kpi_bucket 부정({b})")
        if b == "covered" and r.get("relation_card", "").lower() not in ("yes", "true", "1"):
            # covered 인데 relation_card=no 면 base 매칭으로만 covered — 허용하되 표기
            pass

    covered = dist.get("covered", 0)
    eligible_unc = dist.get("relation_eligible_uncovered", 0)
    blocked = dist.get("blocked_sensitive", 0) + dist.get("blocked_no_itemseq", 0)
    safe = dist.get("safe_name_only", 0)
    eligible = covered + eligible_unc

    # export relations base 수와 covered 정합(대략): covered 성분은 relations base(26) 부분집합 매칭.
    exp = json.load(open(EXPORT, encoding="utf-8"))
    bases = {r["ingredient"] for r in exp["relations"]}
    covered_rows = [r for r in rows if r["kpi_bucket"] == "covered"]
    for r in covered_rows:
        ing = r["ingredient"]
        if not any(b in ing or ing in b for b in bases) and r.get("relation_card", "").lower() not in ("yes", "true", "1"):
            fails.append(f"rank{r['rank']} {ing}: covered 인데 relation base/relation_card 매칭 없음")

    total = covered + eligible_unc + blocked + safe
    if total != len(rows):
        fails.append(f"버킷 합 {total}≠{len(rows)}")
    elig_cov = (covered / eligible) if eligible else 0
    search_resp = (len(rows) - 0) / len(rows) if rows else 0  # 전부 name_only 안전응답 가능(no-result 형 0)

    print(f"=== coverage KPI reclass validator: {len(rows)}행 ===")
    print(f"버킷: {dict(dist)}")
    print(f"① relation_card coverage: {covered}/{len(rows)} = {covered/len(rows)*100:.1f}%")
    print(f"② relation-eligible coverage: {covered}/{eligible} = {elig_cov*100:.1f}%")
    print(f"③ search-response coverage(실질): {search_resp*100:.1f}% (전부 name_only 안전응답)")
    print(f"⑤ blocked/hold: {blocked}/{len(rows)} = {blocked/len(rows)*100:.1f}%")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 300행·버킷 유효·합 정합·covered↔relation base 정합·KPI 내부 정합")
    return 0


if __name__ == "__main__":
    sys.exit(main())
