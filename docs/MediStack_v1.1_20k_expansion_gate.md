# MediStack v1.1 — 20k Full Drug Index 확장 게이트

> 작성일: 2026-06-13. full drug name index **10,000 → ~20,000** 확장의 **사전 게이트**.
> **별도 PM 승인 없이는 실행하지 않음.** 기준선 = `MediStack_v1.1_plan.md` §1.
> 성능 근거 = `MediStack_v1.0_full_drug_index_10k_stability_report.md` §5.

---

## 1. 성능 게이트 (외삽)

| 지표 | 10,000 (실측) | 20,000 (외삽) | 임계 |
|---|---|---|---|
| JSON 원본 | 4.79MB | ~9.6MB | — |
| **gzip 전송** (Pages) | **278KB** | **~556KB** | **< 1.5MB** |
| JSON.parse 중앙값 | 12.3ms | ~24.5ms | — |
| **buildNameOnlyIndex** | 2.3ms | **~4.6ms** | **< 100ms** |
| 초기로드(parse+build) 데스크톱 | 14.6ms | ~29ms | — |
| 저사양 모바일 추정 (×4) | ~58ms | **~115ms** | — |
| **searchNameOnly 최악**(전체스캔) | 0.31ms | **~0.6ms** | **< 5ms** |

→ 20k는 세 임계 모두 **여유롭게 충족**(gzip 556KB ≪ 1.5MB, build 4.6ms ≪ 100ms, search 0.6ms ≪ 5ms). **성능은 STOP 사유가 아님.**
재현: `python3 scripts/measure_full_index_performance.py data/full_drug_name_index_sample_v1_0.json`.

> 핵심: 원본 JSON은 크지만(품목명/필드 반복) **gzip ~17배 압축** → 전송·체감 부담 작음. 검색은 normalized 사전 1회 + 상한 30이라 선형이어도 sub-ms.

## 2. 수집 천장 / 품질 STOP 기준 (진짜 위험)

성능이 아니라 **데이터 수집 가능성·품질**이 20k의 실제 제약이다.

- **수집 천장**: nedrug `searchDrug?ingrName1=` 부분일치만으로 +10,000 신규(중복·제외 후)는 어려울 수 있음. 10k에서 이미 `excl_dup 4,730` / `rows_seen 14,249` / `kept 4,500`. → 성분 풀 추가 확장(`DIVERSE_INGREDIENTS_EXT3`, 485 → ~700) 또는 보완 수집축(getItemDetail / 제형 / 업체) 필요.
- **STOP — 양 미달**: 풀 확장에도 신규 충당이 정체되면 **억지로 20k를 채우지 말고 중단 보고**(10k plan §4-1 원칙 계승).
- **STOP — 중복 과다**: dedup율이 비정상적으로 높으면(신규 대비 `excl_dup` 급증) 중단.
- **STOP — 편중**: 최대 단일 성분 비율이 현저히 상승(10k 기준 **0.90%**)하거나 소수 성분이 대량을 점하면 중단.
- **STOP — nedrug 부하**: 요청 실패율 상승 / 타임아웃 빈발 시 중단(sleep 상향 후 재시도, 그래도 안 되면 보류).

## 3. 검증 필수 (게이트 통과 조건)

- **standalone potassium blocklist** PASS 필수 (`validate_potassium_name_only_policy.py`, `blocked_standalone = 0`).
- **full index validator** PASS — 20k 게이트 추가: `target_total>=20000 → total>=20000` (Phase 5와 동형, 조건부).
- **search regression smoke** PASS — 넥시움 / 에스오메프라졸 / asdfqwer = **0 불변**.
- **relation 30 불변**, **alias 621 불변**.
- 전종 validator + Actions deploy + **live HTTP 200**.

## 4. 절대 금지 (확장 시에도)

- relation 확장 금지 / alias JSON 수정 금지 / DATA_URL 변경 금지 / data export(md5 `401b097a`) 변경 금지.
- clinical_reviewed · published 임의 변경 금지.
- 제품 · 구매 · 제휴 UI 금지 / **name_only 의학적 판단 표시 금지**.
- 제외 유지: 13 canonical · 에스오메프라졸/넥시움 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄.
- **신규 name_only만 추가**(augment 무손실), 기존 10,000 **byte-identical 보존**.

## 5. 실행 절차 (승인 시)

1. `DIVERSE_INGREDIENTS_EXT3` 추가 → 성분 풀 485 → ~700 (미수록 치료군 보강 · 신규 우선 정렬).
2. `collect_full_drug_name_index_sample.py --augment --target 20000 --per-cap N --max-pages M` (기존 10,000 seed 보존).
3. validator 20k 게이트 추가 + potassium + search smoke.
4. 성능 재측정(`measure_full_index_performance.py`) — 임계 초과 시 plan §B(압축/분할 로딩) 검토.
5. fixture `name_only_index_size` · `data_basis` 갱신.
6. report + handoff + 라이브 QA.

## 6. 재개 트리거

- **"메디스택 20k"** → 본 게이트 적용, 별도 PM 승인 하에 실행.

## 7. 실행 결과 (2026-06-13) — 20k 시도 → 17,580 공급 천장

PM 승인 후 실행. **목표 20,000 미달, 17,580 도달에서 공급 천장(억지 충족 회피, gate §2 준수).**

- **방법**: 성분 풀 485 → **696**(`DIVERSE_INGREDIENTS_EXT3` 211종: 지혈·편두통·구충·종양 경구·HIV/HCV·마취/근이완·호르몬·추가 외용/점안/이비인후/정신·항부정맥·면역). **4-shard 병렬 수집**(`--shard I/K` + `merge_full_index_shards.py`) — 단일 스트림 대비 대폭 단축, 서버 부하 문제 없음(2-pass 통틀어 ing_fail 2=전송 블립).
  - pass 1(per-cap 45·max-pages 12): 10,000 → 14,471 (**+4,471**).
  - pass 2(per-cap 80·max-pages 25, resumable): 14,471 → 17,580 (**+3,109**).
- **천장 근거**: pass 2 `rows_seen 30,096` 중 `excl_dup 16,829`(**56% 중복**) — 같은 성분 깊은 페이지가 이미 수집분 재출현. 더 깊은 페이지 grinding은 force-fill(gate 금지). **신규 성분(EXT4) 추가는 합법 경로지만 성분이 점점 희귀(저빈도)**해져 20k 도달 비용 대비 효익 낮음 → PM 판정으로 17,580 확정.
- **품질(천장이지 결함 아님)**: 편중 max_single **1.175%**(< Phase 4 1.21%) · 고유성분 2,213 · 제조사 420 · **blocked_standalone 0**(potassium 안전) · **원본 10,000 byte-identical 보존** · name_only 의학필드 0.
- **성능(17,580)**: JSON 8.47MB · **gzip 497KB** · parse 21ms + build 4.6ms = 모바일 ~103ms · 검색 ≤0.56ms. 임계 내(gzip < 1.43MB, build < 100ms).
- **메타**: `target_total=17,580`, `target_attempted=20,000`, `expansion_note`(천장 사유) 기록. 검증기 Phase 6 게이트(`target>=20000→total>=20000`)는 미발동(target 17,580)·Phase 5 게이트 통과. **20k 라벨 위장 안 함.**
- **잔여(별도 승인)**: 20k가 꼭 필요하면 EXT4(미수록 저빈도 성분 ~150-200) 1-2패스 추가. 단 수익 체감 — "메디스택 20k 재시도" 트리거.
