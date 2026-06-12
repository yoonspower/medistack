# MediStack v1.0 — Full Drug Name Search Index 분리 설계 (v1.0-B)

> 자기완결 설계 문서. v1.0-B 트랙. **문서만 작성한다.**
> relation 30 · alias 621은 **그대로 유지**하고, relation 없는 약도 검색 결과에 **"품목명 확인만 가능 / 등록된 약-영양소 참고정보 없음"** 으로 표시할 수 있는 **별도 full drug name search index** 구조를 설계한다.
> **full drug index 파일 실제 생성 금지**(설계만). 코드·데이터·alias·queue·validator·src·relation·DATA_URL·export·tag 일절 수정하지 않는다.

---

## 0. 현행 검색 아키텍처 (설계 근거)

실제 `src/js/*`에서 확인한 현행 구조:

| 파일 | 역할 | 실패 정책 |
|---|---|---|
| `data.js` `DATA_URL` | relation export(`medistack_v0.2_beta_export.json`) | **fatal** (throw) |
| `data.js` `ALIAS_URL` | alias(`medistack_v0.3_aliases.json`) | **fail-soft** (실패/HTTP≠200/shape 불일치 → `null` → relation-only) |
| `guards.js` `getRenderableRelations` | 렌더 풀(30 relation, **15행/excluded 구조적 제외**) | — |
| `guards.js` `buildAliasIndex` | 런타임 인덱스 `[{alias(norm), canonical(norm)}]`, malformed skip | alias 부재 시 `[]` |
| `app.js` 검색 | `getRenderableRelations` 풀을 `filterRelations(rels, …, aliasIndex)` 로 필터 | alias 실패해도 relation-only 정상 |

**핵심 사실:** 검색은 **항상 relation 풀(30)만** 결과로 낸다. alias는 질의를 canonical_ingredient로 해석해 **relation 있는 약**으로 연결할 뿐이다. → **relation 없는 약을 검색하면 무조건 "결과 없음"(empty).**

현행 alias 스키마(참고):
- `product_alias` = `{alias, canonical_ingredient, kind:"product", lang, item_seq, source_relation_ids:[…]}`
- `verified_item_seqs` = canonical별 `[{item_seq, item_name, verified_at, method, …}]`

본 설계는 이 fail-soft·별도 파일 패턴(ALIAS_URL)을 **세 번째 인덱스로 재사용**한다.

---

## 1. 현재 문제

- relation-linked alias(621)만으로는 사용자가 흔한 약을 검색해도 **"결과 없음"이 많다**. 현재 검색 커버리지 = relation 30 + 그에 연결되는 alias 621뿐.
- **체감 완성도 문제:** 품목명이라도 확인되면 "이 약은 존재하는데 참고정보가 아직 없다"는 신뢰 신호가 된다. 반면 "결과 없음"은 "검색이 안 되는 앱"으로 오해된다.
- 단, 커버리지 확장이 **의학 정보(상호작용 카드) 확장으로 오인되면 안 된다.** → relation DB와 **분리**가 전제.

---

## 2. 핵심 원칙

- **relation 30 확장 금지.** 의학적 판단 / 상호작용 카드 확장 금지.
- full drug name index는 relation DB와 **물리적·논리적 분리**(별도 파일 · 별도 fetch · 별도 validator).
- relation 없는 약은 **정보 없음(name_only) 상태로만** 표시.
- 복용 판단 / 추천 금지. 제품 / 구매 / 제휴 금지.
- full index는 **품목명 확인용**이지 medical 정보가 아니다(alias와 동일한 위치: 검색 보조).

---

## 3. 데이터 구조 설계

**세 인덱스 분리:**

| 인덱스 | 파일 | 내용 | 상태 |
|---|---|---|---|
| relation_alias_index | `data/medistack_v0.3_aliases.json` (현행) | alias 621 → canonical → relation | **불변** |
| relation export | `data/medistack_v0.2_beta_export.json` (현행) | relation 30 | **불변** |
| **full_drug_name_index** | **(신규 별도 파일, 본 설계 = 미생성)** | 전체 품목명 | **설계만** |

**full_drug_name_index 엔트리 스키마 초안 (append-only, 미적용):**
```json
{
  "item_seq": "199900886",                  // 1차 키(고유)
  "item_name": "...",                        // 품목명(표면형, 개행 정제 적용)
  "ingredient_name": "...",                  // 주성분명
  "company_name": "...",                     // 업체명
  "covered_by_relation": false,              // true → relation_card 경로로 위임
  "display_mode": "name_only",               // relation_card | name_only
  "no_relation_notice_required": true,       // name_only 필수 고지 플래그
  "source_checked_at": "2026-07-01T00:00:00+09:00",
  "source_method": "nedrug.searchDrug"       // nedrug.searchDrug | nedrug.getItemDetail
}
```

