# MediStack — F4/F6/F10 small-family grouping strategy (v1.4)

> NOT LIVE / planning. 단일 소스: `data/review/f4_f6_f10_small_family_live_dryrun_v1_4.json` (scope_scenarios).

## 통합 가능 = 2 (F4 1 + F6 1 + F10 0)

| scope | 후보 | count | relations | 비고 |
|---|---|---|---|---|
| **integrable**(권고) | RF-F4-0173 · RF-F6-0201 | 2 | **60→62** (id 62·63) | 두 렌더 경로 모두 live 선례 |
| family:F4 | RF-F4-0173 | 1 | 60→61 (id 62) | absorption/al_mg_antacid (id61 경로) |
| family:F6 | RF-F6-0201 | 1 | 60→61 (id 62) | depletion/B12 (id12/id13 경로) |
| family:F10 | RF-F10-0275 | 0 | STOP | needs_review(route/availability) |
| conditional(0275 해소) | +RF-F10-0275 | +1 | 60→63 | reviewer 국내 oral/scoping 확정 후 |

## 권고
1. **integrable 2 한 번에**(60→62). F4·F6 성분/counterpart disjoint·중복 0·각 렌더 경로 live → 동시 통합 안전·단순.
2. 보수적이라면 family별 순차(F4 → F6). 결과 동일(60→62).
3. F10 은 어느 경우에도 제외(needs_review). 0275 해소 시 별도 +1(60→63).

## 다른 wave 와의 조합 (disjoint·dedup 0)
- F1(퀴놀론)/F2(테트라)/F3(비스포) antibiotic-mineral wave 와 disjoint.
- F9(만성 depletion) chronic-depletion wave 와 disjoint(에스오메프라졸×B12 는 F9 엽산/비타민D 와 별개 pair).
- 합산 헤드라인: **F1+F2+F3+F9+F4+F6 = 60→93**. (F10 제외.)

## id 배정
- runtime max+1. 단독/순차 통합 시 그 시점 max+1 부터. F1/F2/F3/F9 먼저 통합되면 자동 조정(true base 91 → +2 = 93).

## reviewer-note grouping 선언
- reviewer-note 에 grouping 결정 명시 필수(integrable subset 한 번에 / family별). 게이트가 grouping 토큰(grouping/묶음/개별/subset/bundle/한 번에) 요구.
