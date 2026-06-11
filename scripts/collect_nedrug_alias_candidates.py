#!/usr/bin/env python3
"""
collect_nedrug_alias_candidates.py
MediStack v0.5 bulk alias pipeline — Phase 2 외부 수집기(nedrug searchDrug, dry-run).

목적(설계: docs/MediStack_v0.5_bulk_alias_pipeline_plan.md / phase1_report):
  - 라이브 relation 30 에 연결된 허용 canonical(에스오메프라졸 제외) 별로 식약처 nedrug
    searchDrug(주성분 검색) 결과에서 **완제·경구·정상** 품목명을 dry-run 수집해
    review queue 에 **status=pending product_full_name** 후보로 추가한다.
  - 이번 단계는 dry-run 수집만. **alias JSON 미수정 · approved 미생성.**
  - 기존 Phase 1 후보(brand_core deferred / rejected)는 보존(병합).

안전 게이트(코드 강제):
  - 허용 canonical = Phase 1 생성기와 동일(라이브 − 에스오메프라졸 − excluded 전용). 그 외 성분 미수집.
  - 보수적 성분 매칭: 행의 주성분에 canonical 이 포함될 때만 채택. 아니면 스킵(pending 금지).
  - 완제의약품 + 경구 고형(정/캡슐) + 취소/취하=정상 만 채택. 원료/점안/주사/외용/시럽/수출용 제외.
  - 에스오메프라졸/넥시움/15행 의심 후보는 rejected(또는 제외). itemSeq 201600209 차단.
  - 기존 alias 66 · 현재 queue alias · verified_item_seqs(4) 와 중복 제외.
  - 성분당 최대 N개(기본 5). itemSeq 오름차순 결정적 선택.
  - 상세(getItemDetail) 미실행 → confidence ≤ medium.
  - 수집 후보 source_method = "nedrug.searchDrug". 기존 Phase 1 후보 source_method 는 화이트리스트
    값("internal.phase1")으로 정규화(검증기 source_method enum 충족).

네트워크 실패/응답없음/파싱실패 → 전체 실패가 아니라 해당 성분을 skipped 로 기록(0건 허용).

사용:
  python3 scripts/collect_nedrug_alias_candidates.py --no-network        # 네트워크 없이 구조 검증(병합/정규화만)
  python3 scripts/collect_nedrug_alias_candidates.py --max-per-ingredient 5   # dry-run 수집
종료 코드: 0 정상(0건 포함), 2 입력 오류.
"""
import argparse
import csv
import html
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
RELATIONS_PATH = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
OUT_DIR = os.path.join(REPO, "data", "candidates")
DEF_QUEUE_JSON = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.json")
DEF_QUEUE_CSV = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.csv")

DEFAULT_CHECKED_AT = "2026-06-11"  # 실행일(환경 기준). --checked-at 로 override.
PHASE2_BATCH_ID = "v0.5-002"
PHASE5_BATCH_ID = "v0.5-005"  # Phase 5 재수집(max-per-ingredient 상향) 신규 후보 batch_id
EXCLUDED_BYPASS_INGREDIENT = "에스오메프라졸"
FORBIDDEN_ITEMSEQS = {"201600209"}
SOURCE_METHOD = "nedrug.searchDrug"
PHASE1_SOURCE_METHOD = "internal.phase1"  # Phase 1 후보 정규화 대상값
ALLOWED_SOURCE_METHODS = {"manual.nedrug", "nedrug.searchDrug", "nedrug.getItemDetail",
                          "internal.phase1", "phase1.seed"}

