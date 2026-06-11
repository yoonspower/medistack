# MediStack v0.6 — Phase 13 batch6 후보 확보 리포트

작성일: **2026-06-12** / 상태: **✅ batch6 approved-ready 50건 생성 완료 (alias 무반영·incorporated=false)** / 상위: `MediStack_v0.6_alias_500_plan.md` / 다음: `MediStack_v0.6_phase14_batch6_incorporation_plan.md`

> Phase 13 = v0.6 batch6 **후보 확보 단계**. 기존 held 확정분(네트워크 0)에서 batch6 approved-ready **50건**을 생성했다. **alias JSON·relation·DATA_URL·앱 전부 불변**(alias_count 206 유지). 실제 alias 반영은 Phase 14 별도 PM 게이트.

---

## 1. 목적 / 범위
- v0.5 Phase 11(v0.5-006) 재수집의 **held 확정분**에서 batch6 approved-ready 최대 50건 생성.
- **네트워크 0** — getItemDetail 재호출 없이 기존 detail_confirmed=true 후보만 사용.
- alias 무반영(incorporated=false). Phase 14에서 206→256 반영 예정.

## 2. 산출 / 수정 파일
- **신규**: `data/candidates/bulk_alias_approved_ready_batch6_v0_6.json` (50건) · `..._batch6_v0_6.csv`.
- **수정(메타만)**: `data/candidates/bulk_alias_review_queue_v0_5.json`(+`.csv`) — `meta.phase13_confirmation` 추가. **candidates 배열 md5 불변**(status 미변경, 후보 내용 0 변경).
- **스크립트 최소 보강**:
  - `scripts/confirm_nedrug_item_details.py` — `--ar-version` 옵션 추가(approved-ready meta version 라벨, 기본 `v0.5`; batch6 은 `v0.6`).
  - `scripts/validate_bulk_alias_candidates.py` — batch6 검증 블록 추가(base_no=120, ≤50, incorporated=false strict). `DEF_AR6` + argv[10] 배선.
- **alias/relation/export/앱(src) 무변경.**

## 3. held / 공급 분석
| 구간 | 수 | 설명 |
|---|---|---|
| held (pending + detail_confirmed=true) | **55** | 시프로20·레보17·오플8·알렌6·독시1·미노1·토라1·푸로1 |
| 그 중 itemSeq 이미 alias 보유(중복 제품, 자동 제외) | **4** | 독시1·미노1·토라1·푸로1 (v0.5-002 잔여) |
| **batch6 pickable**(detail_confirmed & itemSeq∉alias) | **51** | 레보17·시프로20·알렌6·오플8 (전부 v0.5-006) |
| **batch6 선별(--ar-limit 50, balanced)** | **50** | 1건 held(시프로 1, 다음 batch 이월) |

- 생성 명령: `confirm_nedrug_item_details.py --no-network --ar-only-batch v0.5-006 --ar-balanced --ar-limit 50 --ar-batch-id v0.6-batch-6 --ar-incorporated false --ar-version v0.6`.
- balanced 라운드로빈 → canonical 균등 분산(공급 가능한 4성분 내).

## 4. batch6 approved-ready 50건 목록 (canonical별)

### 레보플록사신 (17건) — source_relation_ids [1,2,3]
레보에이블정500밀리그램(201902167) · 레보에프정500밀리그램(201701554) · 레보카신정(199800454) · 레보카신정750밀리그램(201406037) · 레보타신정100밀리그램(201801895) · 레보탐정(199801012) · 레보투정100밀리그램(201901897) · 레보투정500밀리그램(201901896) · 레보트라정(201401334) · 레보펙신정(199400369) · 레보푸라신정(199903254) · 레보푸라신정250밀리그램(201701601) · 레보프사정100밀리그램(202003099) · 레보플라정100밀리그램(201906311) · 레보플라정500밀리그램(201906213) · 레보플러스정750밀리그램(201406125) · 레보플로정(201403940)

### 시프로플록사신 (19건) — source_relation_ids [4,5,6]
시플록신정250밀리그램(200404700) · 시플록큐정250mg(201604019) · 싸이러스정250밀리그램(201309509) · 싸이로칸정250밀리그램(199401754) · 싸이스펙정250밀리그램(199202497) · 싸이신정250밀리그램(199000362) · 싸이신정500밀리그램(199000363) · 싸이프로신정250mg(201403459) · 싸이프로정(199300927) · 싸이플록신정100밀리그람(200201509) · 싸이플록신정250밀리그램(199601533) · 싸이플록정250밀리그램(201903428) · 씨록사신정(201600601) · 씨록신정250밀리그램(199201214) · 씨록정250밀리그램(199001346) · 씨에프정250mg(199900995) · 씨큐로베이정250밀리그램(201500661) · 씨트로정(200707894) · 씨팍신정250밀리그램(201403586)

