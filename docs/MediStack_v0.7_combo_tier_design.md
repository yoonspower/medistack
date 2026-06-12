# MediStack v0.7 — 복합제 tier UX 고지 + combo validator 설계 문서 (B1 · 설계만, 구현 전)

작성일: **2026-06-12** / 상태: **설계만 — alias/data/code/validator 무변경. 구현은 본 문서 승인 + 후속 구현 게이트 전까지 금지.** / 상위: `MediStack_v0.7_combo_tier_policy.md`(정책 검토), `MediStack_v0.6_handoff.md`

> **PM 판정(2026-06-12)**: v0.7 은 **B1 방향**. **HCTZ 복합제 제외**, 대상 = **메트포르민·알렌드론산·오메프라졸 복합제 + brand_core 14**. 본 문서는 ① **복합제 UX 고지 문구·렌더 설계**와 ② **combo validator 설계**를 정의한다. **alias/data/code 무변경** — 이 문서는 설계 청사진이며 아무것도 구현하지 않는다.

---

## 1. B1 확정 스코프 (2026-06-12 실측)
| 트랙 | 대상 | 건수 | 성분 구조 | 고지 필요 |
|---|---|---|---|---|
| 복합제(메트포르민) | 메트포르민 + 당뇨약 | 76 | 2성분, relation 보유 1개 | **필요** |
| 복합제(알렌드론산) | 알렌드론산 + 비타민D | 28 | 2성분, relation 보유 1개 | **필요** |
| 복합제(오메프라졸) | 오메프라졸 + 제산성분 | 6 | 2성분, relation 보유 1개 | **필요** |
| brand_core | 단일성분 브랜드 어간 | 14(고유 itemSeq 10) | **단일성분** | 불요(완전정보) |
| **합계 후보** | | **124** | | |
- **제외**: HCTZ 복합제 112(칼륨 오도 위험·PM 결정), 에스오메프라졸(영구 차단).
- **🔑 B1 스코프는 칼륨 무관**: 메트포르민×B12 · 알렌드론산×칼슘 · 오메프라졸×B12/마그네슘 — `potassium_safety_card` 행 없음. HCTZ 제외로 칼륨 안전 이슈 완전 회피.
- **500 산수**: 382 + (확정 복합제 ≤110) + (brand_core ≤14) → 목표 500~506. deferred 110 은 collect-level 미확정 → confirm 후 실수율 적용.

### 1-1. 대상 복합제 파트너 성분 (고지·schema 근거)
- **메트포르민(76)**: 글리메피리드29 · 시타글립틴24 · 빌다글립틴4 · 리나글립틴8 · 글리벤클라미드4 · 아나글립틴3 · 엠파글리플로진3 · 글리클라지드1. (전부 혈당강하제, relation 미보유.)
- **알렌드론산(28)**: 콜레칼시페롤/농축콜레칼시페롤(비타민D3) 27 · 칼시트리올1. (비타민D — 칼슘 흡수 맥락과 정합하나 자체 relation 없음.)
- **오메프라졸(6)**: 탄산수소나트륨4 · 침강탄산칼슘2. (제산 성분.)
- **공통**: 어떤 복합제도 **relation 보유 성분을 2개 이상 갖지 않음**(전수 1개) → 매핑 모호성 0, 다중 canonical 불필요.

### 1-2. brand_core 14 (단일성분, 고지 불요)
| 표면형 | canonical | itemSeq |
|---|---|---|
| 바이포민서방정 | 메트포르민 | 200709701 |
| 리목스정 | 목시플록사신 | 201402438 |
| 모록사신 / 모록사신정 | 목시플록사신 | 201309618 |
| 미노씬캡슐 | 미노사이클린 | 198501028 |
| 미노젠 / 미노젠캡슐 | 미노사이클린 | 202500078 |
| 시프로민정 | 시프로플록사신 | 199901094 |
| 라이트알렌드론 / 라이트알렌드론정 | 알렌드론산 | 201902246 |
| 제일타리비드 | 오플록사신 | 198600307 |
| 세토람 / 세토람정 | 토라세미드 | 200600084 |
| 토렘정 | 토라세미드 | 200611522 |
- 전부 **이미 검증된 단일성분 제품의 dose/제형 제거 브랜드 어간** — itemSeq 가 verified_item_seqs 에 이미 존재. **위험 = 표면형(어간) 과매칭뿐**(itemSeq 검증 위험 없음). **복합제 고지 불요**(단일성분 = 완전정보, 기존 "관련 정보로 연결" 안내로 충분).

---

## 2. Part A — 복합제 UX 고지 설계

### 2-1. 왜 고지가 필요한가
- 복합제는 성분 2~3개인데 alias 는 1개 canonical 로만 연결 → **그 1개 성분의 약-영양소 정보만** 노출(부분정보).
- 부분정보는 거짓이 아니나(그 성분은 실제 함유), **사용자가 "제품 전체 정보"로 오인하면 안전 원칙("오도 금지") 위반.** → **명시적 고지로 부분정보임을 알려 정직성 확보.**

