# MediStack — Factory v1.5 trigger policy (v1.4 기준 재판단)

> 판단 시점: 2026-06-17 (F4/F6/F10 small-family 통합 준비 완료 직후). 단일 소스: `data/review/reviewer_ready_global_plan_v1_4.json`.

## 결론: **run_now = false (보류 유지)**

| 항목 | 값 |
|---|---|
| reviewer-ready 37 패키징 완료 | **37/37** (integrable 33 + needs_review 4 전부 triage/패키징) |
| integration-ready 총수 | **33** (F1 18·F2 5·F3 1·F9 7·F4 1·F6 1) |
| needs_review 총수 | **4** (F3 0148/0149 · F9 0245 · F10 0275) |
| remaining unpackaged | **0** (F4/F6/F10 small-family 재검증으로 마지막 pending 해소) |
| live PR | **0** (per-family/small-family reviewer-note·live 통합 미완) |

## 트리거 규칙 대조
- 규칙 ①: integration-ready ≥ 30 이고 live PR = 0 이면 Factory v1.5 **계속 보류 권장**. → integration-ready 33·live PR 0 → **보류**.
- 규칙 ②: remaining unpackaged = 0 이면 "packaging 조건 충족"으로 표기. → **충족**(0).
- 규칙 ③: reviewer note/live PR 병목이 남으면 **run_now=false 유지**. → live PR 0·needs_review 4 backlog → **유지**.

즉 **packaging 조건은 충족**(remaining unpackaged 0)이나, **live PR 병목 + needs_review 4 backlog** 때문에 신규 harvest/family 확장은 보류.

## 선행조건 (run 전)
1. F1/F2/F3/F9/F4/F6 reviewer note 확보 + per-family/small-family **live PR**(60→93 경로).
2. needs_review backlog 4건 정리: F3 에티드론산(0148/0149) parse · F9 카르바마제핀×엽산(0245) standalone 근거 · F10 케토코나졸(0275) route/availability(국내 oral 존재/formulation-scoping).
3. factory dedup 키(ingredient, counterpart/category) 표준화.

## 추천 시점
- 위 선행조건 중 **최소 reviewer note 트랙(per-family/small-family live PR) 가동 후**. 그 전 신규 후보 추가는 backlog 부풀림·중복 위험.

## 비고
- 본 판단은 planning 전용(글로벌 도구는 export 무수정). live 승격은 per-family/small-family integrator + 별도 PM + clinical reviewer note + 별도 PR.
- published=false·clinical_reviewed=false·reviewed_by 공란 유지.
