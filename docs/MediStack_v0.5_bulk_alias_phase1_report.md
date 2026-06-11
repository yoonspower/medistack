# MediStack v0.5 — bulk alias pipeline Phase 1 보고서

작성일: **2026-06-11** / 단계: **Phase 1(skeleton) 구현 완료, alias JSON 미반영** / 상위 설계: `MediStack_v0.5_bulk_alias_pipeline_plan.md`

> PM 판정(v0.5 Phase 1): 목표 alias 200·batch 30·review queue JSON+CSV·itemSeq는 getItemDetail/공식 원문 확정 필수·v0.5는 alias만 확장(relation 불변)·brand_core 자동 편입 금지(별도 tier)·approved/rejected/deferred workflow·DATA_URL 변경은 별도 게이트·실제 alias JSON 반영은 아직 안 함.
> 이 단계 산출물: **후보 생성기 + 후보 검증기 + review queue(JSON/CSV) + 본 보고서**. `data/medistack_v0.3_aliases.json` 미수정, alias_count 66·relation 30·DATA_URL 불변.

---

## 1. 작업 목적
v0.5 대량 alias 확장(목표 200)을 **사람이 손으로 한 건씩** 넣는 방식이 아니라, **자동 후보 생성 → 자동 검증 → 사람 승인 → batch 반영** 파이프라인으로 전환한다. Phase 1은 그 파이프라인의 **뼈대(skeleton)와 review queue 스키마를 고정**하는 단계다.
- 이번 단계는 **외부 API 대량 호출 없이** 내부 데이터(현행 alias 파일·relations export)만으로 후보 생성기·검증기·큐 포맷을 확정한다.
- 실제 alias 편입(approved → alias JSON 반영)은 **하지 않는다.** 모든 후보는 `pending/deferred/rejected` 로만 나오고 `approved` 는 0건이다.
- 후보가 적게 나오는 것은 실패가 아니다. **파이프라인 골격·스키마·안전 게이트 검증이 목적**이며, 대량 후보는 Phase 2(외부 소스)에서 채운다.

## 2. 생성기 / 검증기 파일 설명
### 2.1 `scripts/generate_bulk_alias_candidates.py` (후보 생성기)
- 입력(읽기 전용): `data/medistack_v0.3_aliases.json`, `data/medistack_v0.2_beta_export.json`.
- 출력: `data/candidates/bulk_alias_review_queue_v0_5.json`(정본) + `.csv`(리뷰 보조).
- 허용 canonical = **라이브 relation 성분 − 에스오메프라졸 − excluded 전용 성분 = 13종**. 그 외 성분은 후보를 만들지 않는다(스킵 카운트만 기록).
- 안전 게이트(코드 강제): 에스오메프라졸/15행/excluded 후보 미생성 · 에스오메프라졸 대표 itemSeq(`201600209`) 등장 금지 · 기존 66 alias 와 정규화 중복 제외 · **itemSeq 는 검증된 기존 제품 alias 에서 상속만(미검증 값 생성 금지)**.
- Phase 1 생성 규칙:
  - **R-BC(brand_core 추출)**: 검증된 product alias 표면형에서 용량·제형 토큰을 제거해 브랜드 코어 후보를 만든다. 코어가 기존 성분명(전체)을 포함하면 제네릭/제조사+제네릭으로 보고 **자동 거부(candidate_type=rejected)**, 그 외는 **brand_core(status=deferred)**.
  - **R-TA(Type A 변형)**: 내부 seed 기반. v0.4 에서 표준 성분 변형을 이미 흡수하여 **현재 seed 비어 있음 → 산출 0**. 코드 경로만 유지(대량 Type A 는 Phase 2 외부 소스).
- **idempotent**: 타임스탬프는 고정 상수(런타임 now() 미사용) → 재실행 시 바이트 동일, git diff 안정.

### 2.2 `scripts/validate_bulk_alias_candidates.py` (후보 검증기)
review queue 가 안전 게이트를 지키는지 16개 항목으로 검사(승인 export 우회 차단). FAIL 시 `X #N` 형식 출력(greppable):

