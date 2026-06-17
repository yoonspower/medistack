# MediStack AutoFactory v1.5 — Cleanup Report

> needs_review/source_pending **재harvest + 재분류** (실 MFDS·다중 itemSeq·broadened scan). NO-LIVE-WRITE. run_date 2026-06-17.

## 대상 & 결과
| 항목 | 수 |
|---|---|
| cleanup 대상 (prod needs_review 16 + source_pending 147 + 기존 needs_review 4) | 167 |
| label fetches (다중 itemSeq) | 274 |
| 실 quote 발견 (source-confirmed) | 17 |
| **신규 reviewer-ready** | **0** |
| still_needs_review | 167 |

## verdict 사유 분포
| 사유 | 수 |
|---|---|
| no_supporting_quote_after_multi_label_search | 150 |
| counterpart_not_standalone_supplement (F3 교훈) | 9 |
| pregnancy_context_not_drug_depletion (F9 교훈) | 7 |
| no_absorption_mechanism_verb | 1 |

## 왜 신규 reviewer-ready가 0인가 (정직한 결과)
- 17개 실 quote 전부 refute-by-default 로 강등됨: 미네랄이 제산제 구성성분(F1/F2 ×Mg/Ca)이거나, 엽산이 임신/태아 맥락(F9 ×folate)이거나, 첨가제 표 noise(알렌드론산).
- 150건은 다중 itemSeq 라벨에서도 지지 인용 미발견 — 한국 허가 완제 미존재(주사제 졸레드론산/파미드론산 등) 또는 라벨에 해당 counterpart 상호작용 문구 없음.
- **독립 감사(53 agents)가 16개 quote 후보 전부 HOLD 확정 · false-demotion 0** → 강등이 옳음을 검증.

## 기존 needs_review 4 재검
| id | 약물×counterpart | cleanup 결과 |
|---|---|---|
| RF-F3-0148 | 에티드론산×칼슘 | 지지 인용 미발견 → still_needs_review |
| RF-F3-0149 | 에티드론산×철분 | 지지 인용 미발견 → still_needs_review |
| RF-F9-0245 | 카르바마제핀×엽산 | 임신맥락 인용만 → needs_review 유지(권위 일치) |
| RF-F10-0275 | 케토코나졸×제산제 | 지지 인용 미발견 → still_needs_review |

## Source fidelity
- official source ratio: 100% (nedrug.mfds.go.kr) · 비공식/쇼핑몰/블로그 0건.
- mineral/antacid 혼동 차단: 9 · folate 임신맥락 차단: 7 · family 일반화 승격: 0 · 허위 인용: 0.

## 산출물
`data/review/autofactory_v1_5_cleanup_{reviewed·source_confirmed·reviewer_ready·reviewer_ready_waves·still_needs_review·hold_reject·dashboard}.json`
