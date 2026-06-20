#!/usr/bin/env python3
"""
smoke_pr5_potassium_depletion_post_integration_v1_4.py
PR-5 통합 후 **앱 렌더/검색 스모크** (읽기전용·live 무수정).
  - disclaimers.common 존재(렌더 fail-safe)
  - 신규 6건 display_text_ko/management_ko/source 존재
  - 🔑 신규 6건 potassium_safety_card=true · counterpart_category=null
  - display 라벨귀속/알람어/수치 단정 비노출
  - 검색 스모크: 칼륨 / 6 약물명
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
LOCK = os.path.join(REPO, "data", "review", "pr5_potassium_depletion_candidate_lock_v1_4.json")
ALARM = ["소아", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아", "분리하도록 안내", "수치 변화", "수치가 걱정"]
_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    new_ids = set(lock["expected_ids"])
    new_rels = [r for r in rels if r["id"] in new_ids]

    print("=== PR-5 칼륨 depletion render/search smoke ===")
    ok("disclaimers.common 존재(렌더 fail-safe)", bool(exp.get("disclaimers", {}).get("common")))
    ok("신규 6건 로드", len(new_rels) == 6, str(len(new_rels)))
    miss = [r["id"] for r in new_rels if not r.get("display_text_ko") or not r.get("management_ko") or not r.get("source")]
    ok("신규 display/management/source 존재", not miss, str(miss))
    kcard = [r["id"] for r in new_rels if r.get("potassium_safety_card") is not True]
    ok("🔑 신규 6건 potassium_safety_card=true", not kcard, str(kcard))
    nullcat = [r["id"] for r in new_rels if r.get("counterpart_category") is not None]
    ok("신규 counterpart_category=null(영양소)", not nullcat, str(nullcat))
    alarm = [r["id"] for r in new_rels if any(a in r.get("display_text_ko", "") for a in ALARM)]
    ok("신규 display 알람어/라벨귀속/수치 비노출", not alarm, str(alarm))

    def search(tok):
        return [r for r in rels if tok in r.get("ingredient", "") or tok in r.get("nutrient", "")]
    ok("검색 '칼륨' ≥ 11건(기존5+신규6)", len(search("칼륨")) >= 11, f"{len(search('칼륨'))}건")
    for d in lock["drugs"]:
        ok(f"검색 '{d}' ≥ 1건(신규)", len(search(d)) >= 1, f"{len(search(d))}건")

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}"); return 1
    print("RESULT: PASS — 신규 6건 렌더/검색 계약 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
