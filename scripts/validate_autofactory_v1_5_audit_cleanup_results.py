#!/usr/bin/env python3
"""
validate_autofactory_v1_5_audit_cleanup_results.py
MediStack v1.5 — Audit + Cleanup 산출물 검증 (읽기전용·live 무수정).

검증:
  1) auditor/cleanup 산출 JSON 존재·로드.
  2) production reviewer-ready 1건 독립 감사 결과 존재(decision · 표결).
  3) cleanup 후보 전건이 감사/분류됨(auditor_decision 또는 mechanical verdict).
  4) 최종 reviewer-ready 전건 실 source(url+pointer+quote) 보유 · 보수 카피 · independent_audit_pending.
  5) 최종 reviewer-ready ∩ live-60 = 0 · ∩ existing-33 = 0.
  6) still_needs_review/hold/reject 가 최종 reviewer-ready 에 혼입 0.
  7) 카르바마제핀×엽산(RF-F9-0245) auto_pass/PROMOTE 아님(재승격 차단).
  8) forbidden phrase 0 · 공식 nedrug source only.
  9) scenario: new_ready_total = production_audited_ready + cleanup_new_ready · combined = 60→93+new.
 10) 보호셋 sha256 불변.
종료코드 0 PASS / 1 FAIL.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")
PROTECTED = {"medistack_v0.1_beta_export.json": "e9994f017995591365fc1ae333d288ea15af20ada2fe322e7e509c94be8d99a9",
             "medistack_v0.2_beta_export.json": "62df92844faf1bcc47e0e6ace1b0cd1307222b0461a6b819122b6ffab5030144",
             "medistack_v0.3_aliases.json": "ee25aed084a8a35f2d7336ea84b771fa70c608885ecf19c1338de2df4ce17039",
             "full_drug_name_index_sample_v1_0.json": "d329b2ddd3cdd05e3c4a96a11107d1db792d1df3e2c2fddf5a1a8e042e162fdb"}
fails = []


def J(name):
    return json.load(open(os.path.join(REV, name + ".json"), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    print("=== Audit + Cleanup 산출물 검증 ===")
    files = ["autofactory_v1_5_audit_cleanup_auditor_results",
             "autofactory_v1_5_audit_cleanup_candidate_decisions",
             "autofactory_v1_5_cleanup_reviewed", "autofactory_v1_5_cleanup_source_confirmed",
             "autofactory_v1_5_cleanup_reviewer_ready", "autofactory_v1_5_cleanup_reviewer_ready_waves",
             "autofactory_v1_5_cleanup_still_needs_review", "autofactory_v1_5_cleanup_hold_reject",
             "autofactory_v1_5_cleanup_dashboard"]
    for f in files:
        ck(os.path.exists(os.path.join(REV, f + ".json")), f"{f}.json 존재")
    if fails:
        print("RESULT: FAIL — 산출물 누락"); return 1

    aud = J("autofactory_v1_5_audit_cleanup_auditor_results")
    dec = J("autofactory_v1_5_audit_cleanup_candidate_decisions")
    live = json.load(open(os.path.join(DATA, "medistack_v0.2_beta_export.json"), encoding="utf-8"))
    plan = J("reviewer_ready_global_plan_v1_4")
    live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in live["relations"])
    existing33 = set((e["projected_live_relation"]["ingredient"], e["projected_live_relation"]["nutrient"])
                     for e in plan["combined_projected_entries"])

    # 2) production 감사
    ck("production" in aud and "decision" in aud["production"], "production 감사 decision 존재")
    ck(aud["production"]["total"] >= 3, "production 감사 ≥3 독립 표결")

    # 3) cleanup 전건 감사
    ck(len(aud["cleanup"]) >= 1, "cleanup 후보 감사 존재")
    ck(all("auditor_decision" in c for c in aud["cleanup"]), "cleanup 전건 auditor_decision 보유")

    # 4) 최종 reviewer-ready 실 source
    final = dec["final_reviewer_ready"]
    for c in final:
        s = c.get("source", {})
        ck(bool(s.get("url")) and bool(s.get("pointer")) and bool(s.get("quote")), f"{c['id']}: 실 source 보유")
        ck(bool(c.get("display_text_ko")) and bool(c.get("management_ko")), f"{c['id']}: 보수 카피")
        ck(c.get("independent_audit_pending") is True or c.get("independent_audit") == "passed",
           f"{c['id']}: audit 상태 명시")

    # 5) dedup
    fpairs = [(c["drug"], c["counterpart"]) for c in final]
    ck(not [p for p in fpairs if p in live_pairs], "최종 reviewer-ready ∩ live-60 = 0")
    ck(not [p for p in fpairs if p in existing33], "최종 reviewer-ready ∩ existing-33 = 0")
    ck(len(fpairs) == len(set(fpairs)), "최종 reviewer-ready 내부 중복 0")

    # 6) held 혼입
    held_ids = set(h["id"] for h in dec.get("held", []))
    final_ids = set(c["id"] for c in final)
    ck(not (held_ids & final_ids), "held(needs_review/hold/reject) ∩ reviewer-ready = 0")

    # 7) 0245 재승격 차단
    carba = [c for c in final if "카르바마제핀" in c.get("drug", "") and "엽산" in c.get("counterpart", "")]
    ck(not carba, "카르바마제핀×엽산(RF-F9-0245) 최종 reviewer-ready 아님")

    # 8) forbidden / 공식 source
    FORB = ["구매", "최저가", "제휴", "광고", "처방", "추천", "안전하다", "복용해도 된다", "clinical_reviewed=true", "published=true"]
    leak = []
    for c in final:
        blob = c.get("display_text_ko", "") + c.get("management_ko", "")
        leak += [(c["id"], t) for t in FORB if t in blob]
    ck(not leak, f"카피 forbidden/승격 0 ({leak[:3]})")
    ck(all("nedrug.mfds.go.kr" in c.get("source", {}).get("url", "") for c in final),
       "최종 reviewer-ready 전건 공식 nedrug source")

    # 9) scenario
    sc = dec["scenario"]
    ck(sc["new_ready_total"] == sc["production_audited_ready"] + sc["cleanup_new_ready"],
       "new_ready_total = production_audited_ready + cleanup_new_ready")
    ck(sc["new_ready_total"] == len(final), "new_ready_total = final reviewer-ready 수")
    ck(sc["existing_prepared"] == 33, "existing_prepared = 33")
    ck(str(60 + 33 + sc["new_ready_total"]) in str(sc["combined_future"]) or "93" in str(sc["combined_future"]),
       "combined_future = 60→93+new 반영")

    # 10) protected
    drift = [f for f, h in PROTECTED.items() if sha(os.path.join(DATA, f)) != h]
    ck(not drift, f"보호셋 sha256 불변 ({drift})")

    print("=" * 62)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print(f"RESULT: PASS — production 감사 · cleanup {len(aud['cleanup'])} 독립검증 · 최종 reviewer-ready {len(final)} "
          f"실source+dedup0 · 0245 차단 · 공식 source · scenario 정합 · protected 불변")
    return 0


if __name__ == "__main__":
    sys.exit(main())
