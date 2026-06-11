# MediStack v0.6 — Phase 16 batch7 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-12** / 상태: **✅ 반영 완료 (PM 승인, alias 256→306, 2026-06-12)** / 상위: `MediStack_v0.6_alias_500_plan.md`, `MediStack_v0.6_phase15_batch7_candidate_report.md`

> **(갱신) PM 승인 후 실행 완료**: batch7 50건 alias 반영 — product_aliases +50(218→**268**) · verified_item_seqs +50(194→**244**, 5성분 append·canonicals 12 유지) · alias_count 256→**306**. validator **#154 옵션 A** 갱신. 5 validator(bulk 122·v0.1 12·v0.2 15·v0.3 13·TypeB 7) + smoke **10/10** ALL PASS. relation 30·DATA_URL·export 불변. 반영 = ephemeral `/tmp/ms_incorporate_v0_6_batch7.py`(미커밋). 아래는 실행 전 계획 원문(참고 보존). v0.5 Phase 14 패턴 동일 적용.

---

## 1. 목적 / 범위
- Phase 15 산출 **batch7 approved-ready 50건**(`bulk_alias_approved_ready_batch7_v0_6.json`, incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- Phase 14 패턴 그대로: **product_aliases +50 AND verified_item_seqs +50 동반 확장**.

## 2. batch7 반영 대상 (50건)
canonical 5성분. 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high·**기존 verified 키**.

| canonical | 건수 | source_relation_ids |
|---|---|---|
| 레보플록사신 | 13 | [1, 2, 3] |
| 메트포르민 | 12 | [12] |
| 시프로플록사신 | 12 | [4, 5, 6] |
| 오메프라졸 | 12 | [13, 14] |
| 알렌드론산 | 1 | [29] |

> 5성분 전부 기존 verified canonical 키 → 반영은 **append only**, **verified canonicals 12 → 12 유지(신규 키 없음)**.

## 3. 반영 매핑 (Phase 16 실행 시)
- **product_aliases (+50)**: `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`.
- **verified_item_seqs (+50)**: 5성분 append. entry = `{item_seq, item_name, verified_at, method:"...Phase15 batch v0.6-batch-7 ingrName=...", batch_id:"v0.6-batch-7", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 15) | 반영 후(Phase 16) |
|---|---|---|
| meta.alias_count | 256 | **306** (+50) |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 218 | **268** (+50) |
| verified_item_seqs entries | 194 | **244** (+50) |
| verified canonicals | 12 | **12** (불변 — append only) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 16 에서도 불변)
- relation export 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch7 엔 없음) · 에스오메프라졸 alias 금지 · 15행 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch7 itemSeq ∩ 기존 alias = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.

## 6. validator 조건 (Phase 16 통과 기준) — ⚠️ #154 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 50건 status pending→**approved**(reviewer v0.6-phase16-batch7), batch7 AR 50건 **incorporated=true**.
- **bulk candidate validator**:
  - 🔴 **#154 갱신 필수**: 현재 #154 = "batch7 incorporated=false(Phase 15 생성)". 반영하면 incorporated=true → **#154 FAIL**. → #134(batch6) 진화와 동일하게 **#154 를 incorporation-aware(옵션 A)로 갱신**: "incorporated ∈ {false,true} 정합" + true 면 base+12(#152)로 실제 반영 검증. **PM 승인 필요(옵션 A 패턴).**
  - #153(≤50)·#155(필드 보유)는 그대로 통과.
- **v0.3 alias validator**: #8 이 verified +50 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 50건 각 alias→해당 canonical 1종 · 회귀(타리비드3·포사맥스1·토렘2·넥시움0·#r15) 유지.

## 7. rollback 조건
- alias JSON git 버전관리 → **반영 커밋 1개 단위** `git revert` 즉시 256 복원.
- STOP: 반영 후 alias_count ≠ 306 · relation ≠ 30 · DATA_URL 변경 · product ≠ 268 · verified ≠ 244 · validator/smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.

## 8. PM 승인 필요사항
1. **batch7 50건 반영 승인 여부**(alias 256→306).
2. **validator #154 incorporation-aware 갱신 승인**(옵션 A 패턴).
3. **source_relation_ids 매핑 확정**(§2 표) · batch7 신규 verified canonical 없음(전부 append) 확인.
4. 306 도달 후 방향: **batch8**(held 57, 네트워크 0 → 306→~356) 계속.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
