# MediStack — F9 만성복용 depletion Grouping Strategy (v1.4)

> NOT LIVE. 통합 가능 7건(survives 3 + copy_change 4)의 묶음·순서 권고. live 는 per-family integrator(reviewer-note 게이트) 위임.

## 통합 가능 7건
| counterpart | candidates | 수 |
|---|---|---|
| 엽산 | 설파살라진(0269)·트리메토프림(0272)·페니토인(0242) | 3 |
| 비타민D | 카르바마제핀(0246)·페노바르비탈(0252)·페니토인(0243)·프리미돈(0255) | 4 |

## 권고 grouping
1. **integrable 7 한 번에** (60→67) — 모두 depletion/monitoring·영양소(엽산/비타민D)·동일 렌더 경로(메트포르민×B12) → 단일 wave 무리 없음.
2. **by-nutrient 2-wave** (권고): 엽산 3 (60→63) → 비타민D 4 (63→67). 비타민D 3건은 copy_change(display reframe) 검토 포인트가 있어 분리하면 reviewer 부담 분산.
   - scope: `--scope folate` → `--scope vitd`.
3. **survives 우선** (선택): survives 3 (60→63) 먼저, copy_change 4 (63→67) 별도 — 카피 보수화 후보를 분리 검토.
   - scope: `--scope survives` → `--scope copy_change`.

> id 는 runtime max+1. F1/F2/F3 가 먼저 live 면 그 시점 max+1 부터 자동 조정(예: F1+F2+F3=84 → 84→91).

## needs_review (묶음 제외)
- **RF-F9-0245 카르바마제핀×엽산** — 저신호 이상반응 열거('드물게...엽산 결핍증'). reviewer 가 카르바마제핀 라벨 전문에서 엽산 저하 standalone 근거 확정 후 별도. (카르바마제핀×비타민D 0246 은 본 묶음에 포함 — 약물 누락 아님.)

## 통합 전 PM 판단사항
- 비타민D copy_change 3건(0252/0243/0255) display reframe('수치 변화'→'관련 주의')가 적절한지 — 라벨이 vitD '수치 저하'를 직접 명시하지 않고 remedy 로 언급하기 때문.
- '장기/연용' framing: 설파살라진(0269)은 라벨이 '병용투여 시'(연용 아님)이나 만성 IBD/RA 약 맥락. 카드 '장기간 복용' 표현 승인 여부.
- 모니터링 톤: 검사 지시·처방 단정 아님, '정기적인 확인이 필요할 수 있습니다 · 상담' 수준 유지.
- factory 일괄 integrator 는 (ingredient, counterpart) 키로 본 F9 통합분 skip(중복 생성 금지).
