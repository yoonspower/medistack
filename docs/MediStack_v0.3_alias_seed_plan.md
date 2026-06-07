# MediStack v0.3 — alias seed 계획서

작성 기준일: 2026-06-07 / 단계: **계획만** (코드·alias JSON 생성·DATA_URL·deploy 전부 미실행)
상위: `docs/MediStack_v0.3_roadmap.md`(UX-A), `docs/MediStack_v0.3_alias_schema_design.md`(스키마).
기준 데이터: `data/medistack_v0.2_beta_export.json` (relations 30건 / live 성분 14종 / excluded_v0_1 = id 15).
PM 결정 반영: alias는 **별도 파일** `data/medistack_v0.3_aliases.json` / 검색매칭 + 카드 보조표시까지(상세 제품UI 금지) / **v0.2 30건 연결 alias만**.

> 이 문서는 무엇을 seed로 넣을지 범위·기준·개수만 정의한다. 실제 JSON 작성·코드·validator·배포는 PM 판정 후 별도.

---

## 0. 전제 (못박음)
- alias = **검색 보조**. 새 의학정보 아님. **alias만으로 relation 신규생성 금지.**
- v0.3 seed는 **v0.2 30건에 연결된 성분/대표품목 alias만.** 전체 품목 대량수집은 v0.4 이후.
- 제품 추천·구매·제휴 UI **금지**. **15행 excluded 관련 제품명 alias 금지**(PM 확정).
- published/clinical_reviewed **금지** 유지.

## 1. v0.3 alias seed 목적
- 같은 30건 데이터에 **검색 진입로**(상품명·영문/이형 성분명)를 붙여 체감 커버리지를 올린다.
- 데이터 건수·의학내용은 불변. seed는 "찾아짐"만 넓힌다.

## 2. v0.2 30건 relation 기준 alias 범위 (live 14성분, 대표품목 1:1)
| 성분(canonical) | live relation ids | 대표품목(=pointer 인용) | itemSeq | 제품alias 대상 |
|---|---|---|---|---|
| 레보플록사신 | 1,2,3 | 레보플록사신수화물정 | 199900886 | ✅ |
| 시프로플록사신 | 4,5,6 | 시프로민정250밀리그램 | 199901094 | ✅ |
| 독시사이클린 | 7,8,9 | 국제독시사이클린하이클레이트수화물캡슐100mg | 198000105 | ✅ |
| 레보티록신 | 10,11 | 씬지로이드정 | 201903264 | ✅ |
| 메트포르민 | 12 | 바이포민서방정500mg | 200709701 | ✅ |
| 오메프라졸 | 13,14 | 오메라졸캡슐 | 200411095 | ✅ |
| 에스오메프라졸 | **16만(live)** + 15(excluded) | 에소메프라정20mg | 201600209 | **❌(§6/§7)** |
| 푸로세미드 | 17,18 | 라식스정 | 196400037 | ✅ |
| 히드로클로로티아지드 | 19,20 | 다이크로짇정 | 196000008 | ✅ |
| 오플록사신 | 21,22,23 | 제일타리비드정 | 198600307 | ✅ |
| 목시플록사신 | 24,25 | 리목스정400mg | 201402438 | ✅ |
| 미노사이클린 | 26,27,28 | 미노씬캡슐50mg | 198501028 | ✅ |
| 알렌드론산 | 29 | 포사맥스70밀리그램정 | 200009061 | ✅ |
| 토라세미드 | 30,31 | 토렘정5밀리그람 | 200611522 | ✅ |

- 성분 alias 대상: 14종 전부(에스오메프라졸은 §7 단서 — 성분 alias도 PM 판정).
- 제품 alias 대상: 13종(에스오메프라졸 제외).
- alias 데이터에 영양소(nutrient) 제품명은 **불포함**(제품추천 오인 방지).

## 3. 성분명 alias 우선순위
1. **(P0) 영문 INN** — 검색 수요 큼. 예: levofloxacin, ciprofloxacin, doxycycline, levothyroxine, metformin, omeprazole, furosemide, hydrochlorothiazide(HCTZ), ofloxacin, moxifloxacin, minocycline, alendronate(alendronic acid), torasemide(torsemide).
2. **(P1) 염/수화물 정식표기** — pointer에 등장. 예: 레보플록사신수화물, 목시플록사신염산염, 시프로플록사신염산염, 미노사이클린염산염, 메트포르민염산염, 레보티록신나트륨수화물, 알렌드론산나트륨수화물.
3. **(P2) 표준 한글 이형/축약** — 통용 표기차(예: 토라세미드/토르세미드, 히드로클로로티아지드/하이드로클로로티아지드, HCTZ). 표준 범위만, 속어·오타 제외.

