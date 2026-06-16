#!/usr/bin/env python3
"""
integrate_f1_quinolone_batch_v1_4.py
MediStack — Relation Factory v1.4 **F1 플루오로퀴놀론 18건** live 통합 **준비/드라이런** 스크립트.
integrate_penicillamine_subset_v1_3.py / integrate_theme_map_draft_batch_v1_3.py 패턴 승계
(reviewer-ready batch → 적대검증 통과(survives) F1 18건만, subset/scope 지원).

대상(소스: data/drafts/relation_factory_reviewer_ready_batch_v1_4.json · family==F1 · adversarial_verdict==survives):
  nutrient 10건(철분4·칼슘3·아연3) — counterpart_category=null=일반 영양소(live FQ×광물 relation 과 동일 렌더)
  al_mg_antacid 8건 — counterpart_category=al_mg_antacid=약물 counterpart(id61 이트라코나졸 선례와 동일 렌더)
  drug ingredient: 노르·레보·로메·발로·오플·자보·토수·페플록사신 (레보/오플은 live 에 ×광물만 존재 → al_mg_antacid 는 별도 counterpart)

작업 C(F1 family-specific 재검증, reverify()):
  10 렌즈(itemSeq·counterpart 직접언급·Al/Mg제산제 vs Mg영양제·quote boundary·negation/항응고·방향·
  복용지시·제품/보충·금칙어·live 중복) refute-by-default 재적용.
  결과: survives 17 · survives_with_copy_change 1(RF-F1-0020 끝 stray '1' 트림=verbatim 부분문자열) · needs_review/hold/reject 0.
  ⚠️ copy_change 는 source_quote(=source.pointer) hygiene 만 — display/management 카피 불변.

⚠️⚠️ 기본값 **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만 수행
(별도 PM 승인 + clinical reviewer 전까지 절대 금지·본 세션 호출 안 함).
  dry-run = 라이브/보호 데이터 **무수정** + 예상 산출물 기록:
    data/review/f1_quinolone_inventory_v1_4.json     (작업 B/C — 18건 감사 + 재검증 렌즈)
    data/review/f1_quinolone_live_dryrun_v1_4.json   (작업 G — scope별 예상 count/id + 가드 + 충돌 + v0.2 증거)
    data/review/f1_quinolone_index_impact_v1_4.json  (작업 K — full index/aliases 영향)

scope(작업 D grouping):
  --scope all18      (기본) 18건 — 60→78 · id 62~79
  --scope nutrient10 철분/칼슘/아연 10건 — 60→70 (live FQ×광물 동일 렌더·신규성 0=권고 1차)
  --scope antacid8   Al/Mg 제산제 8건 — 60→68 (id61 렌더 경로)
  --candidate-ids A,B,...  명시 후보(F1 ∩ survives 만)
  ⚠️ live write 시 reviewer-note 의 scope 선언이 요청 scope 와 일치해야 함(check_reviewer_note).

live 통합 선행조건: **없음(0)**. al_mg_antacid(id61)·일반 영양소(live FQ×광물) 둘 다 현행 v0.2 validator + src 렌더 지원.
  full index: 레보/오플 이미 covered(91+33) · 신규 6 성분은 현 index sample 에 부재 → flip 0 · relation_card 1168/name_only 16412 불변.
  aliases: 신규 6 성분 부재(decoupled fail-soft 검색보조) → 통합에 alias 변경 불필요(옵션 enrichment).

사용:
  python3 scripts/integrate_f1_quinolone_batch_v1_4.py                                    # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_f1_quinolone_batch_v1_4.py --scope nutrient10                 # dry-run(특정 scope)
  python3 scripts/integrate_f1_quinolone_batch_v1_4.py --pm-approved --reviewer-note X     # live(별도 PM·reviewer 후·본 세션 금지)
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
INVENTORY_ARTIFACT = os.path.join(DATA, "review", "f1_quinolone_inventory_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "f1_quinolone_live_dryrun_v1_4.json")
INDEX_IMPACT_ARTIFACT = os.path.join(DATA, "review", "f1_quinolone_index_impact_v1_4.json")

BASELINE_RELATIONS = 60      # AT-FEX/칼륨/theme/페니실라민 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-16"  # source-check + 적대검증 + F1 family 재검증 확인일


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
CONSULT = "약사 또는 의사"

# ── 작업 C copy_change(F1 family 재검증) — source_quote hygiene 만. cleaned 는 원문 verbatim 부분문자열이어야 함 ──
F1_COPY_CHANGES = {
    "RF-F1-0020": {
        "field": "source_quote",
        "cleaned": ("수크랄페이트, 알루미늄 또는 마그네슘 함유 제산제, 철분 함유 제제, 칼슘 함유 제제, "
                    "아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 "
                    "경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다(단, 경구제에 한함)."),
        "reason": "원문 끝 stray footnote marker ' 1' 제거(verbatim 부분문자열). "
                  "'(단, 경구제에 한함)' 경구 한정 — display copy '함께 복용'(경구)과 정합 → reviewer 경구 scope note.",
    },
}

# ── 후보별 reviewer note(작업 C soft-flag·다운그레이드 아님) ──
F1_REVIEWER_NOTES = {
    "RF-F1-0040": ["원문이 '병용을 피하는 것이 바람직하다'(간격 미명시)→카드는 일반 separation. "
                   "원문보다 강하지 않음(separation < avoid_concomitant). reviewer 가 action 입도(separation 유지 vs "
                   "avoid_concomitant·al_mg_antacid) 확정."],
    "RF-F1-0020": ["원문 '(단, 경구제에 한함)' — 경구 제형 한정. 주사제 제외 scope 를 카드/노트에 남길지 reviewer 확정."],
}

NUTRIENT_COUNTERPARTS = {"철분", "칼슘", "아연"}
ANTACID_CATEGORY = "al_mg_antacid"


def _scope_split(recs):
    nutrient = [r["candidate_id"] for r in recs if r["counterpart_type"] == "nutrient"]
    antacid = [r["candidate_id"] for r in recs if r.get("counterpart_category") == ANTACID_CATEGORY]
    return nutrient, antacid


def load_f1():
    """reviewer-ready batch → F1 18건(survives) + 작업 C copy_change 적용 + reverify.
    (records, reverify_summary) 반환. records 는 cleaned source_quote 반영. live 무수정."""
    rr = json.load(open(REVIEWER_READY, encoding="utf-8"))
    f1 = [dict(r) for r in rr["reviewer_ready_relations"] if r.get("family") == "F1"]
    # copy_change 적용(verbatim 부분문자열 보증)
    for r in f1:
        cc = F1_COPY_CHANGES.get(r["candidate_id"])
        if cc:
            orig = r[cc["field"]]
            assert cc["cleaned"] in orig, \
                f"{r['candidate_id']}: cleaned {cc['field']} 가 원문 부분문자열 아님 — 카피 위조 차단"
            r[cc["field"]] = cc["cleaned"]
            r["_copy_change"] = cc
    summary = reverify_all(f1)
    return f1, summary


def reverify(rec):
    """F1 family-specific 10 렌즈 재검증(refute-by-default). (lens_results, verdict, flags) 반환."""
    q = rec.get("source_quote", "") or ""
    disp = rec.get("display_copy", "") or ""
    mng = rec.get("management_copy", "") or ""
    copy_txt = f"{disp} {mng}"
    cp = rec.get("counterpart", "")
    ctype = rec.get("counterpart_type", "")
    cat = rec.get("counterpart_category")
    L = {}
    flags = []

    # L1 source fidelity(itemSeq 실값·section)
    seq = str(rec.get("itemSeq", ""))
    L["L1_source_fidelity"] = "pass" if (seq.isdigit() and len(seq) >= 8 and rec.get("source_section")) \
        else "fail:itemSeq/section"
    # L2 counterpart 직접 언급
    if ctype == "nutrient":
        token = {"철분": "철분", "칼슘": "칼슘", "아연": "아연"}.get(cp, cp)
        L["L2_direct_cooccurrence"] = "pass" if token in q else f"fail:{cp} 미언급"
    else:  # al_mg_antacid 약물
        L["L2_direct_cooccurrence"] = "pass" if ("제산제" in q and ("알루미늄" in q or "마그네슘" in q)) \
            else "fail:Al/Mg제산제 미언급"
    # L3 Al/Mg 제산제 vs Mg 영양제 혼동
    if cat == ANTACID_CATEGORY:
        L["L3_antacid_vs_mg_nutrient"] = "pass" if ("약물" in cp and cp != "마그네슘") else "fail:Mg영양제 혼동"
    elif ctype == "nutrient":
        L["L3_antacid_vs_mg_nutrient"] = "pass" if cp in NUTRIENT_COUNTERPARTS else f"fail:비영양소 counterpart {cp}"
    else:
        L["L3_antacid_vs_mg_nutrient"] = "fail:분류 불명"
    # L4 quote boundary / hygiene
    stray = bool(re.search(r"[.\)]\s+\d+\s*$", q)) or q.strip().endswith(" 1")
    if rec.get("_copy_change"):
        L["L4_quote_boundary"] = "copy_change:stray marker trimmed"
        flags.append("copy_change")
    elif stray:
        L["L4_quote_boundary"] = "fail:stray marker"
    else:
        L["L4_quote_boundary"] = "pass"
    # L5 negation / 항응고·비타민K 혼입
    L["L5_negation_anticoag"] = "pass" if not any(t in q or t in copy_txt for t in ANTICOAG_TERMS) \
        else "fail:항응고/비타민K 혼입"
    # L6 방향(흡수저하/킬레이트)
    L["L6_direction"] = "pass" if (("흡수" in q) and ("저하" in q or "저해" in q or "감소" in q) or "킬레이트" in q) \
        else "fail:방향 불명"
    # L7 복용 지시(명령형) 금지
    L["L7_no_directive"] = "pass" if not any(c in copy_txt for c in DIRECTIVE_CMDS) else "fail:복용 지시"
    # L8 제품/구매/제휴 + 보충 권유
    bad_prod = [p for p in PRODUCT_PHRASES if p in copy_txt]
    bad_sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy_txt]
    L["L8_product_supplement"] = "pass" if not bad_prod and not bad_sup else f"fail:{bad_prod}{bad_sup}"
    # L9 금칙어
    fb = vfp.scan(copy_txt)
    L["L9_forbidden_phrase"] = "pass" if not fb else f"fail:{fb}"
    # L10 상담 톤(참고정보)
    L["L10_consult_tone"] = "pass" if CONSULT in copy_txt else "fail:상담 톤 없음"

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
                                  "reviewer_notes": F1_REVIEWER_NOTES.get(r["candidate_id"], [])}
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
    """argv → (scope_label, [candidate_id...]). 기본 all18."""
    ids_all = [r["candidate_id"] for r in recs]
    nutrient, antacid = _scope_split(recs)
    if "--candidate-ids" in sys.argv:
        i = sys.argv.index("--candidate-ids")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        want = [c.strip() for c in raw.split(",") if c.strip()]
        return "custom", want
    if "--scope" in sys.argv:
        i = sys.argv.index("--scope")
        s = sys.argv[i + 1] if i + 1 < len(sys.argv) else "all18"
        return {"all18": ("all18", ids_all), "nutrient10": ("nutrient10", nutrient),
                "antacid8": ("antacid8", antacid)}.get(s, ("all18", ids_all))
    return "all18", ids_all


def build_subset(exp, scope_ids):
    """scope_ids(F1 ∩ survives) → projected entries. live 무수정. (entries, viol)."""
    recs, _summary = load_f1()
    by_id = {r["candidate_id"]: r for r in recs}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, viol = [], []
    nid = max_id
    for cid in scope_ids:
        rec = by_id.get(cid)
        if rec is None:
            viol.append(f"{cid}: F1 reviewer-ready(survives) 집합에 없음")
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


# ── reviewer 노트 인터록(F1 전용) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date", "<scope")
SCOPE_MARKERS = ("scope", "범위")
REVIEWER_ID_RE = re.compile(r"검수자|검토자|reviewer|RPH|PM[ \t]*승인")
GROUPING_MARKERS = ("grouping", "묶음", "개별", "by-counterpart", "성분별", "상대성분별", "한 번에", "subset")
INTERVAL_MARKERS = ("간격", "separation 간격", "시간")  # 분리 간격 노출 결정
ANTACID_MARKERS = ("al_mg_antacid",)    # category 결정(약물 counterpart) — 명시적 category id 요구(bare '제산제'로 불충분)
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴 추천 없음", "제품 추천 없음", "제품 추천 아님", "상업 추천 없음",
                       "제품·구매·제휴·보충제 추천 없음")
NOT_SUPPLEMENT_MARKERS = ("금속이온", "철분·칼슘·아연 보충 권유 없음", "보충 권유 없음", "보충 권유 아님",
                          "제산제 복용 권유 없음", "복용 권유 없음")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|보충제?[ \t]*추천)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_RECO_RE = re.compile(
    r"(철분|칼슘|아연|제산제|보충제)[ \t]*(보충|복용|섭취)?[ \t]*(권장|권유|하세요|하십시오|드세요|섭취하|허용)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")


def check_reviewer_note(reviewer_note, scope_ids):
    """F1 live 통합 reviewer 노트 게이트. (note, violations). 빈 리스트 = 통과. main()/테스트 공유.
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
        bad.append("scope 선언 미명시(all18/nutrient10/antacid8/명시 ids)")
    if not any(m in note for m in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(한 번에/성분별/상대성분별/subset)")
    if not any(m in note for m in ANTACID_MARKERS):
        bad.append("category 결정 'al_mg_antacid'(Al/Mg 제산제=약물 counterpart·id61 선례) 미명시")
    if not any(m in note for m in INTERVAL_MARKERS):
        bad.append("separation 간격(2~4시간) 카드 노출 여부 결정 미명시")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품 추천 아님 명시 필요")
    if not any(m in note for m in NOT_SUPPLEMENT_MARKERS):
        bad.append("금속이온/제산제 복용 권유 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품/보충 추천 허용 문구 — 금지")
    if SUPPLEMENT_RECO_RE.search(note):
        bad.append("금속이온/제산제 복용 권유/권장 허용 문구 — 금지")
    return note, bad


def _index_impact(recs):
    """full index/aliases 영향(읽기전용)."""
    idx = json.load(open(FULL_INDEX, encoding="utf-8"))
    ents = idx["entries"]
    al = json.load(open(ALIASES, encoding="utf-8"))
    al_txt = json.dumps(al, ensure_ascii=False)
    ings = sorted({r["drug_ingredient"] for r in recs})
    per = {}
    flips = 0
    for ing in ings:
        matched = [e for e in ents if ing in (e.get("ingredient_name") or "")]
        covered = sum(1 for e in matched if e.get("covered_by_relation"))
        name_only = sum(1 for e in matched if not e.get("covered_by_relation"))
        flips += name_only
        per[ing] = {"index_items": len(matched), "covered_by_relation": covered,
                    "name_only": name_only, "in_aliases": ing in al_txt}
    counts = idx["meta"].get("counts", {})
    return {
        "full_index_counts_current": counts,
        "per_ingredient": per,
        "relation_card_flip_required": flips,
        "relation_card_after": counts.get("relation_card"),
        "name_only_after": counts.get("name_only"),
        "index_change_required": flips > 0,
        "alias_change_required": False,
        "interpretation": "레보/오플록사신은 이미 covered(live ×광물). 신규 6 성분(노르·로메·발로·자보·토수·페플록사신)은 "
                          "현 index sample(17,580)에 부재 → flip 0 · relation_card 1168/name_only 16412 불변. "
                          "index/aliases 는 relation export 와 decoupled(런타임 재생성·fail-soft 검색보조) → F1 통합 선행 변경 불필요. "
                          "차후 index 재생성 시 6 성분 품목이 추가되면 자연히 relation_card 로 표기(별도 index 작업·통합 전제 아님).",
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
    recs, summary = load_f1()
    scope_label, scope_ids = resolve_scope(recs)
    entries, viol = build_subset(exp, scope_ids)
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== F1 퀴놀론 {scope_label}({len(entries)}건) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
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

        # scope별 예상(runtime max+1) — 단독 통합 시.
        def scope_proj(cids):
            return {"count": len(cids), "expected_count": before + len(cids),
                    "expected_ids": list(range(base_max + 1, base_max + 1 + len(cids))),
                    "candidate_ids": cids}
        scope_scenarios = {
            "recommended": "by_counterpart_2wave",
            "all18": scope_proj([r["candidate_id"] for r in recs]),
            "nutrient10": scope_proj(nutrient_ids),
            "antacid8": scope_proj(antacid_ids),
            "by_counterpart_2wave": {
                "wave1_nutrient10": {"expected_count": before + len(nutrient_ids),
                                     "note": "live FQ×광물과 동일 렌더·신규성 0 → 1차 권고."},
                "wave2_antacid8": {"expected_count": before + len(nutrient_ids) + len(antacid_ids),
                                   "note": "id61 al_mg_antacid 렌더 경로 → 2차."},
                "note": "wave1 60→70, wave2 70→78. rollback 단위 분리·reviewer 부담 분할. all18 일괄도 허용(양 렌더 경로 live 검증됨).",
            },
            "by_ingredient": {ing: sorted(r["candidate_id"] for r in recs if r["drug_ingredient"] == ing)
                              for ing in sorted({r["drug_ingredient"] for r in recs})},
            "id_rule": "id 는 runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. AT-FEX/칼륨/theme/페니실라민 먼저면 자동 조정.",
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
                "name": "f1_quinolone_inventory_v1_4",
                "status": "DRAFT-ONLY — NOT LIVE / live_integration_forbidden=true / 적대검증(survives)+F1 family 재검증 통과만",
                "purpose": "F1 플루오로퀴놀론 18건 감사 + 작업 C family-specific 재검증(10 렌즈). reviewer package/integrator 의 단일 소스.",
                "family": "F1 Fluoroquinolone × metal cation / Al·Mg 함유 제산제(absorption/separation)",
                "count": len(recs),
                "counterpart_split": {"nutrient": len(nutrient_ids), "al_mg_antacid": len(antacid_ids)},
                "reverify_counts": summary["counts"],
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "confirmed_at": CONFIRMED_AT,
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
            json.dump({"meta": {"name": "f1_quinolone_index_impact_v1_4",
                                "status": "ANALYSIS — read-only / no index/alias write",
                                "purpose": "F1 18건 live 통합 시 full index/relation_card/name_only/aliases 영향 분석.",
                                "confirmed_at": CONFIRMED_AT},
                       "impact": index_impact}, f, ensure_ascii=False, indent=1)
            f.write("\n")

        # ── 작업 G dry-run ──
        artifact = {
            "meta": {
                "name": "f1_quinolone_live_dryrun_v1_4",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "F1 18건 live 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_f1_quinolone_dryrun_v1_4.py 가 안전·계약을 검증.",
                "requested_scope": scope_label,
                "baseline_relations": before, "baseline_max_id": base_max,
                "expected_relation_count_before": before,
                "expected_relation_count_after_full": before + len(recs),
                "expected_relation_count_after": after,
                "expected_ids_full": list(range(base_max + 1, base_max + 1 + len(recs))),
                "expected_ids": ids,
                "included_candidate_ids": [e["candidate_id"] for e in entries],
                "all_f1_candidate_ids": [r["candidate_id"] for r in recs],
                "excluded_non_f1_note": "다른 family(F2/F3/F4/F6/F9/F10)·pending(페니실라민/theme/칼륨/AT-FEX)은 본 batch 제외.",
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
                    "separation_interval_decision_required": True,
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/placeholder/빈 노트 · 토큰/candidate_id(scope 전건)/scope/grouping/al_mg_antacid/"
                               "간격/verified_reference 누락 · clinical_reviewed=true·제품추천·금속이온/제산제 복용 권유 허용",
                    "template": "docs/MediStack_reviewer_package_f1_quinolone_v1_4.md §reviewer-note",
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
                },
                "duplicate_summary": {"exact_dup_with_live": dup,
                                      "note": "레보/오플록사신은 live 에 ×광물(nutrient)만 — al_mg_antacid 는 별도 counterpart(id61 선례)로 중복 아님."},
                "conflict_summary": {
                    "live_60": "중복 0(위 duplicate_summary).",
                    "penicillamine_2": "성분/counterpart 무관 — 충돌 0.",
                    "theme_map_6": "지용성비타민/세팔로 acid_reducing_drug/페니실라민 — F1 무관·충돌 0.",
                    "potassium_4": "이뇨제×칼륨 depletion — F1 무관·충돌 0.",
                    "at_fex_1": "펙소페나딘×제산제 — F1 무관·충돌 0.",
                    "at_itz_id61": "이트라코나졸×Al/Mg제산제 — 동일 al_mg_antacid 렌더 경로(선례)·성분 다름·충돌 0.",
                    "other_factory_families": "F2/F3/F9/F10 reviewer-ready — 성분/관계 다름·충돌 0.",
                    "full_factory_integrator_dedup": "차후 factory 37 일괄 integrator 는 (ingredient, counterpart/category-counterpart) "
                                                     "키로 본 F1 통합분을 skip 해야 함(중복 생성 금지).",
                },
                "full_index_alias_impact": index_impact,
                "v0_2_validator_evidence": {
                    "sim_all_passed": ok_all, "sim_all_tail": tail_all,
                    "sim_nutrient_passed": ok_nut, "sim_nutrient_tail": tail_nut,
                    "interpretation": "al_mg_antacid(id61 선례)·일반 영양소(live FQ×광물) 둘 다 현행 v0.2 validator PASS → 선행조건 0.",
                },
                "render_safety_summary": "nutrient 10건 = live FQ×광물과 동일(영양소 facet·separation chip). "
                                         "al_mg_antacid 8건 = id61 렌더 경로(약물 counterpart kicker). src 변경 불필요.",
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
        print(f"[dry-run] index flip 필요={index_impact['relation_card_flip_required']} · alias 변경 필요={index_impact['alias_change_required']}.")
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
        (" | F1 퀴놀론 %s(%d건) live 통합: 플루오로퀴놀론 × 철분/칼슘/아연(영양소)·Al/Mg 함유 제산제(al_mg_antacid·약물). "
         "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지." % (scope_label, len(projected), before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE F1 QUINOLONE ({scope_label}): DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
