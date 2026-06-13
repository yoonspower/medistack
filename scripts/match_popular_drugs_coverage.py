#!/usr/bin/env python3
"""
match_popular_drugs_coverage.py
MediStack — popular-like 약 seed 후보를 full index 17,580 / relation_card 558 / name_only 17,022 에
매칭해 커버리지를 분류한다 (읽기 전용 분석 스크립트).

⚠️ 이 스크립트는 보호 데이터(relation/full index/alias/export/src)를 한 줄도 수정하지 않는다.
   seed 리스트는 **실측 검색량이 아니라 임상/OTC 인지도 기반 priority_seed_rank** 다 (외부 데이터 없음).
   출력은 covered / name_only_only / missing / ambiguous 분류뿐이며 relation 을 생성하지 않는다.

읽기:
  data/popular_drug_seed_candidates_v1_1.csv      (seed 후보 — priority_seed_rank, query_name, ...)
  data/full_drug_name_index_sample_v1_0.json      (17,580 = relation_card 558 + name_only 17,022)
  data/relation_card_coverage_snapshot_v1_1.csv   (relation_card 558 스냅샷 — 교차검증용)
  data/medistack_v0.3_aliases.json                (alias 621 = ingredient 38 + product 583)
  data/medistack_v0.2_beta_export.json            (relation 30 — relation 제목/연결용)

쓰기(분석 산출물만):
  data/popular_drug_coverage_match_v1_1.csv
  docs/MediStack_popular_drug_coverage_match.md

사용:
  python3 scripts/match_popular_drugs_coverage.py
  python3 scripts/match_popular_drugs_coverage.py --no-write
종료 코드: 0 정상, 1 기준 수치 불일치(STOP)
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
DOCS = os.path.join(REPO, "docs")

SEED_CSV = os.path.join(DATA, "popular_drug_seed_candidates_v1_1.csv")
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
SNAPSHOT_CSV = os.path.join(DATA, "relation_card_coverage_snapshot_v1_1.csv")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")

OUT_CSV = os.path.join(DATA, "popular_drug_coverage_match_v1_1.csv")
OUT_MD = os.path.join(DOCS, "MediStack_popular_drug_coverage_match.md")

# 기준 수치(불변) — 어긋나면 STOP
EXPECT = {"total": 17580, "relation_card": 558, "name_only": 17022, "relations": 30}

# 민감 약군 게이트 — name_only_only 라도 relation_expansion_candidate 로 라벨하지 않고
# high_risk_hold 로 분리한다(정신건강·항응고/항혈소판·임신/피임). priority_plan §5 와 일치.
SENSITIVE_CATEGORIES = {"수면/진정/정신건강"}
SENSITIVE_INGREDIENTS = {"클로피도그렐", "리바록사반", "드로스피레논", "와파린"}


def load():
    seeds = list(csv.DictReader(open(SEED_CSV, encoding="utf-8")))
    full = json.load(open(FULL_INDEX, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))
    snap = list(csv.DictReader(open(SNAPSHOT_CSV, encoding="utf-8")))
    return seeds, full, aliases, exp, snap


def build_index(full, aliases, exp):
    ents = full["entries"]
    rc = [e for e in ents if e.get("display_mode") == "relation_card"]
    no = [e for e in ents if e.get("display_mode") == "name_only"]

    by_norm = defaultdict(list)
    for e in ents:
        by_norm[e.get("normalized_item_name", "")].append(e)

    # ingredient_alias: alias(소문자) -> canonical_ingredient
    ing_alias = {}
    for a in aliases.get("ingredient_aliases", []):
        ing_alias[a["alias"].strip().lower()] = a["canonical_ingredient"]
    # product_alias: alias(소문자) -> (item_seq, canonical_ingredient)
    prod_alias = {}
    for a in aliases.get("product_aliases", []):
        prod_alias[a["alias"].strip().lower()] = (a.get("item_seq", ""), a.get("canonical_ingredient", ""))

    # ingredient -> relations (relation 제목/연결)
    ing2rel = defaultdict(list)
    for r in exp["relations"]:
        ing2rel[r["ingredient"]].append(r)

    return ents, rc, no, by_norm, ing_alias, prod_alias, ing2rel


def check_baseline(ents, rc, no, exp, snap):
    actual = {"total": len(ents), "relation_card": len(rc),
              "name_only": len(no), "relations": len(exp["relations"])}
    ok = actual == EXPECT
    print("=== 기준 수치 검증 ===")
    for k in EXPECT:
        flag = "OK" if actual[k] == EXPECT[k] else "MISMATCH"
        print(f"  {k}: {actual[k]} (기대 {EXPECT[k]}) [{flag}]")
    # 스냅샷 교차검증: 스냅샷 행수 == relation_card 수
    snap_ok = len(snap) == EXPECT["relation_card"]
    print(f"  snapshot rows: {len(snap)} (기대 {EXPECT['relation_card']}) [{'OK' if snap_ok else 'MISMATCH'}]")
    return ok and snap_ok


def rel_title(r):
    return f"{r['ingredient']}×{r['nutrient']}"


def match_seed(seed, ents, by_norm, ing_alias, prod_alias, ing2rel):
    """precedence: normalized exact -> alias -> ingredient(exact/substring) -> brand_core(item substring).
    returns dict of match result fields."""
    q = seed["query_name"].strip()
    ql = q.lower()
    method = None
    matched = []

    # 1) normalized item name exact
    if q in by_norm and by_norm[q]:
        matched = list(by_norm[q])
        method = "normalized_exact"

    # 2) alias match
    if not matched:
        canon = None
        if ql in ing_alias:
            canon = ing_alias[ql]
            method = "alias_ingredient"
        elif ql in prod_alias:
            seq, canon = prod_alias[ql]
            method = "alias_product"
        if canon:
            matched = [e for e in ents if e.get("ingredient_name") and
                       (e["ingredient_name"] == canon or canon in e["ingredient_name"])]

    # 3) ingredient match (exact preferred, then substring for salt-form/combo)
    if not matched:
        exact = [e for e in ents if e.get("ingredient_name") == q]
        if exact:
            matched = exact
            method = "ingredient_exact"
        else:
            sub = [e for e in ents if e.get("ingredient_name") and q in e["ingredient_name"]]
            if sub:
                matched = sub
                method = "ingredient_substring"

    # 4) brand_core: item_name substring (lowest confidence)
    if not matched:
        bc = [e for e in ents if q in e.get("item_name", "")]
        if bc:
            matched = bc
            method = "brand_core_item_substring"

    # ---- classify ----
    rc_m = [e for e in matched if e.get("display_mode") == "relation_card"]
    no_m = [e for e in matched if e.get("display_mode") == "name_only"]
    distinct_ings = sorted({e.get("ingredient_name", "") for e in matched if e.get("ingredient_name")})

    ambiguous = method == "brand_core_item_substring" and len(distinct_ings) > 1

    if not matched:
        status = "missing_from_full_index"
    elif ambiguous:
        status = "ambiguous_manual_review"
    elif rc_m:
        status = "relation_card_covered"
    else:
        status = "name_only_only"

    # representative matched item + relation linkage
    rep = (rc_m[0] if rc_m else (matched[0] if matched else None))
    matched_item_seq = rep["item_seq"] if rep else ""
    matched_item_name = rep["item_name"] if rep else ""
    matched_ing = ";".join(distinct_ings[:5])
    display_mode = rep["display_mode"] if rep else ""

    rel_ids, rel_titles = [], []
    for ing in {e.get("ingredient_name") for e in rc_m}:
        for r in ing2rel.get(ing, []):
            rel_ids.append(str(r["id"]))
            rel_titles.append(rel_title(r))

    # confidence
    conf = {
        "normalized_exact": "high", "ingredient_exact": "high",
        "alias_ingredient": "high", "alias_product": "high",
        "ingredient_substring": "medium",
        "brand_core_item_substring": "low",
    }.get(method, "n/a")

    # reason
    if status == "relation_card_covered":
        reason = f"{method}: relation_card {len(rc_m)}건 + name_only {len(no_m)}건 — 이미 참고정보 표시"
    elif status == "name_only_only":
        reason = f"{method}: name_only {len(no_m)}건만, relation_card 0건 — 이름은 있으나 정보 없음"
    elif status == "missing_from_full_index":
        reason = "인덱스에 매칭 품목 없음 (정규/alias/성분/브랜드 모두 불일치)"
    else:
        reason = f"{method}: 다중 성분({len(distinct_ings)}) 모호 매칭 — 수동 확인 필요"

    # next_action
    prev = (seed.get("est_prevalence") or "").strip()
    is_sensitive = (seed["seed_category"] in SENSITIVE_CATEGORIES) or (q in SENSITIVE_INGREDIENTS)
    if status == "relation_card_covered":
        next_action = "no_action (already covered)"
    elif status == "name_only_only":
        if is_sensitive:
            next_action = "high_risk_hold (sensitive group)"
        elif prev in ("high", "medium"):
            next_action = "relation_expansion_candidate"
        else:
            next_action = "monitor (low prevalence)"
    elif status == "missing_from_full_index":
        next_action = "full_index_expansion_candidate (별도 트랙)"
    else:
        next_action = "manual_review"

    return {
        "seed_rank": seed["priority_seed_rank"],
        "query_name": q,
        "seed_category": seed["seed_category"],
        "matched_status": status,
        "matched_item_seq": matched_item_seq,
        "matched_item_name": matched_item_name,
        "matched_ingredient_name": matched_ing,
        "matched_relation_id": ";".join(sorted(set(rel_ids), key=int)) if rel_ids else "",
        "relation_title": "; ".join(sorted(set(rel_titles))) if rel_titles else "",
        "display_mode": display_mode,
        "matched_total": len(matched),
        "matched_relation_card_count": len(rc_m),
        "matched_name_only_count": len(no_m),
        "match_method": method or "none",
        "confidence": conf,
        "reason": reason,
        "next_action": next_action,
        "_est_prevalence": prev,
    }


COLS = ["seed_rank", "query_name", "seed_category", "matched_status",
        "matched_item_seq", "matched_item_name", "matched_ingredient_name",
        "matched_relation_id", "relation_title", "display_mode",
        "matched_total", "matched_relation_card_count", "matched_name_only_count",
        "match_method", "confidence", "reason", "next_action"]


def write_csv(rows):
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLS})
    print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)}  ({len(rows)} rows)")


def pct(n, d):
    return f"{n/d*100:.1f}%" if d else "0.0%"


def write_md(rows):
    n = len(rows)
    sc = Counter(r["matched_status"] for r in rows)
    covered = sc["relation_card_covered"]
    name_only = sc["name_only_only"]
    missing = sc["missing_from_full_index"]
    ambig = sc["ambiguous_manual_review"]

    # category breakdown
    cats = []
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["seed_category"]].append(r)
    # preserve seed order of categories
    seen = []
    for r in rows:
        if r["seed_category"] not in seen:
            seen.append(r["seed_category"])
    for cat in seen:
        cr = by_cat[cat]
        c_cov = sum(1 for x in cr if x["matched_status"] == "relation_card_covered")
        c_no = sum(1 for x in cr if x["matched_status"] == "name_only_only")
        c_mi = sum(1 for x in cr if x["matched_status"] == "missing_from_full_index")
        c_am = sum(1 for x in cr if x["matched_status"] == "ambiguous_manual_review")
        cats.append((cat, len(cr), c_cov, c_no, c_mi, c_am))

    # name_only_only that are relation_expansion_candidate (high/medium prevalence, 민감군 제외)
    no_cands = [r for r in rows if r["matched_status"] == "name_only_only"
                and r["next_action"] == "relation_expansion_candidate"]
    no_cands.sort(key=lambda r: (-r["matched_name_only_count"], int(r["seed_rank"])))
    # 민감 약군(정신건강·항응고/항혈소판·임신/피임) — 후보 아닌 high_risk_hold 로 분리
    high_risk = [r for r in rows if r["next_action"] == "high_risk_hold (sensitive group)"]
    high_risk.sort(key=lambda r: int(r["seed_rank"]))

    L = []
    L.append("# MediStack — popular-like 약 커버리지 매칭 (Coverage Match)\n")
    L.append("> 작성일: 2026-06-13. **분석 전용 — 데이터/렌더 한 줄도 변경하지 않는다.**")
    L.append(f"> 재현: `python3 scripts/match_popular_drugs_coverage.py` (읽기 전용). "
             f"결과 CSV: `data/popular_drug_coverage_match_v1_1.csv`.")
    L.append("> ⚠️ seed 리스트는 **실측 검색량/판매량 데이터가 아니다.** 임상·OTC 인지도 기반 "
             "`priority_seed_rank`(confidence=low) 이며, '인기약 Top N'으로 확정 표현하지 않는다. "
             "외부 인기약 실데이터 매칭은 다음 단계(`data/external_popular_drugs_top100.csv`)로 보완한다.\n")
    L.append("---\n")

    L.append("## 0. 범위와 한계\n")
    L.append("- 본 문서는 **popular-like seed 후보가 현재 relation_card 558 에 얼마나 덮이는지** 정량 분류한다. relation 을 추가하지 않는다.")
    L.append("- 매칭은 성분명 기준(정규명 exact → alias → 성분 exact/substring → 브랜드 부분)으로 결정적이며, 기준 수치(17,580/558/17,022/relation 30) 불일치 시 STOP 한다.")
    L.append('- "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현은 사용하지 않는다. 제공 정보는 허가사항 정리 **참고용**이다.\n')
    L.append("---\n")

    L.append("## 1. seed 후보 요약\n")
    L.append(f"- seed 후보 총수: **{n}**")
    L.append("- 출처: 임상/OTC 인지도 추정 (실측 검색량 아님). confidence=low.")
    L.append("- 매칭 방식: normalized_exact → alias → ingredient(exact/substring) → brand_core(item substring) → 미매칭=missing.")
    L.append("- seed 성분 표기는 인덱스 음역에 맞춰 정렬했다(예: 네비볼롤→네비보롤, 세르트랄린→설트랄린). 표기 불일치로 인한 거짓 missing 을 줄이기 위함이다.\n")

    L.append("## 2. 커버리지 분류 결과\n")
    L.append("| 분류 | 수 | 비율 | 의미 |")
    L.append("|---|---|---|---|")
    L.append(f"| relation_card_covered | **{covered}** | {pct(covered,n)} | 검색 시 이미 참고정보 표시 |")
    L.append(f"| name_only_only | **{name_only}** | {pct(name_only,n)} | 이름은 있으나 정보 없음 (**확장 검토 1차 모집단** — 근거 있는 것만 승격) |")
    L.append(f"| missing_from_full_index | **{missing}** | {pct(missing,n)} | 인덱스에 없음 (full index 확장 트랙) |")
    L.append(f"| ambiguous_manual_review | **{ambig}** | {pct(ambig,n)} | 다중/모호 매칭 (수동 확인) |")
    L.append(f"| 합계 | {n} | 100% | |\n")

    L.append("## 3. 카테고리별 커버리지\n")
    L.append("| 카테고리 | seed | covered | name_only | missing | ambiguous |")
    L.append("|---|---|---|---|---|---|")
    for cat, tot, c_cov, c_no, c_mi, c_am in cats:
        L.append(f"| {cat} | {tot} | {c_cov} | {c_no} | {c_mi} | {c_am} |")
    L.append("")

    L.append("## 4. name_only_only 중 확장 검토 1차 모집단 (high/medium 인지도·민감군 제외)\n")
    L.append("> `next_action=relation_expansion_candidate`. name_only 매핑수 내림차순. "
             "**이 표는 후보 풀(1차 모집단)일 뿐 전부 채택 대상이 아니다** — 확립된 약물-영양소 상호작용 근거가 있는 것만 "
             "`MediStack_relation_expansion_priority_plan.md` 에서 승격한다(암로디핀·항히스타민·감기약 등은 근거 없어 §plan §4 에서 제외).\n")
    L.append("| seed_rank | query_name | 카테고리 | name_only 매핑 | 매칭법 | confidence |")
    L.append("|---|---|---|---|---|---|")
    for r in no_cands:
        L.append(f"| {r['seed_rank']} | {r['query_name']} | {r['seed_category']} | "
                 f"{r['matched_name_only_count']} | {r['match_method']} | {r['confidence']} |")
    L.append(f"\n→ 확장 검토 1차 모집단(name_only_only · high/medium · 민감군 제외): **{len(no_cands)}건**\n")
    if high_risk:
        L.append("### 4-1. high_risk_hold — 민감 약군 (후보화 보류)\n")
        L.append("> 정신건강·항응고/항혈소판·임신/피임 등 민감군. name_only_only 라도 **확장 후보로 올리지 않는다**(criterion 8). "
                 "영양소 관계 근거가 약하거나 임상판단 영역이라 별도 임상검토 전까지 보류. priority_plan §5 참조.\n")
        L.append("| seed_rank | query_name | 카테고리 | name_only 매핑 |")
        L.append("|---|---|---|---|")
        for r in high_risk:
            L.append(f"| {r['seed_rank']} | {r['query_name']} | {r['seed_category']} | {r['matched_name_only_count']} |")
        L.append(f"\n→ high_risk_hold(민감군·후보화 보류): **{len(high_risk)}건**\n")

    L.append("## 5. 이미 covered 인 seed (조치 불필요)\n")
    cov_rows = [r for r in rows if r["matched_status"] == "relation_card_covered"]
    L.append("| query_name | relation_id | relation | rc 매핑 |")
    L.append("|---|---|---|---|")
    for r in sorted(cov_rows, key=lambda x: int(x["seed_rank"])):
        L.append(f"| {r['query_name']} | {r['matched_relation_id']} | {r['relation_title']} | {r['matched_relation_card_count']} |")
    L.append("")

    L.append("## 6. missing_from_full_index (full index 확장 트랙·별도)\n")
    L.append("> ⚠️ 여기서 **missing = 현재 17,580 *샘플* 인덱스에 매칭 품목이 없음**을 뜻한다. "
             "해당 약이 한국에 존재하지 않는다는 의미가 **아니다.** 인덱스는 `full_drug_name_index_sample_v1_0` "
             "= 확장 중인 샘플이다(메타 target_total 기준). 이 항목들은 full index 확장 트랙의 입력이다.\n")
    if missing:
        L.append("| query_name | 카테고리 | 비고 |")
        L.append("|---|---|---|")
        notes = {
            "에스오메프라졸": "인덱스에 에스오메프라졸 품목 0건 → relation16(에스오메프라졸×Mg)이 relation_card 0건인 근본 원인(기존 분석과 일치). 주요 PPI 브랜드(넥시움) 미인덱싱(정량 처방량 단정 아님) → full index 확장 시 우선 검토.",
        }
        for r in [x for x in rows if x["matched_status"] == "missing_from_full_index"]:
            note = notes.get(r["query_name"], "샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음")
            L.append(f"| {r['query_name']} | {r['seed_category']} | {note} |")
        L.append("")
    else:
        L.append("(없음)\n")

    L.append("## 7. ambiguous_manual_review\n")
    if ambig:
        L.append("| query_name | 카테고리 | matched_ingredient | reason |")
        L.append("|---|---|---|---|")
        for r in [x for x in rows if x["matched_status"] == "ambiguous_manual_review"]:
            L.append(f"| {r['query_name']} | {r['seed_category']} | {r['matched_ingredient_name']} | {r['reason']} |")
        L.append("")
    else:
        L.append("(없음 — 모든 매칭이 단일 성분 또는 명확한 계열로 해소됨)\n")

    L.append("## 8. 사용자 체감 가치 평가\n")
    L.append(f"- popular-like seed {n}건 중 **{covered}건({pct(covered,n)})** 은 이미 참고정보가 붙는다 → "
             "흔한 만성질환 핵심군(당뇨 메트포르민·고혈압 HCTZ·갑상선·항생제·골다공증·PPI 오메프라졸)은 검색 시 정보 표시.")
    L.append(f"- 그러나 **{name_only}건({pct(name_only,n)})** 은 name_only_only — 사용자가 흔히 찾는데 정보가 없다. "
             "여기가 체감 가치 향상 여지가 가장 큰 구간이다.")
    L.append("- 가장 큰 공백 카테고리(아래 §9)는 relation 확장 우선순위 입력으로 쓴다.\n")

    L.append("## 9. 가장 큰 공백 카테고리 (확장 우선순위 입력)\n")
    gap = sorted(cats, key=lambda x: -x[3])  # name_only count desc
    L.append("| 카테고리 | name_only_only | 비고 |")
    L.append("|---|---|---|")
    for cat, tot, c_cov, c_no, c_mi, c_am in gap:
        if c_no:
            L.append(f"| {cat} | {c_no} | seed {tot}건 중 |")
    L.append("\n→ 공백이 크고 기존 relation 과 계열 인접성이 높은 카테고리(기타 PPI·스타틴·치아지드 유사·당뇨 외 대사·"
             "비스포스포네이트 인접)를 relation 확장 우선순위로 둔다. 상세는 "
             "`MediStack_relation_expansion_priority_plan.md`.\n")

    L.append("---\n")
    L.append("## 재현 / 무변경 보증\n")
    L.append("```\npython3 scripts/match_popular_drugs_coverage.py            # CSV + 본 문서\n"
             "python3 scripts/match_popular_drugs_coverage.py --no-write # 콘솔만\n```\n")
    L.append("본 분석은 seed CSV · full index · relation_card 스냅샷 · alias · export 를 **읽기만** 한다. "
             "published / clinical_reviewed = false 유지. relation/full index/alias/export/src 무변경.\n")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"[write] {os.path.relpath(OUT_MD, REPO)}")
    return covered, name_only, missing, ambig, no_cands


def main():
    write = "--no-write" not in sys.argv
    seeds, full, aliases, exp, snap = load()
    ents, rc, no, by_norm, ing_alias, prod_alias, ing2rel = build_index(full, aliases, exp)
    if not check_baseline(ents, rc, no, exp, snap):
        print("\n[STOP] 기준 수치 불일치 — 데이터가 예상과 다름. 분석 중단.")
        return 1

    rows = [match_seed(s, ents, by_norm, ing_alias, prod_alias, ing2rel) for s in seeds]

    sc = Counter(r["matched_status"] for r in rows)
    print(f"\n=== seed {len(rows)}건 매칭 결과 ===")
    for k in ("relation_card_covered", "name_only_only", "missing_from_full_index", "ambiguous_manual_review"):
        print(f"  {k}: {sc[k]} ({pct(sc[k], len(rows))})")

    print("\n=== name_only_only (확장 후보 high/medium, name_only 매핑 내림차순) ===")
    cands = sorted([r for r in rows if r["matched_status"] == "name_only_only"
                    and r["next_action"] == "relation_expansion_candidate"],
                   key=lambda r: -r["matched_name_only_count"])
    for r in cands:
        print(f"  {r['query_name']:14s} name_only={r['matched_name_only_count']:4d}  "
              f"[{r['seed_category']}]  {r['match_method']}/{r['confidence']}")

    if write:
        write_csv(rows)
        write_md(rows)
    else:
        print("\n(--no-write: 산출물 미생성)")
    print("\nMATCH POPULAR DRUGS COVERAGE: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
