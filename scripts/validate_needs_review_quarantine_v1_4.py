#!/usr/bin/env python3
"""
validate_needs_review_quarantine_v1_4.py
MediStack v1.4 — needs_review 4건이 live PR 산출물(readiness/wave/command plan/note 요건/global true scenario)에
섞이지 않았는지 검증 (읽기전용·live 무수정). 종료코드 0 PASS / 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
fails = []


def J(p):
    return json.load(open(os.path.join(REV, p), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def main():
    print("=== needs_review 4 격리 검증 ===")
    Q = J("needs_review_quarantine_v1_4.json")
    R = J("per_family_live_pr_readiness_v1_4.json")
    cmd = J("live_pr_command_plan_v1_4.json")
    note = J("reviewer_note_requirements_live_pr_v1_4.json")
    gp = J("reviewer_ready_global_plan_v1_4.json")["meta"]

    nr = set(it["id"] for it in Q["items"])
    ck(len(nr) == 4, "needs_review 4건")
    ck(nr == set(sum(gp["needs_review_by_family"].values(), [])), "global plan needs_review 와 일치")
    ck(nr == {"RF-F3-0148", "RF-F3-0149", "RF-F9-0245", "RF-F10-0275"}, "대상 4건 정확")

    # readiness wave 전부 제외
    for w, wd in R["waves"].items():
        ck(not (nr & set(wd["candidate_ids"])), f"wave {w} 제외")
    # all33 true scenario 제외
    ck(not (nr & set(R["waves"]["all33"]["candidate_ids"])), "all33 제외")
    # reviewer note 템플릿 제외(승인 id 에 없음)
    for t, td in note["templates"].items():
        ck(not (nr & set(td["candidate_ids"])), f"note 템플릿 {t} 승인 id 제외")
    # command plan: 어떤 wave 의 actual integration 도 needs_review id 미포함 + DO NOT RUN guard
    for w, c in cmd["waves"].items():
        ck("DO NOT RUN" in c["04_actual_integration"], f"command {w} actual=DO NOT RUN guard")
    # 격리 메타
    ck(set(["all waves", "true scenario"]).issubset(set(Q["excluded_from"]))
       or len(Q["excluded_from"]) >= 3, "excluded_from 명시")
    # 각 항목 resolve_when 명시
    ck(all(it.get("resolve_when") for it in Q["items"]), "각 needs_review 해소 조건 명시")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — needs_review 4 전 산출물에서 격리 · true scenario/wave/note/command 제외 · 해소 조건 명시")
    return 0


if __name__ == "__main__":
    sys.exit(main())
