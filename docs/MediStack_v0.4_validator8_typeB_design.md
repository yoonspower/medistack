# MediStack v0.4 — validator #8 일반화 + 유형 B alias 설계안

작성 기준일: 2026-06-11 / 단계: **설계 문서만** (코드·validator·alias JSON·data·DATA_URL·deploy 미변경)
상위: `MediStack_v0.4_alias_expansion_candidates.md`(유형 A/B 정의 §3·§6), `MediStack_v0.4_typeA_alias_addition_plan.md`(유형 A 9건 — **편입·배포 완료**, alias 53→62, 커밋 4e90143).

> 이 문서는 유형 B(교차확인 2번째 품목) alias를 실제 추가하기 **전에** validator #8을 어떻게 일반화할지 설계만 정의한다.
> 유형 B alias 실제 편입·validator 코드 수정·데이터 변경은 PM 판정 후 별도 단계.

---

## 1. 현재 validator #8 — 목적과 제한

`scripts/validate_medistack_v0_3_aliases.py` check #8 (참조: 184~194행):

```
8) product alias: item_seq 가 해당 성분 relation 의 itemSeq 집합에 속함
```

- **동작**: 라이브 `relations[].source.url`에서 `itemSeq=(\d+)`를 수집해 성분별 itemSeq 집합(`ing_to_seqs`)을 만들고, `kind=product`인 alias의 `item_seq`가 그 집합에 속하는지 검사.
- **목적**: 제품 alias가 **relation 원문에서 실제 인용된 품목**만 가리키게 강제 → 임의 제품명/미검증 itemSeq로 검색 표면을 부풀리는 것을 차단.
- **현재 제한**: relation source는 성분당 **대표 itemSeq 1개**만 인용한다(v0.2 30건 전수 확인: 14성분 각 1 itemSeq). 즉 #8의 허용 집합 = "성분당 정확히 1개 품목". 대표 품목이 아닌 어떤 제품 alias도 — 식약처에 실재하고 같은 성분이어도 — 기계적으로 FAIL.

## 2. 유형 B가 #8과 충돌하는 이유

- 유형 B = v0.2 Phase 2에서 **원문 교차확인에 실제 사용한 동일 성분 2번째 품목**의 품목명/브랜드코어 alias.
- 그 2번째 품목의 itemSeq는 **relation 데이터 어디에도 없다**(source.url은 대표 품목 1개만 인용). → `ing_to_seqs`에 없음 → #8 즉시 FAIL.
- 즉 충돌은 정책 위반이 아니라 **#8의 허용 집합 정의가 "relation 인용 itemSeq"로 좁기 때문**. 유형 B는 "검증된 동일 성분 품목"이라는 점에서 대표 품목과 안전 등급이 같지만, 현재 #8은 그 검증 사실을 표현할 자리가 없다.

## 3. 유형 B alias 정의

- **같은 canonical_ingredient로 귀속되는 2번째(이후) 품목명/제품명 alias.** `kind: product`.
- **relation 신규 생성 금지**: alias는 기존 라이브 relation 검색 결과로만 연결된다. relation 풀·내용·개수(30건)는 불변.
- **검색 보조 전용**: 의학정보 아님. 제품 추천·구매 유도·제품 UI 아님. 매칭 결과는 기존 성분 relation 카드뿐.

## 4. 허용 가능한 유형 B alias 기준 (전부 충족해야 편입 후보)

