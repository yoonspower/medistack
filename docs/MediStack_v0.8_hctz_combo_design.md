# MediStack v0.8 — HCTZ 복합제 개방 설계 문서 (H1 · 설계만, 구현 전)

> **트랙**: v0.8 B / **결정**: H1(조건부 개방) PM 승인 2026-06-12
> **이 문서는 설계만 한다. 코드·데이터·alias·validator·src 를 일절 수정하지 않았다.**
> 선행 정책 검토: `docs/MediStack_v0.8_hctz_safety_review.md`. 본 문서는 그 §9(후속 게이트)를 구체화한다.
> HCTZ 복합제 112 건은 여전히 **미반영**. 실제 편입은 구현 게이트(§6)에서 단계별 PM 승인 후에만.

---

## 1. H1 확정 스코프 (2026-06-12 실측)

| 구성 | 건수 | 파트너 칼륨 방향 |
|---|---|---|
| 2성분 ARB + HCTZ | 98 | ARB ↑K (상쇄) |
| 3성분 ARB + CCB + HCTZ | 14 | ARB ↑K · CCB 무관 (상쇄) |
| 칼륨보존이뇨제 + HCTZ | **0** | (역전·영구차단 대상) |
| **합계** | **112** | |

### 1-1. 대상 파트너 성분 (고지·validator 근거)
- **ARB**: 로사르탄칼륨 · 발사르탄 · 올메사르탄메독소밀 · 칸데사르탄실렉세틸 · 텔미사르탄 · 피마사르탄칼륨삼수화물
- **CCB**: 암로디핀베실산염
- canonical(basis) = **히드로클로로티아지드** 단일(전 건 relation 보유 성분 정확히 1개).
- ⚠️ 염이름 칼륨: `로사르탄칼륨`·`피마사르탄칼륨` 의 "칼륨"은 짝이온 염 — nutrient 칼륨 아님(§3 V5).
- ⚠️ 데이터 품질: `올메사탄메독소밀`(오타) 혼재 → confirm 정규화 대상.

---

## 2. Part A — 칼륨 반전 고지 설계 (HCTZ 고유, 신규)

### 2-1. 왜 추가 고지가 필요한가
- 기존 복합제 고지(v0.7 G2: 배지 + "표시 정보는 OO 성분 기준" 부분정보 배너)는 **"정보 누락"** 용이다.
- HCTZ 복합제는 한 단계 더 위험: 파트너 ARB 가 칼륨을 **반대 방향(보존)** 으로 움직인다 → 표시된 "HCTZ 칼륨 소실" 정보를 보고 자가보충 시 ARB 와 합쳐 **고칼륨혈증** 위험. 부분정보 배너만으론 **방향 반전을 알리지 못한다.**
- → 칼륨 행에 **반전 고지 1줄**을 추가한다(HCTZ 복합제 한정).

### 2-2. 고지 문구 (초안 — PM 확정 대상)
> "이 제품은 복합제입니다. 위 칼륨 관련 정보는 **히드로클로로티아지드 성분** 기준이며, 함께 든 성분(ARB 계열 등)은 칼륨을 **반대 방향(보존)**으로 움직일 수 있습니다. 칼륨은 임의로 보충하면 위험하므로, 보충·검사 여부는 반드시 의사·약사와 상담하세요."

- 안전 원칙 준수: 허가사항에 있는 사실만, **보충 지시 없음**, 제품링크 없음, 칼륨 안전카드 유지.
- 단일 HCTZ(복합제 아님)에는 **표시하지 않는다**(파트너 없음).

### 2-3. 렌더 배치 (설계 — 구현 아님)
- 위치: 칼륨 행의 기존 `potassium_safety_card` 바로 아래, 복합제 부분정보 배너와 함께.
- **트리거(렌더 시점 파생 — 신규 데이터 플래그 불요)**: `alias.is_combination === true && alias.combination_basis_ingredient === '히드로클로로티아지드' && relation.nutrient === '칼륨'`.
  - 즉 반전 고지는 **render 레이어 상수**로, alias 의 기존 `is_combination`/`basis` 플래그만 읽는다. **relation export·DATA_URL·스키마 무변경.**
- app.js 무변경 목표(v0.7 G2 와 동일하게 guards/render 한정).

### 2-4. 데이터 스키마 (변경 없음 — 권고)
- **신규 플래그 추가하지 않는다.** HCTZ combo alias 는 기존 복합제 스키마(`is_combination`, `combination_basis_ingredient='히드로클로로티아지드'`, `combination_notice_required=true`)만 사용.
- 반전 고지는 render 가 basis=HCTZ + nutrient=칼륨 조합에서 파생 → append-only 표면조차 늘리지 않음(불변선 최소 접촉).

---

## 3. Part B — validator 설계 (정책 §6 V1~V6 구체화)

