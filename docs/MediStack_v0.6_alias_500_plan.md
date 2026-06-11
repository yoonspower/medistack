# MediStack v0.6 — alias 500 확장 계획 (계획 문서 · 실행 전)

작성일: **2026-06-11** / 상태: **계획만 — 수집·반영·코드 변경 미실행** / 상위: `MediStack_v0.5_release_notes.md`, `MediStack_v0.5_handoff.md` / 시작점: v0.5-beta(alias **206**, commit `9dae621`)

> 이 문서는 v0.5(alias 206)에서 **alias 500**으로 확장하기 위한 설계·근거·게이트 정의다. **이 단계에서는 nedrug 수집도, alias JSON 반영도, 코드/validator 수정도 하지 않는다.** 모든 수치는 현재 repo 데이터에서 실측한 ground truth이며, "심층 재수집 수율"만 추정(별도 recon dry-run으로 실측 예정)으로 명시한다. alias 는 **검색 보조**일 뿐 의학정보가 아니며, relation(약-영양소 의료 데이터)·DATA_URL·앱 UI 는 v0.6 에서도 **불변**이다.

---

## 1. 목표 / 범위

- **목표**: 검색 보조 alias **206 → 500**(제품/성분 표면형 확장, 검색 적중률 향상).
- **불변 원칙(= v0.5 그대로)**: relation **30 동결** · DATA_URL `./data/medistack_v0.2_beta_export.json` 동결 · data export 동결 · 앱/UI 동결 · alias 로 relation 신규 생성·풀 확장 금지.
- **핵심 제약**: alias 확장 대상은 **relation 약물 성분에 한정**한다. v0.6 은 의료 데이터를 넓히지 않으므로 **신규 성분 트랙이 없다**(아래 §2-A). 즉 500 은 *기존 성분의 제품/표면형을 더 모으는* 것으로만 달성한다.

## 2. 현재 공급 원장 (ground truth, 2026-06-11 실측)

### 2-A. alias 확장 우주 = 13성분 (신규 성분 없음)
relation 30건의 distinct 약물 성분은 **14종**. 그 중 **13종은 이미 alias 커버**, 유일한 미커버는 **에스오메프라졸 — 영구 alias 금지 대상**(id16 ×Mg 는 정상 live relation 이나 id15 ×B12 excluded 와의 혼동 방지로 alias 보류). 따라서:

> **v0.6 의 alias 확장 우주 = 아래 13성분뿐이다. 새 성분을 alias 하려면 새 relation 이 필요한데 relation 은 30 동결이므로, 신규 성분 트랙은 존재하지 않는다.** 에스오메프라졸은 v0.6 에서도 alias 대상이 아니다.

| 성분 | relation 수 | 현재 product alias | 현재 verified |
|---|---|---|---|
| 레보플록사신 | 3 | 26 | 25 |
| 오플록사신 | 3 | 26 | 24 |
| 시프로플록사신 | 3 | 24 | 22 |
| 독시사이클린 | 3 | 10 | 9 |
| 미노사이클린 | 3 | 4 | 2 |
| 레보티록신 | 2 | 18 | 16 |
| 알렌드론산 | 1 | 18 | 16 |
| 오메프라졸 | 2 | 11 | 9 |
| 목시플록사신 | 2 | 7 | 5 |
| 토라세미드 | 2 | 7 | 5 |
| 푸로세미드 | 2 | 3 | 1 |
| 히드로클로로티아지드 | 2 | 2 | 0(prod-only) |
| 메트포르민 | 1 | 12 | 10 |
| ~~에스오메프라졸~~ | 1 | **금지** | — |

(현재 product alias 합계 168 = 위 13성분 + 잔여. ingredient_alias 38 은 동의어/표기 변형.)

### 2-B. 즉시 가용 예비 (네트워크 0)
v0.5 Phase 11 재수집(v0.5-006)에서 남은 확정 후보 + 미반영 deferred.

| 트랙 | 건수 | 성분 분포 | 상태 |
|---|---|---|---|
| **held** (확정완료 pending, batch6 즉시 가능) | **55** | 시프로20·레보17·오플8·알렌6·독시1·미노1·토라1·푸로1 | detail_confirmed=true, alias 미반영 |
| unconfirmed pending | 3 | 레보2·독시1 | getItemDetail 확정 필요 |
| **brand_core deferred** | **14** | 목시3·미노3·토라3·알렌2·메트1·시프로1·오플1 | tier 규칙+검증 필요(§4-2) |
| **combo deferred** | **105** | HCTZ45·메트35·알렌23·오메2 | 정책결정 필요(§4-3, 현재 금지) |

