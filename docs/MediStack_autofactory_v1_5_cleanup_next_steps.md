# MediStack AutoFactory v1.5 — Cleanup Next Steps

> audit + cleanup 이후 권장 순서. 모든 live 통합은 **reviewer note + per-family integrator** 게이트 필수. 이 트랙 live write 0.

## 현 상태
- existing prepared 33 (60→93)
- audited production reviewer-ready: 1 (시프로×제산제 · AUDIT_PASS)
- cleanup 신규 reviewer-ready: 0
- new_ready_total: 1 → combined 60→93→94 (reviewer note 후)
- still_needs_review: 167 (quote 보유 16 HOLD + 무인용 150 + 기존 4) · false-demotion 0

## 권장 순서
1. **reviewer note(사람) 확보** → **PR-1 antibiotic23(기존 60→83)** live PR — 최우선 병목(readiness 이미 완료).
2. 시프로×제산제 1건: auditor 통과 → PR-1 에 **F1 add-on(+1)** 또는 별도 소 wave (reviewer note 후).
3. PR-2 chronic8(기존 F9+F6 +8) · PR-3 F3+F4(기존 +2).
4. needs_review 해소(근거 인용 확보 시): 에티드론산 0148/0149 standalone 인용 · 카르바마제핀 0245 약물귀인 인용 · 케토코나졸 0275 route.
5. harvester 개선 적용(quote truncation → 문장 단위 보존) 후 필요 시 Factory v1.6.

## reviewer note 필요 범위
- 기존 33(PR-1/2/3) + 시프로×제산제 1 = live PR 대상 34. 각 wave 별 reviewer note.

## Factory v1.6 필요 여부: **보류**
- cleanup 신규 0 = 방어가능 신규관계 희소 재확인. 추가 대량 harvest 는 source_pending backlog 만 키움.
- 우선순위: reviewer note · live PR 트랙. v1.6 은 그 후 재검토.

## bot-runner 구축 필요 여부: **현 시점 불요**
- 자동 harvest 의 실가치는 source-check queue + 강등 ledger 이며, 신규 reviewer-ready 산출은 희소.
- 상시 bot-runner 보다 **on-demand production/cleanup + 독립 auditor workflow** 조합이 적합(이번 라운드로 검증).
