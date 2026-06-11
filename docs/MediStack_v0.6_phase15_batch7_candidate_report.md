# MediStack v0.6 — Phase 15 batch7 후보 확보 리포트 (외부 심층 재수집)

작성일: **2026-06-12** / 상태: **✅ batch7 approved-ready 50건 생성 완료 (외부 재수집·alias 무반영·incorporated=false)** / 상위: `MediStack_v0.6_alias_500_plan.md` / 다음: `MediStack_v0.6_phase16_batch7_incorporation_plan.md`

> Phase 15 = v0.6 batch7 **후보 확보 단계**. held 소진으로 **외부 nedrug searchDrug 심층 재수집(`--max-pages 25/28`)** + getItemDetail 확정 → batch7 approved-ready **50건** 생성. **alias JSON·relation·DATA_URL·앱 전부 불변**(alias_count 256 유지). 실제 alias 반영은 Phase 16 별도 PM 게이트.

---

## 1. 목적 / 범위
- batch6 반영 후 held 거의 소진(confirmed 5) → **외부 재수집 필요**. nedrug searchDrug 깊은 페이지(20~30)로 13 canonical 단일성분 long tail 확보.
- getItemDetail 원문 확정 → batch7 approved-ready 최대 50건. alias 무반영(incorporated=false). Phase 16에서 256→306 반영 예정.

## 2. 산출 / 수정 파일
- **신규**: `data/candidates/bulk_alias_approved_ready_batch7_v0_6.json` (50건) · `..._batch7_v0_6.csv`.
- **수정**: `data/candidates/bulk_alias_review_queue_v0_5.json`(+`.csv`) — 신규 후보 158건 적재(pending +107·deferred +51) + getItemDetail 확정(detail_confirmed=true 107) + meta. **status approved 전환 0**(alias 미반영).
- **스크립트 보강**: `scripts/validate_bulk_alias_candidates.py` — batch7 검증 블록 추가(base_no=140, ≤50, incorporated=false strict). `DEF_AR7` + argv[11].
- **alias/relation/export/앱(src) 무변경.**

## 3. 수집 / 확정 분석
| 단계 | 명령 | 결과 |
|---|---|---|
| collect 1 | `--max-per-ingredient 12 --max-pages 25 --batch-id v0.6-007` | 신규 66 (단일 42 pending + 복합제 24 deferred) |
| collect 2 (top-up) | `--max-per-ingredient 20 --max-pages 28` | 신규 92 (단일 65 + 복합제 27) |
| **수집 합계** | | **신규 158** (단일성분 pending **107** + 복합제 deferred **51**) |
| confirm | `--target-batch v0.6-007` (getItemDetail) | **107/107 확정** (combo 0·성분불일치 0·실패 0) |
| batch7 AR | `--ar-only-batch v0.6-007 --ar-balanced --ar-limit 50` | **50건** (held 57 이월) |

- 수집 dedup 4중(surface ∉ alias256 · ∉ queue · itemSeq ∉ alias · item_name ∉ alias)으로 순수 net-new만 적재.
- 복합제는 collect 단계에서 ingr_name '/' 감지 → 자동 deferred(단일성분만 pending). getItemDetail 재확인도 combo 0.

## 4. batch7 approved-ready 50건 목록 (canonical별)

### 레보플록사신 (13) — src_rel [1,2,3]
레복사신정100·250·500밀리그램 · 레브록신정 · 레비신정100mg·500mg · 레사크라정100밀리그램 · 레크로신정 · 레펙신정 · 레포신정100밀리그램 · 레폭신정 · 레프렉스정100mg · 레프로신정

### 메트포르민 (12) — src_rel [12]
글루세라서방정500mg · 글루엠서방정 · 글루코닐정 · 글루코다운정250·500·1000밀리그램 · 글루코젠정500밀리그램 · 글루코파지엑스알서방정·1000밀리그램 · 글루코파지정250·500·1000밀리그램

### 시프로플록사신 (12) — src_rel [4,5,6]
씨록탄정500밀리그램 · 씨큐로바이정 · 씨티신정 · 씨프로바이정250밀리그램 · 씨프록정250밀리그램 · 씨프록탄정250mg·500mg · 씨프론정250mg · 씨플로정 · 씨플록스정 · 씨플록정250mg · 알리코염산시프로플록사신정250밀리그람

