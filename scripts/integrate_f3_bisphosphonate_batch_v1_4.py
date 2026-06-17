#!/usr/bin/env python3
"""
integrate_f3_bisphosphonate_batch_v1_4.py
MediStack — Relation Factory v1.4 **F3 비스포스포네이트** live 통합 **준비/드라이런** 스크립트.
integrate_f2_tetracycline_batch_v1_4.py / integrate_f1_quinolone_batch_v1_4.py 패턴 승계
(reviewer-ready batch → F3 + family-specific 재검증(작업 C)).

대상(소스: data/drafts/relation_factory_reviewer_ready_batch_v1_4.json · family==F3):
  reviewer-ready(적대검증) 3건:
    RF-F3-0147  이반드론산 × Al/Mg 함유 제산제(약물)  — al_mg_antacid(id61 선례)
    RF-F3-0148  에티드론산 × 칼슘                     — nutrient(?)
    RF-F3-0149  에티드론산 × 철분                     — nutrient(?)
  drug ingredient: 이반드론산(=live ×칼슘/철분/마그네슘 이미 존재)·에티드론산(신규)

⚠️⚠️ **작업 C(F3 family-specific 재검증, reverify(), refute-by-default) 결과 — 적대검증과 다름**:
  survives 1 · survives_with_copy_change 0 · **needs_review 2** · hold 0 · reject 0.
  ── 헤드라인 발견 ①(에티드론산 0148/0149 강등) ──
    소스 quote("미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제")는
    문법상 양이온 목록이 **'…이 고농도로 함유된 제산제'에 결속**된다(제산제의 함유 성분). 즉 standalone
    칼슘/철분 '보충제'가 아니라 **칼슘/철분 고함유 제산제**를 가리킨다. 별도 standalone 항목은 '미네랄이 첨가된
    비타민제'(종합비타민)뿐. → 에티드론산×칼슘/철분의 **standalone nutrient 분류는 원문 근거 취약** → needs_review.
    live(알렌/리세/이반×칼슘/철분)은 *다른 약물 라벨*(포사맥스 등)에 '칼슘보충제' 명시가 있어 통합된 것 →
    에티드론산에 그 선례를 적용하면 **계열 일반화(금지)**. 따라서 reviewer 가 에티드론산 라벨 전문에서
    standalone 칼슘/철분 근거(또는 '미네랄 첨가 비타민제'→종합비타민 매핑)를 확정해야 함.
  ── 헤드라인 발견 ②(이반드론산 0147 overlap) ──
    이반드론산은 **live 에 ×칼슘(id41)/철분(id51)/마그네슘(id52)** 이미 존재 → Al/Mg 제산제(약물·al_mg_antacid)
    relation 추가가 정보 가치(제산제 제품 맥락) vs 중복인지 reviewer 판단(id61·F2 독시/미노 선례). exact dup 아님.

따라서 **F3 통합 가능(survives) = 1건(0147)** 뿐이며, 그조차 overlap 판단을 요한다.
0148/0149 는 reviewer 의 에티드론산 라벨 parse 확정 전까지 통합 불가(needs_review).

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만 수행
(별도 PM 승인 + clinical reviewer 전까지 절대 금지·본 세션 호출 안 함).
  dry-run = 라이브/보호 데이터 **무수정** + 예상 산출물 기록:
    data/review/f3_bisphosphonate_inventory_v1_4.json     (작업 B/C — 3 reviewer-ready 감사 + family 재검증 렌즈)
    data/review/f3_bisphosphonate_live_dryrun_v1_4.json   (작업 G — scope별 예상 count/id + 가드 + 충돌 + v0.2 증거)
    data/review/f3_bisphosphonate_index_impact_v1_4.json  (작업 K — full index/aliases 영향)

scope(작업 D grouping):
  --scope survives   (기본) survives 만 = [0147] — 60→61 · id (runtime max+1)
  --scope antacid1   이반드론산×Al/Mg제산제 1건 = [0147] — 60→61
  --candidate-ids A,B,...  명시 후보(F3 ∩ survives 만; needs_review 는 build_subset 에서 STOP)
  ⚠️ nutrient 2건(0148/0149)은 needs_review — scope 로 요청해도 통합 거부(STOP). reviewer parse 확정 후 별도.

live 통합 선행조건: **없음(0)**. al_mg_antacid(id61) 렌더 경로는 현행 v0.2 validator + src 가 지원(live 이반드론산×광물 동일 약물).
  full index: 이반드론산은 이미 covered(73 relation_card·verified_item_seqs). 에티드론산은 index sample 1건 name_only(in_aliases=false)
  — 단 0148/0149 는 needs_review 라 본 scope 통합 대상 아님 → 에티드론산 latent flip 은 reviewer parse 확정+통합+alias 등록 시에만(조건부).
  full index/aliases 는 relation export 와 decoupled(pool=aliases.verified_item_seqs) → relation-only 통합 자동 flip 0(1168/16412 불변).

사용:
  python3 scripts/integrate_f3_bisphosphonate_batch_v1_4.py                                   # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_f3_bisphosphonate_batch_v1_4.py --scope antacid1                  # dry-run(특정 scope)
  python3 scripts/integrate_f3_bisphosphonate_batch_v1_4.py --pm-approved --reviewer-note X     # live(별도 PM·reviewer 후·본 세션 금지)
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
INVENTORY_ARTIFACT = os.path.join(DATA, "review", "f3_bisphosphonate_inventory_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "f3_bisphosphonate_live_dryrun_v1_4.json")
INDEX_IMPACT_ARTIFACT = os.path.join(DATA, "review", "f3_bisphosphonate_index_impact_v1_4.json")

BASELINE_RELATIONS = 60      # F1/F2/AT-FEX/칼륨/theme/페니실라민 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-17"  # source-check + 적대검증 + F3 family 재검증 확인일
F3_REVIEWER_READY_COUNT = 3  # 적대검증 reviewer-ready(0147/0148/0149)
F3_SURVIVES_COUNT = 1        # 작업 C family 재검증 통과(0147)


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
PEDIATRIC_BONE_TERMS = ["소아", "임신", "수유", "치아", "착색", "성장기", "골형성", "골다공증성 골절"]
CONSULT = "약사 또는 의사"

# ── 작업 C copy_change(F3 family 재검증) — source_quote hygiene(원문 끝 '○ 파제트병' 섹션 헤딩 fragment 트림) ──
# ⚠️ 0148/0149 는 별도로 standalone-nutrient parse 취약으로 needs_review 강등됨(L3). copy_change 는 hygiene 만 기록·
#    cleaned 는 original_full 의 verbatim 부분문자열(위조 차단). batch 에는 cleaned 가 이미 반영됨.
_ETID_FULL = "미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제 ○ 파제트병"
_ETID_CLEAN = "미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제"
F3_COPY_CHANGES = {
    "RF-F3-0148": {"field": "source_quote", "original_full": _ETID_FULL, "cleaned": _ETID_CLEAN,
                   "reason": "원문 끝 '○ 파제트병'(파제트병=적응증 항목 머리) 섹션 헤딩 fragment 제거(cleaned 는 original_full 의 verbatim 부분문자열). "
                             "⚠️ 별개로 standalone 칼슘 nutrient parse 취약(L3) → needs_review."},
    "RF-F3-0149": {"field": "source_quote", "original_full": _ETID_FULL, "cleaned": _ETID_CLEAN,
                   "reason": "원문 끝 '○ 파제트병' 섹션 헤딩 fragment 제거(verbatim 부분문자열). "
                             "⚠️ 별개로 standalone 철분 nutrient parse 취약(L3) → needs_review."},
}

NUTRIENT_COUNTERPARTS = {"칼슘", "철분"}     # F3 비스포 nutrient 후보(에티드론산). F2 와 달리 칼슘 포함(에티드론산 라벨은 칼슘을 미네랄 목록에 나열)
ANTACID_CATEGORY = "al_mg_antacid"
# 라벨 문장에서 nutrient counterpart 직접언급 토큰(F3 에티드론산 quote 는 '칼슘'/'철분' verbatim — F2(철→철)와의 family 차이)
NUTRIENT_QUOTE_TOKEN = {"칼슘": "칼슘", "철분": "철분"}
# standalone-nutrient parse 취약 패턴: counterpart 가 '… 함유된 제산제' 양이온 목록 안에만 나타남(제산제 결속).
_ANTACID_CATION_TAIL_RE = re.compile(r"(고농도로\s*)?함유(되어\s*있|된|하고\s*있)?[^\n]{0,6}제산제")

# 라이브 60 컨텍스트(L11 live 중복 · L12 다른 family overlap 렌즈에서 참조)
_exp_cache = json.load(open(EXPORT, encoding="utf-8"))
LIVE_PAIRS = {(r.get("ingredient"), r.get("nutrient")) for r in _exp_cache["relations"]}
LIVE_BISPHOSPHONATE = sorted({r["ingredient"] for r in _exp_cache["relations"]
                              if r.get("ingredient", "").endswith("드론산")})
F1_QUINOLONES = {"노르플록사신", "레보플록사신", "로메플록사신", "발로플록사신", "오플록사신",
                 "자보플록사신", "토수플록사신", "페플록사신", "시프로플록사신", "목시플록사신"}
F2_TETRACYCLINES = {"테트라사이클린", "독시사이클린", "미노사이클린"}


def _scope_split(recs):
    nutrient = [r["candidate_id"] for r in recs if r["counterpart_type"] == "nutrient"]
    antacid = [r["candidate_id"] for r in recs if r.get("counterpart_category") == ANTACID_CATEGORY]
    return nutrient, antacid


def _survives_ids(recs):
    out = []
    for r in recs:
        _L, verdict, _f = reverify(r)
        if verdict in ("survives", "survives_with_copy_change"):
            out.append(r["candidate_id"])
    return out


def load_f3():
    """reviewer-ready batch → F3 3건(적대검증 reviewer-ready) + copy_change 출처 기록 + family 재검증.
    (records, reverify_summary) 반환. live 무수정."""
    rr = json.load(open(REVIEWER_READY, encoding="utf-8"))
    f3 = [dict(r) for r in rr["reviewer_ready_relations"] if r.get("family") == "F3"]
    for r in f3:
        cc = F3_COPY_CHANGES.get(r["candidate_id"])
        if cc:
            # batch 의 source_quote(=cleaned)가 original_full 의 verbatim 부분문자열인지(위조 차단).
            assert cc["cleaned"] in cc["original_full"], \
                f"{r['candidate_id']}: cleaned 가 original_full 부분문자열 아님 — 카피 위조 차단"
            assert r[cc["field"]] == cc["cleaned"], \
                f"{r['candidate_id']}: batch source_quote 가 cleaned 와 불일치 — 무결성 위반"
            r["_copy_change"] = cc
    summary = reverify_all(f3)
    return f3, summary


def reverify(rec):
    """F3 family-specific 재검증(refute-by-default). (lens_results, verdict, flags).
    핵심 = L3_standalone_nutrient_support: nutrient counterpart 가 '…함유된 제산제' 양이온 목록 안에만
    나타나면(standalone 보충제 근거 없음) FAIL → needs_review(에티드론산 0148/0149)."""
    q = rec.get("source_quote", "") or ""
    disp = rec.get("display_copy", "") or ""
    mng = rec.get("management_copy", "") or ""
    copy_txt = f"{disp} {mng}"
    cp = rec.get("counterpart", "")
    ctype = rec.get("counterpart_type", "")
    cat = rec.get("counterpart_category")
    ing = rec.get("drug_ingredient", "")
    L = {}
    flags = []

    # L1 성분명↔itemSeq(실값·section). 실제 국내 품목 매칭은 reviewer Q(자동 fail 아님).
    seq = str(rec.get("itemSeq", ""))
    L["L1_source_fidelity"] = "pass" if (seq.isdigit() and len(seq) >= 8 and rec.get("source_section")) \
        else "fail:itemSeq/section"
    # L2 counterpart 직접 언급(에티드론산 quote 는 '칼슘'/'철분' verbatim)
    if ctype == "nutrient":
        token = NUTRIENT_QUOTE_TOKEN.get(cp, cp)
        L["L2_direct_cooccurrence"] = "pass" if token in q else f"fail:{cp}({token}) 미언급"
    else:  # al_mg_antacid 약물
        L["L2_direct_cooccurrence"] = "pass" if ("제산제" in q and ("알루미늄" in q or "마그네슘" in q)) \
            else "fail:Al/Mg제산제 미언급"
    # ★ L3 standalone nutrient 근거(F3 핵심 family 렌즈) — 양이온이 '…함유된 제산제' 안에만 결속되면 standalone 아님.
    if ctype == "nutrient":
        token = NUTRIENT_QUOTE_TOKEN.get(cp, cp)
        # token 이 등장하는 위치 뒤로 '…함유된 제산제' 가 이어지면(제산제 결속), 그리고 token 의 별도 standalone 언급이 없으면 fail.
        m = _ANTACID_CATION_TAIL_RE.search(q)
        cation_in_antacid_clause = bool(m) and (token in q[:m.end()]) and (token not in q[m.end():])
        # standalone 단서: 'token 보충제'/'token 제제'/'token 함유 식품/제품' 처럼 제산제 외 맥락.
        standalone_cue = any(p in q for p in (f"{token}보충제", f"{token} 보충제", f"{token} 함유 식품",
                                              f"{token}제", f"{token} 제제", f"{token}을 함유", f"{token}이 함유된 식품"))
        if cation_in_antacid_clause and not standalone_cue:
            L["L3_standalone_nutrient_support"] = (
                f"fail:{cp} 양이온이 '…함유된 제산제'에 결속(제산제 함유 성분) — standalone 보충제 근거 없음. "
                "별도 standalone 항목은 '미네랄 첨가 비타민제'(종합비타민)뿐 → 계열 일반화 금지·reviewer parse 확정 요")
        else:
            L["L3_standalone_nutrient_support"] = "pass"
    else:
        L["L3_standalone_nutrient_support"] = "n/a:약물 counterpart"
    # L4 Al/Mg 제산제 vs Mg 영양제 혼동
    if cat == ANTACID_CATEGORY:
        L["L4_antacid_vs_mg_nutrient"] = "pass" if ("약물" in cp and cp != "마그네슘") else "fail:Mg영양제 혼동"
    elif ctype == "nutrient":
        L["L4_antacid_vs_mg_nutrient"] = "pass" if cp in NUTRIENT_COUNTERPARTS else f"fail:비영양소 counterpart {cp}"
    else:
        L["L4_antacid_vs_mg_nutrient"] = "fail:분류 불명"
    # L5 흡수저하/킬레이트 방향
    L["L5_direction"] = "pass" if (("흡수" in q) and ("저하" in q or "저해" in q or "감소" in q or "방해" in q)
                                   or "킬레이트" in q) else "fail:방향 불명"
    # L6 소아/임신/골/치아 문맥을 흡수저하 relation 으로 오인 안 함
    L["L6_no_pediatric_bone"] = "pass" if not any(t in q for t in PEDIATRIC_BONE_TERMS) \
        else "fail:소아/임신/골/치아 문맥 혼입"
    # L7 quote boundary / stray marker / 섹션 헤딩 fragment('○ …')
    stray = bool(re.search(r"[.\)]\s+\d+\s*$", q)) or q.strip().endswith(" 1") or "○" in q
    if rec.get("_copy_change"):
        # copy_change(헤딩 fragment 트림)가 실제로 '○' 를 제거했는지 확인.
        L["L7_quote_boundary"] = "copy_change:heading fragment trimmed" if "○" not in q else "fail:헤딩 fragment 잔존"
        flags.append("copy_change")
    elif stray:
        L["L7_quote_boundary"] = "fail:stray marker/헤딩 fragment"
    else:
        L["L7_quote_boundary"] = "pass"
    # L8 복용 지시(명령형) 금지
    L["L8_no_directive"] = "pass" if not any(c in copy_txt for c in DIRECTIVE_CMDS) else "fail:복용 지시"
    # L9 제품/구매/제휴 + 보충 권유
    bad_prod = [p for p in PRODUCT_PHRASES if p in copy_txt]
    bad_sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy_txt]
    L["L9_product_supplement"] = "pass" if not bad_prod and not bad_sup else f"fail:{bad_prod}{bad_sup}"
    # L10 기존 live 60 exact 중복(이반드론산 antacid 는 별도 counterpart=id61 선례 → exact dup 아님)
    L["L10_no_live_dup"] = "pass" if (ing, cp) not in LIVE_PAIRS else f"fail:live 중복 {(ing, cp)}"
    # L11 F1 퀴놀론 / F2 사이클린 후보와 혼동
    if ing in F1_QUINOLONES:
        L["L11_no_other_family_overlap"] = f"fail:F1 성분 {ing}"
    elif ing in F2_TETRACYCLINES:
        L["L11_no_other_family_overlap"] = f"fail:F2 성분 {ing}"
    else:
        L["L11_no_other_family_overlap"] = "pass"
    # L12 금칙어 / L13 상담 톤 / L14 항응고
    fb = vfp.scan(copy_txt)
    L["L12_forbidden_phrase"] = "pass" if not fb else f"fail:{fb}"
    L["L13_consult_tone"] = "pass" if CONSULT in copy_txt else "fail:상담 톤 없음"
    L["L14_negation_anticoag"] = "pass" if not any(t in q or t in copy_txt for t in ANTICOAG_TERMS) \
        else "fail:항응고/비타민K 혼입"

    hard_fail = any(str(v).startswith("fail") for v in L.values())
    if hard_fail:
        verdict = "needs_review"
    elif rec.get("_copy_change"):
        verdict = "survives_with_copy_change"
    else:
        verdict = "survives"
    return L, verdict, flags


# ── 후보별 reviewer note(작업 C soft-flag / downgrade 사유) ──
_OVERLAP_NOTE = ("live 에 이반드론산 ×칼슘(id41)/철분(id51)/마그네슘(id52) 이미 존재 → Al/Mg 제산제(약물·al_mg_antacid) "
                 "relation 추가가 정보 가치(제산제 제품 맥락) vs 중복인지 reviewer 판단(id61·F2 독시/미노 선례). "
                 "카드 렌더는 약물 counterpart kicker 로 영양소와 구분.")
_ETID_PARSE_NOTE = ("에티드론산 라벨 quote 의 '칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제'는 "
                    "문법상 양이온이 제산제 함유 성분(제산제 결속)을 의미 → standalone {cp} 보충제 근거 취약. "
                    "별도 standalone 항목은 '미네랄 첨가 비타민제'(종합비타민)뿐. live(타 약물 라벨) 선례 적용은 계열 일반화(금지). "
                    "reviewer 가 에티드론산 라벨 전문에서 standalone {cp} 근거를 확정해야 통합 가능(현재 needs_review).")
F3_REVIEWER_NOTES = {
    "RF-F3-0147": ["이반드론산×Al/Mg제산제: al_mg_antacid(id61 선례)·이반드론산 신규 counterpart. " + _OVERLAP_NOTE,
                   "이반드론산은 신규 성분 아님(live ×칼슘/철분/마그네슘) — F3 통합 가능분은 본 1건뿐."],
    "RF-F3-0148": ["needs_review(작업 C 강등). " + _ETID_PARSE_NOTE.format(cp="칼슘")],
    "RF-F3-0149": ["needs_review(작업 C 강등). " + _ETID_PARSE_NOTE.format(cp="철분")],
}


def reverify_all(recs):
    out = {}
    counts = {"survives": 0, "survives_with_copy_change": 0, "needs_review": 0, "hold": 0, "reject": 0}
    for r in recs:
        L, verdict, flags = reverify(r)
        counts[verdict] = counts.get(verdict, 0) + 1
        out[r["candidate_id"]] = {"lens_results": L, "verdict": verdict, "flags": flags,
                                  "reviewer_notes": F3_REVIEWER_NOTES.get(r["candidate_id"], [])}
    return {"per_candidate": out, "counts": counts}


def to_row(rec):
    """reviewer-ready 레코드 → integ.draft_to_live/guard_projected 가 기대하는 row 형태(필드명 어댑터)."""
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
    """argv → (scope_label, [candidate_id...]). 기본 survives(=family 재검증 통과만 = [0147])."""
    survives = _survives_ids(recs)
    _nutrient, antacid = _scope_split(recs)
    antacid_survives = [c for c in antacid if c in survives]
    if "--candidate-ids" in sys.argv:
        i = sys.argv.index("--candidate-ids")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        want = [c.strip() for c in raw.split(",") if c.strip()]
        return "custom", want
    if "--scope" in sys.argv:
        i = sys.argv.index("--scope")
        s = sys.argv[i + 1] if i + 1 < len(sys.argv) else "survives"
        return {"survives": ("survives", survives),
                "antacid1": ("antacid1", antacid_survives)}.get(s, ("survives", survives))
    return "survives", survives


def build_subset(exp, scope_ids):
    """scope_ids(F3 ∩ survives) → projected entries. live 무수정. needs_review 는 STOP. (entries, viol)."""
    recs, _summary = load_f3()
    by_id = {r["candidate_id"]: r for r in recs}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in scope_ids:
        rec = by_id.get(cid)
        if rec is None:
            viol.append(f"{cid}: F3 reviewer-ready 집합에 없음")
            continue
        _L, verdict, _f = reverify(rec)
        if verdict not in ("survives", "survives_with_copy_change"):
            viol.append(f"{cid}: 재검증 verdict={verdict} (survives 아님 — needs_review 통합 금지·reviewer parse 확정 요)")
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
            "counterpart_category": rel.get("counterpart_category"),
            "recommended_action": rel["recommended_action"],
            "evidence_level": rel["evidence_level"],
            "confidence": rec.get("confidence", ""),
            "adversarial_verdict": rec.get("adversarial_verdict", ""),
            "reverify_verdict": verdict,
            "copy_change": rec.get("_copy_change"),
            "projected_live_relation": rel,
        })
    return entries, viol


# ── reviewer 노트 인터록(F3 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date", "<scope")
SCOPE_MARKERS = ("scope", "범위")
REVIEWER_ID_RE = re.compile(r"검수자|검토자|reviewer|RPH|PM[ \t]*승인")
GROUPING_MARKERS = ("grouping", "묶음", "개별", "by-counterpart", "성분별", "상대성분별", "한 번에", "subset")
ANTACID_MARKERS = ("al_mg_antacid",)    # category 결정(약물 counterpart) — 명시적 category id 요구(bare '제산제'로 불충분)
OVERLAP_MARKERS = ("중복", "overlap", "정보 가치", "추가 노출", "이반드론산")  # 이반드론산 nutrient-overlap 판단 명시
INTERVAL_MARKERS = ("간격", "separation 간격", "시간")  # 분리 간격 노출 결정
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음",
                       "제품·구매·제휴·보충제 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("금속이온", "칼슘·철분 보충 권유 없음", "보충 권유 없음", "보충 권유 아님",
                          "제산제 복용 권유 없음", "복용 권유 없음", "우유·유제품 섭취 권유 없음")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|보충제?[ \t]*추천)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_RECO_RE = re.compile(
    r"(칼슘|철분|제산제|보충제|우유|유제품)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")
# 소아/임신/골/치아 문맥 또는 계열 일반화 허용 — 금지(비스포 라벨 외 맥락 확대·에티드론산 standalone 일반화 차단)
GENERALIZE_PERMIT_RE = re.compile(
    r"(소아|임신|수유|치아|착색|골형성|골절|성장기|계열|에티드론산 standalone)[^\n]{0,24}(일반화|확대|간주)[ \t]*(승인|허용|가능|함|적용)"
    r"|(일반화|확대)[ \t]*(승인|허용)")


def check_reviewer_note(reviewer_note, scope_ids):
    """F3 live 통합 reviewer 노트 게이트. (note, violations). 빈 리스트 = 통과. main()/테스트 공유.
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
        bad.append("scope 선언 미명시(survives/antacid1/명시 ids)")
    if not any(m in note for m in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(한 번에/성분별/상대성분별/subset)")
    if not any(m in note for m in ANTACID_MARKERS):
        bad.append("category 결정 'al_mg_antacid'(Al/Mg 제산제=약물 counterpart·id61 선례) 미명시")
    if not any(m in note for m in OVERLAP_MARKERS):
        bad.append("이반드론산 nutrient-overlap(기존 ×칼슘/철분/마그네슘) 판단 미명시")
    if not any(m in note for m in INTERVAL_MARKERS):
        bad.append("separation 간격(예: 2시간/30분) 카드 노출 여부 결정 미명시")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품 추천 아님 명시 필요")
    if not any(m in note for m in NOT_SUPPLEMENT_MARKERS):
        bad.append("금속이온/제산제/우유·유제품 복용 권유 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품/보충 추천 허용 문구 — 금지")
    if SUPPLEMENT_RECO_RE.search(note):
        bad.append("금속이온/제산제/우유·유제품 복용 권유/권장 허용 문구 — 금지")
    if GENERALIZE_PERMIT_RE.search(note):
        bad.append("소아/임신/골/치아 문맥 또는 계열 일반화(에티드론산 standalone 일반화 포함) 허용 문구 — 금지")
    return note, bad


def _index_impact(recs, integrated_ids):
    """full index/aliases 영향(읽기전용). pool=aliases.verified_item_seqs 라 relation 과 decoupled →
    relation-only 통합은 자동 flip 0. 에티드론산 name_only 1건은 needs_review(0148/0149)라 본 scope 통합 대상 아님 →
    latent flip 은 reviewer parse 확정+통합+alias 등록 시에만(조건부)."""
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    ents = idx["entries"]
    al = json.load(open(ALIASES, encoding="utf-8"))
    al_txt = json.dumps(al, ensure_ascii=False)
    by_id = {r["candidate_id"]: r for r in recs}
    integrated_ings = sorted({by_id[c]["drug_ingredient"] for c in integrated_ids if c in by_id})
    per = {}
    latent_now = 0
    for ing in sorted({r["drug_ingredient"] for r in recs}):
        matched = [e for e in ents if ing in (e.get("ingredient_name") or "")]
        covered = sum(1 for e in matched if e.get("covered_by_relation"))
        name_only = sum(1 for e in matched if not e.get("covered_by_relation"))
        in_al = ing in al_txt
        latent = name_only if not in_al else 0
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
        "latent_flip_if_etidronate_resolved_and_enriched": 1,
        "interpretation": "이반드론산(통합 가능분 0147)은 이미 covered_by_relation(73 relation_card·verified_item_seqs 등록·in_aliases) → "
                          "relation 추가해도 index 영향 0(latent 0). 에티드론산(0148/0149)은 index sample 1건 name_only(in_aliases=false)지만 "
                          "본 scope 에서 needs_review 라 통합 대상 아님 → 현 통합분 latent flip 0. reviewer 가 에티드론산 parse 확정 후 "
                          "0148/0149 통합 + 에티드론산을 verified_item_seqs 등록(별도 alias 작업)하면 1건 flip(1169/16411·조건부). "
                          "full index/aliases 는 export relations 와 decoupled(런타임 재생성·fail-soft) → relation-only 통합은 자동 flip 0·"
                          "relation_card 1168/name_only 16412 불변. 통합 차단 아님.",
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
    recs, summary = load_f3()
    scope_label, scope_ids = resolve_scope(recs)
    entries, viol = build_subset(exp, scope_ids)
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== F3 비스포스포네이트 {scope_label}({len(entries)}건) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    print(f"재검증(작업 C): {summary['counts']} (survives 만 통합 가능 — 0148/0149 needs_review)")
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
        nutrient_ids, antacid_ids = _scope_split(recs)
        survives = _survives_ids(recs)
        needs_review = [r["candidate_id"] for r in recs if r["candidate_id"] not in survives]

        def scope_proj(cids):
            return {"count": len(cids), "expected_count": before + len(cids),
                    "expected_ids": list(range(base_max + 1, base_max + 1 + len(cids))),
                    "candidate_ids": cids}
        scope_scenarios = {
            "recommended": "survives 만 통합(=[0147] 이반드론산×al_mg_antacid) → 60→61. 단 이반드론산 nutrient-overlap "
                           "결정 1건 surface(reviewer). 0148/0149(에티드론산×칼슘/철분)은 standalone parse 취약 → needs_review, "
                           "reviewer 의 에티드론산 라벨 parse 확정 전까지 통합 불가.",
            "survives": scope_proj(survives),
            "antacid1": scope_proj([c for c in antacid_ids if c in survives]),
            "conditional_if_etidronate_parse_resolved": {
                "candidate_ids": [c for c in nutrient_ids if c in needs_review],
                "expected_count_added": len([c for c in nutrient_ids if c in needs_review]),
                "expected_count_after_with_survives": before + len(survives) + len([c for c in nutrient_ids if c in needs_review]),
                "note": "reviewer 가 에티드론산 라벨 전문에서 standalone 칼슘/철분 근거를 확정하면(또는 '미네랄 첨가 비타민제'→종합비타민 "
                        "매핑) 0148/0149 가 통합 가능 → survives 1 + 2 = 3 → 60→63. 현재는 needs_review 라 통합 대상 아님(계열 일반화 금지).",
            },
            "scenario_if_f1_already_live": {
                "baseline": 78, "expected_after_survives": 79, "expected_after_conditional_full": 81,
                "note": "F1 18건(60→78) 먼저 live 면 F3 survives 1건은 78→79(conditional full 78→81). runtime max+1 자동 조정.",
            },
            "scenario_if_f1_and_f2_already_live": {
                "baseline": 83, "expected_after_survives": 84, "expected_after_conditional_full": 86,
                "note": "F1 18 + F2 5(60→83) 먼저 live 면 F3 survives 1건은 83→84(conditional full 83→86). runtime max+1 자동 조정.",
            },
            "id_rule": "id 는 runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. F1/F2/AT-FEX/칼륨/theme/페니실라민 먼저면 자동 조정.",
        }

        ok_all, tail_all = integ.run_v0_2(integ._sim_with(exp, projected)) if projected else (True, "n/a(0건)")
        index_impact = _index_impact(recs, [e["candidate_id"] for e in entries])

        live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
        dup = [f"{r['ingredient']}×{r['nutrient']}" for r in projected
               if (r["ingredient"], r["nutrient"]) in live_pairs]

        # ── 작업 B/C 인벤토리 ──
        inventory = {
            "meta": {
                "name": "f3_bisphosphonate_inventory_v1_4",
                "status": "DRAFT-ONLY — NOT LIVE / live_integration_forbidden=true / 적대검증 reviewer-ready 3 + F3 family 재검증",
                "purpose": "F3 비스포스포네이트 reviewer-ready 3건 감사 + 작업 C family-specific 재검증(14 렌즈·refute-by-default). "
                           "reviewer package/integrator 의 단일 소스.",
                "family": "F3 Bisphosphonate × mineral / Al·Mg 함유 제산제(absorption/separation)",
                "audited": 4, "reviewer_ready_adversarial": F3_REVIEWER_READY_COUNT,
                "reverify_counts": summary["counts"],
                "survives_count": len(survives), "survives_ids": survives, "needs_review_ids": needs_review,
                "counterpart_split_reviewer_ready": {"nutrient": len(nutrient_ids), "al_mg_antacid": len(antacid_ids)},
                "ingredients_reviewer_ready": sorted({r["drug_ingredient"] for r in recs}),
                "ingredients_integrable": sorted({by["drug_ingredient"] for by in recs if by["candidate_id"] in survives}),
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "confirmed_at": CONFIRMED_AT,
                "headline_finding_1_etidronate_parse": "에티드론산 0148/0149: 소스 quote 의 양이온 목록이 '…고농도로 함유된 제산제'에 "
                    "결속(제산제 함유 성분) → standalone 칼슘/철분 보충제 근거 취약. 별도 standalone 항목은 '미네랄 첨가 비타민제'(종합비타민)뿐. "
                    "live(타 약물 라벨) 선례 적용은 계열 일반화(금지) → needs_review(reviewer 가 에티드론산 라벨 parse 확정 요).",
                "headline_finding_2_ibandronate_overlap": "이반드론산 0147: live 에 ×칼슘(id41)/철분(id51)/마그네슘(id52) 이미 존재 → "
                    "Al/Mg 제산제(약물) relation 추가가 정보 가치 vs 중복인지 reviewer 판단(id61·F2 선례). exact dup 아님.",
                "live_bisphosphonate_context": {ing: sorted(r.get("nutrient") for r in _exp_cache["relations"]
                                                            if r.get("ingredient") == ing) for ing in LIVE_BISPHOSPHONATE},
                "note": "survives = 자동 적대검증 + F3 family 재검증 통과를 의미하며 임상 검수 완료·식약처 승인·법적 문제 없음 을 "
                        "의미하지 않는다. live 승격은 별도 PM + clinical reviewer note + 별도 PR.",
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
            json.dump({"meta": {"name": "f3_bisphosphonate_index_impact_v1_4",
                                "status": "ANALYSIS — read-only / no index/alias write",
                                "purpose": "F3 통합 시 full index/relation_card/name_only/aliases 영향 분석.",
                                "confirmed_at": CONFIRMED_AT},
                       "impact": index_impact}, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── 작업 G dry-run ──
        artifact = {
            "meta": {
                "name": "f3_bisphosphonate_live_dryrun_v1_4",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "F3 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_f3_bisphosphonate_dryrun_v1_4.py 가 안전·계약을 검증.",
                "requested_scope": scope_label,
                "baseline_relations": before, "baseline_max_id": base_max,
                "expected_relation_count_before": before,
                "expected_relation_count_after": after,
                "expected_relation_count_after_survives": before + len(survives),
                "expected_relation_count_after_conditional_full": before + F3_REVIEWER_READY_COUNT,
                "expected_ids": ids,
                "included_candidate_ids": [e["candidate_id"] for e in entries],
                "all_f3_reviewer_ready_ids": [r["candidate_id"] for r in recs],
                "survives_ids": survives, "needs_review_ids": needs_review,
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
                    "category_decision": "al_mg_antacid",
                    "ibandronate_overlap_decision_required": True,
                    "separation_interval_decision_required": True,
                    "verified_reference_consent_required": True,
                    "etidronate_parse_resolution_required_for_nutrient": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id(scope 전건)/scope/grouping/al_mg_antacid/"
                               "overlap/간격/verified_reference 누락 · clinical_reviewed=true·제품추천·금속이온/제산제/우유 복용 권유·"
                               "에티드론산 standalone 계열 일반화 허용",
                    "template": "docs/MediStack_reviewer_package_f3_bisphosphonate_v1_4.md §reviewer-note",
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
                    "antacid_category_al_mg_only": all(
                        r.get("counterpart_category") == ANTACID_CATEGORY
                        for r in projected if "제산제" in r.get("nutrient", "")),
                    "ingredient_all_bisphosphonate": all(r["ingredient"].endswith("드론산") for r in projected),
                    "no_needs_review_integrated": all(e["reverify_verdict"] in ("survives", "survives_with_copy_change")
                                                      for e in entries),
                },
                "duplicate_summary": {"exact_dup_with_live": dup,
                                      "note": "이반드론산은 live 에 ×칼슘/철분/마그네슘(영양소)만 — Al/Mg 제산제(al_mg_antacid·약물)는 "
                                              "별도 counterpart(id61 선례)로 exact dup 아님. exact dup 0."},
                "conflict_summary": {
                    "live_60": "exact dup 0(위 duplicate_summary). 단 이반드론산 nutrient-overlap(headline 2) reviewer 판단.",
                    "f1_quinolone_18": "퀴놀론(록사신)×광물/제산제 — 성분 다름·충돌 0(F3=드론산).",
                    "f2_tetracycline_5": "사이클린×광물/제산제 — 성분 다름·충돌 0(F3=드론산).",
                    "penicillamine_2": "성분/counterpart 무관 — 충돌 0.",
                    "theme_map_6": "지용성비타민/세팔로/페니실라민 — F3 무관·충돌 0.",
                    "potassium_4": "이뇨제×칼륨 depletion — F3 무관·충돌 0.",
                    "at_fex_1": "펙소페나딘×제산제 — F3 무관·충돌 0.",
                    "at_itz_id61": "이트라코나졸×Al/Mg제산제 — 동일 al_mg_antacid 렌더 경로(선례)·성분 다름·충돌 0.",
                    "other_factory_families": "F4/F6/F9/F10 reviewer-ready — 성분/관계 다름·충돌 0.",
                    "ibandronate_nutrient_overlap": "이반드론산은 ×칼슘/철분/마그네슘 nutrient 이미 live — antacid(약물) relation 은 별도 "
                                                    "counterpart 라 exact dup 아니나 정보 중복 여부는 reviewer 판단(headline_finding_2).",
                    "etidronate_needs_review": "0148/0149(에티드론산×칼슘/철분)은 standalone parse 취약 → 통합 대상 아님(needs_review). "
                                               "reviewer 의 라벨 parse 확정 전까지 충돌/통합 논외.",
                    "full_factory_integrator_dedup": "차후 factory 일괄 integrator 는 (ingredient, counterpart/category) 키로 본 F3 통합분(0147)을 "
                                                     "skip 해야 함(중복 생성 금지).",
                },
                "full_index_alias_impact": index_impact,
                "v0_2_validator_evidence": {
                    "sim_all_passed": ok_all, "sim_all_tail": tail_all,
                    "interpretation": "al_mg_antacid(id61 선례·live 이반드론산×광물 동일 약물) 현행 v0.2 validator PASS → 선행조건 0.",
                },
                "render_safety_summary": "survives 1건 = id61 렌더 경로(약물 counterpart kicker). src 변경 불필요.",
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
              f"에티드론산 parse 확정+enrich 시 latent={index_impact['latent_flip_if_etidronate_resolved_and_enriched']}.")
        print(f"[dry-run] needs_review 2(0148/0149) — 통합 제외(에티드론산 standalone parse reviewer 확정 요).")
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
        (" | F3 비스포스포네이트 %s(%d건) live 통합: 비스포×Al/Mg 함유 제산제(al_mg_antacid·약물). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (scope_label, len(projected), before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE F3 BISPHOSPHONATE ({scope_label}): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
