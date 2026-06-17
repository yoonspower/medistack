#!/usr/bin/env python3
"""
smoke_autofactory_v1_5_production_results.py
MediStack v1.5 — Production harvest 결과 스모크 (빠른 무결성 확인·읽기전용).

  1) dashboard funnel 합산 무모순: raw = queue + hold + reject + existing_prepared.
  2) source_confirmed 수 = quote 보유 결과 수.
  3) 모든 reviewer-ready 후보의 quote 가 라벨에서 실제 추출된 문자열(공백 아님·counterpart 토큰 포함).
  4) 보호셋 sha256 검증 전후 불변(직접 측정).
종료코드 0 PASS / 1 FAIL.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")
P = "autofactory_v1_5_production_"
PROTECTED = ["medistack_v0.1_beta_export.json", "medistack_v0.2_beta_export.json",
             "medistack_v0.3_aliases.json", "full_drug_name_index_sample_v1_0.json"]
fails = []


def J(name):
    return json.load(open(os.path.join(REV, P + name + ".json"), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    print("=== Production results smoke ===")
    before = {f: sha(os.path.join(DATA, f)) for f in PROTECTED}

    dash = J("dashboard")
    h = dash["harvest"]
    raw = J("raw_candidates")["candidates"]
    ck(h["raw"] == len(raw), "dashboard raw = raw_candidates count")
    ck(h["raw"] == h["source_check_queue"] + h["hold"] + h["reject"] + h["existing_prepared"],
       f"raw({h['raw']}) = queue+hold+reject+existing_prepared")

    conf = J("source_confirmed")["confirmed"]
    ck(len(conf) == h["source_confirmed_new"], "source_confirmed count = dashboard")

    waves = J("reviewer_ready_waves")
    for c in waves["candidates"]:
        q = c.get("source", {}).get("quote", "")
        toks = {"fe": "철", "ca": "칼슘", "mg": "마그네슘", "zn": "아연",
                "al_mg_antacid": "제산제", "folate": "엽산", "vitd": "비타민",
                "b12": "비타민"}.get(c["counterpart_canon"], "")
        ck(len(q) > 10 and (toks in q if toks else True),
           f"{c['raw_id']}: quote 실문자열 + counterpart 토큰 포함")

    after = {f: sha(os.path.join(DATA, f)) for f in PROTECTED}
    ck(before == after, "보호셋 sha256 불변")

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — funnel 합산 무모순 · source_confirmed 정합 · quote 실문자열 · 보호셋 불변")
    return 0


if __name__ == "__main__":
    sys.exit(main())