1. **기존 라이브 relation의 canonical_ingredient와 연결 가능**해야 한다(현 #4와 동일 — 신규 성분 불가).
2. **식약처 공식 품목명 또는 명확한 대표 품목명 기반**: nedrug에서 품목명+itemSeq+성분 일치를 browse로 실확인(후보수집 SOP §5, 미확인=드롭). 가능하면 v0.2 Phase 2 교차확인 기록과 대조.
3. **에스오메프라졸/15행 제외**: 에스오메프라졸 제품 alias 금지(#9 유지), relation 15·excluded 연결 금지(#5·#6 유지). 에스오메프라졸은 라이브 relation이 있어도 제품 alias 대상에서 계속 제외.
4. **미검증 브랜드 alias 제외**: itemSeq 실확인 못 한 브랜드, 순열/용량/제형 변형, 숫자 채우기용 항목 금지.
5. **제품 추천/구매 유도 금지**: alias 항목에 링크·가격·구매 관련 필드 금지(#10 유지). 매칭 표면은 검색뿐.

## 5. validator #8 일반화 방향

핵심: 허용 itemSeq 집합을 "relation 인용분"에서 "**relation 인용분 ∪ 검증된 교차확인 화이트리스트**"로 확장한다. 나머지 가드(#1~#7, #9~#11)는 그대로.

- **화이트리스트 위치(안)**: alias 파일 meta 옆 별도 섹션 `verified_item_seqs`(성분별 `{canonical_ingredient: [{item_seq, item_name, verified_at, method}]}`) — 데이터(export)는 건드리지 않고 alias 운영 파일 안에서 자기완결. (대안: 별도 파일. 단순성 때문에 동일 파일 내 섹션 권고.)
- **일반화된 #8 판정**:
  - `kind=product`의 `item_seq` ∈ (해당 성분 relation itemSeq 집합 ∪ 해당 성분 화이트리스트) → PASS. 둘 다 아니면 FAIL.
  - **product alias가 성분당 여러 개여도, 같은 canonical_ingredient로 귀속되면 허용.**
- **불변 조건(일반화해도 FAIL이어야 함)**:
  - alias/화이트리스트가 **relation을 새로 만들면 실패**: canonical_ingredient가 라이브 relation 성분이 아니면 #4 FAIL. 화이트리스트의 성분 키도 라이브 성분이어야 함(신규 검사).
  - **excluded row·unpublished/clinical_reviewed 봉인 항목으로 연결되면 실패**: relation 15·excluded_v0_1 연결(#5·#6), excluded 전용 성분 매핑, 에스오메프라졸 제품 alias(#9) 전부 기존대로 FAIL. 화이트리스트에 에스오메프라졸/excluded 성분 키가 있어도 FAIL(신규 검사).
  - **product_link_allowed=false 대상(칼륨 행: relation 17·19·30)이 구매/제품 UI와 연결되면 실패**: alias·화이트리스트 어디에도 링크/구매/제휴 필드가 있으면 FAIL(#10을 화이트리스트까지 확대). 앱에 제품 UI 자체가 없으므로(불변 원칙) alias는 칼륨 성분이어도 "검색→기존 칼륨 안전카드 relation 노출"만 한다 — 이것은 허용이며, 금지되는 것은 제품/구매 연결이다.
- **검사 추가 형태**: 기존 11-check 유지 + #8 판정식 확장 + 화이트리스트 자체 검증(성분 실재·excluded/에스오메프라졸 금지·필드 금지·itemSeq 형식·중복) 1~2개 신규 check. 기존 PASS 케이스(현 62개)는 화이트리스트가 비어 있어도 전부 그대로 PASS여야 한다(하위호환).

## 6. 실패해야 하는 케이스

| # | 케이스 | 걸리는 검사 |
|---|---|---|
| F1 | product alias의 item_seq가 relation 인용분에도 화이트리스트에도 없음 | #8(일반화) |
| F2 | 화이트리스트에 라이브 relation에 없는 성분 키(예: 신규 성분) | 신규(화이트리스트 성분 실재) |
| F3 | alias가 라이브에 없는 canonical_ingredient를 가리킴(relation 신규 생성 시도) | #4 |
| F4 | source_relation_ids에 15 또는 excluded id 포함 | #6 |
| F5 | excluded 전용 성분으로 매핑 | #5 |
| F6 | 에스오메프라졸 제품 alias(화이트리스트 경유 포함) | #9 + 신규 |
| F7 | alias 또는 화이트리스트 항목에 link/buy/price/affiliate류 필드 | #10(확대) |
| F8 | 같은 alias 표면형 중복(정규화 후) | #3 |
| F9 | 화이트리스트 item_seq가 비숫자/빈값/중복 | 신규 |
| F10 | nutrient(영양소)로 매핑되는 alias | #11 |

## 7. 통과해야 하는 케이스

| # | 케이스 | 근거 |
|---|---|---|
| P1 | 현행 62개 alias 전체(화이트리스트 없음/빈 상태) | 하위호환 — 일반화는 순수 확장 |
| P2 | 대표 품목 product alias(현 24개, item_seq=relation 인용분) | 기존 #8 경로 그대로 |
| P3 | 유형 B: 알렌드론산 2번째 품목 alias — itemSeq 식약처 실확인 + 화이트리스트 등재 + canonical=알렌드론산 | #8 일반화 경로 |
| P4 | 유형 B: 토라세미드 2번째 품목 alias(칼륨 안전카드 성분) — 링크/구매 필드 없음, 검색→기존 relation 30(칼륨 카드) 노출만 | product_link_allowed는 제품 UI 게이트지 검색 차단이 아님 |
| P5 | 성분당 product alias 2개 이상(대표+교차확인), 모두 같은 canonical | §5 "여러 개 허용" |

## 8. 유형 B 실제 편입 전 필요한 QA

1. **후보 검증**: 각 2번째 품목을 nedrug에서 browse 실확인(품목명 실재 + 성분 일치 + itemSeq 채록 + 확인일 기록). v0.2 Phase 2 교차확인 기록과 대조. 미확인 드롭.
2. **validator 작업 순서**: 일반화 코드 수정 → 현행 62개 alias로 **하위호환 PASS(기존 11-check 전부)** 먼저 확인 → §6 실패 케이스를 임시 픽스처로 전부 FAIL 확인(특히 F1·F2·F6) → 그다음에만 유형 B 데이터 투입.
3. **검색 smoke**: 신규 유형 B 각 alias → 해당 성분 relation만 매칭(건수 명시), prefix 오매칭 없음.
4. **회귀**: 타리비드→오플록사신 3건 / 포사맥스→알렌드론산 1건 / 토렘→토라세미드 2건 / 넥시움·esomeprazole→0건 / #/r/15 fail-safe / relation 30건 / DATA_URL 불변.
5. **배포 게이트**: validator 3종(v0.1/v0.2/v0.3) PASS → 커밋 → push → Actions success → 라이브 HTTP 200 + 라이브 alias count 확인.

## 9. v0.4에서 아직 하지 않을 것

- 유형 B alias 실제 추가(이 문서는 설계만) / validator 코드 실수정.
- 제네릭 대량(300밴드)·성분당 추가 브랜드 N종 — v0.5 트랙.
- 에스오메프라졸 alias(성분/제품), 15행 재편입, relation 확장/수정, DATA_URL 변경.
- nutrient alias, 제품/구매/제휴 UI, published/clinical_reviewed 전환, HCl 축약 4종(계속 제외).

## 10. PM 판정 필요사항

1. **화이트리스트 위치**: alias 파일 내 `verified_item_seqs` 섹션(권고) vs 별도 파일.
2. **화이트리스트 필수 메타**: `item_seq`+`item_name`+`verified_at`+`method` 4필드로 충분한지.
3. **유형 B 1차 대상 성분**: 후보 문서 §3 기준 알렌드론산·토라세미드·목시플록사신·미노사이클린 4성분(성분당 정식명 1, 검증 통과분만)으로 시작할지.
4. **브랜드코어 포함 여부**: 1차는 정식 품목명만 / 브랜드코어(검증분)까지.
5. **진행 순서 승인**: (a) validator 일반화+픽스처 검증 단계 → PM 판정 → (b) 유형 B 데이터 편입 단계, 2단계 분리로 진행.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