### 2-2. 고지 문구 (초안 — PM 확정 대상)
- **검색 결과 연결 안내(복합제 변형)** — 기존 "관련 정보로 연결됩니다" 를 복합제일 때 교체:
  > **'{검색어}'은(는) 복합제입니다 — {basis성분} 성분 기준 정보로 연결됩니다.**
- **상세 카드 복합제 배너(전체 고지)** — relation 카드 상단:
  > **⚠️ 이 제품은 둘 이상의 성분을 가진 복합제입니다.**
  > 아래 약-영양소 참고 정보는 **{basis성분}** 성분을 기준으로 하며, 함께 포함된 다른 성분에 대한 정보는 포함하지 않습니다. 전체 성분 정보는 의약품 허가사항(첨부문서)을 확인하세요.
- **변수**: `{basis성분}` = canonical(메트포르민/알렌드론산/오메프라졸). `{검색어}` = 사용자 입력. (선택) 파트너 성분 노출 시 `{partners}` 추가 — 단 원료 염/수화물 접미사가 길어 **기본은 미표기**, 정제 라벨 확보 시에만.
- **배지**: 결과·상세에 `복합제` 배지(텍스트 라벨, 색강조). 의료 단정·복용지시·제품추천 표현 금지.

### 2-3. 렌더 배치 (설계 — 구현 아님)
- alias 매칭 결과가 `is_combination` 이면: ① 결과 줄에 `복합제` 배지 + 연결 안내 복합제 변형, ② 상세 카드 최상단에 복합제 배너(2-2). `is_combination` 아니면 기존 동작 100% 유지.
- **brand_core 는 단일성분 → 기존 안내 그대로, 복합제 배지/배너 없음.**
- fail-safe: `is_combination` 인데 basis성분 미상이면 **상세 렌더 차단**(안전쪽).

### 2-4. 데이터 스키마 (append-only 설계 — 지금 적용 안 함)
- product_alias 항목에 **append-only 필드 3종 추가(PM 확정 2026-06-12)**: `is_combination: true` · `combination_basis_ingredient`(= canonical) · `combination_notice_required: true`. 파트너 성분 **미표기** 결정 → `combo_partner_ingredients` 필드 없음.
- 기존 단일성분/brand_core alias 는 필드 부재 = `is_combination` 미존재 → 기존 동작 불변(하위호환).
- ⚠️ **이 스키마는 앱 `render`/`guards` 가 새 필드를 읽어야 하므로 `앱 UI 금지` 불변규칙 완화를 수반** — 정책 문서 §4 에서 식별, PM 이 §2-2 고지 추가를 승인함으로써 본 완화에 동의한 것으로 간주(구현 게이트에서 재확인).

---

## 3. Part B — combo validator 설계

### 3-1. 복합제 수용 규칙 (CMB) — 신규 sub-validator
| # | 규칙 | FAIL 조건 |
|---|---|---|
| CMB-1 | `is_combination === true` AND `ingr_name` 에 `/` 존재 | 플래그/구성 불일치 |
| CMB-2 | 구성 성분 중 **relation 보유 성분 정확히 1개** | 0개(데이터 없음) 또는 ≥2개(다중매핑·범위밖) |
| CMB-3 | `canonical_ingredient` == 그 relation 보유 성분 1개 | 불일치 |
| CMB-4 | canonical ∈ **{메트포르민, 알렌드론산, 오메프라졸}** (B1 allowlist) | **히드로클로로티아지드·에스오메프라졸 등 → HARD FAIL** |
| CMB-5 | itemSeq getItemDetail 확정(distinct 성분 집합 검증) AND ∈ verified_item_seqs | 미검증/화이트리스트 외 |
| CMB-6 | itemSeq 전역 고유(동일 제품 중복 alias 금지) | 중복 |
| CMB-7 | alias 표면형 기존 alias 와 중복 아님 | 중복 |
| CMB-8 | `is_combination` 항목은 basis(canonical) 보유 → 고지 렌더 전제 충족 | basis 미상 |
- **CMB-2 가 핵심 안전 게이트**: "relation 성분 정확히 1개" 가 부분정보를 **결정적·정직하게** 만든다(어느 성분 기준인지 모호성 0). 실측상 대상 110 전부 통과(전수 1개).
- **CMB-4 의 HCTZ 차단은 정책이 아니라 코드 하드체크** — 검증기에서 막아 우회 불가.

### 3-2. brand_core 수용 규칙 (BC) — 별도 경량 검증
| # | 규칙 | FAIL 조건 |
|---|---|---|
| BC-1 | `candidate_type === "brand_core"`, `ingr_name` 단일(`/` 없음) | 복합제 혼입 |
| BC-2 | canonical 정확히 1개·relation 보유·∉{HCTZ, 에스오메프라졸} | 차단 성분 |
| BC-3 | itemSeq ∈ verified_item_seqs(기검증 제품 유래) + 단일성분 확정 | 미검증 |
| BC-4 | **어간 과매칭 가드**: 어간 prefix 가 **다른 canonical 제품**으로 해소되지 않음(표면형 복수→동일 itemSeq/canonical 은 허용) | 타 성분 충돌 |
| BC-5 | 복합제 고지 **불요**(단일성분=완전) — 기존 "관련 정보로 연결" 안내 적용 | — |
- brand_core 는 **복합제 아님** → §2 고지/배지 대상 아님. 위험은 어간 표면형뿐이라 BC-4 가 핵심.

