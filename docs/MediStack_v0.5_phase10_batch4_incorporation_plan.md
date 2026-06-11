# MediStack v0.5 — Phase 10 batch 4 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-11** / 상태: **계획(반영 전 — PM 승인 대기)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase9_report.md`, `..._phase8_report.md`

> Phase 8(batch 3, alias 123→153)와 **동일한 incorporation 패턴**을 batch 4(23건, alias 153→176)에 적용하기 위한 사전 계획. **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트(Phase 10).**

---

## 1. 목적 / 범위
- Phase 9 산출 **batch 4 approved-ready 23건**(`data/candidates/bulk_alias_approved_ready_batch4_v0_5.json`, 현재 incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- Phase 8 패턴 그대로: **product_aliases +23 AND verified_item_seqs +23 동반 확장**(둘 다 해야 v0.3 validator #8 통과).
- **이번 단계(문서)에서는 반영하지 않는다.** alias_count 153 유지, alias JSON 무변경.

## 2. batch 4 approved-ready 23건 (반영 대상)
canonical 5성분. 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high. 표면형/itemSeq 전체 목록은 `..._phase9_report.md` §3 참조.

| canonical | 건수 | source_relation_ids | verified_item_seqs |
|---|---|---|---|
| 레보티록신 | 2 | [10, 11] | 기존(append) |
| 레보플록사신 | 6 | [1, 2, 3] | 기존(append) |
| 시프로플록사신 | 7 | [4, 5, 6] | 기존(append) |
| 알렌드론산 | 1 | [29] | 기존(append) |
| 오플록사신 | 7 | [21, 22, 23] | 기존(append) |

> **batch 4 의 5성분은 전부 기존 verified canonical 키** → batch 4 반영은 **append only**, **verified canonicals 12 → 12 유지(신규 키 없음)**. (Phase 8 과 동일.)

## 3. 반영 매핑 (Phase 10 실행 시)
### 3-1. product_aliases (+23)
각 항목 = 기존 스키마 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. source_relation_ids = §2 표의 라이브 relation id.

### 3-2. verified_item_seqs (+23 entries)
- 5개 기존 성분에 **append**(신규 canonical 키 없음) → verified canonical **12 → 12 유지**, entries **91 → 114**.
- 각 entry 추적정보 보존: `{item_seq, item_name, verified_at, method:"...v0.5-batch-4 ingrName=...", batch_id:"v0.5-batch-4", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 9) | 반영 후(Phase 10) |
|---|---|---|
| meta.alias_count | 153 | **176** |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 115 | **138** (+23) |
| verified_item_seqs entries | 91 | **114** (+23) |
| verified canonicals | 12 | **12** (불변 — append only) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 10 에서도 불변)
- relation export 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch 4 엔 없음 — 전부 단일성분) · 에스오메프라졸 alias 금지 · 15행 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch 4 itemSeq ∩ 기존 alias itemSeq = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.

## 6. validator 조건 (Phase 10 통과 기준) — ⚠️ #94 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 23건 status pending→**approved + incorporated 표시**(Phase 8 패턴), batch 4 AR 23건 **incorporated=true**.
- **bulk candidate validator**:
  - 기존 incorporation-aware 체크 유지(#16 alias_count==항목수·relation30·≥66 단조 → 176 통과, #72/#92 incorporated 후보 실제 반영검증 등).
  - **🔴 #94 갱신 필수**: 현재 #94 = "batch 4 approved-ready 는 incorporated=false". 반영하면 incorporated=true → **#94 FAIL**. → Phase 6 #54 / Phase 8 #74 진화와 **동일하게 #94 를 incorporation-aware(옵션 A)로 갱신**: "incorporated ∈ {false,true} 정합" + true 면 base+12(#92)로 실제 반영 검증. **PM 승인 필요(옵션 A 패턴).**
  - #93(≤30)·#95(incorporated 필드 보유)는 그대로 통과.
- **v0.3 alias validator**: #8 이 verified +23 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 23건 각 alias→해당 canonical 1종 · filterRelations 결과가 그 canonical relation 전부. 회귀 유지.

## 7. rollback 조건
- alias JSON 은 git 버전관리 → **반영 커밋 1개 단위**로 `git revert` 즉시 153 복원.
- STOP: 반영 후 alias_count ≠ 176 · relation ≠ 30 · DATA_URL 변경 · product_aliases ≠ 138 · verified ≠ 114 · validator/smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.

## 8. PM 승인 필요사항
1. **batch 4 23건 즉시 반영 승인 여부**(alias 153→176).
2. **validator #94 incorporation-aware 갱신 승인**(옵션 A 패턴).
3. **source_relation_ids 매핑 확정**(§2 표) · batch 4 신규 verified canonical 없음(전부 append) 확인.
4. 표면형 = 전체 품목명 확정.
5. 반영 후 **재수집 → batch 5 처리 시점**(held 소진, 200 도달엔 ~24건 추가 재수집 필요).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
