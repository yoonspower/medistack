# MediStack v0.2 — Phase 1 검색/필터 UX 설계 (설계만, 코드 수정 없음)

작성 기준일: 2026-06-07 / 전제: 정적 ES module 앱 유지 · v0.2 데이터 기준 동작 · v0.1 봉인
적용 안전 규칙(불변): 제품/제휴 UI 금지 · published·clinical 뱃지 금지 · excluded_v0_1 렌더 금지 · common disclaimer fail-safe · 칼륨 potassium_notice/제품차단 유지

---

## 1. 검색/필터 UX 설계
- 위치: **목록 화면(`#/`) 상단.** 상세 화면은 그대로(검색/필터는 목록에만 영향).
- 구성(위→아래): 검색 입력창 → 필터 칩 행(영양소 / 액션 / 근거수준) → (활성 조건 있을 때) `필터 초기화` 버튼 → 결과 카드 목록 → (무매치 시) 결과없음 상태.
- 동작: 검색어 입력(디바운스 ~150–200ms) 또는 필터 토글 시 **목록만 재렌더**. SPA라 상세 갔다 와도 조건 유지(인메모리 상태). 페이지 새로고침 시 초기화(베타 허용).
- 상태 보관: **인메모리 filter state**(query·선택 facet). (옵션: 해시 쿼리 `#/?q=…&nutrient=…` 미러링으로 공유/뒤로가기 보존 — 후순위 enhancement)
- 결과 카운트 표기: 기존 `listhead`를 "조건 일치 N건"으로 갱신(전체 대비). 단정/안전 표현 아님.

## 2. 필터 대상 필드 목록
**facet 값은 데이터에서 동적 도출**(distinct), 하드코딩 금지 → 50건 확장 시 자동 갱신.
- `nutrient` (영양소) — baseline: 칼슘 / 철분 / 마그네슘 / 비타민B12 / 칼륨
- `recommended_action` (액션) — separation→"복용 간격" / monitoring→"상태 모니터링"
- `evidence_level` (근거수준) — high / moderate → **중립 라벨**(예: "참고 근거: 높음 / 보통"). 카드엔 표시 안 함(필터 facet으로만), 임상등급 인상 금지.

필터 제외(노출/검색 대상 아님): `mechanism`(내부), `id`, `source`, `product_link_allowed`·`potassium_safety_card`(내부 플래그), `display_text_ko`·`management_ko`(본문).

## 3. 검색 매칭 기준
- 대상 필드: **`ingredient`(약물명) + `nutrient`(영양소명)** 만.
- 방식: 대소문자 무시 + 공백 trim/정규화(NFC) 후 **부분일치(substring)**. 예: "레보"→레보플록사신, "마그"→마그네슘.
- 두 필드 **OR**(둘 중 하나라도 포함이면 매치).
- 빈 검색어 = 검색 미적용(전체).
- 필터와 **AND** 결합: 최종결과 = (검색 매치) ∩ (영양소 facet) ∩ (액션 facet) ∩ (근거 facet).
- facet 내부는 **OR**(예: 칼슘 OR 철분), facet 간은 **AND**. 아무것도 선택 안 한 facet = 미적용.
- 본문(display/management) 검색·초성검색·퍼지검색은 **Phase 1 제외**(향후 후보).

## 4. empty state 문구 (두 상태 구분)
- **검색/필터 무매치(신규, app 상수)**: "검색·필터 조건에 맞는 참고 정보가 없습니다. 검색어나 필터를 바꾸거나 ‘필터 초기화’를 눌러 보세요."
  - ‘결과 없음 = 안전/문제없음’ 의미 아님. 의학적 결론 금지. `필터 초기화` 버튼 동반.
- **데이터 0건(기존 유지, 별개)**: `disclaimers.empty_state` 그대로 — "…관련 관계가 없음을 보장하지 않으며, 표시되지 않은 약-영양소 관계가 있을 수 있습니다…".
- 두 상태는 트리거·문구 모두 분리(무매치=쿼리 문제 / 데이터 0건=등록 없음).

