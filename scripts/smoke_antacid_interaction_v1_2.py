#!/usr/bin/env python3
"""
smoke_antacid_interaction_v1_2.py
MediStack antacid_interaction 카피 **렌더 시뮬레이션 스모크**(읽기전용).
표면 카피가 (a)출처 귀속·비지시(앱이 '복용하지 마세요'라고 지시하지 않음), (b)병용 프레이밍 유지
('시간 간격 두세요'로 약화 안 함), (c)상담 종결, (d)상대=제산제 명시(Mg 영양제 오인 0)인지,
내부 directive/label_quote 가 원문 강도를 보존하는지 시뮬레이션 점검한다.
종료코드: 0 PASS, 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DRAFT = os.path.join(REPO, "data", "drafts", "antacid_interaction_draft_batch_v1_2.json")


def main():
    d = json.load(open(DRAFT, encoding="utf-8"))
    fails = []
    n = 0
    for r in d.get("draft_relations", []):
        did = r["draft_id"]
        disp = r.get("display_text_ko", "")
        n += 1
        # (a) 출처 귀속·비지시: '허가사항 문구가 있습니다' 포함, 직접 지시('복용하지 마세요') 없음
        if "허가사항 문구가 있습니다" not in disp:
            fails.append(f"{did}: 출처 귀속('허가사항 문구가 있습니다') 누락 — 비지시성 약화")
        if "복용하지 마세요" in disp:
            fails.append(f"{did}: 직접 지시('복용하지 마세요') 노출 — 앱 지시 금지")
        # (b) 병용 프레이밍 유지(separation 다운그레이드 금지)
        if "함께 사용할 때" not in disp:
            fails.append(f"{did}: 병용 프레이밍('함께 사용할 때') 누락")
        if "시간 간격을 두세요" in disp or "간격을 두는 것이 도움" in disp:
            fails.append(f"{did}: separation 다운그레이드 표현 노출(라벨 강도 약화)")
        # (c) 상담 종결
        if "약사 또는 의사에게 확인" not in disp:
            fails.append(f"{did}: 상담 종결 누락")
        # (d) 상대=제산제 명시, Mg 영양제 오인 0
        if "제산제" not in disp:
            fails.append(f"{did}: 상대(제산제) 명시 누락")
        for bad in ("마그네슘 영양제", "마그네슘 보충제"):
            if bad in disp:
                fails.append(f"{did}: Mg 영양제 오인 표현 '{bad}'")
        # 내부 강도 보존: label_quote 비공란 + directive_type 유효
        if not (r.get("label_quote") or "").strip():
            fails.append(f"{did}: 내부 label_quote 공란(원문 강도 보존 실패)")
        if r.get("label_directive_type") not in ("avoid_concomitant", "separation"):
            fails.append(f"{did}: label_directive_type 부정")
    print(f"=== antacid_interaction smoke: {n}개 카피 시뮬레이션 ===")
    if fails:
        for f in fails:
            print(f"[FAIL] {f}")
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 출처 귀속·비지시·병용 프레이밍 유지·상담 종결·제산제 명시(Mg 오인 0)·내부 강도 보존")
    return 0


if __name__ == "__main__":
    sys.exit(main())
