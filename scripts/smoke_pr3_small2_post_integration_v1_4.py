#!/usr/bin/env python3
"""
smoke_pr3_small2_post_integration_v1_4.py
PR-3 small2 통합 후 **앱 렌더/검색 스모크** (읽기전용·live 무수정).
  - disclaimers.common 존재
  - 신규 2건 display_text_ko/management_ko/source 존재 · potassium_safety_card=false
  - 신규 전건 al_mg_antacid(약물 counterpart) → nutrient 표기에 '약물' 포함 · counterpart_category=al_mg_antacid
  - display 라벨귀속 '분리하도록 안내' 단정 비노출
  - 검색 스모크: 이반드론산/레보티록신/제산제
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
LOCK = os.path.join(REPO, "data", "review", "pr3_small2_candidate_lock_v1_4.json")
_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def search(rels, token):
    return [r for r in rels if token in r.get("ingredient", "") or token in r.get("nutrient", "")]


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    new_ids = set(lock["expected_ids"])
    new_rels = [r for r in rels if r["id"] in new_ids]

    print("=== PR-3 small2 render/search smoke ===")
    ok("disclaimers.common 존재(렌더 fail-safe)", bool(exp.get("disclaimers", {}).get("common")))
    ok("신규 2건 로드", len(new_rels) == 2, str(len(new_rels)))
    miss = [r["id"] for r in new_rels if not r.get("display_text_ko") or not r.get("source")]
    ok("신규 전건 display_text_ko + source 존재", not miss, str(miss))
    nomng = [r["id"] for r in new_rels if not r.get("management_ko")]
    ok("신규 전건 management_ko 존재", not nomng, str(nomng))
    kcard = [r["id"] for r in new_rels if r.get("potassium_safety_card") is not False]
    ok("신규 전건 potassium_safety_card=false", not kcard, str(kcard))

    bad_label = [r["id"] for r in new_rels if r.get("counterpart_category") != "al_mg_antacid"
                 or "약물" not in r.get("nutrient", "")]
    ok("신규 전건 al_mg_antacid · nutrient 에 '약물' 표기", not bad_label, str(bad_label))

    bad_attr = [r["id"] for r in new_rels if "분리하도록 안내" in r.get("display_text_ko", "")]
    ok("신규 display 라벨귀속 '분리하도록 안내' 단정 비노출", not bad_attr, str(bad_attr))

    for tok, lo in [("이반드론산", 1), ("레보티록신", 1), ("제산제", 2)]:
        hits = search(new_rels, tok)
        ok(f"검색 '{tok}' ≥ {lo}건(신규)", len(hits) >= lo, f"{len(hits)}건")

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print("RESULT: PASS — 신규 2건 렌더/검색 계약 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
