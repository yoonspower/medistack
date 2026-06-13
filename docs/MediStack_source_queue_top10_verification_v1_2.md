# MediStack — Top10 확장 후보 source 확인 결과 v1.2 (작업3+4)

> 작성일: 2026-06-14. **source-verification + draft 전용. 라이브 변경 0.**
> relations 는 **41 그대로**이며 이번에 **구현/flip/승격 0건**이다. 모든 후보 `do_not_implement_yet=true`.
> 산출물: 본 문서 + `data/source_queue_top10_verification_v1_2.csv` + (source_confirmed ≥1 이므로) `data/relation_expansion_draft_v1_2.json` + `docs/MediStack_relation_expansion_draft_v1_2.md`.
> 검증 스크립트: `scripts/verify_source_queue_top10_v1_2.py` (읽기 전용 + nedrug getItemDetail fetch).

---

## 0. 한 줄 결론

다음 relation 확장 큐(Q01–Q18)의 **Top10 우선 후보**를 식약처 nedrug 허가사항 원문으로 확인한 결과,
**6건이 허가사항 상호작용/주의 문맥에 신호어 실재(source_confirmed)** 했고, 그중 **진짜 새 가치는 Q06(퀴놀론×아연)·Q07(테트라사이클린×아연)** 이다(예측 적중).
나머지 confirmed 중 **Q02(오메프라졸 잔여)** 는 기존 relation(13/14) enrichment라 신규 relation이 아니며, **Q04(비스포×철/Mg)** 는 기존 칼슘 relation(40/41)에 다가양이온 라벨 기반 테마를 더하는 enrichment, **Q10/Q11(치아지드유사 이뇨제×K/Mg)** 는 신규 성분 relation(칼륨 안전정책 승계 필수).
**Q03(알렌드론산 Ca/Fe/Mg)·Q08(레보티록신 Mg)** 은 허가사항 미기재로 **reject**. **Q01(에스오메 index-track)·Q05(세팔로 class 일반화)** 은 **needs_review**. carry-forward(Q09/Q12–Q18)는 기존 verdict 승계.

---

## 1. 방법론 (A티어 패턴 승계)

`verify_atier_relation_sources.py` / `verify_ppi_calcium_combo_sources.py` 의 검증 패턴을 그대로 승계:

1. **fetch**: 테마별 단일성분 대표 품목 2~3건의 `getItemDetail`(itemSeq) HTML → 태그 제거 → 공백 정규화.
   - 대표 itemSeq 는 `data/medistack_v0.3_aliases.json` 의 `verified_item_seqs` 에서 추출.
   - name_only 인 클로르탈리돈/인다파미드는 `full_drug_name_index_sample_v1_0.json` 에서 **단일성분(ingredient_name 정확 일치)** 대표를 추출.
2. **signal**: 테마별 특정 신호어를 **상호작용/주의/이상반응 문맥에서만** 매칭하고 증거 스니펫 캡처.
3. **additive exclusion**: 첨가제/조성표 문맥(첨가제·착색·코팅·활택·부형·산화마그네슘·스테아르산마그네슘·분량·규격 등)은 배제.
4. **gate**: 허가사항-우선. 문헌만 있으면 미채택(H2×B12 선례).

### 신호어(요지)
| 테마 | 신호 | 첨가제 배제 |
|---|---|---|
| 아연(흡수, FQ/테트라) | '아연' + (흡수/병용/다가양이온/제산제/함유 제제) | 첨가제 문맥 제외 |
| 다가양이온(흡수, 비스포) | '다가 양이온' 직접 매칭 | — |
| 철/마그네슘(흡수, 비스포) | 다가양이온 문맥 내 철·마그네슘 | 산화철/스테아르산Mg 제외 |
| 저마그네슘(고갈, PPI/이뇨) | '저마그네슘' | 조성 Mg 제외 |
| B12(고갈, PPI) | '시아노코발라민'/'비타민 B12' + 흡수·결핍 문맥 | — |
| 칼륨(고갈, 이뇨) | '저칼륨'/'칼륨 저하·배설·소실·혈증' | — |

### 정직성 가드
- `source_confirmed` 는 **실제로 fetch한 허가사항의 상호작용/주의/이상반응 문맥**에 신호어가 있을 때만.
- "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 류 표현 금지. published/clinical_reviewed false.
- 약한 후보를 confirmed 로 밀지 않음. 모호 → needs_review, 부재 → reject, 고위험 → hold.