FIELDS = [
    "candidate_alias", "candidate_type", "canonical_ingredient", "item_seq", "item_name",
    "ingr_name", "source_url", "source_method", "source_checked_at", "confidence",
    "risk_level", "reason", "status", "exclusion_reason", "reviewer", "batch_id",
]
CSV_FIELDS = [
    "canonical_ingredient", "candidate_alias", "status", "reason", "risk_level",
    "candidate_type", "item_seq", "item_name", "ingr_name", "source_url",
    "source_method", "source_checked_at", "confidence", "exclusion_reason", "reviewer", "batch_id",
]
STATUS_VALUES = ["pending", "approved", "rejected", "deferred"]
CANDIDATE_TYPES = ["ingredient", "product_full_name", "brand_core", "rejected"]

ITEMSEQ_RE = re.compile(r"itemSeq=(\d+)")
ANCHOR_RE = re.compile(r'getItemDetail\?itemSeq=(\d+)"[^>]*>\s*([^<]+?)\s*</a>')
ORAL_RE = re.compile(r"(정|캡슐)")
NONORAL_RE = re.compile(r"(점안|점이|점비|주사|연고|크림|로션|겔|외용|흡입|패치|좌제|관장|시럽|현탁|가글|스프레이|에어로졸|틴크|패취)")
EXPORT_RE = re.compile(r"수출")
ESO_HINT_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium)", re.IGNORECASE)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15"


def norm(s):
    return (s or "").strip().lower()


def load(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FATAL] {label} 로드 실패: {path}: {e}")
        sys.exit(2)


def build_context():
    adata = load(ALIAS_PATH, "alias")
    rdata = load(RELATIONS_PATH, "relations")
    rels = rdata.get("relations") or []
    excl = rdata.get("excluded_v0_1") or []
    live = {r.get("ingredient") for r in rels if r.get("ingredient")}
    excl_ings = {e.get("ingredient") for e in excl if e.get("ingredient")}
    excluded_only = excl_ings - live
    allowed = sorted((live - {EXCLUDED_BYPASS_INGREDIENT}) - excluded_only)
    wl = adata.get("verified_item_seqs", {}) or {}
    wl_seqs, wl_names = set(), set()
    for lst in wl.values():
        for ent in (lst or []):
            if ent.get("item_seq"):
                wl_seqs.add(ent["item_seq"].strip())
            if ent.get("item_name"):
                wl_names.add(norm(ent["item_name"]))
    # 기존 product_aliases 가 대표하는 itemSeq 도 중복 기준에 포함(동일 제품 재수집 방지)
    for p in (adata.get("product_aliases") or []):
        if (p.get("item_seq") or "").strip():
            wl_seqs.add(p["item_seq"].strip())
    existing = {norm(a["alias"]) for a in
                (adata.get("ingredient_aliases") or []) + (adata.get("product_aliases") or []) if a.get("alias")}
    return {
        "adata": adata, "allowed": allowed, "excluded_only": excluded_only,
        "wl_seqs": wl_seqs, "wl_names": wl_names, "existing": existing,
        "alias_count": adata.get("meta", {}).get("alias_count"), "relation_count": len(rels),
    }


# ---------- 네트워크(분리) ----------
def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def nedrug_search(opener, ingredient, page=1, timeout=25):
    """searchDrug 주성분 검색(page). (html, url) 반환. 실패 시 예외."""
    enc = urllib.parse.quote(ingredient)
    url = f"https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1={enc}&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    with opener.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace"), url


def field(row, label):
    m = re.search(re.escape(f'<span class="s-th">{label}</span>') + r'(.*?)(?=<span class="s-th">|</td>|</tr>)', row, re.S)
    if not m:
        return ""
    txt = re.sub(r"<[^>]+>", " ", m.group(1))
    return " ".join(html.unescape(txt).split()).strip()


def parse_rows(html_text):
    """searchDrug HTML → [{item_seq, item_name, ingr_name, finished, status_cancel}]."""
    out = []
    for chunk in re.split(r"<tr[ >]", html_text):
        if "getItemDetail?itemSeq=" not in chunk:
            continue
        m = ANCHOR_RE.search(chunk)
        if not m:
            continue
        out.append({
            "item_seq": m.group(1),
            "item_name": html.unescape(m.group(2)).strip(),
            "ingr_name": field(chunk, "주성분"),
            "finished": field(chunk, "완제/원료구분"),
            "status_cancel": field(chunk, "취소/취하구분"),
        })
    return out


