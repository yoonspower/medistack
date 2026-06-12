#!/usr/bin/env python3
"""
recollect_surface_candidates_v0_9.py
MediStack v0.9 — 표면형 보류 후보 재채록(getItemDetail) → approved-ready 분리.

v0.9 표면형 트랙에서 manual review 로 보류했던 queue pending 후보(candidate_alias 에 개행 포함)를
nedrug getItemDetail 원문으로 재채록한다. 재채록 결과 개행은 nedrug 공식 품목명의
'{브랜드}\\n(주성분)' 줄바꿈으로 확인됨(searchDrug 파싱 오류 아님) → 개행만 제거하면 라이브
동일성분 alias 의 지배적 표기 '{브랜드}(주성분)' 와 완전 동형(레보플록사신 85/89·독시사이클린 8/10
이미 동일형). 단일성분·canonical 일치·itemSeq 고유·중복 0 을 확인한 후보만 approved-ready 로 분리.

⚠️ 이 스크립트는 alias JSON·queue 를 절대 수정하지 않는다(incorporated=false·approved_ready=true·
   별도 AR 파일로만 표현). 실제 alias 반영은 다음 PM 승인 단계에서 별도 수행.

모드:
  (기본)        nedrug getItemDetail 재채록 → AR json/csv 생성 + 즉시 검증
  --validate    네트워크 없이 기존 AR 파일을 안전기준으로 재검증(suite/CI 용)

사용:
  python3 scripts/recollect_surface_candidates_v0_9.py
  python3 scripts/recollect_surface_candidates_v0_9.py --validate
종료 코드: 0 PASS, 1 FAIL
"""
import argparse
import csv
import json
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import confirm_nedrug_item_details as C            # noqa: E402
from validate_alias_surface_forms import surface_anomalies  # noqa: E402

AR_JSON = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_surface_v0_9.json")
AR_CSV = os.path.join(REPO, "data", "candidates", "bulk_alias_approved_ready_surface_v0_9.csv")
QUEUE = os.path.join(REPO, "data", "candidates", "bulk_alias_review_queue_v0_5.json")
BATCH_ID = "v0.9-surface-1"
CHECKED_AT = "2026-06-12"

CSV_COLS = ["candidate_alias", "canonical_ingredient", "item_seq", "item_name", "ingr_name",
            "source_url", "source_method", "source_checked_at", "detail_source_method",
            "detail_checked_at", "confidence", "risk_level", "batch_id", "approved_ready",
            "reason", "reviewer_required", "incorporated"]


def nfc(s):
    return unicodedata.normalize("NFC", s or "").strip().lower()


def clean_surface(s):
    """개행/CR/탭(제어 공백)만 제거. 다른 문자 보존 = 순수 표면형 정규화."""
    return "".join(ch for ch in (s or "") if ch not in "\r\n\t").strip()


def live_alias_surfaces(alias):
    out = set()
    for lst in (alias.get("ingredient_aliases") or []), (alias.get("product_aliases") or []):
        for e in lst:
            if isinstance(e, dict) and isinstance(e.get("alias"), str):
                out.add(nfc(e["alias"]))
    return out


def find_surface_pending(queue):
    """queue 에서 표면형 이상(개행 등)을 가진 pending 후보 [(idx, cand)] 추출."""
    res = []
    for i, c in enumerate(queue.get("candidates", [])):
        if c.get("status") == "pending" and surface_anomalies(c.get("candidate_alias", "")):
            res.append((i, c))
    return res


