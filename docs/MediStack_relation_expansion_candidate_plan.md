# MediStack — relation 확장 후보 계획 (Expansion Candidate Plan)

> 작성일: 2026-06-13. 기준 HEAD `a0b9430`. **이 문서·후보 CSV 는 "검토 후보(candidate only)"일 뿐, 실제 relation 이 아니다. 이번 단계에서 relation/데이터는 한 줄도 추가·수정하지 않는다.**
> 동반: 현황 분석 `MediStack_relation_card_coverage_analysis.md`. 후보 초안 CSV: `data/relation_expansion_candidates_v1_1_draft.csv`.
> **후속(2026-06-13): 인기약 커버리지 매칭으로 본 7종 후보(C01–C07)를 20건 우선순위 후보로 확장 → `MediStack_relation_expansion_priority_plan.md` + `data/relation_expansion_priority_candidates_v1_1.csv`. 매칭 근거는 `MediStack_popular_drug_coverage_match.md`.**

---

## 0. 원칙 (먼저 읽기)

- 후보는 전부 `status=candidate_for_review`, `confirmed=false`, `source_required=true`, `review_required=true`, `clinical_reviewed=false`.
- 후보의 **nutrient 테마는 "가설(미확정)"** 이다 — 상호작용을 사실로 단정하지 않으며, 복용지시가 아니다. 실제 채택은 **허가사항 등 공식 출처 확인 + 검토**를 통과해야 한다.
- "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 금지. 제품 추천·구매·제휴 금지. published / clinical_reviewed 봉인.
- 본 계획은 **타깃 선정(어떤 약을 다음에 검토할지)** 까지다. 실제 relation 작성은 별도 단계(데이터 변경, PM 승인 필요).

---

## 1. 후보 선정 기준 (6)

1. 일반 사용자가 많이 검색할 법한 약품명/성분 (대중 인지도·만성 복용).
2. OTC/일반약 또는 대중 인지도 높은 약품명 우선.
3. **기존 relation 과 계열적으로 연결 가능성**이 있는 성분군 (동일 약효군이면 출처·문구 재현이 쉽고 안전선 승계 용이).
4. 식약처/DUR/허가사항 등 **공식 출처로 확인 가능성**이 높은 것.
5. 문구를 **복용지시가 아니라 참고정보 톤**으로 표현 가능한 것.
6. 제품 추천/구매/제휴와 무관한 것.

> 보정 관점(§분석 9): 현 558은 상위 3군 76% 편중(항생제·메트포르민·HCTZ). 후보는 **편중을 줄이는 방향**(기존 약효군 내 동일계열 보강 + 공백 만성질환군 일부)으로 고른다.

---

## 2. 후보 초안 7종 (candidate only)

> `name_only≈` = 현재 name_only 인덱스의 해당 성분 substring 매칭 건수(검색 수요·시장 존재의 1차 proxy). 실제 관계 가설은 **미확정**.

| ID | 성분(대표) | 약품군 | 기존 relation 연결 | name_only≈ | 검토 nutrient 테마(가설·미확정) | 비고 |
|---|---|---|---|---|---|---|
| C01 | 판토프라졸 | PPI | 오메프라졸 | 45 | 마그네슘·비타민B12 | 동일 PPI 계열, 출처 재현 쉬움 |
| C02 | 란소프라졸 | PPI | 오메프라졸 | 55 | 마그네슘·비타민B12 | 동일 PPI 계열 |
| C03 | 라베프라졸 | PPI | 오메프라졸 | 216 | 마그네슘·비타민B12 | name_only 최다 PPI |
| C04 | 클로르탈리돈 | 치아지드 이뇨제 | HCTZ | 64 | 전해질(칼륨 등) | **칼륨 안전 정책 승계 필수** |
| C05 | 인다파미드 | 치아지드 유사 이뇨제 | HCTZ | 16 | 전해질(칼륨 등) | 칼륨 안전 정책 승계 검토 |
| C06 | 로수바스타틴 | 스타틴 | (신규 계열) | 472 | 코엔자임Q10(문헌 보고) | name_only 최대 단일군, **신규 계열→신중** |
| C07 | 아토르바스타틴 | 스타틴 | (신규 계열) | 267 | 코엔자임Q10(문헌 보고) | 대중 인지도 높음, 신규 계열→신중 |

**우선순위 제안(검토 난이도·안전선 기준):**
- **1순위 = C01–C03 (기타 PPI)**: 기존 오메프라졸 관계와 **동일 약효군** → 허가사항 출처 패턴·문구 재현이 가장 쉽고 안전선 그대로 승계. 편중도 크게 안 늘림.
- **2순위 = C04–C05 (치아지드 계열)**: HCTZ 안전 정책(칼륨 product_link 금지·potassium_safety_card) **승계 설계가 선행**돼야 함. 승계 확인 전 보류.
- **3순위 = C06–C07 (스타틴×CoQ10)**: 검색 수요는 최대지만 **신규 약효군**이라 출처 표현·문구를 가장 신중히 검토. CoQ10 은 영양소 보충 권유로 읽히지 않도록 "참고" 톤 엄수.

