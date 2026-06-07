# MediStack v0.1 — 카드 렌더 규격

작성 기준일: 2026-06-07 / 데이터 소스: `medistack_v0.1_beta_export.json`
동봉 목업: `MediStack_v0.1_card_mockup.html`

## 프레임 (불변)
- v0.1은 **verified_reference 기반 베타 참고정보**다. 진단·처방·복약지시 아님.
- **published / clinical_reviewed 뱃지·문구 표시 금지** (clinical reviewer 부재).
- 렌더 대상은 **relations 19건만.** `excluded_v0_1`는 **앱 렌더 금지**(내부 QA/관리용).
- 의학적 단정·복용 지시·구매 유도 카피 금지.

---

## 1. 필드 매핑표

| JSON 필드 | UI 요소 | 화면 | 렌더 규칙 |
|---|---|---|---|
| `id` | 내부 key / 딥링크 | - | 화면 미표시(라우팅용) |
| `ingredient` | 카드 제목 좌측 | 목록·상세 | 항상 표시 |
| `nutrient` | 카드 제목 우측(× 영양소) | 목록·상세 | 항상 표시 |
| `recommended_action` | 액션 라벨 칩 | 목록·상세 | separation→"복용 간격", monitoring→"상태 모니터링" |
| `mechanism` | (없음) | - | 내부값. 전문용어라 소비자 카드 미표시 |
| `evidence_level` | (없음) | - | 내부 큐레이션값. 임상등급 오해 방지 위해 v0.1 미표시 권장 |
| `display_text_ko` | 본문 설명 | 상세 | 상세 전용(목록엔 라벨만) |
| `management_ko` | 가이드 블록 | 상세 | 상담/확인 톤. 지시문으로 렌더 금지 |
| `product_link_allowed` | 제품영역 게이트 | 상세 | `=== true` 이고 제품데이터 존재 시에만 제품영역. false면 강제 차단 |
| `potassium_safety_card` | 칼륨 고지 트리거 | 상세 | `=== true`이면 potassium_notice 추가 렌더 |
| `requires_clinical_review` | (없음) | - | 전 행 false. 미표시(내부 가드) |
| `source.type` | 출처 라벨 | 상세 | "출처: 식약처 허가사항" 등 |
| `source.url` | 원문 보기 링크 | 상세 | 식약처 nedrug 링크(=출처 링크, 제품 링크 아님) |
| `source.pointer` | 출처 상세 | 상세 | 접기/펼치기 보조(옵션) |
| `meta.published` / `meta.clinical_reviewed` | (없음) | - | false 고정. 렌더 금지 가드로만 사용 |
| `disclaimers.common` | 공통 면책문구 | 상세 하단 | 모든 상세에 항상. 없으면 상세 렌더 차단(fail-safe) |
| `disclaimers.card_footer` | 짧은 푸터 | 목록/상세 보조 | 옵션 |
| `disclaimers.onboarding` | 온보딩 모달 | 최초 1회 | 옵션 |
| `disclaimers.potassium_notice` | 칼륨 고지 박스 | 상세 | potassium_safety_card=true일 때만 |
| `disclaimers.empty_state` | 빈 화면 문구 | empty | 관계 0건 시 |
| `excluded_v0_1` | (렌더 금지) | - | 앱 미노출. 내부 QA/관리용 |

---

## 2. 목록 카드 규격
- **구성:** `[성분] × [영양소]` 제목 + 액션 라벨 칩 + chevron. (옵션: card_footer 한 줄)
- **사용 필드:** ingredient, nutrient, recommended_action. display_text/management은 목록 미표시.
- **동작:** 탭 → 해당 id 상세 진입.
- **데이터 규칙:** `relations` 전체 = 정확히 19개. excluded_v0_1·15행 절대 미포함.
- **금지:** published/clinical 뱃지, evidence 뱃지(권장 미표시), 제품 썸네일/가격.