def judge(seq, canonical, cand_alias, title, distinct, existing_seqs, live_surfaces):
    """재채록 결과를 approved-ready 기준으로 판정 → (ok, cleaned, ingr, reason/err)."""
    if not title or not distinct:
        return False, "", "", "getItemDetail 파싱 실패(title/주성분 없음)"
    if C.ESO_HINT_RE.search(title) or any(C.ESO_HINT_RE.search(x) for x in distinct) or seq in C.FORBIDDEN_ITEMSEQS:
        return False, "", "", "에스오메프라졸/넥시움/15행 신호 — 차단"
    if len(distinct) >= 2:
        return False, "", "", f"복합제(주성분 {len(distinct)}종: {' / '.join(distinct)}) — 단일성분 아님"
    ingr = distinct[0]
    if not canonical or canonical not in ingr:
        return False, "", "", f"주성분 '{ingr}' 에 canonical '{canonical}' 불포함"
    cleaned = clean_surface(title)
    anomalies = surface_anomalies(cleaned)
    if anomalies:
        return False, "", "", f"개행 제거 후에도 표면형 이상 잔존: {anomalies}"
    if C.base_name(cleaned) != C.base_name(cand_alias):
        return False, "", "", f"품목명 base 불일치(cleaned={cleaned!r} vs cand={cand_alias!r})"
    if seq in existing_seqs:
        return False, "", "", f"itemSeq {seq} 이미 라이브 alias 보유(중복 제품)"
    if nfc(cleaned) in live_surfaces:
        return False, "", "", f"표면형 {cleaned!r} 이미 라이브 alias 중복"
    return True, cleaned, ingr, "getItemDetail 재채록: 개행만 제거→공식 '{브랜드}(주성분)' 동형·단일성분·canonical 포함. 사람 검토 후 다음 batch 반영 대상"


def make_entry(seq, canonical, cleaned, ingr, reason):
    return {
        "candidate_alias": cleaned,
        "canonical_ingredient": canonical,
        "item_seq": seq,
        "item_name": cleaned,
        "ingr_name": ingr,
        "source_url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={seq}",
        "source_method": "nedrug.getItemDetail",
        "source_checked_at": CHECKED_AT,
        "detail_source_method": "nedrug.getItemDetail",
        "detail_checked_at": CHECKED_AT,
        "confidence": "high",
        "risk_level": "low",
        "batch_id": BATCH_ID,
        "approved_ready": "true",
        "reason": reason,
        "reviewer_required": "true",
        "incorporated": "false",
    }


