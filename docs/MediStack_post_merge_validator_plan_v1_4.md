# MediStack v1.4 — post-merge validator plan

> NO-LIVE-WRITE PLAN — 각 live PR wave 통합 직후 실행할 검증 묶음. 구현: `scripts/validate_live_pr_readiness_v1_4.py --post-merge --wave <W>` + 기존 v0.2/family/guard.

## 검증 항목 (wave 통합 후)
| 항목 | 기대 | 도구 |
|---|---|---|
| expected relation_count | `직전 count + delta` (하드코드 금지) | validate_live_pr_readiness --post-merge |
| exact candidate ids present | 승인 전건이 live 에 존재 | post-merge validator |
| no extra candidate ids | 승인 외 신규 0 | post-merge validator |
| published=false | 불변 | v0.2 validator |
| clinical_reviewed=false | 불변 | v0.2 validator |
| reviewed_by blank | relation 전건 부재 | post-merge validator |
| source pointers preserved | source_quote/section 보존 | family smoke |
| management copy preserved | 참고·상담 톤 보존 | family smoke |
| forbidden phrase 없음 | 0 | validate_forbidden_phrases_v1_2 |
| product/purchase/affiliate UI 없음 | 0 | v0.2 validator (제품 필드 금지) |
| schedule inactive | 비활성 | validate_harvester_schedule_safety_v1_3 |
| DATA_URL v0.2 유지 | `medistack_v0.2_beta_export.json` | post-merge validator (data.js grep) |
| relation_card / name_only | 1168 / 16412 (relation-only → flip 0) | readiness validator |
| alias impact | 0 (alias enrichment 별도 작업) | readiness validator |
| app / search / relation card smoke | 렌더-safe | smoke_search_regression_v1_0 + family smoke |
| saved stack smoke | 가능 시 포함 | (앱 수동 QA) |

## 동작 (validate_live_pr_readiness_v1_4.py --post-merge --wave W)
- live count == 60 → **미통합(rehearsal 상태)**: baseline published/clinical=false·reviewed_by 부재만 확인 (PASS·정보).
- live count == 60+delta → **통합됨**: meta.relation_count·published/clinical/reviewed_by·제품링크 검증.
- 그 외 → **FAIL** (예상치 못한 count).

## 실행 순서 (통합 후)
1. `validate_medistack_v0_2_export.py` (스키마/제품금지/enum)
2. `validate_live_pr_readiness_v1_4.py --post-merge --wave <W>`
3. 해당 family `smoke_*_dryrun_v1_4.py` + `smoke_search_regression_v1_0.py`
4. `validate_forbidden_phrases_v1_2.py` · `validate_harvester_schedule_safety_v1_3.py`
5. CI: `.github/workflows/deploy.yml` (validate→deploy gate) 통과 후에만 라이브.
