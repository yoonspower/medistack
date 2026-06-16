#!/usr/bin/env python3
"""
integrate_f2_tetracycline_batch_v1_4.py
MediStack — Relation Factory v1.4 **F2 테트라사이클린 5건** live 통합 **준비/드라이런** 스크립트.
integrate_f1_quinolone_batch_v1_4.py / integrate_theme_map_draft_batch_v1_3.py 패턴 승계
(reviewer-ready batch → 적대검증 통과(survives) F2 5건만, subset/scope 지원).

대상(소스: data/drafts/relation_factory_reviewer_ready_batch_v1_4.json · family==F2 · adversarial_verdict==survives):
  nutrient 2건(테트라사이클린×철분·아연) — counterpart_category=null=일반 영양소(live 독시/미노×철분/아연 와 동일 렌더)
  al_mg_antacid 3건(독시·미노·테트라사이클린 × Al/Mg 함유 제산제(약물)) — id61 이트라코나졸 선례와 동일 렌더
  drug ingredient: 독시사이클린·미노사이클린·테트라사이클린

⚠️ 5건 모두 **단일 테트라사이클린계 라벨 문장**("칼슘, 마그네슘, 알루미늄을 함유하는 제산제 …
  철ㆍ아연을 함유하고 있는 제제 … 에 의해 테트라사이클린계 약물의 흡수가 저하되어 효과가 저하될 수 있다.")
  근거. 따라서 reviewer 는 **약물별 국내 품목(itemSeq) 매칭**을 확정해야 한다(reviewer_questions).

작업 C(F2 family-specific 재검증, reverify()): 12 렌즈(+금칙어/상담/항응고 3) refute-by-default 재적용.
  결과: survives 5 · copy_change 0 · needs_review 0 · hold 0 · reject 0.
  soft-flag(다운그레이드 아님): 독시/미노는 live 에 ×칼슘/철분/마그네슘/아연(영양소)이 이미 존재 →
  Al/Mg 제산제(약물) relation 추가가 **정보 가치(제산제 제품 맥락) vs 중복**인지 reviewer 판단(id61 선례·F2 헤드라인 질문).
  ⚠️ 우유/유제품·소아/임신/골/치아 문맥은 본 라벨 문장에 없음(보수적 batch — 해당 후보 0).

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만 수행
(별도 PM 승인 + clinical reviewer 전까지 절대 금지·본 세션 호출 안 함).
  dry-run = 라이브/보호 데이터 **무수정** + 예상 산출물 기록:
    data/review/f2_tetracycline_inventory_v1_4.json     (작업 B/C — 5건 감사 + 재검증 렌즈)
    data/review/f2_tetracycline_live_dryrun_v1_4.json   (작업 G — scope별 예상 count/id + 가드 + 충돌 + v0.2 증거)
    data/review/f2_tetracycline_index_impact_v1_4.json  (작업 K — full index/aliases 영향)

scope(작업 D grouping):
  --scope all5       (기본) 5건 — 60→65 · id 62~66
  --scope nutrient2  테트라×철분/아연 2건 — 60→62 (live 독시/미노×광물 동일 렌더·1차 권고)
  --scope antacid3   Al/Mg 제산제 3건 — 60→63 (id61 렌더 경로)
  --scope top2       nutrient2 동의어(가장 깨끗한 2건) — 60→62
  --scope top3       테트라사이클린 by-ingredient(철분/아연/제산제) 3건 — 60→63 (신규 성분 단독)
  --candidate-ids A,B,...  명시 후보(F2 ∩ survives 만)
  ⚠️ live write 시 reviewer-note 의 scope 선언이 요청 scope 와 일치해야 함(check_reviewer_note).

live 통합 선행조건: **없음(0)**. al_mg_antacid(id61)·일반 영양소(live 독시/미노×철분/아연) 둘 다 현행 v0.2 validator + src 렌더 지원.
  full index: 독시(11)/미노(3) 이미 covered · 테트라사이클린은 index sample 에 1건 name_only — 단, full index/aliases 는
  relation export 와 **decoupled**(pool=aliases.verified_item_seqs·런타임 재생성). relation-only 통합은 자동 flip 0
  (relation_card 1168/name_only 16412 불변). 테트라사이클린 verified_item_seqs 등록 시에만 1건 flip(1169/16411·별도 alias 작업·통합 차단 아님).

사용:
  python3 scripts/integrate_f2_tetracycline_batch_v1_4.py                                    # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_f2_tetracycline_batch_v1_4.py --scope nutrient2                  # dry-run(특정 scope)
  python3 scripts/integrate_f2_tetracycline_batch_v1_4.py --pm-approved --reviewer-note X     # live(별도 PM·reviewer 후·본 세션 금지)
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
INVENTORY_ARTIFACT = os.path.join(DATA, "review", "f2_tetracycline_inventory_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "f2_tetracycline_live_dryrun_v1_4.json")
INDEX_IMPACT_ARTIFACT = os.path.join(DATA, "review", "f2_tetracycline_index_impact_v1_4.json")

BASELINE_RELATIONS = 60      # F1/AT-FEX/칼륨/theme/페니실라민 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-17"  # source-check + 적대검증 + F2 family 재검증 확인일
F2_COUNT = 5


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
PEDIATRIC_BONE_TERMS = ["소아", "임신", "수유", "치아", "착색", "성장기", "골형성", "뼈", "골격"]
CONSULT = "약사 또는 의사"

# F2 는 작업 C 결과 copy_change 0(라벨 문장 깨끗·trailing marker 없음). 빈 dict 유지(F1 RF-F1-0020 대비).
F2_COPY_CHANGES = {}

# ── 후보별 reviewer note(작업 C soft-flag·다운그레이드 아님) ──
_OVERLAP_NOTE = ("live 에 동일 약물 ×칼슘/철분/마그네슘/아연(영양소) 이미 존재 → Al/Mg 제산제(약물·al_mg_antacid) relation 추가가 "
                 "정보 가치(제산제 제품 맥락 명시) vs 중복인지 reviewer 판단(id61 선례). 카드 렌더는 약물 counterpart kicker 로 영양소와 구분.")
_SHARED_QUOTE_NOTE = ("테트라사이클린계 공통 라벨 문장 근거 — 약물별 국내 품목(itemSeq) 매칭 정확성 reviewer 확정 필요.")
F2_REVIEWER_NOTES = {
    "RF-F2-0105": [_SHARED_QUOTE_NOTE, "독시사이클린: " + _OVERLAP_NOTE],
    "RF-F2-0110": [_SHARED_QUOTE_NOTE, "미노사이클린: " + _OVERLAP_NOTE,
                   "원문 표기 '비스무스(bismuth)' — 다른 후보의 '비스무트' 와 철자 변형(각 품목 라벨 verbatim). hygiene 문제 아님."],
    "RF-F2-0111": [_SHARED_QUOTE_NOTE, "테트라사이클린: 신규 성분·영양소 relation(live 독시/미노×철분 동일 렌더)·cleanly additive."],
    "RF-F2-0114": [_SHARED_QUOTE_NOTE, "테트라사이클린: 신규 성분·영양소 relation(live 독시/미노×아연 동일 렌더)·cleanly additive."],
    "RF-F2-0115": [_SHARED_QUOTE_NOTE,
                   "테트라사이클린×Al/Mg 제산제: 신규 성분·al_mg_antacid(id61 선례)·cleanly additive. "
                   "참고: 테트라사이클린은 현재 ×칼슘/×마그네슘 영양소 relation 미보유(독시/미노 대비 완전성 격차) — 차후 확장 후보(본 scope 외)."],
}

NUTRIENT_COUNTERPARTS = {"철분", "아연"}     # F2 에는 칼슘/마그네슘 영양소 후보 없음(라벨 문장상 제산제 맥락만)
ANTACID_CATEGORY = "al_mg_antacid"
# 라벨 문장에서 counterpart 직접언급 토큰(철분→'철': 원문은 '철ㆍ아연'으로 '철분' 아닌 '철' 사용 — F1 와의 family 차이)
NUTRIENT_QUOTE_TOKEN = {"철분": "철", "아연": "아연"}

# 라이브 60 컨텍스트(L11 live 중복 · L12 F1 overlap 렌즈에서 참조)
_exp_cache = json.load(open(EXPORT, encoding="utf-8"))
LIVE_PAIRS = {(r.get("ingredient"), r.get("nutrient")) for r in _exp_cache["relations"]}
F1_QUINOLONES = {"노르플록사신", "레보플록사신", "로메플록사신", "발로플록사신", "오플록사신",
                 "자보플록사신", "토수플록사신", "페플록사신", "시프로플록사신", "목시플록사신"}


def _scope_split(recs):
    nutrient = [r["candidate_id"] for r in recs if r["counterpart_type"] == "nutrient"]
    antacid = [r["candidate_id"] for r in recs if r.get("counterpart_category") == ANTACID_CATEGORY]
    return nutrient, antacid


def _tetra_ids(recs):
    return [r["candidate_id"] for r in recs if r["drug_ingredient"] == "테트라사이클린"]


def load_f2():
    """reviewer-ready batch → F2 5건(survives) + 작업 C copy_change(현재 0) + reverify.
    (records, reverify_summary) 반환. live 무수정."""
    rr = json.load(open(REVIEWER_READY, encoding="utf-8"))
    f2 = [dict(r) for r in rr["reviewer_ready_relations"] if r.get("family") == "F2"]
    for r in f2:
        cc = F2_COPY_CHANGES.get(r["candidate_id"])
        if cc:
            orig = r[cc["field"]]
            assert cc["cleaned"] in orig, \
                f"{r['candidate_id']}: cleaned {cc['field']} 가 원문 부분문자열 아님 — 카피 위조 차단"
            r[cc["field"]] = cc["cleaned"]
            r["_copy_change"] = cc
    summary = reverify_all(f2)
    return f2, summary


def reverify(rec):
    """F2 family-specific 12 렌즈(+금칙어/상담/항응고) 재검증(refute-by-default). (lens_results, verdict, flags)."""
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
    # L2 counterpart 직접 언급(철분→'철' 토큰 매핑)
    if ctype == "nutrient":
        token = NUTRIENT_QUOTE_TOKEN.get(cp, cp)
        L["L2_direct_cooccurrence"] = "pass" if token in q else f"fail:{cp}({token}) 미언급"
    else:  # al_mg_antacid 약물
        L["L2_direct_cooccurrence"] = "pass" if ("제산제" in q and ("알루미늄" in q or "마그네슘" in q)) \
            else "fail:Al/Mg제산제 미언급"
    # L3 cation 문맥 구분(제제(영양소) vs 제산제). 철·아연=standalone '제제' / Al·Mg·Ca=제산제 절.
    if ctype == "nutrient":
        L["L3_context_discrimination"] = "pass" if ("제제" in q and cp in NUTRIENT_COUNTERPARTS) \
            else f"fail:{cp} 영양소 제제 맥락 아님"
    else:
        L["L3_context_discrimination"] = "pass" if "제산제" in q else "fail:제산제 맥락 아님"
    # L4 Al/Mg 제산제 vs Mg 영양제 혼동
    if cat == ANTACID_CATEGORY:
        L["L4_antacid_vs_mg_nutrient"] = "pass" if ("약물" in cp and cp != "마그네슘") else "fail:Mg영양제 혼동"
    elif ctype == "nutrient":
        L["L4_antacid_vs_mg_nutrient"] = "pass" if cp in NUTRIENT_COUNTERPARTS else f"fail:비영양소 counterpart {cp}"
    else:
        L["L4_antacid_vs_mg_nutrient"] = "fail:분류 불명"
    # L5 supplement/nutrient vs 함유 제산제 — 영양소 후보는 칼슘/마그네슘(제산제 절 전용 cation) 아님
    if ctype == "nutrient":
        L["L5_nutrient_vs_antacid_ctx"] = "pass" if cp not in ("칼슘", "마그네슘") else "fail:제산제절 cation 을 영양소로 오인"
    else:
        L["L5_nutrient_vs_antacid_ctx"] = "pass" if cat == ANTACID_CATEGORY else "fail:제산제 약물 category 아님"
    # L6 소아/임신/골/치아 문맥을 흡수저하 relation 으로 오인 안 함
    L["L6_no_pediatric_bone"] = "pass" if not any(t in q for t in PEDIATRIC_BONE_TERMS) \
        else "fail:소아/임신/골/치아 문맥 혼입"
    # L7 흡수저하/킬레이트/효과감소 방향
    L["L7_direction"] = "pass" if (("흡수" in q) and ("저하" in q or "저해" in q or "감소" in q) or "킬레이트" in q) \
        else "fail:방향 불명"
    # L8 quote boundary / 다른 번호목록·문장 끌어옴 / stray marker
    stray = bool(re.search(r"[.\)]\s+\d+\s*$", q)) or q.strip().endswith(" 1")
    if rec.get("_copy_change"):
        L["L8_quote_boundary"] = "copy_change:stray marker trimmed"
        flags.append("copy_change")
    elif stray:
        L["L8_quote_boundary"] = "fail:stray marker"
    elif q.count("다.") > 1 or q.count("효과가 저하될 수 있다.") != 1:
        L["L8_quote_boundary"] = "fail:문장 경계 의심(복수 종결)"
    else:
        L["L8_quote_boundary"] = "pass"
    # L9 복용 지시(명령형) 금지
    L["L9_no_directive"] = "pass" if not any(c in copy_txt for c in DIRECTIVE_CMDS) else "fail:복용 지시"
    # L10 제품/구매/제휴 + 보충 권유
    bad_prod = [p for p in PRODUCT_PHRASES if p in copy_txt]
    bad_sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy_txt]
    L["L10_product_supplement"] = "pass" if not bad_prod and not bad_sup else f"fail:{bad_prod}{bad_sup}"
    # L11 기존 live 60 exact 중복(독시/미노 antacid 는 별도 counterpart=id61 선례 → exact dup 아님)
    L["L11_no_live_dup"] = "pass" if (ing, cp) not in LIVE_PAIRS else f"fail:live 중복 {(ing, cp)}"
    # L12 F1 퀴놀론 후보와 중복/혼동
    L["L12_no_f1_overlap"] = "pass" if ing not in F1_QUINOLONES else f"fail:F1 성분 {ing}"
    # L13 금칙어 / L14 상담 톤 / L15 항응고
    fb = vfp.scan(copy_txt)
    L["L13_forbidden_phrase"] = "pass" if not fb else f"fail:{fb}"
    L["L14_consult_tone"] = "pass" if CONSULT in copy_txt else "fail:상담 톤 없음"
    L["L15_negation_anticoag"] = "pass" if not any(t in q or t in copy_txt for t in ANTICOAG_TERMS) \
        else "fail:항응고/비타민K 혼입"

    hard_fail = any(str(v).startswith("fail") for v in L.values())
    if hard_fail:
        verdict = "needs_review"
    elif rec.get("_copy_change"):
        verdict = "survives_with_copy_change"
    else:
        verdict = "survives"
    return L, verdict, flags


def reverify_all(recs):
    out = {}
    counts = {"survives": 0, "survives_with_copy_change": 0, "needs_review": 0, "hold": 0, "reject": 0}
    for r in recs:
        L, verdict, flags = reverify(r)
        counts[verdict] = counts.get(verdict, 0) + 1
        out[r["candidate_id"]] = {"lens_results": L, "verdict": verdict, "flags": flags,
                                  "reviewer_notes": F2_REVIEWER_NOTES.get(r["candidate_id"], [])}
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
    """argv → (scope_label, [candidate_id...]). 기본 all5."""
    ids_all = [r["candidate_id"] for r in recs]
    nutrient, antacid = _scope_split(recs)
    tetra = _tetra_ids(recs)
    if "--candidate-ids" in sys.argv:
        i = sys.argv.index("--candidate-ids")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        want = [c.strip() for c in raw.split(",") if c.strip()]
        return "custom", want
    if "--scope" in sys.argv:
        i = sys.argv.index("--scope")
        s = sys.argv[i + 1] if i + 1 < len(sys.argv) else "all5"
        return {"all5": ("all5", ids_all), "nutrient2": ("nutrient2", nutrient),
                "antacid3": ("antacid3", antacid), "top2": ("top2", nutrient),
                "top3": ("top3", tetra)}.get(s, ("all5", ids_all))
    return "all5", ids_all


def build_subset(exp, scope_ids):
    """scope_ids(F2 ∩ survives) → projected entries. live 무수정. (entries, viol)."""
    recs, _summary = load_f2()
    by_id = {r["candidate_id"]: r for r in recs}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in scope_ids:
        rec = by_id.get(cid)
        if rec is None:
            viol.append(f"{cid}: F2 reviewer-ready(survives) 집합에 없음")
            continue
        _L, verdict, _f = reverify(rec)
        if verdict not in ("survives", "survives_with_copy_change"):
            viol.append(f"{cid}: 재검증 verdict={verdict} (survives 아님)")
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


# ── reviewer 노트 인터록(F2 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date", "<scope")
SCOPE_MARKERS = ("scope", "범위")
REVIEWER_ID_RE = re.compile(r"검수자|검토자|reviewer|RPH|PM[ \t]*승인")
GROUPING_MARKERS = ("grouping", "묶음", "개별", "by-counterpart", "성분별", "상대성분별", "한 번에", "subset")
INTERVAL_MARKERS = ("간격", "separation 간격", "시간")  # 분리 간격 노출 결정
ANTACID_MARKERS = ("al_mg_antacid",)    # category 결정(약물 counterpart) — 명시적 category id 요구(bare '제산제'로 불충분)
OVERLAP_MARKERS = ("중복", "overlap", "정보 가치", "추가 노출", "nutrient")  # 독시/미노 nutrient-overlap 판단 명시
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음",
                       "제품·구매·제휴·보충제 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("금속이온", "철분·아연 보충 권유 없음", "보충 권유 없음", "보충 권유 아님",
                          "제산제 복용 권유 없음", "복용 권유 없음", "우유·유제품 섭취 권유 없음")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|보충제?[ \t]*추천)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_RECO_RE = re.compile(
    r"(철분|아연|제산제|보충제|우유|유제품)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")
# 소아/임신/골/치아 문맥 또는 계열 일반화 허용 — 금지(테트라사이클린 라벨 외 맥락 확대 차단)
GENERALIZE_PERMIT_RE = re.compile(
    r"(소아|임신|수유|치아|착색|골형성|뼈|골격|성장기|계열)[^\n]{0,24}(일반화|확대)[ \t]*(승인|허용|가능|함|적용)"
    r"|(일반화|확대)[ \t]*(승인|허용)")


def check_reviewer_note(reviewer_note, scope_ids):
    """F2 live 통합 reviewer 노트 게이트. (note, violations). 빈 리스트 = 통과. main()/테스트 공유.
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
        bad.append("scope 선언 미명시(all5/nutrient2/antacid3/top2/top3/명시 ids)")
    if not any(m in note for m in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(한 번에/성분별/상대성분별/subset)")
    if not any(m in note for m in ANTACID_MARKERS):
        bad.append("category 결정 'al_mg_antacid'(Al/Mg 제산제=약물 counterpart·id61 선례) 미명시")
    if not any(m in note for m in OVERLAP_MARKERS):
        bad.append("독시/미노 nutrient-overlap(기존 ×칼슘/철분/마그네슘/아연) 판단 미명시")
    if not any(m in note for m in INTERVAL_MARKERS):
        bad.append("separation 간격(2~4시간) 카드 노출 여부 결정 미명시")
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
        bad.append("소아/임신/골/치아 문맥 또는 계열 일반화 허용 문구 — 금지")
    return note, bad


def _index_impact(recs):
    """full index/aliases 영향(읽기전용). pool=aliases.verified_item_seqs 라 relation 과 decoupled →
    relation-only 통합은 자동 flip 0. 테트라사이클린 name_only 1건은 alias 등록 시에만 flip(latent)."""
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    ents = idx["entries"]
    al = json.load(open(ALIASES, encoding="utf-8"))
    al_txt = json.dumps(al, ensure_ascii=False)
    ings = sorted({r["drug_ingredient"] for r in recs})
    per = {}
    latent_flip = 0
    for ing in ings:
        matched = [e for e in ents if ing in (e.get("ingredient_name") or "")]
        covered = sum(1 for e in matched if e.get("covered_by_relation"))
        name_only = sum(1 for e in matched if not e.get("covered_by_relation"))
        in_al = ing in al_txt
        # alias pool 에 없는 성분의 name_only 항목만 latent flip 후보(등록 시).
        latent = name_only if not in_al else 0
        latent_flip += latent
        per[ing] = {"index_items": len(matched), "covered_by_relation": covered,
                    "name_only": name_only, "in_aliases": in_al, "latent_flip_if_alias_enriched": latent}
    counts = idx["meta"].get("counts", {})
    return {
        "full_index_counts_current": counts,
        "index_pool_source": "data/medistack_v0.3_aliases.json · verified_item_seqs/product_aliases (export relations 와 decoupled)",
        "per_ingredient": per,
        "automatic_flip_from_relation_integration": 0,
        "relation_card_flip_required": 0,
        "relation_card_after": counts.get("relation_card"),
        "name_only_after": counts.get("name_only"),
        "index_change_required": False,
        "alias_change_required": False,
        "latent_flip_if_alias_enriched": latent_flip,
        "relation_card_after_if_alias_enriched": (counts.get("relation_card") or 0) + latent_flip,
        "name_only_after_if_alias_enriched": (counts.get("name_only") or 0) - latent_flip,
        "interpretation": "독시사이클린(11)/미노사이클린(3)은 이미 covered_by_relation(verified_item_seqs 등록·in_aliases). "
                          "테트라사이클린은 index sample 에 1건 name_only(in_aliases=false). full index/aliases 의 coverage 는 "
                          "alias pool(verified_item_seqs)로 결정되며 export relations 와 decoupled(런타임 재생성·fail-soft 검색보조) → "
                          "relation-only 통합은 자동 flip 0 · relation_card 1168/name_only 16412 불변. "
                          "테트라사이클린을 verified_item_seqs 에 등록(별도 alias 작업)하면 1건 flip → relation_card 1169/name_only 16411 "
                          "(F1(전 성분 부재) 대비 F2 차이점: 테트라 1건은 latent flip 후보). 통합 차단 아님.",
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
    recs, summary = load_f2()
    scope_label, scope_ids = resolve_scope(recs)
    entries, viol = build_subset(exp, scope_ids)
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== F2 테트라사이클린 {scope_label}({len(entries)}건) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    print(f"재검증(작업 C): {summary['counts']}")
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
        tetra_ids = _tetra_ids(recs)

        # scope별 예상(runtime max+1) — 단독 통합 시.
        def scope_proj(cids):
            return {"count": len(cids), "expected_count": before + len(cids),
                    "expected_ids": list(range(base_max + 1, base_max + 1 + len(cids))),
                    "candidate_ids": cids}
        scope_scenarios = {
            "recommended": "all5 once (60→65) — 5건 소규모·reviewer 1패스. 단 독시/미노 nutrient-overlap 결정 1건 surface. "
                           "isolate 원하면 by_counterpart_2wave. F1 동시 통합 시 antibiotic_mineral_wave 로 fold.",
            "all5": scope_proj([r["candidate_id"] for r in recs]),
            "nutrient2": scope_proj(nutrient_ids),
            "antacid3": scope_proj(antacid_ids),
            "top2": scope_proj(nutrient_ids),
            "top3_tetra_by_ingredient": scope_proj(tetra_ids),
            "by_counterpart_2wave": {
                "wave1_nutrient2": {"expected_count": before + len(nutrient_ids),
                                    "note": "테트라×철분/아연 — live 독시/미노×광물과 동일 렌더·cleanly additive → 1차 권고."},
                "wave2_antacid3": {"expected_count": before + len(nutrient_ids) + len(antacid_ids),
                                   "note": "독시/미노/테트라×Al/Mg제산제(id61 렌더). 독시/미노 nutrient-overlap reviewer 판단 후 → 2차."},
                "note": "wave1 60→62, wave2 62→65. rollback 단위 분리·overlap 결정 격리. all5 일괄도 허용(양 렌더 경로 live 검증됨).",
            },
            "scenario_if_f1_already_live": {
                "baseline": 78, "expected_after_full": 83,
                "note": "F1 18건(60→78) 먼저 live 면 F2 5건은 78→83(id 80~84). runtime max+1 자동 조정.",
            },
            "antibiotic_mineral_wave_with_f1": {
                "nutrient_wave": "F1 nutrient10 + F2 nutrient2 = 12건(전부 live 광물 렌더 동일)",
                "antacid_wave": "F1 antacid8 + F2 antacid3 = 11건(al_mg_antacid·id61 렌더)",
                "note": "항생제×금속/제산제 통합 wave 로 F1·F2 묶음. 통합 여부·순서는 reviewer/PM.",
            },
            "by_ingredient": {ing: sorted(r["candidate_id"] for r in recs if r["drug_ingredient"] == ing)
                              for ing in sorted({r["drug_ingredient"] for r in recs})},
            "id_rule": "id 는 runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. F1/AT-FEX/칼륨/theme/페니실라민 먼저면 자동 조정.",
        }

        ok_all, tail_all = integ.run_v0_2(integ._sim_with(exp, projected))
        sep_nutrient = [e["projected_live_relation"] for e in entries if e["counterpart_type"] == "nutrient"]
        ok_nut, tail_nut = integ.run_v0_2(integ._sim_with(exp, sep_nutrient)) if sep_nutrient else (True, "n/a")
        index_impact = _index_impact(recs)

        live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
        dup = [f"{r['ingredient']}×{r['nutrient']}" for r in projected
               if (r["ingredient"], r["nutrient"]) in live_pairs]

        # ── 작업 B/C 인벤토리 ──
        inventory = {
            "meta": {
                "name": "f2_tetracycline_inventory_v1_4",
                "status": "DRAFT-ONLY — NOT LIVE / live_integration_forbidden=true / 적대검증(survives)+F2 family 재검증 통과만",
                "purpose": "F2 테트라사이클린 5건 감사 + 작업 C family-specific 재검증(12+3 렌즈). reviewer package/integrator 의 단일 소스.",
                "family": "F2 Tetracycline × metal cation / Al·Mg 함유 제산제(absorption/separation)",
                "count": len(recs),
                "counterpart_split": {"nutrient": len(nutrient_ids), "al_mg_antacid": len(antacid_ids)},
                "ingredients": sorted({r["drug_ingredient"] for r in recs}),
                "reverify_counts": summary["counts"],
                "shared_label_quote": True,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "confirmed_at": CONFIRMED_AT,
                "headline_reviewer_question": "독시/미노사이클린은 live 에 ×칼슘/철분/마그네슘/아연(영양소) 이미 존재 — "
                                              "Al/Mg 제산제(약물) relation 추가가 정보 가치(제산제 제품 맥락) vs 중복인지 reviewer 판단(id61 선례).",
                "note": "survives/copy_change = 자동 적대검증+family 재검증 통과를 의미하며 임상 검수 완료·식약처 승인·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 별도 PM + clinical reviewer note + 별도 PR.",
            },
            "candidates": [
                {
                    "candidate_id": r["candidate_id"], "relation": r["relation"],
                    "drug_ingredient": r["drug_ingredient"], "counterpart": r["counterpart"],
                    "counterpart_type": r["counterpart_type"], "counterpart_category": r.get("counterpart_category"),
                    "itemSeq": r["itemSeq"], "source_section": r["source_section"],
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
            json.dump({"meta": {"name": "f2_tetracycline_index_impact_v1_4",
                                "status": "ANALYSIS — read-only / no index/alias write",
                                "purpose": "F2 5건 live 통합 시 full index/relation_card/name_only/aliases 영향 분석.",
                                "confirmed_at": CONFIRMED_AT},
                       "impact": index_impact}, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── 작업 G dry-run ──
        artifact = {
            "meta": {
                "name": "f2_tetracycline_live_dryrun_v1_4",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "F2 5건 live 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_f2_tetracycline_dryrun_v1_4.py 가 안전·계약을 검증.",
                "requested_scope": scope_label,
                "baseline_relations": before, "baseline_max_id": base_max,
                "expected_relation_count_before": before,
                "expected_relation_count_after_full": before + len(recs),
                "expected_relation_count_after": after,
                "expected_ids_full": list(range(base_max + 1, base_max + 1 + len(recs))),
                "expected_ids": ids,
                "scenario_if_f1_already_live": {"baseline": 78, "expected_after_full": 83},
                "included_candidate_ids": [e["candidate_id"] for e in entries],
                "all_f2_candidate_ids": [r["candidate_id"] for r in recs],
                "excluded_non_f2_candidate_ids_note": "다른 family(F1/F3/F4/F6/F9/F10)·pending(페니실라민/theme/칼륨/AT-FEX)은 본 batch 제외.",
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
                    "nutrient_overlap_decision_required": True,
                    "separation_interval_decision_required": True,
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id(scope 전건)/scope/grouping/al_mg_antacid/"
                               "overlap/간격/verified_reference 누락 · clinical_reviewed=true·제품추천·금속이온/제산제/우유 복용 권유 허용",
                    "template": "docs/MediStack_reviewer_package_f2_tetracycline_v1_4.md §reviewer-note",
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
                    "nutrient_no_category": all(
                        "counterpart_category" not in r
                        for e, r in zip(entries, projected) if e["counterpart_type"] == "nutrient"),
                    "ingredient_all_tetracycline": all(r["ingredient"].endswith("사이클린") for r in projected),
                },
                "duplicate_summary": {"exact_dup_with_live": dup,
                                      "note": "독시/미노사이클린은 live 에 ×칼슘/철분/마그네슘/아연(영양소)만 — Al/Mg 제산제(al_mg_antacid·약물)는 "
                                              "별도 counterpart(id61 선례)로 exact dup 아님. 테트라사이클린은 신규 성분. exact dup 0."},
                "conflict_summary": {
                    "live_60": "exact dup 0(위 duplicate_summary).",
                    "f1_quinolone_18": "퀴놀론(록사신)×광물/제산제 — 성분 다름·충돌 0(F2=사이클린).",
                    "penicillamine_2": "성분/counterpart 무관 — 충돌 0.",
                    "theme_map_6": "지용성비타민/세팔로 acid_reducing_drug/페니실라민 — F2 무관·충돌 0.",
                    "potassium_4": "이뇨제×칼륨 depletion — F2 무관·충돌 0.",
                    "at_fex_1": "펙소페나딘×제산제 — F2 무관·충돌 0.",
                    "at_itz_id61": "이트라코나졸×Al/Mg제산제 — 동일 al_mg_antacid 렌더 경로(선례)·성분 다름·충돌 0.",
                    "other_factory_families": "F3/F9/F10 reviewer-ready — 성분/관계 다름·충돌 0.",
                    "doxy_mino_nutrient_overlap": "독시/미노는 ×칼슘/철분/마그네슘/아연 nutrient 이미 live — antacid(약물) relation 은 별도 "
                                                  "counterpart 라 exact dup 아니나 정보 중복 여부는 reviewer 판단(headline_reviewer_question).",
                    "full_factory_integrator_dedup": "차후 factory 37 일괄 integrator 는 (ingredient, counterpart/category-counterpart) "
                                                     "키로 본 F2 통합분을 skip 해야 함(중복 생성 금지).",
                },
                "full_index_alias_impact": index_impact,
                "v0_2_validator_evidence": {
                    "sim_all_passed": ok_all, "sim_all_tail": tail_all,
                    "sim_nutrient_passed": ok_nut, "sim_nutrient_tail": tail_nut,
                    "interpretation": "al_mg_antacid(id61 선례)·일반 영양소(live 독시/미노×철분/아연) 둘 다 현행 v0.2 validator PASS → 선행조건 0.",
                },
                "render_safety_summary": "nutrient 2건 = live 독시/미노×철분/아연과 동일(영양소 facet·separation chip). "
                                         "al_mg_antacid 3건 = id61 렌더 경로(약물 counterpart kicker). src 변경 불필요.",
                "live_integration_prerequisites": [],
                "validator_result_summary": f"sim 전체 v0.2 PASS={ok_all} · nutrient PASS={ok_nut} (선행조건 0)",
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
        print(f"[dry-run] v0.2 validator: 전체 PASS={ok_all} · nutrient PASS={ok_nut} (선행조건 0).")
        print(f"[dry-run] index 자동 flip={index_impact['relation_card_flip_required']} · "
              f"latent flip(테트라 alias 등록 시)={index_impact['latent_flip_if_alias_enriched']} · alias 변경 필요={index_impact['alias_change_required']}.")
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
        (" | F2 테트라사이클린 %s(%d건) live 통합: 테트라사이클린계 × 철분/아연(영양소)·Al/Mg 함유 제산제(al_mg_antacid·약물). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (scope_label, len(projected), before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE F2 TETRACYCLINE ({scope_label}): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
