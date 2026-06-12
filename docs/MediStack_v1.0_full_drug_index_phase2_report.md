# MediStack v1.0-B Phase 2 — Full Drug Name Index 1,000 샘플 리포트

> v1.0-B 설계의 Phase 2. "검색했는데 안 나오는 약" 체감을 줄이기 위한 **전체 품목명 인덱스 1,000 샘플** 생성.
> relation/의학 정보는 확장하지 않는다. relation 없는 약은 **name_only**("품목명 확인만 가능 / 등록된 약-영양소 참고정보 없음")로만 다룬다.
> 이번 단계 = **데이터 샘플 + 수집 스크립트 + validator + 리포트**. **앱 UI/src 미구현**(name_only UX = Phase 3).

---

## 1. 수집 방법

**두 트랙 분리:**

| 트랙 | 출처 | covered_by_relation | display_mode | 비고 |
|---|---|---|---|---|
| **relation_card** | 기존 `medistack_v0.3_aliases.json`의 verified relation-covered itemSeq (verified_item_seqs + product_aliases) | **true** | relation_card | **날조 0** — itemSeq/이름만 재사용, 의학정보 미부착 |
| **name_only** | nedrug `searchDrug` 실수집 | **false** | name_only | relation 미연결, `no_relation_notice_required=true` |

**name_only 수집 파이프라인** (`scripts/collect_full_drug_name_index_sample.py`):
1. 13 canonical relation 성분 **외**의 다양 성분 94종을 `searchDrug?ingrName1=<성분>` 으로 검색(편중 방지).
2. 각 행에서 itemSeq·품목명·주성분·완제구분·취소상태·업체명을 원문에서 추출(`parse_full`).
3. 필터: **수출용·원료·취소(비정상)·에스오메프라졸/넥시움·forbidden itemSeq·중복·relation-covered pool·13성분 포함** 제외.
4. 성분당 최대 8건(편중 방지), 1,000 도달까지(name_only cap 442) 수집.
5. **getItemDetail 미사용** — searchDrug 목록 행만으로 itemSeq/이름/주성분/업체명 확보(보수적·고속).

기존 수집 함수(`nedrug_search`/정규식/`field`)는 `collect_nedrug_alias_candidates.py` 에서 재사용(중복 구현 없음).

---

## 2~7. 수집/제외 통계

| 항목 | 값 |
|---|---|
| **총 수집(rows_seen)** | 784 (nedrug searchDrug 행) |
| 검색 성분 | 59 / 94 (1,000 도달 시 조기 종료) · 네트워크 실패 **0** |
| **최종 index 수 (total)** | **1,000** |
| **covered_by_relation=true (relation_card)** | **558** (13 canonical 성분) |
| **name_only (covered_by_relation=false)** | **442** (distinct 주성분 조합 **123**, company_name **442/442**) |
| 제외: 수출용 | 132 |
| 제외: 원료 | 58 |
| 제외: 취소/비정상 | 95 |
| 제외: 에스오메프라졸/넥시움 | 2 |
| 제외: 13 relation 성분 포함(→ relation 트랙) | 8 |
| **중복 제거(같은 수집 내)** | 14 |
| 제외: 기존 relation-covered pool 중복 | 33 |
| **kept (name_only)** | **442** |

→ **목표 1,000 정확히 달성**(relation_card 558 + name_only 442). 보류/manual review 없음(필터 통과분만 채택).

---

## 8. 대표 샘플 20개

**relation_card (covered_by_relation=true, display_mode=relation_card):**
```
201902246  라이트알렌드론정70mg                      <- 알렌드론산
200500488  보나드론정70밀리그램(알렌드론산나트륨수화물)   <- 알렌드론산
200501339  본에이드정70밀리그램(알렌드론산나트륨수화물)   <- 알렌드론산
200803184  본필정70밀리그램(알렌드론산나트륨수화물)      <- 알렌드론산
201507146  비노스토발포정(알렌드론산나트륨삼수화물)       <- 알렌드론산
200501531  비스본정(알렌드론산나트륨수화물)             <- 알렌드론산
200502717  아렌맥스정(알렌드론산나트륨삼수화물)          <- 알렌드론산
200805740  알드렌정70밀리그램(알렌드론산나트륨삼수화물)    <- 알렌드론산
201603153  알레네정70밀리그램(알렌드론산나트륨삼수화물)    <- 알렌드론산
200500211  알렌드로정70밀리그램(알렌드론산나트륨수화물)    <- 알렌드론산
```

**name_only (covered_by_relation=false, display_mode=name_only, 참고정보 없음):**
```
202002523  건트라셋서방정              | 아세트아미노펜/트라마돌염산염
202002522  건트라셋세미서방정          | 아세트아미노펜/트라마돌염산염
202107495  게보린브이정(아세트아미노펜)  | 아세트아미노펜
202501561  광동콜에스액               | 아세트아미노펜/구아이페네신/에페드린염산염/…
201404328  광동탕에이액               | 감초/건강/육계/대추/작약/아세트아미노펜
201908635  광동탕엠액                 | 감초/육계/행인/마황/아세트아미노펜
201906521  굿트라셋세미정             | 트라마돌염산염/아세트아미노펜
201800309  굿트라셋정                 | 트라마돌염산염/아세트아미노펜
202302051  건일이부프로펜연질캡슐400밀리그램 | 이부프로펜
202007294  게보린릴랙스연질캡슐         | 이부프로펜/산화마그네슘
```
name_only 엔트리에는 relation/nutrient/supplement/product/management 류 필드가 **일절 없다**(itemSeq·품목명·정규화명·주성분·업체명·source 메타만).

