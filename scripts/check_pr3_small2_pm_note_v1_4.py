#!/usr/bin/env python3
"""
check_pr3_small2_pm_note_v1_4.py
MediStack v1.4 — PR-3 **small2** PM-reviewed verified-reference note **checker** (읽기전용·네트워크 0·live 무수정).

PR-3 small2 = F3 이반드론산 × Al/Mg 함유 제산제 1 + F4 레보티록신 × 알루미늄 함유 제산제 1 = 2건.
relation_count 92 → 94. (둘 다 absorption/separation · counterpart_category=al_mg_antacid · drug counterpart.)

이 note 는 **임상 검수(clinical review)가 아니다.** PM-reviewed verified-reference integration note 이며
published=false / clinical_reviewed=false / reviewed_by 공란 을 유지한다. checker 는 노트가
(1) PM 토큰 전건 (2) candidate 2 전건 (3) 보호 상태 유지 승인 (4) 금지 행위 미요구
(5) source-fidelity copy 원칙(라벨귀속 '분리하도록 안내' 단정 제거 · 레보티록신 Al-only) 인지 임을 확인한다.

wave→candidate_ids/delta 는 data/review/pr3_small2_candidate_lock_v1_4.json 에서 읽는다(단일 진실원).

사용:
  python3 scripts/check_pr3_small2_pm_note_v1_4.py --note data/review/pr3_small2_pm_reviewed_note_v1_4.md
PASS=종료코드 0, FAIL=1.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCK = os.path.join(ROOT, "data", "review", "pr3_small2_candidate_lock_v1_4.json")

PM_TOKENS = [
    "PM_REVIEWED_VERIFIED_REFERENCE_ONLY",
    "NO_CLINICAL_REVIEW_CLAIM",
    "NO_PRODUCT_UI",
    "NO_SCHEDULE",
    "PR3_SMALL2_92_TO_94",
]

FORBIDDEN = [
    ("SAMPLE", "SAMPLE 토큰(템플릿 그대로 승격 거부)"),
    ("PLACEHOLDER", "placeholder 토큰"),
    ("YYYY-MM-DD", "placeholder 날짜"),
    ("XXXX", "placeholder candidate"),
    ("최저가", "최저가/광고성"),
    ("구매 권유", "구매 권유"),
    ("구매권유", "구매 권유"),
    ("제휴 허용", "제휴 허용"),
    ("제품 추천 허용", "제품 추천 허용"),
    ("제품추천 허용", "제품 추천 허용"),
    ("schedule 활성", "schedule 활성화 허용"),
    ("reviewed_by 입력", "reviewed_by 입력 요구"),
    ("reviewed_by 기입", "reviewed_by 입력 요구"),
    ("면허번호", "reviewer 면허번호 강제 입력 요구"),
]

CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음|금지|유지))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인|식약처[ \t]*문제없음|전문가[ \t]*검수[ \t]*완료)"
    r"(?![ \t]*(아님|아닙|없음|금지))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|보충제?[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|구매[ \t]*버튼)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
USER_FACING_CLAIM_RE = re.compile(
    r"(안전하다|문제없다|문제 없다|복용해도 된다|복용해도된다)(?![ \t]*(고 단정 금지|는 표현 금지|아님|없음|금지))"
    r"|(처방|진단|치료 지시|치료지시)(?![ \t]*(아님|아닙|없음|금지|하지))")
# 검사/처방/투여 지시 허용(모니터링 톤 위반)
TEST_TREAT_PERMISSION_RE = re.compile(
    r"(검사|처방|투여)[ \t]*(지시|받으세요|하세요|권고)[ \t]*(허용|추가|노출|승인)"
    r"|(검사|처방)[ \t]*지시[ \t]*(문구[ \t]*)?(허용|추가)")

# PR-3 in-scope = F3/F4. F1/F2/F6/F9/F10 candidate 가 승인 맥락(제외 라인 밖)에 등장하면 거부.
EXCLUDED_FAMILY_RE = re.compile(r"\bRF-(F1|F2|F6|F9|F10)-\S+")


def load_lock():
    return json.load(open(LOCK, encoding="utf-8"))


def check_pm_note(note_path, lock):
    problems = []
    if not note_path or not os.path.exists(note_path):
        return False, ["PM note 파일 없음(비공란 실물 필요)"]
    t = open(note_path, encoding="utf-8").read()
    if not t.strip():
        return False, ["PM note 비공란 필요"]
    low = t.lower()

    expected_ids = lock["candidate_ids"]
    delta = lock["relation_delta"]
    base = lock["baseline_relation_count"]
    after = lock["expected_relation_count_after"]
    nr_ids = lock["needs_review_exclusion"]

    # 0) lock 무결성
    for c in lock["candidates"]:
        if not c.get("has_source"):
            problems.append(f"candidate {c['candidate_id']} source 없음 — 승격 차단")
    fams = {c["family"] for c in lock["candidates"]}
    if "F3" not in fams:
        problems.append("lock 에 F3 후보 없음")
    if "F4" not in fams:
        problems.append("lock 에 F4 후보 없음")

    # 1) PM 토큰
    for tok in PM_TOKENS:
        if tok not in t:
            problems.append(f"PM 토큰 누락: {tok}")

    # 2) 금지 토큰/정규식
    for tok, msg in FORBIDDEN:
        if tok in t:
            problems.append(f"금지: {msg}")
    if CLINICAL_PROMO_RE.search(t):
        problems.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(t):
        problems.append("제품/구매/제휴/보충 추천 허용 문구 — 금지")
    if USER_FACING_CLAIM_RE.search(t):
        problems.append("안전/문제없음/복용권유/처방·진단·치료 단정 — 금지")
    if TEST_TREAT_PERMISSION_RE.search(t):
        problems.append("검사/처방/투여 지시 카피 허용 문구 — 금지")

    # 3) PM / reviewer 식별자 + 검토일
    if "PM" not in t and "검토자" not in t and "reviewer" not in low:
        problems.append("PM/검토자 식별자 라벨 없음")
    if not re.search(r"\b(?:PM|RPH|PHARM|MD|REV|PMREV)[-A-Z0-9]*\d", t):
        problems.append("PM/검토 식별 토큰 없음(예: PM-001)")
    if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", t):
        problems.append("검토일(YYYY-MM-DD 실날짜) 없음")

    # 4) version / commit / branch / wave
    if "v1.4" not in t and "v1_4" not in t:
        problems.append("패키지 version(v1.4) 없음")
    if "commit" not in low or not re.search(r"\b[0-9a-f]{7,40}\b", t):
        problems.append("base commit 해시 없음")
    if "small2" not in t:
        problems.append("wave(PR-3 small2) 명시 없음")
    if "live/pr3-small2" not in t and "target" not in low and "branch" not in low:
        problems.append("target branch 명시 없음")

    # 5) candidate id 2 전건
    missing = [i for i in expected_ids if i not in t]
    if missing:
        problems.append(f"candidate_id 미명시: {missing}")

    # 6) scope (F3 1 / F4 1)
    if not re.search(r"F3[^\n]*?1", t):
        problems.append("scope: F3 1 명시 없음")
    if not re.search(r"F4[^\n]*?1", t):
        problems.append("scope: F4 1 명시 없음")
    if "이반드론산" not in t:
        problems.append("scope: 이반드론산 명시 없음")
    if "레보티록신" not in t:
        problems.append("scope: 레보티록신 명시 없음")

    # 7) needs_review / 제외 family / PR-1·PR-2 재추가 금지 — '제외' 맥락에서만 허용
    nr_bad, fam_bad = [], []
    for line in t.splitlines():
        for i in nr_ids:
            if i in line and i not in expected_ids and "제외" not in line:
                nr_bad.append(i)
        for full in EXCLUDED_FAMILY_RE.finditer(line):
            fid = full.group(0)
            in_scope = any(fid.startswith(c) for c in expected_ids)
            if not in_scope and "제외" not in line and "PR-1" not in line and "PR-2" not in line \
               and "PR1" not in line and "PR2" not in line:
                fam_bad.append(fid)
    if nr_bad:
        problems.append(f"needs_review candidate 포함(승인 맥락): {sorted(set(nr_bad))}")
    if fam_bad:
        problems.append(f"F1/F2/F6/F9/F10 candidate 포함(승인 맥락): {sorted(set(fam_bad))}")
    if "needs_review" not in t or "제외" not in t:
        problems.append("needs_review 제외 확인 문구 없음")
    if "RF-F3-0148" not in t and "에티드론산" not in t:
        problems.append("RF-F3-0148/0149(에티드론산) needs_review 제외 인지 명시 없음")
    if ("PR-1" not in t and "PR-2" not in t) or ("재추가" not in t and "재통합" not in t and "중복" not in t):
        problems.append("PR-1/PR-2 후보 재추가 금지 확인 문구 없음")

    # 8) delta / before→after
    md = re.search(r"delta[^\n]*?\+?\s*(\d+)", t)
    if not md or int(md.group(1)) != delta:
        problems.append(f"relation delta 불일치(기대 +{delta})")
    me = re.search(rf"{base}\s*[→\-]+>?\s*(\d+)", t)
    if not me or int(me.group(1)) != after:
        problems.append(f"expected count 불일치(기대 {base}→{after})")

    # 9) source fidelity / copy_change / al_mg_antacid / 레보티록신 Al-only
    if "출처" not in t or ("일치" not in t and "보존" not in t):
        problems.append("source fidelity(출처 일치/보존) 확인 없음")
    if "copy_change" not in t and "copy change" not in low and "reframe" not in low:
        problems.append("copy_change 반영 여부 명시 없음")
    if "al_mg_antacid" not in t and "제산제" not in t:
        problems.append("counterpart category(al_mg_antacid/제산제) 명시 없음")
    if not re.search(r"(absorption|흡수)", t) or not re.search(r"(separation|분리|복용\s*시점|투여간격)", t):
        problems.append("mechanism/action(absorption/separation·복용 시점 분리) 명시 없음")
    # 라벨귀속 '분리하도록 안내' 단정 보수화 인지(이반드론산 FACT-only)
    if "분리" not in t or ("단정" not in t and "제거" not in t and "보수" not in t and "유도" not in t):
        problems.append("'분리-안내' 단정 보수화(source-fidelity) 인지 없음")
    # 레보티록신 Al-only(Mg 미명시) 인지
    if "알루미늄" not in t or ("Mg 미명시" not in t and "마그네슘 미명시" not in t
                             and "Al-only" not in t and "Al only" not in t and "Al 함유" not in t):
        problems.append("레보티록신 Al-only(Mg 미명시) 인지 없음")

    # 10) grouping / management 보수성
    if "grouping" not in low or "승인" not in t:
        problems.append("grouping 승인 없음")
    if "관리 문구" not in t or "보수" not in t:
        problems.append("management copy 보수성 확인 없음")

    # 11) 보호 상태
    if "published=false" not in t:
        problems.append("published=false 유지 승인 없음")
    if "clinical_reviewed=false" not in t:
        problems.append("clinical_reviewed=false 유지 승인 없음")
    if "reviewed_by 공란" not in t:
        problems.append("reviewed_by 공란 유지 승인 없음")
    if "제품" not in t or "없음" not in t:
        problems.append("제품/구매/제휴 UI 없음 확인 없음")
    if "schedule" not in low or ("비활성" not in t and "inactive" not in low):
        problems.append("schedule 비활성 확인 없음")
    if "rollback" not in low or "가능" not in t:
        problems.append("rollback 가능성 확인 없음")

    return len(problems) == 0, problems


def main():
    ap = argparse.ArgumentParser(description="PR-3 small2 PM-reviewed note checker (no write)")
    ap.add_argument("--note")
    ap.add_argument("--lock", default=LOCK)
    args = ap.parse_args()
    lock = json.load(open(args.lock, encoding="utf-8"))
    ok, problems = check_pm_note(args.note, lock)
    if ok:
        print(f"PASS — PR-3 small2 PM note 유효 "
              f"(candidate {lock['total']} · delta +{lock['relation_delta']} · "
              f"{lock['baseline_relation_count']}→{lock['expected_relation_count_after']} · "
              f"needs_review/F1·F2·F6·F9·F10 제외 · PM 토큰 {len(PM_TOKENS)})")
        return 0
    print(f"FAIL — PR-3 small2 PM note 거부 ({len(problems)}건):")
    for p in problems:
        print("  -", p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
