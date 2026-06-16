# MediStack — F1 퀴놀론 18건 live 통합 grouping 전략 (v1.4)

> **상태: 전략/문서 전용 — live 통합 0.** 실제 통합은 reviewer note 실물 + 별도 PM + 별도 PR 전제.
> 근거 데이터: `data/review/f1_quinolone_live_dryrun_v1_4.json` (`scope_scenarios`). 확인일 2026-06-16.

## 1. 사전 조건 (요약)

- **선행조건 0**: al_mg_antacid(id61 선례) · 일반 영양소(live FQ×광물) 둘 다 현행 v0.2 validator + src 렌더 지원 (theme map 처럼 validator/src 선행 PR 불필요).
- **id 정책**: runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터 부여. AT-FEX/칼륨/theme/페니실라민이 먼저 통합되면 자동 조정(코드가 산정).
- **index/aliases**: 변경 불필요(작업 K). relation_card 1168 / name_only 16412 불변.
- **rollback 단위**: 통합 묶음 = rollback 묶음. subset 통합이 작을수록 rollback·검토 부담↓.

## 2. grouping 후보

| # | 전략 | 묶음 | count | id(단독 통합 시) | 장점 | 위험/부담 |
|---|---|---|---|---|---|---|
| 1 | **all18 일괄** | 18 | 60→78 | 62~79 | 빠름·1 PR | reviewer 18건 일괄 검토 부담↑ |
| 2 | **by-counterpart 2-wave** (권고) | wave1 nutrient10 → wave2 antacid8 | 60→70→78 | w1 62~71 · w2 72~79 | 렌더 경로별 분리·rollback 2단·신규성 낮은 것 먼저 | PR 2회 |
| 3 | by-counterpart 1차만 | nutrient10 (top10) | 60→70 | 62~71 | live FQ×광물과 **동일 렌더·신규성 0** | antacid8 별도 |
| 3' | by-counterpart al_mg | antacid8 (top8) | 60→68 | 62~69 | id61 렌더 경로 검증됨 | nutrient10 별도 |
| 4 | by-ingredient | 8 성분 묶음 | 가변 | 가변 | 성분 단위 rollback·검토 | PR 多·count 분산 |
| 5 | conservative subset | top 5~8 high-signal | 60→65~68 | 가변 | 최소 노출 | 선별 기준 필요(전건 동일 evidence=moderate) |

### count 시나리오 (baseline 60)
- **60→78** all 18
- **60→70** top10 = nutrient10 (철분4·칼슘3·아연3)
- **60→68** top8 = antacid8 (Al/Mg 제산제 약물 8)
- **by-counterpart 2-wave**: 60→70(nutrient) → 70→78(antacid)
- **by-ingredient**: 노르4 / 자보4 / 토수3 / 페3 / 레보1 / 로메1 / 발로1 / 오플1

## 3. 추천안 — **by-counterpart 2-wave** (전략 2)

1. **wave 1 — nutrient 10 (60→70)**: 퀴놀론 × 철분/칼슘/아연. live FQ×광물(id 1·2·5·21·22·43~45 등)과 **동일 렌더·신규성 0** → 가장 낮은 위험. 1차 통합 권고.
2. **wave 2 — al_mg_antacid 8 (70→78)**: 퀴놀론 × Al/Mg 함유 제산제(약물). id61 이트라코나졸 렌더 경로(약물 counterpart kicker)와 동일 → 검증된 경로. 2차.

**근거**: 두 렌더 경로 모두 이미 live 검증됨 → **all18 일괄(전략 1)도 허용**. 다만 (a) reviewer 검토 부담 분할, (b) rollback 단위 분리, (c) 신규성이 0 인 nutrient 를 먼저 검증해 운영 안정 확보 측면에서 2-wave 가 보수적·안전.

**비권고**: by-ingredient(전략 4)는 count·PR 가 과하게 분산되어 운영 부담만 큼(전건 동일 evidence·mechanism 이라 성분 단위 분리 실익 적음). conservative subset(전략 5)도 전건 evidence=moderate 라 선별 기준이 모호.

## 4. reviewer note burden (by scope)

- **all18**: candidate_id 18 전건 명시 필요(노트 1회·검토 18건).
- **nutrient10 / antacid8**: 해당 scope candidate_id 전건 명시(노트 1회·검토 10/8건). gate(`check_reviewer_note`)가 scope 선언 ↔ 요청 scope 일치 + 전건 명시를 강제.
- 공통 필수 결정(노트): 승인 토큰 · scope · grouping · **al_mg_antacid category(id61 선례·Mg 영양제 아님)** · separation 간격 노출 여부 · verified_reference 동의 · clinical_reviewed≠true · 제품 추천 아님 · 금속이온/제산제 복용 권유 아님 · reviewer 식별자/PM 승인 근거.

## 5. 실행

```
# dry-run(쓰기 0)
python3 scripts/integrate_f1_quinolone_batch_v1_4.py                       # all18
python3 scripts/integrate_f1_quinolone_batch_v1_4.py --scope nutrient10    # 1차
python3 scripts/integrate_f1_quinolone_batch_v1_4.py --scope antacid8      # 2차
python3 scripts/integrate_f1_quinolone_batch_v1_4.py --candidate-ids RF-F1-0021,RF-F1-0022

# live (별도 PM + clinical reviewer note 실물 후 · 본 세션 금지)
python3 scripts/integrate_f1_quinolone_batch_v1_4.py --scope nutrient10 --pm-approved --reviewer-note PATH
```
