# MediStack — coverage-queue relation factory batch2 보고 (v1.2+)

> 작성일: 2026-06-14. **데이터/코드/렌더/DATA_URL/기존 validator 무변경(라이브 relations 57 그대로).** 본 라운드는 coverage 우선순위 큐(Top100) 기반 **대량 precheck → 안전후보 nedrug 실측 source check → 적대적 검증 → draft batch 생성 → 검증/문서화**까지만 수행했고 **라이브 relation 통합은 0**이다.
>
> 선행/연계(자기완결 인계): `CLAUDE.md` · `MediStack_relation_factory_source_check_v1_2.md`(직전 라운드 75후보) · `MediStack_coverage_kpi_analysis_v1_2.md`(KPI 방법론) · `MediStack_coverage_kpi_batch2_impact_v1_2.md`(이번 KPI 영향) · `MediStack_source_policy_literature_hold_v1_2.md`(source-policy) · `MediStack_potassium_draft_hold_review_v1_2.md`(칼륨 hold).
>
> **정체성(불변):** MediStack 은 식약처 허가사항 기반 약-영양소 **참고정보 베타**. 진단·처방·복약지시·영양제 추천·구매 동선 아님. published / clinical_reviewed = **false 봉인 유지**.

---

## 0. 한 줄 요약

coverage 우선순위 큐 **Top100**(품목수 proxy)을 후보 소스로, **precheck 분류기(병렬 4 + false-reject 복구 비평가)** 가 100건을 정밀 분류 → 안전·관계개연 후보 **2건만** nedrug 허가사항 실측 source check → **적대적 검증(독립 회의론자 3, 라벨 재fetch, refute-by-default)**. 결과 **source_confirmed 1(알마게이트×철분 흡수/간격) · reject 1(보노프라잔×철분)**. confirmed 1건만 **draft batch(CQF01)** 로 생성(라이브 미반영·`live_integration_forbidden=true`). **어떤 라이브 데이터도 변경하지 않았다**(relations 57 · DATA_URL v0.2 · published/clinical false 전부 불변).

> 🎯 이번 배치의 1원칙: **"많이 처리하는 것보다 잘못된 relation을 막는 것이 우선."** Top100 고품목 약은 대부분 허가사항에 영양소 상호작용이 없어(NSAID·항히스타민·PDE5·5ARI·가바펜티노이드·치매약 등) **rejected_precheck 72건**으로 분리했고, 영양소 관계가 실재하는 계열은 이미 covered거나 직전 라운드에 처리됨. **정직한 소규모 산출(confirmed 1)** 이 올바른 결과다. 처리량 부풀리기 없음.

---

## 1. 작업 범위

| 단계 | 내용 | 산출물 |
|---|---|---|
| A precheck | Top100 성분 100건 → rejected_precheck/sensitive_hold/source_check_candidate/already_covered 분류 + false-reject 복구 | `data/coverage_queue_precheck_v1_2.csv` |
| B source check | 안전후보 2건 nedrug `searchDrug`→`getItemDetail`→detector 실측 | `scripts/verify_coverage_queue_sources_v1_2.py`, `data/coverage_queue_source_check_v1_2.csv` |
| C 적대적 검증 | confirmed 1건 독립 회의론자 3 라벨 재fetch·6렌즈 반증 | `data/coverage_queue_adversarial_verify_v1_2.json` |
| D draft batch | adversarial confirm 만 draft(라이브 미반영) | `scripts/build_coverage_queue_draft_batch_v1_2.py`, `data/coverage_queue_draft_batch_v1_2.json` |
| H 검증 | 금지어 스캐너 확장 + batch2 validator/smoke 신규 + 전체 회귀 | `scripts/validate_coverage_queue_draft_batch_v1_2.py`, `scripts/smoke_coverage_queue_draft_batch_v1_2.py` |

---

## 2. Top100 선별 기준 (precheck)

후보 소스 = `data/coverage_kpi_top_candidates_v1_2.csv` 의 Top100(품목수 proxy desc). 분류 원칙:

