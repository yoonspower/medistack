# MediStack — popular-like 약 커버리지 매칭 (Coverage Match)

> 작성일: 2026-06-13. **분석 전용 — 데이터/렌더 한 줄도 변경하지 않는다.**
> 재현: `python3 scripts/match_popular_drugs_coverage.py` (읽기 전용). 결과 CSV: `data/popular_drug_coverage_match_v1_1.csv`.
> ⚠️ seed 리스트는 **실측 검색량/판매량 데이터가 아니다.** 임상·OTC 인지도 기반 `priority_seed_rank`(confidence=low) 이며, '인기약 Top N'으로 확정 표현하지 않는다. 외부 인기약 실데이터 매칭은 다음 단계(`data/external_popular_drugs_top100.csv`)로 보완한다.

---

## 0. 범위와 한계

- 본 문서는 **popular-like seed 후보가 현재 relation_card 558 에 얼마나 덮이는지** 정량 분류한다. relation 을 추가하지 않는다.
- 매칭은 성분명 기준(정규명 exact → alias → 성분 exact/substring → 브랜드 부분)으로 결정적이며, 기준 수치(17,580/558/17,022/relation 30) 불일치 시 STOP 한다.
- "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현은 사용하지 않는다. 제공 정보는 허가사항 정리 **참고용**이다.

---

## 1. seed 후보 요약

- seed 후보 총수: **120**
- 출처: 임상/OTC 인지도 추정 (실측 검색량 아님). confidence=low.
- 매칭 방식: normalized_exact → alias → ingredient(exact/substring) → brand_core(item substring) → 미매칭=missing.
- seed 성분 표기는 인덱스 음역에 맞춰 정렬했다(예: 네비볼롤→네비보롤, 세르트랄린→설트랄린). 표기 불일치로 인한 거짓 missing 을 줄이기 위함이다.

## 2. 커버리지 분류 결과

| 분류 | 수 | 비율 | 의미 |
|---|---|---|---|
| relation_card_covered | **13** | 10.8% | 검색 시 이미 참고정보 표시 |
| name_only_only | **101** | 84.2% | 이름은 있으나 정보 없음 (**확장 검토 1차 모집단** — 근거 있는 것만 승격) |
| missing_from_full_index | **6** | 5.0% | 인덱스에 없음 (full index 확장 트랙) |
| ambiguous_manual_review | **0** | 0.0% | 다중/모호 매칭 (수동 확인) |
| 합계 | 120 | 100% | |

## 3. 카테고리별 커버리지

| 카테고리 | seed | covered | name_only | missing | ambiguous |
|---|---|---|---|---|---|
| 해열진통제/소염진통제 | 10 | 0 | 9 | 1 | 0 |
| 감기약/종합감기약 | 8 | 0 | 8 | 0 | 0 |
| 소화제/위장약/PPI/H2 | 15 | 1 | 13 | 1 | 0 |
| 항히스타민/알레르기약 | 7 | 0 | 7 | 0 | 0 |
| 혈압약/ARB/CCB/이뇨제 | 19 | 3 | 15 | 1 | 0 |
| 당뇨약 | 9 | 1 | 8 | 0 | 0 |
| 고지혈증약/스타틴 | 7 | 0 | 7 | 0 | 0 |
| 갑상선약 | 3 | 1 | 2 | 0 | 0 |
| 항생제 | 14 | 6 | 8 | 0 | 0 |
| 골다공증/여성건강/빈혈 | 8 | 1 | 4 | 3 | 0 |
| 수면/진정/정신건강 | 5 | 0 | 5 | 0 | 0 |
| 기타 흔한 만성질환 | 15 | 0 | 15 | 0 | 0 |

## 4. name_only_only 중 확장 검토 1차 모집단 (high/medium 인지도·민감군 제외)

> `next_action=relation_expansion_candidate`. name_only 매핑수 내림차순. **이 표는 후보 풀(1차 모집단)일 뿐 전부 채택 대상이 아니다** — 확립된 약물-영양소 상호작용 근거가 있는 것만 `MediStack_relation_expansion_priority_plan.md` 에서 승격한다(암로디핀·항히스타민·감기약 등은 근거 없어 §plan §4 에서 제외).

