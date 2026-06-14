# MediStack — source-policy 선택지 비교 (Option A/B/C) + 본 라운드 사례 연결 (v1.2)

> 작성일: 2026-06-14. **정책/설계 문서 전용 — 데이터/코드/relation/게이트 판정 한 줄도 변경하지 않는다.** 본 라운드 **live 승격 0**, `published=false`·`clinical_reviewed=false` 유지. 본 문서는 source 천장 정책의 선택지(A/B/C)를 자기완결적으로 비교하고, 현재 기본 = **Option A** 임을 명문화하며, 이번 라운드 게이트 사례(레보도파×철·플루오르화나트륨×칼슘 등)를 옵션 트랙에 연결한다.
>
> 선행/짝 문서:
> - `CLAUDE.md` §1(절대 불변)·§6(clinical reviewer 트랙)
> - `MediStack_source_policy_literature_hold_v1_2.md` (literature_only hold 정책 — 본 문서의 모(母)정책)
> - `MediStack_relation_factory_design_v1_2.md` §4(source-policy 게이트)
> - ground truth ledger(읽기전용 인용): `data/review/source_confirm_gate_v1_2.json`, `data/review/needs_review_itemseq_recheck_v1_2.csv`
>
> 정체성(불변): 식약처 허가사항 기반 약-영양소 **참고정보 베타**. 진단·처방·복약지시·제품·구매·제휴 아님.

---

## 0. 한 줄 요약

MediStack 의 source 천장은 **식약처 허가사항(nedrug `getItemDetail`) 원문 직접근거**다. 이차문헌(임상 가이드라인·메타분석·교과서)만이 근거인 후보는 현재 정책상 **draft/live 승격하지 않고 hold** 한다. 본 문서는 향후 선택지 **Option A(현행)/B/C** 를 채택이 아닌 **비교 목적**으로 정리하고, 이번 라운드에서 게이트가 분리한 사례(레보도파×철·플루오르화나트륨×칼슘)를 어느 옵션의 후보로 보관하는지 기록한다. **본 문서는 어떤 옵션도 채택·실행을 지시하지 않는다.** Option B/C 전환은 PM(및 C의 경우 clinical reviewer) 별도 결정 사안이다.

---

## 1. 현재 기본 정책 = Option A (명문화)

- **Option A = 허가사항 직접근거만 허용.** source_confirmed 는 nedrug 허가사항 원문에 해당 영양소 상호작용/이상반응 동거어가 **직접** 있을 때만 부여된다.
- **literature_only 항목은 live/draft 어느 쪽으로도 승격 금지.** 이차문헌상 잘 알려진 약리 상호작용이라도, 국내 허가사항 직접근거가 없으면 게이트를 통과하지 못한다(`DEFAULT DENY · fail-closed`).
- 본 라운드 게이트(`source_confirm_gate_v1_2.json`) 적용 결과(읽기전용 인용):
  - nutrient_track: `reject 3 · needs_review 2`, **nutrient_source_confirmed = 0**.
  - antacid_track: `antacid_draft_confirmed 2 · reject 3 · needs_review 1` (제산제 트랙은 영양소 relation 이 아니며 동일하게 **live 금지**).
  - **live_promotions = 0** (meta·summary 양쪽 명시).
- 즉 **본 라운드는 정책 변경 0 · Option A 그대로 적용**. 본 문서는 그 위에서 향후 선택지를 비교·보관할 뿐이다.

---

## 2. 향후 선택지 비교 (채택 아님 · 옵션 대조)

> 아래 표/설명은 **의사결정 보조용 비교**다. 어느 옵션도 본 라운드에서 채택·실행하지 않는다.

| Option | 정의 | source 천장 | coverage 영향 | 정체성/리스크 | 게이트 변화 | 상태 |
|---|---|---|---|---|---|---|
| **A (현행)** | 허가사항 **직접근거만** 허용. 이차문헌만이면 hold | 허가사항 원문 | 보수적(작음) | 정체성 유지·리스크 최저 | 현재 fail-closed 4조건 유지 | ✅ **현재 적용** |
| **B** | 공신력 있는 **이차문헌까지 draft 만** 허용(**live 아님**) | 허가사항 + 화이트리스트 이차문헌 | 큼(레보도파×철·스타틴×CoQ10 등 후보 유입) | 정체성 변경 압력("허가사항 기반"→"근거 기반")·출처 등급 필요 | `evidence_tier` 분기 + draft-only 캡 신설 | 미채택(PM 결정) |
| **C** | 허가사항은 그대로, 이차문헌은 **약사/임상 검수 후** 별도 `reviewed_reference` 트랙으로만 표기 | 허가사항(직접) ∥ 검수된 참고문헌(분리 트랙) | 중간(검수 병목 만큼) | 정체성 보존 + 확장 여지·reviewer 확보 전제 | reviewed 트랙 별도 게이트(`reviewed_by`/`reviewed_at`) | 미채택(PM·reviewer 결정) |