## 4. 대표 제품명 alias 우선순위 (13성분, 에스오메프라졸 제외)
1. **(P0) 대표품목 정식명** — pointer가 실제 인용한 품목명(위 표). 예: 제일타리비드정, 포사맥스70밀리그램정, 라식스정.
2. **(P1) 브랜드 코어/축약** — 용량·제형 접미 제거형. 예: 타리비드, 포사맥스, 라식스, 토렘, 다이크로짇, 미노씬, 씬지로이드, 시프로민. ← 사용자 실제 검색어에 가장 근접.
3. **(P2) 표기변형** — 용량/띄어쓰기/숫자표기 변형은 원칙적으로 **§10 정규화로 흡수**(엔트리 남발 금지). 정규화로 못 잡는 핵심 변형만 명시 등록.

> 주의: §10 정규화가 용량·띄어쓰기·대소문자를 흡수하므로, **순열식 변형을 entry로 대량 생성하지 않는다**(개수 부풀리기 금지). 개수 목표(§11)는 의미있는 진입어 기준.

## 5. alias 수집 기준 (편입 허용)
- canonical_ingredient가 **relations[].ingredient에 실재**.
- 제품 alias는 그 성분 relation의 **source가 인용한 대표품목**(+v0.2 교차확인 품목이 있으면 그것)에 한정. `item_seq`가 source.url itemSeq와 일치.
- 영문 INN은 표준 명칭(식약처/WHO INN) 기준.
- 모든 alias는 **하나의 canonical_ingredient로만** 매핑(다대일 금지: 한 alias가 두 성분 가리키면 제외).

## 6. alias 제외 기준 (금지)
- relations에 없는 약물/성분 alias(새 의학정보 유입).
- **에스오메프라졸 제품명 alias(넥시움/에소메프라정 등) — 전면 금지**(15행 excluded 관련, PM 확정).
- nutrient(칼슘·철분·마그네슘·칼륨…) 제품명/보충제 브랜드 alias(제품추천 오인).
- 시장 전 제네릭 상품명 대량수집(v0.4 이후).
- 오타·속어·자동 동의어 확장.
- 제품 링크/가격/구매/제휴 정보를 담는 필드.

## 7. excluded 15행 우회 방지
- **함정:** 에스오메프라졸은 id 15(×B12, excluded) + id 16(×Mg, live)에 걸침. 같은 품목(에소메프라정)이 두 행의 출처.
- **규칙:**
  1. 에스오메프라졸 **제품명 alias는 seed에 넣지 않는다**(§6). → "넥시움/에소메프라정" 검색으로 id 16조차 제품경로로는 안 나옴(보수적, PM 방향).
  2. 에스오메프라졸 **성분명 alias(esomeprazole/에스오메프라졸) 편입 여부는 PM 판정**(§12-1). 편입하더라도 alias 해석은 **renderable relations로만** → id 16(live)만, **id 15(B12) 절대 미노출**.
  3. 모든 alias 해석은 getRenderableRelations 경유. excluded_v0_1은 alias 경로로 진입 불가.
  4. validator가 "excluded 전용 매핑 alias"와 "에스오메프라졸 제품 alias"를 **FAIL**로 차단(§9).

## 8. alias 검증 기준 (데이터 품질)
- 각 alias 행: `alias`, `canonical_ingredient`, `kind`, `lang`, (product) `item_seq`·`source_relation_ids` 채움.
- `canonical_ingredient` ∈ live ingredients(14종). product alias의 `item_seq` ∈ 그 성분 relation의 itemSeq.
- 중복 alias(같은 표기 2회) 금지. 한 alias→한 성분.
- 영문/한글 표기 출처는 식약처 품목명·INN. 임의 작명 금지.

