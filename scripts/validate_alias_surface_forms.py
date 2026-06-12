#!/usr/bin/env python3
"""
validate_alias_surface_forms.py
MediStack v0.9 — alias 표면형(surface form) 위생 검증기.

라이브 검색 alias 의 검색/표시 문자열(alias, item_name)과 매핑 키(canonical_ingredient,
verified_item_seqs 성분 키)에 lookup 을 깨뜨리는 표면형 이상이 없는지 검사한다.
표면형 문자열만 검사하며 의미/매핑/개수는 읽지도 바꾸지도 않는다(읽기 전용 검증).

탐지 이상(개행/제어/공백 위생):
  - 개행(\\n) / 캐리지리턴(\\r) / 탭(\\t)
  - 기타 C0/C1 제어문자
  - 앞뒤 공백(leading/trailing whitespace)
  - 연속 공백 2칸 이상(multiple consecutive spaces)
  - 제로폭 문자(zero-width: U+200B~200D, U+FEFF)
  - 비분리/유니코드 공백(NBSP U+00A0, U+3000 등)

배경: 검색 인덱스(guards.js norm = NFC + trim + lower)는 앞뒤 공백만 제거하고
내부 개행/탭/다중공백/제로폭은 보존하므로, 이런 표면형이 alias 에 섞이면 해당 alias 가
사실상 검색 불가가 된다(2026-06 v0.5 '신일모노독시엠캡슐\\n(...)' nedrug 개행 사례).
이 검증기는 그런 표면형이 라이브 alias 에 유입되는 것을 영구 차단한다(v0.9 표면형 정제 트랙).
버전 비종속(개수 하드코딩 없음) → 이후 버전에서도 그대로 게이트로 쓸 수 있다.

사용:
    python3 validate_alias_surface_forms.py <aliases.json>
종료 코드: 0 = PASS, 1 = FAIL
"""
import sys
import json
import re

DEFAULT_ALIAS_PATH = "data/medistack_v0.3_aliases.json"

# 표면형 이상 탐지 규칙 (일반 ASCII space U+0020 단일은 정상)
_NEWLINE = re.compile(r"[\r\n]")
_TAB = re.compile(r"\t")
_MULTISPACE = re.compile(r"  +")  # ASCII space 2칸 이상
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")  # \t,\n,\r 제외 제어문자
_ZEROWIDTH = re.compile("[​‌‍﻿]")
_UNISPACE = re.compile("[   -     　]")


def surface_anomalies(s):
    """문자열의 표면형 이상 태그 리스트(없으면 빈 리스트). 비문자열은 빈 리스트."""
    if not isinstance(s, str):
        return []
    out = []
    if _NEWLINE.search(s): out.append("NEWLINE")
    if _TAB.search(s): out.append("TAB")
    if _CTRL.search(s): out.append("CTRL")
    if s != s.strip(): out.append("LEAD/TRAIL")
    if _MULTISPACE.search(s): out.append("MULTISPACE")
    if _ZEROWIDTH.search(s): out.append("ZEROWIDTH")
    if _UNISPACE.search(s): out.append("UNISPACE")
    return out


class V:
    def __init__(self):
        self.fails = []
        self.passes = []
    def check(self, ok, no, title, detail=""):
        (self.passes if ok else self.fails).append((no, title) if ok else (no, title, detail))
        return ok


def load_json(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"[FATAL] {label} 파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"[FATAL] {label} JSON 파싱 실패: {e}"


def _scan_list_field(items, field, label, cap=15):
    """리스트 items 각 dict 의 field 표면형 검사 → (표본 위반리스트, 총 위반수)."""
    viol = []
    for i, e in enumerate(items if isinstance(items, list) else []):
        if not isinstance(e, dict):
            continue
        tags = surface_anomalies(e.get(field))
        if tags:
            viol.append(f"{label}[{i}].{field} {tags} {e.get(field)!r}")
    return viol[:cap], len(viol)


def main(alias_path):
    data, err = load_json(alias_path, "alias")
    if err:
        print(err)
        return 1
    v = V()

    ia = data.get("ingredient_aliases")
    pa = data.get("product_aliases")
    vis = data.get("verified_item_seqs")

    # #1 구조
    struct_ok = isinstance(ia, list) and isinstance(pa, list) and isinstance(vis, dict)
    v.check(struct_ok, 1,
            "구조(ingredient_aliases/product_aliases 리스트 + verified_item_seqs 딕셔너리)",
            "" if struct_ok else f"types={type(ia).__name__}/{type(pa).__name__}/{type(vis).__name__}")
    ia = ia if isinstance(ia, list) else []
    pa = pa if isinstance(pa, list) else []
    vis = vis if isinstance(vis, dict) else {}

    # #2 ingredient_aliases.alias 표면형
    s, n = _scan_list_field(ia, "alias", "ingredient_aliases")
    v.check(n == 0, 2, "ingredient_aliases.alias 표면형 위생(개행/탭/제어/앞뒤·다중공백/제로폭 금지)",
            f"viol={n} {s}" if n else "")

    # #3 product_aliases.alias 표면형
    s, n = _scan_list_field(pa, "alias", "product_aliases")
    v.check(n == 0, 3, "product_aliases.alias 표면형 위생(개행/탭/제어/앞뒤·다중공백/제로폭 금지)",
            f"viol={n} {s}" if n else "")

    # #4 verified_item_seqs[*][].item_name 표면형
    vi_viol = []
    for canon, entries in vis.items():
        for j, e in enumerate(entries if isinstance(entries, list) else []):
            if not isinstance(e, dict):
                continue
            tags = surface_anomalies(e.get("item_name"))
            if tags:
                vi_viol.append(f"verified_item_seqs[{canon!r}][{j}].item_name {tags} {e.get('item_name')!r}")
    v.check(not vi_viol, 4, "verified_item_seqs.item_name 표면형 위생",
            f"viol={len(vi_viol)} {vi_viol[:15]}" if vi_viol else "")

    # #5 매핑 키 표면형(canonical_ingredient + verified 성분 키): 깨지면 lookup 키가 어긋남
    map_viol = []
    for label, items in (("ingredient_aliases", ia), ("product_aliases", pa)):
        for i, e in enumerate(items):
            if not isinstance(e, dict):
                continue
            tags = surface_anomalies(e.get("canonical_ingredient"))
            if tags:
                map_viol.append(f"{label}[{i}].canonical_ingredient {tags} {e.get('canonical_ingredient')!r}")
    for canon in vis.keys():
        tags = surface_anomalies(canon)
        if tags:
            map_viol.append(f"verified_item_seqs key {tags} {canon!r}")
    v.check(not map_viol, 5, "매핑 키(canonical_ingredient/verified 성분키) 표면형 위생",
            f"viol={len(map_viol)} {map_viol[:15]}" if map_viol else "")

    total = len(v.passes) + len(v.fails)
    overall = "PASS" if not v.fails else "FAIL"
    bar = "=" * 64
    print(bar); print(f"MediStack v0.9 alias 표면형 검증: {alias_path}"); print(bar)
    if v.fails:
        print(f"\n[FAIL] {len(v.fails)}건")
        for no, title, detail in sorted(v.fails):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print("\n모든 표면형 검증 통과(라이브 alias 표면형 위생 OK).")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)"); print(bar)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ALIAS_PATH
    sys.exit(main(a))
