# MediStack v0.4 — alias 확장 후보 목록 설계

작성 기준일: 2026-06-08 / 단계: **설계만** (alias JSON 미수정, 코드·데이터·DATA_URL·deploy 무변경)
상위: `MediStack_v0.4_scope_and_plan.md` §3. 현행 운영 alias = `data/medistack_v0.3_aliases.json` (53개 = 성분 29 + 제품 24, live 13성분 제품 커버, 에스오메프라졸 제외).
PM 확정 우선순위: ①alias 확장 ②UX-B 카피 ③에스오메프라졸/15행 계속 보류 ④relation 확장 보류.

> 이 문서는 "무엇을 후보로 추가할지" 목록·기준·개수 현실성만 정의한다. 실제 alias 편입·검증·코드·배포는 PM 판정 후 별도.

---

## 0. 전제
- live 14성분(제품 13) **범위 내에서만**. 새 약물 alias는 relation 확장(보류) 동반 필요 → v0.4 제외.
- 에스오메프라졸 alias **계속 보류**(성분·제품 모두). nutrient 제품 alias 금지. 제품 추천/구매/제휴 금지.
- alias = 검색 보조. relation 신규생성·검색풀 확장 불가. prefix 매칭·fail-soft 유지.
- **순열 부풀리기 금지**(용량·띄어쓰기 변형을 entry로 양산 → 정규화로 흡수). **제네릭 전수 금지**(v0.5+).

## 1. 목적
검색 진입로를 늘려 체감 커버리지 향상. 단 **검증 가능·표준 명칭·중복 없음** 범위에서만. 숫자(100~150)를 위해 품질을 희생하지 않는다(§4에서 현실 검토).

## 2. 안전 net-new 후보 — 유형 A: 성분명(영문 INN·염 형태·표준 전사)
지금 바로 검증 가능(WHO INN/식약처 성분명 표준). 현행과 중복 제외한 **추가 후보**:

| 성분 | 추가 후보(성분 alias) | 비고 |
|---|---|---|
| 시프로플록사신 | ciprofloxacin hydrochloride, ciprofloxacin HCl | 염 영문 표준 |
| 메트포르민 | metformin hydrochloride, metformin HCl | 염 영문 표준 |
| 목시플록사신 | moxifloxacin hydrochloride, moxifloxacin HCl | 염 영문 표준 |
| 미노사이클린 | minocycline hydrochloride, minocycline HCl | 염 영문 표준 |
| 알렌드론산 | alendronate sodium, 알렌드론산나트륨수화물 | 염/수화물 표준 |
| 토라세미드 | 토르세미드 | 한글 전사 변형 |
| 레보티록신 | 레보티록신나트륨수화물 | 수화물 정식 표기 |
| 독시사이클린 | doxycycline hyclate(보유)·독시사이클린하이클레이트수화물 | 수화물 표기 |
| 레보플록사신 | 레보플록사신수화물(보유) — 추가 없음 | — |
| 오메프라졸 | (염 없음) 추가 없음 | — |
| 오플록사신 | (단순 INN) 추가 없음 | — |
| 푸로세미드 | furosemide/frusemide(보유) 추가 없음 | — |
| 히드로클로로티아지드 | hydrochlorothiazide/HCTZ/하이드로…(보유) 추가 없음 | — |

- 유형 A 순증: **약 +10~13**(중복·과도한 기술명 제외).
- "HCl" 같은 축약은 prefix 매칭상 "hcl"로 시작해야 매칭 → 단독 "hcl" 검색은 무의미하나 "metformin hcl" 전체 입력 케이스 보조. 가치 낮으면 드롭 가능(§9 PM).

## 3. 안전 net-new 후보 — 유형 B: 교차확인 2번째 품목(검증 필요)
- v0.2 Phase 2에서 신규클래스·안전민감 행에 대해 **동일 성분 2번째 품목 원문 교차확인**을 수행함(비스포스포네이트=알렌드론산, 칼륨계열=토라세미드 등). 그 교차확인 품목의 **정식명/브랜드코어**가 제품 alias 후보.
- **단, 2번째 itemSeq·품목명은 현재 relation 데이터에 없음**(relation source는 대표 itemSeq 1개만). → v0.2 phase2 문서에서 회수하거나 **gstack browse로 재확인** 후에만 편입.
- 후보(품목명은 검증 전 미확정, 성분만 표시): 알렌드론산 2nd, 토라세미드 2nd, 목시플록사신 2nd, 미노사이클린 2nd 등.
- 순증: **약 +4~10**(성분당 정식명 1 + 브랜드코어 1, 검증 통과분만).
- ⚠️ validator 충돌(§6): 현 validator #8은 "item_seq가 그 성분 **relation의** itemSeq 집합에 속함"을 요구 → 2번째 itemSeq는 relation에 없어 **FAIL**. 일반화 필요.

