#!/usr/bin/env python3
"""
validate_antacid_interaction_v1_2.py
MediStack antacid_interaction 트랙 draft/candidates **데이터 계약 검증**(읽기전용).

검사(draft batch):
  - 각 draft relation_type=antacid_interaction (표면 중립).
  - counterpart_category=al_mg_antacid (영양소 트랙 아님 — Mg 보충제 오인 차단).
  - label_directive_type ∈ {avoid_concomitant, separation}.
  - product_link_allowed=false · potassium_safety_card=false.
  - published=false · clinical_reviewed=false · live_integration_forbidden=true · do_not_implement_yet=true.
  - label_quote(라벨 원문) 비공란 + source.checked_at 존재.
  - display = §4 PM 승인 템플릿 verbatim, management 공란(상담 트리거는 display 종결문).
  - 게이트 정합: gate ledger 의 antacid_draft_confirmed 집합과 draft draft_id 집합 일치.
검사(candidates CSV):
  - 모든 행 live_integration_forbidden=True.
  - draft_eligible=True 행만 verdict=antacid_draft_confirmed.
사용: python3 scripts/validate_antacid_interaction_v1_2.py
종료코드: 0 PASS, 1 FAIL.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")
CAND = os.path.join(DATA, "candidates", "antacid_interaction_candidates_v1_2.csv")
GATE = os.path.join(DATA, "review", "source_confirm_gate_v1_2.json")

DISPLAY_TEMPLATE = ("일부 알루미늄·마그네슘 함유 제산제와 함께 사용할 때 약물 흡수에 영향을 줄 수 있다는 "
                    "허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.")
DIRECTIVE_OK = {"avoid_concomitant", "separation"}
# Mg 영양제 오인 유발 표현(antacid 트랙 카피에 있으면 안 됨).
MG_SUPPLEMENT_CONFUSION = ["마그네슘 영양제", "마그네슘 보충제", "마그네슘제를", "마그네슘을 보충"]
COPY_FORBIDDEN = ["복용하지 마세요", "복용하세요", "시간 간격을 두세요", "구매", "제휴", "추천", "치료", "예방"]


def main():
    fails = []
    if not os.path.exists(DRAFT):
        print(f"[FAIL] 파일 없음: {DRAFT}")
        return 1
    d = json.load(open(DRAFT, encoding="utf-8"))
    drafts = d.get("draft_relations", [])
    draft_ids = set()
    for r in drafts:
        did = r.get("draft_id")
        draft_ids.add(did)
        if r.get("relation_type") != "antacid_interaction":
            fails.append(f"{did}: relation_type≠antacid_interaction")
        if r.get("counterpart_category") != "al_mg_antacid":
            fails.append(f"{did}: counterpart_category≠al_mg_antacid")
        if r.get("label_directive_type") not in DIRECTIVE_OK:
            fails.append(f"{did}: label_directive_type 부정({r.get('label_directive_type')})")
        for fld, exp in (("product_link_allowed", False), ("potassium_safety_card", False),
                         ("published", False), ("clinical_reviewed", False),
                         ("live_integration_forbidden", True), ("do_not_implement_yet", True)):
            if r.get(fld) != exp:
                fails.append(f"{did}: {fld}={r.get(fld)} (기대 {exp})")
        if not (r.get("label_quote") or "").strip():
            fails.append(f"{did}: label_quote 공란(라벨 원문 보존 누락)")
        if not (r.get("source", {}).get("checked_at")):
            fails.append(f"{did}: source.checked_at 누락")
        if r.get("display_text_ko") != DISPLAY_TEMPLATE:
            fails.append(f"{did}: display ≠ §4 템플릿 verbatim")
        if (r.get("management_ko") or "") != "":
            fails.append(f"{did}: management 비공란(상담 트리거는 display 종결문)")
        disp = r.get("display_text_ko", "")
        for fb in MG_SUPPLEMENT_CONFUSION:
            if fb in disp:
                fails.append(f"{did}: Mg 영양제 오인 표현 '{fb}'")
        for fb in COPY_FORBIDDEN:
            if fb in disp:
                fails.append(f"{did}: 카피 금지어 '{fb}'")

    # 게이트 정합
    if os.path.exists(GATE):
        g = json.load(open(GATE, encoding="utf-8"))
        confirmed = {x["candidate_id"] for x in g.get("antacid_track", [])
                     if x.get("verdict") == "antacid_draft_confirmed"}
        if confirmed != draft_ids:
            fails.append(f"게이트 confirmed {sorted(confirmed)} ≠ draft {sorted(draft_ids)}")

    # candidates CSV
    if os.path.exists(CAND):
        for row in csv.DictReader(open(CAND, encoding="utf-8")):
            if row.get("live_integration_forbidden", "").lower() not in ("true", "1"):
                fails.append(f"cand {row.get('candidate_id')}: live_integration_forbidden≠True")
            elig = row.get("draft_eligible", "").lower() in ("true", "1")
            if elig and row.get("verdict") != "antacid_draft_confirmed":
                fails.append(f"cand {row.get('candidate_id')}: draft_eligible 인데 verdict≠antacid_draft_confirmed")

    print(f"=== antacid_interaction validator: draft {len(drafts)}건 ===")
    print(f"draft ids: {sorted(draft_ids)}")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 레이어 분리(표면 antacid_interaction/내부 directive·al_mg_antacid) · live 금지 · Mg 오인 0 · 템플릿 정합")
    return 0


if __name__ == "__main__":
    sys.exit(main())