## 5. 기존 렌더 규칙 영향 여부
- **relations-only 유지**: 검색/필터는 `getRenderableRelations(data)` 결과 위에서만 동작 → `excluded_v0_1`·15행 진입 불가(불변).
- **상세 화면 불변**: common disclaimer fail-safe, 칼륨 potassium_notice, 제품 UI 차단 전부 그대로. 필터된 카드도 같은 상세로 연결.
- **뱃지/제품 무도입**: 검색창·필터칩·초기화 버튼은 제품/제휴·published/clinical 요소를 일절 추가하지 않음. 근거수준 필터는 facet 컨트롤이지 카드 뱃지 아님.
- **guards 경유 강제**: 필터/검색 함수는 순수 함수로 guards에 추가하되 **반드시 relations 소스만** 사용(원시 데이터·excluded 우회 금지).
- 데이터 버전 무관: 검색/필터 코드는 로드된 relations에만 의존 → v0.2(19→50) 그대로 동작. (라이브 DATA_URL의 v0.2 전환은 Phase 3, Phase 1 개발/테스트는 v0.2 baseline로)

## 6. 필요한 코드 수정 파일 목록 (Phase 1 실제 구현 시)
- `src/js/guards.js` — 순수 함수 추가: `getFacets(rels)`(동적 facet), `filterRelations(rels, {query, nutrients, actions, evidences})`. relations 소스만.
- `src/js/render.js` — 목록 상단 검색/필터 바 마크업 + 필터된 subset 렌더 + 결과 카운트.
- `src/js/states.js` — 검색/필터 무매치 상태 `renderNoResults()` 추가(신규 상수).
- `src/js/app.js` — 입력/토글/초기화 이벤트 배선, 인메모리 filter state, 목록 재렌더(라우팅 유지).
- `src/css/styles.css` — 검색창·필터칩·초기화 버튼 스타일(clinical 톤 유지, 칼륨 색 의존 금지 원칙과 동일하게 활성상태 텍스트/체크 병행).
- 변경 없음: `data/*`(데이터 작업 아님), `index.html`(목록 컨테이너 기존), validator(Phase 1은 데이터 스키마 불변).

## 7. QA 추가 케이스
- 약물명 부분검색("레보") → 해당 subset만.
- 영양소명 검색("마그") → 해당 subset만.
- 검색 무매치 → **결과없음 상태**(데이터-0건 상태와 구분), `필터 초기화`로 복귀.
- nutrient 필터(단일/복수) → 정확 subset. facet이 데이터에서 도출되는지(하드코딩 아님).
- action / evidence 필터 → 정확 subset. 근거수준 라벨 중립(임상등급 인상 없음).
- 검색 + 필터 동시(AND) → 교집합 정확.
- `필터 초기화` → 전체 목록 복원.
- 필터된 목록에서도: excluded/15행 절대 미출현 / 결과 카드 클릭 → 상세에 common disclaimer / 칼륨 결과 → potassium_notice + 제품 UI 없음.
- 필터 UI가 published·clinical 뱃지·제품 요소를 추가하지 않음.
- 데이터 relations 0건 → 데이터-empty 상태(검색바 비활성/숨김 graceful).
- 접근성: 검색 input 라벨, 필터칩 키보드 조작, 초기화 도달 가능.
- 무매치 문구가 ‘안전’으로 읽히지 않음.

## 8. 위험요소
- **무매치 = ‘안전’ 오인** → 전용 중립 문구 + 데이터-0건과 분리 + 의학 결론 금지.
- **근거수준 필터 노출로 임상등급 오해** → 중립 라벨, 카드 미표시, 노출 범위·문구는 PM 확인 필요.
- **facet 하드코딩** → 데이터 도출로 50건 확장 자동 대응(스테일 영양소 목록 방지).
- **검색/필터가 렌더 가드 우회**(원시/excluded 검색) → `getRenderableRelations`만 입력으로.
- **상태 영속성**: 인메모리는 새로고침 시 소실(베타 허용). 공유 필요하면 해시 미러링(후순위).
- **한글 매칭**: substring으로 충분, 초성/퍼지는 제외(향후). NFC·trim 정규화로 미스매치 방지.
- **성능**: 19→50건 인메모리 필터는 무부담. 검색 입력 디바운스로 thrash만 방지.
- **접근성 색 의존**: 필터 활성상태를 색만으로 구분 금지(텍스트/체크 병행).
- **스코프 크립**: 정렬·페이지네이션·퍼지·본문검색은 Phase 1 제외.

---

## PM 확인 필요 (소수)
- 근거수준(evidence) 필터 **노출 여부·라벨 문구**(중립 "참고 근거: 높음/보통" 권장, 카드 미표시 유지).
- 필터 선택 방식: **다중선택 칩(권장, facet 내 OR)** vs 단일선택 드롭다운.
- 해시 쿼리 미러링(공유/뒤로가기 보존) Phase 1 포함 vs 후순위.

> 안전 원칙: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
