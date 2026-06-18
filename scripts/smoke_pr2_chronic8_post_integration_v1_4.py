#!/usr/bin/env python3
"""
smoke_pr2_chronic8_post_integration_v1_4.py
PR-2 chronic8 통합 후 **앱 렌더/검색 스모크** (읽기전용·live 무수정).

  - disclaimers.common 존재(없으면 상세 렌더 차단=fail-safe)
  - 신규 8건 display_text_ko/management_ko/source 존재 · potassium_safety_card=false
  - 신규 전건 nutrient(엽산/비타민D/비타민B12) · counterpart_category 부재(약물 아님)
  - display 골질환 alarm(구루병/골연화증 등) 비노출
  - 검색 스모크: 신규 약물/영양소 토큰이 relation 에서 검색됨
종료코드 0 PASS / 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
LOCK = os.path.join(REPO, "data", "review", "pr2_chronic8_candidate_lock_v1_4.json")

BONE_ALARM = ["구루병", "골연화증", "골다공증", "골절", "치아형성", "치조골"]
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

    print("=== PR-2 chronic8 render/search smoke ===")
    ok("disclaimers.common 존재(렌더 fail-safe)", bool(exp.get("disclaimers", {}).get("common")))
    ok("신규 8건 로드", len(new_rels) == 8, str(len(new_rels)))

    miss = [r["id"] for r in new_rels if not r.get("display_text_ko") or not r.get("source")]
    ok("신규 전건 display_text_ko + source 존재", not miss, str(miss))
    nomng = [r["id"] for r in new_rels if not r.get("management_ko")]
    ok("신규 전건 management_ko 존재", not nomng, str(nomng))
    kcard = [r["id"] for r in new_rels if r.get("potassium_safety_card") is not False]
    ok("신규 전건 potassium_safety_card=false(칼륨 카드 오노출 방지)", not kcard, str(kcard))

    # 전건 nutrient(약물 counterpart 아님)
    badcat = [r["id"] for r in new_rels if "counterpart_category" in r
              or r.get("nutrient") not in ("엽산", "비타민D", "비타민B12")]
    ok("신규 전건 nutrient(엽산/비타민D/B12)·category 생략", not badcat, str(badcat))

    # display 골질환 alarm 비노출
    alarm = [(r["id"], [w for w in BONE_ALARM if w in r.get("display_text_ko", "")]) for r in new_rels]
    alarm = [a for a in alarm if a[1]]
    ok("신규 전건 display 골질환 alarm 비노출", not alarm, str(alarm))

    # 검색 스모크
    for tok, lo in [("설파살라진", 1), ("카르바마제핀", 1), ("트리메토프림", 1), ("페노바르비탈", 1),
                    ("페니토인", 2), ("프리미돈", 1), ("에스오메프라졸", 1),
                    ("엽산", 3), ("비타민D", 4), ("비타민B12", 1)]:
        hits = search(new_rels, tok)
        ok(f"검색 '{tok}' ≥ {lo}건(신규)", len(hits) >= lo, f"{len(hits)}건")

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print("RESULT: PASS — 신규 8건 렌더/검색 계약 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
