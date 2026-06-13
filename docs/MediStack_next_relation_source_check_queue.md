# MediStack — 다음 relation 확장 source 확인 큐 v1.1

> 작성일: 2026-06-14. **읽기/문서화 전용(데이터 무변경).** A티어 source_confirmed 7후보(구 E01–E06·E08)가 라이브 통합되어 **relations=41(ids ~42)·relation_card=1072** 가 된 이후 상태에서, **다음에 허가사항 출처를 확인할 향후 확장 후보를 우선순위로 큐잉**한다.
>
> ⚠️ **본 단계는 큐(미래 source 확인 대상) 작성뿐이다.** relation 추가·수정·flip·구현 없음. **relations 는 41 로 그대로이며, 어떤 후보도 지금 구현하지 않는다.** 전건 `do_not_implement_yet=true`. 어떤 후보도 `source_confirmed` 로 표시하지 않는다(전부 "향후 확인 대기"). 품질이 모호하면 승격하지 않고 `needs_review`/`hold` 로 둔다.
>
> source 확인 방법(승계): `verify_atier_relation_sources.py` 패턴 — 후보 성분별 단일성분 대표 2~3품목 nedrug `getItemDetail` fetch → 테마 신호어 검색 → `source_confirmed/needs_review/missing/reject`. **허가사항 우선 gate**(문헌만 있으면 미채택, H2×B12 선례).

---

## 0. 한 줄 결론

**쉬운 고가치 후보(PPI·비스포·세프디니르 7건)는 이미 라이브 통합 완료(relations 41).** 남은 향후 후보는 (가) **enrichment(기존 covered 품목에 nutrient 테마만 추가·신규 card 0)**, (나) **계열 일반화 위험(세팔로스포린 class)**, (다) **칼륨 안전정책 선행 필요(치아지드유사)**, (라) **고가치이나 허가사항 미기재 예상(스타틴×CoQ10)**, (마) **고위험·영구 보류(항응고·항암·임신/소아/정신건강)** 으로 갈린다. → **진짜 다음 레버는 개별 후보가 아니라 "이차문헌 출처 허용 여부" source-policy 결정**(스타틴 944건 + H2 202건이 전부 여기 걸림). 그 전까지 안전한 진입은 enrichment(P1)뿐.

---

## 1. 큐의 목적 (무엇이고 무엇이 아닌가)

- **이것은:** 향후 relation_card 확장을 위해 **허가사항 출처를 확인할 후보 목록**과 그 우선순위. source 확인 자체도 아직 안 했고, 확인 결과(통과/미통과)도 미정이다.
- **이것이 아닌 것:** 구현 지시가 아니다. "이 관계가 사실이다"라는 단정이 아니다. relation/full index/alias/export/src 변경이 아니다. `source_confirmed` 표시가 아니다.
- 모든 nutrient 테마는 **가설(미확정)** 이다. 실제 채택은 허가사항 확인 + 검토 통과 + PM 승인 후 별도 단계에서만 일어난다.

---

## 2. 후보 그룹과 점수 근거 — `data/next_relation_source_check_queue_v1_1.csv`

점수: `user_value_score`/`source_availability_score` 는 1–5(보수적), `risk_level ∈ {low, moderate, high}`, `source_check_priority ∈ {P1, P2, P3, hold}`. 품질 판정은 `current_status` 에 담는다 — `source_check_queue`(향후 확인 대상) / `needs_review`(모호·단독 채택 금지) / `high_risk_hold`(안전정책상 비대상). `likely_source_type` 은 가능하면 식약처 허가사항(첨부문서)/nedrug 를 참조한다. `expected_card_impact` 는 채택 시 새로 카드가 붙을 추정 품목 수(enrichment 는 0).

### 그룹 A — enrichment / 인덱스트랙 (source 확실·안전·신규 card 거의 0) — **P1 우선**

| 큐 | 테마 | nutrient | card 임팩트 | 근거 |
|---|---|---|---|---|
| **Q01** | 에스오메프라졸 (PPI x B12/Mg 추가) | B12·Mg | index_only(relation16 존재·카드0) | relation16 이미 존재하나 alias 미부여로 매핑 0. 막힌 건 **relation 신설이 아니라 full index/alias 확장 트랙**. PPI 계열 동거 신호 강함. |
| **Q06** | 플루오로퀴놀론 x 아연 | 아연 | 0(enrichment) | 기존 퀴놀론 relation 이 이미 '다가양이온(칼슘·철·Mg)' 라벨 인용 → 아연 동일 문장 동거 가능성 매우 높음. 톤 안전. |
| **Q07** | 테트라사이클린 x 아연 | 아연 | 0(enrichment) | 독시/미노사이클린 동일 다가양이온 패턴. 아연 동거 가능성 높음. |
| **Q04** | 비스포스포네이트 x 철/Mg (기존성분) | 철·Mg | 0(enrichment) | 현재 비스포는 칼슘 단독. 허가사항이 다가양이온 함께 간격 권고 → 철·Mg 동거 신호 가능. |
| **Q08** | 레보티록신 x Mg (기존성분) | Mg | 0(enrichment) | relation10·11(칼슘·철) 존재 → Mg 제산제 문맥 동거 가능. |

