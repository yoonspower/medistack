# MediStack v0.4 — 유형 A(성분명) alias 편입안

작성 기준일: 2026-06-08 / 단계: **편입안(계획)만** (alias JSON·코드·데이터·DATA_URL·deploy 미변경)
상위: `MediStack_v0.4_alias_expansion_candidates.md`(유형 A/B 정의), `MediStack_v0.4_scope_and_plan.md`.
현행 운영 alias: `data/medistack_v0.3_aliases.json` = 53개(성분 29 + 제품 24). PM 확정 목표 v0.4 = **80~100**.

> 이 문서는 유형 A로 **추가할 정확한 성분명 alias 목록**과 근거·검증 영향만 정의한다. 실제 JSON 편입·검증·배포는 PM 판정 후 별도.
> 범위 한정(PM): **유형 A 성분명만**. 유형 B(교차확인 2번째 품목)·추가 브랜드·에스오메프라졸·15행·relation 확장 **전부 제외**.

---

## 0. 원칙
- live 14성분 범위, **성분명(kind=ingredient)만**. 제품 alias 추가 없음.
- **표준 명칭만**: 영문 염 형태(INN+salt) / 한글 염·수화물 정식 표기 / 표준 전사 변형. 순열·축약 부풀리기·미검증 금지.
- 현행 53개와 **중복 제외**(net-new만). 에스오메프라졸 alias 없음.

## 1. 추가 후보 (net-new 9건) — 확정안
모두 `kind: ingredient`. canonical_ingredient는 live 성분과 정확 일치.

| # | alias | canonical_ingredient | lang | 근거 |
|---|---|---|---|---|
| 1 | ciprofloxacin hydrochloride | 시프로플록사신 | en | 한글 "시프로플록사신염산염"(보유)의 영문 정식 염 표기 |
| 2 | metformin hydrochloride | 메트포르민 | en | 한글 "메트포르민염산염"(보유)의 영문 |
| 3 | moxifloxacin hydrochloride | 목시플록사신 | en | 한글 "목시플록사신염산염"(보유)의 영문 |
| 4 | minocycline hydrochloride | 미노사이클린 | en | 한글 "미노사이클린염산염"(보유)의 영문 |
| 5 | alendronate sodium | 알렌드론산 | en | "alendronate"(보유)의 염 정식 표기(Fosamax 성분) |
| 6 | 알렌드론산나트륨수화물 | 알렌드론산 | ko | **relation 원문 품목명에 실재**(포사맥스70밀리그램정 성분 표기). 현행은 "알렌드론산나트륨"만 |
| 7 | 레보티록신나트륨수화물 | 레보티록신 | ko | **relation 원문에 실재**(씬지로이드정 성분 표기). 현행은 "레보티록신나트륨"만 |
| 8 | 독시사이클린하이클레이트수화물 | 독시사이클린 | ko | **relation 원문에 실재**(국제독시사이클린하이클레이트수화물캡슐). 현행은 "독시사이클린하이클레이트"만 |
| 9 | 토르세미드 | 토라세미드 | ko | "torsemide"(보유 영문)의 한글 전사 변형(토라세미드↔토르세미드 통용) |

- 6·7·8은 **우리 relation source.pointer 원문에 실제 등장하는 정식 성분 표기**(검증 완료, 위 Bash 확인).
- 1~5는 이미 보유한 한글 염 표기/영문 INN의 **표준 영문 염 형태**(신규 의미 아님, 표기 보강).
- 9는 표준 전사 변형.

## 2. 중복/충돌 점검
- **중복 없음**: 위 9건 모두 현행 53개에 미존재(성분별 현행 목록과 대조).
- **prefix(startsWith) 충돌 없음**: 신규 alias가 다른 성분 alias의 접두가 되어 오매칭되는 경우 없음.
  - 영문 "...hydrochloride"·"alendronate sodium"은 각 성분 고유 어두 → 타 성분 매칭 불가.
  - 한글 "...수화물"·"토르세미드"는 해당 성분 고유.
  - (참고: v0.3에서 잡았던 "ofloxacin⊂levofloxacin" 류는 **substring** 문제였고, 현재 alias 매칭은 **prefix**라 재발 없음. 신규 9건도 prefix 기준 안전.)

## 3. 제외(이번 유형 A에서 안 함)
- 무(無) net-new 성분: 레보플록사신·오메프라졸·오플록사신·푸로세미드·히드로클로로티아지드 — 표준 추가 표기 없음(이미 충분).
- **"HCl" 축약형**(ciprofloxacin hcl 등 4종): 가치 낮음(prefix상 "hcl" 단독은 무의미, 전체 입력시만 보조). **이번 편입 제외**, 필요 시 PM 별도 판정(§5-2).
- 유형 B(교차확인 2번째 품목)·추가 브랜드 제품 alias: 별도 트랙(validator #8 일반화 후).
- 에스오메프라졸 성분/제품 alias, nutrient alias: 보류/금지 유지.

## 4. 편입 후 개수 / validator 영향
- 편입 후: 53 → **62** (성분 29→38, 제품 24 유지). 목표 80~100의 **1차 증분**(유형 B + 검증 브랜드가 후속 채움).
- **validator 변경 불필요**: 9건 전부 `kind=ingredient` → item_seq/source_relation_ids 무관(현 validator #8은 product만 검사). 현 11-check 그대로 PASS 예상.
  - meta.alias_count는 53→62로 갱신 필요(현 validator는 alias_count 미검사라 FAIL 안 나지만, 데이터 일관성 위해 갱신).
- 회귀: v0.1/v0.2/v0.3 export·게이트 무영향. CI 3종 유지.

## 5. 편입 절차(승인 후) / QA
1. `data/medistack_v0.3_aliases.json`의 `ingredient_aliases`에 9건 append + `meta.alias_count` 62로 갱신.
2. v0.3 alias validator PASS(11/11) + v0.1/v0.2 PASS 확인.
3. 로컬 검색 QA: "ciprofloxacin hydrochloride"→시프로플록사신(4·5·6), "토르세미드"→토라세미드(30·31), "alendronate sodium"→알렌드론산(29), "독시사이클린하이클레이트수화물"→독시사이클린(7·8·9). prefix 오매칭 없음. 넥시움/esomeprazole→0건 유지. #/r/15 미노출.
4. 단계별 PM 판정 → 커밋 → push → deploy 게이트(3종) → 라이브 회귀.

## 6. PM 판정 필요사항
1. **9건 편입 확정** 여부(그대로 / 일부 제외).
2. **"HCl" 축약 4종** 포함 여부(기본 제외 권고).
3. 편입을 **이번 단계에서 진행**할지(첫 alias 데이터 변경) / 본 편입안만 커밋 후 별도 단계로.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
