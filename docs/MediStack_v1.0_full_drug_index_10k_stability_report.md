# MediStack v1.0 — Full Drug Name Index 10,000 확장 + 안정화 QA 리포트

> 상태: **5,500 → 10,000 확장 완료 + 안정화 QA PASS.** name_only 전량 nedrug 실수집, 의학정보 0.
> relation/alias/DATA_URL/export 불변. src/app UX 미변경. published/clinical_reviewed false 봉인 유지.
> 선행: Phase 2(1,000) → Phase 4(5,500, `..._phase4_report.md`) → **Phase 5(10,000, 본 문서)**.
> 계획 근거: `MediStack_v1.0_full_drug_index_10k_plan.md`(§2 방법론·§4 위험·§6 성능 게이트).
> 작성일: 2026-06-13.

---

## 1. 요약 (TL;DR)

- full drug name index를 **5,500 → 10,000**으로 확장(name_only **4,942 → 9,442**, relation_card 558 고정).
- 신규 4,500건은 **전량 name_only**(품목명 확인만, 의학정보 0). 기존 5,500은 **byte-identical 보존**(무손실 augment).
- **성능 비이슈**: 10k gzip 전송 **278KB**, 모바일 초기로드 추정 **~58ms**, 검색 ≤0.31ms. **20k까지 안전**(외삽).
- 전종 validator/smoke **PASS**. potassium standalone 보충제 **0건**. 불변값 8종 전부 유지.
- **결론: 10k 라이브 배포 안전.** 20k 확장도 성능상 여유(별도 데이터·승인 트랙).

## 2. 확장 방법론 (Phase 4 자산 재사용)

`scripts/collect_full_drug_name_index_sample.py --augment --target 10000 --per-cap 45 --max-pages 7 --checked-at 2026-06-13`

- **augment**: 기존 출력(5,500)을 seed로 **보존**(itemSeq/이름/날짜 불변), 신규 name_only만 append.
- **성분 풀 309 → 485**(`DIVERSE_INGREDIENTS_EXT2` 176종 신규): 미수록 치료군 보강 — 외용·점안·이비인후/흡입·
  구강/인후·국소마취·진해거담·소화효소·추가 항생/항결핵/항바이러스·파킨슨·정신·비뇨/부인과·항부정맥·PAH·
  면역조절·금연/중독·PDE5. **신규 성분을 앞에 정렬** → 미수록 niche 우선 충당(다양성·균형).
- 제외 유지(Phase 4 동일·안전): **13 canonical · 에스오메프라졸 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄**.

### 수집 통계 (collection_stats)

| 항목 | 값 |
|---|---|
| ingredients_searched | 381 / 485 (cap 도달로 조기 종료) |
| **ing_fail** | **0** (EXT2 성분명 전부 유효) |
| rows_seen | 14,249 |
| excl_export(수출용) | 1,737 |
| excl_raw(원료) | 616 |
| excl_cancel(취소/취하) | 2,178 |
| excl_eso(에스오메/넥시움) | 15 |
| excl_13(canonical 13성분) | 336 |
| excl_dup(기존 중복) | 4,730 |
| excl_pool(relation pool) | 137 |
| **kept(신규 name_only)** | **4,500** (cap 정확 도달) |

소요: 약 31분(08:36 → 09:07), sleep 0.2s, request timeout 15s, 네트워크 실패 0.

## 3. 무결성 (STOP 가드)

| 검사 | 결과 |
|---|---|
| total | **10,000** (relation_card 558 + name_only 9,442) |
| itemSeq 유일 | 10,000 distinct, **중복 0** |
| 기존 5,500 보존 | **byte-identical** (orig md5 `eaec1e1e` == new[:5500] md5 `eaec1e1e`) — 무손실 |
| 신규 4,500 순도 | 전량 name_only·covered_by_relation=false·notice_required=true·checked_at=2026-06-13·source=nedrug.searchDrug |
| name_only 금지 필드 | **0** (상호작용/영양소/제품/구매/관리 일절 없음) |
| 13 canonical 유입 | 0 (검증기 통과) |
| 에스오메/넥시움 유입 | 0 (넥시움·에스오메프라졸·nexium·esomeprazole 검색 전부 0) |
| relation pool 충돌 | 0 |

JSON md5 `5fb8ee964b0691efae28e96421e16f2a` · JSON 4.79MB · CSV 10,000 logical rows / 2.20MB.

## 4. 검색 품질 / 다양성

- **고유 주성분 문자열 1,292**(name_only) · **최대 단일 성분 0.90%**(Phase 4의 1.21%보다 개선) · 제조사 321(최대 1.84%).
- 신규 niche 커버 실측(limit 30): 벤지다민 12 · 에르도스테인 30 · 미녹시딜 30 · 타크로리무스 30 ·
  사이클로스포린 29 · 리도카인 22 · 레트로졸 7 · 날트렉손 10 — 기존 상용 경구약 위주였던 인덱스에 미수록 약 보강.
- 기존 쿼리 깊이 증가: 이부프로펜 30 · 아세트아미노펜 20 · 암로디핀 30(상한) · 게보린 3 · 노바스크 3.

### 3상태 라우팅 불변 (relation_card / name_only / empty)

`smoke_search_regression_v1_0.py` (실제 guards.js+render.js, A~H) **PASS**:

