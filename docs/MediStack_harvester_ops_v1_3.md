# MediStack — relation harvester bot v1.3 운영 문서 (manual run 루틴)

> **참고(2026-06-16):** 대량 후보는 별도 **Relation Factory Bot v1.4**(`scripts/relation_factory_bot_v1_4.py` + `adversarial_verify_relation_factory_v1_4.py`) 트랙에서 생성·적대검증한다(harvester 와 비연동). factory 운영 절차는 `docs/MediStack_operator_runbook_v1_3.md` §12.6.
> factory reviewer-ready 의 첫 reviewer-gated 통합 후보 = **F1 퀴놀론 18건**(`scripts/integrate_f1_quinolone_batch_v1_4.py` dry-run·live 0·harvester 비연동·schedule 무관).
> 두 번째 후보 = **F2 테트라사이클린 5건**(`scripts/integrate_f2_tetracycline_batch_v1_4.py` dry-run·live 0·60→65·harvester 비연동·schedule 무관).

작성일: 2026-06-14 · 상태: **운영 가이드 / schedule 비활성** · 대상 AI/PM 세션 핸드오프용 자기완결 문서

> 이 문서는 harvester bot 의 **수동 운영 절차**와 **안전 불변**을 정리한다. 봇은 PM review queue(분석 산출물)만 만들고
> **live relation 을 만들지도 배포하지도 않는다**(`do_not_implement_yet`). 구현/승격은 PM + source 재확인 + clinical reviewer 후 별도 단계.

## 0. 한 줄 요약
relation harvester bot v1.3 = `fetch → detect → gate → PM 큐` 오케스트레이터. 출력은 **`data/harvest_queue/` 전용**.
판정은 안 하고 **라우팅만**(source_confirm_gate + detector 가 판정). live/배포/승격 **0**.

## 1. 첫 운영 run 결과 (2026-06-14)
- **online manual subset run 완료 + PASS**(이전 세션 기록, antacid 트랙 §11 에 reconcile). 두 antacid 후보(AT-FEX 펙소페나딘 · AT-ITZ 이트라코나졸)를 `antacid_draft_confirmed` 로 확정하고, 기존 v1.2 draft 와 **다른 유효 대표 itemSeq** 를 `online_reconcile` provenance 로 보강(기존 근거 폐기 0).
- **커밋된 `data/harvest_queue/` 베이스라인 = offline dry-run(fixtures, network=0) 산출물**(결정적·재현가능). 현재 `run_meta.json` 기준:
  - mode `offline_dryrun(fixtures)`, SDK network=0, live_relations_created=0, live_promotions=0, deploy=none.
  - counts: harvest_total 77 · source_checked 29 · draft_eligible 3 · needs_review 24 · source_reject 2 · already_covered 6 · hold 46 · rejected_precheck 52.
  - safety: live_data_written=false · write_scope=`data/harvest_queue/ only` · judgment=`source_confirm_gate + detector(봇은 라우팅만)`.
- **online run 산출물은 커밋하지 않는다**(재현가능 — 동일 입력이면 재생성됨). 커밋되는 것은 결정적 offline dry-run 베이스라인뿐. SDK 런타임 캐시/raw/log(`data/harvest_queue/_sdk/`)는 `.gitignore`(리뷰 큐 산출물 아님).
- SDK 캐시 오염 fix(2026-06-14, 커밋 3804b78): `cache_dir/raw_dir` 에 mode 서브디렉토리(`offline/`·`online/`) 분리 → fixture↔실데이터 캐시 오염 차단.

## 2. manual run 루틴 (로컬, 권장 순서)
모든 단계는 보호/live 데이터를 한 줄도 수정하지 않는다. 위반 시 가드가 FAIL.

```bash
# (선택) SDK dry-run 자가검증 — 네트워크 0
python3 medistack_sdk/test_nedrug_client_dryrun.py

# (A) offline dry-run(fixtures, network=0) — 결정적 베이스라인. CI 기본값과 동일 서브셋.
python3 scripts/guard_no_live_write_v1_3.py --run-bot \
  --bot-args "--ingredients 세파클러,프레드니솔론,아세타졸아미드,펙소페나딘"

# (B) online 실 nedrug fetch — 실데이터. 산출물은 커밋 제외(재현가능).
python3 scripts/guard_no_live_write_v1_3.py --run-bot --bot-args "--online"

# (C) 큐 검증(스키마·no-live-promote·금칙어·PM smoke)
python3 scripts/validate_harvest_queue_v1_3.py

# (D) live data 무수정 재검증(deploy 게이트와 동일 검증대상)
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
python3 scripts/validate_full_drug_name_index.py data/full_drug_name_index_sample_v1_0.json
```

