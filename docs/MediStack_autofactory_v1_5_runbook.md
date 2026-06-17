# MediStack AutoFactory v1.5 — Runbook

> 실행 절차서. 모든 단계 NO-LIVE-WRITE. live PR(실제 통합)은 이 도구 범위 밖이며 reviewer note + per-family integrator 로만.

## 0. 전제
- 작업은 **별도 branch** 에서만. main 직접 작업 금지.
- live/protected data(v0.1/v0.2 export·aliases·full index·src·.github) 무수정.

## 1. 기본 실행 (대량 준비)
```
git checkout -b agent/autofactory-v1.5-production
python3 scripts/run_medistack_autofactory_orchestrator_v1_5.py \
  --target-raw 1200 --target-source-check 600 --target-source-confirmed 200 \
  --target-reviewer-ready 100 --max-needs-review 120 --no-live-write --dry-run --seed 1
```
→ `data/review/autofactory_v1_5_*.json` 11개 생성.

## 2. family 한정 / 제외
```
--families F1,F2          # 해당 family 만 harvest
--exclude-families F5,F11 # 고위험 family 제외(이미 HOLD 기본)
```

## 3. 보고만 (재요약)
```
python3 scripts/run_medistack_autofactory_orchestrator_v1_5.py --report-only
```

## 4. 검증 (생성 직후 필수)
```
python3 scripts/validate_autofactory_orchestrator_v1_5.py
python3 scripts/smoke_autofactory_orchestrator_v1_5.py
python3 scripts/test_autofactory_orchestrator_guards_v1_5.py
```
+ 기존 가드: `guard_no_live_write_v1_3.py` · `validate_global_reviewer_ready_dryrun_v1_4.py` ·
`validate_live_pr_readiness_v1_4.py` · `validate_needs_review_quarantine_v1_4.py`.

## 5. 산출물 읽는 순서
1. `autofactory_v1_5_dashboard.json` — funnel·달성률·병목·Factory v1.6 추천.
2. `autofactory_v1_5_reviewer_ready_waves.json` — 신규 ready(현재 0)·existing_prepared 33.
3. `autofactory_v1_5_needs_review_quarantine.json` — genuine 4 + source_pending recheck 후보.
4. `autofactory_v1_5_hold_reject_ledger.json` — hold/reject 분기 근거.

## 6. 신규 source 확정(병목 해소) — 별도 live 단계
오프라인 orchestrator 는 source 를 확정하지 못한다. 신규 reviewer-ready 를 만들려면:
1. network harvest 활성 환경에서 source_check_queue 의 raw 후보별 **식약처 라벨 직접 인용** 확보.
2. 인용을 근거로 per-family adversarial(refute-by-default) 재검 → auto_pass/copy_change/needs_review.
3. auto_pass/copy_change 만 reviewer-ready wave 로 패키징.
4. reviewer note 실물 확보 후에만 per-family integrator 로 live PR.

## 7. 절대 금지 (재확인)
main 직접 작업 · live/protected 수정 · export/DATA_URL 수정 · actual integration · reviewer note 없는 통합 ·
published/clinical_reviewed=true · reviewed_by 입력 · schedule 활성 · 제품/구매/제휴 UI ·
구매처/추천/최저가/제품명/광고 문구 · "안전하다/문제없다/복용해도 된다/치료·처방·추천" 류 사용자 노출 ·
source 보다 강한 표현 · family 일반론만으로 개별 성분 relation 생성 · needs_review/hold/reject 를 ready wave 에 혼입.
