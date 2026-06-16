# MediStack — 운영자 Runbook (v1.3, 2026-06-15)

작성일: 2026-06-15 · 상태: **운영 가이드 / schedule 비활성 · live 승격 0** · 대상 PM/AI 세션 핸드오프용 자기완결 문서

> 이 문서는 MediStack 의 **일상 운영 절차**를 한 곳에 묶는다. harvester 수동 운영 → PM review queue 확인 → reviewer note 확보 →
> dry-run 검증 → live 통합 승인 → deploy → rollback 까지의 흐름이다. 세부 정본은 상호참조로 가리킨다(중복 최소화):
> harvester 운영 → `MediStack_harvester_ops_v1_3.md` · 핸드오프 → `MediStack_clinical_reviewer_handoff_v1_2.md` ·
> reviewer 패키지 → `MediStack_reviewer_package_potassium_v1_3.md` / `MediStack_reviewer_package_antacid_fex_v1_3.md` ·
> schedule 활성화 → `MediStack_harvester_schedule_activation_v1_3.md` · 다음 라운드 → `MediStack_next_prompts_2026_06_15.md`.
>
> **불변 전제**: live 승격 0 · published/clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 UI 0 · schedule 비활성 · 칼륨 보충 권유 0.

---

## 0. 현재 라이브 스냅샷 (2026-06-15)

| 위치 | 값 |
|---|---|
| live URL | https://yoonspower.github.io/medistack/ (HTTP 200) |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (v0.2) |
| relations | **60** (AT-ITZ 이트라코나졸×Al/Mg 제산제 id61 포함) |
| full index | relation_card **1,168** / name_only **16,412** (총 17,580) |
| meta.published / clinical_reviewed | **false / false** · reviewed_by 공란 |
| 검수 대기(드라이런 준비 완료) | AT-FEX 1건(60→61) · 칼륨 PM-ready 4건 DF01·DF04·DF05·DF-PRED-01(60→64) |
| schedule | **비활성**(harvest.yml cron 주석) |

---

## 1. 일상/주간 운영 흐름 (한눈에)

```
[주기적]  harvester 수동 run (offline 또는 online)         → §2
            └→ PM review queue 확인 (draft_eligible 라우팅)  → §3
                  └→ (신규 후보면) clinical reviewer 패키지로 핸드오프 → §4
[승격 시]  reviewer note 확보 → dry-run 검증 → live 통합 승인 → §4·§5·§6
            └→ deploy 확인 → live 200 → git clean             → §7
[문제 시]  rollback 원칙                                       → §8
```

- **일상(수시)**: harvester run + 큐 확인. live 변경 0. 이건 "후보를 모아두는" 작업이다.
- **주간/비정기**: PM 라운드 — reviewer note 가 확보된 후보만 통합. live 변경 발생(per-row·제한적).
- **현재 schedule 비활성** → 모든 harvester run 은 **수동**(§9). 자동화는 PM 결정 후 PR 로만(§10).

---

## 2. manual harvester run (live 무수정)

`MediStack_harvester_ops_v1_3.md` §2 정본. 요약:

```bash
# (선택) SDK dry-run 자가검증 — 네트워크 0
python3 medistack_sdk/test_nedrug_client_dryrun.py
# (A) offline dry-run(fixtures, network=0) — 결정적 베이스라인
python3 scripts/guard_no_live_write_v1_3.py --run-bot \
  --bot-args "--ingredients 세파클러,프레드니솔론,아세타졸아미드,펙소페나딘"
# (B) online 실 nedrug fetch — 산출물 커밋 제외(재현가능). argparse 주의: --bot-args=--online (= 형식)
python3 scripts/guard_no_live_write_v1_3.py --run-bot --bot-args=--online
# (C) 큐 검증
python3 scripts/validate_harvest_queue_v1_3.py
# (D) live data 무수정 재검증
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
python3 scripts/validate_full_drug_name_index.py data/full_drug_name_index_sample_v1_0.json
```

- guard wrapper 가 보호셋 sha256 불변·write-scope=`data/harvest_queue/` 한정·direct-http 신규 0 을 강제한다.
- **runtime `data/harvest_queue/` 커밋 금지**(§9). online 산출물은 재현가능 → `git checkout -- data/harvest_queue/` 로 복원. `_sdk/` 는 `.gitignore`.

**theme map expansion 편입(선택 · candidate-only · 2026-06-16 프롬프트 9)** — 정본 `MediStack_harvester_ops_v1_3.md` §14:

