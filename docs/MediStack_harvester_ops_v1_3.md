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
