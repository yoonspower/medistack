#!/usr/bin/env python3
"""
analyze_coverage_kpi_v1_3_draft.py
MediStack — coverage KPI **5축 재정의** 초안(읽기전용, 결정론적).

배경: 기존 "Top300 relation_card 95% 목표"는 부정확하다. relation_card 가 없어도 검색은
**안전하게 응답**(name_only / 정보없음)하므로 "정보 없음 = 실패"가 아니다. 그래서 단일 비율 대신
**5축**으로 coverage 를 재정의하고, Top300 각 성분을 5축 관점 버킷으로 재분류한다.

5축 KPI(이 스크립트가 모두 산출):
  ① relation_card coverage      : relation_card 있는 성분/품목 비율(현 기준선 — 무리하게 95% 목표 삼지 않음)
  ② relation-eligible coverage  : 참고정보 **근거가 있는** 성분 중 source_confirmed 비율(분모=eligible만)
  ③ search-response coverage    : 검색 시 relation_card OR 안전한 name_only/정보없음 응답 가능 비율(≈100%)
  ④ weighted coverage           : 품목수 가중 relation_card coverage(현 기준선)
  ⑤ blocked/hold coverage       : 민감군·literature_only·itemSeq 없음·계열 일반화 금지로 막힌 비율

⚠️ 이 스크립트는 **분석 전용**이다. source_confirmed/draft/live 판정을 새로 하거나 바꾸지 않는다.
   앞단계 ledger(relations 59 = source_confirmed ground truth)를 **읽기전용**으로 인용만 한다.
⚠️ 보호 데이터(export/full index/alias/src/.github/validator) 한 줄도 수정하지 않는다(읽기만).
   기존 v1_2 스크립트의 CLASS_RULES·classify·covered_match·SENSITIVE_CLASSES 를 import 재사용한다.

읽기: full index(품목수 proxy·display_mode·item_seq) · export(relations=source_confirmed) · v1_2 랭킹 로직.
쓰기(분석 산출물만, --no-write 로 끄기 가능):
  data/coverage/top300_kpi_reclassified_v1_2.csv
사용: python3 scripts/analyze_coverage_kpi_v1_3_draft.py [--top N] [--no-write]
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict

# 기존 v1_2 로직 재사용(보호데이터 무수정 읽기전용). 같은 scripts/ 폴더.
from analyze_coverage_kpi_v1_2 import (
    CLASS_RULES, SENSITIVE_CLASSES, classify, covered_match,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
OUT_DIR = os.path.join(DATA, "coverage")
OUT_CSV = os.path.join(OUT_DIR, "top300_kpi_reclassified_v1_2.csv")

# 5축 버킷 정의(재분류 CSV의 kpi_bucket 값).
#   covered                     : relation_card 보유(=source_confirmed 근거 존재) → ①④에 산입
#   relation_eligible_uncovered : 상호작용 근거가 있을 개연이 큰 계열인데 아직 미커버 → ② 분모(eligible)·미충족
#   blocked_sensitive           : 민감/고위험군(정신건강·항혈전·항암) → ⑤ hold, reviewer 트랙 전 차단
#   blocked_no_itemseq          : 품목 식별자(item_seq) 없음 → relation_card 렌더 불가, ⑤ blocked
#   safe_name_only              : 근거 약하거나 일반 성분 → name_only/정보없음 안전응답(③에서 성공, 실패 아님)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=300)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    full = json.load(open(FULL, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))
    ents = full["entries"]
    counts = full["meta"]["counts"]

    # 성분별 품목수(복용빈도 proxy) + relation_card 품목수 + item_seq 결손 품목수
    prod_count = Counter()
    rc_count = Counter()
    no_seq_count = Counter()
    for e in ents:
        ing = e.get("ingredient_name")
        if not ing:
            continue
        prod_count[ing] += 1
        if e.get("display_mode") == "relation_card":
            rc_count[ing] += 1
        if not e.get("item_seq"):
            no_seq_count[ing] += 1

    # relations(=source_confirmed ground truth, 읽기전용 인용)
    covered_bases = sorted({r["ingredient"] for r in exp["relations"]})

    # relation-eligible: 상호작용 근거 메커니즘(absorption/depletion)이 알려진 치료군 계열.
    #   relations 의 mechanism 이 흡수저해/고갈에 집중 → 같은 메커니즘 개연이 큰 치료군을 eligible 로 본다.
    #   ⚠️ eligible 판정은 "근거가 있을 개연" 추정일 뿐, relation 확정이 아니다(source-check 필요).
    ELIGIBLE_CLASSES = {
        "소화/위장", "항생/항균", "골다공증", "갑상선/내분비",
        "고혈압/심혈관", "당뇨",
    }

    ranked = prod_count.most_common()  # 결정론: Counter.most_common 은 동수일 때 삽입순(파일 순서) 유지
    topN = ranked[:args.top]

    rows = []
    for rank, (ing, cnt) in enumerate(topN, start=1):
        cls = classify(ing)
        cov_base = covered_match(ing, covered_bases)
        rc = rc_count[ing]
        covered = bool(cov_base) or rc > 0
        sensitive = cls in SENSITIVE_CLASSES
        all_no_seq = cnt > 0 and no_seq_count[ing] == cnt  # 모든 품목에 item_seq 없음
        eligible = cls in ELIGIBLE_CLASSES

        if covered:
            bucket = "covered"
            reason = (f"relation_card 보유(base={cov_base or ing}, "
                      f"relation_card 품목 {rc}건) — source_confirmed 근거 존재")
        elif sensitive:
            bucket = "blocked_sensitive"
            reason = (f"민감/고위험군({cls}) — 임상판단·출혈/상호작용 위험으로 "
                      "clinical reviewer 트랙 전까지 hold")
        elif all_no_seq:
            bucket = "blocked_no_itemseq"
            reason = "전 품목 item_seq 결손 — 허가사항 식별 불가, relation_card 렌더 차단"
        elif eligible:
            bucket = "relation_eligible_uncovered"
            reason = (f"근거 개연 계열({cls}, 흡수/고갈 메커니즘 후보)인데 미커버 — "
                      "source-check 우선 대상(확정 아님)")
        else:
            bucket = "safe_name_only"
            reason = (f"근거 약함/일반 계열({cls}) — name_only/정보없음 안전응답, "
                      "검색은 정상 응답(실패 아님)")

        rows.append({
            "rank": rank,
            "ingredient": ing,
            "product_count": cnt,
            "therapeutic_class": cls,
            "relation_card": "yes" if covered else "no",
            "kpi_bucket": bucket,
            "reason": reason,
        })

    # ---------- 5축 KPI 집계 (Top N) ----------
    n = len(rows)
    bucket_n = Counter(r["kpi_bucket"] for r in rows)
    bucket_p = Counter()
    for r in rows:
        bucket_p[r["kpi_bucket"]] += r["product_count"]
    top_products = sum(r["product_count"] for r in rows)

    n_covered = bucket_n["covered"]
    p_covered = bucket_p["covered"]
    n_eligible = bucket_n["covered"] + bucket_n["relation_eligible_uncovered"]
    n_blocked = (bucket_n["blocked_sensitive"] + bucket_n["blocked_no_itemseq"])
    p_blocked = (bucket_p["blocked_sensitive"] + bucket_p["blocked_no_itemseq"])

    # ① relation_card coverage (성분)
    kpi1_ing = n_covered / n if n else 0.0
    # ② relation-eligible coverage = covered / eligible (분모=eligible만)
    kpi2 = (n_covered / n_eligible) if n_eligible else 0.0
    # ③ search-response coverage = covered + safe_name_only + (eligible_uncovered 도 안전응답 가능)
    #    blocked 만 "응답은 되지만 의도된 정보 차단" → 보수적으로 분자에서 제외해 하한 제시.
    #    실제로는 blocked 도 name_only 안전응답은 되므로 ③ 실질 ≈100%(주석으로 명시).
    n_safe_response = n - n_blocked
    kpi3 = n_safe_response / n if n else 0.0
    kpi3_full = 1.0  # blocked 포함 시 모든 검색은 최소 안전응답 가능
    # ④ weighted coverage (품목수 가중 relation_card)
    kpi4 = (p_covered / top_products) if top_products else 0.0
    # ⑤ blocked/hold coverage
    kpi5_ing = n_blocked / n if n else 0.0
    kpi5_p = (p_blocked / top_products) if top_products else 0.0

    def pct(x):
        return f"{x*100:.1f}%"

    print(f"=== coverage KPI 5축 재정의 (Top {n} 성분 by 품목수 proxy) ===")
    print(f"고유 성분 총: {len(prod_count)} | relation 보유 성분(source_confirmed base): {len(covered_bases)}")
    print(f"버킷 분포(성분): {dict(bucket_n)}")
    print(f"버킷 분포(품목수): {dict(bucket_p)}")
    print("-" * 60)
    print(f"① relation_card coverage(성분)   : {n_covered}/{n} = {pct(kpi1_ing)}")
    print(f"② relation-eligible coverage     : {n_covered}/{n_eligible} = {pct(kpi2)} (분모=eligible)")
    print(f"③ search-response coverage(하한)  : {n_safe_response}/{n} = {pct(kpi3)}")
    print(f"③ search-response coverage(실질)  : {pct(kpi3_full)} (blocked 도 name_only 안전응답)")
    print(f"④ weighted coverage(품목)        : {p_covered:,}/{top_products:,} = {pct(kpi4)}")
    print(f"⑤ blocked/hold coverage(성분)    : {n_blocked}/{n} = {pct(kpi5_ing)}")
    print(f"⑤ blocked/hold coverage(품목)    : {p_blocked:,}/{top_products:,} = {pct(kpi5_p)}")

    if not args.no_write:
        os.makedirs(OUT_DIR, exist_ok=True)
        cols = ["rank", "ingredient", "product_count", "therapeutic_class",
                "relation_card", "kpi_bucket", "reason"]
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)}")
    else:
        print("\n(--no-write)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
