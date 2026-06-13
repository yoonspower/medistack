# MediStack — 다음 세션 실행 프롬프트 모음

> 작성일: 2026-06-14(작업11 보강). **프롬프트 모음 전용 — 코드/데이터 무변경.** 각 프롬프트(A~G)는 **자기완결**이다: 새 AI 세션이 이 문서의 해당 프롬프트 하나만 읽고도 정책 가드레일·성공기준·STOP 조건을 알고 안전하게 실행할 수 있도록, 매 프롬프트마다 목표·입력/선행자료·허용 범위·금지·성공기준·STOP·산출물을 **반복** 기재한다.
>
> 사용법: 다음 세션 시작 시, PM이 아래 A~G 중 하나를 골라 그 블록을 그대로(또는 거의 그대로) 새 세션 프롬프트로 붙여넣는다. 각 프롬프트는 시작 시 `CLAUDE.md` + `docs/MediStack_v1.1_handoff.md` + `docs/MediStack_v1.2_plan.md` + 해당 선행자료를 먼저 읽도록 지시한다.
>
> **프롬프트 색인:** A=source_confirmed 후보 relation 승격 · B=내 약 목록 저장 MVP 구현 · C=Free/Plus 기능 플래그 설계 · D=relation source 표시 UI 구현 · E=name_only UX 개선 구현 · F=별도 영양제 앱 기획(분리 우선) · G=v1.2-beta release readiness.
>
> ⚠️ **v1.2 라운드 산출물 참조 규칙**: 아래 A~F 가 가리키는 `docs/MediStack_*_v1_2.md` / `data/relation_expansion_draft_v1_2.json` 등은 **이번(2026-06-14) 라운드에서 병렬로 작성 중인 설계/기획 문서**다. 각 프롬프트는 "**해당 라운드 산출물이 있으면 입력으로 사용**, 없으면 v1.1 선행자료(설계 근거) 로 폴백"한다. 경로는 정확히 명시하되, 존재를 단정하지 말고 실행 시점에 확인한다.

---

## 0. 전(全) 프롬프트 공통 가드레일 (각 프롬프트가 자체 재기술하지만, 한 번 더 박제)

이 가드레일은 MediStack 정체성에서 나오며 **어떤 작업에서도 불변**이다:

- ❌ **제품/구매/제휴/영양제 추천 동선 금지** — 링크·버튼·제품 예시·제품 필드·영양제 보충 권유 표현 0.
- ❌ **복용 지시 / 진단 / 처방 / 치료 / 위험 확정 / "드세요·보충하세요·중단하세요" 금지.**
- ❌ **"식약처 승인" / "법적 문제없음 확정" / "약사 검수 완료" 표현 금지.**
- ❌ **신규 relation 구현 금지** (relation 41 불변). 출처는 **허가사항 우선 gate**(문헌만으로는 미채택).
- ❌ **published / clinical_reviewed 전환 금지** — 천장 = `verified_reference`. 봉인 유지.
- ❌ **v0.1 데이터 직접 수정 금지** · **DATA_URL(v0.2) 변경 금지** · **무단 deploy / 무단 tag 금지.**
- ✅ relation 없는 약은 **name_only** 로만 표시. name_only 에 의학정보 부착 금지.
- ✅ 칼륨 정책 유지(`product_link_allowed=false` + `potassium_safety_card=true`).
- ✅ 복합제는 **부분정보 고지 동반**(HCTZ 는 칼륨 반전 고지) · 칼슘 완충 복합제는 other_label 을 **"칼슘"이 아니라 완충 기능명**으로.
- ✅ **데이터 변경 시 CI 전체 세트(validator + smoke)를 로컬에서 선실행** 후에만 진행(surface-forms / v0.1 / potassium selftest 포함).

### 현재 라이브 기준선(2026-06-14, 작업11 시점 · 모든 프롬프트의 회귀 기준)

| 항목 | 값 |
|---|---|
| relations (export) | **41** (불변) |
| relation_card | **1,072** |
| name_only | **16,508** |
| full index total | **17,580** |
| product_aliases | **679** |
| alias_count (meta) | **717** |
| verified_item_seqs | **1,059 / 20** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (v0.2, 불변) |
| published / clinical_reviewed | **false / false** (봉인) |

> 이 숫자는 작업11 직전 세션에서 C(PPI+침강탄산칼슘 18건)를 buffer_combo 트랙으로 flip 한 결과다(`scripts/integrate_combo_banner_c_v1_1.py`). 보호 데이터를 건드리지 않는 프롬프트(B·C·D·E·F·G)는 이 숫자가 **그대로 유지**되어야 한다. 데이터-only 프롬프트(**A 승격 · H buffer_combo**)만 **PM 명시 승인 batch** 에서 이 숫자를 바꿀 수 있고, 그 경우 갱신된 기대값으로 회귀를 **재확인**한다(published/clinical false·DATA_URL v0.2·full index total 17,580 은 어느 경우에도 불변).

---

## A. source_confirmed 후보 → 실제 relation 승격 (데이터-only) 프롬프트

> **목표:** 출처 확인 라운드에서 **`source_confirmed` 로 분류된 relation 확장 후보만**, 기존 A티어 통합기 패턴을 승계한 **데이터-only 배치**로 실제 relation 으로 승격한다. **신규 relation 은 오직 (PM 승인 ∧ source_confirmed=허가사항) 게이트를 통과한 후보만.** 출처 미확인·문헌-only·needs_review·missing 후보는 **승격 금지(do_not_implement_yet)**.

**입력 / 선행자료 (먼저 읽기):**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표1·목표2)
- **(이번 라운드 산출물이 있으면 입력으로 사용)** Top10 출처 확인 산출물 — `docs/MediStack_source_queue_top10_verification_v1_2.md`(있으면) 또는 `data/source_queue_top10_verification_v1_2.csv` + `scripts/verify_source_queue_top10_v1_2.py`(이번 라운드 실제 산출 형태). Top10 후보별 `source_confirmed/needs_review/missing/reject` 분류·근거(itemSeq·신호어·확인일). **없으면** v1.1 선행자료로 폴백: `docs/MediStack_next_relation_source_check_queue.md` + `data/next_relation_source_check_queue_v1_1.csv`(아직 확인 단계면 승격 진행 불가 → STOP).
- **(이번 라운드 산출물이 있으면 입력으로 사용)** `data/relation_expansion_draft_v1_2.json` — 승격 대상 후보의 relation 초안(성분·basis·source url/pointer). **없으면** v1.1 패턴 참고: `data/relation_expansion_draft_v1_1.json` + `docs/MediStack_relation_expansion_live_integration_v1_1.md`(통합 절차).
- 통합기 권위 패턴: `scripts/verify_atier_relation_sources.py`(출처 확인) + A티어 라이브 통합 절차(`MediStack_relation_expansion_live_integration_v1_1.md`) + C buffer_combo 데이터-only flip(`scripts/integrate_combo_banner_c_v1_1.py`, idempotent).
- validator/smoke 명령 세트: `docs/MediStack_v1.1_handoff.md` §6.

**선행 게이트(PM gate, 통과 못 하면 즉시 STOP):**
1. PM 명시 승인(승격할 후보 id 목록 지정)이 있는가?
2. 각 후보가 `source_confirmed` 이고 **출처가 식약처 허가사항**(문헌만은 불가)이며 url + pointer(확인일) 가 있는가?
3. 데이터 변경 전 **CI 전체 세트를 로컬에서 선실행**해 현재 baseline PASS 임을 먼저 확인했는가?
   세 조건 중 하나라도 미충족이면 데이터를 건드리지 말고 보고 후 멈춘다.

**허용 범위:**
- source_confirmed + PM 승인 후보만 **데이터-only append**: full index name_only → relation_card 재배분(total 17,580 불변) + relation export 추가(`relations` += · `meta.relation_count` 일치) + 각 신규 relation 에 `source.type=허가사항`·url·pointer(확인일) 부착 + validator 상수 갱신.
- 통합 후 validator + smoke **전체 세트**(v0.1/v0.2/v0.3 export·full index·potassium·surface-forms·search/HCTZ/alias smoke) 라이브 파일 인자로 재실행·기록.
- 적대 렌더 리뷰(과장·오도·원문보다 강한 표현·name_only 강등 누락) 통과 확인.

**금지:**
- ❌ **출처 미확인/문헌-only/needs_review/missing/reject 후보 승격 금지.** 허가사항 미기재(스타틴×CoQ10·H2×B12 등)는 source-policy 결정 전 통합 금지.
- ❌ **PM 승인 없는 임의 승격 금지** · 풀(대량) 확장 금지 · relation 카드별 개별 출처 신설 금지(relation 단위 부여·카드 상속 유지).
- ❌ full index total 17,580 변경(추가 확장은 별도 PM 승인) · DATA_URL 변경 · published/clinical flip.
- ❌ 제품/구매/영양제 추천 표현, 복용지시, "원문보다 강한" 위험·복용량 표현, "식약처 승인/약사 검수 완료/법적 문제없음" 표현.

**성공기준(검증가능):**
- 승격된 신규 relation 전건이 `source.type=허가사항`+url+pointer 보유, PM 승인 id 목록과 1:1 일치.
- 통합 후 `relations ≥ 41` & `meta.relation_count` 일치 · full index total 17,580 불변(name_only↔relation_card 재배분만) · published/clinical false.
- validator + smoke 전체 세트 **PASS** · 적대 렌더 리뷰 통과.
- 데이터-only(스키마 append-only) · 통합기 idempotent.

**STOP 조건 (멈추고 PM에 보고):**
- 선행 게이트 3조건 중 하나라도 미충족 → 데이터 미변경, 보고.
- 후보가 source_confirmed 로 보여도 출처가 허가사항이 아니거나(문헌-only) pointer 가 없으면 제외·기록.
- validator/smoke 중 하나라도 FAIL → 즉시 멈추고 원인 보고(임의 수정·강행 금지).
- 승격이 풀 확장/근거 약화로 번지면 멈추고 범위 재조정.

