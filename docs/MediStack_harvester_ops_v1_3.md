# MediStack — relation harvester bot v1.3 운영 문서 (manual run 루틴)

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
