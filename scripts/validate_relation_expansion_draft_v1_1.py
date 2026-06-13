#!/usr/bin/env python3
"""
validate_relation_expansion_draft_v1_1.py
MediStack — relation 확장 draft(data/relation_expansion_draft_v1_1.json) 전용 validator.

검증 원칙:
  - **기존 relation 30 불변**: draft 의 id 1–14,16–31 이 v0.2 export 와 dict-equal(핵심자산 훼손 0).
  - **신규 11(ids 32–42)**: 필수필드·enum(evidence high/moderate·action sep/mon·mechanism absorption/depletion)·
    requires_clinical_review=false·potassium_safety_card=false·제품필드 금지·출처(허가사항+itemSeq URL+확인일).
  - **참고정보 톤**: display_text/management 에 복용지시·영양제/제품 추천·진단/처방 표현 금지, 헤지 문구 존재.
  - **금지 성분 미포함**: missing 3(파모티딘/라푸티딘/니자티딘) + 에스오메프라졸 = relations 에 없음.
  - **라이브 무변경**: meta.published/clinical_reviewed=false·live=false, DATA_URL(src/js/data.js)=v0.2 유지.

사용: python3 scripts/validate_relation_expansion_draft_v1_1.py
종료: 0 PASS / 1 FAIL
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
DRAFT = os.path.join(DATA, "relation_expansion_draft_v1_1.json")
V02 = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

ALLOWED_EVIDENCE = {"high", "moderate"}
ALLOWED_ACTION = {"separation", "monitoring"}
ALLOWED_MECHANISM = {"absorption", "depletion"}
REQUIRED = ("id", "ingredient", "nutrient", "recommended_action", "mechanism",
            "evidence_level", "display_text_ko", "management_ko",
            "product_link_allowed", "potassium_safety_card", "requires_clinical_review", "source")
FORBIDDEN_RELATION_FIELDS = ("status", "published", "clinical_reviewed")
PRODUCT_FIELD_HINT = re.compile(r"(affiliate|shop|buy|store|purchase|cart)", re.IGNORECASE)
# 복용지시/영양제·제품 추천/진단·처방 표현 금지(참고정보 톤 위반)
FORBIDDEN_COPY = ["복용하세요", "드세요", "섭취하세요", "보충하세요", "보충제를 복용", "보충하시", "구매",
                  "사세요", "추천합니다", "추천드", "처방", "진단", "치료하세요", "복용하십시오"]
HEDGE = ["수 있습니다", "수 있다는", "권장될 수 있", "필요할 수 있", "문의해볼 수 있", "상담"]

NEW_IDS = set(range(32, 43))
EXPECT_NEW_INGREDIENTS = {"라베프라졸", "판토프라졸", "란소프라졸", "덱스란소프라졸",
                          "리세드론산", "이반드론산", "세프디니르"}
FORBIDDEN_INGREDIENTS = {"파모티딘", "라푸티딘", "니자티딘", "에스오메프라졸"}

CHECKS = []


def ck(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))


def main():
    draft = json.load(open(DRAFT, encoding="utf-8"))
    v02 = json.load(open(V02, encoding="utf-8"))
    djs = open(DATA_JS, encoding="utf-8").read()

    meta = draft.get("meta", {})
    rels = draft.get("relations", [])
    by_id = {r["id"]: r for r in rels if isinstance(r, dict) and "id" in r}
    v02_by_id = {r["id"]: r for r in v02["relations"]}

    ck("구조: meta(dict)+relations(list)", isinstance(meta, dict) and isinstance(rels, list))
    ck("relation_count == len(relations) == 41",
       meta.get("relation_count") == len(rels) == 41, f"meta={meta.get('relation_count')} len={len(rels)}")
    ck("id 유니크", len(by_id) == len(rels))

    # 기존 30 불변(dict-equal v0.2)
    base_ids = sorted(v02_by_id.keys())
    mismatch = [i for i in base_ids if by_id.get(i) != v02_by_id.get(i)]
    ck("기존 relation 30 v0.2와 dict-equal(핵심자산 불변)", not mismatch, f"불일치 id={mismatch[:5]}")
    ck("기존 30 id 집합 보존", set(base_ids).issubset(set(by_id.keys())))

    # 신규 11
    new = [by_id[i] for i in sorted(NEW_IDS) if i in by_id]
    ck("신규 id 32-42 = 11건", set(by_id.keys()) - set(base_ids) == NEW_IDS,
       f"신규 id={sorted(set(by_id.keys())-set(base_ids))}")

    miss_req = [f"id{r.get('id')}:{k}" for r in new for k in REQUIRED if k not in r]
    ck("신규 필수필드 완비", not miss_req, str(miss_req[:5]))

    enum_bad = []
    for r in new:
        if r.get("evidence_level") not in ALLOWED_EVIDENCE: enum_bad.append(f"id{r['id']} ev={r.get('evidence_level')}")
        if r.get("recommended_action") not in ALLOWED_ACTION: enum_bad.append(f"id{r['id']} act={r.get('recommended_action')}")
        if r.get("mechanism") not in ALLOWED_MECHANISM: enum_bad.append(f"id{r['id']} me={r.get('mechanism')}")
    ck("신규 enum 경계(evidence high/moderate·action sep/mon·mechanism absorption/depletion)", not enum_bad, str(enum_bad[:5]))

    ck("신규 requires_clinical_review=false 전건",
       all(r.get("requires_clinical_review") is False for r in new))
    ck("신규 potassium_safety_card=false 전건(칼륨 후보 없음)",
       all(r.get("potassium_safety_card") is False for r in new))
    ck("신규 product_link_allowed boolean",
       all(isinstance(r.get("product_link_allowed"), bool) for r in new))

    forb_field = [f"id{r['id']}:{k}" for r in new for k in r
                  if k in FORBIDDEN_RELATION_FIELDS or PRODUCT_FIELD_HINT.search(k)]
    ck("신규 금지필드 없음(status/published/clinical_reviewed/제품)", not forb_field, str(forb_field[:5]))

    # 출처
    src_bad = []
    for r in new:
        s = r.get("source", {})
        if s.get("type") != "허가사항": src_bad.append(f"id{r['id']} type")
        if "itemSeq=" not in (s.get("url") or ""): src_bad.append(f"id{r['id']} url")
        if "확인일 2026-06-13" not in (s.get("pointer") or ""): src_bad.append(f"id{r['id']} pointer/날짜")
    ck("신규 출처: 허가사항+itemSeq URL+확인일 2026-06-13", not src_bad, str(src_bad[:5]))

    # 참고정보 톤
    tone_bad, hedge_bad = [], []
    for r in new:
        txt = (r.get("display_text_ko", "") + " " + r.get("management_ko", ""))
        for f in FORBIDDEN_COPY:
            if f in txt: tone_bad.append(f"id{r['id']}:{f}")
        if not any(h in txt for h in HEDGE): hedge_bad.append(f"id{r['id']}")
    ck("신규 참고정보 톤(복용지시/영양제·제품추천/진단·처방 표현 없음)", not tone_bad, str(tone_bad[:5]))
    ck("신규 헤지 문구 존재(단정 아님)", not hedge_bad, str(hedge_bad[:5]))

    # 신규 성분 정확히 7 + 금지 성분 미포함(전 relations)
    new_ings = {r["ingredient"] for r in new}
    ck("신규 성분 = 확정 7후보", new_ings == EXPECT_NEW_INGREDIENTS,
       f"신규={sorted(new_ings)}")
    # 금지 성분은 *신규* relation 에 없어야 함(missing 후보 미승격). 기존 30의 id16 에스오메프라졸은
    # v0.2 그대로 보존된 것(위 dict-equal 검증)으로 신규 추가가 아님 → 신규만 검사.
    forb_ing = [r["id"] for r in new if r.get("ingredient") in FORBIDDEN_INGREDIENTS]
    ck("신규에 금지 성분(파모티딘/라푸티딘/니자티딘/에스오메프라졸) 미승격", not forb_ing, str(forb_ing[:5]))

    # 라이브 무변경
    ck("meta.published=false", meta.get("published") is False)
    ck("meta.clinical_reviewed=false", meta.get("clinical_reviewed") is False)
    ck("meta.live=false(draft)", meta.get("live") is False)
    m = re.search(r"DATA_URL\s*=\s*'([^']+)'", djs)
    ck("DATA_URL=v0.2 유지(라이브 무변경)",
       m and m.group(1) == "./data/medistack_v0.2_beta_export.json", m.group(1) if m else "없음")

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    total = len(CHECKS)
    print("=== relation_expansion_draft v1.1 validator ===")
    for name, ok, detail in CHECKS:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if not ok and detail else ""))
    allok = passed == total
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}  ({passed}/{total} checks passed)")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
