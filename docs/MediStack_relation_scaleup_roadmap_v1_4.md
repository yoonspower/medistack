# MediStack — Relation Scale-up Roadmap (v1.4, 1,000 relation 목표)

> Relation Factory Bot v1.4 라운드(2026-06-16) 산출. **live 승격 0** — 본 문서는 1,000 relation 달성 경로·구조·수확률.
> 정본 데이터: `data/review/relation_factory_*_v1_4.*` · draft `data/drafts/relation_factory_draft_batch_v1_4.json`.
>
> **F1 퀴놀론 18건 통합 준비(2026-06-16, live 0):** 첫 reviewer-gated 통합 후보 = **F1 18건**(60→78). by-counterpart 2-wave 권고(nutrient10 60→70 → antacid8 70→78). 선행조건 0·index/alias 무변경. `scripts/integrate_f1_quinolone_batch_v1_4.py` + docs `MediStack_f1_quinolone_*_v1_4.md`. 1,000 경로의 첫 가시적 진척.
> **F9 만성복용 depletion 8건 통합 준비(2026-06-17, live 0):** 네 번째 후보 = **F9 통합 가능 7건**(survives 3·copy_change 4·**needs_review 1**·60→67). 항전간제(페노바르비탈/페니토인/프리미돈/카르바마제핀)·설파살라진·트리메토프림 × **엽산/비타민D**(depletion/monitoring, 메트포르민×B12 렌더 선례). **카르바마제핀×엽산(0245) 강등**: '드물게...엽산 결핍증' 저신호 이상반응 열거(기전·level-direction·연용-remedy 없음) → needs_review(카르바마제핀은 ×비타민D 0246 으로 coverage 유지). 항전간제×비타민D 3건은 nutrient=remedy → display reframe(copy_change), 페니토인×엽산은 stray ' 1' 트림. 선행조건 0·index 자동 flip 0(전부 name_only·alias decoupled·latent ≤18 별도). by-nutrient 2-wave(엽산 3·비타민D 4). 글로벌 family map 갱신: 통합 가능 **24→31**·pending **11→3(F4/F6/F10)**. 조합 F1+F2+F3+F9 **60→91**. `scripts/integrate_f9_chronic_depletion_batch_v1_4.py` + docs `MediStack_f9_chronic_depletion_*_v1_4.md`. ↓이전:
> **F3 비스포스포네이트 + 글로벌 reviewer-ready 계획(2026-06-17, live 0):** F3 3건 family 재검증 → **survives 1·needs_review 2**(에티드론산 0148/0149 인용 양이온이 제산제에 결속·계열 일반화 금지 → 강등). 통합 가능 = 이반드론산×al_mg_antacid 1건(60→61·overlap reviewer 판단). 글로벌 family map: F1 18✅/F2 5✅/F3 1✅/F4 1⏳/F6 1⏳/F9 8⏳/F10 1⏳ = **통합 가능 24·pending 11**. 조합(disjoint): F1+F2+F3 **60→84**(combined v0.2 PASS). Factory v1.5 = **보류 권장**. `scripts/integrate_f3_bisphosphonate_batch_v1_4.py`·`integrate_reviewer_ready_global_batch_v1_4.py`(no-live-write planner) + docs `MediStack_f3_bisphosphonate_*_v1_4.md`·`MediStack_reviewer_ready_global_plan_v1_4.md`. ↓이전:
>
> **F2 테트라사이클린 5건 통합 준비(2026-06-17, live 0):** 두 번째 후보 = **F2 5건**(survives 5/5·60→65, F1 후 78→83). nutrient 2(테트라×철분·아연)+al_mg_antacid 3(독시·미노·테트라×제산제). 선행조건 0·index 자동 flip 0(테트라 latent 1·alias decoupled). all5 once 또는 by-counterpart 2-wave(60→62→65). F1+F2 antibiotic-mineral wave 가능. `scripts/integrate_f2_tetracycline_batch_v1_4.py` + docs `MediStack_f2_tetracycline_*_v1_4.md`.

## 1. 현재 위치

| 구분 | 수 |
|---|---|
| **live relations** | **60** (id1~61, published=false·clinical_reviewed=false) |
| reviewer-gated near-term(통합 준비 완료) | 페니실라민 2 · theme map 6 · 칼륨 4 · AT-FEX 1 = **13** |
| **신규 factory source_confirmed draft(v1.4)** | **43** (적대검증 전 raw) |
| **factory 적대검증 후 reviewer-ready(v1.4)** | **37** (survives 31 + copy_change 6 — live 아님) · 강등 6 |
| raw 후보 풀(v1.4) | 301 (중복 제거 후 신규 262 · source-check queue 200) |

