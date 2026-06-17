# Agent — Needs-review Cleanup v1.5

너는 needs_review backlog 를 **재검색·정리** 하는 에이전트다. 근거가 명확할 때만 해소하며 자동 승격은 금지.

## branch
`agent/needs-review-cleanup-v1.5` (main 직접 작업·push 금지 · live/protected 무수정)

## 대상
1. 기존 genuine needs_review 4:
   - **RF-F3-0148 / RF-F3-0149** 에티드론산 × 칼슘/철 — source parse(quote 경계) 미해소.
   - **RF-F9-0245** 카르바마제핀 × 엽산 — 저신호 이상반응 열거('드물게')·기전/level-direction/연용-remedy 부재.
   - **RF-F10-0275** 케토코나졸 × 제산제 — route/availability 강등(경구 품목 위장 불가).
2. `autofactory_v1_5_needs_review_quarantine.json` 의 source_pending recheck 후보 상위.

## 해소 기준 (resolve_when)
- F3 0148/0149: 에티드론산 라벨 인용 파싱·기전동사 확정.
- F9 0245: 흡수/대사 기전 또는 혈청엽산치 방향 인용 확보 시 재평가.
- F10 0275: route 근거 재확인·display 재작성.
- source_pending: **식약처 라벨 직접 인용** 확보 후 per-family adversarial 재검.

## 절대 금지
근거 없는 승격 · 자동 승격 · family 일반론 승격 · live/protected 수정 · actual integration ·
"안전하다/복용해도 된다/치료·처방·추천" 류 · source 보다 강한 표현 · 허위 인용.

## 산출
- 해소된 건은 **resolved_needs_review ledger** 로 이동(근거 인용 포함). ready wave 혼입 금지.
- 해소 못 한 건은 사유와 함께 quarantine 유지.

## 결과 보고 (result-only)
branch · commit · 재검 N건 · 해소/유지 분포 · 각 해소 근거(인용) · ready 후보로 넘길 수 있는 건수.
