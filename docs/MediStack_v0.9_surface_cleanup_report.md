# MediStack v0.9 — alias 표면형(surface form) 정제 리포트

작성: 2026-06-12 / 트랙: v0.9 "표면형 개행 정제" (PM 자동 진행 모드 승인)
기준 상태: HEAD `030ee26` (v0.8-beta), 라이브 alias 618.

## 0. 목적 / 범위
검색 alias 의 **표면형 문자열만** 정제한다. 약학 relation·성분 매핑·alias 의미·개수
(product_aliases 580 / ingredient_aliases 38 / verified_item_seqs 542 / 13성분)·relation 30·
DATA_URL 은 **바꾸지 않는다.** 정제 전후 alias lookup 결과가 동일해야 한다.

정제 허용: alias/표시 문자열 내 개행 제거, 연속 공백 축소, 앞뒤 trim, 표면형 표시용 필드 개행 정제,
표면형 개행 금지 validator/회귀 smoke 추가.

## 1. 탐지 결과

전 JSON/CSV 데이터에서 표면형 이상(개행/CR/탭/제어/앞뒤·다중공백/제로폭/유니코드공백)을 스캔.

| 대상 | 표면형 이상 |
|---|---|
| **라이브 alias `data/medistack_v0.3_aliases.json`** (alias / item_name / canonical 전수) | **0건 (이미 clean)** |
| 후보 queue `data/candidates/bulk_alias_review_queue_v0_5.json` | 3 후보 × 2필드 = 6건 (개행) |
| 후보 queue CSV `..._v0_5.csv` | 동일 3 후보 (개행 셀 6) |
| 그 외 모든 후보/export JSON | 0건 |

라이브 데이터가 표면형 이상 0건인 이유: v0.5 파이프라인이 개행 품목명을 **수집 단계에서 이미
approved-ready 에서 제외하고 pending 으로 격리**했기 때문(아래 §2). 즉 정제가 필요한 라이브 항목은 없다.
이는 실패가 아니라 "이미 깨끗"한 상태이며, v0.9 의 산출물은 **이 상태를 영구 고정하는 validator/회귀**다.

## 2. 보류(manual review) — queue 후보 3건

| idx | candidate_alias (repr) | canonical | status | 처리 |
|---|---|---|---|---|
| 9  | `'신일모노독시엠캡슐\n(독시사이클린수화물)'` | 독시사이클린 | pending | **manual review** |
| 64 | `'레보펙신정250밀리그램\n(레보플록사신수화물)'` | 레보플록사신 | pending | **manual review** |
| 65 | `'레보펙신정500밀리그램\n(레보플록사신수화물)'` | 레보플록사신 | pending | **manual review** |

**왜 자동 정제하지 않는가 (보류 사유):**
- 이 개행은 단순 공백 위생 문제가 아니라 **구조적 파싱 아티팩트**다. nedrug searchDrug 행에서
  `품목명\n(주성분)` 형태로 품목명과 주성분이 개행으로 연결되어 캡처되었다.
- 개행을 공백/제거로 정규화하면 `"신일모노독시엠캡슐 (독시사이클린수화물)"` 같은 **잘못된 표면형**이 된다.
  올바른 표면형 `"신일모노독시엠캡슐"` 로 만들려면 **내용 재추출(주성분 괄호 절단)** 이 필요한데,
  이는 표면형 정제가 아니라 **의미 변경**이라 v0.9 범위를 벗어난다(브리프: "의미 변화 없어야 함").
- 세 후보 모두 `status=pending`, `detail_confirmed` 미설정, `approved_ready`/`incorporated` 아님 →
  **라이브 alias 에 미반영**. lookup·개수에 영향 없음. 안전하게 보류 가능.

**향후 처리(v0.9+ 또는 별도 트랙):** getItemDetail 로 정확한 단일 품목명을 원문 채록하여 재편입
(= alias **추가**이므로 PM 명시 승인 batch 필요). v0.9 표면형 트랙에서는 수행하지 않는다.

## 3. 산출물 (전부 additive — 데이터 0 diff)

