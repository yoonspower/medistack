# MediStack AutoFactory v1.5 — Audit Report

> production reviewer-ready 1건 + cleanup 강등 16건의 **독립 적대 감사** (workflow wf_ef5c28bc-745 · 53 agents · refute-by-default · quote 만 근거·no fetch). NO-LIVE-WRITE.

## Part A — production reviewer-ready 독립 감사
**시프로플록사신 × Al/Mg 함유 제산제(약물)** (F1 · absorption/separation)

| 렌즈 | verdict |
|---|---|
| source-supports-claim | AUDIT_PASS |
| counterpart-type | AUDIT_PASS |
| individual-ingredient | AUDIT_PASS |
| dedup-policy | AUDIT_PASS |
| copy-conservatism | PASS_WITH_COPY_CHANGE |

**결정: AUDIT_PASS (5/5 통과)**

- 5명 모두 관계 유효 판정: quote 가 '이 약의 흡수가 저하되어 효과가 저하' 명시 · counterpart 는 미네랄이 아니라 **제산제(약물 카테고리)** 자체라 F3 에티드론산 트랩과 무관 · 시프로 개별 라벨 근거(계열 일반화 아님) · live 시프로×미네랄과 별개 관계.
- copy-conservatism 렌즈 1명이 **유효한 지적**: 기계 harvester 가 quote 를 흡수저하 절에서 truncate → display 의 '복용 시점 분리 안내' 주장이 quote 범위 초과(PASS_WITH_COPY_CHANGE).
- **해소**: 전체 라벨 재확인 → "이 약 투여 전 1～2시간 및 투여 후 4시간 이내에는 병용하지 않는 것이 바람직하다" 실재 확인 → **fuller quote 채택**, display(분리 안내) source-backed → **AUDIT_PASS 확정**.
- 신규 F1 add-on 가능 여부: **가능** (auditor 통과 · reviewer note 확보 후 per-family integrator).

## Part B — cleanup 강등 16건 독립 재판정 (false-demotion 검사)
각 후보 3렌즈(standalone-vs-antacid-component · context-validity · mechanism-and-attribution) refute-by-default.

| 결과 | 수 |
|---|---|
| HOLD 확정 (강등 옳음) | **16** |
| PROMOTE (false-demotion) | **0** |

- F1/F2 ×마그네슘·칼슘 (9): 미네랄이 'Al/Mg 함유 제산제' 구성성분 → standalone 보충제 아님(HOLD 확정).
- F9 ×엽산 (6, 카르바마제핀 0245 포함): 임신/태아/보충권장 맥락 → 약물 depletion 아님(HOLD 확정·0245 재승격 차단 재확인).
- 알렌드론산 ×Mg/제산제 (2): 첨가제 표(스테아르산마그네슘) noise → HOLD.
- 로메/자보 ×마그네슘은 1/3 PROMOTE 표(라벨에 '철분/칼슘 함유 제제' standalone 형태도 병기되나, 후보는 ×마그네슘이고 Mg 는 제산제에만 등장 → 다수 HOLD).

## 결론
- production 1건 **독립 감사 통과**(fuller quote 보정 후 AUDIT_PASS).
- 기계 분류의 강등 16건 **전부 독립 확정**, false-demotion **0** → 분류 방법론 검증.
- 핵심 교훈: 적대 감사가 harvester 의 **quote truncation 결함**을 잡아 source-fidelity 를 강화(display 가 라벨 범위 내인지 검증).
