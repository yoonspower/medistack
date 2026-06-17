#!/usr/bin/env python3
"""
integrate_f9_chronic_depletion_batch_v1_4.py
MediStack — Relation Factory v1.4 **F9 만성복용 depletion** live 통합 **준비/드라이런** 스크립트.
integrate_f3_bisphosphonate_batch_v1_4.py / integrate_f2_tetracycline_batch_v1_4.py / integrate_f1_quinolone_batch_v1_4.py
패턴 승계(reviewer-ready batch → F9 + family-specific 재검증(작업 C)).

F9 family = **만성/장기복용 약물 × 엽산·비타민D depletion(mechanism=depletion·action=monitoring)**.
F1/F2/F3(흡수 차단·separation)과 달리 **결핍/저하 모니터링** 계열 — live 선례: 메트포르민×비타민B12(id12, depletion/monitoring).
counterpart = 영양소(엽산/비타민D)만(약물/제산제 없음 → counterpart_category 생략).

대상(소스: data/drafts/relation_factory_reviewer_ready_batch_v1_4.json · family==F9): reviewer-ready(적대검증) **8건**
  RF-F9-0269  설파살라진 × 엽산
  RF-F9-0245  카르바마제핀 × 엽산
  RF-F9-0246  카르바마제핀 × 비타민D
  RF-F9-0272  트리메토프림 × 엽산
  RF-F9-0252  페노바르비탈 × 비타민D
  RF-F9-0242  페니토인 × 엽산
  RF-F9-0243  페니토인 × 비타민D
  RF-F9-0255  프리미돈 × 비타민D

⚠️⚠️ **작업 C(F9 family-specific 재검증, reverify(), refute-by-default) 결과 — 적대검증과 다름**:
  survives 3 · survives_with_copy_change 4 · **needs_review 1** · hold 0 · reject 0 → **통합 가능 7**(survives+copy_change).
  ── 헤드라인 발견 ①(카르바마제핀×엽산 0245 강등) ──
    소스 quote("드물게 백혈구 증가, 임파절 장애, 엽산 결핍증")는 **이상반응 열거** 안의 bare 항목으로 (a)흡수/대사/길항
    기전 동사 없음 + (b)혈청엽산치 '저하' 같은 level-direction 없음(질환명 '엽산 결핍증'만) + (c)'드물게' 빈도.
    → F9 **저신호 이상반응 열거**(adversarial 의 옥스카르바제핀 강등 패턴과 동형) → needs_review.
    카르바마제핀은 ×비타민D(0246, '25-hydroxy-콜레칼시페롤의 감소' 명시)로 coverage 유지 → 약물 누락 아님.
  ── 헤드라인 발견 ②(항전간제×비타민D copy_change: nutrient=remedy) ──
    페노바르비탈/페니토인/프리미돈 × 비타민D(0252/0243/0255)는 연용(장기) **골연화증·구루병** + 비타민D **섭취/투여**(remedy).
    라벨은 혈청칼슘·무기인 '저하'를 적시하나 **비타민D 자체의 '수치 저하'는 명시 안 함**(효소유도제 골연화증 기전은 교과서적
    이나 라벨 문구는 vitD 를 '관리 수단'으로 언급) → 관계는 유효하나 display 의 "비타민D 수치 변화"는 source 보다 강함
    → **copy_change(display reframe)**: "비타민D 수치 변화"→"비타민D와 관련된 주의 문구"(측정치 단정 제거·골질환 알람어 비노출).
  ── 헤드라인 발견 ③(페니토인×엽산 0242 quote hygiene) ──
    "…혈청엽산치 저하가 나타날 수 있다(경구제에 한함.). 1" 끝의 stray 섹션 마커 ' 1' 트림(F1 stray '1' 동형) → copy_change(quote-trim).
    엽산치 '저하' 명시라 관계 자체는 strong.

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만 수행
(별도 PM 승인 + clinical reviewer 전까지 절대 금지·본 세션 호출 안 함).
  dry-run = 라이브/보호 데이터 **무수정** + 예상 산출물 기록:
    data/review/f9_chronic_depletion_inventory_v1_4.json    (작업 B/C — 8 reviewer-ready 감사 + family 재검증 렌즈)
    data/review/f9_chronic_depletion_live_dryrun_v1_4.json  (작업 G — scope별 예상 count/id + 가드 + 충돌 + v0.2 증거)
    data/review/f9_chronic_depletion_index_impact_v1_4.json (작업 K — full index/aliases 영향)

scope(작업 D grouping):
  --scope integrable (기본) survives+copy_change = 7건 — 60→67
  --scope survives   survives 3건 = [0269,0272,0246] — 60→63
  --scope copy_change survives_with_copy_change 4건 = [0242,0252,0243,0255] — 60→64
  --scope folate     통합 가능 ∩ 엽산 = [0269,0272,0242] — 60→63
  --scope vitd       통합 가능 ∩ 비타민D = [0246,0252,0243,0255] — 60→64
  --candidate-ids A,B,...  명시 후보(F9 ∩ 통합 가능; needs_review 는 build_subset 에서 STOP)
  --base-count N     scenario 표시용 baseline override(id 는 항상 runtime max+1)
  ⚠️ needs_review 1건(0245)은 scope 로 요청해도 통합 거부(STOP). reviewer standalone 근거 확정 후 별도.

live 통합 선행조건: **없음(0)**. depletion/monitoring 영양소 렌더 경로는 live(메트포르민×B12) 동일 — src 변경 불필요.
  full index: 6개 약물 모두 name_only·in_aliases=false → relation-only 통합 자동 flip 0(relation export 와 decoupled·1168/16412 불변).
  통합분을 verified_item_seqs 로 alias-enrich 하면(별도 작업) 조건부 latent flip(≤18) — 본 라운드 미수행.

사용:
  python3 scripts/integrate_f9_chronic_depletion_batch_v1_4.py                                  # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_f9_chronic_depletion_batch_v1_4.py --scope folate                   # dry-run(특정 scope)
  python3 scripts/integrate_f9_chronic_depletion_batch_v1_4.py --pm-approved --reviewer-note X     # live(별도 PM·reviewer 후·본 세션 금지)
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
INVENTORY_ARTIFACT = os.path.join(DATA, "review", "f9_chronic_depletion_inventory_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "f9_chronic_depletion_live_dryrun_v1_4.json")
INDEX_IMPACT_ARTIFACT = os.path.join(DATA, "review", "f9_chronic_depletion_index_impact_v1_4.json")

BASELINE_RELATIONS = 60      # F1/F2/F3 등 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-17"  # source-check + 적대검증 + F9 family 재검증 확인일
F9_REVIEWER_READY_COUNT = 8  # 적대검증 reviewer-ready
F9_SURVIVES_COUNT = 3        # 작업 C family 재검증 survives(0269/0272/0246)
F9_COPY_CHANGE_COUNT = 4     # survives_with_copy_change(0242/0252/0243/0255)
F9_INTEGRABLE_COUNT = 7      # survives + copy_change
TRUE_BASE_F1F2F3 = 84        # F1 18 + F2 5 + F3 1 모두 live 가정 baseline(조건부 시나리오).


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
ANTICOAG_TERMS = ["와파린", "항응고", "비타민 K", "비타민K", "INR", "프로트롬빈"]
# DISPLAY 노출 금지 — 소아/임신/골/치아 알람어(라벨 quote 에는 있을 수 있으나 카드에는 비노출)
PEDIATRIC_BONE_TERMS = ["소아", "임신", "수유", "치아", "구루병", "골연화증", "골다공증", "골절", "치조골", "치아형성"]
# 검사/처방 지시로 읽힐 카피 금지(모니터링 톤 유지)
TEST_TREAT_DIRECTIVE = ["검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요", "투여받으세요", "처방하세요"]
CONSULT = "약사 또는 의사"

# 영양소 counterpart(F9). 약물/제산제 없음 → counterpart_category 생략(null).
NUTRIENT_COUNTERPARTS = {"엽산", "비타민D"}
# 라벨 문장에서 nutrient counterpart 직접언급 토큰(엽산=엽산/폴산, 비타민D=비타민 D/콜레칼시페롤/hydroxy)
NUTRIENT_QUOTE_TOKENS = {
    "엽산": ("엽산", "폴산"),
    "비타민D": ("비타민 D", "비타민D", "콜레칼시페롤", "hydroxy"),
}
# depletion 방향 동사(라벨 quote)
_DEPLETION_DIR = ("저하", "감소", "결핍", "악화", "고갈", "낮아")
# 흡수/대사/길항/유도 기전 동사(저신호 이상반응 열거 판별)
_MECHANISM_WORDS = ("흡수", "대사", "길항", "유도", "배설", "고갈")
# 만성/연용/장기 framing
_CHRONIC_WORDS = ("연용", "장기", "만성", "지속", "오래", "장기간")
# 빈도 부사(저신호)
_RARE_WORDS = ("드물게", "희박하게", "극히 드물")
# 비타민D '관리 수단(remedy)' framing — 라벨이 vitD 를 섭취/투여로 권고(수치 저하 직접 명시 아님)
_REMEDY_WORDS = ("섭취", "투여", "보충", "복용")

# ── 작업 C copy_change(F9 family 재검증) ──
# kind="quote_trim": source_quote 끝 stray 마커 트림(cleaned 는 original_full 의 verbatim 부분문자열).
# kind="display_reframe": display_copy 를 source 충실 문구로 reframe(측정치 단정·골질환 알람어 제거).
_0242_Q_FULL = ("기타 : 결절성 동맥주위염, 다발성 관절증, 과혈당, 드물게 발열, 갑상샘기능검사치(혈청 T3, T4치 등)이상, "
                "다모, 혈청엽산치 저하가 나타날 수 있다(경구제에 한함.). 1")
_0242_Q_CLEAN = ("기타 : 결절성 동맥주위염, 다발성 관절증, 과혈당, 드물게 발열, 갑상샘기능검사치(혈청 T3, T4치 등)이상, "
                 "다모, 혈청엽산치 저하가 나타날 수 있다(경구제에 한함.)")
_VITD_DISP_FULL = ("이 약을 장기간 복용할 때 비타민D 수치 변화와 관련된 허가사항 문구가 있습니다. "
                   "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
_VITD_DISP_CLEAN = ("이 약을 장기간 복용할 때 비타민D와 관련된 허가사항 주의 문구가 있습니다. "
                    "증상이 걱정되면 약사 또는 의사와 상담하세요.")
_VITD_REFRAME_REASON = ("라벨은 연용(장기) 골대사 이상 + 비타민D 섭취/투여(remedy)를 적시하나 비타민D '수치 저하' 자체는 "
                        "명시 안 함 → display 의 '비타민D 수치 변화'는 source 보다 강함. '비타민D와 관련된 주의 문구'로 "
                        "reframe(측정치 단정·골질환 알람어 비노출). 관계(효소유도제 vitD depletion)는 유효 → 통합 가능.")
F9_COPY_CHANGES = {
    "RF-F9-0242": {"kind": "quote_trim", "field": "source_quote",
                   "original_full": _0242_Q_FULL, "cleaned": _0242_Q_CLEAN,
                   "reason": "원문 끝 stray 섹션 마커 ' 1' 트림(cleaned 는 original_full 의 verbatim 부분문자열·F1 stray '1' 동형). "
                             "혈청엽산치 '저하' 명시라 관계 strong."},
    "RF-F9-0252": {"kind": "display_reframe", "field": "display_copy",
                   "original": _VITD_DISP_FULL, "cleaned": _VITD_DISP_CLEAN, "reason": _VITD_REFRAME_REASON},
    "RF-F9-0243": {"kind": "display_reframe", "field": "display_copy",
                   "original": _VITD_DISP_FULL, "cleaned": _VITD_DISP_CLEAN, "reason": _VITD_REFRAME_REASON},
    "RF-F9-0255": {"kind": "display_reframe", "field": "display_copy",
                   "original": _VITD_DISP_FULL, "cleaned": _VITD_DISP_CLEAN, "reason": _VITD_REFRAME_REASON},
}

# 라이브 60 컨텍스트(L10 live 중복 · L11 다른 family overlap 렌즈에서 참조)
_exp_cache = json.load(open(EXPORT, encoding="utf-8"))
LIVE_PAIRS = {(r.get("ingredient"), r.get("nutrient")) for r in _exp_cache["relations"]}
F1_QUINOLONES = {"노르플록사신", "레보플록사신", "로메플록사신", "발로플록사신", "오플록사신",
                 "자보플록사신", "토수플록사신", "페플록사신", "시프로플록사신", "목시플록사신"}
F2_TETRACYCLINES = {"테트라사이클린", "독시사이클린", "미노사이클린"}
F3_BISPHOSPHONATES = {"이반드론산", "에티드론산", "알렌드론산", "리세드론산"}


def _quote_tokens(cp):
    return NUTRIENT_QUOTE_TOKENS.get(cp, (cp,))


def _scope_split(recs):
    """통합 가능(survives+copy_change) 후보를 counterpart 별로 분리."""
    integ_ids = _survives_ids(recs)
    by_id = {r["candidate_id"]: r for r in recs}
    folate = [c for c in integ_ids if by_id[c]["counterpart"] == "엽산"]
    vitd = [c for c in integ_ids if by_id[c]["counterpart"] == "비타민D"]
    return folate, vitd


def _survives_ids(recs):
    """통합 가능 = survives + survives_with_copy_change(needs_review/hold/reject 제외)."""
    out = []
    for r in recs:
        _L, verdict, _f = reverify(r)
        if verdict in ("survives", "survives_with_copy_change"):
            out.append(r["candidate_id"])
    return out


def load_f9():
    """reviewer-ready batch → F9 8건(적대검증 reviewer-ready) + copy_change 적용 + family 재검증.
    (records, reverify_summary) 반환. live 무수정."""
    rr = json.load(open(REVIEWER_READY, encoding="utf-8"))
    f9 = [dict(r) for r in rr["reviewer_ready_relations"] if r.get("family") == "F9"]
    for r in f9:
        cc = F9_COPY_CHANGES.get(r["candidate_id"])
        if cc:
            field = cc["field"]
            batch_key = {"source_quote": "source_quote", "display_copy": "display_copy"}[field]
            if cc["kind"] == "quote_trim":
                # batch 의 원문(=original_full)에서 stray 마커 트림 → cleaned(verbatim 부분문자열).
                assert cc["cleaned"] in cc["original_full"], \
                    f"{r['candidate_id']}: cleaned 가 original_full 부분문자열 아님 — 카피 위조 차단"
                assert r[batch_key] == cc["original_full"], \
                    f"{r['candidate_id']}: batch {field} 가 original_full 와 불일치 — 무결성 위반"
                r[batch_key] = cc["cleaned"]
            else:  # display_reframe
                assert r[batch_key] == cc["original"], \
                    f"{r['candidate_id']}: batch {field} 가 original 과 불일치 — 무결성 위반"
                r[batch_key] = cc["cleaned"]
            r["_copy_change"] = cc
    summary = reverify_all(f9)
    return f9, summary


def reverify(rec):
    """F9 family-specific 재검증(refute-by-default). (lens_results, verdict, flags).
    핵심 = L3_nutrient_depletion_support + L4_not_low_signal_enumeration(0245 강등)."""
    q = rec.get("source_quote", "") or ""
    disp = rec.get("display_copy", "") or ""
    mng = rec.get("management_copy", "") or ""
    copy_txt = f"{disp} {mng}"
    cp = rec.get("counterpart", "")
    ctype = rec.get("counterpart_type", "")
    ing = rec.get("drug_ingredient", "")
    tokens = _quote_tokens(cp)
    L = {}
    flags = []

    # L1 성분명↔itemSeq(실값·section). 실제 국내 품목 매칭은 reviewer Q(자동 fail 아님).
    seq = str(rec.get("itemSeq", ""))
    L["L1_source_fidelity"] = "pass" if (seq.isdigit() and len(seq) >= 8 and rec.get("source_section")) \
        else "fail:itemSeq/section"
    # L2 counterpart 직접 언급(엽산=엽산/폴산, 비타민D=비타민 D/콜레칼시페롤/hydroxy)
    L["L2_direct_cooccurrence"] = "pass" if any(t in q for t in tokens) else f"fail:{cp} 미언급"
    # ★ L3 nutrient depletion 근거(F9 핵심 렌즈) — (a)nutrient 토큰 인근 저하/감소/결핍 OR (b)연용+remedy framing.
    direct_decrease = any(d in q for d in _DEPLETION_DIR) and any(t in q for t in tokens)
    remedy_framing = (any(c in q for c in _CHRONIC_WORDS) and any(rw in q for rw in _REMEDY_WORDS)
                      and any(t in q for t in tokens))
    if direct_decrease or remedy_framing:
        L["L3_nutrient_depletion_support"] = "pass" + (":remedy_framing(copy_change)" if (remedy_framing and not direct_decrease) else "")
    else:
        L["L3_nutrient_depletion_support"] = f"fail:{cp} 저하/결핍 직접 근거도 연용-remedy framing 도 없음"
    # ★ L4 저신호 이상반응 열거 판별(0245 강등) — '드물게' 등 빈도 부사 + 기전 동사 없음 + level-direction 없음 + remedy framing 없음.
    rare = any(rw in q for rw in _RARE_WORDS)
    has_mech = any(mw in q for mw in _MECHANISM_WORDS)
    has_level_dir = bool(re.search(r"(혈청\s*)?(엽산|폴산|비타민\s*D|콜레칼시페롤)[^\n]{0,6}(치\s*)?(저하|감소)", q))
    if rare and not has_mech and not has_level_dir and not remedy_framing:
        L["L4_not_low_signal_enumeration"] = ("fail:저신호 이상반응 열거('드물게' + 기전/level-direction/연용-remedy 없음) "
                                              "— 모니터링 카드 근거 취약(reviewer standalone 근거 확정 요)")
    else:
        L["L4_not_low_signal_enumeration"] = "pass"
    # L5 depletion 방향(sanity)
    L["L5_depletion_direction"] = "pass" if any(d in q for d in _DEPLETION_DIR) else "fail:방향 불명"
    # L6 소아/임신 한정 근거 일반화 금지 — quote 의 유일 근거가 임신/소아면서 일반 기전 부재면 fail.
    preg_only = (any(p in q for p in ("임신중", "임부", "임산부", "수유부", "소아에 한")) and not has_mech and not remedy_framing and not has_level_dir)
    L["L6_no_special_population_only"] = "fail:임신/소아 한정 근거 일반화" if preg_only else "pass"
    # L7 quote boundary / stray marker / 섹션 헤딩 fragment
    stray = bool(re.search(r"[.\)]\s+\d+\s*$", q)) or q.strip().endswith(" 1") or "○" in q
    if rec.get("_copy_change", {}).get("kind") == "quote_trim":
        L["L7_quote_boundary"] = "copy_change:quote stray marker trimmed" if not stray else "fail:트림 후에도 stray 잔존"
        flags.append("copy_change:quote_trim")
    elif stray:
        L["L7_quote_boundary"] = "fail:stray marker/헤딩 fragment"
    else:
        L["L7_quote_boundary"] = "pass"
    if rec.get("_copy_change", {}).get("kind") == "display_reframe":
        flags.append("copy_change:display_reframe")
    # L8 복용 지시(명령형) 금지 + 검사/처방 지시 금지(모니터링 톤)
    bad_dir = [c for c in DIRECTIVE_CMDS + TEST_TREAT_DIRECTIVE if c in copy_txt]
    L["L8_no_directive"] = "pass" if not bad_dir else f"fail:복용/검사/처방 지시 {bad_dir}"
    # L9 제품/구매/제휴 + 보충 권유(display/management 만 — 라벨 quote 의 '보충한다'는 무관)
    bad_prod = [p for p in PRODUCT_PHRASES if p in copy_txt]
    bad_sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy_txt]
    L["L9_product_supplement"] = "pass" if not bad_prod and not bad_sup else f"fail:{bad_prod}{bad_sup}"
    # L10 기존 live 60 exact 중복(F9 는 전부 신규 영양소 관계)
    L["L10_no_live_dup"] = "pass" if (ing, cp) not in LIVE_PAIRS else f"fail:live 중복 {(ing, cp)}"
    # L11 F1 퀴놀론 / F2 사이클린 / F3 비스포 후보와 혼동
    if ing in F1_QUINOLONES:
        L["L11_no_other_family_overlap"] = f"fail:F1 성분 {ing}"
    elif ing in F2_TETRACYCLINES:
        L["L11_no_other_family_overlap"] = f"fail:F2 성분 {ing}"
    elif ing in F3_BISPHOSPHONATES:
        L["L11_no_other_family_overlap"] = f"fail:F3 성분 {ing}"
    else:
        L["L11_no_other_family_overlap"] = "pass"
    # L12 금칙어 / L13 상담 톤 / L14 항응고·비타민K
    fb = vfp.scan(copy_txt)
    L["L12_forbidden_phrase"] = "pass" if not fb else f"fail:{fb}"
    L["L13_consult_tone"] = "pass" if CONSULT in copy_txt else "fail:상담 톤 없음"
    L["L14_negation_anticoag"] = "pass" if not any(t in q or t in copy_txt for t in ANTICOAG_TERMS) \
        else "fail:항응고/비타민K 혼입"
    # L15 display 소아/골/치아 알람어 비노출(라벨 quote 에는 있을 수 있음 — display 만 검사)
    bad_ped = [t for t in PEDIATRIC_BONE_TERMS if t in copy_txt]
    L["L15_display_no_pediatric_bone"] = "pass" if not bad_ped else f"fail:display 소아/골/치아 알람어 {bad_ped}"
    # L16 영양소 counterpart 정상(약물 category 없음)
    L["L16_nutrient_counterpart"] = "pass" if (ctype == "nutrient" and cp in NUTRIENT_COUNTERPARTS
                                               and not rec.get("counterpart_category")) else f"fail:비영양소 {cp}"

    hard_fail = any(str(v).startswith("fail") for v in L.values())
    if hard_fail:
        verdict = "needs_review"
    elif rec.get("_copy_change"):
        verdict = "survives_with_copy_change"
    else:
        verdict = "survives"
    return L, verdict, flags


# ── 후보별 reviewer note(작업 C soft-flag / downgrade 사유) ──
_LOW_SIGNAL_NOTE = ("카르바마제핀×엽산: 소스 quote('드물게 ... 엽산 결핍증')는 이상반응 열거 안 bare 항목 — 흡수/대사 기전 동사, "
                    "혈청엽산치 'level-direction', 연용-remedy framing 모두 없음('드물게' 빈도). F9 저신호 이상반응 열거"
                    "(adversarial 옥스카르바제핀 강등 패턴 동형) → needs_review. reviewer 가 카르바마제핀 라벨 전문에서 "
                    "엽산 저하 standalone 근거를 확정해야 통합 가능. (카르바마제핀은 ×비타민D 0246 으로 coverage 유지.)")
_REMEDY_NOTE = ("{ing}×비타민D: 라벨은 연용(장기) 골대사 이상 + 비타민D 섭취/투여(remedy)를 적시하나 비타민D '수치 저하' 자체는 "
                "명시 안 함 → display 의 '수치 변화'를 '비타민D와 관련된 주의 문구'로 reframe(copy_change). 효소유도제 vitD "
                "depletion 기전은 유효 → 통합 가능. reviewer 는 카드가 골연화증/구루병 알람으로 읽히지 않는지 확인.")
F9_REVIEWER_NOTES = {
    "RF-F9-0269": ["설파살라진×엽산: '엽산의 흡수가 저하되고...엽산결핍증' 명시(흡수 기전 동사). survives. "
                   "reviewer 는 카드의 '장기간 복용' framing 이 라벨('병용투여 시')과 어긋나지 않는지 확인(설파살라진은 만성 IBD/RA 약)."],
    "RF-F9-0272": ["트리메토프림×엽산: '폴산결핍을 악화시켜 거대적아구성빈혈' + '폴산대사길항제'(DHFR 억제 기전) 명시. survives. "
                   "quote 가 폴산결핍 특수군 caution 이나 길항 기전은 약물 본연(코트리목사졸 포함)이라 일반화 아님."],
    "RF-F9-0246": ["카르바마제핀×비타민D: '혈중25-hydroxy-콜레칼시페롤의 감소' 명시(vitD 직접 저하). survives. "
                   "quote 가 표(table) 추출이라 reviewer 가 라벨 원문 대조 권장."],
    "RF-F9-0242": ["페니토인×엽산: '혈청엽산치 저하' 명시. quote 끝 stray ' 1' 트림(copy_change·quote-trim). survives_with_copy_change."],
    "RF-F9-0252": [_REMEDY_NOTE.format(ing="페노바르비탈")],
    "RF-F9-0243": [_REMEDY_NOTE.format(ing="페니토인")],
    "RF-F9-0255": [_REMEDY_NOTE.format(ing="프리미돈")],
    "RF-F9-0245": ["needs_review(작업 C 강등). " + _LOW_SIGNAL_NOTE],
}


def reverify_all(recs):
    out = {}
    counts = {"survives": 0, "survives_with_copy_change": 0, "needs_review": 0, "hold": 0, "reject": 0}
    for r in recs:
        L, verdict, flags = reverify(r)
        counts[verdict] = counts.get(verdict, 0) + 1
        out[r["candidate_id"]] = {"lens_results": L, "verdict": verdict, "flags": flags,
                                  "reviewer_notes": F9_REVIEWER_NOTES.get(r["candidate_id"], [])}
    return {"per_candidate": out, "counts": counts}


def to_row(rec):
    """reviewer-ready 레코드 → integ.draft_to_live/guard_projected 가 기대하는 row 형태(필드명 어댑터)."""
    seq = str(rec["itemSeq"])
    return {
        "candidate_id": rec["candidate_id"],
        "drug_ingredient": rec["drug_ingredient"],
        "counterpart": rec["counterpart"],
        "counterpart_type": rec["counterpart_type"],
        "counterpart_category": rec.get("counterpart_category"),   # F9 = None(영양소)
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
    """argv → (scope_label, [candidate_id...]). 기본 integrable(=survives+copy_change=7)."""
    integ_ids = _survives_ids(recs)
    by_id = {r["candidate_id"]: r for r in recs}
    survives = [c for c in integ_ids if not by_id[c].get("_copy_change")]
    copy_change = [c for c in integ_ids if by_id[c].get("_copy_change")]
    folate, vitd = _scope_split(recs)
    if "--candidate-ids" in sys.argv:
        i = sys.argv.index("--candidate-ids")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        want = [c.strip() for c in raw.split(",") if c.strip()]
        return "custom", want
    if "--scope" in sys.argv:
        i = sys.argv.index("--scope")
        s = sys.argv[i + 1] if i + 1 < len(sys.argv) else "integrable"
        return {"integrable": ("integrable", integ_ids),
                "survives": ("survives", survives),
                "copy_change": ("copy_change", copy_change),
                "folate": ("folate", folate),
                "vitd": ("vitd", vitd)}.get(s, ("integrable", integ_ids))
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
    """scope_ids(F9 ∩ 통합 가능) → projected entries. live 무수정. needs_review 는 STOP. (entries, viol)."""
    recs, _summary = load_f9()
    by_id = {r["candidate_id"]: r for r in recs}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in scope_ids:
        rec = by_id.get(cid)
        if rec is None:
            viol.append(f"{cid}: F9 reviewer-ready 집합에 없음")
            continue
        _L, verdict, _f = reverify(rec)
        if verdict not in ("survives", "survives_with_copy_change"):
            viol.append(f"{cid}: 재검증 verdict={verdict} (통합 가능 아님 — needs_review 통합 금지·reviewer 근거 확정 요)")
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
            "projected_id": nid,
            "counterpart_type": rec["counterpart_type"],
            "counterpart": rec["counterpart"],
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


# ── reviewer 노트 인터록(F9 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date", "<scope")
SCOPE_MARKERS = ("scope", "범위")
REVIEWER_ID_RE = re.compile(r"검수자|검토자|reviewer|RPH|PM[ \t]*승인")
GROUPING_MARKERS = ("grouping", "묶음", "개별", "by-nutrient", "성분별", "영양소별", "한 번에", "subset", "wave")
NUTRIENT_MARKERS = ("엽산", "비타민D", "비타민 D")     # 영양소 monitoring 대상 명시
MONITORING_TONE_MARKERS = ("모니터링", "정기", "수치 확인 문의", "검사 지시 아님", "처방 아님", "참고", "monitoring")
CHRONIC_MARKERS = ("장기", "연용", "만성", "장기간")    # 장기복용 framing 결정
NEEDS_REVIEW_ACK_MARKERS = ("RF-F9-0245", "카르바마제핀")  # 0245 needs_review 인지
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음",
                       "제품·구매·제휴·보충제 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("엽산·비타민D 보충 권유 없음", "보충 권유 없음", "보충 권유 아님",
                          "영양제 복용 권유 없음", "복용 권유 없음", "섭취 권유 없음")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|보충제?[ \t]*추천)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_RECO_RE = re.compile(
    r"(엽산|비타민\s*D|철분|보충제|영양제)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")
# ⚠️ permission 단어(허용/추가/노출/승인)가 반드시 뒤따라야 매치 — '검사 지시 아님'(모니터링 톤 마커) false-positive 방지.
TEST_TREAT_PERMISSION_RE = re.compile(
    r"(검사|처방|투여)[ \t]*(지시|받으세요|하세요|권고)[ \t]*(허용|추가|노출|승인)"
    r"|(검사|처방)[ \t]*지시[ \t]*(문구[ \t]*)?(허용|추가)")
# 소아/임신/골/치아 문맥 또는 계열 일반화 허용 — 금지
GENERALIZE_PERMIT_RE = re.compile(
    r"(소아|임신|수유|치아|구루병|골연화증|골다공증|골절|성장기|계열|효소유도제 일반)[^\n]{0,24}(일반화|확대|간주)[ \t]*(승인|허용|가능|함|적용)"
    r"|(일반화|확대)[ \t]*(승인|허용)")


def check_reviewer_note(reviewer_note, scope_ids):
    """F9 live 통합 reviewer 노트 게이트. (note, violations). 빈 리스트 = 통과. main()/테스트 공유.
    scope_ids = 이번 통합 대상(노트가 전건 명시 + scope 일치해야 함)."""
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
        bad.append("scope 선언 미명시(integrable/survives/copy_change/folate/vitd/명시 ids)")
    if not any(m in note for m in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(한 번에/영양소별/by-nutrient/wave/subset)")
    if not any(m in note for m in NUTRIENT_MARKERS):
        bad.append("영양소 monitoring 대상(엽산/비타민D) 명시 누락")
    if not any(m in note for m in MONITORING_TONE_MARKERS):
        bad.append("모니터링 톤(검사 지시·처방 아님·참고/정기 확인 문의) 결정 미명시")
    if not any(m in note for m in CHRONIC_MARKERS):
        bad.append("장기/연용 복용 framing 결정 미명시")
    if not any(m in note for m in NEEDS_REVIEW_ACK_MARKERS):
        bad.append("RF-F9-0245(카르바마제핀×엽산) needs_review 인지 미명시")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품 추천 아님 명시 필요")
    if not any(m in note for m in NOT_SUPPLEMENT_MARKERS):
        bad.append("엽산·비타민D 보충/영양제 복용 권유 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품/보충 추천 허용 문구 — 금지")
    if SUPPLEMENT_RECO_RE.search(note):
        bad.append("엽산·비타민D·철분/영양제 보충/복용 권유/권장 허용 문구 — 금지")
    if TEST_TREAT_PERMISSION_RE.search(note):
        bad.append("검사/처방/투여 지시 카피 허용 문구 — 금지(모니터링 톤)")
    if GENERALIZE_PERMIT_RE.search(note):
        bad.append("소아/임신/골/치아 문맥 또는 family/효소유도제 계열 일반화 허용 문구 — 금지")
    return note, bad


def _index_impact(recs, integrated_ids):
    """full index/aliases 영향(읽기전용). pool=aliases.verified_item_seqs 라 relation 과 decoupled →
    relation-only 통합 자동 flip 0. 6개 약물 모두 name_only·in_aliases=false → alias-enrich(별도) 시에만 조건부 latent."""
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
        latent = name_only if not in_al else 0
        latent_all += latent
        integrated = ing in integrated_ings
        if integrated:
            latent_now += latent
        per[ing] = {"index_items": len(matched), "covered_by_relation": covered,
                    "name_only": name_only, "in_aliases": in_al,
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
        "interpretation": "F9 6개 약물(설파살라진/카르바마제핀/트리메토프림/페노바르비탈/페니토인/프리미돈)은 모두 full index sample 에서 "
                          "name_only·in_aliases=false. full index/aliases 는 export relations 와 decoupled(pool=aliases.verified_item_seqs·"
                          "런타임 재생성·fail-soft) → relation-only 통합은 자동 flip 0·relation_card 1168/name_only 16412 불변(통합 차단 아님). "
                          "통합분을 verified_item_seqs 로 alias-enrich 하면(별도 alias 작업·본 라운드 미수행) 조건부 latent flip "
                          f"(현 scope ≤{latent_now} · 통합 가능 전체 ≤{latent_all}).",
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
    recs, summary = load_f9()
    scope_label, scope_ids = resolve_scope(recs)
    entries, viol = build_subset(exp, scope_ids)
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== F9 만성복용 depletion {scope_label}({len(entries)}건) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    print(f"재검증(작업 C): {summary['counts']} (survives+copy_change 만 통합 가능 — 0245 needs_review)")
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
        integ_ids = _survives_ids(recs)
        by_id = {r["candidate_id"]: r for r in recs}
        survives = [c for c in integ_ids if not by_id[c].get("_copy_change")]
        copy_change = [c for c in integ_ids if by_id[c].get("_copy_change")]
        needs_review = [r["candidate_id"] for r in recs if r["candidate_id"] not in integ_ids]
        folate, vitd = _scope_split(recs)
        base_override = _base_count()

        def scope_proj(cids):
            return {"count": len(cids), "expected_count": before + len(cids),
                    "expected_ids": list(range(base_max + 1, base_max + 1 + len(cids))),
                    "candidate_ids": cids}
        scope_scenarios = {
            "recommended": "by-nutrient 2-wave: folate 3(60→63) → vitd 4(63→67). 또는 integrable 7 한 번에(60→67). "
                           "0245(카르바마제핀×엽산)은 저신호 이상반응 열거 → needs_review, reviewer standalone 근거 확정 전까지 통합 불가.",
            "integrable": scope_proj(integ_ids),
            "survives": scope_proj(survives),
            "copy_change": scope_proj(copy_change),
            "folate": scope_proj(folate),
            "vitd": scope_proj(vitd),
            "conditional_if_0245_resolved": {
                "candidate_ids": needs_review,
                "expected_count_added": len(needs_review),
                "expected_count_after_with_integrable": before + len(integ_ids) + len(needs_review),
                "note": "reviewer 가 카르바마제핀 라벨 전문에서 엽산 저하 standalone 근거를 확정하면 0245 통합 가능 → "
                        "integrable 7 + 1 = 8 → 60→68. 현재는 needs_review 라 통합 대상 아님(저신호 열거).",
            },
            "scenario_on_f1f2f3_true_base": {
                "baseline": TRUE_BASE_F1F2F3,
                "expected_after_integrable": TRUE_BASE_F1F2F3 + len(integ_ids),
                "expected_after_conditional_full": TRUE_BASE_F1F2F3 + len(integ_ids) + len(needs_review),
                "note": "F1 18 + F2 5 + F3 1 모두 live(60→84) 면 F9 integrable 7 은 84→91(conditional 0245 포함 84→92). "
                        "runtime max+1 자동 조정.",
            },
            "base_count_override": base_override,
            "id_rule": "id 는 runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. F1/F2/F3 먼저면 자동 조정.",
        }

        ok_all, tail_all = integ.run_v0_2(integ._sim_with(exp, projected)) if projected else (True, "n/a(0건)")
        index_impact = _index_impact(recs, [e["candidate_id"] for e in entries])

        live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
        dup = [f"{r['ingredient']}×{r['nutrient']}" for r in projected
               if (r["ingredient"], r["nutrient"]) in live_pairs]

        # ── 작업 B/C 인벤토리 ──
        inventory = {
            "meta": {
                "name": "f9_chronic_depletion_inventory_v1_4",
                "status": "DRAFT-ONLY — NOT LIVE / live_integration_forbidden=true / 적대검증 reviewer-ready 8 + F9 family 재검증",
                "purpose": "F9 만성복용 depletion reviewer-ready 8건 감사 + 작업 C family-specific 재검증(16 렌즈·refute-by-default). "
                           "reviewer package/integrator 의 단일 소스.",
                "family": "F9 Chronic-use depletion × 엽산/비타민D (mechanism=depletion·action=monitoring)",
                "audited": F9_REVIEWER_READY_COUNT, "reviewer_ready_adversarial": F9_REVIEWER_READY_COUNT,
                "reverify_counts": summary["counts"],
                "integrable_count": len(integ_ids), "integrable_ids": integ_ids,
                "survives_ids": survives, "copy_change_ids": copy_change, "needs_review_ids": needs_review,
                "counterpart_split_integrable": {"엽산": len(folate), "비타민D": len(vitd)},
                "ingredients_reviewer_ready": sorted({r["drug_ingredient"] for r in recs}),
                "ingredients_integrable": sorted({by_id[c]["drug_ingredient"] for c in integ_ids}),
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "confirmed_at": CONFIRMED_AT,
                "headline_finding_1_low_signal_0245": "카르바마제핀×엽산(0245): quote '드물게 ... 엽산 결핍증' 은 이상반응 열거 안 bare 항목 — "
                    "흡수/대사 기전 동사·혈청엽산치 level-direction·연용-remedy framing 모두 없음('드물게' 빈도). F9 저신호 이상반응 열거 → "
                    "needs_review(reviewer standalone 근거 확정 요). 카르바마제핀은 ×비타민D(0246) 로 coverage 유지.",
                "headline_finding_2_vitd_remedy_copy_change": "페노바르비탈/페니토인/프리미돈 × 비타민D(0252/0243/0255): 연용 골대사 이상 + "
                    "비타민D 섭취/투여(remedy). 라벨은 vitD '수치 저하' 자체 미명시 → display '수치 변화'를 '비타민D와 관련된 주의 문구'로 "
                    "reframe(copy_change). 효소유도제 vitD depletion 관계는 유효 → 통합 가능.",
                "headline_finding_3_quote_hygiene_0242": "페니토인×엽산(0242): '혈청엽산치 저하' 명시(strong) — quote 끝 stray ' 1' 트림(copy_change·quote-trim).",
                "note": "통합 가능 = 자동 적대검증 + F9 family 재검증 통과(survives+copy_change)를 의미하며 임상 검수 완료·식약처 승인·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 별도 PM + clinical reviewer note + 별도 PR.",
            },
            "candidates": [
                {
                    "candidate_id": r["candidate_id"], "relation": r["relation"],
                    "drug_ingredient": r["drug_ingredient"], "counterpart": r["counterpart"],
                    "counterpart_type": r["counterpart_type"], "counterpart_category": r.get("counterpart_category"),
                    "itemSeq": r["itemSeq"], "source_product": None, "source_section": r["source_section"],
                    "source_quote": r["source_quote"], "mechanism": r["mechanism"],
                    "recommended_action": r["recommended_action"], "evidence_level": r["evidence_level"],
                    "confidence": r.get("confidence"), "risk_level": r.get("risk_level"),
                    "display_copy": r["display_copy"], "management_copy": r.get("management_copy"),
                    "product_link_allowed": False, "potassium_safety_card": False,
                    "adversarial_verdict": r.get("adversarial_verdict"),
                    "reverify": summary["per_candidate"][r["candidate_id"]],
                    "copy_change": r.get("_copy_change"),
                    "live_integration_forbidden": True, "published": False,
                    "clinical_reviewed": False, "reviewed_by": "",
                }
                for r in recs
            ],
        }
        os.makedirs(os.path.dirname(INVENTORY_ARTIFACT), exist_ok=True)
        with open(INVENTORY_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(inventory, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── 작업 K index impact ──
        with open(INDEX_IMPACT_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump({"meta": {"name": "f9_chronic_depletion_index_impact_v1_4",
                                "status": "ANALYSIS — read-only / no index/alias write",
                                "purpose": "F9 통합 시 full index/relation_card/name_only/aliases 영향 분석.",
                                "confirmed_at": CONFIRMED_AT},
                       "impact": index_impact}, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── 작업 G dry-run ──
        artifact = {
            "meta": {
                "name": "f9_chronic_depletion_live_dryrun_v1_4",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "F9 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_f9_chronic_depletion_dryrun_v1_4.py 가 안전·계약을 검증.",
                "requested_scope": scope_label,
                "baseline_relations": before, "baseline_max_id": base_max,
                "expected_relation_count_before": before,
                "expected_relation_count_after": after,
                "expected_relation_count_after_integrable": before + len(integ_ids),
                "expected_relation_count_after_survives": before + len(survives),
                "expected_relation_count_after_copy_change": before + len(copy_change),
                "expected_relation_count_after_conditional_full": before + len(integ_ids) + len(needs_review),
                "expected_ids": ids,
                "included_candidate_ids": [e["candidate_id"] for e in entries],
                "all_f9_reviewer_ready_ids": [r["candidate_id"] for r in recs],
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
                    "nutrient_target_decision": "엽산/비타민D(영양소 monitoring·약물 category 없음)",
                    "monitoring_tone_decision_required": True,
                    "chronic_framing_decision_required": True,
                    "needs_review_ack_required": "RF-F9-0245(카르바마제핀×엽산) needs_review 인지",
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id(scope 전건)/scope/grouping/영양소/모니터링톤/장기framing/"
                               "0245 ack/verified_reference 누락 · clinical_reviewed=true·제품추천·엽산/비타민D 보충 권유·검사/처방 지시·"
                               "소아/골/치아·family/효소유도제 계열 일반화 허용",
                    "template": "docs/MediStack_reviewer_package_f9_chronic_depletion_v1_4.md §reviewer-note",
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
                    "all_depletion_mechanism": all(r["mechanism"] == "depletion" for r in projected),
                    "all_monitoring_action": all(r["recommended_action"] == "monitoring" for r in projected),
                    "all_nutrient_no_category": all("counterpart_category" not in r for r in projected),
                    "all_nutrient_folate_or_vitd": all(r["nutrient"] in NUTRIENT_COUNTERPARTS for r in projected),
                    "no_needs_review_integrated": all(e["reverify_verdict"] in ("survives", "survives_with_copy_change")
                                                      for e in entries),
                    "no_display_pediatric_bone": all(not any(t in (r.get("display_text_ko", "") + " " + r.get("management_ko", ""))
                                                             for t in PEDIATRIC_BONE_TERMS) for r in projected),
                },
                "duplicate_summary": {"exact_dup_with_live": dup,
                                      "note": "F9 약물(설파살라진/카르바마제핀/트리메토프림/항전간제)·영양소(엽산/비타민D)는 live 60 에 미존재 → "
                                              "exact dup 0. 엽산/비타민D 는 live 신규 nutrient(기존: 칼슘/철분/아연/마그네슘/칼륨/B12/제산제)."},
                "conflict_summary": {
                    "live_60": "exact dup 0(F9 성분·영양소 전부 신규). depletion/monitoring 렌더는 live 메트포르민×B12(id12) 선례.",
                    "f1_quinolone_18": "퀴놀론(록사신)×광물/제산제 — 성분/관계 다름·충돌 0(F9=만성 depletion).",
                    "f2_tetracycline_5": "사이클린×광물/제산제 — 성분/관계 다름·충돌 0.",
                    "f3_bisphosphonate_1": "비스포×Al/Mg제산제 — 성분/관계 다름·충돌 0.",
                    "penicillamine_2": "성분/counterpart 무관 — 충돌 0.",
                    "theme_map_6": "지용성비타민/세팔로/페니실라민 — F9 무관·충돌 0.",
                    "potassium_4": "이뇨제×칼륨(K-sparing 아님) — F9(엽산/비타민D depletion)와 무관·충돌 0.",
                    "at_fex_1": "펙소페나딘×제산제 — F9 무관·충돌 0.",
                    "carbamazepine_folate_needs_review": "0245(카르바마제핀×엽산)은 저신호 이상반응 열거 → 통합 대상 아님(needs_review). "
                                                         "단 카르바마제핀×비타민D(0246)는 통합 가능(다른 counterpart·strong quote).",
                    "other_factory_families": "F4/F6/F10 reviewer-ready — 성분/관계 다름·충돌 0.",
                    "full_factory_integrator_dedup": "차후 factory 일괄 integrator 는 (ingredient, counterpart/category) 키로 본 F9 통합분을 "
                                                     "skip 해야 함(중복 생성 금지).",
                },
                "full_index_alias_impact": index_impact,
                "v0_2_validator_evidence": {
                    "sim_all_passed": ok_all, "sim_all_tail": tail_all,
                    "interpretation": "depletion/monitoring 영양소(엽산/비타민D·category 생략) 현행 v0.2 validator PASS "
                                      "(live 메트포르민×B12 동일 shape) → 선행조건 0.",
                },
                "render_safety_summary": f"통합 가능 {len(integ_ids)}건 = depletion/monitoring 영양소 카드(메트포르민×B12 렌더 경로). src 변경 불필요. "
                                         "비타민D copy_change 3건은 골질환 알람어 비노출 display.",
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
              f"latent flip(현 scope)={index_impact['latent_flip_if_alias_enriched_this_scope']} · "
              f"통합 가능 전체 alias-enrich 시 latent≤{index_impact['latent_flip_if_alias_enriched_all_integrable']}(별도 작업).")
        print(f"[dry-run] needs_review 1(0245 카르바마제핀×엽산) — 통합 제외(저신호 이상반응 열거·reviewer 근거 확정 요).")
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
        (" | F9 만성복용 depletion %s(%d건) live 통합: 약물×엽산/비타민D(depletion·monitoring). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (scope_label, len(projected), before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE F9 CHRONIC DEPLETION ({scope_label}): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