```bash
# 신규 theme map 6건을 candidate-only 로 PM 큐에 편입(기본 비활성 flag)
python3 scripts/guard_no_live_write_v1_3.py --run-bot \
  --bot-args "--ingredients 세파클러,프레드니솔론,아세타졸아미드,펙소페나딘 --include-theme-map-expansion"
python3 scripts/validate_harvester_theme_map_v1_3.py   # 17 검사군 + 결함주입 9
python3 scripts/smoke_harvester_theme_map_v1_3.py        # PM queue + 6 카드
```

- flag 없으면 기존 run 무변경. seed = `data/config/theme_map_seeds_v1_3.json`(읽기 전용). runtime `data/harvest_queue/theme_map_*` 는 `.gitignore`(커밋 0) — 요약만 `data/review/theme_map_harvest_incorporation_v1_3.json`. **live 통합·schedule 활성화·자동 integrate 0**, 승격은 clinical reviewer note 후 별도 PR.

---

## 3. PM review queue 확인

- 사람-대면 큐: `data/harvest_queue/pm_review_queue.md`(+ `draft_candidates.json` · `needs_review.csv` · `source_check_results.csv`).
- **draft_eligible 후보만** 다음 단계로. 봇은 라우팅만 하고 **판정/승격하지 않는다**.
- 후보가 **기존 트리아지와 동일**인지 itemSeq 로 대조(`MediStack_candidate_backlog_v1_3.md`). 신규 draft-ready 가 0 이면 새 batch 를 만들지 않는다(없는 후보 지어내지 않음).
- 신규 후보면 → §4(clinical reviewer 패키지로 핸드오프). 미유통/literature-only/방향성 동거어 부재면 reject(재후보화는 국내 시판 시에만).

---

## 4. reviewer note 확보 (승격의 필요조건)

1. 후보를 **reviewer 패키지**로 핸드오프: 칼륨 → `MediStack_reviewer_package_potassium_v1_3.md`, AT-FEX → `MediStack_reviewer_package_antacid_fex_v1_3.md`.
2. 검수자(약사/의사)가 §5 note 템플릿을 채워 반환. **승인 토큰 + 대상 식별자 전건 + 빈칸 채움**이 필수(아래 인터록).
3. reviewer-note 인터록(`check_reviewer_note`, 미충족 시 STOP):
   - **칼륨**: 승인 토큰(`approved`|`승인`) + draft_id **4건 전건**(DF01·DF04·DF05·DF-PRED-01) + SAMPLE/placeholder 없음.
   - **AT-FEX**: 승인 토큰 + candidate_id(AT-FEX-01/AT-01) + primary itemSeq **202202380** + evidence **moderate** + SAMPLE/placeholder 없음.
   - 공통: 빈/garbage/일부 누락/SAMPLE 토큰/미기입 placeholder 거부. 템플릿 그대로 제출 시 거부.
4. **reviewer note 가 와도 자동 승격하지 않는다**(핸드오프 §4): `clinical_reviewed=true`·`published=true` 즉시 전환 금지. per-row·제한적 승격만.

---

## 5. dry-run 검증 (통합 전 재현)

```bash
# AT-FEX
python3 scripts/integrate_antacid_fex_v1_2.py            # dry-run 60→61, live 무수정
python3 scripts/validate_antacid_fex_dryrun_v1_2.py
# 칼륨 4건
python3 scripts/integrate_potassium_pm_ready_v1_2.py     # dry-run 60→64, live 무수정
python3 scripts/validate_potassium_dryrun_v1_2.py
python3 scripts/validate_potassium_pm_ready_v1_2.py
# 게이트 회귀(공통)
python3 scripts/test_reviewer_note_gate_v1_3.py          # invalid 거부 + valid temp-copy 통과 + live sha 불변
```

- dry-run 은 `data/review/*_dryrun_v1_2.json` 에 예상 결과만 기록(live export sha **62df9284…** 불변).

---

## 6. live integration 승인 기준 (per-row·제한적)

다음을 **전건** 충족할 때만 `--pm-approved --reviewer-note <노트>` 로 통합:

- [ ] reviewer note 확보(§4 인터록 통과 — 승인 토큰 + 대상 전건 + SAMPLE/placeholder 없음).
- [ ] 해당 후보 dry-run·검증기 PASS(§5).
- [ ] 칼륨: whitelist {DF01,DF04,DF05,DF-PRED-01} 만(DF02/CQF03/DF03/DF06/DF07 동반 금지). CQF03 correctness 는 별도 선결.
- [ ] AT-FEX: AT-01(avoid_concomitant) 만. evidence_level 임의 상향 금지.
- [ ] 통합 후 relation-count 하드코딩 validator 갱신(칼륨 +4=>64 / AT-FEX 60→61, 통합 순서에 따라 baseline 조정).
- [ ] published/clinical_reviewed=false 유지 · reviewed_by 는 reviewer 만 · 제품/구매/제휴 0 · 칼륨 product_link=false.

