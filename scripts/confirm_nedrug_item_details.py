#!/usr/bin/env python3
"""
confirm_nedrug_item_details.py
MediStack v0.5 bulk alias pipeline — Phase 3 상세확정(nedrug getItemDetail, dry-run).

목적(설계: docs/MediStack_v0.5_bulk_alias_pipeline_plan.md / phase2_report):
  - Phase 2 가 수집한 **pending product_full_name** 후보를 nedrug getItemDetail 원문으로 확인해
    품목명·단일 주성분 일치를 확정하고, **다음 batch 반영 직전의 approved-ready 목록**을 만든다.
  - alias JSON 미수정 · approved status 미생성(approved 0 유지). approved-ready 는 **별도 파일**로만 표현.
  - 상세 확인 성공 후보는 queue 안에서 **status=pending 유지**(detail_confirmed=true 표시)하고,
    approved-ready 파일에 approved_ready=true 로 따로 적는다.

안전 게이트(코드 강제):
  - 대상은 status=pending 且 candidate_type=product_full_name 且 item_seq 보유 후보만. 그 외 미변경.
  - getItemDetail 원문에서 품목명(title) + distinct 주성분(ingrName) 추출.
  - 확정 조건: 품목명 base 일치 + 주성분 distinct 1개(단일성분) + canonical ⊆ 그 주성분.
  - 복합제(주성분 ≥2)·성분 불일치 → status=deferred 강등(이유 기록). approved-ready 금지.
  - 품목명 불일치/네트워크/파싱 실패 → status=pending 유지(이유 기록). approved-ready 금지.
  - 에스오메프라졸/넥시움/itemSeq 201600209 → approved-ready 금지(대상도 아님; 방어적 차단).
  - 기존 deferred/rejected/brand_core 후보는 미변경(보존).

사용:
  python3 scripts/confirm_nedrug_item_details.py --no-network        # 구조 검증(상세 미호출)
  python3 scripts/confirm_nedrug_item_details.py                     # dry-run 상세확정
종료 코드: 0 정상(0건 포함), 2 입력 오류.
"""
import argparse
import csv
import http.cookiejar
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
RELATIONS_PATH = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
OUT_DIR = os.path.join(REPO, "data", "candidates")
DEF_QUEUE_JSON = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.json")
DEF_QUEUE_CSV = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.csv")
DEF_AR_JSON = os.path.join(OUT_DIR, "bulk_alias_approved_ready_v0_5.json")
DEF_AR_CSV = os.path.join(OUT_DIR, "bulk_alias_approved_ready_v0_5.csv")

DEFAULT_CHECKED_AT = "2026-06-11"
DETAIL_SOURCE_METHOD = "nedrug.getItemDetail"
EXCLUDED_BYPASS_INGREDIENT = "에스오메프라졸"
FORBIDDEN_ITEMSEQS = {"201600209"}
ESO_HINT_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium)", re.IGNORECASE)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15"

BASE_FIELDS = [
    "candidate_alias", "candidate_type", "canonical_ingredient", "item_seq", "item_name",
    "ingr_name", "source_url", "source_method", "source_checked_at", "confidence",
    "risk_level", "reason", "status", "exclusion_reason", "reviewer", "batch_id",
]
DETAIL_FIELDS = ["detail_confirmed", "detail_source_method", "detail_checked_at",
                 "detail_item_seq", "detail_item_name", "detail_ingr_name", "detail_match_result"]
QUEUE_CSV_FIELDS = [
    "canonical_ingredient", "candidate_alias", "status", "reason", "risk_level",
    "candidate_type", "item_seq", "item_name", "ingr_name", "source_url",
    "source_method", "source_checked_at", "confidence", "exclusion_reason", "reviewer", "batch_id",
] + DETAIL_FIELDS
AR_FIELDS = [
    "candidate_alias", "canonical_ingredient", "item_seq", "item_name", "ingr_name",
    "source_url", "source_method", "source_checked_at", "detail_source_method", "detail_checked_at",
    "confidence", "risk_level", "batch_id", "approved_ready", "reason", "reviewer_required",
]
STATUS_VALUES = ["pending", "approved", "rejected", "deferred"]

