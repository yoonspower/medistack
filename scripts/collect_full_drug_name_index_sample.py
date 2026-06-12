#!/usr/bin/env python3
"""
collect_full_drug_name_index_sample.py
MediStack v1.0-B Phase 2 — full drug name index 1,000 샘플 수집기.

목적:
  "검색했는데 안 나오는 약" 체감을 줄이기 위한 전체 품목명 인덱스 샘플 생성.
  relation/의학 정보는 확장하지 않는다. relation 없는 약은 name_only("품목명 확인만 가능").

두 트랙:
  relation_card  — 기존 verified relation-covered itemSeq(날조 0, 의학정보 없이 itemSeq/이름만 재사용).
                   covered_by_relation=true · display_mode=relation_card · no_relation_notice_required=false.
  name_only      — nedrug searchDrug 실수집(13 relation 성분·에스오메프라졸·수출·원료·취소 제외).
                   covered_by_relation=false · display_mode=name_only · no_relation_notice_required=true.
                   relation/nutrient/supplement/product/management 필드 일절 없음.

수집 안전:
  - itemSeq/itemName 은 기존 검증 데이터 또는 nedrug 원문에서만(날조 금지).
  - 13 canonical 성분을 포함한 약은 name_only 에서 제외(relation 트랙 대상) → 오연결 방지.
  - 에스오메프라졸/넥시움/forbidden itemSeq 제외.
  - 수집 실패/애매 항목은 제외하고 stats 에 기록.

기존 수집 함수(nedrug_search/parse rows/field/정규식)는 collect_nedrug_alias_candidates 에서 재사용.

사용: python3 scripts/collect_full_drug_name_index_sample.py [--target 1000] [--max-pages 2] [--checked-at YYYY-MM-DD] [--no-network]
출력: data/full_drug_name_index_sample_v1_0.json + .csv
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from collect_nedrug_alias_candidates import (  # noqa: E402  (재사용)
    make_opener, nedrug_search, field, ANCHOR_RE, EXPORT_RE, ESO_HINT_RE, FORBIDDEN_ITEMSEQS,
)

ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
OUT_JSON = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")
OUT_CSV = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.csv")

TARGET_TOTAL = 1000
PER_INGREDIENT_CAP = 8
DEFAULT_CHECKED_AT = "2026-06-12"
NAME_ONLY_NOTICE = (
    "이 약은 MediStack의 약-영양소 참고정보 DB에 아직 등록된 항목이 없습니다. "
    "현재는 품목명 확인만 가능합니다. 복용 판단은 약사 또는 의사와 상담하세요."
)

# relation 트랙 13 canonical 성분(name_only 에서 제외 → relation 오연결 방지)
CANONICAL_13 = [
    "독시사이클린", "레보티록신", "레보플록사신", "메트포르민", "목시플록사신",
    "미노사이클린", "시프로플록사신", "알렌드론산", "오메프라졸", "오플록사신",
    "토라세미드", "푸로세미드", "히드로클로로티아지드",
]

# name_only 수집용 다양 성분(13 외, 에스오메프라졸 제외). 검색 다양성(편중 방지) 목적.
DIVERSE_INGREDIENTS = [
    "아세트아미노펜", "이부프로펜", "덱시부프로펜", "나프록센", "아세클로페낙", "디클로페낙",
    "멜록시캄", "셀레콕시브", "록소프로펜", "케토롤락", "트라마돌", "에토돌락",
    "아목시실린", "세파클러", "세푸록심", "세프디니르", "아지트로마이신", "클래리트로마이신",
    "록시트로마이신", "메트로니다졸", "클린다마이신", "세프트리악손", "아시클로비르", "발라시클로비르",
    "플루코나졸", "이트라코나졸", "암로디핀", "텔미사르탄", "발사르탄", "로사르탄",
    "칸데사르탄", "올메사르탄", "이르베사르탄", "비소프롤롤", "카르베딜롤", "네비볼롤",
    "딜티아젬", "라미프릴", "페린도프릴", "클로피도그렐", "실로스타졸", "아스피린",
    "아토르바스타틴", "로수바스타틴", "심바스타틴", "프라바스타틴", "피타바스타틴", "에제티미브",
    "페노피브레이트", "판토프라졸", "란소프라졸", "라베프라졸", "모사프리드", "레바미피드",
    "이토프리드", "돔페리돈", "파모티딘", "글리메피리드", "시타글립틴", "리나글립틴",
    "엠파글리플로진", "다파글리플로진", "글리클라지드", "피오글리타존", "세티리진", "레보세티리진",
    "로라타딘", "펙소페나딘", "베포타스틴", "에바스틴", "몬테루카스트", "암브록솔",
    "아세틸시스테인", "레보드로프로피진", "슈도에페드린", "에스시탈로프람", "설트랄린", "둘록세틴",
    "프레가발린", "가바펜틴", "졸피뎀", "알프라졸람", "라모트리진", "쿠에티아핀",
    "도네페질", "탐스로신", "두타스테리드", "피나스테리드", "솔리페나신", "알로푸리놀",
    "콜키신", "베타히스틴", "실데나필", "타다라필",
]


def norm_name(s):
    return " ".join(unicodedata.normalize("NFC", str(s or "")).split()).strip().lower()


def contains_13(ingr):
    n = ingr or ""
    return any(c in n for c in CANONICAL_13)


def parse_full(html_text):
    """searchDrug HTML → [{item_seq, item_name, ingr_name, finished, status_cancel, company}]."""
    out = []
    for chunk in re.split(r"<tr[ >]", html_text):
        if "getItemDetail?itemSeq=" not in chunk:
            continue
        m = ANCHOR_RE.search(chunk)
        if not m:
            continue
        out.append({
            "item_seq": m.group(1),
            "item_name": html.unescape(m.group(2)).strip(),
            "ingr_name": field(chunk, "주성분"),
            "finished": field(chunk, "완제/원료구분"),
            "status_cancel": field(chunk, "취소/취하구분"),
            "company": field(chunk, "업체명"),
        })
    return out


def build_relation_card_seed(checked_at):
    a = json.load(open(ALIAS_PATH, encoding="utf-8"))
    seed = {}  # item_seq -> {item_name, ingredient_name, source_checked_at}
    for ing, lst in (a.get("verified_item_seqs") or {}).items():
        for e in (lst or []):
            s = str(e.get("item_seq") or "").strip()
            nm = (e.get("item_name") or "").strip()
            if s and nm and s not in seed:
                seed[s] = {"item_name": nm, "ingredient_name": ing,
                           "source_checked_at": e.get("verified_at") or checked_at}
    for p in (a.get("product_aliases") or []):
        s = str(p.get("item_seq") or "").strip()
        nm = (p.get("alias") or "").strip()
        if s and nm and s not in seed:
            seed[s] = {"item_name": nm, "ingredient_name": p.get("canonical_ingredient", ""),
                       "source_checked_at": checked_at}
    entries = []
    for s, e in seed.items():
        entries.append({
            "item_seq": s,
            "item_name": e["item_name"],
            "normalized_item_name": norm_name(e["item_name"]),
            "ingredient_name": e["ingredient_name"],
            "company_name": None,
            "covered_by_relation": True,
            "display_mode": "relation_card",
            "no_relation_notice_required": False,
            "source": "MFDS nedrug",
            "source_method": "internal.medistack_v0_3_aliases",
            "source_checked_at": e["source_checked_at"],
        })
    return entries, set(seed.keys())


def collect_name_only(pool_seqs, cap, checked_at, max_pages, timeout, sleep):
    op = make_opener()
    out, seen = [], set(pool_seqs)
    st = {"ingredients_searched": 0, "ing_fail": 0, "rows_seen": 0,
          "excl_export": 0, "excl_raw": 0, "excl_cancel": 0, "excl_eso": 0,
          "excl_13": 0, "excl_dup": 0, "excl_pool": 0, "kept": 0, "fails": []}
    for ing in DIVERSE_INGREDIENTS:
        if len(out) >= cap:
            break
        st["ingredients_searched"] += 1
        got = 0
        for page in range(1, max_pages + 1):
            if len(out) >= cap or got >= PER_INGREDIENT_CAP:
                break
            try:
                html_text, _ = nedrug_search(op, ing, page=page, timeout=timeout)
            except Exception as e:
                st["ing_fail"] += 1
                st["fails"].append(f"{ing} p{page}: {type(e).__name__}")
                break
            time.sleep(sleep)
            for r in parse_full(html_text):
                if len(out) >= cap or got >= PER_INGREDIENT_CAP:
                    break
                st["rows_seen"] += 1
                seq, name, ingr = str(r["item_seq"]).strip(), r["item_name"].strip(), (r["ingr_name"] or "").strip()
                if not seq or not name:
                    continue
                if EXPORT_RE.search(name):
                    st["excl_export"] += 1; continue
                if "원료" in (r["finished"] or ""):
                    st["excl_raw"] += 1; continue
                if (r["status_cancel"] or "") != "정상":
                    st["excl_cancel"] += 1; continue
                if ESO_HINT_RE.search(name) or ESO_HINT_RE.search(ingr) or seq in FORBIDDEN_ITEMSEQS:
                    st["excl_eso"] += 1; continue
                if seq in seen:
                    st["excl_pool" if seq in pool_seqs else "excl_dup"] += 1; continue
                if contains_13(ingr):
                    st["excl_13"] += 1; continue
                seen.add(seq); got += 1; st["kept"] += 1
                comp = (r.get("company") or "").strip() or None
                out.append({
                    "item_seq": seq,
                    "item_name": name,
                    "normalized_item_name": norm_name(name),
                    "ingredient_name": ingr,
                    "company_name": comp,
                    "covered_by_relation": False,
                    "display_mode": "name_only",
                    "no_relation_notice_required": True,
                    "source": "MFDS nedrug",
                    "source_method": "nedrug.searchDrug",
                    "source_checked_at": checked_at,
                })
    return out, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=TARGET_TOTAL)
    ap.add_argument("--max-pages", type=int, default=2)
    ap.add_argument("--checked-at", default=DEFAULT_CHECKED_AT)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--sleep", type=float, default=0.15)
    ap.add_argument("--no-network", action="store_true", help="relation_card seed 만(name_only 수집 생략)")
    args = ap.parse_args()

    rc, pool = build_relation_card_seed(args.checked_at)
    print(f"[seed] relation_card(covered_by_relation=true) = {len(rc)}  (relation-covered pool itemSeqs)")

    name_cap = max(0, args.target - len(rc))
    if args.no_network:
        no, st = [], {"note": "no-network: name_only 수집 생략"}
        print("[name_only] --no-network → 생략")
    else:
        print(f"[name_only] 수집 시작 (cap {name_cap}, max-pages {args.max_pages}, {len(DIVERSE_INGREDIENTS)} 성분)")
        no, st = collect_name_only(pool, name_cap, args.checked_at, args.max_pages, args.timeout, args.sleep)
        print(f"[name_only] kept {len(no)} / cap {name_cap}  (ingredients {st['ingredients_searched']}, rows {st['rows_seen']})")

    entries = rc + no
    meta = {
        "name": "full_drug_name_index_sample_v1_0",
        "schema_version": "1.0",
        "purpose": "검색 커버리지 확장용 전체 품목명 인덱스 샘플(v1.0-B 설계 Phase 2). relation/alias 와 분리. name_only 는 '품목명 확인만 가능'. 앱 미배선(Phase 3).",
        "source_basis": "MFDS nedrug (식약처 의약품통합정보)",
        "generated_checked_at": args.checked_at,
        "target_total": args.target,
        "counts": {
            "total": len(entries),
            "relation_card": len(rc),
            "name_only": len(no),
        },
        "name_only_notice": NAME_ONLY_NOTICE,
        "note": "relation_card=기존 verified relation-covered itemSeq(의학정보 없이 itemSeq/이름만). name_only=relation 미연결(13성분·에스오메·수출·원료·취소 제외). 의학적 판단/상호작용/영양소 정보 없음.",
        "collection_stats": st,
    }
    doc = {"meta": meta, "entries": entries}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    csv_fields = ["item_seq", "item_name", "normalized_item_name", "ingredient_name",
                  "company_name", "covered_by_relation", "display_mode",
                  "no_relation_notice_required", "source", "source_method", "source_checked_at"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        w.writeheader()
        for e in entries:
            w.writerow(e)

    print(f"[out] {OUT_JSON}  total={len(entries)} (relation_card {len(rc)} + name_only {len(no)})")
    print("[stats] " + json.dumps(st, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