> near-term 13 + factory reviewer-ready 37 = 잠재 +50 → reviewer note/dry-run 통과분만 단계적 live. **개수보다 정확성 우선**.
> 적대검증에서 6건 강등(needs_review 5·hold 1) — 정확성 우선 원칙으로 의심분 제거. 정본 §7.

## 2. 단계 목표

| 단계 | 목표 relation | 내용 |
|---|---|---|
| v1.3 | 60 → ~75 | 페니실라민 2 + theme map 6(선행 PR 후) + 칼륨 4 + AT-FEX 1 (reviewer note 후) |
| **v1.4** | 75 → ~120 | factory 43 draft 중 adversarial+reviewer 통과분(FQ/tetracycline/bisphosphonate × mineral·antacid, AED × folate/vitD) |
| v1.5 | 120 → ~200 | 신규 family 2차 수확(bile-acid·azole·만성 depletion 확장) + 미커버 약물 |
| v2.0 | 200 → 300+ | family universe 확장 + 주간 factory run 누적 |
| long-term | → **1,000** verified_reference | 아래 §4 구조 |

## 3. family별 수확률 (v1.4 source-check 실측)

| family | source-check | confirmed | yield | 비고 |
|---|---|---|---|---|
| F1 Fluoroquinolone × metal | 85 | 18 | **0.21** | live 다수 존재→신규는 미커버 약물(노르/페/발로/자보/토수플록사신 등) |
| F2 Tetracycline × metal | 27 | 5 | 0.19 | 테트라사이클린·미노/독시(antacid) |
| F3 Bisphosphonate × mineral | 29 | 4 | 0.14 | 에티드론산(Ca/Fe)·알렌드론/이반드론(antacid) |
| F4 Thyroid × mineral/antacid | 4 | 1 | 0.25 | 레보티록신×antacid (Fe/Ca live) |
| F6 Acid-reducer × Fe/B12 | 16 | 1 | 0.06 | 에스오메프라졸×B12(저위산증). 대부분 live/약신호 |
| F7 Bile-acid seq × fat-sol vit | 4 | 0 | 0.00 | 콜레세벨람/콜레스티폴 — 라벨 미기재(needs_review) |
| **F9 Chronic-use depletion** | 33 | 12 | **0.36** | 항전간제(페니토인·카르바마제핀·페노바르비탈·프리미돈)×엽산/비타민D·설파살라진/트리메토프림×엽산 |
| F10 Azole × antacid | 2 | 2 | **1.00** | 케토/포사코나졸(pH 의존 흡수) |

**수확 인사이트**
- **최고 수확 = F9(만성 depletion 0.36)·F10(azole 1.0)** — live 미개척 영역. F1/F2 는 live 가 이미 mineral 흡수를 흡수해 신규 여지 적음(미커버 약물만).
- **no_domestic 90건** = 가티/게미/스파르플록사신 등 다수 미유통(fail-closed 정상). 미유통은 재후보화 금지.
- direction_mismatch(needs_review) 17 · label_not_found 50 — 라벨은 있으나 직접근거 약함 → reviewer 판단.

## 4. 1,000 relation 달성 구조

1,000 verified_reference 는 단일 라운드로 불가 — **공장 파이프라인 + reviewer batch** 가 필요.

- **draft pool 3,000+**: family universe 확장(현 11 family → 30+). 약물군 × counterpart 조합 대량 생성(중복 차단 inventory 필수).
- **source-check queue 10,000+**: SDK-only·fail-closed·캐시. 라벨당 1회 fetch 로 다중 counterpart 동시 확인(비용 절감).
- **reject/hold ledger 영속화**: `relation_factory_inventory_v1_4.json` 확장 — 미유통·세파계×철분·K-sparing·고위험 재후보화 영구 차단.
- **reviewer batch**: source_confirmed draft → adversarial(refute-by-default) → reviewer package → dry-run integrator → live(별도). 배치당 20~40건.
- **주간 factory run**(향후·schedule 아님): 신규 seed/약물만 대상(같은 family 반복 run 은 신규 0 수렴 → 비효율). 신규 family 확장이 가치.
- **품질 게이트 자동화**: `validate_relation_factory_batch_v1_4.py`(결함주입 10) — Mg 영양제 오인·제산제 양이온 오분류·보충 권유·항응고 오인·고위험 약물·live 중복을 기계 차단.

## 5. 다음 확장 family 후보(우선순위)

