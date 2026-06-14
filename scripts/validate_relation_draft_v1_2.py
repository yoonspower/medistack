#!/usr/bin/env python3
"""
validate_relation_draft_v1_2.py
MediStack — v1.2 draft relation 14건(D01-D14) **라이브 통합 정합성** 검증기.

integrate_relation_draft_v1_2.py 통합 결과를 사후 검증한다(데이터 무수정·읽기전용).
강제: ①신규 relation 14건(ids 43-56)이 draft source_confirmed 와 정합 ②기존 relation 41건 보존
      ③draft-전용 필드 미누출 ④evidence 일관성 조정(D12/D14 moderate) ⑤칼륨 안전정책 승계
      ⑥full index flip(클로르탈리돈·인다파미드 단일 relation_card·복합 name_only) ⑦봉인 불변.

사용: python3 scripts/validate_relation_draft_v1_2.py
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
DRAFT = os.path.join(DATA, "relation_expansion_draft_v1_2.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

NEW_IDS = set(range(43, 57))  # 43..56 (v1.2 draft14 통합분)
FACTORY_IDS = {57, 58}        # factory draft batch DF06·DF07(리오티로닌×칼슘/철분) 후속 통합분
DRAFT_ONLY_FIELDS = {"draft_id", "source_queue_id", "published", "clinical_reviewed",
                     "review_required", "source_required", "do_not_implement_yet", "note"}
EVIDENCE_MODERATE = {("클로르탈리돈", "마그네슘"), ("인다파미드", "마그네슘")}
FLIP_INGREDIENTS = {"클로르탈리돈", "인다파미드"}
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    full = json.load(open(FULL, encoding="utf-8"))

    checks = []
    def ck(name, ok, detail=""):
        checks.append((bool(ok), name, detail))

    rels = exp["relations"]
    by_id = {r["id"]: r for r in rels}
    new = [r for r in rels if r["id"] in NEW_IDS]
    drafts = {(d["ingredient"], d["nutrient"]): d for d in draft["draft_relations"]}

    # 1) 신규 14건 존재 + 기존 41 보존
    ck("신규 relation 14건(ids 43-56) 존재", len(new) == 14, f"{len(new)}")
    ck("총 relations == 57 (draft14 + factory DF06·DF07)", len(rels) == 57, f"{len(rels)}")
    ck("meta.relation_count == 57", exp["meta"].get("relation_count") == 57, str(exp["meta"].get("relation_count")))
    old_ids = {r["id"] for r in rels} - NEW_IDS - FACTORY_IDS
    ck("기존 id 1-42(15 제외) 보존", old_ids == (set(range(1, 43)) - {15}), f"{sorted(old_ids)[:5]}...")

    # 2) 신규 14건 각각 draft 와 (ingredient,nutrient) 정합 + draft 전체 통합
    new_pairs = {(r["ingredient"], r["nutrient"]) for r in new}
    ck("신규 14건 (ingredient,nutrient) == draft 14건", new_pairs == set(drafts.keys()),
       f"missing={set(drafts.keys())-new_pairs} extra={new_pairs-set(drafts.keys())}")

    # 3) draft-전용 필드 미누출 + 금지 성분 미유입
    leaked = [r["id"] for r in new if DRAFT_ONLY_FIELDS & set(r.keys())]
    ck("draft-전용 필드(published/clinical_reviewed/draft_id 등) 미누출", not leaked, f"{leaked}")
    forb = [r["id"] for r in new if FORBIDDEN_RE.search(r.get("ingredient", ""))]
    ck("금지 성분(에스오메/와파린) 미유입", not forb, f"{forb}")

    # 4) source.checked_at 미누출 + pointer 확인일 부착 + url itemSeq
    src_bad = []
    for r in new:
        s = r.get("source") or {}
        if "checked_at" in s:
            src_bad.append(f"id{r['id']}:checked_at누출")
        if "확인일" not in (s.get("pointer") or ""):
            src_bad.append(f"id{r['id']}:확인일없음")
        if not re.search(r"itemSeq=\d+", s.get("url") or ""):
            src_bad.append(f"id{r['id']}:url itemSeq없음")
    ck("source {type,url(itemSeq),pointer(확인일)} 정합·checked_at 미누출", not src_bad, f"{src_bad}")

    # 5) evidence 일관성: D12/D14(치아지드유사×Mg)=moderate, 그 외 신규=draft 와 동일(전부 high)
    ev_bad = []
    for r in new:
        pair = (r["ingredient"], r["nutrient"])
        want = "moderate" if pair in EVIDENCE_MODERATE else "high"
        if r.get("evidence_level") != want:
            ev_bad.append(f"id{r['id']} {pair} ev={r.get('evidence_level')}!={want}")
    ck("evidence 일관성(D12/D14 moderate·그 외 high)", not ev_bad, f"{ev_bad}")

    # 6) 칼륨 안전정책: 칼륨 nutrient 신규 행 → card=true·link=false
    k_bad = []
    for r in new:
        if r["nutrient"] == "칼륨":
            if not (r.get("potassium_safety_card") is True and r.get("product_link_allowed") is False):
                k_bad.append(f"id{r['id']}")
    ck("칼륨 신규 행 안전정책(card=true·link=false) 승계", not k_bad, f"{k_bad}")
    # 칼륨 행은 정확히 2건(클로르탈리돈·인다파미드)
    k_ct = sum(1 for r in new if r["nutrient"] == "칼륨")
    ck("신규 칼륨 행 정확히 2건(클로르탈리돈·인다파미드)", k_ct == 2, f"{k_ct}")

    # 7) full index flip: 클로르탈리돈·인다파미드 단일 relation_card / 복합 name_only
    def has_sep(i): return ("/" in i) or ("," in i)
    flip_bad, combo_bad = [], []
    pool = set()
    for lst in (aliases.get("verified_item_seqs") or {}).values():
        for e in lst:
            pool.add(str(e.get("item_seq")))
    for p in (aliases.get("product_aliases") or []):
        pool.add(str(p.get("item_seq")))
    for e in full["entries"]:
        ing = e.get("ingredient_name") or ""
        if ing in FLIP_INGREDIENTS:  # 단일성분 정확 일치
            if e.get("display_mode") != "relation_card" or str(e.get("item_seq")) not in pool:
                flip_bad.append(str(e.get("item_seq")))
        elif any(f in ing for f in FLIP_INGREDIENTS) and has_sep(ing):  # 복합제
            if e.get("display_mode") != "name_only" or str(e.get("item_seq")) in pool:
                combo_bad.append(str(e.get("item_seq")))
    ck("클로르탈리돈·인다파미드 단일 → relation_card ∧ pool", not flip_bad, f"{flip_bad[:5]}")
    ck("클로르탈리돈·인다파미드 복합 → name_only ∧ ∉pool(보수적 유지)", not combo_bad, f"{combo_bad[:5]}")

    # 8) verified_item_seqs 키 추가(클로르탈리돈·인다파미드)
    vis = aliases.get("verified_item_seqs") or {}
    ck("verified_item_seqs 에 클로르탈리돈·인다파미드 키 추가",
       "클로르탈리돈" in vis and "인다파미드" in vis,
       f"클로르탈리돈={'O' if '클로르탈리돈' in vis else 'X'} 인다파미드={'O' if '인다파미드' in vis else 'X'}")
    ck("verified_item_seqs total 1064/22", sum(len(v) for v in vis.values()) == 1064 and len(vis) == 22,
       f"{sum(len(v) for v in vis.values())}/{len(vis)}")

    # 9) 봉인 불변
    ck("published=false", exp["meta"].get("published") is False)
    ck("clinical_reviewed=false", exp["meta"].get("clinical_reviewed") is False)
    djs = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"DATA_URL\s*=\s*'([^']+)'", djs)
    ck("DATA_URL=./data/medistack_v0.2_beta_export.json 불변",
       m and m.group(1) == "./data/medistack_v0.2_beta_export.json", m.group(1) if m else "none")
    ck("requires_clinical_review=true 행 없음(신규)",
       not [r["id"] for r in new if r.get("requires_clinical_review") is True])

    width = max(len(n) for _, n, _ in checks)
    fails = 0
    for ok, name, detail in checks:
        line = ("[PASS] " if ok else "[FAIL] ") + name.ljust(width)
        if not ok and detail:
            line += "  " + detail
        print(line)
        if not ok:
            fails += 1
    print("=" * 64)
    print(f"RESULT: {'PASS' if not fails else 'FAIL'}  ({len(checks)-fails}/{len(checks)} checks passed)")
    print("=" * 64)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
