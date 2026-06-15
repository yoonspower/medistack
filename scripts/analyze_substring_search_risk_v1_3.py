#!/usr/bin/env python3
"""
analyze_substring_search_risk_v1_3.py — substring 지배 검색 위험 광역 탐색 (분석 산출물·round3 후속).

직전 라운드(`analyze_substring_domination_v1_3.py`)는 universe 를 theme∪carried∪live∪KPI(366)로
한정했다. 본 스크립트는 **full drug name index 의 distinct ingredient_name(전체)** 까지 universe 를
확대해, 짧은 성분명이 더 긴 성분명에 묻혀 `search_itemseqs` 가 놓칠 수 있는 케이스를 더 찾는다.

분류 원리(직전 라운드 하드닝과 동일):
  - A ⊊ B (A 가 B 의 proper substring, A≠B, len(A)≥3, 단일성분=A·B 모두 '/'·',' 없음)
  - idx = B.find(A):
    · idx==0          → B = A + 접미사(염/수화물/제형) = **같은 약물** → salt_or_formulation_trap
    · B[idx-1] 한글   → A 앞에 접두사가 붙은 **다른 약물의 연속 명칭**(메틸/에스/덱스…) → 지배 위험
    · 그 외(구분자)    → 복합제/구분자 뒤 동거성분 → no_action
  - 성분 A 단위 집계: prefix 위험 superset 유무 / salt superset / combo superset
  - 위험도:
    · high_risk_substring  : prefix 위험 + A 가 relation factory/harvester seed 범위(theme∪carried∪live∪KPI∪antacid)
    · medium_risk_substring: prefix 위험 + seed 밖(실 단일성분이나 영양소 트랙 관련성 약함)
    · salt_or_formulation_trap: prefix 위험 없음 + salt 접미사 superset 만(같은 약물·무위험)
    · no_action            : 그 외(combo-only/사소)
  - 프레드니솔론·오메프라졸·란소프라졸 = 직전 처리 완료(baseline) 플래그.

deep-check(`--deep`): high/medium 중 **seed 관련** 후보만 cache-first SDK 로 search_itemseqs 실행.
  결과 라벨: exact_ingredient_found / shallow_miss_confirmed / shallow_already_safe /
            no_domestic_product / ambiguous.

⚠️ 분석 전용. live/protected 무수정·SDK-only(직접 http 금지)·live 승격 0.
사용:
  python3 scripts/analyze_substring_search_risk_v1_3.py            # 분류만(네트워크 0)
  python3 scripts/analyze_substring_search_risk_v1_3.py --deep     # + high/medium seed 후보 SDK deep-check
종료코드: 0.
"""
import argparse
import csv
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
QUEUE = os.path.join(DATA, "harvest_queue")
SDK_DIR = os.path.join(QUEUE, "_sdk")

sys.path.insert(0, REPO)
from medistack_sdk import NedrugClient  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


vfs = _load("vfs", "verify_factory_sources_v1_2.py")

FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
KPI_CSV = os.path.join(DATA, "coverage_kpi_top_candidates_v1_2.csv")

BASELINE_HANDLED = {"프레드니솔론", "오메프라졸", "란소프라졸"}  # 직전 라운드 처리/확인 완료

# 형태/제형 기술 접두사 — 성분명 앞에 붙어도 **같은 활성성분**(다른 약물 아님). 검색 지배 위험 양성이나
# deep fallback 이 정확 base 를 무해 복구하고 relation(활성성분 단위)에는 영향 없음.
FORMULATION_PREFIXES = ("무수", "미분화", "미세화", "미세", "주사용", "제피", "장용", "서방", "속방",
                        "건조", "동결건조", "침강", "결정", "무정형", "정제", "분말", "구형")
# 다른 활성성분을 만드는 접두사(이성질체/유도체) — 진짜 지배 위험(메틸/에스/덱스/레보/데스/레미/수/알 등).


def _is_hangul(ch):
    return "가" <= ch <= "힣"


def _prefix_kind(superset, short):
    """superset 의 short 앞 접두사가 형태기술(같은 약물)인지 다른-활성(이성질체/유도체)인지."""
    idx = superset.find(short)
    pre = superset[:idx]
    return "formulation" if pre.startswith(FORMULATION_PREFIXES) else "diff_active"


