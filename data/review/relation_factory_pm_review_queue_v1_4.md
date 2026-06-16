# MediStack — Relation Factory v1.4 PM Review Queue (adversarial 반영)

> **LIVE 아님 · 자동 승격 금지 · reviewer/PM 승인·clinical reviewer note 전 live 금지 · 제품/구매/제휴 없음.**
> 적대검증(refute-by-default 10-lens) 후. 정본: `relation_factory_adversarial_verify_v1_4.json` · reviewer-ready `relation_factory_reviewer_ready_batch_v1_4.json`.

## 1. 적대검증 요약

- 대상 draft: **43**
- survives: **31** · survives_with_copy_change: **6** → **reviewer-ready 37**
- needs_review: **5** · hold: **1** · reject: **0** → **강등 6**

## 2. family 별 생존율

| family | total | survives | yield |
|---|---|---|---|
| F1 | 18 | 18 | 1.0 |
| F10 | 2 | 1 | 0.5 |
| F2 | 5 | 5 | 1.0 |
| F3 | 4 | 3 | 0.75 |
| F4 | 1 | 1 | 1.0 |
| F6 | 1 | 1 | 1.0 |
| F9 | 12 | 8 | 0.67 |

## 3. 강등 후보(draft 제외)

| candidate_id | relation | verdict | 사유 |
|---|---|---|---|
| RF-F3-0139 | 알렌드론산 × Al/Mg 함유 제산제(약물) | needs_review | Al/Mg 제산제를 직접 명시하지 않는 generic quote('제산제')이고, 명시 양이온은 칼슘뿐(이미 live). 특이성 부족 — refute(직접근거 약함). |
| RF-F10-0276 | 포사코나졸 × Al/Mg 함유 제산제(약물) | hold | 포사코나졸 quote 가 H2 차단제 상호작용만 서술 — al_mg_antacid 로 매핑 불가(주어/카테고리 불일치). refute: 제산제 직접근거 없음. acid_reducing_drug(H2/PPI) category 미존재로 현재 표현 불가 → hold. |
| RF-F9-0260 | 라모트리진 × 엽산 | needs_review | 동물(랫트)·임신 한정 근거를 인체 만성 depletion 으로 일반화 — 근거 강도/맥락 불일치(refute: 인체 만성 depletion 직접근거 아님). |
| RF-F9-0257 | 옥스카르바제핀 × 엽산 | needs_review | 엽산 결핍이 이상반응 열거문에 저신호로 매몰 — 직접 depletion 근거로 보기 약함. |
| RF-F9-0251 | 페노바르비탈 × 엽산 | needs_review | 임신 한정 근거를 일반 장기복용으로 일반화 — '원문보다 강하면 금지' 위반 소지. (페노바르비탈 효소유도 엽산저하는 임상상 알려졌으나 라벨 quote 는 임신 한정.) |
| RF-F9-0254 | 프리미돈 × 엽산 | needs_review | 프리미돈×엽산: 임신 한정 근거를 일반 장기복용으로 일반화 — 동 RF-F9-0251. |

## 4. 주요 false-positive 패턴

- F10 acid-reducer 주어 혼동: 포사코나졸 quote 는 H2 차단제 — al_mg_antacid 매핑 불가.
- F9 임신 한정 근거 일반화: 페노바르비탈/프리미돈 × 엽산 quote '임신중' → 카드 '장기간 복용' 과일반화.
- F9 동물·임신 근거: 라모트리진 × 엽산 = 랫트 시험.
- F9 이상반응 열거 저신호: 옥스카르바제핀 엽산이 저나트륨혈증 나열문에 매몰.
- F3 generic '제산제' quote + live 중복: 알렌드론산 antacid 가 칼슘(live)만 명시.
- quote hygiene(비치명): 에티드론산 '○ 파제트병'·카르바마제핀 표 raw·레보티록신 Al-only.

## 5. 다음 액션(LIVE 아님)

1. reviewer-ready 37 → clinical reviewer note(family 그룹별) → dry-run integrator → 선택 subset 별도 PR live.
2. needs_review 5 → 라벨 재검색(임신 외 엽산·Al/Mg 직접 명시) 후 재평가.
3. hold 1(포사코나졸) → acid_reducing_drug category 설계 트랙.
4. 다음 수확: F9 만성 depletion·F10 azole 확장(최고 수확) + 미커버 약물.
