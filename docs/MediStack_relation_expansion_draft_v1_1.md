# MediStack — relation 확장 draft v1.1 (source_confirmed 7후보)

> 작성일: 2026-06-13. 기준 HEAD `559fb43` 이후. **DRAFT — 라이브 미반영.** v0.2 export·full index·alias·DATA_URL·src 를 한 줄도 변경하지 않는다.
>
> 산출: `data/relation_expansion_draft_v1_1.json` (relation 41 = 기존 30 verbatim + 신규 11). 생성기 `scripts/build_relation_expansion_draft_v1_1.py`, 전용 validator `scripts/validate_relation_expansion_draft_v1_1.py`(21/21 PASS).
> 근거: `MediStack_relation_source_verification_atier.md` (A티어 Top10 허가사항 출처 확인). 후보: `MediStack_relation_expansion_priority_plan.md`.

---

## 0. 범위와 한계

- 본 단계는 source_confirmed 7후보(E01–E06·E08)의 relation 11건을 **별도 draft 파일로만 작성**한다. **라이브(DATA_URL=v0.2)·full index·alias 는 무변경**이라 실제 사용자 노출/relation_card 증가는 없다.
- 기존 relation 30(ids 1–14,16–31)은 **dict-equal 로 불변**(핵심자산 훼손 0). 신규는 ids 32–42 추가만.
- missing 3후보(E07/E09/E10 파모티딘·라푸티딘·니자티딘 H2×B12)와 에스오메프라졸은 **신규에 절대 미포함**.
- 모든 문구는 허가사항 원문 근거의 **참고정보 톤**(복용지시·영양제/제품 추천·진단·처방 표현 0). `published`/`clinical_reviewed`/`live` = false.

---

## 1. 신규 relation 11건 (ids 32–42)

> 기존 톤 미러링: depletion=오메프라졸 13·14 / absorption=알렌드론산 29. 출처=허가사항(nedrug getItemDetail) 확인일 2026-06-13.

| id | 성분 | nutrient | mechanism | action | evidence | 후보 |
|---|---|---|---|---|---|---|
| 32 | 라베프라졸 | 비타민B12 | depletion | monitoring | moderate | E01 |
| 33 | 라베프라졸 | 마그네슘 | depletion | monitoring | moderate | E01 |
| 34 | 판토프라졸 | 비타민B12 | depletion | monitoring | moderate | E02 |
| 35 | 판토프라졸 | 마그네슘 | depletion | monitoring | moderate | E02 |
| 36 | 란소프라졸 | 비타민B12 | depletion | monitoring | moderate | E03 |
| 37 | 란소프라졸 | 마그네슘 | depletion | monitoring | moderate | E03 |
| 38 | 덱스란소프라졸 | 비타민B12 | depletion | monitoring | moderate | E05 |
| 39 | 덱스란소프라졸 | 마그네슘 | depletion | monitoring | moderate | E05 |
| 40 | 리세드론산 | 칼슘 | absorption | separation | high | E04 |
| 41 | 이반드론산 | 칼슘 | absorption | separation | high | E06 |
| 42 | 세프디니르 | 철분 | absorption | separation | high | E08 |

- **문구(예)**: depletion — "{성분}을(를) 장기간 복용하는 경우 {영양소} 상태에 영향이 있을 수 있다는 보고가 있어, 상태 확인이 필요할 수 있습니다." / absorption — "{성분}과(와) {영양소}이(가) 함유된 제품을 같은 시간에 복용하면 {성분}의 흡수가 줄어들 수 있습니다." (전부 기존 relation 문구와 동일 패턴, 복용지시/제품권유 아님)
- **출처(예)**: id33 라베프라졸×Mg = "경보라베프라졸정10mg(itemSeq 201405854) / 이상반응 / 드물게 저마그네슘혈증 / 확인일 2026-06-13". id42 세프디니르×철분 = "세프다나캡슐100밀리그램(itemSeq 200711458) / 상호작용 / 철분제제 병용 시 흡수 약 1/10 저해·3시간 간격 / 확인일 2026-06-13". 전건 source.pointer 에 품목·itemSeq·섹션·확인일 고정.

### 비스포스포네이트 ×칼슘 단독 결정