- **guard wrapper(`guard_no_live_write_v1_3.py --run-bot`)로 봇을 감싸 실행**한다. 가드가 봇 실행 전후로 ① 보호셋(export·full index·alias·src·validator·SDK) sha256 불변 ② write-scope=`data/harvest_queue/` 한정 ③ SDK 밖 직접 nedrug 호출 신규 0 을 강제한다.
- **PM review queue 확인**: `data/harvest_queue/pm_review_queue.md`(사람이 읽는 검토 큐) + `draft_candidates.json` + `needs_review.csv` + `source_check_results.csv`. draft_eligible 후보만 `antacid_draft_confirmed` 류.
- CI(`.github/workflows/harvest.yml`)는 같은 체인을 돌리고 기본 **artifact 업로드**(main 무오염). `commit=true` 옵트인 시에만 **전용 브랜치 + PR**(직접 main push 금지).

## 3. 안전 불변 (변경 금지)
- 봇 write-scope = **`data/harvest_queue/` 전용**. 그 밖 한 줄이라도 바뀌면 가드 FAIL.
- 보호셋(sha256 고정): `data/medistack_v0.*` export, `full_drug_name_index_*`, `medistack_v0.3_aliases*`, `index.html`, `src/**`, `.github/workflows/*`, `scripts/validate_*.py|js`, `medistack_sdk/**`.
- 봇은 **판정하지 않는다** — source_confirm_gate(fail-closed) + detector 가 판정, 봇은 라우팅/큐 생성만.
- **live relation 생성·배포·승격 0.** 모든 큐 후보 `do_not_implement_yet`. 구현은 PM + source 재확인 + clinical reviewer 후 별도.
- nedrug 조회는 **SDK(`medistack_sdk/nedrug_client.py`) 단일 게이트웨이**만 — retry·cache(mode 분리)·raw·log·normalize·offline fixtures. SDK 밖 직접 http 신규 금지(점진 마이그레이션 allowlist 만 예외, 줄어들어야 함).

## 4. 자동화 상태 (보류 유지)
- **`schedule` 비활성**(harvest.yml 에서 cron 주석처리). 트리거 = 수동 `workflow_dispatch` 만(mode: offline/online, commit: 기본 false).
- **하루 1회 자동화는 아직 보류.** 안정화(여러 수동 online run 으로 큐 품질/오탐 검증) 후 PM 결정으로 `schedule` 주석 해제(KST 월 03:00 = UTC 일 18:00 초안). 이번 라운드에서 활성화하지 않는다.
- 자동화 활성화 전 충족 조건(권장): 수동 online run N회 안정 · 큐 validator 무위반 지속 · no-live-write 가드 무위반 · PM 검토 피드백 반영 · direct-http allowlist 추가 감소.

## 5. 다음 manual run 시 체크리스트
- [ ] `medistack_sdk/test_nedrug_client_dryrun.py` PASS(네트워크 0).
- [ ] guard `--run-bot` (offline 또는 online) PASS — 보호셋 불변·write-scope·direct-http 0.
- [ ] `validate_harvest_queue_v1_3.py` PASS.
- [ ] live data 무수정 재검증(v0.2 export + full index) PASS.
- [ ] online run 산출물은 **커밋 제외**(재현가능). 커밋은 결정적 offline 베이스라인만(필요 시).
- [ ] `pm_review_queue.md` 검토 → draft_eligible 후보를 PM 라운드로 핸드오프(직접 승격 금지).