---

## 9. validator 결과

`scripts/validate_full_drug_name_index.py` — **RESULT: PASS (29/29)**. 주요 체크:
- itemSeq unique · item_name/normalized_item_name non-empty · display_mode enum · covered_by_relation boolean.
- 일관성: `covered_by_relation ⟺ relation_card` · name_only → `no_relation_notice_required=true`.
- name_only: relation/nutrient/product/management 류 필드 금지 · itemSeq ∉ relation-covered pool · 13성분 미포함.
- relation_card: itemSeq ∈ relation-covered pool(충돌/날조 없음).
- 에스오메프라졸/넥시움/forbidden itemSeq 제외 · source_method 화이트리스트.
- 교차 불변: alias 621 · product 583 · ingredient 38 · verified 545/13 · relation 30 · DATA_URL · published/clinical_reviewed false.

**음성 테스트(`--selftest`) PASS** — 11종 변조(itemSeq 중복·빈 이름·일관성 위반·notice=false·금지필드·13성분·pool 충돌·에스오메·source_method 등)를 전부 포착(검증기 non-no-op 입증).

전체 회귀 배터리 동시 PASS:
```
v0.1 12 · v0.2 15 · v0.3 16 · surface 5 · TypeB 7 · combo 9 · combo_AR 13 · combo_approved_ready 13 · bulk 152
full_index 29 (+ selftest)
smoke_alias 7 · smoke_hctz · smoke_search(검색 회귀 ~70)
```

### ⚠️ search regression smoke E-기준선 최소 갱신 (필요 조치, PM 확인 要)
v1.0-C smoke(`smoke_search_regression_v1_0.py`)의 E-기준선에는 "full drug index 데이터 파일 **미존재**" 체크가 있었다(설계상 "full index 출시 시 뒤집히는 신호", smoke report §6 기록). Phase 2 가 PM 지정 파일 `data/full_drug_name_index_sample_v1_0.json` 을 생성하므로 이 체크가 FAIL 된다.
→ **최소 갱신**: "파일 미존재" 단언을 제거하고, **의미있는 가드인 `data.js 가 name_only/full index 를 미배선`**(= 검색이 여전히 relation-only)만 유지. behavior 케이스(아세트아미노펜→0 등)가 검색 동작 불변을 계속 고정한다. 미사용 `glob` import 제거. **이 갱신은 src/validator/data/alias 가 아니며 STOP 조건 미해당.** 갱신 후 smoke **PASS** 유지.

---

## 10. 기존 alias / relation 불변 확인

| 항목 | 값 | 상태 |
|---|---|---|
| alias_count | 621 (product 583 + ingredient 38) | 불변 |
| verified_item_seqs | 545 / 13 canonical | 불변 |
| relations | 30 | 불변 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` | 불변 |
| published / clinical_reviewed | false / false | 불변(봉인) |

`data/medistack_v0.3_aliases.json`·relation export·queue·src(앱)·DATA_URL **무변경**. full index 는 **완전 별도 파일**.

---

## 11. 향후 Phase 3 — name_only UX 구현 계획

1. **데이터 확장(선택)**: 샘플 1,000 → 5,000 → 10,000+(`--max-pages`·성분 리스트 확장, 동일 필터·validator).
2. **앱 배선(`src/`)**: `data.js` 에 `FULL_INDEX_URL` **fail-soft fetch** 추가(alias 패턴 재사용, 실패 시 현행 relation-only degrade).
3. **3-상태 검색 라우팅**(`app.js`/`render.js`):
   - relation 매칭 → 기존 relation_card.
   - relation 없음 + full index 매칭 → **name_only 카드**: meta `name_only_notice` 문구 표시
     > "이 약은 MediStack의 약-영양소 참고정보 DB에 아직 등록된 항목이 없습니다. 현재는 품목명 확인만 가능합니다. 복용 판단은 약사 또는 의사와 상담하세요."
   - 둘 다 없음 → 기존 empty.
4. **회귀 가드 갱신**: `search_regression_v1_0` 의 `full_index_future_baseline` 그룹(아세트아미노펜·타이레놀 → 0) 기대값을 name_only 표시로 갱신 + E-기준선을 "배선됨" 확인으로 전환. 그 외 그룹(relation_card/combo/HCTZ/empty/surface/degrade)은 계속 불변.
5. **불변 유지**: relation 30·DATA_URL·published/clinical_reviewed·제품/구매/제휴 UI 금지·name_only 에 의학정보 금지.

⚠️ CI(deploy.yml) full index validator 배선은 **미수행**(v1.0-beta 태그 직후·앱 미사용이라 보류). Phase 3 배선 시 함께 게이트 추가 권장.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / **relation 없는 약은 name_only(정보 없음)로만 표시 · 의학적 판단/상호작용/영양소 정보 부착 금지**.
