# MediStack relation factory — 설계 (v1.2)

> 상태: **설계 + 후보 큐만**. 라이브 데이터(relation export / full index / aliases / src / .github / validator) **무수정**.
> 이 문서가 정의하는 것: 후보 → 통합까지의 파이프라인, impact/risk 스코어링, source-policy 게이트.
> 이 문서가 **하지 않는 것**: relation 생성, source_confirmed 승격, published/clinical 전환, 통합.
> 모든 후보 `do_not_implement_yet=true`. 통합은 PM 승인 + source 확인 후 **별도 단계**.

관련 산출물:
- `scripts/harvest_relation_candidates.py` — 읽기 전용 harvest 스크립트.
- `data/candidates/relation_factory_candidates_input_v1_2.json` — 후보 제안 입력(이 라운드 75건).
- `data/relation_factory_candidates_v1_2.csv` — harvest 출력(counts·impact·risk 부착, 75행).
- `docs/MediStack_relation_factory_candidates_v1_2.md` — 후보 요약 리포트.

---

## 0. 왜 factory 인가

라운드별 후보를 즉흥 처리하면 (1) 같은 성분 중복 후보화, (2) 근거 약한 계열 일반화,
(3) source 미확인 채로 통합되는 사고가 난다. factory 는 그걸 **고정된 게이트 파이프라인**으로 막는다.
핵심 불변식: **harvest 는 데이터를 한 줄도 바꾸지 않는다(읽기 매칭만)**, 그리고
**source_status 는 후보가 들고온 값을 그대로 보존하고 어떤 후보도 자동으로 `source_confirmed`가 되지 않는다.**

---

## 1. 파이프라인 (7 단계)

```
[1] harvest      후보 제안(JSON) → full index/seed 매칭 → counts 부착 → 후보 CSV
                 (읽기 전용. 데이터 무변경. 이 스크립트가 담당하는 유일한 단계)
        │
[2] count        matched_item_count / name_only_item_count / popular_seed_match_count
                 → estimated_card_impact (name_only 기반 휴리스틱 등급)
        │
[3] risk score   risk_level + caution_flags + 민감군/방향성 게이트 → 통과/hold 분리
        │
[4] source queue source_priority(P1>P2>P3>hold)별 source-check 큐 작성
                 (허가사항 동거어 fetch 작업 목록. 이차문헌은 source-policy 미정)
        │
[5] PM 승인      PM 이 source-check 결과 + impact/risk 보고 검토 → 승격 여부 결정
                 (factory 는 결정하지 않는다. 권고만 한다)
        │
[6] draft        승인된 후보만 relation_expansion_draft 로 작성
                 (published=false, clinical_reviewed=false, do_not_implement_yet=true)
        │
[7] 통합         별도 integrate 스크립트 + validator PASS + CI 전체셋 → 라이브
                 (이 문서/이 라운드 범위 밖)
```

**이 라운드는 [1]~[4] 까지만.** [5] 이후는 PM 의 별도 지시가 있어야 진입한다.

---

## 2. counts 정의 (단계 [2])

harvest 는 `ingredient_or_class` 를 full index 의 `ingredient_name` 에 **부분문자열(substring)** 매칭한다.
복합제(예: `로수바스타틴/에제티미브`)도 잡기 위해 substring 을 쓴다. exact 매칭은 복합제를 놓친다.

| 필드 | 정의 | 해석 |
|---|---|---|
| `matched_item_count` | `ingredient_name` 에 후보 성분 문자열이 포함된 **전체** 품목 수 | 그 성분이 index 에 얼마나 깔려 있나 |
| `name_only_item_count` | 그 중 `display_mode == name_only` 인 품목 수 | **신규 relation 으로 새로 커버될 잠재 품목 수** |
| `popular_seed_match_count` | seed `query_name` 과 부분문자열로 겹치는 seed 수(양방향) | 대중 인지도 신호(검색량 아님) |

핵심: `matched > 0` 인데 `name_only == 0` 이면 **이미 relation_card 로 covered** 된 성분이다
(예: `D-THZ-06` HCTZ×Ca 113건 전부 relation_card, `F-CEPH-IDX-01` 세프디니르 8건 전부 covered).
이런 후보는 신규 relation 가치가 0 → hold 가 정당하다.
`matched == 0` 이면 그 성분명이 index 에 아예 없다(국내 미유통이거나 성분 표기 불일치) → 국내 품목 존재 확인이 선행 과제.

### estimated_card_impact 등급 (name_only 기반 휴리스틱)
| 등급 | name_only_item_count |
|---|---|
| `very_high(n)` | ≥ 200 |
| `high(n)` | 50–199 |
| `medium(n)` | 10–49 |
| `low(n)` | 1–9 |
| `none(0)` | 0 (신규 커버 없음 — 이미 covered 거나 index 부재) |

> 이 등급은 **잠재 품목 수**일 뿐, "이 relation 을 만들어야 한다"는 뜻이 아니다.
> impact 가 높아도 source/risk 게이트를 통과하지 못하면 hold 다(§3, §4 참조).

---

## 3. risk 스코어링 (단계 [3])