- 즉시 가용(combo 제외) = held 55 + unconfirmed 3 + brand_core 14 = **72** → 반영 시 206 → **278**.
- (참고: v0.5 handoff 의 "held 51" 은 batch5 직후 추정치였고, 현 실측 확정-pending 은 **55**. 본 문서 수치를 기준으로 한다.)

## 3. 500 도달 경로 (supply math)

| 단계 | 출처 | 증가 | 누계 | 네트워크 |
|---|---|---|---|---|
| 시작 | v0.5-beta | — | **206** | — |
| ① held 반영 | 확정 pending 55 | +55 | 261 | 0 |
| ② unconfirmed 확정 | pending 3 | +3 | 264 | 소량 |
| ③ brand_core tier | deferred 14 (§4-2 규칙 통과분) | +최대14 | ~278 | 검증 1회 |
| ④ 단일성분 심층 재수집 | 13성분 long tail(§4-1) | **+~222 필요** | **→500** | **주 엔진** |
| (게이트) combo tier | deferred 105 (§4-3, 정책 변경 시) | 예비 | — | — |

**판단**: ①②③ 으로 약 **278** 까지는 기존 예비로 도달(추가 수집 거의 없음). **나머지 222 는 단일성분 심층 재수집(④)이 사실상 유일한 안전 엔진**이다. combo(105)는 가장 큰 예비지만 안전 정책상 게이트(§4-3).

### 3-1. 심층 재수집 수율 추정 (⚠️ recon dry-run 으로 실측 필요)
한국 제네릭 시장 깊이 기준 성분별 잔여 단일성분 완제 추정(현 커버리지·시장 관찰 기반, **미검증 추정**):

| 깊이 | 성분 | 성분당 추가 추정 |
|---|---|---|
| 高 | 레보플록사신·시프로플록사신·오플록사신·메트포르민·오메프라졸·레보티록신·알렌드론산 (7종) | +20~40 |
| 中 | 목시플록사신·독시사이클린·토라세미드 (3종) | +10~20 |
| 低 | 미노사이클린·푸로세미드·히드로클로로티아지드(단일) (3종) | +5~15 |

- 보수 추정 합계 ≈ **+200~285**(단일성분·완제·경구·getItemDetail 확정 통과분만). → 222 충당 **가능권**.
- 단, HCTZ 는 단일 완제가 드물고 대부분 복합제(combo 45) → 단일 트랙 기여 낮음.
- **실측 절차**: v0.6 첫 단계에서 `collect_nedrug_alias_candidates.py --max-pages 20~30 --max-per-ingredient 40~60` **dry-run**(alias 무반영)으로 13성분 잔여 단일성분 실수를 측정 → 본 추정 보정 → 500 도달 가능성 확정.

### 3-2. 현실 시나리오 2종
- **시나리오 A (combo 미사용, 권고)**: held+brand_core+심층재수집으로 충당. 단일성분 수율이 추정 하단(~200)이면 **현실 천장 ≈ 460~480**, 500 미달 시 v0.6 을 그 수치로 마감하거나 ingredient_alias 동의어(§4-5)로 보강.
- **시나리오 B (combo tier 가동, 정책 변경 필요)**: §4-3 combo 규칙 + PM 정책 승인 시 105 예비로 500 초과 여유 확보. 단 안전 프로파일 변경(아래 리스크 §7).

## 4. tier 설계

### 4-1. 단일성분 심층 재수집 (주 엔진, 안전도 高)
- v0.5 파이프라인 그대로, **페이지 깊이만 확대**: `--max-pages 20~30`(현 8~10), `--max-per-ingredient 40~60`.
- collect dedup 4중(surface∉alias · ∉queue · itemSeq∉alias · item_name∉alias)으로 **순수 net-new** 만 적재.
- 품질 게이트(불변): 점안/주사/원료/복합제 코드 필터 → **단일성분·완제·경구**만. getItemDetail 의 `ingrName` distinct=1 확정. confidence high.
- 표면형 정제: nedrug 품목명 개행 포함분은 표면형 정규화(개행 제거) 후 적재(미정규화분은 보류).

### 4-2. brand_core tier (deferred 14, 안전도 中 — 규칙 신설 필요)
brand_core = 검증된 단일성분 제품명에서 용량/제형을 제거한 **브랜드 어간**(예: `바이포민서방정500mg` → `바이포민서방정`). 위험은 "한 브랜드 어간이 서로 다른 성분에 재사용"되는 경우.

