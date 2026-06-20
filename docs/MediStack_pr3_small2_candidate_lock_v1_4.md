# MediStack v1.4 — PR-3 small2 candidate lock (handoff)

기계 판독 단일 진실원: `data/review/pr3_small2_candidate_lock_v1_4.json`.
checker(`check_pr3_small2_pm_note_v1_4.py`) + integrator(`integrate_pr3_small2_live_v1_4.py`) 공유.

## 잠금 요약
- wave: small2 · total: 2 (F3 1 · F4 1)
- baseline_relation_count: 92 · expected_relation_count_after: 94 · relation_delta: +2
- baseline_max_id: 93 · expected_ids: 94..95 (runtime max+1)
- live_exact_duplicate 0 · existing_prepared_duplicate 0 · internal_duplicate 0 · pr1_pr2_duplicate 0
- relation_card_name_only_auto_flip 0

## 통합 대상
- RF-F3-0147 이반드론산 × Al/Mg 함유 제산제(약물) · absorption/separation · al_mg_antacid · itemSeq 201207007
- RF-F4-0173 레보티록신 × 알루미늄 함유 제산제(약물) · absorption/separation · al_mg_antacid · itemSeq 197400278
live 렌더 선례: 이트라코나졸×Al/Mg제산제(id61) + PR-1 F1/F2 al_mg_antacid 18건.

## 제외 (lock 강제)
- needs_review_exclusion: RF-F3-0148, RF-F3-0149, RF-F9-0245, RF-F10-0275
- family_exclusion: F1, F2, F6, F9, F10
  - F1/F2 = PR-1 live · F6/F9 = PR-2 live (재추가 금지)
  - F10(케토코나졸 0275) = route/availability needs_review
  - F3 0148/0149(에티드론산) = cation 결속 needs_review

## 검증 게이트
- check_pr3_small2_pm_note_v1_4.py / integrate_pr3_small2_live_v1_4.py(--dry-run/--apply) /
  validate_pr3_small2_post_integration_v1_4.py + smoke
