# MediStack v0.3 — 앱 검색 alias 합류 설계서

작성 기준일: 2026-06-07 / 단계: **계획만** (src 코드 미수정, DATA_URL 무변경, 배포 없음)
상위: `alias_schema_design.md` · `alias_seed_plan.md` · `alias_operational_seed_plan.md` · `alias_sample_validator.md`
대상 운영데이터: `data/medistack_v0.3_aliases.json` (53개, 앱 미반영 상태). 라이브 relation = v0.2 30건(불변).

현 앱 구조(검증):
- `data.js` `loadData()` → `DATA_URL`(v0.2) relation JSON fetch + shape 가드.
- `guards.js` `filterRelations(rels, state)` = 순수함수, `SEARCH_FIELDS=['ingredient','nutrient']` substring 매칭. **입력은 항상 `getRenderableRelations(data)` 결과** → excluded_v0_1/15행 구조적 진입 불가.
- `app.js` boot: loadData → state.data → renderResults(filterRelations).

> 이 문서는 변경 계획·QA 게이트만. 실제 src 수정·배포는 PM 판정 후 별도.

---

## 0. 불변 전제
- **DATA_URL=v0.2 유지.** relation JSON 변경 금지. alias는 **별도 파일 fetch**.
- 제품 추천/구매/제휴 UI 금지. published/clinical 표시 금지.
- excluded/15행 우회 금지. 에스오메프라졸 alias 보류 유지(파일에 없음).
- alias 부재/실패 시 **기존 검색 유지(graceful degrade)** — alias는 부가기능.

## 1. alias JSON fetch 방식
- DATA_URL(relation)과 **독립된 별도 fetch**. 신규 상수 `ALIAS_URL = './data/medistack_v0.3_aliases.json'`.
- 위치: `data.js`에 `loadAliases()` 추가(또는 신규 `aliases.js` 모듈). relation 로드와 분리.
- **fail-soft**: `fetch` 실패·HTTP≠200·JSON 파싱 실패·shape 불일치 → **throw 안 하고 `null` 반환**(앱은 relation-only 검색 유지). relation 로드와 달리 alias 실패는 치명 아님.
- `cache: 'no-store'`(relation과 동일 정책).
- shape 가드(최소): 객체 + `ingredient_aliases`/`product_aliases` 배열. 아니면 무시.

## 2. 기존 relation 검색과 alias 검색 병합 방식
- 부팅 시 alias로 **런타임 인덱스** 1회 생성: `aliasIndex = [{ normAlias, canonicalIngredient }]` (정규화 키).
- 검색 질의 q에 대해 **alias 해석**: `resolveAliasIngredients(q, aliasIndex)` → `norm(alias).includes(norm(q))`인 alias들의 `canonical_ingredient` 집합(정규화) 반환.
- `filterRelations` 매칭 규칙 확장(순수함수 유지, alias 인덱스는 인자로 주입):
  - 기존: `norm(ingredient)` 또는 `norm(nutrient)`에 q substring → match.
  - 추가: **relation의 `norm(ingredient)`가 alias해석 집합에 정확히 포함**되면 match.
  - 즉 `직접매칭 OR alias매칭` (facet AND 조건은 기존 그대로).
- **안전 핵심**: `filterRelations` 입력 풀은 여전히 `getRenderableRelations` 결과뿐. alias는 "어떤 성분을 질의로 칠지"만 넓힐 뿐, **풀 자체를 못 넓힘** → excluded/15행 진입 불가(자동 보장).
- 매칭 단일키 = canonical_ingredient(정규화 **정확 일치**, substring 아님) → alias가 엉뚱한 성분에 번지지 않음.

## 3. alias 검색 결과 표시 문구
- 목적: 사용자가 상품명(예 "타리비드")으로 쳤을 때 결과가 **성분 기준임을 알리되**, 제품/의학 단정으로 읽히지 않게.
- **권장(A)**: 결과 목록 상단 **맥락 안내 1줄**(제품카드/뱃지 아님). 예:
  - `"'타리비드'은(는) 오플록사신의 제품명으로 검색했습니다."` (alias→canonical 노출, 검색 보조임을 명시)
- 대안(B): 각 결과 카드에 작은 "상품명 검색" 표식 — **비권장**(카드가 제품정보처럼 보일 위험).
- 조건: q가 **direct 매칭 없이 alias로만** 해석됐을 때만 안내(직접 성분명 검색이면 불필요).
- 카피 확정은 PM. 어떤 경우에도 "안전/위험/복용" 단정 금지, 제품링크·구매 없음.

## 4. alias가 없는 경우 기존 검색 유지
- aliasIndex 비었거나(`null`/0건) q가 어떤 alias에도 안 걸리면 → `filterRelations`는 **기존 direct substring 매칭만** 수행(동작 무변화).
- alias는 **순수 부가**: 켜져도 기존 결과를 줄이지 않고 **늘리기만** 함(OR 결합).

