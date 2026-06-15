# MediStack — harvester schedule 활성화 PR-ready 설계 (v1.3, 2026-06-15)

작성일: 2026-06-15 · 상태: **PR-ready 설계만 / schedule 비활성 유지 · 실행 0** · 자기완결

> 이 문서는 harvester `schedule`(cron) 자동화를 **나중에** 켤 때 필요한 **최소 diff·PR 체크리스트·구조적 안전 보증**을 정리한다.
> **이 라운드에서 schedule 을 켜지 않는다.** `.github/workflows/harvest.yml` 의 `schedule:`/`cron:` 은 주석 유지(현 main 그대로).
> `.github/workflows/*` 는 no-live-write 보호셋이라 **이 라운드에서 수정하지 않는다.** 활성화는 별도 PM 결정 + PR 로만.
>
> 선행/근거: ops §4(자동화 상태)·§7(운영 원칙)·§12(켜기 전 체크리스트) · `scripts/validate_harvester_schedule_safety_v1_3.py`(구조 검증) ·
> 운영 절차 → `docs/MediStack_operator_runbook_v1_3.md` · 다음 라운드 프롬프트 → `docs/MediStack_next_prompts_2026_06_15.md` 프롬프트 6.

---

## 0. 한 줄 요약

활성화 = `harvest.yml` 의 **두 줄 주석 해제**가 전부다(아래 §1). 그러나 그 두 줄을 켜기 전에 ops §12 게이트(9항목)를 통과해야 하고,
켠 뒤에도 harvester 는 **후보 수집·라우팅** 권한만 갖는다 — live write·auto-integrate 권한은 **구조적으로 없다**(§3).

---

## 1. 최소 diff (patch preview — 적용 금지, 미리보기만)

현재(비활성):

```yaml
  # 안정화 후 주석 해제(초기 비활성). KST 월 03:00 = UTC 일 18:00.
  # schedule:
  #   - cron: "0 18 * * 0"
```

활성화 시(PR 에서만 적용):

```diff
-  # 안정화 후 주석 해제(초기 비활성). KST 월 03:00 = UTC 일 18:00.
-  # schedule:
-  #   - cron: "0 18 * * 0"
+  # KST 월 03:00 = UTC 일 18:00. 자동 run 도 commit 기본 false · output=artifact only · auto-integrate 0.
+  schedule:
+    - cron: "0 18 * * 0"
```

- **이게 활성화 diff 의 전부다.** `on:` 의 `workflow_dispatch:`, `inputs`(mode/commit), job steps, permissions, no-live-write 가드 호출은 **일절 변경하지 않는다.**
- cron 값 `0 18 * * 0` = 매주 일요일 UTC 18:00 = **KST 월요일 03:00**(주 1회). 초안이며 PM 이 빈도를 조정할 수 있으나, **commit 기본 false·artifact-only·auto-integrate 0** 은 빈도와 무관하게 불변.
- schedule 트리거는 `inputs` 를 받지 않으므로 기본값(mode=offline, commit=false)이 적용된다 → **자동 run 은 기본적으로 offline·artifact-only**. online·commit 은 여전히 수동 `workflow_dispatch` 에서 명시 옵트인해야 한다.

> ⚠️ schedule run 은 입력 기본값을 쓴다. 현재 `commit` 기본값은 `false`(artifact only). 활성화 PR 에서 이 기본값을 **절대 true 로 바꾸지 않는다**(§3 R3). 자동 커밋이 필요해 보이면 그것은 활성화가 아니라 **별도 정책 변경**이며 다시 검토 대상이다.

---

## 2. PR-ready 체크리스트

활성화 PR 은 아래를 **본문에 첨부**하고, 전건 충족 시에만 머지한다. (ops §12 게이트와 1:1 대응 + PR 절차.)

