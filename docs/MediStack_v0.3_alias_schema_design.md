# MediStack v0.3 — UX-A 제품명/성분명 alias 설계서

작성 기준일: 2026-06-07 / 단계: **설계만** (코드·데이터·DATA_URL·deploy 전부 미실행)
상위 문서: `docs/MediStack_v0.3_roadmap.md` (UX-A 트랙). 짝: v0.2 SOP·validator 문서.
기준 데이터: `data/medistack_v0.2_beta_export.json` (relations 30건, excluded_v0_1 1건=id 15, 성분 14종).

> 이 문서는 스키마·규칙·QA 케이스만 정의한다. 실제 alias 데이터 작성·코드·validator 구현·배포는 PM 판정 후 별도.

---

## 핵심 전제 (먼저 못박음)
- alias는 **검색 보조용**이다. 새로운 의학정보가 **아니다.**
- alias만으로 relation을 **새로 만들 수 없다.** alias는 이미 검증된 relation의 약물/제품으로 가는 **입구**일 뿐.
- 검증된 relation에 연결된 **제품명/성분명만** 허용. 그 외 약물은 alias로 끌어오지 않는다.
- 제품 추천·구매·제휴 UI **금지** 유지. alias는 검색 매칭에만 쓰이고, 상세에 제품 카드를 만들지 않는다.
- `published`/`clinical_reviewed` **금지** 유지(천장=verified_reference).

---

## 1. alias 기능 목적
- 현재 검색은 **성분명·영양소명**(예: "오플록사신", "칼슘")만 매칭. 사용자는 **상품명**("타리비드", "포사맥스", "넥시움")이나 **영문/이형 성분명**("levofloxacin", "ofloxacin")으로 찾는다.
- 목적: 같은 검증 데이터(30건)에 대해 **검색 진입로를 넓혀** 체감 커버리지를 올린다. 데이터의 의학적 내용·건수는 그대로.

## 2. 검색 체감 커버리지 전략
- 데이터 건수를 늘리지 않고도, 한 relation에 **여러 검색어**가 붙으면 "찾아짐" 확률이 오른다.
- 두 축으로 진입로 확대:
  - **제품명 축**: 상품명/브랜드 → 성분 → 그 성분의 live relations.
  - **성분명 이형 축**: 영문명·축약·표기변형 → 정규 성분명 → live relations.
- 원칙: 진입로만 넓히고 **도착지(검증된 relation 집합)는 불변.** "찾아짐"이 "안전/위험 단정"으로 읽히지 않게 카피는 기존 그대로.

## 3. relation 데이터와 alias 데이터 분리 원칙
- **relation 데이터 = 의학정보(검증·불변 규약).** alias 데이터 = 검색 인덱스(보조·교체 가능).
- 둘을 **물리적으로 분리**한다: alias는 relations 배열 안에 섞지 않고 **별도 최상위 키**(`search_aliases`)로 둔다.
- 이유: ①relation validator(v0.2 15항목)의 "제품 필드 전면 금지" 규약을 건드리지 않음 ②alias는 언제든 추가/수정/삭제해도 의학 데이터 무결성·md5 봉인에 영향 없음 ③롤백 단위 분리.
- 현재 데이터에는 **제품명 전용 필드가 없음**(품목명은 `source.pointer` 자유텍스트 안에만 존재). alias를 pointer 파싱으로 만들면 취약 → **구조화된 별도 인덱스로 명시 입력**한다.

## 4. alias 스키마 초안
별도 최상위 키. relations 스키마는 **무변경**.

```json
"search_aliases": {
  "version": "0.3",
  "note": "검색 보조 인덱스. 의학정보 아님. 검증된 relation의 ingredient/품목에만 연결.",
  "ingredient_aliases": [
    { "alias": "levofloxacin", "canonical_ingredient": "레보플록사신", "kind": "ingredient", "lang": "en" },
    { "alias": "레보플록사신수화물", "canonical_ingredient": "레보플록사신", "kind": "ingredient", "lang": "ko" }
  ],
  "product_aliases": [
    { "alias": "제일타리비드정", "canonical_ingredient": "오플록사신", "kind": "product",
      "item_seq": "198600307", "source_relation_ids": [21, 22, 23] }
  ]
}
```

필드 정의:
- `alias` — 사용자가 입력할 수 있는 검색어(상품명 또는 성분 이형). 표시 비대상(상세 UI에 노출 안 함).
- `canonical_ingredient` — relations[].ingredient 와 **정확히 일치**해야 하는 정규 성분명. 해석의 단일 키.
- `kind` — `"product"` | `"ingredient"`.
- `lang` — `"ko"` | `"en"` (정규화/표시용 참고).
- (product 전용) `item_seq` — 그 상품명이 가리키는 품목의 itemSeq. relations의 source.url itemSeq 중 하나와 일치해야 함(추적·검증용).
- (product 전용) `source_relation_ids` — 이 제품이 근거가 된 relation id 목록(추적용, 매칭 자체는 canonical_ingredient로 함).

