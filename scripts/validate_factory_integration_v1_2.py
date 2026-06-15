#!/usr/bin/env python3
"""
validate_factory_integration_v1_2.py
MediStack — factory draft batch **DF06·DF07(리오티로닌×칼슘/철분) 라이브 통합 정합성** 검증기(읽기전용).

강제:
  ①relations==58·meta.relation_count==58 (draft14 55 → factory +2 → CQF01 +1)
  ②신규 ids 57·58 = 리오티로닌×칼슘 / 리오티로닌×철분, absorption/separation, evidence high,
    potassium_safety_card=false, requires_clinical_review=false
  ③draft-전용 필드(draft_id/source_batch/source_candidate_id/live_integration_forbidden/published/
    clinical_reviewed/do_not_implement_yet/adversarial_verified/note) 미누출, reviewer 크레딧 미부여
  ④source {type=허가사항, url itemSeq, pointer 확인일} 정합
  ⑤draft batch DF06/DF07 (ingredient,nutrient) 와 정합
  ⑥**DF01-DF05(칼륨) 라이브 미통합(보류 유지)**
  ⑦카피 금지어 0 (참고정보 톤)
  ⑧full index relation_card 1131·name_only 16449·total 17580(CQF01 알마게이트 54 flip 후 라이브 baseline), alias 717 불변·verified 1118/23
  ⑨published/clinical false·DATA_URL v0.2 불변

사용: python3 scripts/validate_factory_integration_v1_2.py
종료 코드: 0 PASS, 1 FAIL
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
BATCH = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

sys.path.insert(0, HERE)
from validate_forbidden_phrases_v1_2 import scan  # noqa: E402

FACTORY_IDS = {57, 58}
DRAFT_ONLY = {"draft_id", "source_batch", "source_candidate_id", "live_integration_forbidden",
              "published", "clinical_reviewed", "review_required", "source_required",
              "do_not_implement_yet", "adversarial_verified", "note", "reviewed_by", "reviewed_at"}
EXPECT = {(57, "리오티로닌", "칼슘"), (58, "리오티로닌", "철분")}


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    batch = json.load(open(BATCH, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))

    checks = []
    def ck(name, ok, detail=""):
        checks.append((bool(ok), name, detail))

    rels = exp["relations"]
    by_id = {r["id"]: r for r in rels}
    new = [r for r in rels if r["id"] in FACTORY_IDS]

    ck("relations == 60 (factory DF06·DF07 + CQF01 + CQF02 + AT-ITZ)", len(rels) == 60, str(len(rels)))
    ck("meta.relation_count == 60", exp["meta"].get("relation_count") == 60, str(exp["meta"].get("relation_count")))
    ck("신규 ids 57·58 존재", len(new) == 2, str([r["id"] for r in new]))
    got = {(r["id"], r["ingredient"], r["nutrient"]) for r in new}
    ck("신규 = 리오티로닌×칼슘(57)·철분(58)", got == EXPECT, str(got))

    for r in new:
        i = r["id"]
        ck(f"id{i} mechanism=absorption", r.get("mechanism") == "absorption", str(r.get("mechanism")))
        ck(f"id{i} action=separation", r.get("recommended_action") == "separation", str(r.get("recommended_action")))
        ck(f"id{i} evidence=high", r.get("evidence_level") == "high", str(r.get("evidence_level")))
        ck(f"id{i} potassium_safety_card=false", r.get("potassium_safety_card") is False)
        ck(f"id{i} requires_clinical_review=false", r.get("requires_clinical_review") is False)
        leaked = DRAFT_ONLY & set(r.keys())
        ck(f"id{i} draft-전용/reviewer 필드 미누출", not leaked, str(leaked))
        s = r.get("source") or {}
        ck(f"id{i} source type=허가사항", s.get("type") == "허가사항")
        ck(f"id{i} source url itemSeq", bool(re.search(r"itemSeq=\d+", s.get("url") or "")))
        ck(f"id{i} source pointer 확인일", "확인일" in (s.get("pointer") or ""))
        ck(f"id{i} source checked_at 미누출", "checked_at" not in s)
        hits = scan(r.get("display_text_ko", "")) + scan(r.get("management_ko", ""))
        ck(f"id{i} 카피 금지어 0", not hits, str(hits))

    # draft batch 정합
    drafts = {d["draft_id"]: d for d in batch["draft_relations"]}
    for did, rid in (("DF06", 57), ("DF07", 58)):
        d = drafts[did]; r = by_id.get(rid)
        ck(f"{did}↔id{rid} (ingredient,nutrient) 정합",
           r and (d["ingredient"], d["nutrient"]) == (r["ingredient"], r["nutrient"]))

    # DF01-DF05(칼륨) 보류 — 라이브 미통합
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in rels}
    k_leaked = [d["draft_id"] for d in batch["draft_relations"]
                if d["nutrient"] == "칼륨" and (d["ingredient"], d["nutrient"]) in live_pairs]
    ck("DF01-DF05 칼륨 draft 라이브 미통합(보류 유지)", not k_leaked, str(k_leaked))

    # 불변(리오티로닌 인덱스 0 → flip 0)
    counts = full["meta"]["counts"]
    ck("relation_card 1168 (CQF01 알마게이트 54 + CQF02 테고프라잔 37 flip 후 라이브 baseline)", counts.get("relation_card") == 1168, str(counts.get("relation_card")))
    ck("name_only 16412 (CQF01 54 + CQF02 37 flip 후 라이브 baseline)", counts.get("name_only") == 16412, str(counts.get("name_only")))
    ck("total 17580 불변", counts.get("total") == 17580, str(counts.get("total")))
    ck("alias_count 717 불변", aliases["meta"].get("alias_count") == 717, str(aliases["meta"].get("alias_count")))
    vis = aliases.get("verified_item_seqs") or {}
    ck("verified 1155/24 (CQF01 +54 + CQF02 테고프라잔 +37 후 라이브 baseline)", sum(len(v) for v in vis.values()) == 1155 and len(vis) == 24,
       f"{sum(len(v) for v in vis.values())}/{len(vis)}")

    # 봉인
    ck("published=false", exp["meta"].get("published") is False)
    ck("clinical_reviewed=false", exp["meta"].get("clinical_reviewed") is False)
    djs = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"DATA_URL\s*=\s*'([^']+)'", djs)
    ck("DATA_URL v0.2 불변", m and m.group(1) == "./data/medistack_v0.2_beta_export.json",
       m.group(1) if m else "none")

    width = max(len(n) for _, n, _ in checks)
    fails = 0
    for ok, name, detail in checks:
        if not ok:
            print("[FAIL] " + name.ljust(width) + ("  " + detail if detail else ""))
            fails += 1
    print("=" * 64)
    print(f"factory 통합(DF06·DF07) 검사 {len(checks)} | "
          f"RESULT: {'PASS' if not fails else 'FAIL'} ({len(checks)-fails}/{len(checks)})")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
