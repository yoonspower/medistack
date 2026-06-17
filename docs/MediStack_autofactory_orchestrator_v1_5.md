# MediStack AutoFactory Orchestrator v1.5

> **NO-LIVE-WRITE 자동화.** 이 도구는 reviewer-ready 후보를 **무비용·무위험으로 준비**하는 단계까지만 한다.
> live/protected data 무수정 · actual integration 0 · reviewer note 없는 통합 0 · 미검증 source 승격 0.

## 무엇인가
`scripts/run_medistack_autofactory_orchestrator_v1_5.py` 는 MediStack 후보 파이프라인(생성→점검→분류→패키징→리포트)을
한 번에 결정적으로 돌리는 오케스트레이터다. 출력은 `data/review/autofactory_v1_5_*.json` (planning area) 11개.

## 정직한 funnel (핵심 설계)
- raw 후보는 family universe(`relation_family_universe_v1_4.json`)에서 **결정적 enumerate**, `source_pointer=null`.
  **허위 인용을 절대 생성하지 않는다.** 실제 라벨 인용은 별도 network harvest 단계에서만 채워진다.
- 따라서 오프라인 실행에서는 **신규 source 확정 0 → 신규 reviewer-ready 0** 이 정상이며, 이것이 가드가 작동하는 증거다.
- 이미 실인용으로 source-confirmed 된 집합(global plan 의 integrable 33 + needs_review 4)은 auto-reviewer 가
  **점수화하되 분류는 family adversarial 권위 판정에 위임**한다(33 auto_pass · 4 needs_review).
- 33 은 `existing_prepared` 로만 표시(신규 카운트 중복 금지). combined future = 60→93 + new_ready(0).

## 9 stage
| Stage | 내용 | 산출 |
|---|---|---|
| 0 Preflight | git/protected snapshot · live count · DATA_URL · published/clinical/schedule/product UI snapshot | (메모리) |
| 1 Candidate Harvest | family universe enumerate · normalize · live exact dup 표시 · source_pointer=null | `raw_candidates` |
| 2 Source Check Queue | source pointer 요구 · live dup/hold family/reject 사전 분기 | `source_check_queue` |
| 3 Auto Source Reviewer | source-confirmed 집합 점수화(7지표·overall 0~100) | `auto_reviewed` |
| 4 Adversarial Refutation | refute-by-default 권위 분류 위임 | `adversarial_results` |
| 5 Family Clustering | high/medium/small wave 추천 | `family_clusters` |
| 6 Auto Packager | auto_pass+copy_change → reviewer-ready (전부 existing_prepared → 신규 0) | `reviewer_ready_waves` |
| 7 Dry-run/Rehearsal | no-write rehearsal(antibiotic23 83·chronic8 68·all33 93) | `dryrun_summary` |
| 8 Validation | protected 불변·forbidden·unsourced·needs_review leak 가드 | (dashboard.guards) |
| 9 Report | dashboard·달성률·병목·Factory v1.6 추천 | `dashboard`, `run_config` |

## 실행
```
python3 scripts/run_medistack_autofactory_orchestrator_v1_5.py \
  --target-raw 1200 --target-source-check 600 --target-source-confirmed 200 \
  --target-reviewer-ready 100 --max-needs-review 120 --no-live-write --dry-run
```
기본값: `--no-live-write`, `--dry-run`, `--strict-source-fidelity`, `--fail-on-protected-change` 전부 true.
`--allow-live-write` 는 **지원하지 않으며 exit 1 로 거부**된다.

### 옵션
`--target-raw/-source-check/-source-confirmed/-reviewer-ready` · `--max-needs-review` ·
`--families F1,F2` · `--exclude-families` · `--no-live-write` · `--dry-run` · `--resume` ·
`--batch-size` · `--max-runtime-minutes` · `--report-only` · `--seed` ·
`--strict-source-fidelity` · `--fail-on-protected-change`.

## 현재 run 결과(seed 1, 기본 target)
- raw **301** → source-check queue **196** (prefiltered: live_dup 35 · hold 67 · reject 3)
- source-confirmed(existing) **33** (auto_pass 33) + genuine needs_review **4**
- source_pending → needs_review **120** (cap; overflow 76 — 실제 harvest 시 재평가 대상)
- **신규 reviewer-ready 0** · existing_prepared **33** · combined future **60→93** (변동 없음)
- 병목: **실제 source harvest(network)** + 33 의 reviewer note 실물 확보.

## 검증
`validate_autofactory_orchestrator_v1_5.py` · `smoke_autofactory_orchestrator_v1_5.py` ·
`test_autofactory_orchestrator_guards_v1_5.py` — 전수 PASS.

자세한 운영/가드/대시보드/멀티에이전트 모델은 동급 `MediStack_autofactory_v1_5_*` 문서 참조.
