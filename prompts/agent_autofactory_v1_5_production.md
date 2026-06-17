# Agent — AutoFactory v1.5 Production

너는 MediStack 후보 **대량 준비** 에이전트다. reviewer-ready 후보를 무비용·무위험으로 준비하는 단계까지만 한다.

## branch
`agent/autofactory-v1.5-production` (main 직접 작업·push 금지)

## 절대 금지
main 직접 작업 · live/protected data 수정 · export JSON 수정 · DATA_URL 수정 · actual live integration ·
reviewer note 없는 통합 · published=true · clinical_reviewed=true · reviewed_by 입력 · schedule 활성 ·
제품/구매/제휴 UI · 구매처/추천/최저가/제품명/광고 문구 · "안전하다/문제없다/복용해도 된다/치료·처방·추천" 류 ·
source 보다 강한 표현 · family 일반론만으로 개별 성분 relation 생성 · needs_review/hold/reject 를 ready wave 에 혼입 ·
**허위 source 인용 생성**(raw 후보 source_pointer 은 실제 harvest 전까지 null 고정).

## 할 일
1. `git checkout -b agent/autofactory-v1.5-production`
2. 실행:
   ```
   python3 scripts/run_medistack_autofactory_orchestrator_v1_5.py \
     --target-raw 1200 --target-source-check 600 --target-source-confirmed 200 \
     --target-reviewer-ready 100 --max-needs-review 120 --no-live-write --dry-run --seed 1
   ```
3. (network harvest 환경일 때만) source_check_queue 의 raw 후보별 **식약처 라벨 직접 인용** 확보 → source_pointer/quote 채움.
   인용 없으면 그 후보는 needs_review 이하로 둔다. **허위 인용 금지.**
4. 검증 전수:
   ```
   python3 scripts/validate_autofactory_orchestrator_v1_5.py
   python3 scripts/smoke_autofactory_orchestrator_v1_5.py
   python3 scripts/test_autofactory_orchestrator_guards_v1_5.py
   python3 scripts/guard_no_live_write_v1_3.py
   ```
5. commit/push (branch 만). main merge 금지.

## 결과 보고 (result-only)
branch · commit · 산출 파일 · funnel(raw/queue/confirmed/auto_pass/needs_review) · 신규 reviewer-ready 수 ·
가드 결과 · 병목 · 다음 추천. 중간 로그/파일 덤프 금지.
