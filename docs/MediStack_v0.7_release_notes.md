# MediStack v0.7 — 복합제 tier + brand_core 릴리스 노트 (🎯 alias 500 달성)

작성일: **2026-06-12** / 상태: **v0.7 마감 — 복합제 tier B1 + brand_core 반영, alias 506 (목표 500 달성·초과)** / 라이브: https://yoonspower.github.io/medistack/

> v0.6 에서 **단일성분 트랙 천장 382** 에 도달해 500 미달로 마감했고(옵션 A), 500 잔여분은 복합제 tier(옵션 B) 로만 도달 가능함이 확인됐다. v0.7 은 **복합제 tier B1**(메트포르민/알렌드론산/오메프라졸 복합제·HCTZ 제외) 110 건과 **brand_core 어간** 14 건을 반영해 **alias 382 → 506 으로 500 목표를 달성**했다. relation(약-영양소 의료 데이터)·DATA_URL·data export 는 v0.7 에서도 **전부 불변**이며, alias 는 검색 보조일 뿐 의학정보가 아니다. 복합제는 **부분정보 고지**(표시 정보는 기준 성분 1개 기준·다른 성분 미포함)를 동반한다.

---

## 1. v0.7 목표 (계획)
- **alias_count 382 → 500**: 단일성분 트랙으로 도달 불가했던 잔여를 **복합제 tier 개방**으로 채움.
- **복합제 tier B1**: deferred 복합제 중 **relation 보유 성분이 정확히 1개**인 제품만 그 성분(canonical)을 기준으로 편입. **HCTZ 복합제는 제외**(칼륨 오도 위험). 대상 = 메트포르민/알렌드론산/오메프라졸 복합제.
- **brand_core 14**: 검증된 단일성분 제품의 짧은 브랜드 어간(검색 적중률 보강).
- **의료 데이터 비확장**: relation 30 유지, DATA_URL/export 불변, alias 로 relation 신규 생성 금지.

## 2. 최종 결과 (실측)
| 항목 | 값 |
|---|---|
| **meta.alias_count** | **506** 🎯 (목표 500 달성·초과) |
| product_aliases | **468** (복합제 110 + 단일성분 358) |
| ingredient_aliases | 38 |
| verified_item_seqs | **430** entries / 12 canonical 성분 |
| relations | **30 (불변)** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| data export md5 | `401b097a1bd812b6da983b7f3dfc6d20` (불변) |
| latest data commit | `113a79b` (Incorporate v0.7 G5 brand_core aliases (492->506)) |
| queue 총 | 561 (approved 440 · pending 7 · rejected 2 · deferred 112) |
| 라이브 | HTTP 200 |

- alias 증가 경로: **382 → 492 → 506** (G4 복합제 +110, G5 brand_core +14).
- **복합제 110**: 메트포르민 76 · 알렌드론산 28 · 오메프라졸 6. 전부 `is_combination=true` + `combination_basis_ingredient`(=canonical) + `combination_notice_required=true`.
- **brand_core 14**: 메트포르민 1 · 목시플록사신 3 · 미노사이클린 3 · 시프로플록사신 1 · 알렌드론산 2 · 오플록사신 1 · 토라세미드 3 (10 unique itemSeq, 단일성분 어간).

## 3. 🎯 500 달성 경로
- **382 (단일성분 천장, v0.6)** → 단일성분 제품 풀 소진으로 더 못 모음.
- **+110 복합제 (G4)** → 492. deferred 복합제 222 중 **relation 성분 정확히 1개**인 110 건만(메트/알렌/오메) 그 성분 기준으로 편입. 부분정보 고지 동반.
- **+14 brand_core (G5)** → **506**. 검증된 제품의 짧은 어간(`토렘정`·`바이포민서방정` 등). item_seq 가 **이미 #8 허용집합(relation-cited ∪ whitelist)** 에 있어 verified_item_seqs **미확장(430 유지)**.
- 결과: **506 = 단일성분 382 + 복합제 110 + brand_core 14.**

