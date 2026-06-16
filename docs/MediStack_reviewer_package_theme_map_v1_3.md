# MediStack — Theme Map Expansion Reviewer Package (v1.3)

> **목적**: clinical reviewer / PM 이 theme map 신규 family **6건**을 단일 문서로 검토하고, live 통합 전
> 확인 질문에 답하며, 승인 note 를 작성할 수 있게 한다.
> **상태**: 6건 모두 **source_confirmed(식약처 nedrug 허가사항) · adversarial_verified(프롬프트 8) · harvester 편입(프롬프트 9)**.
> 현재 **live 통합 0** — review artifact / dry-run 상태. 본 패키지는 live 데이터를 바꾸지 않는다.
> **연관**: dry-run 산출물 `data/review/theme_map_live_dryrun_v1_3.json`, category 정책 `docs/MediStack_counterpart_category_policy_v1_3.md`,
> grouping 전략 `docs/MediStack_theme_map_grouping_strategy_v1_3.md`, draft `data/drafts/theme_map_draft_batch_v1_3.json`.

---

## 1. 범위

| 포함(검토 대상) | 제외 |
|---|---|
| theme map draft **6건**(아래 §3) | hold **7건**(미유통/임상판단/오인위험 — §6) |
| | 칼륨 PM-ready 4건 (별도 트랙) |
| | AT-FEX 펙소페나딘 (별도 트랙) |
| | 기존 live relation 60건 |

> **reviewer note ≠ clinical_reviewed=true**. 이 검토의 천장은 **verified_reference**(허가사항 출처 참고정보 노출)다.
> `clinical_reviewed`/`published` 전환은 clinical reviewer 확보 + 별도 버전에서만 (CLAUDE.md §1·§6).

## 2. 안전 원칙 (전 후보 공통)

- 진단·처방·치료·예방 아님. 복용 지시 아님. 보충제 추천 아님.
- 제품·구매·제휴·할인 UI/문구 없음 (`product_link_allowed=false`).
- source quote 는 **허가사항 원문**, app copy(display/management)는 그와 **분리된 비지시 참고 문구**.
- "식약처 승인 / 약사 검수 완료 / 법적 문제 없음" 류 표현 금지.
- 지용성 비타민·비타민 K 카드는 **항응고(와파린/INR) 맥락 금지** — 흡수 정보로만.
- 제산제·H2·PPI 약물 counterpart 는 **'약물'** 로 표기 — Mg 영양제로 오인 금지.

## 3. 후보별 상세 카드 (6건)

각 카드: relation · itemSeq · 대표 품목 · source quote(verbatim) · app copy · category · action/mechanism ·
evidence/confidence · adversarial verdict · remaining risks · reviewer 질문.

### TM-LIP-01 — 오르리스타트 × 지용성 비타민(A·D·E·K·베타카로틴)
- itemSeq **200806047** / 리피다운캡슐60밀리그램(오르리스타트) / 사용상 주의사항
- source quote: *"이 약에 의해 몇몇 지용성 비타민 및 베타카로틴의 흡수가 감소될 수 있으므로 … 비타민 보충제는 이 약 투여 최소 2시간 전 또는 취침 시와 같이 이 약 투여 최소 2시간 후에 복용해야 한다."*
- app copy(display): "일부 지용성 비타민(A·D·E·K)과 베타카로틴의 흡수를 줄일 수 있다는 허가사항 문구가 있습니다. … 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- counterpart_category: **fat_soluble_vitamin**(nutrient_group) · action **separation** · mechanism absorption
- evidence high · confidence high · adversarial **survives_with_copy_change**(source_quote 라벨 verbatim 정정 완료)
- remaining risk: 지용성 비타민군 **단일 카드 vs 비타민별 분리**(reviewer 결정).
- reviewer Q: (a) 그룹 단일 relation vs 분리? (b) 카피가 보충 '권유'로 읽히지 않는가(라벨은 권장하나 우리는 시점 분리만)?

### TM-LIP-02 — 콜레스티라민 × 지용성 비타민(A·D·K)
- itemSeq **198800813** / 보령퀘스트란현탁용산(콜레스티라민레진) / 상호작용
- source quote: *"이 약은 담즙산과 결합하므로 정상적인 지방의 소화와 흡수를 방해하여 비타민 A, D, K와 같은 지용성 비타민의 흡수를 저해할 수 있다…"*
- counterpart_category: **fat_soluble_vitamin** · action separation · mechanism absorption
- evidence high · confidence high · adversarial **survives** (콜레스티라민은 id57/58 source pointer 에 binder 로만 등장 — 역방향·무충돌)
- remaining risk: 엽산 라벨 미확인 → **A·D·K 한정 유지**(라벨에 없는 영양소 추가 금지).
- reviewer Q: (a) 비타민 K 가 항응고 맥락으로 오인되지 않는가? (b) 엽산 제외 유지 적절한가?

