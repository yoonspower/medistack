# MediStack v0.5 — Phase 6 batch 2 incorporation 계획 (⚠️ 계획만, 실제 반영 금지)

작성일: **2026-06-11** / 상태: **계획 문서 (alias JSON 미수정)** / 상위: `..._pipeline_plan.md`, `..._phase5_report.md`, `..._phase4_report.md`

> **이 문서는 계획만 기술한다. `data/medistack_v0.3_aliases.json` 은 절대 수정하지 않는다. 실제 batch 2 반영은 다음 PM 판정 후 별도 진행.**
> Phase 4(batch 1, alias 66→93)와 **동일한 incorporation 패턴**을 batch 2(30건, alias 93→123)에 적용하기 위한 사전 계획.

---

## 1. 목적 / 범위
- Phase 5 산출 **batch 2 approved-ready 30건**(`data/candidates/bulk_alias_approved_ready_batch2_v0_5.json`, 현재 incorporated=false)을 `data/medistack_v0.3_aliases.json` 에 반영.
- Phase 4 패턴 그대로: **product_aliases +30 AND verified_item_seqs +30 동반 확장**(둘 다 해야 v0.3 validator #8 `itemSeq ∈ relation itemSeq ∪ verified 화이트리스트` 통과).
- **이번 단계(문서)에서는 반영하지 않는다.** alias_count 93 유지, alias JSON 무변경.

## 2. batch 2 approved-ready 30건 (반영 대상)
canonical 라운드로빈 균등분산 9성분(Phase 5 `--ar-balanced`). 전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high.

| canonical | 건수 | itemSeq → 표면형(품목명) |
|---|---|---|
| 독시사이클린 | 4 | 201406196 독시라마이신캡슐100mg(독시사이클린수화물) · 201908023 독시메디정(독시사이클린수화물) · 201507460 독시엔디정(독시사이클린수화물) · 202202687 독시크정50밀리그램(독시사이클린수화물) |
| 레보티록신 | 4 | 201902912 씬지로이드정0.0375밀리그램 · 201605340 씬지로이드정0.075밀리그램 · 201900107 씬지로이드정0.112밀리그램 · 201804237 씬지로이드정0.2밀리그램 (전부 레보티록신나트륨수화물) |
| 레보플록사신 | 4 | 200201176 동구레보플록사신수화물정100mg · 200800332 동구레보플록사신수화물정250mg · 200800333 동구레보플록사신수화물정500mg · 200200715 동성레보플록사신정 |
| 메트포르민 | 3 | 199301512 그리코민정 · 199701437 그린페지정 · 200607691 글라비스서방정500밀리그람 (전부 메트포르민염산염) |
| 목시플록사신 | 3 | 199906848 아벨록스정400밀리그람 · 201406133 조이록신정400밀리그램 · 201201789 퀴녹스정400밀리그램 (전부 목시플록사신염산염) |
| 시프로플록사신 | 3 | 199603455 록신정250밀리그램 · 200201724 메가록신정250밀리그램 · 201901582 메가시플록정 (전부 시프로플록사신염산염수화물) |
| 알렌드론산 | 3 | 200501339 본에이드정70밀리그램 · 200803184 본필정70밀리그램 · 201507146 비노스토발포정 (알렌드론산나트륨수화물/삼수화물) |
| 오메프라졸 | 3 | 200302518 대한뉴팜오엠프라졸캡슐 · 199202074 라메졸캡슐20밀리그램 · 200402992 메프라졸캡슐 (전부 오메프라졸) |
| 오플록사신 | 3 | 201603714 리록신정 · 199502582 삼익오플록사신정 · 199100970 삼천당오플록사신정 (전부 오플록사신) |

(전체 필드는 approved-ready 파일 참조. 표면형=전체 품목명, Phase 4와 동일 규약.)

## 3. 반영 매핑 (Phase 6 실행 시)
### 3-1. product_aliases (+30)
각 항목 = 기존 스키마 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. **source_relation_ids = 해당 canonical 의 라이브 relation id**(아래 확정 매핑, 라이브 export 에서 산출):

| canonical | source_relation_ids | verified_item_seqs |
|---|---|---|
| 독시사이클린 | [7, 8, 9] | 기존 성분(append) |
| 레보티록신 | [10, 11] | 기존 |
| 레보플록사신 | [1, 2, 3] | 기존 |
| 메트포르민 | [12] | 기존 |
| 목시플록사신 | [24, 25] | 기존 |
| 시프로플록사신 | [4, 5, 6] | 기존 |
| 알렌드론산 | [29] | 기존 |
| **오메프라졸** | **[13, 14]** | **NEW 성분(verified 신규 키)** |
| 오플록사신 | [21, 22, 23] | 기존 |

### 3-2. verified_item_seqs (+30 entries)
- 8개 기존 성분에 append, **오메프라졸은 신규 canonical 키 생성** → verified canonical **11 → 12**.
- 각 entry 추적정보 보존(Phase 4 패턴): `{item_seq, item_name, verified_at, method:"nedrug searchDrug+getItemDetail Phase5 batch v0.5-batch-2 ingrName=...", batch_id:"v0.5-batch-2", source_method, source_checked_at, detail_checked_at}`.

## 4. 예상 결과 (반영 후)
| 항목 | 현재(Phase 5) | 반영 후(Phase 6) |
|---|---|---|
| meta.alias_count | 93 | **123** |
| ingredient_aliases | 38 | 38(불변) |
| product_aliases | 55 | **85** (+30) |
| verified_item_seqs entries | 31 | **61** (+30) |
| verified canonicals | 11 | **12** (오메프라졸 신규) |
| relations | 30 | 30(불변) |
| DATA_URL | v0.2 export | 불변 |

## 5. 반영 금지 항목 (Phase 6 에서도 불변)
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · DATA_URL 불변 · data export 수정 금지.
- 앱 코드/UI 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- brand_core/복합제 alias 추가 금지(batch 2 엔 없음 — 전부 단일성분) · 에스오메프라졸 alias 금지 · 15행(id15 ×B12) 재편입 금지.
- published/clinical_reviewed 전환 금지 · 천장 verified_reference 유지.
- 미검증 alias/itemSeq 금지 · 동일 itemSeq 중복 alias 금지(batch 2 itemSeq ∩ 기존 alias itemSeq = 0 확인됨).
- 신규 tag 금지 · 수동 deploy 금지.
- held 53(Phase 5 cap 초과 confirmed)은 이번 batch 에 **포함하지 않는다**(batch 2 = 정확히 30).

## 6. validator 조건 (Phase 6 통과 기준) — ⚠️ #54 incorporation-aware 갱신 필요
반영 후 기대 상태:
- queue 30건 status pending→**approved + incorporated 표시**(Phase 4 패턴), batch 2 AR 30건 **incorporated=true**.
- **bulk candidate validator**:
  - 기존 incorporation-aware 체크 유지: #7/#24/#44/#31/#51(incorporated 제외), #16(alias_count==항목수·relation30·≥66 단조 → 123 통과), #30(queue approved 는 alias 반영 검증), #32/#52(incorporated 후보는 alias 실제 반영 검증).
  - **🔴 #54 갱신 필수**: 현재 #54 = "batch 2 approved-ready 는 incorporated=false". 반영하면 incorporated=true 가 되어 **#54 가 FAIL**. → Phase 4 의 #16/#7/#24/#31 진화와 동일하게 **#54 를 incorporation-aware 로 갱신**(예: "incorporated ∈ {false(미반영), true(반영)} 정합" + true 면 #52 로 실제 반영 검증) 또는 #52 로 대체. **이 validator 진화는 PM 승인 필요(Phase 4 옵션 A 패턴).**
  - #53(≤30)·#55(incorporated 필드 보유)는 그대로 통과.
- **v0.3 alias validator**: #8(itemSeq ∈ relation ∪ verified 화이트리스트)이 verified +30 동반확장으로 통과. 13/13 유지.
- **v0.1 12/12 · v0.2 15/15 · TypeB 7/7** 회귀 0.
- **smoke**: 신규 30건 각 alias→resolveAliasIngredients 정확히 해당 canonical 1종 · filterRelations 결과가 그 canonical relation 전부. 회귀(타리비드/포사맥스/토렘/넥시움0/#r15 fail-safe) 유지.

## 7. rollback 조건
- alias JSON 은 git 버전관리 → **반영 커밋 1개 단위**로 묶어 `git revert <commit>` 로 즉시 93 복원(batch 단위 원자성).
- STOP: 반영 후 alias_count ≠ 123 · relation ≠ 30 · DATA_URL 변경 · product_aliases ≠ 85 · verified ≠ 61 · validator/ smoke 실패 · Actions/deploy 실패 → 즉시 중단·revert.
- queue/AR 의 incorporated 표시도 동일 커밋에 포함(원복 시 함께 revert).

## 8. PM 승인 필요사항
1. **batch 2 30건 즉시 반영 승인 여부**(alias 93→123).
2. **validator #54 incorporation-aware 갱신 승인**(Phase 4 옵션 A 패턴 — 반영 후 #54 충돌 해소). 갱신 없이는 반영 후 bulk validator FAIL.
3. **source_relation_ids 매핑 확정**(§3-1 표) · **오메프라졸 verified 신규 canonical 생성 확인**.
4. 표면형 = 전체 품목명(Phase 4 동일) 확정.
5. 반영 후 **held 53 → batch 3 처리 시점**(batch 2 반영 직후 연속 vs 별도 게이트).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 실제 alias 반영은 다음 PM 게이트.**