| seed_rank | query_name | 카테고리 | name_only 매핑 | 매칭법 | confidence |
|---|---|---|---|---|---|
| 41 | 암로디핀 | 혈압약/ARB/CCB/이뇨제 | 667 | ingredient_substring | medium |
| 70 | 로수바스타틴 | 고지혈증약/스타틴 | 472 | ingredient_substring | medium |
| 13 | 클로르페니라민 | 감기약/종합감기약 | 407 | ingredient_substring | medium |
| 11 | 슈도에페드린 | 감기약/종합감기약 | 268 | ingredient_substring | medium |
| 69 | 아토르바스타틴 | 고지혈증약/스타틴 | 267 | ingredient_substring | medium |
| 12 | 덱스트로메토르판 | 감기약/종합감기약 | 262 | ingredient_substring | medium |
| 23 | 라베프라졸 | 소화제/위장약/PPI/H2 | 216 | ingredient_substring | medium |
| 115 | 몬테루카스트 | 기타 흔한 만성질환 | 208 | ingredient_substring | medium |
| 113 | 프레가발린 | 기타 흔한 만성질환 | 200 | ingredient_exact | high |
| 79 | 아목시실린 | 항생제 | 198 | ingredient_substring | medium |
| 108 | 피나스테리드 | 기타 흔한 만성질환 | 193 | ingredient_exact | high |
| 34 | 세티리진 | 항히스타민/알레르기약 | 186 | ingredient_substring | medium |
| 62 | 시타글립틴 | 당뇨약 | 180 | ingredient_substring | medium |
| 28 | 모사프리드 | 소화제/위장약/PPI/H2 | 173 | ingredient_substring | medium |
| 80 | 클라불란산 | 항생제 | 170 | ingredient_substring | medium |
| 44 | 로사르탄 | 혈압약/ARB/CCB/이뇨제 | 168 | ingredient_substring | medium |
| 106 | 탐스로신 | 기타 흔한 만성질환 | 163 | ingredient_substring | medium |
| 73 | 피타바스타틴 | 고지혈증약/스타틴 | 150 | ingredient_substring | medium |
| 99 | 탄산칼슘 | 골다공증/여성건강/빈혈 | 150 | ingredient_substring | medium |
| 31 | 레바미피드 | 소화제/위장약/PPI/H2 | 149 | ingredient_exact | high |
| 84 | 클래리트로마이신 | 항생제 | 144 | ingredient_exact | high |
| 7 | 아세클로페낙 | 해열진통제/소염진통제 | 143 | ingredient_exact | high |
| 46 | 올메사르탄 | 혈압약/ARB/CCB/이뇨제 | 142 | ingredient_substring | medium |
| 8 | 록소프로펜 | 해열진통제/소염진통제 | 140 | ingredient_substring | medium |
| 114 | 가바펜틴 | 기타 흔한 만성질환 | 137 | ingredient_exact | high |
| 61 | 글리메피리드 | 당뇨약 | 136 | ingredient_exact | high |
| 81 | 세파클러 | 항생제 | 135 | ingredient_substring | medium |
| 45 | 칸데사르탄 | 혈압약/ARB/CCB/이뇨제 | 124 | ingredient_substring | medium |
| 35 | 레보세티리진 | 항히스타민/알레르기약 | 123 | ingredient_substring | medium |
| 94 | 리세드론산 | 골다공증/여성건강/빈혈 | 118 | ingredient_substring | medium |
| 48 | 피마사르탄 | 혈압약/ARB/CCB/이뇨제 | 114 | ingredient_substring | medium |
| 38 | 베포타스틴 | 항히스타민/알레르기약 | 111 | ingredient_substring | medium |
| 25 | 파모티딘 | 소화제/위장약/PPI/H2 | 106 | ingredient_exact | high |
| 5 | 덱시부프로펜 | 해열진통제/소염진통제 | 99 | ingredient_exact | high |
| 9 | 멜록시캄 | 해열진통제/소염진통제 | 99 | ingredient_exact | high |
| 119 | 콜린알포세레이트 | 기타 흔한 만성질환 | 99 | ingredient_exact | high |
| 2 | 이부프로펜 | 해열진통제/소염진통제 | 94 | ingredient_exact | high |
| 107 | 두타스테리드 | 기타 흔한 만성질환 | 94 | ingredient_exact | high |
| 43 | 발사르탄 | 혈압약/ARB/CCB/이뇨제 | 87 | ingredient_exact | high |
| 16 | 아세틸시스테인 | 감기약/종합감기약 | 82 | ingredient_exact | high |
| 57 | 카르베딜롤 | 혈압약/ARB/CCB/이뇨제 | 73 | ingredient_exact | high |
| 42 | 텔미사르탄 | 혈압약/ARB/CCB/이뇨제 | 59 | ingredient_exact | high |
| 71 | 심바스타틴 | 고지혈증약/스타틴 | 55 | ingredient_exact | high |
| 65 | 엠파글리플로진 | 당뇨약 | 50 | ingredient_exact | high |
| 3 | 아스피린 | 해열진통제/소염진통제 | 47 | ingredient_exact | high |
| 21 | 판토프라졸 | 소화제/위장약/PPI/H2 | 45 | ingredient_substring | medium |
| 15 | 암브록솔 | 감기약/종합감기약 | 44 | ingredient_substring | medium |
| 37 | 펙소페나딘 | 항히스타민/알레르기약 | 44 | ingredient_substring | medium |
| 4 | 나프록센 | 해열진통제/소염진통제 | 42 | ingredient_exact | high |
| 63 | 리나글립틴 | 당뇨약 | 37 | ingredient_exact | high |
| 1 | 아세트아미노펜 | 해열진통제/소염진통제 | 34 | ingredient_exact | high |
| 110 | 페북소스타트 | 기타 흔한 만성질환 | 33 | ingredient_exact | high |
| 36 | 로라타딘 | 항히스타민/알레르기약 | 20 | ingredient_exact | high |
| 75 | 페노피브레이트 | 고지혈증약/스타틴 | 17 | ingredient_exact | high |
| 83 | 아지트로마이신 | 항생제 | 14 | ingredient_substring | medium |
| 64 | 빌다글립틴 | 당뇨약 | 13 | ingredient_exact | high |
| 58 | 비소프롤롤 | 혈압약/ARB/CCB/이뇨제 | 12 | ingredient_substring | medium |
| 22 | 란소프라졸 | 소화제/위장약/PPI/H2 | 10 | ingredient_exact | high |
| 10 | 디클로페낙 | 해열진통제/소염진통제 | 7 | ingredient_exact | high |
| 82 | 세프디니르 | 항생제 | 7 | ingredient_exact | high |
| 91 | 메트로니다졸 | 항생제 | 7 | ingredient_exact | high |
| 29 | 돔페리돈 | 소화제/위장약/PPI/H2 | 6 | ingredient_exact | high |
| 67 | 글리클라지드 | 당뇨약 | 6 | ingredient_exact | high |
| 66 | 다파글리플로진 | 당뇨약 | 4 | ingredient_exact | high |
| 77 | 메티마졸 | 갑상선약 | 4 | ingredient_exact | high |
| 118 | 도네페질 | 기타 흔한 만성질환 | 4 | ingredient_exact | high |
| 74 | 에제티미브 | 고지혈증약/스타틴 | 3 | ingredient_exact | high |
| 49 | 라미프릴 | 혈압약/ARB/CCB/이뇨제 | 2 | ingredient_exact | high |
| 109 | 알로푸리놀 | 기타 흔한 만성질환 | 2 | ingredient_exact | high |
| 116 | 우르소데옥시콜산 | 기타 흔한 만성질환 | 2 | ingredient_exact | high |
| 32 | 트리메부틴 | 소화제/위장약/PPI/H2 | 1 | ingredient_exact | high |