> ⚠️ C04–C05: 치아지드/유사 이뇨제는 칼륨 관련 → **반드시 기존 칼륨 안전 정책**(product_link_allowed=false, potassium_safety_card=true, 칼륨 salt-form 보충제 취급 금지, 제품링크 금지)을 승계해야 채택 가능. 미승계 시 후보에서 제외.

---

## 3. 인기약 Top N 매칭 설계 (다음 단계 입력)

이번 단계에서는 **외부 데이터를 수집하지 않는다.** 다음 단계에서 인기약 Top 100~200 리스트를 넣으면 자동 매칭하도록 형식만 고정한다.

**입력 파일(다음 단계):** `data/external_popular_drugs_top100.csv`

| 컬럼 | 의미 |
|---|---|
| `rank` | 인기 순위 |
| `query_name` | 검색에 쓸 약품명/성분명 |
| `source` | 출처(예: 처방통계·약국 판매·검색량) |
| `note` | 비고 |

**매칭 방식(우선순위):**
1. `normalized_item_name` exact
2. alias match (`medistack_v0.3_aliases.json` 621 surface forms)
3. `ingredient_name` match
4. brand_core(브랜드 핵심어) 부분 매칭 — 후순위·수동 확인

**결과 분류:**
| 분류 | 의미 | 후속 |
|---|---|---|
| `relation_card_covered` | 이미 참고정보 표시 | 조치 불필요 |
| `name_only_only` | 이름은 있으나 정보 없음 | **relation 후보 1순위** |
| `missing_from_full_index` | 인덱스에 없음 | full index 확장 후보(별도) |
| `ambiguous_manual_review` | 다중/모호 매칭 | 수동 확인 |

> 목표: Top N 대비 `name_only_only` 비율이 높은 성분 = 체감 가치 향상 효과가 큰 relation 후보. 이 결과로 **relation 후보 20~50개를 최종 선정**한다.

---

## 4. 다음 단계 순서

1. 인기약 Top 100~200 외부 리스트 수집 → `external_popular_drugs_top100.csv`.
2. 위 매칭 스크립트로 covered / name_only / missing / ambiguous 분류.
3. `name_only_only` 상위 + 본 문서 후보(C01–C07) 교집합으로 **relation 후보 20~50 확정**.
4. 후보별 **허가사항 출처 확인**(nedrug getItemDetail) → 출처 있는 것만 통과.
5. (별도·PM 승인) relation 데이터 실제 작성 → validator/smoke → relation_card 재생성.

---

## 5. relation 확장 원칙 (불변)

- **출처 있는 것만**: 허가사항 등 공식 출처로 확인되지 않으면 채택 금지(공개 게이트의 source confirmed 원칙과 연동 — `MediStack_source_attribution_design.md`).
- **검토 후보로만**: 본 단계 산출은 candidate. confirmed=false.
- **참고정보 톤**: display_text/management 는 복용지시·단정이 아니라 "줄어들 수 있습니다 / 상담하세요" 톤.
- **제품 추천 금지**: product_link·구매·제휴 없음. 칼륨 관련은 제품링크 영구 금지.
- **clinical_reviewed / published = false 유지.**
- relation 데이터(핵심 자산)는 한 건도 사라지면 안 된다 — 확장은 추가만, 기존 30 불변.

---

## 6. 다음 작업 프롬프트 초안 (참고)

```
PM 판정: MediStack 인기약 Top N 매칭 단계 진행.
1. data/external_popular_drugs_top100.csv (rank,query_name,source,note) 수집/배치.
2. scripts 신규: match_popular_drugs.py — normalized→alias→ingredient→brand_core 순 매칭,
   결과를 relation_card_covered / name_only_only / missing / ambiguous 로 분류해 CSV+MD 출력.
3. name_only_only 상위 + relation_expansion_candidates_v1_1_draft.csv 교집합으로 relation 후보 20~50 선정.
4. 각 후보 허가사항 출처 확인(nedrug) — 출처 있는 것만 통과.
5. 데이터(relation/full index/alias/export/src) 변경 금지, candidate only, tag 금지.
6. validator/smoke 전종 + live 200 확인. 커밋 "Match popular drugs to coverage".
```

---

## 7. 금지 / 안전 (본 단계)

relation 추가·수정 / alias 수정 / full index 수정 / export 수정 / src·렌더 수정 / DATA_URL 변경 / source gate 변경 / disclaimer 변경 / published·clinical_reviewed true / 제품·구매·제휴·영양제 추천 UI / candidate→relation 승격 / tag 생성 / `scripts/__pycache__` 커밋 — **전부 금지.** 본 단계는 분석·후보 문서·후보 CSV 까지만.
