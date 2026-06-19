#!/usr/bin/env bash
# MediStack AutoFactory v1.7 ONLINE harvest — Mac Mini(한국 IP) 실행 래퍼.
# autoharvest.yml(GitHub Actions)의 step 들을 1:1 이식. GitHub-hosted 러너(Azure IP)는
# nedrug 네트워크단 차단(connection timeout)으로 online raw 0 → 한국 IP(이 Mac Mini)로 실행 위치만 이전.
#
# 안전 하드락(autoharvest.yml 과 동일):
#  - harvest 고정 플래그: --no-live-write --dry-run --strict-source-fidelity --fail-on-protected-change --cap-raw 300
#  - 보호셋 8종 수정 0 (git-status 로 강제 검사·위반 시 abort)
#  - main 직접 push/commit 0 — 산출은 전용 브랜치 agent/autofactory-auto-<ts> push 만, 자동 머지 0
#  - live-write 0, published/clinical=false 등 orchestrator 가드 유지
set -euo pipefail
cd "$(dirname "$0")/.."                         # repo 루트
export GIT_TERMINAL_PROMPT=0                     # cron 에서 인증 프롬프트로 hang 방지
mkdir -p logs
LOG="logs/harvest_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
echo "== harvest run $(date -u +%FT%TZ) =="

# ── 최신 main 기준(steady-state: repo 는 main 에 있고 wrapper 는 main 에 존재) ──
git fetch origin --quiet
git checkout main
git pull --ff-only origin main
# 작업트리 더러움 검사(추적 파일 변경만 — 미추적 logs/cache 는 무시)
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "STOP: 작업트리 더러움(추적 파일 변경 존재)"; git status --porcelain --untracked-files=no; exit 1
fi

# ── 사전 게이트(네트워크 0) ──
python3 medistack_sdk/test_nedrug_client_dryrun.py
python3 scripts/test_nedrug_online_client_v1_7.py
python3 scripts/test_extract_gold_v1_7.py                       # GOLD 3/3
python3 scripts/test_autofactory_orchestrator_guards_v1_7.py    # B1~B8
python3 scripts/validate_autofactory_orchestrator_v1_7.py
python3 scripts/smoke_autofactory_orchestrator_v1_7.py
python3 scripts/guard_no_live_write_v1_3.py                     # 보호셋 sha 스냅샷(before)

# ── ONLINE harvest (한국 IP) ──
python3 scripts/run_medistack_autofactory_orchestrator_v1_7.py \
  --online --cap-raw 300 --no-live-write --dry-run \
  --strict-source-fidelity --fail-on-protected-change

# ── 보호셋 불변 재검증(git) ──
PROT="data/medistack_v0.1_beta_export.json data/medistack_v0.2_beta_export.json data/medistack_v0.3_aliases.json data/full_drug_name_index_sample_v1_0.json src/js/app.js src/js/data.js index.html src/css/styles.css"
CHANGED="$(git status --porcelain -- $PROT || true)"
if [ -n "$CHANGED" ]; then echo "STOP: 보호셋 수정 감지 — live-write 위반"; echo "$CHANGED"; exit 1; fi
echo "보호셋 무수정 OK"
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
python3 scripts/validate_full_drug_name_index.py data/full_drug_name_index_sample_v1_0.json

# ── 산출: 전용 브랜치 push (write-scope 한정 · main push 0 · 자동 머지 0) ──
git add data/review/autofactory_v1_7_*.json
OUT="$(git diff --cached --name-only | grep -v '^data/review/autofactory_v1_7_' || true)"
if [ -n "$OUT" ]; then echo "STOP: data/review/ 밖 staged 변경"; echo "$OUT"; exit 1; fi
if git diff --cached --quiet; then
  echo "변경 없음 — 커밋·push 생략(raw 0 또는 신규 0)"; echo "== done $(date -u +%FT%TZ) =="; exit 0
fi
BR="agent/autofactory-auto-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BR"
git -c user.name=medistack-autofactory-bot -c user.email=bot@local commit -q -m "chore(autofactory): v1.7 dryrun package refresh [mac-cron]

AutoFactory v1.7 online harvest(한국 IP·dry-run·no-live-write). live relation/배포 0.
PM source-fidelity 적대검증 후 별도 live-PR 선별."
git push origin "$BR"
echo "PUSHED: $BR"
echo "== done $(date -u +%FT%TZ) =="
