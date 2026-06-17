# MediStack — Factory v1.5 trigger policy (v1.4 기준 재판단)

> 판단 시점: 2026-06-17 (per-family **live PR readiness pack** 완성 직후). 단일 소스: `data/review/reviewer_ready_global_plan_v1_4.json` + `data/review/factory_v1_5_trigger_decision_v1_4.json` + `data/review/per_family_live_pr_readiness_v1_4.json`.

## 결론: **run_now = false (보류 유지)**

| 항목 | 값 |
|---|---|
| reviewer-ready 37 패키징 완료 | **37/37** (integrable 33 + needs_review 4 전부 triage/패키징) |
| integration-ready 총수 | **33** (F1 18·F2 5·F3 1·F9 7·F4 1·F6 1) |
| needs_review 총수 | **4** (F3 0148/0149 · F9 0245 · F10 0275) |
| remaining unpackaged | **0** |
| **live PR readiness pack** | **완성** (wave 분할안 A/B/C · reviewer-note checker · rehearsal · post-merge/rollback/baseline plan) |
| live PR (실제 통합) | **0** (reviewer note 실물 미확보) |

## 트리거 규칙 대조
- 규칙 ①: integration-ready ≥ 30 이고 live PR = 0 이면 Factory v1.5 **보류**. → 33·live PR 0 → **보류**.
- 규칙 ②: remaining unpackaged = 0 이면 packaging 조건 충족. → **충족**.
- 규칙 ③: reviewer note/live PR 병목 남으면 run_now=false 유지. → reviewer note 0·needs_review 4 backlog → **유지**.

이번 세션으로 **packaging 은 한 단계 더 진전**(live PR 까지 무비용·무위험으로 분할/검증 완료)했으나, 병목은 **reviewer note 실물 확보 + 실제 live PR 0** 으로 동일. 신규 harvest/family 확장은 backlog 만 키우므로 계속 보류.

## 추천 시점 (recheck_when)
- **최소 1~2개 live PR wave** (예: option B PR-1 `antibiotic23` 23건) 가 reviewer note 와 함께 실제 통합되고,
- needs_review 4 중 일부가 해소된 후 재판단.

## 선행조건 (run 전)
1. wave reviewer note 확보 → per-family/small-family integrator 로 live PR (60→…→93 경로).
2. needs_review 4 정리: F3 에티드론산(0148/0149) parse · F9 카르바마제핀×엽산(0245) 근거 · F10 케토코나졸(0275) route.
3. factory dedup 키(ingredient, counterpart/category) 표준화.

## 비고
- planning 전용(글로벌 도구는 export 무수정). live 승격은 per-family integrator + PM + clinical reviewer note + 별도 PR.
- published=false·clinical_reviewed=false·reviewed_by 공란 유지.
