# MediStack v0.6 — alias 500 확장 계획 (계획 문서 · 실행 전)

작성일: **2026-06-11** (마감 갱신 **2026-06-12**) / 상태: **✅ v0.6 마감 — 단일성분 트랙 천장 alias 382 도달·옵션 A(382 마감) 채택** / 상위: `MediStack_v0.6_release_notes.md`, `MediStack_v0.6_handoff.md` / 시작점: **v0.5-beta(alias 206, commit `9dae621`)** / 종료점: **alias 382 도달 commit `67724a4` → `v0.6-beta` 마감 태그(릴리스노트 포함 스냅샷)**

> v0.6 의 목표는 검색 보조 alias 를 **206 → 500** 으로 확장하는 것뿐이다. **relation(약-영양소 의료 데이터)·DATA_URL·앱 UI 는 v0.6 에서도 불변**이며, alias 는 검색 보조일 뿐 의학정보가 아니다. 이 문서는 설계·근거·게이트만 정의하고, **이 단계에서 nedrug 후보 재수집도 alias JSON 반영도 코드/validator 수정도 하지 않는다.** 수치는 현재 repo 데이터에서 실측한 ground truth이며, 심층 재수집 수율만 추정(별도 recon dry-run으로 실측 예정)이다.

**현재 기준선 (2026-06-11 실측)**: alias_count **206** · ingredient_aliases 38 · product_aliases **168** · verified_item_seqs **144 entries / 12 canonical** · relations **30** · DATA_URL `./data/medistack_v0.2_beta_export.json`.

---

## 1. v0.6 목표

- **alias_count 206 → 500** (제품/성분 표면형 확장으로 검색 적중률 향상).
- **relation 30 유지** (의료 데이터 비확장 — alias 로 relation 신규 생성·풀 확장 금지).
- **DATA_URL 유지** (`./data/medistack_v0.2_beta_export.json` 불변).
- **제품/구매/제휴 UI 금지 유지** (칼륨 제품링크 금지 포함).
- **확장 우주 = relation 30 의 13 canonical 성분뿐.** relation 약물 14종 중 13종은 이미 alias 커버, 유일 미커버는 **에스오메프라졸(영구 alias 금지 대상)**. relation 30 동결이므로 **신규 성분 트랙은 없고**, 500 은 *기존 13성분의 단일성분 제품을 더 모으는 것*으로만 달성한다.

## 2. batch 전략

- **200~500 구간은 50개 단위로 확대.** batch6 부터 **+50 목표** (206 → 256 → 306 → 356 → 406 → 456 → 506). batch6~11 약 **6 batch** 로 500 초과.
- **품질 부족 시 30개 단위 유지 가능.** 특정 성분의 단일성분 완제 공급이 얕거나 getItemDetail 확정 통과율이 낮으면 해당 batch 는 +30 으로 축소(안전 우선, 무리한 +50 금지).
- **batch 당 approved-ready → incorporation 2단계 구조 유지** (생성↔반영 분리): 생성 단계는 alias 무반영(incorporated=false), 반영 단계는 PM 명시 승인 후 ephemeral `/tmp/ms_incorporate_v0_6_batchN.py`(전제/사후 assert, 미커밋)로 product_aliases + verified_item_seqs **동반 확장**.
- **즉시 공급 근거**: v0.5 Phase 11 재수집(v0.5-006)에서 남은 **held 55건**(확정완료 pending = detail_confirmed true, alias 미반영)이 있어 **batch6 +50 은 네트워크 0 으로 충당 가능**(잔여 5 → batch7 이월). batch7 이후는 단일성분 심층 재수집(§3)이 주 엔진.

| 공급 트랙 | 건수 | 비고 |
|---|---|---|
| held (batch6 즉시) | 55 | 시프로20·레보17·오플8·알렌6·독시1·미노1·토라1·푸로1, 네트워크 0 |
| 심층 재수집 (batch7~) | ~+240 추정 | 13성분 단일성분 long tail, recon 으로 실측 |
| (제외) brand_core | 14 | **v0.6 제외**(§3) |
| (제외) 복합제 combo | 105 | **v0.6 제외**(§3) |

