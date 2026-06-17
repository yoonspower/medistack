# MediStack AutoFactory v1.5 — Dashboard

> `data/review/autofactory_v1_5_dashboard.json` 사람용 요약. run_date 2026-06-17 · seed 1 · 기본 target.
> 상태: **NO-LIVE-WRITE — actual integration 0 · 미검증 source 승격 0.**

## Funnel
| 단계 | 수 |
|---|---|
| raw candidates | 301 |
| source-check queue | 196 |
| prefiltered: live_duplicate | 35 |
| prefiltered: hold_family | 67 |
| prefiltered: reject_direction | 3 |
| source-confirmed (existing) | 33 |
| → auto_pass | 33 |
| → copy_change | 0 |
| genuine needs_review | 4 |
| source_pending → needs_review (cap) | 120 (overflow 76) |
| **신규 reviewer-ready** | **0** |
| existing_prepared | 33 |

## 달성률 vs target
| 지표 | target | 결과 | 비고 |
|---|---|---|---|
| raw | 1200 | 301 | family universe(source_check=true) 결정적 enumerate 한도 |
| source-check | 600 | 196 | live dup/hold 사전 분기 후 |
| source-confirmed | 200 | 신규 0 (existing 33) | **실제 source harvest(network) 필요** |
| reviewer-ready | 100 | 신규 0 (existing 33) | 미검증 source 승격 0 가드 |
| needs_review | ≤120 | genuine 4 + source_pending 120 | overflow 76 |

> **숫자를 무리하게 채우지 않는다.** reviewer-ready 100 보다 source fidelity 품질이 우선.

## Dry-run (no-write rehearsal)
antibiotic23 → **83** · chronic8 → **68** · all33 → **93** · live_write=False.

## Combined future scenario
baseline 60 · existing all33 93 · **new_ready 0 → projected 93 (변동 없음)**.

## 병목
**실제 source harvest(식약처 라벨 직접 인용·network)** — 오프라인 orchestrator 는 신규 source 확정 0.
그 다음 병목은 existing_prepared 33 의 **reviewer note 실물 확보**.

## Factory v1.6 추천
`run_now=false`. 신규 source 확정 0 상태에서 대량 생성은 source_pending backlog 만 키운다.
network harvest 활성 + reviewer note 트랙 가동 후 `--target-raw 800~1200` 재실행 권장.
