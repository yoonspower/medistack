# MediStack Factory v1.5 — Scale Targets

> 대량 실행 목표치와 품질 우선순위. **숫자 채우기보다 source fidelity 우선.**

## 목표 funnel (network harvest 활성 시)
| 단계 | 목표 |
|---|---|
| raw candidates | 800 ~ 1200 |
| source-check queue | 400 ~ 600 |
| source-confirmed draft | 150 ~ 250 |
| reviewer-ready | 80 ~ 120 |
| needs_review | 80 ~ 120 |
| reject/hold | 나머지 |

## 현 상태 (오프라인, seed 1)
raw 301 · queue 196 · source-confirmed(existing) 33 · 신규 reviewer-ready **0** · needs_review(genuine 4 + source_pending cap 120).
→ 목표 대비 미달은 **정상**. 오프라인은 신규 source 를 확정할 수 없고, 도구는 미검증 승격을 0 으로 강제한다.

## 달성 못 할 때 규칙
- 무리해서 숫자를 채우지 않는다. **달성률과 병목을 보고**한다.
- reviewer-ready 100 개보다 **source fidelity 품질**이 우선.
- 병목(network harvest·reviewer note)을 먼저 해소한 뒤 target 을 올린다.

## wave 패키징 한도
- high confidence wave: 30 ~ 80 건
- medium wave: 10 ~ 30 건
- small risky wave: 1 ~ 10 건
- all-in-one wave: 기본 비추천

## 기존 33 과 충돌 방지
- 기존 integration-ready 33(F1 18·F2 5·F3 1·F9 7·F4 1·F6 1)은 `existing_prepared`.
- 신규 reviewer-ready 수에 **중복 포함 금지**.
- combined future = **60→93 + new_ready**.
- 기존 needs_review 4(RF-F3-0148/0149·RF-F9-0245·RF-F10-0275)는 ready wave 제외. 재검색 후보로만 표시.
  해소 시 별도 resolved ledger 로 이동(자동 승격 금지, 근거 명확 필수).

## 권장 실행 시점 (Factory v1.6)
1. network harvest 활성화(식약처 라벨 직접 인용).
2. existing 33 의 reviewer note 트랙(per-family live PR) 가동.
3. 그 후 `--target-raw 800~1200` 대량 실행.
