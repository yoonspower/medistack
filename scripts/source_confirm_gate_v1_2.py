#!/usr/bin/env python3
"""
source_confirm_gate_v1_2.py
MediStack — **단일 fail-closed source_confirm 게이트**(이번 라운드 B/C/D 후보 통합 판정).

설계 원칙(이 스크립트가 유일한 confirm/draft 판정 지점):
  - DEFAULT DENY. 애매하면 통과 금지(needs_review/reject).
  - source_confirmed 는 (a)허가사항 직접 동거어 + 방향 일치, (b)국내 단일 경구 완제 itemSeq 확보,
    (c)완화/부정 문구 부재, (d)계열 일반화 아님 — 4조건 전부 충족할 때만.
  - antacid_interaction 트랙은 영양소 relation 과 분리: Al/Mg 제산제 directive 동거 + directive context +
    부정문구 부재 + 단일 경구 itemSeq → antacid draft 후보(여전히 live_integration_forbidden=true).
  - ⚠️ 어떤 후보도 이번 라운드 **live 승격 금지**. confirm 되어도 draft(live_integration_forbidden=true) 까지만.

입력(읽기전용, 앞단계 결정론 산출물):
  D: data/coverage/coverage_queue_top301_500_source_check_v1_2.csv
  C: data/review/needs_review_itemseq_recheck_v1_2.csv
  B: data/candidates/antacid_interaction_evidence_v1_2.json
출력: data/review/source_confirm_gate_v1_2.json (통합 판정 ledger)
사용: python3 scripts/source_confirm_gate_v1_2.py
종료코드: 0(정상). 게이트는 데이터를 한 줄도 수정하지 않는다.
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
D_CSV = os.path.join(DATA, "coverage", "coverage_queue_top301_500_source_check_v1_2.csv")
C_CSV = os.path.join(DATA, "review", "needs_review_itemseq_recheck_v1_2.csv")
B_JSON = os.path.join(DATA, "candidates", "antacid_interaction_evidence_v1_2.json")
OUT = os.path.join(DATA, "review", "source_confirm_gate_v1_2.json")

# 완화/부정(흡수장애·고갈 주장 무효화). antacid quote 재검(defense in depth).
NEGATION_RE = re.compile(
    r"영향(을)?\s*(받지\s*않|미치지\s*않|주지\s*않|없)|임상적(으로)?\s*(유의|관련)성(이)?\s*없|"
    r"흡수\s*(장애|정도).{0,12}(일어나지\s*않|없)|유의(미|할만)?\s*(한|하지)?\s*않|"
    r"감소시키지\s*못|차이(가)?\s*없")
DIRECTIVE_RE = re.compile(r"복용하지|투여하지|병용\s*금지|간격|2\s*시간|투여\s*간격|동시\s*(복용|투여)|함께\s*(복용|투여|사용)")


def gate_nutrient(row, track):
    """nutrient 트랙(C/D) 단일 게이트. DEFAULT DENY."""
    st = row.get("source_status", "")
    seqs = row.get("itemseqs_checked", "")
    reason = row.get("rejection_or_needs_review_reason", "")
    if st == "source_confirmed" and seqs:
        return {"verdict": "source_confirmed", "draft_eligible": True,
                "live_integration_forbidden": True,
                "gate_reason": "허가사항 직접 동거어+방향 일치+단일 경구 itemSeq 확보(verify 결정론). 적대검증 후 draft only."}
    if st == "needs_review":
        return {"verdict": "needs_review", "draft_eligible": False, "live_integration_forbidden": True,
                "gate_reason": f"DENY(fail-closed): {reason or '단일 경구 완제 미확보/근거 불명확'}"}
    return {"verdict": "reject", "draft_eligible": False, "live_integration_forbidden": True,
            "gate_reason": f"DENY: {reason or '허가사항 직접 근거 없음'}"}


def gate_antacid(ev):
    """antacid_interaction 트랙(B) 단일 게이트. DEFAULT DENY. 영양소 relation 으로 박지 않는다."""
    if not ev.get("found"):
        if not ev.get("itemseqs_checked"):
            return {"verdict": "needs_review", "draft_eligible": False, "live_integration_forbidden": True,
                    "track": "antacid_interaction",
                    "gate_reason": "DENY: 국내 단일 경구 완제 itemSeq 미확보 — 직접 지정 재확인 필요."}
        return {"verdict": "reject", "draft_eligible": False, "live_integration_forbidden": True,
                "track": "antacid_interaction",
                "gate_reason": "DENY: 라벨에 Al/Mg 제산제 병용 directive 동거어 미확인."}
    quote = ev.get("quote", "")
    # defense in depth: directive context 必, 부정문구 不
    if NEGATION_RE.search(quote):
        return {"verdict": "reject", "draft_eligible": False, "live_integration_forbidden": True,
                "track": "antacid_interaction", "directive_kind": ev.get("directive_kind"),
                "gate_reason": "DENY: 제산제 동거어는 있으나 동일 문맥에 '흡수장애 일어나지 않음/영향 없음' 등 부정문구 → 상호작용 성립 불명확(과다해석 방지)."}
    if not DIRECTIVE_RE.search(quote):
        return {"verdict": "needs_review", "draft_eligible": False, "live_integration_forbidden": True,
                "track": "antacid_interaction", "directive_kind": ev.get("directive_kind"),
                "gate_reason": "DENY: 제산제 동거어 있으나 directive(복용금지/간격/동시복용) 문맥 약함 — 라벨 전문 재확인."}
    strength = {"avoid_concomitant": "high", "separation_or_spacing": "high",
                "coadmin_caution": "low"}.get(ev.get("directive_kind"), "low")
    return {"verdict": "antacid_draft_confirmed", "draft_eligible": True, "live_integration_forbidden": True,
            "track": "antacid_interaction", "directive_kind": ev.get("directive_kind"),
            "copy_strength": strength, "counterpart_category": "al_mg_antacid",
            "gate_reason": "Al/Mg 제산제 directive 동거어+directive 문맥+부정문구 부재+단일 경구 itemSeq → antacid draft 후보(영양소 relation 아님, live 금지)."}


def main():
    result = {
        "meta": {
            "name": "source_confirm_gate_v1_2", "created_at": "2026-06-14",
            "status": "GATE LEDGER — 단일 fail-closed 판정. live 승격 0(이번 라운드).",
            "principle": "DEFAULT DENY · 직접근거+단일경구itemSeq+부정문구부재+계열일반화아님 4조건 → confirm · confirm 되어도 draft(live_integration_forbidden=true)까지만.",
            "live_promotions_this_round": 0,
        },
        "nutrient_track": [], "antacid_track": [], "summary": {},
    }
    # D (Top301-500)
    if os.path.exists(D_CSV):
        for r in csv.DictReader(open(D_CSV, encoding="utf-8")):
            g = gate_nutrient(r, "D_top301_500")
            result["nutrient_track"].append({"candidate_id": r["candidate_id"], "track": "D_top301_500",
                                             "ingredient": r["drug_ingredient"], "nutrient": r["nutrient"],
                                             "itemseqs_checked": r["itemseqs_checked"], **g})
    # C (needs_review recheck)
    if os.path.exists(C_CSV):
        for r in csv.DictReader(open(C_CSV, encoding="utf-8")):
            g = gate_nutrient(r, "C_needs_review")
            result["nutrient_track"].append({"candidate_id": r["candidate_id"], "track": "C_needs_review",
                                             "ingredient": r["drug_ingredient"], "nutrient": r["nutrient"],
                                             "itemseqs_checked": r["itemseqs_checked"], **g})
    # B (antacid)
    if os.path.exists(B_JSON):
        b = json.load(open(B_JSON, encoding="utf-8"))
        for ev in b.get("evidence", []):
            g = gate_antacid(ev)
            result["antacid_track"].append({"candidate_id": ev["candidate_id"], "ingredient": ev["ingredient"],
                                            "itemseqs_checked": ev.get("itemseqs_checked", []),
                                            "quote": ev.get("quote", "")[:300], **g})

    from collections import Counter
    nv = Counter(x["verdict"] for x in result["nutrient_track"])
    av = Counter(x["verdict"] for x in result["antacid_track"])
    draft_elig = [x for x in result["nutrient_track"] + result["antacid_track"] if x["draft_eligible"]]
    result["summary"] = {
        "nutrient_verdicts": dict(nv), "antacid_verdicts": dict(av),
        "nutrient_source_confirmed": nv.get("source_confirmed", 0),
        "antacid_draft_confirmed": av.get("antacid_draft_confirmed", 0),
        "draft_eligible_total": len(draft_elig),
        "live_promotions": 0,
    }
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("=== source_confirm_gate (단일 fail-closed) ===")
    print(f"nutrient track verdicts: {dict(nv)}")
    print(f"antacid  track verdicts: {dict(av)}")
    print(f"draft-eligible: {len(draft_elig)} (live promotions: 0)")
    for x in draft_elig:
        print(f"  DRAFT-OK [{x.get('track','antacid')}] {x['candidate_id']} {x['ingredient']} "
              f"({x['verdict']}{'/'+x.get('directive_kind','') if x.get('directive_kind') else ''}) live_forbidden={x['live_integration_forbidden']}")
    print(f"[write] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
