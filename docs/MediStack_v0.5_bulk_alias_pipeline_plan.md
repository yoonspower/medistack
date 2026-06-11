# MediStack v0.5 — bulk alias pipeline 설계안

작성 기준일: 2026-06-11 / 단계: **설계 문서만** (alias JSON·데이터·코드·candidate 파일·DATA_URL·deploy 전부 미변경)
상위: `MediStack_v0.4_scope_and_plan.md`, `MediStack_v0.4_typeB_alias_candidates.md`(유형 A/B 수작업 큐레이션), `MediStack_v0.4_validator8_typeB_design.md`(validator #8 일반화 + `verified_item_seqs`).

> 이 문서는 v0.5의 **bulk alias 자동 후보 생성 → 자동 검증 → 사람 승인 → batch 반영** pipeline의 **설계만** 정의한다.
> 실제 수집기/검증기/export 스크립트 구현, candidate JSON/CSV 생성, alias JSON 대량 수정은 **PM 판정 후 별도 단계**.
> 현 라이브(v0.3-beta): alias 66 · relation 30 · DATA_URL=`./data/medistack_v0.2_beta_export.json` — **이 문서로 변경 없음**.

> **진행(2026-06-11)**: Phase 1(skeleton) 완료 — 생성기/검증기(16체크)/review queue/`phase1_report`(커밋 431d545). Phase 2(nedrug 수집 dry-run) 완료 — `scripts/collect_nedrug_alias_candidates.py`(searchDrug 단독)로 13성분 dry-run 수집, **queue 16→62**(pending 32 단일성분 + deferred 28[brand_core 14+복합제 14] + rejected 2, **approved 0**), 검증기 18체크로 보강, `phase2_report` 작성. Phase 3(getItemDetail 상세확정 dry-run) 완료 — `scripts/confirm_nedrug_item_details.py`로 pending 32 원문 확인(**confirmed 31** + 표면형개행 1), 검증기 **31체크**로 보강(#19 detail 무결성·#20~#31 approved-ready 검증), queue에 detail 필드 추가, **approved-ready 별도 파일 27건**(`bulk_alias_approved_ready_v0_5.json/csv`, itemSeq 중복 4 제외) 생성, `phase3_report` 작성. queue status 불변(pending 32·deferred 28·rejected 2·**approved 0**). Phase 4(batch 1 반영) 완료 — approved-ready 27을 **실제 alias JSON 반영**: product_aliases +27(28→55) + **verified_item_seqs +27 동반 확장**(4→31 entries, #8 통과용) + **alias_count 66→93**. queue 27건 status→approved(incorporated 이력), validator를 **incorporation-aware**로 갱신(#16 정합화·#7/#24/#31 incorporated 제외·#30 approved 반영검증·#32 신규, **32체크**). v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·bulk 32/32·smoke(27신규+회귀 5종) ALL PASS. **relation 30·DATA_URL·export·앱 불변.** Phase 5(후보 풀 확대 + batch 2 생성) 완료 — collect 에 **페이지네이션**(`--max-pages`, page=N) 추가 → **max 15/성분·6페이지** 재수집, **신규 115**(pending 83 단일 + combo deferred 32), **queue 62→177**. 신규 pending 83 전수 getItemDetail 확정(**confirmed 83/83**, idempotent 재실행으로 재네트워크 0). **batch 2 approved-ready 30건**(`bulk_alias_approved_ready_batch2_v0_5.json/csv`, `--ar-balanced` canonical 라운드로빈 9성분 분산·incorporated=false·cap 30, held 53 staged). validator 에 **batch 2 검증(#40~52 + #53≤30·#54 incorporated=false·#55)** 추가 → **bulk 47/47**. v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 5/5·smoke(회귀 + batch2 미반영 0) ALL PASS. **alias JSON 0 diff(완전 무변경)·alias_count 93·relation 30·DATA_URL·batch1 27·export·앱 불변.** 신규 진입 canonical=오메프라졸·히드로클로로티아지드(13성분 전체). **Phase 6(batch 2 실제 반영) 완료** — PM 승인 → batch 2 30건 `data/medistack_v0.3_aliases.json` 반영(**product +30(55→85)·verified_item_seqs +30(31→61 entries, 11→12성분, 오메프라졸 신규)·alias_count 93→123**), queue 30 status→approved+incorporated, AR 30 incorporated=true. **validator #54 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 #52서 실제 반영 검증 — Phase 4 #16/#7/#24/#31 패턴). bulk 47/47·v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 3/3·smoke(신규 30 라이브 + 회귀) ALL PASS. relation 30·DATA_URL·export·batch1 27·앱 불변. **Phase 7(batch 3 approved-ready 생성 — alias 무반영) 완료** — PM 승인 → Phase 5 held 53 을 **네트워크 없이**(`confirm --no-network --ar-only-batch v0.5-005 --ar-balanced --ar-batch-id v0.5-batch-3 --ar-limit 30`) 재사용, batch 2 의 30 itemSeq 가 `existing_alias_itemseqs()` 로 자동 제외 → **batch 3 approved-ready 30건**(`bulk_alias_approved_ready_batch3_v0_5.json/csv`·incorporated=false·canonical 8성분 분산 독시2/레보티5/레보플5/메트1/시프로5/알렌5/오메2/오플5·held 23 staged). confirm 최소 보강(이미 approved 후보 redundant 오라벨 금지·멱등). validator 에 **batch 3 검증(#60~75 + #73≤30·#74 incorporated=false 강제·#75)** 추가 → **bulk 62/62**(batch3 제외 47/47 차등 확인). v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 5/5(#74/#73/#66/#64 + 정상)·smoke 12/12(회귀 + batch3 30 미반영 + batch2 live 유지) ALL PASS. **alias JSON 0 diff·alias_count 123·product 85·verified 61·relation 30·DATA_URL·batch1/batch2 AR·queue 후보 0변경(meta만)·export·앱 불변.** batch 3 의 8성분은 전부 기존 verified 키(오메프라졸 포함) → Phase 8 반영 시 append only·verified canonicals 12 유지. **Phase 8(batch 3 실제 반영) 완료** — PM 승인(반영 + #74 옵션 A) → batch 3 30건 `data/medistack_v0.3_aliases.json` 반영(**product +30(85→115)·verified_item_seqs +30(61→91 entries, 12성분 유지 — append only, 신규 키 없음)·alias_count 123→153**), queue 30 status→approved(reviewer v0.5-phase8-batch3, approved 57→87), AR 30 incorporated=true. **validator #74 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 base+12(#72)서 실제 반영 검증 — Phase 4/6 패턴). bulk 62/62·v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 3/3(garbage→#74·가짜→#72·정상 PASS)·smoke(신규 30 라이브 30/30 + 회귀) ALL PASS. relation 30·DATA_URL·v0.1/v0.2 export·batch1/batch2 AR·앱 불변(md5 0-diff). 라이브 153(product 115·verified 12성분). 반영=ephemeral `/tmp/ms_incorporate_batch3.py`(assert 내장·미커밋). **Phase 9(batch 4 approved-ready 생성 — alias 무반영) 완료** — PM 승인 → Phase 7 held 23 을 **네트워크 없이**(`confirm --no-network --ar-only-batch v0.5-005 --ar-balanced --ar-batch-id v0.5-batch-4 --ar-limit 30`) 재사용, batch 3 의 30 itemSeq 가 자동 제외 → **batch 4 approved-ready 23건**(`bulk_alias_approved_ready_batch4_v0_5.json/csv`·incorporated=false·canonical 5성분 레보티2/레보플6/시프로7/알렌1/오플7·**held 0** = v0.5-005 confirmed 83 전량 소진[30+30+23]). validator 에 **batch 4 검증(#80~95 + #93≤30·#94 incorporated=false strict·#95)** 추가 → **bulk 77/77**(batch4 제외 62/62 차등 확인). v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 5/5(#94/#93/#86/#84 + 정상)·smoke 11/11(회귀 + batch4 23 미반영 + batch3 live 유지) ALL PASS. **alias JSON 0 diff·alias_count 153·product 115·verified 91·relation 30·DATA_URL·batch1/2/3 AR·queue 후보 0변경(meta만)·export·앱 불변.** batch 4 의 5성분 전부 기존 verified 키 → Phase 10 반영 시 append only·verified canonicals 12 유지. **Phase 10(batch 4 실제 반영) 완료** — PM 승인(반영 + #94 옵션 A) → batch 4 23건 `data/medistack_v0.3_aliases.json` 반영(**product +23(115→138)·verified_item_seqs +23(91→114 entries, 12성분 유지 — append only)·alias_count 153→176**), queue 23 status→approved(reviewer v0.5-phase10-batch4, approved 87→110), AR 23 incorporated=true. **validator #94 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 base+12(#92)서 실제 반영 검증 — Phase 4/6/8 패턴). bulk 77/77·v0.1 12/12·v0.2 15/15·v0.3 13/13·TypeB 7/7·음성 3/3(garbage→#94·가짜→#92·정상 PASS)·smoke(신규 23 라이브 23/23 + 회귀) ALL PASS. relation 30·DATA_URL·v0.1/v0.2 export·batch1/2/3 AR·앱 불변(md5 0-diff). 라이브 176(product 138·verified 12성분). 반영=ephemeral `/tmp/ms_incorporate_batch4.py`(assert 내장·미커밋). **🔑 held 풀 소진(v0.5-005 confirmed 단일 83 전량 = batch2 30+batch3 30+batch4 23)** → 다음=Phase 11/batch 5 **재수집 필수**(미노/토라세미드/푸로세미드/HCTZ 단일 + 기존 13성분 다른 페이지 searchDrug `&page=N`/`--max-pages` 상향 → getItemDetail 확정 → ~24건 추가, 176→200).

---

## 1. 목표
- **v0.5 alias_count 목표: 200~300.**
- **v0.6 alias_count 목표: 500~1,000.**
- **10,000개는 즉시 목표 아님** → 장기 "전체 품목명 검색 DB" 레벨로 **분리**(별도 데이터 자산/인프라, alias 운영 파일과 다른 트랙).
- v0.5의 핵심은 수작업 채록이 아니라 **자동 후보 생성 + 자동 검증 + 사람 승인** 구조를 **수립**하는 것. (숫자 달성보다 pipeline·안전선 확립이 우선.)
- 기존 안전 게이트(원문 itemSeq 확인, `verified_item_seqs`, validator PASS, 에스오메프라졸/15행 제외, published 봉인)는 **전부 유지·자동화**.

## 2. 현재 한계
- 현재 **alias_count 66**(성분 38 + 제품 28). 수작업 유형 A(성분명 9건)·유형 B(제품명 4건) 큐레이션으로 도달.
- 수작업 방식은 **안전하지만 확장 속도가 느림**: 성분당 nedrug browse·상세 원문 확인·문서화·커밋. 80~100까지는 가능하나 **500~1,000은 비현실적**.
- 그러나 **다음은 v0.5에서도 유지해야 함**: itemSeq 원문 확인 / `verified_item_seqs` 화이트리스트 / validator 13체크 / 유형 B test suite.
- **금지 유지**: 숫자 채우기용 순열(용량·제형·띄어쓰기 변형) alias, 미검증 브랜드 alias, 원문 없는 alias.
- 즉, v0.5는 "사람이 하던 채록·검증을 **기계가 후보 생성 + 1차 검증**하고, **사람은 승인만**" 하는 구조로 전환해 속도와 안전을 동시에 확보한다.

## 3. 데이터 소스 전략
- **식약처/nedrug 공식 품목 데이터 기반**(임의 추론·비공식 출처 금지).
- 소스 후보(우선순위순, v0.5에서 실측·확정):
  1. **식약처 OpenAPI / 공공데이터**(data.go.kr) — 의약품 제품 허가정보(품목명·주성분·업체·제형 일괄). serviceKey 필요. 대량 수집에 가장 적합.
  2. **nedrug `searchDrug?ingrName1=<성분>`** — 주성분 기준 품목 목록(유형 B 채록에 이미 검증된 경로, 쿠키 jar + 리다이렉트 필요).
  3. **nedrug `getItemDetail?itemSeq=<seq>`** — 개별 품목 상세 원문(품목명·ingrName·ingrCode 확정 검증용, 최종 확인 채널).
- 각 소스 레코드에서 수집할 필드:
  - `itemSeq`(필수 키), `itemName`(품목명), `ingrName`/`ingredient`(주성분), `ingrCode`(성분코드, canonical 교차확인용), `entpName`(업체), `dosageForm`(제형).
  - 참고용: 전문/일반 여부(`etcOtcCode`), 품목 상태(취소/취하/유효 — `cancelCode` 등) → **취소·취하 품목 필터링용**.
- **출처 추적 필수**: 모든 후보에 `source_url`(또는 API endpoint) + `source_method`(예: `data.go.kr DrugPrdtPrmsnInfo getList` / `nedrug getItemDetail`) + `source_checked_at`(확인일) 기록. 원문 추적 불가 후보는 즉시 reject.
- **신뢰 등급**: getItemDetail 상세 원문 확인 = 최고 신뢰. 목록 API만으로 수집한 건 = 1차 후보(상세 확인 전엔 product alias 편입 불가).

## 4. canonical ingredient 매칭 전략
- **기준 = 기존 relation 30의 `canonical_ingredient`**(라이브 14성분). alias는 이 성분들로만 귀속.
- **relation 신규 생성 절대 금지**. alias는 검색 보조 전용 — 매칭 결과는 기존 relation 카드뿐(풀 확장 없음).
- **canonical_ingredient가 없는 성분은 후보만 보관(deferred), alias 편입 금지.** (relation이 14성분뿐이므로, 다른 성분 품목은 검색돼도 연결할 relation이 없음 → 편입 불가. relation 확장은 별도 의학 데이터 게이트.)
- **에스오메프라졸/15행/excluded 우회 금지**: 에스오메프라졸은 라이브 성분이어도 alias 대상 제외(validator #9·#12). excluded 전용 성분·relation 15 연결 금지(#5·#6).
- **동일 성분명 변형 처리 원칙**(정규화로 흡수 vs entry 분리):
  - 한글/영문/염/수화물 정식 표기 = **별도 entry 허용**(유형 A 패턴: "메트포르민"·"metformin"·"메트포르민염산염"·"metformin hydrochloride").
  - 용량/제형/띄어쓰기/대소문자 변형 = **entry 금지**(런타임 정규화 `norm()`이 흡수). 숫자 부풀리기 금지.
  - 과도한 축약(예: "HCl" 단독) = **별도 판정**(기본 보류).
- **유형 A(성분명, `kind=ingredient`)와 유형 B(제품명, `kind=product`)를 분리 처리**: 유형 A는 ingrName 기반 성분 변형, 유형 B는 itemName 기반 품목명(+ `verified_item_seqs` 필수). 생성·검증·승인·반영 트랙을 나눈다.

## 5. 후보 생성 규칙
### 5-A. 유형 A 후보 (성분명, `kind=ingredient`)
- 성분명 / INN / 염·수화물 포함 성분명 / 표준 한글 전사.
- 라이브 14성분에 귀속 가능한 표준 표기만. (기존 53→62 유형 A 패턴 확장.)
- **HCl 등 과도한 축약 = 별도 판정**(기본 보류, prefix 매칭상 가치 낮음).

### 5-B. 유형 B 후보 (제품명, `kind=product`)
- **공식 품목명 전체**(전체 품목명 = PM 확정 표면형, 유형 B A군과 동일).
- **itemSeq 확인 가능**(getItemDetail 상세 원문) + **canonical_ingredient 연결 가능** + **`verified_item_seqs`에 기록 가능**.
- 대표(relation 인용) itemSeq 외 동일 성분 품목 → 화이트리스트 경유(validator #8 일반화).
- 경구 흡수 상호작용 relation 맥락 일치 권장(제형 고려; 점안/외용/주사가 흡수 상호작용과 무관하면 신중).

### 5-C. 브랜드코어 후보 (예: 전체 품목명에서 용량/제형 제거한 축약명)
- 예: "라이트알렌드론정70mg" → "라이트알렌드론정".
- **v0.5에서는 기본 보류 또는 별도 review tier**(`candidate_type=brand_core`). **자동 편입 금지.**
- 오매칭(prefix) 위험·제품 추천 오인 가능성 때문에 PM 별도 판정.

### 5-D. 금지 후보 (생성 단계에서 reject)
- 원문 확인 불가 / relation 신규 생성 필요 / 성분 불명확.
- 에스오메프라졸·15행 관련.
- 칼륨 제품 링크·구매로 연결될 가능성(product_link_allowed=NO 대상의 구매 UI 연결).
- 제품 추천처럼 보이는 alias.
- 숫자 채우기용 순열(용량·제형·띄어쓰기 변형) alias.

## 6. review queue 구조
후보는 **alias JSON에 직접 넣지 않고** review queue로 분리한다. 사람 승인(`approved`)만 export 단계로 넘어간다.

### 6-A. JSON 스키마 초안 (`data/candidates/bulk_alias_review_queue_v0_5.json`)
```json
{
  "meta": {
    "version": "0.5-queue",
    "generated_at": "<ISO date>",
    "source_method": "<생성기 + 소스 식별>",
    "relation_source": "medistack_v0.2_beta_export.json",
    "note": "검색 보조 alias 후보 큐. 의학정보 아님. approved 만 alias JSON 반영. relation 신규생성 불가."
  },
  "candidates": [
    {
      "candidate_alias": "라이트알렌드론정70mg",
      "candidate_type": "product_full_name",        // ingredient | product_full_name | brand_core | rejected
      "canonical_ingredient": "알렌드론산",
      "item_seq": "201902246",
      "item_name": "라이트알렌드론정70mg",
      "ingr_name": "알렌드론산나트륨수화물",
      "source_url": "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=201902246",
      "source_method": "nedrug getItemDetail",
      "source_checked_at": "2026-06-11",
      "confidence": "high",                          // high | medium | low
      "risk_level": "low",                           // low | med | high
      "reason": "동일 성분 2nd 경구정, ingrCode 교차확인",
      "status": "pending",                           // pending | approved | rejected | deferred
      "exclusion_reason": null,                      // rejected/deferred 사유
      "reviewer": null,
      "batch_id": null
    }
  ]
}
```

### 6-B. CSV 스키마 초안 (`data/candidates/bulk_alias_review_queue_v0_5.csv`)
헤더(동일 필드, 검토 편의용 평면 포맷):
```
candidate_alias,candidate_type,canonical_ingredient,item_seq,item_name,ingr_name,source_url,source_method,source_checked_at,confidence,risk_level,reason,status,exclusion_reason,reviewer,batch_id
```
- JSON = 파이프라인 정본(export 입력), CSV = 사람 리뷰/스프레드시트 편의(양방향 동기화는 JSON 우선). (둘 다 둘지 = §14 PM 판정.)

## 7. batch 반영 전략
- **한 번에 500/1,000개 반영 금지.** rollback 가능한 작은 단위.
- **v0.5 batch size: 30~50개.** **v0.6 batch size: 50~100개.**
- 각 batch마다(= 1 커밋 단위, rollback 가능):
  - `batch_id`별 **alias_count 증가량 확인**(예상치 = approved 건수).
  - **중복 alias 0**(정규화 strip+lower 기준).
  - **canonical 연결 확인**(라이브 성분 실재).
  - **relation 30 유지**(또는 명시된 relation 확장 작업과 **분리** — alias batch엔 relation 변경 없음).
  - **DATA_URL 유지 확인**.
  - **validator PASS**(13체크 + 유형 B suite).
  - **smoke test**(신규 alias 매칭 + 회귀: 타리비드/포사맥스/토렘/넥시움0/#r15 fail-safe).
  - 실패 시 **해당 batch 커밋 revert**(작은 단위라 영향 격리).

## 8. validator 확장 계획
현 `validate_medistack_v0_3_aliases.py`(13체크, #8 일반화 + #12/#13 화이트리스트)를 **전제·유지**. bulk용으로 추가 설계:

**A. review queue 검증기 (신규, `scripts/validate_bulk_alias_candidates.py`)** — alias JSON 반영 전 큐 자체 검증:
- bulk 후보 **중복 검사**(큐 내부 + 기존 alias JSON 대조).
- alias **canonical 존재 검사**(라이브 성분 실재).
- **itemSeq 형식 검사**(숫자형) + product 후보의 **`verified_item_seqs` 존재 검사**(편입 시 화이트리스트 동반 보장).
- **에스오메프라졸/15행 차단 검사**.
- **product_link_allowed=NO 대상 구매 UI 연결 차단 검사**(필드/링크 금지).
- **brand_core 자동 편입 금지 검사**(`candidate_type=brand_core` → status가 approved여도 export 차단, 별도 tier 승인 필요).
- **source_url/source_method/source_checked_at 누락 검사**.
- `status` enum 검사(pending/approved/rejected/deferred), rejected/deferred 사유 존재 검사.

**B. export 후 alias JSON 검증 (기존 13체크 재사용 + 추가)**:
- **rejected/deferred 후보가 alias JSON에 섞이지 않았는지 검사**(approved만 반영됐는지 큐↔JSON 대조).
- **batch_id별 alias_count 증가량 검사**(meta.alias_count 델타 == approved 건수).
- 기존 #1~#13 전부 PASS(중복·canonical·excluded·#8 화이트리스트 등).

**원칙**: validator 로직은 **append-only 확장**(기존 13체크 의미 불변). bulk 검증은 별도 스크립트로 분리해 기존 게이트와 독립.

## 9. pipeline 단계 설계
**Phase 0 — 현재 v0.4 상태 고정**
- alias 66 · relation 30 · DATA_URL=v0.2 · 유형 A/B 검증 구조(validator 13체크 + 유형 B suite) 확보. (현재 완료 상태 = 시작점.)

**Phase 1 — bulk 후보 생성기 설계/구현** (`scripts/generate_bulk_alias_candidates.py`)
- 입력: canonical ingredient list(라이브 14성분) + 소스 설정.
- 출력: **review queue**(JSON/CSV, status=pending). **alias JSON 미수정.**
- 성분별 소스 조회 → 후보 정규화 → 유형 분류(A/B/brand_core/rejected) → 큐 작성.

**Phase 2 — 후보 검증기** (`scripts/validate_bulk_alias_candidates.py`)
- 원문 필드 검증(itemSeq/품목명/성분/출처) + 중복·충돌 검사 + 위험군 제외(§5-D, §8-A).
- 자동 reject/deferred 사유 기록. pending 잔여만 사람 검토 대상.

**Phase 3 — 사람 승인**
- `pending → approved | rejected | deferred`. **PM 판정 필요.** brand_core는 별도 tier 승인.
- reviewer·exclusion_reason·batch_id 기입.

**Phase 4 — alias export** (`scripts/export_approved_aliases.py`)
- **approved만** alias JSON 반영. product 후보는 **`verified_item_seqs` 자동 추가**(item_seq·item_name·verified_at·method).
- **meta.alias_count 자동 갱신**. rejected/deferred 제외 보장.

**Phase 5 — batch deploy**
- 30~50개 단위 커밋 → validator(13체크 + bulk 검증) → push → GitHub Actions(validate→deploy 게이트) → smoke → 라이브 확인. batch 단위 rollback.

**Phase 6 — SEO/API 확장 준비**
- alias DB와 relation DB **분리 가능성** 검토(alias = 검색 보조 자산, relation = 의학 데이터).
- 검색 인덱스 **분리 가능성**(런타임 index → 사전 빌드 index, 대량 alias 성능).
- "전체 품목명 검색 DB"(10,000+)는 이 단계에서 **별도 자산**으로 분리 설계.

## 10. 저장 파일 구조 제안 (⚠️ 이번 단계 생성 안 함 — 설계만)
- `data/candidates/bulk_alias_review_queue_v0_5.json` — review queue 정본.
- `data/candidates/bulk_alias_review_queue_v0_5.csv` — 리뷰 편의 평면 포맷.
- `scripts/generate_bulk_alias_candidates.py` — Phase 1 생성기.
- `scripts/validate_bulk_alias_candidates.py` — Phase 2 큐 검증기.
- `scripts/export_approved_aliases.py` — Phase 4 export.
- `docs/MediStack_v0.5_bulk_alias_pipeline_plan.md` — 본 문서.
- `docs/MediStack_v0.5_bulk_alias_review_policy.md` — 리뷰 정책/판정 기준(승인 룰·tier·reviewer 가이드).
- (참고) `data/candidates/`는 **alias 운영 파일·relation export와 분리**된 작업 영역. 정본 alias = `data/medistack_v0.3_aliases.json` 유지.

## 11. 위험 관리
- 의료 정보 앱 → alias 확장이 **정보 품질·법적 안전선**에 영향. 숫자보다 안전 우선.
- **alias는 검색 보조이지 의학적 판단이 아님.** relation 신규 생성 금지 / 임의 추론 금지 / 원문보다 강한 표현 금지.
- 복용량·구매·제품추천 금지 / 칼륨 제품 링크 금지(product_link_allowed=NO 존중).
- **clinical_reviewed/published 봉인 유지.** DATA_URL 변경은 **별도 릴리즈 게이트**(alias batch와 분리).
- bulk 자동화의 고유 위험 = **대량 오염**: 그래서 (a) 사람 승인 필수, (b) batch 소단위 + rollback, (c) export 후 큐↔JSON 대조 검증, (d) brand_core/rejected/deferred export 차단.

## 12. 수익화와의 연결
- bulk alias는 **단순 숫자 증가가 아니라 검색 유입·SEO·B2B API 기반** 자산.
- B2C 유료앱보다 **약국 상담 보조 카드 / API·위젯 / SEO 콘텐츠**에 가치. v0.5~v0.6 alias 확장 = 약국용 상담 카드·검색 품질의 토대.
- **제품 제휴는 v0.6 이후에도 분리 검토, 직접 추천 금지**(현 봉인 유지). alias 확장이 제휴 UI를 끌어들이지 않도록 경계.

## 13. v0.5에서 하지 않을 것
- relation 대량 확장 / DATA_URL 변경 / published·clinical_reviewed 전환.
- 에스오메프라졸·15행 재편입 / 제품·구매·제휴 UI.
- 1,000개 한 번에 반영 / 10,000개 전체 DB화 / 브랜드코어 자동 반영 / 미검증 alias 숫자 부풀리기.

## 14. PM 판정 필요사항
1. **v0.5 alias 목표**: 200 / 300.
2. **batch size**: 30 / 50.
3. **brand_core 후보**: 보류 / 별도 tier(review 후 수동 편입).
4. **review queue 파일 형식**: JSON / CSV / 둘 다.
5. **`source_checked_at` 기준**: 생성 시각 / 상세 원문 확인 시각(권고) / 둘 다 기록.
6. **itemSeq 원문 확인 자동화 허용 범위**: 목록 API만으로 product 편입 허용? / getItemDetail 상세 확인 필수?(권고).
7. **approved/rejected/deferred workflow**: 누가·어떻게 승인(PM 단독 / reviewer 역할 분리), deferred 재검토 주기.
8. **v0.5에서 relation 확장 없이 alias만 확장할지**(권고: alias만, relation은 별도 의학 게이트).
9. **v0.6부터 검색 인덱스 분리할지**(런타임 index → 사전 빌드, 대량 alias 성능).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증·순열 alias 금지.