## 4. 개수 현실성 — 정직한 검토 (중요)
- 유형 A(+10~13) + 유형 B(+4~10) = **현행 53 → 약 67~76**.
- **100~150은 위 두 유형만으로 도달 불가.** 도달하려면 셋 중 하나 필요:
  1. **성분당 추가 대표 브랜드 N종**(검증된 실제 식약처 품목) — "대표품목 1종" 규칙 완화. 제네릭 전수는 아님(상위 브랜드 1~3종). v0.5의 제네릭 트랙과 경계가 모호 → **범위 결정 필요**.
  2. 용량/제형/띄어쓰기 변형을 entry로 추가 — **금지(정규화로 흡수)**. 채택 안 함.
  3. v0.5로 미룸 — v0.4 목표를 **현실치(약 70~90)**로 재설정.
- **권고:** v0.4 목표를 **80~100**으로 재설정(유형 A 전량 + 유형 B 검증분 + 성분당 검증된 추가 브랜드 1종까지 허용). 150은 v0.5 제네릭 트랙으로. (PM §9-1 결정)
- 원칙 재확인: **숫자 맞추려 미검증/순열 alias 만들지 않는다.**

## 5. 후보 수집 SOP (편입 전 절차)
1. 유형 A: 표준 명칭 대조(중복 제거) → 바로 후보 확정 가능.
2. 유형 B/추가 브랜드: **식약처 품목명·itemSeq를 browse로 확인**(상품명 실재 + 해당 성분). 미확인 시 드롭.
3. 각 alias: canonical_ingredient = live 성분 정확 일치. product는 item_seq + source_relation_ids(그 성분 live ids).
4. prefix 매칭 충돌 점검(짧은 alias가 다른 성분 alias의 접두가 되어 오매칭 나는지).
5. validator(확장 포함) PASS + 로컬 검색 QA.

## 6. validator 영향 / item_seq 규칙 일반화
2번째/추가 품목 alias를 허용하려면 현 `validate_medistack_v0_3_aliases.py` 확장 필요:
- **현행 #8:** product alias item_seq ∈ 해당 성분 **relation의** itemSeq 집합 → 추가 품목 itemSeq는 FAIL.
- **일반화안:** "성분 단위 **허용 itemSeq 화이트리스트**"로 확장. 화이트리스트 = relation itemSeq ∪ (alias 파일 meta에 명시한 검증된 추가 itemSeq). 추가 itemSeq는 **검증 출처(browse 확인일·품목명)를 alias 데이터 또는 docs에 기록**.
- 신규 체크 후보: meta.alias_count 일치 / lang∈{ko,en} / item_seq 숫자형식 / 정규화 충돌 가드 / (비차단)커버리지 경고.
- 회귀: v0.1/v0.2/v0.3 동작·게이트 무영향. CI 3종 유지.

## 7. QA 케이스(편입 단계에서)
- 유형 A 표본: "ciprofloxacin hydrochloride"→시프로플록사신(4·5·6), "토르세미드"→토라세미드(30·31), "alendronate sodium"→알렌드론산(29).
- 유형 B 표본: 교차확인 품목명→해당 성분 live ids, item_seq 화이트리스트 통과.
- prefix 오매칭 없음(예: 신규 영문 alias가 다른 INN 접두와 충돌 안 함).
- 넥시움/esomeprazole→0건 유지. #/r/15 미노출. 제품/구매 UI 없음.
- alias validator(확장) PASS + v0.1/v0.2 PASS. 라이브 회귀(목록 30/콘솔0/칼륨3).

## 8. 제외 / 금지 (v0.4 alias)
- 에스오메프라졸 alias(성분·제품) 전부.
- nutrient(영양소) 제품 alias.
- 제네릭 전수(상위 1종 초과 대량) → v0.5+.
- 용량·띄어쓰기·대소문자 순열 entry(정규화로 흡수).
- 오타·속어·미검증 상품명.
- 제품 링크/가격/구매/제휴 필드.

## 9. PM 판정 필요사항
1. **목표치 재설정** — 권고 80~100(품질) vs 원안 100~150(추가 브랜드 검증 필요). 150 도달 위해 "성분당 추가 대표 브랜드 N종" 허용할지/제한 수.
2. **유형 B(교차확인 2번째 품목) 편입 여부** + validator item_seq 화이트리스트 일반화 승인.
3. **유형 A 축약("HCl" 등) 포함 여부** — 가치 낮으면 드롭.
4. **추가 브랜드 검증 방식** — browse로 식약처 품목 확인 후 편입(검증 출처 기록).
5. **편입 진행 방식** — 본 후보 승인 후 (a)유형 A 먼저 일괄 편입 → (b)유형 B/브랜드는 검증 트랙 분리, 단계별 PM 판정.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