**산출물:** (게이트 통과 시) 데이터-only 통합 배치 + 통합 로그 문서(승격 id·출처·전후 baseline 숫자·validator/smoke 결과). (게이트 미통과 시) "승격 보류 사유" 보고만, 라이브 무변경.

---

## B. "내 약 목록 저장" MVP — 구현 프롬프트 (로컬 전용·무서버·민감정보 0)

> **목표:** 확정된 설계를 따라 **"내 약 목록 저장" MVP를 실제 구현**한다. **로컬 전용**(localStorage/IndexedDB) · **서버·계정·백엔드 0** · **개인정보/건강정보 수집 0**(약명/품목 식별자만) · **복용지시·해석 0**(자가 기록 보관까지만). 정적 SPA 범위 안에서만.

**입력 / 선행자료 (먼저 읽기):**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표3)
- **(이번 라운드 산출물이 있으면 입력으로 사용)** `docs/MediStack_saved_stack_mvp_design_v1_2.md` — 데이터 모델·저장소·Free 한도·"내 목록" 화면 스펙·면책/개인정보 문구. **없으면** STOP(설계 미확정 상태에서 구현 착수 금지) 또는 PM에 설계 선행 요청. 근거: `docs/MediStack_monetization_strategy_v1_1.md` §2·§3·§5.
- 렌더/가드 규약: `src/js/render.js`·`guards.js`·`app.js`(라우터)·`states.js`·`data.js`. 면책 노출 검증: `smoke_disclaimer_render.py`.

**허용 범위:**
- **클라이언트 로컬 저장 구현만**: localStorage/IndexedDB 에 보관. 저장 항목 = item_seq/품목명/추가일/(선택)자유 메모 정도까지만. 추가/삭제/비우기/내보내기(로컬 파일) UI.
- Free 한도(예: 5개) 게이트는 **C(Free/Plus 플래그)와 정합**하도록 플래그 기반으로 배선(C 산출물이 있으면 그 플래그를 사용, 없으면 단순 상수+TODO 표기).
- "내 목록" 라우트/화면 + 면책·"자가 기록 보관(복용지시 아님)" 고지 + 개인정보 비수집 고지. 기존 면책/출처/렌더 가드 승계.
- 변경 후 smoke(disclaimer·search regression) + 수동 브라우저 QA 절차 기록.

**금지:**
- ❌ **서버·계정·DB·동기화·외부 전송 일체 금지**(local-first 가 아니라 **local-only**). 분석/트래킹/원격 로그 0.
- ❌ **증상·질환·복용이력·연락처·생년 등 개인정보/건강정보 입력 경로 0**(약명/품목 식별자만). 저장 데이터가 "건강정보 컬렉션"으로 비치지 않도록 입력 필드 최소화.
- ❌ 저장된 약을 **해석·지시**하는 기능("이 약엔 X 보충/같이 드시면 안 됨") — 보관/표시까지만. 신규 의학 판단·점수·위험등급 생성 금지.
- ❌ name_only 저장 항목에 의학정보 부착(불변 규칙) · 제품/구매/제휴/영양제 추천 · 결제 구현(상품 등록은 별도 라운드).
- ❌ relation/export/full index/DATA_URL/published/clinical 변경. "식약처 승인/약사 검수 완료/법적 문제없음" 표현.

**성공기준(검증가능):**
- 저장은 **클라이언트 로컬 한정**(네트워크 요청 0 — 브라우저 네트워크 탭으로 확인) · 계정/서버/백엔드 0.
- 저장 데이터에 개인정보·건강정보 필드 0(약명/품목 식별자/추가일/메모만).
- "내 목록"은 복용지시·해석 없이 자가 기록 보관임이 화면 문구로 명시 · 공통 면책 노출 유지(smoke PASS).
- name_only 저장 항목 의학정보 미부착 · 기준선 데이터 숫자(relations 41 등) 불변(데이터 무변경).
- validator/smoke(영향 범위) PASS · 수동 브라우저 QA 통과.

**STOP 조건:**
- 설계 문서(`..._saved_stack_mvp_design_v1_2.md`)가 없으면 구현 착수하지 말고 설계 선행 요청.
- 구현이 서버/계정/동기화를 요구하기 시작하면 그 부분은 **후속 라운드**로 분리하고 MVP는 local-only 유지.
- 어떤 입력 필드가 건강정보(증상·질환 등) 성격이면 즉시 제거하고 약명/식별자만 남긴다.
- 저장 약을 해석·지시하는 방향으로 번지면 멈추고 "보관/표시까지만"으로 되돌린다.

**산출물:** "내 약 목록" MVP 구현(`src/js/*` + 필요한 화면/스타일) + 구현 로그 문서(저장 모델·local-only 확인·QA 결과). relation/export 데이터 무변경(`git status` 로 data/ 보호파일 clean).

---

## C. Free / Plus 기능 플래그 — 설계 프롬프트 (관리 도구 유료화·제품 0)

> **목표:** Free/Plus **기능 경계를 코드에서 분기할 기능 플래그(feature flag) 체계**를 설계한다(결제·상품 등록·결제 SDK 배선은 범위 밖). 유료화 가치 축 = **개인 관리 도구(정리·보관·상담 준비)** 이며, **Plus 가 의학 조언/복용량/제품 추천으로 넘어가지 않도록** 안전 경계를 플래그 수준에서 박는다.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표4)
- **(이번 라운드 산출물이 있으면 입력으로 사용)** `docs/MediStack_free_plus_plan_v1_2.md` — Free/Plus 기능 매트릭스 확정본·페이월 경계·각 Plus 기능 안전 근거. **없으면** v1.1 폴백: `docs/MediStack_monetization_strategy_v1_1.md` §1·§3·§3.1·§6.
- (정합) B 프롬프트 산출물(있으면 `docs/MediStack_saved_stack_mvp_design_v1_2.md`) — 내 목록 Free 한도가 동일 플래그로 게이트되도록.

**허용 범위 (플래그 설계 — 결제 구현 0):**
- 기능 플래그 스키마 설계: 플래그 키 목록(예: `feature.savedStack.limit`, `feature.familyProfile`, `feature.questionBuilder` …) · 기본값(Free) · Plus 해금 시 값 · 평가 위치(클라이언트, 로컬). 가치 축 = 관리 도구.
- **Free 핵심 약속을 플래그로 고정**: 약 검색·name_only 확인·기본 relation_card·면책/출처/복합제 배너·제한적 내 목록 저장 = **플래그와 무관하게 항상 ON**(페이월 뒤에 가둘 수 없는 항목으로 분류·문서화). 정보 접근은 절대 Plus 게이트 뒤로 보내지 않는다.
- 각 Plus 플래그에 **안전 정렬 근거** 부기(왜 이 기능이 "정리/보관/상담 준비" 성격인지). 가격/과금/엔타이틀먼트 검증은 **후보·자리표시(stub)까지만**.

**금지 (Plus 안전 경계 = 본 프롬프트 핵심):**
- ❌ **Plus 플래그가 복용량·진단·치료·위험 확정·영양제 추천 기능을 해금하는 것 금지.** 유료라고 "더 위험한 의학 판단을 대신"하지 않는다.
- ❌ 정보 접근(검색·name_only·기본 relation_card·면책/출처)을 Plus 게이트 뒤로 옮기는 플래그 금지.
- ❌ 알림 관련 플래그라도 "정보 갱신 사실 고지"까지만 — 행동 유도(보충/중단) 푸시 해금 금지.
- ❌ 결제 SDK/상품 등록/엔타이틀먼트 실검증 배선(별도 승인 라운드) · 본체 제품/구매/제휴 · 신규 relation · published/clinical flip. "식약처 승인/약사 검수 완료" 표현.

**성공기준(검증가능):**
- 플래그 스키마가 한 문서로 자기완결 + Free 핵심 약속이 "항상 ON(페이월 불가)" 으로 명시 고정.
- 각 Plus 플래그에 안전 근거 + "Plus 가 의학 조언으로 넘어가지 않음" 명문화 · 가격은 후보로만.
- 라이브 무변경(`git status` clean), 기준선 숫자 불변(설계 단계 — src 미배선 또는 stub만).

**STOP 조건:**
- 어떤 Plus 플래그가 복용지시/진단/제품 추천 성격이면 **Plus 에서 제외**하고 사유 기록.
- 결제/엔타이틀먼트 실배선이 필요해 보이면 멈추고 "별도 승인 라운드" 로 분리.
- Free 항목을 Plus 로 옮기려는 시점에 멈추고 "정보 접근 항상 Free" 원칙 재확인.

**산출물:** Free/Plus 기능 플래그 설계 문서(플래그 스키마 + Free 항상-ON 목록 + Plus 안전 근거). 결제/데이터 무변경.

---

## D. relation source 표시 UI — 구현 프롬프트 (fail-closed 공개 gate·과신 문구 0)

> **목표:** 확정 설계를 따라 relation_card 의 **식약처 허가사항 출처(attribution) 표시 UI를 구현**하고, **공개 모드 fail-closed gate**(source 미확정 → name_only 강등, 중간 라벨 없음)를 배선한다. **현행 라이브(내부 모드)는 무변경** 보장. 출처 표시는 **"허가사항 출처"까지만** — "승인/검수 완료/안전 보장" 같은 **과신(over-trust) 문구 금지**.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표5)
- **(이번 라운드 산출물이 있으면 입력으로 사용)** `docs/MediStack_relation_source_ui_design_v1_2.md` — 출처 표시 UI 스펙·`publicRelationGate` 스펙(fail-closed)·강등 UX 문구. **없으면** v1.1 폴백: `docs/MediStack_source_attribution_design.md`(설계 원리: relation 단위 부여·카드 상속·`source_status`·gate).
- 현 렌더: `src/js/render.js renderDetail()`(이미 `source.type` + `원문 보기↗` + `<details>출처 상세</details>` 상속 표시 중) · `guards.js` · `app.js`(모드 분기). 검증: `smoke_disclaimer_render.py`(S4 출처 출력).

