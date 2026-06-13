# MediStack — relation 확장 우선순위 계획 (Expansion Priority Plan)

> 작성일: 2026-06-13. 기준 HEAD `cb66a3c` 이후. **이 문서·후보 CSV 는 "검토 후보(candidate only)"일 뿐, 실제 relation 이 아니다. 이번 단계에서 relation/full index/alias/export/src 는 한 줄도 추가·수정하지 않는다.**
>
> 입력: 커버리지 매칭 `MediStack_popular_drug_coverage_match.md` (+ `data/popular_drug_coverage_match_v1_1.csv`).
> 선행 문서: 현황 분석 `MediStack_relation_card_coverage_analysis.md`, 후보 초안 `MediStack_relation_expansion_candidate_plan.md`.
> 후보 CSV: `data/relation_expansion_priority_candidates_v1_1.csv` (20건, 전건 `do_not_implement_yet=true`).

---

## 0. 원칙 (먼저 읽기)

- 후보는 전부 `do_not_implement_yet=true`, `source_required=true`, `review_required=true`. nutrient 테마는 **가설(미확정)** 이며 상호작용을 사실로 단정하지 않는다 — 복용지시·진단·제품권유가 아니다.
- 실제 채택은 **허가사항 등 공식 출처 확인 + 검토 통과** 후 별도 단계(데이터 변경, PM 승인)에서만.
- "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 금지. 제품 추천·구매·제휴 금지. `published` / `clinical_reviewed` 봉인 유지(false).
- **방어 가능한 약물-영양소 관계만 후보화한다.** name_only 가 많다는 이유만으로 관계를 만들지 않는다(날조 금지). 확립된 흡수/고갈 상호작용이 없는 약은 후보에서 제외한다(§4).
- 와파린×비타민K 등 **antagonism/임상판단 행은 CLAUDE.md 가 영구 금지** — 후보화하지 않는다.

---

## 1. 방법 요약 (어떻게 골랐나)

1. popular-like seed 120건을 full index/relation_card/name_only 에 매칭 → covered 13 / **name_only_only 101** / missing 6 / ambiguous 0.
2. `name_only_only` 중 **기존 relation 과 계열·기전 인접성이 있고**(출처·문구·안전선 승계 용이), **확립된 약물-영양소 상호작용이 있는** 성분만 후보로 승격.
3. 기존 후보 초안 7종(C01–C07)을 전부 반영(매핑은 §3 표의 비고 참조).
4. 우선순위 = (출처 확보 가능성 × 사용자 가치 × 안전선 승계 용이성) 종합. card 증가 효과(name_only 매핑 수)는 가치 신호이되, **출처 게이트(허가사항 우선)** 와 **위험도** 가 우선한다.
5. 민감 약군(정신건강·임신·소아·항응고·항암)과 방어 불가 약군은 후보에서 분리(§4·§5).

---

## 2. 우선순위 티어 (요약)

| 티어 | 묶음 | 후보 | 근거 |
|---|---|---|---|
| **A** 즉시검토군 | 기타 PPI × B12/Mg, 경구 비스포스포네이트 × Ca/Fe/Mg | E01–E06 | 기존 relation(오메프라졸13·14 / 알렌드론산29)과 **동일 계열** → 허가사항 출처·문구·안전선 재현 가장 쉬움. 위험 낮음 |
| **B** 인접기전군 | H2 차단제 × B12, 세프디니르 × 철분 | E07–E10 | 위산억제 기전 인접(B12) / 잘 알려진 흡수 상호작용. 출처 확인 난이도 A보다 다소 높음 |
| **C** 칼륨주의군 | 치아지드(유사) 이뇨제 × 전해질 | E11–E12 | HCTZ 계열이나 **칼륨 안전 정책 승계 선행 필수**. name_only 소수 |
| **D** 문헌·톤주의군 | 스타틴 × CoQ10 | E13–E16 | card 효과 최대(로수바472)이나 **허가사항 미기재 가능성 + 보충권유 오인 위험** → source gate 통과 불확실, 문구 가장 신중 |
| **E** 테마보강군 | 레보티록신 × Mg, 퀴놀론/테트라 × 아연 | E17–E19 | 기존 covered 품목에 nutrient 테마 추가(새 covered 품목 증가 0). 정보 풍부화 |
| **F** 인덱스트랙 | 에스오메프라졸 | E20 | relation16 이미 존재. 카드 0 원인은 인덱스 부재 → **relation 신설 아님, full index/alias 확장** |

