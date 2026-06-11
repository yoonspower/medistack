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
DEF_AR = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_v0_5.json")  # (Phase 3) 있으면 검증
DEF_AR2 = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_batch2_v0_5.json")  # (Phase 5) 있으면 검증
DEF_AR3 = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_batch3_v0_5.json")  # (Phase 7) 있으면 검증
DEF_AR4 = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_batch4_v0_5.json")  # (Phase 9) 있으면 검증
DEF_AR5 = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_batch5_v0_5.json")  # (Phase 11) 있으면 검증

DETAIL_FIELDS = ["detail_confirmed", "detail_source_method", "detail_checked_at",
                 "detail_item_seq", "detail_item_name", "detail_ingr_name", "detail_match_result"]
AR_REQUIRED = ["candidate_alias", "canonical_ingredient", "item_seq", "item_name", "ingr_name",
               "source_url", "source_method", "source_checked_at", "detail_source_method",
               "detail_checked_at", "confidence", "risk_level", "batch_id", "approved_ready",
               "reason", "reviewer_required"]
EXCLUDED_BYPASS_INGREDIENT_NAME = "에스오메프라졸"
FORBIDDEN_ITEMSEQS = {"201600209"}

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


def main(json_path, csv_path, alias_path, rel_path, ar_path=DEF_AR, ar2_path=DEF_AR2, ar3_path=DEF_AR3, ar4_path=DEF_AR4, ar5_path=DEF_AR5):
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
    # incorporated(status=approved) 후보는 이미 alias 로 graduate → 기존 alias 와 '같아야' 정상이므로 제외
    coll = sorted({norm(c.get("candidate_alias")) for c in cands
                   if c.get("status") != "approved" and norm(c.get("candidate_alias")) in existing})
    v.check(not coll, 7, "기존 alias와 중복 금지(incorporated/approved 제외)", f"collide={coll}")

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
    # (Phase 4) batch 반영으로 alias_count 는 증가 가능 → 하드코딩 대신 내부 정합 + relation 30 + 단조(≥66) 검사.
    ac = adata.get("meta", {}).get("alias_count")
    n_alias = len(adata.get("ingredient_aliases") or []) + len(adata.get("product_aliases") or [])
    n_rel = len(rdata.get("relations") or [])
    v.check(isinstance(ac, int) and ac == n_alias and n_rel == 30 and ac >= 66, 16,
            "alias 정합(alias_count==항목수·relation 30·≥66 단조)",
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

    # 19) detail_confirmed=true 후보 무결성: detail 필드 완비 + itemSeq 일치 + 단일주성분 + canonical 포함
    dc_bad = []
    for c in cands:
        if str(c.get("detail_confirmed", "")).strip().lower() != "true":
            continue
        for fld in DETAIL_FIELDS:
            if not str(c.get(fld, "")).strip():
                dc_bad.append(f"{c.get('candidate_alias')!r}:{fld}빈값")
        if (c.get("detail_item_seq") or "").strip() != (c.get("item_seq") or "").strip():
            dc_bad.append(f"{c.get('candidate_alias')!r}:detail_item_seq≠item_seq")
        din = c.get("detail_ingr_name") or ""
        if "/" in din:
            dc_bad.append(f"{c.get('candidate_alias')!r}:detail_ingr 복합제")
        if c.get("canonical_ingredient", "") not in din:
            dc_bad.append(f"{c.get('candidate_alias')!r}:canonical∉detail_ingr")
    v.check(not dc_bad, 19, "detail_confirmed=true 무결성(detail 필드·itemSeq 일치·단일주성분·canonical 포함)", f"viol={dc_bad[:8]}")

    # 화이트리스트(canonical→itemSeq) + 전체 alias itemSeq (incorporated 검증·#30~#32 용)
    wl_by_canon = {}
    for ing, lst in (adata.get("verified_item_seqs") or {}).items():
        wl_by_canon[ing] = {(e.get("item_seq") or "").strip() for e in (lst or []) if (e.get("item_seq") or "").strip()}
    alias_seqs = {(p.get("item_seq") or "").strip() for p in (adata.get("product_aliases") or [])
                  if (p.get("item_seq") or "").strip()}
    for s in wl_by_canon.values():
        alias_seqs |= s

    # 30) queue approved 후보는 alias JSON 에 실제 반영(alias∈aliases · itemSeq∈whitelist[canonical])
    inc_bad = []
    for c in cands:
        if c.get("status") != "approved":
            continue
        if norm(c.get("candidate_alias")) not in existing:
            inc_bad.append(f"{c.get('candidate_alias')!r}:alias미반영")
        if (c.get("item_seq") or "").strip() not in wl_by_canon.get(c.get("canonical_ingredient"), set()):
            inc_bad.append(f"{c.get('candidate_alias')!r}:itemSeq미화이트리스트")
    v.check(not inc_bad, 30, "queue approved 후보는 alias JSON 반영됨(alias∈aliases·itemSeq∈whitelist)", f"viol={inc_bad[:8]}")

    # --- approved-ready batch1 검증(있을 때, 번호 20~32) ---
    if ar_path and os.path.exists(ar_path):
        _validate_approved_ready(v, ar_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                                 base_no=20, tag="")

    # --- approved-ready batch2 검증(있을 때, Phase 5, 번호 40~52): 미반영(incorporated=false) 전제 + ≤30 ---
    if ar2_path and os.path.exists(ar2_path):
        _validate_approved_ready(v, ar2_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                                 base_no=40, tag="batch2")
        ar2_data, _e2 = load_json(ar2_path, "approved-ready batch2")
        ar2 = (ar2_data or {}).get("approved_ready") if isinstance(ar2_data, dict) else None
        if isinstance(ar2, list):
            v.check(len(ar2) <= 30, 53, "batch2 approved-ready ≤ 30건", f"count={len(ar2)}")
            # (Phase 6 옵션 A) 반영 전=false / 반영 후=true 둘 다 정합. incorporated=true 의 실제 반영 검증은 #52.
            bad_inc = [e.get("candidate_alias") for e in ar2 if str(e.get("incorporated", "")).strip().lower() not in ("false", "true")]
            v.check(not bad_inc, 54, "batch2 approved-ready incorporated ∈ {false(미반영),true(반영)} 정합(true는 #52에서 실제 반영 검증)", f"viol={bad_inc}")
            no_inc = [e.get("candidate_alias") for e in ar2 if "incorporated" not in e]
            v.check(not no_inc, 55, "batch2 approved-ready 는 incorporated 필드 보유", f"viol={no_inc}")

    # --- approved-ready batch3 검증(있을 때, Phase 7, 번호 60~72): 미반영(incorporated=false) 전제 + ≤30 ---
    if ar3_path and os.path.exists(ar3_path):
        _validate_approved_ready(v, ar3_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                                 base_no=60, tag="batch3")
        ar3_data, _e3 = load_json(ar3_path, "approved-ready batch3")
        ar3 = (ar3_data or {}).get("approved_ready") if isinstance(ar3_data, dict) else None
        if isinstance(ar3, list):
            v.check(len(ar3) <= 30, 73, "batch3 approved-ready ≤ 30건", f"count={len(ar3)}")
            # (Phase 8 옵션 A) 반영 전=false / 반영 후=true 둘 다 정합. incorporated=true 의 실제 반영 검증은 base+12(#72).
            bad_inc3 = [e.get("candidate_alias") for e in ar3 if str(e.get("incorporated", "")).strip().lower() not in ("false", "true")]
            v.check(not bad_inc3, 74, "batch3 approved-ready incorporated ∈ {false(미반영),true(반영)} 정합(true는 #72에서 실제 반영 검증)", f"viol={bad_inc3}")
            no_inc3 = [e.get("candidate_alias") for e in ar3 if "incorporated" not in e]
            v.check(not no_inc3, 75, "batch3 approved-ready 는 incorporated 필드 보유", f"viol={no_inc3}")

    # --- approved-ready batch4 검증(있을 때, Phase 9, 번호 80~92): 미반영(incorporated=false) 전제 + ≤30 ---
    if ar4_path and os.path.exists(ar4_path):
        _validate_approved_ready(v, ar4_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                                 base_no=80, tag="batch4")
        ar4_data, _e4 = load_json(ar4_path, "approved-ready batch4")
        ar4 = (ar4_data or {}).get("approved_ready") if isinstance(ar4_data, dict) else None
        if isinstance(ar4, list):
            v.check(len(ar4) <= 30, 93, "batch4 approved-ready ≤ 30건", f"count={len(ar4)}")
            # (Phase 10 옵션 A) 반영 전=false / 반영 후=true 둘 다 정합. incorporated=true 의 실제 반영 검증은 base+12(#92).
            bad_inc4 = [e.get("candidate_alias") for e in ar4 if str(e.get("incorporated", "")).strip().lower() not in ("false", "true")]
            v.check(not bad_inc4, 94, "batch4 approved-ready incorporated ∈ {false(미반영),true(반영)} 정합(true는 #92에서 실제 반영 검증)", f"viol={bad_inc4}")
            no_inc4 = [e.get("candidate_alias") for e in ar4 if "incorporated" not in e]
            v.check(not no_inc4, 95, "batch4 approved-ready 는 incorporated 필드 보유", f"viol={no_inc4}")

    # --- approved-ready batch5 검증(있을 때, Phase 11, 번호 100~112): 미반영(incorporated=false) 전제 + ≤30 ---
    if ar5_path and os.path.exists(ar5_path):
        _validate_approved_ready(v, ar5_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                                 base_no=100, tag="batch5")
        ar5_data, _e5 = load_json(ar5_path, "approved-ready batch5")
        ar5 = (ar5_data or {}).get("approved_ready") if isinstance(ar5_data, dict) else None
        if isinstance(ar5, list):
            v.check(len(ar5) <= 30, 113, "batch5 approved-ready ≤ 30건", f"count={len(ar5)}")
            # (Phase 12 옵션 A) 반영 전=false / 반영 후=true 둘 다 정합. incorporated=true 의 실제 반영 검증은 base+12(#112).
            bad_inc5 = [e.get("candidate_alias") for e in ar5 if str(e.get("incorporated", "")).strip().lower() not in ("false", "true")]
            v.check(not bad_inc5, 114, "batch5 approved-ready incorporated ∈ {false(미반영),true(반영)} 정합(true는 #112에서 실제 반영 검증)", f"viol={bad_inc5}")
            no_inc5 = [e.get("candidate_alias") for e in ar5 if "incorporated" not in e]
            v.check(not no_inc5, 115, "batch5 approved-ready 는 incorporated 필드 보유", f"viol={no_inc5}")

    return _report(v, json_path)


def _validate_approved_ready(v, ar_path, cands, existing, allowed, excluded_only, alias_seqs, wl_by_canon,
                             base_no=20, tag=""):
    """approved-ready 파일 1개 검증. base_no=시작 번호(batch1=20·batch2=40), tag=표시 라벨."""
    T = f" [{tag}]" if tag else ""
    ar_data, err = load_json(ar_path, "approved-ready" + T)
    if err:
        v.check(False, base_no, "approved-ready 로드" + T, err); return
    ar = ar_data.get("approved_ready") if isinstance(ar_data, dict) else None
    if not isinstance(ar, list):
        v.check(False, base_no, "approved-ready 구조(approved_ready 리스트)" + T, f"type={type(ar).__name__}"); return
    v.check(True, base_no, "approved-ready 구조(approved_ready 리스트)" + T)
    qby = {norm(c.get("candidate_alias")): c for c in cands}

    miss = [f"row{i}:{f}" for i, e in enumerate(ar) for f in AR_REQUIRED
            if not str(e.get(f, "")).strip()]
    v.check(not miss, base_no + 1, "approved-ready 필수 16필드 비어있지 않음" + T, f"viol={miss[:8]}")

    not_in_q, bad = [], []
    for e in ar:
        k = norm(e.get("candidate_alias"))
        c = qby.get(k)
        if not c:
            not_in_q.append(e.get("candidate_alias")); continue
        # incorporated 후보는 status=approved 로 graduate → pending/approved 둘 다 허용
        if c.get("status") not in ("pending", "approved") or c.get("candidate_type") != "product_full_name":
            bad.append(f"{e.get('candidate_alias')!r}:queue status/type({c.get('status')}/{c.get('candidate_type')})")
        if str(c.get("detail_confirmed", "")).strip().lower() != "true":
            bad.append(f"{e.get('candidate_alias')!r}:detail_confirmed≠true")
    v.check(not not_in_q, base_no + 2, "approved-ready 후보는 queue 에 존재" + T, f"missing={not_in_q}")
    v.check(not bad, base_no + 3, "approved-ready 의 queue 후보는 pending/approved·product_full_name·detail_confirmed" + T, f"viol={bad[:8]}")

    coll = sorted({e.get("candidate_alias") for e in ar
                   if str(e.get("incorporated", "")).strip().lower() != "true" and norm(e.get("candidate_alias")) in existing})
    v.check(not coll, base_no + 4, "approved-ready 기존 alias 중복 금지(incorporated 제외)" + T, f"collide={coll}")

    ci_bad = [f"{e.get('candidate_alias')!r}->{e.get('canonical_ingredient')!r}" for e in ar
              if e.get("canonical_ingredient") not in allowed]
    v.check(not ci_bad, base_no + 5, "approved-ready canonical ∈ 허용" + T, f"viol={ci_bad}")

    eso, combo, seqbad = [], [], []
    for e in ar:
        ci, seq, ingr = e.get("canonical_ingredient"), (e.get("item_seq") or "").strip(), e.get("ingr_name") or ""
        if ci == EXCLUDED_BYPASS_INGREDIENT_NAME or ci in excluded_only or seq in FORBIDDEN_ITEMSEQS \
                or "에스오메프라졸" in ingr or "넥시움" in str(e.get("candidate_alias", "")):
            eso.append(e.get("candidate_alias"))
        if "/" in ingr:
            combo.append(e.get("candidate_alias"))
        c = qby.get(norm(e.get("candidate_alias")))
        if not NUMERIC_RE.match(seq) or (c and seq != (c.get("item_seq") or "").strip()) \
                or (c and seq != (c.get("detail_item_seq") or "").strip()):
            seqbad.append(f"{e.get('candidate_alias')!r}:item_seq")
    v.check(not eso, base_no + 6, "approved-ready 에스오메프라졸/15행 금지" + T, f"viol={eso}")
    v.check(not combo, base_no + 7, "approved-ready 복합제 금지(ingr_name '/')" + T, f"viol={combo}")
    v.check(not seqbad, base_no + 8, "approved-ready item_seq 숫자형·queue/detail itemSeq 일치" + T, f"viol={seqbad}")

    ar_flag = [e.get("candidate_alias") for e in ar if str(e.get("approved_ready", "")).strip().lower() != "true"]
    v.check(not ar_flag, base_no + 9, "approved-ready 는 approved_ready=true" + T, f"viol={ar_flag}")

    # +11) approved-ready item_seq ∉ 기존 alias itemSeq(미반영 후보만 — incorporated 는 반영됐으므로 제외)
    seq_dup = sorted({f"{e.get('candidate_alias')!r}:{(e.get('item_seq') or '').strip()}" for e in ar
                      if str(e.get("incorporated", "")).strip().lower() != "true"
                      and (e.get("item_seq") or "").strip() in alias_seqs})
    v.check(not seq_dup, base_no + 11, "approved-ready item_seq ∉ 기존 alias itemSeq(incorporated 제외)" + T, f"viol={seq_dup}")

    # +12) incorporated=true approved-ready 후보는 alias JSON 에 실제 반영(alias∈aliases·itemSeq∈whitelist[canonical])
    inc_bad = []
    for e in ar:
        if str(e.get("incorporated", "")).strip().lower() != "true":
            continue
        if norm(e.get("candidate_alias")) not in existing:
            inc_bad.append(f"{e.get('candidate_alias')!r}:alias미반영")
        if (e.get("item_seq") or "").strip() not in wl_by_canon.get(e.get("canonical_ingredient"), set()):
            inc_bad.append(f"{e.get('candidate_alias')!r}:itemSeq미화이트리스트")
    v.check(not inc_bad, base_no + 12, "approved-ready incorporated 후보는 alias JSON 반영됨(alias∈aliases·itemSeq∈whitelist)" + T, f"viol={inc_bad[:8]}")


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
    arp = sys.argv[5] if len(sys.argv) > 5 else DEF_AR
    arp2 = sys.argv[6] if len(sys.argv) > 6 else DEF_AR2
    arp3 = sys.argv[7] if len(sys.argv) > 7 else DEF_AR3
    arp4 = sys.argv[8] if len(sys.argv) > 8 else DEF_AR4
    arp5 = sys.argv[9] if len(sys.argv) > 9 else DEF_AR5
    sys.exit(main(jp, cp, ap, rp, arp, arp2, arp3, arp4, arp5))
