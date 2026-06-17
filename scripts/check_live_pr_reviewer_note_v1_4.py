#!/usr/bin/env python3
"""
check_live_pr_reviewer_note_v1_4.py
MediStack v1.4 — per-family **live PR** reviewer-note **상위 checker** (읽기전용·네트워크 0·live 무수정).

per-family integrator(integrate_*_batch_v1_4)들이 각자 게이트를 갖지만, live PR 은 family 를 묶는
wave(antibiotic23 / chronic8 / all33 등) 단위로도 나갈 수 있다. 이 checker 는 wave 단위 reviewer note
실물을 받아 통합 직전 한 번 더 검증한다. **아무것도 쓰지 않는다.**

wave→candidate_ids/delta 는 data/review/per_family_live_pr_readiness_v1_4.json 에서 읽는다(단일 진실원).

지원 wave: f1_nutrient10 f1_antacid8 f1_all18 f2_all5 f3_single f9_all7 f4_f6_small2 antibiotic23 chronic8 all33

사용:
  python3 scripts/check_live_pr_reviewer_note_v1_4.py --wave antibiotic23 --reviewer-note note.txt
  python3 scripts/check_live_pr_reviewer_note_v1_4.py --help

PASS=종료코드 0, FAIL=1. note 없거나 placeholder/SAMPLE/needs_review 포함/delta 불일치 등은 FAIL.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
READINESS = os.path.join(ROOT, "data", "review", "per_family_live_pr_readiness_v1_4.json")
BASELINE = 60

# note 본문에 등장하면 즉시 거부(검토자가 금지 행동을 요구/허용)
FORBIDDEN = [
    ("SAMPLE", "SAMPLE 토큰"),
    ("PLACEHOLDER", "placeholder 토큰"),
    ("YYYY-MM-DD", "placeholder 날짜"),
    ("XXXX", "placeholder candidate"),
    ("clinical_reviewed=true", "clinical_reviewed=true 요구"),
    ("clinical_reviewed 승격", "clinical 승격 요구"),
    ("published=true", "published=true 요구"),
    ("제품 추천 허용", "제품 추천 허용"),
    ("제품추천 허용", "제품 추천 허용"),
    ("구매 권유", "구매 권유"),
    ("구매권유", "구매 권유"),
    ("제휴 허용", "제휴 허용"),
    ("최저가", "최저가/광고성"),
    ("복용해도 된다", "복용 권유 단정"),
    ("안전하다", "안전 단정"),
    ("문제없다", "안전 단정"),
    ("처방", "처방 지시"),
    ("치료 지시", "치료 지시"),
    ("진단", "진단 지시"),
    ("면허번호", "reviewer 면허번호 강제 입력 요구"),
    ("schedule 활성", "schedule 활성화 허용"),
    ("reviewed_by 입력", "reviewed_by 입력 요구"),
    ("reviewed_by 기입", "reviewed_by 입력 요구"),
    ("용량", "용량/복용 지시"),
]

# 반드시 존재해야 하는 항목: (검사함수, 누락 시 메시지)
def _has(t, *subs):
    return all(s in t for s in subs)


def check_reviewer_note(note_path, expected_ids, delta, wave_label, needs_review_ids):
    """반환: (ok: bool, problems: [str])"""
    problems = []
    if not note_path or not os.path.exists(note_path):
        return False, ["reviewer note 파일 없음(비공란 실물 필요)"]
    t = open(note_path, encoding="utf-8").read()
    if not t.strip():
        return False, ["reviewer note 비공란 필요"]

    # 1) 금지 토큰
    for tok, msg in FORBIDDEN:
        if tok in t:
            problems.append(f"금지: {msg}")

    # 2) reviewer 식별자 (라벨 + 식별 토큰, 실명/면허 강제 아님; RF-* candidate id 와 구분)
    if "검수자" not in t and "reviewer" not in t.lower():
        problems.append("reviewer 식별자 라벨 없음")
    if not re.search(r"\b(?:RPH|PHARM|MD|REV|RN|DR|PM)[-A-Z0-9]*\d", t):
        problems.append("reviewer 식별 토큰 없음(예: RPH-001)")

    # 3) 검토일 (실제 날짜)
    if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", t):
        problems.append("검토일(YYYY-MM-DD 실날짜) 없음")

    # 4) 패키지/버전/commit/scope
    if "v1.4" not in t and "v1_4" not in t:
        problems.append("패키지 version(v1.4) 없음")
    if "commit" not in t.lower() or not re.search(r"\b[0-9a-f]{7,40}\b", t):
        problems.append("commit 해시 없음")
    if wave_label not in t:
        problems.append(f"scope(wave={wave_label}) 명시 없음")

    # 5) candidate id 전건
    missing = [i for i in expected_ids if i not in t]
    if missing:
        problems.append(f"candidate_id 미명시: {missing[:4]}{'…' if len(missing) > 4 else ''}")

    # 6) needs_review id 는 '제외' 맥락(같은 줄에 '제외')에서만 허용 — 그 외 줄에 등장하면 승인 시도로 간주
    nr_in = []
    for line in t.splitlines():
        for i in needs_review_ids:
            if i in line and i not in expected_ids and "제외" not in line:
                nr_in.append(i)
    if nr_in:
        problems.append(f"needs_review candidate 포함(승인 맥락): {sorted(set(nr_in))}")
    if "needs_review" not in t or "제외" not in t:
        problems.append("needs_review 제외 확인 문구 없음")

    # 7) relation count delta 일치 (+delta · 60 → 60+delta)
    md = re.search(r"delta[^\n]*?\+?\s*(\d+)", t)
    if not md or int(md.group(1)) != delta:
        problems.append(f"relation delta 불일치(기대 +{delta})")
    me = re.search(r"60\s*[→\-]+>?\s*(\d+)", t)
    if not me or int(me.group(1)) != BASELINE + delta:
        problems.append(f"expected count 불일치(기대 {BASELINE + delta})")

    # 8) grouping / source fidelity / copy conservatism 승인
    if "grouping" not in t.lower() or "승인" not in t:
        problems.append("grouping 승인 없음")
    if "출처" not in t or ("일치" not in t and "보존" not in t):
        problems.append("source fidelity(출처 일치/보존) 승인 없음")
    if "관리 문구" not in t or "보수" not in t:
        problems.append("management copy 보수성 확인 없음")

    # 9) 보호 상태 유지 승인
    if "published=false" not in t:
        problems.append("published=false 유지 승인 없음")
    if "clinical_reviewed=false" not in t:
        problems.append("clinical_reviewed=false 유지 승인 없음")
    if "reviewed_by 공란" not in t:
        problems.append("reviewed_by 공란 유지 승인 없음")
    if not _has(t, "제품", "없음") and not _has(t, "제휴", "없음"):
        problems.append("제품/구매/제휴 UI 없음 확인 없음")
    if "schedule" not in t.lower() or ("비활성" not in t and "inactive" not in t.lower()):
        problems.append("schedule 비활성 확인 없음")
    if "rollback" not in t.lower() or "가능" not in t:
        problems.append("rollback 가능성 확인 없음")

    return len(problems) == 0, problems


def build_valid_note(wave_label, expected_ids, delta, needs_review_ids):
    """게이트를 통과하는 모범 reviewer note(테스트/템플릿 기준)."""
    ids_line = ", ".join(expected_ids)
    nr_line = ", ".join(needs_review_ids)
    return (
        f"검수자: RPH-LIVEPR-001 (PM 승인 근거 첨부)   검토일 2026-07-01\n"
        f"검토 패키지: per_family_live_pr_readiness v1.4 / commit 56f6ddf\n"
        f"scope(wave={wave_label}) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.\n"
        f"승인 candidate_id 전건: {ids_line}.\n"
        f"relation delta: +{delta} (60 → {BASELINE + delta}, 신규 id = runtime max+1).\n"
        f"grouping 승인: 본 wave 단위 한 번에 통합.\n"
        f"출처(source) fidelity: 식약처 허가사항 인용과 일치 보존 확인.\n"
        f"관리 문구(management copy): 참고·상담 톤 보수성 유지 확인(분리복용/정기확인 문의, 지시 아님).\n"
        f"published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.\n"
        f"제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.\n"
        f"needs_review {nr_line} 는 본 승인에서 제외 확인.\n"
        f"rollback 가능(wave 단위 git revert) 확인.\n"
    )


def load_wave(wave_label):
    R = json.load(open(READINESS, encoding="utf-8"))
    waves = R["waves"]
    if wave_label not in waves:
        raise SystemExit(f"unknown wave: {wave_label} (지원: {', '.join(waves)})")
    nr = R["needs_review_quarantine"]["ids"]
    w = waves[wave_label]
    return w["candidate_ids"], w["delta"], nr


def main():
    ap = argparse.ArgumentParser(description="live PR wave reviewer-note checker (no write)")
    ap.add_argument("--wave", required=True,
                    help="f1_nutrient10 f1_antacid8 f1_all18 f2_all5 f3_single f9_all7 f4_f6_small2 antibiotic23 chronic8 all33")
    ap.add_argument("--reviewer-note", help="reviewer note 파일 경로")
    args = ap.parse_args()
    ids, delta, nr = load_wave(args.wave)
    ok, problems = check_reviewer_note(args.reviewer_note, ids, delta, args.wave, nr)
    if ok:
        print(f"PASS — wave={args.wave} reviewer note 유효 (candidate {len(ids)} · delta +{delta} · 60→{BASELINE + delta} · needs_review 제외)")
        return 0
    print(f"FAIL — wave={args.wave} reviewer note 거부 ({len(problems)}건):")
    for p in problems:
        print("  -", p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
