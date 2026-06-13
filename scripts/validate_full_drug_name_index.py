#!/usr/bin/env python3
"""
validate_full_drug_name_index.py
MediStack v1.0-B Phase 2 — full drug name index 샘플 검증기.

검증 대상: data/full_drug_name_index_sample_v1_0.json
원칙: full index 는 검색 보조이지 의학 정보 아님. relation 없는 약은 name_only(정보 없음)로만.

체크:
  구조/필드   — meta+entries · itemSeq unique · item_name/normalized_item_name non-empty
  enum/타입   — display_mode ∈ {relation_card,name_only} · covered_by_relation boolean · company_name str|null
  일관성      — covered_by_relation ⟺ relation_card · name_only ⟺ no_relation_notice_required=true
  name_only   — relation/nutrient/supplement/product/management 류 필드 금지 · itemSeq ∉ relation-covered pool
                · ingredient 가 13 canonical 성분 미포함(relation 트랙 대상 아님)
  relation_card — itemSeq ∈ relation-covered pool(충돌/날조 없음)
  안전        — 에스오메프라졸/넥시움/forbidden itemSeq 제외 · source_method 화이트리스트
  교차 불변   — alias_count 621 · product 583 · ingredient 38 · verified 545/13 · relation 30
                · DATA_URL 불변 · published/clinical_reviewed false

사용:
  python3 scripts/validate_full_drug_name_index.py [data/full_drug_name_index_sample_v1_0.json]
  python3 scripts/validate_full_drug_name_index.py --selftest   # 음성 테스트(검증기 non-no-op 확인)
종료 코드: 0 PASS, 1 FAIL
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEF_INDEX = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")
ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
RELATIONS_PATH = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

# name_only 에 (substring으로도) 나타나면 안 되는 성분 — 전 품목(단일+복합)이 relation_card 인 13성분.
# ⚠️ v1.1 relation 확장 7성분(라베/판토/란소/덱스란소프라졸·리세드론산·이반드론산·세프디니르)은 여기에
#    포함하지 않는다: **단일성분 품목만** relation_card 로 flip 했고, **복합제는 보수적으로 name_only 유지**
#    (라베+산화Mg/PPI+칼슘/비스포+비타민D 등 nutrient 혼재 카드 혼란 방지)이라 name_only 에 7성분 substring 잔존이
#    정상이다. 복합 통합은 후속 라운드. (relation_card 행은 'itemSeq ∈ pool' 로만 검증되므로 이 목록과 무관.)
CANONICAL_13 = [
    "독시사이클린", "레보티록신", "레보플록사신", "메트포르민", "목시플록사신",
    "미노사이클린", "시프로플록사신", "알렌드론산", "오메프라졸", "오플록사신",
    "토라세미드", "푸로세미드", "히드로클로로티아지드",
]
ESO_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium)", re.IGNORECASE)
FORBIDDEN_ITEMSEQS = {"201600209"}
ALLOWED_SOURCE_METHODS = {"nedrug.searchDrug", "nedrug.getItemDetail", "internal.medistack_v0_3_aliases"}
# name_only 에 있으면 안 되는 의학/제품 필드(있으면 FAIL)
FORBIDDEN_NAMEONLY_FIELDS = {
    "relation", "relations", "nutrient", "nutrients", "supplement", "supplements",
    "interaction", "interactions", "mechanism", "recommended_action", "management",
    "management_ko", "display_text_ko", "evidence_level", "potassium_safety_card",
    "product_links", "product_examples", "products", "affiliate_links", "buy_links",
    "requires_clinical_review", "source_relation_ids",
}
EXPECT_DATA_URL = "./data/medistack_v0.2_beta_export.json"


def build_pool():
    a = json.load(open(ALIAS_PATH, encoding="utf-8"))
    pool = set()
    for lst in (a.get("verified_item_seqs") or {}).values():
        for e in (lst or []):
            s = str(e.get("item_seq") or "").strip()
            if s:
                pool.add(s)
    for p in (a.get("product_aliases") or []):
        s = str(p.get("item_seq") or "").strip()
        if s:
            pool.add(s)
    return pool, a


def load_invariants(alias_data):
    e = json.load(open(RELATIONS_PATH, encoding="utf-8"))
    vis = alias_data.get("verified_item_seqs") or {}
    djs = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"DATA_URL\s*=\s*'([^']+)'", djs)
    return {
        "alias_count": alias_data.get("meta", {}).get("alias_count"),
        "product": len(alias_data.get("product_aliases") or []),
        "ingredient": len(alias_data.get("ingredient_aliases") or []),
        "vis_total": sum(len(v) for v in vis.values()),
        "vis_ing": len(vis),
        "relations": len(e.get("relations") or []),
        "published": e.get("meta", {}).get("published"),
        "clinical_reviewed": e.get("meta", {}).get("clinical_reviewed"),
        "data_url": m.group(1) if m else None,
    }


def validate(doc, pool, inv):
    checks = []

    def ck(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    meta = doc.get("meta")
    entries = doc.get("entries")
    ck("구조: meta(dict)+entries(list)", isinstance(meta, dict) and isinstance(entries, list))
    if not isinstance(entries, list):
        return checks
    entries = [e for e in entries if isinstance(e, dict)]

    seqs = [str(e.get("item_seq") or "").strip() for e in entries]
    ck("itemSeq unique", len(seqs) == len(set(seqs)), f"{len(seqs)} entries, {len(set(seqs))} distinct")
    ck("itemSeq non-empty", all(seqs))
    ck("item_name non-empty", all((e.get("item_name") or "").strip() for e in entries))
    ck("normalized_item_name non-empty", all((e.get("normalized_item_name") or "").strip() for e in entries))
    ck("display_mode ∈ {relation_card,name_only}",
       all(e.get("display_mode") in ("relation_card", "name_only") for e in entries))
    ck("covered_by_relation boolean", all(isinstance(e.get("covered_by_relation"), bool) for e in entries))
    ck("company_name str|null",
       all(e.get("company_name") is None or isinstance(e.get("company_name"), str) for e in entries))
    ck("source/source_method/source_checked_at non-empty",
       all((e.get("source") or "").strip() and (e.get("source_method") or "").strip()
           and (e.get("source_checked_at") or "").strip() for e in entries))
    ck("source_method 화이트리스트",
       all(e.get("source_method") in ALLOWED_SOURCE_METHODS for e in entries))

    # 일관성: covered_by_relation ⟺ display_mode
    ck("covered_by_relation ⟺ relation_card",
       all((e.get("covered_by_relation") is True) == (e.get("display_mode") == "relation_card") for e in entries))

    rc = [e for e in entries if e.get("display_mode") == "relation_card"]
    no = [e for e in entries if e.get("display_mode") == "name_only"]

    ck("name_only → no_relation_notice_required=true",
       all(e.get("no_relation_notice_required") is True for e in no))
    ck("relation_card → no_relation_notice_required=false",
       all(e.get("no_relation_notice_required") in (False, None) for e in rc))

    # name_only: 금지 필드 없음
    bad_fields = [e.get("item_seq") for e in no if FORBIDDEN_NAMEONLY_FIELDS & set(e.keys())]
    ck("name_only: relation/nutrient/product/management 류 필드 금지", not bad_fields,
       f"위반 {bad_fields[:3]}")

    # name_only: 13 canonical 성분 미포함
    bad13 = [e.get("item_seq") for e in no if any(c in (e.get("ingredient_name") or "") for c in CANONICAL_13)]
    ck("name_only: 13 relation 성분 미포함(relation 트랙 아님)", not bad13, f"위반 {bad13[:3]}")

    # name_only: itemSeq ∉ relation-covered pool
    no_in_pool = [e.get("item_seq") for e in no if str(e.get("item_seq")).strip() in pool]
    ck("name_only: itemSeq ∉ relation-covered pool", not no_in_pool, f"위반 {no_in_pool[:3]}")

    # relation_card: itemSeq ∈ pool (충돌/날조 없음)
    rc_off = [e.get("item_seq") for e in rc if str(e.get("item_seq")).strip() not in pool]
    ck("relation_card: itemSeq ∈ relation-covered pool", not rc_off, f"위반 {rc_off[:3]}")

    # 에스오메프라졸/넥시움/forbidden itemSeq 제외
    eso = [e.get("item_seq") for e in entries
           if ESO_RE.search(e.get("item_name") or "") or ESO_RE.search(e.get("ingredient_name") or "")
           or str(e.get("item_seq")).strip() in FORBIDDEN_ITEMSEQS]
    ck("에스오메프라졸/넥시움/forbidden itemSeq 제외", not eso, f"위반 {eso[:3]}")

    # meta.counts 정합
    counts = (meta or {}).get("counts", {})
    ck("meta.counts.total == len(entries)", counts.get("total") == len(entries),
       f"{counts.get('total')} vs {len(entries)}")
    ck("meta.counts.relation_card == 실제", counts.get("relation_card") == len(rc))
    ck("meta.counts.name_only == 실제", counts.get("name_only") == len(no))

    # v1.0 Phase 4 확장 목표(meta.target_total>=5000 일 때만 게이트). 검색 "안 나오는 약" 체감 축소.
    tt = (meta or {}).get("target_total", 0)
    if isinstance(tt, int) and tt >= 5000:
        ck("Phase 4: total >= 5,000 (검색 커버리지 확장)", len(entries) >= 5000, f"total {len(entries)}")
    # v1.0 Phase 5 확장 목표(meta.target_total>=10000 일 때만 게이트). Phase 4 게이트와 동형·조건부.
    if isinstance(tt, int) and tt >= 10000:
        ck("Phase 5: total >= 10,000 (검색 커버리지 확장)", len(entries) >= 10000, f"total {len(entries)}")
    # v1.1 Phase 6 확장 목표(meta.target_total>=20000 일 때만 게이트). Phase 5 게이트와 동형·조건부.
    if isinstance(tt, int) and tt >= 20000:
        ck("Phase 6: total >= 20,000 (검색 커버리지 확장)", len(entries) >= 20000, f"total {len(entries)}")

    # 교차 불변(다른 트랙 회귀 감지)
    ck("불변: alias_count 621", inv["alias_count"] == 621, str(inv["alias_count"]))
    ck("불변: product_aliases 583", inv["product"] == 583, str(inv["product"]))
    ck("불변: ingredient_aliases 38", inv["ingredient"] == 38, str(inv["ingredient"]))
    ck("불변: verified_item_seqs 963/20 (v1.1 relation 확장 +418/+7성분)",
       inv["vis_total"] == 963 and inv["vis_ing"] == 20, f"{inv['vis_total']}/{inv['vis_ing']}")
    ck("불변: relations 41 (v1.1 relation 확장 30→41)", inv["relations"] == 41, str(inv["relations"]))
    ck("불변: DATA_URL", inv["data_url"] == EXPECT_DATA_URL, str(inv["data_url"]))
    ck("불변: published=false", inv["published"] is False, str(inv["published"]))
    ck("불변: clinical_reviewed=false", inv["clinical_reviewed"] is False, str(inv["clinical_reviewed"]))

    return checks


def run_file(path):
    doc = json.load(open(path, encoding="utf-8"))
    pool, alias = build_pool()
    inv = load_invariants(alias)
    checks = validate(doc, pool, inv)
    width = max(len(n) for n, _, _ in checks)
    fails = 0
    for name, ok, detail in checks:
        line = ("[PASS] " if ok else "[FAIL] ") + name.ljust(width)
        if not ok and detail:
            line += "  " + detail
        print(line)
        if not ok:
            fails += 1
    n = len(checks)
    total = doc.get("meta", {}).get("counts", {}).get("total")
    print("=" * 64)
    if total is not None and total < doc.get("meta", {}).get("target_total", 1000):
        print(f"NOTE: total {total} < target {doc['meta'].get('target_total', 1000)} — report 에 사유 필수")
    print(f"RESULT: {'PASS' if not fails else 'FAIL'}  ({n - fails}/{n} checks passed)")
    print("=" * 64)
    return 1 if fails else 0


def selftest():
    """음성 테스트: 정상 doc 을 변조해 각 핵심 체크가 잡는지 확인(non-no-op)."""
    pool, alias = build_pool()
    inv = load_invariants(alias)
    good_seq_rc = next(iter(pool))  # relation-covered pool 의 실제 itemSeq
    base = {
        "meta": {"counts": {"total": 2, "relation_card": 1, "name_only": 1}, "target_total": 1000},
        "entries": [
            {"item_seq": good_seq_rc, "item_name": "테스트정", "normalized_item_name": "테스트정",
             "ingredient_name": "테스트성분", "company_name": None, "covered_by_relation": True,
             "display_mode": "relation_card", "no_relation_notice_required": False,
             "source": "MFDS nedrug", "source_method": "internal.medistack_v0_3_aliases",
             "source_checked_at": "2026-06-12"},
            {"item_seq": "999999001", "item_name": "이름없는약정", "normalized_item_name": "이름없는약정",
             "ingredient_name": "암로디핀", "company_name": None, "covered_by_relation": False,
             "display_mode": "name_only", "no_relation_notice_required": True,
             "source": "MFDS nedrug", "source_method": "nedrug.searchDrug",
             "source_checked_at": "2026-06-12"},
        ],
    }
    import copy

    def fails_on(mut, label):
        d = copy.deepcopy(base)
        mut(d)
        checks = validate(d, pool, inv)
        caught = any(not ok for _, ok, _ in checks)
        print(("[PASS] " if caught else "[FAIL] ") + f"음성: {label} → 검증기 포착={caught}")
        return caught

    def base_clean():
        checks = validate(copy.deepcopy(base), pool, inv)
        bad = [n for n, ok, _ in checks if not ok]
        print(("[PASS] " if not bad else "[FAIL] ") + f"정상 base PASS (위반 {bad})")
        return not bad

    ok = True
    ok &= base_clean()
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("item_seq", d["entries"][0]["item_seq"]), "itemSeq 중복")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("item_name", ""), "item_name 빈값")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("display_mode", "relation_card"), "name_only인데 covered=false 불일치")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("no_relation_notice_required", False), "name_only notice=false")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("mechanism", "absorption"), "name_only 금지필드(mechanism)")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("ingredient_name", "메트포르민"), "name_only 13성분 포함")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("item_seq", next(iter(pool))), "name_only itemSeq∈pool")
    ok &= fails_on(lambda d: d["entries"][0].__setitem__("item_seq", "999999777"), "relation_card itemSeq∉pool")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("item_name", "넥시움정"), "에스오메(넥시움) 미제외")
    ok &= fails_on(lambda d: d["entries"][1].__setitem__("source_method", "made.up"), "source_method 비화이트리스트")
    print("=" * 64)
    print(f"SELFTEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    sys.exit(run_file(sys.argv[1] if len(sys.argv) > 1 else DEF_INDEX))