> 그룹 A 는 **source gate 통과가 거의 확실**하고 톤이 안전하나, **card 증가가 0**(이미 covered 인 약에 nutrient 테마만 추가). Q01 은 relation 신설이 아니라 인덱스/alias 확장 트랙임에 주의(신규 relation 불필요). "기존 카드 충실도↑" 가치는 있으나 커버리지 확장은 아니다.

### 그룹 B — same-class·신규 후보 소량 (source 가능성 보통, 임계/정책 선행)

| 큐 | 테마 | nutrient | card 임팩트 | 근거 |
|---|---|---|---|---|
| **Q02** | 잔여 PPI 단일제 | B12·Mg | low | A티어 PPI 4종 라이브. 잔여 단일제는 품목수 적어 한계효용 낮음. 동거 가능성은 높음. |
| **Q03** | 잔여 경구 비스포스포네이트 | Ca·Fe·Mg | low~med | 알렌/리세/이반 칼슘 라이브. 경구 비스포 간격 라벨 계열 공통. 주사제(졸레드론산) 제외. |

### 그룹 C — 칼륨 안전정책 선행 필수 (치아지드유사 이뇨제)

| 큐 | 테마 | nutrient | card 임팩트 | 근거 |
|---|---|---|---|---|
| **Q10** | 클로르탈리돈 x 칼륨/Mg | K·Mg | med(name_only 64)·복합 다수 | HCTZ relation19·20 동일 치아지드. ★승격 전 **칼륨 안전정책 승계 필수**(`product_link_allowed=false`·`potassium_safety_card=true`). |
| **Q11** | 인다파미드 x 칼륨/Mg | K·Mg | low~med(name_only 16) | 치아지드 유사. Q10 과 동일 정책 승계 필요. |

### 그룹 D — 계열 일반화 위험 (개별 허가사항 확인 필요) — `needs_review`

| 큐 | 테마 | nutrient | card 임팩트 | 근거 |
|---|---|---|---|---|
| **Q05** | 세팔로스포린/FQ class x 철/칼슘/Mg | Fe·Ca·Mg | med(name_only 다수)이나 계열 일반화 불가 | 세프디니르×철(id42)은 **철-세프디니르 적색 비흡수복합 형성이라는 성분특이** 상호작용. 세파클러·세프포독심 등 다수 경구 세팔로스포린(name_only 331)은 동일 철 킬레이션 근거 약함 → **계열 일괄확장 시 관계 날조 위험.** 성분별 허가사항 동거어 없으면 reject. |

### 그룹 E — 고가치·고임팩트이나 허가사항 미기재 예상 (source-policy 입력) — `needs_review`

| 큐 | 테마 | nutrient | card 임팩트 | 근거 |
|---|---|---|---|---|
| **Q12** | 로수바스타틴 x CoQ10 | CoQ10 | large(name_only **472**) | name_only 최대 단일군·체감 가치 높음. ★CoQ10 은 한국 허가사항 미기재 가능성 높음(문헌전용) → **source gate 미통과 예상.** 보충제 권유 톤 오도 위험. 사실상 source-policy 결정 대상. |
| **Q13** | 아토르바스타틴 x CoQ10 | CoQ10 | large(name_only 267) | 인지도 최상위. Q12 동일 리스크. |
| **Q14** | 잔여 스타틴(피타바·심바 등) x CoQ10 | CoQ10 | med(name_only 합 ~205) | Q12 동일 주의(미기재 예상·톤 리스크). |

> 그룹 E 는 **card 잠재력 최대(합 ~944)·사용자 체감 가치 최고**지만, 현 허가사항-우선 gate 에서는 **거의 확실히 missing**(스타틴 라벨에 CoQ10 기재 관행 없음). source 확인을 하더라도 결과는 "missing 확정 → source-policy 결정 입력"일 가능성이 높다. 따라서 `needs_review`(단독 채택 금지)로 큐잉.

### 그룹 F — 보류 / 고위험 (현재 비대상) — `hold` / `high_risk_hold`

