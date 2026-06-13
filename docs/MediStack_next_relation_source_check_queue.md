# MediStack — 다음 relation 확장 source 확인 큐 v1.1

> 작성일: 2026-06-13. **읽기/문서화 전용(데이터 무변경).** 우선순위 후보 20건(`relation_expansion_priority_candidates_v1_1.csv`)의 source 확인 진행 상태를 분류하고, **다음에 허가사항 출처를 확인할 후보를 우선순위로 제안**한다. relation 추가·수정·flip 없음.
>
> source 확인 방법(승계): `verify_atier_relation_sources.py` 패턴 — 후보 성분별 단일성분 대표 2~3품목 nedrug `getItemDetail` fetch → 테마 신호어 검색 → `source_confirmed/needs_review/missing/reject`. **허가사항 우선 gate**(문헌만 있으면 미채택, H2×B12 선례).

---

## 0. 한 줄 결론

**쉬운 고가치 후보(PPI·비스포·세프디니르 7건)는 이미 라이브 통합 완료.** 남은 9개 미확인 후보는 (가) **enrichment(신규 covered 0)** 또는 (나) **소규모 치아지드(칼륨 정책 선행 필요)** 또는 (다) **고가치이나 허가사항 미기재 예상(스타틴×CoQ10)** 으로 갈린다. → **진짜 다음 레버는 개별 후보가 아니라 "이차문헌 출처 허용 여부" source-policy 결정**(스타틴 944건 + H2 202건 + PPI×칼슘이 전부 여기 걸림).

---

## 1. 20후보 source 확인 상태 (전수 분류)

| 상태 | 후보 | 비고 |
|---|---|---|
| ✅ **DONE**(source_confirmed→라이브) | E01·E02·E03·E04·E05·E06·E08 (7) | relations 30→41(신규 11). PPI 4종 ×B12·Mg + 비스포 2종 ×칼슘 + 세프디니르 ×철. |
| ⛔ **CHECKED=missing**(허가사항 미기재) | E07·E09·E10 (3) | H2 차단제(파모티딘·라푸티딘·니자티딘) × B12. 문헌전용 → 현 gate 미통과. **source-policy 결정 대기.** |
| 🟡 **UNCHECKED**(다음 대상) | E11·E12·E13·E14·E15·E16·E17·E18·E19 (9) | 아래 §2 큐. |
| ▫️ **N/A**(relation 트랙 아님) | E20 (1) | 에스오메프라졸×Mg는 relation16 이미 존재. 막힌 건 full index/alias 확장이지 relation 신설 아님. |

> 추가로 이번 세션에서 **PPI×칼슘(케이스 C 전환 전제)** 을 source 확인 → `missing/reject`(허가사항 0/22, 칼슘=완충제). `MediStack_ppi_calcium_combo_review_v1_1.md` 참조.

---

## 2. 다음 source 확인 큐 (9건 우선순위) — `data/next_relation_source_check_queue_v1_1.csv`

6개 기준(① 사용자 가치 ② source 확보 가능성 ③ 기존 구조 유사 ④ 톤 안전 ⑤ card 증가 ⑥ 추천/지시 위험 낮음)으로 순위화.

### 묶음 A — source 확실·안전·빠름 (단, 신규 covered 0 = enrichment)

| 순위 | 후보 | 테마 | 근거 |
|---|---|---|---|
| **Q1** | E18 플루오로퀴놀론 × **아연** | 흡수(간격) | 기존 퀴놀론 relation 이 이미 "다가양이온(칼슘·철·Mg)" 라벨 인용 → 아연 동일 문장 동거 가능성 매우 높음. 톤=분리 권장(안전). **신규 covered 0**(기존 covered 품목 테마 보강). |
| **Q2** | E19 테트라사이클린 × **아연** | 흡수(간격) | 독시/미노사이클린 동일 다가양이온 패턴. 신규 covered 0. |
| **Q3** | E17 레보티록신 × **마그네슘** | 흡수(간격) | relation10·11(칼슘·철)에 Mg 제산제 문맥 동거 가능. 신규 covered 0. |