## 3. 수집 전략

- **기존 relation 30 의 canonical 13성분 내에서 우선 확장.** 신규 성분·신규 relation 도입 금지.
- **nedrug searchDrug → getItemDetail 파이프라인 계속 사용.** searchDrug 로 후보 표면형/itemSeq 수집 → getItemDetail 원문으로 `ingrName` distinct=1(**단일성분**) 확정. 깊은 페이지(`--max-pages 20~30`, `--max-per-ingredient 40~60`)로 long tail 확보.
- **품질 게이트(불변)**: 점안/주사/원료/복합제 코드 필터 → **단일성분·완제·경구**만. confidence high. nedrug 품목명 개행 포함 표면형은 정규화(개행 제거) 후 적재(미정규화분 보류).
- **기존 verified_item_seqs 중복 제외.** collect dedup 4중(surface ∉ alias · ∉ queue · itemSeq ∉ alias · item_name ∉ alias)으로 **순수 net-new** 만 적재 → 동일 itemSeq 중복 alias 0.
- **제외 대상(v0.6 편입 금지)**:
  - **복합제(combo)** — 단일성분 매핑 부적합(현 'combo 금지' 불변규칙 유지).
  - **brand_core** — 용량/제형 제거 브랜드 어간, 무검증 오매칭 위험으로 v0.6 제외.
  - **에스오메프라졸** — id16 ×Mg 는 정상 live relation 이나 id15 ×B12 excluded 혼동 방지로 alias 금지.
  - **15행(id15, 에스오메프라졸×B12, excluded_v0_1)** — 앱 렌더 금지·재편입 금지.

## 4. validator 전략

