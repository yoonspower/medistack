# MediStack v0.5 — Phase 12 batch 5 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-11** / 상태: **계획(반영 전 — PM 승인 대기)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase11_report.md`, `..._phase10_report.md`

> Phase 10(batch 4, alias 153→176)와 **동일한 incorporation 패턴**을 batch 5(30건, alias 176→206)에 적용하기 위한 사전 계획. **🎯 batch 5 반영 시 alias 206 = v0.5 목표 200 도달.** **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트(Phase 12).**

---

## 1. 목적 / 범위
- Phase 11 산출 **batch 5 approved-ready 30건**(`data/candidates/bulk_alias_approved_ready_batch5_v0_5.json`, 현재 incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- Phase 10 패턴 그대로: **product_aliases +30 AND verified_item_seqs +30 동반 확장**.
- **이번 단계(문서)에서는 반영하지 않는다.** alias_count 176 유지, alias JSON 무변경.

## 2. batch 5 approved-ready 30건 (반영 대상)
canonical 6성분. 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high. 표면형/itemSeq 전체 목록은 `..._phase11_report.md` §4 참조.

| canonical | 건수 | source_relation_ids | verified_item_seqs |
|---|---|---|---|
| 레보플록사신 | 6 | [1, 2, 3] | 기존(append) |
| 메트포르민 | 5 | [12] | 기존(append) |
| 시프로플록사신 | 5 | [4, 5, 6] | 기존(append) |
| 알렌드론산 | 5 | [29] | 기존(append) |
| 오메프라졸 | 4 | [13, 14] | 기존(append) |
| 오플록사신 | 5 | [21, 22, 23] | 기존(append) |

> **batch 5 의 6성분은 전부 기존 verified canonical 키** → 반영은 **append only**, **verified canonicals 12 → 12 유지(신규 키 없음)**.

## 3. 반영 매핑 (Phase 12 실행 시)
### 3-1. product_aliases (+30)
각 항목 = 기존 스키마 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. source_relation_ids = §2 표.
### 3-2. verified_item_seqs (+30 entries)
- 6개 기존 성분에 **append**(신규 키 없음) → verified canonical **12 → 12 유지**, entries **114 → 144**.
- 각 entry 추적정보: `{item_seq, item_name, verified_at, method:"...v0.5-batch-5 ingrName=...", batch_id:"v0.5-batch-5", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 11) | 반영 후(Phase 12) |
|---|---|---|
| meta.alias_count | 176 | **206** 🎯(v0.5 목표 200 도달) |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 138 | **168** (+30) |
| verified_item_seqs entries | 114 | **144** (+30) |
| verified canonicals | 12 | **12** (불변 — append only) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 12 에서도 불변)
- relation export 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch 5 엔 없음) · 에스오메프라졸 alias 금지 · 15행 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch 5 itemSeq ∩ 기존 alias = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.
- held 51(Phase 11 cap 초과 confirmed)은 이번 batch 에 **포함하지 않는다**(batch 5 = 정확히 30).

## 6. validator 조건 (Phase 12 통과 기준) — ⚠️ #114 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 30건 status pending→**approved + incorporated 표시**, batch 5 AR 30건 **incorporated=true**.
- **bulk candidate validator**:
  - 기존 incorporation-aware 체크 유지(#16 alias_count==항목수·relation30·≥66 단조 → 206 통과, #112 incorporated 후보 실제 반영검증 등).
  - **🔴 #114 갱신 필수**: 현재 #114 = "batch 5 는 incorporated=false". 반영하면 incorporated=true → **#114 FAIL**. → Phase 6 #54 / Phase 8 #74 / Phase 10 #94 진화와 **동일하게 #114 를 incorporation-aware(옵션 A)로 갱신**: "incorporated ∈ {false,true} 정합" + true 면 base+12(#112)로 실제 반영 검증. **PM 승인 필요(옵션 A 패턴).**
  - #113(≤30)·#115(incorporated 필드 보유)는 그대로 통과.
- **v0.3 alias validator**: #8 이 verified +30 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 30건 각 alias→해당 canonical 1종 · filterRelations 결과가 그 canonical relation 전부. 회귀 유지.

## 7. rollback 조건
- alias JSON 은 git 버전관리 → **반영 커밋 1개 단위**로 `git revert` 즉시 176 복원.
- STOP: 반영 후 alias_count ≠ 206 · relation ≠ 30 · DATA_URL 변경 · product_aliases ≠ 168 · verified ≠ 144 · validator/smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.

## 8. PM 승인 필요사항
1. **batch 5 30건 즉시 반영 승인 여부**(alias 176→206, v0.5 목표 200 도달).
2. **validator #114 incorporation-aware 갱신 승인**(옵션 A 패턴).
3. **source_relation_ids 매핑 확정**(§2 표) · batch 5 신규 verified canonical 없음(전부 append) 확인.
4. 표면형 = 전체 품목명 확정.
5. 200 도달 후 방향: **v0.5 종료/릴리스 노트 vs batch 6 계속(held 51 → ~236)**.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
