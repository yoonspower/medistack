# MediStack — F1 퀴놀론 18건 full index / aliases 영향 분석 (v1.4 · 작업 K)

> **상태: 분석 전용 — read-only.** full index/aliases/relation_card/name_only **무수정.**
> 근거 데이터: `data/review/f1_quinolone_index_impact_v1_4.json` (integrator dry-run, 읽기전용). 확인일 2026-06-16.

## 1. 결론

**F1 18건 live 통합은 현 full index / aliases 산출물에 변경을 요구하지 않는다.**
- relation_card **1168 불변** · name_only **16412 불변** · total 17580 불변.
- covered_by_relation flip **0** · alias 추가 **불필요(옵션)**.

## 2. full index (`full_drug_name_index_sample_v1_0.json`, 17,580 sample)

| ingredient | index_items | covered_by_relation | name_only | in_aliases |
|---|:-:|:-:|:-:|:-:|
| 레보플록사신 | 91 | 91 | 0 | ✓ |
| 오플록사신 | 33 | 33 | 0 | ✓ |
| 노르플록사신 | 0 | 0 | 0 | ✗ |
| 로메플록사신 | 0 | 0 | 0 | ✗ |
| 발로플록사신 | 0 | 0 | 0 | ✗ |
| 자보플록사신 | 0 | 0 | 0 | ✗ |
| 토수플록사신 | 0 | 0 | 0 | ✗ |
| 페플록사신 | 0 | 0 | 0 | ✗ |

- **레보·오플록사신**: 이미 100% covered_by_relation(live ×광물 relation 존재). 본 batch 의 ×Al/Mg 제산제(약물)는 LHS ingredient 가 동일하므로 **추가 flip 0**.
- **신규 6 성분**(노르·로메·발로·자보·토수·페플록사신): 현 index **sample(17,580)에 부재** → flip 대상 0. (index 는 Phase 2 sample · target 동일; 6 성분 품목은 아직 미수록.)
- 따라서 relation_card 1168 / name_only 16412 **불변**.

## 3. aliases (`medistack_v0.3_aliases.json`)

- ingredient_aliases 38 · product_aliases 679. 레보·오플록사신만 present.
- 신규 6 성분은 부재. **단, aliases 는 relation export 와 decoupled 된 fail-soft 검색보조** → relation 추가에 alias 변경 **불필요**.
- (옵션) 차후 검색 품질을 위해 norfloxacin/lomefloxacin/… 등 en alias 를 enrichment 할 수 있으나 **통합 전제 아님**(별도 작업).

## 4. 정책 정합 — relation-only export 로 충분

- 현재 라이브 데이터 모델은 relation export(`medistack_v0.2_beta_export.json`)와 full index / aliases 가 **독립**. 앱은 relation 을 우선 렌더하고, 미커버 약은 full index 의 name_only 안내로 fail-soft.
- F1 relation 추가는 export 의 relations 만 늘린다(60→78/70/68). index/alias 는 런타임 재생성 산출물이므로 동시 수정 불필요.
- **차후 index 재생성 시점**에 6 신규 성분의 품목이 index 에 포함되면, 그 품목들은 자연히 relation_card(covered)로 표기된다 — 이는 **별도 index-regeneration 작업**이며 F1 relation live 통합의 선행/동시 조건이 아니다.

## 5. 비교 — 알마게이트(id59) 사례와의 차이

- id59 알마게이트 통합 시에는 알마게이트 단일성분 54품목이 index sample 에 **이미 존재**했기에 relation_card flip 이 발생했다.
- F1 신규 6 성분은 index sample 에 **부재**하므로 flip 이 발생하지 않는다(레보/오플은 이미 covered). → F1 통합은 index 측 무변경.
