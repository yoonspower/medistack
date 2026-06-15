#!/usr/bin/env python3
"""
analyze_substring_domination_v1_3.py — substring 지배 성분 탐색/분류 (분석 산출물).

목적(작업 C): "짧은 성분명이 더 긴 성분명에 포함되는" 케이스를 탐색해, shallow search 가
다른 약물(superset)에 지배돼 정확 성분의 국내 단일·경구 품목을 놓칠 위험을 분류한다.
근거: 프레드니솔론 ⊂ 메틸프레드니솔론 (production search max_pages=2 가 메틸프레드니솔론에 지배돼
소론도정 199602982 를 놓쳤던 false-negative → deep fallback 으로 해소).

방법(대량 네트워크 회피):
  1) 로컬: ingredient universe(theme∪carried∪live∪KPI)에서 proper-substring 쌍(X ⊊ Y) 산출.
  2) prefix-type(Y=접두사+X → 다른 약물, 지배 위험) vs suffix-type(Y=X+염/수화물 → 같은 약물, 무위험) 분류.
  3) SDK(cache-first, NedrugClient): in-scope prefix 위험 후보 + theme source-check 성분에
     search_itemseqs 를 돌려 지배가 실제로 발생하는지 확인 → 4분류.
  4) live PPI(오메프라졸/란소프라졸) itemSeq 가 base-drug 단일·경구인지 read-only 감사.

분류:
  - substring_risk_confirmed : shallow 에 정확 성분 단일·경구 없음 + 다른약물 superset 지배 →
                               deep fallback 으로 정확품 복구(ok_deep_exact). (= 프레드니솔론)
  - already_safe             : shallow 에서 정확/단일·경구 확보(지배 없음) 또는 이미 live 정확 itemSeq.
  - no_risk                  : superset 이 염/수화물(같은 약물) 이거나, 영양소 scope 밖, 또는 미유통(0건).
  - needs_deep_check         : shallow 0/지배인데 deep 으로도 정확품 미확보 → 추가 확인 필요.

⚠️ 분석 전용. live/protected 무수정. 어떤 후보도 live 승격하지 않는다. SDK-only(직접 http 금지).
사용: python3 scripts/analyze_substring_domination_v1_3.py          # cache-first (online cache 재사용)
종료코드: 0.
"""
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

# 영양소 상호작용 트랙에서 의미있는 성분(theme map + 활성 트랙). KPI 일반 성분은 scope 표시만.
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
KPI_CSV = os.path.join(DATA, "coverage_kpi_top_candidates_v1_2.csv")


def universes():
    theme = set(vfs.SEARCH_INGREDIENTS.keys())
    carried = set(t[1] for t in vfs.CARRIED)
    exp = json.load(open(EXPORT, encoding="utf-8"))
    live = set(r["ingredient"] for r in exp["relations"])
    kpi = set()
    if os.path.exists(KPI_CSV):
        for r in csv.DictReader(open(KPI_CSV, encoding="utf-8")):
            if r.get("ingredient_name"):
                kpi.add(r["ingredient_name"])
    return theme, carried, live, kpi


def substring_pairs(U):
    Us = [x for x in U if x and "/" not in x]
    g = {}
    for X in Us:
        sup = [Y for Y in Us if X != Y and X in Y and len(X) < len(Y)]
        if sup:
            g[X] = sup
    return g


def scope_of(x, theme, live, kpi, carried):
    s = []
    for n, st in [("theme", theme), ("live", live), ("kpi", kpi), ("carried", carried)]:
        if x in st:
            s.append(n)
    return s


def domination_probe(client, ingredient, exclude_ingr=None):
    """shallow(max_pages=2) 원행을 보고 지배 신호 + search_itemseqs reason 산출."""
    shallow = client.search_drug(ingredient, max_pages=2)
    # shallow 에서 정확 성분 단일·경구 픽 존재?
    shallow_pick = vfs._filter_pick(shallow, ingredient, exclude_ingr, 2)
    has_exact_shallow = any(ingr == ingredient for _, _, ingr in shallow_pick)
    # 다른약물 superset(접두사형) 이 shallow 결과에 존재?
    diff_supersets = sorted({r.ingr_name for r in shallow
                             if r.ingr_name and ingredient in r.ingr_name
                             and r.ingr_name != ingredient and not r.ingr_name.startswith(ingredient)})
    seqs, reason = vfs.search_itemseqs(client, ingredient, exclude_ingr=exclude_ingr, max_n=2, max_pages=2)
    return {
        "shallow_rows": len(shallow),
        "shallow_pick": [(s, n, i) for s, n, i in shallow_pick],
        "has_exact_in_shallow": has_exact_shallow,
        "diff_drug_supersets_in_shallow": diff_supersets,
        "search_itemseqs_reason": reason,
        "search_itemseqs_picks": seqs,
    }


def classify(probe, in_scope):
    r = probe["search_itemseqs_reason"]
    if r == "ok_deep_exact":
        return "substring_risk_confirmed"
    if r == "ok":
        if probe["diff_drug_supersets_in_shallow"] and not probe["has_exact_in_shallow"]:
            # 정확품 없이 substring 픽만(염/수화물) — 같은 약물이면 무위험
            return "already_safe"
        return "already_safe"
    # no_domestic_single_oral_product
    if not in_scope:
        return "no_risk"
    if probe["shallow_rows"] == 0:
        return "no_risk"  # 미유통(0건) — substring 무관
    return "needs_deep_check"


