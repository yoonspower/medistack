# MediStack — F2 테트라사이클린 grouping 전략 (작업 D · v1.4)

> **상태: 계획 문서 — live 통합 아님.** 실제 통합은 clinical reviewer note 실물 + 별도 PM + 별도 PR 전까지 금지.
> 근거 산출물: `data/review/f2_tetracycline_live_dryrun_v1_4.json` (`scope_scenarios`).

## 0. 대상
- F2 reviewer-ready 5건: nutrient 2 (테트라사이클린×철분·아연) + al_mg_antacid 3 (독시·미노·테트라사이클린 × Al/Mg 제산제).
- id 규칙: **runtime max+1** (단독/순차 통합 시 그 시점 max id + 1 부터). F1/AT-FEX/칼륨/theme/페니실라민 먼저 통합되면 자동 조정.

## 1. grouping 후보 & 예상 relation count

| 전략 | 대상 | 건수 | 예상 count | 예상 id(현 max=61) | rollback 단위 |
|---|---|---|---|---|---|
| **all5 once** | 전체 5 | 5 | **60 → 65** | 62~66 | 1 PR |
| by-counterpart wave1 (nutrient2 / top2) | 테트라×철분·아연 | 2 | 60 → 62 | 62~63 | wave |
| by-counterpart wave2 (antacid3) | 독시·미노·테트라×제산제 | 3 | (62 →) 65 | 64~66 | wave |
| top2 (= nutrient2) | 가장 깨끗한 2 | 2 | 60 → 62 | 62~63 | 1 PR |
| top3 (테트라 by-ingredient) | 테트라×철분·아연·제산제 | 3 | 60 → 63 | 62~64 | 1 PR |
| by-ingredient | 독시(1)·미노(1)·테트라(3) | 1/1/3 | 단계별 | runtime | 성분 PR |

- **antacid3 단독**: 60 → 63 (id 62~64).
- 칼슘/마그네슘 영양소 후보는 **없음**(라벨 문장상 제산제 절 cation) → 영양소 wave 는 철분/아연 2건뿐.

## 2. F1 이후 시나리오 (순서 의존)
- F1 18건이 먼저 live(60→78)면 F2 5건은 **78 → 83** (id 80~84). runtime max+1 자동 조정.
- subset 도 동일하게 max+1 기준 이동(예: F1 후 antacid3 = 78→81).

## 3. F1+F2 antibiotic-mineral combined wave (옵션)
- **nutrient wave**: F1 nutrient10 + F2 nutrient2 = **12건** (전부 live 광물 렌더와 동일).
- **antacid wave**: F1 antacid8 + F2 antacid3 = **11건** (al_mg_antacid · id61 렌더).
- 항생제 × 금속/제산제 통합 wave 로 F1·F2 를 묶으면 reviewer 가 동일 렌더 경로를 한 번에 검토. 통합 여부·순서는 reviewer/PM.

## 4. 추천안
1. **기본 추천: all5 once (60→65).** F2 는 5건 소규모이고 양 렌더 경로(영양소 / al_mg_antacid)가 이미 live 검증(독시/미노×광물, id61)됨 → reviewer 1패스 부담 낮음.
   - 단, **독시/미노 nutrient-overlap** 결정 1건(제산제 약물 relation 의 정보 가치 vs 중복)을 reviewer note 에 명시해야 함(gate 강제).
2. **overlap 결정을 격리하고 싶으면: by-counterpart 2-wave.**
   - wave1 = nutrient2 (60→62) — 테트라×철분/아연, cleanly additive·신규 성분·live 렌더 동일 → 최저 위험 선행.
   - wave2 = antacid3 (62→65) — 독시/미노 overlap reviewer 판단 후 통합.
3. **F1 과 동시 진행 시: antibiotic-mineral combined wave 로 fold**(§3). nutrient/antacid wave 를 family 횡단으로 묶음.
- 어느 안이든 **reviewer note 의 scope 선언 = 통합 scope** 여야 함(`check_reviewer_note` 강제). rollback 은 PR/wave 단위.

## 5. 운영 메모
- relation-only 통합으로 충분(full index/aliases 는 decoupled — 작업 K). 테트라사이클린 verified_item_seqs 등록 시에만 index 1건 flip(별도 alias 작업, 통합 차단 아님).
- 통합 시 relation-count baseline validator 동반 갱신 필요(60 → target). full factory 37 일괄 integrator 는 본 F2 통합분을 (ingredient, counterpart) 키로 skip.
