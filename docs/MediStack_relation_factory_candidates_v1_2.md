# MediStack relation factory — 후보 요약 리포트 (v1.2)

> 출처: `data/relation_factory_candidates_v1_2.csv` (75행, harvest 자동 생성).
> 생성: `scripts/harvest_relation_candidates.py` (읽기 전용. 라이브 데이터 무수정).
> **전건 `do_not_implement_yet=true` · `source_confirmed` 0건 · 통합 0건.** PM 승인 + source 확인 전까지 hold.
> 설계: `docs/MediStack_relation_factory_design_v1_2.md`.

## 0. 한눈에

- 후보 **75건**.
- source_status: `needs_source` 26 · `candidate_only` 41 · `source_check_needed` 8 · `source_confirmed` **0**.
- source_priority: **P2 13 · P3 18 · hold 44**.
- risk_level: low 26 · moderate 24 · high 25.
- 핵심 신호: **impact 가 가장 큰 테마(스타틴×CoQ10·항응고/항혈소판·정신건강)는 전부 hold** —
  근거가 이차문헌이거나(허가사항 missing) 민감군/영구금지라 게이트를 못 넘는다.
  반대로 **source-check 가 실제 가치 있는 in-scope 후보는 코르티코스테로이드 칼륨/칼슘 + 세팔로스포린×철** 묶음이다.

---

## 1. 테마별 집계 (name_only 합 내림차순)

| 테마 family | 건수 | name_only 합 | P2 | P3 | hold | high_risk | 비고 |
|---|---:|---:|---:|---:|---:|---:|---|
| STATIN×CoQ10 | 5 | 1,015 | 0 | 0 | 5 | 0 | 이차문헌만 — source-policy 미정, 전건 hold |
| 항응고/항혈소판(영구금지) | 8 | 533 | 0 | 0 | 8 | 8 | 출혈·임상판단 — factory 범위 밖, 분류 보관 |
| CORTICOSTEROID | 7 | 402 | 3 | 4 | 0 | 0 | **in-scope 최우선**(칼륨/칼슘 허가사항 동거어) |
| 정신건강/민감군 | 7 | 306 | 0 | 0 | 7 | 7 | clinical reviewer 트랙 — 범위 밖 |
| CEPH(세팔로스포린×철) | 10 | 304 | 3 | 5 | 2 | 0 | 성분별 동거어 확인 필수(계열 일반화 금지) |
| SGLT2 | 2 | 303 | 0 | 0 | 2 | 0 | Mg 방향성 상승 보고 우세 — depletion 부적합 가능 |
| H2×B12 | 3 | 214 | 0 | 0 | 3 | 0 | A티어 허가사항 missing 확정 — hold |
| 항암(고위험) | 3 | 14 | 0 | 0 | 3 | 3 | clinical reviewer 전 대상 아님 |
| PPI 잔여(일라프라졸) | 2 | 4 | 0 | 0 | 2 | 0 | index 2품목뿐 — 한계효용 낮음 |
| 테트라사이클린 | 1 | 1 | 0 | 0 | 1 | 0 | index 1품목 — near-zero coverage |
| CARBONIC-ANHYDRASE | 1 | 0 | 1 | 0 | 0 | 0 | 아세타졸아미드 — index 부재, 국내 품목 확인 선행 |
| LOOP 잔여 | 5 | 0 | 2 | 3 | 0 | 0 | 전부 index 부재 — 국내 itemSeq 확인 선행 |
| THIAZIDE 잔여 | 6 | 0 | 2 | 3 | 1 | 0 | 전부 index 부재(메토라존 등) — 국내 품목 확인 선행 |
| FQ/갑상선 enrichment | 2 | 0 | 2 | 0 | 0 | 0 | 신규 커버 0(이미 covered) — 동거어 확인 시 enrichment만 |
| THYROID(T3 등) | 3 | 0 | 0 | 3 | 0 | 0 | 리오티로닌 국내 유통 불확실 |
| BIGUANIDE 잔여 | 1 | 0 | 0 | 0 | 1 | 0 | 부포르민 국내 미유통 가능 |
| CEPH(index-track) | 1 | 0 | 0 | 0 | 1 | 0 | 세프디니르 — relation 트랙 아님(alias 충실도) |
| 허브(범위 밖) | 3 | 0 | 0 | 0 | 3 | 2 | 베타 범위 밖 |
| K-sparing(상승방향) | 4 | 0 | 0 | 0 | 4 | 4 | 칼륨 상승 — depletion 반대, 범위 밖 |
| 약-약 상호작용(범위 밖) | 1 | 0 | 0 | 0 | 1 | 1 | 영양소 고갈 아님 |

> name_only 합이 큰 상위 3개(STATIN·항응고·정신건강)가 전부 hold 인 게 핵심이다.
> **impact 와 채택 가능성은 별개** — impact 만 보고 통합하면 안 된다.

---

## 2. Top 후보 (source-check 가 실제 가치 있는 in-scope, name_only desc)

P2 이면서 신규 커버(name_only)가 큰 후보. 이게 source-check 의 1차 대상이다.

| candidate_id | 성분 × 영양소 | name_only | seed | source_status | risk | 비고 |
|---|---|---:|---:|---|---|---|
| F-CEPH-01 | 세파클러 × 철분 | 135 | 1 | needs_source | low | 세팔로스포린 중 index 최대. 동거어 없으면 reject |
| D-CORT-01 | 프레드니솔론 × 칼륨 | 117 | 0 | needs_source | moderate | 칼륨카드 승계 필요. 용량/기간 맥락 확인 |
| D-CORT-02 | 프레드니솔론 × 칼슘 | 117 | 0 | candidate_only | moderate | 골대사 직접 문구 약할 수 있음 → literature 강등 가능 |
| D-CORT-03 | 메틸프레드니솔론 × 칼륨 | 73 | 0 | needs_source | moderate | 프레드니솔론과 동일 패턴 |
| F-CEPH-02 | 세푸록심 × 철분 | 39 | 0 | needs_source | low | 제산제/철 동거어 개별 확인 |
| F-CEPH-03 | 세프포독심 × 철분 | 39 | 0 | needs_source | low | 위산 의존 흡수 — 제산제 언급 가능 |

