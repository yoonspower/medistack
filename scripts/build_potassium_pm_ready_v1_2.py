#!/usr/bin/env python3
"""
build_potassium_pm_ready_v1_2.py
MediStack 칼륨 depletion/monitoring 6건(DF01-05·CQF03) **PM-ready 최종화** 산출물 생성.

이 스크립트는 source_confirmed 판정을 새로 하지 않는다 — 6건은 이미 적대검증 통과 source_confirmed(high).
여기서는 (a)통일 문구(track doc §1) 적용, (b)PM 승인 준비도 분류, (c)승격 후보 표시(플래그일 뿐 승격 아님),
(d)장기·고용량 맥락 플래그를 결정론적으로 부여한다. **이번 라운드 live 승격 0**(전건 live_integration_forbidden).

분류(track doc §2 + 보류 사유 반영):
  PM-ready                       : 근거·국내 유통·통일문구 적용 명확 → 승격 후보(플래그)
  needs_clinical_wording_review  : 근거는 있으나 wording(약한 MC·제형 맥락) 임상 검수 권장
  hold_continue                  : 국내 유통/가용성 등 추가 확인 필요로 보류 지속

⚠️ 보호 데이터 무수정(읽기전용 입력 + review 산출물만 write).
출력:
  data/review/potassium_depletion_pm_ready_v1_2.json
  data/review/potassium_depletion_pm_ready_v1_2.csv
사용: python3 scripts/build_potassium_pm_ready_v1_2.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
FACTORY = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")          # DF01-05
BATCH3 = os.path.join(DATA, "coverage_queue_draft_batch3_v1_2.json")            # CQF03
OUT_JSON = os.path.join(DATA, "review", "potassium_depletion_pm_ready_v1_2.json")
OUT_CSV = os.path.join(DATA, "review", "potassium_depletion_pm_ready_v1_2.csv")

# track doc §1 / 작업 A 권장 통일 문구(verbatim).
DISPLAY = ("이 약을 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, "
           "진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.")
DISPLAY_NAMED = ("{ing}을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, "
                 "진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.")
MANAGEMENT = "칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요."

# PM 준비도 분류(track doc §2 + 보류 사유). 모두 long_term_high_dose_context=True.
CLASSIFICATION = {
    "DF01": ("PM-ready", True, "라벨 직접근거 명확(칼륨손실+저칼륨성 알칼리혈증). 글루코코르티코이드 대표. 통일문구 적용 시 승격 후보."),
    "DF04": ("PM-ready", True, "탄산탈수효소억제 이뇨·저칼륨혈증 직접 listing·국내 유통(아세타졸정). 승격 후보."),
    "DF05": ("PM-ready", True, "루프이뇨제(유레틴정)·저칼륨혈증 직접·국내 유통 명확. 승격 후보."),
    "DF02": ("needs_clinical_wording_review", False, "미네랄코르티코이드 작용 약함·라벨은 '저칼륨성 알칼리혈증'만(칼륨손실 직접어 없음) → wording 강도 임상 검수 권장."),
    "CQF03": ("needs_clinical_wording_review", False, "외용 비중 큰 성분·전신 제형(래피손정) 한정 wording 필요 → 임상 검수 권장."),
    "DF03": ("hold_continue", False, "강한 MC이나 국내 유통 적음(플로리네프정 1품목) — 품목 가용성 재확인 후 검토. 보류 지속."),
}
ORDER = ["DF01", "DF04", "DF05", "DF02", "CQF03", "DF03"]  # 근거·유통 명확도 순(track doc §3 승격순서)


def load_six():
    rows = {}
    fac = json.load(open(FACTORY, encoding="utf-8"))
    for r in fac["draft_relations"]:
        if r["draft_id"] in ("DF01", "DF02", "DF03", "DF04", "DF05"):
            rows[r["draft_id"]] = r
    b3 = json.load(open(BATCH3, encoding="utf-8"))
    for r in b3["draft_relations"]:
        if r["draft_id"] == "CQF03":
            rows["CQF03"] = r
    return rows


def main():
    src = load_six()
    items = []
    for did in ORDER:
        r = src[did]
        cls, promo, why = CLASSIFICATION[did]
        seq = r["source"]["url"].split("itemSeq=")[-1]
        items.append({
            "draft_id": did, "ingredient": r["ingredient"], "nutrient": "칼륨",
            "mechanism": "depletion", "recommended_action": "monitoring", "evidence_level": "high",
            "source_confirmed": True, "adversarial_verified": True,
            "itemseq": seq,
            "pm_readiness": cls,
            "promotion_candidate": promo,        # 플래그일 뿐 — 이번 라운드 승격 아님
            "long_term_high_dose_context": True,
            "final_display_text_ko": DISPLAY,
            "final_display_text_ko_named": DISPLAY_NAMED.format(ing=r["ingredient"]),
            "final_management_ko": MANAGEMENT,
            "potassium_safety_card": True,
            "product_link_allowed": False,
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "live_integration_forbidden": True,   # 이번 라운드 전건 금지
            "classification_reason": why,
            "source_pointer": r["source"]["pointer"],
        })

    from collections import Counter
    dist = Counter(i["pm_readiness"] for i in items)
    promos = [i["draft_id"] for i in items if i["promotion_candidate"]]
    out = {
        "meta": {
            "name": "potassium_depletion_pm_ready_v1_2", "created_at": "2026-06-14",
            "status": "PM-READY 분류 — live 승격 0(전건 live_integration_forbidden). 승격은 PM 승인+clinical reviewer 노트 후.",
            "track": "potassium depletion/monitoring",
            "copy_source": "track doc §1 통일 문구(작업 A 권장) verbatim",
            "count": len(items),
            "distribution": dict(dist),
            "promotion_candidates": promos,
            "policy": "potassium_safety_card=true·product_link_allowed=false·published/clinical_reviewed=false 유지. 칼륨 보충 권유 0·결핍 단정 0.",
            "note": "6건 모두 source_confirmed high(적대검증 통과). 분류는 승격 준비도이며 근거 부족 보류는 없음. 승격 후보(promotion_candidate=true)는 플래그일 뿐 이번 라운드 승격 아님.",
        },
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    cols = ["draft_id", "ingredient", "itemseq", "pm_readiness", "promotion_candidate",
            "long_term_high_dose_context", "evidence_level", "source_confirmed", "adversarial_verified",
            "potassium_safety_card", "product_link_allowed", "live_integration_forbidden",
            "final_display_text_ko", "final_management_ko", "classification_reason"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i in items:
            w.writerow({k: i[k] for k in cols})

    print(f"=== potassium PM-ready: {len(items)}건 ===")
    print(f"분류 분포: {dict(dist)}")
    print(f"승격 후보(플래그, 승격 아님): {promos}")
    for i in items:
        print(f"  {i['draft_id']} {i['ingredient']:10s} {i['pm_readiness']:32s} promo={i['promotion_candidate']} live_forbidden={i['live_integration_forbidden']}")
    print(f"[write] {os.path.relpath(OUT_JSON, REPO)}")
    print(f"[write] {os.path.relpath(OUT_CSV, REPO)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