> ⚠️ 정정: `MediStack_source_attribution_design.md` 본문 숫자는 작성 시점(relation 30 / relation_card 558)이다. **현재는 relations 41 / relation_card 1,072.** "relation 단위 부여 + 카드 상속" 원리는 그대로, 수치는 공통 §0 기준선을 사용한다.

**허용 범위:**
- 출처 표시 UI 구현(상속 구조 렌더 개선·문구 정련). 필요한 필드는 **append-only**(`relation_source_title`/`source_checked_at`/`source_status` 등 — 기존 필드 의미 불변).
- 공개 모드 gate 배선: `mode==='public'` 이고 `source_status !== 'confirmed'` 이면 **name_only 로 강등**(fail-closed · 중간 "확인 중" 라벨 노출 0 · 단일 경로). 강등은 **표시 라우팅만**(relation 41건 데이터 무손실). **내부/현행 모드(`mode!=='public'`)는 항상 relation_card — 무변경 보장.**
- smoke(disclaimer 출처 출력·search regression) + 내부/공개 양 모드 수동 QA 기록.

**금지 (과신 차단 = 본 프롬프트 핵심):**
- ❌ **과신 문구 금지**: "식약처 승인 / 약사 검수 완료 / 법적 문제없음 / 안전 보장 / 관계 없음 보장". 출처는 "허가사항에 근거한 참고정보 출처"까지만. 면책 톤 유지.
- ❌ `source_status` 를 **임의로 `confirmed` 자동 부여 금지**(승격은 규제 자문/검토 후 A·별도 단계). gate 가 confirmed 를 임의 통과시키지 않게.
- ❌ 공개 모드 강등을 **삭제/숨김**으로 구현 금지(데이터 손실 0 — 라우팅 강등만). relation_card 카드별 개별 출처 신설 금지(상속 유지).
- ❌ relation/export/full index/DATA_URL 변경 · published/clinical flip · 내부 모드 동작 변경.

**성공기준(검증가능):**
- 출처 표시 = relation 단위 상속(카드별 개별 출처 신설 0) · 과신 문구 0(면책 톤).
- 공개 모드: confirmed 아니면 무조건 name_only 강등 · 중간 라벨 0 · relation 41건 무손실(강등=라우팅).
- 내부 모드(현행 라이브) 무변경(`mode!=='public'` → 항상 relation_card) · smoke PASS · 양 모드 QA 통과.
- 데이터 무변경(`git status` 보호파일 clean) 또는 append-only 필드만 · 기준선 숫자 불변.

**STOP 조건:**
- 설계(`..._relation_source_ui_design_v1_2.md`)가 없으면 v1.1 설계로 폴백하되, gate 정책이 모호하면 설계 선행 요청.
- **일반 공개(공개 모드 실노출)는 규제 자문(STOP #1)+source confirmed 승격(STOP #2) 전까지 NO-GO** — gate 코드는 구현하되 공개 모드를 라이브 기본값으로 켜지 않는다(내부 모드 유지).
- `source_status` 를 데이터에 임의 confirmed 부여하려는 시점에 멈춘다.

**산출물:** 출처 표시 UI + 공개 gate 구현(`src/js/*`) + 구현 로그(상속 확인·fail-closed 동작·내부 모드 무변경·QA 결과). relation/export 데이터 무변경.

---

## E. name_only UX 개선 — 구현 프롬프트 (개인/건강정보 수집 0)

> **목표:** 확정 설계를 따라 **name_only(품목명 확인) 화면의 UX를 구현·개선**한다 — **의학정보를 부착하지 않는 범위 내에서** 문구 명료화·검색 보조 향상만. "정보 없음 = 안전 아님"을 오해 없이 전달한다. **개인정보/건강정보 수집 경로 0.** 핵심 약속(검색 보조일 뿐, 의학 정보 아님) 불변.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표8)
- **(이번 라운드 산출물이 있으면 입력으로 사용)** `docs/MediStack_name_only_ux_improvement_v1_2.md` — name_only UX 개선 스펙(고지 문구·중립성·검색 보조 동선·smoke 갱신 스펙). **없으면** v1.1 폴백: `docs/MediStack_v1.1_handoff.md`(name_only UX 핵심 약속) + `docs/MediStack_v1.2_plan.md` 목표8.
- 현 렌더/검증: `src/js/render.js`·`states.js`·`guards.js` · `smoke_search_regression`(name_only 케이스 A~H) · `validate_potassium_name_only_policy`.

**허용 범위:**
- name_only 화면 문구·레이아웃 구현 개선: 고지 문구 명료화(중립 면책 톤) · "등록 정보 없음이 관계 없음 보장 아님" 명시 · 검색 보조 동선(재검색·유사 표기 안내 등) 개선. name_only 는 **비클릭(상세 라우팅 없음)** 동작 유지.
- 변경 시 `smoke_search_regression`(name_only 케이스) 갱신 + 수동 QA.

**금지 (의학정보 미부착 = 본 프롬프트 핵심):**
- ❌ **name_only 에 의학정보 부착 0**: 상호작용·영양소·복용지시·관리·칼륨 보충안내 등 일절 금지(불변 규칙).
- ❌ 문구가 "안전합니다/복용하세요/걱정 없음" 류로 읽히게 하는 것 금지(중립 면책 톤 유지).
- ❌ **개인정보/건강정보 입력·수집 경로 추가 금지**(증상·질환·복용 의도 등 질문 0). name_only 는 순수 검색 보조.
- ❌ name_only 를 상세 카드로 클릭 라우팅 연결 · 제품/구매/영양제 추천 · relation/export/full index/DATA_URL 변경 · published/clinical flip · "식약처 승인/약사 검수 완료" 표현.

**성공기준(검증가능):**
- name_only 의학정보 부착 0 · 문구 중립(안전/복용 단정 0) · 비클릭 동작 유지.
- 개인정보/건강정보 수집 경로 0 · 칼륨 standalone 차단 정책(`validate_potassium_name_only_policy`) 무영향.
- `smoke_search_regression`(A~H) PASS · 수동 QA 통과 · 기준선 데이터 숫자 불변(데이터 무변경).

**STOP 조건:**
- 문구 "개선"이 의학정보 부착·과장·"안전 보장"으로 번지면 즉시 멈추고 중립 면책 톤으로 되돌린다.
- 어떤 입력/질문이 건강정보 성격이면 제거(name_only 는 정보 수집 화면이 아니다).
- name_only 를 클릭→상세로 연결하려는 시점에 멈춘다(비클릭 유지).

**산출물:** name_only UX 구현(`src/js/*` + 스타일/문구) + 구현 로그(의학정보 미부착 확인·문구 중립성·QA·smoke 결과). relation/export 데이터 무변경.

---

## F. 별도 영양제 앱 기획 — 분리 우선 프롬프트

