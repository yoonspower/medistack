# MediStack — A티어 Top10 relation 후보 출처 확인 (Source Verification)

> 작성일: 2026-06-13. 기준 HEAD `9b73fc4` 이후. **출처 존재 여부만 확인한다 — relation 을 추가/승격하지 않고, 데이터/렌더를 한 줄도 변경하지 않는다.**
>
> 재현: `python3 scripts/verify_atier_relation_sources.py` (읽기 전용 + nedrug fetch). 결과 CSV: `data/relation_source_verification_atier_v1_1.csv`.
> 입력 후보: `MediStack_relation_expansion_priority_plan.md` 의 A티어 Top10(E01–E10). 출처: MFDS nedrug 허가사항 `getItemDetail`.

---

## 0. 범위와 한계

- 본 단계는 A티어 Top10 후보의 제안 nutrient 테마가 **식약처 허가사항(nedrug) 원문에 실재하는지** 만 확인한다. relation 작성·승격·데이터 변경은 하지 않는다.
- 분류: `source_confirmed`(허가사항 상호작용/주의에 신호 존재) / `needs_review`(부분·모호) / `missing`(fetch 품목에 신호 없음) / `reject`(테마가 근거와 어긋남).
- **출처가 약하면 과감히 missing/needs_review.** 신호어는 첨가제·우연 언급과 구분되는 특정어(저마그네슘·시아노코발라민·다가 양이온·철분제제 등)로만 매칭하고 증거 스니펫을 캡처한다.
- "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현 금지. 제품추천·복용지시·영양제 추천 문구 금지(허가사항 원문 인용만). `published`/`clinical_reviewed` = false 유지.

---

## 1. 방법

- 후보 성분별 **단일성분 경구제 대표 품목 2~3건**의 `getItemDetail` HTML 을 fetch → 태그 제거 → 정규화 후 신호어 검색.
- 한 후보의 ≥1 품목에서 신호어가 상호작용/주의 문맥에 잡히면 그 nutrient 를 `source_confirmed`. 전 품목에 없으면 `missing`.
- 신호어 정의:

| 테마 | 신호어(특정) | 첨가제/우연 배제 |
|---|---|---|
| 마그네슘(고갈) | `저마그네슘`(저마그네슘혈증) | 산화마그네슘·스테아르산마그네슘 등 첨가제 배제 |
| 비타민B12(고갈) | `시아노코발라민` 또는 `B12`+흡수 문맥 | 흡수/흡수장애 문맥 요구 |
| 칼슘·철·Mg(흡수, 비스포) | `다가 양이온` / `제산제` | 상호작용 문맥 |
| 철분(흡수, 세팔로) | `철` + (흡수/병용/적색 대변) | 착색용 산화철 배제 |

---

## 2. 결과 요약

| 분류 | 후보(×nutrient) | candidate |
|---|---|---|
| **source_confirmed** | 11행 | **E01·E02·E03·E04·E05·E06·E08 (7후보)** |
| missing | 3행 | E07·E09·E10 (H2 차단제 × B12) |
| needs_review | 0 | — |
| reject | 0 | — |

→ **다음 relation 승격 검토 대상(promote_eligible=true): E01·E02·E03·E04·E05·E06·E08 (7후보).**
→ 보류/제외: E07·E09·E10 — 한국 허가사항에 B12 기재 없음(문헌 전용) → 현 허가사항-우선 source gate 미통과.

---

## 3. 후보별 출처 확인 (증거)

> 전체 증거·source_url·found_item_seqs 는 `data/relation_source_verification_atier_v1_1.csv`. 아래는 대표 인용(허가사항 원문).

### ✅ source_confirmed (승격 검토 대상)

| id | 성분 | nutrient | 방향 | 허가사항 원문 근거(요약 인용) |
|---|---|---|---|---|
| E01 | 라베프라졸 | 마그네슘 | depletion | "드물게 **저마그네슘혈증** … 보고" |
| E01 | 라베프라졸 | 비타민B12 | depletion | "이 약의 장기투여로 인해 저염산증/무위산증에 의해 **비타민 B12(시아노코발라민) 흡수장애**가 나타날 가능성" |
| E02 | 판토프라졸 | 마그네슘 | depletion | "저나트륨혈증, **저마그네슘혈**, CK 상승 …" |
| E02 | 판토프라졸 | 비타민B12 | depletion | "장기간 투여시 저염산증/무위산증에 의해 **비타민 B12(cyanocobalamin) 흡수장애**" |
| E03 | 란소프라졸 | 마그네슘 | depletion | "대사 및 영양계 : **저마그네슘혈증**" |
| E03 | 란소프라졸 | 비타민B12 | depletion | "**시아노코발라민(비타민B12)결핍** : 위산 억제 약물을 장기간(3년 이상) … 흡수장애" |
| E05 | 덱스란소프라졸 | 마그네슘 | depletion | "대사 및 영양 장애: **저마그네슘혈증**, 저나트륨혈증" |
| E05 | 덱스란소프라졸 | 비타민B12 | depletion | "**시아노코발라민(비타민B12) 결핍** : 위산 억제약물 장기간 … 흡수장애" |
| E04 | 리세드론산 | 칼슘·철·Mg(다가양이온) | absorption | "**다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)**을 함유한 약물 … 이 약의 **흡수를 방해** … 동시 투여 말 것" |
| E06 | 이반드론산 | 칼슘·철·Mg(다가양이온) | absorption | "상호작용: 우유, 음식물, 칼슘, **다가 양이온(알루미늄, 마그네슘, 철)** … 이 약의 **흡수를 저해**" |
| E08 | 세프디니르 | 철분 | absorption | "상호작용: **철분제제와 함께 복용하면 이 약의 흡수를 약 1/10까지 저해** … 3시간 이상 간격" |

