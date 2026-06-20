#!/usr/bin/env python3
"""
check_pr5_potassium_depletion_pm_note_v1_4.py
MediStack v1.4 — PR-5 **칼륨 depletion** PM-reviewed verified-reference note **checker** (읽기전용·네트워크 0·live 무수정).

PR-5 = 스테로이드·이뇨제 × 칼륨 depletion 6건. relation_count 95 → 101.
(mechanism=depletion · recommended_action=monitoring · counterpart_category=null · 영양소 직접.)
🔑 6건 전부 칼륨 → potassium_safety_card=true · product_link_allowed=false (production 최초 칼륨 safety).

이 note 는 **임상 검수(clinical review)가 아니다.** PM-reviewed verified-reference integration note 이며
published=false / clinical_reviewed=false / reviewed_by 공란 을 유지한다. checker 는 노트가
(1) PM 토큰 전건 (2) candidate 6 (3) 🔑칼륨 safety 승인(kcard·plink·보충단정 아님) (4) 보호 상태 유지
(5) 금지 행위 미요구 (6) source-fidelity + 제외(미유통/Mg/프레드니솔론/기존 live 칼륨 dedup) 임을 확인한다.

wave→candidate_ids/delta 는 data/review/pr5_potassium_depletion_candidate_lock_v1_4.json 에서 읽는다(단일 진실원).
사용: python3 scripts/check_pr5_potassium_depletion_pm_note_v1_4.py --note data/review/pr5_potassium_depletion_pm_reviewed_note_v1_4.md
PASS=종료코드 0, FAIL=1.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCK = os.path.join(ROOT, "data", "review", "pr5_potassium_depletion_candidate_lock_v1_4.json")

PM_TOKENS = [
    "PM_REVIEWED_VERIFIED_REFERENCE_ONLY",
    "NO_CLINICAL_REVIEW_CLAIM",
    "NO_PRODUCT_UI",
    "NO_SCHEDULE",
    "PR5_POTASSIUM_DEPLETION_95_TO_101",
]
FORBIDDEN = [
    ("SAMPLE", "SAMPLE 토큰(템플릿 그대로 승격 거부)"),
    ("PLACEHOLDER", "placeholder 토큰"),
    ("YYYY-MM-DD", "placeholder 날짜"),
    ("XXXX", "placeholder candidate"),
    ("최저가", "최저가/광고성"),
    ("구매 권유", "구매 권유"), ("구매권유", "구매 권유"),
    ("제휴 허용", "제휴 허용"),
    ("제품 추천 허용", "제품 추천 허용"), ("제품추천 허용", "제품 추천 허용"),
    ("보충 권유 허용", "보충 권유 허용"), ("보충제 추천 허용", "보충제 추천 허용"),
    ("schedule 활성", "schedule 활성화 허용"),
    ("reviewed_by 입력", "reviewed_by 입력 요구"), ("reviewed_by 기입", "reviewed_by 입력 요구"),
    ("면허번호", "reviewer 면허번호 강제 입력 요구"),
]
EVIDENCE_UPGRADE_RE = re.compile(
    r"high[ \t]*(으?로)?[ \t]*(상향|승격|올림)(?![ \t]*(금지|안|불가|없|아님))")
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음|금지|유지))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인|식약처[ \t]*문제없음|전문가[ \t]*검수[ \t]*완료)"
    r"(?![ \t]*(아님|아닙|없음|금지))")
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|보충제?[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크|구매[ \t]*버튼)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")
SUPPLEMENT_PERMISSION_RE = re.compile(
    r"(칼륨|마그네슘|영양제|보충제)[ \t]*(보충|복용|섭취)[ \t]*(권장|권유|하세요|하십시오|드세요|허용|승인)"
    r"(?![ \t]*(안|불가|금지|없|아님|아닙))")
USER_FACING_CLAIM_RE = re.compile(
    r"(안전하다|문제없다|문제 없다|복용해도 된다|복용해도된다)(?![ \t]*(고 단정 금지|는 표현 금지|아님|없음|금지))"
    r"|(처방|진단|치료 지시|치료지시)(?![ \t]*(아님|아닙|없음|금지|하지))")
TEST_TREAT_PERMISSION_RE = re.compile(
    r"(검사|처방|투여)[ \t]*(지시|받으세요|하세요|권고)[ \t]*(허용|추가|노출|승인)")


def check_pm_note(note_path, lock):
    problems = []
    if not note_path or not os.path.exists(note_path):
        return False, ["PM note 파일 없음(비공란 실물 필요)"]
    t = open(note_path, encoding="utf-8").read()
    if not t.strip():
        return False, ["PM note 비공란 필요"]
    low = t.lower()

    expected_ids = lock["candidate_ids"]
    drugs = lock["drugs"]
    delta = lock["relation_delta"]
    base = lock["baseline_relation_count"]
    after = lock["expected_relation_count_after"]
    seqs = [c["itemSeq"] for c in lock["candidates"]]
    live_k_ids = lock["existing_live_potassium_ids"]

    # 0) lock 무결성
    for c in lock["candidates"]:
        if not c.get("has_source"):
            problems.append(f"candidate {c['candidate_id']} source 없음 — 승격 차단")
        if c.get("counterpart") == "칼륨" and not (c.get("potassium_safety_card") is True
                                                 and c.get("product_link_allowed") is False):
            problems.append(f"🔑 lock {c['candidate_id']} 칼륨 invariant 위반(kcard/plink)")
    if lock["total"] != 6:
        problems.append(f"PR-5 는 6건 — lock total {lock['total']} != 6")

    # 1) PM 토큰
    for tok in PM_TOKENS:
        if tok not in t:
            problems.append(f"PM 토큰 누락: {tok}")
    # 2) 금지
    for tok, msg in FORBIDDEN:
        if tok in t:
            problems.append(f"금지: {msg}")
    if CLINICAL_PROMO_RE.search(t):
        problems.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지")
    if PRODUCT_PERMISSION_RE.search(t):
        problems.append("제품/구매/제휴/보충 추천 허용 문구 — 금지")
    if SUPPLEMENT_PERMISSION_RE.search(t):
        problems.append("칼륨/마그네슘/영양제 보충·복용·섭취 권유/허용 문구 — 금지")
    if USER_FACING_CLAIM_RE.search(t):
        problems.append("안전/문제없음/복용권유/처방·진단·치료 단정 — 금지")
    if TEST_TREAT_PERMISSION_RE.search(t):
        problems.append("검사/처방/투여 지시 카피 허용 문구 — 금지")
    if EVIDENCE_UPGRADE_RE.search(t):
        problems.append("evidence_level high 임의 상향 요구 — 금지(moderate 유지)")

    # 3) PM/reviewer 식별자 + 검토일
    if "PM" not in t and "검토자" not in t and "reviewer" not in low:
        problems.append("PM/검토자 식별자 라벨 없음")
    if not re.search(r"\b(?:PM|RPH|PHARM|MD|REV|PMREV)[-A-Z0-9]*\d", t):
        problems.append("PM/검토 식별 토큰 없음(예: PM-001)")
    if not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", t):
        problems.append("검토일(YYYY-MM-DD 실날짜) 없음")
    # 4) version/commit/branch/wave
    if "v1.4" not in t and "v1_4" not in t:
        problems.append("패키지 version(v1.4) 없음")
    if "commit" not in low or not re.search(r"\b[0-9a-f]{7,40}\b", t):
        problems.append("base commit 해시 없음")
    if "potassium_depletion" not in low:
        problems.append("wave(PR-5 potassium_depletion) 명시 없음")
    if "live/pr5-potassium-depletion" not in t and "target" not in low and "branch" not in low:
        problems.append("target branch 명시 없음")

    # 5) candidate id 전건 + 약물명 전건
    miss_id = [i for i in expected_ids if i not in t]
    if miss_id:
        problems.append(f"candidate_id 미명시: {miss_id}")
    miss_dr = [d for d in drugs if d not in t]
    if miss_dr:
        problems.append(f"약물명 미명시: {miss_dr}")

    # 6) scope (depletion 6)
    if not re.search(r"depletion[^\n]*?6|6[^\n]*?depletion|6\s*건", t):
        problems.append("scope: depletion 6 명시 없음")
    if "monitoring" not in t and "monitor" not in low:
        problems.append("recommended_action=monitoring 명시 없음")

    # 7) 🔑 칼륨 safety
    if "potassium_safety_card=true" not in t:
        problems.append("🔑 potassium_safety_card=true 승인 없음")
    if "product_link_allowed=false" not in t:
        problems.append("🔑 product_link_allowed=false 승인 없음")
    if not re.search(r"보충[ \t]*(지시|권유|단정)[^\n]*(아니|아님|않|0|없)", t):
        problems.append("보충 지시/권유 아님(결핍 주의 참고) 명시 없음")
    if "고칼륨혈증" not in t or ("아님" not in t and "depletion" not in low):
        problems.append("방향성(저칼륨혈증 depletion·고칼륨혈증 아님) 명시 없음")

    # 8) source fidelity + itemSeq 전건
    if "출처" not in t or ("일치" not in t and "보존" not in t):
        problems.append("source fidelity(출처 일치/보존) 확인 없음")
    miss_seq = [s for s in seqs if s not in t]
    if miss_seq:
        problems.append(f"itemSeq 미명시: {miss_seq}")
    if not re.search(r"(이상반응|부작용|일반적\s*주의)", t):
        problems.append("in-scope 섹션(이상반응/부작용/일반적 주의) 명시 없음")

    # 9) delta / before→after
    md = re.search(r"delta[^\n]*?\+?\s*(\d+)", t)
    if not md or int(md.group(1)) != delta:
        problems.append(f"relation delta 불일치(기대 +{delta})")
    me = re.search(rf"{base}\s*[→\-]+>?\s*(\d+)", t)
    if not me or int(me.group(1)) != after:
        problems.append(f"expected count 불일치(기대 {base}→{after})")

    # 10) 제외 / dedup
    if "미유통" not in t and "not_reachable" not in low:
        problems.append("미유통 reject 인지 없음")
    if "마그네슘" not in t or "제외" not in t:
        problems.append("마그네슘 reject(아조세미드×Mg) 제외 인지 없음")
    if "프레드니솔론" not in t:
        problems.append("프레드니솔론 reject(순수 경구 부재) 인지 없음")
    for i in live_k_ids:
        if str(i) not in t:
            problems.append(f"기존 live 칼륨 id {i} dedup 인지 없음")
    if "재추가" not in t and "재통합" not in t and "중복" not in t:
        problems.append("기존 live 칼륨 재추가 금지/중복 0 확인 없음")

    # 11) grouping / management 보수
    if "grouping" not in low or "승인" not in t:
        problems.append("grouping 승인 없음")
    if "관리 문구" not in t or "보수" not in t:
        problems.append("management copy 보수성 확인 없음")

    # 12) evidence_level moderate 유지
    if "moderate" not in t or "유지" not in t:
        problems.append("evidence_level=moderate 유지 명시 없음")

    # 13) 보호 상태
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
    ap = argparse.ArgumentParser(description="PR-5 칼륨 depletion PM note checker (no write)")
    ap.add_argument("--note")
    ap.add_argument("--lock", default=LOCK)
    args = ap.parse_args()
    lock = json.load(open(args.lock, encoding="utf-8"))
    ok, problems = check_pm_note(args.note, lock)
    if ok:
        print(f"PASS — PR-5 칼륨 depletion PM note 유효 "
              f"(candidate {lock['total']} · delta +{lock['relation_delta']} · "
              f"{lock['baseline_relation_count']}→{lock['expected_relation_count_after']} · "
              f"🔑칼륨 safety·미유통/Mg/프레드니솔론 제외·기존 live K dedup · PM 토큰 {len(PM_TOKENS)})")
        return 0
    print(f"FAIL — PR-5 칼륨 depletion PM note 거부 ({len(problems)}건):")
    for p in problems:
        print("  -", p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