설계 규칙:
- **itemSeq = 1차 키(고유).** full index 내 중복 금지.
- **충돌 위임:** alias의 `item_seq`(또는 relation의 itemSeq)와 겹치면 그 엔트리는 `covered_by_relation=true` + `display_mode=relation_card`로 두어 **표시를 relation 경로에 위임**(중복 카드 금지). full index의 본질은 `name_only`.
- meta: `index_kind="full_drug_name"`, `count`, `source_basis`, `schema_version`. **relation/alias와 교차 불변 검증**(relation_count=30, alias_count=621 참조).

---

## 4. UX 설계

검색 결과를 **3-상태로 구분**(현재는 1·3만 존재, 2가 신설):

| 상태 | 조건 | 표시 |
|---|---|---|
| ① relation 있음 | relation 직접/alias 매칭 | **기존 relation_card** (고지·관리·source) |
| ② relation 없음 + full index 있음 | full_drug_name_index 매칭, `covered_by_relation=false` | **name_only 카드**: "등록된 약-영양소 참고정보 없음 / 품목명 확인만 가능" + 약사·의사 상담 고지. 제품/구매 없음 |
| ③ 둘 다 없음 | 매칭 0 | **진짜 "결과 없음"**(기존 empty) |

- 상태 ②와 ③을 **명확히 구분**한다(현재는 둘 다 empty라 "있는 약/없는 약"이 구별 안 됨).
- name_only 카드는 **medical claim이 아님**을 문구로 명시. 단정·복용지시·위험확정·제품추천 금지.
- **fail-soft:** full index 로드 실패 시 상태 ②가 사라지고 **현행 동작(①/③만)으로 degrade**. 치명 아님(ALIAS_URL과 동일 패턴, `FULL_INDEX_URL` 신설 시 동일 fail-soft 적용).
- 검색 우선순위: relation 매칭 우선 → 없으면 full index → 없으면 empty.

---

## 5. validator 설계 (신규, 별도 파일)

full index 전용 validator 체크 초안:
- full index 내 **itemSeq 중복 금지**.
- **relation_alias_index의 `item_seq` / relation itemSeq와 충돌 금지** — 겹치면 `covered_by_relation=true` 강제(위임).
- `covered_by_relation=false` 엔트리에 **relation_card 금지** → `display_mode=name_only` 강제.
- `display_mode=name_only` 엔트리는 **`no_relation_notice_required=true` 필수**.
- **제품 / 구매 / 제휴 / 가격 필드 전면 금지**(스키마에 존재 시 FAIL).
- **에스오메프라졸 / 15행(id15) itemSeq 차단**(재편입 금지) · 칼륨 제품 링크 금지.
- 교차 불변: relation 30 · DATA_URL · alias_count 621 변동 시 FAIL(다른 트랙 회귀 감지).
- name_only `item_name` 표면형 개행/공백 위생(v0.9 surface validator 규약 재사용).

---

## 6. 단계별 확장 계획

| Phase | 작업 | 변경 범위 | 게이트 |
|---|---|---|---|
| **1** | 설계 문서 (**본 문서**) | 문서만 | 완료 시 PM 판정 |
| **2** | **1,000개 샘플** full index 생성 | 신규 데이터 파일 + validator | nedrug searchDrug 수집 · getItemDetail 보수적 확정 · PM 승인 |
| **3** | **name_only UX 구현** | `src/` (FULL_INDEX_URL fail-soft · 3-상태 라우팅) | 별도 게이트 · 회귀 smoke |
| **4** | **5,000개 확장** | 데이터 | PM 승인 · validator PASS |
| **5** | **10,000개+ 장기 확장** | 데이터 | 단계 배치 · 노이즈 필터 |

각 Phase 공통: **PM 명시 승인 + validator PASS + relation/alias/DATA_URL/export 불변 + 무단 deploy/tag 금지.** Phase 2~5는 본 v1.0-B 범위 밖(설계 확정 후 별도 트랙).

---

## 7. 안전선 (불변)

- **`clinical_reviewed` / `published` 전환 금지** (천장 = verified_reference).
- **relation 30 유지** · **DATA_URL 유지**(`./data/medistack_v0.2_beta_export.json`) · **export 불변**(md5 `401b097a`).
- **에스오메프라졸 / 15행(id15) 재편입 금지** (full index itemSeq 차단 · id16×Mg는 정상 live·혼동 주의).
- **칼륨 제품 링크 금지** · 칼륨 행 `product_link_allowed=false` 유지.
- **제품 / 구매 / 제휴 UI 추가 금지** — name_only 카드에도 제품 영역 없음.
- full index는 **검색 보조이지 의학 정보가 아니다** — `name_only`는 품목명 확인용.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / relation 없는 약은 name_only(정보 없음)로만 표시 / 제품·구매·제휴 UI 금지.
