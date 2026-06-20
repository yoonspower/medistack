#!/usr/bin/env python3
"""
smoke_depletion_extractor_dryrun_v1_8.py — depletion v1.8 reviewer-ready **앱 렌더/검색 스모크**(읽기전용).
  - 각 RR: display_text_ko/management_ko/source 존재 · counterpart_category=null
  - 칼륨 행 potassium_safety_card=true · 비칼륨은 false
  - display 라벨귀속/알람어 비노출(소아·골·치아·'분리하도록 안내'·수치 단정)
  - disclaimers.common 존재(live 렌더 fail-safe 회귀)
  - 검색 스모크: 약물명/영양소(칼륨)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
RR = os.path.join(REPO, "data", "review", "depletion_extractor_reviewer_ready_v1_8.json")
ALARM = ["소아", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아", "분리하도록 안내", "수치 변화", "수치가 걱정"]
_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    rr = json.load(open(RR, encoding="utf-8"))
    cands = rr["candidates"]
    rels = [c["projected_relation"] for c in cands]

    print("=== depletion v1.8 render/search smoke ===")
    ok("disclaimers.common 존재(렌더 fail-safe)", bool(exp.get("disclaimers", {}).get("common")))
    ok("RR 6건 로드", len(cands) == 6, str(len(cands)))
    miss = [r["id"] for r in rels if not r.get("display_text_ko") or not r.get("management_ko") or not r.get("source")]
    ok("display/management/source 존재", not miss, str(miss))
    nullcat = [r["id"] for r in rels if r.get("counterpart_category") is not None]
    ok("counterpart_category=null(영양소)", not nullcat, str(nullcat))
    kbad = [r["id"] for r in rels if (r["nutrient"] == "칼륨") != (r.get("potassium_safety_card") is True)]
    ok("칼륨↔potassium_safety_card 일치", not kbad, str(kbad))
    alarm = [r["id"] for r in rels if any(a in r.get("display_text_ko", "") for a in ALARM)]
    ok("display 알람어/라벨귀속/수치 단정 비노출", not alarm, str(alarm))

    def search(tok):
        return [r for r in rels if tok in r.get("ingredient", "") or tok in r.get("nutrient", "")]
    for tok, lo in [("칼륨", 6), ("아세타졸아미드", 1), ("아조세미드", 1), ("메틸프레드니솔론", 1)]:
        ok(f"검색 '{tok}' ≥ {lo}건", len(search(tok)) >= lo, f"{len(search(tok))}건")

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}"); return 1
    print("RESULT: PASS — RR 6건 렌더/검색 계약 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
