# MediStack — coverage KPI 5축 재정의 (v1.2)

> 작성일: 2026-06-14. **설계/분석 전용 — 데이터·렌더·relation 한 줄도 변경하지 않는다.** 이번 라운드 **live 승격 0** (published=false·clinical_reviewed=false 유지). 재현: `python3 scripts/analyze_coverage_kpi_v1_3_draft.py`. 산출 CSV: `data/coverage/top300_kpi_reclassified_v1_2.csv`.
> 선행 문서: `docs/MediStack_coverage_kpi_analysis_v1_2.md`(복용빈도 proxy 랭킹·source-check 큐). 본 문서는 그 위에 **KPI 정의를 5축으로 재정의**한다.
> ground truth 인용(읽기전용): `data/medistack_v0.2_beta_export.json` relations **59건**, source_confirmed 성분(base) **26개**. 이 판정은 앞단계에서 끝났고 본 문서는 인용만 한다 — source_confirmed/draft/live 판정을 새로 하거나 바꾸지 않는다.

---

## 0. 왜 재정의하나 (문제 정의)

기존 목표 **"Top300 relation_card 95%"** 는 부정확하다. 두 가지 잘못된 전제가 깔려 있었다.

1. **"relation_card 없음 = 실패"라는 전제가 틀렸다.** MediStack 검색은 relation_card 가 없어도 **name_only / "관련 참고정보 없음" 안전응답**을 정상적으로 돌려준다. 사용자는 "이 약은 등록된 약-영양소 참고정보가 없습니다" 라는 응답을 받는다 — 이것은 빈 화면도 오류도 아니다. **정보 없음 = 실패가 아니라 안전응답이다.**
2. **분모가 잘못됐다.** Top300 성분 대부분은 애초에 **상호작용 근거(허가사항 동거어)가 없는 일반 성분**이다. 근거 없는 성분까지 분모에 넣고 95% 를 요구하면, 근거 없는 relation 을 억지로 만들라는 압력이 된다 — 안전 원칙 정면 위반.

→ 그래서 단일 비율 대신 **5축**으로 나누고, "무엇을 95% 목표로 삼고 무엇을 삼지 않는지"를 명문화한다.

---

## 1. 5축 KPI 정의

| 축 | 이름 | 정의(분자/분모) | 역할 |
|---|---|---|---|
| ① | **relation_card coverage** | relation_card 보유 성분 / Top300 전체 성분 | 현 기준선. **무리하게 95% 목표 삼지 않음**(근거 없는 relation 강제 금지) |
| ② | **relation-eligible coverage** | source_confirmed 성분 / **eligible 성분만**(근거 개연 계열) | 근거가 있을 개연이 큰 성분을 얼마나 덮었나. **상품 목표축** |
| ③ | **search-response coverage** | 안전응답 가능 성분 / Top300 전체 | "검색하면 무엇이든 안전하게 답한다"는 사용자 체감. **상품 목표축** |
| ④ | **weighted coverage** | relation_card 품목수 / Top300 품목수합 | 복용빈도 proxy(품목수) 가중 실질 커버리지. 현 기준선 |
| ⑤ | **blocked/hold coverage** | 차단·hold 성분 / Top300 전체 | 의도적으로 막은 비율(안전장치가 작동 중이라는 양성 지표) |

### 핵심 원칙: "정보 없음 = 안전응답"

축 ③은 **"relation_card 가 있다"가 아니라 "안전한 응답을 돌려준다"**를 센다. full index(MFDS 실품목 **17,580**) 전체가 최소 name_only 로 응답 가능하므로, 검색 실패(빈 화면·오류·억측)는 구조적으로 0에 가깝다. relation_card 가 없는 성분도 ③에서는 **성공**으로 친다 — 근거 없이 정보를 지어내지 않는 것이 정답이기 때문이다.

---

## 2. 5축 KPI 측정값 (Top300, 스크립트 출력 그대로)

