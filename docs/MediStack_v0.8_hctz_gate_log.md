# MediStack v0.8 — HCTZ 복합제 개방 구현 게이트 로그 (H-G1~H-G4)

> 정책: `MediStack_v0.8_hctz_safety_review.md` · 설계: `MediStack_v0.8_hctz_combo_design.md`
> PM 자동진행 모드(2026-06-12): H-G1~H-G3 정상조건 자동 진행, **H-G4 실제 alias 반영은 별도 PM 승인 후**.
> 불변: alias JSON·queue·relation·DATA_URL·data export 무변경. 칼륨보존이뇨제 파트너 영구차단. 에스오메프라졸/15행 차단.

---

## H-G1 — combo validator 가드 (alias 무변경) ✅

**변경 파일(코드/테스트/픽스처만, data/src 무변경):**
- `scripts/validate_combo_approved_ready.py` (combo AR validator)
  - #6 basis allowlist 에 **히드로클로로티아지드 추가**(에스오메프라졸 계속 차단).
  - **신규 #12**: 칼륨보존이뇨제 파트너 하드차단(`KSPARING_RE` = 트리암테렌/아밀로라이드/스피로노락톤/에플레레논/칸레논, 영문 포함). `ingr_name` 성분 토큰 매칭. **염이름 '칼륨'(로사르탄칼륨·피마사르탄칼륨)은 토큰에 없어 미매칭(V5 분리).**
  - **신규 #13**: canonical=HCTZ 면 칼륨 반전 고지 파생조건 정합(is_combination·basis=HCTZ·notice=true) — render 트리거 보장.
- `scripts/validate_medistack_v0_3_aliases.py` (라이브 alias validator)
  - #15 basis allowlist 에 **히드로클로로티아지드 추가**.
  - **신규 #16**: 라이브 복합제 alias 표시 문자열에 칼륨보존이뇨제 토큰 금지(라이브엔 `ingr_name` 부재 → alias 문자열 방어). 염이름 칼륨 미매칭.
- 픽스처: combo AR(`v0_7_combo_ar/`) — 신규 `allow_hctz_arb`·`allow_hctz_arb_ccb`·`reject_C6_basis_blocked`·`reject_C12_kspare`·`reject_C13_hctz_notice`, 폐기 `reject_C6_hctz`. aliases(`v0_7_combo/`) — 신규 `allow_hctz_combo`·`reject_C15_basis_blocked`·`reject_C16_kspare`, 폐기 `reject_C1_hctz_combo`.
- 테스트: `test_validate_combo_ar.py`(9→13 케이스), `test_validate_v0_3_combo.py`(7→9 케이스).

