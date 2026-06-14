#!/usr/bin/env python3
"""
validate_search_empty_state_copy_v1_2.py
MediStack 검색 empty-state 안전문구 **카피 검증**(읽기전용).

검사:
  - canonical fixtures(scripts/fixtures/empty_state_copy_v1_2.json)의 PM 4문장 + 재시도 한 줄이
    설계 문서(docs/MediStack_search_empty_state_copy_v1_2.md)에 verbatim 존재.
  - 모든 카피가 forbidden phrase 게이트 통과(validate_forbidden_phrases_v1_2.scan 재사용).
  - 안전 속성: ②문장이 안전/위험 양방향 비단정("안전하거나 위험하지 않다는 의미는 아닙니다"),
    ③문장이 상담 종결("상담하세요"), ④문장이 제품/추천/복용지시 부정.
  - live_integration_forbidden=true · published/clinical_reviewed=false.
사용: python3 scripts/validate_search_empty_state_copy_v1_2.py
종료코드: 0 PASS, 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FIX = os.path.join(HERE, "fixtures", "empty_state_copy_v1_2.json")
DOC = os.path.join(REPO, "docs", "MediStack_search_empty_state_copy_v1_2.md")

# forbidden scanner 재사용(단일 게이트 로직 공유).
_spec = importlib.util.spec_from_file_location(
    "fp", os.path.join(HERE, "validate_forbidden_phrases_v1_2.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)


def _norm(t):
    """markdown bold(**)·개행·중복 공백 제거 후 비교(문서 포맷 무관 verbatim 검사)."""
    return " ".join(t.replace("**", "").split())


def main():
    fails = []
    fix = json.load(open(FIX, encoding="utf-8"))
    doc = open(DOC, encoding="utf-8").read() if os.path.exists(DOC) else ""
    if not doc:
        fails.append(f"설계 문서 없음: {DOC}")
    ndoc = _norm(doc)

    s = fix["pm_disclaimer_sentences"]
    copies = list(s) + [fix["no_result_retry_line"]]
    # ① verbatim 존재(포맷 정규화 후)
    for c in copies:
        if doc and _norm(c) not in ndoc:
            fails.append(f"문서에 verbatim 누락: '{c[:40]}...'")
    # ② 금지어 스캔: 긍정 카피(문장1-3 + 재시도)는 raw 게이트 통과 必.
    #    문장4 는 "제품 추천/복용 지시를 제공하지 않습니다" 부정 고지(승인됨) — raw 부분문자열 게이트 면제,
    #    대신 부정 종결('제공하지 않습니다')을 명시 검사한다(false negation 방지).
    affirmative = list(s[:3]) + [fix["no_result_retry_line"]]
    for c in affirmative:
        hits = fp.scan(c)
        if hits:
            fails.append(f"금지어 '{hits}' in 긍정 카피 '{c[:40]}...'")
    disclaimer = s[3] if len(s) >= 4 else ""
    if "제공하지 않습니다" not in disclaimer:
        fails.append("문장4가 부정 고지('제공하지 않습니다') 형태가 아님 — 추천/지시 부정 불명확")
    # 부정 고지라도 구매/제휴 등 동선 어휘가 섞이면 안 됨(부정 외 위반 검사)
    for bad in ("구매", "구입", "제휴", "할인", "최저가", "클릭", "바로가기"):
        if bad in disclaimer:
            fails.append(f"문장4에 동선 어휘 '{bad}'")

    if len(s) != 4:
        fails.append(f"PM 문장 수 {len(s)}≠4")
    else:
        if "안전하거나 위험하지 않다는 의미는 아닙니다" not in s[1]:
            fails.append("②문장 양방향 비단정 누락")
        if "상담하세요" not in s[2]:
            fails.append("③문장 상담 종결 누락")
        if "제품 추천이나 복용 지시를 제공하지 않습니다" not in s[3]:
            fails.append("④문장 제품/복용지시 부정 누락")
    for fld, exp in (("live_integration_forbidden", True), ("published", False), ("clinical_reviewed", False)):
        if fix.get(fld) != exp:
            fails.append(f"{fld}={fix.get(fld)} (기대 {exp})")

    print(f"=== empty-state copy validator: {len(copies)}개 카피 ===")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — PM 4문장+재시도 verbatim·금지어 0·양방향 비단정·상담 종결·제품/복용지시 부정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
