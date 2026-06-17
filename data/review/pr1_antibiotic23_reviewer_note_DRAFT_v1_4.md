# PR-1 antibiotic23 — reviewer note DRAFT (검토자 작성용 양식)
#
# ⚠️ 이 파일은 **빈 양식**입니다. 검토자가 아래 <...> 자리를 실제 값으로 채워야 하며,
#    채우기 전에는 check_live_pr_reviewer_note 가 **거부**합니다(placeholder/commit/식별자 미충족).
#    채운 뒤 별도 파일로 저장하여 checker 통과 시에만 live PR 진행.

검수자: RPH-<검수자ID> (PM 승인 근거 첨부)   검토일 YYYY-MM-DD
검토 패키지: per_family_live_pr_readiness v1.4 / commit <commit-hash>
scope(wave=antibiotic23) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.
승인 candidate_id 전건 (23건 = F1 18 + F2 5):
[F1 — 퀴놀론 × 미네랄/제산제]
  - RF-F1-0021
  - RF-F1-0022
  - RF-F1-0024
  - RF-F1-0041
  - RF-F1-0042
  - RF-F1-0044
  - RF-F1-0066
  - RF-F1-0067
  - RF-F1-0026
  - RF-F1-0029
  - RF-F1-0025
  - RF-F1-0010
  - RF-F1-0035
  - RF-F1-0040
  - RF-F1-0020
  - RF-F1-0045
  - RF-F1-0070
  - RF-F1-0030
[F2 — 테트라사이클린 × 금속/제산제]
  - RF-F2-0105
  - RF-F2-0110
  - RF-F2-0111
  - RF-F2-0114
  - RF-F2-0115
relation delta: +23 (60 → 83, 신규 id = runtime max+1).
grouping 승인: antibiotic23 wave 단위 한 번에 통합.
출처(source) fidelity: 식약처 허가사항 인용과 일치 보존 확인.
관리 문구(management copy): 참고·상담 톤 보수성 유지 확인(분리복용/정기확인 문의, 지시 아님).
published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.
제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.
needs_review RF-F3-0148, RF-F3-0149, RF-F9-0245, RF-F10-0275 는 본 승인에서 제외 확인.
rollback 가능(wave 단위 git revert) 확인.
