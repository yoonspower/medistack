# MediStack — F3 비스포스포네이트 grouping 전략 (v1.4)

> NOT LIVE. 통합 가능 = survives 1(RF-F3-0147). needs_review 2(0148/0149)는 reviewer parse 확정 전 제외.

## 1. scope 옵션 (`integrate_f3_bisphosphonate_batch_v1_4.py --scope ...`)
| scope | 후보 | count | 비고 |
|---|---|---|---|
| `survives`(기본) | RF-F3-0147 | 60→61 (id runtime max+1) | 통합 가능 전부 |
| `antacid1` | RF-F3-0147 | 60→61 | survives 와 동일(al_mg_antacid 1건) |
| `--candidate-ids RF-F3-0148,…` | (needs_review) | **STOP** | needs_review 통합 차단(reviewer parse 선행) |

## 2. count 시나리오
- F3 standalone: **60→61**(survives 1).
- 조건부(에티드론산 parse 확정 시 +2): 60→63. **현재 통합 대상 아님**(needs_review).
- F1(60→78) 후: **78→79**(survives) / 조건부 78→81.
- F1+F2(60→83) 후: **83→84**(survives) / 조건부 83→86.
- id = runtime max+1 (단독 시 현 max 61 → id 62).

## 3. 권고
- **survives once (60→61)** 1차 권고 — 1건 소규모, al_mg_antacid 렌더는 id61·live 이반드론산×광물(동일 약물)로 이미 검증.
- 단 **reviewer 가 이반드론산 nutrient-overlap(headline B)을 먼저 판단**해야 함(정보 가치 vs 중복). overlap 결정이 "중복"이면 0147 보류 가능 → 그 경우 F3 통합 0건.
- **에티드론산 0148/0149** 는 별도 트랙: reviewer 가 에티드론산 라벨 전문 parse 확정 → needs_review 해소 → 그때 nutrient2 통합(60→63 또는 후속 baseline).
- **항생제·비스포 mineral wave 와 결합**: F1 nutrient10 + F2 nutrient2 + (F3 에티드론산 2, parse 확정 후) 로 nutrient wave 묶음 가능. antacid wave = F1 antacid8 + F2 antacid3 + **F3 antacid1(0147)** = 12.