## 9. alias validator 설계 초안 (`scripts/validate_medistack_v0_3_aliases.*`, 구현 별도)
검사 항목(규칙만 정의):
1. JSON 로드 + 스키마 형태(필수 필드 존재, kind ∈ {product,ingredient}).
2. 모든 `canonical_ingredient` ∈ relations[].ingredient (미존재 FAIL).
3. **excluded 전용 매핑 금지**: canonical_ingredient가 live relation 0건이면 FAIL.
4. **에스오메프라졸 제품 alias 금지**: kind=product & canonical_ingredient=에스오메프라졸 → FAIL(15행 우회 가드).
5. product alias `item_seq` ∈ 해당 성분 relation source.url itemSeq 집합.
6. `source_relation_ids` 실재 + 그 relation.ingredient == canonical_ingredient.
7. nutrient 명으로 매핑되는 alias 금지(영양소 제품 alias 차단).
8. 제품 링크/가격/구매/제휴 필드 부재(제품 필드 전면 금지 확장).
9. alias 중복·다대일 매핑 금지.
10. (회귀) relations·v0.1 봉인·meta.relation_count 기존 게이트 무영향.

## 10. QA 케이스
alias JSON + 검색코드 적용 후(로컬).
- [ ] "타리비드"/"제일타리비드정" → 오플록사신 live(21·22·23).
- [ ] "포사맥스" → 알렌드론산 live(29). "라식스" → 푸로세미드(17·18). "토렘" → 토라세미드(30·31).
- [ ] "levofloxacin" → 레보플록사신(1·2·3). "HCTZ" → 히드로클로로티아지드(19·20).
- [ ] **"넥시움"/"에소메프라정" → 0건**(에스오메프라졸 제품 alias 미존재) → UX-B 미수록 안내.
- [ ] (성분alias 편입 시) "esomeprazole" → **id 16(Mg)만**, id 15(B12) 미노출. 미편입 결정 시 → 0건.
- [ ] 카드 보조표시: 상품명으로 매칭된 결과에 "상품명으로 검색됨" 정도 표기(상세엔 제품정보/구매 없음).
- [ ] alias 파일 제거 → 성분명 검색 graceful degrade.
- [ ] alias 적용 후 회귀: 목록 30건/콘솔 0/칼륨 필터 3건(17·19·30)/`#/r/15` 미노출/제품·구매 UI 부재.

## 11. v0.3 목표 alias 개수
- relations: **30건 유지**(불변).
- alias 목표: **약 100~150개**(의미있는 진입어 기준). 구성 추정:
  - 성분 alias ≈ 14성분 × (INN 1 + 염/수화물 1~2 + 한글이형 0~2) ≈ **40~70**.
  - 제품 alias ≈ 13성분 × (정식명 1 + 브랜드코어 1~2) ≈ **26~50**.
- PM 밴드 상한(300)은 **용량·띄어쓰기 순열을 entry로 풀어야** 도달 → 그건 §10 정규화로 흡수하는 게 맞음. v0.3은 **품질·정규화 우선**으로 100~150 권장(개수 부풀리기 지양). 상한 도달 필요 시 §12-3로 협의.

## 12. PM 판정 필요한 항목
1. **에스오메프라졸 성분명 alias 편입 여부**: 제품 alias는 금지 확정. 성분 alias(esomeprazole)는 renderable 필터로 id 16(live)만 나오고 id 15는 안 나옴 — **편입 허용 vs 보수적 제외**. (권장: 제외 — PM의 "15행 관련 alias 금지" 기조에 맞춰 v0.3은 에스오메프라졸 alias 전체 보류, id 16은 "에스오메프라졸"/"마그네슘" 기존 성분·영양소 검색으로 도달 가능.)
2. **alias 개수 목표**: 100~150 권장(품질) vs PM 밴드 100~300 상향. 정규화로 흡수할 변형을 entry로 셀지 결정.
3. **정규화 강도**: 용량표기(70밀리그램/70mg)·띄어쓰기·영문 대소문자 흡수 범위(과정규화 시 오매칭).
4. **카드 보조표시 문구**: "상품명으로 검색됨" 정확 카피·노출 조건(상품명 매칭 시에만).
5. **교차확인 2번째 품목 alias 포함 여부**: v0.2에서 교차확인한 품목명도 제품 alias로 넣을지(추적성↑ vs 개수↑).
6. **UX-B 묶음**: alias(찾아짐)와 미등록 안내(못 찾음)를 한 PR로 묶을지.

---

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성 금지 / 15행 excluded 관련 제품명 alias 금지.
