#!/usr/bin/env python3
"""
audit_depletion_fidelity_v1_8.py — depletion 후보 **독립 fidelity-audit + 승격 가드(DB1-7)**.

추출기(extract_label_depletion_v1_8)와 **별개 코드 경로**로 refute-by-default 재검증한다.
auto_pass(추출 성공)만으로 reviewer-ready 직행 금지(DB6) — 본 audit PASS 만 reviewer-ready.

🔑 칼륨 invariant(영구 불변): nutrient==칼륨 인 모든 신규 후보는
   potassium_safety_card=true + product_link_allowed=false 강제. 누락 시 그 후보 reject(가드).

승격 가드(hard rule):
  DB1 counterpart 가 정의된 영양소(칼륨/마그네슘 등) 아니면 승격 금지.
  DB2 B2 — 임부/이상반응-무관(상호작용 약-약·과량·고령자) 맥락 결핍은 승격 금지(in-scope 강제).
  DB3 mechanism=depletion + 결핍 명시(STATE/배설증가/저하) 없으면 승격 금지.
  DB4 source 없거나 문장 불완전하거나 scope 약하면 needs_review.
  DB5 copy-lint: 보충 지시 단정·수치 단정·source 초과·능동 register → reject.
  DB6 auto_pass → reviewer-ready 직행 금지. 본 audit(인용완전성·섹션출처·방향성·칼륨플래그·copy fidelity) PASS 만.
  DB7 auto_pass 전수 또는 ≥20% spot-check. false_auto_pass ≥1 → batch 재검 + 보고(호출자).

공개 API:
  safe_depletion_copy(nutrient) -> (display, management)
  potassium_enforce(rel) -> (rel, violations)
  fidelity_audit(cand, label_html=None, live_pairs=None) -> {verdict, lenses, flags}
  audit_corpus(cands, label_htmls=None, live_pairs=None) -> {per, counts, false_auto_pass}
  potassium_invariant_ok(rels) -> (ok, violations)
verdict ∈ {reviewer_ready, needs_review, reject}
"""
import importlib.util
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_tpl = _load("tpl", "fix_harvester_display_template_v1_6.py")   # safe_app_copy / copy_lint / quote_truncation_ok
_dp = _load("dp", "extract_label_depletion_v1_8.py")            # nutrient_depletion / is_depletion_scope

# v1.8 depletion 추출기 범위 = 칼륨/마그네슘(엽산/비타민D/B12 는 F9 별도 파이프라인 — 본 audit 의 방향검증 밖).
DEFINED_NUTRIENTS = {"칼륨", "마그네슘"}
POTASSIUM = "칼륨"
# display/management 에서 금지(모니터링 톤) — 보충/검사/처방 지시.
DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "보충하세요",
             "섭취하세요", "검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요"]
