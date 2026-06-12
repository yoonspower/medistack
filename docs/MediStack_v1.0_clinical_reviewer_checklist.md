# MediStack v1.0 — Clinical Reviewer Checklist (검수자 플로우)

> 자기완결 설계 문서. v1.0-A 트랙. **문서만 작성한다.**
> clinical reviewer / 검수자 플로우를 **설계·문서화**만 한다. `clinical_reviewed` / `published` 의 실제 값 전환은 **금지**(외부 검수자 확보 전까지 봉인).
> 코드·데이터·alias·queue·validator·src·relation·DATA_URL·export·tag 일절 수정하지 않는다.

---

## 0. 현재 상태 (검수 전 봉인 스냅샷)

실제 데이터(`data/medistack_v0.2_beta_export.json`)에서 확인한 봉인 상태:

| 위치 | 필드 | 현재 값 | 의미 |
|---|---|---|---|
| meta | `lifecycle_status_included` | `verified_reference` | **천장**. clinical 승격 전 한계 |
| meta | `clinical_reviewed` | `false` | 검수 완료 0 |
| meta | `published` | `false` | 공개 승격 0 |
| meta | `relation_count` | `30` | 불변 |
| relation(×30) | `requires_clinical_review` | `false` (30/30) | 임상판단 행은 데이터에 **진입하지 않음**(제외) |
| relation(×30) | `evidence_level` / `source{type,url,pointer}` | 존재 | 검수 근거 |
| relation(×30) | `reviewed_by` / `reviewed_at` / `review_log` | **부재** | 본 문서가 스키마 초안 |

해석: 현재 30건은 전부 `verified_reference` + `requires_clinical_review=false`. 임상판단이 필요한 관계(antagonism, 예: 와파린×비타민K)와 15행(에스오메프라졸×B12)은 **애초에 제외**되어 있다. 검수자 플로우는 이 30건을 대상으로 한 **승격 레일**이다.

---

## 1. clinical reviewer 역할 정의

| 항목 | 정의 |
|---|---|
| **누가** | 면허 보유 약사 또는 의사(임상). 신원·자격(면허 구분)을 기록한다. |
| **무엇을** | 각 relation을 **식약처 허가사항 원문 대비** 검수: 의학적 정확성, 표현 강도(원문 이하인지), 안전 고지 충족. |
| **권한** | relation 단위로 `verified_reference → clinical_reviewed` 승격 판정(approved/revise/reject). |
| **책임 경계** | `published` 승격은 **검수자 단독 권한이 아님** — 법무/면책/제품책임 게이트 별도(§5). |
| **독립성** | PM(별도 AI 세션)·개발 세션과 분리. 검수자가 데이터를 직접 수정하지 않고 **판정·로그만** 남긴다. |

---

## 2. 검수 대상 범위

**대상 (검수 O):**
- live 30 relation (현재 `verified_reference`).
- relation별 검수 필드: `mechanism`, `recommended_action`, `evidence_level`, `display_text_ko`, `management_ko`, `source.pointer`(원문 위치), 칼륨/복합제 고지.

**범위 밖 (검수 X, 영구):**
- **alias** — 검색 보조일 뿐 의학 정보가 아니다. 검수 대상 아님.
- **excluded_v0_1 / 15행(id15)** — 렌더 금지·재편입 금지. 검수 대상 아님.
- **제품/구매/제휴 UI** — 존재하지 않으며 추가 금지.
- **신규 relation(antagonism·임상판단 행)** — 검수자 확보 후 **별도 버전**에서만 신설 검토. 본 트랙에서 신규 생성 금지.

---

## 3. `reviewed_by` / `reviewed_at` / `review_log` 스키마 초안 (append-only, 미적용)

⚠️ **스키마 초안일 뿐이다.** 실제 필드 추가·값 설정은 reviewer 확보 후 **별도 버전 파일 + 신 validator** 로만 한다(append-only: 기존 필드 의미 불변).

