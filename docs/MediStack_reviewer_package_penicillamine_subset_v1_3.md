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

**통합 전 마지막 금지사항(게이트가 거부 — note 에 쓰지 말 것)**
- `SAMPLE`/`샘플`/`PLACEHOLDER`/`NOT-VALID` 등 예시 토큰이 남으면 **절대 통과 안 됨** — 템플릿 그대로 제출 금지.
- `<…>`/`YYYY-MM-DD` 등 미교체 placeholder 가 남으면 거부.
- `clinical_reviewed=true`/`published=true` 승격 요구·"약사 검수 완료"·"식약처 승인" 단정 → 거부(천장 = verified_reference).
- "제품 추천 허용"·"구매/제휴 링크 추가" → 거부.
- "철분/아연 보충 권장/권유/복용하세요" → 거부. **복용 지시('복용하세요/피하세요/반드시')는 app copy 에도 금지.**

## 7. full-6 integrator 와의 관계 (충돌 주의)

- 이 subset 통합기와 full-6 통합기(`integrate_theme_map_draft_batch_v1_3.py`)는 **동시 사용 금지**(같은 후보 중복).
- subset 을 **먼저** 통합하면(60→62), 이후 나머지 4건(TM-LIP-01/02·TM-CEPH-AC-01/02)은 별도 PR 에서 통합.
  현행 full-6 통합기는 후보가 이미 live 면 STOP 하므로, subset-우선 경로에서는 full-6 통합기에 **나머지 4건만** 대상으로
  하는 `--only` 변형(next_prompts 프롬프트 16) 또는 idempotency skip 보강이 선행돼야 한다.
- id 는 runtime max+1 — subset 이 먼저면 나머지 4건은 64~67 로 자동 정합.
- **중복 생성 불가(실증)**: full-6 `build_projected` 는 `(ingredient, nutrient)` 가 이미 live 면 violation 을 쌓고
  `main()` 이 STOP 한다(2026-06-16 검증: FE/ZN 이 live 인 temp export 에 full-6 build → `TM-CHEL-01-FE/ZN: 이미 live 에 존재`
  2건 → STOP). 즉 subset 통합 후 full-6 를 **naive 재실행하면 전체 STOP**(중복 0). 나머지 4건만 통합하려면 `--only` 가 **선행 필수**.

---

## 8. reviewer 결정 체크리스트

> reviewer note 작성 전, 아래를 결정한다(게이트가 강제하는 항목 표시). 미결정 항목이 있으면 note 게이트가 거부한다.

- [ ] **TM-CHEL-01-FE 페니실라민×철분 live 후보 승인**(verified_reference 노출) — *게이트: candidate_id 필수*
- [ ] **TM-CHEL-01-ZN 페니실라민×아연 live 후보 승인**(verified_reference 노출) — *게이트: candidate_id 필수*
- [ ] **ZN mechanism = Option A(absorption 추론·confidence moderate·user 카피 '효과 감소' 충실)** 승인 — *게이트: 'mechanism/기전' 줄 필수* (상세 = mechanism 결정 문서 §3)
- [ ] **FE/ZN 개별 카드 유지**(묶음 카드 아님) — *게이트: 'grouping 결정/개별 카드' 줄 필수*
- [ ] **verified_reference 수준 노출**(= clinical_reviewed=true 아님) — *게이트: 'verified_reference' + 'clinical_reviewed=true 아님' 필수*
- [ ] **제품·구매·제휴 추천 아님 / 철분·아연 보충 권유 아님** 확인 — *게이트: 해당 부정 문구 필수 + 허용 문구 거부*
- [ ] reviewer 식별자(RPH-…) 또는 PM 승인 근거 기재

## 9. PM decision table (부분 승인 포함)

> id 는 runtime max+1. **단건 승인 시 그 단건이 id 62 를 차지**(both 일 때만 FE=62·ZN=63). dry-run artifact
> `meta.partial_approval_scenarios` 가 동일 값을 기계검증(validator).

| 결정 | included | expected count | expected ids | validator 영향 | 권고 |
|---|---|---|---|---|---|
| **approve both** | FE + ZN | 60 → **62** | **62, 63** | 현행 v0.2 PASS(선행조건 0) | ✅ **권고** |
| approve FE only | FE | 60 → 61 | **62**(max+1) | 현행 v0.2 PASS | ZN 보류 사유 있을 때 |
| approve ZN only | ZN | 60 → 61 | **62**(max+1, 63 아님) | 현행 v0.2 PASS | ⚠️ 비권장(FE 가 더 확실) |
| hold ZN (= FE only) | FE | 60 → 61 | 62 | — | ZN needs_review 유지 |
| reject subset | — | 60 → 60 | (없음) | 변화 없음 | live 0 |

- **현행 통합기는 both-approval 전제**(게이트가 FE/ZN 2건·grouping 강제). 부분 승인이 실제 결정되면 **별도 `--only` 변형(dry-run 우선)**
  PR 이 필요하며, 본 라운드에서 `--only` 인자는 STOP 처리(미구현)된다. 부분 승인 시나리오 수치는 문서/artifact 로만 제공.

## 10. 부분 승인 — FE-only / ZN-only 판단 근거

- **FE-only**: ZN 라벨 근거('효과 감소'·absorption 추론)가 reviewer 판단에 부족하면 ZN 을 needs_review 로 보류하고 FE 만 노출. 안전(FE 는 '흡수율 저하' 직접근거).
- **ZN-only**: FE 를 빼고 ZN 만 노출할 실익은 낮다(FE 가 더 확실한 근거인데 제외할 사유가 통상 없음). reviewer 가 FE 특정 위험(예: 전문약 맥락)을 별도 보류할 때만. **권장하지 않음**.
- **both(권고)**: 둘 다 source-confirmed + 동일 라벨(198300142) + 동일 separation 안내. 일관성·완결성에서 both 가 최선.
- **neither**: subset 전체 reject → live 0. 차후 재검토.

## 11. 통합 후 rollback / post-live 검증 절차 (다음 단계용 — 본 세션 미실행)

**rollback 원칙**
- merge **전**(작업 브랜치): `git reset --hard <통합 직전 SHA>` 또는 브랜치 폐기.
- merge **후**(main): `git revert <통합 commit>` (export 되돌림) → v0.2 validator 재검증 → push.
- export 에서 relation id 62/63 제거 시 `meta.relation_count` 동기화 + v0.2 validator 재실행 **필수**(count 불일치 시 배포 게이트 FAIL).
- full index/aliases 는 무관(subset 은 변경 안 함) — rollback 시에도 건드리지 않는다.

**post-live 검증(통합 직후)**
- relations **62** · 신규 id **62, 63** · `meta.relation_count==62`
- published=false · clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 UI 0
- live HTTP 200 · data HTTP 200 · forbidden phrase 0 · smoke 9종 PASS
- App copy: 철분/아연 **보충 권유 없음** · source quote ↔ app copy 분리 · 제품/구매/제휴 없음 · 상담 톤('약사 또는 의사')
- counterpart_category 키 부재(일반 영양소) · separation chip '복용 간격' 정상 렌더
