#!/usr/bin/env python3
"""
validate_live_pr_wave_rehearsal_v1_4.py
rehearse_live_pr_waves_no_write_v1_4 결과(live_pr_wave_rehearsal_v1_4.json) 무결성 검증 (읽기전용·live 무수정).
없으면 rehearsal --emit 으로 생성 후 검증. 종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
OUT = os.path.join(REV, "live_pr_wave_rehearsal_v1_4.json")
READINESS = os.path.join(REV, "per_family_live_pr_readiness_v1_4.json")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def main():
    if not os.path.exists(OUT):
        spec = importlib.util.spec_from_file_location(
            "reh", os.path.join(HERE, "rehearse_live_pr_waves_no_write_v1_4.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        old = sys.argv
        sys.argv = ["prog", "--wave", "all", "--base-count", "60", "--dry-run", "--emit"]
        try:
            mod.main()
        finally:
            sys.argv = old

    d = json.load(open(OUT, encoding="utf-8"))
    R = json.load(open(READINESS, encoding="utf-8"))
    print("=== live PR wave rehearsal 결과 검증 ===")
    m = d["meta"]
    ck(m["live_write"] is False, "rehearsal live_write=false")
    ck(m["protected_unchanged"] is True, "protected 파일 무수정")
    ck(m["live_export_unchanged"] is True, "live export 무수정")
    ck(m["live_relations"] == 60, "live relations 60")
    # 10 wave 전부 rehearsed + pass
    ck(len(d["results"]) == 10, "10 wave rehearsed")
    ck(all(r["pass"] for r in d["results"]), "전 wave rehearsal pass")
    # wave별 delta/planned 가 readiness 와 일치
    for r in d["results"]:
        w = R["waves"][r["wave"]]
        c = r["checks"]
        ck(c["delta"] == w["delta"] and c["candidate_count"] == len(w["candidate_ids"]),
           f"{r['wave']}: delta/count readiness 일치")
        ck(not c["live_exact_duplicate"] and not c["needs_review_in_wave"],
           f"{r['wave']}: live 중복 0 · needs_review 0")
        ck(c["index_auto_flip"] == 0 and c["index_relation_card_delta"] == 0 and c["index_name_only_delta"] == 0,
           f"{r['wave']}: index flip 0(relation-only)")
        ck(c["command_has_no_run_guard"], f"{r['wave']}: command plan DO-NOT-RUN guard 존재")
    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — rehearsal 결과 무결 · live_write=false · protected/live 무수정 · 10 wave readiness 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