1. **만성 depletion 확장**(최고 수확): 더 많은 효소유도제·항대사물질 × 비타민/미네랄(라벨 직접근거).
2. **azole/pH 의존 흡수**: 항진균·일부 항바이러스 × 제산제/H2/PPI.
3. **bile-acid/lipid 흡수**: 미확인 품목 라벨 직접 확인(콜레세벨람은 미기재).
4. **미커버 mineral 흡수 약물**: live 에 없는 개별 약물(테트라사이클린계·일부 FQ).
- ⚠️ **고위험 제외 유지**: warfarin×비타민K(antagonism)·이식/면역억제·항암(MTX)·임신·정신과·K-sparing×칼륨(상승 방향). 계열 일반화 금지.

## 6. manual run 절차 (Relation Factory Bot v1.4)

> harvester/schedule 와 **연동하지 않음**(별도 manual tool). 향후 PR 로 provider 편입 검토.

```bash
# 1) 인벤토리(중복 차단) 갱신 — 읽기전용
python3 scripts/build_relation_factory_inventory_v1_4.py
# 2) family universe + 후보 생성 + precheck + source-check queue (offline·안전·쓰기 data/review 만)
python3 scripts/relation_factory_bot_v1_4.py
# 3) (선택) SDK-only source-check + draft batch + PM queue — 네트워크 최소·fail-closed
python3 scripts/relation_factory_bot_v1_4.py --online-source-check --max-source-check 200 [--p0-only] [--families F1,F9]
# 4) 검증
python3 scripts/validate_relation_factory_batch_v1_4.py   # 결함주입 10
python3 scripts/smoke_relation_factory_batch_v1_4.py
# 5) 적대검증(refute-by-default) — draft → reviewer-ready 필터 + ledger
python3 scripts/adversarial_verify_relation_factory_v1_4.py
python3 scripts/validate_relation_factory_batch_v1_4.py   # 적대검증 정합성 + 결함주입 15
python3 scripts/smoke_relation_factory_batch_v1_4.py        # reviewer-ready 카드 시뮬
```
- 기본 실행은 **live write 0 · export write 0 · src write 0 · no auto integrate**. 산출물은 `data/review/`·`data/drafts/` 만.
- SDK 캐시: `data/harvest_queue/_sdk/`(gitignore). runtime queue 커밋 금지.
- live 통합은 draft → adversarial → reviewer note → dry-run integrator → 별도 PR(본 라운드 0).

## 7. 적대검증 결과(v1.4, 2026-06-16)

factory 43 draft 를 refute-by-default 10-lens(source fidelity·direct co-occurrence·direction·negation·category·supplement safety·clinical high-risk·formulation/route·duplicate conflict·copy/render safety)로 검증.

| verdict | 수 | |
|---|---|---|
| survives | 31 | 라벨 직접 quote·방향 일치·중복 0 |
| survives_with_copy_change | 6 | quote 정비/카테고리 note 후 유지 |
| **reviewer-ready 소계** | **37** | reviewer note → dry-run → 별도 PR |
| needs_review | 5 | 라벨 재검색 후 재평가 |
| hold | 1 | acid_reducing_drug category 트랙 |
| reject | 0 | |

**family 생존율**: F1 18/18(1.0) · F2 5/5(1.0) · F4 1/1 · F6 1/1 · F3 3/4(0.75) · F9 8/12(0.67) · F10 1/2(0.5).

**주요 false-positive 패턴(강등 사유)**
1. **acid-reducer 주어 혼동**: 포사코나졸 quote 가 H2 차단제만 서술 → al_mg_antacid 매핑 불가(hold).
2. **임신 한정 근거 일반화**: 페노바르비탈·프리미돈 × 엽산 quote '임신중' → 카드 '장기복용' 과일반화(needs_review).
3. **동물·임신 근거**: 라모트리진 × 엽산 = 랫트 시험(needs_review).
4. **이상반응 열거 저신호**: 옥스카르바제핀 엽산이 저나트륨혈증 나열문 매몰(needs_review).
5. **generic 제산제 + live 중복**: 알렌드론산 antacid quote 가 칼슘(live)만 명시·Al/Mg 미명시(needs_review).
6. quote hygiene(비치명, copy_change): 에티드론산 '○ 파제트병'·카르바마제핀 표 raw·레보티록신 Al-only.

정본: `data/review/relation_factory_adversarial_verify_v1_4.json`(ledger) · `data/drafts/relation_factory_reviewer_ready_batch_v1_4.json`(37) · `docs/MediStack_reviewer_package_relation_factory_v1_4.md`(패키지).
