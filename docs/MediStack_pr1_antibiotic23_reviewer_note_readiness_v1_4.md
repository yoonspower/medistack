# MediStack v1.4 — PR-1 antibiotic23 reviewer note readiness

> NO-LIVE-WRITE — reviewer note 실물 **미확보**. 본 문서는 PR-1(antibiotic23, 60→83) 통합 직전 reviewer note 양식·gate 준비. live/protected 무수정.

## scope
- wave: **antibiotic23** = F1 18 + F2 5 = **23건** · delta **+23** · expected relation_count **60 → 83**
- needs_review 제외: `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`
- internal duplicate: False · live exact duplicate: 0

### F1 (18 · 퀴놀론 × 미네랄/제산제)
`RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029`, `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030`

### F2 (5 · 테트라사이클린 × 금속/제산제)
`RF-F2-0105`, `RF-F2-0110`, `RF-F2-0111`, `RF-F2-0114`, `RF-F2-0115`

## reviewer note
- **DRAFT 생성**: `data/review/pr1_antibiotic23_reviewer_note_DRAFT_v1_4.md` (검토자 fill-in 양식)
- **actual reviewer note 확보: NO** (사람 검토자 미확보 → 통합 차단 전제 유지)
- DRAFT 는 checker 에 의해 **거부**됨(placeholder 날짜 / commit 미충족 / 식별 토큰 미충족) → 채우기 전 통합 불가 보장
- **VALID fixture**(형식 유효 예시·실제 승인 아님): `pr1_antibiotic23_reviewer_note_VALID_fixture_v1_4.txt` → checker 통과
- invalid fixture: candidate 누락 / needs_review 혼입 / delta 불일치 / 금지요구(제품·구매·clinical=true) 전건 거부

## 검토자 절차
1. DRAFT 의 `RPH-<검수자ID>` · `YYYY-MM-DD` · `<commit-hash>` 를 실제 값으로 채운다.
2. `python3 scripts/check_live_pr_reviewer_note_v1_4.py --wave antibiotic23 --reviewer-note <채운파일>` → PASS 확인.
3. PASS 시에만 per-family integrator(F1+F2)로 live PR 실행(actual: 60→83). 그 전까지 실행 금지.

## rehearsal (no-write)
- `python3 scripts/rehearse_live_pr_waves_no_write_v1_4.py --wave antibiotic23 --base-count 60 --dry-run` → PASS · n=23 +23 → 83 · duplicate 0 · needs_review 0 · index flip 0 · live write 0

## baseline / rollback / post-merge
- baseline: 60 → 83 (expected = 직전 count + delta · 신규 id = runtime max+1, 현 max 61)
- rollback: PR-1 단일 commit + `pre-livepr-antibiotic23` 태그 → 트리거 시 `git revert`
- post-merge: `validate_live_pr_readiness_v1_4.py --post-merge --wave antibiotic23` (count 83·published/clinical/reviewed_by·제품UI) + F1/F2 smoke + v0.2 export validator