> E01–E05(PPI): 기존 오메프라졸 relation 13(B12)·14(Mg)와 **동일 약효군·동일 출처 패턴** 재현 — 안전선 그대로 승계 가능. Mg·B12 둘 다 confirmed.
> E04·E06(경구 비스포스포네이트): 기존 알렌드론산 relation 29(칼슘 흡수)와 동일 계열. 라벨이 칼슘·마그네슘·철을 **다가 양이온**으로 묶어 기술 → 후보 nutrient 테마와 일치.
> E08(세프디니르): 철분 흡수 저해가 라벨 상호작용에 명시(정량 "1/10")—기존 항생제 흡수 패턴과 동일 성격, 계열만 신규.

### ⚠️ missing (보류 — 승격 부적격)

| id | 성분 | nutrient | 확인 결과 |
|---|---|---|---|
| E07 | 파모티딘 | 비타민B12 | fetch 2품목 라벨에 B12/시아노코발라민/비타민 **0회** — 허가사항 미기재 |
| E09 | 라푸티딘 | 비타민B12 | fetch 3품목 라벨에 B12 관련 표기 **0회** — 허가사항 미기재 |
| E10 | 니자티딘 | 비타민B12 | fetch 3품목 라벨에 B12 관련 표기 **0회** — 허가사항 미기재 |

> H2 차단제 × B12 는 위산억제 기전상 가설은 성립하나 **한국 허가사항에 기재되어 있지 않다**(문헌 전용). MediStack 의 source gate 는 허가사항 우선이므로 **현 단계 승격 부적격**. 향후 별도로 신뢰 가능한 이차출처를 source 정책에 명시적으로 허용하는 결정이 없으면 채택하지 않는다. (테마 자체가 틀린 것은 아니므로 reject 가 아니라 missing.)

---

## 4. 승격 검토 대상 (다음 단계 입력)

source_confirmed 7후보만 다음 relation 승격 검토 단계로 넘긴다. **단, 출처 확인 = 승격이 아니다.** 실제 relation 작성은 별도 단계(데이터 변경·PM 승인)에서 다음을 추가로 통과해야 한다.

1. **문구 안전성**: display_text/management 를 참고정보 톤("줄어들 수 있다/간격 권장/상담하세요")으로만. 복용지시·제품권유 0건.
2. **출처 고정**: 각 relation 에 확인된 `item_seq` + nedrug URL + 확인일을 source 로 고정(기존 relation 30 형식 승계). 본 CSV 의 `found_item_seqs`/`source_url` 사용.
3. **칼륨 정책**: 본 7후보에는 칼륨 테마 없음(해당 없음). 향후 치아지드(E11·E12) 승격 시에만 칼륨 안전 정책 승계 필요.
4. **clinical/published 봉인 유지.** candidate→relation 변환은 PM 승인 게이트.

승격 시 예상 신규 relation(검토 대상, 미확정):

| 후보 | 예상 relation(기존 패턴 승계) | 비고 |
|---|---|---|
| E01 라베프라졸 | ×B12(depletion), ×Mg(depletion) | 오메프라졸 13·14 형식 |
| E02 판토프라졸 | ×B12, ×Mg | 〃 |
| E03 란소프라졸 | ×B12, ×Mg | 〃 |
| E05 덱스란소프라졸 | ×B12, ×Mg | 〃 |
| E04 리세드론산 | ×칼슘(±철·Mg) absorption | 알렌드론산 29 형식 |
| E06 이반드론산 | ×칼슘(±철·Mg) absorption | 〃 |
| E08 세프디니르 | ×철분 absorption | 신규 계열, 출처 강함 |

---

## 5. 다음 단계 프롬프트 초안

```
[옵션 A] source_confirmed 7후보(E01–E06·E08) 중 1순위군부터 relation 실제 작성 (PM 승인·데이터 변경 단계)
  - 새 버전 export(또는 relation append) + 새 validator(절대불변원칙) + relation_card 재생성.
  - 각 relation source = 본 CSV found_item_seqs + nedrug URL + 확인일(2026-06-13)로 고정.
  - display_text/management 참고정보 톤, disclaimer 승계, 문구 안전성 리뷰 동반.
  - relation 30 → +N (PPI 8 + 비스포 2~4 + 세프디니르 1 범위), 기존 30 불변(추가만).
[옵션 B] 문구 안전성 사전 리뷰만 먼저(데이터 무변경): 7후보 display_text 초안 작성 → 적대 리뷰.
[옵션 C] E07·E09·E10(H2×B12) source 정책 결정: 허가사항 외 이차출처 허용 여부(미허용 시 영구 보류).
```

---

## 6. 금지 / 안전 (본 단계)

relation 추가·수정 / full index·alias·export·src 수정 / DATA_URL 변경 / source gate·disclaimer 변경 / `published`·`clinical_reviewed` true / candidate→relation 승격 / 제품·구매·제휴·영양제 추천 / 신규 태그 / `scripts/__pycache__` 커밋 — **전부 금지.** 본 단계는 출처 확인·문서·CSV 까지만.
