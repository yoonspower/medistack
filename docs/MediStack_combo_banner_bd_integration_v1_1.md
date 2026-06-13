# MediStack — 복합제 고지 배너 배선 + relation_card flip (1순위 B·D 35건) 라이브 통합 v1.1

> 작성일: 2026-06-13. **라이브 통합 완료(데이터만, 앱 src 무변경).** PM 승인(복합제 검토 v1.1 로드맵 **1순위**: B 라베프라졸+탄산수소나트륨 27건 + D 라베프라졸+아스피린 8건 = **35건**). 선행 분석: `MediStack_combo_relation_review_v1_1.md`.
>
> 통합기: `scripts/integrate_combo_banner_bd_v1_1.py`(idempotent). DATA_URL=v0.2 **in-place**. 되돌림=git revert.

---

## 0. 변경 요약

| 항목 | 통합 전 | 통합 후 | 비고 |
|---|---|---|---|
| relation_card (full index) | 976 | **1,011** | **+35** (B 27·D 8 flip) |
| name_only (full index) | 16,604 | **16,569** | −35 |
| full index total | 17,580 | **17,580** | **유지** |
| product_aliases | 583 | **618** | **+35** (is_combination=true) |
| alias_count | 621 | **656** | +35 |
| verified_item_seqs | 963 / 20성분 | **998 / 20성분** | +35 (라베프라졸 174→209, pool 진입) |
| ingredient_aliases | 38 | **38** | 불변 |
| relations (export) | 41 | **41** | **불변**(신규 relation 0) |
| DATA_URL | v0.2 | **v0.2** | **불변**(in-place) |
| published / clinical_reviewed | false | **false** | 봉인 유지 |

> **복합제 고지 배너 적용 = 35건** (B 27 + D 8). **relation_card 증가 = +35.**

---

## 1. 한 일 — 왜 "데이터만"으로 충분한가

복합제 고지 배너(`.combobox`)는 **render.js v0.7 에 이미 구현·라이브**(기존 메트포르민/알렌드론산/오메프라졸/HCTZ 복합제 **222건**에서 가동 중)였다. 따라서 **앱 코드(src) 변경 없이 데이터 배선만**으로 B·D 를 같은 메커니즘에 편입했다.

1. **full index flip (35)**: B·D 35건을 `name_only` → `relation_card`(covered_by_relation=true). validator 불변식 `relation_card ⟺ itemSeq ∈ pool` 충족 위해 alias pool 진입과 동시 수행(둘은 강결합).
2. **aliases ① verified_item_seqs['라베프라졸'] +35**: flip 된 35 item_seq 를 pool 에 등록(174→209). alias validator #8(`product alias item_seq ∈ 성분 relation itemSeq ∪ 검증 화이트리스트`) 충족.
3. **aliases ② product_aliases +35**: `is_combination=true`·`combination_basis_ingredient='라베프라졸'`·`combination_notice_required=true`·`source_relation_ids=[32,33]`. 기존 오메프라졸+탄산수소나트륨 combo 와 **동일 스키마**.

**렌더 동작(실측)**: 복합제 제품명 검색 → alias 가 라베프라졸로 해석 → 라베프라졸 relation 카드(id32 ×B12·id33 ×Mg) 표시 + 복합제 배너:

> **복합제** — 이 제품은 둘 이상의 성분을 가진 복합제입니다. 표시된 약-영양소 참고 정보는 **라베프라졸 성분을 기준**으로 하며, 함께 포함된 다른 성분에 대한 정보는 포함하지 않습니다. 전체 성분은 의약품 허가사항(첨부문서)을 확인하세요.

성분명("라베프라졸") 직접 검색 시엔 `aliasHint`가 directInFiltered 로 배너를 억제 → 단일성분 검색엔 배너 미노출(기존 동작 불변).

---

## 2. 금지 준수