설계 선택: 매칭의 단일 진실원은 **`canonical_ingredient`**. `source_relation_ids`/`item_seq`는 출처추적·validator 교차검증용이지 매칭 1차 키 아님(중복·표류 방지).

## 5. alias가 연결 가능한 대상
- **연결 가능:** relations 배열에 **실제 등장하는 ingredient**, 그리고 그 relation의 `source`가 인용한 **품목명/itemSeq**.
- **연결 불가:**
  - relations에 없는 약물·성분(=새 의학정보 유입 금지).
  - excluded_v0_1에만 있는 관계(아래 §6).
  - 영양소(nutrient) 쪽 상품명(예: 특정 칼슘 보충제 상품명) — **제품 추천으로 읽힐 위험** → v0.3 비범위.
- 즉 alias는 **약물(ingredient) 진입로**만 넓힌다. 영양소 제품 alias는 금지.

## 6. excluded_v0_1 / 15행 우회 방지 규칙 (안전 핵심)
함정: 에스오메프라졸은 **id 15(×비타민B12) = excluded**이면서 **id 16(×마그네슘) = live**. 성분이 excluded·live 양쪽에 걸칠 수 있다.

규칙(절대):
1. alias 해석 결과는 **항상 renderable relations로만** 한정한다. alias → canonical_ingredient → **그 성분의 live relation들**만 결과로. excluded_v0_1은 alias 경로로 **절대 진입 불가**.
   - 예) "넥시움"(에스오메프라졸) 검색 → id 16(마그네슘, live)만 노출, **id 15(B12, excluded)는 미노출.** 이게 올바른 안전 동작.
2. **excluded에만 존재하고 live relation이 0건인 성분**으로 해석되는 alias는 **추가 금지**(있어도 결과 0건이어야 하며, validator가 차단).
3. alias 매칭은 반드시 **getRenderableRelations 경유 동일 소스**를 거친다. 별도 경로로 raw/excluded를 훑지 않는다.
4. 상품명이 "있을 법하지만 미수록"인 경우(예: 와파린 상품명) → alias 없음 → 검색 0건 → **UX-B 미등록 안내 문구**로(="안전" 오인 금지).

## 7. 제품명 alias 입력 기준
- **검증된 relation의 source.pointer가 실제 인용한 품목명**만 입력. 임의 상품명·미인용 제네릭 대량 투입 금지.
- 각 product alias는 `item_seq`가 그 성분 relation의 source.url itemSeq와 **일치**해야 함(추적 가능).
- 한 성분에 대표품목 + (v0.2에서 교차확인한) 2번째 품목 수준까지. **시장 전 제네릭 나열 금지**(노이즈·제품추천 오인).
- 상품명 표기는 식약처 품목명 기준(띄어쓰기·용량 표기 변형은 §10 정규화로 흡수).

## 8. 성분명 alias 입력 기준
- 정규 성분명(relations[].ingredient)에 대한 **영문명/표준 이형/축약**만. 예: 레보플록사신↔levofloxacin, 오플록사신↔ofloxacin, 에스오메프라졸↔esomeprazole.
- 염·수화물 표기 변형 허용: "레보플록사신수화물"→"레보플록사신". 단 **의미가 바뀌면 안 됨**(다른 성분으로 매핑 금지).
- 오타·속어·통칭은 v0.3 비범위(검증·유지 비용↑). 표준 이형만.

## 9. 대표품목/제네릭 처리 기준
- 매칭 키는 **성분(canonical_ingredient)**이므로, 대표품목·제네릭 어느 상품명으로 들어와도 **같은 성분의 동일 live relation 집합**으로 도착(결과 일관).
- 제네릭 상품명은 **추적상 필요한 최소만** 등록(전수 등록 금지). 등록 안 된 제네릭 상품명으로 검색하면 성분명/대표품목명으로는 찾을 수 있게 안내(UX-B와 연계).
- 동일 성분 여러 itemSeq가 있어도 alias→성분→relation 매핑은 1:N(성분→relations)로 단순 유지.