---

## 3. 우선순위 후보 20건 (candidate only)

> 전건 `do_not_implement_yet=true`. `card영향` = name_only 매핑 수(채택 시 카드 증가 추정). 상세 필드는 `data/relation_expansion_priority_candidates_v1_1.csv`.

| rank | id | 성분/계열 | 테마(가설) | nutrient | 방향 | 가치 | card영향 | 위험 | 출처유형 | 비고 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | E01 | 라베프라졸(PPI) | 위산억제→Mg/B12 | Mg·B12 | depletion | high | 216 | low | 허가사항 | ←C03, name_only 최다 PPI |
| 2 | E02 | 판토프라졸(PPI) | 위산억제→Mg/B12 | Mg·B12 | depletion | med | 45 | low | 허가사항 | ←C01 |
| 3 | E03 | 란소프라졸(PPI) | 위산억제→Mg/B12 | Mg·B12 | depletion | low | 10 | low | 허가사항 | ←C02 |
| 4 | E04 | 리세드론산(비스포스포네이트) | 경구흡수 간격 | Ca·Fe·Mg | absorption | high | 118 | low | 허가사항 | ←알렌드론산29 계열 |
| 5 | E05 | 덱스란소프라졸(PPI) | 위산억제→Mg/B12 | Mg·B12 | depletion | low | 4 | low | 허가사항 | 란소프라졸 활성이성질체 |
| 6 | E06 | 이반드론산(경구 비스포) | 경구흡수 간격 | Ca·Fe·Mg | absorption | med | 73 | low | 허가사항 | 졸레드론산(주사)은 제외 |
| 7 | E07 | 파모티딘(H2) | 위산억제→B12 | B12 | depletion | high | 106 | low_med | 허가사항+문헌 | 기전 인접(PPI 아님) |
| 8 | E08 | 세프디니르(세팔로) | 철분 흡수 | 철분 | absorption | low | 7 | low_med | 허가사항 | 신규 계열·잘 알려진 상호작용 |
| 9 | E09 | 라푸티딘(H2) | 위산억제→B12 | B12 | depletion | low | 48 | low_med | 허가사항+문헌 | 파모티딘 동일 기전 |
| 10 | E10 | 니자티딘(H2) | 위산억제→B12 | B12 | depletion | low | 48 | low_med | 허가사항+문헌 | 파모티딘 동일 기전 |
| 11 | E11 | 클로르탈리돈(치아지드) | 전해질 | K·Mg | depletion | low | 2 | **medium** | 허가사항 | ←C04, **칼륨 정책 승계 필수** |
| 12 | E12 | 인다파미드(치아지드 유사) | 전해질 | K·Mg | depletion | low | 3 | **medium** | 허가사항 | ←C05, 칼륨 정책 승계 |
| 13 | E13 | 로수바스타틴(스타틴) | CoQ10(문헌) | CoQ10 | depletion | high | 472 | medium | **이차문헌** | ←C06, source gate 불확실·톤 주의 |
| 14 | E14 | 아토르바스타틴(스타틴) | CoQ10(문헌) | CoQ10 | depletion | high | 267 | medium | **이차문헌** | ←C07, 동일 주의 |
| 15 | E15 | 피타바스타틴(스타틴) | CoQ10(문헌) | CoQ10 | depletion | med | 150 | medium | **이차문헌** | 동일 주의 |
| 16 | E16 | 심바스타틴(스타틴) | CoQ10(문헌) | CoQ10 | depletion | med | 55 | medium | **이차문헌** | 동일 주의 |
| 17 | E17 | 레보티록신(기존 covered) | Mg 흡수(신규 nutrient) | Mg | absorption | low | 0 | low | 허가사항 | 기존 10·11에 Mg 보강 |
| 18 | E18 | 퀴놀론(기존 covered) | 아연 흡수(신규 nutrient) | 아연 | absorption | low | 0 | low | 허가사항 | 기존 품목 테마 보강 |
| 19 | E19 | 테트라사이클린(기존 covered) | 아연 흡수(신규 nutrient) | 아연 | absorption | low | 0 | low | 허가사항 | 기존 품목 테마 보강 |
| 20 | E20 | 에스오메프라졸(relation16 존재) | (관계 있음·인덱스 부재) | Mg(+B12) | depletion | med | 0 | low | 허가사항+인덱스 | **relation 트랙 아님 → full index 확장** |

