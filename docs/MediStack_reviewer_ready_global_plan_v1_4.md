# MediStack — 글로벌 reviewer-ready 37 통합 계획 + Factory v1.5 판단 (v1.4)

> NOT LIVE / no-live-write. 단일 소스 = `data/review/reviewer_ready_global_plan_v1_4.json`. 생성/검증:
> `integrate_reviewer_ready_global_batch_v1_4.py`(dry-run) + `validate_global_reviewer_ready_dryrun_v1_4.py`.
> **글로벌 도구는 export 를 절대 쓰지 않음**(planning 전용). live 통합은 per-family integrator / small-family bundle(reviewer-note 게이트)에만 위임.

## 1. family map (reviewer-ready 37, 적대검증 → family 재검증)

| family | 관계 | reviewer-ready | family 재검증 | **통합 가능** | 비고 |
|---|---|---|---|---|---|
| F1 | Fluoroquinolone × metal/antacid | 18 | ✅ | **18** | survives 18 (커밋 7288d91) |
| F2 | Tetracycline × metal/antacid | 5 | ✅ | **5** | survives 5 (커밋 4649888) |
| F3 | Bisphosphonate × mineral/antacid | 3 | ✅ | **1** | survives 1·needs_review 2 (커밋 5ce237e) |
| F9 | Chronic-depletion × folate/vitD | 8 | ✅ | **7** | survives 3·copy_change 4·needs_review 1 (커밋 d172630) |
| F4 | Thyroid × mineral/antacid | 1 | ✅ | **1** | small-family copy_change 1 (이 라운드) |
| F6 | Acid-reducer × Fe/B12 | 1 | ✅ | **1** | small-family copy_change 1 (이 라운드) |
| F10 | Azole × antacid | 1 | ✅ | **0** | small-family **needs_review 1**(0275 route) (이 라운드) |
| **합계** | | **37** | F1–F10 전부 | **33** | **pending 0** · needs_review 4(F3 2·F9 1·F10 1) |

**원칙**: family-specific 재검증을 통과한 family 만 통합 가능. 이번 라운드로 마지막 pending(F4/F6/F10)이 small-family bundle 재검증을 통과 →
**pending 0**. (교훈: family 재검증이 F1 stray '1'·F2 철→철 토큰·F3 에티드론산 parse·F9 저신호 이상반응 열거(0245)·
**F10 케토코나졸 route/availability(국내 외용 전용·수출용 source) 0275** 처럼 광역검증이 놓친 family 특이 결함을 잡음.)

## 2. 조합 시나리오 (통합 가능분 · 모두 disjoint · dedup 0)

성분 set 완전 분리(F1 록사신 / F2 사이클린 / F3 드론산 / F9 만성복용약 / F4 레보티록신 / F6 에스오메프라졸) → 교차 family overlap 0, live exact dup 0.

| 조합 | relations | | 조합 | relations |
|---|---|---|---|---|
| F1 only | 60→78 | | F4 only | 60→61 |
| F2 only | 60→65 | | F6 only | 60→61 |
| F3 only | 60→61 | | F4+F6 | 60→62 |
| F9 only | 60→67 | | F1+F2+F3 | 60→84 |
| F1+F2+F3+F9 | **60→91** | | **F1+F2+F3+F9+F4+F6** | **60→93** |

- **duplicate/overlap risk**: 교차 family exact dup **0**. v0.2 sim(combined 33, 60→93) **PASS**.
- 공유 렌더 경로: al_mg_antacid(F1 8 + F2 3 + F3 1 + F4 1 = 13·id61 선례) · nutrient B12(F6 1 + id12/id13 계열) · depletion/monitoring(F9 7).
- 현행 헤드라인: **F1+F2+F3+F9 = 60→91** · **+small-family F4·F6 = 60→93**. F10(케토코나졸 0275)은 route/availability needs_review → 통합 0.

## 3. 글로벌 dry-run integrator
- **scope 지원**: `--families F1,F2,F3,F9,F4,F6`(기본 전체 통합 가능 6). 통합 가능 0 family(F10) 요청 시 blocked + 노트 게이트 거부.
- **reviewer-note gate**: 승인 토큰 · 통합 family 전건 명시 · **per-family/small-family reviewer-note 위임 명시** · needs_review backlog(F3 0148/0149·F9 0245·F10 0275) 제외 인지 · family/계열 일반화·clinical=true 금지.
- **no-live-write**: 글로벌 도구는 export 무수정(planning 전용·sha 불변). live 는 per-family/small-family `--pm-approved --reviewer-note`.
- **duplicate policy**: (ingredient, counterpart/category) 키로 live 60·타 family·자기 배치와 중복 금지.
- **status**: DRY-RUN PLAN(검증 PASS).

## 4. Factory v1.5 판단 — **지금 실행 보류 권장** (상세: `MediStack_factory_v1_5_trigger_policy_v1_4.md`)

| 항목 | 판단 |
|---|---|
| 지금 신규 harvest/family 확장 실행 | **보류(run_now=false)** |
| packaging 조건 | **충족**(remaining unpackaged 0 — reviewer-ready 37 = integrable 33 + needs_review 4 전부 패키징/triage) |
| 이유 | (a) 통합 가능 33건(F1·F2·F3·F9·F4·F6) reviewer note·live PR 미완(live PR 병목) · (b) needs_review backlog 4건(F3 0148/0149·F9 0245·F10 0275) 미정리 · 신규 후보는 backlog 부풀림·중복 위험 |
| 선행조건 | ① F1/F2/F3/F9/F4/F6 reviewer note + live PR(60→93) · ② needs_review backlog 4건 재검색/정리 · ③ factory dedup 키 표준화 |
| 추천 시점 | reviewer note 트랙(per-family/small-family live PR) 가동 후 |

## 5. 다음 단계 (PM)
1. F1/F2/F3/F9/F4/F6 reviewer note 실물 → per-family integrator / small-family bundle live PR(개별 또는 antibiotic-mineral / chronic-depletion / small-family wave). 통합 가능 33건 → 60→93.
2. needs_review 해소: F3 에티드론산(0148/0149) parse · F9 카르바마제핀×엽산(0245) standalone 근거 · **F10 케토코나졸(0275) route/availability**(국내 oral 존재 여부·formulation-scoping).
3. Factory v1.5 는 1~2 이후.