**제안 규칙(brand_core 승인 조건, 전부 충족 시만)**:
1. 그 brand_core 출처가 **검증된 단일성분 제품**일 것.
2. nedrug searchDrug 에서 그 brand_core 로 검색한 **모든 히트가 동일 단일성분**일 것(다른 성분·복합제 히트 0 — 브랜드 고유성 검증).
3. 기존 alias 와 **다른 canonical 로의 충돌 표면형 없음**.
4. brand_core 가 일반어·부분문자열 오매칭 위험 없음(짧은 일반명사 제외).
- → **brand_core 전용 sub-validator** 1개 추가(검증 2번 자동화). 14건 중 통과분만 승인.
- 14건 성분: 목시3·미노3·토라3·알렌2·메트1·시프로1·오플1 — 전부 기존 verified canonical → 반영은 append.

### 4-3. 복합제 combo tier (deferred 105, 안전도 低 — 정책결정 게이트)
combo = 카논 성분을 **여러 성분 중 하나로** 포함하는 제품(예: `가드메트정`=아나글립틴+메트포르민 → 메트포르민). 분포: HCTZ45·메트35·알렌23·오메2.

**쟁점**:
- (찬성) combo 도 카논 성분을 **실제로 함유** → 검색어 매핑은 사실. 검색 보조로서 "가드메트 → 메트포르민" 은 유용.
- (반대·현 불변규칙) **"복합제는 단일성분 매핑 부적합으로 보류"** 가 현재 hard rule. combo 의 상호작용은 카논 성분분만 표시되어 **불완전**할 수 있고, 복합제에 *다른* relation 약물이 동시에 들어가면 매핑이 모호(예: 한 정제에 relation 약물 2종).

**제안 규칙(만약 PM 가 combo 게이트를 여는 경우에만)**:
1. combo 가 **relation 약물을 정확히 1종만** 포함(2종↑ → 모호 → 제외).
2. 그 1종이 검증된 canonical 이고, combo 전체가 getItemDetail 로 성분 확정.
3. 표면형은 제품 전체명(부분 브랜드 금지).
4. (UX 무변경 전제) alias 는 검색 보조이므로 결과는 카논 성분 relation 으로 안내 — combo 별도 라벨/면책 UI 는 **추가하지 않음**(앱 UI 동결 유지). 따라서 "combo 를 alias 해도 사용자는 단일성분 relation 만 본다"는 한계를 PM 가 수용해야 함.

> **권고: v0.6 은 시나리오 A(combo 미사용)를 기본으로 한다.** combo tier 는 위 규칙을 *문서로만* 준비해두고, 단일성분 수율이 500 에 미달할 때 **별도 PM 정책 승인**(현 "combo 금지" 불변규칙 완화)을 받아 소규모 파일럿으로만 가동한다. 자동 편입 금지.

### 4-4. held → batch6 (즉시, 안전도 高)
- `confirm --no-network --ar-only-batch v0.5-006 --ar-balanced --ar-batch-id v0.6-batch-6 --ar-limit 30` → batch6 approved-ready 30 생성 → PM 승인 → ephemeral incorporate → 206→236. 네트워크 0. (나머지 held 25 → batch7.)

### 4-5. ingredient_alias 동의어 보강 (보조, 안전도 高)
- 13성분의 **표기 변형·염 형태·영문·일반 오타**(예: ciprofloxacin/시프로/싸이프로) 추가. 현 38 → 소폭 증가. 검색 적중률 보강용, 제품 alias 와 독립.

## 5. 파이프라인 & validator 확장 (v0.5 구조 재사용)