---

## 2. Top10 active 후보별 결과 (네트워크 fetch)

### ✅ source_confirmed (6)

**Q06 — Fluoroquinolone × 아연 (★신규 relation 핵심)**
- 레보/시프로/오플록사신/목시플록사신 **전부** 허가사항 상호작용에 아연 동거.
- 증거(레보플록사신, itemSeq 201207060): *"…철분 함유 제제, 칼슘 함유 제제, **아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하**되어 효과가 저하…투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다."*
- 목시플록사신(itemSeq 201309618): *"…**철 또는 아연을 포함하는 제제는 이 약의 흡수를 감소시키므로** 이러한 약들의 투여 4시간 전이나 투여 8시간 후에 복용…"*
- 판정: **신규 relation 후보**. 기존 FQ relation(레보 1-3 / 시프로 4-6 / 오플록사신 21-23 / 목시 24-25)에 아연 추가. 톤 안전(분리/간격).

**Q07 — Tetracycline × 아연 (★신규 relation 핵심)**
- 독시/미노사이클린 **3/3** 동거.
- 증거(독시정, itemSeq 201403031): *"칼슘, 마그네슘, 알루미늄을 함유하는 제산제…, **철·아연을 함유하고 있는 제제**…에 의해 **테트라사이클린계 약물의 흡수가 저하**되어 효과가 저하…"*
- 판정: **신규 relation 후보**(독시 7-9 / 미노 26-28 에 아연 추가).

**Q02 — 잔여 PPI(오메프라졸) × B12/Mg (enrichment, 신규 relation 아님)**
- 오메프라졸 잔여 단일제 2/2 동거. 증거(라메졸, itemSeq 199202074): *"대사 및 영양계: 매우 드물게 **저마그네슘혈증**"* + *"이 약의 장기투여로 인해 저염산증 또는 무위산증에 의해 **비타민 B12(시아노코발라민) 흡수장애**가 나타날 가능성"*.
- 판정: **오메프라졸은 relation13(B12)·14(Mg) 이미 라이브 → 신규 relation 불필요.** 잔여 단일제 매핑은 인덱스/alias 트랙(PM 승인). draft 미포함.

**Q04 — 비스포스포네이트 × 철/Mg (enrichment)**
- 리세드론산·이반드론산 **2/3** 동거(알렌드론산은 다가양이온 라벨 없음→제외).
- 증거(리세드론산, itemSeq 201903166): *"**다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 약물**…은 이 약의 흡수를 방해…동시에 투여하지 말아야 한다."*
- 증거(이반드론산, itemSeq 201306285): *"우유, 음식물, 칼슘, **다가 양이온(예, 알루미늄, 마그네슘, 철)들을 포함한 제품들은 이 약의 흡수를 저해**…"*
- 판정: 기존 칼슘 relation(40/41)에 **철·마그네슘 테마 추가** draft. **알렌드론산은 미적용**(라벨에 다가양이온/철 부재).

**Q10 — 클로르탈리돈 × 칼륨/Mg (★신규 relation, 칼륨 안전정책 필수)**
- 단일성분 2/2 동거. 증거(클로베네정, itemSeq 202500118): 이상반응(전해질과 대사) *"주로 고용량에서의 **저칼륨혈증**…자주 저나트륨혈증, **저마그네슘혈증**"* + 금기 *"불응성 저칼륨혈증 환자"*.
- 판정: **신규 relation 후보**. HCTZ relation19/20·푸로세미드17/18 동일 모델. **승격 시 칼륨 안전정책(`product_link_allowed=false`·`potassium_safety_card=true`) 승계 필수.**

**Q11 — 인다파미드 × 칼륨/Mg (★신규 relation, 칼륨 안전정책 필수)**
- 단일성분 3/3 동거. 증거(나트릭스서방정, itemSeq 199900835): *"임상시험동안, **저칼륨혈증(혈장칼륨<3.4mmol/l)이 환자의 10%에서 나타났으며**…"* + (대사 및 영양계) *"흔하게 저칼륨혈증…드물게 저염소혈증 **저마그네슘혈증**"*.
- 판정: **신규 relation 후보**. Q10 동일 칼륨 안전정책 승계 필수.

### ⚠️ needs_review (2)