- [ ] **ops §12 게이트 9항목 전건 통과**(트리거 안정성·artifact only·commit false·live write 0·no-live-write guard·runtime queue 커밋 금지·PM queue만·자동 integrate 금지·실패 시 알림/보고만).
- [ ] **`workflow_dispatch` 정상**: 활성화 후에도 수동 트리거(offline/online·commit 입력)가 그대로 동작.
- [ ] **schedule cron 은 PR 에서만 추가**: main 직접 push 금지. 리뷰·승인 후 머지.
- [ ] **commit 기본 false**: 자동 run 은 artifact-only 가 기본. 자동 커밋·자동 PR 머지 0.
- [ ] **artifact only 기본**: 산출물은 `actions/upload-artifact`(PM review queue) + `data/review/` 요약뿐. live export/full index/aliases/src/.github 무수정.
- [ ] **live write 0**: 자동 run 이 live relation 0건 생성. published/clinical_reviewed/reviewed_by 무변경. 모든 후보 `do_not_implement_yet`.
- [ ] **no-live-write guard 필수**: 자동 run 도 `guard_no_live_write_v1_3.py --run-bot` 경로 → 보호셋 sha256 불변·write-scope·direct-http 0.
- [ ] **runtime queue 커밋 금지**: online 산출물은 재현가능 → 커밋 제외(`_sdk/` 는 `.gitignore`). 자동화가 이를 커밋하지 않음.
- [ ] **PM review queue만 생성**: 사람-대면 출력은 `pm_review_queue.md`(draft_eligible 라우팅)뿐. 직접 승격 경로 없음.
- [ ] **자동 integrate 금지**: schedule 을 켜도 `integrate_*.py`/live 통합은 절대 자동 실행 안 함. 승격은 항상 사람 PM + clinical reviewer 노트 + `--pm-approved --reviewer-note` 수동.
- [ ] **실패 시 보고/알림만**: 자동 run 실패는 알림/로그/요약으로만(자동 재시도로 live 쓰기 시도 금지). fail-soft.
- [ ] **구조 검증 PASS**: PR 브랜치에서 `python3 scripts/validate_harvester_schedule_safety_v1_3.py` 가, cron 활성화 후에도 **R1 외 8규칙(R2~R9) PASS** 인지 확인(R1 schedule_not_active 는 활성화하면 의도적으로 바뀌므로, 활성화 PR 에서는 R1 을 "schedule 은 활성·그러나 commit false·integrate 0" 로 재해석하고 나머지 8규칙으로 안전을 보증).

> R1 해석 주의: 본 검증기의 R1 은 **현재 main = schedule 비활성** 을 지키는 가드다. 활성화 PR 에서는 R1 이 의도적으로 FAIL(=schedule 활성)이 되며, 이때 안전 보증은 **R2~R9 (특히 R3 commit false·R5 write-scope·R6 무쓰기·R7 integrate 미호출·R8 guard·R9 artifact-only)** 가 담당한다. 즉 "schedule 을 켜도 R3·R5·R6·R7·R9 가 여전히 PASS" 가 활성화 안전의 핵심 조건이다.

---

## 3. schedule 을 켜도 live write/auto-integrate 가 불가능한 구조적 근거

활성화 여부와 무관하게 harvester job 은 아래 때문에 live 를 쓸 수 없다. `validate_harvester_schedule_safety_v1_3.py` 가 규칙별로 강제한다.

| 구조 | 무엇을 막나 | 검증 규칙 |
|---|---|---|
| 봇 write-scope = `data/harvest_queue/` 한정 | 봇이 export/full index/alias/src 를 못 씀(보호셋 sha256 불변) | R5·R6·R8 |
| no-live-write guard wrapper(`--run-bot`) | 봇 실행 전후 보호셋 불변·write-scope·direct-http 강제 | R8 |
| `integrate_*.py` 미호출 | live 승격 스크립트가 CI 경로에 없음 | R7 |
| commit 기본 false + artifact 업로드 | 자동 run 산출물은 artifact·큐뿐(main 무오염) | R3·R9 |
| commit=true 시에도 전용 브랜치 + PR | main 직접 push 0(out-of-scope staged 차단 가드) | R4·R5 |
| deploy/Pages publish 스텝 부재 | harvester job 이 배포를 트리거하지 못함 | R9 |

> 결론: **schedule 은 "큐를 더 자주 갱신"할 뿐, live·배포·승격 권한을 얻지 않는다.** 승격은 영구히 사람 PM + clinical reviewer 노트 + 수동 `--pm-approved --reviewer-note` 경로뿐(ops §7·§12, 핸드오프 §4).

---

## 4. 범위 / 금지 (본 문서)

- ✅ 문서 + `data/review/harvester_schedule_activation_patch_preview_v1_3.json`(기계판독 미리보기) + 검증 스크립트(`scripts/validate_harvester_schedule_safety_v1_3.py`)만.
- 🚫 `.github/workflows/harvest.yml` 실제 수정 0(보호셋) · schedule/cron 활성화 0 · live write 0 · auto-integrate 0 · main 직접 push 0.
- 🚫 published/clinical_reviewed=true · reviewed_by 작성 · 제품/구매/제휴 UI · DATA_URL 변경 0.
