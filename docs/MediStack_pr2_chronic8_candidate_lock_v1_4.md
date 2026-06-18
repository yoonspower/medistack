# MediStack v1.4 — PR-2 chronic8 candidate lock (handoff)

기계 판독 단일 진실원: `data/review/pr2_chronic8_candidate_lock_v1_4.json`.
checker(`check_pr2_chronic8_pm_note_v1_4.py`) + integrator(`integrate_pr2_chronic8_live_v1_4.py`) 공유.

## 잠금 요약
- wave: chronic8
- total: 8 (F9 7 = 엽산 3 + 비타민D 4 · F6 1)
- baseline_relation_count: 84 · expected_relation_count_after: 92 · relation_delta: +8
- baseline_max_id: 85 · expected_ids: 86..93 (runtime max+1)
- live_exact_duplicate: 0 · existing_prepared_duplicate: 0 · internal_duplicate: 0 · pr1_duplicate: 0
- relation_card_name_only_auto_flip: 0 (pool=aliases.verified_item_seqs 와 decoupled)

## 통합 약물·영양소
F9: 설파살라진/트리메토프림/페니토인 × 엽산 · 카르바마제핀/페노바르비탈/페니토인/프리미돈 × 비타민D.
F6: 에스오메프라졸 × 비타민B12.
모두 mechanism=depletion · action=monitoring · counterpart_type=nutrient · counterpart_category=null.
live 렌더 선례: 메트포르민×B12(id12) · PPI×B12 5건.

## 제외 (lock 강제)
- needs_review_exclusion: RF-F9-0245, RF-F10-0275, RF-F3-0148, RF-F3-0149
- family_exclusion: F1, F2, F3, F4, F10
  - F1/F2 = PR-1 antibiotic24 이미 live(재추가 금지)
  - F3/F4 = PR-3 small2(92→94) 별도
  - F10(케토코나졸 0275) = route/availability needs_review

## 검증 게이트
- check_pr2_chronic8_pm_note_v1_4.py : PM note 가 토큰/scope/제외/보호상태/copy 원칙 충족
- integrate_pr2_chronic8_live_v1_4.py --dry-run/--apply : build_subset 재사용 + 계약/가드 + PM note 게이트
- validate_pr2_chronic8_post_integration_v1_4.py / smoke : 통합 후 84→92·범위·보호상태·source·금칙