> 출처: `python3 scripts/analyze_coverage_kpi_v1_3_draft.py` 실행 결과(결정론적). 분모 Top300 = 품목수 proxy 상위 300 성분, 품목수합 **13,268**.

| 축 | KPI | 측정값 | 비고 |
|---|---|---|---|
| ① | relation_card coverage(성분) | **25/300 = 8.3%** | 기준선. 목표 95% 아님 |
| ② | relation-eligible coverage | **25/92 = 27.2%** | 분모=eligible(근거 개연 계열) 92개만 |
| ③ | search-response coverage(하한) | **281/300 = 93.7%** | blocked 19건을 보수적으로 분자에서 제외한 하한 |
| ③ | search-response coverage(실질) | **≈100%** | blocked 성분도 name_only 안전응답은 가능 |
| ④ | weighted coverage(품목) | **1,135/13,268 = 8.6%** | 복용빈도 proxy 가중 |
| ⑤ | blocked/hold coverage(성분) | **19/300 = 6.3%** | 전원 민감/고위험군 hold |
| ⑤ | blocked/hold coverage(품목) | **833/13,268 = 6.3%** | — |

> 해석: ①④(8.3%/8.6%)만 보면 "거의 못 덮었다"로 읽히지만, 이는 **분모에 근거 없는 일반 성분이 다 들어가서**다. ②(eligible 27.2%)가 "근거 있을 만한 것 중 실제 덮은 비율"이라 더 정직한 진척 지표이고, ③(≈100%)이 사용자 체감(검색 실패 없음)이다. ⑤(6.3%)는 안전장치가 막고 있는 비율 — 줄이는 게 목표가 아니라 **reviewer 트랙 전까지 유지**해야 하는 양성 신호다.

---

## 3. Top300 5축 재분류 (버킷 분포)

> 산출: `data/coverage/top300_kpi_reclassified_v1_2.csv` (컬럼: `rank,ingredient,product_count,therapeutic_class,relation_card,kpi_bucket,reason`).

| kpi_bucket | 성분수 | 품목수합 | 의미 |
|---|---|---|---|
| `covered` | 25 | 1,135 | relation_card 보유(source_confirmed 근거 존재) → ①④ 산입 |
| `relation_eligible_uncovered` | 67 | 3,189 | 근거 개연 계열인데 미커버 → ② 분모, source-check 우선 대상(**확정 아님**) |
| `blocked_sensitive` | 19 | 833 | 민감/고위험군(정신건강·항혈전·항암) → ⑤ hold |
| `blocked_no_itemseq` | 0 | 0 | item_seq 결손 품목 → relation_card 렌더 불가(이 index 샘플엔 결손 0, **방어적 버킷 유지**) |
| `safe_name_only` | 189 | 8,111 | 근거 약함/일반 계열 → name_only/정보없음 안전응답(③ 성공, **실패 아님**) |
| **합계** | **300** | **13,268** | |

### 버킷 판정 규칙(스크립트와 1:1)

1. `covered` — relation 보유 성분(base) 매칭 OR relation_card 품목 존재.
2. `blocked_sensitive` — 치료군이 정신건강(민감)·항혈전(민감)·항암/면역(민감). 임상판단·출혈/상호작용 위험으로 clinical reviewer 트랙 전까지 hold(factory hold 정책 승계).
3. `blocked_no_itemseq` — 전 품목 item_seq 결손. 허가사항 식별 불가 → relation_card 렌더 차단(현 샘플 0건, 인덱스 확장 시 재발 가능해 버킷 유지).
4. `relation_eligible_uncovered` — 흡수저해/고갈 메커니즘 개연이 큰 계열(소화/위장·항생/항균·골다공증·갑상선/내분비·고혈압/심혈관·당뇨)이면서 미커버. **여기 오른다고 relation 확정이 아니다** — `verify_factory_sources_v1_2.py` 로 허가사항 동거어를 확인해 근거 있는 것만 source-check 통과.
5. `safe_name_only` — 위 어디에도 안 걸리는 나머지. name_only 안전응답 대상.