- relation_card: 타리비드 3 · 포사맥스 1 · 토렘 2 (기존 불변) · HCTZ combo(미카르디스플러스) 칼륨 반전 고지 유지.
- name_only: relation 0건일 때만 보조 동작(게보린·이부프로펜·niche). 카드에 상호작용/칼륨/제품/링크 **없음**(H 검증).
- empty: **asdfqwer 0 · 넥시움 0 · 에스오메프라졸 0** (불변 유지). 타이레놀 0(브랜드 표면형 미포착 — 하드불변 아님).

## 5. 성능 (10k 진입 게이트 — plan §6)

`scripts/measure_full_index_performance.py` (실제 guards.js를 node로 측정 · 데스크톱 V8 기준):

| 지표 | 5,500(기준) | **10,000** | 20,000(외삽) |
|---|---|---|---|
| JSON 원본 | 2.59MB | **4.79MB** | ~9.6MB |
| **gzip 전송**(Pages) | 144KB | **278KB** | ~556KB |
| JSON.parse 중앙값 | 6.5ms | **12.3ms** | ~24.5ms |
| buildNameOnlyIndex | 1.2ms | **2.3ms** | ~4.6ms |
| 초기로드(parse+build) 데스크톱 | 7.7ms | **14.6ms** | ~29ms |
| **저사양 모바일 추정**(×4) | ~31ms | **~58ms** | ~115ms |
| searchNameOnly 최악(전체스캔) | 0.18ms | **0.31ms** | ~0.6ms |

- 임계(권장): build < 100ms · gzip < 1.5MB → **10k 충족**(build 2.3ms, gzip 278KB). 대응 불필요.
- 핵심: 원본 JSON은 크지만(품목명/필드 반복) **gzip ~17배 압축** → 전송·체감 부담 작음. 검색은 normalized 사전
  1회 + 상한 30이라 선형이어도 sub-ms.
- **20k 전망**: gzip ~556KB, 모바일 로드 ~115ms — 여전히 임계 내. **20k 확장은 성능상 안전**(데이터 수집
  천장·다양성·별도 PM 승인은 별개 판단). 임계 초과 신호 없음 → **STOP 사유 없음**.

## 6. 안전 / 칼륨 정책 (10k 재검증)

`validate_potassium_name_only_policy.py` **PASS 8/8** · selftest 0 failures:

| stats | 값 |
|---|---|
| 칼륨(item_name 기준) | 128 |
| 칼륨(ingredient 기준) | 289 |
| 검사 대상(subject) | 289 |
| allowed_saltform | 283 |
| manual_review | **6** (비차단) |
| **blocked_standalone** | **0** |

- standalone 칼륨보충제/전해질 repletion 제품 **0건** — name_only 유입 없음(검색 성분에 칼륨염 미포함).
- manual_review 6건은 전부 **비-보충제 문맥**(자동 삭제·차단 아님, 정책의 "애매하면 manual-review" 경로):
  점안액(L-아스파르트산칼륨/염화칼륨 co-ingredient·인공눈물 전해질) · 시린이 치약(질산칼륨, 지각과민) ·
  아미노산 수액(다전해질 부수성분). **standalone 경구 칼륨보충제 아님.**
- name_only는 의학정보 0이므로 salt-form 항목도 **칼륨 주의/보충 안내 미표시**(PM 안전조건 충족).

## 7. 알려진 경미 항목 (투명 기록)

- **품목명 줄바꿈 10건**(name_only 9,442 중 0.1%): nedrug 공식 품목명 `{브랜드}\n({주성분})` 패턴.
  - 검색 영향 **없음**: `normalized_item_name`은 개행 0(norm()이 공백 병합) → 검색 정상.
  - 표시 영향 **없음**: 렌더는 `<span class="noname">`(white-space:normal) → HTML 공백 병합으로 한 줄 표시.
  - 기존 데이터와 동형 패턴 → 정규화 시 의미 변경 위험이라 **유지**(데이터 무수정 원칙). 결함 아님.

## 8. 회귀 (전종 PASS)

v0.1 12/12 · v0.2 15/15 · v0.3-alias 16/16 · surface 5/5 · combo-AR 13/13 · HCTZ-AR(v0.8) 13/13 ·
bulk 152/152 · test-typeB 7/7 · test-combo 9/9 · test-comboAR 13/13 · smoke-hctz · smoke-alias(7) ·
**full-index 31/31**(Phase 5 게이트 포함) · full-selftest · **potassium 8/8** · potassium-selftest · search-regr.

## 9. 종단 불변 확인

alias_count **621** · product_aliases **583** · ingredient_aliases **38** · verified_item_seqs **545/13** ·
relations **30** · DATA_URL **./data/medistack_v0.2_beta_export.json** · export md5 **401b097a**(불변) ·
published=false · clinical_reviewed=false. **src/app·export·aliases 미변경.**

## 10. 다음 (별도 승인)

1. **20k 확장** — 성능상 안전(본 측정). 단 수집 천장(searchDrug 부분일치)·다양성·nedrug 부하는 별도 검토.
   성분 풀 추가 확장 또는 보완 수집축(getItemDetail/제형/업체) 필요할 수 있음. **억지 충족 금지 원칙 유지.**
2. **clinical reviewer 트랙** — name_only는 검색 보조일 뿐, relation/의학정보 확장은 reviewer 확보 후 별도 버전.
3. **v1.1-beta 문서화** — 본 확장 + 안정화를 v1.1 마일스톤으로 정리(태그는 PM 승인 시에만).
