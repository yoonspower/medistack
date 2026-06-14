#!/usr/bin/env python3
"""
validate_forbidden_phrases_v1_2.py
MediStack — **사용자 노출 카피 금지어/위험문구 자동검사**(재사용 게이트).

대상(사용자에게 보이는 문자열만 — 라벨 원문 인용/내부 노트는 제외):
  1) 라이브 export relations 의 display_text_ko / management_ko (읽기전용 회귀)
  2) draft 14건(라이브 통합 완료) relation_expansion_draft_v1_2.json 의 display_text_ko / management_ko
  3) factory draft batch(있으면) relation_factory_draft_batch_v1_2.json 의 display_text_ko / management_ko
  4) factory source-check CSV 의 safe_user_copy 컬럼(있으면)

검사 사유: 참고정보 베타 톤 위반(의료 단정·복용지시·승인 주장·구매/제휴/추천) 차단.
라벨 원문을 그대로 인용하는 source.pointer / evidence / internal_note 는 **검사 대상 아님**
(원문에 치료·예방·금기 등 의학 용어가 정당하게 등장하므로).

⚠️ 데이터 무수정·읽기전용. 어떤 라이브/draft 파일도 쓰지 않는다.
사용: python3 scripts/validate_forbidden_phrases_v1_2.py
종료 코드: 0 PASS(위반 0), 1 FAIL.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")

EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRAFT14 = os.path.join(DATA, "relation_expansion_draft_v1_2.json")
FACTORY_DRAFT = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")
SOURCE_CSV = os.path.join(DATA, "relation_factory_source_check_v1_2.csv")
# batch2(coverage-queue) 산출물도 동일 게이트로 스캔
COVERAGE_DRAFT = os.path.join(DATA, "coverage_queue_draft_batch_v1_2.json")
COVERAGE_SOURCE_CSV = os.path.join(DATA, "coverage_queue_source_check_v1_2.csv")
# v1.2 라운드 신규 산출물(사용자 노출 카피만 스캔 — label_quote/source_pointer 등 라벨 원문 인용은 제외)
ANTACID_DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")
POTASSIUM_PM = os.path.join(DATA, "review", "potassium_depletion_pm_ready_v1_2.json")

# 사용자 노출 카피에서 절대 금지(정확 부분문자열). 명령형 복용지시·승인주장·구매/제휴/추천·의료단정.
# 주의: '피하고'(신중 톤)는 허용, '피하세요'(명령)는 금지 — 정확 어구만.
FORBIDDEN = [
    # 승인/검수/법적 단정
    "식약처 승인", "식약처 인증", "식약처 허가 완료", "법적 문제 없음", "법적 문제없음",
    "약사 검수 완료", "약사 검수완료", "약사검수 완료", "의사 검수 완료", "임상 검증 완료",
    # 추천/구매/제휴(영양제 추천 동선)
    "추천 영양제", "추천영양제", "제품 추천", "제품추천", "추천 제품", "영양제 추천",
    "구매", "구입", "제휴", "할인", "쿠폰", "클릭", "바로가기", "최저가",
    # 복용지시(명령형)
    "복용하세요", "복용하십시오", "드세요", "드십시오", "반드시 드", "꼭 드",
    "보충하세요", "중단하세요", "끊으세요", "피하세요", "드시면 됩니다",
    # 의료 단정(치료·예방·진단 효능 주장) — 사용자 노출 카피엔 bare 형도 금지(라벨 원문 인용은 스캔 대상 아님)
    "치료합니다", "치료됩니다", "예방합니다", "예방됩니다", "진단", "완치",
    "효과가 있습니다", "안전합니다", "문제없습니다", "치료", "예방",
]


def scan(text):
    t = text or ""
    return [p for p in FORBIDDEN if p in t]


def collect():
    """(label, copy_text) 쌍 목록. 사용자 노출 필드만."""
    items = []
    # 1) 라이브 relations
    try:
        exp = json.load(open(EXPORT, encoding="utf-8"))
        for r in exp.get("relations", []):
            for fld in ("display_text_ko", "management_ko"):
                if r.get(fld):
                    items.append((f"live relation id{r.get('id')}.{fld}", r[fld]))
    except FileNotFoundError:
        pass
    # 2) draft14
    try:
        d = json.load(open(DRAFT14, encoding="utf-8"))
        for r in d.get("draft_relations", []):
            for fld in ("display_text_ko", "management_ko"):
                if r.get(fld):
                    items.append((f"draft14 {r.get('draft_id')}.{fld}", r[fld]))
    except FileNotFoundError:
        pass
    # 3) factory draft batch (있으면)
    if os.path.exists(FACTORY_DRAFT):
        d = json.load(open(FACTORY_DRAFT, encoding="utf-8"))
        for r in d.get("draft_relations", []):
            for fld in ("display_text_ko", "management_ko"):
                if r.get(fld):
                    items.append((f"factory_draft {r.get('draft_id')}.{fld}", r[fld]))
    # 4) source-check CSV safe_user_copy (있으면)
    if os.path.exists(SOURCE_CSV):
        with open(SOURCE_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                c = row.get("safe_user_copy", "")
                if c.strip():
                    items.append((f"sourcecsv {row.get('candidate_id')}.safe_user_copy", c))
    # 5) coverage-queue factory draft batch (있으면)
    if os.path.exists(COVERAGE_DRAFT):
        d = json.load(open(COVERAGE_DRAFT, encoding="utf-8"))
        for r in d.get("draft_relations", []):
            for fld in ("display_text_ko", "management_ko"):
                if r.get(fld):
                    items.append((f"cq_draft {r.get('draft_id')}.{fld}", r[fld]))
    # 6) coverage-queue source-check CSV safe_user_copy (있으면)
    if os.path.exists(COVERAGE_SOURCE_CSV):
        with open(COVERAGE_SOURCE_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                c = row.get("safe_user_copy", "")
                if c.strip():
                    items.append((f"cq_sourcecsv {row.get('candidate_id')}.safe_user_copy", c))
    # 7) antacid_interaction draft (있으면) — display/management 만(label_quote 는 라벨 원문이라 제외)
    if os.path.exists(ANTACID_DRAFT):
        d = json.load(open(ANTACID_DRAFT, encoding="utf-8"))
        for r in d.get("draft_relations", []):
            for fld in ("display_text_ko", "management_ko"):
                if r.get(fld):
                    items.append((f"antacid_draft {r.get('draft_id')}.{fld}", r[fld]))
    # 8) potassium PM-ready (있으면) — final_display/final_management 만(source_pointer 는 라벨 원문이라 제외)
    if os.path.exists(POTASSIUM_PM):
        d = json.load(open(POTASSIUM_PM, encoding="utf-8"))
        for r in d.get("items", []):
            for fld in ("final_display_text_ko", "final_display_text_ko_named", "final_management_ko"):
                if r.get(fld):
                    items.append((f"potassium_pm {r.get('draft_id')}.{fld}", r[fld]))
    return items


def main():
    items = collect()
    violations = []
    for label, text in items:
        hits = scan(text)
        if hits:
            violations.append((label, hits, text))

    print(f"=== 금지어 검사: 사용자 노출 카피 {len(items)} 문자열 ===")
    for label, hits, text in violations:
        print(f"[FAIL] {label}: {hits}")
        print(f"        \"{text[:90]}\"")
    print("=" * 64)
    if violations:
        print(f"RESULT: FAIL — {len(violations)}건 위반 / {len(items)} 검사")
        return 1
    print(f"RESULT: PASS — 위반 0 / {len(items)} 검사")
    print("(라벨 원문 인용 pointer/evidence/internal_note 는 검사 대상 아님 — 정상)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
