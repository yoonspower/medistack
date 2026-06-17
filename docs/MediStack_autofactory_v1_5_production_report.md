# MediStack AutoFactory v1.5 — Production Harvest Report

> **실제 MFDS 허가사항 원문 harvest · NO-LIVE-WRITE.** run_date 2026-06-17 · online mode · branch `agent/autofactory-v1.5-production`.
> 허위 인용 0 · source 없는 후보 승격 0 · live/protected 무수정 · actual integration 0.

## 요약
SDK(`medistack_sdk.nedrug_client`)로 family universe 약물의 식약처 허가사항 라벨을 실제 fetch하고,
**라벨에 실재하는 verbatim 인용**만으로 source pointer/quote를 채운 뒤 refute-by-default로 분류했다.

| 단계 | 수 |
|---|---|
| raw candidates | 301 |
| source-check queue | 164 |
| source-confirmed 신규 (실 인용 보유) | 17 |
| source_pending (인용 미발견) | 147 |
| hold (정책민감 family) | 67 |
| reject (live dup·방향오류) | 38 |
| existing_prepared (기존 33 중복) | 32 |
| drugs fetched | 62 (label text 확보 47) |

## Auto-review (refute-by-default)
| verdict | 수 |
|---|---|
| auto_pass | **1** |
| copy_change | 0 |
| needs_review | 16 |
| **reviewer-ready 신규** | **1** (independent audit pending) |

신규 reviewer-ready 1건: **시프로플록사신 × Al/Mg 함유 제산제(약물)** (F1·absorption/separation).
근거 인용: "알루미늄 또는 마그네슘 함유 제산제…의 병용에 의해 이 약의 흡수가 저하되어 효과가 저하" (식약처 nedrug, 확인일 2026-06-17).
live는 시프로플록사신 ×철/칼슘/마그네슘/아연만 보유 → 제산제(약물) 관계는 신규·중복 0. 기존 8개 퀴놀론 al_mg_antacid 패턴과 동형.

## 목표 대비 달성률
| 지표 | target | 결과 |
|---|---|---|
| raw | 800~1200 | 301 (universe source_check=true 한도) |
| source-check queue | 400~600 | 164 |
| source-confirmed 신규 | 100~200 | 17 (실 인용) |
| reviewer-ready 신규 | 50~100 | **1** |
| needs_review 신규 | 80~150 | 16 + source_pending 147 |

> **target 미달이나 source fidelity를 낮추지 않았다.** 신규 reviewer-ready를 100에 맞추려고 약한 source를 올리지 않았다.

## 왜 reviewer-ready가 1인가 (정직한 병목)
대부분의 신규 (약물×counterpart) 후보는 다음 중 하나라 refute-by-default로 demote/제외됐다:
- **미네랄이 standalone 보충제가 아니라 '알루미늄/마그네슘 **함유 제산제**' 구성성분으로만 등장**(F3 에티드론산 교훈) → 9건 needs_review.
- **엽산 언급이 약물 유발 depletion이 아니라 임신/태아 기형 맥락**(F9 0245 교훈) → 6건 needs_review (카르바마제핀×엽산 RF-F9-0245 재승격 차단 포함).
- 흡수 기전 동사 부재 1건.
- 이미 live(60) 또는 existing-prepared(33)에 covered.
- 한국 허가 완제 미존재(search 0) 또는 라벨에 해당 상호작용 문구 없음 → source_pending 147.

즉 방어 가능한 신규 관계는 희소하며, 이것이 기존 33이 family별 정밀 검토를 거친 이유다. 1건은 보수적·정직한 결과다.

## Source fidelity
- source pointer coverage: 17/164 (queue 중 실 인용 보유)
- official source ratio: **100%** (식약처 nedrug 허가사항만 · SDK 단일 게이트웨이)
- 비공식/블로그/쇼핑몰 source: **0건 사용**
- family 일반화 승격: **0** (약물별 라벨 직접 인용만)

## 가드
live write 0 · protected hash 불변 · forbidden phrase 0 · reviewer-ready ∩ live = 0 · ∩ existing-33 = 0 ·
모든 신규 reviewer-ready `independent_audit_pending=true` (auditor agent + reviewer note 전까지 live 금지).

## 산출물
`data/review/autofactory_v1_5_production_{raw_candidates·source_check_queue·source_confirmed·auto_reviewed·adversarial_results·family_clusters·reviewer_ready_waves·needs_review_quarantine·dashboard}.json`