| 큐 | 테마 | 처리 | 근거 |
|---|---|---|---|
| **Q09** | 메트포르민 x B12 확장 | `hold` | relation12 라이브 + 인덱스 메트포르민 113품목 **전건 covered**(headroom 0). 신규 작업 없음, 새 품목 유입 모니터링만. |
| **Q15** | H2 차단제 x B12 | `hold` | A티어 확인서에서 **허가사항 미기재(missing) 확정**(구 E07/E09/E10). 현 한국 허가사항 근거 약함(문헌전용)→gate 미통과. source-policy 결정 시에만 재검토. |
| **Q16** | 와파린/DOAC/항혈소판 x 비타민K | `high_risk_hold` | **CLAUDE.md 영구 금지(antagonism·임상판단 행).** 후보화 자체 금지. |
| **Q17** | 항암제 x 영양소 | `high_risk_hold` | 임상판단·개인차 강한 고위험군. 참고정보 베타 톤으로 다룰 수 없음. seed 미포함. |
| **Q18** | 임신/소아/정신건강 x 영양소 | `high_risk_hold` | 민감군·근거 불충분·개인차 큼. clinical reviewer 트랙에서만 별도 검토. |

---

## 3. 전략 권고 — 다음 레버는 후보가 아니라 source-policy

A티어 소진(relations 41) 후, 남은 커버리지 확장은 **둘 중 하나**에 막혀 있다:

1. **enrichment(그룹 A)**: source 확실하나 신규 커버리지 ~0.
2. **고임팩트(그룹 E 스타틴 ~944 + 그룹 F Q15 H2 ~202)**: 사용자 가치·커버리지 크나 **허가사항 미기재**.

→ **권고 우선순위:**
- **(1순위) source-policy 결정**: "충분히 확립된 이차문헌(예: depletion 테마)을 source 로 허용할지"를 PM/임상검토 트랙에서 결정. 허용 시 스타틴×CoQ10·H2×B12 가 한 번에 열림(가장 큰 커버리지 레버). 미허용 시 영구 보류로 박제.
- **(2순위) 그룹 A(Q01·Q06·Q07·Q04·Q08) enrichment / 인덱스트랙**: source 확실·안전·저비용. 커버리지 확장은 아니나 기존 카드 충실도 향상. Q01(에스오메프라졸)은 relation 이 아닌 인덱스/alias 확장임에 유의.
- **(3순위) 그룹 C(Q10·Q11) 치아지드유사**: 칼륨 안전정책 승계 작업 선행 후 source 확인. 소규모.
- **(보류) 그룹 D(Q05)**: 계열 일반화 금지 — 성분별 허가사항 확인 후에만, 동거어 없으면 reject.

> 즉, 다음 라운드에서 **개별 후보 source 확인보다 source-policy 의사결정이 ROI 가 훨씬 크다.** 후보 source 확인을 먼저 한다면 그룹 A(확실·안전)부터.

---

## 4. 모호/보류로 플래그한 후보 (정직성)

- **Q05 세팔로스포린 class** → `needs_review`: 세프디니르×철은 성분특이(적색 비흡수복합)이지 세팔로스포린 계열 일반 성질이 아니다. name_only 331(세파클러·세프트리악손 등)을 계열 근거로 일괄 채택하면 관계 날조. **계열 일반화 금지, 개별 확인 필요.**
- **Q12–Q14 스타틴×CoQ10** → `needs_review`: card 임팩트 최대지만 허가사항 미기재 예상(문헌전용). 단독 채택 금지, source-policy 입력용.
- **Q09 메트포르민×B12** → `hold`: 이미 relation12 + 전건 covered, headroom 0. 신규 작업 없음.
- **Q15 H2×B12** → `hold`: source 확인 이미 완료(missing 확정). 재source 확인 불필요, 정책 결정 대기.
- **Q16–Q18 항응고/항암/임신·소아·정신건강** → `high_risk_hold`: 안전 정책상 후보화 자체 비대상(Q16 은 CLAUDE.md 영구 금지).

---

## 5. 금지 / 안전 준수

- ✅ 본 단계는 **큐 문서 + CSV 뿐**. relation 추가·수정·flip·full index·alias·export·src·DATA_URL·validator·smoke·integrate 변경 0. **relations 41 불변·이번에 구현 0건.**
- ✅ "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 없음. 제품·구매·제휴·영양제 추천·복용지시·진단·치료 단정 없음. `published`/`clinical_reviewed` false 유지.
- ✅ 어떤 후보도 `source_confirmed` 로 표시하지 않는다 — 전부 **향후 source 확인 대기 후보**(`source_check_queue`)로만 기재. 스타틴/CoQ10·H2 는 "missing 예상/확정"으로 보수 표기.
- ✅ 칼륨 후보(Q10·Q11)는 승격 시 칼륨 안전정책(`product_link_allowed=false`·`potassium_safety_card=true`) 승계 선행 조건 명시.

> 산출물: 본 문서 + `data/next_relation_source_check_queue_v1_1.csv`(Q01–Q18, 전건 `do_not_implement_yet=true`).
