#!/usr/bin/env python3
"""
validate_bulk_alias_candidates.py
MediStack v0.5 bulk alias review queue 검증기.

review queue(JSON 정본 + CSV 보조)가 안전 게이트를 지키는지 검사한다.
승인(approved)으로 export 되는 후보가 정책을 우회하지 못하게 코드로 강제:
  - 후보는 라이브 relation 성분에만 귀속(에스오메프라졸/15행/excluded 차단).
  - 기존 alias(현재 66개)와 중복 금지, 큐 내부 중복 금지.
  - status/candidate_type enum, 필수 필드, batch_id 존재.
  - brand_core 는 approved 금지(별도 tier, PM v0.5 #6).
  - rejected/deferred 가 approved 처럼 export 금지.
  - source(method/checked_at)·reviewer 없으면 approved 금지(pending 까지만).
  - item_seq 없는 product_full_name 은 approved 금지.
  - JSON↔CSV 정합, alias JSON 무변경(alias_count 66·relation 30) 점검.

사용:
    python3 validate_bulk_alias_candidates.py [queue.json] [queue.csv] [aliases.json] [relations.json]
종료 코드: 0 = PASS, 1 = FAIL
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEF_JSON = os.path.join(REPO, "data", "candidates", "bulk_alias_review_queue_v0_5.json")
DEF_CSV = os.path.join(REPO, "data", "candidates", "bulk_alias_review_queue_v0_5.csv")
DEF_ALIAS = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
DEF_REL = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")

REQUIRED_FIELDS = [
    "candidate_alias", "candidate_type", "canonical_ingredient", "item_seq", "item_name",
    "ingr_name", "source_url", "source_method", "source_checked_at", "confidence",
    "risk_level", "reason", "status", "exclusion_reason", "reviewer", "batch_id",
]
STATUS_VALUES = {"pending", "approved", "rejected", "deferred"}
CANDIDATE_TYPES = {"ingredient", "product_full_name", "brand_core", "rejected"}
ALWAYS_NONEMPTY = {"candidate_alias", "candidate_type", "canonical_ingredient", "status", "batch_id"}
# (v0.5 Phase 2) source_method 화이트리스트
ALLOWED_SOURCE_METHODS = {"manual.nedrug", "nedrug.searchDrug", "nedrug.getItemDetail",
                          "internal.phase1", "phase1.seed"}

EXCLUDED_BYPASS_INGREDIENT = "에스오메프라졸"
FORBIDDEN_ITEMSEQS = {"201600209"}  # 에스오메프라졸 대표 itemSeq
NUMERIC_RE = re.compile(r"^\d+$")
ITEMSEQ_RE = re.compile(r"itemSeq=(\d+)")


class V:
    def __init__(self):
        self.fails, self.passes = [], []
    def check(self, ok, no, title, detail=""):
        (self.passes if ok else self.fails).append((no, title) if ok else (no, title, detail))
        return ok


def norm(s):
    return (s or "").strip().lower()


def load_json(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"[FATAL] {label} 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"[FATAL] {label} JSON 파싱 실패: {e}"


def build_allowed(rdata):
    rels = rdata.get("relations") or []
    excl = rdata.get("excluded_v0_1") or []
    live = {r.get("ingredient") for r in rels if r.get("ingredient")}
    excl_ings = {e.get("ingredient") for e in excl if e.get("ingredient")}
    excluded_only = excl_ings - live
    allowed = (live - {EXCLUDED_BYPASS_INGREDIENT}) - excluded_only
    return live, excluded_only, allowed


def main(json_path, csv_path, alias_path, rel_path):
    v = V()
    qdata, err = load_json(json_path, "queue JSON")
    if err:
        print(err); return 1
    rdata, err = load_json(rel_path, "relations")
    if err:
        print(err); return 1
    adata, err = load_json(alias_path, "aliases")
    if err:
        print(err); return 1

    live, excluded_only, allowed = build_allowed(rdata)

    # 1) JSON 구조: meta + candidates(list)
    cands = qdata.get("candidates") if isinstance(qdata, dict) else None
    ok_struct = isinstance(qdata, dict) and isinstance(qdata.get("meta"), dict) and isinstance(cands, list)
    v.check(ok_struct, 1, "queue JSON 구조(meta 객체 + candidates 리스트)",
            f"type={type(qdata).__name__}")
    if not ok_struct:
        _report(v, json_path); return 1
    cands = [c for c in cands if isinstance(c, dict)]

    # 2) CSV parse + 헤더 필드 완비 + 행수 == JSON
    csv_rows, csv_err = [], ""
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            csv_header = reader.fieldnames or []
            csv_rows = list(reader)
    except Exception as e:
        csv_err = str(e); csv_header = []
    miss_cols = [c for c in REQUIRED_FIELDS if c not in csv_header]
    v.check(not csv_err and not miss_cols and len(csv_rows) == len(cands), 2,
            "CSV parse·필드 완비·행수 일치",
            f"err={csv_err} missing_cols={miss_cols} csv={len(csv_rows)} json={len(cands)}")

    # 3) 필수 필드 존재 + 항상 비면 안 되는 필드
    miss = []
    for i, c in enumerate(cands):
        for fld in REQUIRED_FIELDS:
            if fld not in c:
                miss.append(f"row{i}:{fld}없음")
        for fld in ALWAYS_NONEMPTY:
            if not str(c.get(fld, "")).strip():
                miss.append(f"row{i}:{fld}빈값")
    v.check(not miss, 3, "필수 필드 존재 + 핵심 필드 비어있지 않음", f"viol={miss[:8]}")

    # 4) status enum
    bad_status = [f"{c.get('candidate_alias')!r}:{c.get('status')!r}" for c in cands
                  if c.get("status") not in STATUS_VALUES]
    v.check(not bad_status, 4, "status ∈ {pending,approved,rejected,deferred}", f"viol={bad_status}")

    # 5) candidate_type enum
    bad_type = [f"{c.get('candidate_alias')!r}:{c.get('candidate_type')!r}" for c in cands
                if c.get("candidate_type") not in CANDIDATE_TYPES]
    v.check(not bad_type, 5, "candidate_type ∈ {ingredient,product_full_name,brand_core,rejected}", f"viol={bad_type}")

    # 6) 큐 내부 candidate_alias 중복 금지(정규화)
    seen, dup = {}, []
    for c in cands:
        k = norm(c.get("candidate_alias"))
        if not k:
            continue
        seen[k] = seen.get(k, 0) + 1
    dup = sorted([k for k, n in seen.items() if n > 1])
    v.check(not dup, 6, "큐 내부 candidate_alias 중복 금지", f"dup={dup}")

    # 7) 기존 alias 66개와 중복 금지
    existing = {norm(a.get("alias")) for a in
                (adata.get("ingredient_aliases") or []) + (adata.get("product_aliases") or [])
                if a.get("alias")}
    coll = sorted({norm(c.get("candidate_alias")) for c in cands if norm(c.get("candidate_alias")) in existing})
    v.check(not coll, 7, "기존 alias(66)와 중복 금지", f"collide={coll}")

    # 8) canonical_ingredient ∈ 허용 canonical(라이브−에스오메프라졸−excluded전용)
    bad_ci = [f"{c.get('candidate_alias')!r}->{c.get('canonical_ingredient')!r}" for c in cands
              if c.get("canonical_ingredient") not in allowed]
    v.check(not bad_ci, 8, "canonical_ingredient ∈ 허용 canonical(신규 relation 금지)", f"viol={bad_ci}")

    # 9) 에스오메프라졸/15행/excluded 차단(canonical·itemSeq·excluded-only)
    eso = []
    for c in cands:
        ci = c.get("canonical_ingredient")
        seq = (c.get("item_seq") or "").strip()
        if ci == EXCLUDED_BYPASS_INGREDIENT:
            eso.append(f"{c.get('candidate_alias')!r}:에스오메프라졸")
        elif ci in excluded_only:
            eso.append(f"{c.get('candidate_alias')!r}:excluded-only({ci})")
        if seq in FORBIDDEN_ITEMSEQS:
            eso.append(f"{c.get('candidate_alias')!r}:금지itemSeq{seq}")
    v.check(not eso, 9, "에스오메프라졸/15행/excluded 후보 차단", f"viol={eso}")

    # 10) brand_core 는 approved 금지
    bc_appr = [f"{c.get('candidate_alias')!r}" for c in cands
               if c.get("candidate_type") == "brand_core" and c.get("status") == "approved"]
    v.check(not bc_appr, 10, "brand_core approved 금지(별도 tier, PM v0.5 #6)", f"viol={bc_appr}")

    # 11) rejected/deferred 가 approved 처럼 export 금지(approved ⇒ type∈{ingredient,product_full_name})
    rd_appr = [f"{c.get('candidate_alias')!r}:{c.get('candidate_type')}" for c in cands
               if c.get("status") == "approved" and c.get("candidate_type") not in {"ingredient", "product_full_name"}]
    v.check(not rd_appr, 11, "approved 후보는 ingredient/product_full_name 만(rejected/brand_core approved 금지)", f"viol={rd_appr}")

    # 12) approved 완전성: source_method·source_checked_at·reviewer 없으면 approved 금지(pending 까지만)
    incomplete = []
    for c in cands:
        if c.get("status") != "approved":
            continue
        for fld in ("source_method", "source_checked_at", "reviewer"):
            if not str(c.get(fld, "")).strip():
                incomplete.append(f"{c.get('candidate_alias')!r}:{fld}빈값")
    v.check(not incomplete, 12, "approved 완전성(source_method·source_checked_at·reviewer 필수)", f"viol={incomplete}")

    # 13) item_seq 없는/비숫자 product_full_name 은 approved 금지
    pfn_bad = []
    for c in cands:
        if c.get("candidate_type") == "product_full_name" and c.get("status") == "approved":
            seq = (c.get("item_seq") or "").strip()
            if not NUMERIC_RE.match(seq):
                pfn_bad.append(f"{c.get('candidate_alias')!r}:item_seq={seq!r}")
    v.check(not pfn_bad, 13, "approved product_full_name 은 숫자형 item_seq 필수", f"viol={pfn_bad}")

    # 14) batch_id 존재(모든 행)
    no_batch = [f"{c.get('candidate_alias')!r}" for c in cands if not str(c.get("batch_id", "")).strip()]
    v.check(not no_batch, 14, "batch_id 존재(모든 후보)", f"viol={no_batch}")

    # 15) JSON↔CSV 정합((alias,status) 집합 일치)
    json_pairs = sorted((norm(c.get("candidate_alias")), c.get("status")) for c in cands)
    csv_pairs = sorted((norm(r.get("candidate_alias")), r.get("status")) for r in csv_rows)
    v.check(json_pairs == csv_pairs, 15, "JSON↔CSV (alias,status) 정합", f"json!=csv (json {len(json_pairs)} / csv {len(csv_pairs)})")

    # 16) alias JSON 무변경 점검(alias_count 66 + 실제 항목수 66 + relation 30)
    ac = adata.get("meta", {}).get("alias_count")
    n_alias = len(adata.get("ingredient_aliases") or []) + len(adata.get("product_aliases") or [])
    n_rel = len(rdata.get("relations") or [])
    v.check(ac == 66 and n_alias == 66 and n_rel == 30, 16,
            "alias JSON 무변경(alias_count 66·항목 66·relation 30)",
            f"alias_count={ac} 항목={n_alias} relation={n_rel}")

    # 17) source_method ∈ 허용 목록(provenance enum)
    bad_sm = sorted({f"{c.get('candidate_alias')!r}:{c.get('source_method')!r}" for c in cands
                     if c.get("source_method") not in ALLOWED_SOURCE_METHODS})
    v.check(not bad_sm, 17, "source_method ∈ {manual.nedrug,nedrug.searchDrug,nedrug.getItemDetail,internal.phase1,phase1.seed}", f"viol={bad_sm}")

    # 18) product_full_name(pending/approved)은 item_seq·source_method·source_checked_at 필수
    pfn_src = []
    for c in cands:
        if c.get("candidate_type") != "product_full_name" or c.get("status") not in {"pending", "approved"}:
            continue
        seq = (c.get("item_seq") or "").strip()
        for fld, ok in (("item_seq", bool(NUMERIC_RE.match(seq))),
                        ("source_method", bool(str(c.get("source_method", "")).strip())),
                        ("source_checked_at", bool(str(c.get("source_checked_at", "")).strip()))):
            if not ok:
                pfn_src.append(f"{c.get('candidate_alias')!r}:{fld}")
    v.check(not pfn_src, 18, "product_full_name(pending/approved)은 item_seq·source_method·source_checked_at 필수", f"viol={pfn_src}")

    return _report(v, json_path)


def _report(v, json_path):
    total = len(v.passes) + len(v.fails)
    overall = "PASS" if not v.fails else "FAIL"
    bar = "=" * 64
    print(bar); print(f"MediStack v0.5 bulk alias 후보 검증: {json_path}"); print(bar)
    if v.fails:
        print(f"\n[FAIL] {len(v.fails)}건")
        for no, title, detail in sorted(v.fails):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print("\n모든 검증 통과.")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)"); print(bar)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    jp = sys.argv[1] if len(sys.argv) > 1 else DEF_JSON
    cp = sys.argv[2] if len(sys.argv) > 2 else DEF_CSV
    ap = sys.argv[3] if len(sys.argv) > 3 else DEF_ALIAS
    rp = sys.argv[4] if len(sys.argv) > 4 else DEF_REL
    sys.exit(main(jp, cp, ap, rp))