def make_row(**kw):
    row = {f: "" for f in FIELDS}
    row["reviewer"] = ""
    row.update(kw)
    return row


def collect_for_ingredient(opener, ing, ctx, seen_alias, max_n, checked_at, batch_id, max_pages=1):
    """한 성분 수집(최대 max_pages 페이지) → (rows, status). status ∈ {success, skipped:reason}.
    searchDrug 페이지당 15행(수출/원료/주사 노이즈 다수)이라, 적격 경구단일을 max_n 까지 모으려면 페이지 순회."""
    rows, picked, pages_ok = [], 0, 0
    for page in range(1, max_pages + 1):
        try:
            html_text, _ = nedrug_search(opener, ing, page=page)
        except Exception as e:
            if page == 1:
                return [], f"skipped:network({type(e).__name__})"
            break  # 이후 페이지 네트워크 실패 → 지금까지 수집분 유지하고 종료
        parsed = parse_rows(html_text)
        if not parsed:
            break  # 결과 끝(빈 페이지)
        pages_ok += 1
        for p in sorted(parsed, key=lambda x: int(x["item_seq"])):
            if picked >= max_n:
                break
            name, seq, ingr = p["item_name"], p["item_seq"], p["ingr_name"]
            nkey = norm(name)
            # 1) 봉인/금지 우선 차단
            if seq in FORBIDDEN_ITEMSEQS or ESO_HINT_RE.search(name) or (ingr and ESO_HINT_RE.search(ingr)):
                continue
            # 2) 중복 제외(기존 alias · 현재 queue · 이번 수집 · verified/product itemSeq)
            if nkey in ctx["existing"] or nkey in seen_alias or nkey in ctx["wl_names"] or seq in ctx["wl_seqs"]:
                continue
            # 3) 완제·정상·경구고형·비수출 필터
            if "원료" in p["finished"] or (p["finished"] and "완제" not in p["finished"]):
                continue
            if p["status_cancel"] and p["status_cancel"] != "정상":
                continue
            if EXPORT_RE.search(name) or NONORAL_RE.search(name) or not ORAL_RE.search(name):
                continue
            # 4) 보수적 성분 매칭: 행 주성분에 canonical 포함(없으면 채택 안 함)
            if not ingr or ing not in ingr:
                continue
            seen_alias.add(nkey)
            # 복합제(다성분 주성분, '/') 는 단일성분 아님 → pending 금지, deferred(사람 검토). 단일성분만 pending.
            is_combo = "/" in ingr
            if is_combo:
                status, conf, exr = "deferred", "low", "복합제(다성분 주성분) — 단일성분 아님, 사람 검토 필요"
                reason = (f"nedrug searchDrug(ingrName1={ing}) 결과 복합제 주성분 '{ingr}'(canonical {ing} 포함). "
                          f"단일성분 아님 → deferred, 사람 검토")
            else:
                status, conf, exr = "pending", "medium", ""
                reason = (f"nedrug searchDrug(ingrName1={ing}) 결과 단일 주성분 '{ingr}' 확인(완제·경구·정상). "
                          f"getItemDetail 상세 미실행 → 승인 전 원문 확인 필요")
            rows.append(make_row(
                candidate_alias=name, candidate_type="product_full_name", canonical_ingredient=ing,
                item_seq=seq, item_name=name, ingr_name=ingr,
                source_url=f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={seq}",
                source_method=SOURCE_METHOD, source_checked_at=checked_at,
                confidence=conf, risk_level="low", reason=reason,
                status=status, exclusion_reason=exr, batch_id=batch_id,
            ))
            picked += 1
        if picked >= max_n:
            break
    if pages_ok == 0:
        return [], "skipped:no-rows"
    return rows, "success"


