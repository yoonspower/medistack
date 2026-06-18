#!/usr/bin/env python3
"""
smoke_pr1_antibiotic24_post_integration_v1_4.py
PR-1 antibiotic24 통합 후 **앱 렌더/검색 스모크** (읽기전용·live 무수정).

앱(src/js)의 렌더 계약 관점에서 신규 24건이 안전히 렌더/검색되는지 가벼운 확인:
  - disclaimers.common 존재(없으면 상세 렌더 차단=fail-safe)
  - 신규 전건 display_text_ko/management_ko/source 존재 · potassium_safety_card=false(칼륨 카드 오노출 방지)
  - counterpart_category 가 al_mg_antacid 인 신규는 nutrient 표기에 '약물' 포함(약물 counterpart 렌더 경로)
  - 검색 스모크: 신규 핵심 토큰이 relation 에서 검색됨
종료코드 0 PASS / 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
LOCK = os.path.join(REPO, "data", "review", "pr1_antibiotic24_candidate_lock_v1_4.json")

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def search(rels, token):
    """앱 검색 휴리스틱: ingredient/nutrient 부분일치 relation 수."""
    return [r for r in rels if token in r.get("ingredient", "") or token in r.get("nutrient", "")]


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    new_ids = set(lock["expected_ids"])
    new_rels = [r for r in rels if r["id"] in new_ids]

    print("=== PR-1 antibiotic24 render/search smoke ===")
    ok("disclaimers.common 존재(렌더 fail-safe)", bool(exp.get("disclaimers", {}).get("common")))
    ok("신규 24건 로드", len(new_rels) == 24, str(len(new_rels)))

    miss = [r["id"] for r in new_rels if not r.get("display_text_ko") or not r.get("source")]
    ok("신규 전건 display_text_ko + source 존재", not miss, str(miss))
    nomng = [r["id"] for r in new_rels if not r.get("management_ko")]
    ok("신규 전건 management_ko 존재", not nomng, str(nomng))
    kcard = [r["id"] for r in new_rels if r.get("potassium_safety_card") is not False]
    ok("신규 전건 potassium_safety_card=false(칼륨 카드 오노출 방지)", not kcard, str(kcard))

    # al_mg_antacid 약물 counterpart 렌더 경로
    antacid = [r for r in new_rels if r.get("counterpart_category") == "al_mg_antacid"]
    bad_label = [r["id"] for r in antacid if "약물" not in r.get("nutrient", "")]
    ok("al_mg_antacid 신규는 nutrient 에 '약물' 표기(%d건)" % len(antacid), not bad_label, str(bad_label))
    nut = [r for r in new_rels if not r.get("counterpart_category")]
    ok("nutrient 신규는 category 생략(%d건)" % len(nut),
       all("counterpart_category" not in r for r in nut))

    # 검색 스모크
    for tok, lo in [("노르플록사신", 1), ("자보플록사신", 1), ("토수플록사신", 1),
                    ("페플록사신", 1), ("테트라사이클린", 1), ("로메플록사신", 1),
                    ("발로플록사신", 1), ("제산제", len(antacid)), ("시프로플록사신", 1)]:
        hits = search(rels, tok)
        ok(f"검색 '{tok}' ≥ {lo}건", len(hits) >= lo, f"{len(hits)}건")
    # 시프로플록사신 add-on: ×제산제(약물) 신규 존재
    cipro_antacid = [r for r in new_rels if r["ingredient"] == "시프로플록사신"
                     and r.get("counterpart_category") == "al_mg_antacid"]
    ok("시프로플록사신 × Al/Mg 제산제 add-on 신규 1건", len(cipro_antacid) == 1, str(len(cipro_antacid)))

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print("RESULT: PASS — 신규 24건 렌더/검색 계약 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
