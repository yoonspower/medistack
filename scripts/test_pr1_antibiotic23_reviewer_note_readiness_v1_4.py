#!/usr/bin/env python3
"""
test_pr1_antibiotic23_reviewer_note_readiness_v1_4.py
MediStack v1.4 — PR-1 antibiotic23 live PR reviewer-note **readiness** 회귀 테스트 (읽기전용·네트워크 0·live 무수정).

검증:
  1) DRAFT 양식(미채움·placeholder)은 checker 가 **거부** — 채우기 전 통합 불가 보장.
  2) VALID fixture(형식 유효 예시)는 checker **통과**.
  3) invalid 변형(candidate 누락 / needs_review 혼입 / delta 불일치 / 금지요구)은 **거부**.
  4) PR-1 rehearsal(antibiotic23, base 60 → 83) PASS · duplicate 0 · needs_review 0 · live write 0.
  5) actual reviewer note 미확보 → 통합 차단 전제 유지.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DRAFT = os.path.join(REV, "pr1_antibiotic23_reviewer_note_DRAFT_v1_4.md")
VALID = os.path.join(REV, "pr1_antibiotic23_reviewer_note_VALID_fixture_v1_4.txt")
fails = []


def _load(f):
    spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(HERE, f))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _write(tmp, text):
    p = os.path.join(tmp, "n.txt")
    open(p, "w", encoding="utf-8").write(text)
    return p


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def main():
    import tempfile
    chk = _load("check_live_pr_reviewer_note_v1_4.py")
    ids, delta, nr = chk.load_wave("antibiotic23")
    tmp = tempfile.mkdtemp(prefix="ms_pr1_")
    print("=== PR-1 antibiotic23 reviewer-note readiness (live 무수정) ===")
    ck(len(ids) == 23 and delta == 23, "scope: candidate 23 · delta +23")

    # 1) DRAFT 차단
    ok_d, probs_d = chk.check_reviewer_note(DRAFT, ids, delta, "antibiotic23", nr)
    ck(not ok_d, f"DRAFT(미채움) checker 거부 ({len(probs_d)}건)")

    # 2) VALID fixture 통과
    ok_v, probs_v = chk.check_reviewer_note(VALID, ids, delta, "antibiotic23", nr)
    ck(ok_v, f"VALID fixture checker 통과 (probs={probs_v})")

    # 3) invalid 변형
    V = open(VALID, encoding="utf-8").read()
    def rej(label, text, must=None):
        ok, probs = chk.check_reviewer_note(_write(tmp, text), ids, delta, "antibiotic23", nr)
        good = (not ok) and (must is None or any(must in p for p in probs))
        ck(good, label)
    rej("candidate 1건 누락 거부", V.replace(ids[0], "RF-F1-9999"), "candidate_id 미명시")
    rej("needs_review 혼입(승인 맥락) 거부", V + f"\n추가 승인: {nr[0]}.", "needs_review candidate 포함")
    rej("delta 불일치(+22) 거부", V.replace("delta: +23", "delta: +22").replace("60 → 83", "60 → 82"), "delta 불일치")
    rej("expected count 위조 거부", V.replace("60 → 83", "60 → 999"), "expected count 불일치")
    rej("clinical=true 승격 요구 거부", V + "\nclinical_reviewed=true 로 승격 승인.", "clinical_reviewed=true 요구")
    rej("제품 추천 허용 거부", V + "\n관련 제품 추천 허용.", "제품 추천 허용")
    rej("구매 권유 거부", V + "\n영양제 구매 권유 추가.", "구매 권유")

    # 4) PR-1 rehearsal
    reh = _load("rehearse_live_pr_waves_no_write_v1_4.py")
    R = json.load(open(reh.READINESS, encoding="utf-8"))
    cmd = json.load(open(reh.CMD_PLAN, encoding="utf-8"))
    live = json.load(open(reh.LIVE, encoding="utf-8"))
    live_ids = sorted(r["id"] for r in live["relations"])
    res = reh.rehearse_wave(R, cmd, live_ids, 60, "antibiotic23")
    c = res["checks"]
    ck(res["pass"], "PR-1 rehearsal PASS")
    ck(c["planned_count"] == 83, "rehearsal expected 83")
    ck(c["candidate_count"] == 23 and c["delta"] == 23, "rehearsal n=23 +23")
    ck(not c["live_exact_duplicate"] and not c["needs_review_in_wave"], "rehearsal live dup 0 · needs_review 0")
    ck(c["live_write"] is False, "rehearsal live write 0")

    # 5) actual note 미확보
    summary = json.load(open(os.path.join(REV, "pr1_antibiotic23_readiness_v1_4.json"), encoding="utf-8"))
    ck(summary["reviewer_note"]["actual_reviewer_note_obtained"] is False, "actual reviewer note 미확보(통합 차단 전제)")
    ck(len(live["relations"]) == 60, "live relations 60 유지")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — DRAFT 차단 + VALID 통과 + invalid/forbidden 거부 + rehearsal 60→83 · live 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