> 주의: `D-CORT-02`(프레드니솔론×칼슘)는 "처방약 부작용을 보충제 정보로 오인 금지" 플래그가 붙은 후보다.
> 골다공증 예방 주장·복용지시 어휘 금지. 허가사항 직접 문구 없으면 literature_only 강등 → hold.

---

## 3. hold 분리 (사유별)

`hold` 44건 = source-check 자체를 보류/금지하는 후보. impact 와 무관하게 게이트에서 막힌다.

| hold 사유 | 대표 후보 | 처리 |
|---|---|---|
| **영구 금지(CLAUDE.md)** | F-WAR-01 와파린×K | 후보화·source 확인 영구 금지 |
| **항응고/항혈소판(출혈·임상판단)** | F-DOAC-01~04, F-APL-01~03 | clinical reviewer 트랙. 분류 보관만 |
| **항암(고위험·개인차)** | F-ONC-01~03 | clinical reviewer 확보 전 대상 아님 |
| **정신건강/임신/소아 민감군** | F-SSRI/F-BZD/F-AP/F-OC/F-PED | clinical reviewer 트랙에서만 |
| **이차문헌만(허가사항 missing)** | F-STA-01~05, F-H2-01~03 | source-policy(이차문헌 허용) 결정 전 hold |
| **방향 반대(상승/고칼륨혈증)** | H-KSPAR-01~04, D-THZ-06 | depletion factory 범위 밖. 혼동 방지 기록 |
| **약-약 상호작용(영양소 고갈 아님)** | H-WARN-01 | 별도 트랙 여부 PM 결정 |
| **허브-약물(범위 밖)** | F-HERB-01~03 | 베타 범위 밖 |
| **방향성 불명확(Mg 상승 우세)** | D-SGLT2-01~02 | 방향 재확인 — 상승이면 폐기 |
| **near-zero coverage / 미유통** | F-TET-01, F-PPI-01~02, D-BIG-01, F-CEPH-09/10 | 한계효용 낮음 |
| **이미 covered(신규 0)** | F-CEPH-IDX-01 세프디니르 | relation 트랙 아님(alias 충실도 별도) |

---

## 4. 다음 source-check 우선순위 (P1/P2/P3)

> P1 없음(영구금지/임상판단 후보는 hold 로 분리). 실제 진행 순서는 **P2 → P3**.
> 단, PM 이 "이 묶음 진행" 지시 전까지 fetch 금지.

### P1 — 없음
영양소 고갈 high-confidence 이면서 즉시 진행 후보는 이번 라운드에 없다(전부 source-check 또는 hold 필요).

### P2 (13건) — 1차 source-check 대상
두 갈래:
1. **신규 커버 큰 묶음(허가사항 fetch 가치 높음)**: `F-CEPH-01`(세파클러, no=135), `D-CORT-01/02/03`(코르티코스테로이드 칼륨/칼슘, no=117/117/73), `F-CEPH-02/03`(세푸록심·세프포독심, no=39).
   → 허가사항 동거어 확인 → 있으면 draft 승격 후보, 없으면 reject.
2. **국내 품목 존재 확인 선행(index 부재, no=0)**: `D-THZ-01`(메토라존), `D-THZ-03`(트리클로르메티아지드), `D-LOOP-01`(부메타니드), `D-LOOP-04`(아조세미드), `D-CA-01`(아세타졸아미드).
   → itemSeq 존재 확인이 먼저. 품목 없으면 hold 전환.
   `F-FQ-01/02`(목시플록사신×칼슘·레보티록신×Mg)는 enrichment(신규 0) — 동거어 있으면만 기존 relation 보강.

### P3 (18건) — 2차
- 세팔로스포린 중간 묶음: `F-CEPH-04/05/06`(세프프로질·세픽심·세프라딘, no=32/26/16).
- 코르티코스테로이드 잔여: `D-CORT-04`(덱사메타손, 저칼륨 약함 확인), `D-CORT-05`(하이드로코르티손 전신만), `D-CORT-07`(메틸프레드니솔론×칼슘), `D-CORT-06`(플루드로코르티손).
- 이뇨제 잔여 Mg/품목확인: `D-THZ-02/04`, `D-LOOP-02/03/05`, `D-THZ-05`.
- 갑상선 잔여: `D-THY-01`(레보티록신×아연 — Mg reject 전례, 없으면 reject), `D-THY-02/03`(리오티로닌 국내 유통 확인).
- 세팔로스포린 소수: `F-CEPH-07/08`(세프카펜·세프디토렌).

### hold (44건) — source-check 금지/보류
§3 표 참조. PM 정책 결정(이차문헌 허용 여부 / 상승방향 포함 여부 / clinical reviewer 확보) 전까지 진입 불가.

---

## 5. 검증 결과

- CSV 행수: **75** (헤더 제외).
- `source_confirmed`: **0건** (전부 needs_source/candidate_only/source_check_needed).
- `do_not_implement_yet`: **75/75 = true**.
- 라이브 데이터(full index/export/aliases/src/.github/validator): **무수정**(harvest 읽기 매칭만, full index 수치 17,580/1,077/16,503 무결성 통과).
- 통합: **0건**(PM 승인 대기).