**기존 후보 7종 반영:** C01→E02, C02→E03, C03→E01, C04→E11, C05→E12, C06→E13, C07→E14 (전부 포함).

---

## 4. 후보에서 제외한 고빈도 약 (정직성 — 왜 빼는가)

name_only 가 많아도 **확립된 약물-영양소(흡수/고갈) 상호작용이 없으면 후보로 만들지 않는다.** 다음은 검색 빈도는 높지만 relation 후보가 **아니다.**

| 약/계열 | name_only | 제외 사유 |
|---|---|---|
| 암로디핀(CCB) | 667 | 확립된 미량영양소 상호작용 없음 — 관계 날조 불가 |
| 클로르페니라민·세티리진 등 항히스타민 | 186–407 | 영양소 흡수/고갈 상호작용 표준 근거 없음 |
| 슈도에페드린·덱스트로메토르판 등 감기약 | 262–268 | 동일 — 근거 없음 |
| 아세트아미노펜·이부프로펜 등 진통/NSAID | 34–143 | 동일 — 근거 없음(NSAID-위장 보호는 영양소 관계 아님) |
| ARB/ACEi(로사르탄·발사르탄·텔미사르탄 등) | 59–168 | 미량영양소 흡수/고갈 상호작용 표준 근거 없음 + 칼륨은 **상승(고칼륨) 방향=임상판단 영역**이라 본 depletion/absorption 테마에 부적합(§5 스피로노락톤과 동일 논리). HCTZ 복합은 기존 커버 |
| 아목시실린·클라불란산 | 170–198 | 페니실린계는 양이온 킬레이션 상호작용 없음(퀴놀론/테트라와 다름) |
| DPP-4/SGLT2/SU 당뇨약 | 13–180 | 메트포르민-B12 외 확립 근거 없음 |
| 탐스로신·두타스테리드·피나스테리드 | 94–193 | 미량영양소 상호작용 근거 없음 |

> 결론: 흔하다고 다 후보가 아니다. **상위 name_only(암로디핀·항히스타민·감기약)는 의도적으로 비워 둔다.** 이는 "정보를 못 채운 것"이 아니라 **근거 없는 관계를 만들지 않는 안전 정책**이다.

---

## 5. 민감 약군 (high_risk — 후보 분리·우선순위 낮춤)

CLAUDE.md/제품원칙상 민감하거나 임상판단이 개입하는 약군은 별도 취급한다.

| 약군 | 처리 |
|---|---|
| 정신건강(SSRI·벤조·항정신병: 에스시탈로프람·설트랄린·알프라졸람·졸피뎀·쿠에티아핀) | name_only 16–103 존재하나 **후보화 보류**. 영양소 관계 근거 약하고 민감군. 필요 시 별도 임상검토 |
| 항응고/항혈소판(와파린·리바록사반·클로피도그렐) | **와파린×비타민K = CLAUDE.md 영구 금지(antagonism)**. DOAC/항혈소판도 비타민K/영양소 관계는 임상판단 → 후보화 안 함 |
| 임신/피임(드로스피레논 등) | 여성건강 민감군. 영양소 관계 근거 불충분 → 후보화 안 함 |
| 소아·항암 | 본 seed 에 미포함. 향후에도 high_risk·낮은 우선순위 |
| 칼륨 관련(치아지드·스피로노락톤 등) | E11·E12 는 **칼륨 안전 정책(product_link 금지·potassium_safety_card·칼륨 salt 보충제 취급 금지) 승계 선행** 조건부. 스피로노락톤(칼륨보존)은 고칼륨 방향이라 더 신중 → 현재 미후보 |