relation 객체에 추가할 후보 블록:
```json
"review": {
  "clinical_reviewed": false,
  "reviewed_by": null,            // 검수자 식별(익명화 ID, 평문 신원 비저장)
  "reviewer_credential": null,    // "약사" | "의사(임상)"
  "reviewed_at": null,            // ISO8601 (예: 2026-07-01T00:00:00+09:00)
  "review_log": [                 // append-only 이력 (덮어쓰기 금지)
    {
      "reviewed_at": "2026-07-01T00:00:00+09:00",
      "reviewer": "<익명화 ID>",
      "credential": "약사",
      "verdict": "approved",          // approved | revise | reject
      "scope": ["display_text_ko", "source.pointer"],
      "source_rechecked": "nedrug itemSeq=... 원문 재확인",
      "notes": "..."
    }
  ]
}
```
meta 추가 후보: `reviewed_count`(집계), `review_schema_version`. 기존 `clinical_reviewed`/`published`는 **집계 결과**로만 true 후보가 된다(임의 설정 금지).

설계 원칙:
- **append-only** — `review_log`는 누적. 과거 판정 삭제·수정 금지(감사 추적).
- **데이터-판정 분리** — 검수자는 `review` 블록만 추가, relation 본문(`display_text_ko` 등) 직접 수정 금지. 문구 수정이 필요하면 `verdict=revise` + notes로 제안 → 별도 버전 게이트에서 반영.

---

## 4. `clinical_reviewed` 전환 기준

relation 단위 승격 조건(**전부 충족 시에만**):
1. 면허 검수자 `verdict = approved`.
2. `source.url` 식약처 원문 접근 가능 + `source.pointer` 위치 정확(재확인).
3. 표현 강도가 **원문 이하** — 단정·복용지시·위험확정 없음.
4. `requires_clinical_review=true` 행이면 제외 유지가 기본. 검수자가 명시 승인한 경우에만 예외(별도 기록).
5. `review_log`에 판정 기록 존재.

승격 단위·가역성:
- **relation 단위** 승격. `meta.clinical_reviewed=true`는 **전 relation 검수 완료** 시에만 후보(집계 결과).
- 가역적: 이후 `revise`/`reject` 발생 시 해당 relation은 `verified_reference`로 회귀.

---

## 5. `published` 전환 기준

- **선행 필수:** 전 relation `clinical_reviewed=true`.
- **추가 게이트(검수자 권한 밖):** 법무/면책 검토, 제품책임, 배포 채널 정책, 면책문구 최종 확정.
- `published=true`는 **medical claim 공개 노출**을 의미하므로 가장 보수적으로 다룬다. **본 v1.0-A 트랙 범위 밖**(별도 게이트·별도 버전).

---

## 6. 검수자가 없을 때 유지할 상태 (현 상태 = 영구 기본값)

검수자 미확보 동안 **아래를 영구 기본값으로 유지**한다(= 현재 상태):

- `lifecycle_status_included = verified_reference` (천장 유지).
- `clinical_reviewed = 0` (false).
- `published = 0` (false).
- 모든 relation `requires_clinical_review = false` 유지 / 임상판단 행 **제외 유지**.
- 앱은 `status`/`published`/`clinical_reviewed` 필드를 **읽지도 출력하지도 않는다**(render 규칙·fail-safe).
- 모든 상세에 `disclaimers.common` 표시.

즉, 검수자가 없어도 앱은 **참고 정보 베타**로서 안전하게 동작한다. 검수자 부재가 곧 결함이 아니다.

---

## 7. 약사/의료전문가 검수 체크리스트 (relation 1건당)

검수자는 relation 1건마다 아래를 확인하고 `verdict`를 기록한다:

- [ ] `source.url` 식약처(nedrug) 원문 접근 가능
- [ ] `source.pointer` 원문 위치(품목/itemSeq/섹션/확인일) 정확
- [ ] `mechanism`(absorption 등) 원문과 일치
- [ ] `recommended_action`(separation 등) 원문 이하 강도
- [ ] `evidence_level`(high/…) 근거 타당
- [ ] `display_text_ko` — 단정·복용지시·위험확정 **없음**, 원문 이하
- [ ] `management_ko` — "약사와 상담" 류 유지, 지시형 단정 아님
- [ ] 칼륨 행 — `potassium_safety_card=true` + 제품링크 없음(§10)
- [ ] 복합제 — 부분정보 고지 + (HCTZ) 칼륨 반전 고지 동반
- [ ] `disclaimers.common` 표시 확인
- [ ] `requires_clinical_review` 판정 — 임상판단 필요 시 **제외 권고**
- [ ] **verdict**: `approved` / `revise` / `reject` + `notes` + `source_rechecked`