- **incorporation-aware validator 유지.** batch 별 approved-ready 파일을 base_no 로 검증(생성 단계 strict false → 반영 단계 option A: incorporated ∈ {false(미반영), true(반영)} 정합, true 는 base+12 에서 alias 실제 반영 검증). base_no 를 **120 / 140 / 160 …** 로 연장(v0.5 의 20~100 패턴 계속). batch 당 약 +15 checks.
- **batch별 approved-ready → incorporation 구조 유지.** queue status pending→approved + AR incorporated=true + alias_count 갱신을 한 묶음으로 검증.
- **alias_count / product_aliases / verified_item_seqs 내부정합 검사 강화** (신규/보강 체크):
  - **C1**: `meta.alias_count == len(ingredient_aliases) + len(product_aliases)` (정확 일치).
  - **C2**: 모든 `product_alias.item_seq ∈ verified_item_seqs` (화이트리스트 완전성 — v0.3 #8 강화).
  - **C3**: `item_seq` 전역 중복 0 (동일 제품 중복 alias 금지).
  - **C4**: `verified_item_seqs` canonical 키 ⊆ **13 relation 약물 성분** (에스오메프라졸·미관계 성분 키 출현 시 FAIL).
  - **C5**: 모든 `product_alias.canonical_ingredient` 가 relation 약물 성분이며 ≠ 에스오메프라졸.
  - **C6**: `alias_count` 단조 증가 · `relations == 30` · `DATA_URL` 불변 (배포 게이트).
- 회귀(불변): v0.1 12/12 · v0.2 15/15 · v0.3 13/13 · TypeB 7/7 · bulk(현 92/92, batch 증가분 반영). smoke = batch 별 신규 N/N(각 alias→canonical 1종·filterRelations 결과가 그 canonical relation 전부) + 회귀(타리비드3·포사맥스1·토렘2·넥시움0·#r15 fail-safe). guards.js 는 package.json 없음 → `/tmp/*.mjs` 복사 후 node import.

## 5. v0.6 에서 하지 않을 것 (범위 밖)

- **relation 확장** (의료 상호작용 데이터 추가) — clinical reviewer 트랙.
- **DATA_URL 변경** · data export 변경.
- **published / clinical_reviewed 전환** · clinical claim 추가 (천장 = verified_reference 유지).
- **전체 10,000 품목명 인덱스 분리** — 장기 트랙(현 단일 alias 파일은 ~1-2k 까지 충분, 500 에선 불필요).
- **제품 추천 / 구매 / 제휴 UI** · 칼륨 제품링크.
- **복합제 / brand_core / 에스오메프라졸 / 15행 편입.**

## 6. 다음 단계

- **Phase 13 — batch6 후보 확보(재수집)**: held 55 활용을 기본으로 batch6 +50 구성(`confirm --no-network --ar-only-batch v0.5-006 --ar-balanced --ar-batch-id v0.6-batch-6 --ar-limit 50`). held 부족·품질 미달 시에만 nedrug 재수집(`--max-pages 20~30`)으로 보충. **alias 무반영**(approved-ready 생성, incorporated=false). validator strict false.
- **Phase 14 — batch6 실제 반영**: **PM 명시 승인 게이트** → ephemeral incorporate(product +50 · verified +50 동반확장 · alias_count 206→256) → validator base_no 120 + option A + smoke. queue status→approved, AR incorporated=true.
- **목표: 206 → 250~260** (batch6 +50 = 256, PM 목표 구간 내). 이후 batch7~ 심층 재수집으로 500 진행.

## 진행 메모 (2026-06-12)
- **✅ Phase 13 완료**: batch6 approved-ready **50건 생성**(held 51 pickable → balanced 50, 1 held over), **네트워크 0·alias 무반영**(incorporated=false). canonical 레보17·시프로19·알렌6·오플8. validator **107/107**(batch6 블록 base_no=120)·v0.1 12·v0.2 15·v0.3 13·TypeB 7·회귀 smoke 5/5 ALL PASS. alias_count 206·product 168·verified 144·relation 30·DATA_URL 불변(alias md5 동일). 상세=`MediStack_v0.6_phase13_batch6_candidate_report.md`.
- **✅ Phase 14 완료(2026-06-12)**: batch6 50건 alias 반영 — **product_aliases 168→218 · verified_item_seqs 144→194(4성분 append·canonicals 12 유지) · alias_count 206→256**, validator #134 옵션 A 갱신. 5 validator(bulk 107·v0.1 12·v0.2 15·v0.3 13·TypeB 7) + smoke 10/10 ALL PASS. relation 30·DATA_URL·export 불변. 계획/결과=`MediStack_v0.6_phase14_batch6_incorporation_plan.md`. **alias 256/500 — 다음 batch7~(단일성분 심층 재수집, 나머지 성분 long tail).**
- **✅ Phase 15 완료(2026-06-12)**: 외부 심층 재수집(`--max-pages 25/28`)으로 batch7 approved-ready **50건 생성**(레보13·메트12·시프로12·오메12·알렌1, 전부 기존 canonical·신규 0). 수집 158(단일 107 pending + 복합제 51 deferred·HCTZ 32 전량 복합제)→confirm 107/107→balanced 50(held 57 batch8 staged). **alias 무반영(256 유지)**·validator **122/122**(batch7 블록 base_no=140)·smoke 5/5. **✅ Phase 16 완료(2026-06-12)**: batch7 50건 반영 — product 218→268·verified 194→244(5성분 append·canonicals 12)·**alias 256→306**·#154 옵션 A. 5 validator(bulk 122)+smoke 10/10 PASS·무손실(256⊆306). **alias 306/500** — 누적 66→…→256→306. 다음=batch8(held 57·네트워크 0→~356). 리포트=`..._phase15_batch7_candidate_report.md`·계획/결과=`..._phase16_batch7_incorporation_plan.md`.
- **✅ Phase 17 완료(2026-06-12)**: held 57(Phase 15 staged)로 batch8 approved-ready **50건 생성**(레보14·시프로13·오메13·메트10·신규 canonical 0)·**네트워크 0·alias 무반영(306 유지)**. held 8 batch9 staged. validator **137/137**(batch8 base_no=160)·smoke 5/5. **✅ Phase 18 완료(2026-06-12)**: batch8 50건 반영 — product 268→318·verified 244→294(4성분 append·canonicals 12)·**alias 306→356**·#174 옵션 A. 5 validator(bulk 137)+smoke 9/9 PASS·무손실(306⊆356). **alias 356/500** — 누적 66→…→306→356. 다음=batch9(held 8·네트워크 0) 또는 신규 재수집. 리포트=`..._phase17_batch8_candidate_report.md`·계획/결과=`..._phase18_batch8_incorporation_plan.md`.
- **🚧 Phase 19 완료(2026-06-12) — 단일성분 공급 벽 도달**: 주력 심층 재수집(`--max-pages 35`)→신규 84(단일 18·복합제 deferred 66). batch9 AR **26건**(레보19·메트4·시프로2·오메1 = 신규18+held8)·**잔여 단일성분 0**(batch9가 전량). **시프로/오메/알렌/기타 7성분 신규 0 → 13 약물 단일성분 풀 소진**. **단일성분 천장 ≈ 382**(356+26). 500까지 잔여 118은 **deferred 복합제 236**(HCTZ112·메트77·알렌30 등)뿐 — `복합제 금지` 불변규칙에 차단. validator **152/152**·smoke 5/5·alias 356 불변. **✅ Phase 20 완료(2026-06-12)**: batch9 26건 반영 → **alias 382**(product 344·verified 320·canon 12)·#194 옵션 A·bulk 152+smoke 9/9·무손실(356⊆382)·라이브. 🏁 **단일성분 트랙 마감**. **500 방향 PM 결정 필요**: 옵션 A(382 마감·안전) / 옵션 B(복합제 tier 개방→500 가능·정책+안전검토 필요) / 옵션 C(brand_core·소량). 리포트=`..._phase19_batch9_recollect_report.md`·계획=`..._phase20_batch9_incorporation_plan.md`.

## 🏁 단일성분 트랙 마감 기록 (Phase 20, 2026-06-12)
- **최종 상태: alias 382 라이브** — ingredient_aliases 38 · product_aliases 344 · verified_item_seqs 320 entries / **12 canonical** · relations 30 불변 · DATA_URL 불변 · 앱 UI 불변.
- **단일성분 확장 완료**: v0.6 batch6~9 = **+176**(206 → 382). 13 relation 약물 중 단일성분 완제가 존재하는 성분을 전수 alias화 — 시프로/오메/알렌/독시/레보티록신/목시/미노/오플/토라/푸로 신규 단일성분 **0**(풀 소진), 레보·메트가 마지막 잔여 공급.
- **잔여(미사용 예비)**: deferred 복합제 **236**(HCTZ112·메트77·알렌30·오메6·기타) — `복합제 금지` 불변규칙으로 차단. 미확정 pending 7(엣지). brand_core 14.
- **500 도달은 단일성분 기준 불가**(천장 382). 잔여 118은 **복합제 tier 개방(옵션 B·PM 정책 결정)** 으로만 가능. v0.5 plan의 "단일성분 +~240 추정"은 과대평가(실측 +176).
- **파이프라인 자산 보존**: collect/confirm/validate 스크립트 · batch1~9 approved-ready · incorporation-aware validator(base_no 20~180·옵션 A) 전부 repo 유지 — 복합제 tier 또는 신규 relation 확장 시 재사용 가능.
- **PM 결정: 옵션 A(382 마감) 채택**(2026-06-12) — v0.6 종료. 릴리스 노트 `MediStack_v0.6_release_notes.md` + 핸드오프 `MediStack_v0.6_handoff.md` 작성, **`v0.6-beta` 태그**(alias 382 동결 스냅샷, lightweight). 코드/데이터/alias 무변경(문서 전용 커밋). 500(옵션 B·복합제 tier)·brand_core(옵션 C)는 v0.7 정책 결정 사항.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 후보 재수집·반영·코드 변경은 다음 PM 게이트.**