def normalize_existing(cands):
    """Phase 1 등 기존 후보 source_method 를 화이트리스트 값으로 정규화(미수록 → internal.phase1).
    candidate 식별(alias/type/status/item_seq) 등 나머지는 보존."""
    out = []
    for c in cands:
        c = dict(c)
        for f in FIELDS:
            c.setdefault(f, "")
        if c.get("source_method") not in ALLOWED_SOURCE_METHODS:
            c["source_method"] = PHASE1_SOURCE_METHOD
        out.append(c)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-per-ingredient", type=int, default=5)
    ap.add_argument("--max-pages", type=int, default=1, help="성분당 searchDrug 페이지 순회 상한(페이지당 15행)")
    ap.add_argument("--limit-ingredients", type=int, default=None)
    ap.add_argument("--no-network", action="store_true", help="네트워크 호출 없이 병합/정규화만")
    ap.add_argument("--dry-run", action="store_true", default=True, help="dry-run(기본). alias JSON 미수정·approved 미생성")
    ap.add_argument("--checked-at", default=DEFAULT_CHECKED_AT)
    ap.add_argument("--batch-id", default=PHASE2_BATCH_ID, help="신규 수집 후보 batch_id (예: phase5 = v0.5-005)")
    ap.add_argument("--phase", type=int, default=2, help="수집 단계 번호(meta phaseN_collection 키)")
    ap.add_argument("--queue-in", default=DEF_QUEUE_JSON)
    ap.add_argument("--out-json", default=DEF_QUEUE_JSON)
    ap.add_argument("--out-csv", default=DEF_QUEUE_CSV)
    args = ap.parse_args()

    ctx = build_context()
    # (Phase 4+) batch 반영으로 alias_count 는 단조 증가(≥66). relation 은 항상 30. 그 외만 경고.
    if not (isinstance(ctx["alias_count"], int) and ctx["alias_count"] >= 66) or ctx["relation_count"] != 30:
        print(f"[WARN] 입력 불변식: alias_count={ctx['alias_count']}(≥66 기대) relation={ctx['relation_count']}(30 기대)")

    base = load(args.queue_in, "queue-in")
    existing_cands = normalize_existing(base.get("candidates", []))
    # 현재 queue 의 alias 도 중복 기준에 포함
    seen_alias = {norm(c["candidate_alias"]) for c in existing_cands if c.get("candidate_alias")}

    targets = ctx["allowed"][:args.limit_ingredients] if args.limit_ingredients else ctx["allowed"]
    success, skipped, new_rows = [], {}, []
    if args.no_network:
        print("[--no-network] 네트워크 호출 생략 — 병합/정규화/구조 검증만 수행.")
    else:
        opener = make_opener()
        for ing in targets:
            rows, st = collect_for_ingredient(opener, ing, ctx, seen_alias, args.max_per_ingredient, args.checked_at, args.batch_id, args.max_pages)
            new_rows.extend(rows)
            if st == "success":
                success.append((ing, len(rows)))
                print(f"  [수집] {ing}: {len(rows)}건")
            else:
                skipped[ing] = st
                print(f"  [스킵] {ing}: {st}")

    merged = existing_cands + new_rows
    merged.sort(key=lambda r: (r["canonical_ingredient"], r["candidate_type"], r["candidate_alias"]))

    counts = {s: 0 for s in STATUS_VALUES}
    for r in merged:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    # 기존 meta 보존(phase2_collection / phase3_confirmation / phase4_incorporation 등 이력 유지) + 이번 phase 정보만 갱신.
    meta = dict(base.get("meta", {}))
    meta["schema"] = "bulk_alias_review_queue"
    meta["version"] = "v0.5"
    meta["phases"] = sorted(set((meta.get("phases") or [1, 2]) + [args.phase]))
    meta["generators"] = sorted(set((meta.get("generators") or []) + [
        "scripts/generate_bulk_alias_candidates.py", "scripts/collect_nedrug_alias_candidates.py"]))
    meta["relation_source"] = "data/medistack_v0.2_beta_export.json"
    meta["alias_source"] = "data/medistack_v0.3_aliases.json"
    meta["alias_count_at_generation"] = ctx["alias_count"]
    meta["relation_count"] = ctx["relation_count"]
    meta["allowed_canonical"] = ctx["allowed"]
    meta["allowed_canonical_count"] = len(ctx["allowed"])
    meta["external_api_used"] = bool(meta.get("external_api_used")) or ((not args.no_network) and bool(success))
    meta["source_methods_allowed"] = sorted(ALLOWED_SOURCE_METHODS)
    meta["status_values"] = STATUS_VALUES
    meta["candidate_types"] = CANDIDATE_TYPES
    batches = dict(meta.get("batches") or {})
    batches.setdefault("v0.5-001", "phase1 internal(brand_core/rejected)")
    batches.setdefault("v0.5-002", "phase2 nedrug.searchDrug dry-run(product_full_name pending)")
    batches[args.batch_id] = (f"phase{args.phase} nedrug.searchDrug dry-run"
                              f"(max {args.max_per_ingredient}/성분, product_full_name pending)")
    meta["batches"] = batches
    meta["counts"] = {"total": len(merged), **counts}
    meta[f"phase{args.phase}_collection"] = {
        "checked_at": args.checked_at, "max_per_ingredient": args.max_per_ingredient,
        "max_pages": args.max_pages,
        "batch_id": args.batch_id, "alias_count_at_collection": ctx["alias_count"],
        "ingredients_targeted": len(targets),
        "ingredients_success": len(success), "ingredients_skipped": len(skipped),
        "new_candidates": len(new_rows),
        "success_detail": {i: n for i, n in success}, "skipped_detail": skipped,
        "no_network": args.no_network,
    }
    meta["note"] = (f"Phase {args.phase} dry-run 재수집(max {args.max_per_ingredient}/성분). nedrug searchDrug 만 사용"
                    "(상세 getItemDetail 미실행 → confidence≤medium). 신규 후보=status pending product_full_name"
                    "(완제·경구·정상·주성분 일치) 또는 복합제 deferred. approved 0건·alias JSON 미수정. "
                    "기존 후보/이력(phase1~4) 보존. 칼륨 행은 검색→안전카드 노출만, 구매/제품 추천 링크 금지(불변).")
    meta.setdefault("phase3_todo", [
        "pending product_full_name 후보 getItemDetail 원문 확인(주성분·품목명·성분코드) → confidence 상향",
        "사람 검토 → approved(reviewer·source 채움), brand_core tier 결정",
        "approved batch(30) → alias JSON 반영(별도 PM 게이트, validator 전종 재통과)",
        "data.go.kr OpenAPI 보강(선택)",
    ])

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "candidates": merged}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # CSV 는 기존 컬럼(detail/incorporated_at 등)을 잃지 않도록 동적 superset 으로 기록.
    csv_fields = list(CSV_FIELDS)
    for r in merged:
        for k in r:
            if k not in csv_fields:
                csv_fields.append(k)
    with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in merged:
            w.writerow({k: r.get(k, "") for k in csv_fields})

    print("=" * 64)
    print("MediStack v0.5 Phase 2 nedrug 수집(dry-run)")
    print("=" * 64)
    print(f"대상 canonical: {len(targets)} | 성공 {len(success)} | 스킵 {len(skipped)}")
    print(f"신규 수집 후보: {len(new_rows)} | 전체 queue: {len(merged)}")
    print(f"counts: {meta['counts']}")
    print(f"external_api_used: {meta['external_api_used']}  (approved 0 · alias JSON 미수정)")
    print(f"JSON: {os.path.relpath(args.out_json, REPO)}  CSV: {os.path.relpath(args.out_csv, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