### 3-3. 기존 validator 보존 (additive)
- v0.1 12/12 · v0.2 15/15 · v0.3 13/13 · TypeB 7/7 · bulk(현 152) — **회귀 0 유지**. CMB/BC 는 **추가** 검사이며 기존 항목 의미 불변.
- v0.3 #8(itemSeq ∈ relation ∪ verified whitelist) 은 복합제 itemSeq 도 verified 동반확장으로 통과(단일성분과 동일 메커니즘).
- relation 30 · DATA_URL · export · 칼륨 안전 플래그 전부 불변.

### 3-4. confirm 단계 combo 모드 설계 (구현 게이트에서)
- 현 `confirm_nedrug_item_details.py` 는 distinct 성분 ≠ 1 이면 복합제로 **거부**. → **combo 모드 추가 설계**: distinct ≥2 이면 ① 구성 성분 distinct 채록, ② 그중 relation 보유 성분 카운트, ③ **정확히 1개일 때만** approved-ready 승격(canonical=그 1개), ④ ≥2개·0개는 deferred 유지. HCTZ canonical 은 승격 차단.

---

## 4. 안전 점검 (B1 설계 기준)
- ✅ **칼륨 무관**: B1 스코프(메트·알렌·오메)에 `potassium_safety_card` 행 없음. HCTZ 제외로 칼륨 오도 위험 0.
- ✅ **부분정보 정직성**: CMB-2(정확히 1개) + §2 고지로 "어느 성분 기준인지 + 다른 성분 미포함" 명시 → 오인 방지.
- ✅ **에스오메프라졸/15행 우회 불가**: CMB-4·BC-2 하드 차단.
- ✅ **하위호환**: `is_combination` 미존재 alias 는 기존 동작 100% 유지.
- ⚠️ **앱 UI 변경 수반**: §2 고지 렌더는 `render`/스키마 변경 필요(`앱 UI 금지` 완화) — 구현 게이트에서 최소 변경·fail-safe 로.

## 5. PM 결정 (2026-06-12 확정)
1. ✅ **고지 문구 = §2-2 초안 채택**(연결 안내 + 상세 배너 + `복합제` 배지).
2. ✅ **파트너 성분 = 기본 미표기**(고지에 다른 성분명 나열 안 함).
3. ✅ **스키마 = `is_combination` + `combination_basis_ingredient` + `combination_notice_required`**(3필드, §2-4).
4. ✅ **앱 UI 고지 렌더 = 허용**(`앱 UI 금지` 완화 승인 — B1 전제 충족).
5. ✅ **brand_core 14 = 동시 진행 허용**(§1-2, BC 규칙).

## 6. 다음 단계 (본 문서 승인 후 · 구현 게이트, 여전히 단계별 PM 승인)
1. ✅ **구현 G1 완료(2026-06-12)** — combo **라이브 ship-gate** 를 v0.3 alias validator 에 추가: **#14**(is_combination 메타 정합: product 한정·basis==canonical·notice_required·orphan 금지) + **#15**(basis ∈ {메트포르민,알렌드론산,오메프라졸} → **HCTZ·에스오메프라졸 하드 차단**), `COMBO_ALLOWED_BASIS` 상수. fixture 6종 + `test_validate_v0_3_combo.py`(7/7: 정상 PASS·C1 HCTZ→#15·C2~C5→#14). 회귀 0(v0.1 12·v0.2 15·v0.3 **15**·TypeB 7·bulk 152). **data/alias/앱 무변경**(검증기·테스트만). ⚠️ **CMB-2(relation 성분 정확히 1개)·CMB-5~7·BC-1~4 는 ingr_name·getItemDetail 필요 → G3 confirm combo 모드에서 구현**(라이브 alias엔 ingr_name 없음). brand_core 라이브 검증은 기존 #1~#13 으로 커버.
2. **구현 G2 — 앱 고지 렌더 + 스키마**: `render`/`guards` 최소 변경(복합제 배지·배너·연결 안내 변형) + append-only 필드 + fail-safe. 헤드리스 smoke.
3. **구현 G3 — confirm combo 모드**: deferred 110 getItemDetail 확정(distinct·relation 1개).
4. **구현 G4 — batch 반영**: 단일성분과 동일 생성↔반영 분리 + PM 명시 승인 batch.
- 각 게이트는 별도 PM 승인. 본 문서는 **설계만**.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하거나 오도하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / 복합제는 **relation 성분 정확히 1개 + 고지** 충족 시에만 / HCTZ·에스오메프라졸·15행 우회 금지 / **이 문서는 설계만 — alias/코드/데이터 변경은 구현 게이트(PM 승인).**
