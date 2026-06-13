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
  - (v0.4 유형 B) verified_item_seqs 화이트리스트: 동일 성분의 검증된 2번째 itemSeq 만 #8 허용집합에 추가.
    성분 키는 라이브 실재 + excluded·에스오메프라졸 금지(#12), 엔트리는 숫자형 itemSeq·중복·필드 위생(#13).
    섹션 부재 시 빈 집합 → 기존(relation 인용분만) 동작과 동일(하위호환).
  - (v0.7 복합제 tier + v0.8 HCTZ) 복합제 alias 라이브 가드: is_combination=true 인 product alias 는 고지 메타가 정합해야 하고
    (#14: product 한정·basis==canonical·notice_required=true·orphan 고지필드 금지), basis 성분은 허용 allowlist
    안이어야 한다(#15: 메트포르민/알렌드론산/오메프라졸/히드로클로로티아지드 — v0.8 HCTZ 개방·에스오메프라졸 하드 차단).
    복합제 alias 표시 문자열에 칼륨보존이뇨제 토큰 금지(#16: K보존 파트너 영구차단·염이름 '칼륨'은 미매칭).
    복합제 entry 부재 시 세 검사 모두 빈 집합 → 기존 동작과 동일(하위호환).

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
# v0.7 B1 + v0.8 H-G1 복합제 basis allowlist: 이 성분들만 복합제 basis 로 허용.
# v0.8: 히드로클로로티아지드(HCTZ) 개방(ARB+HCTZ 고혈압 복합제). 에스오메프라졸은 계속 하드 차단.
# v1.1 복합제검토 1순위: 라베프라졸 개방(B 라베+탄산수소나트륨·D 라베+아스피린, nutrient 무관 35건).
#       라베+산화Mg(E)·라베+칼슘(C)·비스포+D3(A) 는 미개방(직접모순/미수록 상호작용 — 로드맵 2·3순위·영구금지).
COMBO_ALLOWED_BASIS = {"메트포르민", "알렌드론산", "오메프라졸", "히드로클로로티아지드", "라베프라졸"}
# v0.8 H-G1(#16): 라이브 복합제 alias 표시 문자열에 칼륨보존이뇨제 토큰 금지(K보존 파트너 영구차단).
# 특정 약물명 토큰만 → 'XX칼륨'(로사르탄칼륨/피마사르탄칼륨) 염 이름의 '칼륨'은 매칭 안 됨(V5 염이름 분리).
KSPARING_RE = re.compile(
    r"(트리암테렌|아밀로라이드|아밀로리드|스피로노락톤|에플레레논|칸레논|"
    r"triamterene|amiloride|spironolactone|eplerenone|canrenone)", re.IGNORECASE)
# 제품/제휴 의심 필드명(전면 금지). item_seq/source_relation_ids 는 추적 메타라 허용.
PRODUCT_FIELD_HINT = re.compile(r"(affiliate|shop|buy|store|purchase|cart|price|link|coupon|deal)", re.IGNORECASE)
ITEMSEQ_RE = re.compile(r"itemSeq=(\d+)")
NUMERIC_RE = re.compile(r"^\d+$")  # item_seq 는 숫자 문자열만 (식약처 itemSeq)


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

    # --- v0.4 유형 B: 검증된 교차확인 itemSeq 화이트리스트 ---
    # verified_item_seqs: { canonical_ingredient: [ {item_seq, item_name, verified_at, method}, ... ] }
    # relation 원문이 인용한 대표 itemSeq 1개 외에, 동일 성분의 검증된 2번째 품목 itemSeq 를 #8 허용집합에 추가.
    # 섹션 부재 시 빈 화이트리스트 → #8 동작은 기존(relation 인용분만)과 동일(하위호환).
    # 정당성(#12)/위생(#13)을 통과한 itemSeq 만 #8 union 에 등록(부정 화이트리스트가 #8 우회 못 함).
    wl_raw = adata.get("verified_item_seqs", {})
    ing_to_wl_seqs = {}   # ing -> set(item_seq), #8 union 용(검증 통과분만)
    wl_bad_ing = []       # #12 위반 누적
    wl_bad_entry = []     # #13 위반 누적
    if not isinstance(wl_raw, dict):
        wl_bad_ing.append(f"verified_item_seqs!=object({type(wl_raw).__name__})")
        wl_raw = {}
    for ing, lst in wl_raw.items():
        ing_ok = True
        if ing == EXCLUDED_BYPASS_INGREDIENT:
            wl_bad_ing.append(f"{ing!r}:에스오메프라졸-금지(15행 우회)"); ing_ok = False
        elif ing in excluded_only_ings:
            wl_bad_ing.append(f"{ing!r}:excluded-only-매핑금지"); ing_ok = False
        elif not nonempty_str(ing) or ing not in live_ings:
            wl_bad_ing.append(f"{ing!r}:비라이브성분(신규 relation 금지)"); ing_ok = False
        if not isinstance(lst, list):
            wl_bad_entry.append(f"{ing!r}:entries!=list"); continue
        seen_seq = set()
        for ent in lst:
            if not isinstance(ent, dict):
                wl_bad_entry.append(f"{ing!r}:entry!=object"); continue
            seq = ent.get("item_seq")
            if not nonempty_str(seq) or not NUMERIC_RE.match(seq.strip()):
                wl_bad_entry.append(f"{ing!r}:item_seq={seq!r}(숫자형 아님)")
            else:
                s = seq.strip()
                if s in seen_seq:
                    wl_bad_entry.append(f"{ing!r}:item_seq={s}(성분내 중복)")
                seen_seq.add(s)
                if ing_ok:
                    ing_to_wl_seqs.setdefault(ing, set()).add(s)
            for k in ent.keys():
                if PRODUCT_FIELD_HINT.search(k):
                    wl_bad_entry.append(f"{ing!r}:'{k}'(제품/구매 필드 금지)")

    # 8) product alias: item_seq ∈ (해당 성분 relation itemSeq ∪ 검증 화이트리스트 itemSeq)
    seq_bad = []
    for _, e in dict_entries:
        if e.get("kind") != "product":
            continue
        ci = e.get("canonical_ingredient")
        seq = e.get("item_seq")
        valid_seqs = ing_to_seqs.get(ci, set()) | ing_to_wl_seqs.get(ci, set())
        if not nonempty_str(seq) or seq not in valid_seqs:
            seq_bad.append(f"{e.get('alias')!r}:item_seq={seq} (성분 {ci} 유효={sorted(valid_seqs)})")
    v.check(not seq_bad, 8, "product alias item_seq ∈ 성분 relation itemSeq ∪ 검증 화이트리스트", f"viol={seq_bad}")

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

    # 12) verified_item_seqs 성분 키 정당성: 라이브 relation 성분 실재 + excluded·에스오메프라졸 금지
    #     (화이트리스트가 신규 relation/봉인 항목으로 우회 연결되는 것을 차단)
    v.check(not wl_bad_ing, 12,
            "verified_item_seqs 성분 키 라이브 실재(excluded·에스오메프라졸 금지)", f"viol={wl_bad_ing}")
    # 13) verified_item_seqs 엔트리 위생: item_seq 숫자형 + 성분내 중복 금지 + 제품/구매/제휴 필드 금지
    v.check(not wl_bad_entry, 13,
            "verified_item_seqs 엔트리 위생(item_seq 형식·중복·금지필드)", f"viol={wl_bad_entry}")

    # --- v0.7 복합제(combo) tier 라이브 가드 ---
    # 복합제 alias 는 product 한정 + 고지 메타(is_combination/basis/notice_required) 정합 필요.
    # 복합제 entry 부재 시 빈 집합 → 기존 동작과 동일(하위호환).
    # 14) is_combination 메타 정합성
    combo_bad = []
    for src, e in dict_entries:
        isc = e.get("is_combination")
        basis = e.get("combination_basis_ingredient")
        notice = e.get("combination_notice_required")
        if isc is True:
            if src != "product_aliases" or e.get("kind") != "product":
                combo_bad.append(f"{e.get('alias')!r}:복합제는 product alias만")
            if not nonempty_str(basis):
                combo_bad.append(f"{e.get('alias')!r}:combination_basis_ingredient 누락")
            elif basis != e.get("canonical_ingredient"):
                combo_bad.append(f"{e.get('alias')!r}:basis({basis})!=canonical({e.get('canonical_ingredient')})")
            if notice is not True:
                combo_bad.append(f"{e.get('alias')!r}:combination_notice_required!=true")
        else:
            if isc not in (None, False):
                combo_bad.append(f"{e.get('alias')!r}:is_combination={isc!r}(bool 아님)")
            if notice is True or nonempty_str(basis):
                combo_bad.append(f"{e.get('alias')!r}:비복합제인데 복합제 고지필드 존재(orphan)")
    v.check(not combo_bad, 14,
            "is_combination 메타 정합(product 한정·basis==canonical·notice_required=true·orphan 금지)",
            f"viol={combo_bad}")

    # 15) 복합제 basis 성분 allowlist(히드로클로로티아지드·에스오메프라졸·범위밖 하드 차단)
    combo_basis_bad = []
    for _, e in dict_entries:
        if e.get("is_combination") is True:
            basis = e.get("combination_basis_ingredient")
            if basis not in COMBO_ALLOWED_BASIS:
                combo_basis_bad.append(f"{e.get('alias')!r}:basis={basis!r}(allowlist 외 차단)")
    v.check(not combo_basis_bad, 15,
            f"복합제 basis ∈ {sorted(COMBO_ALLOWED_BASIS)}(v0.8 HCTZ 개방·에스오메프라졸 하드 차단)",
            f"viol={combo_basis_bad}")

    # 16) (v0.8 H-G1) 복합제 alias 표시 문자열에 칼륨보존이뇨제 토큰 금지(K보존 파트너 영구차단).
    #     라이브 combo alias 에는 ingr_name 이 없어 표시 문자열(alias)로 방어. 'XX칼륨' 염이름은 미매칭(V5).
    kspare_bad = []
    for _, e in dict_entries:
        if e.get("is_combination") is True and KSPARING_RE.search(str(e.get("alias") or "")):
            kspare_bad.append(f"{e.get('alias')!r}")
    v.check(not kspare_bad, 16,
            "복합제 alias 칼륨보존이뇨제 토큰 금지(트리암테렌/아밀로라이드/스피로노락톤/에플레레논/칸레논)",
            f"viol={kspare_bad}")

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
