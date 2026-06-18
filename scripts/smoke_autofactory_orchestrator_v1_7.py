#!/usr/bin/env python3
"""
smoke_autofactory_orchestrator_v1_7.py — v1.7 스모크(네트워크 0·결정론적).

커밋된 fixture HTML 만으로 추출→감사 핵심 불변을 즉시 확인:
  1) extract_interactions 결정성(같은 HTML → 같은 finding) + GOLD 3건 재현.
  2) audit_harvested 독립 재검: 4개 harvested 후보(committed fixture)를 재추출·재검 → 전건 audit_pass·false_auto_pass 0.
  3) 보정 불가 결함(잘린 quote)은 audit_fail → false_auto_pass(B8 동작).
  4) 보호셋 sha256 불변.
종료코드 0 PASS / 1 FAIL.
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FX = os.path.join(ROOT, "tests", "fixtures", "nedrug")
DATA = os.path.join(ROOT, "data")
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


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "<MISSING>"


# committed fixture 로 재현 가능한 후보: (cid, ingredient, seq, scope_supported).
# 알렌드론산은 라벨이 일반 '제산제'만 명명 → Al/Mg-specific 미지원(scope_supported=False, 격리 대상).
HARVESTED = [
    ("H7-F3-001", "리세드론산", "200713889", True),
    ("H7-F3-003", "이반드론산", "201207007", True),
    ("H7-F4-004", "레보티록신", "197400278", True),
    ("H7-F3-002", "알렌드론산", "199800180", False),
]


def main():
    print("=== AutoFactory Orchestrator v1.7 smoke (offline·fixtures) ===")
    ex = load("ex", os.path.join(HERE, "extract_label_interaction_v1_7.py"))
    fix = load("fix", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))
    audit17 = load("a17", os.path.join(HERE, "audit_fidelity_v1_7.py"))
    orch = load("orch", os.path.join(HERE, "run_medistack_autofactory_orchestrator_v1_7.py"))

    before = {p: sha(p) for p in orch.PROTECTED}

    # 1) 결정성 + GOLD
    raw1 = open(os.path.join(FX, "detail_201903166.html"), encoding="utf-8").read()
    a = [f["source_quote"] for f in ex.extract_interactions(raw1)]
    b = [f["source_quote"] for f in ex.extract_interactions(raw1)]
    ck(a == b, "extract_interactions 결정성")
    ck("칼슘보충제, 제산제 및 다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 경구투여 약물의 병용 투여는 이 약의 흡수를 방해한다." in a,
       "GOLD #2(리세드론산) 재현")

    # 2) audit_harvested 독립 재검: scope 지원 3건 → audit_pass, 미지원(알렌드론산) → counterpart_overclaim 격리
    clean, overclaim = [], []
    for cid, ing, seq, scope_ok in HARVESTED:
        html = open(os.path.join(FX, f"detail_{seq}.html"), encoding="utf-8").read()
        findings = ex.extract_interactions(html)
        f = next((f for f in findings if f["counterpart_category"] == "al_mg_antacid"
                  and f["direction"] == "this_drug_lowered"), None)
        ck(f is not None, f"{cid}: fixture 에서 al_mg_antacid·this_drug_lowered finding 추출")
        if not f:
            continue
        cp = ex.antacid_scope_from_quote(f["source_quote"])
        if scope_ok:
            ck(cp is not None, f"{cid}: scope 지원 → counterpart 표시명 결정({cp})")
            disp, mgmt = fix.safe_app_copy(cp, "separation")
            clean.append({"candidate_id": cid, "family": cid.split("-")[1], "ingredient": ing,
                          "counterpart": cp, "counterpart_category": "al_mg_antacid",
                          "mechanism": "absorption", "action": "separation", "evidence_level": "moderate",
                          "source_pointer": f"itemSeq {seq}", "item_seq": seq, "source_quote": f["source_quote"],
                          "display_text_ko": disp, "management_ko": mgmt, "already_live_on_base": False})
        else:
            ck(cp is None, f"{cid}(알렌드론산): 일반 제산제 → antacid_scope None(Al/Mg 미명명)")
            overclaim.append((cid, seq, f["source_quote"], html))

    provider = {c["item_seq"]: open(os.path.join(FX, f"detail_{c['item_seq']}.html"), encoding="utf-8").read()
                for c in clean}
    results, asum = audit17.audit_harvested_corpus(clean, lambda s: provider[s])
    ck(asum["audit_pass"] == len(clean) and asum["false_auto_pass"] == 0,
       f"scope 지원 harvested 전건 audit_pass={asum['audit_pass']}·false_auto_pass=0")

    # 3a) counterpart 과확장(알렌드론산을 Al/Mg 로 강제) → audit_fail_counterpart_overclaim(B7)
    cid, seq, q, html = overclaim[0]
    forced = {"candidate_id": cid, "family": "F3", "ingredient": "알렌드론산",
              "counterpart": "Al/Mg 함유 제산제(약물)", "counterpart_category": "al_mg_antacid",
              "mechanism": "absorption", "action": "separation", "evidence_level": "moderate",
              "source_pointer": f"itemSeq {seq}", "item_seq": seq, "source_quote": q,
              "display_text_ko": fix.safe_app_copy("Al/Mg 함유 제산제(약물)", "separation")[0],
              "management_ko": fix.safe_app_copy("Al/Mg 함유 제산제(약물)", "separation")[1],
              "already_live_on_base": False}
    fr = audit17.audit_harvested(forced, html)
    ck(fr["audit_pass"] is False and fr["verdict"] == "audit_fail_counterpart_overclaim" and fr["false_auto_pass"] is True,
       "B7: 일반 제산제를 Al/Mg 로 강제 → audit_fail_counterpart_overclaim")

    # 3b) 잘린/미재현 quote → audit_fail(B8) — 합성 결함
    bad = {**clean[0], "candidate_id": "BAD", "source_quote": "이 약의 흡수를 방해"}
    bres = audit17.audit_harvested(bad, provider[bad["item_seq"]])
    ck(bres["audit_pass"] is False and bres["false_auto_pass"] is True,
       "합성 결함(미재현 quote) → audit_fail·false_auto_pass(B8)")

    # 4) 보호셋 불변
    after = {p: sha(p) for p in orch.PROTECTED}
    ck(before == after, "보호셋 sha256 불변(live/app/css 무수정)")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — 결정성·GOLD·harvested 독립재검 audit_pass·B8 결함검출·보호셋 불변")
    return 0


if __name__ == "__main__":
    sys.exit(main())
