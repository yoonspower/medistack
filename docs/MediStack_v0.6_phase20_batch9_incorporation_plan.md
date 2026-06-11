# MediStack v0.6 — Phase 20 batch9 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-12** / 상태: **✅ 반영 완료 (PM 승인, alias 356→382, 2026-06-12) — 🏁 단일성분 트랙 마감** / 상위: `MediStack_v0.6_alias_500_plan.md`, `MediStack_v0.6_phase19_batch9_recollect_report.md`

> **(갱신) PM 승인 후 실행 완료**: batch9 26건 alias 반영 — product_aliases +26(318→**344**) · verified_item_seqs +26(294→**320**, 4성분 append·canonicals 12 유지) · alias_count 356→**382**. validator **#194 옵션 A** 갱신. 5 validator(bulk 152·v0.1 12·v0.2 15·v0.3 13·TypeB 7) + smoke **9/9** ALL PASS·무손실(356⊆382). relation 30·DATA_URL·export 불변. 반영 = ephemeral `/tmp/ms_incorporate_v0_6_batch9.py`(미커밋). **🏁 batch9는 단일성분 트랙의 최종 batch — 13 relation 약물 단일성분 완제 풀 소진(천장 382). 이후 단일성분 batch 없음.** 500은 복합제 tier(PM 정책 결정) 필요 — Phase 19 §5 참조.

---

## 1. 목적 / 범위
- Phase 19 산출 **batch9 approved-ready 26건**(`bulk_alias_approved_ready_batch9_v0_6.json`, incorporated=false)을 alias 에 반영.
- Phase 18 패턴 그대로: **product_aliases +26 AND verified_item_seqs +26 동반 확장**.
- ⚠️ batch9는 **단일성분 잔여 전량** — 이후 단일성분 batch 없음(공급 소진, Phase 19 §4).

## 2. batch9 반영 대상 (26건)
| canonical | 건수 | source_relation_ids |
|---|---|---|
| 레보플록사신 | 19 | [1, 2, 3] |
| 메트포르민 | 4 | [12] |
| 시프로플록사신 | 2 | [4, 5, 6] |
| 오메프라졸 | 1 | [13, 14] |

> 4성분 전부 기존 verified canonical 키 → **append only**, canonicals 12 유지.

## 3. 반영 매핑 (Phase 20 실행 시)
- **product_aliases (+26)**: `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`.
- **verified_item_seqs (+26)**: 4성분 append. method `"...Phase19 batch v0.6-batch-9 ingrName=..."`·batch_id `v0.6-batch-9`.

## 4. 예상 결과
| 항목 | 현재(Phase 19) | 반영 후(Phase 20) |
|---|---|---|
| meta.alias_count | 356 | **382** (+26) |
| product_aliases | 318 | **344** (+26) |
| verified_item_seqs | 294 | **320** (+26) |
| verified canonicals | 12 | **12** (불변) |
| ingredient_aliases / relations / DATA_URL | 38 / 30 / v0.2 | 불변 |

## 5. 반영 금지 항목 (불변)
- relation export·DATA_URL·data export·앱 UI 수정 금지 · 칼륨 제품링크 금지.
- 복합제/brand_core/에스오메프라졸/15행 금지 · 미검증·동일 itemSeq 중복 금지.
- published/clinical 전환 금지 · 신규 tag 금지 · 수동 deploy 금지.

## 6. validator 조건 — ⚠️ #194 incorporation-aware 갱신 필요
- queue 26건 status pending→approved(reviewer v0.6-phase20-batch9), batch9 AR incorporated=true.
- 🔴 **#194 갱신 필수**: strict false → **옵션 A**("incorporated ∈ {false,true}" + true는 base+12(#192)로 실제 반영 검증). #193(≤50)·#195(필드 보유) 그대로.
- v0.3 #8 verified +26 동반확장 통과. v0.1/v0.2/TypeB 회귀 0. smoke: 신규 26 각 alias→canonical 1종 + 회귀 유지.

## 7. rollback
- 반영 커밋 1개 `git revert` 즉시 356 복원. STOP: alias≠382·product≠344·verified≠320·relation≠30·DATA_URL변경·validator/smoke/Actions 실패.

## 8. PM 승인 필요사항
1. **batch9 26건 반영 승인**(alias 356→382).
2. **validator #194 옵션 A 갱신 승인**.
3. **382 이후 500 방향 결정**(Phase 19 §5): **옵션 A**(382 마감) / **옵션 B**(복합제 tier 개방 → 500) / **옵션 C**(brand_core). ⚠️ 단일성분으로는 382가 천장 — 500은 옵션 B 필수.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / **복합제 alias 는 PM 정책 결정 전 금지** / 15행·excluded·에스오메프라졸 우회 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