### Option A — 허가사항 직접근거만 (현행)

- **정의:** source_confirmed = nedrug 허가사항 원문 직접 동거어 + 단일 경구 itemSeq + 부정문구 부재 + 계열 일반화 아님(4조건). 이차문헌만이면 hold.
- **장점:** ① 단일 공식 출처(nedrug)로 **결정론적 재검증** 가능. ② "식약처 허가사항 기반" 정체성·사용자 신뢰·법적 노출이 가장 안정적. ③ 과다해석 위험 최저.
- **단점/한계:** coverage 가 보수적. 잘 알려진 약리 상호작용이라도 허가사항에 동거어가 없으면 노출 불가(레보도파×철 등 후보 누락).
- **위험:** 낮음. 현행 안전선과 정합.
- **게이트:** 변화 없음(현재 4조건 유지).
- **예시(본 라운드):** 세푸록심·세프카펜피복실·세프디토렌피복실 × 철분 = 허가사항 동거어 미기재로 `reject`(직접근거 부재). 제산제 트랙에서 펙소페나딘·이트라코나졸 = 직접 directive 동거어 + 부정문구 부재로 `antacid_draft_confirmed`(draft 까지만, live 금지) — Option A 안에서도 직접근거가 있으면 draft 가능함을 보여주는 대조 사례.

### Option B — 공신력 이차문헌까지 draft 만 (live 아님)

- **정의:** 허용 화이트리스트(예: 식약처 의약품안전사용정보(DUR)·AHFS·동료심사 메타분석 등)에 근거가 있으면 **draft 단계까지만** 생성. live 승격은 여전히 금지.
- **장점:** ① coverage 확장(레보도파×철·스타틴×CoQ10·H2/PPI×B12 등 후보 유입). ② live 가 아니므로 사용자 직접 노출은 보류 — 내부 검토/우선순위용 자료 확보.
- **단점:** ① 출처 등급·인용 검증 체계가 새로 필요. ② draft 라도 "허가사항 기반" 카피와 충돌 → 정체성 문구 정정 압력.
- **위험:** 중. 천장이 허가사항 밖으로 확장되며, draft 가 실수로 노출되면 정체성·법적 노출 증가.
- **게이트 변화:** `evidence_tier`(허가사항=primary / 화이트리스트 문헌=secondary) 필드 분기 + secondary 는 `draft_eligible=true, live_integration_forbidden=true` 로 **하드 캡**. 화이트리스트 외 출처는 여전히 DENY.
- **선결 조건:** ① 허용 이차문헌 출처 화이트리스트 정의 ② `evidence_tier` 스키마 ③ 인용 검증 절차 ④ 사용자 카피 "허가사항 기반" 문구 정정 ⑤ 참고정보 책임 범위 법적 검토.
- **예시 후보:** 레보도파×철(아래 §3), 스타틴×CoQ10, H2×B12.

### Option C — 검수 후 reviewed_reference 별도 트랙

- **정의:** 허가사항 직접근거 트랙은 그대로 두고, 이차문헌 근거는 **약사/임상 reviewer 검수를 통과한 것만** 별도 `reviewed_reference` 트랙에 분리 표기. UI 에서 "허가사항" vs "검수된 참고문헌" 출처 구분.
- **장점:** ① "허가사항 기반" 정체성 보존(직접 트랙 불변) + 확장 여지. ② 검수 게이트로 과다해석 차단. ③ 출처 구분 표기로 사용자에게 근거 등급 투명.
- **단점:** ① reviewer 확보가 전제(병목). ② 두 트랙 UI/스키마 분리 비용. ③ `clinical_reviewed` 천장 정책과 정합 필요.
- **위험:** 중(reviewer 미확보 시 진행 불가) ~ 낮음(검수 통과분만 노출). 검수 품질이 위험을 좌우.
- **게이트 변화:** `reviewed_reference` 트랙 별도 게이트 — `reviewed_by`/`reviewed_at`/`source_tier` 필드, reviewer 서명 없으면 노출 차단(fail-closed). 직접 트랙 게이트는 불변.
- **선결 조건:** ① `reviewed_reference` 스키마(reviewed_by/reviewed_at/source_tier) ② clinical reviewer 확보 ③ 허가사항 트랙과 UI 분리 표기 ④ `published`/`clinical_reviewed` 천장 정책과 정합(CLAUDE.md §6).
- **예시 후보:** 레보도파×철(reviewer 판단 사안으로 적합), 스타틴×CoQ10, H2×B12 — 모두 검수 통과 시에만.

