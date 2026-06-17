# MediStack v1.4 — needs_review 격리
> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 실물 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 불변. 단일 소스: `data/review/per_family_live_pr_readiness_v1_4.json`.

## 대상 4건 (4)
| id | family | desc | reason | 해소 조건 |
|---|---|---|---|---|
| `RF-F3-0148` | F3 | 에티드론산 × 칼슘 | source parse 미해소(quote 경계) | 에티드론산 라벨 인용 파싱·기전동사 확정 |
| `RF-F3-0149` | F3 | 에티드론산 × 철분 | source parse 미해소 | 동일 — 에티드론산 parse |
| `RF-F9-0245` | F9 | 카르바마제핀 × 엽산 | 저신호 이상반응 열거('드물게')·기전/level-direction/연용-remedy 부재 | 흡수/대사 기전 또는 혈청엽산치 방향 인용 확보 시 재평가 |
| `RF-F10-0275` | F10 | 케토코나졸 × 제산제 | route/availability 강등(경구 품목 위장 불가) | route 근거 재확인·display 재작성 |

- 제외 대상: all waves, true scenario, reviewer note templates, actual integration commands

## conditional scenarios (reviewer 가 needs_review 해소 note 별도 제공 시에만)
- F3_with_etidronate: 60→63(+에티드론산 2)
- F9_with_0245: 60→68(+0245 1)
- F10_with_0275: 60→61(+0275 1)
- note: 위 conditional 은 reviewer 가 needs_review 해소 note 를 별도 제공할 때만. 본 live PR wave 와 격리.

> 검증: `python3 scripts/validate_needs_review_quarantine_v1_4.py`