## 3. 상세 카드 규격
렌더 순서(위→아래):
1. 헤더 — `[성분] × [영양소]`
2. 액션 라벨 — 복용 간격 / 상태 모니터링
3. `display_text_ko` 본문
4. `management_ko` 가이드 블록
5. (칼륨 한정) `disclaimers.potassium_notice` 고지 박스
6. 출처 — `source.type` + "원문 보기"(`source.url`), `source.pointer` 접기(옵션)
7. `disclaimers.common` 공통 면책문구 — **하단 고정**

- **제품영역:** `product_link_allowed === true && 제품데이터 존재` 시에만. v0.1은 제품데이터가 없어 **전 행 제품 UI 없음.**
- **금지:** published/clinical 표기, 제품 링크/예시/구매 버튼(칼륨은 이중 차단).

## 4. 면책문구 렌더 위치
- `common` — **모든 상세 화면 하단 고정**, 항상 노출. 누락 시 상세 렌더 차단(error).
- `card_footer` — 목록 카드 또는 상세 상단 보조 한 줄(옵션).
- `onboarding` — 앱 최초 진입 1회 모달(옵션).
- `empty_state` — 관계 0건 빈 화면.
- `potassium_notice` — 칼륨 상세에서 `management_ko` 근처 별도 강조 박스.

## 5. 칼륨 고지 렌더 조건
- **트리거:** `relation.potassium_safety_card === true` (id 17·19). **nutrient 문자열 매칭 금지** — 플래그 기준만.
- **표시:** `disclaimers.potassium_notice`를 caution 스타일 박스로, `management_ko`(칼륨 안전문구)와 함께.
- **동시 강제:** `product_link_allowed === false` → 제품 UI 일절 없음. (이중 가드: 플래그 false거나 potassium_safety_card true면 제품영역 skip)
- **일반 행:** `potassium_safety_card !== true` → potassium_notice 렌더 안 함.

## 6. empty / error state 문구
- **empty(관계 0건):** `disclaimers.empty_state` 그대로 사용.
- **error(로드 실패/파싱 실패):** 고정 안전 문구 — "정보를 불러오지 못했어요. 네트워크 상태를 확인하고 다시 시도해 주세요." + 재시도 버튼. **의학 콘텐츠·이전 데이터 렌더 금지.**
- **필드 누락 처리:**
  - relation 필수필드(display_text_ko 등) 누락 → 해당 카드 **skip**(반쪽 의학문장 렌더 금지) + 로그.
  - `disclaimers.common` 누락 → 상세 렌더 차단, error 처리(면책 없는 의학정보 노출 금지).
- **금지:** empty/error에 "안전합니다 / 복용하세요 / 문제없습니다" 등 단정·지시·안심 문구.

## 8. 구현자 주의사항
- 데이터는 `medistack_v0.1_beta_export.json`만. `excluded_v0_1` 렌더 금지.
- 정확히 `relations` 19건. **status로 런타임 필터하지 말 것**(필드 없음 = 포함된 게 곧 노출 대상).
- published/clinical_reviewed: meta는 false 고정, 렌더 가드로만. 뱃지·문구 금지.
- 제품 UI: `product_link_allowed === true`(엄격 ===) **&& 제품데이터 존재** 시에만. 칼륨(false)은 절대. truthy 체크 금지.
- 칼륨 고지: `potassium_safety_card === true` 플래그 기준. nutrient 문자열 매칭 금지(표기·i18n 변동 위험).
- 면책: `common` 없으면 fail-safe(상세 차단). 모든 상세에 항상.
- 출처 링크는 식약처 nedrug(출처)지 제품 링크 아님 — 명확히 구분.
- evidence_level/mechanism은 내부값. 소비자 카드에 임상등급처럼 노출 금지(v0.1 미표시 권장).
- 접근성: 칼륨 경고를 색만으로 구분 금지(아이콘+텍스트 병행). 대비·폰트 크기 확보.
- 배포 전 `validate_medistack_v0_1_export.py` PASS + QA 표 P0 전부 PASS 필수.
- 카피 금지: 의학적 단정 / 복용 지시 / 구매 유도 (QA B10·B13·B14 대응).
