#!/usr/bin/env python3
"""
smoke_potassium_pm_ready_v1_2.py
MediStack 칼륨 PM-ready 카피 **렌더 시뮬레이션 스모크**(읽기전용).
validator(데이터 계약)와 별개로, 사용자에게 보일 문구가 참고정보 톤·비단정·상담 종결·
칼륨 안전(임의 보충 금지)인지, named 변형이 약물명을 정확히 삽입하는지 시뮬레이션 점검한다.
종료코드: 0 PASS, 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PM = os.path.join(REPO, "data", "review", "potassium_depletion_pm_ready_v1_2.json")


def main():
    d = json.load(open(PM, encoding="utf-8"))
    fails = []
    n = 0
    for i in d.get("items", []):
        did = i["draft_id"]
        disp, dispn, mgmt = i["final_display_text_ko"], i["final_display_text_ko_named"], i["final_management_ko"]
        n += 1
        # 비단정(가능성 표현) — '있을 수 있어' 포함, '빠집니다/생깁니다' 단정 없음
        if "있을 수 있어" not in disp:
            fails.append(f"{did}: 가능성 표현('있을 수 있어') 누락 — 단정 위험")
        # 상담 트리거 종결
        if "문의해볼 수 있습니다" not in disp:
            fails.append(f"{did}: 상담 트리거 종결 누락")
        # 장기·고용량 조건절(원문보다 강하지 않게)
        if "장기간 복용하거나 고용량" not in disp:
            fails.append(f"{did}: 장기·고용량 조건절 누락(과해석 방지)")
        # named 변형 약물명 삽입
        if not dispn.startswith(i["ingredient"]):
            fails.append(f"{did}: named 변형이 약물명으로 시작하지 않음")
        # management: 임의 보충 금지 + 전문가 결정 위임
        if "임의로 보충하지 말고" not in mgmt or "상담해 결정" not in mgmt:
            fails.append(f"{did}: management 임의보충금지/상담결정 누락")
        # 칼륨 보충 권유/결핍 단정 0
        for bad in ("칼륨을 보충하세요", "칼륨이 부족", "칼륨 결핍", "칼륨이 빠집니다"):
            if bad in disp or bad in mgmt:
                fails.append(f"{did}: 금지 표현 '{bad}'")
    print(f"=== potassium PM-ready smoke: {n}개 카피 시뮬레이션 ===")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 비단정·상담 종결·장기/고용량 맥락·임의보충금지·결핍단정 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
