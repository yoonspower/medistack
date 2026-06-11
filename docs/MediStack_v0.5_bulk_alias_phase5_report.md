# MediStack v0.5 — bulk alias pipeline Phase 5 보고서 (후보 풀 확대 + batch 2 approved-ready 생성)

작성/실행일: **2026-06-11** / 단계: **Phase 5 (재수집 상한 5→15 + 페이지네이션 → batch 2 approved-ready 30건 생성)** / 상위: `..._pipeline_plan.md`, `..._phase4_report.md`

> PM 판정(Phase 5): nedrug searchDrug 재수집 상한을 성분당 **15**로 올려 후보 풀 확대. 신규 pending 만 getItemDetail 상세확정 → **batch 2 approved-ready 후보 파일(최대 30, incorporated=false)** 생성까지만. **alias JSON 절대 미수정 · 실제 batch 2 반영은 다음 PM 게이트(Phase 6)**. batch 1 incorporated 27건·기존 이력 보존. 복합제/brand_core/에스오메프라졸/15행 approved-ready 금지. 품질 우선(≤30, <30도 실패 아님).

---

## 1. 생성/수정 파일
| 파일 | 변경 |
|---|---|
| `scripts/collect_nedrug_alias_candidates.py` | **페이지네이션**(`--max-pages`, page=N 순회) + `--batch-id`/`--phase`(phaseN_collection) + 기존 meta·이력 보존(phase2~4 비파괴) + CSV 동적 superset + product_aliases itemSeq 중복기준 추가 |
| `scripts/confirm_nedrug_item_details.py` | `--target-batch`(신규만 확정) + `--ar-batch-id`/`--ar-incorporated`/`--ar-limit`/`--ar-only-batch`/`--ar-balanced`(canonical 라운드로빈) + incorporated 필드 + idempotent 재실행(재네트워크 생략) + phaseN_confirmation + CSV superset |
| `scripts/validate_bulk_alias_candidates.py` | `_validate_approved_ready` 파라미터화(base_no/tag) → **batch 2 검증 추가(#40~52)** + #53(≤30)·#54(incorporated=false)·#55(incorporated 필드) |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 신규 후보 115건 병합(status pending/deferred only). 기존 62건·status·이력 보존 |
| `data/candidates/bulk_alias_approved_ready_batch2_v0_5.json/csv` | **신규 생성** — batch 2 approved-ready 30건(approved_ready=true·incorporated=false·reviewer_required=true) |
| (불변) `data/medistack_v0.3_aliases.json` | **0 diff(완전 무변경)** — alias_count 93·product 55·verified 11성분/31 |
| (불변) relation export(v0.1/v0.2)·batch1 AR·src/·index.html·.github/ | 무변경(git diff 0) |

## 2. 재수집 대상 canonical / 상한
- 대상 = 라이브 relation 성분 − 에스오메프라졸 − excluded-only = **13개**(독시사이클린·레보티록신·레보플록사신·메트포르민·목시플록사신·미노사이클린·시프로플록사신·알렌드론산·**오메프라졸**·오플록사신·토라세미드·푸로세미드·**히드로클로로티아지드**).
  - Phase 2~4는 11성분만 커버 → 이번에 **오메프라졸·히드로클로로티아지드** 신규 진입(오메프라졸은 에스오메프라졸과 별개 라이브 성분, 허용).
- **max-per-ingredient = 15** (PM 지정, 5→15). **max-pages = 6**(searchDrug 페이지당 15행·수출/원료/주사 노이즈 多 → page 1만으론 batch1이 이미 소진. 페이지네이션 필수).

## 3. 수집 결과(신규 queue 후보)
- **신규 115건**: pending(단일성분) **83** + deferred(복합제) **32**. 전체 queue **62 → 177**.
- 성분별 수집(pending 단일 기준): 독시6·레보티록신11·레보플록사신15·메트포르민4·목시3·시프로15·알렌드론산9·오메프라졸5·오플록사신15(미노/토라세미드/푸로세미드/HCTZ는 page 1~6서 신규 단일 0, 대부분 batch1 소진 또는 복합제).
- HCTZ·메트포르민·알렌드론산 등은 복합제 신호('/') 다수 → **deferred 강등**(approved-ready 금지).

## 4. 전체 queue 후보 수 / 분포
- **total 177** — pending 88 · approved 27 · rejected 2 · deferred 60.
- batch_id: v0.5-001(16: brand_core 14 deferred + rejected 2) · v0.5-002(46: pending 5 + approved 27 + combo deferred 14) · **v0.5-005(115: pending 83 + combo deferred 32)**.
- detail_confirmed=true 누적 **114**(approved 27 + 기존 redundant 4 + 신규 83).

## 5. 신규 상세확정(getItemDetail) 결과
- 대상 신규 pending **83건**(`--target-batch v0.5-005`) → **confirmed 83 / 83(100%)**. combo·성분불일치·품목명불일치·표면형·fetch/parse 실패 **0**.
- 사유: 수집 단계 사전필터(주성분 단일·완제·경구·정상)가 정확 → 상세서 품목명·단일 주성분 전수 일치. 전부 source_method=nedrug.getItemDetail·confidence=high.

## 6. batch 2 approved-ready 후보 수 / 분포
- **30건**(cap 30 적용, held 53). **canonical 라운드로빈 균등 분산**으로 dose 변이 독식 방지:
  - 독시사이클린 4 · 레보티록신 4 · 레보플록사신 4 · 메트포르민 3 · 목시플록사신 3 · 시프로플록사신 3 · 알렌드론산 3 · 오메프라졸 3 · 오플록사신 3 (**9개 canonical**).
- 전부 단일성분·완제·경구·getItemDetail 원문확정. approved_ready=true · **incorporated=false** · reviewer_required=true · batch_id=v0.5-batch-2.
- (균등 분산 미적용 시 알파벳순 → 독시/레보티록신/레보플록사신 3성분 독식·씬지로이드 dose 11개 등 성분내 중복 과다였음. `--ar-balanced`로 9성분 분산 = 검색 커버리지 우선.)

## 7. 제외/보류 사유 요약
- **held 53**(v0.5-005 confirmed, batch2 외, cap 초과분): 독시2·레보티록신7·레보플록사신11·메트포르민1·시프로12·알렌드론산6·오메프라졸2·오플록사신12. **queue 에 detail_confirmed=true·pending 으로 staged → batch 2 반영(Phase 6) 후 itemSeq 가 alias 진입하면 batch 3/4 로 자동 회수**.
- **복합제 deferred 32(신규)**: 주성분 '/' 다성분 — 단일성분 아님, approved-ready 금지(사람 검토 tier).
- 기존 보류: brand_core deferred 14 · rejected 2 · 기존 itemSeq 중복 pending 4 · 표면형 개행 pending 1 · 복합제 deferred 14(v0.5-002).
- **에스오메프라졸/15행**: 영구 제외(canonical·itemSeq 201600209·품목명/주성분 신호 다층 차단). 오메프라졸(별개 라이브 성분)은 정상 채택.

## 8. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(main + batch1 + **batch2**) | **PASS 47/47** (기존 32 + batch2 신규 15: #40~52 + #53/54/55) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (alias JSON 무변경) |
| Type B suite | **PASS 7/7** |
| 음성 테스트(ephemeral) | **5/5** — count>30→#53 · incorporated 위조→#54(+#52) · 복합제→#47 · 에스오메프라졸→#45/#46 · 필드누락→#55 (위반 정확 포착) |

## 9. smoke test 결과
- **회귀 ALL PASS**(alias JSON 무변경 → Phase 4와 동일): 타리비드→오플록사신 3 · 포사맥스→알렌드론산 1 · 토렘→토라세미드 2 · 넥시움→0 · #/r/15(excluded B12) fail-safe · renderable pool 30.
- **batch 2 미반영 확인**: 30건 전부 라이브 alias 검색 해석 0 · 기존 alias/verified itemSeq 중복 0 (앱 동작 불변, batch 2 는 아직 검색되지 않음).

## 10. 불변 / 안전
- **alias JSON 완전 무변경(git diff 0)** · alias_count **93 유지** · product 55 · verified 11/31 · **relation 30 유지** · DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**.
- batch 1 incorporated 27건 그대로 · batch 1 AR 파일 무변경 · 실제 alias 추가 0 · approved status 신규 0(여전히 27).
- 복합제/brand_core/에스오메프라졸/15행 approved-ready 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- alias 는 검색 보조(guards.js 는 ingredient_aliases+product_aliases만 인덱싱). relation 신규생성 없음.

## 11. 다음 단계 (Phase 6 제안)
1. **batch 2 실제 alias 반영(Phase 6 게이트)**: approved-ready 30건을 `data/medistack_v0.3_aliases.json` 에 product_aliases +30 **AND** verified_item_seqs +30 동반 확장(Phase 4 패턴). alias_count 93 → **123**. queue 30건 status pending→approved+incorporated, batch2 AR incorporated=true. validator 전종 재통과 + smoke.
2. **batch 3**: held 53(이미 confirmed)을 batch 2 반영 후 build(existing_seqs 가 batch2 itemSeq 제외 → 다음 30 자동) → ~123→153. 추가 재수집(다른 성분/페이지) 병행 → 200 도달.
3. 잔여 처리: 복합제 deferred(별도 tier 판정) · 표면형 개행 정제 · brand_core tier.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / batch 2 는 incorporated=false(미반영) — 실제 반영은 Phase 6 게이트.
