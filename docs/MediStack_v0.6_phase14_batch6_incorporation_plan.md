# MediStack v0.6 — Phase 14 batch6 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-12** / 상태: **계획만 — PM 승인 전 실제 반영 금지** / 상위: `MediStack_v0.6_alias_500_plan.md`, `MediStack_v0.6_phase13_batch6_candidate_report.md`

> v0.5 Phase 12(batch5, 176→206)와 **동일한 incorporation 패턴**을 batch6(50건, **206→256**)에 적용하기 위한 사전 계획. **이 문서 단계에서는 반영하지 않는다.** alias_count 206 유지, alias JSON 무변경.

---

## 1. 목적 / 범위
- Phase 13 산출 **batch6 approved-ready 50건**(`data/candidates/bulk_alias_approved_ready_batch6_v0_6.json`, 현재 incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- v0.5 패턴 그대로: **product_aliases +50 AND verified_item_seqs +50 동반 확장**(v0.3 #8 [itemSeq ∈ relation ∪ whitelist] 통과 핵심).
- **이번 단계(문서)에서는 반영하지 않는다.**

## 2. batch6 반영 대상 (50건)
canonical 4성분. 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high·기존 verified 키. 전체 표면형/itemSeq = `..._phase13_batch6_candidate_report.md` §4.

| canonical | 건수 | source_relation_ids | verified_item_seqs |
|---|---|---|---|
| 레보플록사신 | 17 | [1, 2, 3] | 기존(append) |
| 시프로플록사신 | 19 | [4, 5, 6] | 기존(append) |
| 알렌드론산 | 6 | [29] | 기존(append) |
| 오플록사신 | 8 | [21, 22, 23] | 기존(append) |

> batch6 4성분은 전부 기존 verified canonical 키 → 반영은 **append only**, **verified canonicals 12 → 12 유지(신규 키 없음)**.

## 3. 반영 매핑 (Phase 14 실행 시)
### 3-1. product_aliases (+50)
각 항목 = 기존 스키마 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. source_relation_ids = §2 표.
### 3-2. verified_item_seqs (+50 entries)
- 4개 기존 성분에 **append**(신규 키 없음) → verified canonical **12 → 12 유지**, entries **144 → 194**.
- 각 entry 추적정보: `{item_seq, item_name, verified_at, method:"...v0.6-batch-6 ingrName=...", batch_id:"v0.6-batch-6", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 13) | 반영 후(Phase 14) |
|---|---|---|
| meta.alias_count | 206 | **256** (+50) |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 168 | **218** (+50) |
| verified_item_seqs entries | 144 | **194** (+50) |
| verified canonicals | 12 | **12** (불변 — append only) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 14 에서도 불변)
- relation export 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch6 엔 없음) · 에스오메프라졸 alias 금지 · 15행 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch6 itemSeq ∩ 기존 alias = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.

## 6. validator 조건 (Phase 14 통과 기준) — ⚠️ #134 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 50건 status pending→**approved + incorporated 표시**, batch6 AR 50건 **incorporated=true**.
- **bulk candidate validator**:
  - 🔴 **#134 갱신 필수**: 현재 #134 = "batch6 incorporated=false(Phase 13 생성)". 반영하면 incorporated=true → **#134 FAIL**. → v0.5 #54/#74/#94/#114 진화와 **동일하게 #134 를 incorporation-aware(옵션 A)로 갱신**: "incorporated ∈ {false,true} 정합" + true 면 base+12(#132)로 실제 반영 검증. **PM 승인 필요(옵션 A 패턴).**
  - #133(≤50)·#135(incorporated 필드 보유)는 그대로 통과.
  - base+12(#132): incorporated=true 후보가 alias∈aliases · itemSeq∈whitelist[canonical] 실제 반영 검증.
- **v0.3 alias validator**: #8 이 verified +50 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 50건 각 alias→해당 canonical 1종 · filterRelations 결과가 그 canonical relation 전부. 회귀(타리비드3·포사맥스1·토렘2·넥시움0·#r15) 유지.

## 7. rollback 조건
- alias JSON 은 git 버전관리 → **반영 커밋 1개 단위**로 `git revert` 즉시 206 복원.
- STOP: 반영 후 alias_count ≠ 256 · relation ≠ 30 · DATA_URL 변경 · product_aliases ≠ 218 · verified ≠ 194 · validator/smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.

## 8. PM 승인 필요사항
1. **batch6 50건 반영 승인 여부**(alias 206→256).
2. **validator #134 incorporation-aware 갱신 승인**(옵션 A 패턴).
3. **source_relation_ids 매핑 확정**(§2 표) · batch6 신규 verified canonical 없음(전부 append) 확인.
4. 표면형 = 전체 품목명 확정.
5. 256 도달 후 방향: batch7 계속(단일성분 심층 재수집, 나머지 성분 long tail) → 500 진행.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
