# MediStack — coverage-queue relation factory batch3 리포트 (v1.2)

> 작성일: 2026-06-14. **draft 전용 — 라이브 relation/full index/alias/export/src 한 줄도 변경하지 않는다.**
> 범위: coverage KPI Top101–200(precheck 대역, cap 100) → precheck 분류 → 안전후보 nedrug source-check →
> 적대적 검증(독립 회의론자 3명·라벨 전문 재대조·refute-by-default·6렌즈) → **만장일치 confirm 만 draft**.
> **batch3 live 통합 금지**(전 draft `live_integration_forbidden=true`). 실제 채택은 PM 승인 + 검토 별도 단계.

---

## 0. 한 줄 결과
Top101–200 precheck 100건 → source_check_candidate 9 → nedrug 실측 source_confirmed 3 →
적대검증 만장일치 confirm **2**(테고프라잔×철분 · 히드로코르티손×칼륨) → draft **CQF02·CQF03**.
펙소페나딘×마그네슘은 적대검증 2/3 split(방향/카피 반론)으로 **needs_review 보류**.

---

## 1. precheck (Top101–200, cap 100)
- 분류 산출: `data/coverage_queue_precheck_batch3_v1_2.csv` (생성기 `scripts/build_coverage_queue_precheck_batch3.py`).
- 후보 발굴: 4 독립 렌즈 병렬(흡수킬레이션·산분비·고갈·완전성비평, medistack-batch3-precheck workflow).
- 분포: **rejected_precheck 66 · sensitive_hold 17 · already_covered_or_drafted 8 · source_check_candidate 9.**
- 함정 적발(salt/함유, draft 제외): 스타틴 칼슘염(로수바·아토르바·피타바)·ARB 칼륨염(로사르탄칼륨)·칼슘 함유 제산제(칼슘 기준).
- **cap**: Top201–300(100건)은 이번 batch3 미precheck — 다음 batch 이월(빈도 proxy 하위). 무음 누락 아님(명시).

## 2. source-check (nedrug 실측, 9건)
- 산출: `data/coverage_queue_source_check_batch3_v1_2.csv` (`verify_coverage_queue_sources_v1_2.py --precheck … --out …`, iron detector v2 포함).
- 결과: **source_confirmed 3 · reject 4 · needs_review 2.**
  - confirmed: 펙소페나딘×Mg(itemSeq 202202380) · 테고프라잔×철분(202501770) · 히드로코르티손×칼륨(200703172).
  - reject 4: 세프포독심·세푸록심·세픽심×철분(허가사항 철 동거어 부재 — **cefdinir만 적색복합체 확립, 계열 일반화 아님 입증**) · 시메티딘×철분.
  - needs_review 2: 침강탄산칼슘 복합·비사코딜(국내 단일 경구 완제품목 미확보 — itemSeq 직접 지정 재확인 필요).

## 3. 적대검증 (독립 회의론자 3명 × 라벨 전문 · refute-by-default · 6렌즈)
- 산출: `data/coverage_queue_adversarial_verify_batch3_v1_2.json` (medistack-batch3-adversarial workflow).
- **confirmed_before_adversarial = 3 · confirmed_after_adversarial = 2.**

| candidate | 약×영양소 | 표결 | final | 근거(라벨 직접 인용) |
|---|---|---|---|---|
| CQ-118 | 테고프라잔×철분 | 3/3 | **confirm** | "…이 약 투여 중에는 …, 철염, …의 흡수가 감소될 수 있다"(상호작용·pH의존). P-CAB 단일 라벨 직접 명시(계열 일반화 아님). |
| CQ-199 | 히드로코르티손×칼륨 | 3/3 | **confirm** | "칼륨배설증가에 의한 저칼륨혈증" + "체액·전해질: 칼륨손실, 저칼륨성 알칼리혈증". 래피손정(단일 경구 tablet·전신). 고갈 방향. |
| CQ-103 | 펙소페나딘×마그네슘 | 2/3 | **needs_review(보류)** | 라벨="Al/Mg 함유 제산제 복용하지 마십시오"(병용금기). 회의론자 반론: 카피의 'separation(간격 두기)'가 병용금기를 약화·방향 재해석 → 만장일치 미달, 보수적 보류. |

