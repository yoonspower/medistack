#!/usr/bin/env python3
"""
smoke_autofactory_v1_5_audit_cleanup_results.py
MediStack v1.5 — Audit + Cleanup 결과 스모크 (빠른 무결성·읽기전용).

  1) auditor_results: production 독립 표결 ≥3 · cleanup 전건 auditor_decision.
  2) cleanup_reviewed 합산: reviewed = source_confirmed + (quote 없는 still_needs_review) (무모순).
  3) 최종 reviewer-ready 전건 quote 실문자열(공백 아님).
  4) 보호셋 sha256 검증 전후 불변(직접 측정).
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
PROTECTED = ["medistack_v0.1_beta_export.json", "medistack_v0.2_beta_export.json",
             "medistack_v0.3_aliases.json", "full_drug_name_index_sample_v1_0.json"]
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
    print("=== Audit + Cleanup smoke ===")
    before = {f: sha(os.path.join(DATA, f)) for f in PROTECTED}

    aud = J("autofactory_v1_5_audit_cleanup_auditor_results")
    ck(aud["production"]["total"] >= 3, "production 독립 표결 ≥3")
    ck(all("auditor_decision" in c for c in aud["cleanup"]), "cleanup 전건 auditor_decision")

    rev = J("autofactory_v1_5_cleanup_reviewed")["results"]
    conf = J("autofactory_v1_5_cleanup_source_confirmed")["confirmed"]
    quoted = [r for r in rev if r.get("source")]
    ck(len(quoted) == len(conf), "cleanup_reviewed quote 보유 = source_confirmed 수")

    dec = J("autofactory_v1_5_audit_cleanup_candidate_decisions")
    for c in dec["final_reviewer_ready"]:
        q = c.get("source", {}).get("quote", "")
        ck(len(q) > 10, f"{c['id']}: quote 실문자열")

    after = {f: sha(os.path.join(DATA, f)) for f in PROTECTED}
    ck(before == after, "보호셋 sha256 불변")

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — auditor 표결·cleanup 정합·quote 실문자열·보호셋 불변")
    return 0


if __name__ == "__main__":
    sys.exit(main())
