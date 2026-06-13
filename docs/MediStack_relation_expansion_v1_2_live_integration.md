# MediStack v1.2 — draft relation 14건 라이브 통합 보고서

실행일 2026-06-14 · 통합기 `scripts/integrate_relation_draft_v1_2.py`(idempotent·dry-run 지원)
선행 게이트 `docs/MediStack_draft_relation_14_preflight_v1_2.md`(14건 전부 pass_to_integrate)
PM 승인 = 이번 라운드 프롬프트(draft `do_not_implement_yet` 해제, source_confirmed 재검증분 한정).

## 1. 통합 대상 / 제외

- **통합 14건(전건 source_confirmed)**: D01–D14 → 라이브 relation ids **43–56**.
- **제외 0건.** needs_review/reject/hold 후보 혼입 0(source queue에서 사전 분리).

| live id | 성분 × 영양소 | mechanism/action | evidence | 칼륨안전 | 비고 |
|---|---|---|---|---|---|
| 43 | 레보플록사신 × 아연 | absorption/separation | high | — | Q06 FQ×아연 |
| 44 | 시프로플록사신 × 아연 | absorption/separation | high | — | Q06 |
| 45 | 오플록사신 × 아연 | absorption/separation | high | — | Q06 |
| 46 | 목시플록사신 × 아연 | absorption/separation | high | — | Q06 |
| 47 | 독시사이클린 × 아연 | absorption/separation | high | — | Q07 테트라×아연 |
| 48 | 미노사이클린 × 아연 | absorption/separation | high | — | Q07 |
| 49 | 리세드론산 × 철분 | absorption/separation | high | — | Q04 enrichment |
| 50 | 리세드론산 × 마그네슘 | absorption/separation | high | — | Q04 |
| 51 | 이반드론산 × 철분 | absorption/separation | high | — | Q04 |
| 52 | 이반드론산 × 마그네슘 | absorption/separation | high | — | Q04 |
| 53 | 클로르탈리돈 × 칼륨 | depletion/monitoring | high | card=true·link=false | Q10 신규성분 |
| 54 | 클로르탈리돈 × 마그네슘 | depletion/monitoring | **moderate** | — | Q10 (evidence 하향) |
| 55 | 인다파미드 × 칼륨 | depletion/monitoring | high | card=true·link=false | Q11 신규성분 |
| 56 | 인다파미드 × 마그네슘 | depletion/monitoring | **moderate** | — | Q11 (evidence 하향) |

**evidence 일관성 조정(D12·D14 = id54·56)**: draft "high" → `moderate`. 근거 = 라이브 relation20(HCTZ×Mg) 선례 일치(draft가 '동일 모델'로 명시) + 원문보다 강하지 않게(인다파미드 라벨 "드물게 저마그네슘혈증"). 칼륨 행(53·55)은 depletion×칼륨 선례(17/19/30 전부 high) 일치로 high 유지.

## 2. 통합 전/후 수치 (실측)

| 지표 | 전 | 후 | 변화 |
|---|---|---|---|
| relations / meta.relation_count | 41 | **55** | +14 |
| relation_card (full index) | 1,072 | **1,077** | +5 |
| name_only (full index) | 16,508 | **16,503** | −5 |
| full index total | 17,580 | 17,580 | 불변 |
| verified_item_seqs | 1,059 / 20 | **1,064 / 22** | +5 / +2 |
| alias_count | 717 | 717 | 불변 |
| product_aliases | 679 | 679 | 불변 |
| ingredient_aliases | 38 | 38 | 불변 |
| DATA_URL | v0.2 | v0.2 | 불변 |
| published / clinical_reviewed | false / false | false / false | 불변 |

**full index flip = 5건** (클로르탈리돈 단일 2: 클로베네정·하이그로톤정 / 인다파미드 단일 3: 나트릭스서방정·다피드정·후루덱스서방정). FQ·테트라·비스포 8성분은 이미 전건 relation_card → enrichment only(flip 0). 복합제(클로르탈리돈 62·인다파미드 13)는 **name_only 유지**(v1.1 7성분 패턴 승계·CANONICAL_13 미등재).

## 3. 변경 파일

데이터: `data/medistack_v0.2_beta_export.json`(relations append) · `data/full_drug_name_index_sample_v1_0.json`(5 flip+counts) · `data/medistack_v0.3_aliases.json`(verified_item_seqs +5/+2).
검증 상수: `validate_full_drug_name_index.py`(verified 1064/22·relations 55) · `validate_potassium_name_only_policy.py`(name_only 16503·rc 1077).
신규: `integrate_relation_draft_v1_2.py` · `validate_relation_draft_v1_2.py`(통합 정합 19체크) · `smoke_relation_draft_v1_2.py`(렌더 안전 209체크) · preflight doc/CSV.
fixture: `search_regression_v1_0.json`(타리비드/신일모노독시엠캡슐/레보펙신정 3→4·리센플러스 1→3·name_only_index_size 16503·v1.2 신규 케이스).
**src(`src/js/*`) 무변경.** **v0.1 봉인 무변경.**

## 4. 검증 결과 (전수 PASS)

- **CI 게이트 7**: v0.1(12/12)·v0.2(15/15)·v0.3 aliases(16/16)·surface(5/5)·full index(31/31)·potassium(8/8)·potassium --selftest(0 fail) — 전부 PASS.
- **로컬 smoke/unit 11**: search regression·disclaimer·hctz·alias·combo_approved·combo/combo_ar/typeB unit·**relation_draft_v1_2 validator(19/19)**·**relation_draft_v1_2 smoke(209)**·full index --selftest — 전부 PASS.
- **회귀 불변**: A/B/C/D/E combo 전부 유지. E(라베프라졸+산화마그네슘) name_only 유지. 칼륨 정책 8/8 유지(standalone 0·금지필드 0). 기존 relation 1–42 보존.
- **안전 톤**: 신규 14 카드 상세 렌더에 추천/구매/복용지시/제품 어휘 0, 외부 링크=nedrug 출처만, 공통 면책·출처 표시 유지, 칼륨 카드 '칼륨 주의'+임의보충 위험 고지.

## 5. 다음

- relation factory 다음 후보(draft/queue까지·live 통합 금지) → `docs/MediStack_relation_factory_*`.
- v1.2 release readiness → `docs/MediStack_v1_2_release_readiness.md`.
- 재개 트리거: '메디스택 relation factory' 또는 '메디스택 v1.2 릴리스'.
