# MediStack AutoFactory v1.5 — Cleanup needs_review / still_needs_review

> cleanup 재harvest 후에도 강등 유지된 후보. **reviewer-ready 격리.** 자동 승격 금지·근거 인용 확보 시에만 재평가.

## 강등 유지 분포 (167)
| 사유 | 수 | 재평가 조건 |
|---|---|---|
| no_supporting_quote_after_multi_label_search | 150 | 다른 itemSeq/품목 라벨에서 실 상호작용 인용 확보 시 |
| counterpart_not_standalone_supplement (F3) | 9 | '철분/칼슘 함유 제제' 식 standalone 보충제 흡수저하 인용 확보 시 |
| pregnancy_context_not_drug_depletion (F9) | 7 | '혈청엽산치 저하'·'엽산의 흡수 저하' 약물귀인 level-direction 인용 확보 시 |
| no_absorption_mechanism_verb | 1 | 첨가제 표 아닌 상호작용 문구 + 흡수저하 동사 확보 시 |

## quote 보유 16건 (독립 감사 HOLD 확정)
- **F1/F2 ×마그네슘·칼슘** (8): 미네랄이 'Al/Mg 함유 제산제' 구성성분으로만 등장 → standalone 보충제 아님.
- **F9 ×엽산** (6, 카르바마제핀 0245 포함): 임신/태아/보충권장 맥락 → 약물 depletion 아님.
- **알렌드론산 ×마그네슘·제산제** (2): 첨가제 표(스테아르산마그네슘) noise.

## 150 무인용 그룹 — 주요 사유
- 주사제·한국 완제 미존재(졸레드론산·파미드론산·인카드론산 등 일부 비스포·일부 희소 퀴놀론).
- 라벨에 해당 counterpart 상호작용 문구 없음(B12/엽산/비타민D depletion 직접근거 부재 다수).

## 기존 needs_review 4
- RF-F3-0148/0149 에티드론산: 지지 인용 미발견 → still_needs_review.
- RF-F9-0245 카르바마제핀×엽산: 임신맥락 인용만 → needs_review 유지(권위 판정 일치).
- RF-F10-0275 케토코나졸×제산제: 지지 인용 미발견 → still_needs_review.

## 격리 원칙
needs_review/still_needs_review/hold/reject 는 **어떤 reviewer-ready wave 에도 혼입 금지.** 해소는 근거 인용 + 독립 검토로만, 자동 승격 금지.
