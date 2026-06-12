# MediStack v1.0 — Full Drug Name Index 10,000 확장 계획서

> 상태: **계획 문서(설계만)**. 10,000 실제 수집·배포는 **본 문서 검토 후 별도 PM 승인**으로만 착수한다.
> 선행: Phase 2(1,000 샘플) → Phase 4(5,000+ 확장, 결과는 `MediStack_v1.0_full_drug_index_phase4_report.md`).

## 0. 전제 / 불변

- full drug name index는 **검색 커버리지 보조**(품목명 확인)이지 의학 정보가 아니다.
- relation/의학 판단은 **확장하지 않는다.** relation 30·alias 621·verified 545·DATA_URL 불변.
- 확장분은 **전량 name_only**. relation_card는 alias pool 기반 **558 고정**(pool을 늘리지 않으므로 불변).
- name_only에 상호작용/영양소/제품/구매/제휴/관리 필드 **절대 금지**(검증기 `FORBIDDEN_NAMEONLY_FIELDS`).
- 에스오메프라졸/넥시움·칼륨/칼륨보존이뇨제·13 canonical 성분·와파린·비타민/미네랄(relation 얽힘) **제외 유지**.

## 1. 목표

- full drug name index를 **5,000+ → 10,000+** 로 확장하여 "검색했는데 안 나오는 약" 체감을 추가로 축소.
- schema/UX 100% 호환(Phase 2/3/4 entry 스키마 동일, append-only).

## 2. 방법론 (Phase 4 자산 재사용)

1. `scripts/collect_full_drug_name_index_sample.py --augment` 그대로 재사용.
   - 기존 5k 출력을 seed로 **보존**(itemSeq/이름/날짜 불변), 신규 name_only만 append.
2. `DIVERSE_INGREDIENTS` 추가 확장(현 309 → ~500): 미수록 치료군/성분 보강.
   - 후보군: 추가 항암 보조·안약·이비인후·피부 외용·국소마취·구강·소아 시럽 제형 등 상용 성분.
3. `--per-cap` 상향(현 30 → 40~50) + `--max-pages` 상향(현 5 → 6~8).
4. **보완 수집축**(성분 검색 천장 대비): `getItemDetail` 기반 itemSeq 직접 조회 또는 업체/제형 축 검색을
   보조로 추가. 단, 수집은 **품목명/itemSeq 중심**이며 약학적 해석은 하지 않는다.

## 3. 필요 조건

- nedrug 연결·응답 속도(요청량이 Phase 4의 약 2배). `--sleep` 유지 + 실패 재시도/백오프.
- 충분한 신규 성분 풀(5k→10k는 신규 name_only 약 +5,000 필요).
- itemSeq dedup 무결(5k seed·relation pool과 충돌 0).
- 동일 validator/smoke/UX 통과 + 전종 회귀 green.

## 4. 위험 (착수 전 검토 필수)

1. **수집 천장** — `searchDrug` 성분 부분일치만으로 10k 도달이 어려울 수 있음. 성분 풀 고갈 시
   보완 수집축(itemSeq/제형/업체) 없이는 양 미달 → **억지 충족 금지, 중단·보고**.
2. **nedrug 부하/차단** — 대량 요청 throttle 위험. 분할 실행·sleep·백오프 필요.
3. **편중** — per-cap 상향 시 commons 비중 증가. per-ingredient 분포 모니터링 필수(리포트에 top 분포).
4. **클라이언트 로드 성능(가장 중요)** — 10k JSON은 약 4~5MB(현 1k ≈ 0.49MB, 5k ≈ 별도 리포트).
   앱은 `loadFullIndex` fetch 1회 + `buildNameOnlyIndex`(전체 순회) + `searchNameOnly`(선형 includes).
   10k에서 빌드/검색 비용·모바일 fetch 시간 **사전 측정 필수**. 체감 지연 시 대응:
   - normalized 사전 1회 구축(현행) + 결과 상한 30(현행) 유지로 검색 비용은 제한적이나,
     `buildNameOnlyIndex` 1회 비용과 fetch 페이로드가 관건.
   - 필요 시: 인덱스 필드 최소화(현재도 item_seq/name/normalized/company만 앱 반입), 지연 로드(검색 시 1회),
     또는 chunked/prefix 분할. **이 측정·대응이 끝나기 전 10k 배포 금지.**
5. **name_only 순도** — 대량 수집에서도 의학/제품 필드 유입 0(검증기로 강제).
6. **제외 누출** — 확장 성분 풀에서 에스오메/칼륨/13성분/와파린 재유입 0(코드 + 검증기 이중 가드).

## 5. 검증 / 스모크 확장

- `validate_full_drug_name_index.py`: `meta.target_total>=10000`일 때 `total>=10,000` 게이트 추가(현 5,000 게이트와 동형, 조건부).
- `smoke_search_regression_v1_0.py` + fixture: `name_only_index_size` 갱신, 신규 대표 쿼리 추가,
  **넥시움/에스오메프라졸/asdfqwer = 0 불변**, relation_card(타리비드/포사맥스/토렘)·HCTZ combo 불변.
- 전종 회귀(v0.1~v0.2~v0.3~surface~TypeB~combo~combo AR~HCTZ~bulk~full index~search regr) + 라이브 QA 재수행.

## 6. 성능 사전 검토 (10k 진입 게이트)

10k 착수 전 **반드시** 측정·기록:
1. `full_drug_name_index_sample_v1_0.json` 10k 가정 크기 / gzip(Pages 기본 압축) 후 전송 크기.
2. `buildNameOnlyIndex` 1회 빌드 시간(10k 엔트리) — 저사양 모바일 기준.
3. `searchNameOnly` 평균 검색 시간(선형, 상한 30) — 흔한 prefix 기준.
4. 결과가 체감 임계(예: 빌드 >100ms 또는 fetch 체감 지연)면 §4-4 대응 후 재측정.

## 7. STOP

- 본 문서는 **계획만** 담는다. 10,000 실제 수집/정규화/검증/배포는 **별도 PM 승인** 후 착수한다.
- 승인 없이 데이터/CI/src 변경 금지. relation·alias·DATA_URL·published·clinical_reviewed 불변.
