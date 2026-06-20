#!/usr/bin/env python3
"""
test_extract_depletion_gold_v1_8.py — PHASE 1 GOLD TEST(depletion 추출기 self-check 게이트).

3건의 실제 nedrug 라벨 fixture 에서 **칼륨 결핍 명시 완전 문장**을 정확히 재현하는지 검증.
재현 실패 = 추출기 결함 → STOP(고치고 재시도).

GOLD(3 mechanistic class·전부 in-scope·비임부·결핍 STATE/방향 명시):
  메틸프레드니솔론 199800324 (글루코코르티코이드) — 이상반응 체액·전해질: 칼륨손실/저칼륨성 알칼리혈증
  아조세미드       199001306 (루프 이뇨제)        — 부작용 대사: 저칼륨혈증
  아세타졸아미드   201403403 (탄산탈수효소억제제) — 일반적 주의: 저칼륨혈증 + 정기 전해질 검사

🔑 B2/off-scope 회귀 가드: 상호작용(약-약 '칼륨방출 증가')·임부(신생아 저마그네슘혈증)·고령자·과량 섹션의
   칼륨/마그네슘 동거어는 추출 0. 고칼륨혈증(↑·칼륨보존성)은 wrong_direction → 추출 0.
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


# 라벨 원문 verbatim GOLD(실 fixture·추출기 split 기준 — strict-source-fidelity).
GOLD = {
    "199800324": "체액ㆍ전해질 : 부종, 나트륨저류, 칼륨손실, 체액저류, 저칼륨성 알칼리혈증, "
                 "감수성 환자에 있어서 울혈성 심부전, 고혈압 등이 나타날 수 있다.",
    "199001306": "대사 : 때때로 저칼륨혈증, 저나트륨혈증, 저염소혈증성 알칼리증 등의 전해질평형실조, "
                 "고뇨산혈증, BUN·혈청크레아티닌의 상승, 드물게 고혈당이 나타날 수 있으므로 충분히 관찰하고 "
                 "이상이 인정되는 경우는 감량 또는 휴약 등 적절한 처치를 한다.",
    "201403403": "이 약의 투여에 의해 대사성산증 뿐 아니라 저나트륨혈증 및 저칼륨혈증을 포함한 전해질평형실조가 "
                 "나타날 수 있으므로 혈청 전해질에 대한 정기적인 검사가 권장된다.",
}


def main():
    print("=== extract_label_depletion v1.8 — GOLD TEST ===")
    dp = load("dp", os.path.join(HERE, "extract_label_depletion_v1_8.py"))

    for seq, gold in GOLD.items():
        raw = open(os.path.join(FX, f"detail_{seq}.html"), encoding="utf-8").read()
        findings = dp.extract_depletions(raw)
        quotes = [f["source_quote"] for f in findings]
        ck(gold in quotes, f"GOLD {seq}: verbatim 완전 문장 재현")
        gf = next((f for f in findings if f["source_quote"] == gold), None)
        if gf:
            ck(gf["nutrient"] == "칼륨", f"GOLD {seq}: nutrient=칼륨")
            ck(gf["mechanism"] == "depletion" and gf["action"] == "monitoring",
               f"GOLD {seq}: mechanism=depletion·action=monitoring")
            ck(gf["direction"] == "drug_depletes_nutrient", f"GOLD {seq}: 방향=drug_depletes_nutrient")
            ck(dp.is_depletion_scope(gf["section"]), f"GOLD {seq}: in-scope({gf['section']})")
        # 모든 quote 완전 문장(중간 잘림 0)
        ck(all(q.rstrip().endswith(".") for q in quotes), f"{seq}: 모든 quote 완전 문장(잘림 0)")
        # 모든 finding in-scope 섹션
        ck(all(dp.is_depletion_scope(f["section"]) for f in findings), f"{seq}: 모든 finding in-scope")

    # B2/off-scope 격리(아세타졸아미드 201403403): 상호작용·임부·고령자·과량 칼륨/Mg 동거어 추출 0.
    raw = open(os.path.join(FX, "detail_201403403.html"), encoding="utf-8").read()
    quotes = [f["source_quote"] for f in dp.extract_depletions(raw)]
    ck(not any("칼륨방출이 증가" in q for q in quotes),
       "B2: 상호작용(약-약 '칼륨방출 증가') 미추출")
    ck(not any("저마그네슘혈증" in q for q in quotes),
       "B2: 임부 신생아 '저마그네슘혈증' 미추출")
    ck(not any("고령자에서" in q for q in quotes), "off-scope: 고령자 섹션 미추출")
    ck(not any(f["nutrient"] == "마그네슘" for f in dp.extract_depletions(raw)),
       "마그네슘 false-positive 0(K-only 라벨)")

    # 방향 단위 테스트
    ck(dp.nutrient_depletion("저칼륨혈증이 나타날 수 있다.")[0] == "칼륨", "결핍 STATE 저칼륨혈증 → 칼륨")
    ck(dp.nutrient_depletion("칼륨의 배설을 증가시킨다.")[0] == "칼륨", "배설증가 → 칼륨")
    ck(dp.nutrient_depletion("고칼륨혈증이 나타날 수 있다.")[0] is None, "wrong-direction 고칼륨혈증 → reject")
    ck(dp.nutrient_depletion("칼륨보존성 이뇨제와 병용한다.")[0] is None, "칼륨보존성 → reject")
    ck(dp.nutrient_depletion("두통, 발진이 나타날 수 있다.")[0] is None, "영양-무관 이상반응 열거 → 미매칭")

    # 정확성분 매칭(부분매칭 오탐 차단)
    ck(dp.exact_ingredient_match("메틸프레드니솔론", "프레드니솔론") is False, "exact: 메틸프레드니솔론≠프레드니솔론")
    ck(dp.exact_ingredient_match("미분화플루드로코르티손아세테이트", "플루드로코르티손") is True,
       "exact: 미분화...아세테이트=플루드로코르티손(수식어·에스터 허용)")
    ck(dp.is_single_oral_depletion({"item_name": "메니솔론정", "ingr_name": "메틸프레드니솔론",
                                    "finished": "완제의약품", "status_cancel": "정상"}, "메틸프레드니솔론"),
       "single_oral_depletion: 단일성분 정제+정확매칭 통과")
    ck(not dp.is_single_oral_depletion({"item_name": "두두엔액", "ingr_name": "프레드니솔론발레로아세테이트/L-멘톨",
                                        "finished": "완제의약품", "status_cancel": "정상"}, "프레드니솔론"),
       "single_oral_depletion: '/' 복합제 제외")

    print("=" * 64)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — GOLD 3/3 verbatim 재현·B2/off-scope 격리·완전문장·방향·정확매칭")
    return 0


if __name__ == "__main__":
    sys.exit(main())
