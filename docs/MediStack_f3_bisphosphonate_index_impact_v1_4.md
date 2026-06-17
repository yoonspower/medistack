# MediStack — F3 비스포스포네이트 full index / aliases 영향 (v1.4)

> 읽기전용 분석. index/alias write 없음. 단일 소스 = `data/review/f3_bisphosphonate_index_impact_v1_4.json`.

## 1. 핵심
full index/aliases coverage 는 **alias pool**(`data/medistack_v0.3_aliases.json` · `verified_item_seqs`/`product_aliases`)로 결정되며 export `relations` 와 **decoupled**(`validate_full_drug_name_index.build_pool()` 은 alias 만 읽음·런타임 재생성·fail-soft 검색보조). 따라서 **relation-only 통합은 자동 flip 0**.

| 지표 | 값 |
|---|---|
| 자동 flip(relation 통합) | **0** |
| relation_card | 1,168 → **1,168 불변** |
| name_only | 16,412 → **16,412 불변** |
| alias 변경 필요 | false |

## 2. 성분별 (통합 가능 0147 = 이반드론산)

| 성분 | index 항목 | covered_by_relation | name_only | in_aliases | 통합 scope | latent flip |
|---|---|---|---|---|---|---|
| 이반드론산 | 73 | 73 | 0 | **true** | ✅(0147) | **0** (이미 covered) |
| 에티드론산 | 1 | 0 | 1 | false | ✗(needs_review) | 조건부 1 |

- **이반드론산**: v1.1 relation 확장 7성분에 포함 → 이미 전량 relation_card. 0147(×al_mg_antacid) 통합해도 index 영향 **0**.
- **에티드론산**: index sample 1건 name_only · in_aliases=false. 단 0148/0149 가 **needs_review** 라 본 scope 통합 대상 아님 → **현 통합분 latent flip 0**.
  - 조건부: reviewer 가 에티드론산 parse 확정 → 0148/0149 통합 + 에티드론산을 `verified_item_seqs` 등록(별도 alias 작업)하면 1건 flip(relation_card 1169 / name_only 16411). **통합 차단 아님**.

## 3. F1/F2 대비 차이
- F1: 신규 6성분 전부 index sample 부재 → latent 0.
- F2: 테트라사이클린 1건 name_only → latent 1(조건부).
- **F3: 이반드론산은 이미 covered(통합 가능분 latent 0)**, 에티드론산은 needs_review 라 통합 미대상 → 현 scope **latent 0**, 에티드론산 조건부 1(parse 확정+enrich 시). family 별 index 결합도가 다름을 보여줌.