---

## 6. 후보 필드 루브릭 (CSV 해석)

- `candidate_type`: `same_class_extension`(기존 계열 확장·가장 안전) / `adjacent_mechanism`(기전 인접) / `new_specific`(신규 특정 상호작용) / `new_class_literature`(신규 계열·문헌) / `existing_ingredient_new_nutrient`(기존 성분 nutrient 보강) / `index_alias_track`(관계 아닌 인덱스 확장).
- `estimated_card_expansion_impact`: name_only 매핑 수(채택 시 새로 카드가 붙을 추정 품목 수). 보강군(E17–E19)·인덱스트랙(E20)은 0.
- `risk_level`: low / low_medium / medium. `caution_flags`: 칼륨(potassium_safety_inherit)·문헌전용(literature_only_source)·CoQ10 톤(coq10_supplement_tone_risk) 등.
- `suggested_source_type`: 허가사항 우선. 문헌전용(스타틴 CoQ10)은 **source gate(허가사항) 통과 불확실** — 통과 못 하면 보류.
- `suggested_copy_tone`: 전부 "줄어들 수 있다 / 간격 권장 / 상담하세요" 톤. **"보충하세요/복용하세요" 금지.**

---

## 7. 다음 단계 프롬프트 초안 (Task E)

다음 단계 후보(택1 또는 순차). **전부 PM 승인 후 별도 단계.**

```
[옵션 1] external popular drug 실데이터 입력 후 재매칭
  - data/external_popular_drugs_top100.csv (rank,query_name,source,note) 수집/배치
    (처방통계·약국 판매·검색량 등 실출처 명시).
  - python3 scripts/match_popular_drugs_coverage.py 가 seed 대신/추가로 외부 리스트도 읽도록 확장.
  - 실데이터 기준 name_only_only 재산출 → 우선순위 재정렬.

[옵션 2] relation priority Top 10(E01–E10) 출처 확인
  - 각 후보 성분의 허가사항(nedrug getItemDetail) "상호작용/주의사항"에서
    제안 nutrient 테마 실재 여부 확인 → 출처 있는 것만 통과 표시(여전히 candidate, 데이터 미반영).
  - 스타틴 CoQ10(E13–E16)은 허가사항 미기재 시 보류 처리.

[옵션 3] relation 30 → 40 소폭 확장 (PM 승인·데이터 변경 단계)
  - 출처 통과한 A 티어(PPI/비스포스포네이트)부터 relation 신규 작성.
  - 새 버전 export + 새 validator(절대불변원칙) + relation_card 재생성 + smoke 전종 + 배포 게이트.
  - 칼륨군(E11·E12)은 칼륨 안전 정책 승계 코드 확인 후에만.

[옵션 4] relation 문구 안전성 리뷰
  - display_text/management 톤 점검(복용지시·단정·제품권유 0건) + disclaimer 승계.

[옵션 5] candidate→relation 승격 validator 설계
  - source_confirmed=true & review passed & copy_tone OK & (칼륨이면 정책 승계) 만 승격 허용하는
    게이트 스크립트. candidate CSV → relation 변환은 이 게이트 통과 시에만.
```

---

## 8. 금지 / 안전 (본 단계)

relation 추가·수정 / full index 수정 / alias 수정 / export 수정 / src·렌더 수정 / DATA_URL 변경 / source gate·disclaimer 변경 / `published`·`clinical_reviewed` true / 제품·구매·제휴·영양제 추천 UI / candidate→relation 승격 / seed 를 실측 검색순위로 과장 / tag 생성 / `scripts/__pycache__` 커밋 — **전부 금지.** 본 단계는 분석·후보 문서·후보 CSV 까지만.