→ 확장 검토 1차 모집단(name_only_only · high/medium · 민감군 제외): **71건**

### 4-1. high_risk_hold — 민감 약군 (후보화 보류)

> 정신건강·항응고/항혈소판·임신/피임 등 민감군. name_only_only 라도 **확장 후보로 올리지 않는다**(criterion 8). 영양소 관계 근거가 약하거나 임상판단 영역이라 별도 임상검토 전까지 보류. priority_plan §5 참조.

| seed_rank | query_name | 카테고리 | name_only 매핑 |
|---|---|---|---|
| 100 | 드로스피레논 | 골다공증/여성건강/빈혈 | 9 |
| 101 | 졸피뎀 | 수면/진정/정신건강 | 16 |
| 102 | 에스시탈로프람 | 수면/진정/정신건강 | 103 |
| 103 | 설트랄린 | 수면/진정/정신건강 | 21 |
| 104 | 알프라졸람 | 수면/진정/정신건강 | 26 |
| 105 | 쿠에티아핀 | 수면/진정/정신건강 | 130 |
| 111 | 클로피도그렐 | 기타 흔한 만성질환 | 158 |
| 112 | 리바록사반 | 기타 흔한 만성질환 | 43 |

→ high_risk_hold(민감군·후보화 보류): **8건**

## 5. 이미 covered 인 seed (조치 불필요)

| query_name | relation_id | relation | rc 매핑 |
|---|---|---|---|
| 오메프라졸 | 13;14 | 오메프라졸×마그네슘; 오메프라졸×비타민B12 | 42 |
| 히드로클로로티아지드 | 19;20 | 히드로클로로티아지드×마그네슘; 히드로클로로티아지드×칼륨 | 113 |
| 푸로세미드 | 17;18 | 푸로세미드×마그네슘; 푸로세미드×칼륨 | 2 |
| 토라세미드 | 30;31 | 토라세미드×마그네슘; 토라세미드×칼륨 | 6 |
| 메트포르민 | 12 | 메트포르민×비타민B12 | 113 |
| 레보티록신 | 10;11 | 레보티록신×철분; 레보티록신×칼슘 | 17 |
| 레보플록사신 | 1;2;3 | 레보플록사신×마그네슘; 레보플록사신×철분; 레보플록사신×칼슘 | 91 |
| 시프로플록사신 | 4;5;6 | 시프로플록사신×마그네슘; 시프로플록사신×철분; 시프로플록사신×칼슘 | 69 |
| 목시플록사신 | 24;25 | 목시플록사신×마그네슘; 목시플록사신×철분 | 6 |
| 오플록사신 | 21;22;23 | 오플록사신×마그네슘; 오플록사신×철분; 오플록사신×칼슘 | 33 |
| 독시사이클린 | 7;8;9 | 독시사이클린×마그네슘; 독시사이클린×철분; 독시사이클린×칼슘 | 11 |
| 미노사이클린 | 26;27;28 | 미노사이클린×마그네슘; 미노사이클린×철분; 미노사이클린×칼슘 | 3 |
| 알렌드론산 | 29 | 알렌드론산×칼슘 | 52 |