### TM-CEPH-AC-01 — 세프포독심프록세틸 × 위산 감소·중화 약물(제산제·H2 차단제)
- itemSeq **199300168** / 바난정(세프포독심프록세틸) / 상호작용
- source quote: *"위장 내의 pH를 올리게 되는 약물(제산제, H2-길항제)은 생체이용률을 떨어뜨리고…"*
- counterpart_category: **acid_reducing_drug**(antacid_drug, **약물**) · action separation · mechanism absorption(pH 의존)
- evidence high · confidence high · adversarial **survives**
- remaining risk: 라벨은 **PPI 미명시** → 여기엔 PPI 추가 금지(세프디토렌과 구분).
- reviewer Q: (a) category 를 id61(al_mg_antacid)과 통합 vs 신규 **acid_reducing_drug**? (b) counterpart 가 약물임이 분명한가(Mg 영양제 아님)?

### TM-CEPH-AC-02 — 세프디토렌피복실 × 제산제·위산 감소 약물(H2 차단제·PPI 등)
- itemSeq **199500901** / 보령메이액트정100밀리그램(세프디토렌피복실) / 상호작용
- source quote: *"이 약을 제산제나 위산을 감소시키는 다른 약물과 동시에 복용하는 것은 권장되지 않는다(이 약의 흡수가 감소되었다.)."*
- counterpart_category: **acid_reducing_drug**(약물) · action **avoid_concomitant**(라벨 '권장되지 않는다' verbatim) · mechanism absorption
- evidence high · confidence high · adversarial **survives_with_copy_change**(counterpart 를 PPI 포함 광의로 확장)
- remaining risk: 카르니틴 결핍 별도 주의는 본 relation 과 무관 — 혼입 금지.
- reviewer Q: (a) avoid_concomitant 톤이 과도하지 않은가? (b) counterpart PPI 포함 확장이 라벨 '위산을 감소시키는 다른 약물'에 충실한가?
- ⚠️ **live 선행조건**: 현행 v0.2 validator 검사 #15 가 avoid_concomitant 를 al_mg_antacid 로만 허용 → acid_reducing_drug 채택 시 validator 확장 필요(§7).

### TM-CHEL-01-FE — 페니실라민 × 철분
- itemSeq **198300142** / 알타민캡슐250밀리그램(디-페니실라민) / 상호작용
- source quote: *"경구철제제(구연산제일철나트륨, 황산철 등) … 는 이 약의 흡수율을 저하시켜 효과를 감소시킬 수 있으므로, 반드시 투여해야 하는 경우에는 동시투여를 피한다."*
- counterpart_category: **null**(일반 영양소 relation — 철분) · action separation · mechanism absorption('흡수율을 저하' 명시)
- evidence high · confidence high · adversarial **survives**
- remaining risk: 전문의약품·소량 유통 — 베타 노출 가치는 reviewer. 동일 라벨의 Al/Mg 제산제 각도는 risk_flag 로 분리(미확장).
- reviewer Q: (a) Al/Mg 제산제 각도를 antacid 트랙으로도 만들지? (b) 전문약·소량 유통이 베타 노출 가치에 맞는가?

### TM-CHEL-01-ZN — 페니실라민 × 아연
- itemSeq **198300142**(FE 와 동일 라벨) / 상호작용
- source quote: *"아연을 함유하는 경구제는 이 약의 효과를 감소시킬 수 있으므로, 반드시 병용해야 하는 경우에는 동시투여를 피한다."*
- counterpart_category: **null**(일반 영양소 — 아연) · action separation · mechanism absorption(**추론** — 라벨은 '효과 감소'만 명시)
- evidence high · confidence **moderate** · adversarial **survives_with_copy_change**(mechanism INFERRED flag·confidence high→moderate)
- remaining risk: mechanism 태그는 reviewer 가 absorption vs interaction 확정 — **user 카피는 '효과 감소'로 라벨 충실(영향 없음)**.
- reviewer Q: (a) FE 와 묶어 다중 영양소 카드로 노출할지? (b) mechanism 을 absorption 으로 둘지(라벨은 '효과 감소'만)?

## 4. category별 검토 질문

- **fat_soluble_vitamin** (TM-LIP-01/02): 영양소군(약물 아님). 비타민 K 항응고 맥락 0 확인. 그룹 단일 vs 분리(§grouping).
- **acid_reducing_drug** (TM-CEPH-AC-01/02): **신규 채택 여부**. id61 al_mg_antacid(cation chelation)와 구분(H2/PPI·pH 의존). '약물' 표기 확인.
- **null / 일반 영양소** (TM-CHEL-01-FE/ZN): 철분·아연 단일 영양소 relation. 보충 권유 0 확인. 아연 mechanism 태그 확정.