기존 combo validator(CMB #1~11)·v0_3 aliases validator(#14/#15)에 **additive** 로 확장. 기존 규칙 의미 불변.

| # | 규칙 | 위치 | 비고 |
|---|---|---|---|
| **V1** | basis allowlist 에 `히드로클로로티아지드` 추가. **에스오메프라졸은 계속 하드차단** | CMB #6 · v0_3 #15 · confirm `COMBO_ALLOWED_BASIS` | 3곳 동시 일치 |
| **V2** | **칼륨보존이뇨제 파트너 하드차단**(트리암테렌·아밀로라이드·스피로노락톤·에플레레논·칸레논): `ingr_name` 에 등장 시 FAIL | CMB 신규 #12 | 현재 0건·future-proof·영구 |
| **V3** | HCTZ combo 의 칼륨 행 `potassium_safety_card=true` · `product_link_allowed=false` **보존 검증** | CMB 신규 #13 | 칼륨 제품링크금지 불변 |
| **V4** | basis=HCTZ combo 는 `combination_notice_required=true` 필수(반전 고지 게이트) | 기존 CMB #7 승계 | render §2-3 전제 |
| **V5** | **염이름 칼륨 ≠ nutrient 칼륨**: combo 로 인한 `ingredient_aliases` 의 `칼륨` 키 생성/`canonical='칼륨'` 0 검증 | v0_3 aliases validator 신규 | 로사르탄칼륨·피마사르탄칼륨 오생성 차단 |
| **V6** | (기존) is_combination=true · basis==canonical · relation 보유 성분 정확히 1개 · itemSeq 숫자·전역중복0 · 에스오메/넥시움 신호 금지 | 기존 CMB 승계 | 무변경 |

- fixture: HCTZ ARB combo 양성 ≥3 + K보존 음성 ≥1(가공) + 염이름 칼륨 음성 ≥1 + 에스오메 음성.
- confirm `--combo`: `COMBO_ALLOWED_BASIS` 에 HCTZ 추가 + **K보존 파트너 거름**(V2 와 일치) + 새 combo AR 파일(`bulk_alias_approved_ready_combo_v0_8_hctz.*`). 멱등.

---

## 4. 안전 점검 (H1 설계 기준)

| 불변/위험 | 처리 |
|---|---|
| 칼륨 제품링크금지 | V3 — `product_link_allowed=false` 보존 검증 |
| 칼륨 방향 역전(최고위험) | V2 — K보존 파트너 영구 하드차단(0건이나 봉쇄) |
| 자가보충 오인 | 반전 고지(§2-2) + 기존 management "임의보충 위험·상담" |
| 염이름 칼륨 오인 | V5 — 칼륨 alias 오생성 차단 |
| 에스오메프라졸·15행 | 계속 하드차단(V1·V6 승계) |
| relation/DATA_URL/export | **무변경**(반전 고지는 render 파생, 스키마 추가 0) |
| published/clinical | 무관(천장 verified_reference 유지) |
| 자동편입 | 금지 — §6 게이트서 PM 명시 승인 batch 만 |

---

## 5. PM 결정 (이 설계 게이트 — 확인 필요)

1. **반전 고지 문구(§2-2) 확정** 또는 수정 지시.
2. **앱 UI 완화 승인**: render 에 반전 고지 1줄 분기 추가(guards/render 한정, app.js 무변경 목표).
3. **basis allowlist 에 HCTZ 추가 승인**(V1, 3곳). 에스오메프라졸 계속 차단.
4. **K보존 파트너 영구 하드차단(V2) + 염이름 칼륨 분리(V5)** 안전선 채택.
5. **스키마 무변경(§2-4) 동의** 또는 명시적 append-only 플래그 선호 여부.

---

## 6. 다음 단계 (본 설계 승인 후 · 구현 게이트 · 여전히 단계별 PM 승인)

> v0.7 G1~G5 패턴 승계. 각 게이트 끝 validator+smoke PASS·금지파일 0diff 확인.

| 게이트 | 내용 | alias | 산출물 |
|---|---|---|---|
| **H-G1** | validator 확장(V1~V6) + fixture/음성. **alias 무변경** | 506 | combo/aliases validator·tests |
| **H-G2** | 반전 고지 render 분기(§2-3) + 문구 확정. **라이브 inert**(HCTZ combo 0 → 화면 무변경) | 506 | guards/render |
| **H-G3** | confirm `--combo` HCTZ 추가 + K보존 거름 → 112 getItemDetail distinct 확정 → combo AR 생성. **alias 미반영** | 506 | combo AR(_v0_8_hctz) |
| **H-G4** | 편입(product+verified 동반확장·큐 flip·ephemeral incorporate). **PM 명시 승인 batch** | 506→~618 (확정 수율 따라 하향) | alias JSON |
| **H-G5** | 마감(release notes + handoff + tag) | — | docs·tag |

- ⚠️ 112 는 collect 단계 미확정 후보 → H-G3 confirm 수율에 따라 최종 편입 수 하향 가능(과거 batch 전례).
- ⚠️ 편입은 H-G4 에서만, **PM 명시 승인 batch 단위**로. incorporation-aware 게이트(옵션 A) 승계.

---

> **안전 원칙(불변, 재확인)**: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / **칼륨 제품링크 금지** / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias 는 검색 보조이지 의학정보 아님 / 15행·excluded·에스오메프라졸 alias 우회 금지 / **칼륨보존이뇨제 복합제 영구 차단** / 복합제는 부분정보 + 반전 고지 동반 / 자동편입 금지 · 수동 deploy·무단 tag 금지. 이 문서는 설계이며 코드·데이터를 변경하지 않았다.
