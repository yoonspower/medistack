# MediStack v0.5 — bulk alias pipeline Phase 11 보고서 (batch 5 재수집 + approved-ready 생성, alias 무반영)

작성/실행일: **2026-06-11** / 단계: **Phase 11 batch 5 재수집 + approved-ready 30건 생성(생성만 — alias JSON 무변경, 반영은 Phase 12 PM 게이트)** / 상위: `..._bulk_alias_pipeline_plan.md`, `..._phase10_report.md`, `..._phase9_report.md`

> PM 판정(Phase 11): held 풀 소진 → **외부 nedrug searchDrug 재수집 허용**(max-per-ingredient 20~30·max-pages 8~10). 신규 후보 수집→getItemDetail 확정→**batch 5 approved-ready 24~30건 생성**. **alias JSON 수정 금지**(alias_count 176 유지), relation 30·DATA_URL·export·앱 불변. 실제 반영은 Phase 12.

---

## 1. 생성/수정 파일
| 파일 | 변경 |
|---|---|
| `data/candidates/bulk_alias_approved_ready_batch5_v0_5.json` | **신규** — batch 5 approved-ready 30건(incorporated=false) |
| `data/candidates/bulk_alias_approved_ready_batch5_v0_5.csv` | **신규** — 동일 30건 CSV |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | **신규 후보 142건 병합**(queue 177→319) + 신규 81건 detail_confirmed=true + meta(phase11_collection·phase11_confirmation) |
| `scripts/validate_bulk_alias_candidates.py` | 최소 보강 — batch5 approved-ready 검증 추가(번호 100~115): base 검증 + #113(≤30)·#114(incorporated=false strict)·#115(필드 보유) |
| (불변) `data/medistack_v0.3_aliases.json` · relation export(v0.1/v0.2) · batch1~4 AR · src/ · index.html · .github/ · DATA_URL | **무변경**(git diff 0, alias md5 불변) |

## 2. 재수집 (외부 nedrug searchDrug)
- **대상 성분**: 라이브 허용 13성분 전체(독시사이클린·레보티록신·레보플록사신·메트포르민·목시플록사신·미노사이클린·시프로플록사신·알렌드론산·오메프라졸·오플록사신·토라세미드·푸로세미드·히드로클로로티아지드).
- **파라미터**: `--max-per-ingredient 25` · `--max-pages 10` · `--batch-id v0.5-006` · `--phase 11`.
- **신규 수집 142건**(queue 177→319): **pending 83 단일성분** + **deferred 59 복합제**. 성분별 신규: 레보플록사신 25·시프로플록사신 25·히드로클로로티아지드 25(전부 combo)·알렌드론산 25(11 단일+14 combo)·메트포르민 25(5 단일+20 combo)·오플록사신 13·오메프라졸 4. (독시·레보티록신·목시·미노·토라세미드·푸로세미드 = 0 신규 — 현 페이지 깊이서 신규 단일 소진/잔여는 전부 combo·기존.)
- combo(복합제, ingrName '/') 자동 deferred 강등(메트포르민 20·알렌드론산 14·HCTZ 25). 에스오메프라졸 0.

## 3. getItemDetail 상세확정 (신규 pending 83)
- `--target-batch v0.5-006`로 신규 83건만 확정 → **confirmed 81** + surface_form_whitespace 2(nedrug 품목명 개행 → approved-ready 제외·pending 유지). combo/성분불일치/품목명불일치/실패/에스오메프라졸 **전부 0**.
- 확정 81건 = 단일성분·완제·경구·canonical⊆주성분. **status=pending 유지(approved 0)**, source_method→nedrug.getItemDetail·confidence→high.