## 10. 검색 매칭 방식
- 런타임에 `search_aliases`를 읽어 **{정규화 검색어 → canonical_ingredient}** 맵 생성.
- 정규화: 공백·정/대소문자(영문)·전각/반각·용량표기("70밀리그램"/"70mg") 제거 후 비교(구현 시 확정). 부분일치는 기존 검색 동작과 일관되게.
- 사용자 입력 → (a) 기존 성분명/영양소명 매칭 + (b) alias 맵 매칭 → 매칭된 canonical_ingredient의 **live relations** 반환. 두 경로 결과를 합집합 후 dedup.
- alias는 **검색 인덱스에만** 영향. 상세 화면 렌더·출처·면책·칼륨 카드 로직은 **무변경**(여전히 relation 데이터 기준).
- alias 데이터 부재/로드 실패 시 → **기존 성분명 검색으로 graceful degrade**(alias는 부가기능, 실패해도 앱 정상).

## 11. validator 추가 규칙 (alias 무결성)
alias 도입 시 검증 항목(구현은 별도, 규칙만 정의):
1. 모든 `canonical_ingredient`는 relations[].ingredient에 **존재**해야 한다(미존재 = FAIL).
2. **excluded_v0_1에만 있고 live relation 0건인 성분**으로 매핑되는 alias 금지(FAIL). → 15행 우회 차단의 데이터단 보증.
3. product alias의 `item_seq`는 해당 성분 relation의 source.url itemSeq 집합에 **포함**돼야 함(미포함 = FAIL).
4. `source_relation_ids`는 실제 relation id이고, 그 relation의 ingredient == canonical_ingredient여야 함.
5. alias 데이터는 **제품 링크/구매/가격/제휴 필드를 가지면 안 됨**(relations의 "제품 필드 금지" 규약을 alias에도 확장).
6. nutrient(영양소) 상품명 alias 금지(§5) — alias가 nutrient로 매핑되지 않음.
7. (회귀) relations·v0.1 봉인·meta.relation_count 기존 검증은 **그대로 통과**해야 함(alias 추가가 기존 게이트를 깨지 않음).

## 12. QA 케이스
로컬(`http.server`) 기준. alias 데이터 + 검색 코드 적용 후.
- [ ] "타리비드" → 오플록사신 live(21·22·23) 노출.
- [ ] "포사맥스" → 알렌드론산 live(29) 노출.
- [ ] "levofloxacin" → 레보플록사신 live(1·2·3) 노출.
- [ ] **"넥시움" → id 16(마그네슘, live)만 노출, id 15(B12) 미노출** ← 우회방지 핵심.
- [ ] excluded 전용으로 매핑되는 alias 없음(validator FAIL로 사전 차단 확인).
- [ ] alias 미등록 상품명(예: 와파린 상품명) → 0건 → UX-B "미수록≠안전" 안내(연계 트랙).
- [ ] alias 데이터 일부러 제거 → 기존 성분명 검색 정상(graceful degrade).
- [ ] alias 적용 후에도: 목록 30건/콘솔 0/칼륨 필터 3건(17·19·30)/`#/r/15` 미노출/제품·구매 UI 부재.
- [ ] 같은 성분 다른 상품명 입력 → 동일 relation 집합(결과 일관).

## 13. v0.3에서 할 범위 / 하지 않을 범위
**할 것:**
- ingredient_aliases(영문·표준 이형) + product_aliases(검증 relation이 인용한 대표/교차확인 품목명).
- 검색 매칭에 alias 합류 + graceful degrade.
- alias validator 규칙.

**하지 않을 것:**
- nutrient(영양소) 상품명 alias / 제품 추천·구매·제휴 UI.
- 시장 전 제네릭 전수 등록.
- 오타·속어·자동 동의어 확장.
- alias를 근거로 한 신규 relation 생성(=새 의학정보).
- published/clinical 승격, excluded 15행 노출.

## 14. PM 판정 필요한 결정사항
1. **excluded 걸친 성분의 제품 alias 허용 여부**: "넥시움"(에스오메프라졸)은 live id 16이 있어 §6 규칙상 안전하게 노출 가능. 그래도 혼동 우려로 **제외할지**, 규칙대로 **허용할지**. (설계 권장: 허용 — renderable 필터가 robust하고 동작이 올바름. 단 QA 케이스로 명시.)
2. **alias 데이터 배치**: §3대로 별도 키 `search_aliases`로 v0.2 파일에 **append**할지, 아니면 v0.3 신규 export 파일로 갈지(로드맵 §4 버전운용과 연동).
3. **정규화 강도**: 용량표기/영문 대소문자/띄어쓰기 어디까지 흡수할지(과정규화 시 오매칭 위험).
4. **제품명 표시 정책**: alias는 검색에만 쓰고 상세에 상품명 노출 안 함(현행) 유지할지, 아니면 출처 pointer에 이미 있는 품목명을 어떻게 다룰지(현행 유지 권장).
5. **UX-B 묶음 여부**: alias(찾아짐 확대)와 미등록 안내(못 찾음 처리)는 짝 → 한 PR로 묶을지.

---

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / excluded 15행 alias 우회 금지.
