# MediStack v0.4 — 유형 B(교차확인 2번째 품목) alias 편입 후보안

작성 기준일: 2026-06-11 / 최종 갱신: 2026-06-11 / 단계: **A군 4종 편입·라이브 완료** + B군 후보 분류
상위: `MediStack_v0.4_alias_expansion_candidates.md`(§3 유형 B 정의), `MediStack_v0.4_validator8_typeB_design.md`(validator #8 일반화 — **구현·배포 완료**, 커밋 189b401).

> **A군 4종은 itemSeq 원문 확인 → alias JSON 편입 → 라이브 반영 완료**(2026-06-11, 커밋 9fdf97b, Actions run 27321963167 success). B군 이하는 후보 분류 단계로 유지.
> B군의 `expected_item_seq`는 미검증 추정값을 박지 않고 `TBD`로 둔다(원문 browse 확인 = 편입 전 게이트, §7).

---

## 1. 현재 상태 요약
- **alias_count = 66**(성분 38 + 제품 28). 라이브 v0.3-beta. (A군 Type B product alias 4건 편입, 62→66.)
- **relation = 30**(v0.2 export, 불변). DATA_URL = `./data/medistack_v0.2_beta_export.json`(불변).
- **validator #8 일반화 완료**(189b401): `item_seq ∈ (성분 relation itemSeq ∪ 검증 화이트리스트 itemSeq)`. 화이트리스트 가드 #12(성분 키 정당성)·#13(엔트리 위생) 추가. 실제 파일 **13/13 PASS**, 유형 B test suite **7/7 PASS**.
- **✅ A군 4종 편입·라이브 완료(2026-06-11, 커밋 9fdf97b, Actions run 27321963167 success, deploy success)**: `verified_item_seqs` 섹션 4성분 + product_alias 4건 라이브 반영. §5-A 표 incorporated. 채록 로그 = `MediStack_v0.4_typeB_itemseq_verification_log.md`.
- **에스오메프라졸/15행 제외 유지**, relation 30·DATA_URL 불변.

## 2. 유형 B alias 정의
- **같은 canonical_ingredient에 귀속되는 2번째(이후) 공식 품목명/제품명 alias** (`kind: product`).
- **검색 보조 전용**: 의학정보·복약지시 아님. 매칭 결과 = 기존 라이브 relation 카드뿐.
- **relation 신규 생성 금지**: relation 풀·내용·개수(30) 불변. alias는 기존 relation 검색만 보조.
- **구매/제품 추천 UI와 연결 금지**: 제품 링크·구매 버튼·제휴·가격 필드 없음(앱에 제품 UI 자체 없음). 칼륨 행은 검색→안전카드 노출만 허용, 구매/링크 금지.

## 3. 후보 선정 기준 (전부 충족해야 후보)
1. **식약처(nedrug) 공식 품목명 또는 명확한 대표 품목명 기반** — 실재 품목 + 동일 성분.
2. **기존 relation의 canonical_ingredient와 연결 가능** — 라이브 14성분(에스오메프라졸 제외 13) 한정. 신규 성분 불가(validator #4).
3. **`verified_item_seqs`에 item_seq를 기록할 수 있는 후보만** — browse로 itemSeq 채록·확인일 기록 가능해야 함. 채록 불가 시 드롭.
4. **에스오메프라졸/15행 제외** — 성분/제품 alias 모두 금지(validator #9·#12, 15행 우회 가드).
5. **칼륨 제품 링크/구매 UI 금지** — 칼륨 행(푸로세미드 17·히드로클로로티아지드 19·토라세미드 30, `product_link_allowed=false`)은 검색→안전카드만, 구매/링크 연결 금지.
6. **미검증 브랜드 alias 제외** — itemSeq 미확인 브랜드, 추정 품목명 금지.
7. **순열 부풀리기 금지** — 용량/제형/띄어쓰기 변형은 런타임 정규화로 흡수. entry로 추가 금지.

## 4. 후보군 분류

**A. 즉시 검토 가능 후보** — v0.2 Phase 2에서 **이미 동일 성분 2번째 품목 원문 교차확인을 수행**한 안전민감/신규클래스 성분. 2nd 공식 품목 존재 가능성 높고 검증 = nedrug 1회 조회.
- 알렌드론산, 토라세미드, 목시플록사신, 미노사이클린.

**B. 추가 원문 확인 필요 후보** — 라이브 성분이나 2nd 품목의 검색 가치·실재를 browse로 더 확인해야 함.
- 레보플록사신, 시프로플록사신, 독시사이클린, 레보티록신, 메트포르민, 오메프라졸, 오플록사신, 푸로세미드, 히드로클로로티아지드.

**C. v0.5 이후 이관 후보**
- 성분당 추가 대표 브랜드 N종(상위 1~3), 제네릭 대량(300밴드 전수). 유형 B(성분당 정식명 1)와 경계 분리.

**D. 제외 후보**
- 에스오메프라졸(15행/보류), 칼륨 행의 구매/제품 링크 연결, itemSeq 미확인 브랜드, 용량/제형/띄어쓰기 순열.

## 5. 후보 표

> status: `incorporated`(라이브 반영 완료) / `needs_verification`(browse 채록 대기) / `needs_PM_decision`(브랜드코어 등) / `deferred`(v0.5) / `excluded`. B군 이하의 `expected_item_seq`/`candidate_alias`는 **browse 확정 전 미확정 = TBD**.

### 5-A. ✅ **편입·라이브 완료(2026-06-11, 4/4, 커밋 9fdf97b)**

> itemSeq·품목명은 nedrug `getItemDetail` 상세 원문에서 직접 확인(주성분·제형·용량 일치) 후 alias JSON 편입. 채록 상세: `MediStack_v0.4_typeB_itemseq_verification_log.md`.
> PM 판정: 표면형 = **전체 품목명**, verified_item_seqs = **alias JSON 파일 내 섹션**, A군 4종 **일괄 편입**. `incorporated` = 라이브 반영 완료.

| candidate_alias | canonical_ingredient | expected_item_seq | expected_item_name | source_to_verify | reason | risk | status |
|---|---|---|---|---|---|---|---|
| 라이트알렌드론정70mg | 알렌드론산 | **201902246** | 라이트알렌드론정70mg(알렌드론산나트륨수화물) | nedrug getItemDetail 201902246 확인(ingrCode M222873=포사맥스와 동일) | 비스포스포네이트, 대표 200009061 외 경구정 70mg 단일성분 | low | **incorporated** |
| 세토람정5밀리그람 | 토라세미드 | **200600084** | 세토람정5밀리그람(토라세미드) | nedrug getItemDetail 200600084 확인(ingrName 토라세미드) | 칼륨 안전민감(행 30). 검색→안전카드만, **구매/링크 금지** | med(칼륨 행) | **incorporated** |
| 모록사신정400밀리그램 | 목시플록사신 | **201309618** | 모록사신정400밀리그램(목시플록사신염산염) | nedrug getItemDetail 201309618 확인(ingrName 목시플록사신염산염) | 플루오로퀴놀론, 대표 201402438 외 경구정 400mg 단일성분 | low | **incorporated** |
| 미노젠캡슐50밀리그램 | 미노사이클린 | **202500078** | 미노젠캡슐50밀리그램(미노사이클린염산염) | nedrug getItemDetail 202500078 확인(ingrName 미노사이클린염산염) | 테트라사이클린계, 대표 198501028 외 경구캡슐 50mg 단일성분 | low | **incorporated** |

### 5-B. 추가 원문 확인 필요 (검색 가치·실재 확인 후 편입 여부 판정)

| candidate_alias | canonical_ingredient | expected_item_seq | expected_item_name | source_to_verify | reason | risk | status |
|---|---|---|---|---|---|---|---|
| (2nd 품목명 — browse) | 레보플록사신 | TBD | TBD | nedrug "레보플록사신"(대표 199900886 외) | 다빈도 항생제, 2nd 품목 검색 가치 확인 필요 | low | needs_verification |
| (2nd 품목명 — browse) | 시프로플록사신 | TBD | TBD | nedrug "시프로플록사신"(대표 199901094 외) | 다빈도 항생제 | low | needs_verification |
| (2nd 품목명 — browse) | 독시사이클린 | TBD | TBD | nedrug "독시사이클린"(대표 198000105 외) | 테트라사이클린계 | low | needs_verification |
| (2nd 품목명 — browse) | 레보티록신 | TBD | TBD | nedrug "레보티록신"(대표 201903264 외) | 갑상선, 씬지로이드 외 품목 확인 | low | needs_verification |
| (2nd 품목명 — browse) | 메트포르민 | TBD | TBD | nedrug "메트포르민"(대표 200709701 외) | 다빈도 당뇨약, 품목 매우 많음 → 대표 1건만 | low | needs_verification |
| (2nd 품목명 — browse) | 오메프라졸 | TBD | TBD | nedrug "오메프라졸"(대표 200411095 외) | PPI. **에스오메프라졸과 혼동 금지**(별개 성분) | med(혼동) | needs_verification |
| (2nd 품목명 — browse) | 오플록사신 | TBD | TBD | nedrug "오플록사신"(대표 198600307 외) | 타리비드 외 품목 | low | needs_verification |
| (2nd 품목명 — browse) | 푸로세미드 | TBD | TBD | nedrug "푸로세미드"(대표 196400037 외) | 칼륨 안전민감(행 17). 검색→안전카드만, **구매/링크 금지** | med(칼륨 행) | needs_verification |
| (2nd 품목명 — browse) | 히드로클로로티아지드 | TBD | TBD | nedrug "히드로클로로티아지드"(대표 196000008 외) | 칼륨 안전민감(행 19). 검색→안전카드만, **구매/링크 금지** | med(칼륨 행) | needs_verification |

### 5-C/D. 이관·제외

| candidate_alias | canonical_ingredient | expected_item_seq | expected_item_name | source_to_verify | reason | risk | status |
|---|---|---|---|---|---|---|---|
| 브랜드코어 N종(성분당 1~3) | (라이브 성분 전반) | — | — | v0.5 트랙 | 유형 B(정식명 1) 초과분 = 브랜드 트랙 | — | deferred |
| 제네릭 대량(300밴드) | (전반) | — | — | v0.5 트랙 | 범위 분리 | — | deferred |
| (임의 품목/추정) | 에스오메프라졸 | — | — | — | 15행/보류, alias 금지(#9·#12) | high | excluded |
| 용량/제형/띄어쓰기 변형 | (전반) | — | — | — | 런타임 정규화로 흡수, entry 금지 | — | excluded |

## 6. v0.4 유형 B 순증 현황/목표
- **✅ A군 4종 편입 완료 → alias_count 62 → 66**(검증 통과분만 반영, 미검증/순열 금지).
- 추가 순증 후보: B군(추가확인 9성분) 검증 통과분 + 브랜드코어(§9 PM 판정). 브랜드코어 허용 시 70대 후반~80대.
- **숫자 자체를 목표로 삼지 않는다** — 원문 검증 통과분만. 80~100 무리한 채우기 금지.

## 7. 편입 단계 체크리스트 (A군 ✅ 완료 / B군은 동일 절차 재사용)
A군은 아래를 전부 통과해 라이브 반영(커밋 9fdf97b). B군 편입 시 동일 절차 반복:
1. **item_seq 원문 확인**: nedrug browse → 품목명 실재 + 동일 성분 + itemSeq 채록 + 확인일 기록. 미확인 드롭. (A군: §5-A·로그문서 완료)
2. **`verified_item_seqs` 위치/메타**: PM 확정 = **alias JSON 파일 내 섹션**, 메타 item_seq·item_name·verified_at·method.
3. **product_alias 추가**: 전체 품목명 → `kind=product`, canonical=성분, item_seq=채록값, source_relation_ids=라이브 relation id.
4. **validator 13/13 PASS**(v0.1 12/12·v0.2 15/15·v0.3 alias 13/13).
5. **유형 B test suite 7/7 PASS**(`scripts/test_validate_v0_3_typeB.py`).
6. **smoke test**: 신규 alias → 해당 성분 relation만 매칭(건수), prefix 오매칭 없음. 회귀(타리비드/포사맥스/토렘/넥시움0/#r15 fail-safe).
7. **alias_count 증가 확인**(A군: 62 → 66).
8. **relation 30 유지·DATA_URL 유지 확인**.

## 8. 아직 하지 않을 것 (이 단계 금지)
- alias JSON 수정 / 유형 B alias 실제 추가.
- relation 확장·수정 / data export 수정 / DATA_URL 변경 / validator·코드 추가 수정.
- 에스오메프라졸 alias 추가, 15행 재편입.
- 제품/구매/제휴 UI 추가, published/clinical_reviewed 전환.
- itemSeq 미검증 추정값 기록(표의 TBD를 임의 숫자로 채우지 않음).

## 9. PM 판정 — 진행 현황
**A군 관련(✅ 판정·반영 완료):**
1. `verified_item_seqs` 위치 → **alias JSON 파일 내 섹션**.
2. A군 4종 → **일괄 편입 완료**(전체 품목명).
4. item_seq 검증 출처 → **nedrug getItemDetail 원문**(확인일·method 메타 기록).

**B군 이후(판정 대기):**
3. **브랜드코어 허용 여부**: 1차 정식 품목명만 / 검증된 브랜드코어까지(80대 가능).
5. **B군 편입 범위·v0.4 alias 목표**: 70대(정식명 위주) vs 80대(브랜드코어 포함).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
