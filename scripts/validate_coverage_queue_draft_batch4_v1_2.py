#!/usr/bin/env python3
"""
validate_coverage_queue_draft_batch4_v1_2.py
MediStack — coverage-queue relation factory **batch4 draft batch(Top201-300) 정합성·안전성** 검증기(읽기전용).
validate_coverage_queue_draft_batch3_v1_2.py 패턴 승계, 입력만 batch4 파일로 교체.
batch4 는 source_confirmed 0건 → draft 0건(count=0). count=0 은 정상 PASS(잘못된 relation 차단이 처리량보다 우선).

강제:
  ①모든 draft 봉인(있다면): published/clinical/reviewed_by/seal 플래그
  ②칼륨 nutrient → card=true ∧ link=false / 비칼륨 → card=false
  ③source 정합 ④카피 금지어 0 ⑤source_confirmed + 적대적 confirm ⑥금지 성분 미유입
  ⑦라이브 export relations==59(CQF01+CQF02)·published=false 불변, batch4 draft 라이브 미유입(0건이라 자명)
  ⑧count=0 정상 PASS

사용: python3 scripts/validate_coverage_queue_draft_batch4_v1_2.py
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
BATCH = os.path.join(DATA, "coverage_queue_draft_batch4_v1_2.json")
SRC_CSV = os.path.join(DATA, "coverage_queue_source_check_batch4_v1_2.csv")
ADV = os.path.join(DATA, "coverage_queue_adversarial_verify_batch4_v1_2.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")

sys.path.insert(0, HERE)
from validate_forbidden_phrases_v1_2 import scan  # noqa: E402

FORBIDDEN_INGR = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)
SEAL_TRUE = ["do_not_implement_yet", "review_required", "source_required",
             "live_integration_forbidden", "source_confirmed"]
SEAL_FALSE = ["published", "clinical_reviewed", "requires_clinical_review"]
LIVE_RELATIONS = 59          # CQF01(id59) + CQF02(id60) 승격 반영
PROMOTED = set()             # batch4 라이브 승격분 없음(source_confirmed 0)


def main():
    if not os.path.exists(BATCH):
        print(f"[STOP] batch4 draft 없음: {BATCH}")
        return 1
    batch = json.load(open(BATCH, encoding="utf-8"))
    drafts = batch["draft_relations"]
    src = ({r["candidate_id"]: r for r in csv.DictReader(open(SRC_CSV, encoding="utf-8"))}
           if os.path.exists(SRC_CSV) else {})
    adv = ({v["candidate_id"]: v for v in json.load(open(ADV, encoding="utf-8"))["verifications"]}
           if os.path.exists(ADV) else {})

    checks = []
    def ck(name, ok, detail=""):
        checks.append((bool(ok), name, detail))

    m = batch["meta"]
    ck("meta live_integration_forbidden=true", m.get("live_integration_forbidden") is True)
    ck("meta published=false·clinical_reviewed=false",
       m.get("published") is False and m.get("clinical_reviewed") is False)
    ck("meta do_not_implement_yet=true", m.get("do_not_implement_yet") is True)
    ck("meta count == draft 수", m.get("count") == len(drafts), f"{m.get('count')} vs {len(drafts)}")

    for d in drafts:
        did = d["draft_id"]
        for fld in SEAL_TRUE:
            ck(f"{did} {fld}=true", d.get(fld) is True, str(d.get(fld)))
        for fld in SEAL_FALSE:
            ck(f"{did} {fld}=false", d.get(fld) is False, str(d.get(fld)))
        ck(f"{did} reviewed_by 공란", (d.get("reviewed_by") or "") == "", repr(d.get("reviewed_by")))
        if d["nutrient"] == "칼륨":
            ck(f"{did} 칼륨 card=true", d.get("potassium_safety_card") is True)
            ck(f"{did} 칼륨 link=false", d.get("product_link_allowed") is False)
        else:
            ck(f"{did} 비칼륨 card=false", d.get("potassium_safety_card") is False)
        s = d.get("source") or {}
        ck(f"{did} source type=허가사항", s.get("type") == "허가사항")
        ck(f"{did} source url itemSeq", bool(re.search(r"itemSeq=\d+", s.get("url") or "")))
        ck(f"{did} source pointer 확인일", "확인일" in (s.get("pointer") or ""))
        ck(f"{did} source checked_at", bool(s.get("checked_at")))
        hits = scan(d.get("display_text_ko", "")) + scan(d.get("management_ko", ""))
        ck(f"{did} 카피 금지어 0", not hits, str(hits))
        ck(f"{did} 금지 성분 미유입", not FORBIDDEN_INGR.search(d.get("ingredient", "")))
        cid = d["source_candidate_id"]
        rrow = src.get(cid)
        vv = adv.get(cid)
        ck(f"{did} 후보 source_confirmed({cid})",
           bool(rrow) and rrow["source_status"] == "source_confirmed", cid)
        ck(f"{did} 후보 pass_to_draft=true({cid})", bool(rrow) and rrow["pass_to_draft"] == "true")
        ck(f"{did} 후보 적대적 final_verdict=confirm({cid})", bool(vv) and vv.get("final_verdict") == "confirm")

    draft_cids = {d["source_candidate_id"] for d in drafts}
    leaked = [c for c in draft_cids if src.get(c, {}).get("source_status") in ("hold", "reject", "needs_review")]
    ck("hold/reject/needs_review 후보 draft 미혼입", not leaked, str(leaked))

    exp = json.load(open(EXPORT, encoding="utf-8"))
    ck(f"라이브 relations=={LIVE_RELATIONS} (CQF01+CQF02 승격 반영)",
       len(exp["relations"]) == LIVE_RELATIONS, str(len(exp["relations"])))
    ck("라이브 published=false 불변", exp["meta"].get("published") is False)
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    leaked_live = [d["draft_id"] for d in drafts
                   if d["draft_id"] not in PROMOTED and (d["ingredient"], d["nutrient"]) in live_pairs]
    ck("batch4 draft 라이브 미통합(0건 자명)", not leaked_live, str(leaked_live))

    width = max((len(n) for _, n, _ in checks), default=10)
    fails = 0
    for ok, name, detail in checks:
        if not ok:
            print("[FAIL] " + name.ljust(width) + ("  " + detail if detail else ""))
            fails += 1
    print("=" * 64)
    print(f"coverage-queue batch4 draft (count={len(drafts)}) | 검사 {len(checks)} | "
          f"RESULT: {'PASS' if not fails else 'FAIL'} ({len(checks)-fails}/{len(checks)})")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
