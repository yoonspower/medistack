# MediStack — F9 만성복용 depletion Index/Alias Impact (v1.4)

> ANALYSIS — read-only / no index·alias write. 단일 소스: `data/review/f9_chronic_depletion_index_impact_v1_4.json`.

## 결론: 자동 flip 0 (relation_card 1168 / name_only 16412 불변)

full index/aliases 는 export relations 와 **decoupled**(pool = `aliases.verified_item_seqs`/product_aliases · 런타임 재생성 · fail-soft). 따라서 **relation-only 통합은 자동 flip 0**이며 통합을 차단하지 않는다.

| 약물 | index sample items | covered_by_relation | name_only | in_aliases | 통합 |
|---|---|---|---|---|---|
| 설파살라진 | 1 | 0 | 1 | false | ✅(엽산) |
| 카르바마제핀 | 10 | 0 | 10 | false | ✅(비타민D) |
| 트리메토프림 | 1 | 0 | 1 | false | ✅(엽산) |
| 페노바르비탈 | 0 | 0 | 0 | false | ✅(비타민D) |
| 페니토인 | 5 | 0 | 5 | false | ✅(엽산·비타민D) |
| 프리미돈 | 1 | 0 | 1 | false | ✅(비타민D) |

- **full index counts(현행)**: total 17,580 · relation_card **1,168** · name_only **16,412**.
- **자동 flip**: 0. relation_card/name_only 불변. index/alias 변경 불필요.
- **조건부 latent flip**: 6개 약물 모두 name_only·in_aliases=false. 통합분을 `verified_item_seqs` 로 **alias-enrich(별도 alias 작업·본 라운드 미수행)** 하면 최대 **18건** flip 가능(현 scope·통합 가능 전체 동일). 카르바마제핀(10)이 대부분.
- 영양소(엽산/비타민D)는 **신규 nutrient 값**(기존 live: 칼슘/철분/아연/마그네슘/칼륨/비타민B12/Al·Mg제산제)이나, 영양소는 약물명 full index 대상이 아니므로 index counts 영향 없음.

## 해석
relation 통합과 full index 는 분리되어 있어, F9 7건을 통합해도 full index/aliases 는 그대로다(1168/16412). 약물 색인 노출(latent)을 원하면 reviewer 승인 후 통합분을 별도 alias 작업으로 `verified_item_seqs` 에 등록해야 하며, 이는 본 라운드 범위가 아니다.
