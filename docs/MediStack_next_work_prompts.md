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