def load_universe():
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    index_ings = sorted({e.get("ingredient_name", "") for e in idx["entries"] if e.get("ingredient_name")})
    al = json.load(open(ALIASES, encoding="utf-8"))
    alias_ings = set()
    for a in al.get("ingredient_aliases", []):
        if not isinstance(a, dict):
            continue
        canon = a.get("canonical_ingredient", "")
        alias = a.get("alias", "")
        if canon:
            alias_ings.add(canon)
        # 한글 alias 만(영문 음역은 한글 substring 분석과 무관)
        if alias and any("가" <= ch <= "힣" for ch in alias):
            alias_ings.add(alias)
    exp = json.load(open(EXPORT, encoding="utf-8"))
    live = set(r["ingredient"] for r in exp["relations"])
    theme = set(vfs.SEARCH_INGREDIENTS.keys())
    carried = set(t[1] for t in vfs.CARRIED)
    kpi = set()
    if os.path.exists(KPI_CSV):
        for r in csv.DictReader(open(KPI_CSV, encoding="utf-8")):
            if r.get("ingredient_name"):
                kpi.add(r["ingredient_name"])
    antacid_stems = {"레보플록사신", "펙소페나딘", "이트라코나졸"}
    seed = theme | carried | live | kpi | antacid_stems
    return index_ings, alias_ings, live, theme, carried, kpi, seed


def single(name):
    return name and "/" not in name and "," not in name and len(name) >= 3


def analyze(scan_universe, seed):
    # universe = full index ingredients ∪ alias(한글) ∪ seed (단일성분만)
    ings = sorted({i for i in scan_universe if single(i)})
    iset = ings  # list for substring scan
    # 성분 A 별 superset 분류
    per = {}
    for A in ings:
        prefix_sup, salt_sup, combo_sup = [], [], []
        for B in iset:
            if B == A or A not in B or len(B) <= len(A):
                continue
            idx = B.find(A)
            if idx == 0:
                salt_sup.append(B)
            elif _is_hangul(B[idx - 1]):
                prefix_sup.append(B)
            else:
                combo_sup.append(B)
        if prefix_sup or salt_sup or combo_sup:
            per[A] = {"prefix": sorted(prefix_sup), "salt": sorted(salt_sup), "combo": sorted(combo_sup)}
    # 분류
    rows = []
    for A, sup in per.items():
        in_seed = A in seed
        diff_active = [B for B in sup["prefix"] if _prefix_kind(B, A) == "diff_active"]
        form_pref = [B for B in sup["prefix"] if _prefix_kind(B, A) == "formulation"]
        if diff_active:  # 다른 활성성분 접두사 = 진짜 지배 위험
            cls = "high_risk_substring" if in_seed else "medium_risk_substring"
        elif form_pref or sup["salt"]:  # 형태접두사·염/수화물 = 같은 약물 무위험
            cls = "salt_or_formulation_trap"
        else:
            cls = "no_action"
        rows.append({"ingredient": A, "in_seed": in_seed, "classification": cls,
                     "baseline_handled": A in BASELINE_HANDLED,
                     "diff_active_supersets": diff_active[:6], "diff_active_count": len(diff_active),
                     "formulation_supersets": form_pref[:4], "formulation_count": len(form_pref),
                     "salt_superset_count": len(sup["salt"]), "combo_superset_count": len(sup["combo"])})
    return rows


