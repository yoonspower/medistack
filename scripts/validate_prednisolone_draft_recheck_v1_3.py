#!/usr/bin/env python3
"""validate_prednisolone_draft_recheck_v1_3.py
data/review/prednisolone_potassium_draft_recheck_v1_3.json (draft-only 후보) 안전 불변 검증.
live export/full index/alias 무관 — draft 아티팩트 계약만 확인. PASS 없으면 비-0 종료.

검증 항목:
  1) meta: live_integration_forbidden/do_not_implement_yet=true, published/clinical_reviewed=false, reviewed_by 공란, live_relations/promotions=0.
  2) 각 item: live_integration_forbidden=true, published=false, clinical_reviewed=false, reviewed_by="",
     requires_clinical_review=true, product_link_allowed=false.
  3) 칼륨 행: potassium_safety_card=true, mechanism=depletion, recommended_action=monitoring.
  4) itemseq 는 실 NEDRUG itemSeq(숫자, fixture 100001~100006 금지).
  5) management = anti-supplement(임의 보충 금지 문구) — 보충 '권유' 금지.
  6) display = 장기/고용량/문의 프레이밍 + 결핍 단정 없음.
  7) source_quote 에 칼륨 고갈 동거어(칼륨손실/저칼륨) 존재.
  8) forbidden phrase(식약처 승인/약사 검수 완료/법적 문제 없음/구매/제휴/할인) 0.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PATH = os.path.join(REPO, "data", "review", "prednisolone_potassium_draft_recheck_v1_3.json")

FIXTURE_SEQS = {"100001", "100002", "100003", "100004", "100005", "100006"}
FORBIDDEN = ["식약처 승인", "약사 검수 완료", "법적 문제 없음", "구매", "제휴", "할인", "최저가",
             "결핍입니다", "결핍 상태입니다", "보충하세요", "복용하세요", "드세요"]
SUPP_RECO = ["칼륨을 보충", "칼륨 보충제", "칼륨을 드", "칼륨을 섭취하세요"]


def main():
    errs = []
    d = json.load(open(PATH, encoding="utf-8"))
    m = d.get("meta", {})
    # 1) meta
    for k, want in [("live_integration_forbidden", True), ("do_not_implement_yet", True),
                    ("published", False), ("clinical_reviewed", False),
                    ("live_relations_created", 0), ("live_promotions", 0)]:
        if m.get(k) != want:
            errs.append(f"meta.{k}={m.get(k)!r} (expected {want!r})")
    if m.get("reviewed_by", "x") != "":
        errs.append(f"meta.reviewed_by 비공란: {m.get('reviewed_by')!r}")

    items = d.get("items", [])
    if not items:
        errs.append("items 비어있음")
    for it in items:
        cid = it.get("draft_id") or it.get("candidate_id") or "?"
        # 2) item 불변
        for k, want in [("live_integration_forbidden", True), ("published", False),
                        ("clinical_reviewed", False), ("requires_clinical_review", True),
                        ("product_link_allowed", False)]:
            if it.get(k) != want:
                errs.append(f"{cid}.{k}={it.get(k)!r} (expected {want!r})")
        if it.get("reviewed_by", "x") != "":
            errs.append(f"{cid}.reviewed_by 비공란")
        # 3) 칼륨 행
        if it.get("nutrient") == "칼륨":
            if it.get("potassium_safety_card") is not True:
                errs.append(f"{cid}: 칼륨 행인데 potassium_safety_card!=true")
            if it.get("mechanism") != "depletion":
                errs.append(f"{cid}: mechanism!=depletion")
            if it.get("recommended_action") != "monitoring":
                errs.append(f"{cid}: recommended_action!=monitoring")
        # 4) itemseq 실값
        seq = str(it.get("itemseq", ""))
        if not seq.isdigit():
            errs.append(f"{cid}: itemseq 비숫자({seq!r})")
        if seq in FIXTURE_SEQS:
            errs.append(f"{cid}: fixture itemseq({seq}) 사용 금지 — 실 NEDRUG itemSeq 필요")
        # 5) management anti-supplement
        mg = it.get("final_management_ko", "")
        if "임의로 보충하지" not in mg and "임의로 보충하면" not in mg:
            errs.append(f"{cid}: management anti-supplement 문구 부재")
        for bad in SUPP_RECO:
            if bad in mg or bad in it.get("final_display_text_ko_named", ""):
                errs.append(f"{cid}: 칼륨 보충 권유 문구 감지({bad})")
        # 6) display 프레이밍 + 결핍 단정 없음
        disp = it.get("final_display_text_ko_named", "") + it.get("final_display_text_ko", "")
        if not (("장기간" in disp or "고용량" in disp) and ("문의" in disp or "상담" in disp or "확인" in disp)):
            errs.append(f"{cid}: display 장기/고용량/문의 프레이밍 부재")
        # 7) source_quote 동거어
        sq = it.get("source_quote", "")
        if not ("칼륨손실" in sq or "저칼륨" in sq or "칼륨 배설" in sq or "칼륨손" in sq):
            errs.append(f"{cid}: source_quote 칼륨 고갈 동거어 부재")
        # 8) forbidden
        blob = json.dumps(it, ensure_ascii=False)
        for bad in FORBIDDEN:
            if bad in blob:
                errs.append(f"{cid}: forbidden phrase '{bad}'")

    if errs:
        print("FAIL — prednisolone draft recheck 검증 실패:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"PASS — prednisolone draft-only batch 검증 통과 (items={len(items)}, "
          f"itemseq 실값, 칼륨 안전카드/anti-supplement/clinical-review-gate/forbidden 0).")


if __name__ == "__main__":
    main()
