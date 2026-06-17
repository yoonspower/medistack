# MediStack v1.4 — live PR readiness dashboard

> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 · 라이브 relations 60.

## 1. Integration-ready
- **total 33** = F1 18(nutrient10+antacid8) · F2 5 · F3 1 · F9 7 · F4 1 · F6 1
- combined true: **60 → 93** (F1+F2+F3+F9 91 → +F4/F6 93)
- remaining unpackaged 0 · live duplicate 0 · cross-family 0 · needs_review 혼입 0

## 2. PR wave 추천
- 기본 **option B(3 PR)**: PR-1 antibiotic23(→83) · PR-2 chronic8(→+8) · PR-3 F3+F4(→+2)
- per-family note 시 option A(5 PR) · all33 명시 note+gate 시 option C(1 PR, 비추천)

## 3. reviewer note
- checker: `check_live_pr_reviewer_note_v1_4.py --wave <W> --reviewer-note <note>` (10 wave 지원)
- 필수 16항목 · 금지 8요구 · placeholder/SAMPLE/needs_review 혼입/delta 불일치 자동 거부
- **현재 reviewer note 실물 0 → 통합 차단 전제 유지**

## 4. rehearsal
- `rehearse_live_pr_waves_no_write_v1_4.py` 10 wave PASS · duplicate 0 · needs_review exclusion · index flip 0 · **live write 0**

## 5. baseline / rollback / post-merge
- baseline: expected = `직전 count + delta` (하드코드 금지) · 신규 id = runtime max+1 (현재 max 61)
- rollback: wave 단위 단일 commit + 태그, 7 트리거 → git revert
- post-merge: count·ids·published/clinical/reviewed_by·제품UI·schedule·DATA_URL·index·smoke

## 6. needs_review 격리
- `RF-F3-0148` F3 에티드론산 × 칼슘 — source parse 미해소(quote 경계)
- `RF-F3-0149` F3 에티드론산 × 철분 — source parse 미해소
- `RF-F9-0245` F9 카르바마제핀 × 엽산 — 저신호 이상반응 열거('드물게')·기전/level-direction/연용-remedy 부재
- `RF-F10-0275` F10 케토코나졸 × 제산제 — route/availability 강등(경구 품목 위장 불가)
- true scenario / wave / note 템플릿 / actual command 전부 제외 (conditional scenario 에만 표기)

## 7. Factory v1.5
- packaging 충족 · **run_now=false** · live PR 0·reviewer note 0·needs_review 4 병목
- 재검토: live PR wave 1~2건 통합 + needs_review 일부 해소 후

## 8. 검증 (전수 PASS)
- 신규: check_live_pr_reviewer_note(test) · validate_live_pr_readiness(pack+post-merge) · rehearse+validate rehearsal · validate_needs_review_quarantine
- 기존: global validator · F1/F2/F3/F9/F4F6 family gate·smoke · v0.1/v0.2 export · full index · aliases · forbidden phrase · schedule safety · no-live-write guard

## 9. live / protected (불변 확인)
- `medistack_v0.1_beta_export.json` `e9994f0179955913`
- `medistack_v0.2_beta_export.json` `62df92844faf1bcc`
- `medistack_v0.3_aliases.json` `ee25aed084a8a35f`
- `full_drug_name_index_sample_v1_0.json` `d329b2ddd3cdd05e`
- relations 60 · relation_card 1168 · name_only 16412 · DATA_URL v0.2 · published/clinical=false · reviewed_by 공란 · schedule 비활성 · 제품/구매/제휴 UI 0
