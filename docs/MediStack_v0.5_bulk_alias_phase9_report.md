# MediStack v0.5 — bulk alias pipeline Phase 9 보고서 (batch 4 approved-ready 생성, alias 무반영)

작성/실행일: **2026-06-11** / 단계: **Phase 9 batch 4 approved-ready 생성(생성만 — alias JSON 무변경, 반영은 Phase 10 PM 게이트)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase8_report.md`, `..._phase7_report.md`

> PM 판정(Phase 9): Phase 7 held 후보를 **네트워크 없이** 재사용해 **batch 4 approved-ready 생성**. **alias JSON(`data/medistack_v0.3_aliases.json`) 수정 금지**(alias_count 153 유지). 실제 반영은 다음 PM 승인 후 Phase 10. relation 30·DATA_URL·export·앱 불변.

---

## 1. 생성/수정 파일
| 파일 | 변경 |
|---|---|
| `data/candidates/bulk_alias_approved_ready_batch4_v0_5.json` | **신규** — batch 4 approved-ready 23건(incorporated=false) |
| `data/candidates/bulk_alias_approved_ready_batch4_v0_5.csv` | **신규** — 동일 23건 CSV |
| `data/candidates/bulk_alias_review_queue_v0_5.json` | meta 만 갱신(`phases`+9, `phase9_confirmation` 추가). **후보 0건 변경** |
| `data/candidates/bulk_alias_review_queue_v0_5.csv` | 컬럼순서 정규화(Phase 8 superset → confirm 표준순서, 후보 데이터 0-diff) |
| `scripts/validate_bulk_alias_candidates.py` | 최소 보강 — batch4 approved-ready 검증 추가(번호 80~95): base 검증 + #93(≤30)·#94(incorporated=false strict)·#95(필드 보유) |
| (불변) `data/medistack_v0.3_aliases.json` · relation export(v0.1/v0.2) · batch1/2/3 AR · src/ · index.html · .github/ · DATA_URL | **무변경**(git diff 0) |

## 2. held/staged 후보 → batch 4 선별
- Phase 5 confirmed 단일성분 83건 → batch 2(30, Phase 6) + batch 3(30, Phase 8) 반영 → 잔여 **held 23건**(detail_confirmed=true·batch v0.5-005·status pending).
- batch 3 의 30 itemSeq 가 Phase 8 에서 alias 진입 → `existing_alias_itemseqs()` 자동 제외 → batch 4 적격 풀 = **정확히 23건**(전부 pending·product_full_name·복합제 0·에스오메프라졸 0·기존 alias 표면형 중복 0).
- `--ar-balanced` + `--ar-limit 30` → 23 ≤ 30 이므로 **held 풀 전량(23건) 편성**, **held = 0**(v0.5-005 confirmed 풀 소진).

## 3. batch 4 approved-ready 23건 (canonical 5성분)
| canonical | 건수 | itemSeq → 표면형(품목명) |
|---|---|---|
| 레보티록신 | 2 | 201706147 씬지록신정75마이크로그램 · 201706861 씬지록신정88마이크로그램 (레보티록신나트륨수화물) |
| 레보플록사신 | 6 | 201801057 레보건정500밀리그램 · 201207402 레보라신정 · 200200467 레보미신정 · 201302165 레보바이정 · 201902151 레보바이정250밀리그램 · 201902152 레보바이정500밀리그램 (전부 레보플록사신수화물) |
| 시프로플록사신 | 7 | 200401235 시록신정250mg · 199100750 시폭사신정250밀리그람 · 201402874 시푸로신정 · 201907106 시프라신정250밀리그램 · 202002785 시프로사정 · 201505089 시프로신정 · 199202036 신일시프로플록사신염산염수화물정 (시프로플록사신염산염/수화물) |
| 알렌드론산 | 1 | 200402671 알렌맥스정70밀리그램(알렌드론산나트륨) |
| 오플록사신 | 7 | 199603322 엑센정 · 199102449 영풍오플록사신정100밀리그램 · 201405581 오라록신정100mg · 199102137 오로신정100밀리그램 · 201506769 오록사신정100밀리그램 · 199101034 오비드정 · 201309390 오플라정 (전부 오플록사신) |

(전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high·risk_level low. 전체 필드는 approved-ready 파일 참조. 표면형=전체 품목명, Phase 4~8 동일 규약.)

## 4. canonical 분포 / 제외·보류 사유
- 분포: 레보티록신2·레보플록사신6·시프로플록사신7·알렌드론산1·오플록사신7 = **23**. (held 풀 전량, balanced cap 미적용 — 23 < 30)
- **held 0**: v0.5-005 confirmed 단일성분(83) 전부 batch2/3/4 로 소진(30+30+23=83). 추가 batch 는 **재수집 필요**.
- **제외**: batch1(27)·batch2(30)·batch3(30) = only_batch=v0.5-005 + existing_seqs 자동 제외. 복합제 deferred(32, v0.5-005) = detail_confirmed≠true 제외. 미확정 pending 5(개행/실패 등) = detail_confirmed≠true 제외. 에스오메프라졸/15행 = 0.

## 5. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(batch4 포함) | **PASS 77/77** (batch4 미포함 62/62 → +15 차등 확인) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (alias 무변경) |
| Type B suite | **PASS 7/7** |
| batch4 음성테스트 | **5/5** (incorporated=true→#94 · >30→#93 · 에스오메프라졸→#86 · 기존 alias 충돌→#84 · 정상→PASS) |
| smoke | **PASS 11/11** |

## 6. smoke 결과 (회귀 불변 + batch4 미반영)
- 회귀: 타리비드→3 · 포사맥스→1 · 토렘→2 · 넥시움→0 · #/r/15 fail-safe. alias_count 153·product 115·relation 30.
- **batch4 미반영 확인**: batch4 23 itemSeq 전부 product_aliases 미존재 · batch4 표면형 23건 전부 `resolveAliasIngredients` 빈 Set. **이전 batch live 유지**(바이독시정→독시사이클린).

## 7. 불변 / 안전 (Phase 9 무반영 게이트)
- **alias JSON 0-diff**, alias_count **153 유지** · product_aliases **115 유지** · verified_item_seqs **91 entries(12성분) 유지**.
- relation **30 유지**, DATA_URL **불변**, v0.1/v0.2 export·앱 코드·CI·batch1/2/3 AR **무변경**.
- batch4 전부 incorporated=false · queue status approved 신규전환 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published 봉인 · 제품 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1/2/3 incorporated 87 그대로(queue approved 87 불변).

## 8. 다음 단계 (Phase 10 / batch 4 실제 반영 — PM 승인 필요)
- batch 4 23건 반영 시 **alias 153→176**(product +23→138, verified +23→114). batch4 5성분 전부 **기존 verified 키**→**append only, verified canonicals 12 유지**.
- 반영 시 **validator #94 옵션 A 갱신 필요**(현재 strict false → {false,true} 정합, true는 #92 실제 반영 검증 — Phase 4/6/8 패턴). 계획서: `MediStack_v0.5_phase10_batch4_incorporation_plan.md`.
- **200 목표**: held 소진(176) → **추가 재수집 ~24건 필요**(미노사이클린/토라세미드/푸로세미드/HCTZ 단일 등 다른 페이지/성분 searchDrug 재수집 → getItemDetail 확정 → batch 5).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 단계는 생성만 — 실제 alias 반영은 Phase 10 PM 게이트.**
