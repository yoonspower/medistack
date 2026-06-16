# MediStack — Penicillamine FE/ZN Subset Reviewer Package (v1.3)

> **목적**: theme map 6건 중 **페니실라민 × 철분/아연 2건만** 우선 검토·승인하기 위한 단일 패키지.
> 이 subset 은 둘 다 **counterpart_category=null(일반 영양소 relation)** 이라 **live 선행조건이 0** (validator/src/facet/chip 변경 불필요)
> → theme map 6건 중 **가장 먼저 안전하게 통합 가능한 묶음**.
> **상태**: source_confirmed(식약처 nedrug 198300142) · adversarial_verified(프롬프트 8) · harvester 편입(프롬프트 9) 완료. **live 통합 0**.
> **연관**: dry-run `data/review/penicillamine_subset_live_dryrun_v1_3.json` · mechanism 결정 `docs/MediStack_penicillamine_mechanism_decision_v1_3.md` ·
> full reviewer package `docs/MediStack_reviewer_package_theme_map_v1_3.md` · grouping `docs/MediStack_theme_map_grouping_strategy_v1_3.md`.

---

## 1. 범위

| 포함(검토 대상) | 제외 |
|---|---|
| **TM-CHEL-01-FE** 페니실라민 × 철분 | 같은 라벨의 **Al/Mg 제산제** 각도(별도 antacid 트랙 — 이번 아님) |
| **TM-CHEL-01-ZN** 페니실라민 × 아연 | 페니실라민의 **다른 영양소**(copper/B6 등 — 라벨에 있더라도 이번 범위 아님·근거 없는 확장 금지) |
| | theme map 나머지 4건(TM-LIP-01/02·TM-CEPH-AC-01/02 — 선행조건 PR 필요) · 칼륨 4 · AT-FEX |

> reviewer note ≠ `clinical_reviewed=true`. 천장 = **verified_reference**(허가사항 출처 참고정보 노출).

## 2. 안전 원칙

- 철분/아연 **복용 권유 아님**. 제품 추천 아님. 복용 지시 아님. source quote 기반 참고정보.
- 흡수/효과 상호작용과 **복용 시점 분리**만 안내(라벨 '동시투여를 피한다' 충실 · 직접 명령 금지).
- "식약처 승인 / 약사 검수 완료 / 법적 문제 없음" 표현 금지.

## 3. 후보별 카드

### TM-CHEL-01-FE — 페니실라민 × 철분
- itemSeq **198300142** / 알타민캡슐250밀리그램(디-페니실라민) / 상호작용
- source quote: *"경구철제제(구연산제일철나트륨, 황산철 등), 마그네슘 또는 알루미늄 함유제산제(수산화마그네슘, 수산화알루미늄)는 이 약의 흡수율을 저하시켜 효과를 감소시킬 수 있으므로, 반드시 투여해야 하는 경우에는 동시투여를 피한다."*
- app display: "이 약은 철분제와 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- management: "철분 보충제와는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
- mechanism **absorption** · action **separation** · evidence **high** · confidence **high** · adversarial **survives**
- remaining risk: 전문의약품·소량 유통(베타 노출 가치는 reviewer). 라벨의 Al/Mg 제산제 각도는 **이 카드에 미확장**(별도 트랙).
- reviewer Q: (a) Al/Mg 제산제 각도를 antacid 트랙으로도 만들지? (b) 전문약·소량 유통이 베타 노출 가치에 맞는가?

### TM-CHEL-01-ZN — 페니실라민 × 아연
- itemSeq **198300142**(FE 와 동일 라벨) / 상호작용
- source quote: *"아연을 함유하는 경구제는 이 약의 효과를 감소시킬 수 있으므로, 반드시 병용해야 하는 경우에는 동시투여를 피한다."*
- app display: "이 약은 아연 보충제와 함께 복용하면 약의 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- management: "아연 보충제와는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
- mechanism **absorption(추론)** · action **separation** · evidence **high** · confidence **moderate** · adversarial **survives_with_copy_change**
- remaining risk: 라벨은 아연에 대해 **'효과 감소'만** 명시(철분은 '흡수율 저하' 명시) → mechanism=absorption 은 **추론**. **user 카피는 라벨대로 '효과 감소'**(absorption 단정 안 함 — 영향 없음).
- reviewer Q: (a) FE 와 묶어 다중 영양소 카드로? (b) mechanism 을 absorption 으로 둘지(상세 `docs/MediStack_penicillamine_mechanism_decision_v1_3.md`)?