- **결정론적 detector 5영양소(칼륨·마그네슘·철분·칼슘·아연)만 source_check_candidate 대상.** B12·엽산·CoQ10·비타민D·나트륨 등은 detector 부재 → literature/rejected.
- **품목수가 많다는 이유만으로 후보화 금지.** 허가사항에 영양소 고갈/흡수 동거어가 약리학적으로 실재할 개연이 있는 약만 source_check_candidate.
- 자동 제외(hold/needs_review 분리): **정신건강 · 항응고/항혈전/항혈소판 · 항암 · 임신/수유/소아 · 칼륨 상승방향(ARB/사르탄·칼륨보존이뇨제) · 허브/건기식 · 국내 허가 확인 어려움.**
- relation 후보성이 낮은 항목은 source fetch **전에** `rejected_precheck` 로 분리해 불필요한 fetch 제거.
- 각 후보마다 source check 전에 **분류 사유(reason)** 1차 기록(CSV reason 컬럼).

### precheck 결과 (100건)

| precheck_class | 수 | 의미 |
|---|---|---|
| **rejected_precheck** | **72** | 허가사항 5영양소 depletion/absorption 개연 낮음(fetch 불필요). literature_only(스타틴×CoQ10·H2×B12)·방향상승(SGLT2i×Mg)·주사제·국소제·나트륨/CoQ10(detector 부재) 포함 |
| **sensitive_hold** | **18** | 민감 카테고리(정신건강·항혈전·칼륨상승 ARB 등). fetch 금지·검토만 |
| **already_covered_or_drafted** | **8** | 이미 live relation covered(라베프라졸·메트포르민·HCTZ·레보플록사신·시프로플록사신·이반드론산·알렌드론산) 또는 draft(메틸프레드니솔론×칼륨=DF01 보류) |
| **source_check_candidate** | **2** | 안전·관계개연 — 실측 fetch 대상(알마게이트×철분, 보노프라잔×철분) |

- **precheck rejected(precheck-거른) 수: 72**(+민감 18 = 90건 fetch 제외). 큐가 명목상 source_check_candidate로 넘긴 87건을 **2건으로 좁혀 ~85건의 불필요/위험 fetch를 제거**.
- **false-reject 복구 비평가 결과: 복구 0건.** rejected 72건 전부 reject 유지가 정당함을 직전 라운드 실측(세파클러·세팔로스포린 스윕·H2×B12·레보티록신×Mg/아연 모두 label_missing) 인용으로 확인. 세팔로스포린 철 킬레이션은 세프디니르 성분특이이며 계열효과 아님(계열 일반화 금지 재확인).

---

## 3. source check 처리 결과 (2건)

| candidate | 관계 | itemSeq | 결과 | 근거/사유 |
|---|---|---|---|---|
| 알마게이트 × 철분 | absorption/separation | 199501234 (대원알마게이트정) | **source_confirmed** | 상호작용: "철(Fe)염 제제 : 흡수를 감소시킬 수 있으므로 2∼3시간 간격을 두고 복용한다" |
| 보노프라잔 × 철분 | absorption/separation | 202600069 | **reject** | 라벨의 철 등장은 "철결핍성 빈혈"(이상반응)·"혈액 철 감소/증가"(검사치 이상반응)뿐 — 흡수저해/병용간격 상호작용 아님 |

- **source check 처리 수: 2**
- **confirmed_before_adversarial: 1** (알마게이트×철분)
- **reject: 1** (보노프라잔×철분)
- **needs_review: 0**, **hold: 0**

### 🔬 detector 갭 발견·보강 (이번 라운드 핵심 기술 산출)

결정론적 iron detector(`verify_factory_sources_v1_2.d_iron_absorption`)가 **알마게이트를 처음 false-reject** 했다. 원인: 라벨이 `철(Fe)염` 으로 표기(철과 염 사이 `(Fe)` 삽입)해 기존 정규식 `철염` 패턴을 미스. **라벨 원문 직접 grep 검증**으로 진짜 동거어를 확인하고, batch2 스크립트 안에서 **보강 detector(`d_iron_absorption_v2`, `철\(Fe\)염?` 패턴 추가)** 로 메워 confirmed 로 정정. (직전 라운드 파일은 불변 유지 — 보강은 batch2 스크립트 내부에서만.)