## 4. 완료 게이트 요약 (G1~G5)
| 게이트 | 내용 | alias | commit |
|---|---|---|---|
| 정책 | 복합제 tier 정책 검토(B1·HCTZ 제외 결정) | 382 | `bd4d47a` |
| 설계 | UX 고지 + combo/BC validator 설계 | 382 | `548aea5` |
| G1 | v0.3 validator combo 라이브 가드 #14/#15 (basis allowlist·HCTZ/에스오메 하드차단) + fixture/test | 382 | `752052e` |
| G2 | 앱 복합제 고지 렌더(배지+부분정보 배너) + append-only 3필드 스키마 (라이브 0 combo → inert·화면 byte-identical) | 382 | `f33c4c1` |
| G3 | confirm `--combo` 모드 → deferred 복합제 110 getItemDetail 확정(relation 정확히 1개) → combo AR + combo AR validator | 382 | `a3e8a6f` |
| G4 | **복합제 110 반영** (product+110·verified+110·큐 flip) | 382→**492** | `0962e44` |
| G5 | **brand_core 14 반영** (product+14·verified 불변·incorporation-aware bulk #10/#11/#30) | 492→**506** | `113a79b` |

- 패턴(v0.5/v0.6 계승): **생성 단계**=alias 무반영(approved-ready, incorporated=false), **반영 단계**=PM 명시 승인 후 ephemeral `/tmp/ms_incorporate_*.py`(전제/사후 assert·**미커밋**)로 원자적 수행. 생성↔반영 분리 안전 게이트 유지.

## 5. 복합제 tier B1 정책 (핵심 안전)
- **수용 기준**: 복합제 구성 성분 중 **relation 보유 성분이 정확히 1개** → 그 성분을 canonical(=`combination_basis_ingredient`)로 매핑. 0개·2개 이상은 거부(다중 매핑 충돌 방지).
- **HCTZ 복합제 제외**: 히드로클로로티아지드(이뇨제) 복합제는 **칼륨 오도 위험**(이뇨제 K 소실 vs ARB 파트너 K 보존 상충, `potassium_safety_card` 영역) → B1 스코프에서 하드 차단. B1 대상 3성분(메트=B12·알렌=칼슘·오메=B12/Mg)은 **칼륨 무관**.
- **부분정보 고지**: 복합제 검색 시 배지(`복합제`) + 배너("이 제품은 둘 이상의 성분을 가진 복합제입니다. 표시된 정보는 {기준 성분} 기준이며 함께 포함된 다른 성분 정보는 포함하지 않습니다. 전체 성분은 허가사항 확인."). brand_core 는 단일성분이라 **고지 불요**.
- **스키마**: append-only 3필드(`is_combination`·`combination_basis_ingredient`·`combination_notice_required`). 단일성분 alias 와 하위호환(필드 부재 시 기존 동작).

## 6. incorporation-aware validator 진화 (G4/G5)
- **G4**: combo approved-ready validator `validate_combo_approved_ready.py` 옵션 A(`#10` incorporated ∈ {false,true} · `#11` incorporated=true → alias 실제 반영 검증). combo 큐는 `product_full_name` 타입이라 bulk #10/#11 미저촉, 단 **detail_confirmed 미설정**으로 bulk #19(단일주성분 가정·`/` 충돌) 회피.
- **G5**: brand_core 는 `candidate_type=brand_core` 라 bulk **#10/#11**(brand_core approved 하드차단, PM v0.5 #6)·**#30**(approved itemSeq ∈ whitelist)과 정면 충돌 → **incorporation-aware 완화(PM 판정 A)**:
  - `#10`/`#11`: brand_core approved 는 **incorporated=true 이고 live alias 에 동일 canonical 로 실제 반영된 경우에만** 허용. **미반영 brand_core approved 는 계속 하드차단**(`_bc_incorporated` 가드).
  - `#30`: **brand_core 에 한해** itemSeq ∈ whitelist **∪ relation-cited** 허용(검증된 제품의 relation 인용 itemSeq 재사용 = verified 미확장 수용). 그 외 타입은 whitelist 엄격 유지.
- 명명 안전규칙("brand_core approved 금지")은 **alias 실반영 가드**로 보존됨(자동 편입은 여전히 차단).

## 7. 검증 결과 (최종, G5 반영 후)
| validator | 결과 |
|---|---|
| bulk candidate validator | **152/152 PASS** |
| v0.1 export validator | **12/12 PASS** |
| v0.2 export validator | **15/15 PASS** |
| v0.3 alias validator | **15/15 PASS** (combo 가드 #14/#15 포함) |
| combo approved-ready validator | **11/11 PASS** |
| Type B suite | **7/7 PASS** |
| combo guard suite (`test_validate_v0_3_combo`) | **7/7 PASS** |
| combo AR suite (`test_validate_combo_ar`) | **9/9 PASS** |
| combo 고지 smoke (G4) | **10/10 라이브 PASS** |
| brand_core smoke (G5) | **10/10 라이브 PASS** |

**회귀 / 무손실**:
- 단일성분 회귀: 타리비드 → 오플록사신 · 포사맥스 → 알렌드론산 · 토렘 → 토라세미드 유지 · 넥시움 → 0건(에스오메프라졸 제외) · `#/r/15` fail-safe 유지.
- 복합제 고지: 가드메트정 → 메트포르민 복합제 배지/배너 정상. brand_core(토렘정·바이포민서방정·제일타리비드) → 단일 연결·**복합제 고지 없음**.
- 무손실: non-combo 344 ⊆ 358 · combo 110 불변 · 과매칭 0 · dup 0 · ingredient 38 · canonical 12.

## 8. 안전선 (v0.7 전 과정 불변)
- **relation 30 불변** · **DATA_URL 불변** · **data export 불변**(md5 `401b097a…`) · **앱 UI(`src/`) 불변**(G2 이후 추가 변경 0).
- **HCTZ 복합제 제외** · **에스오메프라졸 alias 금지**(id16 ×Mg 정상 live·id15 ×B12 excluded 혼동 방지) · **15행(id15) excluded 유지**(렌더·재편입 금지).
- **복합제는 부분정보 고지 동반** · 복합제/brand_core 는 **PM 명시 승인 + 검증된 itemSeq + incorporation-aware 게이트** 통과분만 편입(자동 편입 금지).
- **제품/구매/제휴 UI 없음** · **칼륨 제품 링크 금지** · **published/clinical_reviewed 봉인**(천장 verified_reference) 유지.
- alias 는 **검색 보조**이며 **의학정보 아님** · alias 로 relation 신규 생성·풀 확장 금지.

## 9. 잔여 / 다음 단계
- **deferred 복합제 112 (전량 HCTZ)**: 칼륨 상충 위험으로 B1 에서 의도적 제외. 추가 개방은 별도 안전 검토(potassium 고지 강화) 선행 필요.
- **표면형 개행 제외 후보**: nedrug 품목명 개행 포함분(검색 표면형 정제 필요).
- **추가 relation 확장**: clinical reviewer 트랙(별도 버전·published 봉인 유지).
- **파이프라인 자산 보존**: collect/confirm(`--combo`)/validate 스크립트 · combo AR · brand_core 큐 · incorporation-aware validator(bulk #10/#11/#30, combo AR 옵션 A) 전부 repo 유지.
- **tag**: 본 마감은 **문서 전용**이며 `v0.7-beta` **태그는 아직 생성하지 않음**(PM 별도 지시 대기).

## 10. v0.7 에서 하지 않은 것 (범위 밖·의도적 제외)
- HCTZ 복합제 편입 · 에스오메프라졸 / 15행 편입 · relation 확장(의료 상호작용 데이터 추가).
- DATA_URL 변경 · data export 변경 · 앱 UI 추가 변경(G2 이후).
- published / clinical_reviewed 전환 · clinical claim 추가.
- 제품 추천 / 구매 / 제휴 UI · 복합제의 **모든** 구성 성분 노출(부분정보 고지로 한정).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / HCTZ 복합제·미검증·동일 itemSeq 중복 alias 금지 / 복합제는 부분정보 고지 동반.