## 4. FE vs ZN 차이

| | TM-CHEL-01-FE 철분 | TM-CHEL-01-ZN 아연 |
|---|---|---|
| 라벨 표현 | **'흡수율을 저하'** (직접) | **'효과를 감소'** (흡수 미명시) |
| mechanism | absorption (명확) | absorption (**추론**) |
| confidence | high | moderate |
| verdict | survives | survives_with_copy_change |

→ FE 는 absorption/separation 비교적 명확. ZN 은 mechanism 태그 결정 필요(권고 = Option A: absorption 유지 + 추론 flag, user 카피는 '효과 감소' 충실). 상세 = mechanism 결정 문서.

## 5. live integration readiness

| 항목 | 상태 |
|---|---|
| v0.2 validator(현행) | ✅ **PASS** (separation·absorption·counterpart_category=null) |
| src getFacets / render chip | **변경 불필요**(일반 영양소 — separation chip '복용 간격') |
| full index / aliases / relation_card 1168·name_only 16412 | **변경 불필요** |
| **live 선행조건** | **0** (dry-run `live_integration_prerequisites: []`) |

> 예상 통합: relations **60 → 62**(id 62~63). full index/aliases 무변경.

## 6. reviewer note 템플릿

> 꺾쇠 placeholder 를 실제 값으로 교체. 미교체(`<…>`/`YYYY-MM-DD`)·`SAMPLE` 토큰이 남으면 게이트가 거부.
> 게이트(`integrate_penicillamine_subset_v1_3.check_reviewer_note`) 강제 요건: 승인 토큰 · **FE/ZN 2건 전건** ·
> ZN mechanism 결정 · grouping(개별 카드) 결정 · verified_reference 동의 · clinical_reviewed=true 아님 ·
> 제품 추천 아님 · **철분/아연 보충 권유 아님**.

```
검수자: <검수자 식별자>  검토일 <검토일 YYYY-MM-DD 를 실제 날짜로>
승인(approved): 페니실라민 subset 2건 TM-CHEL-01-FE, TM-CHEL-01-ZN 을 verified_reference 노출로 승인.
mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지
  (흡수 추론·confidence moderate·user 카피 영향 없음).
grouping 결정: FE/ZN 개별 카드 유지.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 철분·아연 보충 권유 없음.
```

> 승인 후 live 통합: `python3 scripts/integrate_penicillamine_subset_v1_3.py --pm-approved --reviewer-note <노트경로>`
> (별도 PM 승인 + 별도 PR 에서만. 본 세션은 실행하지 않음.) 회귀 = `scripts/test_penicillamine_reviewer_note_gate_v1_3.py`.

## 7. full-6 integrator 와의 관계 (충돌 주의)

- 이 subset 통합기와 full-6 통합기(`integrate_theme_map_draft_batch_v1_3.py`)는 **동시 사용 금지**(같은 후보 중복).
- subset 을 **먼저** 통합하면(60→62), 이후 나머지 4건(TM-LIP-01/02·TM-CEPH-AC-01/02)은 별도 PR 에서 통합.
  현행 full-6 통합기는 후보가 이미 live 면 STOP 하므로, subset-우선 경로에서는 full-6 통합기에 **나머지 4건만** 대상으로
  하는 `--only` 변형(next_prompts 프롬프트 12) 또는 idempotency skip 보강이 선행돼야 한다.
- id 는 runtime max+1 — subset 이 먼저면 나머지 4건은 64~67 로 자동 정합.