**검증 결과:**
| 검사 | 결과 |
|---|---|
| combo AR 테스트 | PASS 13/13 (HCTZ+ARB·3성분 PASS, K보존#12·반전고지#13 reject 단언) |
| v0_3 combo 가드 테스트 | PASS 9/9 (HCTZ PASS, 토라세미드#15·K보존#16 reject 단언) |
| v0.1 export | PASS 12/12 |
| v0.2 export | PASS 15/15 |
| v0.3 aliases (live) | PASS **16/16** (기존 15 + #16, 회귀 0) |
| bulk | PASS 152/152 |
| TypeB 단위 | PASS 7/7 (회귀 0) |
| combo AR (live v0.7) | PASS **13/13** (기존 11 + #12/#13, 회귀 0) |

**불변(무변경) 확인:** alias_count 506 · product_aliases 468 · verified_item_seqs 430/12 · relations 30 · DATA_URL `./data/medistack_v0.2_beta_export.json`. data/ src/ 추적파일 diff 0.

**회귀:** 기존 combo 110·brand_core 14 라이브 — 새 검사(#12/#13/#16)는 HCTZ-canonical/K보존 토큰이 없어 모두 inert → PASS 유지(회귀 0).

---

## H-G2 — HCTZ 칼륨 반전 고지 render (src 최소 수정·app.js 무변경) ✅

**설계 결정:** 상세뷰(`renderDetail`)는 alias 맥락이 없어 단일 HCTZ 와 복합제를 구분 못 함(단일 HCTZ 에 반전 고지를 띄우면 오고지). 복합제 맥락(`comboBases`)을 가진 **`renderAliasHint`(목록/검색뷰)** 가 정확한 위치 → app.js 라우팅 변경 불요.

**변경 파일(src 3개·app.js 무변경):**
- `src/js/guards.js` — `aliasHint()` 에 `hctzPotassiumNotice` 플래그 추가. 조건: `comboBases` 에 히드로클로로티아지드 포함 **AND** 결과에 HCTZ 의 `potassium_safety_card===true` 행 존재(= 칼륨 행). **nutrient 문자열 매칭 금지 원칙 → 플래그로 판정.**
- `src/js/render.js` — `renderAliasHint()` 에 `info.hctzPotassiumNotice` 시 `.combonotice` 1줄(설계 §2-2 문구: "…ARB 계열 등은 칼륨을 반대 방향(보존)으로… 임의보충 위험·상담"). 기존 combo 배너 유지.
- `src/css/styles.css` — `.combonotice`/`.kbadge`(기존 clay 팔레트 재사용).

**트리거(데이터 파생, append-only 플래그 무):** `is_combination` + `combination_basis_ingredient=히드로클로로티아지드` (기존 스키마) → `comboBases` 도출 → 칼륨 행 동반 시에만 표시.

**smoke 결과(`scripts/smoke_hctz_disclosure.py`, ES module /tmp 복사 + node):**
| 시나리오 | 결과 |
|---|---|
| A 라이브 메트 복합제 → combobox O·반전고지 X(inert) | PASS 3/3 |
| B 합성 HCTZ+ARB → combobox O·반전고지 O('반대 방향') | PASS 3/3 |
| C HCTZ 복합제+마그네슘 필터 → 반전고지 X(칼륨 행 없음) | PASS 2/2 |
| D 단일 HCTZ(비복합제) → 배지·반전고지 X | PASS 2/2 |
| **합계** | **SMOKE PASS 10/10** |

**라이브 화면 회귀:** HCTZ 복합제 0건 → `hctzPotassiumNotice` 항상 미설정 → `renderAliasHint` 출력 라이브 동일(신규 코드 경로 휴면). `.combonotice` CSS 는 라이브에서 매칭 엘리먼트 0 → 시각 동일. data/validator 무변경.

---

## H-G3 — HCTZ combo confirm + approved-ready (큐/alias 무변경·incorporated=false) ✅

**변경 파일:**
- `scripts/confirm_nedrug_item_details.py` — `COMBO_ALLOWED_BASIS` 에 히드로클로로티아지드 추가 + `classify_combo` 에 **칼륨보존이뇨제 파트너 필터**(`KSPARING_RE`, distinct 성분 등장 시 `potassium_sparing_partner` 로 제외). AR meta version/note 를 v0.8·K보존 제외로 갱신.
- 신규 산출물(approved-ready 후보 풀, **alias 아님·incorporated=false**): `data/candidates/bulk_alias_approved_ready_combo_v0_8_hctz.json` · `.csv`.

**실행:** `confirm --combo --combo-ar-json …combo_v0_8_hctz.json --ar-batch-id v0.8-hctz-1 --ar-version v0.8 --checked-at 2026-06-12` (getItemDetail 실네트워크 112건).

**결과:**
| 항목 | 값 |
|---|---|
| 대상 deferred combo | 112 (전량 HCTZ·메트/알렌/오메는 v0.7 반영완료라 비대상) |
| getItemDetail 결과 | **combo_confirmed 112/112** (fetch/parse 실패 0·basis_mismatch 0·multi_relation 0) |
| **potassium-sparing partner** | **0** (KSPARING_RE 매칭 0 — 진짜 역전 위험군 없음 재확인) |
| 염이름 칼륨 오인 | 0 (로사르탄칼륨·피마사르탄칼륨 → relation 성분 매칭은 HCTZ 정확히 1개, 칼륨 미오인) |
| 구조 | 2성분 ARB+HCTZ **98** · 3성분 ARB+CCB+HCTZ **14** = 112 |
| AR 항목 | 112 · incorporated 전부 false · is_combination true · basis=HCTZ · notice=true · itemSeq 112/112 고유 |
| meta | version v0.8 · incorporated false |

**검증(전체 회귀):** v0.1 12/12 · v0.2 15/15 · v0.3 **16/16** · bulk 152/152 · typeB 7/7 · combo 가드 9/9 · combo AR 테스트 13/13 · **AR(v0.8 HCTZ) 13/13** · AR(v0.7) 13/13 · smoke 10/10 — ALL PASS.

**STOP 가드(전부 충족):** queue 추적파일 diff 0(**flip 없음** — 여전히 deferred 112) · alias JSON diff 0 · **alias_count 506 유지** · relation 30 · DATA_URL 불변 · incorporated=true 0건. 신규 파일은 combo AR(json/csv)뿐.

---

## H-G4 — HCTZ 복합제 112건 alias 반영 (PM 명시 승인 2026-06-12) ✅

**승인:** PM "v0.8 H-G4 반영 승인…전제/사후 assert 통과 시에만 커밋·deploy."

**반영 방식:** ephemeral `/tmp/ms_incorporate_hctz.py`(전제/사후 assert 내장·**미커밋**) — v0.7 G4 패턴 승계(생성↔반영 분리).

**5개 변경(전제 assert 통과 후 적용):**
1. product_aliases +112 (alias=getItemDetail 품목명·canonical=HCTZ·is_combination·basis=HCTZ·notice·source_relation_ids=[19,20] = HCTZ 칼륨/마그네슘).
2. verified_item_seqs["히드로클로로티아지드"] 신규 +112 (430→542·12→13).
3. meta.alias_count 506→618.
4. queue flip 112 deferred→approved(reviewer=v0.8-hctz-g4·incorporated_at·**detail_confirmed 미설정**=bulk#19 회피) — JSON+CSV 동기(CSV 112행만).
5. combo AR incorporated=true ×112 + meta.incorporated=true(옵션 A #11 실반영 검증 대상화).

**델타(전제→사후 assert 둘 다 통과):**
| 항목 | 전 | 후 |
|---|---|---|
| alias_count | 506 | **618** |
| product_aliases | 468 | **580** |
| verified_item_seqs | 430/12 | **542/13** (HCTZ 112 신규) |
| queue | deferred 112 | **approved 552**(deferred 0) |
| ingredient_aliases · relation · DATA_URL | 38 · 30 · 불변 | **38 · 30 · 불변** |

**검증(반영 후 전체):** v0.1 12/12 · v0.2 15/15 · v0.3 **16/16** · bulk **152/152** · combo AR(v0.8 HCTZ) **13/13**(incorporated=true·#11 실반영) · typeB 7/7 · combo 가드 9/9 · combo AR 테스트 13/13 · smoke 10/10 — ALL PASS.

**diff 무결성:** alias JSON 은 `json.dump(indent=2·ensure_ascii=False)` 와 원본 byte-identical 확인 → 변경은 **순수 추가**(기존 468 product·430 verified·38 ingredient byte 동일·verified 기존키 동일). 큰 라인수는 반복 JSON git 정렬 artifact(데이터 동일성·validator 입증). CSV 112행만. 금지불변: 에스오메/15행 0·K보존 파트너 0·제품/구매 필드 0·relation/DATA_URL/export 불변.
