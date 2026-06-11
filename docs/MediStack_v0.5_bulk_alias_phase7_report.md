# MediStack v0.5 — bulk alias pipeline Phase 7 보고서 (batch 3 approved-ready 생성, alias 무변경)

작성/실행일: **2026-06-11** / 단계: **Phase 7 batch 3 approved-ready 생성(생성만 — alias JSON 무변경, 반영은 Phase 8 PM 게이트)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase6_report.md`, `..._phase5_report.md`

> PM 판정(Phase 7): Phase 5 held 후보를 **네트워크 없이** 재사용해 **batch 3 approved-ready ≤ 30건** 생성. **alias JSON(`data/medistack_v0.3_aliases.json`) 절대 수정 금지**(alias_count 123 유지). 실제 반영은 다음 PM 승인 후 Phase 8. relation 30·DATA_URL·export·앱 불변.

---

## 1. 생성/수정 파일
| 파일 | 변경 |
|---|---|
| `data/candidates/bulk_alias_approved_ready_batch3_v0_5.json` | **신규** — batch 3 approved-ready 30건(incorporated=false) |
| `data/candidates/bulk_alias_approved_ready_batch3_v0_5.csv` | **신규** — 동일 30건 CSV |
| `data/candidates/bulk_alias_review_queue_v0_5.json` | meta 만 갱신(`phases`+7, `phase7_confirmation` 추가). **후보 0건 변경**(status/incorporated/detail 불변) |
| `scripts/confirm_nedrug_item_details.py` | 최소 보강 — 이미 반영(status=approved)된 후보는 `confirmed_redundant_itemseq` 오라벨 금지(재실행 멱등, batch3 출력 불변) |
| `scripts/validate_bulk_alias_candidates.py` | 최소 보강 — batch3 approved-ready 검증 추가(번호 60~75): base 검증 + #73(≤30)·#74(incorporated=false 강제)·#75(필드 보유) |
| (불변) `data/medistack_v0.3_aliases.json` · queue CSV · relation export(v0.1/v0.2) · batch1/batch2 AR · src/ · index.html · .github/ · DATA_URL | **무변경**(git diff 0, alias md5 불변) |

## 2. held/staged 후보 → batch 3 선별
- **Phase 5 confirmed 단일성분 83건** 중 batch 2 로 30건 반영(Phase 6) → 잔여 **held 53건**(detail_confirmed=true·batch v0.5-005·status pending).
- batch 2 의 30 itemSeq 가 Phase 6 에서 alias(product+verified)에 진입 → `existing_alias_itemseqs()`(74 itemSeq)가 **자동 제외** → batch 3 적격 풀 = **정확히 53건**(전부 pending·product_full_name·복합제 0·에스오메프라졸 0·기존 alias 표면형 중복 0).
- `--ar-balanced`(canonical 라운드로빈) + `--ar-limit 30` → **batch 3 = 30건**, **held = 23건**(다음 batch 회수, queue pending 유지).

## 3. batch 3 approved-ready 30건 (canonical 균등분산 8성분)
| canonical | 건수 | itemSeq → 표면형(품목명) |
|---|---|---|
| 독시사이클린 | 2 | 201506123 바이독시정(독시사이클린수화물) · 199502147 영풍독시사이클린정100밀리그램 |
| 레보티록신 | 5 | 202500938 씬지록신정112마이크로그램 · 201706645 씬지록신정125마이크로그램 · 202500949 씬지록신정137마이크로그램 · 201706671 씬지록신정25마이크로그램 · 200301117 씬지록신정50마이크로그램 (전부 레보티록신나트륨수화물) |
| 레보플록사신 | 5 | 200101393 라이록사신정 · 201210744 레나신정 · 201309123 레노보정 · 199801298 레록신정 · 201903825 레보건정100밀리그램 (전부 레보플록사신수화물) |
| 메트포르민 | 1 | 200400304 글라비스정(메트포르민염산염) |
| 시프로플록사신 | 5 | 199602137 미래시프로플록사신정 · 200807647 베아신정250밀리그램 · 201601711 베아신정500밀리그램 · 198801052 사이톱신정 · 200000453 삼성시플로프록사신정 (시프로플록사신염산염/수화물) |
| 알렌드론산 | 5 | 200501531 비스본정 · 200502717 아렌맥스정 · 200805740 알드렌정70밀리그램 · 201603153 알레네정70밀리그램 · 200500211 알렌드로정70밀리그램 (알렌드론산나트륨수화물/삼수화물) |
| 오메프라졸 | 2 | 199907296 바로메졸캡슐(오메프라졸) · 200410999 바이넥스오메프라졸캡슐(오메프라졸장용성과립) |
| 오플록사신 | 5 | 201902566 서울오플록사신정 · 200401862 셀릭스오플록사신정100밀리그램 · 200500476 셀트리온오플록신정100밀리그램 · 199703570 안플레임정 · 199100426 에펙신정100밀리그램 (전부 오플록사신) |

(전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high·risk_level low. 전체 필드는 approved-ready 파일 참조. 표면형=전체 품목명, Phase 4~6 동일 규약.)

## 4. canonical 분포 / 제외·보류 사유
- 분포: 독시2·레보티록신5·레보플록사신5·메트포르민1·시프로플록사신5·알렌드론산5·오메프라졸2·오플록사신5 = **30**. (메트포르민·독시·오메프라졸은 적격 풀이 적어 1~2건, 나머지는 5건씩 라운드로빈)
- **held 23건**(다음 batch): 레보티록신2·레보플록사신6·시프로플록사신7·알렌드론산1·오플록사신7 (적격 풀에서 cap 30 초과분, queue pending 유지·detail_confirmed 보존).
- **제외(approved-ready 미포함)**: batch 1(27, v0.5-001/002)·batch 2(30, alias 반영됨) = only_batch=v0.5-005 + existing_seqs 로 자동 제외. 복합제 deferred(32, v0.5-005) = detail_confirmed≠true 로 제외. 에스오메프라졸/15행 = 0(애초 풀에 없음).

## 5. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(batch3 포함) | **PASS 62/62** (batch3 미포함 시 47/47 → +15 가 batch3 검증, 차등 확인) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (alias 무변경) |
| Type B suite | **PASS 7/7** |
| batch3 음성테스트 | **5/5** (incorporated=true→#74+#72 · >30→#73 · 에스오메프라졸→#66 · 기존 alias 충돌→#64 · 정상→PASS) |
| smoke | **PASS 12/12** |

## 6. smoke 결과 (회귀 불변 + batch3 미반영)
- 회귀: 타리비드→3 · 포사맥스→1 · 토렘→2 · 넥시움→0 · #/r/15(excluded B12) fail-safe. alias_count 123·product 85·ingredient 38·relation 30.
- **batch3 미반영 확인**: batch3 30 itemSeq 전부 product_aliases 미존재 · batch3 표면형 30건 전부 `resolveAliasIngredients` 빈 Set(아직 검색에 안 잡힘). **이전 batch live 유지**(라메졸캡슐20밀리그램→오메프라졸 2건).

## 7. 불변 / 안전 (Phase 7 무반영 게이트)
- **alias JSON 0-diff**(md5 불변), alias_count **123 유지** · product_aliases **85 유지** · verified_item_seqs **61 entries 유지**(12성분).
- relation **30 유지**, DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**, v0.1/v0.2 export·앱 코드·CI·batch1/batch2 AR **무변경**.
- batch3 전부 incorporated=false · queue status approved 신규전환 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1 incorporated 27 · batch 2 incorporated 30 그대로(queue approved 57 불변).

## 8. 다음 단계 (Phase 8 / batch 3 실제 반영 — PM 승인 필요)
- batch 3 30건을 alias JSON 반영 시 **alias 123 → 153**(product +30→115, verified +30→91 entries). 8성분 전부 기존 verified 키 → **append only, verified canonicals 12 유지**(신규 키 없음).
- Phase 6 와 동일 패턴 + **validator #74 옵션 A 갱신**(incorporated=false→{false,true} 정합, true는 #72 실제 반영 검증)이 반영 시 필요(현재 #74 는 strict false). → **Phase 8 PM 게이트.** 상세=`MediStack_v0.5_phase8_batch3_incorporation_plan.md`.
- 이후: held 23 + 추가 재수집(다른 페이지/성분) → 200 도달.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 단계는 생성만 — 실제 alias 반영은 Phase 8 PM 게이트.**