> 승격은 항상 **사람 PM + source 재확인 + clinical reviewer 노트 + 수동 명령**. 자동 승격 경로 없음.

---

## 7. deploy 확인

- 통합 커밋을 main 에 push → `.github/workflows/deploy.yml`(validate→deploy 게이트, Pages Source=GitHub Actions)이 자동 배포.
- 확인: deploy run 성공 · `curl -s -o /dev/null -w "%{http_code}" https://yoonspower.github.io/medistack/` → **200** · `git status` clean.
- 통합 PR/커밋 전 전수 validator/smoke PASS 필수(§아래 §11 검증 목록).

---

## 8. rollback 원칙

- **live export 는 append-only**(기존 relation 의미 불변). 잘못된 통합은 **해당 relation 제거 + meta.relation_count 복원 + relation-count validator 되돌림**을 한 커밋으로(revert).
- export 직접 손편집 금지 — 통합은 `integrate_*.py`, 되돌림은 git revert 또는 동일 스크립트의 역연산/재생성으로.
- rollback 후에도 전수 validator PASS + deploy + live 200 확인. full index/aliases 는 통합과 무관(무변경)하므로 rollback 대상 아님.
- 의심 시 **승격 보류가 기본값**(verified_reference 천장은 안전한 정지 상태 — 검수자 부재 ≠ 결함).

---

## 9. schedule 비활성 상태의 수동 운영 (현재)

- schedule 은 **비활성**(harvest.yml cron 주석). 모든 harvester run 은 수동 `workflow_dispatch`(GitHub Actions UI) 또는 로컬(§2).
- CI harvest.yml 기본 = **artifact 업로드**(main 무오염). `commit=true` 옵트인 시에만 전용 브랜치 + PR(직접 main push 금지).
- **runtime `data/harvest_queue/` 커밋 금지**: online 산출물은 재현가능. 커밋되는 건 결정적 offline 베이스라인뿐. 분석 요약만 `data/review/` 에 보존.
- harvester 는 영구히 **후보 수집·라우팅** 권한만 — live·배포·승격 권한 없음.

---

## 10. schedule 활성화 전 체크리스트 (켜지 않음 · 게이트만)

활성화는 **별도 PM 결정 + PR** 로만. 켜기 전 `MediStack_harvester_ops_v1_3.md` §12 게이트(9항목)를 전건 통과해야 한다:
트리거 안정성 · output=artifact only · commit 기본 false · live write 0 · no-live-write guard · runtime queue 커밋 금지 · PM queue만 · **자동 integrate 금지** · 실패 시 알림/보고만.

- 최소 diff·PR 체크리스트·구조 검증: `MediStack_harvester_schedule_activation_v1_3.md`.
- 구조 검증: `python3 scripts/validate_harvester_schedule_safety_v1_3.py`(현 main 9규칙 PASS + 결함주입 탐지). 활성화 PR 에선 R1 외 R2~R9 PASS 가 안전의 핵심.
- 켜더라도 harvester 는 live·승격 권한을 얻지 않는다(§9 불변).

---

## 11. 운영 검증 목록 (통합/배포 전 전수 PASS)

```bash
python3 medistack_sdk/test_nedrug_client_dryrun.py
python3 scripts/test_search_depth_v1_3.py
python3 scripts/test_reviewer_note_gate_v1_3.py
python3 scripts/validate_harvester_schedule_safety_v1_3.py
python3 scripts/validate_potassium_dryrun_v1_2.py
python3 scripts/validate_prednisolone_draft_recheck_v1_3.py
python3 scripts/validate_antacid_fex_dryrun_v1_2.py
python3 scripts/validate_antacid_interaction_v1_2.py
python3 scripts/validate_harvest_queue_v1_3.py
python3 scripts/guard_no_live_write_v1_3.py            # 보호셋 sha256 불변·direct-http 0
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
python3 scripts/validate_full_drug_name_index.py data/full_drug_name_index_sample_v1_0.json
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json
python3 scripts/validate_potassium_name_only_policy.py
python3 scripts/validate_forbidden_phrases_v1_2.py
# + smoke 9종(smoke_*.py) · node v0.1/v0.2 validator(.js)
```

---

## 12. 외부 알림 설정법 (작업 완료 보고용 — 선택)

> 알림은 **선택**이다. 설정값이 없거나 실패해도 **작업 실패로 처리하지 않는다.** **맥(macOS) 알림은 사용하지 않는다.**

운영 도구가 작업 완료 메시지를 보낼 때 아래 환경변수를 본다(우선순위: Telegram → 실패 시 iMessage):

