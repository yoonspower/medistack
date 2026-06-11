#!/usr/bin/env python3
"""
generate_bulk_alias_candidates.py
MediStack v0.5 bulk alias 후보 생성기 — Phase 1(skeleton, 외부 API 미사용).

목적(설계: docs/MediStack_v0.5_bulk_alias_pipeline_plan.md):
  - 라이브 relation 30건에 연결된 canonical ingredient 만 대상으로 alias 후보를 만들어
    사람 검토용 review queue(JSON 정본 + CSV 보조)를 생성한다.
  - 이번 단계는 **외부 nedrug/data.go.kr 대량 호출 없이** 내부 데이터(현재 alias 파일/relations)만으로
    pipeline skeleton + schema 를 고정한다. 외부 연동은 Phase 2 TODO.
  - 생성기는 alias JSON 을 **읽기만** 한다. data/medistack_v0.3_aliases.json 미수정.
  - 후보는 전부 status=pending/deferred/rejected 로만 나오며 approved 는 생성하지 않는다(사람 승인 단계 별도).

안전 게이트(코드로 강제):
  - 후보 대상 canonical = 라이브 relation 성분 − 에스오메프라졸 − excluded 전용 성분.
  - 에스오메프라졸/15행/excluded 관련 성분은 후보를 만들지 않는다(스킵 카운트만 기록).
  - 기존 alias(현재 66개)와 정규화 중복되는 후보는 제외.
  - 숫자(itemSeq)를 위해 미검증 값을 지어내지 않는다. itemSeq 는 검증된 기존 제품 alias 에서 상속만.
  - brand_core 후보는 PM 판정(v0.5 #6)에 따라 status=deferred(자동 편입 금지, 별도 tier).

Phase 1 내부 생성 규칙:
  R-BC) brand_core 추출 — 검증된 product alias 표면형에서 용량/제형 토큰을 제거해 브랜드 코어 후보를 만든다.
        코어가 기존 성분명(ingredient alias/canonical) 전체를 포함하면 제네릭/제조사+제네릭으로 보고
        candidate_type=rejected(자동 거부). 그 외에는 brand_core(deferred).
  R-TA) Type A 성분 변형 — 내부 seed(아래 SEED_TYPE_A). v0.4 에서 표준 변형을 이미 흡수하여 현재 비어 있음
        (코드 경로만 유지, 실제 산출 0). 대량 Type A 확장은 Phase 2 외부 소스 필요.

사용:  python3 scripts/generate_bulk_alias_candidates.py
출력:  data/candidates/bulk_alias_review_queue_v0_5.json
       data/candidates/bulk_alias_review_queue_v0_5.csv
재실행 시 동일 입력 → 동일 출력(idempotent; 타임스탬프는 고정 상수).
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
RELATIONS_PATH = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
OUT_DIR = os.path.join(REPO, "data", "candidates")
OUT_JSON = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.json")
OUT_CSV = os.path.join(OUT_DIR, "bulk_alias_review_queue_v0_5.csv")

# 재실행 idempotency 용 고정 상수(런타임 now() 미사용 → git diff 안정).
GENERATED_AT = "2026-06-11"
WHITELIST_CHECKED_AT = "2026-06-11"     # verified_item_seqs 검증일
RELATION_CHECKED_AT = "2026-06-07"      # v0.2 export 원문 확인일(relation pointer 기준)
BATCH_ID = "v0.5-001"

EXCLUDED_BYPASS_INGREDIENT = "에스오메프라졸"  # 후보 생성 제외(15행 우회 차단). 라이브(id16)+excluded(15) 양쪽.
FORBIDDEN_ITEMSEQS = {"201600209"}            # 에스오메프라졸 대표 itemSeq(절대 후보에 등장 금지)

# review queue 16필드 스키마(정본 순서).
FIELDS = [
    "candidate_alias", "candidate_type", "canonical_ingredient", "item_seq", "item_name",
    "ingr_name", "source_url", "source_method", "source_checked_at", "confidence",
    "risk_level", "reason", "status", "exclusion_reason", "reviewer", "batch_id",
]
# CSV 는 사람 검토 편의상 앞쪽에 핵심 컬럼을 둔다(정본은 JSON).
CSV_FIELDS = [
    "canonical_ingredient", "candidate_alias", "status", "reason", "risk_level",
    "candidate_type", "item_seq", "item_name", "ingr_name", "source_url",
    "source_method", "source_checked_at", "confidence", "exclusion_reason", "reviewer", "batch_id",
]

STATUS_VALUES = ["pending", "approved", "rejected", "deferred"]
CANDIDATE_TYPES = ["ingredient", "product_full_name", "brand_core", "rejected"]

# Type A 내부 seed(canonical -> [(alias, lang), ...]). v0.4 에서 표준 변형 흡수 완료 → 현재 비어 있음.
# 코드 경로 유지용. 대량 Type A 는 Phase 2(외부 소스)로 채운다.
SEED_TYPE_A = {}

ITEMSEQ_RE = re.compile(r"itemSeq=(\d+)")
# 용량 토큰(이 지점부터 끝까지 제거 → 브랜드 코어). 용량 뒤 제형(정 등)도 함께 잘림.
DOSE_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:밀리그램|밀리그람|마이크로그램|밀리리터|mcg|mg|ml|g|그램|그람|%|IU|단위)")
# 코어 끝 제형 토큰 제거 → 더 짧은 코어.
FORM_RE = re.compile(r"(?:서방정|장용정|연질캡슐|경질캡슐|캡슐|정|시럽|현탁액|건조시럽|주사|주|액)$")


def norm(s):
    return (s or "").strip().lower()


def load(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FATAL] {label} 로드 실패: {path}: {e}")
        sys.exit(2)


def build_context():
    adata = load(ALIAS_PATH, "alias")
    rdata = load(RELATIONS_PATH, "relations")

    rels = rdata.get("relations") or []
    excl = rdata.get("excluded_v0_1") or []
    live_ings = {r.get("ingredient") for r in rels if r.get("ingredient")}
    excl_ings = {e.get("ingredient") for e in excl if e.get("ingredient")}
    excluded_only = excl_ings - live_ings
    # 허용 canonical = 라이브 − 에스오메프라졸 − excluded 전용
    allowed = (live_ings - {EXCLUDED_BYPASS_INGREDIENT}) - excluded_only

    ing_to_relseqs = {}
    for r in rels:
        ing = r.get("ingredient")
        m = ITEMSEQ_RE.search((r.get("source") or {}).get("url", "") or "")
        if ing and m:
            ing_to_relseqs.setdefault(ing, set()).add(m.group(1))

    wl = adata.get("verified_item_seqs", {}) or {}
    wl_seqs = set()
    for lst in wl.values():
        for ent in (lst or []):
            s = (ent.get("item_seq") or "").strip()
            if s:
                wl_seqs.add(s)

    ing_aliases = adata.get("ingredient_aliases") or []
    prod_aliases = adata.get("product_aliases") or []
    existing_norm = {norm(a["alias"]) for a in ing_aliases + prod_aliases if a.get("alias")}

    # 자동 거부용: 기존 성분명(ingredient alias 표면형 + canonical) 정규화 집합(len>=4).
    ingredient_name_strings = {norm(a["alias"]) for a in ing_aliases if a.get("alias")}
    ingredient_name_strings |= {norm(x) for x in live_ings}
    ingredient_name_strings = {s for s in ingredient_name_strings if len(s) >= 4}

    return {
        "adata": adata, "rdata": rdata,
        "live_ings": live_ings, "excluded_only": excluded_only, "allowed": allowed,
        "ing_to_relseqs": ing_to_relseqs, "wl_seqs": wl_seqs,
        "prod_aliases": prod_aliases, "existing_norm": existing_norm,
        "ingredient_name_strings": ingredient_name_strings,
        "alias_count": adata.get("meta", {}).get("alias_count"),
        "relation_count": len(rels),
    }


def checked_at_for(seq, ing, ctx):
    if seq in ctx["wl_seqs"]:
        return WHITELIST_CHECKED_AT
    if seq in ctx["ing_to_relseqs"].get(ing, set()):
        return RELATION_CHECKED_AT
    return ""


def brand_core_variants(product_name):
    """product 표면형 → 브랜드 코어 후보(중복 제거, 최대 2개: 제형포함/제형제거)."""
    m = DOSE_RE.search(product_name)
    core_with_form = product_name[:m.start()] if m else product_name
    core_bare = FORM_RE.sub("", core_with_form)
    out = []
    for c in (core_with_form, core_bare):
        c = c.strip()
        if c and c != product_name and c not in out:
            out.append(c)
    return out


def make_row(**kw):
    row = {f: "" for f in FIELDS}
    row["batch_id"] = BATCH_ID
    row["reviewer"] = ""
    row.update(kw)
    return row


def generate(ctx):
    rows = []
    skipped = {"excluded_or_esomeprazole": 0, "dedup_existing": 0, "type_a_seed_dedup": 0}
    seen_in_queue = set()

    # R-BC) brand_core 추출
    for pa in ctx["prod_aliases"]:
        ing = pa.get("canonical_ingredient")
        product = pa.get("alias")
        seq = (pa.get("item_seq") or "").strip()
        if not ing or not product:
            continue
        if ing == EXCLUDED_BYPASS_INGREDIENT or ing in ctx["excluded_only"] or ing not in ctx["allowed"]:
            skipped["excluded_or_esomeprazole"] += 1
            continue
        if seq in FORBIDDEN_ITEMSEQS:
            skipped["excluded_or_esomeprazole"] += 1
            continue
        checked_at = checked_at_for(seq, ing, ctx)
        src_url = f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={seq}" if seq else ""
        for core in brand_core_variants(product):
            nkey = norm(core)
            if nkey in ctx["existing_norm"]:
                skipped["dedup_existing"] += 1
                continue
            if nkey in seen_in_queue:
                continue
            seen_in_queue.add(nkey)
            # 자동 거부: 코어가 기존 성분명(전체)을 포함 → 제네릭/제조사+제네릭
            hit = next((s for s in ctx["ingredient_name_strings"] if s in nkey), None)
            if hit:
                rows.append(make_row(
                    candidate_alias=core, candidate_type="rejected", canonical_ingredient=ing,
                    item_seq=seq, item_name=product, ingr_name=ing, source_url=src_url,
                    source_method=f"brand-core extraction from verified product '{product}' (itemSeq {seq})",
                    source_checked_at=checked_at, confidence="low", risk_level="low",
                    reason=f"코어가 성분명 '{hit}' 을(를) 포함 → 제네릭/제조사+제네릭, 브랜드 코어 아님",
                    status="rejected",
                    exclusion_reason="contains full ingredient name; not a brand core",
                ))
            else:
                rows.append(make_row(
                    candidate_alias=core, candidate_type="brand_core", canonical_ingredient=ing,
                    item_seq=seq, item_name=product, ingr_name=ing, source_url=src_url,
                    source_method=f"brand-core extraction from verified product '{product}' (itemSeq {seq})",
                    source_checked_at=checked_at, confidence="low", risk_level="medium",
                    reason=f"검증된 제품 '{product}'(itemSeq {seq})에서 추출한 브랜드 코어. 승인 전 사람 검토 필요",
                    status="deferred",
                    exclusion_reason="brand_core tier deferred (PM v0.5 #6: 자동 편입 금지)",
                ))

    # R-TA) Type A seed(현재 비어 있음 → 0건)
    for ing, variants in SEED_TYPE_A.items():
        if ing == EXCLUDED_BYPASS_INGREDIENT or ing not in ctx["allowed"]:
            skipped["excluded_or_esomeprazole"] += 1
            continue
        for alias, _lang in variants:
            nkey = norm(alias)
            if nkey in ctx["existing_norm"] or nkey in seen_in_queue:
                skipped["type_a_seed_dedup"] += 1
                continue
            seen_in_queue.add(nkey)
            rows.append(make_row(
                candidate_alias=alias, candidate_type="ingredient", canonical_ingredient=ing,
                ingr_name=ing, confidence="medium", risk_level="low",
                reason="Type A 성분 표기 변형(내부 seed). 표기 확인 후 승인", status="pending",
            ))

    rows.sort(key=lambda r: (r["canonical_ingredient"], r["candidate_type"], r["candidate_alias"]))
    return rows, skipped


def counts_by_status(rows):
    c = {s: 0 for s in STATUS_VALUES}
    for r in rows:
        c[r["status"]] = c.get(r["status"], 0) + 1
    return c


def write_outputs(ctx, rows, skipped):
    counts = counts_by_status(rows)
    meta = {
        "schema": "bulk_alias_review_queue",
        "version": "v0.5",
        "phase": 1,
        "generated_at": GENERATED_AT,
        "generator": "scripts/generate_bulk_alias_candidates.py",
        "relation_source": "data/medistack_v0.2_beta_export.json",
        "alias_source": "data/medistack_v0.3_aliases.json",
        "alias_count_at_generation": ctx["alias_count"],
        "relation_count": ctx["relation_count"],
        "allowed_canonical": sorted(ctx["allowed"]),
        "allowed_canonical_count": len(ctx["allowed"]),
        "external_api_used": False,
        "batch_id": BATCH_ID,
        "status_values": STATUS_VALUES,
        "candidate_types": CANDIDATE_TYPES,
        "counts": {"total": len(rows), **counts},
        "skipped": skipped,
        "note": ("Phase 1 skeleton. 내부 데이터만 사용(외부 API 0회). 모든 후보는 사람 승인 전까지 미반영. "
                 "approved 0건. brand_core=deferred(PM v0.5 #6). 에스오메프라졸/15행/excluded 후보 미생성. "
                 "alias JSON 미수정. 대량 Type A/B·itemSeq 확정은 Phase 2(nedrug/data.go.kr) 필요."),
        "phase2_todo": [
            "nedrug searchDrug(ingrName1) 로 성분별 2번째~N번째 완제품 목록 수집",
            "getItemDetail(itemSeq) 로 품목명·주성분·성분코드 원문 확정(product_full_name 후보)",
            "data.go.kr OpenAPI 로 제네릭 품목명 대량 수집(중복·제형 필터)",
            "brand_core deferred 후보 사람 검토 → approved 승격(별도 tier 결정)",
        ],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "candidates": rows}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})
    return meta


def main():
    ctx = build_context()
    # 안전 확인(생성 자체가 라이브 상태를 바꾸지 않지만, 입력 전제 점검).
    if ctx["alias_count"] != 66:
        print(f"[WARN] alias_count={ctx['alias_count']} (기대 66) — 입력 alias 파일 확인 필요")
    if ctx["relation_count"] != 30:
        print(f"[WARN] relation_count={ctx['relation_count']} (기대 30)")
    rows, skipped = generate(ctx)
    meta = write_outputs(ctx, rows, skipped)
    print("=" * 64)
    print("MediStack v0.5 bulk alias 후보 생성 — Phase 1(skeleton)")
    print("=" * 64)
    print(f"허용 canonical({meta['allowed_canonical_count']}): {meta['allowed_canonical']}")
    print(f"외부 API 사용: {meta['external_api_used']}")
    print(f"생성 후보 total: {meta['counts']['total']}")
    for s in STATUS_VALUES:
        print(f"  {s:<9}: {meta['counts'][s]}")
    print(f"skip: {skipped}")
    print(f"JSON: {os.path.relpath(OUT_JSON, REPO)}")
    print(f"CSV : {os.path.relpath(OUT_CSV, REPO)}")
    print("alias JSON 미수정(읽기 전용). approved 0건. 사람 승인 전까지 alias 반영 없음.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
