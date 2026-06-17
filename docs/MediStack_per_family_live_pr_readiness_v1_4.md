# MediStack v1.4 — per-family live PR readiness
> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 실물 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 불변. 단일 소스: `data/review/per_family_live_pr_readiness_v1_4.json`.

## Integration-ready 33건
| family | count | candidate ids |
|---|---|---|
| F1 | 18 | `RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029`, `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030` |
| F2 | 5 | `RF-F2-0105`, `RF-F2-0110`, `RF-F2-0111`, `RF-F2-0114`, `RF-F2-0115` |
| F3 | 1 | `RF-F3-0147` |
| F9 | 7 | `RF-F9-0269`, `RF-F9-0246`, `RF-F9-0272`, `RF-F9-0252`, `RF-F9-0242`, `RF-F9-0243`, `RF-F9-0255` |
| F4 | 1 | `RF-F4-0173` |
| F6 | 1 | `RF-F6-0201` |

- **total 33** · F1 split: nutrient10 `RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029` / antacid8 `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030`
- combined true: baseline 60 · F1+F2+F3+F9 91 · **all33 93**
- remaining unpackaged 0 · live exact duplicate 0 · cross-family duplicate 0 · needs_review 혼입 0

## live baseline
- relations **60** · max id **61** (id 비연속 → 신규 id = runtime max+1) · meta.relation_count 60
- protected hashes (불변 기준):
  - `medistack_v0.1_beta_export.json` `e9994f0179955913`
  - `medistack_v0.2_beta_export.json` `62df92844faf1bcc`
  - `medistack_v0.3_aliases.json` `ee25aed084a8a35f`
  - `full_drug_name_index_sample_v1_0.json` `d329b2ddd3cdd05e`
- full index: total 17580 · relation_card 1168 · name_only 16412 · relation-only 통합 시 auto flip **0**(alias enrichment 별도)

## waves (대안 grouping — 전부 실행 아님)
| wave | families | n | Δ | →count |
|---|---|---|---|---|
| f1_nutrient10 | F1 | 10 | +10 | 70 |
| f1_antacid8 | F1 | 8 | +8 | 68 |
| f1_all18 | F1 | 18 | +18 | 78 |
| f2_all5 | F2 | 5 | +5 | 65 |
| f3_single | F3 | 1 | +1 | 61 |
| f9_all7 | F9 | 7 | +7 | 67 |
| f4_f6_small2 | F4·F6 | 2 | +2 | 62 |
| antibiotic23 | F1·F2 | 23 | +23 | 83 |
| chronic8 | F9·F6 | 8 | +8 | 68 |
| all33 | F1·F2·F3·F9·F4·F6 | 33 | +33 | 93 |