TITLE_RE = re.compile(r"<title>[^<]*상세보기-(.+?)</title>", re.S)
CTRL_WS_RE = re.compile(r"[\n\r\t]")
INGR_RE = re.compile(r'"ingrName":"((?:\\u[0-9a-fA-F]{4}|[^"\\])*)"')


def norm_name(s):
    return re.sub(r"\s+", "", s or "")


def base_name(s):
    return re.sub(r"\(.*$", "", norm_name(s))


def load(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FATAL] {label} 로드 실패: {path}: {e}")
        sys.exit(2)


def allowed_canonical():
    rdata = load(RELATIONS_PATH, "relations")
    rels = rdata.get("relations") or []
    excl = rdata.get("excluded_v0_1") or []
    live = {r.get("ingredient") for r in rels if r.get("ingredient")}
    excl_ings = {e.get("ingredient") for e in excl if e.get("ingredient")}
    return (live - {EXCLUDED_BYPASS_INGREDIENT}) - (excl_ings - live)


def existing_alias_itemseqs():
    """기존 alias(product_aliases + verified_item_seqs)가 이미 대표하는 itemSeq 집합.
    같은 itemSeq(동일 제품)는 approved-ready 에서 제외(중복 제품 padding 방지)."""
    a = load(ALIAS_PATH, "alias")
    seqs = set()
    for p in (a.get("product_aliases") or []):
        if (p.get("item_seq") or "").strip():
            seqs.add(p["item_seq"].strip())
    for lst in (a.get("verified_item_seqs") or {}).values():
        for e in (lst or []):
            if (e.get("item_seq") or "").strip():
                seqs.add(e["item_seq"].strip())
    return seqs


# ---------- 네트워크(분리) ----------
def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def get_item_detail(opener, item_seq, timeout=25):
    url = f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={item_seq}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    with opener.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace"), url


def parse_detail(html_text):
    mt = TITLE_RE.search(html_text)
    title = mt.group(1).strip() if mt else ""
    ings = []
    for cap in INGR_RE.findall(html_text):
        try:
            v = json.loads('"' + cap + '"')
        except Exception:
            v = cap
        if v and v.strip():
            ings.append(v.strip())
    return title, sorted(set(ings))


def confirm_one(opener, c, checked_at):
    """pending 후보 1건 상세확정. c 를 in-place 갱신, detail_match_result 반환."""
    seq = (c.get("item_seq") or "").strip()
    canonical = c.get("canonical_ingredient", "")
    try:
        html_text, _ = get_item_detail(opener, seq)
    except Exception as e:
        c["detail_match_result"] = f"fetch_failed({type(e).__name__})"
        c["reason"] = c.get("reason", "") + " | 상세확정 실패(fetch) → pending 유지"
        return "fetch_failed"
    title, distinct = parse_detail(html_text)
    c["detail_item_seq"] = seq
    c["detail_item_name"] = " ".join(title.split())  # 저장은 공백 정규화
    c["detail_ingr_name"] = " / ".join(distinct)
    c["detail_checked_at"] = checked_at
    c["detail_source_method"] = DETAIL_SOURCE_METHOD
    if not title or not distinct:
        c["detail_match_result"] = "parse_failed"
        c["reason"] = c.get("reason", "") + " | 상세 파싱 실패 → pending 유지"
        return "parse_failed"
    # 표면형에 개행/탭 등 제어공백 → 검색 alias 부적합. approved-ready 제외(Phase 2 정제 필요), pending 유지.
    if CTRL_WS_RE.search(c.get("candidate_alias", "")) or CTRL_WS_RE.search(title):
        c["detail_match_result"] = "surface_form_whitespace"
        c["reason"] = c.get("reason", "") + " | 표면형 개행/제어공백 — Phase 2 정제 필요, approved-ready 제외(pending 유지)"
        return "surface_form_whitespace"
    # 방어적: 에스오메프라졸/넥시움 신호
    if ESO_HINT_RE.search(title) or any(ESO_HINT_RE.search(x) for x in distinct) or seq in FORBIDDEN_ITEMSEQS:
        c["status"] = "deferred"
        c["detail_match_result"] = "esomeprazole_block"
        c["exclusion_reason"] = "에스오메프라졸/넥시움/15행 관련 — approved-ready 금지"
        return "esomeprazole_block"
    if len(distinct) >= 2:
        c["status"] = "deferred"
        c["detail_match_result"] = "combo_detected"
        c["confidence"] = "low"
        c["exclusion_reason"] = f"getItemDetail 상세 복합제(주성분 {len(distinct)}종: {' / '.join(distinct)}) — 단일성분 아님"
        c["reason"] = c.get("reason", "") + " | 상세확정 결과 복합제 → deferred 강등"
        return "combo_detected"
    single = distinct[0]
    if not canonical or canonical not in single:
        c["status"] = "deferred"
        c["detail_match_result"] = "ingredient_mismatch"
        c["exclusion_reason"] = f"상세 주성분 '{single}' 에 canonical '{canonical}' 불포함"
        c["reason"] = c.get("reason", "") + " | 상세 주성분 불일치 → deferred 강등"
        return "ingredient_mismatch"
    if base_name(title) != base_name(c.get("candidate_alias", "")):
        c["detail_match_result"] = "name_mismatch"
        c["reason"] = c.get("reason", "") + f" | 상세 품목명 base 불일치(detail={title!r}) → pending 유지"
        return "name_mismatch"
    # 확정
    c["detail_confirmed"] = "true"
    c["detail_match_result"] = "confirmed"
    c["source_method"] = DETAIL_SOURCE_METHOD
    c["source_checked_at"] = checked_at
    c["confidence"] = "high"
    c["reason"] = (f"nedrug searchDrug 발견 → getItemDetail 상세확정: 품목명 '{title}' · 단일 주성분 '{single}'"
                   f"(canonical {canonical} 포함). 사람 검토 후 batch 반영 대상")
    return "confirmed"