> 묶음 A 는 **source gate 통과가 거의 확실**하고 톤이 안전하나, **card 증가가 0**(이미 covered 인 약에 nutrient 테마만 추가). "기존 카드 충실도↑" 가치는 있으나 커버리지 확장은 아님.

### 묶음 B — same-class·신규 covered 소량 (칼륨 안전정책 선행 필수)

| 순위 | 후보 | 테마 | 근거 |
|---|---|---|---|
| **Q4** | E11 클로르탈리돈 × 칼륨·마그네슘 | depletion | HCTZ relation19·20 동일 치아지드. 전해질 라벨 신호 가능. ★승격 전 **칼륨 안전정책 승계 필수**(`product_link_allowed=false`·`potassium_safety_card=true`). card 소(2). |
| **Q5** | E12 인다파미드 × 칼륨·마그네슘 | depletion | 치아지드 유사. E11 과 동일 정책 승계. card 소(3). |

### 묶음 C — 고가치·고임팩트이나 허가사항 미기재 예상 (gate 검증용)

| 순위 | 후보 | 테마 | card | 근거 |
|---|---|---|---|---|
| **Q6** | E13 로수바스타틴 × CoQ10 | depletion | **472** | name_only 최대 단일군. ★CoQ10 은 한국 허가사항 미기재 가능성 높음(문헌전용) → **source gate 미통과 예상**. 보충제 톤 오도 위험. source 확인=가설 검증용(예상=missing). |
| **Q7** | E14 아토르바스타틴 × CoQ10 | depletion | 267 | 인지도 최상위. E13 동일 리스크. |
| **Q8** | E15 피타바스타틴 × CoQ10 | depletion | 150 | E13 동일. |
| **Q9** | E16 심바스타틴 × CoQ10 | depletion | 55 | E13 동일. |

> 묶음 C 는 **card 증가 잠재력 최대(합 944)·사용자 체감 가치 최고**지만, 현 허가사항-우선 gate 에서는 **거의 확실히 missing**(스타틴 라벨에 CoQ10 기재 관행 없음). source 확인을 하더라도 결과는 "missing 확정 → source-policy 결정 입력"일 가능성이 높다.

---

## 3. 전략 권고 — 다음 레버는 후보가 아니라 source-policy

쉬운 고가치 후보 소진 후, 남은 커버리지 확장은 **둘 중 하나**에 막혀 있다:

1. **enrichment(Q1-Q3)**: source 확실하나 신규 커버리지 0.
2. **고임팩트(Q6-Q9 스타틴 944 + E07/09/10 H2 202)**: 사용자 가치·커버리지 크나 **허가사항 미기재**.

→ **권고 우선순위**:
- **(1순위) source-policy 결정**: "충분히 확립된 이차문헌(예: depletion 테마)을 source 로 허용할지" 를 PM/임상검토 트랙에서 결정. 허용 시 스타틴×CoQ10·H2×B12 가 한 번에 열림(가장 큰 커버리지 레버). 미허용 시 전부 영구 보류로 박제.
- **(2순위) 묶음 A(Q1-Q3) enrichment**: source 확실·안전. 커버리지 확장은 아니나 기존 카드 충실도 향상. 저비용.
- **(3순위) 묶음 B(Q4-Q5) 치아지드**: 칼륨 안전정책 승계 작업 선행 후 source 확인. 소규모.

> 즉, 다음 라운드에서 **개별 후보 source 확인보다 source-policy 의사결정이 ROI 가 훨씬 크다.** 후보 source 확인을 먼저 한다면 묶음 A(확실·안전)부터.

---

## 4. 금지 / 안전 준수

- ✅ 본 단계는 **분류·문서·CSV 뿐**. relation 추가·수정·flip·full index·alias·export·src·DATA_URL 변경 0.
- ✅ "식약처 승인/법적 문제없음/약사 검수 완료" 표현 없음. 제품·구매·영양제 추천 없음. published/clinical_reviewed false 유지.
- ✅ 어떤 후보도 본 문서가 "확정"하지 않는다 — 전부 **source 확인 대기 후보**로만 기재. 스타틴/CoQ10 은 "missing 예상"으로 보수 표기.

> 산출물: 본 문서 + `data/next_relation_source_check_queue_v1_1.csv`(Q1-Q9).