---

## 8. relation 30 변경 금지 원칙

- 검수는 기존 **30건의 승격 판정만** 한다. relation **신규 생성·풀 확장은 본 트랙에서 금지**.
- `verdict=revise`는 **문구 수정 제안**일 뿐, 데이터 실제 수정은 **별도 버전 게이트**에서만(append-only + 신 validator + PM 승인).
- `meta.relation_count = 30` 불변 · DATA_URL 불변 · export 불변.

---

## 9. 제품 / 구매 / 제휴 UI 금지 원칙

- 검수 통과 여부와 **무관하게** 제품 링크·구매 버튼·제휴 UI·제품 예시·제품 필드 추가 **영구 금지**.
- 검수는 medical 정확성에 한정되며, **수익화 UI를 여는 근거가 되지 않는다**.

---

## 10. 칼륨 제품 링크 금지 원칙

- 칼륨 행: `product_link_allowed=false` + `potassium_safety_card=true` + 추가 고지 **유지**.
- 검수로 `clinical_reviewed=true`가 되더라도 칼륨 제품 링크는 **여전히 금지**(불변).

---

## 11. 에스오메프라졸 / 15행 재편입 금지 원칙

- **15행(에스오메프라졸×B12, id15)** — `excluded_v0_1` 유지. 검수 대상 아님. **재편입 금지**(원문에 B12 흡수장애 주의 없음).
- **에스오메프라졸 alias 금지** — id16(에스오메프라졸×Mg)은 정상 live relation이므로 **혼동 주의**(차단 대상은 id15, alias는 별개로 금지).

---

## 12. v1.0-beta 전환 전 최종 QA

v1.0-beta 안정판으로 닫기 전 확인 항목:

- **validator 전종 PASS** — CI게이트 4(v0.1 12 / v0.2 15 / v0.3 16 / surface 5) + TypeB 7 / combo 9 / combo_AR 13 / bulk 152 / combo_approved_ready 13 / smoke 회귀 7 / HCTZ.
- **불변 수치** — live HTTP 200 · alias_count 621 · product 583 · ingredient 38 · verified_item_seqs 545/13 · relation 30 · DATA_URL `./data/medistack_v0.2_beta_export.json` · export md5 `401b097a`.
- **봉인 확인** — `meta.published=false` · `meta.clinical_reviewed=false` · `lifecycle_status_included=verified_reference`.
- **앱 수동 QA** — 검색 / 고지(disclaimers) / empty / error / 칼륨 안전카드 / 복합제 부분정보·HCTZ 칼륨 반전 고지.
- **문서** — `docs/MediStack_v1.0_plan.md` + 본 checklist 존재.

---

## 13. 향후 실제 검수자 확보 시 절차

1. **검수자 자격 확인·기록** — 면허 구분(약사/의사), 익명화 ID 부여(평문 신원 비저장).
2. **스키마 적용** — §3 `review` 블록을 **별도 버전 파일**에 append-only로 추가 + 신 validator 작성(기존 30건 무손실).
3. **relation 단위 검수** — §7 체크리스트 → `review_log` append → relation별 `clinical_reviewed` 판정.
4. **meta 집계** — 전 relation `approved` 시에만 `meta.clinical_reviewed=true` 후보(임의 설정 금지).
5. **published 게이트** — 법무/면책/제품책임 검토(검수자 권한 밖)를 통과한 경우에만 별도 버전에서 검토.
6. **공통 가드** — 각 단계 **PM 명시 승인** + **validator PASS** + 무단 deploy/tag 금지 + relation/DATA_URL/export 불변.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / **clinical 검수 전 published 금지** / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전 고지) / **검수자는 판정·로그만, 데이터 직접 수정 금지**.