def ensure_fields(c):
    for f in BASE_FIELDS + DETAIL_FIELDS:
        c.setdefault(f, "")
    return c


def build_approved_ready(cands, checked_at, existing_seqs):
    out = []
    for c in cands:
        if c.get("detail_confirmed") != "true":
            continue
        # 기존 alias 가 동일 itemSeq(동일 제품) 보유 → 중복 제품, approved-ready 제외(queue 는 pending 유지).
        if (c.get("item_seq") or "").strip() in existing_seqs:
            c["detail_match_result"] = "confirmed_redundant_itemseq"
            c["reason"] = c.get("reason", "") + " | 기존 alias가 동일 itemSeq(동일 제품) 보유 → approved-ready 제외(중복)"
            continue
        out.append({
            "candidate_alias": c["candidate_alias"], "canonical_ingredient": c["canonical_ingredient"],
            "item_seq": c["item_seq"], "item_name": c.get("detail_item_name") or c.get("item_name"),
            "ingr_name": c.get("detail_ingr_name") or c.get("ingr_name"),
            "source_url": c["source_url"], "source_method": c.get("source_method", DETAIL_SOURCE_METHOD),
            "source_checked_at": c.get("source_checked_at", checked_at),
            "detail_source_method": c.get("detail_source_method", DETAIL_SOURCE_METHOD),
            "detail_checked_at": c.get("detail_checked_at", checked_at),
            "confidence": "high", "risk_level": c.get("risk_level", "low"), "batch_id": c.get("batch_id", ""),
            "approved_ready": "true",
            "reason": "getItemDetail 상세확정(품목명·단일주성분 일치). 사람 검토 후 다음 batch 반영 대상",
            "reviewer_required": "true",
        })
    out.sort(key=lambda r: (r["canonical_ingredient"], r["candidate_alias"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-json", default=DEF_QUEUE_JSON)
    ap.add_argument("--input-csv", default=DEF_QUEUE_CSV)
    ap.add_argument("--out-json", default=DEF_QUEUE_JSON)
    ap.add_argument("--out-csv", default=DEF_QUEUE_CSV)
    ap.add_argument("--approved-ready-json", default=DEF_AR_JSON)
    ap.add_argument("--approved-ready-csv", default=DEF_AR_CSV)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--checked-at", default=DEFAULT_CHECKED_AT)
    args = ap.parse_args()

    qdata = load(args.input_json, "queue")
    cands = [ensure_fields(dict(c)) for c in qdata.get("candidates", [])]

    targets = [c for c in cands if c.get("status") == "pending"
               and c.get("candidate_type") == "product_full_name" and (c.get("item_seq") or "").strip()]
    if args.limit:
        targets = targets[:args.limit]

    results = {k: 0 for k in
               ("confirmed", "combo_detected", "ingredient_mismatch", "name_mismatch",
                "surface_form_whitespace", "fetch_failed", "parse_failed", "esomeprazole_block")}
    if args.no_network:
        print(f"[--no-network] 상세 호출 생략 — 구조/필드 정규화만. 대상 pending {len(targets)}건 미처리.")
    else:
        opener = make_opener()
        for c in targets:
            r = confirm_one(opener, c, args.checked_at)
            results[r] = results.get(r, 0) + 1
            print(f"  [{r}] {c['candidate_alias']} (seq {c['item_seq']})")

    approved_ready = build_approved_ready(cands, args.checked_at, existing_alias_itemseqs())
    counts = {s: 0 for s in STATUS_VALUES}
    for c in cands:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    # queue meta 갱신(기존 meta 보존 + phase3 추가)
    meta = dict(qdata.get("meta", {}))
    meta["phases"] = sorted(set((meta.get("phases") or []) + [3]))
    meta["counts"] = {"total": len(cands), **counts}
    meta["phase3_confirmation"] = {
        "checked_at": args.checked_at, "targets_pending": len(targets),
        "results": results, "approved_ready": len(approved_ready),
        "no_network": args.no_network,
        "detail_source_method": DETAIL_SOURCE_METHOD,
    }
    meta["note"] = ("Phase 3 상세확정. pending product_full_name 을 getItemDetail 원문으로 확인 — 품목명·단일주성분 일치 시 "
                    "detail_confirmed=true(status=pending 유지, source_method=nedrug.getItemDetail, confidence=high). "
                    "복합제·성분불일치는 deferred 강등, 품목명불일치/실패는 pending 유지. approved 0·alias JSON 미수정. "
                    "approved-ready 는 별도 파일(approved_ready=true), 실제 반영은 다음 PM 게이트. 칼륨 행 구매/제품링크 금지 불변.")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "candidates": cands}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=QUEUE_CSV_FIELDS)
        w.writeheader()
        for c in cands:
            w.writerow({k: c.get(k, "") for k in QUEUE_CSV_FIELDS})

    ar_meta = {
        "schema": "bulk_alias_approved_ready", "version": "v0.5", "phase": 3,
        "generated_at": args.checked_at, "generator": "scripts/confirm_nedrug_item_details.py",
        "alias_source": "data/medistack_v0.3_aliases.json",
        "queue_source": "data/candidates/bulk_alias_review_queue_v0_5.json",
        "count": len(approved_ready),
        "note": ("getItemDetail 상세확정 통과 후보(품목명·단일주성분 일치). approved_ready=true 이나 status 는 queue 에서 pending 유지. "
                 "실제 approved 전환·alias JSON 반영은 다음 PM 게이트(reviewer_required=true). brand_core/복합제/에스오메프라졸 제외."),
    }
    with open(args.approved_ready_json, "w", encoding="utf-8") as f:
        json.dump({"meta": ar_meta, "approved_ready": approved_ready}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.approved_ready_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=AR_FIELDS)
        w.writeheader()
        for r in approved_ready:
            w.writerow({k: r.get(k, "") for k in AR_FIELDS})

    print("=" * 64)
    print("MediStack v0.5 Phase 3 getItemDetail 상세확정(dry-run)")
    print("=" * 64)
    print(f"대상 pending: {len(targets)} | 결과: {results}")
    print(f"queue counts: {meta['counts']}  (approved={counts['approved']})")
    print(f"approved-ready: {len(approved_ready)}")
    print(f"queue JSON: {os.path.relpath(args.out_json, REPO)}")
    print(f"approved-ready JSON: {os.path.relpath(args.approved_ready_json, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
