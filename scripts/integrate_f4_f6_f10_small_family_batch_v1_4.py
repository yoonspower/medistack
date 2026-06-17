#!/usr/bin/env python3
"""
integrate_f4_f6_f10_small_family_batch_v1_4.py
MediStack — Relation Factory v1.4 **F4/F6/F10 small-family bundle** live 통합 **준비/드라이런** 스크립트.
integrate_f9_chronic_depletion_batch_v1_4.py / integrate_f3_bisphosphonate_batch_v1_4.py 패턴 승계
(reviewer-ready batch → small-family bundle + family-specific 재검증(작업 B/C)).

small-family bundle = global plan 의 remaining unpackaged 3 family(각 reviewer-ready 1건):
  RF-F4-0173   레보티록신 × Al/Mg 함유 제산제(약물)   absorption/separation (al_mg_antacid)  [흡수]
  RF-F6-0201   에스오메프라졸 × 비타민B12              depletion/monitoring  (nutrient)       [결핍]
  RF-F10-0275  케토코나졸 × Al/Mg 함유 제산제(약물)    absorption/separation (al_mg_antacid)  [흡수]
두 렌더 경로 모두 live 선례 존재 → 선행조건 0:
  absorption/separation·al_mg_antacid = 이트라코나졸×Al/Mg제산제(id61, 위산도 의존 흡수·display 가 콜라/2시간 dosing 제거).
  depletion/monitoring·B12 = 메트포르민×B12(id12) + PPI×B12 5건(오메프라졸 id13·라베프라졸 32·판토 34·란소 36·덱스란소 38).

⚠️⚠️ **작업 B/C(F4/F6/F10 family-specific 재검증, reverify(), refute-by-default) 결과 — 적대검증과 다름**:
  survives 0 · survives_with_copy_change 2 · **needs_review 1** · hold 0 · reject 0 → **통합 가능 2**(F4 1 + F6 1 + F10 0).
  ── 헤드라인 발견 ①(케토코나졸×제산제 0275 강등: route/availability mismatch) ──
    소스(더마졸정 **수출용**, itemSeq 199101243)는 oral tablet 이나, **국내 색인 케토코나졸 10품목 전부 외용(액/크림)**.
    경구 흡수 의존(제산제→위산분비↓→흡수↓) relation 을 ingredient(케토코나졸)에 붙이면 **외용 제품에 경구 상호작용 카드 오부착**.
    광역 10-lens 의 L8(formulation/route)은 *소스가 tablet* 이라 pass 했으나, family 재검증의 L6_route_domestic_availability
    (full index 형태 분류)는 국내 oral 제품 0 → **fail → needs_review**. (live 선례 id61 이트라코나졸은 *국내* 제품 사용.)
    → reviewer 가 (a)국내 oral 케토코나졸 존재 여부 (b)formulation-scoping(경구 한정) 결정 후에만 통합. 수출용 source 도 reviewer 확인.
  ── 헤드라인 발견 ②(레보티록신×제산제 0173 copy_change: aluminum-only) ──
    라벨('씬지로이드정', itemSeq 197400278)은 '**알루미늄** 함유 제산제'만 명시(Mg 미명시). al_mg_antacid category/display 는
    Mg 도 포함 → display '마그네슘' 단정은 **source 보다 강함**. → copy_change(display_reframe): counterpart/display 를
    '알루미늄 함유 제산제'로 좁히고 Mg 비단정. (live id61 도 수산화알루미늄→'Al/Mg' 일반화 — 동일 latent 이슈를 reviewer 에 surface.)
  ── 헤드라인 발견 ③(에스오메프라졸×B12 0201 copy_change: live PPI×B12 톤 정합) ──
    에스오메프라졸은 오메프라졸(id13 live)의 S-거울상 → PPI×B12 5건 live 계열에 합류. display 를 draft('수치 변화')에서
    **live PPI×B12 표준 템플릿**('비타민 B12 상태에 영향이 있을 수 있다는 보고가 있어, 상태 확인이 필요할 수 있습니다')로 reframe
    (장기복용+상태확인 조건 보존). 소스는 복합제(낙소졸정=나프록센+에스오메프라졸·quote 가 에스오메프라졸 명시) → reviewer note.

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만 수행
(별도 PM 승인 + clinical reviewer 전까지 절대 금지·본 세션 호출 안 함).
  dry-run = 라이브/보호 데이터 **무수정** + 예상 산출물 기록:
    data/review/f4_f6_f10_small_family_inventory_v1_4.json    (작업 B/C — 3 reviewer-ready 감사 + family 재검증 렌즈 + F10 family context)
    data/review/f4_f6_f10_small_family_live_dryrun_v1_4.json  (작업 E/G — scope별 예상 count/id + 가드 + 충돌 + v0.2 증거)
    data/review/f4_f6_f10_small_family_index_impact_v1_4.json (작업 G — full index/aliases 영향)

scope(작업 D grouping):
  --scope integrable (기본) survives+copy_change = 2건 — 60→62
  --scope all        reviewer-ready 3건(F10 0275 needs_review 는 build_subset 에서 STOP)
  --scope family:F4  레보티록신 1건 — 60→61
  --scope family:F6  에스오메프라졸 1건 — 60→61
  --scope family:F10 케토코나졸 — needs_review(통합 0·STOP)
  --candidate-ids A,B,...  명시 후보(통합 가능만; needs_review/hold/reject 는 build_subset 에서 STOP)
  --base-count N     scenario 표시용 baseline override(id 는 항상 runtime max+1)
  ⚠️ needs_review 1건(0275)은 scope 로 요청해도 통합 거부(STOP). reviewer route/availability 확정 후 별도.

live 통합 선행조건: **없음(0)**. 두 렌더 경로(id61 absorption/al_mg_antacid · id12/id13 depletion/B12) 모두 live — src 무수정.
  full index: 통합 약물(레보티록신=relation_card 17·에스오메프라졸=색인 0(복합제만)) → relation-only 통합 자동 flip 0
  (relation export 와 decoupled·1168/16412 불변). 케토코나졸은 needs_review 라 미통합.

사용:
  python3 scripts/integrate_f4_f6_f10_small_family_batch_v1_4.py                                # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_f4_f6_f10_small_family_batch_v1_4.py --scope family:F6              # dry-run(특정 family)
  python3 scripts/integrate_f4_f6_f10_small_family_batch_v1_4.py --pm-approved --reviewer-note X  # live(별도 PM·reviewer 후·본 세션 금지)
종료코드: 0 DONE/skip/dry, 1 STOP(가드/노트 위반).
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
REVIEWER_READY = os.path.join(DATA, "drafts", "relation_factory_reviewer_ready_batch_v1_4.json")
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
INVENTORY_ARTIFACT = os.path.join(DATA, "review", "f4_f6_f10_small_family_inventory_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "f4_f6_f10_small_family_live_dryrun_v1_4.json")
INDEX_IMPACT_ARTIFACT = os.path.join(DATA, "review", "f4_f6_f10_small_family_index_impact_v1_4.json")

BASELINE_RELATIONS = 60      # F1/F2/F3/F9 등 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-17"  # source-check + 적대검증 + F4/F6/F10 family 재검증 확인일
BUNDLE_FAMILIES = ("F4", "F6", "F10")
BUNDLE_REVIEWER_READY_COUNT = 3   # 적대검증 reviewer-ready(각 family 1)
BUNDLE_SURVIVES_COUNT = 0         # 작업 C 재검증 survives(copy_change 아닌 그대로)
BUNDLE_COPY_CHANGE_COUNT = 2      # survives_with_copy_change(0173/0201)
BUNDLE_NEEDS_REVIEW_COUNT = 1     # needs_review(0275 route/availability)
BUNDLE_INTEGRABLE_COUNT = 2       # survives + copy_change (F4 1 + F6 1 + F10 0)
TRUE_BASE_F1F2F3F9 = 91           # F1 18 + F2 5 + F3 1 + F9 7 모두 live 가정 baseline(조건부 시나리오·60+18+5+1+7=91).

FAMILY_OF = {"RF-F4-0173": "F4", "RF-F6-0201": "F6", "RF-F10-0275": "F10"}
# source-check 확정 품목명(reviewer 가시성용·inventory 기록).
SOURCE_PRODUCTS = {
    "RF-F4-0173": "씬지로이드정0.1밀리그램(레보티록신나트륨수화물)",
    "RF-F6-0201": "낙소졸정500/20밀리그램(나프록센,에스오메프라졸)",   # 복합제(나프록센+에스오메프라졸) — quote 가 에스오메프라졸 명시
    "RF-F10-0275": "더마졸정(케토코나졸)(수출용)",                      # 수출용(export-only) oral tablet
}
# F10 family context(reviewer-ready 3 밖 · 적대검증 단계에서 이미 분류 — 완결성 위해 기록).
F10_FAMILY_CONTEXT = {
    "RF-F10-0276": {"relation": "포사코나졸 × Al/Mg 함유 제산제(약물)", "status": "hold",
                    "reason": "소스 quote 가 'H2 수용체 억제제'만 언급(Al/Mg 제산제 미명시·주어 불일치) → al_mg_antacid 매핑 불가. "
                              "acid_reducing_drug(H2/PPI) category 설계 트랙으로 이관(hold)."},
    "RF-F10-0277": {"relation": "이트라코나졸 × Al/Mg 함유 제산제(약물)", "status": "reject_duplicate_live",
                    "reason": "이미 live(id61). duplicate_live → REJECT_PRECHECK(중복 생성 금지)."},
}

def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# draft_to_live / guard_projected / run_v0_2 / _sim_with / DRAFT_ONLY / safety scanner 재사용.
integ = _load("integ", "integrate_theme_map_draft_batch_v1_3.py")
prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = ["복용하세요", "복용하지 마", "복용하지마", "드세요", "드십시오", "끊으세요",
                  "중단하세요", "복용을 중단", "보충하세요", "반드시 "]
TEST_TREAT_DIRECTIVE = ["검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요", "투여받으세요", "처방하세요"]
ANTICOAG_TERMS = ["와파린", "항응고", "비타민 K", "비타민K", "INR", "프로트롬빈"]
# DISPLAY 노출 금지 — 구체 시간·용량·복용 지시(0275 quote 의 '2시간'/'콜라' 등은 display 비노출).
DOSING_DETAIL_TERMS = ["2시간", "콜라", "산성음료", "1시간", "30분", "복용 2시간", "투여 2시간"]
# DISPLAY 노출 금지 — 소아/임신/골/치아 알람어(B12/제산제 카드 무관·방어적).
PEDIATRIC_BONE_TERMS = ["소아", "임신", "수유", "치아", "구루병", "골연화증", "골다공증", "골절", "치조골"]
# 상담 톤(L13) — al_mg_antacid 카드(id61)는 '약사 또는 의사', B12 depletion 카드(id12/id13)는 '복약 상담/정기 진료'.
CONSULT_MARKERS = ("약사 또는 의사", "복약 상담", "정기 진료", "진료 시", "상담")

# counterpart 분류
NUTRIENT_COUNTERPARTS = {"비타민B12"}                       # F6
ANTACID_COUNTERPARTS = {"Al/Mg 함유 제산제(약물)", "알루미늄 함유 제산제(약물)"}  # F4/F10 (al_mg_antacid)
# 라벨 quote 직접언급 토큰
ANTACID_QUOTE_TOKENS = ("제산제", "알루미늄", "마그네슘", "수산화알루미늄", "위산분비", "위산도")
B12_QUOTE_TOKENS = ("비타민 B12", "비타민B12", "B12", "코발라민", "시아노코발라민")
# 흡수/방향 동사
_ABSORB_DIR = ("지연", "감소", "저하", "줄어", "낮")
_ACID_DEPEND = ("위산분비", "위산도")          # 위산도 의존 흡수(id61 동형) — absorption 근거로 인정
_CHRONIC_WORDS = ("연용", "장기", "만성", "지속", "오래", "장기간")

# ── 작업 C copy_change(F4/F6/F10 family 재검증) — multi-field display_reframe ──
# integrity: 각 field 의 batch 원문 == original. cleaned 적용. (live 무수정 — projected 에만 반영.)
_F4_DISP_O = ("이 약은 Al/Mg 함유 제산제(약물)과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 "
              "있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요.")
_F4_DISP_C = ("이 약은 알루미늄 함유 제산제(약물)와 함께 복용할 때 약물 흡수가 지연되거나 감소될 수 있다는 허가사항 문구가 "
              "있습니다. 함께 복용해야 하는 경우 복용 시점 분리에 대해 약사 또는 의사에게 확인하세요.")
_F4_MNG_O = "Al/Mg 함유 제산제(약물)과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
_F4_MNG_C = "알루미늄 함유 제산제(약물)와는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
_F6_DISP_O = ("이 약을 장기간 복용할 때 비타민B12 수치 변화와 관련된 허가사항 문구가 있습니다. "
              "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
_F6_DISP_C = ("에스오메프라졸을(를) 장기간 복용하는 경우 비타민 B12 상태에 영향이 있을 수 있다는 보고가 있어, "
              "상태 확인이 필요할 수 있습니다.")
_F6_MNG_O = "정기적인 확인이 필요할 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
_F6_MNG_C = "장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다."
_F4_REASON = ("라벨('씬지로이드정')은 '알루미늄 함유 제산제'만 명시(Mg 미명시) → al_mg_antacid category/display 의 "
              "'마그네슘' 단정은 source 보다 강함. counterpart/display 를 '알루미늄 함유 제산제'로 좁히고 Mg 비단정 + "
              "'효과 감소' → '흡수 지연/감소'(라벨 '흡수가 지연 또는 감소' 충실)로 reframe. category bucket(al_mg_antacid)은 "
              "id61 선례대로 유지하되 reviewer 가 Al-only display vs bucket 재사용 결정(live id61 도 수산화알루미늄→Al/Mg 일반화·동일 latent).")
_F6_REASON = ("에스오메프라졸=오메프라졸(id13 live)의 S-거울상 → PPI×B12 5건 + 메트포르민(id12) live 계열 합류. display 를 "
              "draft('수치 변화와 관련된 문구') → live PPI×B12 표준 템플릿('비타민 B12 상태에 영향이 있을 수 있다는 보고가 있어, "
              "상태 확인이 필요할 수 있습니다')로 reframe(톤 정합·장기복용+상태확인 조건 보존·측정치 단정 회피). "
              "소스는 복합제(낙소졸정=나프록센+에스오메프라졸·quote 가 에스오메프라졸 명시) → reviewer 가 단일성분 source 확인 권장.")
BUNDLE_COPY_CHANGES = {
    "RF-F4-0173": {"kind": "display_reframe", "reason": _F4_REASON, "fields": {
        "counterpart": {"original": "Al/Mg 함유 제산제(약물)", "cleaned": "알루미늄 함유 제산제(약물)"},
        "display_copy": {"original": _F4_DISP_O, "cleaned": _F4_DISP_C},
        "management_copy": {"original": _F4_MNG_O, "cleaned": _F4_MNG_C}}},
    "RF-F6-0201": {"kind": "display_reframe", "reason": _F6_REASON, "fields": {
        "display_copy": {"original": _F6_DISP_O, "cleaned": _F6_DISP_C},
        "management_copy": {"original": _F6_MNG_O, "cleaned": _F6_MNG_C}}},
}

# 라이브 60 컨텍스트 + 타 family 성분(L11 overlap)
_exp_cache = json.load(open(EXPORT, encoding="utf-8"))
LIVE_PAIRS = {(r.get("ingredient"), r.get("nutrient")) for r in _exp_cache["relations"]}
F1_QUINOLONES = {"노르플록사신", "레보플록사신", "로메플록사신", "발로플록사신", "오플록사신",
                 "자보플록사신", "토수플록사신", "페플록사신", "시프로플록사신", "목시플록사신"}
F2_TETRACYCLINES = {"테트라사이클린", "독시사이클린", "미노사이클린"}
F3_BISPHOSPHONATES = {"이반드론산", "에티드론산", "알렌드론산", "리세드론산"}
F9_DEPLETION = {"설파살라진", "카르바마제핀", "트리메토프림", "페노바르비탈", "페니토인", "프리미돈"}

# ── L6 route/availability: full index 형태 분류(경구 제품 존재 여부) ──
_TOPICAL_FORMS = ("액", "크림", "연고", "겔", "외용", "로션", "샴푸", "패치", "카타플", "스프레이")
_ORAL_FORMS = ("정", "캡슐", "세립", "산", "시럽", "과립", "현탁", "트로키")


def _formulation(name):
    n = name or ""
    if any(t in n for t in _TOPICAL_FORMS):
        return "topical"
    if any(t in n for t in _ORAL_FORMS):
        return "oral"
    return "other"


def _oral_present_map(ingredients):
    """full index 에서 ingredient 별 국내 oral 제품 존재 여부 + 형태 분포(읽기전용)."""
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    ents = idx["entries"]
    out = {}
    for ing in ingredients:
        ms = [e for e in ents if e.get("ingredient_name") and ing in e["ingredient_name"]]
        forms = {}
        for e in ms:
            f = _formulation(e.get("item_name"))
            forms[f] = forms.get(f, 0) + 1
        out[ing] = {"index_items": len(ms), "forms": forms, "oral_present": forms.get("oral", 0) > 0}
    return out


_ORAL_PRESENT = None


def oral_present(ing):
    global _ORAL_PRESENT
    if _ORAL_PRESENT is None:
        _ORAL_PRESENT = _oral_present_map(["레보티록신", "케토코나졸", "에스오메프라졸"])
    return _ORAL_PRESENT.get(ing, {"oral_present": True})  # 미색인 성분은 route 미적용(보수: pass)


def _quote_tokens(rec):
    cp = rec.get("counterpart", "")
    if cp in NUTRIENT_COUNTERPARTS:
        return B12_QUOTE_TOKENS
    return ANTACID_QUOTE_TOKENS


def load_bundle():
    """reviewer-ready batch → F4/F6/F10 3건 + copy_change 적용 + family 재검증.
    (records, reverify_summary) 반환. live 무수정."""
    rr = json.load(open(REVIEWER_READY, encoding="utf-8"))
    recs = [dict(r) for r in rr["reviewer_ready_relations"] if r.get("family") in BUNDLE_FAMILIES]
    for r in recs:
        cc = BUNDLE_COPY_CHANGES.get(r["candidate_id"])
        if cc:
            for field, fc in cc["fields"].items():
                assert r[field] == fc["original"], \
                    f"{r['candidate_id']}: batch {field} 가 original 과 불일치 — 카피 위조/무결성 위반"
                r[field] = fc["cleaned"]
            if "counterpart" in cc["fields"]:
                r["relation"] = f"{r['drug_ingredient']} × {r['counterpart']}"
            r["_copy_change"] = cc
    summary = reverify_all(recs)
    return recs, summary


def reverify(rec):
    """F4/F6/F10 family-specific 재검증(refute-by-default). (lens_results, verdict, flags).
    핵심 = L6_route_domestic_availability(0275 강등) + L5_category_clarity."""
    q = rec.get("source_quote", "") or ""
    disp = rec.get("display_copy", "") or ""
    mng = rec.get("management_copy", "") or ""
    copy_txt = f"{disp} {mng}"
    cp = rec.get("counterpart", "")
    ctype = rec.get("counterpart_type", "")
    cat = rec.get("counterpart_category")
    ing = rec.get("drug_ingredient", "")
    mech = rec.get("mechanism", "")
    action = rec.get("recommended_action", "")
    tokens = _quote_tokens(rec)
    is_antacid = cp in ANTACID_COUNTERPARTS
    is_nutrient = cp in NUTRIENT_COUNTERPARTS
    L = {}
    flags = []

    seq = str(rec.get("itemSeq", ""))
    L["L1_source_fidelity"] = "pass" if (seq.isdigit() and len(seq) >= 8 and rec.get("source_section")) \
        else "fail:itemSeq/section"
    L["L2_direct_cooccurrence"] = "pass" if any(t in q for t in tokens) else f"fail:{cp} 미언급"
    # ★ L3 mechanism 근거 — absorption: 흡수+(지연/감소 OR 위산도 의존[id61 동형]); depletion: nutrient+감소/저하.
    if mech == "absorption":
        ok = ("흡수" in q) and (any(d in q for d in _ABSORB_DIR) or any(a in q for a in _ACID_DEPEND))
        L["L3_mechanism_support"] = "pass" if ok else "fail:흡수 저하/위산도 의존 근거 부족"
    elif mech == "depletion":
        ok = any(t in q for t in B12_QUOTE_TOKENS) and any(d in q for d in ("저하", "감소", "결핍", "낮"))
        L["L3_mechanism_support"] = "pass" if ok else "fail:B12 저하/결핍 직접 근거 부족"
    else:
        L["L3_mechanism_support"] = f"fail:mechanism {mech} 비허용"
    # L4 방향 sanity
    L["L4_direction"] = "pass" if (any(d in q for d in _ABSORB_DIR) or any(a in q for a in _ACID_DEPEND)) else "fail:방향 불명"
    # ★ L5 category clarity — antacid drug ⇒ al_mg_antacid + '약물' 표기; nutrient ⇒ category 없음 + B12.
    if is_antacid:
        L["L5_category_clarity"] = "pass" if (ctype == "drug" and cat == "al_mg_antacid" and "약물" in cp) \
            else f"fail:antacid drug category 불명(type={ctype},cat={cat})"
    elif is_nutrient:
        L["L5_category_clarity"] = "pass" if (ctype == "nutrient" and not cat) \
            else f"fail:nutrient category 불명(type={ctype},cat={cat})"
    else:
        L["L5_category_clarity"] = f"fail:counterpart 분류 불명 {cp}"
    # ★★ L6 route/availability(0275 강등) — oral-absorption relation 인데 국내 oral 제품 0(외용 전용)이면 fail.
    if mech == "absorption" and is_antacid:
        op = oral_present(ing)
        if not op["oral_present"]:
            L["L6_route_domestic_availability"] = (
                f"fail:국내 색인 {ing} {op['index_items']}품목 전부 비경구({op['forms']}) — 경구 흡수×제산제 relation 오부착 위험"
                " (소스 수출용 oral tablet·route/availability mismatch·reviewer formulation-scoping 요)")
        else:
            L["L6_route_domestic_availability"] = f"pass:국내 oral 제품 존재({op['forms']})"
    else:
        L["L6_route_domestic_availability"] = "pass:비경구흡수 relation(N/A)"
    # L7 복용 지시(명령형) + 검사/처방 지시 금지(display)
    bad_dir = [c for c in DIRECTIVE_CMDS + TEST_TREAT_DIRECTIVE if c in copy_txt]
    L["L7_no_directive"] = "pass" if not bad_dir else f"fail:복용/검사/처방 지시 {bad_dir}"
    # L8 구체 시간·용량·복용 지시(display 비노출) — 0275 quote 의 2시간/콜라가 display 로 새지 않았는가
    bad_dose = [t for t in DOSING_DETAIL_TERMS if t in copy_txt]
    L["L8_no_dosing_detail_in_display"] = "pass" if not bad_dose else f"fail:display 구체 dosing {bad_dose}"
    # L9 제품/구매/제휴 + 보충 권유(display/management 만)
    bad_prod = [p for p in PRODUCT_PHRASES if p in copy_txt]
    bad_sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy_txt]
    L["L9_product_supplement"] = "pass" if not bad_prod and not bad_sup else f"fail:{bad_prod}{bad_sup}"
    # L10 live 60 exact 중복(전부 신규)
    L["L10_no_live_dup"] = "pass" if (ing, cp) not in LIVE_PAIRS else f"fail:live 중복 {(ing, cp)}"
    # L11 F1/F2/F3/F9 성분 혼동
    other = ("F1" if ing in F1_QUINOLONES else "F2" if ing in F2_TETRACYCLINES
             else "F3" if ing in F3_BISPHOSPHONATES else "F9" if ing in F9_DEPLETION else "")
    L["L11_no_other_family_overlap"] = f"fail:{other} 성분 {ing}" if other else "pass"
    # L12 금칙어 / L13 상담 톤 / L14 항응고
    fb = vfp.scan(copy_txt)
    L["L12_forbidden_phrase"] = "pass" if not fb else f"fail:{fb}"
    L["L13_consult_tone"] = "pass" if any(c in copy_txt for c in CONSULT_MARKERS) else "fail:상담 톤 없음"
    L["L14_negation_anticoag"] = "pass" if not any(t in q or t in copy_txt for t in ANTICOAG_TERMS) \
        else "fail:항응고/비타민K 혼입"
    # L15 display 소아/골/치아 알람어 비노출
    bad_ped = [t for t in PEDIATRIC_BONE_TERMS if t in copy_txt]
    L["L15_display_no_pediatric_bone"] = "pass" if not bad_ped else f"fail:display 소아/골/치아 알람어 {bad_ped}"
    # L16 mechanism/action enum(v0.2 ALLOWED) — absorption/separation · depletion/monitoring
    ok_enum = (mech in ("absorption", "depletion")) and (action in ("separation", "monitoring", "avoid_concomitant"))
    pair_ok = (mech == "absorption" and action == "separation") or (mech == "depletion" and action == "monitoring")
    L["L16_mechanism_action_enum"] = "pass" if (ok_enum and pair_ok) else f"fail:mech/action {mech}/{action}"
    # copy_change flag
    if rec.get("_copy_change"):
        flags.append("copy_change:display_reframe")

    hard_fail = any(str(v).startswith("fail") for v in L.values())
    if hard_fail:
        verdict = "needs_review"
    elif rec.get("_copy_change"):
        verdict = "survives_with_copy_change"
    else:
        verdict = "survives"
    return L, verdict, flags


# ── 후보별 reviewer note(작업 C) ──
BUNDLE_REVIEWER_NOTES = {
    "RF-F4-0173": ["레보티록신×제산제: '알루미늄 함유 제산제와 병용투여시 이 약의 흡수가 지연 또는 감소' 명시(흡수 기전). "
                   "survives_with_copy_change(Al-only). reviewer 는 (a)al_mg_antacid bucket 재사용 vs 'Al 함유 제산제' 한정 표기 결정, "
                   "(b)live id61(이트라코나졸)도 수산화알루미늄→'Al/Mg' 일반화한 점 함께 검토(동일 latent)."],
    "RF-F6-0201": ["에스오메프라졸×B12: '저위산증/무위산증으로 인한 비타민 B12 흡수 감소...장기간 치료' 명시(depletion·monitoring). "
                   "오메프라졸(id13) S-거울상 → PPI×B12 5건 live 계열 합류. survives_with_copy_change(live 템플릿 톤 정합). "
                   "reviewer 는 (a)복합제(낙소졸정) source 대신 단일성분 에스오메프라졸 라벨로 근거 보강 가능 여부, (b)evidence_level 확정."],
    "RF-F10-0275": ["needs_review(작업 C 강등·route/availability). 소스 더마졸정 **수출용** oral tablet 이나 국내 색인 케토코나졸 "
                    "10품목 전부 외용(액/크림) → 경구 흡수×제산제 카드를 ingredient 에 붙이면 외용 제품 오부착. reviewer 가 "
                    "(a)국내 oral 케토코나졸 존재 여부, (b)formulation-scoping(경구 한정 카드), (c)수출용 source 수용 여부 확정 후에만 통합."],
}


def reverify_all(recs):
    out = {}
    counts = {"survives": 0, "survives_with_copy_change": 0, "needs_review": 0, "hold": 0, "reject": 0}
    for r in recs:
        L, verdict, flags = reverify(r)
        counts[verdict] = counts.get(verdict, 0) + 1
        out[r["candidate_id"]] = {"lens_results": L, "verdict": verdict, "flags": flags,
                                  "reviewer_notes": BUNDLE_REVIEWER_NOTES.get(r["candidate_id"], [])}
    return {"per_candidate": out, "counts": counts}


def _integrable_ids(recs):
    out = []
    for r in recs:
        _L, verdict, _f = reverify(r)
        if verdict in ("survives", "survives_with_copy_change"):
            out.append(r["candidate_id"])
    return out


def to_row(rec):
    """reviewer-ready 레코드 → integ.draft_to_live/guard_projected row 어댑터."""
    seq = str(rec["itemSeq"])
    return {
        "candidate_id": rec["candidate_id"],
        "drug_ingredient": rec["drug_ingredient"],
        "counterpart": rec["counterpart"],
        "counterpart_type": rec["counterpart_type"],
        "counterpart_category": rec.get("counterpart_category"),
        "mechanism": rec["mechanism"],
        "recommended_action": rec["recommended_action"],
        "evidence_level": rec["evidence_level"],
        "confidence": rec.get("confidence", ""),
        "source_itemseq": seq,
        "source_section": rec.get("source_section", ""),
        "source_quote": rec.get("source_quote", ""),
        "source_url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={seq}",
        "display_text_ko_draft": rec["display_copy"],
        "management_copy_draft": rec.get("management_copy", ""),
        "adversarial_verdict": rec.get("adversarial_verdict", ""),
    }


def resolve_scope(recs):
    """argv → (scope_label, [candidate_id...]). 기본 integrable(=survives+copy_change=2)."""
    integ_ids = _integrable_ids(recs)
    all_ids = [r["candidate_id"] for r in recs]
    by_fam = {f: [r["candidate_id"] for r in recs if FAMILY_OF[r["candidate_id"]] == f] for f in BUNDLE_FAMILIES}
    if "--candidate-ids" in sys.argv:
        i = sys.argv.index("--candidate-ids")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        return "custom", [c.strip() for c in raw.split(",") if c.strip()]
    if "--scope" in sys.argv:
        i = sys.argv.index("--scope")
        s = sys.argv[i + 1] if i + 1 < len(sys.argv) else "integrable"
        if s.startswith("family:"):
            fam = s.split(":", 1)[1]
            return f"family:{fam}", by_fam.get(fam, [])
        return {"integrable": ("integrable", integ_ids),
                "all": ("all", all_ids)}.get(s, ("integrable", integ_ids))
    return "integrable", integ_ids


def _base_count():
    if "--base-count" in sys.argv:
        i = sys.argv.index("--base-count")
        if i + 1 < len(sys.argv):
            try:
                return int(sys.argv[i + 1])
            except ValueError:
                pass
    return None


def build_subset(exp, scope_ids):
    """scope_ids → projected entries. live 무수정. needs_review/hold/reject 는 STOP. (entries, viol)."""
    recs, _summary = load_bundle()
    by_id = {r["candidate_id"]: r for r in recs}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in scope_ids:
        rec = by_id.get(cid)
        if rec is None:
            viol.append(f"{cid}: F4/F6/F10 reviewer-ready 집합에 없음")
            continue
        _L, verdict, _f = reverify(rec)
        if verdict not in ("survives", "survives_with_copy_change"):
            viol.append(f"{cid}: 재검증 verdict={verdict} (통합 가능 아님 — needs_review/hold/reject 통합 금지·reviewer 확정 요)")
            continue
        row = to_row(rec)
        if (row["drug_ingredient"], row["counterpart"]) in existing:
            viol.append(f"{cid}: 이미 live 에 존재(드라이런 전제 위반)")
            continue
        nid += 1
        rel = integ.draft_to_live(row, nid)
        viol += integ.guard_projected(cid, row, rel)
        entries.append({
            "candidate_id": cid,
            "family": FAMILY_OF[cid],
            "projected_id": nid,
            "counterpart_type": rec["counterpart_type"],
            "counterpart": rec["counterpart"],
            "counterpart_category": rel.get("counterpart_category"),
            "recommended_action": rel["recommended_action"],
            "mechanism": rel["mechanism"],
            "evidence_level": rel["evidence_level"],
            "confidence": rec.get("confidence", ""),
            "adversarial_verdict": rec.get("adversarial_verdict", ""),
            "reverify_verdict": verdict,
            "copy_change": rec.get("_copy_change"),
            "projected_live_relation": rel,
        })
    return entries, viol


# ── reviewer 노트 인터록(small-family bundle 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date", "<scope")
SCOPE_MARKERS = ("scope", "범위")
REVIEWER_ID_RE = re.compile(r"검수자|검토자|reviewer|RPH|PM[ \t]*승인")
# ⚠️ 번들 이름이 'small-family' 라 'family'/'small-family' 는 grouping 마커에서 제외(자명 충족 방지) — 실제 묶음/개별 결정 토큰만.
GROUPING_MARKERS = ("grouping", "묶음", "개별", "한 번에", "subset", "wave", "번들", "bundle")
ANTACID_MARKERS = ("al_mg_antacid", "알루미늄", "제산제")          # F4 category 명시
B12_MARKERS = ("비타민B12", "비타민 B12", "B12")                   # F6 영양소 명시
MECHANISM_MARKERS = ("absorption", "흡수", "depletion", "결핍", "separation", "monitoring")
ALUMINUM_ONLY_ACK = ("알루미늄", "Al-only", "Al only", "마그네슘 미명시", "Mg 미명시")  # F4 copy_change 인지
NEEDS_REVIEW_ACK_MARKERS = ("RF-F10-0275", "케토코나졸", "route", "외용", "수출용")        # 0275 needs_review 인지
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음",
                       "제품·구매·제휴·보충제 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("B12 보충 권유 없음", "보충 권유 없음", "보충 권유 아님",
                          "영양제 복용 권유 없음", "복용 권유 없음", "섭취 권유 없음")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|보충제?[ \t]*추천)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_RECO_RE = re.compile(
    r"(비타민\s*B12|B12|철분|보충제|영양제)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")
# ⚠️ permission 단어(허용/추가/노출/승인)가 반드시 뒤따라야 매치 — 모니터링 톤 마커 false-positive 방지.
TEST_TREAT_PERMISSION_RE = re.compile(
    r"(검사|처방|투여)[ \t]*(지시|받으세요|하세요|권고)[ \t]*(허용|추가|노출|승인)"
    r"|(검사|처방)[ \t]*지시[ \t]*(문구[ \t]*)?(허용|추가)")
# 소아/임신/골/계열 일반화 허용 또는 외용→경구 일반화 허용 — 금지
GENERALIZE_PERMIT_RE = re.compile(
    r"(소아|임신|수유|치아|구루병|골연화증|골다공증|계열|아졸 일반|외용|국소)[^\n]{0,24}(일반화|확대|간주|통합)[ \t]*(승인|허용|가능|함|적용)"
    r"|(일반화|확대)[ \t]*(승인|허용)")


def check_reviewer_note(reviewer_note, scope_ids):
    """small-family bundle live 통합 reviewer 노트 게이트. (note, violations). 빈 리스트 = 통과.
    scope_ids = 이번 통합 대상(노트가 전건 명시 + scope 일치). main()/테스트 공유."""
    bad = []
    note = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note = f.read()
    if not note.strip():
        bad.append(f"노트 비공란 필요(--reviewer-note PATH). 받은 값: {reviewer_note!r}")
        return note, bad
    up, low = note.upper(), note.lower()
    for s in NOTE_SAMPLE_SENTINELS:
        if s.upper() in up:
            bad.append(f"SAMPLE/예시 토큰 감지('{s}') — 템플릿 그대로 승격 거부")
            break
    for m in NOTE_PLACEHOLDER_MARKERS:
        if m in note:
            bad.append(f"미기입 placeholder 감지('{m}')")
            break
    if not any(t in low or t in note for t in APPROVAL_TOKENS):
        bad.append(f"승인 표기({'/'.join(APPROVAL_TOKENS)}) 없음")
    miss = [c for c in scope_ids if c not in note]
    if miss:
        bad.append(f"candidate_id 미명시(승인 scope 전건 필요): {miss}")
    if not REVIEWER_ID_RE.search(note):
        bad.append("reviewer 식별자/PM 승인 근거 미명시(검수자/RPH/PM 승인)")
    if not any(m in note for m in SCOPE_MARKERS):
        bad.append("scope 선언 미명시(integrable/all/family:F4/F6/F10/명시 ids)")
    if not any(m in note for m in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(한 번에/family별/bundle/wave/subset)")
    if not any(m in note for m in ANTACID_MARKERS):
        bad.append("F4 category(al_mg_antacid/알루미늄 함유 제산제) 결정 미명시")
    if not any(m in note for m in B12_MARKERS):
        bad.append("F6 영양소(비타민B12) monitoring 대상 명시 누락")
    if not any(m in note for m in MECHANISM_MARKERS):
        bad.append("mechanism/action 결정 미명시(absorption/separation · depletion/monitoring)")
    if not any(m in note for m in ALUMINUM_ONLY_ACK):
        bad.append("RF-F4-0173 aluminum-only(Mg 미명시) copy_change 인지 미명시")
    if not any(m in note for m in NEEDS_REVIEW_ACK_MARKERS):
        bad.append("RF-F10-0275(케토코나졸) needs_review(route/availability·외용 전용·수출용) 인지 미명시")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품 추천 아님 명시 필요")
    if not any(m in note for m in NOT_SUPPLEMENT_MARKERS):
        bad.append("B12 보충/영양제 복용 권유 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품/보충 추천 허용 문구 — 금지")
    if SUPPLEMENT_RECO_RE.search(note):
        bad.append("비타민B12/철분/영양제 보충/복용 권유/권장 허용 문구 — 금지")
    if TEST_TREAT_PERMISSION_RE.search(note):
        bad.append("검사/처방/투여 지시 카피 허용 문구 — 금지(모니터링 톤)")
    if GENERALIZE_PERMIT_RE.search(note):
        bad.append("소아/임신/골 문맥·아졸 계열·외용→경구 일반화 허용 문구 — 금지")
    return note, bad


def _index_impact(recs, integrated_ids):
    """full index/aliases 영향(읽기전용). pool=aliases.verified_item_seqs 라 relation 과 decoupled →
    relation-only 통합 자동 flip 0."""
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    ents = idx["entries"]
    al = json.load(open(ALIASES, encoding="utf-8"))
    al_txt = json.dumps(al, ensure_ascii=False)
    by_id = {r["candidate_id"]: r for r in recs}
    integrated_ings = sorted({by_id[c]["drug_ingredient"] for c in integrated_ids if c in by_id})
    per = {}
    latent_now = 0
    latent_all = 0
    for ing in sorted({r["drug_ingredient"] for r in recs}):
        matched = [e for e in ents if ing in (e.get("ingredient_name") or "")]
        covered = sum(1 for e in matched if e.get("covered_by_relation"))
        name_only = sum(1 for e in matched if not e.get("covered_by_relation"))
        in_al = ing in al_txt
        op = oral_present(ing)
        # name_only 중 oral 만 latent(외용은 경구 흡수 relation 무관)
        latent = name_only if (not in_al and op["oral_present"]) else 0
        latent_all += latent
        integrated = ing in integrated_ings
        if integrated:
            latent_now += latent
        per[ing] = {"index_items": len(matched), "covered_by_relation": covered,
                    "name_only": name_only, "in_aliases": in_al,
                    "formulations": op.get("forms"), "oral_present": op["oral_present"],
                    "integrated_in_this_scope": integrated,
                    "latent_flip_if_alias_enriched": latent}
    counts = idx["meta"].get("counts", {})
    return {
        "full_index_counts_current": counts,
        "index_pool_source": "data/medistack_v0.3_aliases.json · verified_item_seqs/product_aliases (export relations 와 decoupled)",
        "per_ingredient": per,
        "integrated_ingredients_this_scope": integrated_ings,
        "automatic_flip_from_relation_integration": 0,
        "relation_card_flip_required": 0,
        "relation_card_after": counts.get("relation_card"),
        "name_only_after": counts.get("name_only"),
        "index_change_required": False,
        "alias_change_required": False,
        "latent_flip_if_alias_enriched_this_scope": latent_now,
        "latent_flip_if_alias_enriched_all_integrable": latent_all,
        "interpretation": "레보티록신(relation_card 17·이미 Fe/Ca relation 보유)·에스오메프라졸(색인 0·복합제 내에만)·"
                          "케토코나졸(외용 10·경구 0). full index/aliases 는 export relations 와 decoupled(pool=aliases.verified_item_seqs)"
                          " → relation-only 통합 자동 flip 0·relation_card 1168/name_only 16412 불변. 케토코나졸은 needs_review 라 미통합 "
                          "+ 외용 전용이라 경구 흡수 relation alias-enrich 대상 아님(latent 0).",
    }


def _scenarios(exp, recs, before, base_max):
    integ_ids = _integrable_ids(recs)
    all_ids = [r["candidate_id"] for r in recs]
    needs_review = [c for c in all_ids if c not in integ_ids]
    by_fam = {f: [r["candidate_id"] for r in recs if FAMILY_OF[r["candidate_id"]] == f] for f in BUNDLE_FAMILIES}
    by_fam_integ = {f: [c for c in by_fam[f] if c in integ_ids] for f in BUNDLE_FAMILIES}

    def proj(cids):
        return {"count": len(cids), "expected_count": before + len(cids),
                "expected_ids": list(range(base_max + 1, base_max + 1 + len(cids))), "candidate_ids": cids}
    return {
        "recommended": "integrable 2(F4 1 + F6 1) 한 번에(60→62) 또는 family별(F4 60→61·F6 60→61). "
                       "F10(케토코나졸 0275)은 route/availability mismatch → needs_review, reviewer 확정 전까지 통합 불가.",
        "integrable": proj(integ_ids),
        "all_reviewer_ready": proj(all_ids),
        "family_F4": proj(by_fam_integ["F4"]),
        "family_F6": proj(by_fam_integ["F6"]),
        "family_F10": {"count": 0, "candidate_ids": by_fam["F10"],
                       "note": "0275 needs_review(route/availability·국내 외용 전용·수출용 source) → 통합 0(STOP)."},
        "conditional_if_0275_resolved": {
            "candidate_ids": needs_review,
            "expected_count_added": len(needs_review),
            "expected_count_after_with_integrable": before + len(integ_ids) + len(needs_review),
            "note": "reviewer 가 국내 oral 케토코나졸 확인 또는 formulation-scoping 결정하면 0275 통합 가능 → "
                    "integrable 2 + 1 = 3 → 60→63. 현재는 needs_review(통합 대상 아님).",
        },
        "scenario_on_f1f2f3f9_true_base": {
            "baseline": TRUE_BASE_F1F2F3F9,
            "expected_after_integrable": TRUE_BASE_F1F2F3F9 + len(integ_ids),
            "expected_after_conditional_full": TRUE_BASE_F1F2F3F9 + len(integ_ids) + len(needs_review),
            "note": "F1 18+F2 5+F3 1+F9 7 모두 live(60→91)면 small-family integrable 2 는 91→93(conditional 0275 포함 91→94). "
                    "runtime max+1 자동 조정.",
        },
        "base_count_override": _base_count(),
        "id_rule": "id 는 runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. F1/F2/F3/F9 먼저면 자동 조정.",
    }


def main():
    pm_approved = "--pm-approved" in sys.argv
    reviewer_note = None
    if "--reviewer-note" in sys.argv:
        i = sys.argv.index("--reviewer-note")
        if i + 1 < len(sys.argv):
            reviewer_note = sys.argv[i + 1]

    exp = json.load(open(EXPORT, encoding="utf-8"))
    before = len(exp["relations"])
    recs, summary = load_bundle()
    scope_label, scope_ids = resolve_scope(recs)
    entries, viol = build_subset(exp, scope_ids)
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== F4/F6/F10 small-family {scope_label}({len(entries)}건) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    print(f"재검증(작업 C): {summary['counts']} (survives+copy_change 만 통합 가능 — 0275 needs_review)")
    for e in entries:
        r = e["projected_live_relation"]
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, evidence={r['evidence_level']}, "
              f"cat={r.get('counterpart_category')}, link={r['product_link_allowed']}, "
              f"kcard={r['potassium_safety_card']}, clinical={r['requires_clinical_review']}, "
              f"reverify={e['reverify_verdict']})")

    if not pm_approved:
        with open(EXPORT, "rb") as f:
            sha_before = hashlib.sha256(f.read()).hexdigest()
        base_max = max(r["id"] for r in exp["relations"])
        integ_ids = _integrable_ids(recs)
        by_id = {r["candidate_id"]: r for r in recs}
        survives = [c for c in integ_ids if not by_id[c].get("_copy_change")]
        copy_change = [c for c in integ_ids if by_id[c].get("_copy_change")]
        needs_review = [r["candidate_id"] for r in recs if r["candidate_id"] not in integ_ids]
        scope_scenarios = _scenarios(exp, recs, before, base_max)

        ok_all, tail_all = integ.run_v0_2(integ._sim_with(exp, projected)) if projected else (True, "n/a(0건)")
        index_impact = _index_impact(recs, [e["candidate_id"] for e in entries])

        live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
        dup = [f"{r['ingredient']}×{r['nutrient']}" for r in projected
               if (r["ingredient"], r["nutrient"]) in live_pairs]

        # ── 작업 B/C 인벤토리 ──
        inventory = {
            "meta": {
                "name": "f4_f6_f10_small_family_inventory_v1_4",
                "status": "DRAFT-ONLY — NOT LIVE / live_integration_forbidden=true / 적대검증 reviewer-ready 3 + family 재검증",
                "purpose": "F4/F6/F10 small-family bundle reviewer-ready 3건 감사 + 작업 B/C family-specific 재검증(16 렌즈·refute-by-default). "
                           "reviewer package/integrator 단일 소스.",
                "families": list(BUNDLE_FAMILIES),
                "audited": BUNDLE_REVIEWER_READY_COUNT, "reviewer_ready_adversarial": BUNDLE_REVIEWER_READY_COUNT,
                "reverify_counts": summary["counts"],
                "integrable_count": len(integ_ids), "integrable_ids": integ_ids,
                "survives_ids": survives, "copy_change_ids": copy_change, "needs_review_ids": needs_review,
                "ingredients_reviewer_ready": sorted({r["drug_ingredient"] for r in recs}),
                "ingredients_integrable": sorted({by_id[c]["drug_ingredient"] for c in integ_ids}),
                "counterpart_split_integrable": {
                    "al_mg_antacid(약물)": sum(1 for c in integ_ids if by_id[c]["counterpart"] in ANTACID_COUNTERPARTS),
                    "비타민B12(영양소)": sum(1 for c in integ_ids if by_id[c]["counterpart"] in NUTRIENT_COUNTERPARTS)},
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "confirmed_at": CONFIRMED_AT,
                "headline_finding_1_route_0275": "케토코나졸×제산제(0275): 소스 더마졸정 수출용 oral tablet 이나 국내 색인 케토코나졸 10품목 "
                    "전부 외용(액/크림) → 경구 흡수×제산제 카드를 ingredient 에 붙이면 외용 제품 오부착. 광역 L8(소스가 tablet→pass)이 "
                    "놓친 것을 family L6_route_domestic_availability 가 fail → needs_review. live 선례 id61(이트라코나졸)은 국내 제품 사용.",
                "headline_finding_2_aluminum_only_0173": "레보티록신×제산제(0173): 라벨은 '알루미늄 함유 제산제'만 명시(Mg 미명시) → "
                    "al_mg_antacid display 의 Mg 단정은 source 보다 강함. counterpart/display 를 '알루미늄 함유 제산제'로 좁히고 Mg 비단정 "
                    "+ '효과 감소'→'흡수 지연/감소' reframe(copy_change). live id61 도 동일 일반화(reviewer surface).",
                "headline_finding_3_ppi_b12_template_0201": "에스오메프라졸×B12(0201): 오메프라졸(id13) S-거울상 → PPI×B12 5건 + 메트포르민 "
                    "live 계열 합류. display 를 draft('수치 변화')→live PPI×B12 표준 템플릿으로 reframe(copy_change·톤 정합). "
                    "소스는 복합제(낙소졸정) → 단일성분 source 보강 reviewer note.",
                "note": "통합 가능 = 자동 적대검증 + family 재검증 통과(survives+copy_change)를 의미하며 임상 검수 완료·식약처 승인·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 별도 PM + clinical reviewer note + 별도 PR.",
            },
            "candidates": [
                {
                    "candidate_id": r["candidate_id"], "family": FAMILY_OF[r["candidate_id"]], "relation": r["relation"],
                    "drug_ingredient": r["drug_ingredient"], "counterpart": r["counterpart"],
                    "counterpart_type": r["counterpart_type"], "counterpart_category": r.get("counterpart_category"),
                    "itemSeq": r["itemSeq"], "source_product": SOURCE_PRODUCTS.get(r["candidate_id"]),
                    "source_section": r["source_section"], "source_quote": r["source_quote"],
                    "mechanism": r["mechanism"], "recommended_action": r["recommended_action"],
                    "evidence_level": r["evidence_level"], "confidence": r.get("confidence"),
                    "risk_level": r.get("risk_level"), "display_copy": r["display_copy"],
                    "management_copy": r.get("management_copy"),
                    "product_link_allowed": False, "potassium_safety_card": False,
                    "adversarial_verdict": r.get("adversarial_verdict"),
                    "reverify": summary["per_candidate"][r["candidate_id"]],
                    "copy_change": r.get("_copy_change"),
                    "live_integration_forbidden": True, "published": False,
                    "clinical_reviewed": False, "reviewed_by": "",
                }
                for r in recs
            ],
            "f10_family_context": F10_FAMILY_CONTEXT,
        }
        os.makedirs(os.path.dirname(INVENTORY_ARTIFACT), exist_ok=True)
        with open(INVENTORY_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(inventory, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── index impact ──
        with open(INDEX_IMPACT_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump({"meta": {"name": "f4_f6_f10_small_family_index_impact_v1_4",
                                "status": "ANALYSIS — read-only / no index/alias write",
                                "purpose": "small-family 통합 시 full index/relation_card/name_only/aliases 영향 분석.",
                                "confirmed_at": CONFIRMED_AT},
                       "impact": index_impact}, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── dry-run ──
        artifact = {
            "meta": {
                "name": "f4_f6_f10_small_family_live_dryrun_v1_4",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "small-family 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_f4_f6_f10_small_family_dryrun_v1_4.py 가 안전·계약 검증.",
                "requested_scope": scope_label,
                "baseline_relations": before, "baseline_max_id": base_max,
                "expected_relation_count_before": before,
                "expected_relation_count_after": after,
                "expected_relation_count_after_integrable": before + len(integ_ids),
                "expected_ids": ids,
                "included_candidate_ids": [e["candidate_id"] for e in entries],
                "all_reviewer_ready_ids": [r["candidate_id"] for r in recs],
                "integrable_ids": integ_ids, "survives_ids": survives, "copy_change_ids": copy_change,
                "needs_review_ids": needs_review,
                "scope_scenarios": scope_scenarios,
                "reverify_counts": summary["counts"],
                "live_write_performed": False, "live_promotion": 0,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "data_url": "v0.2 (불변)",
                "export_sha_before": sha_before, "export_sha_after_same": True,
                "reviewer_note_required": True,
                "reviewer_note_interlock": {
                    "required": True,
                    "approval_tokens": list(APPROVAL_TOKENS),
                    "candidate_ids_all_of_scope": True,
                    "scope_decision_required": True,
                    "grouping_decision_required": True,
                    "antacid_category_decision": "al_mg_antacid(F4 레보티록신·알루미늄 함유 제산제·Al-only display)",
                    "nutrient_target_decision": "비타민B12(F6 에스오메프라졸·depletion/monitoring·약물 category 없음)",
                    "mechanism_action_decision_required": True,
                    "aluminum_only_ack_required": "RF-F4-0173 aluminum-only(Mg 미명시) copy_change 인지",
                    "needs_review_ack_required": "RF-F10-0275(케토코나졸) needs_review(route/availability·외용 전용·수출용) 인지",
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id(scope 전건)/scope/grouping/category/영양소/mechanism/"
                               "Al-only ack/0275 ack/verified_reference 누락 · clinical_reviewed=true·제품추천·B12 보충 권유·"
                               "검사/처방 지시·소아/골·아졸 계열·외용→경구 일반화 허용",
                    "template": "docs/MediStack_reviewer_package_f4_f6_f10_small_family_v1_4.md §reviewer-note",
                },
                "guard_checks": {
                    "guard_projected_violations": viol,
                    "all_product_link_false": all(r["product_link_allowed"] is False for r in projected),
                    "all_potassium_card_false": all(r["potassium_safety_card"] is False for r in projected),
                    "all_requires_clinical_review_false": all(r["requires_clinical_review"] is False for r in projected),
                    "no_reviewed_by": all("reviewed_by" not in r for r in projected),
                    "no_draft_only_leak": all(not (integ.DRAFT_ONLY & set(r.keys())) for r in projected),
                    "all_source_itemseq": all(bool(re.search(r"itemSeq=\d+", r["source"]["url"])) for r in projected),
                    "ids_disjoint_from_live": not (set(ids) & {r["id"] for r in exp["relations"]}),
                    "mechanism_in_allowed": all(r["mechanism"] in ("absorption", "depletion") for r in projected),
                    "action_in_allowed": all(r["recommended_action"] in ("separation", "monitoring") for r in projected),
                    "antacid_only_al_mg": all(r.get("counterpart_category") == "al_mg_antacid"
                                              for r in projected if "제산제" in r["nutrient"]),
                    "b12_no_category": all("counterpart_category" not in r for r in projected if r["nutrient"] == "비타민B12"),
                    "no_needs_review_integrated": all(e["reverify_verdict"] in ("survives", "survives_with_copy_change")
                                                      for e in entries),
                    "no_dosing_detail_in_display": all(not any(t in (r.get("display_text_ko", "") + " " + r.get("management_ko", ""))
                                                               for t in DOSING_DETAIL_TERMS) for r in projected),
                    "no_pediatric_bone_in_display": all(not any(t in (r.get("display_text_ko", "") + " " + r.get("management_ko", ""))
                                                                for t in PEDIATRIC_BONE_TERMS) for r in projected),
                    "f4_no_magnesium_assertion": all("마그네슘" not in r.get("display_text_ko", "")
                                                     for r in projected if "알루미늄 함유 제산제" in r["nutrient"]),
                },
                "duplicate_summary": {"exact_dup_with_live": dup,
                                      "note": "레보티록신×제산제·에스오메프라졸×B12 는 live 60 에 미존재 → exact dup 0. "
                                              "al_mg_antacid 렌더는 id61(이트라코나졸) 선례·B12 depletion 은 id12/id13 선례."},
                "conflict_summary": {
                    "live_60": "exact dup 0(레보티록신/에스오메프라졸 신규 pair). al_mg_antacid=id61·B12 depletion=id12/13 렌더 선례.",
                    "f1_quinolone_18": "퀴놀론×광물/제산제 — 성분 다름·충돌 0.",
                    "f2_tetracycline_5": "사이클린×광물/제산제 — 성분 다름·충돌 0.",
                    "f3_bisphosphonate_1": "비스포×Al/Mg제산제 — 성분 다름·충돌 0.",
                    "f9_chronic_depletion_7": "만성복용약×엽산/비타민D — 성분/영양소 다름·충돌 0(에스오메프라졸×B12 는 별개 pair).",
                    "ketoconazole_needs_review": "0275(케토코나졸×제산제)은 route/availability mismatch → 통합 대상 아님(needs_review). "
                                                 "live 선례 id61(이트라코나졸)과 동일 mechanism 이나 케토코나졸은 국내 외용 전용.",
                    "f10_hold_reject_context": "0276(포사코나졸) hold(H2-blocker 주어 불일치·al_mg_antacid 매핑 불가) · "
                                               "0277(이트라코나졸) reject(=live id61 중복). 둘 다 reviewer-ready 3 밖.",
                    "full_factory_integrator_dedup": "차후 factory 일괄 integrator 는 (ingredient, counterpart/category) 키로 본 통합분 skip.",
                },
                "full_index_alias_impact": index_impact,
                "v0_2_validator_evidence": {
                    "sim_all_passed": ok_all, "sim_all_tail": tail_all,
                    "interpretation": "absorption/separation·al_mg_antacid(id61 동형) + depletion/monitoring·B12(id12/13 동형) "
                                      "현행 v0.2 validator PASS → 선행조건 0.",
                },
                "render_safety_summary": f"통합 가능 {len(integ_ids)}건 = al_mg_antacid 흡수 카드(id61 경로) + B12 depletion 카드(id12/13 경로). "
                                         "src 변경 불필요. F4 display Mg 비단정·0275 의 2시간/콜라 dosing display 비노출.",
                "live_integration_prerequisites": [],
                "validator_result_summary": f"sim 전체 v0.2 PASS={ok_all} (선행조건 0)",
                "note": "본 산출물은 드라이런 예상치일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 "
                        "의미하지 않는다. live 승격은 --pm-approved + --reviewer-note + 별도 PM + clinical reviewer.",
            },
            "projected_entries": entries,
        }
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")

        with open(EXPORT, "rb") as f:
            sha_after = hashlib.sha256(f.read()).hexdigest()
        if sha_after != sha_before:
            print("[FATAL] 드라이런인데 live export sha 변경됨 — 중단")
            return 1
        print(f"\n[dry-run] live export sha 불변({sha_before[:8]}). 산출물 3종:")
        print(f"   {os.path.relpath(INVENTORY_ARTIFACT, REPO)}")
        print(f"   {os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print(f"   {os.path.relpath(INDEX_IMPACT_ARTIFACT, REPO)}")
        print(f"[dry-run] v0.2 validator: 전체 PASS={ok_all} (선행조건 0).")
        print(f"[dry-run] index 자동 flip={index_impact['relation_card_flip_required']} · "
              f"latent flip(현 scope)={index_impact['latent_flip_if_alias_enriched_this_scope']}.")
        print(f"[dry-run] needs_review 1(0275 케토코나졸×제산제) — 통합 제외(route/availability·국내 외용 전용·수출용 source).")
        print("[dry-run] live 기록은 --pm-approved + --reviewer-note + 별도 PM/reviewer 필요.")
        return 0

    # ── LIVE 기록(--pm-approved + --reviewer-note): 본 세션 호출 금지. 테스트는 temp 복사본에서만 ──
    _note, note_bad = check_reviewer_note(reviewer_note, scope_ids)
    if note_bad:
        for b in note_bad:
            print(f"[STOP] reviewer 노트: {b}")
        return 1
    exp["relations"] = exp["relations"] + projected
    exp["meta"]["relation_count"] = len(exp["relations"])
    exp["meta"]["note"] = exp["meta"].get("note", "") + \
        (" | F4/F6/F10 small-family %s(%d건) live 통합: 레보티록신×알루미늄제산제(absorption)+에스오메프라졸×B12(depletion). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (scope_label, len(projected), before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE F4/F6/F10 SMALL-FAMILY ({scope_label}): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
