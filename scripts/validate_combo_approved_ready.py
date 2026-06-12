#!/usr/bin/env python3
"""
validate_combo_approved_ready.py
MediStack v0.7 G3 — 복합제(combo) approved-ready 파일 검증기.

confirm_nedrug_item_details.py --combo 가 만든 combo approved-ready 파일을 CMB 규칙으로 검증한다.
이 파일은 아직 alias JSON 에 반영되지 않은 후보 풀(approved_ready=true·incorporated=false)이며,
반영(G4) 전 안전 게이트다. relations export 로 'relation 보유 성분 정확히 1개' 를 직접 재도출한다.

CMB 규칙(코드 강제):
  #1 파일 shape(meta + approved_ready 리스트)
  #2 항목 필수 필드/타입
  #3 is_combination===true(bool) AND ingr_name 에 '/'(실제 복합제)
  #4 ingr_name 구성 중 relation 보유 성분 정확히 1개 AND == combination_basis_ingredient
  #5 combination_basis_ingredient == canonical_ingredient
  #6 basis ∈ {메트포르민,알렌드론산,오메프라졸} (히드로클로로티아지드·에스오메프라졸 하드 차단)
  #7 combination_notice_required===true
  #8 item_seq 숫자형·forbidden 아님·전역 중복 0
  #9 ingr_name/item_name 에 에스오메프라졸/넥시움 신호 금지
  #10 approved_ready===true AND incorporated ∈ {false,true}(옵션 A: 반영 전/후 정합)
  #11 incorporated===true → alias JSON 에 실제 반영(item_seq→is_combination product alias·basis 일치)

사용: python3 validate_combo_approved_ready.py <combo_ar.json> [relations_export.json] [aliases.json]
종료 코드: 0 PASS, 1 FAIL
"""
import sys
import json
import re

DEFAULT_RELATIONS_PATH = "data/medistack_v0.2_beta_export.json"
DEFAULT_ALIAS_PATH = "data/medistack_v0.3_aliases.json"
COMBO_ALLOWED_BASIS = {"메트포르민", "알렌드론산", "오메프라졸"}
FORBIDDEN_ITEMSEQS = {"201600209"}
ESO_HINT_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium)", re.IGNORECASE)
NUMERIC_RE = re.compile(r"^\d+$")
REQUIRED = ["candidate_alias", "canonical_ingredient", "item_seq", "ingr_name",
            "is_combination", "combination_basis_ingredient", "combination_notice_required"]


class V:
    def __init__(self):
        self.fails, self.passes = [], []
    def check(self, ok, no, title, detail=""):
        (self.passes if ok else self.fails).append((no, title) if ok else (no, title, detail))
        return ok


def nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def load(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FATAL] {label} 로드 실패: {path}: {e}")
        sys.exit(1)


def relation_ings(rdata):
    return sorted({r.get("ingredient") for r in (rdata.get("relations") or []) if r.get("ingredient")})


def matched_relation_ings(ingr_name, rel_ings):
    comps = [p.strip() for p in str(ingr_name or "").split("/") if p.strip()]
    return sorted({ri for ri in rel_ings if any(ri in comp for comp in comps)})


