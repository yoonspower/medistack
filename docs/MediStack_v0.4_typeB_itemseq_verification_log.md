# MediStack v0.4 — 유형 B(A군) itemSeq 원문 확인 로그

작성/확인일: **2026-06-11** / 단계: **원문 확인 로그만** (alias JSON·`verified_item_seqs`·데이터·코드·deploy 미변경)
상위: `MediStack_v0.4_typeB_alias_candidates.md`(A군 후보), `MediStack_v0.4_validator8_typeB_design.md`(validator #8 일반화).

> A군 4성분의 **2번째 공식 품목(itemSeq·품목명)** 을 식약처 nedrug 원문에서 직접 확인한 기록.
> **확정 itemSeq는 추정 아님** — 각 품목의 `getItemDetail` 상세 원문에서 주성분(ingrName)·품목명을 직접 확인.
> 이 문서는 **로그/초안만**. alias JSON 편입은 PM 판정 후 별도 단계.

---

## 0. 확인 방법(SOP, 재현 가능)
1. **검색**: nedrug 주성분 검색 `https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1=<성분명>` → 동일 주성분 품목 목록.
2. **선정 기준**: 대표(1번째) 품목과 **동일 경구 제형·동일 용량**, **단일성분**(복합제 제외), **완제의약품**(원료 제외), **비수출용**(수출용/수출명 제외), **다른 브랜드**.
   - 근거: relation 30건은 **경구 흡수 상호작용**(다가양이온 킬레이트로 흡수 저하 등)이라, 2번째 품목도 동일 경구 제형이어야 임상 맥락이 일치. 점안액·치과용연고·주사제·원료·수출용은 제외.
3. **확정 검증**: 선정 품목의 `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=<seq>` 상세 원문에서 **품목명(title)·주성분(ingrName)·성분코드(ingrCode)** 직접 확인.

## 1. 확인 결과 — A군 4성분 (전부 확인 성공, 보류 0건)

| canonical_ingredient | 1번째(대표·기존 relation) itemSeq / 품목명 | **2번째(신규 확정) itemSeq** | 2번째 품목명(원문 title) | 주성분(원문 ingrName) | ingrCode | 제형/용량 일치 | status |
|---|---|---|---|---|---|---|---|
| 알렌드론산 | 200009061 / 포사맥스70밀리그램정 | **201902246** | 라이트알렌드론정70mg | 알렌드론산나트륨수화물 | M222873 (포사맥스와 **동일 코드**) | 경구정 70mg = 70mg ✓ | verified |
| 토라세미드 | 200611522 / 토렘정5밀리그람 | **200600084** | 세토람정5밀리그람 | 토라세미드 | M087101 | 경구정 5mg = 5mg ✓ | verified |
| 목시플록사신 | 201402438 / 리목스정400mg | **201309618** | 모록사신정400밀리그램 | 목시플록사신염산염 | M247915 | 경구정 400mg = 400mg ✓ | verified |
| 미노사이클린 | 198501028 / 미노씬캡슐50mg | **202500078** | 미노젠캡슐50밀리그램 | 미노사이클린염산염 | M223036 | 경구캡슐 50mg = 50mg ✓ | verified |

- **확인 성공: 4/4.** 확인 실패/보류: 0.
- 4종 모두 **대표 itemSeq와 다른 itemSeq**(중복 아님), **동일 주성분·동일 경구 제형·동일 용량·단일성분·완제·비수출**.
- 알렌드론산은 ingrCode(M222873)가 대표(포사맥스)와 **동일**해 주성분 동일성 교차확인까지 완료. 나머지 3종은 주성분 검색(ingrName1) 결과 + 상세 원문 ingrName 일치로 확인.

## 2. 원문 출처 URL (확인일 2026-06-11)
- 알렌드론산 2nd: `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=201902246` (검색: ingrName1=알렌드론산)
- 토라세미드 2nd: `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=200600084` (검색: ingrName1=토라세미드)
- 목시플록사신 2nd: `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=201309618` (검색: ingrName1=목시플록사신)
- 미노사이클린 2nd: `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=202500078` (검색: ingrName1=미노사이클린)

## 3. 편입 단계용 `verified_item_seqs` 초안 (⚠️ 아직 alias JSON 미반영 — 초안만)

> validator #8 일반화(#12 성분 키 라이브 실재·#13 엔트리 위생) 기준에 맞춘 구조. **이 단계에서 alias JSON에 넣지 않는다.** PM 판정(위치·메타) 후 편입.

```json
"verified_item_seqs": {
  "알렌드론산": [
    {"item_seq": "201902246", "item_name": "라이트알렌드론정70mg", "verified_at": "2026-06-11", "method": "nedrug getItemDetail ingrName=알렌드론산나트륨수화물(M222873)"}
  ],
  "토라세미드": [
    {"item_seq": "200600084", "item_name": "세토람정5밀리그람", "verified_at": "2026-06-11", "method": "nedrug getItemDetail ingrName=토라세미드(M087101)"}
  ],
  "목시플록사신": [
    {"item_seq": "201309618", "item_name": "모록사신정400밀리그램", "verified_at": "2026-06-11", "method": "nedrug getItemDetail ingrName=목시플록사신염산염(M247915)"}
  ],
  "미노사이클린": [
    {"item_seq": "202500078", "item_name": "미노젠캡슐50밀리그램", "verified_at": "2026-06-11", "method": "nedrug getItemDetail ingrName=미노사이클린염산염(M223036)"}
  ]
}
```

- 키 = canonical_ingredient(라이브 relation 성분 단축형) → validator #12 통과(4종 모두 live_ings, excluded·에스오메프라졸 아님).
- item_seq 숫자형·성분내 단일·금지필드 없음 → validator #13 통과.

## 4. 동반 product_alias 후보 (편입 단계 결정, ⚠️ 아직 미반영)
편입 시 각 2번째 품목을 `kind=product` alias로 추가할 수 있다. **alias 표면형(전체 품목명 vs 브랜드코어)은 PM 판정(브랜드코어 허용 §9-3)**.

| canonical_ingredient | item_seq | 전체 품목명(alias 후보) | 브랜드코어(축약 후보) | source_relation_ids |
|---|---|---|---|---|
| 알렌드론산 | 201902246 | 라이트알렌드론정70mg | 라이트알렌드론정 | [29] |
| 토라세미드 | 200600084 | 세토람정5밀리그람 | 세토람정 | [30, 31] |
| 목시플록사신 | 201309618 | 모록사신정400밀리그램 | 모록사신정 | [24, 25] |
| 미노사이클린 | 202500078 | 미노젠캡슐50밀리그램 | 미노젠캡슐 | [26, 27, 28] |

- 토라세미드(relation 30, `product_link_allowed=false`)는 **검색→칼륨 안전카드 노출만**, 구매/링크 금지(필드 없음).
- source_relation_ids 는 해당 성분 라이브 relation id(편입 시 validator #6·#7 정합).

## 5. 다음 단계 (편입 가능 여부)
- **4종 원문 확인 완료 → 편입 기술적으로 가능**(validator #8 일반화 완료·검증 데이터 확보).
- **PM 판정 대기**: ① `verified_item_seqs` 위치(파일 내 섹션 = validator 구현 형태 / 별도 파일) ② alias 표면형(전체 품목명 / 브랜드코어) ③ A군 4종 일괄 vs 단계 편입.
- 판정 후 편입 단계: `verified_item_seqs`(위 초안) + product_alias N건 추가 → validator 13/13 + test suite + smoke + 회귀 → alias_count 62→62+N → 커밋·push·deploy.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
