# MediStack v0.6 — Phase 17 batch8 후보 확보 리포트 (held 활용·네트워크 0)

작성일: **2026-06-12** / 상태: **✅ batch8 approved-ready 50건 생성 완료 (held 활용·네트워크 0·alias 무반영)** / 상위: `MediStack_v0.6_alias_500_plan.md` / 다음: `MediStack_v0.6_phase18_batch8_incorporation_plan.md`

> Phase 17 = v0.6 batch8 **후보 확보 단계**. Phase 15 재수집에서 staged된 **held 57**(getItemDetail 확정완료)에서 batch8 approved-ready **50건** 생성. **네트워크 0**(외부 호출 없음). **alias JSON·relation·DATA_URL·앱 전부 불변**(alias_count 306 유지). 실제 반영은 Phase 18 별도 PM 게이트.

---

## 1. 목적 / 범위
- Phase 15(v0.6-007) 확정 후보 중 batch7 미사용분(**held 57**)에서 batch8 최대 50건 생성.
- **네트워크 0** — `confirm --no-network --ar-only-batch v0.6-007`. getItemDetail 재호출 없음.
- alias 무반영(incorporated=false). Phase 18에서 306→356 반영 예정.

## 2. 산출 / 수정 파일
- **신규**: `data/candidates/bulk_alias_approved_ready_batch8_v0_6.json` (50건) · `..._batch8_v0_6.csv`.
- **수정(메타만)**: `bulk_alias_review_queue_v0_5.json`(+`.csv`) — `meta.phase17` 추가. **candidates md5 불변**(status 미flip·내용 0변경).
- **스크립트 보강**: `validate_bulk_alias_candidates.py` — batch8 검증 블록(base_no=160, ≤50, incorporated=false strict) + `DEF_AR8` + argv[12].
- **alias/relation/export/앱(src) 무변경.**

## 3. held / 선별 분석
| 구간 | 수 | 비고 |
|---|---|---|
| held (v0.6-007 confirmed pending, itemSeq∉alias) | **57** | 레보19·시프로15·오메14·메트10 (Phase 15 staged·확정완료) |
| **batch8 선별(--ar-limit 50, balanced)** | **50** | 7건 held(batch9 이월) |

- 생성: `confirm --no-network --ar-only-batch v0.6-007 --ar-balanced --ar-limit 50 --ar-batch-id v0.6-batch-8`.
- batch7 반영분(50, 이미 alias)은 itemSeq∈alias로 자동 제외(approved 후보 redundant 오라벨 없음·멱등).

## 4. batch8 approved-ready 50건 목록 (canonical별)

### 레보플록사신 (14) — src_rel [1,2,3]
레플로신정100밀리그램 · 레플록신정500mg · 렉타신정250밀리그램 · 리플록신정100·250·500밀리그램 · 셀트리온레보플록사신정100밀리그램 · 알피레보플록사신정100·250mg · 원플록신정 · 위더스레보플록사신정100·500밀리그램 · 유니레보정 · 유로레보정250mg

### 메트포르민 (10) — src_rel [12]
글루코프리서방정500·750·1000밀리그램 · 글루테니어정500mg · 글루파민서방정500밀리그램 · 글루파엑스알서방정500·850·1000밀리그램 · 글루파정250mg·1,000㎎

### 시프로플록사신 (13) — src_rel [4,5,6]
알피시프록정250mg · 에프로신정 · 일양바이오염산시프로플록사신정 · 참염산시프로플록사신정 · 케이사신정250밀리그램 · 큐프론정 · 키포신정 · 파마시프로플록사신정250mg · 팜젠시프로플록사신정250mg · 푸로포신정250밀리그램 · 프로딘정250mg · 프록사신바이정 · 프록스코정

### 오메프라졸 (13) — src_rel [13,14]
오메푸졸캡슐 · 오메프라존캡슐 · 오메프란캡슐20밀리그램 · 오메프투캡슐 · 오멕스캡슐 · 오엠피정20·40밀리그램 · 오큐졸캡슐 · 오프라졸캡슐 · 오프라캡슐 · 오프졸캡슐 · 오피라졸캡슐 · 이연오메프라졸캡슐

## 5. canonical 분포
| canonical | 건수 | source_relation_ids | verified 키 |
|---|---|---|---|
| 레보플록사신 | 14 | [1,2,3] | 기존(append) |
| 시프로플록사신 | 13 | [4,5,6] | 기존(append) |
| 오메프라졸 | 13 | [13,14] | 기존(append) |
| 메트포르민 | 10 | [12] | 기존(append) |
| **합계** | **50** | | **4성분 전부 기존 verified 키 → 신규 canonical 0** |

(알렌드론산은 held 잔여 없음 → batch8 미포함.)

## 6. 제외 / 보류 사유
- **held 8**(batch9 staged): 레보5·시프로2·오메1. `--ar-limit 50` 초과분 + v0.5-006 leftover 1, 네트워크 0 즉시 가용.
- **deferred(복합제) 170 누적**: HCTZ 등 단일성분 부적합 — v0.6 제외 유지.

## 7. 재수집 여부
- **재수집 없음(네트워크 0).** held 57(Phase 15 확정완료)만 사용. getItemDetail 재호출 0.

## 8. 검증 결과
| 검증 | 결과 |
|---|---|
| bulk candidate validator (batch8 블록 포함) | **PASS 137/137** (기존 122 + batch8 15) |
| v0.1 / v0.2 / v0.3 / Type B | **12/12 · 15/15 · 13/13 · 7/7 PASS** |
| 회귀 smoke | **PASS 5/5** (타리비드3·포사맥스1·토렘2·넥시움0·#r15) |

## 9. 불변 확인
| 항목 | 값 |
|---|---|
| alias JSON md5 (전후 동일) | `e800a7e42bb999f8fa07777f23af069f` |
| alias_count / product / verified / canon | **306 / 268 / 244 / 12** 유지 |
| relations / DATA_URL | **30 / `./data/medistack_v0.2_beta_export.json`** 유지 |
| queue status | pending 65 · approved **240(미flip)** · rejected 2 · deferred 170 (total 477) |
| export / src(앱) | 불변 |

## 10. 다음 단계
- **Phase 18 — batch8 실제 alias 반영**(PM 별도 승인 게이트): product +50(268→**318**) · verified +50(244→**294**, 4성분 append·canonicals 12 유지) · alias_count **306→356**. validator #174 옵션 A 갱신. 상세 = `MediStack_v0.6_phase18_batch8_incorporation_plan.md`.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지 / **Phase 17 은 후보 생성만 — 실제 alias 반영은 Phase 18 PM 게이트.**