def run_recollect():
    queue = C.load(QUEUE, "queue")
    alias = C.load(C.ALIAS_PATH, "alias")
    existing_seqs = C.existing_alias_itemseqs()
    live_surfaces = live_alias_surfaces(alias)
    targets = find_surface_pending(queue)
    print(f"표면형 이상 pending 후보: {len(targets)}건 (재채록 대상)")
    opener = C.make_opener()
    approved, deferred = [], []
    for idx, c in targets:
        seq = (c.get("item_seq") or "").strip()
        canonical = c.get("canonical_ingredient", "")
        cand = c.get("candidate_alias", "")
        try:
            html, _ = C.get_item_detail(opener, seq)
            title, distinct = C.parse_detail(html)
        except Exception as e:
            deferred.append((idx, seq, f"fetch_failed({type(e).__name__})"))
            print(f"  [DEFER] idx{idx} seq{seq}: fetch 실패 {type(e).__name__}")
            continue
        ok, cleaned, ingr, reason = judge(seq, canonical, cand, title, distinct, existing_seqs, live_surfaces)
        if ok:
            approved.append(make_entry(seq, canonical, cleaned, ingr, reason))
            print(f"  [READY] idx{idx} seq{seq}: {cand!r} → {cleaned!r} ({ingr})")
        else:
            deferred.append((idx, seq, reason))
            print(f"  [DEFER] idx{idx} seq{seq}: {reason}")

    meta = {
        "schema": "bulk_alias_approved_ready_surface_v0_9",
        "version": "0.9",
        "track": "surface-form re-record (manual review → approved-ready)",
        "note": ("v0.9 표면형 보류 후보 getItemDetail 재채록. 개행은 nedrug 공식명 '{브랜드}\\n(주성분)' 줄바꿈 "
                 "→ 개행 제거 시 라이브 '{브랜드}(주성분)' 동형. alias JSON·queue 미수정·incorporated=false. "
                 "실제 반영은 PM 승인 별도 단계."),
        "batch_id": BATCH_ID,
        "checked_at": CHECKED_AT,
        "source": "nedrug.getItemDetail",
        "relation_source": "medistack_v0.2_beta_export.json",
        "alias_source": "medistack_v0.3_aliases.json",
        "alias_count_at_generation": alias["meta"]["alias_count"],
        "approved_ready_count": len(approved),
        "deferred_count": len(deferred),
        "deferred": [{"queue_idx": i, "item_seq": s, "reason": r} for i, s, r in deferred],
    }
    with open(AR_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "approved_ready": approved}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(AR_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        for e in approved:
            w.writerow({k: e.get(k, "") for k in CSV_COLS})
    print(f"\nAR 생성: approved_ready={len(approved)} · deferred={len(deferred)} → {os.path.relpath(AR_JSON, REPO)}")
    return run_validate()


def run_validate(ar_path=AR_JSON):
    """네트워크 없이 AR 파일을 안전기준으로 정적 재검증."""
    if not os.path.exists(ar_path):
        print(f"[FATAL] AR 파일 없음: {ar_path} (먼저 네트워크 모드로 생성)")
        return 1
    ar = C.load(ar_path, "surface AR")
    ents = ar.get("approved_ready") if isinstance(ar, dict) else None
    existing_seqs = C.existing_alias_itemseqs()
    live_surfaces = live_alias_surfaces(C.load(C.ALIAS_PATH, "alias"))
    allowed = C.allowed_canonical()
    fails, seen_seq = [], set()
    if not isinstance(ents, list):
        print("[FAIL] shape(meta + approved_ready 리스트)"); return 1
    for e in ents:
        a = e.get("candidate_alias")
        tag = repr(a)
        for k in ("candidate_alias", "canonical_ingredient", "item_seq", "item_name", "ingr_name"):
            if not str(e.get(k, "")).strip():
                fails.append(f"{tag}: 필수필드 누락 {k}")
        if str(e.get("approved_ready")).lower() != "true":
            fails.append(f"{tag}: approved_ready!=true")
        if str(e.get("incorporated")).lower() != "false":
            fails.append(f"{tag}: incorporated!=false (이 단계는 미반영만)")
        if str(e.get("reviewer_required")).lower() != "true":
            fails.append(f"{tag}: reviewer_required!=true")
        if str(e.get("confidence")) != "high":
            fails.append(f"{tag}: confidence!=high")
        if e.get("is_combination") or e.get("combination_basis_ingredient"):
            fails.append(f"{tag}: 복합제 필드 금지(단일성분 트랙)")
        if surface_anomalies(a):
            fails.append(f"{tag}: candidate_alias 표면형 이상 잔존")
        if a != e.get("item_name"):
            fails.append(f"{tag}: candidate_alias != item_name")
        seq = str(e.get("item_seq", "")).strip()
        if not seq.isdigit():
            fails.append(f"{tag}: item_seq 비숫자")
        if seq in C.FORBIDDEN_ITEMSEQS:
            fails.append(f"{tag}: itemSeq forbidden")
        if seq in seen_seq:
            fails.append(f"{tag}: itemSeq 파일내 중복")
        seen_seq.add(seq)
        if seq in existing_seqs:
            fails.append(f"{tag}: itemSeq 이미 라이브 alias 보유(미반영 단계 위반)")
        canon = e.get("canonical_ingredient")
        if canon == C.EXCLUDED_BYPASS_INGREDIENT or canon not in allowed:
            fails.append(f"{tag}: canonical '{canon}' 허용집합 밖/에스오메프라졸")
        if canon and canon not in str(e.get("ingr_name", "")):
            fails.append(f"{tag}: canonical '{canon}' ⊄ ingr_name")
        if nfc(a) in live_surfaces:
            fails.append(f"{tag}: 표면형 이미 라이브 alias 중복")
        if C.ESO_HINT_RE.search(str(a)) or C.ESO_HINT_RE.search(str(e.get("ingr_name", ""))):
            fails.append(f"{tag}: 에스오메프라졸/넥시움 신호")

    bar = "=" * 64
    print(bar); print(f"v0.9 surface approved-ready 검증: {os.path.relpath(ar_path, REPO)} ({len(ents)} entries)"); print(bar)
    if fails:
        print(f"[FAIL] {len(fails)}건")
        for x in fails[:30]:
            print("  X", x)
        print(f"\nRESULT: FAIL"); print(bar); return 1
    print(f"\n모든 안전기준 통과 ({len(ents)} approved-ready·incorporated=false·라이브 미반영).")
    print(f"RESULT: PASS"); print(bar); return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="네트워크 없이 기존 AR 정적 재검증")
    args = ap.parse_args()
    sys.exit(run_validate() if args.validate else run_recollect())