def deep_check(client, ingredient):
    """cache-first search_itemseqs + shallow 지배 신호 → 결과 라벨."""
    excl = "메틸프레드니솔론" if ingredient == "프레드니솔론" else None
    shallow = client.search_drug(ingredient, max_pages=2)
    if not shallow:
        return {"result": "no_domestic_product", "reason": "shallow 0건", "picks": [], "search_reason": "—"}
    shallow_pick = vfs._filter_pick(shallow, ingredient, excl, 2)
    has_exact_shallow = any(ingr == ingredient for _, _, ingr in shallow_pick)
    seqs, reason = vfs.search_itemseqs(client, ingredient, exclude_ingr=excl, max_n=2, max_pages=2)
    if reason == "ok_deep_exact":
        res = "shallow_miss_confirmed"  # 얕은검색 놓침 → deep 가 정확 base 복구
    elif reason == "ok" and has_exact_shallow:
        res = "shallow_already_safe"
    elif reason == "ok":
        res = "shallow_already_safe"  # substring 픽(염 등)이나 단일·경구 확보
    elif reason == "no_domestic_single_oral_product":
        res = "no_domestic_product" if not shallow_pick else "ambiguous"
    else:
        res = "ambiguous"
    return {"result": res, "search_reason": reason, "has_exact_shallow": has_exact_shallow,
            "picks": [(s, n, i) for s, n, i in seqs]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true", help="high/medium seed 후보 SDK deep-check(cache-first)")
    args = ap.parse_args()

    index_ings, alias_ings, live, theme, carried, kpi, seed = load_universe()
    scan_universe = set(index_ings) | alias_ings | seed
    rows = analyze(scan_universe, seed)

    summary = {}
    for r in rows:
        summary[r["classification"]] = summary.get(r["classification"], 0) + 1

    high = sorted([r for r in rows if r["classification"] == "high_risk_substring"],
                  key=lambda r: -r["diff_active_count"])
    medium = sorted([r for r in rows if r["classification"] == "medium_risk_substring"],
                    key=lambda r: -r["diff_active_count"])

    deep_results = {}
    sdk_stats = None
    if args.deep:
        client = NedrugClient(offline=False, cache_dir=os.path.join(SDK_DIR, "cache"),
                              raw_dir=os.path.join(SDK_DIR, "raw"), log_path=os.path.join(SDK_DIR, "calls.jsonl"))
        # seed 관련 high/medium 만(=relation factory/harvester seed 연관). baseline 제외(이미 확인).
        targets = sorted({r["ingredient"] for r in high} |
                         {r["ingredient"] for r in medium if r["in_seed"]})
        for ing in targets:
            try:
                deep_results[ing] = deep_check(client, ing)
            except Exception as e:  # noqa: BLE001
                deep_results[ing] = {"result": "ambiguous", "error": f"{type(e).__name__}: {e}"}
        sdk_stats = client.stats

    doc = {
        "meta": {
            "title": "MediStack substring 검색 위험 광역 탐색 (v1.3 round3 후속 — 분석 산출물)",
            "purpose": "full drug name index distinct ingredient(전체)까지 확대해 substring 지배 검색 누락 위험 추가 탐색.",
            "method": "full index ingredient universe pairwise substring + prefix/salt/combo 분류 + cache-first SDK deep-check. live/protected 무수정·SDK-only.",
            "do_not_implement_yet": True, "live_integration_forbidden": True,
            "published": False, "clinical_reviewed": False, "deploy": "none",
            "baseline_handled": sorted(BASELINE_HANDLED),
        },
        "universe": {"full_index_distinct_ingredients": len(index_ings),
                     "alias_ingredients": len(alias_ings), "seed_universe": len(seed),
                     "scan_universe_combined": len(scan_universe),
                     "single_ingredient_scanned": len([i for i in scan_universe if single(i)])},
        "classification_summary": summary,
        "high_risk_substring": high,
        "medium_risk_substring": medium,
        "deep_check": deep_results,
        "sdk_stats": sdk_stats,
    }
    out = os.path.join(DATA, "review", "substring_search_risk_v1_3.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("=== analyze_substring_search_risk_v1_3 ===")
    print(f"universe: full index {len(index_ings)} ∪ alias {len(alias_ings)} ∪ seed {len(seed)} = scan {len(scan_universe)} (단일성분 {len([i for i in scan_universe if single(i)])})")
    print(f"분류 요약: {summary}")
    print(f"--- high_risk_substring ({len(high)}) — diff-active 접두사(진짜 지배 위험) ---")
    for r in high:
        bl = " [baseline]" if r["baseline_handled"] else ""
        print(f"  {r['ingredient']} | diff_active {r['diff_active_count']}: {r['diff_active_supersets']}{bl}")
    print(f"--- medium_risk_substring ({len(medium)}) — diff-active 접두사·seed 밖 ---")
    for r in medium:
        print(f"  {r['ingredient']} | diff_active {r['diff_active_count']}: {r['diff_active_supersets']}")
    if args.deep:
        print(f"--- deep-check ({len(deep_results)}) | SDK {sdk_stats} ---")
        for ing, dr in sorted(deep_results.items()):
            print(f"  {ing}: {dr['result']} (reason={dr.get('search_reason','?')}) picks={[s for s,_,_ in dr.get('picks',[])]}")
    print(f"[write] {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
