#!/usr/bin/env python3
"""
test_extract_gold_v1_7.py — Phase 2 GOLD TEST(추출기 self-check 게이트).

3건의 실제 nedrug 라벨 fixture 에서 흡수-방향성 상호작용 **완전 문장**을 정확히 재현하는지 검증.
재현 실패 = 추출기 결함 → STOP(고치고 재시도).

⚠️ GOLD #1(itemSeq 201207007 드로반정/이반드론산): 과제 예시 문자열은 '…'(말줄임)로 시작하는
   PM 근사치였고, 실제 라이브 라벨 원문은 아래 verbatim 문장이다. strict-source-fidelity 는 PM 근사가
   아니라 **라벨 원문 그대로**를 요구하므로, 라벨 verbatim 완전 문장(다가 양이온·알루미늄·'흡수를 저해할 수
   있다.' 종결)을 재현하는지 검증한다. GOLD #2·#3 은 라벨 원문과 과제 예시가 정확히 일치.

또한 v1.6 결함 회귀:
  - 문장 중간 잘림 0(모든 quote 가 종결부호로 끝남).
  - off-scope(이상반응/용법/임부) 섹션의 흡수 동거어는 추출 0.
  - 동사 '방해' 커버(비스포스포네이트 누락 방지).
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FX = os.path.join(ROOT, "tests", "fixtures", "nedrug")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# 라벨 원문 verbatim GOLD(실 fixture 기준 — strict-source-fidelity).
GOLD = {
    "201207007": "우유, 음식물, 칼슘, 다가 양이온(예, 알루미늄, 마그네슘, 철)들을 포함한 제품들은 이 약의 흡수를 저해할 수 있다.",
    "201903166": "칼슘보충제, 제산제 및 다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 경구투여 약물의 병용 투여는 이 약의 흡수를 방해한다.",
    "197400278": "콜레스티라민, 철분제제, 알루미늄 함유 제산제와 병용투여시 이 약의 흡수가 지연 또는 감소될 수 있으므로 투여간격에 주의하며 신중히 투여한다.",
}


def main():
    print("=== extract_label_interaction v1.7 — GOLD TEST ===")
    ex = load("ex", os.path.join(HERE, "extract_label_interaction_v1_7.py"))

    for seq, gold in GOLD.items():
        raw = open(os.path.join(FX, f"detail_{seq}.html"), encoding="utf-8").read()
        findings = ex.extract_interactions(raw)
        quotes = [f["source_quote"] for f in findings]
        # 1) GOLD 완전 문장 정확 재현
        ck(gold in quotes, f"GOLD {seq}: verbatim 완전 문장 재현")
        # 2) 해당 finding 의 방향/기전/scope 정합
        gf = next((f for f in findings if f["source_quote"] == gold), None)
        if gf:
            ck(gf["direction"] == "this_drug_lowered", f"GOLD {seq}: 방향=this_drug_lowered")
            ck(gf["mechanism"] == "absorption" and gf["action"] == "separation",
               f"GOLD {seq}: mechanism=absorption·action=separation")
            ck(ex.is_interaction_scope(gf["section"]), f"GOLD {seq}: scope=상호작용 섹션({gf['section']})")
        # 3) 모든 quote 가 완전 문장(중간 잘림 0)
        truncated = [q for q in quotes if not q.rstrip().endswith(".")]
        ck(not truncated, f"{seq}: 모든 quote 완전 문장(잘림 0)")

    # 4) off-scope 격리: 201903166 의 '음식물은 이 약의 흡수를 방해' (용법/주의 줄)은 추출 0.
    raw = open(os.path.join(FX, "detail_201903166.html"), encoding="utf-8").read()
    quotes = [f["source_quote"] for f in ex.extract_interactions(raw)]
    ck(not any("음식물은 이 약의 흡수를 방해하기 때문에" in q for q in quotes),
       "off-scope 격리: 용법 섹션 '음식물' 줄 미추출")
    # 모든 finding 이 상호작용 scope 섹션
    ck(all(ex.is_interaction_scope(f["section"]) for f in ex.extract_interactions(raw)),
       "모든 finding 이 상호작용 scope 섹션")

    # 5) 동사 '방해' 커버(비스포스포네이트 누락 방지)
    ck(ex.has_direction_verb("이 약의 흡수를 방해한다.") and
       ex.absorption_direction("이 약의 흡수를 방해한다.") == "this_drug_lowered",
       "동사 '방해' 커버 + this_drug_lowered")

    # 6) 문장 분할 단위 테스트
    s = "A는 이 약의 흡수를 저해할 수 있다. 따라서 1시간 동안 섭취하지 말아야 한다."
    sents = ex.split_sentences(s)
    ck(sents == ["A는 이 약의 흡수를 저해할 수 있다.", "따라서 1시간 동안 섭취하지 말아야 한다."],
       "split_sentences: '다.' 경계 분할(소수점 미분할 포함)")
    ck(ex.split_sentences("3) 칼슘보충제는 흡수를 방해한다.") == ["칼슘보충제는 흡수를 방해한다."],
       "split_sentences: enumerator 'N)' 선두 제거")

    # 7) counterpart 분류
    cat, terms = ex.classify_counterparts(GOLD["201903166"])
    ck(cat == "al_mg_antacid" and "제산제" in terms, "classify: 제산제→al_mg_antacid")

    # 8) 단일성분·경구 필터
    ck(ex.is_single_oral_product({"item_name": "건토넬정", "ingr_name": "리세드론산나트륨",
                                  "finished": "완제의약품", "status_cancel": "정상"}),
       "single_oral: 단일성분 정제 통과")
    ck(not ex.is_single_oral_product({"item_name": "마빌큐주", "ingr_name": "이반드론산나트륨",
                                      "finished": "완제의약품", "status_cancel": "정상"}),
       "single_oral: 주사제 제외")
    ck(not ex.is_single_oral_product({"item_name": "OO정", "ingr_name": "성분A, 성분B",
                                      "finished": "완제의약품", "status_cancel": "정상"}),
       "single_oral: 복합성분 제외")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — GOLD 3/3 verbatim 재현·off-scope 격리·완전문장·동사커버·분류·필터")
    return 0


if __name__ == "__main__":
    sys.exit(main())