def main(ar_path, rel_path, alias_path=None):
    v = V()
    ardata = load(ar_path, "combo_ar")
    rdata = load(rel_path, "relations")
    alias_data = load(alias_path, "alias") if alias_path else None
    rel_ings = relation_ings(rdata)

    entries = ardata.get("approved_ready") if isinstance(ardata, dict) else None
    v.check(isinstance(ardata, dict) and isinstance(entries, list), 1,
            "파일 shape(meta + approved_ready 리스트)",
            f"type={type(entries).__name__}")
    if not isinstance(entries, list):
        entries = []

    # 2) 항목 필수 필드/타입
    bad = []
    for e in entries:
        if not isinstance(e, dict):
            bad.append("non-dict"); continue
        for k in REQUIRED:
            if k not in e:
                bad.append(f"{e.get('candidate_alias')!r}:missing {k}")
    v.check(not bad, 2, "항목 필수 필드 보유", f"viol={bad[:8]}")

    ents = [e for e in entries if isinstance(e, dict)]

    # 3) is_combination true(bool) + ingr_name '/'
    c3 = [f"{e.get('candidate_alias')!r}" for e in ents
          if e.get("is_combination") is not True or "/" not in str(e.get("ingr_name") or "")]
    v.check(not c3, 3, "is_combination===true(bool) AND ingr_name 에 '/'", f"viol={c3[:8]}")

    # 4) relation 보유 성분 정확히 1개 AND == basis
    c4 = []
    for e in ents:
        m = matched_relation_ings(e.get("ingr_name"), rel_ings)
        if len(m) != 1 or m[0] != e.get("combination_basis_ingredient"):
            c4.append(f"{e.get('candidate_alias')!r}:matched={m}")
    v.check(not c4, 4, "relation 보유 성분 정확히 1개 AND == basis", f"viol={c4[:8]}")

    # 5) basis == canonical
    c5 = [f"{e.get('candidate_alias')!r}:{e.get('combination_basis_ingredient')}!={e.get('canonical_ingredient')}"
          for e in ents if e.get("combination_basis_ingredient") != e.get("canonical_ingredient")]
    v.check(not c5, 5, "combination_basis_ingredient == canonical_ingredient", f"viol={c5[:8]}")

    # 6) basis allowlist (HCTZ·에스오메프라졸 하드 차단)
    c6 = [f"{e.get('candidate_alias')!r}:{e.get('combination_basis_ingredient')!r}"
          for e in ents if e.get("combination_basis_ingredient") not in COMBO_ALLOWED_BASIS]
    v.check(not c6, 6, f"basis ∈ {sorted(COMBO_ALLOWED_BASIS)}(HCTZ·에스오메프라졸 차단)", f"viol={c6[:8]}")

    # 7) combination_notice_required === true
    c7 = [f"{e.get('candidate_alias')!r}" for e in ents if e.get("combination_notice_required") is not True]
    v.check(not c7, 7, "combination_notice_required===true", f"viol={c7[:8]}")

    # 8) item_seq 숫자형·forbidden 아님·전역 중복 0
    c8, seen = [], {}
    for e in ents:
        seq = str(e.get("item_seq") or "").strip()
        if not seq or not NUMERIC_RE.match(seq):
            c8.append(f"{e.get('candidate_alias')!r}:item_seq={seq!r}(비숫자)")
        elif seq in FORBIDDEN_ITEMSEQS:
            c8.append(f"{e.get('candidate_alias')!r}:forbidden {seq}")
        else:
            seen[seq] = seen.get(seq, 0) + 1
    c8 += [f"dup item_seq {s}" for s, n in seen.items() if n > 1]
    v.check(not c8, 8, "item_seq 숫자형·forbidden 아님·전역 중복 0", f"viol={c8[:8]}")

    # 9) 에스오메프라졸/넥시움 신호 금지
    c9 = [f"{e.get('candidate_alias')!r}" for e in ents
          if ESO_HINT_RE.search(str(e.get("ingr_name") or "")) or ESO_HINT_RE.search(str(e.get("item_name") or ""))]
    v.check(not c9, 9, "ingr_name/item_name 에 에스오메프라졸/넥시움 금지", f"viol={c9[:8]}")

    # 10) approved_ready===true AND incorporated ∈ {false,true} (옵션 A: 반영 전/후 모두 정합)
    c10 = [f"{e.get('candidate_alias')!r}" for e in ents
           if e.get("approved_ready") is not True or e.get("incorporated") not in (False, True)]
    v.check(not c10, 10, "approved_ready===true AND incorporated ∈ {false,true}", f"viol={c10[:8]}")

    # 11) incorporated===true → alias JSON 에 실제 반영(item_seq→is_combination product alias·basis 일치). 옵션 A.
    c11 = []
    if alias_data is not None:
        seq_combo = {}
        for p in (alias_data.get("product_aliases") or []):
            if p.get("is_combination") is True and str(p.get("item_seq") or "").strip():
                seq_combo[str(p["item_seq"]).strip()] = p
        for e in ents:
            if e.get("incorporated") is True:
                p = seq_combo.get(str(e.get("item_seq") or "").strip())
                if not p:
                    c11.append(f"{e.get('candidate_alias')!r}:alias 미반영")
                elif p.get("combination_basis_ingredient") != e.get("combination_basis_ingredient"):
                    c11.append(f"{e.get('candidate_alias')!r}:basis 불일치")
    v.check(not c11, 11, "incorporated=true → alias JSON 실제 반영(is_combination·basis 일치)", f"viol={c11[:8]}")

    total = len(v.passes) + len(v.fails)
    overall = "PASS" if not v.fails else "FAIL"
    bar = "=" * 64
    print(bar); print(f"MediStack v0.7 combo approved-ready 검증: {ar_path}"); print(bar)
    if v.fails:
        print(f"\n[FAIL] {len(v.fails)}건")
        for no, title, detail in sorted(v.fails):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print(f"\n모든 검증 통과. (combo 항목 {len(ents)}건)")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)"); print(bar)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "data/candidates/bulk_alias_approved_ready_combo_v0_7.json"
    r = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_RELATIONS_PATH
    al = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_ALIAS_PATH
    sys.exit(main(a, r, al))