# display 노출 금지 — 소아/골/치아 알람어(라벨 quote 엔 있을 수 있으나 카드 비노출).
DISPLAY_ALARM = ["소아", "임신", "수유", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아"]
PREG_TOKENS = ("임부", "임산부", "임신", "태아", "수유", "신생아", "분만")


def safe_depletion_copy(nutrient):
    """live 선례 depletion 템플릿(DEPL_DISPLAY/DEPL_MGMT)만 사용 — 신규 문구 창작 0·보충 단정 0."""
    return _tpl.safe_app_copy(nutrient, "depletion")


def potassium_enforce(rel):
    """🔑 칼륨 invariant 강제. 칼륨 행은 safety_card=true·product_link=false. 위반 violations 반환."""
    nut = rel.get("nutrient")
    viol = []
    if nut == POTASSIUM:
        if rel.get("potassium_safety_card") is not True:
            viol.append("칼륨인데 potassium_safety_card!=true")
        if rel.get("product_link_allowed") is not False:
            viol.append("칼륨인데 product_link_allowed!=false")
    else:
        if rel.get("potassium_safety_card") is not False:
            viol.append(f"비칼륨({nut})인데 potassium_safety_card!=false")
    return rel, viol


def _is_hedged(quote):
    """효과 부정/완화 헤지('과잉 투여시 이외에는 ... 염려가 없다' 류) — 단독 근거로는 약함."""
    q = quote or ""
    return any(h in q for h in ("염려가 없다", "우려가 없다", "문제되지 않", "없다고 보고"))


def fidelity_audit(cand, label_html=None, live_pairs=None):
    """후보 1건 독립 재검증(refute-by-default). 반환 {verdict, lenses, flags}."""
    L, flags = {}, []
    nut = cand.get("nutrient")
    q = cand.get("source_quote", "") or ""
    sec = cand.get("source_section", "") or ""
    rel = cand.get("projected_relation", {}) or {}
    disp = rel.get("display_text_ko", cand.get("display_text_ko", "")) or ""
    mng = rel.get("management_ko", cand.get("management_ko", "")) or ""
    seq = str(cand.get("itemSeq", ""))

    # A1 source fidelity: itemSeq 실값 + section + (라벨 주어지면) quote verbatim 포함.
    a1 = seq.isdigit() and len(seq) >= 8 and bool(sec)
    if label_html is not None:
        a1 = a1 and (q in label_html)
    L["A1_source_fidelity"] = "pass" if a1 else "fail:itemSeq/section/verbatim"
    # A2 quote 완전성(잘림 0)
    L["A2_quote_complete"] = "pass" if (_tpl.quote_truncation_ok(q) and re.search(r"[다것요]\.$|\.$", q)) \
        else "fail:불완전/잘림"
    # A3 scope(in-scope·off-scope 배제) — DB2
    L["A3_scope_inscope"] = "pass" if _dp.is_depletion_scope(sec) else f"fail:off-scope({sec})"
    # A4 방향성(결핍 ↓, 상승 아님) — DB3
    dn, kind = _dp.nutrient_depletion(q)
    L["A4_direction_depletion"] = "pass" if (dn == nut) else f"fail:방향/영양소 불일치({dn},{kind})"
    # A5 B2 no-preg(문장·섹션 임신/태아 맥락 아님) — DB2
    L["A5_b2_no_preg"] = "pass" if not any(p in q or p in sec for p in PREG_TOKENS) else "fail:임신/태아 맥락"
    # A6 영양소 정의 — DB1
    L["A6_nutrient_defined"] = "pass" if nut in DEFINED_NUTRIENTS else f"fail:미정의 영양소({nut})"
    # A7 🔑 칼륨 invariant — DB(칼륨 safety)
    _r, kviol = potassium_enforce(rel)
    L["A7_potassium_invariant"] = "pass" if not kviol else f"fail:{kviol}"
    # A8 copy fidelity(보충/지시/수치/source초과/알람어) — DB5
    cl = _tpl.copy_lint(disp, q) + _tpl.copy_lint(mng, q)
    cl += [f"directive:{d}" for d in DIRECTIVE if d in (disp + " " + mng)]
    cl += [f"display_alarm:{a}" for a in DISPLAY_ALARM if a in disp]
    L["A8_copy_fidelity"] = "pass" if not cl else f"fail:{cl[:4]}"
    # A9 live 중복 금지
    pair = (rel.get("ingredient", cand.get("ingredient")), nut)
    L["A9_no_live_dup"] = "pass" if (live_pairs is None or pair not in live_pairs) else f"fail:live 중복 {pair}"
    # A10 결핍 명시(bare mention 아님) — DB3
    L["A10_explicit_deficiency"] = "pass" if cand.get("evidence_kind") in (
        "deficiency_state", "excretion_increase", "level_decrease") else "fail:결핍 kind 없음"
    # A11 제품/임상/published 금지
    L["A11_no_product_clinical"] = "pass" if (rel.get("product_link_allowed") is False
                                              and rel.get("requires_clinical_review") is False) else "fail:flag"

    if _is_hedged(q) and cand.get("evidence_kind") != "deficiency_state":
        flags.append("hedged_quote(단독 근거 약함 — 더 강한 finding 선호)")

    hard_fail = any(str(v).startswith("fail") for v in L.values())
    # 소프트(needs_review): A2 잘림 또는 A4 모호 외 약scope. 여기선 hard_fail=reject, 전부 pass=reviewer_ready,
    # 단 hedged-only 는 needs_review 로 강등.
    if hard_fail:
        verdict = "reject"
    elif flags:
        verdict = "needs_review"
    else:
        verdict = "reviewer_ready"
    return {"verdict": verdict, "lenses": L, "flags": flags}


def audit_corpus(cands, label_htmls=None, live_pairs=None):
    """후보 전수 audit(DB7). false_auto_pass = harvest 가 reviewer_ready 라 했는데 audit reject 인 것."""
    label_htmls = label_htmls or {}
    per, counts, false_ap = {}, {"reviewer_ready": 0, "needs_review": 0, "reject": 0}, []
    for c in cands:
        res = fidelity_audit(c, label_htmls.get(str(c.get("itemSeq"))), live_pairs)
        per[c.get("candidate_id", c.get("itemSeq"))] = res
        counts[res["verdict"]] = counts.get(res["verdict"], 0) + 1
        if c.get("harvest_verdict") == "reviewer_ready" and res["verdict"] == "reject":
            false_ap.append(c.get("candidate_id"))
    return {"per": per, "counts": counts, "false_auto_pass": false_ap}


def potassium_invariant_ok(rels):
    viol = []
    for r in rels:
        _r, v = potassium_enforce(r)
        if v:
            viol.append((r.get("ingredient"), r.get("nutrient"), v))
    return (not viol, viol)


if __name__ == "__main__":
    d, m = safe_depletion_copy("칼륨")
    assert _tpl.copy_lint(d) == [] and _tpl.copy_lint(m) == [], (d, m)
    assert "보충" not in d                                   # 칼륨 보충 단정 0
    _r, v = potassium_enforce({"nutrient": "칼륨", "potassium_safety_card": True, "product_link_allowed": False})
    assert not v
    _r, v = potassium_enforce({"nutrient": "칼륨", "potassium_safety_card": False, "product_link_allowed": False})
    assert v   # 칼륨 safety_card 누락 → 위반
    print("audit_depletion_fidelity_v1_8 self-check OK:", repr(d))