## 6. missing_from_full_index (full index 확장 트랙·별도)

> ⚠️ 여기서 **missing = 현재 17,580 *샘플* 인덱스에 매칭 품목이 없음**을 뜻한다. 해당 약이 한국에 존재하지 않는다는 의미가 **아니다.** 인덱스는 `full_drug_name_index_sample_v1_0` = 확장 중인 샘플이다(메타 target_total 기준). 이 항목들은 full index 확장 트랙의 입력이다.

| query_name | 카테고리 | 비고 |
|---|---|---|
| 세레콕시브 | 해열진통제/소염진통제 | 샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음 |
| 에스오메프라졸 | 소화제/위장약/PPI/H2 | 인덱스에 에스오메프라졸 품목 0건 → relation16(에스오메프라졸×Mg)이 relation_card 0건인 근본 원인(기존 분석과 일치). 주요 PPI 브랜드(넥시움) 미인덱싱(정량 처방량 단정 아님) → full index 확장 시 우선 검토. |
| 스피로노락톤 | 혈압약/ARB/CCB/이뇨제 | 샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음 |
| 졸레드론산 | 골다공증/여성건강/빈혈 | 샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음 |
| 랄록시펜 | 골다공증/여성건강/빈혈 | 샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음 |
| 건조황산제일철 | 골다공증/여성건강/빈혈 | 샘플 인덱스 내 성분/정규명/alias/브랜드 부분 매칭 모두 없음 |

## 7. ambiguous_manual_review

(없음 — 모든 매칭이 단일 성분 또는 명확한 계열로 해소됨)

## 8. 사용자 체감 가치 평가

- popular-like seed 120건 중 **13건(10.8%)** 은 이미 참고정보가 붙는다 → 흔한 만성질환 핵심군(당뇨 메트포르민·고혈압 HCTZ·갑상선·항생제·골다공증·PPI 오메프라졸)은 검색 시 정보 표시.
- 그러나 **101건(84.2%)** 은 name_only_only — 사용자가 흔히 찾는데 정보가 없다. 여기가 체감 가치 향상 여지가 가장 큰 구간이다.
- 가장 큰 공백 카테고리(아래 §9)는 relation 확장 우선순위 입력으로 쓴다.

## 9. 가장 큰 공백 카테고리 (확장 우선순위 입력)

| 카테고리 | name_only_only | 비고 |
|---|---|---|
| 혈압약/ARB/CCB/이뇨제 | 15 | seed 19건 중 |
| 기타 흔한 만성질환 | 15 | seed 15건 중 |
| 소화제/위장약/PPI/H2 | 13 | seed 15건 중 |
| 해열진통제/소염진통제 | 9 | seed 10건 중 |
| 감기약/종합감기약 | 8 | seed 8건 중 |
| 당뇨약 | 8 | seed 9건 중 |
| 항생제 | 8 | seed 14건 중 |
| 항히스타민/알레르기약 | 7 | seed 7건 중 |
| 고지혈증약/스타틴 | 7 | seed 7건 중 |
| 수면/진정/정신건강 | 5 | seed 5건 중 |
| 골다공증/여성건강/빈혈 | 4 | seed 8건 중 |
| 갑상선약 | 2 | seed 3건 중 |

→ 공백이 크고 기존 relation 과 계열 인접성이 높은 카테고리(기타 PPI·스타틴·치아지드 유사·당뇨 외 대사·비스포스포네이트 인접)를 relation 확장 우선순위로 둔다. 상세는 `MediStack_relation_expansion_priority_plan.md`.

---

## 재현 / 무변경 보증

```
python3 scripts/match_popular_drugs_coverage.py            # CSV + 본 문서
python3 scripts/match_popular_drugs_coverage.py --no-write # 콘솔만
```

본 분석은 seed CSV · full index · relation_card 스냅샷 · alias · export 를 **읽기만** 한다. published / clinical_reviewed = false 유지. relation/full index/alias/export/src 무변경.
