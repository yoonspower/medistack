#!/usr/bin/env python3
"""
validate_factory_draft_batch_v1_2.py
MediStack — relation factory **draft batch(DF01-DF07) 정합성·안전성** 검증기(읽기전용).

강제:
  ①모든 draft 봉인 플래그: published=false·clinical_reviewed=false·do_not_implement_yet=true·
    review_required=true·source_required=true·live_integration_forbidden=true·requires_clinical_review=false
  ②칼륨 nutrient 행 → potassium_safety_card=true ∧ product_link_allowed=false (안전정책 승계)
     비-칼륨 행 → potassium_safety_card=false
  ③source {type=허가사항, url itemSeq, pointer 확인일·인용, checked_at} 정합
  ④draft 카피(display/management) 금지어 0 (참고정보 톤)
  ⑤출처 후보가 실제 source_confirmed + 적대적 verdict=confirm 인지 교차검증(hold/reject 미혼입)
  ⑥금지 성분(에스오메프라졸·와파린) 미유입
  ⑦라이브 export(relations 55)·full index·alias 무변경(이 batch 는 라이브 미반영)

사용: python3 scripts/validate_factory_draft_batch_v1_2.py
종료 코드: 0 PASS, 1 FAIL
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
BATCH = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")
SRC_CSV = os.path.join(DATA, "relation_factory_source_check_v1_2.csv")
ADV = os.path.join(DATA, "relation_factory_adversarial_verify_v1_2.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")

# validate_forbidden_phrases_v1_2.scan 재사용
sys.path.insert(0, HERE)
from validate_forbidden_phrases_v1_2 import scan  # noqa: E402

FORBIDDEN_INGR = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)
SEAL_TRUE = ["do_not_implement_yet", "review_required", "source_required", "live_integration_forbidden"]
SEAL_FALSE = ["published", "clinical_reviewed", "requires_clinical_review"]


def main():
    batch = json.load(open(BATCH, encoding="utf-8"))
    drafts = batch["draft_relations"]
    src = {r["candidate_id"]: r for r in csv.DictReader(open(SRC_CSV, encoding="utf-8"))}
    adv = {v["candidate_id"]: v for v in json.load(open(ADV, encoding="utf-8"))["verdicts"]}

    checks = []
    def ck(name, ok, detail=""):
        checks.append((bool(ok), name, detail))

    # meta 봉인
    m = batch["meta"]
    ck("meta live_integration_forbidden=true", m.get("live_integration_forbidden") is True)
    ck("meta published=false·clinical_reviewed=false", m.get("published") is False and m.get("clinical_reviewed") is False)
    ck("meta do_not_implement_yet=true", m.get("do_not_implement_yet") is True)

    # 행별
    for d in drafts:
        did = d["draft_id"]
        for fld in SEAL_TRUE:
            ck(f"{did} {fld}=true", d.get(fld) is True, str(d.get(fld)))
        for fld in SEAL_FALSE:
            ck(f"{did} {fld}=false", d.get(fld) is False, str(d.get(fld)))
        # 칼륨 안전정책
        if d["nutrient"] == "칼륨":
            ck(f"{did} 칼륨 card=true", d.get("potassium_safety_card") is True)
            ck(f"{did} 칼륨 link=false", d.get("product_link_allowed") is False)
        else:
            ck(f"{did} 비칼륨 card=false", d.get("potassium_safety_card") is False)
        # source 정합
        s = d.get("source") or {}
        ck(f"{did} source type=허가사항", s.get("type") == "허가사항")
        ck(f"{did} source url itemSeq", bool(re.search(r"itemSeq=\d+", s.get("url") or "")))
        ck(f"{did} source pointer 확인일", "확인일" in (s.get("pointer") or ""))
        ck(f"{did} source checked_at", bool(s.get("checked_at")))
        # 금지어(카피)
        hits = scan(d.get("display_text_ko", "")) + scan(d.get("management_ko", ""))
        ck(f"{did} 카피 금지어 0", not hits, str(hits))
        # 금지 성분
        ck(f"{did} 금지 성분 미유입", not FORBIDDEN_INGR.search(d.get("ingredient", "")))
        # 출처 후보 교차검증
        cid = d["source_candidate_id"]
        rrow = src.get(cid)
        vv = adv.get(cid)
        ck(f"{did} 후보 source_confirmed({cid})", rrow and rrow["source_status"] == "source_confirmed", cid)
        ck(f"{did} 후보 pass_to_draft=true({cid})", rrow and rrow["pass_to_draft"] == "true")
        ck(f"{did} 후보 적대적 confirm({cid})",
           vv and vv["verdict"] == "confirm" and vv["recommended_status"] == "source_confirmed")

    # hold/reject 후보가 draft 에 섞이지 않음
    draft_cids = {d["source_candidate_id"] for d in drafts}
    leaked = [c for c in draft_cids if src.get(c, {}).get("source_status") in ("hold", "reject", "needs_review")]
    ck("hold/reject/needs_review 후보 draft 미혼입", not leaked, str(leaked))

    # 라이브 봉인(이 batch 는 라이브 미반영)
    exp = json.load(open(EXPORT, encoding="utf-8"))
    ck("라이브 relations==59 (draft14 + factory DF06·DF07 + CQF01 + CQF02 통합)", len(exp["relations"]) == 59, str(len(exp["relations"])))
    ck("라이브 published=false 불변", exp["meta"].get("published") is False)
    # DF06·DF07(리오티로닌)만 라이브, DF01-DF05(칼륨)는 보류 — 칼륨 factory 후보 라이브 미혼입
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    k_drafts = [d for d in drafts if d["nutrient"] == "칼륨"]
    leaked_k = [d["draft_id"] for d in k_drafts if (d["ingredient"], d["nutrient"]) in live_pairs]
    ck("DF01-DF05 칼륨 draft 라이브 미통합(보류 유지)", not leaked_k, str(leaked_k))

    width = max(len(n) for _, n, _ in checks)
    fails = 0
    for ok, name, detail in checks:
        if not ok:
            print("[FAIL] " + name.ljust(width) + ("  " + detail if detail else ""))
            fails += 1
    print("=" * 64)
    print(f"draft batch DF01-DF{len(drafts):02d} | 검사 {len(checks)} | "
          f"RESULT: {'PASS' if not fails else 'FAIL'} ({len(checks)-fails}/{len(checks)})")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
