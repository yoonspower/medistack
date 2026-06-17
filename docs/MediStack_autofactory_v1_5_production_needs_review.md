# MediStack AutoFactory v1.5 — Production needs_review / source_pending

> 실 harvest에서 refute-by-default로 demote된 후보. **reviewer-ready wave와 격리.** cleanup agent 재검색 대상.

## needs_review 16건 — demotion 사유 분포
| 사유 | 수 | 교훈 |
|---|---|---|
| counterpart_not_standalone_supplement | 9 | F3 에티드론산 — 미네랄이 'Al/Mg 함유 제산제' 구성성분으로만 등장(standalone 보충제 근거 아님) |
| pregnancy_context_not_drug_depletion | 6 | F9 0245 — 엽산 언급이 약물 유발 depletion이 아니라 임신/태아 기형 맥락 |
| no_absorption_mechanism_verb | 1 | 흡수 기전 동사 부재 |

### 대표 demotion
- **퀴놀론(노르/페플/로메/발로/자보/토수…) × 마그네슘**: 인용이 "알루미늄 또는 **마그네슘 함유 제산제**" → 마그네슘은 제산제 구성성분, standalone 마그네슘 보충제 근거 아님 → needs_review.
- **테트라사이클린 × 칼슘·마그네슘**: "칼슘, 마그네슘, 알루미늄을 **함유하는 제산제**…" → 동일 트랩.
- **카르바마제핀 × 엽산 (= RF-F9-0245 권위 needs_review)**: 인용 "임신 중에는 엽산 결핍이 일어난다" → 약물 depletion 아님 → **재승격 차단**(기존 family 판정과 일치).
- **페노바르비탈·옥스카르바제핀·발프로산 × 엽산**: 전부 임신/태아/보충 권장 맥락 → needs_review.

## source_pending 147건
- 한국 허가 완제 미존재(search 0) 또는 라벨에 해당 counterpart 상호작용 문구 없음 → 실 인용 미확보.
- **source가 없으므로 source-confirmed/reviewer-ready 아님.** cleanup agent가 추가 품목/라벨 재검색 시 재평가.

## resolve 기준
- 미네랄 standalone: 해당 약물 라벨에 '철분 함유 제제'/'칼슘 함유 제제' 식 standalone 보충제 흡수저하 인용 확보 시.
- 엽산/비타민D depletion: 약물 귀인 + level-direction('혈청엽산치 저하'·'흡수가 저하') 인용 확보 시.
- source_pending: 다른 품목(itemSeq) 라벨에서 실 인용 확보 시.

## 격리 원칙
needs_review/source_pending/hold/reject는 **어떤 reviewer-ready wave에도 혼입 금지**. 해소는 cleanup agent + 근거 인용으로만, 자동 승격 금지.