## 6. 보호셋 ↔ 사람 dev 편집 구분 (2026-06-15 메모)
- **보호셋(§3)은 "봇 런타임이 안 건드리는 경계"** 다 — `guard_no_live_write_v1_3.py --run-bot` 이 봇 실행 *전후* sha256 불변으로 강제한다. 고정 baseline 해시를 pin 하는 것이 아니라 **단일 봇 런 내 불변**을 검사한다. 따라서 PM/AI 의 **승인된 dev 편집**(예: validator·render 보강)으로 보호셋 파일이 바뀌어도, 그 편집을 commit 한 뒤 가드를 돌리면 봇은 여전히 그 파일을 안 건드리므로 **PASS** 다(봇 쓰기 ≠ 사람 dev 편집).
- 검증: 2026-06-15 avoid_concomitant 준비로 `scripts/validate_medistack_v0_2_export.py`(#15 추가)·`src/js/render.js`(ACTION_ORDER) 를 편집한 뒤 `--run-bot` 재실행 → 보호셋 47파일 sha256 불변·write-scope=`data/harvest_queue/` 한정·direct-http 0 **PASS**(봇은 편집된 파일을 건드리지 않음).
- **schedule 여전히 비활성**(§4). 이번 라운드도 자동화 활성화·online 자동 실행 0. 봇 live/배포/승격 0.

## 7. 운영 루틴 재확인 (2026-06-15 clinical reviewer 핸드오프 라운드)
이 라운드는 **승격이 아니라 통합 준비/핸드오프**다. 봇 운영 원칙에 변화 없음 — 재명시만 한다.
- **봇 = 후보 수집·라우팅만.** live relation 생성·배포·승격 **0**. 모든 큐 후보 `do_not_implement_yet`. 구현/승격은 PM + source 재확인 + **clinical reviewer 노트** 후 별도 단계(→ `docs/MediStack_clinical_reviewer_handoff_v1_2.md`).
- **manual run 루틴(§2) 불변**: ① `medistack_sdk/test_nedrug_client_dryrun.py`(net 0) → ② `guard_no_live_write_v1_3.py --run-bot`(offline 또는 `--online`) → ③ `validate_harvest_queue_v1_3.py` → ④ live data 무수정 재검증(v0.2 export + full index). guard wrapper 가 보호셋 sha256 불변·write-scope=`data/harvest_queue/` 한정·SDK 밖 direct-http 0 을 강제.
- **runtime harvest_queue 커밋 금지**: online run 산출물은 재현가능 → **커밋 제외**. 커밋되는 건 결정적 offline 베이스라인뿐. `data/harvest_queue/_sdk/` 는 `.gitignore`.
- **PM review queue 확인**: `data/harvest_queue/pm_review_queue.md` 의 draft_eligible 후보를 PM 라운드로 핸드오프(직접 승격 금지).
- **schedule 비활성 유지**(§4). **하루 1회 자동화는 계속 보류.** 활성화 전 충족 권장: 수동 online run N회 안정 · 큐 validator 무위반 지속 · no-live-write 가드 무위반 · direct-http allowlist 감소. 이번 라운드에서 활성화하지 않는다.

## 8. 2차 online run 결과 (2026-06-15)
manual `--online` run 을 guard wrapper 로 1회 수행. **live/배포/승격 0** · 보호셋 sha256 불변 · 산출물은 분석/요약만(runtime 큐 커밋 제외).

- **실행**: `python3 scripts/guard_no_live_write_v1_3.py --run-bot --bot-args=--online` → 가드 **PASS**(보호셋 48파일 불변 · write-scope=`data/harvest_queue/` 한정 · direct-http 신규 0).
  - argparse 주의: `--bot-args --online` 은 `--online` 을 값 없는 옵션으로 오인 → **`--bot-args=--online`(= 형식)** 으로 전달.
- **SDK**: network **0** · cache **68** · fixture 0 · offline_miss **0** · error 0 → 6/14 online 캐시(`_sdk/cache/online/`) 전부 적중. 결정적·재현가능, 신규 네트워크 0.
- **counts**: harvest 78 · source-check 29 → draft 6 · needs_review 11 · reject 12 · already_covered 7 · hold 46 · rejected_precheck 52 · KPI 60.
- **1차 offline 베이스라인(6/14) 대비**: draft 3→6 · needs_review 24→11 · reject 2→12. online 이 offline_miss 23→0 해소 → 실 라벨로 직접근거 확인(draft↑)·문헌-only deny(reject↑)·fail-closed 감소(needs_review↓). hold/rejected_precheck 는 KPI/carry 결정적이라 불변.
- **queue validator**: `validate_harvest_queue_v1_3.py` **PASS**(스키마·no-live-promote·safe_copy 금칙어 0·PM smoke).
- **분석 결론**(상세 → `docs/MediStack_candidate_backlog_v1_3.md`): draft 6건 **전부 기존 트리아지 항목과 동일**(DF01~DF05 + AT-FEX, itemSeq 대조) → **신규 draft-ready 0**. 신규 후보는 needs_review 10(다이유레틱/코르티코스테로이드 대표 itemSeq 미확보)·reject 12(세파계×철분 10 등 한국 허가사항 미기재)뿐.
- **커밋 정책 적용**: runtime `data/harvest_queue/`(6 tracked 파일 변경)는 **`git checkout` 으로 복원**(커밋 제외, offline 베이스라인 유지) · `_sdk/` 는 `.gitignore`. 분석 요약만 `data/review/harvest_run2_summary_v1_3.json` 로 보존.
- **schedule 여전히 비활성**(§4). 자동화 활성화 0 · 봇 live/배포/승격 0. (2차 online run 안정 — 활성화 조건 카운트 누적, PM 결정 전까지 보류.)

## 9. 검색 깊이 정책 — exact 주성분 우선 + deep fallback (2026-06-15)

`scripts/verify_factory_sources_v1_2.py` 의 `search_itemseqs` 는 봇(`run_nutrient_sourcecheck`/`run_antacid_sourcecheck`)이 성분→대표 itemSeq 를 해결하는 단일 진입점이다. 2026-06-15 needs_review 재확인에서 **substring 지배 누락**이 드러났다: `searchDrug?ingrName1=프레드니솔론` 은 부분문자열로 매칭되는 **메틸프레드니솔론**이 앞페이지를 점유해, 얕은 검색(max_pages=2)에서 국내 프레드니솔론 단일 경구품(소론도정 199602982)이 잡히지 않았다(p7 위치). 1차에선 needs_review(fail-closed)로 떨어졌고, 적대 검증이 이를 거짓음성으로 지적했다.

**개선(최소 변경)**: `search_itemseqs(opener, ingredient, ..., deep_max_pages=20)` 에 deep fallback 추가.
- 기본 `max_pages` 얕은 검색 먼저.
- 얕은 검색에 **정확 주성분(주성분==성분명) 후보가 있으면** 그대로 반환(`reason='ok'`).
- 정확 주성분 후보가 **없고** 결과가 성분명을 부분문자열로 포함하는 **더 긴 주성분**에 점유돼 있으면(substring 지배 감지), `deep_max_pages` 까지 **1회 deep 검색**해 **정확 주성분만**(`exact_only`) 재탐색(`reason='ok_deep_exact'`).
- 필터(수출용/원료/외용/주사/복합제/취소품목 제외)·SDK-only·캐시 네임스페이스(`offline/`·`online/`)는 그대로.
- **무조건 깊게 늘리지 않는다** — exact 부족 + substring 지배일 때만 deep(비용 최소화). theme map 78 스캔 결과 deep fallback 발동은 **프레드니솔론 1건뿐**, 나머지 21종(shallow exact 15 + no-product 6)은 무변경(기존 confirmed itemSeq 회귀 0).
- `exact_only` 는 `메칠프레드니솔론`(메칠/메틸 표기차로 exclude 우회) 같은 **부분문자열 동명 오채택**도 차단한다.

**회귀 테스트**: `scripts/test_search_depth_v1_3.py`(FakeOpener·네트워크 0·결정적) — ①프레드니솔론 deep fallback 이 소론도정 정확채택+메칠 오채택 금지+수출/원료 종료 금지 ②미유통(부메타니드 등) 0건 시 deep 미호출 ③하이드로코르티손 외용만이면 deep 후에도 [] ④PM-ready 비교군 얕은 exact 있으면 deep 미호출+기존 itemSeq 유지.

봇은 이 개선을 자동 승계한다(import 경로 동일). runtime harvest_queue 는 여전히 커밋하지 않으며 schedule 비활성 유지.

## 10. 3차 online run + 검색 깊이 하드닝 (2026-06-15 round3)

개선된 `search_itemseqs` 가 harvester full online run 에 제대로 반영되는지 재확인하고, deep fallback 의 **과다 호출**을 하드닝했다. **live/배포/승격 0** · 보호셋 sha256 불변 · runtime 큐 커밋 제외.

- **실행**: `python3 scripts/guard_no_live_write_v1_3.py --run-bot --bot-args "--online --kpi-limit 60"` → 가드 **PASS**(보호셋 **49** 파일 sha256 불변 · write-scope=`data/harvest_queue/` 한정 · direct-http 신규 0).
- **SDK**: 첫 실행 network **3** · cache 139, 재실행 network **0**(완전 캐시·결정적) · error 0.
- **counts**: harvest 78 · source-check 29 → **draft 7 · needs_review 9 · reject 13** · already_covered 7 · hold 46 · rejected_precheck 52 · KPI 60.
- **2차 run(§8) 대비**: draft **6→7** · needs_review **11→9** · reject **12→13**.
  - **D-CORT-01 프레드니솔론×칼륨**: needs_review(검색 0건 false-negative) → **draft(source_confirmed, 소론도정 199602982)**. deep fallback(`ok_deep_exact`)이 harvester 에 자동 반영됨을 입증(= DF-PRED-01 자동 queue 반영).
  - **D-CORT-02 프레드니솔론×칼슘**: needs_review(fail-closed) → **reject**(라벨 확보·칼슘 방향성 동거어 부재). 개선된 검색으로 fail-closed 가 확정 deny 로 격상.
  - 나머지 분포 결정적 불변. AT-ITZ-01 은 `already_covered` 유지(id61 live). 요약 → `data/review/harvest_run3_summary_v1_3.json`.

**검색 깊이 하드닝 (deep fallback 발동 조건 정밀화)**: deep fallback 은 **다른 약물의 연속 명칭(접두사 확장)** 이 얕은 페이지를 점유할 때만 의미가 있다(예: 메틸프레드니솔론이 프레드니솔론을, 에스오메프라졸이 오메프라졸을, 덱스란소프라졸이 란소프라졸을 지배). **염/수화물(접미사형 `X나트륨`·`세파클러수화물`)과 복합제(`Y/X`)** 는 `exact_only` deep 로 절대 복구되지 않으므로(주성분명 'X염'≠'X'), 이런 superset 에는 deep 를 발동하지 않도록 `_prefix_dominated(rows, ingredient)` 헬퍼로 한정했다(성분명 앞 글자가 한글=연속 명칭일 때만 지배 판정).
- **측정**: theme map(25) + live PPI 4종 스캔에서 deep 발동 **20 → 6** (productive 3=프레드니솔론/오메프라졸/란소프라졸 전부 보존, **picks/reason 회귀 0**). 남은 3(세팔렉신/플루드로코르티손/라베프라졸)은 연속명 derivative superset(메틸올세팔렉신리시네이트·미분화플루드로코르티손아세테이트·조라베프라졸나트륨)로, deep 가 정확 base 부재를 확인 후 무해 반환(보수적·정상).
- **harvester 영향 중립**: online run 분포 7/9/13 불변 — 하드닝은 불필요 네트워크만 절감.

**substring 지배 탐색 (작업 C)**: `scripts/analyze_substring_domination_v1_3.py` → `data/review/substring_domination_scan_v1_3.json`. ingredient universe(theme∪carried∪live∪KPI=366)에서 proper-substring 쌍 **40**건 산출, **접두사형(다른약물) 5 / 접미사형(염·수화물 35)** 분류. 접두사형 5 중 nutrient-scope 는 프레드니솔론(처리완료·draft)·오메프라졸·란소프라졸. **오메프라졸/란소프라졸도 substring 지배**(에스/덱스 enantiomer·combo 가 base 단일·경구를 얕은 페이지에서 지배)로 확인됐으나, 둘 다 **이미 live**(오메프라졸 id13/14 itemSeq 200411095=오메라졸캡슐, 란소프라졸 id36/37 itemSeq 201308978=뉴란소캡슐 — read-only fetch 로 base 단일·경구·enantiomer 문자열 없음 확정)이라 신규 조치 불필요. 세티리진·펜타닐은 영양소 scope 밖.

**회귀 테스트 보강**: `scripts/test_search_depth_v1_3.py` 에 ⑤ 하드닝 케이스 추가(염 접미사·복합제는 deep 미발동, 연속명 접두사만 deep 발동) — 총 **5종 PASS**.

- **커밋 정책**: runtime `data/harvest_queue/`(8 tracked 파일)는 **`git checkout` 으로 복원**(커밋 제외) · `_sdk/` 는 `.gitignore`. 분석 요약/탐색만 `data/review/` 에 보존.
- **schedule 여전히 비활성**(§4). 자동화 활성화 0 · 봇 live/배포/승격 0.

## 11. substring 검색 위험 광역 탐색 (2026-06-15 round3 후속)

§10 substring 탐색(universe 366)을 **full drug name index distinct ingredient 전체**까지 확대. `scripts/analyze_substring_search_risk_v1_3.py` → `data/review/substring_search_risk_v1_3.json`. 상세 → `docs/MediStack_substring_search_risk_v1_3.md`.

- **universe**: full index 2,225 ∪ alias(한글) 27 ∪ seed 367 = scan 2,292(단일성분 922). proper-substring 쌍을 **diff-active 접두사**(메틸/에스/덱스 = 다른 약물·진짜 위험) vs **형태접두사**(무수/미세/제피 = 같은 약물) vs **염/수화물 접미사** vs 복합제로 분류.
- **분류**: high_risk 10 · medium_risk 14(seed 밖) · salt_or_formulation_trap 143 · no_action 2.
- **deep-check(cache-first SDK·SDK-only)**: high(diff-active+seed) 10종. **shallow_miss_confirmed = baseline 3종뿐**(프레드니솔론·오메프라졸·란소프라졸, 처리/확인 완료). 신규 diff-active 7종(로라타딘·세티리진·세팔렉신·암로디핀·졸피뎀·펜타닐·펜타닐시트르산염)은 **전부 shallow_already_safe**(다른 활성성분 superset 이 base 를 지배하지 못함) + 영양소 트랙 밖.
- **결론**: 광역 universe 에서도 **신규 substring 지배 false-negative 0 · 신규 draft 후보 0**. deep fallback 하드닝이 광역에서도 과다호출 없이 정확 동작. 형태접두사 domination(무수리세드론산나트륨 등)은 deep fallback 이 무해 복구·live bisphosphonate relation(리세드론산 itemSeq 201903166 등) 정확.
- **불변**: live/protected 무수정 · SDK-only(direct-http 신규 0) · runtime 큐 커밋 0 · live 승격 0 · schedule 비활성.

## 12. schedule 켜기 전 안전 체크리스트 (2026-06-15 — 활성화 아님·문서화만)

> **이 라운드는 schedule 을 켜지 않는다.** `.github/workflows/harvest.yml` 의 `schedule:`/`cron:` 은 주석 유지(§4).
> 아래는 **나중에 PM 이 자동화를 켜기로 결정할 때** 활성화 직전 통과해야 할 게이트만 정의한다(실행 아님). harvester 의 기존
> no-live-promote 불변(§3·§7)을 자동 트리거 맥락으로 재확인하는 것이며, 새 권한을 주는 게 아니다.

활성화 직전 점검(전건 충족 시에만 cron 주석 해제 — 그래도 별도 PM 결정):

- [ ] **트리거 안정성**: 여러 회의 수동 `workflow_dispatch`(offline+online) run 이 큐 validator 무위반으로 안정. cron 도입 후에도 1차는 `workflow_dispatch` 와 동일 경로(mode/commit 입력 동일)여야 한다.
- [ ] **output = artifact only**: 자동 run 의 산출물은 **분석/요약 artifact**(`data/review/…`)와 runtime 큐(`data/harvest_queue/`)뿐. live export/full index/aliases/src/.github 무수정.
- [ ] **commit 기본 false**: 자동 run 은 **기본 commit=false**(workflow 입력 기본값). 자동 커밋·자동 PR 머지 금지. 결정적 offline 베이스라인 외 커밋 금지.
- [ ] **live write 0**: 자동 run 이 live relation 을 0건 생성. `published`/`clinical_reviewed`/`reviewed_by` 무변경. 모든 후보 `do_not_implement_yet`.
- [ ] **no-live-write guard 통과**: 자동 run 도 `guard_no_live_write_v1_3.py --run-bot` 경로를 거쳐 보호셋 sha256 불변 · write-scope=`data/harvest_queue/` 한정 · direct-http 신규 0 을 강제.
- [ ] **runtime queue 커밋 금지**: `data/harvest_queue/` 의 online run 산출물은 재현가능 → 커밋 제외(`_sdk/` 는 `.gitignore`). 자동화가 이를 커밋하지 않는지 확인.
- [ ] **PM review queue만 생성**: 자동 run 의 사람-대면 출력은 `data/harvest_queue/pm_review_queue.md`(draft_eligible 후보 라우팅)뿐. 직접 승격 경로 없음.
- [ ] **자동 integrate 금지**: schedule 을 켠 뒤에도 **integrate_*.py / live 통합은 절대 자동 실행 안 함**. 승격은 항상 사람 PM + source 재확인 + clinical reviewer 노트(§8 핸드오프) + `--pm-approved --reviewer-note` 수동 단계.
- [ ] **실패 시 알림/보고만**: 자동 run 실패는 알림/로그/요약 보고로만 처리(자동 재시도로 live 쓰기 시도 금지). 실패가 안전 위반으로 번지지 않게 fail-soft.

> 활성화하더라도 harvester 의 역할은 **후보 수집·라우팅**에 영구 고정된다(§7). 자동화는 '핸드오프 큐를 더 자주 갱신'할 뿐,
> live·배포·승격 권한을 얻지 않는다. cron 초안은 KST 월 03:00(UTC 일 18:00)이나 이는 예시이며 PM 결정 전까지 주석 유지.

## 13. 새 theme map / relation family 편입 절차 (2026-06-15 theme map expansion 라운드)

> **배경**: 같은 theme map(`vfs.SEARCH_INGREDIENTS` 25)을 반복 online run 하면 draft 분포가 기존 트리아지로 수렴해
> **신규 draft-ready 0**(run2·run3 입증). 신규 relation 확장은 **새 seed/family 의 수동 설계**가 선행돼야 한다.
> 이번 라운드에 신규 family 3종을 **theme map 밖에서** 설계·source-check 해 draft-only 6건을 만들었다
> (`docs/MediStack_theme_map_expansion_v1_3.md`). **harvester 에는 아직 편입하지 않았다.**

신규 family 를 harvester 자동 경로에 넣을지는 **후속 PR / PM 승인 사항**이며, 넣더라도 순서는 고정이다:

1. **source-check queue** — 새 후보를 `data/review/theme_map_source_check_queue_v1_3.json` 류로 우선순위화(P0/P1/P2/HOLD). SDK-only·≤2 fetch·직접 HTTP 0.
2. **PM review** — source-confirmed 만 draft 후보로. high-risk(항응고/항암/정신건강/소아/임신/herbal/문헌단독/방향반대/약-약)는 hold.
3. **draft-only** — `data/drafts/…` 에 `live_integration_forbidden=true`·`published=false`·`clinical_reviewed=false`·`reviewed_by` 공란. 검증기(`validate_theme_map_expansion_v1_3.py`)+smoke 통과.
4. **live 금지** — 실제 승격은 clinical reviewer note + `--pm-approved --reviewer-note` 수동 단계(§8). harvester 가 자동 승격하지 않는다.

> **편입 시 주의(반복 run 비효율)**: theme map 에 seed 를 추가할 때만 새 draft 가 나온다. 같은 seed 재실행은 비용만 든다 —
> 새 seed 없이 run 횟수만 늘리지 말 것. seed 추가는 `vfs.SEARCH_INGREDIENTS`(nutrient) 또는 `harvest_relation_bot_v1_3.py`
> `ANTACID_CANDIDATES`(antacid) 편집(보호셋 아님 — 사람 dev 편집 가능, §6)이며, 그 자체가 PR 리뷰 대상이다.
> schedule 은 비활성 유지(§12). runtime queue(`data/harvest_queue/`) 커밋 금지(§5).

## 14. theme map expansion 편입 — manual flag (2026-06-16 프롬프트 9 · branch+PR)

§13 의 신규 family 6건(프롬프트 8 적대검증 완료)을 harvester 에 **candidate-only 로 편입**했다. **live 통합·schedule 활성화·자동 integrate 0.** §13 이 권한 부재를 재명시한 것과 같이, 이 편입도 harvester 에 승격 권한을 주지 않는다 — PM review queue 를 더 풍부하게 만들 뿐이다.

**방식 = manual flag(기본 비활성) + config-driven 격리 provider** (옵션 1). 별도 runner(옵션 2) 대신 flag 를 택한 이유: "harvester 편입"의 직접 구현이면서, 모든 신규 로직을 격리 provider 모듈로 빼 **기본 run 회귀 0**(플래그 없으면 byte-동일)·validator/smoke 단순화를 동시 달성.

```bash
# theme map expansion 후보를 candidate-only 로 PM 큐에 편입(guard wrapper 권장)
python3 scripts/guard_no_live_write_v1_3.py --run-bot \
  --bot-args "--ingredients 세파클러,프레드니솔론,아세타졸아미드,펙소페나딘 --include-theme-map-expansion"
# provider 단독(요약 갱신) — review summary 만 커밋
python3 scripts/theme_map_harvest_provider_v1_3.py --emit \
  --summary-out data/review/theme_map_harvest_incorporation_v1_3.json --stamp 2026-06-16
# 편입 검증 + 렌더 smoke
python3 scripts/validate_harvester_theme_map_v1_3.py     # 17 검사군 + 결함주입 9
python3 scripts/smoke_harvester_theme_map_v1_3.py         # PM queue + 6 카드 렌더-safe
```

- **seed 의 단일 진실원** = `data/config/theme_map_seeds_v1_3.json`(읽기 전용 policy/pointer). provider 는 이 config + source_of_truth 아티팩트(draft batch / candidates / adversarial ledger)만 읽는다 — SDK·네트워크 0, live/protected 무수정.
- **default disabled**: `--include-theme-map-expansion` 없으면 provider 미호출 → 기존 78-후보 run 무변경(기본 offline/online run, KPI 스캔 모두 그대로).
- **출력**: `data/harvest_queue/theme_map_pm_review_queue.md`(LIVE 아님·자동 승격 금지·source quote/app copy 분리·제품/구매/제휴 없음 배너) + `theme_map_draft_candidates.json`(draft 6) + `theme_map_hold_report.json`(hold 7). 모든 행 live_integration_forbidden=true·published=false·clinical_reviewed=false·reviewed_by 공란·do_not_implement_yet=true.
- **runtime 산출물 커밋 금지**: `data/harvest_queue/theme_map_*` 는 `.gitignore`(§5 와 동형). 커밋되는 건 review summary `data/review/theme_map_harvest_incorporation_v1_3.json` 뿐.
- **신규 category(review-level 처리만, src 무수정)**: `acid_reducing_drug`(세팔로스포린 acid-reducer — pH 의존, id61 `al_mg_antacid` 와 구분·H2/PPI 포함) · `fat_soluble_vitamin`(지용성 비타민군). validator 가 ①약물 category 를 영양소로 표기 ②acid-reducer 를 al_mg_antacid 로 축소 ③지용성/비타민K 항응고 framing ④보충 권유·제품 문구 를 전부 차단.
- **무충돌**: theme map 후보 id 는 `TM-*`(기존 F-*/AT-*/KPI- 와 disjoint). 기존 harvester theme map 의 `F-CEPH-03/08`(세프포독심/세프디토렌×**철분**)과는 counterpart(=acid_reducing_drug)·ingredient 문자열(세프포독심**프록세틸**)이 달라 무충돌. live 60·pending(칼륨 4·AT-FEX)과도 (ingredient,counterpart) 무중복(validator 검증).
- **schedule 비활성 유지**(§4·§12). 편입은 자동 실행을 켜지 않는다. live 통합은 clinical reviewer note + 수동 단계 후 별도 PR.
- **live 통합 reviewer-gated 준비(2026-06-16, PR #3 merge 후·승격 0)**: theme map 6건의 live 통합 dry-run integrator(`scripts/integrate_theme_map_draft_batch_v1_3.py`, 기본 dry-run·`--pm-approved --reviewer-note` 전제·멱등) + reviewer 패키지/category 정책/grouping 전략 문서 + reviewer-note 게이트·dry-run validator·smoke 작성. 예상 60→66(id 62~67·export sha 불변). **live 선행조건**: v0.2 validator #15(avoid_concomitant⇒al_mg_antacid) 를 acid_reducing_drug 포함 확장(TM-CEPH-AC-02) + src getFacets/render chip(별도 PR). 정본 = `docs/MediStack_reviewer_package_theme_map_v1_3.md`, 실행 프롬프트 = next_prompts 프롬프트 11.
- **페니실라민 FE/ZN subset 우선 준비(2026-06-16·선행조건 0·승격 0)**: theme map 6건 중 페니실라민 × 철분/아연 2건만 별도 subset(`scripts/integrate_penicillamine_subset_v1_3.py` dry-run + 게이트/validator/smoke + 전용 reviewer 패키지·mechanism 결정 문서). 일반 영양소(counterpart_category=null)라 **validator/src/facet/chip 선행조건 0**(현행 v0.2 PASS 실증) → 6건 중 최우선 통합 후보(60→62). dry-run = `data/review/penicillamine_subset_live_dryrun_v1_3.json`, 실행 프롬프트 = next_prompts 프롬프트 15. subset 게이트와 full-6 게이트는 상호 배타·동시 실행 금지.