risk 는 **두 축**으로 본다. 둘 중 하나라도 걸리면 통과 못 한다(fail-closed).

### 3.1 risk_level (후보가 들고온 분류, 보존)
- `low` — 흡수 상호작용(다가양이온 킬레이션 등). 칼륨카드 불필요.
- `moderate` — 전해질 고갈(칼륨/Mg), 코르티코스테로이드 대사. 칼륨 행은 `potassium_safety_card` 승계 필요.
- `high` — 항응고/항혈소판, 항암, 정신건강/임신/소아 민감군, 허브 광범위 상호작용, 칼륨 상승(고칼륨혈증) 방향.

### 3.2 caution_flags (자동 hold 트리거)
다음 플래그가 있으면 **impact 와 무관하게 hold**:
- `permanent_ban_claudemd` — 와파린×비타민K 등 CLAUDE.md 영구 금지.
- `anticoagulant` / `antiplatelet` / `bleeding_risk` — 출혈·임상판단 영역.
- `oncology` / `mental_health_sensitive` / `womens_health_sensitive` / `pediatric_sensitive` — 민감군.
- `out_of_beta_scope` — 허브-약물, 약-약 상호작용(영양소 고갈 아님).
- 방향성 충돌: `expected_relation_direction ∈ {unknown(상승), antagonism}` 이면서 depletion 테마와 반대
  (K-sparing 고칼륨혈증, HCTZ 칼슘 retention) — depletion factory 범위 밖, hold.

### 3.3 risk → 게이트 결과
| 조건 | 결과 |
|---|---|
| risk_level=high **또는** 위 hold 플래그 1개 이상 | **hold** (source-check 금지/보류) |
| risk_level ∈ {low, moderate} **그리고** hold 플래그 없음 | source-check 큐 진입 가능(P2/P3) |
| 칼륨(depletion) 후보 | 승격 시 `potassium_safety_card=true` + 제품링크 금지 승계 **필수** |

---

## 4. source-policy 게이트 (단계 [4]→[5] 사이, 가장 중요)

MediStack 베타의 source 천장은 **식약처 허가사항(nedrug getItemDetail) 원문 동거어**다.
이차문헌(임상 가이드라인·메타분석)은 **현재 정책 미정** → 이차문헌만 근거인 후보는 통합 대상이 아니다.

| source_status | 의미 | 게이트 |
|---|---|---|
| `needs_source` | 허가사항 fetch 미수행. 동거어 있을 가능성 | fetch 작업 큐 진입 |
| `source_check_needed` | 인접 relation 존재(enrichment) 또는 동거 가능성. 직접 동거어 미확인 | fetch 후 동거어 있으면만 진행 |
| `candidate_only` | 허가사항 근거 약함/없음(literature_only) **또는** 범위 밖/민감군 | **source-policy 결정 전 hold** |
| `source_confirmed` | (이 라운드에 **0건**. 자동 승격 절대 금지) | PM + 허가사항 원문 확인 후에만 |

핵심 규칙:
1. **harvest 는 status 를 바꾸지 않는다.** 후보가 `candidate_only` 면 출력도 `candidate_only`.
2. 허가사항에 **동거어가 없으면** → 그 후보는 `reject` 기록(계열 일반화로 채워넣지 않는다).
   특히 세팔로스포린 철 킬레이션은 세프디니르(id42)만 확정 — 나머지는 성분별 직접 확인, 없으면 reject.
3. **이차문헌만 근거**(스타틴×CoQ10, H2×B12 등)는 source-policy 결정 전 **전부 hold**.
   impact 가 아무리 커도(스타틴 name_only 합 1,015) 게이트를 못 넘는다.
4. 민감군·항응고·항암·허브·약-약 상호작용은 **factory 범위 밖** → source-check 자체를 하지 않는다(분류 보관만).

---

## 5. PM 권고 형식 (단계 [5] 입력)

factory 는 PM 에게 다음만 전달한다(결정은 PM):
- source-check 우선순위 큐 (P2 → P3, name_only desc).
- 각 후보의 impact(name_only·seed)·risk·source_status·예상 결과(동거어 있음/없음 예측).
- hold 사유(범위 밖 / 근거 약함 / 방향 반대 / 이미 covered).

PM 이 "이 P2 묶음 source-check 진행" 또는 "draft 승격"을 지시하기 전까지 [6] 진입 금지.

---

## 6. 무결성 불변식 (harvest 스크립트가 강제)

스크립트는 다음 중 하나라도 깨지면 **exit 1 (STOP)**:
- full index 수치 ≠ (total 17,580 / relation_card 1,077 / name_only 16,503) → 데이터 오염/변형 의심, 매칭 중단.
- 어떤 후보 `source_status == source_confirmed` → 자동 승격 금지 위반.
- 어떤 후보 `source_status` 가 허용셋{needs_source, candidate_only, source_check_needed} 밖.
- 어떤 출력 행 `do_not_implement_yet != true`.

스크립트는 보호 데이터 파일을 **열어서 읽기만** 하고 절대 쓰지 않는다.
출력은 `data/relation_factory_candidates_v1_2.csv` 한 파일뿐.