### 알렌드론산 (6건) — source_relation_ids [29]
애드본정70밀리그램(200501583) · 타이본위클리정(200502771) · 파렌드정70밀리그램(200604294) · 포사렌드정(200502154) · 포사로닌정70밀리그람(200605491) · 포사롱정70밀리그램(200500070)

### 오플록사신 (8건) — source_relation_ids [21,22,23]
타록시드정100밀리그램(199200490) · 텔비트정100밀리그람(199200705) · 투록신정(198701772) · 투프로정100밀리그램(201904339) · 파비드정(198700537) · 파비스오플록사신정(199401661) · 팜젠오플록사신정(200402467) · 프락신정100밀리그람(199300815)

## 5. canonical 분포
| canonical | 건수 | source_relation_ids | verified 키 |
|---|---|---|---|
| 레보플록사신 | 17 | [1,2,3] | 기존(append) |
| 시프로플록사신 | 19 | [4,5,6] | 기존(append) |
| 알렌드론산 | 6 | [29] | 기존(append) |
| 오플록사신 | 8 | [21,22,23] | 기존(append) |
| **합계** | **50** | | 4성분 전부 기존 verified 키 |

## 6. 제외 / 보류 사유
- **4 held 중복 제외(독시·미노·토라·푸로 각1)**: itemSeq 가 이미 alias(verified_item_seqs)에 존재 → 동일 제품 중복 alias 금지로 자동 제외(queue pending 유지).
- **1건 held over**: `--ar-limit 50` 초과분(시프로 1) → batch7 이월(queue pending 유지).
- **deferred 119 제외**: 복합제 combo 105 + brand_core 14 — v0.6 편입 금지 대상(단일성분 부적합/무검증 오매칭). detail_confirmed 누출 0(검증).
- **canonical 4성분 한정 사유**: batch6 pickable(itemSeq∉alias 신규 단일성분)이 레보·시프로·알렌·오플 4성분에만 잔존. 나머지 9성분은 held 신규분이 없거나(이미 반영) 중복 itemSeq. → 향후 batch(7~)는 §plan §3 단일성분 심층 재수집(나머지 성분 long tail)으로 분산 확대.

## 7. 재수집 여부
- **재수집 없음(네트워크 0).** held 51 pickable ≥ 목표 50 → 외부 nedrug 호출 불필요. getItemDetail 재호출 0.

## 8. 검증 결과
| 검증 | 결과 |
|---|---|
| bulk candidate validator (batch6 블록 포함) | **PASS 107/107** (기존 92 + batch6 15) |
| v0.1 export validator | **PASS 12/12** |
| v0.2 export validator | **PASS 15/15** |
| v0.3 alias validator | **PASS 13/13** |
| Type B suite | **PASS 7/7** |
| 회귀 smoke | **PASS 5/5** |

**batch6 블록(번호 120~135) 통과 내역**: 필수 16필드·queue 존재·pending/product_full_name/detail_confirmed·기존 alias 중복 0·canonical∈허용·에스오메프라졸/15행 0·복합제('/') 0·item_seq 숫자형·approved_ready=true·**item_seq∉기존 alias**·≤50건·**incorporated=false**·incorporated 필드 보유.

**회귀 smoke(라이브 alias 206 불변)**: 타리비드→오플록사신 **3** · 포사맥스→알렌드론산 **1** · 토렘→토라세미드 **2** · 넥시움→**0** · `#/r/15` fail-safe(findRelation(15)=null, renderable 미포함) 유지.

## 9. 불변 확인
| 항목 | 값 |
|---|---|
| alias JSON md5 (before==after) | `1224369b329bd85a8deb9e7fc0f56c19` 동일 |
| queue candidates md5 (before==after) | `dfd227d2299d18f7a4d287660a963d70` 동일 |
| alias_count | **206** 유지 |
| product_aliases | **168** 유지 |
| ingredient_aliases | **38** 유지 |
| verified_item_seqs | **144** 유지 |
| relations | **30** 유지 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` 유지 |
| queue status | pending 58 · approved 140 · rejected 2 · deferred 119 (불변) |

## 10. 다음 단계
- **Phase 14 — batch6 실제 alias 반영**(PM 별도 승인 게이트): product_aliases +50(168→218) · verified_item_seqs +50(144→194, 4성분 append) · alias_count **206→256**. validator #134 를 incorporation-aware(option A)로 갱신. 상세 = `MediStack_v0.6_phase14_batch6_incorporation_plan.md`.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **Phase 13 은 후보 생성만 — 실제 alias 반영은 Phase 14 PM 게이트.**
