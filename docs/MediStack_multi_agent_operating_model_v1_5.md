# MediStack — Multi-Agent Operating Model v1.5

> 후보 대량 준비를 여러 에이전트로 분업하되, **live 승격 권한은 분리·게이트**한다. 모든 production/audit 는 NO-LIVE-WRITE.

## 역할
| 역할 | branch | 권한 | 산출 |
|---|---|---|---|
| **PM / approval** (main conversation) | main(읽기) | 승인·병합 순서 결정·reviewer note 게이트 | 결정 |
| **Production** | `agent/autofactory-v1.5-production` | orchestrator 실행(no-live-write) | `autofactory_v1_5_*` |
| **Adversarial Auditor** | `agent/adversarial-auditor-v1.5` | production 결과 독립 재검증·재분류 | audit ledger |
| **Needs-review Cleanup** | `agent/needs-review-cleanup-v1.5` | 기존 4 + source_pending 상위 재검색 | resolved ledger |
| **Live PR** | `agent/live-pr-<wave>` | reviewer note 확보 후 **only** per-family integrator | live PR |

## branch 격리 규칙
- **main 직접 작업·직접 push 금지.** 모든 작업은 위 branch.
- production/audit/cleanup branch 는 **live/protected 무수정** (data/review·docs·prompts·scripts 만).
- live PR branch 만 export 를 만지며, **reviewer note + per-family integrator + 별도 PR** 로만.

## 병합 순서 (merge order)
1. production → (PM 검토) → main
2. auditor 재검증 결과 반영(재분류 시 production 갱신 후 재머지)
3. cleanup 의 resolved needs_review (근거 명확 시에만)
4. live PR: reviewer note 확보 wave 부터 1 PR = 1 wave = 1 squash commit

## conflict policy
- 같은 산출물 충돌 시 **auditor 판정 우선**(refute-by-default 보수).
- production 과 auditor 가 분류 불일치 → needs_review 로 강등(보수적).
- needs_review/hold/reject 후보는 어떤 ready wave 에도 혼입 금지.

## report 형식 (result-only)
각 에이전트는 **결과만** 반환: branch · commit · 산출 파일 · funnel 수치 · 가드 결과 · 병목 · 다음 추천.
중간 탐색 로그/파일 덤프 금지. PM 은 결론만 받는다.

## context compression
긴 작업은 (단계, 산출 파일, 검증 결과, 다음 단계) 4요소로 압축해 핸드오프.

## 기본 규칙
- **no-main-direct-write** · **no-live-write default** · **미검증 source 승격 0** · **needs_review 자동 승격 금지**.
- 후속 프롬프트: `prompts/agent_autofactory_v1_5_production.md` · `prompts/agent_adversarial_auditor_v1_5.md` ·
  `prompts/agent_needs_review_cleanup_v1_5.md`.
