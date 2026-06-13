# MediStack — relation 확장 초안 v1.2 (DRAFT · 미구현)

> 작성일: 2026-06-14. **초안(DRAFT)일 뿐 라이브가 아니다.** 라이브 export 의 **relations 는 41 그대로**이며, 본 초안의 어떤 행도 구현/승격/flip 되지 않았다.
> 데이터 파일: `data/relation_expansion_draft_v1_2.json` (14 draft_relations, 전건 `published=false`·`clinical_reviewed=false`·`review_required=true`·`source_required=true`·`do_not_implement_yet=true`).
> 근거: `docs/MediStack_source_queue_top10_verification_v1_2.md` / `data/source_queue_top10_verification_v1_2.csv` 의 **source_confirmed** 후보만 초안화.

---

## 1. 무엇이고 무엇이 아닌가

- **이것은:** 허가사항 상호작용/주의/이상반응 문맥에 신호어가 실재함을 확인한(source_confirmed) 후보의 **초안 relation 행**. PM 승인 + 검토 통과 후 별도 단계에서만 라이브 승격 검토 대상.
- **이것이 아닌 것:** 구현 지시 아님. "이 관계가 확정 사실"이라는 단정 아님. export/full index/alias/src 변경 아님. 라이브 relation_card flip 아님.
- draft_id(D01–D14)는 **라이브 id 공간과 분리**(라이브는 1–42). 승격 시 별도 id 재배정.

---

## 2. 초안 14행 요약

| draft_id | 큐 | 성분 | nutrient | 기전/액션 | 칼륨안전 | 비고 |
|---|---|---|---|---|---|---|
| D01 | Q06 | 레보플록사신 | 아연 | absorption/separation | – | 신규 |
| D02 | Q06 | 시프로플록사신 | 아연 | absorption/separation | – | 신규 |
| D03 | Q06 | 오플록사신 | 아연 | absorption/separation | – | 신규 |
| D04 | Q06 | 목시플록사신 | 아연 | absorption/separation | – | 신규 |
| D05 | Q07 | 독시사이클린 | 아연 | absorption/separation | – | 신규 |
| D06 | Q07 | 미노사이클린 | 아연 | absorption/separation | – | 신규 |
| D07 | Q04 | 리세드론산 | 철분 | absorption/separation | – | enrichment(칼슘 relation40 존재) |
| D08 | Q04 | 리세드론산 | 마그네슘 | absorption/separation | – | enrichment |
| D09 | Q04 | 이반드론산 | 철분 | absorption/separation | – | enrichment(칼슘 relation41 존재) |
| D10 | Q04 | 이반드론산 | 마그네슘 | absorption/separation | – | enrichment |
| D11 | Q10 | 클로르탈리돈 | 칼륨 | depletion/monitoring | **✔ 필수** | 신규, product_link_allowed=false |
| D12 | Q10 | 클로르탈리돈 | 마그네슘 | depletion/monitoring | – | 신규 |
| D13 | Q11 | 인다파미드 | 칼륨 | depletion/monitoring | **✔ 필수** | 신규, product_link_allowed=false |
| D14 | Q11 | 인다파미드 | 마그네슘 | depletion/monitoring | – | 신규 |

> **초안에서 제외(정직성):**
> - Q02(오메프라졸 잔여 B12/Mg): source_confirmed이나 **relation13(B12)·14(Mg) 이미 라이브** → 신규 relation 아님. 인덱스/alias 트랙(PM 승인).
> - Q03(알렌드론산 Ca/Fe/Mg)·Q08(레보티록신 Mg): 허가사항 미기재 → reject.
> - Q01(에스오메 index-track)·Q05(세팔로 class 일반화 위험): needs_review.
> - Q09/Q12–Q18: hold/needs_review(carry-forward).

---

## 3. 증거 스니펫 (load-bearing)

- **D01–D04 (FQ×아연)** — 레보(itemSeq 201207060): *"아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하"*; 목시(201309618): *"철 또는 아연을 포함하는 제제는 이 약의 흡수를 감소시키므로…4시간 전이나 8시간 후"*. 시프로(200403053)·오플록사신(199602013) 동일 패턴.
- **D05–D06 (테트라사이클린×아연)** — 독시(201403031)·미노(202500078): *"철·아연을 함유하고 있는 제제…에 의해 테트라사이클린계 약물의 흡수가 저하"*.
- **D07–D10 (비스포×철/Mg)** — 리세(201903166): *"다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 약물…은 이 약의 흡수를 방해"*; 이반(201306285): *"칼슘, 다가 양이온(예, 알루미늄, 마그네슘, 철)들을 포함한 제품들은 이 약의 흡수를 저해"*.
- **D11–D12 (클로르탈리돈×K/Mg)** — 클로베네정(202500118): *"주로 고용량에서의 저칼륨혈증…저마그네슘혈증"* + 금기 *"불응성 저칼륨혈증 환자"*.
- **D13–D14 (인다파미드×K/Mg)** — 나트릭스서방정(199900835): *"저칼륨혈증(혈장칼륨<3.4mmol/l)이 환자의 10%에서 나타났으며"* + *"흔하게 저칼륨혈증…저마그네슘혈증"*.

전 행 source.url + source.pointer 에 실제 itemSeq + 문맥 포인터 + checked_at 2026-06-14 기재.

---

## 4. 톤 / 안전 준수 (확인)

- ✅ 참고정보 톤: "가능성이 있습니다", "약사 또는 의사와 상담하세요". **"드시라/피하라/추천/복용하세요" 류 없음.**
- ✅ 제품/구매/제휴 필드·예시 없음.
- ✅ 칼륨 행(D11·D13): `product_link_allowed=false` + `potassium_safety_card=true` + "칼륨은 임의로 보충하면 위험할 수 있으므로…상담" 고지 승계.
- ✅ 전 행 `published=false`·`clinical_reviewed=false`·`do_not_implement_yet=true`. **라이브 relations 41 불변, 구현 0건.**

---

## 5. 승격 시 선행 조건 (참고 — 본 단계에서 수행 안 함)

1. PM 승인 + (가능 시) clinical reviewer 검토.
2. 신규 데이터 = 신규 버전 파일 + 신규 validator (v0.1 봉인 원칙).
3. 칼륨 행 안전정책 코드 경로 확인(product_link_allowed=false·potassium_safety_card=true 렌더 가드).
4. CI 전체세트(validate v0.2 / surface-forms / potassium selftest) 로컬 선실행.
5. Q06/Q07/Q10/Q11 신규 relation + Q04 enrichment 행만 대상. Q02 는 relation 아닌 인덱스/alias 트랙.
