# MediStack — coverage KPI batch2 영향 분석 (v1.2+)

> 작성일: 2026-06-14. **분석 전용 — 데이터/렌더/relation 한 줄도 변경하지 않는다.** 재현: `python3 scripts/analyze_coverage_kpi_v1_2.py --no-write`(현재) + 본 문서의 projection(알마게이트 가산).
>
> 선행: `MediStack_coverage_kpi_analysis_v1_2.md`(KPI 방법론·한계) · `MediStack_coverage_queue_factory_batch2_report_v1_2.md`(이번 배치). 목적: 이번 batch2 source check 결과가 coverage 에 어떤 영향을 줄 수 있는지 **draft 기준으로 추정**한다.

---

## 0. 방법과 한계 (반드시 같이 읽기)

- **복용빈도 proxy = full index(MFDS 실품목 17,580)의 성분별 품목수.** 실측 검색량/처방통계가 아니다.
- **한계(명시·불변):** ①품목수 ≠ 실제 검색량/복용량(인지도·약가·만성 vs 급성 사용기간·OTC 비중 미반영). ②coverage 공백이 곧 'relation 대상'은 아니다 — **상호작용 근거(허가사항 동거어)가 없는 성분이 다수**(이번 Top100 에서 72/100 이 rejected_precheck). ③인덱스는 확장 중 샘플. → 결과는 **확정 랭킹이 아니라 우선순위 후보 큐**다.
- **외부 실데이터 미확보.** 처방통계/검색량 확보 전까지 내부 index proxy ranking 만 사용. **추측으로 채우지 않는다(limitation 유지).**

---

## 1. 현재 coverage (라이브 relations 57, base 성분 24)

| KPI | 값 |
|---|---|
| ① Top300 성분 coverage | **23/300 = 7.67%** |
| ② Top300 품목수가중 coverage | **1044/13268 = 7.87%** |
| source-check 우선순위 큐(미커버·비민감) | 258 |

> 직전 라운드(DF06/DF07 리오티로닌 승격 후) 기준선과 동일. 이번 batch2 는 **라이브 미반영**이라 현재 KPI 불변.

---

## 2. 이번 batch2 draft 가 승격될 경우 예상 coverage

이번 라운드 source_confirmed + 적대적 통과 = **CQF01 알마게이트×철분 1건**. 알마게이트 = Top300 rank **77**, product_count **54**, 현재 relation_card **0**(전부 name_only).

| KPI | 현재 | CQF01 승격 시 예상 | Δ |
|---|---|---|---|
| ① Top300 성분 coverage | 23/300 = 7.67% | **24/300 = 8.00%** | +1 성분 (+0.33%p) |
| ② Top300 품목수가중 coverage | 1044/13268 = 7.87% | **1098/13268 = 8.28%** | +54 품목 (+0.41%p) |

> 단일 relation 의 coverage 기여는 작다(성분 1·품목 54). 이는 **정상**이다 — 이번 배치 목적은 coverage 점프가 아니라 **잘못된 relation 없이** 안전후보를 정직하게 추가하는 것. 큰 coverage 레버는 §4(다계열·literature_only)에 있다.

---

## 3. 여전히 미커버인 Top 주요 성분 (차기 후보 신호)

Top100 미커버 중 **이번에 reject/hold 된 이유와 함께**:

| 성분(대표) | rank | 분류 | 사유 |
|---|---|---|---|
| 프레가발린·가바펜틴·도네페질·메만틴 | 1·15·11·28 | rejected_precheck | 허가사항 5영양소 상호작용 없음 |
| NSAID(아세클로페낙·이부프로펜·록소프로펜…) | 13·43·17… | rejected_precheck | 영양소 고갈/흡수 동거어 없음 |
| 스타틴(로수바스타틴·아토르바스타틴·심바스타틴) | 31·52·76 | rejected_precheck | CoQ10 = detector 부재·literature_only(§4) |
| H2(파모티딘·니자티딘·라푸티딘) | 30·88·89 | rejected_precheck | B12 = detector 부재·literature_only(§4) |
| ARB(로사르탄칼륨·발사르탄·텔미사르탄·칸데사르탄) | 34·48·70·85 | sensitive_hold | 칼륨 상승방향(고칼륨혈증) — depletion 범위 밖 |
| SGLT2i(다파/엠파글리플로진) | 56·86 | rejected_precheck | 혈청 Mg **상승**(고갈 아님)·방향 불일치 |
| 정신건강(쿠에티아핀·에스시탈로프람·플루옥세틴) | 19·33·27 | sensitive_hold | 민감 카테고리 |

> 결론: **Top100 미커버의 대부분은 "아직 안 만든 것"이 아니라 "허가사항 근거가 없어 만들면 안 되는 것"이다.** coverage 공백 ≠ relation 대상이라는 한계가 실증됨.

---

## 4. coverage 확장 레버 (PM 결정 필요)

이번 Top100 한정 batch 로는 큰 점프가 없다. 더 큰 레버:

1. **Top101–300 의 동거어 풍부 계열.** 품목수 proxy 는 낮아지지만 관계 개연이 높은 계열(PPI 저마그네슘/철 흡수, 추가 이뇨제, 비스포스포네이트, 추가 갑상선호르몬 등)이 Top101–300 에 더 있을 것. 차기 batch3 우선 후보.
2. **source-policy(literature_only) 해금 시.** 스타틴×CoQ10(name_only 합 다수)·H2×B12 등 — 허가사항 미기재라 현재 reject. Option B/C 채택 시 coverage 대폭 확장 가능(단 정체성 변경, `MediStack_source_policy_literature_hold_v1_2.md` 참조).
3. **iron detector 보강 재스윕.** `철(Fe)염` 표기 갭으로 직전 세팔로스포린×철 등에 false-reject 가능성 — 재확인 시 소폭 회수 가능(계열일반화 금지 유지).

---

## 5. source-check 효율 (이번 라운드)

| 지표 | 값 |
|---|---|
| Top100 중 큐 명목 source_check_candidate | 87 |
| precheck 후 실제 fetch 대상 | **2** |
| precheck 로 제거한 fetch | **~85** (rejected_precheck 72 + sensitive 분리) |
| source check 처리 | 2 |
| confirmed / processed | **1 / 2 = 50%** |
| false-reject 복구(recovery) | 0 (1차 분류 정당) |

> precheck 의 가치 = **fetch 절약 + 잘못된 후보 사전 차단.** 87건 전부 fetch 했다면 대부분 reject 였을 것을, precheck 가 2건으로 좁혔다.

---

> **안전 원칙:** "식약처 승인 / 법적 문제없음 / 약사 검수 완료 / 추천 영양제" 표현 미사용. 품목수 proxy 한계 유지. 외부 실데이터 없으면 추측 금지·limitation 으로 남김. coverage 공백 ≠ relation 대상.
