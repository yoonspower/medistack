# MediStack AutoFactory v1.5 — Production Family Waves

> 신규 reviewer-ready 후보의 family clustering. 전건 `independent_audit_pending=true` — auditor agent 통과 + reviewer note 확보 전까지 live 통합 금지.

## 신규 reviewer-ready wave
| wave | family | 후보 | delta |
|---|---|---|---|
| prod_F1_1 | F1 (Fluoroquinolone × antacid) | 시프로플록사신 × Al/Mg 함유 제산제(약물) | +1 |

합계: **1건** (auto_pass 1 · copy_change 0).

## 후보 상세
**AFP-F1-시프로플록사신-al_mg_antacid**
- mechanism: absorption · action: separation · evidence: moderate
- counterpart: Al/Mg 함유 제산제(약물) (counterpart_type=drug)
- source: 식약처 nedrug getItemDetail / 시프로플록사신 / 상호작용 / "알루미늄 또는 마그네슘 함유 제산제…의 병용에 의해 이 약의 흡수가 저하되어 효과가 저하" / 확인일 2026-06-17
- display(보수): "이 약은 Al/Mg 함유 제산제(약물)과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다…"
- dedup: live(시프로 ×철/칼슘/Mg/아연 보유, 제산제 미보유) 0 · existing-33 0
- 선례: 기존 8개 퀴놀론 al_mg_antacid 패턴(id61 포함)과 동형

## existing_prepared (재카운트 금지)
기존 33 integration-ready는 `existing_prepared`로 표시되며 신규 wave 수에 포함하지 않는다.
combined future = 60→93 (existing) + new_ready(1).

## 다음 단계
1. `agent/adversarial-auditor-v1.5` 가 위 1건을 독립 재검증(refute-by-default).
2. 통과 시 PR-1 antibiotic23(F1+F2)과 묶거나 별도 F1 add-on으로 reviewer note 트랙 진입.
3. reviewer note 확보 후에만 per-family integrator(F1)로 live PR.
