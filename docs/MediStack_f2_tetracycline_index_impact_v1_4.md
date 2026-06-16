# MediStack — F2 테트라사이클린 full index / aliases 영향 분석 (작업 K · v1.4)

> **상태: 분석 — read-only.** index/alias 파일 무수정. 산출물: `data/review/f2_tetracycline_index_impact_v1_4.json`.

## 0. 결론 (TL;DR)
- **relation-only 통합으로 자동 index 변경 0** — `relation_card 1168 / name_only 16412` 불변.
- full index/aliases 의 coverage 는 **alias pool(`verified_item_seqs`)** 로 결정되며 **export relations 와 decoupled**(런타임 재생성·fail-soft 검색보조). `build_pool()` 은 `data/medistack_v0.3_aliases.json` 만 읽음 → relation 추가가 pool 을 바꾸지 않음.
- **F1 과의 차이점**: F1 신규 6성분은 index sample 에 전부 부재(flip 0). F2 는 **테트라사이클린 1건이 name_only 로 존재** → alias 등록 시에만 flip(latent).

## 1. 성분별 index 현황 (sample total 17,580)

| 성분 | index_items | covered_by_relation | name_only | in_aliases | latent_flip(alias 등록 시) |
|---|---|---|---|---|---|
| 독시사이클린 | 11 | 11 | 0 | true | 0 |
| 미노사이클린 | 3 | 3 | 0 | true | 0 |
| 테트라사이클린 | 1 | 0 | **1** | false | **1** |

- 독시/미노는 이미 `verified_item_seqs` 등록(in_aliases) → 전 품목 covered(relation_card). F2 antacid relation 추가는 새 index 항목을 만들지 않음(index 는 약물 품목 키, relation 키 아님).
- 테트라사이클린 1건은 alias pool 미등록(in_aliases=false) → 현재 name_only 가 정합. relation 만 추가해도 pool 불변이라 **자동 flip 0**.

## 2. 자동 vs latent

| 항목 | 값 |
|---|---|
| automatic_flip_from_relation_integration | **0** |
| relation_card_flip_required | **0** |
| relation_card_after (relation-only) | 1168 (불변) |
| name_only_after (relation-only) | 16412 (불변) |
| latent_flip_if_alias_enriched (테트라사이클린) | 1 |
| relation_card_after_if_alias_enriched | 1169 |
| name_only_after_if_alias_enriched | 16411 |

- **latent flip** 은 테트라사이클린을 `verified_item_seqs` 에 등록하는 **별도 alias 작업** 시에만 발생. F2 relation 통합의 **선행조건/차단 아님**(옵션 enrichment).
- full index validator(`validate_full_drug_name_index.py`)는 pool=aliases 기준으로 검증 → relation-only 통합 후에도 CI 깨지지 않음(테트라 itemSeq ∉ pool → name_only 정합 유지).

## 3. aliases
- 독시/미노 in_aliases=true, 테트라사이클린 false.
- `alias_change_required=false` — relation 통합에 alias 변경 불필요(decoupled fail-soft 검색보조). 테트라사이클린 alias/verified_item_seqs enrichment 는 별도 옵션 작업(검색 품질 향상용·통합 전제 아님).

## 4. 정책 확인 (CLAUDE.md §2)
- "검색 인덱스 등은 런타임 생성, 데이터에 박지 않는다" — F2 relation 통합은 **relation-only export** 로 충분. index/alias 정적 sample 은 QA 참고 artifact.
- 본 라운드: index/aliases 파일 **무수정**. 통합 라운드에서도 relation-only 가 기본(테트라 alias enrichment 는 별도 판단).