- ✅ **B·D 35건만**. **E(라베+산화마그네슘 1건) flip 금지 준수**(여전히 name_only — Mg 직접모순, 영구 forbidden). **C(라베+칼슘 6건)·A(비스포+비타민D 43건) 미통합**(로드맵 2·3순위).
- ✅ **신규 relation 0**(export relations 41 dict-equal 불변). DATA_URL=v0.2 불변. src 무변경. published/clinical_reviewed false 유지. **tag 없음**.
- ✅ **제품/구매/제휴/영양제 추천 0**: 배너 문구는 "허가사항 확인" 안내뿐(href·구매·제품예시 없음). alias validator #10(제품필드 금지)·#16(칼륨보존이뇨제 토큰 금지) PASS.
- ✅ **에스오메프라졸 무관**(라베프라졸 basis). 칼륨 정책 불변(B=탄산수소나트륨·D=아스피린, 칼륨 없음 → potassium validator 8/8).
- ✅ **basis allowlist 확장은 승인분만**: `COMBO_ALLOWED_BASIS`에 라베프라졸 1개 추가(B/D 한정). 산화Mg/칼슘/비타민D 케이스는 미개방.

---

## 3. 검증 (전부 PASS)

| validator / smoke | 결과 |
|---|---|
| validate_medistack_v0_1_export | PASS |
| validate_medistack_v0_2_export | PASS (export 무변경) |
| validate_medistack_v0_3_aliases | PASS (16/16, #14 메타정합·#15 basis allowlist·#8 pool) |
| validate_alias_surface_forms | PASS (5/5, 신규 35 alias·verified item_name `\s+`→단일공백) |
| validate_full_drug_name_index | PASS (31/31, relation_card⟺pool·product 618·verified 998/20·relations 41) |
| validate_potassium_name_only_policy | PASS (8/8, name_only 16,569·relation_card 1,011) + selftest PASS |
| smoke_search_regression_v1_0 | PASS (**combo_notice_bd**: B·D 검색 count 2·comboBases [라베프라졸] + **combo_render_bd**: 배너 "복합제/라베프라졸 성분을 기준", 칼륨/구매/제품추천 0) |
| smoke_disclaimer_render | PASS |
| smoke_alias_regression / smoke_hctz_disclosure | PASS (기존 alias·HCTZ 배너 무회귀) |
| test_validate_v0_3_combo / combo_ar / typeB | PASS (9/9 · 13/13 · 7/7) |

**flip 검증(실측)**: B 라베+탄산수소나트륨 27 → relation_card · D 라베+아스피린 8 → relation_card · **E 산화Mg 1·C 칼슘 6·A 비타민D 43 → 여전히 name_only**(미통합 확인).

---

## 4. 갱신된 validator 상수 (회귀 감지 기준선)

- `validate_medistack_v0_3_aliases.py`: `COMBO_ALLOWED_BASIS` += 라베프라졸(B/D 한정 개방, E/C/A 미개방 주석).
- `validate_full_drug_name_index.py`: product 583→618 · alias_count 621→656 · verified 963/20→998/20(relations 41·ingredient 38 불변). CANONICAL_13 주석에 B/D flip 명시.
- `validate_potassium_name_only_policy.py`: name_only 16,604→16,569 · relation_card 976→1,011.
- `fixtures/search_regression_v1_0.json`: name_only_index_size 16,604→16,569 + combo_notice_bd/combo_render_bd 케이스 + data_basis 갱신.

---

## 5. 잔여 / 후속 (별도 PM)

- **로드맵 2순위 A(비스포+비타민D 43건)**: 카드 칼슘 경고가 "별도 복용 칼슘 제품"임을 명확화하는 문구/맥락 보강 후 배선.
- **로드맵 3순위 C(PPI+칼슘 18건)**: PPI×칼슘(저산성 탄산칼슘 흡수↓) relation 신규(허가사항 출처) 후 배선.
- **영구 금지 E(라베+산화Mg 1건)**: Mg 직접모순. 배선·flip 영구 불가.
- 기타 v1.1 후속(에스오메 full index 확장·H2×B12 source 정책 등)은 `MediStack_relation_expansion_live_integration_v1_1.md` §5 참조.

> 본 통합은 in-place(DATA_URL=v0.2 유지)라 별도 버전 파일·DATA_URL flip 없음. 되돌림은 git revert.