---

## 3. 본 라운드 사례 연결 (게이트 ledger 인용 → 옵션 트랙 보관)

> 아래 verdict 는 `source_confirm_gate_v1_2.json`·`needs_review_itemseq_recheck_v1_2.csv` 의 **읽기전용 인용**이다. 판정을 새로 하거나 바꾸지 않는다. "옵션 후보 보관"은 채택이 아니라 향후 옵션 결정 시 어느 트랙에서 다뤄질지를 분류해 두는 메모다.

### 3.1 레보도파 × 철분 (CQ-9002)

- **게이트 verdict(인용):** `needs_review` — `DENY(fail-closed): 국내 단일 경구 완제품목 미확보(no_domestic_single_oral_product) — itemSeq 직접 지정 재확인 필요.`
- **CSV 내부메모(인용):** "신경/뇌; needs_review 재확인 — 국내 단일 경구 완제(복합제 레보도파/카르비도파 제외) itemSeq 직접 재검색."
- **상호작용 성격:** 철과 레보도파의 흡수 상호작용은 이차문헌상 잘 알려진 약리 상호작용이다. 다만 국내 유통은 대부분 **복합제(레보도파/카르비도파 등)** 이고, **단일 경구 완제·허가사항 직접근거가 본 라운드에서 미확보**다.
- **옵션 트랙 분류:** Option A 에서는 **제외**(직접근거·단일 경구 완제 부재로 게이트 미통과, 현재 `needs_review` 상태 유지). **Option B/C 후보로 보관** — B 라면 화이트리스트 이차문헌 근거로 draft, C 라면 reviewer 검수 후 reviewed_reference 트랙. 단, 어느 경우든 본 라운드는 채택/승격 0.
- **재확인 경로(현행 게이트 내):** itemSeq 직접 지정 재검색으로 국내 단일 경구 완제 + 허가사항 직접 동거어가 확인되면 Option A 안에서도 재판정 가능(현재는 미확보 → hold).

### 3.2 플루오르화나트륨 × 칼슘 (CQ-9001)

- **게이트 verdict(인용):** `needs_review` — `DENY(fail-closed): 국내 단일 경구 완제품목 미확보(no_domestic_single_oral_product) — itemSeq 직접 지정 재확인 필요.`
- **CSV 내부메모(인용):** "기타; needs_review 재확인 — 국내 단일 경구 완제(치과용/외용 제외) itemSeq 직접 재검색."
- **상호작용 성격:** 국내 플루오르화나트륨 제품은 대부분 **치과용/외용**(도포·구강용 등)이라 경구 영양소 상호작용 트랙의 단일 경구 완제 요건과 맞지 않는다.
- **옵션 트랙 분류:** **제외** — 치과/외용 위주로 경구 영양소 상호작용 대상 자체가 성립 어려움. Option B/C 로도 우선순위 낮음(제형 미스매치). 현재 `needs_review` 상태 유지.

### 3.3 제산제 트랙 (참고 — 영양소 relation 아님)

- 제산제 트랙(`antacid_track`)은 약-**영양소** relation 이 아니라 약-제산제(Al/Mg) 병용 directive 트랙이다. 본 옵션(A/B/C) 비교의 대상이 아니나, 같은 라운드 게이트에 동거하므로 참고로 기록한다.
- 인용: 펙소페나딘(AT-01)·이트라코나졸(AT-05) = `antacid_draft_confirmed`(허가사항 직접 directive 동거어 + 부정문구 부재 → **draft 까지만, live 금지**). 아지트로마이신(AT-02)·플루코나졸(AT-04) = 동거어는 있으나 **부정문구("흡수장애 일어나지 않음/영향 없음")** 동반 → `reject`. 클래리트로마이신(AT-03) = directive 동거어 미확인 → `reject`. 케토코나졸(AT-06) = 단일 경구 itemSeq 미확보 → `needs_review`.
- 시사점: 직접근거가 있어도 **부정문구가 동반되면 reject** 한다는 점은 Option A(및 B/C 모두)에 공통되는 과다해석 방지 원칙이다.