> **목표:** 제품/제휴 수익을 추구할 경우의 **별도 영양제 앱**을 기획한다(정보/비교 도구 방향 — 추천 엔진 아님). **MediStack 본체와 데이터·브랜드·동선이 완전히 분리**됨을 전제로 한다(MediStack 본체에는 제품/구매/제휴·영양제 추천을 영구히 넣지 않는다). **분리가 이 프롬프트의 전부다.**

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`, `docs/MediStack_v1.2_plan.md`(목표10)
- `docs/MediStack_supplement_app_separation_strategy.md` — **존재(2026-06-14 작성·보강됨).** 분리 경계 계약(§5: 데이터·UX·브랜드 비공유) + **금지 크로스오버 구체 예시(§5.4)** + **분리 자가점검(§5.6)** 이 정의돼 있다. 추가 근거: `docs/MediStack_monetization_strategy_v1_1.md` §4·§5. 본 프롬프트는 그 분리 전략을 **실행 기획(기능 우선순위·MVP)으로 구체화**하되, 경계 계약(§5)·자가점검(§5.6)을 게이트로 절대 위반하지 않는다.

**허용 범위 (전부 기획 문서 — 구현 0):**
- 별도 앱의 정체성·**자체** 성분 데이터 출처·브랜드·수익 모델(제품/제휴 허용은 *별도 앱에서만*, 그조차 1차 방향은 정보/비교) 기획.
- 후보 기능은 분리 전략 §4 의 **정보/비교 성격**(성분 검색·항산화 네트워크 설명·메가도스 중립 설명·내 스택 등록·중복/과다 체크·형태/성분당 가격 비교·복용 타이밍 플래너 — 전부 "제품 추천 아님")으로 한정.
- **분리 경계 명문화**: MediStack 본체와 코드/데이터/브랜드/사용자 동선이 섞이지 않음. MediStack 은 "한국용 약-영양소 참고정보 베타"로 순수 유지.

**금지 (분리 원칙 = 본 프롬프트 핵심):**
- ❌ **MediStack 본체에 제품/구매/제휴/영양제 추천을 끌어들이는 모든 설계 금지.** 두 앱의 동선·데이터·브랜드 혼합 금지(§5.4 의 8가지 크로스오버 형태 전부 금지).
- ❌ MediStack relation 데이터를 영양제 앱의 "추천/비교 근거"로 재사용·복제·핸드오프 금지 — 참고정보를 판매 정당화로 전용(신뢰·규제 리스크).
- ❌ 영양제 앱이 **약(의약품) 검색 결과를 입력으로 받는 것** 금지(§5.1). "약 검색 → 영양제 추천 → 구매" 동선은 양쪽 앱에서 영구 금지.
- ❌ MediStack 쪽 코드/데이터/DATA_URL/relation/published 변경. 신규 relation. "식약처 승인/약사 검수 완료/법적 문제없음" 표현. 제품 링크는 별도·나중(§6).

**성공기준(검증가능):**
- 별도 영양제 앱 기획이 한 문서로 자기완결 + **MediStack 과의 분리 경계가 명문화**(§5.4 크로스오버 금지·§5.6 자가점검 통과 항목만 포함).
- 후보 기능 전부가 "정보/비교"(추천 아님) 성격 · 약-결과 입력·relation 재사용 0.
- MediStack 본체는 어떤 변경도 받지 않음(`git status` clean, 기준선 숫자 불변).

**STOP 조건:**
- 기획이 MediStack 본체에 제품/구매 동선을 추가하거나 두 앱을 데이터/동선/브랜드로 묶는 방향으로 흐르면 즉시 멈추고 §5.6 자가점검으로 차단 후 "별도 앱으로 분리"로 되돌린다.
- 영양제 앱이 MediStack relation/면책 톤/약 검색 결과를 추천·판매 근거로 쓰려 하면 멈추고 분리 원칙 재확인.
- 어떤 기능이 "제품 추천"으로 번지면 멈추고 "정보/비교"로 한정.

**산출물:** 별도 영양제 앱 기획 문서(신규) — `docs/MediStack_supplement_app_separation_strategy.md` 의 분리 경계를 준수한 실행 기획. MediStack 본체 무변경.

---

## G. v1.2-beta release readiness — 검증 + 일반공개 NO-GO 게이트 재확인 프롬프트

> **목표:** v1.2-beta 의 **릴리스 준비 상태를 검증**한다 — validator/smoke **전체 세트** 라이브 파일 실행 + 불변(기준선 숫자·봉인) 확인 + 약관/개인정보/면책 링크 동선 점검 + **일반 공개는 NO-GO** 게이트 재확인. **읽기/검증 위주**(약관 링크 동선 등 표시 정리만 PM 승인 시 허용).

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`(§6 validator/smoke 명령 세트), `docs/MediStack_v1.2_plan.md`(목표9·§4 불변 가드·기준선)
- 법적 게이트: `docs/MediStack_public_release_legal_safety_checklist.md`(STOP #1~#6) · 초안 3종: `docs/MediStack_disclaimer_and_terms_draft.md` · `docs/MediStack_privacy_and_feedback_policy_draft.md` · 면책 노출 검증 `smoke_disclaimer_render.py`.
- **(이번 라운드 산출물이 있으면 함께 점검)** A~F 의 v1.2 산출물(`docs/MediStack_*_v1_2.md`)이 데이터/렌더를 건드렸다면 그 변경의 회귀를 본 게이트로 재확인.

**허용 범위:**
- **회귀 실행(읽기/검증)**: validator + smoke **전체 세트**를 라이브 파일 인자로 실행·기록 — v0.1/v0.2/v0.3 export validator · full index · potassium name_only policy · surface-forms · search regression smoke(A~H) · HCTZ/alias smoke · disclaimer render smoke.
- 불변 확인: 기준선 숫자(아래 검증 기대값) · published/clinical_reviewed false 봉인 · DATA_URL v0.2 불변 · full index total 17,580 불변.
- 약관/개인정보/면책 **링크 동선 점검**: 초안 3종이 DRAFT(법률 검토 전)임을 사용자 노출 문구에서 명시 · 면책(`disclaimers.common`) 모든 상세 노출 · 제품/구매/제휴 부재 고지 · 개인정보 비수집 고지 동선 확보. (문구/링크 정리 실변경은 PM 승인 시에만, 그 외엔 점검·보고.)
- **일반 공개 NO-GO 게이트 재확인**: 규제 자문(STOP #1)·relation source confirmed 승격(STOP #2) 미충족 → 일반 공개는 **NO-GO** 임을 명문화.

**검증 기대값 (회귀 성공 = 아래 전부 일치, 데이터 무변경 라운드 기준):**
- `relation_card = 1,072` · `name_only = 16,508` · `full index total = 17,580`
- `relations(export) = 41` · `alias_count = 717` · `product_aliases = 679` · `verified_item_seqs = 1,059/20`
- `published = false` · `clinical_reviewed = false` · `DATA_URL = v0.2`(불변)
- 모든 validator/smoke PASS. (A 라운드에서 PM 승인 데이터-only 승격이 있었으면 그 라운드의 갱신 기대값으로 대체하되 published/clinical false·DATA_URL·full index total 17,580 은 불변.)

**금지:**
- ❌ **일반 공개(공개 모드 라이브 노출)·published/clinical flip 금지** — 규제 자문·source confirmed 전 NO-GO.
- ❌ validator/smoke FAIL 을 임의 수정·무시·강행 금지(멈추고 보고).
- ❌ 데이터/relation/export/DATA_URL/full index 변경(본 프롬프트는 검증+표시 링크 정리까지) · 신규 relation · 제품/구매/제휴.
- ❌ "식약처 승인/법적 문제없음 확정/약사 검수 완료" 표현 · 무단 deploy · 무단 tag · git commit 자동 수행.

**성공기준(검증가능):**
- validator/smoke 전체 세트 PASS + 검증 기대값 전부 일치(또는 A 승인 라운드 갱신값) + 봉인(published/clinical false·DATA_URL·full index total) 불변.
- 약관/개인정보/면책 링크 동선·DRAFT 표기·면책 노출이 점검 리포트로 확정 + 제품/개인정보 비수집 고지 확인.
- **일반 공개 NO-GO** 가 게이트 재확인으로 명문화 · 보호데이터 `git status` clean(검증 단독 실행 시).

**STOP 조건 (멈추고 PM에 보고):**
- 검증 기대값/봉인 중 하나라도 어긋나면 즉시 멈추고 원인 보고(데이터 오염·회귀 의심). 임의 수정 금지.
- 법적 게이트(STOP #1~#6) 중 미충족이 있으면 **일반 공개 진행 금지** — 상태만 보고.
- 링크/문구 실변경이 필요해 보이면 PM 승인 전까지 점검·제안까지만.

**산출물:** v1.2-beta release readiness 리포트(전 validator/smoke 결과 + 검증 기대값 일치 + 봉인 확인 + 약관/개인정보/면책 링크 동선 점검 + 일반 공개 NO-GO 재확인). 라이브 무변경(PM 승인 표시 정리 시에만 해당 변경).

---

## H. C buffer_combo 추가 회귀 — 검증 + (신규 후보 시) 데이터-only 패턴 프롬프트

> **목표:** C(buffer_combo) flip 이후 상태에 대해 **validator/smoke 전체 세트를 재실행**하여 기준선이 유지됨을 확인한다. 그리고 **새로운 buffer_combo 후보가 나타나면** 기존 C 통합기와 **동일한 데이터-only 패턴**(PM 승인·신규 relation 0·other_label 은 완충 기능명)으로만 처리하도록 가드를 재기술한다.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_ppi_calcium_combo_reclassification_v1_1.md` (C = buffer_combo 재분류 정책 · §2-3 other_label 설계 주의 · §3 데이터-only 작업 범위).
- 통합기(권위 패턴): `scripts/integrate_combo_banner_c_v1_1.py` (idempotent flip · `PPI_RID={란소프라졸:[36,37], 라베프라졸:[32,33]}` · `OTHER_LABEL="위산 중화 완충 성분(침강탄산칼슘)"` · 신규 relation 0).
- validator/smoke 명령 세트: `docs/MediStack_v1.1_handoff.md` §6.

**허용 범위:**
- **회귀 실행(읽기/검증)**: validator + smoke 전체 세트를 라이브 파일 인자로 실행하고 결과를 기록.
  - 데이터 변경 시 CI 전체 세트를 로컬 선실행(교훈): surface-forms / v0.1 / potassium selftest 포함.
- (신규 후보가 있을 때만) C 와 동일한 **데이터-only** flip: full index name_only→relation_card(total 17,580 유지) + `verified_item_seqs` += + `product_aliases` +=(is_combination=true·basis=PPI·notice=true·source_relation_ids=기존 PPI relation·**other_label=완충 기능명**) + validator 상수 갱신. **신규 relation 0.**

**검증 기대값 (회귀 성공 = 아래 전부 일치):**
- `relation_card = 1,072` · `name_only = 16,508` · `full index total = 17,580`
- `relations(export) = 41` · `alias_count = 717` · `product_aliases = 679` · `verified_item_seqs = 1,059/20`
- `published = false` · `clinical_reviewed = false` · `DATA_URL = v0.2`(불변)
- 모든 validator/smoke PASS(handoff §6 기대치). 보호데이터 `git status` clean(회귀 단독 실행 시).

**금지:**
- ❌ **신규 relation 생성 금지** — PPI×칼슘 nutrient relation 포함 절대 금지(허가사항 출처 없음·칼슘=완충제). relations 41 불변.
- ❌ buffer_combo other_label 을 **"칼슘"** 으로 쓰는 것 금지 — 반드시 **완충 기능명**("위산 중화 완충 성분(...)" 류). 영양 칼슘 오독 차단이 핵심.
- ❌ 칼슘 추천/보충 표현 · 제품/구매 · 보류군(라베프라졸+산화마그네슘 등, 재분류 문서 "E" 코드 — 본 모음의 프롬프트 E 와 무관) 접촉 · DATA_URL/export relations 변경 · published/clinical flip.
- ❌ PM 승인 없는 신규 후보 flip. 데이터 변경은 **PM 명시 승인 batch** 에서만.

**성공기준:**
- (회귀) 위 "검증 기대값" 전부 일치 + 전 validator/smoke PASS.
- (신규 후보 처리 시) C 패턴 그대로: 신규 relation 0 · other_label=완충 기능명 · idempotent · CI 전체 세트 로컬 선실행 PASS · 적대 렌더 리뷰(칼슘 오독·부분정보 오인) 통과.

**STOP 조건:**
- 검증 기대값 중 하나라도 어긋나면 **즉시 멈추고** 원인 보고(데이터 오염·통합기 재실행 흔적 의심). 임의 수정 금지.
- 새 buffer_combo 후보가 **PM 승인 없이** 발견되면 flip 하지 말고 **후보로만 보고**(do_not_implement_yet).
- other_label 후보가 "칼슘" 단독이거나, 카드에 PPI×칼슘 nutrient 정보가 끼면 멈추고 정정.

**산출물:** 회귀 검증 리포트(전 validator/smoke 결과 + 기준선 숫자 일치 확인). 신규 후보 처리 시에만 데이터-only 통합 + 통합 문서. 그 외 라이브 무변경.

---

## 7. 공통 마무리 (모든 프롬프트)

- 작업 종료 시 보호데이터 `git status` 확인. 프롬프트별 변경 허용 범위:
  - **설계/기획 문서 프롬프트(C·F)** = 데이터/`src` **둘 다 clean**(문서만).
  - **구현 프롬프트(B·D·E)** = `src/js/*` 등 **앱 코드는 변경**하되 **relation/export/full index/DATA_URL 등 보호 데이터는 clean**(append-only 필드 외 데이터 무변경).
  - **데이터-only 프롬프트(A 승격 · H buffer_combo)** = **PM 명시 승인 batch 에서만** 보호 데이터를 만질 수 있다(그 외엔 clean).
  - **검증 프롬프트(G)** = 읽기/검증 위주, PM 승인 표시(링크/문구) 정리 외 보호 데이터 clean.
- 모든 프롬프트는 **데이터 변경 전 CI 전체 세트(validator+smoke)를 로컬 선실행**해 baseline PASS 를 확인한다(이번 라운드 교훈).
- 어떤 프롬프트도 **git commit / deploy / tag 를 자동 수행하지 않는다.** 그 단계는 PM 명시 지시에서만.
- 커밋이 승인되면 메시지 끝에 Co-Authored-By trailer.

> **안전 원칙(불변, 재게시):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / relation 신규·풀 확장 금지 / name_only 의학정보 부착 금지 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전, 칼슘 완충 복합제는 other_label=완충 기능명) / relation 없는 약은 name_only 로만 / 제품·제휴는 별도 앱으로 분리 / 수동 deploy·무단 tag 금지.

---
---

# 작업12 (2026-06-14) — relation factory 파이프라인 + 인프라 실행 프롬프트 6종 (A2~F2)

> 작성일: 2026-06-14(작업12 보강·**append, 위 A~H 블록은 보존**). 이 블록은 위 §A~H 와 **별개의 6종**이다(라벨 충돌 방지 위해 **A2~F2** 사용). 각 프롬프트는 **자기완결**: 재개 트리거 · 먼저 읽을 문서 · 허용/금지 · 성공기준 · STOP 을 매번 반복 기재한다. 위 §0 공통 가드레일·§7 공통 마무리는 이 6종에도 **그대로 적용**된다(중복 기재 최소화).
>
> **이 블록 색인:** A2=relation factory 후보 Top50 source 확인(허가사항 fetch·source_confirmed 승격 게이트) · B2=다음 draft relation 배치 생성(source_confirmed→draft) · C2=다음 live relation 통합(draft→live·validator/smoke/deploy 패턴) · D2=Supabase 스키마 설계(서버 트랙·신규) · E2=relation 도움말 카피 UI 구현(`src` 변경 주의) · F2=내 약 목록(saved stack) MVP 구현(로컬·무서버·민감정보 0).
>
> **A2→B2→C2 는 한 파이프라인**(source 확인 → draft 생성 → live 통합)이고, **D2·E2·F2 는 독립 인프라/UX 트랙**이다. A2~C2 사이의 관계: A2 의 `source_confirmed` 산출이 B2 의 입력, B2 의 draft 가 C2 의 입력. 게이트를 건너뛰지 말 것(미확인 후보가 draft·live 로 새는 것이 최대 위험).

## 작업12 라이브 기준선(2026-06-14, HEAD `91d5486` "Promote v1.2 draft relations 14건 라이브 통합 relations 41→55" 시점)

> ⚠️ 위 §0 표(작업11·relations 41)는 **C2 통합 전 기준선**이다. 작업12 시점의 회귀 기준은 **아래 값**(draft 14건 라이브 통합 후). 두 표가 다르면 **아래(최신)** 가 우선.

| 항목 | 값 |
|---|---|
| relations (export) | **55** (ids 1–14, 16–56 · id15 결번 유지) |
| meta.relation_count | **55** (relations 길이와 일치) |
| relation_card (full index) | **1,077** |
| name_only (full index) | **16,503** |
| full index total | **17,580** (불변) |
| verified_item_seqs | **1,064 / 22** |
| alias_count (meta) | **717** |
| product_aliases | **679** · ingredient_aliases **38** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (v0.2, 불변) |
| published / clinical_reviewed | **false / false** (봉인) |
| 통합기/검증 권위 | `scripts/integrate_relation_draft_v1_2.py`(idempotent·dry-run) · `validate_relation_draft_v1_2.py`(19체크) · `smoke_relation_draft_v1_2.py`(209체크) |

> 이미 라이브 covered(중복 후보 금지): 위 작업지시 헤더의 covered 목록 + 작업12에서 추가된 **FQ×아연(레보/시프로/오플록/목시 = id43–46), 테트라×아연(독시/미노 = id47–48), 리세/이반드론산×철·Mg(id49–52), 클로르탈리돈×K·Mg(id53–54), 인다파미드×K·Mg(id55–56)**. 이 13성분-테마는 **재후보화 금지**(이미 relation).

---

## A2. relation factory 후보 Top50 source 확인 — 허가사항 fetch · source_confirmed 승격 게이트 (데이터 무변경)

> **목표:** relation 확장 후보 풀(목표 ~Top50, 현실 가용분만)에 대해 **식약처 허가사항(nedrug)을 실제 fetch 하여 출처를 확인**하고, 후보별로 `source_confirmed / needs_review / missing / reject / hold` 로 **분류만** 한다. 이 단계는 **source 확인 + 분류 산출까지**이며, **relation/draft/full index/export/src 전부 무변경**이다. `source_confirmed` 는 **허가사항(첨부문서) 신호어가 실제 확인된 후보에만** 부여(문헌-only·동거어 없음·계열 일반화 위험은 금지). 고위험군(와파린·항응고/항혈소판×K·항암·임신/소아/정신건강)은 **분류만 hold/high_risk**, source 확인·채택 금지.
>
> **재개 트리거:** "메디스택 relation factory" / "relation factory Top50 source 확인" / "다음 relation 출처 확인".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md`(리포 가드레일) · 이 문서 §0 공통 가드레일 + 위 "작업12 라이브 기준선".
2. `docs/MediStack_next_relation_source_check_queue.md` — **후보 큐 권위본**(Q01~Q11 그룹 A~F + 점수·우선순위). 단, **Q04/Q06/Q07/Q10/Q11 은 작업12에서 이미 라이브**(id43–56) → **재확인 대상에서 제외**. 남은 P1 enrichment(Q01 에스오메프라졸 인덱스트랙·Q08 레보티록신×Mg)·P2(Q02 잔여 PPI 단일제·Q03 잔여 경구 비스포)·needs_review(Q05 세팔로스포린 class 일반화 위험)·hold(스타틴×CoQ10·H2×B12 = 허가사항 미기재 예상, source-policy 결정 전 NO-GO) 위주.
3. `data/next_relation_source_check_queue_v1_1.csv` — 후보별 점수·`current_status`·`likely_source_type`·`expected_card_impact`.
4. **출처 확인 권위 패턴(승계):** `scripts/verify_atier_relation_sources.py` 와 `scripts/verify_source_queue_top10_v1_2.py` — 후보 성분별 단일성분 대표 2~3품목 nedrug `getItemDetail` fetch → 테마 신호어 검색 → 분류. 산출 형태 참고: `docs/MediStack_source_queue_top10_verification_v1_2.md` + `data/source_queue_top10_verification_v1_2.csv`(Top10 라운드 = source_confirmed6/needs_review5/reject2/hold5).

**선행 게이트(하나라도 미충족이면 STOP·데이터 무변경):**
1. 후보가 위 "작업12 covered" 13성분-테마 또는 헤더 covered 목록과 **중복이 아닌가**(중복이면 제외).
2. 후보가 고위험군(와파린×K·항응고/항혈소판×K·항암·임신/소아/정신건강)이면 source 확인·채택을 **시도하지 않고** `hold`/`high_risk` 분류만.
3. fetch 가 실패/차단되면 추정으로 `source_confirmed` 부여 금지 → `missing` 또는 `needs_review`.

**허용 범위:**
- nedrug `getItemDetail` **실 fetch**(verify 스크립트 패턴) → 허가사항 본문에서 nutrient 동거 신호어(예: "다가양이온", "철·칼슘·마그네슘과 함께 복용 시 흡수 저하", "간격을 두고" 등) 확인 → 후보별 `source_status ∈ {source_confirmed, needs_review, missing, reject, hold}` + 근거(itemSeq·신호어·확인일·url) 기록.
- 산출물 = **source 확인 리포트(신규 docs)** + **확인 CSV(신규 data, 후보 메타만)**. 둘 다 **읽기/문서 트랙**(relation/export/full index/alias/src 무변경).
- **허가사항 우선 gate**: 문헌만 있고 허가사항 동거어가 없으면 `source_confirmed` 금지(H2×B12·스타틴×CoQ10 선례 = source-policy 결정 전 NO-GO).
- 계열 일반화(class-wide)는 **성분별 개별 허가사항 확인**이 없으면 `reject`(세프디니르×철 = 성분특이, 세팔로스포린 일괄확장 금지 = Q05 선례).

**금지:**
- ❌ `source_confirmed` **자동 승격 금지** — 기본값은 `needs_source`/`candidate_only`/`source_check_needed`, 허가사항 신호어가 실제 확인된 후보에만 confirmed.
- ❌ 이 단계에서 **relation 생성·draft 생성·full index flip·alias 부여·export 변경·src 변경 일체 금지**(분류 산출까지만).
- ❌ 고위험군 source 확인·채택(분류만) · 중복 후보 재확인 · 풀(대량 class-wide) 확장.
- ❌ 추천/구매/복용지시 어휘 · "식약처 승인/약사 검수 완료/법적 문제없음" 표현 · published/clinical flip.

**성공기준(검증가능):**
- 후보별 `source_status` + 근거(itemSeq·신호어·url·확인일)가 1:1로 기록 · `source_confirmed` 는 전건 **허가사항 동거어 실확인**.
- 고위험군은 hold/high_risk 분류만(source 확인 0) · 중복·계열 일반화 후보 정상 제외/reject.
- 데이터/src `git status` clean(문서·후보 CSV 신규만) · 기준선 숫자(relations 55 등) 불변.

**STOP 조건(멈추고 PM 보고):**
- fetch 차단/실패가 광범위 → 추정 confirmed 금지, `missing` 기록 후 보고.
- 후보가 허가사항 미기재(스타틴×CoQ10·H2×B12 류)로 드러나면 confirmed 금지 → "source-policy 결정 필요" 로 보고.
- 분류가 "이 관계가 사실이다" 단정이나 채택 지시로 번지면 멈추고 "출처 확인·분류까지만" 으로 환원.

**산출물:** source 확인 리포트(`docs/MediStack_relation_factory_source_check_*.md`) + 후보 메타 CSV(`data/relation_factory_source_check_*.csv`). relation/export/full index/alias/src 무변경. **B2 의 입력은 여기서 `source_confirmed` 로 확인된 후보뿐이다.**

---

## B2. 다음 draft relation 배치 생성 — source_confirmed → draft (데이터: draft 파일까지·live 무변경)

> **목표:** A2(또는 기존 source 확인 라운드)에서 **`source_confirmed`(허가사항 동거어 실확인)** 로 분류된 후보만 골라, 라이브 통합 전 **draft relation 배치(JSON)**로 작성한다. **draft 파일 + preflight 문서까지만**이며, **live(export/full index/alias/src) 무변경**이다. 전건 `published=false` · `do_not_implement_yet=true`. 신규 relation 의 evidence·라벨은 **원문보다 강하지 않게**, 기존 라이브 선례(HCTZ×Mg=moderate 등)와 일관되게.
>
> **재개 트리거:** "메디스택 다음 draft 배치" / "source_confirmed draft 생성".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md` · 이 문서 §0 + "작업12 라이브 기준선".
2. **A2 산출물(있으면 입력)** `docs/MediStack_relation_factory_source_check_*.md` + `data/relation_factory_source_check_*.csv` — `source_confirmed` 후보 목록·출처(itemSeq·신호어·url·확인일). **없으면** 기존 `data/source_queue_top10_verification_v1_2.csv`(작업11 Top10 source_confirmed6)로 폴백하되, **작업12에서 이미 라이브된 후보는 제외**.
3. **draft 작성 권위 패턴:** `scripts/build_relation_expansion_draft_v1_1.py`(draft 빌더) · `data/relation_expansion_draft_v1_2.json`(직전 라운드 draft 스키마 = 성분·nutrient·mechanism/action·evidence·basis·source url/pointer·`do_not_implement_yet`) · 검증 `scripts/validate_relation_draft_v1_2.py`.
4. evidence 일관성 선례: `docs/MediStack_relation_expansion_v1_2_live_integration.md` §1(D12·D14 high→moderate 조정 근거 = 라이브 선례 일치 + 원문보다 강하지 않게).

**선행 게이트(미충족 STOP):**
1. 각 후보가 `source_confirmed` 이고 **출처가 허가사항**이며 url + pointer(itemSeq·신호어·확인일)가 있는가? (문헌-only·needs_review·missing·reject·hold 후보는 draft 진입 금지)
2. 후보가 "작업12 covered"·헤더 covered 와 중복이 아닌가?
3. 고위험군이 아닌가?(와파린×K·항응고/항혈소판×K·항암·임신/소아/정신건강 → draft 금지, hold 유지)

**허용 범위:**
- `source_confirmed` 후보만 **draft JSON 배치**로 작성: relation 초안(성분·nutrient·mechanism/action·evidence·basis·source.type=허가사항·url·pointer) + `published=false` + `do_not_implement_yet=true`. 칼륨 테마 행은 `potassium_safety_card=true`·`product_link_allowed=false` 플래그 동반 표기.
- evidence/라벨은 **라이브 선례와 일관·원문보다 강하지 않게**(저마그네슘혈증 "드물게" 라벨이면 moderate 등).
- draft validator(`validate_relation_draft_v1_2.py` 또는 후속 버전)로 draft 정합 self-check + preflight 문서(각 draft 가 통합 전 통과해야 할 체크리스트) 작성.

**금지:**
- ❌ **draft → live 통합 금지**(이 단계는 C2 가 아님). export/full index/alias/src 무변경.
- ❌ source 미확인/문헌-only/needs_review/reject/hold/고위험 후보 draft 화 · 중복 후보 · 풀 확장.
- ❌ `published`/`do_not_implement_yet` 를 true→해제 · evidence 를 원문보다 강하게(예: high 근거 없이 high) · 추천/구매/복용지시 어휘 · "식약처 승인/약사 검수 완료" 표현 · clinical flip.

**성공기준(검증가능):**
- draft 전건 = `source_confirmed`(허가사항 url+pointer 보유) · `published=false` · `do_not_implement_yet=true` · 중복/고위험 0.
- draft validator self-check PASS · evidence 라이브 선례와 일관(원문보다 강한 표현 0) · preflight 문서로 통합 전 체크리스트 자기완결.
- live 데이터/src `git status` clean(draft JSON + preflight 문서 신규만) · 기준선 숫자(relations 55 등) 불변.

**STOP 조건:**
- A2 산출(또는 source_confirmed 후보)이 없으면 draft 착수 금지 → A2 선행 요청.
- 후보가 confirmed 로 보여도 출처가 허가사항이 아니거나 pointer 없으면 제외·기록.
- draft 가 live 통합으로 번지면 멈추고 "draft 파일까지만"(통합은 C2·PM 승인) 으로 환원.

**산출물:** draft relation 배치 JSON(`data/relation_expansion_draft_*.json`, 전건 do_not_implement_yet=true) + preflight 문서(`docs/MediStack_draft_relation_*_preflight_*.md`). live(export/full index/alias/src) 무변경. **C2 의 입력은 여기서 preflight 통과한 draft 뿐이다.**

---

## C2. 다음 live relation 통합 — draft → live (PM 승인 데이터-only · validator/smoke/deploy 패턴)

> **목표:** B2(또는 직전 라운드)에서 **preflight 통과한 draft relation** 을, 작업12 와 **동일한 데이터-only 통합 패턴**(`integrate_relation_draft_v1_2.py` 승계)으로 **라이브에 통합**한다. **신규 relation 은 (PM 명시 승인 ∧ draft 전건 source_confirmed=허가사항 ∧ preflight pass) 게이트를 통과한 batch 만.** 통합 후 **CI 전체 세트(validator+smoke)를 라이브 파일 인자로 전수 실행**하여 기준선 갱신값으로 회귀 PASS 를 확인한다. **deploy/tag/commit 은 자동 수행하지 않는다**(PM 명시 지시에서만).
>
> **재개 트리거:** "메디스택 draft 라이브 통합" / "다음 relation 통합".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md` · 이 문서 §0 + §7 + "작업12 라이브 기준선".
2. **통합 패턴 권위본:** `docs/MediStack_relation_expansion_v1_2_live_integration.md` — 작업12 통합 보고서(전/후 수치 실측 §2 · 변경 파일 §3 · 검증 결과 §4). 이 14건 통합이 **그대로 따를 절차의 표준**이다.
3. **통합기/검증:** `scripts/integrate_relation_draft_v1_2.py`(idempotent·dry-run 지원·full index flip·verified_item_seqs += · validator 상수 갱신) · `scripts/validate_relation_draft_v1_2.py`(통합 정합 19체크) · `scripts/smoke_relation_draft_v1_2.py`(렌더 안전 209체크).
4. **CI 전체 세트 명령:** `docs/MediStack_v1.1_handoff.md` §6(아래 재게시).
5. preflight: `docs/MediStack_draft_relation_14_preflight_v1_2.md`(전건 pass_to_integrate 형태) 및 B2 가 만든 후속 preflight.

**선행 게이트(셋 다 충족해야 진행·하나라도 미충족 STOP):**
1. **PM 명시 승인**(통합할 draft id 목록 지정 + `do_not_implement_yet` 해제 지시)이 있는가?
2. 통합 대상 draft 전건이 `source_confirmed`(허가사항 url+pointer) + preflight pass 인가?
3. **통합 전** CI 전체 세트를 라이브 파일로 선실행해 **현재 baseline PASS** 임을 먼저 확인했는가?

**허용 범위(데이터-only·append):**
- 통합기 dry-run → 실통합: `medistack_v0.2_beta_export.json`(relations append · `meta.relation_count` 일치) + `full_drug_name_index_sample_v1_0.json`(name_only↔relation_card 재배분·**total 17,580 불변**) + `medistack_v0.3_aliases.json`(verified_item_seqs +=) + **validator 상수 갱신**(`validate_full_drug_name_index.py`·`validate_potassium_name_only_policy.py`) + fixture 갱신(`search_regression_v1_0.json`).
- 각 신규 relation 에 `source.type=허가사항`·url·pointer(확인일) 부착. 칼륨 행은 `potassium_safety_card=true`·`product_link_allowed=false`·고지 동반. 복합제는 부분정보 고지 동반.
- 통합 후 **CI 전체 세트 + 로컬 smoke/unit 전수 재실행**(아래) · **적대 렌더 리뷰**(과장·오도·원문보다 강한 표현·name_only 강등 누락·칼슘 오독·칼륨 임의보충 유도) 통과.

**CI 전체 세트(라이브 파일 인자·전수 PASS 필수, handoff §6 재게시):**
```
python3 scripts/validate_full_drug_name_index.py                                          # (+ --selftest)
python3 scripts/validate_potassium_name_only_policy.py                                    # 8/8 blocked 0 (+ --selftest)
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json    # 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json    # 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # 16/16
python3 scripts/validate_alias_surface_forms.py data/medistack_v0.3_aliases.json          # 5/5
python3 scripts/test_validate_v0_3_typeB.py  # 7/7   ; python3 scripts/test_validate_v0_3_combo.py  # 9/9
python3 scripts/test_validate_combo_ar.py    # 13/13 ; python3 scripts/validate_combo_approved_ready.py  # 13/13
python3 scripts/validate_bulk_alias_candidates.py        # 152/152
python3 scripts/smoke_search_regression_v1_0.py          # SEARCH REGRESSION PASS (A~H)
python3 scripts/smoke_hctz_disclosure.py                 # SMOKE PASS
python3 scripts/smoke_alias_regression.py                # 회귀
python3 scripts/smoke_disclaimer_render.py               # 면책/출처 노출
python3 scripts/validate_relation_draft_v1_2.py          # 통합 정합 (또는 후속 버전)
python3 scripts/smoke_relation_draft_v1_2.py             # 렌더 안전 (또는 후속 버전)
```
> ⚠️ zsh 공백변수 word-split 안 됨 → validator 는 **개별 호출**. guards/render ES module smoke 는 `/tmp` 복사 + `.mjs` 후 node(리포에 package.json 없음).

**금지:**
- ❌ **PM 승인 없는 통합** · source 미확인/문헌-only/needs_review/reject/hold/고위험 draft 통합 · 중복(작업12 covered) · 풀 확장.
- ❌ full index total 17,580 변경(추가 확장은 별도 PM 승인) · DATA_URL 변경 · published/clinical flip · relation 카드별 개별 출처 신설(relation 단위 부여·카드 상속 유지).
- ❌ **자동 deploy/tag/git commit** — PM 명시 지시에서만. 적대 렌더 리뷰 미통과분 통합.
- ❌ 추천/구매/복용지시 어휘 · "원문보다 강한" 위험·복용량 표현 · "식약처 승인/약사 검수 완료/법적 문제없음" 표현.

**성공기준(검증가능):**
- 통합된 신규 relation 전건 `source.type=허가사항`+url+pointer 보유 · PM 승인 id 목록과 1:1 일치.
- `relations == meta.relation_count`(55+N) · full index total 17,580 불변(재배분만) · DATA_URL v0.2·published/clinical false 불변.
- **CI 전체 세트 + 로컬 smoke/unit 전수 PASS** · 적대 렌더 리뷰 통과 · 통합기 idempotent(재실행 무변화).
- 통합 보고서에 전/후 수치 실측 기재(작업12 §2 형식). deploy/tag/commit 미수행(PM 지시 전).

**STOP 조건(멈추고 PM 보고):**
- 선행 게이트 3조건 중 하나라도 미충족 → 데이터 미변경, 보고.
- validator/smoke 중 하나라도 FAIL → 즉시 멈추고 원인 보고(임의 수정·강행 금지).
- 통합 전/후 수치가 기대(예: total 17,580 불변, relations 길이=count)와 어긋나면 멈추고 통합기 dry-run 으로 원인 격리.
- 통합이 풀 확장·근거 약화·deploy 자동수행으로 번지면 멈추고 범위 재조정.

**산출물:** (게이트 통과 시) 데이터-only 통합 batch + 통합 보고서(`docs/MediStack_relation_expansion_*_live_integration.md`, 승격 id·출처·전후 수치·CI/smoke 결과·적대 리뷰). (미통과 시) "통합 보류 사유" 보고만, 라이브 무변경. **deploy 는 PM 명시 지시에서만.**

---

## D2. Supabase 스키마 설계 — 서버 트랙 (신규·설계 문서까지·구현/배선 0)

> **목표:** MediStack 이 (장차) 서버 기능(예: 익명 피드백 수집, 향후 saved stack 동기화 옵션)을 검토할 경우의 **Supabase 스키마를 설계**한다. **설계 문서까지만**이며, **Supabase 프로젝트 생성·테이블 실생성·키 배선·클라이언트 SDK 추가·src 변경 일체 0.** 핵심 제약: MediStack 의 **local-only 정체성을 깨지 않도록**, 서버는 **민감정보(건강정보·개인식별정보) 비수집**을 스키마·RLS 수준에서 강제하고, **현행 라이브(정적 SPA·무서버)는 무변경 보장**. F2(saved stack)는 **로컬 우선**이며 서버는 **옵트인 동기화 후보(별도 승인)**로만 다룬다.
>
> **재개 트리거:** "메디스택 Supabase 스키마" / "서버 트랙 설계".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md` · 이 문서 §0(공통 가드레일) + "작업12 라이브 기준선".
2. `docs/MediStack_saved_stack_mvp_design_v1_2.md` — saved stack 의 **local-only 데이터 모델**(서버 스키마가 가질 수 있는 필드의 상한 = 약명/품목 식별자/추가일/메모, 건강정보 0). Supabase 스키마는 **이 모델을 초과하는 필드를 두지 않는다**.
3. `docs/MediStack_privacy_and_feedback_policy_draft.md` + `docs/MediStack_disclaimer_and_terms_draft.md`(DRAFT) — 개인정보 비수집·피드백 정책 톤. 서버 도입 시 이 정책과 모순되지 않게.
4. `docs/MediStack_public_release_legal_safety_checklist.md`(STOP #1~#6) — 일반 공개·서버 도입 NO-GO 게이트.
5. (라이브러리 최신 스키마/RLS 문법이 필요하면) Context7 로 Supabase 문서 조회 — 기억에 의존하지 말 것.

**허용 범위(설계 문서 — 구현 0):**
- 테이블/컬럼/타입/제약 설계(예: `feedback`(익명·자유텍스트·제출시각, PII 0) / (옵트인 후보) `saved_stack`(익명 device-scoped id·item_seq·품목명·추가일·메모) 등) + **RLS 정책 설계**(익명 키로 본인 row 만·읽기/쓰기 경계) + **민감정보 비수집을 스키마 수준에서 강제**(건강정보·생년·연락처·증상·질환 컬럼 부재 = 설계 원칙으로 명문화).
- 마이그레이션 SQL **초안(텍스트)**·인덱스·보존기간/삭제 정책 설계. 무엇을 **수집하지 않는지** 목록을 명시(negative schema).
- "서버는 옵트인·local-only 기본 불변" 경계 명문화 + 서버 도입이 **일반 공개 NO-GO 게이트**(STOP #1~#6)와 어떻게 상호작용하는지 기재.

**금지:**
- ❌ **Supabase 프로젝트/테이블 실생성·API 키 발급·`.env`/시크릿 추가·클라이언트 SDK(@supabase/supabase-js) 의존성 추가·src 배선 일체 금지**(설계 문서까지만).
- ❌ 스키마에 **건강정보/개인식별정보 컬럼**(증상·질환·복용이력·생년·연락처·이름·정밀위치 등) 설계 금지 — 약명/품목 식별자/익명 device id 상한.
- ❌ local-only 기본을 서버 필수로 바꾸는 설계 · MediStack relation/export 를 서버로 옮기는 설계(참고정보는 정적 유지) · published/clinical flip · 제품/구매/제휴 테이블.
- ❌ "식약처 승인/약사 검수 완료/법적 문제없음" 표현 · 동의 없는 수집 가정.

**성공기준(검증가능):**
- 스키마 설계가 한 문서로 자기완결 + **negative schema(비수집 목록)** 명시 + RLS 로 익명·본인 row 경계.
- saved stack 서버 후보는 **F2 local 모델을 초과하지 않음**(건강정보 0) · 서버는 옵트인·local-only 기본 불변 명문화.
- 라이브/src/데이터 `git status` clean(설계 문서 신규만) · 기준선 숫자 불변 · Supabase 실자원 0.

**STOP 조건:**
- 설계가 건강정보/PII 컬럼을 요구하면 즉시 제거하고 "약명/식별자/익명 id 상한" 으로 환원.
- 실제 프로젝트 생성·키 배선·SDK 추가가 필요해 보이면 멈추고 "별도 승인 라운드(구현)" 로 분리.
- 서버가 local-only 기본을 대체하려 하면 멈추고 "옵트인·로컬 우선" 으로 환원.

**산출물:** Supabase 스키마 설계 문서(`docs/MediStack_supabase_schema_design_*.md`) — 테이블/RLS/마이그레이션 초안 SQL/negative schema/옵트인 경계. Supabase 실자원·src·데이터 무변경.

---

## E2. relation 도움말 카피(help copy) UI 구현 — `src` 변경 주의 (과신 문구 0 · 의학정보 미부착)

> **목표:** relation_card 상세에 **"이 정보가 무엇이고 무엇이 아닌지"를 설명하는 도움말 카피(help copy) UI**(예: 면책 톤의 짧은 안내·접이식 설명·"참고정보이며 복약지시 아님" 명료화)를 구현한다. **`src/js/*` 앱 코드는 변경하되 relation/export/full index/DATA_URL 등 보호 데이터는 무변경.** 카피는 **"허가사항 기반 참고정보"까지만** — "승인/검수 완료/안전 보장/관계 없음 보장" 같은 **과신 문구 금지**, name_only 화면에는 **의학정보 부착 0**.
>
> **재개 트리거:** "메디스택 도움말 카피 UI" / "relation help copy 구현".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md`(§4 렌더 규칙) · 이 문서 §0 + §7.
2. 현 렌더/가드: `src/js/render.js`(`renderDetail()` — 이미 `source.type`·`원문 보기↗`·`<details>출처 상세</details>`·`disclaimers.common` 노출 중) · `src/js/guards.js`(렌더 규칙) · `src/js/states.js` · `src/js/app.js`(라우터/모드 분기) · `src/js/data.js`(`DATA_URL`·가드).
3. 검증: `scripts/smoke_disclaimer_render.py`(면책·출처 노출 = S4) · `scripts/smoke_search_regression_v1_0.py`(name_only 케이스 A~H).
4. 톤 근거: `docs/MediStack_source_attribution_design.md`(출처 표시 원리·면책 톤) · `docs/MediStack_relation_source_ui_design_v1_2.md`(있으면, 과신 차단·강등 UX) — **수치는 작업12 기준선 사용**(문서 내 옛 수치 무시).

**허용 범위(`src` 변경·보호 데이터 무변경):**
- relation_card 상세에 도움말 카피 UI 추가/정련: 면책 톤 짧은 안내 + 접이식("이 정보는 무엇인가/무엇이 아닌가") + "허가사항 기반 참고정보·복약지시 아님" 명료화. 기존 면책/출처/렌더 가드 **승계**(disclaimers.common 없으면 상세 차단 = fail-safe 유지).
- 카피는 데이터에 박지 않고 **앱 코드(문자열 상수)**로(append-only 필드가 정 필요하면 의미 불변 append 만, 단 보호 export 데이터 무변경 원칙 우선 → 가능한 한 src 문자열로).
- 변경 후 `smoke_disclaimer_render.py` + `smoke_search_regression_v1_0.py`(영향 케이스) 갱신/실행 + 수동 브라우저 QA(`python3 -m http.server 8000`) 기록.

**금지:**
- ❌ **과신 문구 금지**: "식약처 승인/약사 검수 완료/법적 문제없음/안전 보장/관계 없음 보장/걱정 없음/복용하세요/피하세요/드세요". 면책 톤·"참고정보" 한도.
- ❌ **name_only 화면에 의학정보·도움말로 위장한 상호작용/영양소/복용지시 부착 금지**(name_only 는 순수 검색 보조·비클릭 유지).
- ❌ 도움말이 **새 의학 판단·점수·위험등급·복용량·제품/영양제 추천**을 생성하는 것 · 개인정보/건강정보 입력 경로 추가.
- ❌ relation/export/full index/alias/DATA_URL 변경 · published/clinical flip · `status/published/clinical_reviewed` 필드 읽기/출력 · 자동 deploy/tag/commit.

**성공기준(검증가능):**
- 도움말 카피 = 면책 톤·"허가사항 기반 참고정보"까지 · 과신 문구 0 · 복용/안전 단정 0.
- name_only 의학정보 미부착(불변) · 기존 면책(disclaimers.common)·출처 노출 유지(smoke S4 PASS).
- `smoke_disclaimer_render.py` + `smoke_search_regression_v1_0.py`(A~H) PASS · 수동 브라우저 QA 통과.
- 보호 데이터(relation/export/full index/alias/DATA_URL) `git status` clean · 기준선 숫자(relations 55 등) 불변 · `src/js/*`만 변경.

**STOP 조건:**
- 카피 "개선"이 과신·복용지시·"안전 보장"으로 번지면 즉시 멈추고 면책 톤으로 환원.
- 도움말을 name_only 에 의학정보로 붙이려는 시점에 멈춘다(미부착 유지).
- 새 의학 판단/점수/추천을 만들려 하면 멈추고 "설명 카피까지만" 으로 환원.

**산출물:** 도움말 카피 UI 구현(`src/js/*` + 스타일/문구) + 구현 로그(과신 문구 0 확인·name_only 미부착·smoke/QA 결과). relation/export 등 보호 데이터 무변경.

---

## F2. 내 약 목록(saved stack) MVP 구현 — 로컬·무서버·민감정보 0

> **목표:** 확정 설계를 따라 **"내 약 목록(saved stack)" MVP 를 실제 구현**한다. **로컬 전용**(localStorage/IndexedDB) · **서버·계정·백엔드·동기화·외부 전송 0** · **개인정보/건강정보 수집 0**(약명/품목 식별자만) · **복용지시·해석 0**(자가 기록 보관까지만). 정적 SPA 범위 안에서만. (이 블록의 §B "내 약 목록 MVP" 와 **동일 목표**이며 F2 는 작업12 기준선 기준 재게시본 — 둘 중 하나만 실행.)
>
> **재개 트리거:** "메디스택 내 약 목록 구현" / "saved stack MVP".

**먼저 읽을 문서(순서대로):**
1. `CLAUDE.md`(§4 렌더 규칙) · 이 문서 §0 + §7.
2. **설계 권위본:** `docs/MediStack_saved_stack_mvp_design_v1_2.md` — 데이터 모델·저장소·Free 한도·"내 목록" 화면 스펙·면책/개인정보 문구. **없으면 구현 착수 금지**(설계 선행 요청).
3. 렌더/가드: `src/js/render.js`·`src/js/guards.js`·`src/js/app.js`(라우터)·`src/js/states.js`·`src/js/data.js`. 검증: `scripts/smoke_disclaimer_render.py`·`scripts/smoke_search_regression_v1_0.py`.
4. (정합) Free 한도 플래그는 §C(Free/Plus 플래그) 산출물이 있으면 그 플래그로 게이트, 없으면 단순 상수+TODO.

**허용 범위(`src` 변경·local-only·보호 데이터 무변경):**
- **클라이언트 로컬 저장 구현만**: localStorage/IndexedDB 보관. 저장 항목 = item_seq/품목명/추가일/(선택)자유 메모 상한. 추가/삭제/비우기/로컬 내보내기 UI. "내 목록" 라우트/화면.
- 면책·"자가 기록 보관(복약지시 아님)"·"개인정보 비수집" 고지 + 기존 면책/출처/렌더 가드 승계. name_only 저장 항목은 **의학정보 미부착**.
- 변경 후 `smoke_disclaimer_render.py` + `smoke_search_regression_v1_0.py`(영향 케이스) + 수동 브라우저 QA(네트워크 탭으로 요청 0 확인) 기록.

**금지:**
- ❌ **서버·계정·DB·동기화·외부 전송·분석/트래킹/원격 로그 일체 금지**(local-only). Supabase 배선 0(D2 는 설계만).
- ❌ **증상·질환·복용이력·연락처·생년 등 개인정보/건강정보 입력 경로 0**(약명/품목 식별자/추가일/메모만). 입력 필드 최소화.
- ❌ 저장 약을 **해석·지시**(이 약엔 X 보충/같이 드시면 안 됨)·새 점수/위험등급 생성 · name_only 저장 항목 의학정보 부착 · 제품/구매/영양제 추천 · 결제 구현.
- ❌ relation/export/full index/alias/DATA_URL 변경 · published/clinical flip · "식약처 승인/약사 검수 완료/법적 문제없음" 표현 · 자동 deploy/tag/commit.

**성공기준(검증가능):**
- 저장 = **클라이언트 로컬 한정**(네트워크 요청 0 — 브라우저 네트워크 탭 확인) · 계정/서버/백엔드 0.
- 저장 데이터에 개인정보·건강정보 필드 0(약명/품목 식별자/추가일/메모만) · name_only 항목 의학정보 미부착.
- "내 목록"은 복용지시·해석 없이 자가 기록 보관임이 화면 문구로 명시 · 공통 면책 노출 유지(smoke PASS).
- `smoke_disclaimer_render.py` + `smoke_search_regression_v1_0.py`(영향) PASS · 수동 QA 통과 · 보호 데이터 `git status` clean · 기준선 숫자(relations 55 등) 불변 · `src/js/*`만 변경.

**STOP 조건:**
- 설계 문서(`..._saved_stack_mvp_design_v1_2.md`)가 없으면 구현 착수 금지 → 설계 선행 요청.
- 구현이 서버/계정/동기화를 요구하기 시작하면 그 부분은 **후속 라운드(D2 옵트인)**로 분리, MVP 는 local-only 유지.
- 입력 필드가 건강정보 성격이면 즉시 제거(약명/식별자만) · 저장 약 해석·지시로 번지면 "보관/표시까지만" 으로 환원.

**산출물:** "내 약 목록" MVP 구현(`src/js/*` + 화면/스타일) + 구현 로그(저장 모델·local-only(요청 0) 확인·QA 결과). relation/export 등 보호 데이터 무변경(`git status` 보호파일 clean).

---

> **작업12 6종 공통 재게시(불변):** A2(source 확인·분류) → B2(source_confirmed→draft) → C2(PM 승인 draft→live·CI 전수 PASS·deploy 별도) 는 **게이트를 건너뛰지 않는다**. D2 는 Supabase **설계만**(실자원 0), E2·F2 는 `src` 만 변경(보호 데이터 clean). 모든 6종: `source_confirmed` 자동승격 금지 · 후보 do_not_implement_yet=true · 고위험(와파린×K·항응고/항혈소판×K·항암·임신/소아/정신건강)=hold·채택금지 · published/clinical false 봉인 · DATA_URL v0.2 불변 · 추천/구매/복용지시/제품 어휘 0 · "식약처 승인/약사 검수 완료/법적 문제없음" 표현 0 · 자동 deploy/tag/commit 금지(PM 명시 지시에서만).
