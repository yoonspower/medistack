# MediStack AutoFactory v1.5 — Next Live Wave Plan

> 이번 production harvest 이후 권장 순서. 모든 live 통합은 **auditor 통과 + reviewer note + per-family integrator** 게이트 필수. 이번 run의 live write 0.

## 현 상태
- existing prepared: 33 (combined 60→93)
- production 신규 reviewer-ready: 1 (시프로플록사신 × Al/Mg제산제 · F1 · independent audit pending)
- production needs_review: 16 · source_pending: 147
- actual live integration: 0 · reviewer note 실물: 없음

## 권장 순서
1. **auditor agent** (`agent/adversarial-auditor-v1.5`): production 신규 1건 + (선택) 기존 33 재검증. refute-by-default.
2. **reviewer note 트랙**: 기존 33의 PR-1 antibiotic23(F1+F2 23→83)이 이미 readiness 완료 → 사람 reviewer note 확보가 최우선 병목.
3. production 신규 1건(시프로 antacid): auditor 통과 시 PR-1 F1에 add-on 하거나 별도 소 wave로. 60→93 경로엔 영향 미미(+1).
4. **cleanup agent** (`agent/needs-review-cleanup-v1.5`): needs_review 16 + source_pending 147 재검색 — 특히 미네랄 standalone 인용·엽산 약물귀인 인용 확보.
5. 위 트랙 진행 후 Factory v1.6(추가 harvest) 재검토.

## live wave 우선순위 (reviewer note 확보 가정)
| 순위 | wave | delta | 비고 |
|---|---|---|---|
| 1 | PR-1 antibiotic23 (기존 F1+F2) | 60→83 | readiness 완료, reviewer note만 필요 |
| 2 | PR-2 chronic8 (기존 F9+F6) | +8 | |
| 3 | PR-3 F3+F4 (기존) | +2 | |
| 4 | production F1 antacid add-on (신규 1) | +1 | auditor 통과 후 |

## Factory v1.6 필요 여부
- source_pending 147 존재 → 추가 harvest 여지 있으나, **방어 가능 신규 관계 희소**가 확인됨.
- 우선순위는 기존 33의 reviewer note·live PR. 신규 대량 harvest보다 **품질·검토 트랙**이 병목.
- Factory v1.6는 reviewer note 트랙 1~2 wave 통합 + cleanup 진전 후 재검토 권장.
