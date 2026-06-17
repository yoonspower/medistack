#!/usr/bin/env python3
"""
smoke_autofactory_orchestrator_v1_5.py
MediStack v1.5 — AutoFactory Orchestrator 스모크 (작은 seeded 실행으로 funnel/no-live-write 즉시 확인).

  1) --seed 동일 → raw 후보 집합 결정적(재현성).
  2) family 한정(--families F1) → 해당 family 만 harvest.
  3) 어떤 실행도 신규 reviewer-ready 0 · live write 0 · protected 불변 (가드 작동).
  4) 보호셋 sha256 실행 전후 불변(직접 측정).
종료코드 0 PASS / 1 FAIL.
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load_orch():
    spec = importlib.util.spec_from_file_location(
        "orch", os.path.join(HERE, "run_medistack_autofactory_orchestrator_v1_5.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    import random
    print("=== AutoFactory Orchestrator v1.5 smoke ===")
    o = load_orch()
    universe = o.J(o.UNIVERSE)
    pre, live, plan, readiness, quar, live_pairs = o.stage0_preflight(True)

    # 보호셋 before
    before = {f: sha(os.path.join(DATA, f)) for f in o.PROTECTED}

    # 1) 결정성: 같은 seed → 같은 raw_id 순서
    r1, _ = o.stage1_harvest(universe, set(), set(), live_pairs, random.Random(7), 50)
    r2, _ = o.stage1_harvest(universe, set(), set(), live_pairs, random.Random(7), 50)
    ck([c["raw_id"] for c in r1] == [c["raw_id"] for c in r2], "seed 동일 → raw 결정적")

    # 2) family 한정
    rf1, _ = o.stage1_harvest(universe, {"F1"}, set(), live_pairs, random.Random(1), 50)
    ck(rf1 and all(c["family"] == "F1" for c in rf1), "--families F1 한정 동작")

    # 3) funnel 가드: 신규 ready 0
    q, pf = o.stage2_source_check_queue(r1)
    reviewed, genuine, capped, overflow = o.stage3_4_auto_reviewer(plan, quar, 20, q)
    pkg = o.stage6_package(reviewed, readiness)
    ck(pkg["new_reviewer_ready_total"] == 0, "신규 reviewer-ready 0 (작은 실행에서도)")
    ck(all(c["source_pointer"] is None for c in r1), "raw source_pointer=null 유지")

    # 4) 보호셋 after
    after = {f: sha(os.path.join(DATA, f)) for f in o.PROTECTED}
    ck(before == after, "보호셋 sha256 실행 전후 불변(live 무수정)")

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — 결정성·family 한정·신규ready 0·보호셋 불변")
    return 0


if __name__ == "__main__":
    sys.exit(main())
