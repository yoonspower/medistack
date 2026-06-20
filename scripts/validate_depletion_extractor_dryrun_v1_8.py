#!/usr/bin/env python3
"""
validate_depletion_extractor_dryrun_v1_8.py — depletion 추출기 v1.8 dry-run 패키지 **검증**(읽기전용·live 무수정).

검증:
  - reviewer-ready count == dryrun funnel · 6+10+0 == queue 16
  - 🔑 칼륨 invariant 전수(칼륨 → potassium_safety_card=true·product_link_allowed=false)
  - copy-lint 전수 통과(보충/지시/수치/과확장 0) · DISPLAY 알람어(소아/골/치아) 0
  - display/management == safe_app_copy(nutrient,'depletion') verbatim(신규 문구 0·source 초과 0)
  - source_quote 가 인용 itemSeq fixture 라벨에 **verbatim 존재**(오프라인 충실도)
  - (ingredient,nutrient) live 중복 0 · 신규 projected id = max+1.. 연속
  - published/clinical_reviewed=false · reviewed_by 공란 · requires_clinical_review=false · 제품 필드 0
  - projected_relation 스키마 == live(mechanism=depletion·action=monitoring·counterpart_category=null)
  - v0.2 export relation_count 불변(95) · reviewer-ready 가 live 에 미반영
  - false_auto_pass == 0
사용: python3 scripts/validate_depletion_extractor_dryrun_v1_8.py
종료: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
RR = os.path.join(DATA, "review", "depletion_extractor_reviewer_ready_v1_8.json")
DRY = os.path.join(DATA, "review", "depletion_extractor_dryrun_v1_8.json")
FX = os.path.join(REPO, "tests", "fixtures", "nedrug")
PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
DIRECTIVE = ["복용하세요", "드세요", "드십시오", "끊으세요", "중단하세요", "보충하세요", "섭취하세요",
             "검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요"]
DISPLAY_ALARM = ["소아", "임신", "수유", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아"]
_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    tpl = load("tpl", "fix_harvester_display_template_v1_6.py")
    exp = json.load(open(EXPORT, encoding="utf-8"))
    rr = json.load(open(RR, encoding="utf-8"))
    dry = json.load(open(DRY, encoding="utf-8"))
    cands = rr["candidates"]
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}

    print("=== depletion 추출기 v1.8 dry-run validator ===")
    f = dry["meta"]["funnel"]
    ok("queue 16 = RR+needs+reject", f["reviewer_ready"] + f["needs_review"] + f["rejected"] == 16,
       str(f))
    ok("reviewer-ready count == meta", len(cands) == rr["meta"]["count"] == f["reviewer_ready"])
    ok("false_auto_pass == 0", f["false_auto_pass"] == 0 and dry["meta"]["false_auto_pass"] == [])

    # 🔑 칼륨 invariant 전수
    kbad = []
    for c in cands:
        rel = c["projected_relation"]
        if rel["nutrient"] == "칼륨":
            if rel.get("potassium_safety_card") is not True or rel.get("product_link_allowed") is not False:
                kbad.append(rel["id"])
        elif rel.get("potassium_safety_card") is not False:
            kbad.append(rel["id"])
    ok("🔑 칼륨 invariant 전수(kcard=true·link=false)", not kbad, str(kbad))

    # copy fidelity
    badcopy, badalarm, badtpl = [], [], []
    for c in cands:
        rel = c["projected_relation"]
        disp, mng, nut = rel["display_text_ko"], rel["management_ko"], rel["nutrient"]
        sq = c.get("source_quote", "")
        if tpl.copy_lint(disp, sq) or tpl.copy_lint(mng, sq) or any(d in disp + mng for d in DIRECTIVE):
            badcopy.append(rel["id"])
        if any(a in disp for a in DISPLAY_ALARM):
            badalarm.append(rel["id"])
        sd, sm = tpl.safe_app_copy(nut, "depletion")
        if disp != sd or mng != sm:
            badtpl.append(rel["id"])
    ok("copy-lint 전수 통과(보충/지시/수치 0)", not badcopy, str(badcopy))
    ok("display 알람어(소아/골/치아) 0", not badalarm, str(badalarm))
    ok("display/management == safe_app_copy(depletion) verbatim(source 초과 0)", not badtpl, str(badtpl))

    # source_quote verbatim ∈ fixture
    badsrc = []
    for c in cands:
        seq = str(c["itemSeq"])
        p = os.path.join(FX, f"detail_{seq}.html")
        if not os.path.exists(p):
            badsrc.append(f"{seq}:fixture없음"); continue
        html = open(p, encoding="utf-8").read()
        if c["source_quote"] not in html:
            badsrc.append(f"{seq}:quote미존재")
    ok("source_quote verbatim ∈ 인용 itemSeq fixture(오프라인 충실도)", not badsrc, str(badsrc))

    # source url itemSeq + pointer
    badurl = [c["itemSeq"] for c in cands
              if not re.search(r"itemSeq=\d+", c["projected_relation"]["source"]["url"])
              or not c["projected_relation"]["source"].get("pointer")]
    ok("source url itemSeq + pointer", not badurl, str(badurl))

    # live 중복 0
    dup = [(c["projected_relation"]["ingredient"], c["projected_relation"]["nutrient"]) for c in cands
           if (c["projected_relation"]["ingredient"], c["projected_relation"]["nutrient"]) in live_pairs]
    ok("(ingredient,nutrient) live 중복 0", not dup, str(dup))

    # projected id 연속(max+1..)
    base = dry["meta"]["live_max_id"]
    ids = sorted(c["projected_relation"]["id"] for c in cands)
    ok("projected id = max+1.. 연속", ids == list(range(base + 1, base + 1 + len(cands))), f"{ids} base={base}")

    # 보호 상태 플래그
    badflag = []
    for c in cands:
        rel = c["projected_relation"]
        if (rel.get("requires_clinical_review") is not False or rel.get("product_link_allowed") is not False
                or c.get("published") is not False or c.get("clinical_reviewed") is not False
                or c.get("reviewed_by") != "" or (PRODUCT_FIELDS & set(rel.keys())) or "schedule" in rel):
            badflag.append(rel["id"])
    ok("published/clinical=false·reviewed_by 공란·제품/schedule 0", not badflag, str(badflag))
    ok("live_integration_forbidden 전건", all(c.get("live_integration_forbidden") is True for c in cands))

    # 스키마 == live
    badschema = [c["projected_relation"]["id"] for c in cands
                 if c["projected_relation"].get("mechanism") != "depletion"
                 or c["projected_relation"].get("recommended_action") != "monitoring"
                 or c["projected_relation"].get("counterpart_category") is not None]
    ok("projected 스키마 depletion·monitoring·counterpart_category=null", not badschema, str(badschema))

    # v0.2 불변
    ok("v0.2 relation_count 불변(95)", len(exp["relations"]) == 95 and exp["meta"].get("relation_count") == 95,
       str(len(exp["relations"])))
    notlive = all(i not in {r["id"] for r in exp["relations"]} for i in ids)
    ok("reviewer-ready id 가 live 에 미반영(dry-run)", notlive)

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}"); return 1
    print("RESULT: PASS — reviewer-ready 6 · 칼륨 invariant · copy/소스 충실 · live 무반영 · 스키마 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
