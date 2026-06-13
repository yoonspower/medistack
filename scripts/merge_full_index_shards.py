#!/usr/bin/env python3
"""
merge_full_index_shards.py
MediStack v1.1 Phase 6 — 병렬 shard 수집 결과 병합기.

collect_full_drug_name_index_sample.py 를 --shard I/K 로 K개 동시 실행하면
각 shard 가 [공통 seed(기존 N) + 자기 ingredient stride 의 신규 name_only] 를 별도 파일로 출력한다.
이 스크립트는 그 shard 들을 병합한다:
  - seed entries(기존 N) 는 **byte-identical 보존**(첫 N 항목을 그대로 prefix).
  - 신규 name_only 만 shard 들에서 모아 **item_seq 기준 dedup**(cross-shard 중복 제거) 후 append.
  - 목표 total(--target) 도달 시 cap(억지 충족 금지 — 공급 부족이면 도달치까지만).
신규 항목 스키마/필드는 shard 출력 그대로(수집기가 생성). 의학/제품 필드는 구조적으로 없음(name_only).

사용: python3 scripts/merge_full_index_shards.py --seed data/full_drug_name_index_sample_v1_0.json \
        --shards /tmp/ms_shard_0.json /tmp/ms_shard_1.json /tmp/ms_shard_2.json /tmp/ms_shard_3.json \
        --target 20000 --out data/full_drug_name_index_sample_v1_0.json
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_SEED = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default=DEFAULT_SEED, help="기존 total seed(byte-identical 보존 대상)")
    ap.add_argument("--shards", nargs="+", required=True, help="shard 출력 JSON 경로들")
    ap.add_argument("--target", type=int, default=20000)
    ap.add_argument("--out", default=DEFAULT_SEED, help="병합 출력 JSON(기본=seed 덮어쓰기)")
    args = ap.parse_args()

    seed = json.load(open(args.seed, encoding="utf-8"))
    seed_entries = seed["entries"]
    seed_seqs = {str(e.get("item_seq")) for e in seed_entries}
    rc = [e for e in seed_entries if e.get("display_mode") == "relation_card"]
    base_no = [e for e in seed_entries if e.get("display_mode") == "name_only"]
    print(f"[seed] total {len(seed_entries)} (relation_card {len(rc)} + name_only {len(base_no)})")

    cap_new = max(0, args.target - len(seed_entries))
    seen = set(seed_seqs)
    new_no = []
    cross_shard_dup = 0
    merged_stats = {"shards": [], "rows_seen": 0, "kept_per_shard": [], "ing_fail": 0,
                    "excl_export": 0, "excl_raw": 0, "excl_cancel": 0, "excl_eso": 0,
                    "excl_13": 0, "excl_dup": 0, "excl_pool": 0}
    for sp in args.shards:
        d = json.load(open(sp, encoding="utf-8"))
        st = (d.get("meta") or {}).get("collection_stats", {}) or {}
        shard_new = 0
        for e in d.get("entries", []):
            if e.get("display_mode") != "name_only":
                continue
            s = str(e.get("item_seq"))
            if s in seen:
                cross_shard_dup += 1
                continue
            seen.add(s)
            new_no.append(e)
            shard_new += 1
        merged_stats["shards"].append(os.path.basename(sp))
        merged_stats["kept_per_shard"].append(shard_new)
        for k in ("rows_seen", "ing_fail", "excl_export", "excl_raw", "excl_cancel",
                  "excl_eso", "excl_13", "excl_dup", "excl_pool"):
            merged_stats[k] += int(st.get(k, 0) or 0)
        print(f"[shard] {os.path.basename(sp)}: name_only {shard_new} 신규 (rows {st.get('rows_seen')}, ing_fail {st.get('ing_fail')})")

    merged_stats["cross_shard_dup_dropped"] = cross_shard_dup
    kept_new = new_no[:cap_new]
    merged_stats["new_name_only_total"] = len(new_no)
    merged_stats["new_name_only_kept"] = len(kept_new)
    merged_stats["capped_at_target"] = len(new_no) > cap_new

    entries = seed_entries + kept_new  # seed 그대로 prefix → byte-identical 보존
    no = base_no + kept_new

    # 다양성/편중 지표(판정용)
    ing_counter = Counter((e.get("ingredient_name") or "").strip() for e in no)
    comp_counter = Counter((e.get("company_name") or "").strip() for e in no if e.get("company_name"))
    total = len(entries)
    merged_stats["diversity"] = {
        "unique_ingredients": len(ing_counter),
        "max_single_ingredient": ing_counter.most_common(1)[0][1] if ing_counter else 0,
        "max_single_ingredient_pct": round(100 * (ing_counter.most_common(1)[0][1] / max(1, len(no))), 3) if ing_counter else 0,
        "unique_companies": len(comp_counter),
    }
    merged_stats["method"] = "parallel shard collect (collect_full_drug_name_index_sample.py --shard I/K) + merge"

    meta = dict(seed.get("meta") or {})
    meta["target_total"] = args.target
    meta["counts"] = {"total": total, "relation_card": len(rc), "name_only": len(no)}
    meta["collection_stats"] = merged_stats
    doc = {"meta": meta, "entries": entries}

    out_json = args.out
    out_csv = out_json[:-5] + ".csv" if out_json.endswith(".json") else out_json + ".csv"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    csv_fields = ["item_seq", "item_name", "normalized_item_name", "ingredient_name",
                  "company_name", "covered_by_relation", "display_mode",
                  "no_relation_notice_required", "source", "source_method", "source_checked_at"]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        w.writeheader()
        for e in entries:
            w.writerow(e)

    print(f"[out] {out_json}  total={total} (relation_card {len(rc)} + name_only {len(no)}) / target {args.target}")
    print("[merged_stats] " + json.dumps(merged_stats, ensure_ascii=False))
    if total < args.target:
        print(f"NOTE: total {total} < target {args.target} — 공급 천장(억지 충족 금지). report 에 사유 필수.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