> **함의(차기 PM 검토 후보):** 직전 라운드 세팔로스포린×철 reject 들도 라벨이 `철(Fe)염` 표기였다면 false-reject 가능성. 단 그것들은 이미 처리·covered/index 트랙이고 계열일반화 금지 대상이라 이번 범위 밖. 차기 batch에서 보강 detector 로 재스윕 가치 있음.

---

## 4. 적대적 검증 (confirmed 1건)

알마게이트×철분 confirmed 를 **독립 회의론자 3** 이 itemSeq 199501234 라벨을 각자 재fetch 해 6렌즈 반증(refute-by-default):

| 렌즈 | 결과 |
|---|---|
| nutrient_co_listed (상호작용 문맥 명시, 첨가제 아님) | ✅ 전원 |
| direction_correct (흡수 감소 + 복용 간격 = absorption/separation) | ✅ 전원 |
| negation_absent ("영향 없음/임상적 관련성 없음" 부정문구 없음) | ✅ 전원 |
| domestic_single_oral_product (대원알마게이트정 단일성분 경구정) | ✅ 전원 |
| not_class_overreach (알마게이트 자신의 라벨, 타 제산제 일반화 아님) | ✅ 전원 |
| copy_reads_as_reference_not_instruction (참고정보 톤) | ✅ 전원 |

- **confirmed_after_adversarial: 1** (3/3 confirm, refuted 0).
- 한 회의론자가 카피 방향 뉘앙스("철분이 영향" vs "알마게이트가 철 흡수 감소")를 짚었으나 separation 방향 일치·참고톤이라 중대 결함 아님으로 판단.

---

## 5. draft batch (1건 · 라이브 미반영)

`data/coverage_queue_draft_batch_v1_2.json` (`live_integration_forbidden=true`):

| draft | 관계 | 기전 | display_text_ko | management_ko |
|---|---|---|---|---|
| **CQF01** | 알마게이트 × 철분 | absorption/separation | "알마게이트을(를) 복용하는 경우 철분과(와) 같은 시간대 복용 시 흡수에 영향이 있을 수 있어, 시간 간격을 두는 것이 도움이 될 수 있습니다." | "구체적인 간격이나 보충 여부는 약사 또는 의사와 상담하세요." |

