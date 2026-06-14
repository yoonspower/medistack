#!/usr/bin/env python3
"""
validate_harvest_queue_v1_3.py — harvester bot 산출물(data/harvest_queue/) **스키마·안전 검증 + PM smoke**.

검사:
  1) 출력 스키마: 7 산출물 존재 + 필수 컬럼/키.
  2) no-live-promote: 어떤 행도 published=true/clinical_reviewed=true 없음 · run_meta live_promotions==0 ·
     모든 draft·source-check 행 do_not_implement_yet=true · live_integration_forbidden=true.
  3) 금칙어: safe_copy / draft safe_copy / pm_review_queue 사용자 노출 카피에 FORBIDDEN 어구 0
     (권위있는 validate_forbidden_phrases.FORBIDDEN 재사용).
  4) PM queue smoke: pm_review_queue.md 에 필수 라벨(relation 후보/source quote/itemSeq/confidence/
     risk_level/recommended_action/safe copy 초안/live 승격 금지) + 'live relation 변경: 0' 존재.
  5) 칼륨 정책: potassium_safety_card=true 행은 항상 live 금지 플래그 유지.

⚠️ 읽기전용. 어떤 파일도 쓰지 않는다.
사용: python3 scripts/validate_harvest_queue_v1_3.py
종료코드: 0 PASS / 1 FAIL.
"""
import csv
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
Q = os.path.join(REPO, "data", "harvest_queue")

_spec = importlib.util.spec_from_file_location("vfp", os.path.join(HERE, "validate_forbidden_phrases_v1_2.py"))
vfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfp)

REQUIRED_FILES = ["harvest_candidates.csv", "source_check_results.csv", "rejected_precheck.csv",
                  "sensitive_hold.csv", "needs_review.csv", "draft_candidates.json",
                  "pm_review_queue.md", "run_meta.json"]
SC_REQUIRED_COLS = {"candidate_id", "track", "ingredient", "verdict", "draft_eligible",
                    "itemseqs_checked", "confidence", "risk_level", "gate_reason",
                    "safe_copy", "live_integration_forbidden"}
PM_REQUIRED_LABELS = ["relation 후보", "source quote", "itemSeq", "confidence",
                      "risk_level", "recommended_action", "safe copy 초안", "live 승격 금지"]

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def read_csv(name):
    with open(os.path.join(Q, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    print("=== validate_harvest_queue_v1_3 ===")
    # 1) 파일 존재
    missing = [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(Q, f))]
    ok("7+1 산출물 전부 존재", not missing, f"누락: {missing}")
    if missing:
        print("RESULT: FAIL — 산출물 누락"); return 1

    sc = read_csv("source_check_results.csv")
    draft = json.load(open(os.path.join(Q, "draft_candidates.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(Q, "run_meta.json"), encoding="utf-8"))
    pm = open(os.path.join(Q, "pm_review_queue.md"), encoding="utf-8").read()

    # 1) 스키마
    ok("source_check_results 필수 컬럼", sc == [] or SC_REQUIRED_COLS <= set(sc[0].keys()),
       str(SC_REQUIRED_COLS - set(sc[0].keys())) if sc else "")
    ok("draft_candidates.json 구조", "meta" in draft and "draft_candidates" in draft)

    # 2) no-live-promote
    dmeta = draft["meta"]
    ok("draft meta: do_not_implement_yet & live_integration_forbidden",
       dmeta.get("do_not_implement_yet") is True and dmeta.get("live_integration_forbidden") is True)
    ok("draft meta: published/clinical_reviewed = false",
       dmeta.get("published") is False and dmeta.get("clinical_reviewed") is False)
    ok("draft meta: live_promotions = 0", dmeta.get("live_promotions") == 0)
    bad_flags = [r["candidate_id"] for r in sc
                 if r.get("live_integration_forbidden") != "true"]
    ok("모든 source-check 행 live_integration_forbidden=true", not bad_flags, str(bad_flags[:5]))
    bad_draft = [r["candidate_id"] for r in draft["draft_candidates"]
                 if r.get("do_not_implement_yet") != "true" or r.get("live_integration_forbidden") != "true"
                 or r.get("published") != "false" or r.get("clinical_reviewed") != "false"]
    ok("모든 draft 행 live 금지 플래그", not bad_draft, str(bad_draft[:5]))
    ok("run_meta: live_relations_created=0 & live_promotions=0",
       meta.get("live_relations_created") == 0 and meta.get("live_promotions") == 0)
    ok("run_meta: deploy=none & live_data_written=False",
       meta.get("deploy") == "none" and meta.get("safety", {}).get("live_data_written") is False)

    # 3) 금칙어(사용자 노출 카피)
    copy_items = []
    for r in sc:
        if r.get("safe_copy", "").strip():
            copy_items.append((f"sc:{r['candidate_id']}", r["safe_copy"]))
    for r in draft["draft_candidates"]:
        if r.get("safe_copy", "").strip():
            copy_items.append((f"draft:{r['candidate_id']}", r["safe_copy"]))
    viol = [(lbl, vfp.scan(t)) for lbl, t in copy_items if vfp.scan(t)]
    ok(f"금칙어 0 (safe_copy {len(copy_items)}건)", not viol, str(viol[:3]))

    # 4) PM queue smoke
    missing_lbl = [l for l in PM_REQUIRED_LABELS if l not in pm]
    ok("pm_review_queue 필수 라벨 포함", not missing_lbl, f"누락: {missing_lbl}")
    ok("pm_review_queue: 'live relation 변경: 0' 명시", "live relation 변경: **0**" in pm)
    # PM md 본문(봇 작성) 금칙어 스캔 — 라벨 원문 인용('- source quote:')만 제외(원문엔 치료/예방 등 정당 등장).
    md_viol = []
    for line in pm.splitlines():
        if line.lstrip().startswith("- source quote:"):
            continue
        hits = vfp.scan(line)
        if hits:
            md_viol.append((line.strip()[:50], hits))
    ok("pm_review_queue 본문 금칙어 0(quote 제외)", not md_viol, str(md_viol[:3]))

    # 5) 칼륨 정책
    k_rows = [r for r in sc if r.get("potassium_safety_card") == "true"]
    k_bad = [r["candidate_id"] for r in k_rows if r.get("live_integration_forbidden") != "true"]
    ok(f"칼륨행 live 금지 유지 ({len(k_rows)}건)", not k_bad, str(k_bad))

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — 스키마·no-live-promote·금칙어·PM smoke 전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
