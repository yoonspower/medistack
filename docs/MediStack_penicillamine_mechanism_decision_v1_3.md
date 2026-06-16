# MediStack — Penicillamine × Zinc Mechanism Decision (TM-CHEL-01-ZN, v1.3)

> **결정 사항**: 페니실라민 × 아연 relation 의 `mechanism` 태그를 무엇으로 둘지. 라벨(itemSeq 198300142 알타민캡슐)은
> 아연에 대해 **'효과를 감소'** 만 명시(철분은 '흡수율을 저하' 명시). 즉 **흡수(absorption)는 추론**이다.
> 본 문서는 reviewer/PM 결정용이며 **실제 live 변경을 하지 않는다**. dry-run 은 Option A 를 채택해 산출.
> 연관: `data/review/penicillamine_subset_live_dryrun_v1_3.json` `meta.zn_mechanism_decision` · reviewer package §3·§4.

## 1. 라벨 근거 (verbatim)

- 철분(FE): *"경구철제제 … 는 이 약의 **흡수율을 저하**시켜 효과를 감소시킬 수 있으므로 … 동시투여를 피한다."*
- 아연(ZN): *"아연을 함유하는 경구제는 이 약의 **효과를 감소**시킬 수 있으므로 … 동시투여를 피한다."*

→ 상호작용·동시투여 회피 자체는 **둘 다 source-confirmed**. 차이는 ZN 라벨이 '흡수'를 명시하지 않는다는 점뿐.

## 2. 옵션 비교

| | **Option A (권고)** mechanism=absorption + 추론 flag | Option B mechanism=interaction/effect_reduction | Option C ZN → needs_review (FE만 통합) |
|---|---|---|---|
| source fidelity | 상호작용·시점분리 충실. 단 'absorption'은 추론(flag 로 표시) | 라벨 '효과 감소'에 가장 중립적·충실 | 가장 보수적(ZN 보류) |
| user copy 안전성 | user 카피는 **'효과 감소'** 그대로(absorption 단정 안 함) → 안전 | 동일하게 안전 | FE만 노출(ZN 미노출) |
| validator 영향 | **현행 v0.2 PASS**(ALLOWED_MECHANISM={absorption,depletion}) — 선행조건 0 | ❌ **interaction 은 ALLOWED_MECHANISM 밖** → v0.2 validator 확장 **선행 PR 필요** | FE만 PASS(현행) |
| live 통합 난이도 | 낮음(즉시 가능·subset 우선의 핵심 이점) | 높음(validator PR 선행) | 낮음(단 ZN 가치 상실) |
| relation consistency | 기존 absorption relation 군과 일관(FE 와 같은 mechanism) | 신규 mechanism 값 도입(렌더/facet/validator 파급) | FE 단독 |

## 3. 권고 결론 — **Option A**

- `mechanism = absorption`(추론) + `risk_flags` 에 INFERRED 표시 + `confidence = moderate`.
- **user-facing 카피는 라벨대로 '효과 감소'** 유지 — mechanism 태그는 내부 분류일 뿐 사용자에게 'absorption'을 단정하지 않음.
- 근거: ①현행 v0.2 validator 통과 → **subset 의 '선행조건 0' 이점을 보존**(Option B 는 validator 확장 PR 을 강제해 이점 상실).
  ②FE 와 같은 absorption 군으로 일관. ③불확실성은 metadata(risk_flags·confidence moderate·본 문서)에 정직하게 기록.
- reviewer 가 **interaction 으로 조정을 원할 경우**: Option B 로 전환하되 v0.2 validator `ALLOWED_MECHANISM` 에 'interaction'
  추가 + 렌더/facet 검토를 **별도 PR**로 선행해야 한다(이 경우 subset 의 '선행조건 0' 이점은 사라짐).

## 4. reviewer 질문

1. ZN mechanism 을 **absorption(추론·Option A, 권고)** 으로 둘지, interaction(Option B, validator PR 선행)으로 조정할지?
2. ZN 을 FE 와 함께 통합(권고)할지, 별도 needs_review(Option C)로 보류할지?
3. user 카피 '효과 감소'(absorption 단정 안 함)가 충분히 중립적인지?

> reviewer 결정은 reviewer note(reviewer package §6)에 'mechanism 결정' 줄로 명시 — 게이트가 강제.

## 5. reviewer 선택 체크박스

- [ ] **Option A (권고)** — mechanism=absorption(추론·inference_flag·confidence moderate), user 카피 '효과 감소' 유지. **선행조건 0**(현행 v0.2 PASS).
- [ ] Option B — mechanism=interaction. ⚠️ v0.2 `ALLOWED_MECHANISM={absorption,depletion}` 밖 → **validator 확장 PR 선행**(렌더/facet 파급) 후에만. subset 의 '선행조건 0' 이점 상실.
- [ ] Option C — ZN → needs_review 보류, FE 만 통합(60→61·id 62). ZN 가치 상실.

> 기본 채택 = **Option A**(dry-run·통합기 `ZN_MECHANISM_DECISION` 에 고정). B/C 를 원하면 reviewer note 에 명시하고 별도 절차(B 는 validator PR 선행).
