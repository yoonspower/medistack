#!/usr/bin/env python3
"""theme map expansion (v1.3) 후보/draft-only 배치 validator.

검증 대상(읽기 전용, live/protected 무관):
- data/review/theme_map_expansion_candidates_v1_3.json
- data/drafts/theme_map_draft_batch_v1_3.json
- (대조) data/medistack_v0.2_beta_export.json — live relation 중복 차단

검사:
 1. candidates schema + initial_status enum + live_allowed=false 전건
 2. draft schema(필수필드) + live_integration_forbidden=true + published/clinical_reviewed=false + reviewed_by 공란
 3. pm_approval_required & clinical_reviewer_required = true
 4. itemSeq 9자리 실값 + source_quote 비어있지 않음
 5. product_link_allowed=false + 제품/구매/제휴 문구 없음(사용자 카피)
 6. forbidden phrase 없음(사용자 카피만 — source_quote/설계필드 제외)
 7. high-risk hold 약물이 source_confirmed/draft 로 들어오지 않음
 8. potassium policy — 칼륨 counterpart 면 potassium_safety_card=true (이 배치엔 칼륨 없음 확인 포함)
 9. antacid counterpart_category — counterpart_type=antacid_drug 면 약물 명시 + Mg 영양제 혼동 없음
10. 중복 없음 — draft 내 (ingredient,nutrient) unique + live 60 relation 과 무중복
11. cross-check — candidates 의 source_confirmed ↔ draft batch 1:1
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "data/review/theme_map_expansion_candidates_v1_3.json")
DRAFT = os.path.join(ROOT, "data/drafts/theme_map_draft_batch_v1_3.json")
EXPORT = os.path.join(ROOT, "data/medistack_v0.2_beta_export.json")

_spec = importlib.util.spec_from_file_location(
    "fp", os.path.join(ROOT, "scripts/validate_forbidden_phrases_v1_2.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

INITIAL_STATUS = {"source_confirmed_draft_candidate", "hold", "needs_review", "source_check_candidate"}
PRODUCT_PHRASES = ["구매", "구입", "제휴", "할인", "쿠폰", "최저가", "바로가기", "제품 링크", "제품링크"]
HIGH_RISK_DRUGS = {
    "와파린", "리바록사반", "아픽사반", "다비가트란", "에독사반", "아스피린", "클로피도그렐",
    "실로스타졸", "메토트렉세이트", "타목시펜", "이마티닙", "카페시타빈", "에스시탈로프람",
    "설트랄린", "알프라졸람", "졸피뎀", "쿠에티아핀", "드로스피레논", "세인트존스워트",
    "밀크씨슬", "은행잎", "스피로노락톤", "에플레레논", "아밀로라이드", "트리암테렌",
}
DRAFT_REQUIRED = ["candidate_id", "family", "ingredient", "nutrient", "counterpart_type",
                  "mechanism", "recommended_action", "evidence_level", "source_itemseq",
                  "source_name", "source_section", "source_quote", "source_url",
                  "display_text_ko_draft", "management_copy_draft", "product_link_allowed",
                  "potassium_safety_card"]


def find_rels(o):
    if isinstance(o, dict):
        if "relations" in o and isinstance(o["relations"], list):
            return o["relations"]
        for v in o.values():
            r = find_rels(v)
            if r is not None:
                return r
    return None


def main():
    errs = []
    cand = json.load(open(CAND))
    draft = json.load(open(DRAFT))
    live = find_rels(json.load(open(EXPORT))) or []
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in live}

    # --- candidates ---
    cm = cand["meta"]
    for k in ("live_allowed",):
        if cm.get(k) is not False:
            errs.append(f"candidates.meta.{k} != false")
    if cm.get("live_integration_forbidden") is not True:
        errs.append("candidates.meta.live_integration_forbidden != true")
    if cm.get("published") is not False or cm.get("clinical_reviewed") is not False:
        errs.append("candidates.meta published/clinical_reviewed must be false")
    if cm.get("reviewed_by", "X") != "":
        errs.append("candidates.meta.reviewed_by must be empty")
    confirmed_ids = set()
    for c in cand["candidates"]:
        cid = c.get("candidate_id", "?")
        if c.get("initial_status") not in INITIAL_STATUS:
            errs.append(f"{cid}: bad initial_status {c.get('initial_status')}")
        if c.get("live_allowed") is not False:
            errs.append(f"{cid}: live_allowed != false")
        st = c.get("initial_status")
        drug = c.get("drug_ingredient", "")
        if st == "source_confirmed_draft_candidate":
            confirmed_ids.add(cid)
            if drug in HIGH_RISK_DRUGS:
                errs.append(f"{cid}: high-risk drug '{drug}' must not be source_confirmed")
        # high-risk drug must only ever be hold
        if drug in HIGH_RISK_DRUGS and st != "hold":
            errs.append(f"{cid}: high-risk drug '{drug}' must be hold (got {st})")

    # --- draft batch ---
    dm = draft["meta"]
    if dm.get("live_integration_forbidden") is not True:
        errs.append("draft.meta.live_integration_forbidden != true")
    if dm.get("published") is not False or dm.get("clinical_reviewed") is not False:
        errs.append("draft.meta published/clinical_reviewed must be false")
    if dm.get("reviewed_by", "X") != "":
        errs.append("draft.meta.reviewed_by must be empty")
    if dm.get("pm_approval_required") is not True or dm.get("clinical_reviewer_required") is not True:
        errs.append("draft.meta pm_approval/clinical_reviewer required must be true")

    seen_pairs = set()
    draft_ids = set()
    for d in draft["drafts"]:
        cid = d.get("candidate_id", "?")
        draft_ids.add(cid)
        for f in DRAFT_REQUIRED:
            if f not in d:
                errs.append(f"{cid}: missing field {f}")
        if d.get("product_link_allowed") is not False:
            errs.append(f"{cid}: product_link_allowed != false")
        # itemSeq 9-digit
        seq = str(d.get("source_itemseq", ""))
        if not re.fullmatch(r"\d{9}", seq):
            errs.append(f"{cid}: source_itemseq not 9-digit real value ({seq})")
        if not (d.get("source_quote") or "").strip():
            errs.append(f"{cid}: empty source_quote")
        # high-risk
        if d.get("ingredient") in HIGH_RISK_DRUGS:
            errs.append(f"{cid}: high-risk drug in draft batch")
        # user-facing copy only
        copy = f"{d.get('display_text_ko_draft','')} {d.get('management_copy_draft','')}"
        bad = fp.scan(copy)
        if bad:
            errs.append(f"{cid}: forbidden phrase in user copy: {bad}")
        for p in PRODUCT_PHRASES:
            if p in copy:
                errs.append(f"{cid}: product/affiliate phrase '{p}' in user copy")
        # potassium policy
        nut = d.get("nutrient", "")
        if "칼륨" in nut and d.get("potassium_safety_card") is not True:
            errs.append(f"{cid}: 칼륨 counterpart requires potassium_safety_card=true")
        # antacid counterpart hygiene
        if d.get("counterpart_type") == "antacid_drug":
            if "약물" not in nut:
                errs.append(f"{cid}: antacid_drug counterpart must label '약물' (got {nut})")
            if not d.get("counterpart_category"):
                errs.append(f"{cid}: antacid_drug counterpart needs counterpart_category")
        # duplicate within batch + vs live
        pair = (d.get("ingredient"), d.get("nutrient"))
        if pair in seen_pairs:
            errs.append(f"{cid}: duplicate (ingredient,nutrient) in batch {pair}")
        seen_pairs.add(pair)
        if pair in live_pairs:
            errs.append(f"{cid}: collides with LIVE relation {pair}")

    # --- cross-check ---
    if confirmed_ids != draft_ids:
        errs.append(f"source_confirmed candidates {confirmed_ids} != draft batch {draft_ids}")

    n_checks = 11
    if errs:
        print(f"RESULT: FAIL ({len(errs)} issue(s))")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"RESULT: PASS ({n_checks} check groups, "
          f"{len(cand['candidates'])} candidates, {len(draft['drafts'])} drafts, "
          f"live relations cross-checked={len(live)})")


if __name__ == "__main__":
    main()
