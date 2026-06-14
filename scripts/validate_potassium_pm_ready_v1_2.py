#!/usr/bin/env python3
"""
validate_potassium_pm_ready_v1_2.py
MediStack 칼륨 depletion/monitoring PM-ready 산출물 **데이터 계약 검증**(읽기전용).

검사:
  - 6건(DF01·DF04·DF05·DF02·CQF03·DF03) 존재, draft_id 유일.
  - 전건 potassium_safety_card=true · product_link_allowed=false.
  - 전건 published=false · clinical_reviewed=false · reviewed_by 공란.
  - 전건 live_integration_forbidden=true (이번 라운드 live 승격 0).
  - 전건 long_term_high_dose_context=true.
  - pm_readiness ∈ {PM-ready, needs_clinical_wording_review, hold_continue}.
  - promotion_candidate=true 는 pm_readiness=PM-ready 일 때만(승격 후보 플래그 정합).
  - final_display/final_management = 통일 템플릿 정합(장기·고용량 맥락 포함, 보충 권유/결핍 단정 0).
  - meta.distribution / promotion_candidates 가 items 와 일치.
사용: python3 scripts/validate_potassium_pm_ready_v1_2.py
종료코드: 0 PASS, 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PM = os.path.join(REPO, "data", "review", "potassium_depletion_pm_ready_v1_2.json")

EXPECT_IDS = {"DF01", "DF02", "DF03", "DF04", "DF05", "CQF03"}
READINESS = {"PM-ready", "needs_clinical_wording_review", "hold_continue"}
# 통일 문구 필수 어구(장기·고용량 맥락 + 비단정 모니터링 + 임의 보충 금지).
DISPLAY_MUST = ["장기간 복용하거나 고용량", "칼륨 상태에 영향", "확인이 필요한지 문의"]
MGMT_MUST = ["임의로 보충하지 말고", "상담해 결정"]
# 칼륨 카피 금지(보충 권유·결핍 단정).
COPY_FORBIDDEN = ["칼륨을 보충", "칼륨제를", "칼륨 섭취를 늘", "결핍입니다", "부족합니다", "빠집니다",
                  "복용하세요", "반드시 드", "구매", "제휴", "추천 영양제", "치료", "예방"]


def main():
    fails = []
    if not os.path.exists(PM):
        print(f"[FAIL] 파일 없음: {PM}")
        return 1
    d = json.load(open(PM, encoding="utf-8"))
    items = d.get("items", [])
    ids = [i["draft_id"] for i in items]

    if set(ids) != EXPECT_IDS:
        fails.append(f"draft_id 집합 불일치: {sorted(ids)} != {sorted(EXPECT_IDS)}")
    if len(ids) != len(set(ids)):
        fails.append("draft_id 중복")

    promo = []
    dist = {}
    for i in items:
        did = i["draft_id"]
        dist[i.get("pm_readiness")] = dist.get(i.get("pm_readiness"), 0) + 1
        if i.get("pm_readiness") not in READINESS:
            fails.append(f"{did}: pm_readiness 부정({i.get('pm_readiness')})")
        for fld, exp in (("potassium_safety_card", True), ("product_link_allowed", False),
                         ("published", False), ("clinical_reviewed", False),
                         ("live_integration_forbidden", True), ("long_term_high_dose_context", True),
                         ("source_confirmed", True)):
            if i.get(fld) != exp:
                fails.append(f"{did}: {fld}={i.get(fld)} (기대 {exp})")
        if i.get("reviewed_by", "") != "":
            fails.append(f"{did}: reviewed_by 비공란")
        if i.get("promotion_candidate"):
            promo.append(did)
            if i.get("pm_readiness") != "PM-ready":
                fails.append(f"{did}: promotion_candidate=true 인데 pm_readiness≠PM-ready")
        disp = i.get("final_display_text_ko", "")
        dispn = i.get("final_display_text_ko_named", "")
        mgmt = i.get("final_management_ko", "")
        for m in DISPLAY_MUST:
            if m not in disp:
                fails.append(f"{did}: final_display 통일문구 누락('{m}')")
        if i["ingredient"] not in dispn or "장기간 복용하거나 고용량" not in dispn:
            fails.append(f"{did}: named 변형 약물명/맥락 누락")
        for m in MGMT_MUST:
            if m not in mgmt:
                fails.append(f"{did}: final_management 통일문구 누락('{m}')")
        for fb in COPY_FORBIDDEN:
            if fb in disp or fb in mgmt or fb in dispn:
                fails.append(f"{did}: 칼륨 카피 금지어 '{fb}'")

    # meta 정합
    meta = d.get("meta", {})
    if meta.get("distribution") != dist:
        fails.append(f"meta.distribution 불일치: {meta.get('distribution')} != {dist}")
    if sorted(meta.get("promotion_candidates", [])) != sorted(promo):
        fails.append(f"meta.promotion_candidates 불일치: {meta.get('promotion_candidates')} != {promo}")
    if meta.get("count") != len(items):
        fails.append("meta.count 불일치")

    print(f"=== potassium PM-ready validator: {len(items)}건 ===")
    print(f"분류 분포: {dist} | 승격 후보: {promo}")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 6건 정합 · live 승격 0 · 통일문구 적용 · 칼륨 금지어 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
