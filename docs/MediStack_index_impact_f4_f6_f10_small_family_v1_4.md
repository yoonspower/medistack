# MediStack — F4/F6/F10 small-family Index/Alias Impact (v1.4)

> ANALYSIS — read-only / no index·alias write. 단일 소스: `data/review/f4_f6_f10_small_family_index_impact_v1_4.json`.

## 결론: 자동 flip 0 · latent 0 (relation_card 1168 / name_only 16412 불변)

full index/aliases 는 export relations 와 **decoupled**(pool = `aliases.verified_item_seqs`/product_aliases · 런타임 재생성).
relation-only 통합은 자동 flip 0.

| 약물 | index items | covered_by_relation | name_only | 형태 | in_aliases | latent(alias-enrich 시) | 통합 |
|---|---|---|---|---|---|---|---|
| 레보티록신 | 17 | 17 | 0 | oral(정) | false | 0 (이미 covered) | ✅(F4) |
| 에스오메프라졸 | 0 | 0 | 0 | (복합제 내에만) | false | 0 (standalone 색인 없음) | ✅(F6) |
| 케토코나졸 | 10 | 0 | 10 | **외용(액/크림)** | false | 0 (외용 — 경구 흡수 relation 무관) | needs_review(미통합) |

- **full index counts(현행)**: total 17,580 · relation_card **1,168** · name_only **16,412**.
- **자동 flip**: 0. relation_card/name_only 불변. index/alias 변경 불필요.
- **latent flip**: **0**. 레보티록신은 이미 relation_card(name_only 0)·에스오메프라졸은 standalone 색인 0·케토코나졸은 외용 전용(경구 흡수 relation alias-enrich 대상 아님). → F9 라운드(latent ≤18)와 달리 본 라운드 latent 0.

## 해석
small-family 2건(레보티록신·에스오메프라졸)을 통합해도 full index/aliases 는 그대로다(1168/16412). 별도 alias-enrich 로 추가 노출시킬 latent 도 없음
(레보티록신 covered·에스오메프라졸 미색인·케토코나졸 외용·미통합). 케토코나졸의 외용 전용 형태 분포가 **0275 needs_review(route/availability)**의 근거이기도 하다.