## 4. batch 5 approved-ready 30건 (canonical 균등분산 6성분)
| canonical | 건수 | itemSeq → 표면형(품목명) |
|---|---|---|
| 레보플록사신 | 6 | 201906844 레보건정250밀리그램 · 201903868 레보나정100밀리그램 · 201903867 레보나정500밀리그램 · 200103330 레보박터정 · 201906940 레보사신정250밀리그램 · 199801068 레보스타정 |
| 메트포르민 | 5 | 201402049 그리코민서방정500밀리그램 · 202001548 글라비스정1000밀리그램 · 201206681 글로포민서방정 · 200400817 글루메트정 · 200001344 글루세라정500밀리그램 |
| 시프로플록사신 | 5 | 201901777 시프로투정250밀리그램 · 201601113 시프록스정 · 201508296 시프록신정 · 201801819 시프사신정250밀리그램 · 201901820 시플로뉴정250밀리그램 |
| 알렌드론산 | 5 | 201801386 알레드론정70mg · 201904313 알렌다정 · 201906584 알렌산정70밀리그램 · 201901596 알렌스타정 · 200512324 알로네이트정 |
| 오메프라졸 | 4 | 201704833 셀트리온오메프라졸캡슐20밀리그램 · 200411207 아메졸캡슐 · 199700918 아주오메프라졸캡슐 · 200411087 애니시드캡슐 |
| 오플록사신 | 5 | 201603948 오플로정 · 201601053 오플록정100밀리그램 · 199202946 옥타신정 · 200404693 제뉴원오플록사신정 · 201904655 지엘오플록사신정100밀리그램 |

(전부 단일성분·완제·경구·getItemDetail 원문확정·confidence high·risk_level low. 표면형=전체 품목명, Phase 4~10 동일 규약.)

## 5. canonical 분포 / 제외·보류 사유
- 분포: 레보플록사신6·메트포르민5·시프로플록사신5·알렌드론산5·오메프라졸4·오플록사신5 = **30**(`--ar-balanced` 라운드로빈, 오메프라졸은 풀 4건 전량).
- **held 51건**(confirmed 81 − batch5 30): Phase 12 반영 후 existing_seqs 가 batch5 30 제외 → batch 6 자동 회수.
- **제외**: batch1~4(110, alias 반영됨) + v0.5-005 잔여 = only_batch=v0.5-006 + existing_seqs 자동 제외. 복합제 deferred(신규 59) = detail_confirmed≠true 제외. surface_form_whitespace 2 = detail_confirmed≠true 제외. 에스오메프라졸/15행 = 0.

## 6. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(batch5 포함) | **PASS 92/92** (batch5 미포함 77/77 → +15 차등 확인) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (alias 무변경) |
| Type B suite | **PASS 7/7** |
| batch5 음성테스트 | **5/5** (incorporated=true→#114 · >30→#113 · 에스오메프라졸→#106 · 기존 alias 충돌→#104 · 정상→PASS) |
| smoke | **PASS 11/11** |

## 7. smoke 결과 (회귀 불변 + batch5 미반영)
- 회귀: 타리비드→3 · 포사맥스→1 · 토렘→2 · 넥시움→0 · #/r/15 fail-safe. alias_count 176·product 138·relation 30.
- **batch5 미반영 확인**: batch5 30 itemSeq 전부 product_aliases 미존재 · 표면형 30건 전부 `resolveAliasIngredients` 빈 Set. **이전 batch live 유지**(batch4 엑센정→오플록사신).

## 8. 불변 / 안전 (Phase 11 무반영 게이트)
- **alias JSON 0-diff**(md5 불변), alias_count **176 유지** · product 138 · verified 114/12성분.
- relation **30 유지**, DATA_URL **불변**, v0.1/v0.2 export·앱·CI·batch1~4 AR **무변경**.
- batch5 전부 incorporated=false · queue status approved 신규전환 0(approved 110 불변) · 복합제/brand_core/에스오메프라졸/15행 0 · published 봉인 · 제품 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1~4 incorporated 110 그대로.

## 9. 다음 단계 (Phase 12 / batch 5 실제 반영 — PM 승인 필요)
- batch 5 30건 반영 시 **alias 176→206**(product +30→168, verified +30→144). batch5 6성분 전부 **기존 verified 키**→**append only, verified canonicals 12 유지**.
- **🎯 alias 206 = v0.5 목표 200 도달·초과**(batch5 반영으로 200 달성).
- 반영 시 **validator #114 옵션 A 갱신 필요**(현재 strict false → {false,true}, true는 #112 실제 반영 검증 — Phase 4/6/8/10 패턴). 계획서: `MediStack_v0.5_phase12_batch5_incorporation_plan.md`.
- 잔여 버퍼: **held 51**(batch 6용) + 신규 deferred combo 59 + 기존 deferred tier(brand_core 14·기존 combo).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지 / **이 단계는 생성만 — 실제 alias 반영은 Phase 12 PM 게이트.**