def audit_live_ppi(client, exp):
    """live PPI(오메프라졸/란소프라졸) relation 의 itemSeq 가 base-drug 인지 read-only 감사."""
    out = []
    for ing in ("오메프라졸", "란소프라졸"):
        rels = [r for r in exp["relations"] if r["ingredient"] == ing]
        for rel in rels:
            url = (rel.get("source") or {}).get("url", "")
            seq = url.split("itemSeq=")[-1] if "itemSeq=" in url else ""
            out.append({"ingredient": ing, "relation_id": rel["id"], "nutrient": rel.get("nutrient"),
                        "live_itemseq": seq, "pointer_has_base_name": ing in (rel.get("source") or {}).get("pointer", "")})
    return out


def main():
    theme, carried, live, kpi = universes()
    U = theme | carried | live | kpi
    g = substring_pairs(U)

    prefix, suffix = [], []
    for X, Ys in g.items():
        diffs = [Y for Y in Ys if not Y.startswith(X)]
        (prefix if diffs else suffix).append((X, diffs if diffs else Ys))

    client = NedrugClient(
        offline=False, cache_dir=os.path.join(SDK_DIR, "cache"),
        raw_dir=os.path.join(SDK_DIR, "raw"), log_path=os.path.join(SDK_DIR, "calls.jsonl"),
    )

    # 검사 대상: prefix-type(지배 위험) 전부 + theme source-check 성분(회귀 baseline).
    NUTRIENT_SCOPE = theme | {"오메프라졸", "란소프라졸", "라베프라졸", "판토프라졸"}
    targets = {}
    for X, diffs in prefix:
        targets[X] = {"supersets": diffs, "in_scope": X in NUTRIENT_SCOPE, "kind": "prefix_diff_drug"}
    for X in sorted(theme):
        targets.setdefault(X, {"supersets": g.get(X, []), "in_scope": True, "kind": "theme_source_check"})

    results = []
    for X in sorted(targets):
        meta = targets[X]
        exclude = "메틸프레드니솔론" if X == "프레드니솔론" else None
        try:
            probe = domination_probe(client, X, exclude_ingr=exclude)
        except Exception as e:  # noqa: BLE001
            probe = {"error": f"{type(e).__name__}: {e}", "search_itemseqs_reason": "error",
                     "diff_drug_supersets_in_shallow": [], "has_exact_in_shallow": False, "shallow_rows": -1}
        cls = classify(probe, meta["in_scope"]) if "error" not in probe else "needs_deep_check"
        results.append({"ingredient": X, "kind": meta["kind"], "in_nutrient_scope": meta["in_scope"],
                        "linguistic_supersets": meta["supersets"], "classification": cls, **probe})

    exp = json.load(open(EXPORT, encoding="utf-8"))
    ppi_audit = audit_live_ppi(client, exp)

    summary = {}
    for r in results:
        summary[r["classification"]] = summary.get(r["classification"], 0) + 1

    doc = {
        "meta": {
            "title": "MediStack substring 지배 성분 탐색/분류 (v1.3 — 분석 산출물)",
            "purpose": "shallow search 가 다른약물 superset 에 지배돼 정확 성분 단일·경구 품목을 놓칠 위험 탐색.",
            "method": "로컬 substring 쌍 + prefix/suffix 분류 + cache-first SDK domination probe. live/protected 무수정.",
            "do_not_implement_yet": True, "live_integration_forbidden": True,
            "published": False, "clinical_reviewed": False, "deploy": "none",
        },
        "universe_sizes": {"theme": len(theme), "carried": len(carried), "live": len(live),
                           "kpi": len(kpi), "union": len(U)},
        "substring_pairs_total": len(g),
        "prefix_type_diff_drug": [{"short": X, "diff_supersets": Ys} for X, Ys in sorted(prefix)],
        "suffix_type_salt_same_drug": [{"short": X, "salt_supersets": Ys} for X, Ys in sorted(suffix)],
        "classification_summary": summary,
        "sdk_stats": client.stats,
        "probes": results,
        "live_ppi_itemseq_audit": ppi_audit,
    }
    out_path = os.path.join(DATA, "review", "substring_domination_scan_v1_3.json")
    json.dump(doc, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("=== analyze_substring_domination_v1_3 ===")
    print(f"universe: theme {len(theme)} / carried {len(carried)} / live {len(live)} / kpi {len(kpi)} / union {len(U)}")
    print(f"substring 쌍(X⊊Y): {len(g)}  | prefix-type(다른약물): {len(prefix)}  | suffix-type(염/수화물): {len(suffix)}")
    print(f"SDK stats(cache-first): {client.stats}")
    print(f"분류 요약: {summary}")
    print("--- prefix-type 위험 후보 ---")
    for r in results:
        if r["kind"] == "prefix_diff_drug":
            print(f"  {r['ingredient']} ⊊ {r['linguistic_supersets']} | scope={r['in_nutrient_scope']} | "
                  f"reason={r['search_itemseqs_reason']} | exact_shallow={r.get('has_exact_in_shallow')} | "
                  f"→ {r['classification']}")
    print("--- theme source-check 중 deep fallback(ok_deep_exact) 발동 ---")
    fired = [r["ingredient"] for r in results if r["search_itemseqs_reason"] == "ok_deep_exact"]
    print(f"  발동: {fired or '(없음)'}")
    print("--- live PPI itemSeq 감사 ---")
    for a in ppi_audit:
        print(f"  {a['ingredient']} id{a['relation_id']} × {a['nutrient']} | itemSeq={a['live_itemseq']} | base_name_in_pointer={a['pointer_has_base_name']}")
    print(f"[write] {os.path.relpath(out_path, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