- **batch 단위**: v0.5 와 동일 6단계(collect dry-run → confirm 확정 → approved-ready 생성[incorporated=false] → PM 명시 승인 → ephemeral `/tmp/ms_incorporate_v0_6_batchN.py`[전제/사후 assert, 미커밋] → validator option-A).
- **batch cadence**: 30~40/batch 권장(리뷰·smoke 관리 가능 범위). 206→500 = +294 → batch6~ 약 **8~10 batch**(40/batch 면 ~7).
- **validator base_no 확장**: batch6=120, batch7=140, … (v0.5 의 20/40/60/80/100 패턴 연장). 각 batch 블록 = base+0..9, +11, +12(12 checks) + 3(≤cap·incorporated·field). DEF_AR6/7/… 경로 추가. 반영 시 #(base+2) option-A.
- **bulk validator 총계**: batch 당 +~15. (현 92/92 → v0.6 종료 시 ~200+/200+.)
- **#16 alias_count 단조 증가** → 500 까지 monotone 유지.
- **smoke**: batch 별 신규 N/N(각 alias→해당 canonical 1종·filterRelations 결과가 그 canonical relation 전부) + 회귀(타리비드3·포사맥스1·토렘2·넥시움0·#r15 fail-safe). `/tmp/*.mjs` 복사로 guards.js import(package.json 없음).
- **성능**: 500 alias 의 prefix 스캔은 무시할 수준(선형 500). 인덱스 분리(option D)는 **v0.6 불필요** — 단일 파일은 ~1-2k 까지 충분. D 는 1만+ 장기 트랙으로 분리 유지.
- **brand_core sub-validator**(§4-2 신설) 1개. combo 가동 시 combo sub-validator(§4-3) 추가.

## 6. 안전선 (v0.6 전 과정 불변)

- **에스오메프라졸 alias 금지** — 유일 미커버 relation 약물이나 v0.6 대상 아님(id15 excluded 혼동 방지). **15행(id15) 재편입 금지.**
- relation **30 동결** · DATA_URL 동결 · data export 동결 · 앱/UI 동결 · alias 로 relation 신규 생성 금지.
- **복합제 combo: 기본 금지 유지**(§4-3 게이트는 별도 PM 정책 승인 시에만). **brand_core: §4-2 규칙·sub-validator 통과분만**(무검증 편입 금지).
- 모든 itemSeq = nedrug getItemDetail 원문 확정. 미검증·동일 itemSeq 중복 alias 금지.
- published/clinical_reviewed 봉인(천장 verified_reference) · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- alias 반영은 **PM 명시 승인 batch 단위**로만 · 수동 deploy 금지 · 무단 tag 금지.

## 7. 리스크 & 미해결 결정 (PM 게이트)

1. **500 도달 가능성**: 단일성분 심층 수율이 추정 하단이면 combo 없이 ~460~480 천장 가능. → **결정 D1**: combo 게이트를 열 것인가, 아니면 현실 천장에서 v0.6 마감할 것인가. (recon dry-run 후 재평가 권장.)
2. **combo 정책**: 현 "combo 금지" 불변규칙 완화는 안전 프로파일 변경. combo alias 는 단일성분 relation 만 노출(불완전성). → **결정 D2**: 수용/거부.
3. **brand_core 규칙 채택**: §4-2 4조건 + sub-validator 승인 여부. → **결정 D3**.
4. **batch 크기**: 30(보수) vs 40~50(속도). → **결정 D4**.
5. **표면형 개행 후보**: 정규화 후 적재 vs 계속 보류. → **결정 D5**.

## 8. 단계 로드맵 (추정, PM 승인 게이트마다 정지)

| 단계 | 내용 | alias | 네트워크 |
|---|---|---|---|
| v0.6-0 | **recon dry-run**: 13성분 `--max-pages 25` 잔여 단일성분 실측 → §3-1 보정 → 500 가능성 확정 보고 | 206 | 측정만 |
| v0.6-1 | batch6 (held 30 반영) | 206→236 | 0 |
| v0.6-2 | batch7 (held 잔여 25 + brand_core tier 통과분) | 236→~280 | 검증 |
| v0.6-3~ | 심층 재수집 batch (40/batch) 반복, validator base_no 120/140/… | →~480 | 주 엔진 |
| v0.6-N | (조건부) combo tier 파일럿 또는 ingredient_alias 보강으로 500 마감 | →500 | 게이트 |
| 마감 | release_notes·handoff 갱신, v0.6-beta 태그(PM 지시 시) | 500 | 0 |

## 9. v0.6 에서 하지 않는 것 (범위 밖)

- relation 확장 · DATA_URL/data export 변경 · 앱 UI 변경.
- 에스오메프라졸/15행 alias · 미검증 itemSeq · combo 자동 편입.
- published/clinical 전환 · clinical claim · 제품 추천/구매/제휴 UI.
- 품목명 1만+ 인덱스 분리(option D, 별도 장기 트랙).

## 10. 즉시 다음 액션 (PM 선택)

- **(권장) v0.6-0 recon dry-run 승인** → 13성분 잔여 단일성분 실측으로 500 도달 가능성·combo 필요 여부를 데이터로 확정한 뒤 batch6 착수.
- 또는 **batch6 즉시 착수**(held 30 반영, 206→236) — recon 없이 안전 예비부터 소진.
- 또는 본 계획의 **결정 D1~D5 사전 확정** 후 일괄 진행.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 문서는 계획만 — 수집·반영·코드 변경은 다음 PM 게이트.**