## 5. excluded / 15행 우회 방지
- 1차(자동): `filterRelations` 풀 = `getRenderableRelations` → 15행/excluded는 애초에 후보에 없음. alias로도 못 부름.
- 2차(데이터): alias 파일에 15행·에스오메프라졸 제품 alias 부재(validator #6/#9 강제, CI 게이트 적용 완료).
- 3차(매칭): alias→canonical은 **정확 일치**라, 우연히 excluded 성분 문자열에 번질 일 없음.
- 회귀 QA: `#/r/15` 직접진입 error 유지, 목록/검색 어디서도 15행 미출현.

## 6. 에스오메프라졸 alias 보류 유지
- 운영 alias 파일에 에스오메프라졸 성분/제품 alias **없음** → "넥시움"/"esomeprazole" 검색 시 alias 경로로 **0건**(direct로도 0건) → §3 안내 없이 UX-B(미수록) 흐름.
- id 16(에스오메프라졸×Mg, live)은 기존 "에스오메프라졸"/"마그네슘" 직접 검색으로만 도달(현행과 동일). 보류 정책 코드상 자동 유지(특별 분기 불필요).

## 7. 실패 시 fallback
- alias fetch/parse 실패 → `loadAliases` null → aliasIndex 빈 배열 → 검색은 relation-only(§4). 콘솔 `console.warn('[MediStack] alias load skipped')` 정도, 사용자 에러화면 없음.
- 인덱스 빌드 중 malformed 엔트리 → 해당 엔트리만 skip(전체 실패 아님).
- relation 로드 실패는 기존대로 error state(이건 치명, 변경 없음).
- 핵심: **alias 때문에 앱이 죽거나 빈 화면 나오면 안 됨.**

## 8. QA 케이스 (로컬 `http.server`, alias 반영 빌드)
검색:
- [ ] "타리비드"→오플록사신 21·22·23, 상단 안내 1줄 노출.
- [ ] "포사맥스"→29, "라식스"→17·18, "토렘"→30·31, "미노씬"→26·27·28.
- [ ] "levofloxacin"→1·2·3, "HCTZ"→19·20, "ofloxacin"→21·22·23.
- [ ] "오플록사신"(직접)→21·22·23, 안내 문구 **미노출**(직접 매칭이므로).
안전/회귀:
- [ ] "넥시움"/"esomeprazole"→0건→UX-B 안내(에스오메프라졸 보류 확인).
- [ ] `#/r/15` 미노출, 목록/검색 어디서도 15행 없음.
- [ ] alias 파일 임시 제거/404→앱 정상, relation-only 검색, 콘솔 warn만, 에러화면 없음.
- [ ] 제품/구매/제휴 UI 부재, published/clinical 문구 부재.
- [ ] 칼륨 필터 3건(17·19·30) 유지, "필터 초기화"→30건 복원, facet 동적도출 유지.
- [ ] 콘솔 에러 0(localhost).
- [ ] alias 매칭이 결과를 **늘리기만** 하고 기존 direct 결과를 빠뜨리지 않음.

## 9. 수정 예상 파일
- `src/js/data.js` — `ALIAS_URL` + `loadAliases()`(fail-soft) 추가. (relation `loadData`는 불변)
- `src/js/guards.js` — `buildAliasIndex(aliasData)` + `resolveAliasIngredients(q, index)` + `filterRelations(rels, state, aliasIndex)` 시그니처 확장(인자 옵션, 기본 동작 보존).
- `src/js/app.js` — boot에서 alias 로드/인덱스, `renderResults`에 aliasIndex 전달 + §3 안내 조건부 표시.
- `src/js/render.js` — §3 안내 1줄 렌더 헬퍼(제품 UI 아님, 단순 텍스트).
- `src/css/styles.css` — 안내 1줄 최소 스타일(선택).
- **DATA_URL·relation JSON·deploy.yml 변경 없음.** validator/CI 게이트는 이미 alias 검증 중.

## 10. 배포 전 게이트
1. 위 파일 수정 후 **로컬 §8 QA 전 항목 그린** + v0.1/v0.2/v0.3 alias validator PASS → **PM 판정**.
2. PR(`v0.3-dev`류) → `validate.yml`(v0.1+v0.2+v0.3 alias) CI 그린 → **PM 판정**.
3. 머지=main push → `deploy.yml` validate(3종)→deploy 통과 → 라이브 검증(검색 alias 동작/안전/회귀) → 이상 시 롤백(코드 revert; alias 무관).
4. DATA_URL은 v0.2 유지. 라이브에 alias 검색 기능만 추가, relation 데이터·건수 불변.
- 각 게이트 직전 단계 보고·승인 없이 진행 금지.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지.