| # | 검사 |
|---|---|
| 1 | queue JSON 구조(meta + candidates 리스트) |
| 2 | CSV parse·필드 완비·행수 == JSON |
| 3 | 필수 16필드 존재 + 핵심 필드 비어있지 않음 |
| 4 | status ∈ {pending,approved,rejected,deferred} |
| 5 | candidate_type ∈ {ingredient,product_full_name,brand_core,rejected} |
| 6 | 큐 내부 candidate_alias 중복 금지(정규화) |
| 7 | 기존 alias(66)와 중복 금지 |
| 8 | canonical_ingredient ∈ 허용 canonical(신규 relation 금지) |
| 9 | 에스오메프라졸/15행/excluded·금지 itemSeq 차단 |
| 10 | brand_core approved 금지(별도 tier) |
| 11 | approved 는 ingredient/product_full_name 만(rejected/brand_core approved 금지) |
| 12 | approved 완전성(source_method·source_checked_at·reviewer 필수) |
| 13 | approved product_full_name 은 숫자형 item_seq 필수 |
| 14 | batch_id 존재(모든 행) |
| 15 | JSON↔CSV (alias,status) 정합 |
| 16 | alias JSON 무변경(alias_count 66·항목 66·relation 30) |

> 검증기 음성 테스트(ephemeral): 에스오메프라졸 후보→#8·#9 / 금지 itemSeq→#9 / approved brand_core→#10·#11 / 기존66 중복→#7 / 잘못된 status→#4 / approved 미완성→#12 / item_seq 없는 approved product→#13 / batch_id 없음→#3·#14 — 9/9 정확 포착(no-op 아님 확인).

## 3. review queue 스키마(16필드)
정본 = JSON(`{meta, candidates[]}`), 보조 = CSV(동일 필드, 사람 검토 편의상 `canonical_ingredient·candidate_alias·status·reason·risk_level` 를 앞쪽에 배치).

| 필드 | 의미 |
|---|---|
| candidate_alias | 후보 검색어(표면형) |
| candidate_type | ingredient / product_full_name / brand_core / rejected |
| canonical_ingredient | 귀속 라이브 성분(허용 canonical) |
| item_seq | 식약처 itemSeq(검증 상속, 미검증 생성 금지) |
| item_name | 근거 품목명 |
| ingr_name | 주성분명 |
| source_url | 원문 URL(getItemDetail 등) |
| source_method | 확정/유래 방법 |
| source_checked_at | 원문 확인일 |
| confidence | low/medium/high |
| risk_level | low/medium/high |
| reason | 후보 사유 |
| status | pending / approved / rejected / deferred |
| exclusion_reason | 거부·보류 사유 |
| reviewer | 승인자(approved 시 필수) |
| batch_id | 배치 식별자 |

승인 규칙(검증기 강제): `approved` 는 source_method·source_checked_at·reviewer 가 모두 있어야 하고, brand_core·rejected 는 approved 불가, product_full_name 은 숫자형 item_seq 필수.

## 4. 생성 후보 수
- **허용 canonical**: 13종(라이브 14 − 에스오메프라졸).
- **외부 API 호출**: 0회.
- **총 후보**: **16건**.
- 기존 66 alias 와 중복으로 제외(dedup): 11건. 에스오메프라졸/excluded 스킵: 0건(해당 성분은 alias 자체가 없음).

## 5. status 분포
| status | 수 | 비고 |
|---|---|---|
| pending | 0 | Type A seed 비어 있음(v0.4 흡수 완료) |
| approved | **0** | 이번 단계 승인·반영 없음(설계상) |
| rejected | 2 | 제네릭/제조사+제네릭 코어 자동 거부(국제독시사이클린… ×2) |
| deferred | 14 | brand_core(별도 tier, 사람 검토 대기) |

deferred 14건 = 검증된 4개 신규 제품(모록사신정·미노젠캡슐·라이트알렌드론정·세토람정) 및 대표 제품들의 브랜드 코어 변형(예: 모록사신/모록사신정, 미노젠/미노젠캡슐, 토렘정, 리목스정, 시프로민정, 제일타리비드, 바이포민서방정 등). 전부 검증된 itemSeq 상속.

