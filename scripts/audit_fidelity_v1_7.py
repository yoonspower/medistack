#!/usr/bin/env python3
"""
audit_fidelity_v1_7.py — B7/B8 독립 fidelity-audit (harvested 신규 후보용).

auto_pass → reviewer-ready 직행 금지. 이 모듈은 harvest 경로를 **신뢰하지 않고**, 캐시된 라벨 HTML 에서
독립적으로 재추출해 다음을 재검한다:
  - 인용 완전성·section 출처: candidate 의 source_quote 가 재추출 상호작용 finding 에 verbatim 존재.
  - 방향성: this_drug_lowered (이 약 흡수 저하) 여야 separation-supporting.
  - counterpart 정합: 재추출 category 와 일치.
  - B1~B4 승급 가드(audit_fidelity_v1_6.promotion_guards 재사용).
  - B6 copy fidelity: display/management 가 Phase A copy_lint clean(필요시 reframe; 불가 시 fail).
verdict: reviewer_ready / reviewer_ready_corrected / audit_fail_{quote,direction,counterpart,copy} / needs_review.
B8: auto_pass 인데 audit fail → false_auto_pass → batch_recheck.
"""
from __future__ import annotations

import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_fix = _load("fix_v16", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))
_v16 = _load("audit_v16", os.path.join(HERE, "audit_fidelity_v1_6.py"))
_ex = _load("extract_v17", os.path.join(HERE, "extract_label_interaction_v1_7.py"))


def audit_harvested(cand, raw_html):
    """harvested 후보 1건을 캐시 HTML 에서 독립 재검. 반환 dict(verdict + 재검 근거)."""
    res = {
        "candidate_id": cand["candidate_id"], "family": cand["family"],
        "ingredient": cand["ingredient"], "counterpart": cand["counterpart"],
        "mechanism": cand["mechanism"], "action": cand["action"],
        "evidence_level": cand.get("evidence_level", "moderate"),
        "source_pointer": cand.get("source_pointer", ""),
        "item_seq": cand["item_seq"],
        "display_text_ko": cand.get("display_text_ko", ""),
        "management_ko": cand.get("management_ko", ""),
        "already_live_on_base": cand.get("already_live_on_base", False),
        "auto_pass_claimed": True,
    }
    quote = cand.get("source_quote", "")

    # 1) 독립 재추출 — harvest 경로 신뢰 0.
    findings = _ex.extract_interactions(raw_html or "")
    match = next((f for f in findings if f["source_quote"] == quote), None)
    if not raw_html or match is None:
        res.update(verdict="audit_fail_quote_not_reproduced", audit_pass=False,
                   reproduced=False, reason="캐시 HTML 재추출에서 quote verbatim 미확인(또는 HTML 없음)")
        res["false_auto_pass"] = True
        return res
    res["reproduced"] = True
    res["reproduced_section"] = match["section"]

    # 2) 방향성
    if match["direction"] != "this_drug_lowered":
        res.update(verdict="audit_fail_direction", audit_pass=False,
                   reason=f"방향={match['direction']} (this_drug_lowered 아님)")
        res["false_auto_pass"] = True
        return res

    # 3) counterpart 정합(category 버킷)
    if match["counterpart_category"] != cand["counterpart_category"]:
        res.update(verdict="audit_fail_counterpart", audit_pass=False,
                   reason=f"counterpart 재추출={match['counterpart_category']} ≠ claim={cand['counterpart_category']}")
        res["false_auto_pass"] = True
        return res

    # 3b) counterpart **표시명 특정성** 정당성(원문보다 강하면 금지) — 독립 재검.
    #     예: 'Al/Mg 함유 제산제(약물)'는 quote 에 알루미늄·마그네슘이 모두 명명돼야 한다.
    #     일반 '제산제'만 명명된 라벨을 Al/Mg-specific 으로 좁히면 source-fidelity 위반(B7 가 차단).
    if not _ex.counterpart_scope_justified(cand["counterpart"], quote):
        res.update(verdict="audit_fail_counterpart_overclaim", audit_pass=False,
                   reason=f"counterpart 표시명 '{cand['counterpart']}'의 양이온 특정성이 quote 에 미명명(원문보다 강함)")
        res["false_auto_pass"] = True
        return res

    # 4) B1~B4 승급 가드(v1.6 재사용)
    rel = {"nutrient": cand["counterpart"], "counterpart_category": cand["counterpart_category"],
           "mechanism": cand["mechanism"], "recommended_action": cand["action"],
           "source": {"pointer": cand.get("source_pointer", "")}}
    guards = _v16.promotion_guards(rel, cand)
    if guards:
        res.update(verdict="audit_fail_guard", audit_pass=False, guard_violations=guards)
        res["false_auto_pass"] = True
        return res

    # 5) 인용 완전성(B5) — 종결부호로 끝나는 완전 문장.
    if not _fix.quote_truncation_ok(quote):
        res.update(verdict="audit_fail_quote_truncated", audit_pass=False,
                   reason="quote 완전성 미달(잘림/짧음)")
        res["false_auto_pass"] = True
        return res

    # 6) B6 copy fidelity — display/management copy_lint clean(필요시 reframe).
    disp, mgmt = cand.get("display_text_ko", ""), cand.get("management_ko", "")
    disp_v = _fix.copy_lint(disp, quote)
    mgmt_v = _fix.copy_lint(mgmt, quote)
    corrected = None
    if disp_v:
        try:
            corrected = _fix.reframe_display(disp, action=cand["action"])
        except Exception:
            corrected = None
        if corrected is None or _fix.copy_lint(corrected, quote):
            res.update(verdict="audit_fail_copy", audit_pass=False, copy_violations=disp_v)
            res["false_auto_pass"] = True
            return res
        res["corrected_display_text_ko"] = corrected
    if mgmt_v:
        res.update(verdict="audit_fail_copy", audit_pass=False, copy_violations=mgmt_v)
        res["false_auto_pass"] = True
        return res

    res.update(verdict=("reviewer_ready_corrected" if corrected else "reviewer_ready"),
               audit_pass=True, copy_corrected=bool(corrected))
    res["false_auto_pass"] = False
    return res


def audit_harvested_corpus(cands, html_provider):
    """harvested 후보 전수 독립 audit. html_provider(item_seq)->raw_html. (results, summary)."""
    results = [audit_harvested(c, html_provider(c["item_seq"])) for c in cands]
    audit_pass = sum(1 for r in results if r.get("audit_pass"))
    false_pass = sum(1 for r in results if r.get("false_auto_pass"))
    corrected = sum(1 for r in results if r.get("verdict") == "reviewer_ready_corrected")
    summary = {
        "total_audited": len(results),
        "audit_pass": audit_pass,
        "reviewer_ready_corrected": corrected,
        "false_auto_pass": false_pass,
        "batch_recheck_required": false_pass > 0,
    }
    return results, summary
