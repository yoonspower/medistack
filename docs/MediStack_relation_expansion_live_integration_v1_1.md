# MediStack — relation 확장 라이브 통합 v1.1 (source_confirmed 7후보)

> 작성일: 2026-06-13. **라이브 통합 완료.** PM 승인(c55a870 draft → 라이브). source_confirmed 7후보(E01–E06·E08)의 relation 11건(ids 32–42)을 라이브 export·full index·alias 에 통합.
>
> 통합기: `scripts/integrate_relation_expansion_v1_1.py` (idempotent). 근거 draft: `data/relation_expansion_draft_v1_1.json`(c55a870). 출처: `MediStack_relation_source_verification_atier.md`.

---

## 0. 변경 요약

| 항목 | 통합 전 | 통합 후 | 비고 |
|---|---|---|---|
| relations | 30 | **41** | 신규 11(ids 32–42, draft_origin 제거) |
| relation_card | 558 | **976** | **+418** (7성분 단일성분 flip) |
| name_only | 17,022 | **16,604** | −418 |
| full index total | 17,580 | **17,580** | **유지** |
| verified_item_seqs | 545 / 13성분 | **963 / 20성분** | +418 / +7 (pool 진입) |
| alias_count | 621 | **621** | 불변(ingredient/product_aliases 무변경) |
| product_aliases | 583 | **583** | 불변 |
| ingredient_aliases | 38 | **38** | 불변 |
| DATA_URL | v0.2 | **v0.2** | **불변**(in-place 통합 — flip 불필요) |
| published / clinical_reviewed | false | **false** | 봉인 유지 |

> **relation_card 증가 수 = +418** (558 → 976). 검색 시 참고정보가 붙는 품목이 75% 증가.

---

## 1. 통합 내용

**신규 relation 11건(ids 32–42)** — 기존 relation 30 dict-equal 불변, 추가만:
- PPI ×비타민B12(depletion·monitoring·moderate) + ×마그네슘(depletion·monitoring·moderate): 라베프라졸(32/33)·판토프라졸(34/35)·란소프라졸(36/37)·덱스란소프라졸(38/39)
- 경구 비스포스포네이트 ×칼슘(absorption·separation·high): 리세드론산(40)·이반드론산(41)
- 세프디니르 ×철분(absorption·separation·high, "흡수 약 1/10 저해")(42)

**full index flip 418건(단일성분만)** → relation_card:
| 성분 | flip(단일성분) |
|---|---|
| 라베프라졸 | 174 |
| 리세드론산 | 76 |
| 이반드론산 | 72 |
| 판토프라졸 | 45 |
| 란소프라졸 | 39 |
| 세프디니르 | 8 |
| 덱스란소프라졸 | 4 |
| **합계** | **418** |

> ⚠️ **복합제 97건은 보수적으로 name_only 유지**(이번 라운드 제외): 라베프라졸+산화마그네슘(Mg 함유 제품에 Mg 카드=모순), PPI+칼슘, 비스포+비타민D 등 nutrient 혼재로 카드 혼란 우려. 복합제 통합은 후속 검토.

**alias pool**: flip 된 418 item_seq 를 `verified_item_seqs` 에 7성분 키로 추가(method="full_index nedrug.searchDrug ingredient_name (relation expansion v1.1)"). pool 진입 → relation_card validator 정합.

---

## 2. 금지 준수 (강한 금지 전부 충족)

- ✅ source_confirmed 7후보만 추가. **E07/E09/E10(H2×B12) 미추가**(검색 count 0 확인). **에스오메프라졸 미추가**(기존 id16만).
- ✅ 기존 relation 30 dict-equal 불변. published/clinical_reviewed false 유지. tag 생성 없음.
- ✅ potassium 정책 불변(신규 7후보 칼륨 무관·potassium validator 8/8 PASS). 신규 relation 칼륨 토큰 0.
- ✅ 문구 참고정보 톤(복용지시·"드세요/피하세요/추천"·제품/구매/영양제 추천 0). 약사/의사 상담 고지 유지. 제품/구매 링크 0(href=nedrug 출처만).

---

## 3. 검증 (전부 PASS)

| validator/smoke | 결과 |
|---|---|
| validate_medistack_v0_2_export | PASS (15/15) |
| validate_full_drug_name_index | PASS (31/31, verified 963/20·relations 41) |
| validate_potassium_name_only_policy | PASS (8/8, name_only 16,604·relation_card 976) |
| validate_medistack_v0_3_aliases | PASS (16/16) |
| validate_relation_expansion_draft_v1_1 | PASS (21/21, base 30 dict-equal) |
| smoke_search_regression_v1_0 | PASS (신규 7성분 relation_card 표시 + missing 3 count 0 + name_only_index 16,604) |
| smoke_disclaimer_render | PASS (전 41 relation common 면책 + source 상속 + 칼륨행 분리) |

**검색 smoke 신규 케이스(실측)**: 라베프라졸→2·판토프라졸→2·란소프라졸→4(덱스란소 substring 중복)·덱스란소프라졸→2·리세드론산→1·이반드론산→1·세프디니르→1. missing 3(파모티딘/라푸티딘/니자티딘)→0.

**렌더 확인**: 신규 카드 common 면책 포함·source href=nedrug 출처(기존 id29 동일 패턴)·제품/구매 링크 0.

---

## 4. 갱신된 validator 상수 (회귀 감지 기준선)

- `validate_full_drug_name_index.py`: verified 545/13→963/20, relations 30→41. CANONICAL_13 유지(7성분 복합제 name_only 잔류 정상 — 주석).
- `validate_potassium_name_only_policy.py`: name_only 17,022→16,604, relation_card 558→976.
- `validate_relation_expansion_draft_v1_1.py`: 기존 30 비교를 고정 base(ids 1-14,16-31)로 견고화(v0.2 41건 대응).
- `fixtures/search_regression_v1_0.json`: name_only_index_size 16,604 + 신규 7성분/missing 3 케이스.
- v0.2 export validator·aliases validator: meta 기반(상수 갱신 불필요).

---

## 5. 잔여 / 후속 (별도 PM)

- **복합제 97건 통합 검토**: nutrient 혼재 카드 정책 결정 후 flip 여부.
- **비스포스포네이트 철·마그네슘 확장**(현재 칼슘 단독), **에스오메프라졸 full index 확장**(relation16 카드화), **H2×B12 source 정책**(이차출처 허용 여부).
- product_aliases 추가(브랜드 검색 시 신규 7성분 카드 연결 — 현재는 성분명 검색만).

> 본 통합은 in-place(DATA_URL=v0.2 유지)라 별도 버전 파일·DATA_URL flip 없음. 되돌림은 git revert.
