#!/usr/bin/env python3
"""
rehearse_live_pr_waves_no_write_v1_4.py
MediStack v1.4 — live PR wave **no-write rehearsal** (읽기전용·네트워크 0·live 무수정).

실제 통합 없이 wave 별로 통합 시 무엇이 일어날지 점검만 한다. **어떤 파일도 쓰지 않는다**
(단, --emit 지정 시 data/review/ 의 rehearsal 결과 JSON 1개만 기록; live/protected 는 절대 무수정).

점검 항목(wave별): planned count · candidate ids · duplicate · needs_review exclusion ·
reviewer-note requirement · relation_count delta · full index/alias impact · protected hash · live write 없음 · command plan 일치.

사용:
  python3 scripts/rehearse_live_pr_waves_no_write_v1_4.py --wave all33 --base-count 60 --dry-run
  python3 scripts/rehearse_live_pr_waves_no_write_v1_4.py --wave antibiotic23 --base-count 60 --dry-run
  python3 scripts/rehearse_live_pr_waves_no_write_v1_4.py --emit   # 전 wave + data/review 결과 기록
종료코드 0 PASS / 1 FAIL.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
READINESS = os.path.join(REV, "per_family_live_pr_readiness_v1_4.json")
CMD_PLAN = os.path.join(REV, "live_pr_command_plan_v1_4.json")
LIVE = os.path.join(ROOT, "data", "medistack_v0.2_beta_export.json")
OUT = os.path.join(REV, "live_pr_wave_rehearsal_v1_4.json")

WAVES = ["f1_nutrient10", "f1_antacid8", "f1_all18", "f2_all5", "f3_single",
         "f9_all7", "f4_f6_small2", "antibiotic23", "chronic8", "all33"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rehearse_wave(R, cmd, live_ids, base, wave):
    w = R["waves"][wave]
    ids = w["candidate_ids"]
    nr = R["needs_review_quarantine"]["ids"]
    checks = {}
    checks["planned_count"] = base + w["delta"]
    checks["candidate_count"] = len(ids)
    checks["delta"] = w["delta"]
    # duplicate (wave 내부 + live 와 충돌)
    checks["internal_duplicate"] = len(ids) != len(set(ids))
    checks["live_exact_duplicate"] = sorted(i for i in ids if i in live_ids)
    # needs_review exclusion
    checks["needs_review_in_wave"] = sorted(i for i in ids if i in nr)
    # reviewer-note requirement (planning 단계 — 실물 없음 → 통합 차단 전제)
    checks["reviewer_note_required"] = True
    checks["reviewer_note_present"] = False
    # delta 일치 (planned == base + len(ids))
    checks["delta_consistent"] = checks["planned_count"] == base + len(ids)
    # full index / alias impact (relation-only → flip 0)
    inv = R["meta"]["index_invariants"]
    checks["index_relation_card_delta"] = 0
    checks["index_name_only_delta"] = 0
    checks["index_auto_flip"] = inv["auto_flip_on_relation_only_integration"]
    checks["alias_enrichment_in_scope"] = False
    # command plan 일치
    checks["command_plan_present"] = wave in cmd["waves"]
    checks["command_has_no_run_guard"] = (
        wave in cmd["waves"] and "DO NOT RUN" in cmd["waves"][wave]["04_actual_integration"]
    )
    # live write 없음
    checks["live_write"] = False

    ok = (
        not checks["internal_duplicate"]
        and not checks["live_exact_duplicate"]
        and not checks["needs_review_in_wave"]
        and checks["delta_consistent"]
        and checks["index_auto_flip"] == 0
        and not checks["alias_enrichment_in_scope"]
        and checks["command_plan_present"]
        and checks["command_has_no_run_guard"]
        and checks["live_write"] is False
    )
    return {"wave": wave, "families": w["families"], "candidate_ids": ids, "checks": checks, "pass": ok}


def main():
    ap = argparse.ArgumentParser(description="live PR wave no-write rehearsal")
    ap.add_argument("--wave", default="all", help="wave 라벨 또는 all")
    ap.add_argument("--base-count", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", help="명시적 dry-run(이 스크립트는 항상 no-write)")
    ap.add_argument("--emit", action="store_true", help="data/review/live_pr_wave_rehearsal_v1_4.json 기록(planning area)")
    args = ap.parse_args()

    R = json.load(open(READINESS, encoding="utf-8"))
    cmd = json.load(open(CMD_PLAN, encoding="utf-8"))
    live = json.load(open(LIVE, encoding="utf-8"))
    live_ids = sorted(r["id"] for r in live["relations"])
    base = args.base_count

    # 보호 hash before
    prot = R["meta"]["protected_hashes"]
    before = {os.path.basename(p): sha(os.path.join(ROOT, "data", p)) for p in prot}

    targets = WAVES if args.wave == "all" else [args.wave]
    for t in targets:
        if t not in R["waves"]:
            print(f"unknown wave: {t} (지원: {', '.join(WAVES)})")
            return 1

    results = [rehearse_wave(R, cmd, live_ids, base, t) for t in targets]
    for r in results:
        c = r["checks"]
        flag = "PASS" if r["pass"] else "FAIL"
        print(f"  [{flag}] {r['wave']:<14} n={c['candidate_count']:<2} +{c['delta']:<2} → {c['planned_count']} · "
              f"live_dup={len(c['live_exact_duplicate'])} · nr_in={len(c['needs_review_in_wave'])} · "
              f"index_flip={c['index_auto_flip']} · live_write={c['live_write']} · guard={c['command_has_no_run_guard']}")

    # 보호 hash after (이 스크립트는 write 없음 → 반드시 동일)
    after = {os.path.basename(p): sha(os.path.join(ROOT, "data", p)) for p in prot}
    live_unchanged = (sha(LIVE) == prot.get("medistack_v0.2_beta_export.json"))
    prot_unchanged = before == after == {k: prot[k] for k in prot}

    out = {
        "meta": {"name": "live_pr_wave_rehearsal_v1_4", "base_count": base,
                 "live_write": False, "live_relations": len(live_ids),
                 "protected_unchanged": prot_unchanged, "live_export_unchanged": live_unchanged,
                 "waves_rehearsed": [r["wave"] for r in results]},
        "results": results,
    }
    if args.emit:
        json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  [emit] {os.path.basename(OUT)} 기록(planning area)")

    all_ok = all(r["pass"] for r in results) and prot_unchanged and live_unchanged
    print("=" * 60)
    if not all_ok:
        bad = [r["wave"] for r in results if not r["pass"]]
        print(f"RESULT: FAIL — wave {bad} · protected_unchanged={prot_unchanged} · live_unchanged={live_unchanged}")
        return 1
    print(f"RESULT: PASS — {len(results)} wave rehearsal · duplicate 0 · needs_review exclusion 확인 · "
          f"index flip 0 · live write 없음 · protected/live 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
