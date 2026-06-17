# MediStack — 글로벌 reviewer-ready 37 통합 계획 + Factory v1.5 판단 (v1.4)

> NOT LIVE / no-live-write. 단일 소스 = `data/review/reviewer_ready_global_plan_v1_4.json`. 생성/검증:
> `integrate_reviewer_ready_global_batch_v1_4.py`(dry-run) + `validate_global_reviewer_ready_dryrun_v1_4.py`.
> **글로벌 도구는 export 를 절대 쓰지 않음**(planning 전용). live 통합은 per-family integrator(reviewer-note 게이트)에만 위임.

## 1. family map (reviewer-ready 37, 적대검증 기준)

| family | 관계 | reviewer-ready | family 재검증 | **통합 가능** | 비고 |
|---|---|---|---|---|---|
| F1 | Fluoroquinolone × metal/antacid | 18 | ✅ | **18** | survives 18 (커밋 7288d91) |
| F2 | Tetracycline × metal/antacid | 5 | ✅ | **5** | survives 5 (커밋 4649888) |
| F3 | Bisphosphonate × mineral/antacid | 3 | ✅ | **1** | survives 1·needs_review 2 (커밋 5ce237e) |
| F9 | Chronic-depletion × folate/vitD | 8 | ✅ | **7** | survives 3·copy_change 4·needs_review 1 (이 라운드) |
| F4 | Thyroid × mineral/antacid | 1 | ⏳ pending | 0 | family 재검증 미수행 |
| F6 | Acid-reducer × Fe/B12 | 1 | ⏳ pending | 0 | family 재검증 미수행 |
| F10 | Azole × antacid | 1 | ⏳ pending | 0 | family 재검증 미수행 |
| **합계** | | **37** | F1/F2/F3/F9 | **31** | pending 3(F4/F6/F10) · needs_review 3(F3 2·F9 1) |

**원칙**: family-specific 재검증을 통과한 family 만 통합 가능. F4/F6/F10(3건)은 적대검증만 거쳤고 **각자 family integrator/재검증 후에만 live**(교훈: family 재검증이 F1 stray '1'·F2 철→철 토큰·F3 에티드론산 parse·**F9 저신호 이상반응 열거(0245)** 같은 family 특이 결함을 잡음 — 광역검증만으로 통합하면 품질 저하).

## 2. 조합 시나리오 (통합 가능분 · 모두 disjoint · dedup 0)

성분 set 이 완전 분리(F1 록사신 / F2 사이클린 / F3 드론산 / F9 만성복용약(설파살라진·트리메토프림·항전간제)) → 교차 family pair overlap 0, live exact dup 0 → 합산 단순. F9 영양소(엽산/비타민D)도 live 신규.

| 조합 | relations | | 조합 | relations |
|---|---|---|---|---|
| F1 only | 60→78 | | F9 only | 60→67 |
| F2 only | 60→65 | | F1+F2 | 60→83 |
| F3 only | 60→61 | | F1+F2+F3 | 60→84 |
| F3+F9 | 60→68 | | F1+F2+F3+F9 | **60→91** |

- **duplicate/overlap risk**: 교차 family exact dup **0**. 공유 렌더 경로 = al_mg_antacid(F1 8 + F2 3 + F3 1 = 12) · nutrient(F1 10 + F2 2 = 12) · depletion/monitoring(F9 7 = 메트포르민×B12 선례). within-family overlap = F2 독시/미노, F3 이반드론산 — reviewer 가치 판단. v0.2 sim(combined 31, 60→91) **PASS**.
- 현행 헤드라인: **F1+F2+F3 = 60→84**(F1/F2/F3 reviewer note·live 후) · **F1+F2+F3+F9 = 60→91**.

## 3. 글로벌 dry-run integrator
- **scope 지원**: `--families F1,F2,F3,F9`(기본 전체) — 통합 가능 family 만. pending(F4/F6/F10) 요청 시 무시 + 노트 게이트 거부.
- **reviewer-note gate**: 승인 토큰 · 통합 family 전건 명시 · **per-family reviewer-note 위임 명시** · F4/F6/F10 family 재검증 선행 확인 · family/계열 일반화·clinical=true 금지. (글로벌 노트는 family 선택·순서용 — 실제 live write 안 함.)
- **no-live-write**: 글로벌 도구는 export 무수정(planning 전용·sha 불변). live 는 per-family `--pm-approved --reviewer-note`.
- **duplicate policy**: (ingredient, counterpart/category) 키로 live 60·타 family·자기 배치와 중복 금지. per-family integrator 가 통합 시점에 live 와 재dedup(이미 통합분 skip).
- **status**: DRY-RUN PLAN(검증 PASS).

## 4. Factory v1.5 판단 — **지금 실행 보류 권장**

| 항목 | 판단 |
|---|---|
| 지금 신규 harvest/family 확장 실행 | **보류(run_now=false)** |
| 이유 | (a) 통합 가능 31건(F1·F2·F3·F9) reviewer note·live PR 미완 · (b) F4/F6/F10 family 재검증 미수행(품질 게이트 미통과) · (c) F3 needs_review 2·F9 needs_review 1 backlog 미정리 · 신규 후보는 backlog 부풀림·중복 위험 |
| 선행조건 | ① F1/F2/F3/F9 reviewer note 확보 + live PR(60→91 경로) · ② F4/F6/F10 family 재검증 + per-family integrator · ③ F3 needs_review 2·F9 needs_review 1 재검색/정리 · ④ factory dedup 키 표준화 |
| 추천 시점 | 위 선행조건 중 최소 reviewer note 트랙(F1/F2/F3/F9 live) 가동 후 |

## 5. 다음 단계 (PM)
1. F1/F2/F3/F9 reviewer note 실물 → per-family integrator live PR(개별 또는 antibiotic-mineral / chronic-depletion wave). 통합 가능 31건 → 60→91.
2. F4/F6/F10 family 재검증 라운드(F1/F2/F3/F9 패턴 복제) → per-family integrator(=small-family bundle 권고: F4 1·F6 1·F10 1).
3. needs_review 해소: F3 에티드론산(0148/0149) parse · F9 카르바마제핀×엽산(0245) standalone 근거.
4. Factory v1.5 는 1~2 이후.