## 5. live integration readiness

| 후보 | 데이터 준비 | 현행 v0.2 validator | 비고 |
|---|---|---|---|
| TM-LIP-01/02 | ✅ | ✅ PASS(separation) | src facet: fat_soluble_vitamin 영양소 facet 포함 필요(§7) |
| TM-CEPH-AC-01 | ✅ | ✅ PASS(separation) | acid_reducing_drug chip/kicker src 필요(§7) |
| TM-CEPH-AC-02 | ✅ | ⚠️ #15 차단 | avoid_concomitant+acid_reducing_drug → validator #15 확장 필요(§7) |
| TM-CHEL-01-FE/ZN | ✅ | ✅ PASS(separation) | 일반 영양소 — src 변경 불필요 |

## 6. HOLD 7건 (검토 대상 아님 — 참고)

TM-CHEL-02(레보도파×철분, 복합제만 유통) · TM-LIP-03(콜레세벨람, 국내 미유통) · TM-CHEL-03(메틸도파, 미유통) ·
TM-B6-01(이소니아지드×B6, 이상반응 치료 지시 — depletion 아님) · TM-HOLD-PHENYTOIN(엽산 양방향·신경계 임상판단) ·
TM-HOLD-MYCO(이식 면역억제제) · TM-HOLD-LDOPA-B6(복합제서 상호작용 무력화 — 'B6 피하라'는 오정보).

## 7. live 통합 선행조건 (별도 PR · 이번 작업 범위 밖)

1. **[validator]** `scripts/validate_medistack_v0_2_export.py` 검사 #15: `avoid_concomitant ⇒ counterpart_category==al_mg_antacid` 를
   **acid_reducing_drug 포함**으로 확장(또는 reviewer 가 TM-CEPH-AC-02 를 separation 으로 하향).
2. **[src]** `src/js/guards.js` `getFacets`: 현재 `counterpart_category` 있는 relation 을 영양소 facet 에서 일괄 제외 →
   **fat_soluble_vitamin(영양소군)은 facet 포함**, **drug category(acid_reducing_drug·al_mg_antacid)만 제외**하도록 분기.
3. **[src]** `src/js/render.js`: **acid_reducing_drug 전용 chip/kicker**(제산제·H2/PPI 약물 표기) 추가
   (현재 avoid_concomitant chip 은 'Al/Mg 함유 제산제' 문구 고정).
4. **reviewer note**(§8) + 별도 PM 승인 + 별도 PR.

## 8. reviewer note 템플릿

> 아래 템플릿을 복사해 **꺾쇠 placeholder 를 실제 값으로 교체**한다. 미교체(`<…>`/`YYYY-MM-DD`)·`SAMPLE` 토큰이
> 남아 있으면 `integrate_theme_map_draft_batch_v1_3.py` 게이트가 **거부**한다(템플릿 그대로 제출 차단).
> 게이트가 강제하는 요건: 승인 토큰 · candidate_id **6건 전건** · category 결정(acid_reducing_drug·fat_soluble_vitamin) ·
> grouping 결정 · TM-CHEL-01-ZN mechanism 결정 · verified_reference 동의 · clinical_reviewed=true 아님 · 제품/보충 추천 아님.

```
검수자: <검수자 식별자>  검토일 <검토일 YYYY-MM-DD 를 실제 날짜로>
승인(approved): theme map 6건 TM-LIP-01, TM-LIP-02, TM-CEPH-AC-01, TM-CEPH-AC-02,
  TM-CHEL-01-FE, TM-CHEL-01-ZN 을 verified_reference 노출로 승인.
category 결정: acid_reducing_drug(세팔로 acid-reducer, al_mg_antacid 와 구분) 채택,
  fat_soluble_vitamin 그룹 채택.
grouping 결정: 지용성 비타민은 그룹 단일 카드 유지(또는 비타민별 분리),
  페니실라민 FE/ZN 은 개별 카드(또는 묶음 카드).
mechanism 결정: TM-CHEL-01-ZN 아연은 라벨 '효과 감소' 충실, 기전 태그 absorption 유지
  (또는 interaction 으로 조정) — user 카피 영향 없음.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴·보충제 추천 없음.
```

> 승인 후 live 통합: `python3 scripts/integrate_theme_map_draft_batch_v1_3.py --pm-approved --reviewer-note <노트경로>`
> (위 §7 선행조건 충족 + 별도 PM 승인 + 별도 PR 에서만. 본 세션은 실행하지 않음.)