> eligible 계열 선정 근거: 현 relations 59건의 mechanism 이 **absorption 37 / depletion 22** 로 흡수저해·영양소 고갈 두 축에 집중. 같은 메커니즘이 작동할 개연이 큰 치료군을 eligible 로 추정(킬레이션·다가양이온·전해질 영향 계열). **추정일 뿐 근거 확정이 아님**을 박제한다.

---

## 4. 최종 상품 coverage 목표 제안

> 개수 목표(예: relation 1,000개)·일률 95%를 폐기하고, **축별로 다른 목표**를 세운다.

| 축 | 제안 목표 | 근거 |
|---|---|---|
| ③ **search-response coverage** | **95%+** (실질 ≈100% 유지) | 사용자 체감의 핵심. 검색 실패(빈 화면·억측) 0 유지가 본질. 이미 달성권 — **회귀 방지가 목표** |
| ② **relation-eligible coverage** | **90%+** | 근거 있을 만한 성분은 거의 다 덮는다. eligible 분모만 추적해 정직하게 진척 측정 |
| ① **relation_card coverage** | **목표로 삼지 않음** | 분모에 근거 없는 일반 성분이 다 들어가 95%가 구조적으로 불가능·부적절. **근거 없는 relation 강제 금지**. 참고지표로만 보고 |
| ④ **weighted coverage** | 라운드별 모니터링(절대목표 X) | ②가 오르면 자연 상승. 단독 목표 삼으면 고빈도 성분 편향 유발 |
| ⑤ **blocked/hold coverage** | **유지(축소 금지)** | 민감군 hold 는 안전장치. reviewer 트랙 확보 전까지 6%대 유지가 정상 |

### 목표 운용 규칙

- ②를 끌어올릴 때도 경로는 동일: §3의 `relation_eligible_uncovered` 67건을 source-check 큐로 → 허가사항 동거어 확인 → 적대적 검증 → source_confirmed 만 다음 라운드 후보. **본 문서·스크립트는 그 큐를 만들 뿐 relation 을 생성하지 않는다.**
- ②의 분모(eligible 92)는 추정이므로, source-check 결과 "근거 없음"으로 판명되면 해당 성분은 `safe_name_only` 로 재분류되어 ②분모에서 빠진다. **분모가 줄며 ②가 자동 상향**될 수 있음을 인지(분모 정합성 라운드별 재측정).
- live 승격 0. 본 라운드는 KPI 정의·재분류·목표 설계까지만. 실제 relation 추가·published/clinical 전환은 별도 승인 라운드.

---

## 5. 한계 (반드시 같이 읽기)

- **품목수 = 복용빈도 proxy일 뿐 실측 아님.** 인지도·약가·만성 vs 급성 사용기간·OTC 비중 미반영(선행 v1.2 §0 승계).
- **eligible 분모는 메커니즘 개연 추정.** source-check 전까지 확정 아님. relation 자동 생성 근거로 쓰지 않는다.
- **이 index 는 확장 중 샘플.** item_seq 결손 0은 현 샘플 한정 — 확장 시 `blocked_no_itemseq` 재발 가능(버킷 유지 이유).
- **③ "≈100%"는 구조적 가능성**(name_only 응답 인프라 존재)이지 모든 검색 품질 보장이 아니다. 오타·미수록 신약은 별도 추적.

---

> **안전 원칙(불변):** 정보 없음 = 실패 아니라 안전응답 / coverage 공백 ≠ relation 대상(source-check 로 근거 확인) / eligible 은 추정 분모 / 민감·고위험군 hold 유지 / 이 문서·스크립트는 KPI 정의·재분류이지 relation 생성 아님 / 데이터·렌더·relation 무변경 / published·clinical_reviewed false 유지 / 제품·구매·제휴·추천 0 / '식약처 승인·법적 문제없음·약사 검수 완료·추천 영양제·복용하세요' 표현 0 / 칼륨 보충 권유·결핍 단정 0.