| 채널 | 환경변수 | 조건 |
|---|---|---|
| **Telegram(우선)** | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | **둘 다** 있을 때만 시도. 하나라도 없으면 시도 안 함 |
| **iMessage(폴백)** | `MEDISTACK_NOTIFY_IMESSAGE_TO` | 있을 때만, **그 지정 수신자에게만**. 임의 연락처 금지 |

설정 예(셸):

```bash
# Telegram (BotFather 토큰 + 대상 chat id)
export TELEGRAM_BOT_TOKEN="123456:ABC-..."
export TELEGRAM_CHAT_ID="987654321"
# iMessage 폴백 (지정 수신자 1)
export MEDISTACK_NOTIFY_IMESSAGE_TO="yoonspower@gmail.com"
```

동작 규칙:
- Telegram·iMessage **둘 다 설정**이면 Telegram 우선, 실패하면 iMessage 시도.
- **둘 다 미설정 또는 실패**면 "외부 알림 미전송(설정 없음 또는 실패)" 로 **보고에만 남긴다**.
- 알림 실패가 안전 위반이나 작업 실패로 번지지 않게 fail-soft.

---

## 12.5 theme map live 통합 (reviewer-gated · 준비 완료 · 미실행)

theme map 6건의 live 통합은 **reviewer note + 선행조건 후 별도 PR**(자동·이번 라운드 실행 0).
1. reviewer 가 `docs/MediStack_reviewer_package_theme_map_v1_3.md` §3 검토 → §8 템플릿으로 note 작성(category·grouping·zinc mechanism 결정 포함).
2. **선행조건(별도 PR)**: v0.2 validator #15 를 acid_reducing_drug 포함 확장 + src(getFacets·acid_reducing_drug chip). dry-run = `data/review/theme_map_live_dryrun_v1_3.json`.
3. `python3 scripts/integrate_theme_map_draft_batch_v1_3.py --pm-approved --reviewer-note <노트>`(60→66·멱등) → 통합 후 검증 전수 + live HTTP 200. 게이트 회귀 = `scripts/test_theme_map_reviewer_note_gate_v1_3.py`. 실행 프롬프트 = next_prompts 프롬프트 11.

> **🟢 페니실라민 FE/ZN subset 우선 경로(2026-06-16·선행조건 0)**: theme map 6건 중 FE/ZN 2건은 일반 영양소(counterpart_category=null)라 **validator/src 선행조건 없이** 먼저 통합 가능(60→62). reviewer 가 `docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md` §6 템플릿으로 note 작성(FE/ZN+ZN mechanism+개별카드) → `python3 scripts/integrate_penicillamine_subset_v1_3.py --pm-approved --reviewer-note <노트>`(멱등). 게이트 회귀 = `scripts/test_penicillamine_reviewer_note_gate_v1_3.py`. 실행 프롬프트 = next_prompts 프롬프트 15. ⚠️ full-6 통합기와 **동시 실행 금지**(같은 후보 중복).

## 12.6 Relation Factory Bot v1.4 (대량 후보 공장 · manual tool · live 0)

> 1,000 relation scale-up 용 별도 manual tool. harvester/schedule 와 **비연동**(향후 PR 검토). 기본 실행 = live/export/src write 0.

```bash
python3 scripts/build_relation_factory_inventory_v1_4.py            # 중복 차단 인벤토리(읽기전용)
python3 scripts/relation_factory_bot_v1_4.py                        # universe+후보+precheck+queue (offline·data/review)
python3 scripts/relation_factory_bot_v1_4.py --online-source-check --max-source-check 200   # SDK source-check+draft+PM
python3 scripts/validate_relation_factory_batch_v1_4.py             # 결함주입 10
python3 scripts/smoke_relation_factory_batch_v1_4.py
```
- 산출물 `data/review/relation_factory_*`·`data/drafts/relation_factory_draft_batch_v1_4.json`. SDK 캐시 `data/harvest_queue/_sdk/`(gitignore).
- draft → adversarial → reviewer note → dry-run integrator → 별도 PR 후에만 live. 정본 `docs/MediStack_relation_scaleup_roadmap_v1_4.md`.

## 13. 금지 (운영 불변)

live relation 실제 추가(승인 경로 외) / export·full index·aliases·DATA_URL 직접 손편집 / schedule 활성화(이 라운드) /
.github workflow 수정(이 라운드) / clinical_reviewed=true · published=true · reviewed_by 임의 작성 / 제품·구매·제휴 UI /
칼륨 보충 권유·결핍 단정 / Mg 영양제 relation 오인 / K-sparing 을 depletion 카드로 / reviewer note 없이 통합 /
runtime harvest_queue 커밋 / 자동 integrate / "식약처 승인·법적 문제 없음·약사 검수 완료" 표현 / 맥 알림 사용.