리세드론산·이반드론산 허가사항은 "다가 양이온(칼슘·마그네슘·철)"을 포괄 기술하나, 신규 relation 은 **기존 알렌드론산 relation 29(×칼슘) 패턴과 일관되게 ×칼슘 단독**으로 둔다(보수적·동일 약효군 일치). source.pointer 에 "라벨상 칼슘·철·마그네슘 포괄"을 명시 — 철·마그네슘 확장은 향후 별도 검토.

---

## 2. 통합 시 relation_card 증가 (예측 — 이번 단계 실제 증가 0)

> **full index 무변경 → 실제 relation_card = 558 유지.** 아래는 라이브 통합(별도 PM 게이트) 시 예측치.

| 성분 | name_only(substring) | 단일성분 |
|---|---|---|
| 라베프라졸 | 216 | 174 |
| 리세드론산 | 118 | 76 |
| 이반드론산 | 73 | 72 |
| 란소프라졸 | 55 | 43 |
| 판토프라졸 | 45 | 45 |
| 세프디니르 | 8 | 8 |
| 덱스란소프라졸 | 4 | 4 |
| **합계** | **519** | **422** |

→ 통합 시 relation_card **558 → 558+422(단일성분) ~ 558+519(substring 포함)** 예측. **이번 단계는 558 그대로.**

---

## 3. 검증

- 전용 draft validator `validate_relation_expansion_draft_v1_1.py`: **21/21 PASS** (기존 30 dict-equal·신규 enum/필수필드·requires_clinical_review=false·출처·참고정보 톤·헤지·금지성분 미승격·라이브 무변경).
- 기존 validator/smoke 전종 **PASS**(라이브 자산 무변경): v0.2 export·full index·potassium policy·search regression·disclaimer render·v0.3 aliases.
- 보호파일 md5 불변: full index `654d3e85`·export `401b097a`·aliases `03fb2137`. DATA_URL=`./data/medistack_v0.2_beta_export.json` 유지.
- **적대 3차원 리뷰 반영(blocker0/major0/minor4)**: ①PPI×Mg evidence high→**moderate**(캡처 근거가 모니터링 경고가 아닌 이상반응 나열 → HCTZ#20·자체 B12=moderate와 일관) ②Mg pointer의 '(PPI 장기투여)' 가공 문구 제거(이상반응 섹션 충실 인용) ③PPI×B12 display 표기 '비타민 B12'(공백) baseline(id12/13) 파리티, nutrient 필드는 '비타민B12'(무공백) baseline 동일 유지 ④세프디니르(모음종결) 조사 '와(과)' 자연형 적용.

---

## 4. 라이브 통합 게이트 (다음 단계·별도 PM 승인)

draft → 라이브는 다음을 한 번에 수행하는 별도 단계다(데이터·검증 상수 연쇄 변경):

1. **relations 반영**: 신규 11건을 v0.2 export 에 병합(또는 새 버전 export + DATA_URL flip). meta.relation_count 30→41.
2. **alias pool 확장**: 7성분의 검증 item_seq 를 `verified_item_seqs`/`product_aliases` 에 추가(relation_card pool 진입). alias 검증 상수(alias_count·product·verified) 갱신.
3. **full index flip**: 7성분 해당 품목을 name_only→relation_card(covered_by_relation=true·no_relation_notice_required=false). relation_card 558→+422~519.
4. **validator 상수 갱신**: full index validator(relations 30→41·CANONICAL 13→20·alias/verified 상수)·v0.2 export validator(relation_count)·alias validator.
5. **회귀 전종 PASS + 문구 안전성 재리뷰 + 칼륨 정책(해당 없음)** 후 deploy.

> 통합은 라이브 핵심자산 대규모 변경이라 **반드시 별도 PM 게이트**. 본 draft 는 그 입력(검증된 relation + 출처 고정)이다.

---

## 5. 금지 / 안전 (본 단계)

기존 relation 30 훼손 / v0.2 export·full index·alias·DATA_URL·src 변경 / missing 3후보(H2×B12) 승격 / 에스오메프라졸 신규 추가 / `published`·`clinical_reviewed`·`live` true / 제품·구매·제휴·영양제 추천 문구 / 복용지시·진단·처방 표현 / 신규 태그 / `scripts/__pycache__` 커밋 — **전부 금지.** 본 단계는 draft 파일·생성기·validator·문서까지만.