## 6. 왜 이번 단계에서 alias JSON을 수정하지 않았는가
1. **PM 판정 #9**: 실제 alias JSON 반영은 아직 안 함. 이번 목표는 파이프라인 골격·스키마 확정.
2. **승인 절차 분리**: 후보(pending/deferred) → 사람 검토 → approved → batch 반영. Phase 1 에 approved 가 0건이므로 반영할 것이 없다.
3. **brand_core 보류(PM #6)**: 이번 산출의 14건은 전부 brand_core(deferred). 자동 편입 금지 tier 라 alias JSON 에 넣지 않는다.
4. **불변식 보호**: alias_count 66·relation 30·DATA_URL 유지. 후보 파일은 `data/candidates/` 에만 생성(앱·검색 인덱스 미참조).

## 7. Phase 2에서 외부 nedrug/data.go.kr 연동이 필요한 이유
- **Type A 고갈**: 안전한 영문 INN/한글 표기/약칭 변형은 v0.4 에서 대부분 흡수됨. 내부 데이터만으로는 **추가 성분 변형이 거의 안 나온다**(현재 pending 0).
- **목표 200 도달 불가(내부만으로)**: 현재 라이브 14성분 × 소수 변형으로는 66 근처가 한계. 200 으로 가려면 **성분별 다수 완제품(제네릭) 품목명**이 필요하고, 이는 외부 소스에만 있다.
- **itemSeq 원문 확정 필수(PM #4)**: product_full_name 후보는 `getItemDetail(itemSeq)` 로 품목명·주성분·성분코드를 원문 확정해야 approved 가능. Phase 1 은 미검증 itemSeq 를 만들지 않으므로 product_full_name 후보를 신규 생성하지 않았다.
- Phase 2 작업(생성기 `phase2_todo` 에 명시):
  1. nedrug `searchDrug?ingrName1=<성분>` → 성분별 완제품 목록 수집.
  2. `getItemDetail?itemSeq=<seq>` → 품목명·주성분·성분코드 원문 확정 → product_full_name 후보.
  3. data.go.kr OpenAPI → 제네릭 품목명 대량 수집(제형·중복 필터).
  4. brand_core deferred 후보 사람 검토 → tier 결정.

## 8. v0.5 목표 200까지 가기 위한 다음 단계
1. **Phase 2 수집기**: nedrug searchDrug(이미 v0.4 에서 경로 검증됨) 우선, data.go.kr serviceKey 발급되면 병행. 성분 13종 × 완제품 N → product_full_name 후보 대량.
2. **itemSeq 원문 확정 루프**: getItemDetail 로 품목명·주성분 일치 확인(에스오메프라졸/excluded·금지 itemSeq 자동 차단은 생성기·검증기에 이미 내장).
3. **검토 큐 승인**: deferred/pending → 사람 검토 → approved(reviewer·source 채움). batch 30개 단위.
4. **batch export → alias JSON 반영**: approved 만 모아 alias 추가 + alias_count 갱신 + 기존 v0.3 validator + Type B suite + 후보 검증기 통과 → 커밋/배포. (별도 PM 게이트)
5. 200 도달까지 batch 반복. v0.6(500~1,000)·DATA_URL 전환은 별도 릴리즈 게이트.

추정: 13성분 × 평균 제네릭 ~15품목 → product_full_name 수백 후보 가능 → dedup·검증·검토 후 **batch 30 × 약 5회로 200 도달** 현실적.

## 9. 위험 관리
- **alias=검색 보조, 의학정보 아님**: 후보가 relation 을 신규 생성하지 않음(canonical 허용 집합 강제). 큐는 앱·검색 인덱스가 참조하지 않음.
- **대량 오염 방어**: 자동 생성은 전부 미승인(pending/deferred). approved 는 사람·source·reviewer 강제(검증기 #11~#13). batch 소단위(30) + 반영 시 전 validator 재통과.
- **봉인 항목 우회 차단**: 에스오메프라졸/15행/excluded·금지 itemSeq 는 생성·검증 양쪽에서 차단. brand_core 자동 편입 금지.
- **미검증 숫자 금지**: itemSeq 는 검증 상속만, 신규 product_full_name 은 Phase 2 원문 확정 후에만.
- **idempotent 생성**: 재실행 결과 동일 → 리뷰 diff 안정, 잠재 churn 없음.

## 10. PM 판정 필요사항
1. **Phase 2 수집 소스 우선순위**: nedrug searchDrug 단독 시작 vs data.go.kr serviceKey 발급 병행.
2. **brand_core tier 처리**: 현재 deferred 14건을 (a)계속 보류 (b)일부 approved 승격 검토 (c)v0.6 로 미룸.
3. **rejected 2건 처리**: 큐에 기록 유지(추적용) vs 다음 생성부터 제외.
4. **batch 반영 게이트**: approved batch → alias JSON 반영 시 별도 PM 판정 단계로 둘지(권장: 둠).
5. **product_full_name 수집 범위**: 성분당 상한(예: 제형별 대표 1~2품목) vs 전수 후 dedup.
6. **review queue 파일 위치/버전닝**: batch 별 파일 분리(v0.5-001, -002 …) vs 단일 파일 status 갱신.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포·반영 금지 / alias 는 검색 보조이지 의학정보 아님 / alias 로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증 alias·itemSeq 금지 / 후보는 사람 승인 전까지 미반영.
