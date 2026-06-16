# MediStack — Theme Map Grouping Strategy (v1.3)

> theme map 6건을 카드로 노출할 때 **묶음 vs 분리** 전략 정리. reviewer 결정용. live 통합·src 변경 없음.
> 연관: reviewer package `docs/MediStack_reviewer_package_theme_map_v1_3.md`, category 정책
> `docs/MediStack_counterpart_category_policy_v1_3.md`, dry-run `data/review/theme_map_live_dryrun_v1_3.json`.

## 1. 지용성 비타민 group — 단일 카드 vs 비타민별 분리

| | 그룹 단일 카드 (권고 기본) | 비타민별 분리 |
|---|---|---|
| 오르리스타트(TM-LIP-01) | 1 relation: 지용성 비타민(A·D·E·K·베타카로틴) | 4~5 relation: A/D/E/K(+베타카로틴) |
| 콜레스티라민(TM-LIP-02) | 1 relation: 지용성 비타민(A·D·K) | 3 relation: A/D/K |
| 장점 | 라벨 표현('지용성 비타민')에 충실 · 카드 수 적음 · 사용자 이해 단순 | 비타민별 검색 적중 ↑ |
| 위험 | 비타민별 검색 시 적중 약함 | 라벨이 개별 비타민을 분리 안 함 → **근거 초과 분해** 위험 · 카드 수 폭증 |
| relation_count 영향 | +2 | +7~8 |

→ **권고: 그룹 단일 카드 유지**(라벨 충실 + 근거 초과 분해 회피). 단, 검색 적중을 위해 alias/index 차원의
별칭 보강은 별도 검토(데이터 박지 않음). **reviewer 최종 결정.**

## 2. 세팔로스포린 acid-reducing drug 카드

| | 세프포독심(TM-CEPH-AC-01) | 세프디토렌(TM-CEPH-AC-02) |
|---|---|---|
| counterpart | 위산 감소·중화 약물(제산제·H2) | 제산제·위산 감소 약물(H2·PPI 등) |
| action | separation | **avoid_concomitant**(라벨 '권장되지 않는다') |
| category | **acid_reducing_drug** (둘 다) | |

- **개별 카드 권고**: 두 약물의 라벨 강도(separation vs avoid_concomitant)와 counterpart 범위(PPI 포함 여부)가 다름 →
  하나로 합치면 라벨 충실도 손실.
- **acid_reducing_drug category 채택 권고**(category 정책 §3): id61 al_mg_antacid 와 구분.
- ⚠️ TM-CEPH-AC-02 는 avoid_concomitant → live 통합 시 v0.2 validator #15 확장 선행조건(reviewer package §7).

## 3. 페니실라민 FE/ZN — 묶음 카드 vs 개별 카드

| | 개별 카드 (권고 기본) | 묶음(다중 영양소) 카드 |
|---|---|---|
| TM-CHEL-01-FE 철분 | 흡수율 저하 **직접 근거**('흡수율을 저하' 라벨 명시) | |
| TM-CHEL-01-ZN 아연 | '효과 감소' 표현 · **mechanism 추론**(absorption INFERRED) · confidence moderate | |
| 장점 | 근거 강도/confidence 차이를 카드별로 정직하게 표현 | 한 약물의 다중 상호작용을 한눈에 |
| 위험 | 같은 약물 카드 2장 | FE(직접근거)와 ZN(추론)을 **같은 강도로 오인** |

→ **권고: 개별 카드**(FE 직접근거 vs ZN 추론 강도 차이 보존). 아연 mechanism 은 reviewer 가
absorption vs interaction 확정(**user 카피는 '효과 감소'로 라벨 충실 — 영향 없음**). **reviewer 최종 결정.**

> **🟢 subset 우선 권고(2026-06-16)**: FE/ZN 2건은 **counterpart_category=null(일반 영양소) → live 선행조건 0**(현행 v0.2 PASS·src/facet/chip/validator 변경 불필요). theme map 6건 중 **가장 먼저 안전 통합 가능**. 전용 패키지 `docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md` · mechanism 결정(Option A=absorption 추론) `docs/MediStack_penicillamine_mechanism_decision_v1_3.md` · dry-run `data/review/penicillamine_subset_live_dryrun_v1_3.json`(60→62). 실행 = next_prompts 프롬프트 15. (지용성비타민·세팔로 4건은 src/validator 선행 PR=프롬프트 16 후.)

## 4. 카드 수 · relation_count 예상

| grouping 시나리오 | 신규 relation | live count |
|---|---|---|
| **권고**(지용성 그룹 단일 · 세팔로 개별 · 페니실라민 개별) | **6** | 60 → **66** (id 62~67) |
| 지용성 비타민별 분리 | 11~12 | 60 → 71~72 |

> AT-FEX/칼륨이 먼저 통합되면 신규 id 는 runtime max+1 로 자동 조정(dryrun integrator 가 계산).

## 5. reviewer 결정 필요사항 (요약)

1. 지용성 비타민: **그룹 단일**(권고) vs 비타민별 분리.
2. acid_reducing_drug category **채택**(권고) vs al_mg_antacid 통합.
3. 세팔로 2건 **개별 카드**(권고) 확인.
4. 페니실라민 FE/ZN **개별 카드**(권고) vs 묶음.
5. TM-CHEL-01-ZN mechanism 태그 absorption(권고) vs interaction.
6. 결정 → reviewer note(reviewer package §8) → 별도 PR live 통합.