- 봉인 플래그 전건: `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란 · `source_confirmed=true` · `do_not_implement_yet=true` · `review_required=true` · `source_required=true` · `live_integration_forbidden=true` · `requires_clinical_review=false`.
- 비-칼륨 행 → `potassium_safety_card=false`. evidence_level=high(상호작용 직접 listing). 칼륨 행 0.
- draft id `CQFxx` 는 라이브 id 공간 및 직전 라운드 `DF01-07` 과 분리.

---

## 6. reject / needs_review / hold 주요 사례

- **주요 reject:** 보노프라잔×철분(라벨 철 = 빈혈 이상반응이지 흡수상호작용 아님 — 과다해석 방지). precheck rejected 72 중 대표: 클래리트로마이신/록시트로마이신×미네랄(마크로라이드는 킬레이션 없음=퀴놀론/테트라 특이), 세파클러×철(세팔로스포린 철 킬레이션은 세프디니르 성분특이·계열일반화 금지), 스타틴×CoQ10(detector 부재 literature_only), SGLT2i×Mg(혈청 Mg **상승**=방향 불일치), 세프트리악손(주사제 전용).
- **주요 needs_review:** 이번 배치 0건(2건 모두 itemSeq 확보).
- **주요 hold(sensitive):** 쿠에티아핀·에스시탈로프람·플루옥세틴·리스페리돈(정신건강), 리바록사반·아픽사반·클로피도그렐·사르포그렐레이트(항혈전/항혈소판), 로사르탄칼륨·발사르탄·텔미사르탄·칸데사르탄·피마사르탄(+combo)(ARB = 칼륨 상승방향) — fetch 자체를 하지 않음(검토만).

---

## 7. coverage KPI 현재/예상 변화

(상세: `MediStack_coverage_kpi_batch2_impact_v1_2.md`)

| KPI | 현재(relations 57) | CQF01 승격 시 예상 |
|---|---|---|
| ① Top300 성분 coverage | 23/300 = **7.67%** | 24/300 = **8.00%** (+1 성분) |
| ② Top300 품목수가중 coverage | 1044/13268 = **7.87%** | 1098/13268 = **8.28%** (+54 품목) |

- source-check 효율: 큐 87 → precheck 2 fetch(절약 85) → **confirmed 1 / processed 2 = 50%**.
- 품목수 proxy 한계 문서에 유지(검색량 아님·처방/복용빈도와 다름·공백≠relation 대상). 외부 실데이터 미확보 → 추측 금지·limitation 유지.

---

## 8. DF01–DF05 칼륨 hold 문구 점검 결과

(상세: `MediStack_potassium_draft_hold_review_v1_2.md` §3.3 — 이번 라운드 보강)

- management "**보충 여부는 반드시 의사 또는 약사와 상담하세요**" 의 "반드시" 가 금지어 정책과 **충돌하지 않음(실측 PASS).** FORBIDDEN 의 "반드시 드"(=복용 권유)만 금지이고 "반드시 ... 상담"은 비대상.
- 더 안전한 대안 문구 "**칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요**" 도 금지어 0 — **directive 강도(명령조)를 낮추는 톤 개선 옵션**으로 PM 판단 보관. 기본값=현재 유지.
- 칼륨 제품 링크/추천/구매/제휴 계속 금지 유지.

---

## 9. 검증 결과 (전수 PASS · 라이브 무변경)

- **신규 게이트:** 금지어 스캐너 PASS(0/166) · coverage-queue draft validator PASS(27/27) · coverage-queue draft smoke PASS(1 render-safe).
- **기존 회귀 전수:** v0.1 export(12/12)·v0.2 export(15/15)·v0.3 alias(16/16)·alias surface·full drug index·potassium name-only·relation draft v1.2·factory draft batch·factory integration·relation expansion draft·combo approved·라이브 relation draft smoke·disclaimer/alias/hctz/search-regression smoke·unit(combo_ar·v0_3_combo·v0_3_typeB) **전부 PASS**.
- **라이브 데이터 무변경:** `git diff` — export/full index/alias/src/.github **변경 0**. tracked 변경은 금지어 validator(강화)·칼륨 hold 문서(보강) 2개뿐. 나머지 batch2 산출물은 전부 신규 untracked.
- **위험문구·제품 UI 0:** 카피 금지어 0, 외부링크=nedrug 출처만, 제품/구매/제휴 UI 0.

---

## 10. 금지선 준수 (본 라운드)

- ✅ **live relation 통합 0**(relations 57 그대로) · export/full index/alias/src/.github 무변경 · DATA_URL v0.2 유지.
- ✅ published / clinical_reviewed **false 유지** · reviewed_by 공란.
- ✅ source_confirmed 없는 후보 draft/live 승격 0 · **high_risk/sensitive hold draft/live 혼입 0**(검증기 강제).
- ✅ 계열 일반화 0(세팔로스포린 철·마크로라이드 등) · 과다해석 0("영향 없음/빈혈 이상반응" → reject) · 칼륨 상승방향 ARB 전부 hold.
- ✅ "식약처 승인 / 법적 문제없음 / 약사 검수 완료 / 추천 영양제 / 복용하세요 / 치료 / 예방 / 구매 / 제휴" 어휘 0(스캐너 PASS).

---

## 11. 다음 PM 판단 필요사항

1. **CQF01(알마게이트×철분) live 승격 여부.** 근거 강함(허가사항 상호작용 직접 + 적대적 3/3 confirm), 안전(흡수/간격, low risk, 칼륨 무관). 승격 시 relations 57→58, 알마게이트 품목 relation_card flip, KPI① 7.67→8.00% / KPI② 7.87→8.28%.
2. **iron detector 보강 재스윕 여부.** `철(Fe)염` 표기 갭이 직전 세팔로스포린×철 reject 에 영향 줬을 가능성 — 차기 batch에서 보강 detector 로 재확인(단 계열일반화 금지·세프디니르 성분특이 유지).
3. **Top101–300 확장 여부.** 이번은 Top100 한정. Top101–300 에 PPI(저마그네슘·철 흡수)·추가 이뇨제 등 **허가사항 동거어 풍부 계열**이 더 있을 것(품목수 proxy 낮아질 뿐 관계 개연은 높음) → 차기 우선 후보군.
4. **source-policy(literature_only) 결정.** 스타틴×CoQ10·H2×B12 = 허가사항 미기재. Option A(허가사항만)/B(이차문헌 draft 허용)/C(reviewed_reference 트랙) 중 선택(상세 `MediStack_source_policy_literature_hold_v1_2.md`). 현재 기본=Option A.

---

## 12. 장기 로드맵 (구현 없이 유지)

- 우리영양소 연동 = **비커머스 import/export 편의 기능만**(제품/구매/제휴 아님).
- saved_stack / 가족 / 그룹 / 구독 = **보류**(coverage·UX 안정화 전 구현 금지).
- 약사 참여 = 추천 권한 아니라 **문구 검수 / 품질 자문 / 상담 신뢰** 확보용.
- 유료화 / 결제 / 구독 = **coverage·saved_stack 안정화 이후**.

---

## 13. 다음 Claude Code 프롬프트 (2개)

### 프롬프트 1 — CQF01 live 승격 (PM 승인 후)

```
메디스택 coverage-queue draft CQF01(알마게이트×철분 흡수/간격)을 live 승격한다.
현재: relations 57, draft=data/coverage_queue_draft_batch_v1_2.json (live_integration_forbidden=true).
선행 필독: docs/MediStack_coverage_queue_factory_batch2_report_v1_2.md, CLAUDE.md, integrate_relation_draft_v1_2.py(승격 패턴).
작업: 멱등 통합기로 신규 relation id=59, draft 전용 필드 미누출, 알마게이트 full index flip(relation_card)·verified_item_seqs,
meta.relation_count 갱신, published/clinical false·DATA_URL v0.2 유지. 통합 후 validator/smoke 전수 + 신규 통합검증기 PASS 아니면 commit 금지.
금지: 미승인 행 승격, 칼륨/민감 혼입, published/clinical 전환.
```

### 프롬프트 2 — Top101–300 + iron detector 재스윕 (차기 batch3)

```
메디스택 coverage-queue factory batch3: Top101–300 + iron detector 보강 재스윕.
선행 필독: docs/MediStack_coverage_queue_factory_batch2_report_v1_2.md(§3 detector 갭·§11 PM 판단), CLAUDE.md.
작업: ①precheck 분류기로 Top101–300 source_check_candidate 선별(PPI 저마그네슘/철흡수·추가 이뇨제 등 동거어 풍부 계열 우선)
②d_iron_absorption_v2(철(Fe)염 보강)로 안전후보 실측 source check ③적대적 검증 ④confirmed만 draft(라이브 미반영) ⑤validator/smoke 전수.
금지: live 통합(별도 승인), source_confirmed 없는 승격, high_risk/sensitive hold 승격, 계열 일반화, 유료화/saved_stack 구현.
```

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / source_confirmed 없으면 draft·live 승격 금지 / high_risk·sensitive hold 승격 금지 / 계열 일반화 금지 / live relation 통합은 PM 승인 별도 단계 / 유료화·saved_stack·Supabase·우리영양소 연동은 coverage·UX 목표 달성 전 구현 보류.
