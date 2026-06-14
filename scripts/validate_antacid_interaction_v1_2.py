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
  - display = directive_type 별 템플릿 verbatim(avoid_concomitant=prohibition 보존형 / separation·coadmin_caution=중립),
    avoid_concomitant 에 weak neutral 카피 금지, management 공란(상담 트리거는 display 종결문).
  - directive ↔ render_action 정합: avoid_concomitant 에 separation('복용 간격') chip 금지(다운그레이드).
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

# directive_type 별 display 템플릿(Option A, 2026-06-14):
#  - 중립(separation/coadmin_caution): '함께 사용할 때 흡수 영향' 톤(병용 자체는 허용·간격/모니터링 신호).
#  - avoid_concomitant 전용: 라벨의 병용금지를 다운그레이드하지 않도록 'prohibition 보존형'(출처 귀속·비지시).
#    중립 템플릿을 avoid_concomitant 에 쓰면 prohibition 을 'co-use 가능+상담'으로 약화 → 금지.
NEUTRAL_TEMPLATE = ("일부 알루미늄·마그네슘 함유 제산제와 함께 사용할 때 약물 흡수에 영향을 줄 수 있다는 "
                    "허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.")
AVOID_CONCOMITANT_TEMPLATE = ("일부 알루미늄·마그네슘 함유 제산제와 함께 복용하지 않도록 안내하는 "
                              "허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.")
TEMPLATE_BY_DIRECTIVE = {
    "avoid_concomitant": AVOID_CONCOMITANT_TEMPLATE,
    "separation": NEUTRAL_TEMPLATE,
    "coadmin_caution": NEUTRAL_TEMPLATE,
}
DIRECTIVE_OK = {"avoid_concomitant", "separation", "coadmin_caution"}
# Mg 영양제 오인 유발 표현(antacid 트랙 카피에 있으면 안 됨).
MG_SUPPLEMENT_CONFUSION = ["마그네슘 영양제", "마그네슘 보충제", "마그네슘제를", "마그네슘을 보충", "영양제를 드세요"]
COPY_FORBIDDEN = ["복용하지 마세요", "복용하세요", "시간 간격을 두세요", "구매", "제휴", "추천", "치료", "예방", "반드시",
                  "식약처 승인", "약사 검수 완료", "법적 문제 없음", "승인 완료"]