1. **`scripts/validate_alias_surface_forms.py`** (신규) — 라이브 alias 표면형 위생 검증기.
   - 검사: alias(ingredient+product)·item_name(verified)·매핑키(canonical_ingredient/verified 성분키)에
     개행/CR/탭/제어/앞뒤공백/다중공백/제로폭/유니코드공백 금지. 5 checks.
   - **버전 비종속**(개수 하드코딩 없음) → 이후 버전 게이트로 재사용 가능.
   - 배경: `guards.js` 의 `norm()=NFC+trim+lower` 는 앞뒤 공백만 제거하고 내부 개행/탭/다중공백은
     보존 → 그런 표면형이 alias 에 섞이면 사실상 검색 불가. 이 게이트가 유입을 영구 차단.
2. **`scripts/smoke_alias_regression.py`** (신규) — 브랜드 alias→성분 relation 회귀 smoke.
   - 이전엔 각 phase ad-hoc /tmp .mjs 로만 돌리던 회귀를 **커밋된 테스트로 승격**. 실제 `guards.js` import.
3. **CI 배선** — `validate.yml`(PR) + `deploy.yml`(배포 게이트) 에 표면형 validator 4번째 step 추가.
   smoke 는 기존 `smoke_hctz_disclosure.py` 관례대로 **로컬 전용**(CI 미배선, node 의존).
4. **본 리포트** `docs/MediStack_v0.9_surface_cleanup_report.md`.

라이브 데이터 파일(`medistack_v0.3_aliases.json`)·queue·CSV·export·src/app 은 **무수정**.

## 4. 검증 결과 (전부 PASS)

**validator/test 스위트 12/12 PASS:**
v0.1(12/12)·v0.2(15/15)·v0.3 aliases·bulk candidates·combo AR(v0.7)·combo AR(v0.8 HCTZ)·
test combo_ar·test v0_3_combo·test v0_3_typeB·smoke HCTZ disclosure·**smoke alias regression(신규)**·
**validate surface forms(신규, 5/5)**.

**표면형 validator 음성 테스트 7/7 검출:** NEWLINE/TAB/LEAD-TRAIL/MULTISPACE/NBSP/ZEROWIDTH/canonical-newline
각각 정확한 체크번호(#2/#3/#5)로 FAIL 유도 확인.

**회귀 smoke 7/7 불변(ground-truth):**
타리비드→오플록사신 **3** · 포사맥스→알렌드론산 **1** · 토렘→토라세미드 **2** · 넥시움→**0** ·
#r15 fail-safe(id 15 미렌더) · 미카르디스플러스정40/12.5밀리그램→HCTZ combo 칼륨 반전고지 ·
단일 HCTZ 직접검색→반전고지 미오작동.

## 5. 불변 조건 확인

| 항목 | 기대 | 결과 |
|---|---|---|
| 라이브 alias md5 | 불변 | `250c25b899ab75c9f01ed7ce6c705246` (정제 전후 동일 = 데이터 0 diff) |
| alias_count | 618 | 618 (meta) |
| product_aliases | 580 | 580 |
| ingredient_aliases | 38 | 38 |
| verified_item_seqs | 542 / 13성분 | 542 / 13 |
| relation | 30 | 30 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` | 불변 |
| HCTZ combo / brand_core / deferred | 112 / 14 / 0 | 불변 |

라이브 alias JSON md5 가 정제 전후 동일하므로 개수·매핑·itemSeq·canonical·lookup 전부 trivially 불변.

## 6. 다음 단계 제안
- (표면형 트랙 계속 시) queue 3 보류 후보를 getItemDetail 단일 품목명 재채록 → 재편입 batch(PM 승인).
- v0.9 잔여 후보: D clinical reviewer 트랙(reviewer 확보 선행) / 루프이뇨제(푸로세미드·토라세미드) 복합제
  반전고지 틀 확장(v0.8 HCTZ 패턴 재사용).
- 표면형 validator 가 CI 게이트에 들어갔으므로 이후 모든 batch 는 자동으로 표면형 개행 유입 차단됨.
