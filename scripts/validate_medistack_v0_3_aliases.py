#!/usr/bin/env python3
"""
validate_medistack_v0_3_aliases.py
MediStack v0.3 검색 alias 데이터 검증기. (relations export 검증기와 분리)

alias = 검색 보조 인덱스. 새 의학정보 아님. alias 만으로 relation 신규생성 불가.
정책을 코드로 강제:
  - alias 는 존재하는(라이브) relation/ingredient 에만 연결.
  - excluded_v0_1(=15행 에스오메프라졸×B12) 연결 금지. relation_id 15 연결 금지.
  - 에스오메프라졸 제품 alias 금지(15행 우회 가드).
  - alias 중복 금지 / 빈 alias 금지.
  - 제품/구매/제휴 필드 금지(검색 보조만, 제품 UI 데이터 없음).
  - nutrient(영양소) 로 매핑되는 alias 금지(제품추천 오인 방지).

사용:
    python3 validate_medistack_v0_3_aliases.py <aliases.json> [relations_export.json]
종료 코드: 0 = PASS, 1 = FAIL
"""
import sys
import json
import re

DEFAULT_ALIAS_PATH = "medistack_v0.3_aliases.sample.json"
DEFAULT_RELATIONS_PATH = "data/medistack_v0.2_beta_export.json"

ALLOWED_KIND = {"product", "ingredient"}
FORBIDDEN_RELATION_ID = 15  # excluded_v0_1 (에스오메프라졸×B12)
EXCLUDED_BYPASS_INGREDIENT = "에스오메프라졸"  # 제품 alias 금지 대상(15행 관련)
# 제품/제휴 의심 필드명(전면 금지). item_seq/source_relation_ids 는 추적 메타라 허용.
PRODUCT_FIELD_HINT = re.compile(r"(affiliate|shop|buy|store|purchase|cart|price|link|coupon|deal)", re.IGNORECASE)
ITEMSEQ_RE = re.compile(r"itemSeq=(\d+)")


class V:
    def __init__(self):
        self.fails = []
        self.passes = []
    def check(self, ok, no, title, detail=""):
        (self.passes if ok else self.fails).append((no, title) if ok else (no, title, detail))
        return ok


def nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def load_json(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"[FATAL] {label} 파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"[FATAL] {label} JSON 파싱 실패: {e}"


def build_relation_index(rel_data):
    """라이브 relations 에서 검증에 쓸 인덱스 구축.
    returns: live_ids(set), id_to_ingredient(dict), live_ingredients(set),
             ingredient_to_itemseqs(dict), excluded_ids(set), excluded_ingredients(set)
    """
    rels = rel_data.get("relations") or []
    excl = rel_data.get("excluded_v0_1") or []
    live_ids, id_to_ing, live_ings, ing_to_seqs = set(), {}, set(), {}
    for r in rels:
        if not isinstance(r, dict):
            continue
        rid = r.get("id")
        ing = r.get("ingredient")
        live_ids.add(rid)
        if nonempty_str(ing):
            live_ings.add(ing)
            id_to_ing[rid] = ing
            url = (r.get("source") or {}).get("url", "")
            m = ITEMSEQ_RE.search(url or "")
            if m:
                ing_to_seqs.setdefault(ing, set()).add(m.group(1))
    excl_ids = {e.get("id") for e in excl if isinstance(e, dict)}
    excl_ings = {e.get("ingredient") for e in excl if isinstance(e, dict) and nonempty_str(e.get("ingredient"))}
    return live_ids, id_to_ing, live_ings, ing_to_seqs, excl_ids, excl_ings


def main(alias_path, rel_path):
    v = V()
    adata, err = load_json(alias_path, "alias")
    if err:
        print(err); return 1
    rdata, err = load_json(rel_path, "relations")
    if err:
        print(err); return 1
    if not isinstance(adata, dict):
        print("[FATAL] alias 최상위가 객체 아님"); return 1

    live_ids, id_to_ing, live_ings, ing_to_seqs, excl_ids, excl_ings = build_relation_index(rdata)
    # excluded 전용 성분(라이브에 전혀 없는) = 절대 매핑 불가
    excluded_only_ings = excl_ings - live_ings

    ing_aliases = adata.get("ingredient_aliases")
    prod_aliases = adata.get("product_aliases")
    ing_ok = isinstance(ing_aliases, list)
    prod_ok = isinstance(prod_aliases, list)

    # 1) 구조: 두 리스트 존재
    tp = []
    if not ing_ok: tp.append("ingredient_aliases!=list")
    if not prod_ok: tp.append("product_aliases!=list")
    v.check(not tp, 1, "alias 구조(ingredient_aliases/product_aliases 리스트)", "; ".join(tp))

    entries = []
    if ing_ok: entries += [("ingredient_aliases", e) for e in ing_aliases]
    if prod_ok: entries += [("product_aliases", e) for e in prod_aliases]

    # 2) 각 항목 dict + 빈 alias 금지 + kind 유효
    bad_struct, empty_alias, bad_kind = [], [], []
    for src, e in entries:
        if not isinstance(e, dict):
            bad_struct.append(src); continue
        if not nonempty_str(e.get("alias")):
            empty_alias.append(repr(e.get("alias")))
        k = e.get("kind")
        if k not in ALLOWED_KIND:
            bad_kind.append(f"{e.get('alias')!r}:{k}")
    v.check(not bad_struct and not empty_alias and not bad_kind, 2,
            "항목 구조/빈 alias 금지/kind∈{product,ingredient}",
            f"non_dict={bad_struct} empty={empty_alias} bad_kind={bad_kind}")

    dict_entries = [(src, e) for src, e in entries if isinstance(e, dict)]

    # 3) alias 중복 금지(정규화: strip + lower)
    norm = {}
    for _, e in dict_entries:
        a = e.get("alias")
        if not nonempty_str(a):
            continue
        key = a.strip().lower()
        norm.setdefault(key, 0)
        norm[key] += 1
    dups = sorted([k for k, c in norm.items() if c > 1])
    v.check(not dups, 3, "alias 중복 금지(정규화 strip+lower)", f"dup={dups}")

    # 4) canonical_ingredient 가 라이브 relation 성분에 실재 (alias 만으로 신규 relation 금지)
    ghost = []
    for _, e in dict_entries:
        ci = e.get("canonical_ingredient")
        if not nonempty_str(ci) or ci not in live_ings:
            ghost.append(f"{e.get('alias')!r}->{ci!r}")
    v.check(not ghost, 4, "canonical_ingredient 라이브 relation 성분에 실재(신규 relation 금지)", f"ghost={ghost}")

    # 5) excluded 전용 성분 매핑 금지 + excluded 성분(에스오메프라졸 등) 우회 가드
    excl_map = []
    for _, e in dict_entries:
        ci = e.get("canonical_ingredient")
        if ci in excluded_only_ings:
            excl_map.append(f"{e.get('alias')!r}->{ci!r}(excluded-only)")
    v.check(not excl_map, 5, "excluded_v0_1 전용 성분 매핑 금지", f"viol={excl_map}")

    # 6) relation_id 15 연결 금지 + source_relation_ids ⊆ 라이브 id (excluded 연결 금지)
    bad_rid, rid15 = [], []
    for _, e in dict_entries:
        srids = e.get("source_relation_ids")
        if srids is None:
            continue
        if not isinstance(srids, list):
            bad_rid.append(f"{e.get('alias')!r}:not-list"); continue
        for rid in srids:
            if rid == FORBIDDEN_RELATION_ID or rid in excl_ids:
                rid15.append(f"{e.get('alias')!r}:id{rid}")
            elif rid not in live_ids:
                bad_rid.append(f"{e.get('alias')!r}:id{rid}(없음)")
    v.check(not bad_rid and not rid15, 6,
            f"source_relation_ids 라이브 id에만(15·excluded 연결 금지)",
            f"unknown={bad_rid} excluded={rid15}")

    # 7) source_relation_ids 의 relation.ingredient == canonical_ingredient (정합성)
    mism = []
    for _, e in dict_entries:
        ci = e.get("canonical_ingredient")
        for rid in (e.get("source_relation_ids") or []):
            ing = id_to_ing.get(rid)
            if ing is not None and ing != ci:
                mism.append(f"{e.get('alias')!r}:id{rid}({ing}!={ci})")
    v.check(not mism, 7, "source_relation_ids 의 relation 성분 == canonical_ingredient", f"mismatch={mism}")

    # 8) product alias: item_seq 가 해당 성분 relation 의 itemSeq 집합에 속함
    seq_bad = []
    for _, e in dict_entries:
        if e.get("kind") != "product":
            continue
        ci = e.get("canonical_ingredient")
        seq = e.get("item_seq")
        valid_seqs = ing_to_seqs.get(ci, set())
        if not nonempty_str(seq) or seq not in valid_seqs:
            seq_bad.append(f"{e.get('alias')!r}:item_seq={seq} (성분 {ci} 유효={sorted(valid_seqs)})")
    v.check(not seq_bad, 8, "product alias item_seq 가 해당 성분 relation itemSeq 에 속함", f"viol={seq_bad}")

    # 9) 에스오메프라졸 제품 alias 금지(15행 우회 가드)
    eso = [f"{e.get('alias')!r}" for _, e in dict_entries
           if e.get("kind") == "product" and e.get("canonical_ingredient") == EXCLUDED_BYPASS_INGREDIENT]
    v.check(not eso, 9, f"{EXCLUDED_BYPASS_INGREDIENT} 제품 alias 금지(15행 우회 가드)", f"viol={eso}")

    # 10) 제품/구매/제휴 필드 금지(필드명 기준; item_seq/source_relation_ids 는 허용 메타)
    field_viol = []
    for _, e in dict_entries:
        for k, val in e.items():
            if PRODUCT_FIELD_HINT.search(k):
                field_viol.append(f"{e.get('alias')!r}:'{k}'")
    v.check(not field_viol, 10, "제품/구매/제휴 필드 금지(affiliate/buy/price/link/...)", f"viol={field_viol}")

    # 11) nutrient(영양소) 매핑 금지: canonical_ingredient 가 어느 relation 의 nutrient 와 같으면 안 됨
    nutrients = {r.get("nutrient") for r in (rdata.get("relations") or []) if isinstance(r, dict)}
    nut_viol = [f"{e.get('alias')!r}->{e.get('canonical_ingredient')!r}"
                for _, e in dict_entries
                if e.get("canonical_ingredient") in nutrients and e.get("canonical_ingredient") not in live_ings]
    v.check(not nut_viol, 11, "nutrient(영양소) 매핑 alias 금지", f"viol={nut_viol}")

    total = len(v.passes) + len(v.fails)
    overall = "PASS" if not v.fails else "FAIL"
    bar = "=" * 64
    print(bar); print(f"MediStack v0.3 alias 검증: {alias_path}"); print(f"  (relations 기준: {rel_path})"); print(bar)
    if v.fails:
        print(f"\n[FAIL] {len(v.fails)}건")
        for no, title, detail in sorted(v.fails):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print("\n모든 검증 통과.")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)"); print(bar)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ALIAS_PATH
    r = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_RELATIONS_PATH
    sys.exit(main(a, r))
