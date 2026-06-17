# MediStack AutoFactory v1.5 — Auditor Recommendation

> 독립 감사자 권고. live 통합은 여전히 **clinical reviewer note + per-family integrator** 게이트 필수. 이 단계 live write 0.

## 권고 1 — production 1건: live PR 후보로 승격(reviewer note 대기)
- **시프로플록사신 × Al/Mg 함유 제산제(약물)** — AUDIT_PASS(5/5).
- 채택 quote(fuller): "…이 약의 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전 1～2시간 및 투여 후 4시간 이내에는 병용하지 않는 것이 바람직하다".
- 권고: 기존 **PR-1 antibiotic23(F1+F2)** wave 에 **F1 add-on(+1)** 으로 묶거나 별도 소 wave. reviewer note 확보 후 per-family integrator(F1) 로 live PR.
- 영향: combined 60→93(existing 33) → **94**(+audited production 1).

## 권고 2 — cleanup 16건: 강등 유지(자동 승격 금지)
- 전부 HOLD 확정. cleanup ledger 에 근거와 함께 보관. ready wave 혼입 금지.
- 재평가 조건: ①미네랄 standalone 보충제 흡수저하 인용('철분/칼슘 함유 제제') ②엽산 약물귀인 level-direction('혈청엽산치 저하') 인용 확보 시. 임신/태아 맥락은 불충분.

## 권고 3 — harvester 개선(source-fidelity)
- adversarial 감사가 **quote truncation** 결함을 적발: find_quote 의 ±160자 트림이 separation 절을 잘라 display 주장과 불일치 유발.
- 권고: harvester 가 흡수저하 절 + 후속 separation/간격 절을 한 문장 단위로 보존하도록 트림 경계 개선(다음 production run 적용).

## 권고 4 — needs_review backlog 4 (기존)
- 에티드론산 0148/0149·케토코나졸 0275: cleanup 재harvest 에서도 지지 인용 미발견 → **still_needs_review 유지**.
- 카르바마제핀 0245: 임신맥락 인용만 존재 재확인 → **needs_review 유지(권위 판정 일치)**.

## 권고 5 — Factory v1.6: 보류
- cleanup 신규 reviewer-ready 0 = 방어가능 신규관계 희소 재확인. source_pending 다수는 한국완제 미존재/임신맥락.
- reviewer note·live PR 트랙이 병목. 추가 대량 harvest 전에 reviewer note 트랙 1~2 wave 진행 권고.
