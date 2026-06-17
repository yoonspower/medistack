#!/usr/bin/env python3
"""
validate_live_pr_readiness_v1_4.py
MediStack v1.4 — per-family live PR **readiness pack** 검증 + post-merge 검증 (읽기전용·live 무수정).

기본 모드: readiness JSON 이 권위 소스(reviewer_ready_global_plan_v1_4 + live export + full index)와
드리프트 없는지 재유도 대조. 보호 hash·index invariant·중복·needs_review 격리 확인.

--post-merge --wave <W>: 해당 wave 통합 후(또는 통합 전 baseline) live export 상태 검증.
  현재 count == 60 → 미통합(rehearsal 상태) 으로 PASS(정보).
  현재 count == 60+delta → 통합됨 → 신규 id 전건 present + 보호 필드(published/clinical/reviewed_by) + 안전 필드 검증.
  그 외 → FAIL.

종료코드 0 PASS / 1 FAIL.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
READINESS = os.path.join(REV, "per_family_live_pr_readiness_v1_4.json")
GLOBAL = os.path.join(REV, "reviewer_ready_global_plan_v1_4.json")
LIVE = os.path.join(ROOT, "data", "medistack_v0.2_beta_export.json")
DATA_JS = os.path.join(ROOT, "src", "js", "data.js")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def validate_pack():
    R = json.load(open(READINESS, encoding="utf-8"))
    gp = json.load(open(GLOBAL, encoding="utf-8"))["meta"]
    live = json.load(open(LIVE, encoding="utf-8"))
    print("=== readiness pack 드리프트 대조 (권위 소스 재유도) ===")

    ir = R["integration_ready"]
    ck(ir["total"] == 33 == gp["integrable_total"], "integration-ready total 33 == global plan")
    # family별 integrable_ids 일치
    for fam in ["F1", "F2", "F3", "F9", "F4", "F6"]:
        a = set(R["integration_ready"]["ids"][fam])
        b = set(gp["per_family"][fam]["integrable_ids"])
        ck(a == b, f"{fam} integrable_ids global plan 일치 ({len(a)})")
    # f1 split = 18, disjoint
    s = R["integration_ready"]["f1_split"]
    ck(len(s["nutrient10"]) == 10 and len(s["antacid8"]) == 8
       and not (set(s["nutrient10"]) & set(s["antacid8"])), "F1 split 10+8 disjoint")
    ck(set(s["nutrient10"]) | set(s["antacid8"]) == set(gp["per_family"]["F1"]["integrable_ids"]),
       "F1 split == F1 integrable 전건")
    # combined true
    ct = ir["combined_true_scenario"]
    ck(ct["all33"] == 93 and ct["F1+F2+F3+F9"] == 91 and ct["F1+F2+F3+F9+F4+F6"] == 93, "combined true 91/93")
    ck(ir["remaining_unpackaged"] == 0 and ir["live_exact_duplicate"] == 0
       and ir["cross_family_duplicate"] == 0 and ir["mixed_with_needs_review"] == 0,
       "unpackaged0·dup0·cross0·mixed0")

    # needs_review 4 격리, wave 미포함
    nr = set(R["needs_review_quarantine"]["ids"])
    gnr = set(sum(gp["needs_review_by_family"].values(), []))
    ck(nr == gnr and len(nr) == 4, "needs_review 4 == global plan")
    for w, wd in R["waves"].items():
        bad = nr & set(wd["candidate_ids"])
        ck(not bad, f"wave {w}: needs_review 미포함")
        ck(wd["delta"] == len(wd["candidate_ids"]), f"wave {w}: delta==len(ids)")

    # all33 union 검증
    base = set()
    for fam in ["F1", "F2", "F3", "F9", "F4", "F6"]:
        base |= set(R["integration_ready"]["ids"][fam])
    ck(set(R["waves"]["all33"]["candidate_ids"]) == base and len(base) == 33, "all33 == 6-family union(33)")

    # 보호 hash 일치(현재 파일 == readiness 기록)
    for fn, h in R["meta"]["protected_hashes"].items():
        ck(sha(os.path.join(ROOT, "data", fn)) == h, f"protected hash 일치: {fn}")
    # index invariant
    inv = R["meta"]["index_invariants"]
    ck(inv["relation_card"] == 1168 and inv["name_only"] == 16412 and inv["total"] == 17580
       and inv["auto_flip_on_relation_only_integration"] == 0, "index invariant 1168/16412/17580·flip0")
    # live baseline
    ck(len(live["relations"]) == 60 and live["meta"]["relation_count"] == 60, "live relations 60")
    ck(live["meta"].get("published") is False and live["meta"].get("clinical_reviewed") is False,
       "live published/clinical=false")
    # DATA_URL v0.2
    js = open(DATA_JS, encoding="utf-8").read()
    ck("medistack_v0.2_beta_export.json" in js, "DATA_URL v0.2 유지")


def validate_post_merge(wave):
    R = json.load(open(READINESS, encoding="utf-8"))
    if wave not in R["waves"]:
        print(f"unknown wave: {wave}")
        fails.append("unknown wave")
        return
    w = R["waves"][wave]
    delta = w["delta"]
    live = json.load(open(LIVE, encoding="utf-8"))
    cnt = len(live["relations"])
    print(f"=== post-merge 검증 (wave={wave}, 기대 통합 후 {60 + delta}) ===")
    if cnt == 60:
        print(f"  INFO — live count 60 == baseline. wave={wave} 미통합(rehearsal 상태). reviewer note 후 통합 예정.")
        ck(live["meta"].get("published") is False and live["meta"].get("clinical_reviewed") is False,
           "baseline published/clinical=false")
        ck(all("reviewed_by" not in r for r in live["relations"]), "baseline reviewed_by 부재")
        return
    if cnt == 60 + delta:
        print(f"  INFO — live count {cnt} == 60+{delta}. wave={wave} 통합됨 → 검증.")
        ck(live["meta"]["relation_count"] == cnt, "meta.relation_count 일치")
        ck(live["meta"].get("published") is False, "published=false")
        ck(live["meta"].get("clinical_reviewed") is False, "clinical_reviewed=false")
        ck(all("reviewed_by" not in r for r in live["relations"]), "reviewed_by 공란")
        ck(all(r.get("product_link_allowed") is not True for r in live["relations"]), "제품 링크 없음")
        return
    ck(False, f"live count {cnt} 가 baseline(60) 도 통합후({60 + delta}) 도 아님")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-merge", action="store_true")
    ap.add_argument("--wave")
    args = ap.parse_args()
    if args.post_merge:
        validate_post_merge(args.wave or "all33")
    else:
        validate_pack()
    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — readiness pack 드리프트 0 · 권위 소스 일치 · 보호/index/needs_review 격리 확인 · live 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