**Q01 — 에스오메프라졸 (index-track)**
- 교차참조 라베프라졸(itemSeq 201405854)에서 저마그네슘·B12 신호 확인되나, **relation16(에스오메×마그네슘) 이미 존재**. 막힌 건 relation 신설이 아니라 alias 미부여로 매핑 카드 0인 **인덱스/alias 확장 트랙**. → **신규 relation 금지**, full index/alias 확장(PM 승인) 별도 단계. 에스오메 단일제 itemSeq 미보유로 본 라운드는 교차참조만.

**Q05 — 세팔로스포린 class × 철/칼슘/Mg (계열 일반화 위험)**
- fetch한 비-세프디니르 대표(itemSeq 199700521)는 철/칼슘/다가양이온 **0건**. 유일한 철 동거어는 세프디니르(이미 relation42, 성분특이 적색 비흡수복합). → **계열 일반화 근거 없음.** 계열 일괄확장 금지, 성분별 개별 확인 후에만, 동거어 없으면 reject.

### ❌ reject (2)

**Q03 — 알렌드론산 × Ca/Fe/Mg**
- 라이트알렌드론(201902246)·보나드론(200500488) **둘 다 다가양이온/철 0건**. 칼슘 언급은 글루코코르티코이드 환자 골흡수 문맥(상호작용 아님). → **허가사항 미기재. reject.**

**Q08 — 레보티록신 × Mg**
- 씬지로이드/씬지록신 3품목 모두 마그네슘 흡수 상호작용 동거어 **0건**(relation10/11 칼슘·철과 달리 Mg 라벨 부재). → **미기재. reject.**

---

## 3. carry-forward (재fetch 없음)

| 큐 | 테마 | verdict | 근거 |
|---|---|---|---|
| Q12 | 로수바스타틴×CoQ10 | needs_review | 허가사항 미기재 예상(literature only). source-policy 입력용. |
| Q13 | 아토르바스타틴×CoQ10 | needs_review | Q12 동일. |
| Q14 | 잔여 스타틴×CoQ10 | needs_review | Q12 동일. |
| Q09 | 메트포르민×B12 | hold | relation12 라이브+전건 covered(headroom 0). |
| Q15 | H2×B12 | hold | A티어서 missing 확정(E07/E09/E10). 정책결정 대기. |
| Q16 | 항응고/항혈소판×비타민K | hold | CLAUDE.md 영구 금지(antagonism). |
| Q17 | 항암제×영양소 | hold | 고위험·임상판단. |
| Q18 | 임신/소아/정신건강×영양소 | hold | 민감군·근거 불충분. |

---

## 4. verdict tally

### Top10 active (10건)
- **source_confirmed: 6** (Q06, Q07, Q02, Q04, Q10, Q11)
- **needs_review: 2** (Q01, Q05)
- **reject: 2** (Q03, Q08)

### 전체(18건, carry-forward 포함)
- source_confirmed 6 · needs_review 5 (Q01·Q05·Q12·Q13·Q14) · reject 2 (Q03·Q08) · hold 5 (Q09·Q15·Q16·Q17·Q18)

### source_confirmed 중 "신규 relation 가치"
- **신규 relation 후보**: Q06(FQ×아연 4행)·Q07(테트라×아연 2행)·Q10(클로르탈리돈×K/Mg 2행)·Q11(인다파미드×K/Mg 2행)·Q04(비스포 enrichment 4행: 리세/이반×철·Mg).
- **신규 relation 아님(인덱스/alias 트랙)**: Q02(오메프라졸은 13/14 이미 라이브).

---

## 5. 금지 / 안전 준수 (확인)

- ✅ **relations 는 41 그대로.** export/full index/alias/src/validator/smoke/integrate/DATA_URL/.github 변경 0. **이번에 구현 0건.**
- ✅ 전 후보 `do_not_implement_yet=true`. 어떤 것도 라이브 flip/승격하지 않음.
- ✅ "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 없음. 제품·제휴·복용지시·추천 톤 없음. published/clinical_reviewed false.
- ✅ source_confirmed 는 전부 실제 fetch한 허가사항 itemSeq + 상호작용/주의/이상반응 문맥 증거 스니펫 보유(첨가제 문맥 아님).
- ✅ 칼륨 후보(Q10/Q11)는 승격 시 칼륨 안전정책(`product_link_allowed=false`·`potassium_safety_card=true`) 승계 선행 조건 명시(draft 에 반영).
- ✅ Q05 계열 일반화 금지(세프디니르 성분특이), Q16 영구 금지 준수.
