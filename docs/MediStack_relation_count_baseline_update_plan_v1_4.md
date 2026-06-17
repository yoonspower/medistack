# MediStack v1.4 — relation_count baseline update plan
> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 실물 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 불변. 단일 소스: `data/review/per_family_live_pr_readiness_v1_4.json`.

- current live relations: **60** · baseline max id 61
- **정책**: expected = runtime current_count + len(approved_new_ids). 신규 id = max(existing_id)+1.. (id 비연속 주의). validator 는 절대값 하드코드 대신 (직전 count, delta) 로 계산.

## standalone (from 60)
| wave | expected |
|---|---|
| f1_nutrient10 | 70 |
| f1_antacid8 | 68 |
| f1_all18 | 78 |
| f2_all5 | 65 |
| f3_single | 61 |
| f9_all7 | 67 |
| f4_f6_small2 | 62 |

## cumulative true
| 누적 | expected |
|---|---|
| F1+F2 | 83 |
| F1+F2+F3 | 84 |
| F1+F2+F3+F9 | 91 |
| F1+F2+F3+F9+F4+F6 | 93 |

## wave aggregates
| wave | expected |
|---|---|
| antibiotic23 | 83 |
| chronic8 | 68 |
| all33 | 93 |

> validator 는 절대값을 하드코드하지 않고 `직전 count + delta` 로 계산한다(중간 wave 순서 의존). 신규 relation id = `max(existing id)+1..` (현재 max 61, count 60 — 비연속).
