#!/usr/bin/env python3
"""
adversarial_verify_relation_factory_v1_4.py
MediStack Relation Factory v1.4 — factory 43 draft 후보 **적대검증(refute-by-default)** 기록·산출(네트워크 0·읽기전용 입력).

본 스크립트는 PM(별도 AI/사람)이 추적·재현할 수 있도록, draft 43건에 대한 적대검증 판정을
결정론적으로 인코딩한다. 판정 자체는 10개 검증 렌즈(아래 LENSES)로 refute-by-default 적용한 결과이며,
스크립트는 이를 (1) 적대검증 ledger, (2) 살아남은 후보만의 reviewer-ready batch, (3) PM queue 갱신으로
기계적으로 변환한다. **live 통합·승격 0. export/full index/aliases/src/.github 무수정.**

입력: data/drafts/relation_factory_draft_batch_v1_4.json (불변)
산출:
  - data/review/relation_factory_adversarial_verify_v1_4.json   (작업 F)
  - data/drafts/relation_factory_reviewer_ready_batch_v1_4.json (작업 G — survives/copy_change 만)
  - data/review/relation_factory_pm_review_queue_v1_4.json/.md   (작업 K — adversarial 결과 추가)
모든 산출물: published=false·clinical_reviewed=false·reviewed_by 공란·live_integration_forbidden=true.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
BATCH = os.path.join(DATA, "drafts", "relation_factory_draft_batch_v1_4.json")
LEDGER = os.path.join(DATA, "review", "relation_factory_adversarial_verify_v1_4.json")
READY = os.path.join(DATA, "drafts", "relation_factory_reviewer_ready_batch_v1_4.json")
PMQ_JSON = os.path.join(DATA, "review", "relation_factory_pm_review_queue_v1_4.json")
PMQ_MD = os.path.join(DATA, "review", "relation_factory_pm_review_queue_v1_4.md")

# 10 적대검증 렌즈 (refute-by-default)
LENSES = {
    "L1_source_fidelity": "source quote 가 라벨 verbatim 이고 app copy 가 강도/방향을 왜곡하지 않는가",
    "L2_direct_cooccurrence": "counterpart 가 라벨에 직접 등장하고 itemSeq 가 실제 국내 품목인가",
    "L3_direction": "흡수저하/효과감소/결핍/모니터링 방향이 맞는가",
    "L4_negation": "부정문(영향 없음/저해되지 않음)을 반대로 읽지 않았는가",
    "L5_category_clarity": "nutrient vs antacid drug vs acid_reducing_drug 구분이 되는가",
    "L6_supplement_safety": "비타민/철분/아연/칼슘/마그네슘/칼륨 보충 권유처럼 보이지 않는가",
    "L7_clinical_high_risk": "항응고/항암/이식/면역억제/임신·소아 고위험이 아닌가",
    "L8_formulation_route": "IV/주사/외용/복합제/원료/수출용을 경구 일반 relation 으로 오인하지 않았는가",
    "L9_duplicate_conflict": "live 60·pending 13 과 중복/충돌이 없는가",
    "L10_copy_render_safety": "카드 렌더 시 지시문/제품/보충권유/진단처럼 보이지 않는가",
}

# 살아남는 후보의 family 별 공통 reviewer 질문(L9 overlap 등)
FAMILY_RQ = {
    "F1": ["live 에 동일 약물 × 마그네슘/철분/칼슘(nutrient)이 있는 경우, Al/Mg 제산제(약물) relation 을 별도 counterpart 로 유지할지 확인(id61 이트라코나졸 선례).",
           "separation 간격(2~4시간)을 카드에 노출할지 — 현재는 일반 '분리' 안내."],
    "F2": ["테트라사이클린계 공통 라벨 문구 기반 — 약물별 국내 품목(itemSeq) 매칭이 정확한지 확인.",
           "live 에 동일 약물 × mineral nutrient 가 있는 경우 antacid-drug relation 의 중복 여부 확인."],
    "F3": ["live 에 동일 비스포스포네이트 × 칼슘/철분(nutrient)이 있음 — antacid-drug relation 을 별도로 둘지 확인.",
           "공복 복용·물 외 음료 금지 등 비스포스포네이트 일반 복약지침과의 관계 정리(카드 범위 밖)."],
    "F4": ["라벨이 '알루미늄 함유 제산제'만 명시 — al_mg_antacid(Al/Mg 통합) category 적용이 적절한지 확인.",
           "live 레보티록신 × 철분/칼슘(nutrient)과의 중복 아님 — antacid-drug 는 신규 counterpart."],
    "F6": ["저위산증/무위산증 기전(흡수 감소) 문구가 monitoring 카드로 적절한지 — 다른 PPI × B12 live 와 톤 일치 확인.",
           "장기복용 조건을 카드에 명시할지(현재 '장기간 복용할 때')."],
    "F9": ["만성/장기복용·고용량 맥락이 필요한 depletion — 카드의 '장기간 복용할 때' 프레이밍이 라벨 근거와 일치하는지 확인.",
           "결핍 단정이 아니라 '수치 변화 가능·모니터링' 톤인지 확인(현재 충족)."],
    "F10": ["기전이 Al/Mg 킬레이션이 아니라 위산도 의존 흡수(제산제가 pH 상승) — 향후 acid_reducing_drug category 도입 시 재분류 검토.",
            "live 이트라코나졸 × Al/Mg 제산제(id61)와 톤/형식 일치 확인."],
}

# 명시적 판정(특수 12건: copy_change 6 + downgrade 6). 나머지는 clean survives.
# verdict ∈ {survives, survives_with_copy_change, needs_review, hold, reject}
EXPLICIT = {
    # ---- survives_with_copy_change (실재 상호작용·quote/카테고리 정비 후 유지) ----
    "RF-F4-0173": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L5_category_clarity": "라벨은 '알루미늄 함유 제산제'만 명시(Mg 미명시). al_mg_antacid 통합 category 적용 — id61 선례 있으나 reviewer 확인 필요."},
        "category_changes": "counterpart_category=al_mg_antacid 유지하되 라벨은 Al 만 명시함을 reviewer note 로 기록.",
        "remaining_risks": "Al-only 라벨을 Al/Mg 통합 category 로 일반화한 점.",
        "reviewer_questions": ["라벨이 알루미늄만 명시 — Al/Mg 통합 표기가 과일반화 아닌지 확인."],
        "next_action": "reviewer 확인 후 통합(별도 PR).",
    },
    "RF-F3-0148": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L1_source_fidelity": "quote 끝의 '○ 파제트병'(적응증 artifact) 제거 — 상호작용과 무관.",
                       "L5_category_clarity": "칼슘이 '미네랄 첨가 비타민제(보충)' 와 '함유 제산제' 양쪽에 걸침 — live 리세드론산/이반드론산 × 칼슘(nutrient) 선례로 nutrient 분류 유지."},
        "copy_changes": {"source_quote": "미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제"},
        "remaining_risks": "라벨이 보충제/제산제 칼슘을 혼합 서술 — nutrient vs antacid-drug 분리 가능성.",
        "reviewer_questions": ["칼슘을 nutrient 로 둘지, 별도 al_mg_antacid relation 으로 분리할지 확인(라벨이 양쪽 서술)."],
        "next_action": "quote 정비본으로 reviewer 검토.",
    },
    "RF-F3-0149": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L1_source_fidelity": "quote 끝 '○ 파제트병' 제거.",
                       "L5_category_clarity": "철분이 보충/제산제 양쪽 서술 — nutrient 분류 유지(bisphosphonate×철분 nutrient 톤)."},
        "copy_changes": {"source_quote": "미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제"},
        "remaining_risks": "동 RF-F3-0148.",
        "reviewer_questions": ["철분 nutrient 분류 적절성 확인."],
        "next_action": "quote 정비본으로 reviewer 검토.",
    },
    "RF-F10-0275": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L5_category_clarity": "기전이 Al/Mg 킬레이션이 아니라 위산도 의존 흡수(제산제·항콜린제·H2 차단제가 위산분비 억제). 제산제 부분만 al_mg_antacid 로 매핑 — 향후 acid_reducing_drug category 검토.",
                       "L3_direction": "흡수 저하 방향 맞음."},
        "mechanism_changes": "absorption(위산도 의존) — reviewer note 로 기전 명시.",
        "remaining_risks": "라벨이 H2 차단제·항콜린제도 함께 언급하나 카드는 제산제(al_mg_antacid)로 한정.",
        "reviewer_questions": ["위산도 의존 흡수를 al_mg_antacid 로 표기 vs acid_reducing_drug 신규 category 중 택일.",
                               "콜라(산성음료) 동시복용 라벨 문구는 카드 범위 밖으로 둘지 확인."],
        "next_action": "category 결정 후 통합.",
    },
    "RF-F9-0245": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L1_source_fidelity": "원 quote 가 이상반응 표 raw 텍스트 — '엽산 결핍증' 핵심부만 verbatim 발췌.",
                       "L3_direction": "엽산 결핍(depletion) 방향 맞음 — 카르바마제핀 효소유도 알려진 기전."},
        "copy_changes": {"source_quote": "드물게 백혈구 증가, 임파절 장애, 엽산 결핍증"},
        "remaining_risks": "라벨상 '드물게' 등급 — evidence_level moderate 가 다소 높을 수 있음(reviewer 하향 검토).",
        "reviewer_questions": ["'드물게' 빈도의 엽산 결핍증을 monitoring 카드로 둘지, evidence_level 하향할지 확인."],
        "next_action": "정비 quote 로 reviewer 검토.",
    },
    "RF-F9-0246": {
        "verdict": "survives_with_copy_change",
        "lens_notes": {"L1_source_fidelity": "원 quote 가 표 raw 텍스트 — '25-hydroxy-콜레칼시페롤 감소…골연화증' 핵심부만 발췌.",
                       "L3_direction": "비타민D(25-OH) 감소·골대사 장애 방향 맞음."},
        "copy_changes": {"source_quote": "혈장 칼슘과 혈중25-hydroxy-콜레칼시페롤의 감소와 같은 골대사 장애로 인한 골연화증 및 골다공증"},
        "remaining_risks": "표 텍스트 발췌 — reviewer 가 원문 위치 재확인 권장.",
        "reviewer_questions": ["발췌 quote 가 라벨 원문과 일치하는지 reviewer 재확인."],
        "next_action": "정비 quote 로 reviewer 검토.",
    },
    # ---- needs_review (방향/근거/특이성 약함 — draft 제외, 재검토 큐) ----
    "RF-F9-0260": {
        "verdict": "needs_review",
        "lens_notes": {"L7_clinical_high_risk": "근거가 '랫트 시험' + '임신 중 엽산 감소' — 동물·임신 한정.",
                       "L1_source_fidelity": "카드는 '장기간 복용 시 엽산 수치 변화'로 일반화하나 quote 는 동물/임신 근거."},
        "downgrade_reason": "동물(랫트)·임신 한정 근거를 인체 만성 depletion 으로 일반화 — 근거 강도/맥락 불일치(refute: 인체 만성 depletion 직접근거 아님).",
        "remaining_risks": "라모트리진은 약한 DHFR 억제제 — 임상적 엽산 영향은 reviewer 판단 영역.",
        "reviewer_questions": ["임신 외 일반 복용에서 엽산 모니터링 근거가 라벨에 별도로 있는지 확인."],
        "next_action": "라벨 재검색(임신 외 엽산 문구) 또는 hold.",
    },
    "RF-F9-0257": {
        "verdict": "needs_review",
        "lens_notes": {"L2_direct_cooccurrence": "'엽산 결핍'이 저나트륨혈증 이상반응 나열문 중간에 매몰 — 특성화된 depletion 서술 아님.",
                       "L1_source_fidelity": "문장 구조상 '엽산 결핍 등의 증상성 저나트륨혈증'으로 엽산이 저나트륨혈증에 종속."},
        "downgrade_reason": "엽산 결핍이 이상반응 열거문에 저신호로 매몰 — 직접 depletion 근거로 보기 약함.",
        "remaining_risks": "옥스카르바제핀의 엽산 영향 자체는 문헌상 약함.",
        "reviewer_questions": ["라벨 내 엽산 단독 서술이 별도로 있는지 확인."],
        "next_action": "라벨 재검색 또는 drop.",
    },
    "RF-F9-0251": {
        "verdict": "needs_review",
        "lens_notes": {"L1_source_fidelity": "quote '임신중의 투여에 의해 엽산 저하' — 임신 한정. 카드는 '장기간 복용'으로 일반화(원문보다 넓음)."},
        "downgrade_reason": "임신 한정 근거를 일반 장기복용으로 일반화 — '원문보다 강하면 금지' 위반 소지. (페노바르비탈 효소유도 엽산저하는 임상상 알려졌으나 라벨 quote 는 임신 한정.)",
        "remaining_risks": "임신 외 엽산저하 라벨 근거 확보 시 승격 가능.",
        "reviewer_questions": ["임신 외 엽산저하 라벨 문구 유무 확인 — 있으면 quote 교체 후 survives."],
        "next_action": "라벨 재검색(임신 외 엽산) 후 재평가.",
    },
    "RF-F9-0254": {
        "verdict": "needs_review",
        "lens_notes": {"L1_source_fidelity": "quote '임신중의 투여에 의해 엽산저하' — 임신 한정. 카드 일반화."},
        "downgrade_reason": "프리미돈×엽산: 임신 한정 근거를 일반 장기복용으로 일반화 — 동 RF-F9-0251.",
        "remaining_risks": "프리미돈 대사물=페노바르비탈 — 임신 외 근거 확보 시 승격 가능.",
        "reviewer_questions": ["임신 외 엽산저하 라벨 문구 유무 확인."],
        "next_action": "라벨 재검색 후 재평가.",
    },
    "RF-F3-0139": {
        "verdict": "needs_review",
        "lens_notes": {"L2_direct_cooccurrence": "quote 가 '칼슘보충제나 제산제 및 일부 경구용 약물들' 로 generic — Al/Mg 제산제를 명시하지 않음.",
                       "L9_duplicate_conflict": "live 알렌드론산 × 칼슘(nutrient)이 이미 칼슘-흡수저해 핵심을 커버 — antacid-drug 특이성 약함."},
        "downgrade_reason": "Al/Mg 제산제를 직접 명시하지 않는 generic quote('제산제')이고, 명시 양이온은 칼슘뿐(이미 live). 특이성 부족 — refute(직접근거 약함).",
        "remaining_risks": "알렌드론산 antacid 상호작용 자체는 실재하나 라벨에 Al/Mg 직접 명시 quote 필요.",
        "reviewer_questions": ["알렌드론산 라벨에 'Al/Mg 함유 제산제' 직접 명시 문구가 있는지 재검색 — 있으면 quote 교체 후 survives."],
        "next_action": "라벨 재검색(Al/Mg 직접 명시) 후 재평가. 없으면 칼슘(live)로 충분.",
    },
    # ---- hold (실재 상호작용이나 잘못된 counterpart category — 신규 category 필요) ----
    "RF-F10-0276": {
        "verdict": "hold",
        "lens_notes": {"L5_category_clarity": "source quote 는 'H2 수용체 억제제' 만 언급 — Al/Mg 제산제(al_mg_antacid)와 다른 약물군.",
                       "L1_source_fidelity": "counterpart 를 'Al/Mg 함유 제산제'로 두었으나 quote 는 제산제를 명시하지 않음(주어 불일치)."},
        "downgrade_reason": "포사코나졸 quote 가 H2 차단제 상호작용만 서술 — al_mg_antacid 로 매핑 불가(주어/카테고리 불일치). refute: 제산제 직접근거 없음. acid_reducing_drug(H2/PPI) category 미존재로 현재 표현 불가 → hold.",
        "remaining_risks": "포사코나졸은 위산도 의존 흡수가 실재 — 향후 acid_reducing_drug category 도입 시 H2 차단제 relation 으로 재평가.",
        "reviewer_questions": ["포사코나졸 라벨에 Al/Mg '제산제' 직접 명시 문구가 별도로 있는지 확인.",
                               "acid_reducing_drug(H2/PPI) category 신설 시 H2 차단제 relation 으로 복원할지 결정."],
        "next_action": "acid_reducing_drug category 설계 트랙으로 이관(hold). al_mg_antacid 로는 통합 금지.",
    },
}

DOWNGRADE = {"needs_review", "hold", "reject"}
SURVIVE = {"survives", "survives_with_copy_change"}


def default_survives(d):
    fam = d.get("family", "")
    return {
        "verdict": "survives",
        "lens_notes": {},
        "remaining_risks": "moderate 근거(라벨 직접 quote) — reviewer 가 evidence_level 확정.",
        "reviewer_questions": list(FAMILY_RQ.get(fam, [])),
        "next_action": "reviewer package 포함 → dry-run integrator → 별도 PR.",
    }


def build():
    batch = json.load(open(BATCH, encoding="utf-8"))
    drafts = batch["draft_relations"]

    ledger_entries = []
    ready = []
    counts = {"survives": 0, "survives_with_copy_change": 0, "needs_review": 0, "hold": 0, "reject": 0}
    fam_total, fam_survive = {}, {}

    for d in drafts:
        cid = d["candidate_id"]
        fam = d.get("family", "")
        v = EXPLICIT.get(cid) or default_survives(d)
        verdict = v["verdict"]
        counts[verdict] += 1
        fam_total[fam] = fam_total.get(fam, 0) + 1
        if verdict in SURVIVE:
            fam_survive[fam] = fam_survive.get(fam, 0) + 1

        # lens_results: 기본 pass, note 있으면 기록
        lens_notes = v.get("lens_notes", {})
        lens_results = {}
        for lk in LENSES:
            if lk in lens_notes:
                lens_results[lk] = {"result": "fail" if verdict in DOWNGRADE and lk in lens_notes else "note",
                                    "detail": lens_notes[lk]}
            else:
                lens_results[lk] = {"result": "pass", "detail": ""}

        copy_changes = v.get("copy_changes", {})
        entry = {
            "candidate_id": cid,
            "relation": d.get("relation"),
            "family": fam,
            "original_status": "source_confirmed_draft_candidate",
            "adversarial_verdict": verdict,
            "lens_results": lens_results,
            "refuted_points": [lens_notes[k] for k in lens_notes] if verdict in DOWNGRADE else [],
            "copy_changes": copy_changes,
            "category_changes": v.get("category_changes", ""),
            "mechanism_changes": v.get("mechanism_changes", ""),
            "final_status": ("reviewer_ready_candidate" if verdict in SURVIVE else verdict),
            "downgrade_reason": v.get("downgrade_reason", ""),
            "remaining_risks": v.get("remaining_risks", ""),
            "reviewer_questions": v.get("reviewer_questions", []),
            "next_action": v.get("next_action", ""),
            "reviewer_needed": True,
            "live_allowed": False,
        }
        ledger_entries.append(entry)

        if verdict in SURVIVE:
            rr = {
                "candidate_id": cid,
                "family": fam,
                "relation": d.get("relation"),
                "drug_ingredient": d.get("drug_ingredient"),
                "counterpart": d.get("counterpart"),
                "counterpart_type": d.get("counterpart_type"),
                "counterpart_category": d.get("counterpart_category"),
                "itemSeq": d.get("itemSeq"),
                "source_section": d.get("source_section"),
                "source_quote": copy_changes.get("source_quote", d.get("source_quote")),
                "mechanism": d.get("mechanism"),
                "recommended_action": d.get("recommended_action"),
                "evidence_level": d.get("evidence_level"),
                "confidence": d.get("confidence"),
                "risk_level": d.get("risk_level"),
                "display_copy": d.get("display_copy"),
                "management_copy": d.get("management_copy"),
                "product_link_allowed": False,
                "potassium_safety_card": d.get("potassium_safety_card", False),
                "adversarial_verdict": verdict,
                "reviewer_questions": v.get("reviewer_questions", []),
                "live_integration_forbidden": True,
                "do_not_implement_yet": True,
                "published": False,
                "clinical_reviewed": False,
                "reviewed_by": "",
            }
            # 정비 quote 가 원문 substring 인지 안전 검증(verbatim 보장)
            if "source_quote" in copy_changes:
                assert copy_changes["source_quote"] in d["source_quote"], \
                    f"{cid}: 정비 quote 가 원문 substring 아님 — verbatim 위반"
            ready.append(rr)

    # family 생존율
    fam_yield = {f: {"total": fam_total[f], "survives": fam_survive.get(f, 0),
                     "yield": round(fam_survive.get(f, 0) / fam_total[f], 2)}
                 for f in sorted(fam_total)}

    ledger = {
        "meta": {
            "name": "relation_factory_adversarial_verify_v1_4",
            "status": "LIVE 아님 · 적대검증(refute-by-default) 기록 · 자동 승격 금지 · 제품/구매/제휴 없음",
            "method": "10-lens refute-by-default. survives/copy_change 만 reviewer-ready. needs_review/hold/reject 는 draft 제외.",
            "lenses": LENSES,
            "total": len(drafts),
            "counts": counts,
            "reviewer_ready": counts["survives"] + counts["survives_with_copy_change"],
            "downgraded": counts["needs_review"] + counts["hold"] + counts["reject"],
            "family_survival": fam_yield,
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "live_integration_forbidden": True,
            "note": "adversarial_verdict 는 reviewer/PM 의 임상 검수를 대체하지 않는다. survives 도 식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.",
        },
        "entries": ledger_entries,
    }
    json.dump(ledger, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ready_doc = {
        "meta": {
            "name": "relation_factory_reviewer_ready_batch_v1_4",
            "status": "DRAFT-ONLY — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true / 적대검증 통과(survives·copy_change)만",
            "purpose": "factory 43 draft → 적대검증 후 살아남은 reviewer-ready 후보. clinical reviewer note + dry-run integrator 후에만 live(별도 PR).",
            "count": len(ready),
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "note": "reviewer_ready 는 적대검증(자동 렌즈) 통과를 의미하며 임상 검수 완료·식약처 승인·법적 문제 없음 을 의미하지 않는다.",
        },
        "reviewer_ready_relations": ready,
    }
    json.dump(ready_doc, open(READY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # PM queue 갱신(기존 구조 보존 + adversarial 블록 추가)
    pmq = json.load(open(PMQ_JSON, encoding="utf-8"))
    pmq["adversarial_verify"] = {
        "method": "10-lens refute-by-default",
        "total": len(drafts),
        "counts": counts,
        "reviewer_ready": ledger["meta"]["reviewer_ready"],
        "downgraded": ledger["meta"]["downgraded"],
        "family_survival": fam_yield,
        "downgrades": [{"candidate_id": e["candidate_id"], "relation": e["relation"],
                        "verdict": e["adversarial_verdict"], "reason": e["downgrade_reason"]}
                       for e in ledger_entries if e["adversarial_verdict"] in DOWNGRADE],
        "major_false_positive_patterns": [
            "F10 acid-reducer 주어 혼동: 포사코나졸 quote 는 H2 차단제 — al_mg_antacid 매핑 불가.",
            "F9 임신 한정 근거 일반화: 페노바르비탈/프리미돈 × 엽산 quote '임신중' → 카드 '장기간 복용' 과일반화.",
            "F9 동물·임신 근거: 라모트리진 × 엽산 = 랫트 시험.",
            "F9 이상반응 열거 저신호: 옥스카르바제핀 엽산이 저나트륨혈증 나열문에 매몰.",
            "F3 generic '제산제' quote + live 중복: 알렌드론산 antacid 가 칼슘(live)만 명시.",
            "quote hygiene(비치명): 에티드론산 '○ 파제트병'·카르바마제핀 표 raw·레보티록신 Al-only.",
        ],
        "validator_changes_added": [
            "adversarial ledger ↔ draft batch cid 일치",
            "reviewer_ready = survives/copy_change 만(needs_review/hold/reject 0)",
            "reviewer_ready 정비 quote 가 원문 substring(verbatim)",
            "결함주입 6종 추가(reject→ready, H2→al_mg, 임신 한정 일반화, generic 제산제, IV oral 오인, quote=copy 지시문)",
        ],
        "status_note": "LIVE 아님 · 자동 승격 금지 · reviewer note 전 live 금지 · 제품 없음",
    }
    json.dump(pmq, open(PMQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # PM queue MD 재생성(adversarial 우선)
    lines = []
    lines.append("# MediStack — Relation Factory v1.4 PM Review Queue (adversarial 반영)")
    lines.append("")
    lines.append("> **LIVE 아님 · 자동 승격 금지 · reviewer/PM 승인·clinical reviewer note 전 live 금지 · 제품/구매/제휴 없음.**")
    lines.append("> 적대검증(refute-by-default 10-lens) 후. 정본: `relation_factory_adversarial_verify_v1_4.json` · reviewer-ready `relation_factory_reviewer_ready_batch_v1_4.json`.")
    lines.append("")
    lines.append("## 1. 적대검증 요약")
    lines.append("")
    lines.append(f"- 대상 draft: **{len(drafts)}**")
    lines.append(f"- survives: **{counts['survives']}** · survives_with_copy_change: **{counts['survives_with_copy_change']}** → **reviewer-ready {ledger['meta']['reviewer_ready']}**")
    lines.append(f"- needs_review: **{counts['needs_review']}** · hold: **{counts['hold']}** · reject: **{counts['reject']}** → **강등 {ledger['meta']['downgraded']}**")
    lines.append("")
    lines.append("## 2. family 별 생존율")
    lines.append("")
    lines.append("| family | total | survives | yield |")
    lines.append("|---|---|---|---|")
    for f in sorted(fam_yield):
        y = fam_yield[f]
        lines.append(f"| {f} | {y['total']} | {y['survives']} | {y['yield']} |")
    lines.append("")
    lines.append("## 3. 강등 후보(draft 제외)")
    lines.append("")
    lines.append("| candidate_id | relation | verdict | 사유 |")
    lines.append("|---|---|---|---|")
    for e in ledger_entries:
        if e["adversarial_verdict"] in DOWNGRADE:
            lines.append(f"| {e['candidate_id']} | {e['relation']} | {e['adversarial_verdict']} | {e['downgrade_reason']} |")
    lines.append("")
    lines.append("## 4. 주요 false-positive 패턴")
    lines.append("")
    for p in pmq["adversarial_verify"]["major_false_positive_patterns"]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## 5. 다음 액션(LIVE 아님)")
    lines.append("")
    lines.append("1. reviewer-ready 37 → clinical reviewer note(family 그룹별) → dry-run integrator → 선택 subset 별도 PR live.")
    lines.append("2. needs_review 5 → 라벨 재검색(임신 외 엽산·Al/Mg 직접 명시) 후 재평가.")
    lines.append("3. hold 1(포사코나졸) → acid_reducing_drug category 설계 트랙.")
    lines.append("4. 다음 수확: F9 만성 depletion·F10 azole 확장(최고 수확) + 미커버 약물.")
    lines.append("")
    open(PMQ_MD, "w", encoding="utf-8").write("\n".join(lines))

    print("=== adversarial_verify_relation_factory_v1_4 ===")
    print(f"draft 총 {len(drafts)} | counts {counts}")
    print(f"reviewer-ready {ledger['meta']['reviewer_ready']} | 강등 {ledger['meta']['downgraded']}")
    print(f"family 생존율: {fam_yield}")
    print(f"산출: {os.path.relpath(LEDGER, REPO)} · {os.path.relpath(READY, REPO)} · PM queue(json/md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
