# MediStack v0.3 — alias sample + validator (구조/규칙)

작성 기준일: 2026-06-07 / 단계: **sample + validator 구조 검증만** (앱 검색 미반영, 운영 alias 데이터 미생성, DATA_URL/deploy 무변경)
산출물: `data/medistack_v0.3_aliases.sample.json`(검증용 샘플) · `scripts/validate_medistack_v0_3_aliases.py`
상위: `docs/MediStack_v0.3_alias_schema_design.md` · `docs/MediStack_v0.3_alias_seed_plan.md`

## sample 파일 구조
`data/medistack_v0.3_aliases.sample.json` (운영 데이터 아님, 검증용. relation JSON과 분리된 별도 파일.)
```json
{
  "meta": { "version":"0.3", "kind":"alias_sample", "relation_source":"medistack_v0.2_beta_export.json", "alias_count":25 },
  "ingredient_aliases": [ { "alias":"levofloxacin", "canonical_ingredient":"레보플록사신", "kind":"ingredient", "lang":"en" }, ... ],
  "product_aliases":    [ { "alias":"타리비드", "canonical_ingredient":"오플록사신", "kind":"product", "lang":"ko", "item_seq":"198600307", "source_relation_ids":[21,22,23] }, ... ]
}
```
- 매칭 단일키 = `canonical_ingredient`(라이브 relation 성분과 정확 일치). `item_seq`·`source_relation_ids` = 추적/검증 메타.
- 샘플 범위: 7성분(오플록사신·레보플록사신·푸로세미드·히드로클로로티아지드·토라세미드·미노사이클린·알렌드론산), alias 25개(성분 12 + 제품 13). v0.2 30건 중 일부(id 1·2·3·17·18·19·20·21·22·23·26·27·28·29·30·31)에만 연결.
- **15행/에스오메프라졸 제품 alias 미포함**(우회 금지).

## validator 규칙 (`validate_medistack_v0_3_aliases.py`, 11 checks)
실행: `python3 scripts/validate_medistack_v0_3_aliases.py <aliases.json> [relations_export.json]` (relations 기본 = v0.2). 종료코드 0=PASS.

| # | 규칙 |
|---|---|
| 1 | 구조: ingredient_aliases/product_aliases 리스트 존재 |
| 2 | 항목 dict · **빈 alias 금지** · kind∈{product,ingredient} |
| 3 | **alias 중복 금지**(정규화 strip+lower) |
| 4 | **canonical_ingredient 가 라이브 relation 성분에 실재**(=alias만으로 신규 relation 생성 금지) |
| 5 | excluded_v0_1 전용 성분 매핑 금지 |
| 6 | **source_relation_ids 라이브 id에만** — relation_id **15·excluded 연결 금지** |
| 7 | source_relation_ids 의 relation 성분 == canonical_ingredient(정합) |
| 8 | product alias `item_seq` 가 해당 성분 relation 의 itemSeq 집합에 속함 |
| 9 | **에스오메프라졸 제품 alias 금지**(15행 우회 가드) |
| 10 | 제품/구매/제휴 필드 금지(affiliate/buy/price/link/coupon…) — item_seq/source_relation_ids 는 허용 메타 |
| 11 | nutrient(영양소) 매핑 alias 금지(제품추천 오인 방지) |

## 검증 결과 (2026-06-07)
- v0.1 export: **PASS (12/12)** — alias 추가가 기존 게이트 무영향.
- v0.2 export: **PASS (15/15)** — relations 무변경.
- v0.3 alias sample: **PASS (11/11)**.
- negative test (의도적 위반 → 정확한 체크에서 FAIL 검출):
  - relation_id 15 연결 → FAIL #6
  - 중복 alias("타리비드") → FAIL #3
  - 미존재 성분("와파린") → FAIL #4
  - 에스오메프라졸 제품 alias("넥시움") → FAIL #9
  - 빈 alias → FAIL #2

## 범위 (이 단계에서 하지 않은 것)
- 앱 검색에 alias 미반영(데이터/validator 구조만).
- 운영 `data/medistack_v0.3_aliases.json` 미생성(샘플뿐).
- DATA_URL/deploy 무변경. published/clinical 봉인 유지.

---
> 안전 원칙(불변): alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded alias 우회 금지 / 제품·구매·제휴 금지 / validator PASS 없으면 배포 금지.