> 채택 기준 = **만장일치 confirm**(CQF01·DF06/07 선례 동형). 2/3 split 은 needs_review.

## 4. draft batch (CQF02·CQF03)
- 산출: `data/coverage_queue_draft_batch3_v1_2.json` (`build_coverage_queue_draft_batch_v1_2.py --id-start 2 …`), preflight CSV 동반.
- draft id 는 CQF01(라이브 승격됨) 다음 **CQF02·CQF03** 연속(DF01-07·라이브 id 공간과 분리).

| draft | 약×영양소 | mechanism/action | evidence | 안전 | 출처 itemSeq |
|---|---|---|---|---|---|
| CQF02 | 테고프라잔×철분 | absorption/separation | high | kcard=false·link=true | 202501770(위더캡정50mg) |
| CQF03 | 히드로코르티손×칼륨 | depletion/monitoring | high | **kcard=true·link=false** | 200703172(래피손정) |

- 전 draft 봉인: published=false·clinical_reviewed=false·reviewed_by 공란·do_not_implement_yet=true·
  review_required=true·source_required=true·**live_integration_forbidden=true**·source_confirmed=true·adversarial_verified=true.
- 칼륨 행(CQF03): product_link_allowed=false·potassium_safety_card=true. 카피=칼륨 보충 권유/결핍 단정 0(상태 확인·상담 안내).
- 카피 톤: 참고정보(복용지시/추천/치료/예방/구매 0). 금지어 스캐너 0.

## 5. coverage KPI
- **현재(라이브=58, CQF01 알마게이트×철분 반영): KPI① 성분 24/300 = 8.00% · KPI② 품목수가중 1,098/13,268 = 8.28%.**
- **batch3 2건(CQF02·CQF03) 승격 가정: KPI① 26/300 = 8.67% · KPI② 1,153/13,268 = 8.69%** (Δ 성분 +2 · 품목수가중 +55).
- 한계(불변): 품목수=복용빈도 proxy(실측 검색량 아님) · coverage 공백 ≠ relation 대상 · 공백이 곧 승격 대상 아님.
- 여전히 미커버 주요 빈출 성분(참고): 프레가발린·암로디핀·각종 ARB/스타틴·항히스타민 등 — 대다수 6대 영양소 라벨 상호작용 근거 약함(reject 다수의 이유).

## 6. 검증
- 신규 batch3 draft validator `validate_coverage_queue_draft_batch3_v1_2.py` **PASS(47/47)**.
- 라이브 회귀 전수 **25/25 PASS**(CI 7 + 통합/draft 8 + smoke 7 + unit 3), 금지어 스캐너 0.
- 라이브 export/full index/alias/src/DATA_URL 무변경 · published/clinical false 유지 · 제품/구매/제휴 UI 0.

## 7. PM 판단 필요사항
1. **CQF02 테고프라잔×철분** 라이브 승격 여부(만장일치·강한 직접근거·고빈도 K-CAB '케이캡' 계열). 승격 시 KPI①→8.33%대.
2. **CQF03 히드로코르티손×칼륨** 라이브 승격 여부 — **칼륨 행**: DF01-05 칼륨 보류 정책과 정합 검토 필요(안전카드 유지, 상승방향 아님/고갈). 칼륨 draft 일괄 PM 정책 결정에 포함 권장.
3. **CQ-103 펙소페나딘×마그네슘**: needs_review. 상호작용 자체는 실재(라벨 직접 명시)하나 카피를 '병용금기' 충실하게 재작성(예: 같은 시간대 복용 회피 권장)할지, separation 톤 유지할지 PM/임상 판단.
4. needs_review 2건(침강탄산칼슘 복합·비사코딜): 단일 경구 완제 itemSeq 직접 지정해 재source-check 할지.
5. Top201–300 + 세팔로스포린 외 잔여 후보 차기 batch 진행 여부.

> 안전 원칙(불변): 허가사항 직접근거만 confirmed · 계열 일반화 금지 · 민감/고위험군 hold · 만장일치 적대검증 ·
> 라이브 미반영(live_integration_forbidden) · published/clinical false · '식약처 승인·추천 영양제' 표현 0.