# 제품/제휴/영양소 링크 필드(antacid draft 에 있으면 안 됨 — 제품/구매/제휴 UI 금지·영양소 relation 오인 차단).
FORBIDDEN_LINK_KEYS = ["product_links", "product_examples", "products", "affiliate_links", "buy_links",
                       "nutrient_link", "product_link", "nutrient_id", "supplement_link"]


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
        directive = r.get("label_directive_type")
        exp_tmpl = TEMPLATE_BY_DIRECTIVE.get(directive)
        if exp_tmpl is None:
            fails.append(f"{did}: label_directive_type '{directive}' 대응 display 템플릿 없음")
        elif r.get("display_text_ko") != exp_tmpl:
            fails.append(f"{did}: display ≠ '{directive}' directive 템플릿 verbatim")
        # avoid_concomitant 는 weak neutral 카피 금지(prohibition 을 'co-use 가능+상담'으로 다운그레이드 차단)
        if directive == "avoid_concomitant" and r.get("display_text_ko") == NEUTRAL_TEMPLATE:
            fails.append(f"{did}: avoid_concomitant 에 weak neutral 카피 금지(prohibition→co-use 다운그레이드)")
        if (r.get("management_ko") or "") != "":
            fails.append(f"{did}: management 비공란(상담 트리거는 display 종결문)")
        disp = r.get("display_text_ko", "")
        for fb in MG_SUPPLEMENT_CONFUSION:
            if fb in disp:
                fails.append(f"{did}: Mg 영양제 오인 표현 '{fb}'")
        for fb in COPY_FORBIDDEN:
            if fb in disp:
                fails.append(f"{did}: 카피 금지어 '{fb}'")
        # reviewed_by 공란 필수(clinical reviewer 미확보 — 검수 완료로 오인 금지)
        if (r.get("reviewed_by") or "") != "":
            fails.append(f"{did}: reviewed_by 비공란({r.get('reviewed_by')!r}) — clinical reviewer 전 공란 유지")
        # 제품/제휴/영양소 링크 필드 금지(제품/구매/제휴 UI·영양소 relation 오인 차단)
        for k in FORBIDDEN_LINK_KEYS:
            if k in r:
                fails.append(f"{did}: 금지 링크 필드 '{k}' 존재(제품/제휴/영양소 링크 금지)")
        # nutrient 영양소 필드로 저장 금지(antacid 는 약물 카테고리 트랙 — Mg 영양소 relation 아님)
        if "nutrient" in r:
            fails.append(f"{did}: nutrient 필드 존재 — antacid 트랙은 counterpart_category 만 사용(영양소 relation 오인 금지)")
        # surface 렌더 매핑(있으면): render_nutrient 는 제산제(약물)여야·영양소 아님 / render_action 유효 / 분리 플래그
        surf = r.get("surface")
        if surf is not None:
            rn = surf.get("render_nutrient", "")
            if "제산제" not in rn:
                fails.append(f"{did}: surface.render_nutrient 에 '제산제' 명시 누락({rn!r}) — 영양소 오인")
            for fb in MG_SUPPLEMENT_CONFUSION:
                if fb in rn:
                    fails.append(f"{did}: surface.render_nutrient Mg 영양제 오인 표현 '{fb}'")
            if rn.strip() in ("마그네슘", "마그네슘(영양소)", "Mg", "철분", "칼슘", "칼륨", "아연"):
                fails.append(f"{did}: surface.render_nutrient 가 영양소 단독({rn}) — antacid 트랙 위반")
            ra = surf.get("render_action")
            if ra not in ("separation", "monitoring"):
                fails.append(f"{did}: surface.render_action 부정({ra})")
            # directive ↔ render_action 정합: '복용 간격'(separation chip)은 'spacing 두면 병용 가능' 신호 →
            # avoid_concomitant(병용금지)에 쓰면 prohibition 다운그레이드. separation chip 은 separation directive 에만 허용.
            if directive == "avoid_concomitant" and ra == "separation":
                fails.append(f"{did}: avoid_concomitant 에 render_action=separation('복용 간격' chip) 금지(prohibition 다운그레이드) — monitoring 등 비-spacing chip 사용")
            if surf.get("not_a_nutrient_relation") is not True:
                fails.append(f"{did}: surface.not_a_nutrient_relation≠true(영양소 분리 플래그 누락)")
        # online_reconcile(있으면): 운영 harvester provenance — online_item_seq 실값 보존(기존 근거 폐기 아님)
        orc = r.get("online_reconcile")
        if orc is not None:
            seq = str(orc.get("online_item_seq") or "")
            if not (seq.isdigit() and len(seq) >= 6):
                fails.append(f"{did}: online_reconcile.online_item_seq 실 itemSeq 아님({seq!r})")
            if not (orc.get("provenance_note") or "").strip():
                fails.append(f"{did}: online_reconcile.provenance_note 공란(기존 근거 폐기 아님 — provenance 필요)")
        # adversarial_verified=true 는 적대검증 통과 표시일 뿐 — 자동 승격 금지(live/published/clinical/reviewed_by 불변)
        if r.get("adversarial_verified") is True:
            if r.get("live_integration_forbidden") is not True or r.get("published") is not False \
               or r.get("clinical_reviewed") is not False or (r.get("reviewed_by") or "") != "":
                fails.append(f"{did}: adversarial_verified=true 이나 안전 플래그 위반 — 적대검증은 승격 아님(live_integration_forbidden/published/clinical_reviewed/reviewed_by 불변 필수)")

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