---

## 4. 계속 hold (옵션 전환 전까지 유지)

> 아래는 `MediStack_source_policy_literature_hold_v1_2.md` 의 hold 대상을 본 옵션 문서 관점에서 재확인한 것이다(신규 판정 아님).

| 후보 | 관계(문헌상) | 허가사항(MFDS) 상태 | 계속 hold 이유 |
|---|---|---|---|
| **스타틴 × CoQ10** | 스타틴이 메발론산 경로로 CoQ10 합성 감소(문헌) | 국내 허가사항에 CoQ10 동거어 **미기재** | ① 허가사항 직접근거 부재(Option A 미통과). ② CoQ10 = 결정론적 detector 부재 영양소(5영양소 밖) → 현재 트랙에서 source check 자체 불가. coverage 레버가 커도 게이트 못 넘음. Option B/C 후보로만 보관. |
| **H2차단제 × B12** | 위산 저하 → B12 흡수 감소(문헌) | 허가사항 B12 동거어 **미기재**(파모티딘·니자티딘·라푸티딘 확인) | ① 허가사항 직접근거 부재(Option A 미통과). ② B12 = detector 부재 영양소 → source check 불가. Option B/C 후보로만 보관. |

- **detector 부재 영양소(B12·엽산·CoQ10·비타민D·비타민C·나트륨 등)** 는 literature_only 와 별개로도 **현재 트랙에서 결정론적 source check 가 불가**하다. 따라서 Option B/C 채택과 무관하게, 이들 영양소를 다루려면 detector 확장이 선행되어야 한다(이는 source 천장 옵션과 묶인 별도 과제).
- 본 라운드에서 이 hold 들은 **변경 없음** — 승격 0, 정책 변경 0.

---

## 5. 약사/임상 참여의 성격 (추천 권한 아님 · 제품/구매/제휴와 비연결)

- 약사 또는 임상 reviewer 의 참여(특히 Option C)는 **추천·권유 권한이 아니다.** 역할은 다음으로 한정한다:
  - **문구 검수:** 사용자 노출 카피가 참고정보 톤·안전선을 지키는지 확인(복용 지시·결핍 단정·근거 등급 과장 차단).
  - **품질 자문:** 이차문헌 근거의 출처 등급·인용 정확성·과다해석 여부 판단.
  - **상담 신뢰용:** reviewed_reference 트랙의 신뢰도 확보(검수 통과분만 분리 표기).
- **명시적 비연결:** reviewer 참여는 **제품 추천·구매 유도·제휴·할인과 일절 연결되지 않는다.** reviewer 가 특정 영양제/제품을 권하거나, reviewed 트랙이 구매 동선과 묶이는 것은 금지(CLAUDE.md §1 제품/제휴 금지와 정합).
- reviewer 가 어떤 relation 을 "검수 통과" 시켜도 그것은 **참고정보의 출처 신뢰도**를 뜻할 뿐, 사용자에게 "이 영양제를 드세요/구매하세요"가 아니다.

---

## 6. 본 문서의 경계 (무엇을 하지 않는가)

- Option B/C 를 **채택하지 않는다.** 실행·전환을 지시하지 않는다. 비교·보관 메모일 뿐이다.
- 게이트 verdict(`source_confirm_gate_v1_2.json`)·recheck(CSV)를 **재판정하지 않는다.** 읽기전용 인용만.
- live 승격 **0**. `published=false`·`clinical_reviewed=false` 유지. draft 후보(제산제 2건)도 live 금지.
- 제품/구매/제휴/추천 UI·문구 **0**. 칼륨 보충 권유·결핍 단정 **금지**.
- 데이터/코드/relation/보호 파일 **불변**.

> **안전 원칙(불변):** 허가사항에 없으면 노출 금지(Option A) / 이차문헌 근거는 옵션 결정 전 hold / 부정문구 동반이면 직접근거라도 reject / "허가사항 기반" 정체성은 옵션 변경 없이는 불변 / reviewer 참여 = 검수·자문이지 추천/제품/제휴 아님 / 사용자 카피에 근거 등급·결핍 과장 금지.
