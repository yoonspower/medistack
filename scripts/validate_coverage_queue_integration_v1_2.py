#!/usr/bin/env python3
"""
validate_coverage_queue_integration_v1_2.py
MediStack — coverage-queue draft batch **CQF01(알마게이트×철분) 라이브 통합 정합성** 검증기(읽기전용).
validate_factory_integration_v1_2.py 패턴 승계 + full index 알마게이트 flip 검사 추가.

강제:
  ①relations==58·meta.relation_count==58 (factory DF06·DF07 57 → CQF01 +1)
  ②신규 id 59 = 알마게이트×철분, absorption/separation, evidence high,
    potassium_safety_card=false, requires_clinical_review=false
  ③draft-전용/reviewer 필드 미누출(draft_id/source_batch/source_candidate_id/live_integration_forbidden/
    published/clinical_reviewed/do_not_implement_yet/adversarial_verified/risk_level/note/reviewed_by)
  ④source {type=허가사항, url itemSeq, pointer 확인일·철(Fe)염 인용} 정합·checked_at 미누출
  ⑤draft batch CQF01 (ingredient,nutrient) 와 정합
  ⑥카피 금지어 0 (참고정보 톤)
  ⑦full index: 알마게이트 단일성분 54품목 relation_card ∧ covered ∧ pool 진입,
    복합(알마게이트/유당수화물)은 name_only ∧ ∉pool(보수적 유지)
  ⑧counts relation_card 1131·name_only 16449·total 17580, alias_count 717 불변·verified 1118/23(알마게이트 54)
  ⑨published/clinical false·DATA_URL v0.2 불변

사용: python3 scripts/validate_coverage_queue_integration_v1_2.py
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
BATCH = os.path.join(DATA, "coverage_queue_draft_batch_v1_2.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

sys.path.insert(0, HERE)
from validate_forbidden_phrases_v1_2 import scan  # noqa: E402

CQF_ID = 59
EXPECT = (59, "알마게이트", "철분")
FLIP_ING = "알마게이트"
DRAFT_ONLY = {"draft_id", "source_batch", "source_candidate_id", "live_integration_forbidden",
              "published", "clinical_reviewed", "review_required", "source_required",
              "do_not_implement_yet", "adversarial_verified", "risk_level", "note",
              "reviewed_by", "reviewed_at"}


def build_pool(aliases):
    pool = set()
    for lst in (aliases.get("verified_item_seqs") or {}).values():
        for e in lst:
            s = str(e.get("item_seq") or "").strip()
            if s:
                pool.add(s)
    for p in (aliases.get("product_aliases") or []):
        s = str(p.get("item_seq") or "").strip()
        if s:
            pool.add(s)
    return pool


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

    ck("relations == 58", len(rels) == 58, str(len(rels)))
    ck("meta.relation_count == 58", exp["meta"].get("relation_count") == 58, str(exp["meta"].get("relation_count")))

    r = by_id.get(CQF_ID)
    ck(f"id{CQF_ID} 존재", r is not None)
    if r:
        got = (r["id"], r["ingredient"], r["nutrient"])
        ck("id59 = 알마게이트×철분", got == EXPECT, str(got))
        ck("id59 mechanism=absorption", r.get("mechanism") == "absorption", str(r.get("mechanism")))
        ck("id59 action=separation", r.get("recommended_action") == "separation", str(r.get("recommended_action")))
        ck("id59 evidence=high", r.get("evidence_level") == "high", str(r.get("evidence_level")))
        ck("id59 potassium_safety_card=false", r.get("potassium_safety_card") is False)
        ck("id59 requires_clinical_review=false", r.get("requires_clinical_review") is False)
        leaked = DRAFT_ONLY & set(r.keys())
        ck("id59 draft-전용/reviewer 필드 미누출", not leaked, str(leaked))
        s = r.get("source") or {}
        ck("id59 source type=허가사항", s.get("type") == "허가사항")
        ck("id59 source url itemSeq", bool(re.search(r"itemSeq=\d+", s.get("url") or "")))
        ck("id59 source pointer 확인일", "확인일" in (s.get("pointer") or ""))
        ck("id59 source pointer 철(Fe)염 인용", "철(Fe)염" in (s.get("pointer") or ""))
        ck("id59 source checked_at 미누출", "checked_at" not in s)
        hits = scan(r.get("display_text_ko", "")) + scan(r.get("management_ko", ""))
        ck("id59 카피 금지어 0", not hits, str(hits))

    # draft batch CQF01 정합
    drafts = {d["draft_id"]: d for d in batch["draft_relations"]}
    d = drafts.get("CQF01")
    ck("CQF01↔id59 (ingredient,nutrient) 정합",
       bool(d) and r and (d["ingredient"], d["nutrient"]) == (r["ingredient"], r["nutrient"]))

    # full index flip: 알마게이트 단일성분 → relation_card ∧ pool / 복합 → name_only ∧ ∉pool
    pool = build_pool(aliases)
    single = [e for e in full["entries"]
              if (e.get("ingredient_name") or "") == FLIP_ING]
    combo = [e for e in full["entries"]
             if FLIP_ING in (e.get("ingredient_name") or "") and (e.get("ingredient_name") or "") != FLIP_ING]
    bad_single = [e.get("item_seq") for e in single
                  if e.get("display_mode") != "relation_card" or e.get("covered_by_relation") is not True
                  or str(e.get("item_seq")).strip() not in pool]
    bad_combo = [e.get("item_seq") for e in combo
                 if e.get("display_mode") != "name_only" or str(e.get("item_seq")).strip() in pool]
    ck("알마게이트 단일 54건 → relation_card ∧ covered ∧ pool", len(single) == 54 and not bad_single,
       f"단일 {len(single)} 위반 {bad_single[:5]}")
    ck("알마게이트 복합(유당수화물) → name_only ∧ ∉pool(보수적)", not bad_combo, f"위반 {bad_combo[:5]}")

    counts = full["meta"]["counts"]
    ck("relation_card 1131", counts.get("relation_card") == 1131, str(counts.get("relation_card")))
    ck("name_only 16449", counts.get("name_only") == 16449, str(counts.get("name_only")))
    ck("total 17580 불변", counts.get("total") == 17580, str(counts.get("total")))

    vis = aliases.get("verified_item_seqs") or {}
    ck("verified_item_seqs 에 알마게이트 키", FLIP_ING in vis)
    ck("알마게이트 verified 54건", len(vis.get(FLIP_ING) or []) == 54, str(len(vis.get(FLIP_ING) or [])))
    ck("verified 1118/23", sum(len(v) for v in vis.values()) == 1118 and len(vis) == 23,
       f"{sum(len(v) for v in vis.values())}/{len(vis)}")
    ck("alias_count 717 불변", aliases["meta"].get("alias_count") == 717, str(aliases["meta"].get("alias_count")))

    ck("published=false", exp["meta"].get("published") is False)
    ck("clinical_reviewed=false", exp["meta"].get("clinical_reviewed") is False)
    djs = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"DATA_URL\s*=\s*'([^']+)'", djs)
    ck("DATA_URL v0.2 불변", bool(m) and m.group(1) == "./data/medistack_v0.2_beta_export.json",
       m.group(1) if m else "none")

    width = max(len(n) for _, n, _ in checks)
    fails = 0
    for ok, name, detail in checks:
        if not ok:
            print("[FAIL] " + name.ljust(width) + ("  " + detail if detail else ""))
            fails += 1
    print("=" * 64)
    print(f"coverage-queue 통합(CQF01 알마게이트×철분) 검사 {len(checks)} | "
          f"RESULT: {'PASS' if not fails else 'FAIL'} ({len(checks)-fails}/{len(checks)})")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
