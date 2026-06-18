# MediStack PR-1 antibiotic24 — Candidate Lock (v1.4)

> PR-1 antibiotic24 라이브 통합 대상 **24건** 잠금 문서. checker(`check_pr1_antibiotic24_pm_note_v1_4.py`)와
> integrator(`integrate_pr1_antibiotic24_live_v1_4.py`)가 공유하는 단일 진실원은
> `data/review/pr1_antibiotic24_candidate_lock_v1_4.json` 이다.

## 요약
- total: **24** (F1 18 + F2 5 + add-on 1)
- relation_count: **60 → 84** (delta +24)
- 신규 id: runtime max+1 (현 max 61 → 62..85)
- live exact duplicate: **0** · existing prepared duplicate: **0** · internal duplicate: **0**
- relation_card/name_only auto-flip: **0**
- alias enrichment: separate task (통합 전제 아님)

## 제외 (격리)
- needs_review 4건: `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`
- family 제외: F3, F9, F4, F6, F10 (F1/F2 만 본 wave 포함)

## F1 — 플루오로퀴놀론 × 미네랄/제산제 (18)
- `RF-F1-0021` — 노르플록사신 × 철분 (nutrient)
- `RF-F1-0022` — 노르플록사신 × 칼슘 (nutrient)
- `RF-F1-0024` — 노르플록사신 × 아연 (nutrient)
- `RF-F1-0041` — 자보플록사신 × 철분 (nutrient)
- `RF-F1-0042` — 자보플록사신 × 칼슘 (nutrient)
- `RF-F1-0044` — 자보플록사신 × 아연 (nutrient)
- `RF-F1-0066` — 토수플록사신 × 철분 (nutrient)
- `RF-F1-0067` — 토수플록사신 × 칼슘 (nutrient)
- `RF-F1-0026` — 페플록사신 × 철분 (nutrient)
- `RF-F1-0029` — 페플록사신 × 아연 (nutrient)
- `RF-F1-0025` — 노르플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0010` — 레보플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0035` — 로메플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0040` — 발로플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0020` — 오플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0045` — 자보플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0070` — 토수플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F1-0030` — 페플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)

## F2 — 테트라사이클린 × 금속/제산제 (5)
- `RF-F2-0105` — 독시사이클린 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F2-0110` — 미노사이클린 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)
- `RF-F2-0111` — 테트라사이클린 × 철분 (nutrient)
- `RF-F2-0114` — 테트라사이클린 × 아연 (nutrient)
- `RF-F2-0115` — 테트라사이클린 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)

## add-on — production·audit-cleanup AUDIT_PASS (1)
- `AFP-F1-시프로플록사신-al_mg_antacid` — 시프로플록사신 × Al/Mg 함유 제산제(약물) (drug/al_mg_antacid)

## 출처(source)
- F1/F2: `data/drafts/relation_factory_reviewer_ready_batch_v1_4.json` (적대검증 survives + family 재검증)
- add-on: `data/review/autofactory_v1_5_audit_cleanup_candidate_decisions.json` (origin=production, independent_audit=passed, fuller quote)

## 통합 등급
PM-reviewed verified-reference integration. published=false / clinical_reviewed=false / reviewed_by 공란 유지.
