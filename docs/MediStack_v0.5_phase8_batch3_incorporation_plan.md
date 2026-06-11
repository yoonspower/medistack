# MediStack v0.5 — Phase 8 batch 3 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-11** / 상태: **계획(반영 전 — PM 승인 대기)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase7_report.md`, `..._phase6_report.md`

> Phase 6(batch 2, alias 93→123)와 **동일한 incorporation 패턴**을 batch 3(30건, alias 123→153)에 적용하기 위한 사전 계획. **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트(Phase 8).**

---

## 1. 목적 / 범위
- Phase 7 산출 **batch 3 approved-ready 30건**(`data/candidates/bulk_alias_approved_ready_batch3_v0_5.json`, 현재 incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- Phase 6 패턴 그대로: **product_aliases +30 AND verified_item_seqs +30 동반 확장**(둘 다 해야 v0.3 validator #8 `itemSeq ∈ relation itemSeq ∪ verified 화이트리스트` 통과).
- **이번 단계(문서)에서는 반영하지 않는다.** alias_count 123 유지, alias JSON 무변경.

## 2. batch 3 approved-ready 30건 (반영 대상)
canonical 라운드로빈 균등분산 8성분(Phase 7 `--ar-balanced`). 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high. 표면형/itemSeq 전체 목록은 `..._phase7_report.md` §3 및 approved-ready 파일 참조.

| canonical | 건수 | source_relation_ids | verified_item_seqs |
|---|---|---|---|
| 독시사이클린 | 2 | [7, 8, 9] | 기존 성분(append) |
| 레보티록신 | 5 | [10, 11] | 기존(append) |
| 레보플록사신 | 5 | [1, 2, 3] | 기존(append) |
| 메트포르민 | 1 | [12] | 기존(append) |
| 시프로플록사신 | 5 | [4, 5, 6] | 기존(append) |
| 알렌드론산 | 5 | [29] | 기존(append) |
| 오메프라졸 | 2 | [13, 14] | 기존(append, batch 2 서 신규생성됨) |
| 오플록사신 | 5 | [21, 22, 23] | 기존(append) |

> **Phase 6 과 차이**: batch 3 의 8성분은 **전부 기존 verified canonical 키**(오메프라졸 포함 — batch 2 서 12번째로 생성). 따라서 batch 3 반영은 **append only**, **verified canonicals 12 → 12 유지(신규 키 없음)**. (Phase 6 은 오메프라졸 신규 키 1개 생성으로 11→12 였음.)

## 3. 반영 매핑 (Phase 8 실행 시)
### 3-1. product_aliases (+30)
각 항목 = 기존 스키마 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. source_relation_ids = §2 표의 라이브 relation id(canonical 별).

### 3-2. verified_item_seqs (+30 entries)
- 8개 기존 성분에 **append**(신규 canonical 키 없음) → verified canonical **12 → 12 유지**, entries **61 → 91**.
- 각 entry 추적정보 보존(Phase 6 패턴): `{item_seq, item_name, verified_at, method:"nedrug searchDrug+getItemDetail Phase5 batch v0.5-batch-3 ingrName=...", batch_id:"v0.5-batch-3", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 7) | 반영 후(Phase 8) |
|---|---|---|
| meta.alias_count | 123 | **153** |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 85 | **115** (+30) |
| verified_item_seqs entries | 61 | **91** (+30) |
| verified canonicals | 12 | **12** (불변 — append only) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 8 에서도 불변)
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch 3 엔 없음 — 전부 단일성분) · 에스오메프라졸 alias 금지 · 15행(id15 ×B12) 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch 3 itemSeq ∩ 기존 alias itemSeq = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.
- held 23(Phase 7 cap 초과 confirmed)은 이번 batch 에 **포함하지 않는다**(batch 3 = 정확히 30).

## 6. validator 조건 (Phase 8 통과 기준) — ⚠️ #74 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 30건 status pending→**approved + incorporated 표시**(Phase 6 패턴), batch 3 AR 30건 **incorporated=true**.
- **bulk candidate validator**:
  - 기존 incorporation-aware 체크 유지(#16 alias_count==항목수·relation30·≥66 단조 → 153 통과, #30 queue approved 반영검증, #52/#72 incorporated 후보 실제 반영검증 등).
  - **🔴 #74 갱신 필수**: 현재 #74 = "batch 3 approved-ready 는 incorporated=false". 반영하면 incorporated=true 가 되어 **#74 가 FAIL**. → Phase 6 의 #54 진화와 **동일하게 #74 를 incorporation-aware(옵션 A)로 갱신**: "incorporated ∈ {false(미반영), true(반영)} 정합" + true 면 base+12(#72)로 실제 반영 검증. **이 validator 진화는 PM 승인 필요(Phase 4/6 옵션 A 패턴).**
  - #73(≤30)·#75(incorporated 필드 보유)는 그대로 통과.
- **v0.3 alias validator**: #8(itemSeq ∈ relation ∪ verified 화이트리스트)이 verified +30 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 30건 각 alias→resolveAliasIngredients 정확히 해당 canonical 1종 · filterRelations 결과가 그 canonical relation 전부. 회귀(타리비드/포사맥스/토렘/넥시움0/#r15 fail-safe) 유지.

## 7. rollback 조건
- alias JSON 은 git 버전관리 → **반영 커밋 1개 단위**로 묶어 `git revert <commit>` 로 즉시 123 복원(batch 단위 원자성).
- STOP: 반영 후 alias_count ≠ 153 · relation ≠ 30 · DATA_URL 변경 · product_aliases ≠ 115 · verified ≠ 91 · validator/smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.
- queue/AR 의 incorporated 표시도 동일 커밋에 포함(원복 시 함께 revert).

## 8. PM 승인 필요사항
1. **batch 3 30건 즉시 반영 승인 여부**(alias 123→153).
2. **validator #74 incorporation-aware 갱신 승인**(Phase 4/6 옵션 A 패턴 — 반영 후 #74 충돌 해소). 갱신 없이는 반영 후 bulk validator FAIL.
3. **source_relation_ids 매핑 확정**(§2 표) · **batch 3 는 신규 verified canonical 없음(전부 append) 확인**.
4. 표면형 = 전체 품목명(Phase 4~6 동일) 확정.
5. 반영 후 **held 23 + 추가 재수집 → batch 4 처리 시점**(연속 vs 별도 게이트).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