### 알렌드론산 (1) — src_rel [29]
포사퀸정70밀리그람

### 오메프라졸 (12) — src_rel [13,14]
오라섹캡슐 · 오메그린캡슐 · 오메다캡슐 · 오메드정10·20밀리그램 · 오메딘캡슐 · 오메라핀캡슐 · 오메존캡슐 · 오메졸캡슐 · 오메큐캡슐 · 오메타졸캡슐 · 오메톤캡슐

(전체 itemSeq = `bulk_alias_approved_ready_batch7_v0_6.json`)

## 5. canonical 분포
| canonical | 건수 | source_relation_ids | verified 키 |
|---|---|---|---|
| 레보플록사신 | 13 | [1,2,3] | 기존(append) |
| 메트포르민 | 12 | [12] | 기존(append) |
| 시프로플록사신 | 12 | [4,5,6] | 기존(append) |
| 오메프라졸 | 12 | [13,14] | 기존(append) |
| 알렌드론산 | 1 | [29] | 기존(append) |
| **합계** | **50** | | **5성분 전부 기존 verified 키 → 신규 canonical 0** |

## 6. 제외 / 보류 사유
- **held 57**(v0.6-007 confirmed, batch8 staged·네트워크 0): 레보19·시프로14·오메14·메트10. `--ar-limit 50` 초과분, 다음 batch 즉시 가용.
- **복합제 deferred 51**(v0.6-007): **HCTZ 32**(히드로클로로티아지드는 단일성분 완제 거의 없음·전량 복합제) · 메트10 · 알렌5 · 오메4. 단일성분 부적합으로 v0.6 제외.
- **0 신규 7성분**(심층 25페이지에도 net-new 0 → 단일성분 풀 소진): 독시사이클린·레보티록신·목시플록사신·미노사이클린·오플록사신·토라세미드·푸로세미드. (기존 alias로 이미 커버 또는 시장 단일성분 제한.)
- **HCTZ 0 in batch7**: 수집 32건 전부 복합제 → 단일성분 0 → batch7·held 미포함. (HCTZ 커버 확대는 복합제 tier 정책 결정 필요 — v0.6 범위 밖.)

## 7. 재수집 여부
- **외부 재수집 YES** (네트워크 사용). nedrug searchDrug `--max-pages 25/28`(PM 20~30 범위) 2회. getItemDetail 107회. **approved 0·alias JSON 미수정**(external_api_used=True, dry-run).

## 8. 검증 결과
| 검증 | 결과 |
|---|---|
| bulk candidate validator (batch7 블록 포함) | **PASS 122/122** (기존 107 + batch7 15) |
| v0.1 / v0.2 / v0.3 / Type B | **12/12 · 15/15 · 13/13 · 7/7 PASS** |
| 회귀 smoke | **PASS 5/5** (타리비드3·포사맥스1·토렘2·넥시움0·#r15) |

**batch7 블록(번호 140~155) 통과**: 필수 16필드·queue 존재·pending/detail_confirmed·기존 alias 중복 0·canonical∈허용·에스오메프라졸/15행 0·복합제 0·item_seq 숫자형·item_seq∉기존 alias·≤50건·**incorporated=false**·필드 보유.

## 9. 불변 확인
| 항목 | 값 |
|---|---|
| alias JSON md5 (수집·확정 전후 동일) | `849bd4583b7ebfad5ca33298f246525a` |
| alias_count / product / verified / canon | **256 / 218 / 194 / 12** 유지 |
| relations / DATA_URL | **30 / `./data/medistack_v0.2_beta_export.json`** 유지 |
| queue status | pending 115 · approved **190(미flip)** · rejected 2 · deferred 170 (total 477) |
| export / src(앱) | 불변 |

## 10. 다음 단계
- **Phase 16 — batch7 실제 alias 반영**(PM 별도 승인 게이트): product_aliases +50(218→**268**) · verified_item_seqs +50(194→**244**, 5성분 append·canonicals 12 유지) · alias_count **256→306**. validator #154 를 incorporation-aware(option A)로 갱신. 상세 = `MediStack_v0.6_phase16_batch7_incorporation_plan.md`.
- 이후: held 57(batch8, 네트워크 0) → 306→~356. 누적 목표 500.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **Phase 15 는 후보 생성만 — 실제 alias 반영은 Phase 16 PM 게이트.**
