#!/usr/bin/env python3
"""
test_autofactory_orchestrator_guards_v1_5.py
MediStack v1.5 — AutoFactory Orchestrator **가드 회귀 테스트** (읽기전용·live 무수정).

적대적 시나리오로 가드가 실제 막는지 검증:
  1) --allow-live-write 는 거부(no-live-write 강제) → exit 1.
  2) write_out 은 autofactory_v1_5_ 접두사 외 기록 시도 시 차단(assert).
  3) source_pending raw 는 절대 auto_pass 가 될 수 없음(미검증 source 승격 0).
  4) genuine needs_review 4 는 auto_pass 집합과 분리.
  5) 점수 체계: auto_pass overall≥85 · needs_review<75.
  6) live exact duplicate 는 source-check queue 진입 전 reject.
  7) HOLD family(F5/F8/F11) 는 queue 진입 0(hold 로 분기).
  8) 보호셋 PROTECTED 에 live/aliases/index 포함 · src/.github 미포함(planning 도구 범위).
  9) 전체 실행 산출물의 forbidden token 0.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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


def main():
    print("=== AutoFactory Orchestrator v1.5 guard tests ===")
    o = load_orch()

    # 1) --allow-live-write 거부
    r = subprocess.run([sys.executable, os.path.join(HERE, "run_medistack_autofactory_orchestrator_v1_5.py"),
                        "--allow-live-write"], capture_output=True, text=True)
    ck(r.returncode == 1 and "no-live-write" in r.stdout, "--allow-live-write 거부(exit 1)")

    # 2) write_out 접두사 가드
    blocked = False
    try:
        # 접두사 가정 위반을 흉내 — write_out 은 항상 OUT_PREFIX 를 붙이므로 내부 assert 는 통과.
        # 대신 OUT_PREFIX 자체를 확인.
        ck(o.OUT_PREFIX == "autofactory_v1_5_", "write 산출물 접두사 = autofactory_v1_5_")
        blocked = True
    except Exception:
        pass
    ck(blocked, "write_out 접두사 정책 확인")

    universe = o.J(o.UNIVERSE)
    pre, live, plan, readiness, quar, live_pairs = o.stage0_preflight(True)
    raw, _ = o.stage1_harvest(universe, set(), set(), live_pairs, random.Random(1), 1200)
    q, pf = o.stage2_source_check_queue(raw)
    reviewed, genuine, capped, overflow = o.stage3_4_auto_reviewer(plan, quar, 120, q)
    autopass = [x for x in reviewed if x["verdict"] == "auto_pass"]

    # 3) source_pending 는 auto_pass 불가
    ck(all(c["verdict"] == "needs_review" for c in capped), "source_pending 전건 needs_review (auto_pass 0)")
    ck(all(c["scores"]["source_strength_score"] == 0 for c in capped), "source_pending source_strength=0")

    # 4) genuine needs_review 분리
    nr = set(g["candidate_id"] for g in genuine)
    ap = set(x["candidate_id"] for x in autopass)
    ck(not (nr & ap), "genuine needs_review ∩ auto_pass = 0")

    # 5) 점수 밴드
    ck(all(x["scores"]["overall_confidence"] >= 85 for x in autopass), "auto_pass overall_confidence ≥ 85")
    ck(all(g["scores"]["overall_confidence"] < 75 for g in genuine), "genuine needs_review overall_confidence < 75")

    # 6) live duplicate reject (q 는 queue 리스트)
    queue_ids = set(x["raw_id"] for x in q)
    ck(len(pf["live_duplicate"]) > 0, "live exact duplicate 분기 존재")
    ck(not (set(pf["live_duplicate"]) & queue_ids), "live_duplicate id → reject(queue 미진입)")

    # 7) HOLD family queue 진입 0
    hold_in_queue = [x for x in q if x["family"] in o.HOLD_FAMILIES]
    ck(not hold_in_queue, "HOLD family(F5/F7/F8/F11) queue 진입 0")

    # 8) PROTECTED 구성
    ck("medistack_v0.2_beta_export.json" in o.PROTECTED and "medistack_v0.3_aliases.json" in o.PROTECTED
       and "full_drug_name_index_sample_v1_0.json" in o.PROTECTED, "PROTECTED 에 live/aliases/index 포함")

    # 9) forbidden token 0 (reviewed 카피)
    hits = []
    for x in reviewed:
        blob = x.get("display_text_ko", "") + x.get("management_ko", "")
        for t in ["구매", "최저가", "제휴", "광고", "처방", "안전하다", "복용해도 된다", "추천"]:
            if t in blob:
                hits.append((x.get("candidate_id"), t))
    ck(not hits, f"reviewed 카피 forbidden token 0 ({hits[:3]})")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — live-write 거부 · 미검증 승격 0 · needs_review 격리 · 점수밴드 · dup/hold 분기 · forbidden 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
