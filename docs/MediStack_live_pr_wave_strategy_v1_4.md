# MediStack v1.4 — live PR wave strategy
> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 실물 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 불변. 단일 소스: `data/review/per_family_live_pr_readiness_v1_4.json`.

## 보수적 small wave (5 PR)
| PR | wave | n | expected |
|---|---|---|---|
| PR-1 | f1_nutrient10 | 10 | 70 |
| PR-2 | f1_antacid8 | 8 | 누적 +8 |
| PR-3 | f2_all5 | 5 | 누적 +5 |
| PR-4 | f3_single+f4_f6_small2 | 3 | 누적 +3 |
| PR-5 | f9_all7 | 7 | 누적 +7 |

- reviewer 부담: family·subset별 분리 — note 부담 최대 5건 · rollback: 최상(작은 단위 revert) · baseline: wave마다 baseline 재계산(count 기반)
- smoke: PR마다 family smoke · source risk: subset별 source 1종 · UI risk: 최소(소규모) · index/alias: relation-only flip 0
- **추천: family별 note 분리 시 추천**

## 중간 크기 wave (3 PR) — 기본 추천
| PR | wave | n | expected |
|---|---|---|---|
| PR-1 | antibiotic23 | 23 | 83 |
| PR-2 | chronic8 | 8 | 누적 +8 |
| PR-3 | f3_single+f4(remaining) | 2 | 누적 +2 |

- reviewer 부담: wave 3건 — 묶음 note · rollback: 양호(wave 단위 revert) · baseline: wave 3회 재계산
- smoke: wave별 다중 family smoke · source risk: wave당 family 2종 · UI risk: 중(23건 한 번) · index/alias: relation-only flip 0
- **추천: 기본 추천(reviewer 묶음 note 제공 시)**

## 최대 단일 wave (1 PR all33) — 비추천/조건부
| PR | wave | n | expected |
|---|---|---|---|
| PR-1 | all33 | 33 | 93 |

- reviewer 부담: 단일 note 이지만 33건 전수 검토 부담 집중 · rollback: 최악(전체 revert·부분 rollback 불가) · baseline: 1회(60→93)
- smoke: 전 family smoke 동시 · source risk: 6 family 동시 노출 · UI risk: 최대(60→93 한 번) · index/alias: relation-only flip 0
- **추천: 비추천 — reviewer 가 all33 명시 note + gate 통과 시에만 조건부**

## 최종 추천
- 기본: **option_B_medium**
- reviewer per-family note 제공 시: option_A_conservative
- reviewer all33 명시 note + gate 통과 시: option_C_single (조건부·비추천)
- 이유: B = reviewer 부담(3 note)·rollback 단위(wave)·baseline 재계산 횟수(3)의 균형. A 는 rollback 안전성 최상이나 note 5건. C 는 단일 note 편의 대비 rollback/blast-radius 최악이라 비추천.
