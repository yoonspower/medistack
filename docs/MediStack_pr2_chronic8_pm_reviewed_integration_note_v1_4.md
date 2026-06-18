# MediStack v1.4 — PR-2 chronic8 PM-reviewed verified-reference integration note (handoff)

이 문서는 PR-2 chronic8 live 통합의 PM-reviewed verified-reference 통합 노트 핸드오프본이다.
기계 검증용 단일 진실원은 다음 두 파일이며, 본 문서는 사람 검토자용 요약이다.
- `data/review/pr2_chronic8_pm_reviewed_note_v1_4.md` (checker 입력)
- `data/review/pr2_chronic8_candidate_lock_v1_4.json` (candidate lock)

## 핵심
- **PM-reviewed verified-reference integration** 이며 **임상 검수(clinical review)가 아니다.**
- published=false / clinical_reviewed=false / reviewed_by 공란 **유지**.
- relation_count **84 → 92** (delta +8, 신규 id 86..93 = runtime max+1).
- 통합 등급 천장 = verified_reference.

## scope (8건)
| family | 약물 × 영양소 | mechanism/action | candidate_id |
|---|---|---|---|
| F9 엽산 | 설파살라진 × 엽산 | depletion/monitoring | RF-F9-0269 |
| F9 엽산 | 트리메토프림 × 엽산 | depletion/monitoring | RF-F9-0272 |
| F9 엽산 | 페니토인 × 엽산 | depletion/monitoring | RF-F9-0242 |
| F9 비타민D | 카르바마제핀 × 비타민D | depletion/monitoring | RF-F9-0246 |
| F9 비타민D | 페노바르비탈 × 비타민D | depletion/monitoring | RF-F9-0252 |
| F9 비타민D | 페니토인 × 비타민D | depletion/monitoring | RF-F9-0243 |
| F9 비타민D | 프리미돈 × 비타민D | depletion/monitoring | RF-F9-0255 |
| F6 | 에스오메프라졸 × 비타민B12 | depletion/monitoring | RF-F6-0201 |

## PR-2 copy 원칙(반영됨)
1. 영양소 '수치 저하' 는 원문이 직접 말하지 않으면 단정하지 않는다(수치 단정 회피). F9 display 7건은
   '수치 변화/수치가 걱정되면' → '관련된 허가사항 주의 문구/증상이 걱정되면' 으로 통일 reframe.
2. 비타민D 항전간제는 라벨이 연용 골연화증·구루병 + 비타민D remedy 만 적시 → 골질환 alarm phrase 는 display 비노출.
3. management 는 8건 통일: "장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지
   문의해볼 수 있습니다." (검사/복약 지시 아님·영양제 복용 권유 아님).
4. F6 display 는 live PPI×B12 표준 템플릿(상태 영향·상태 확인)으로 정합.

## 제외
- needs_review: RF-F9-0245(카르바마제핀×엽산·저신호 이상반응 열거), RF-F10-0275(케토코나졸·route/availability),
  RF-F3-0148/0149(에티드론산·cation 결속).
- F3/F4 family → PR-3 small2(92→94) 별도.
- PR-1 antibiotic24(F1/F2/add-on) → 이미 live, 재추가 금지.

## PM approval tokens
PM_REVIEWED_VERIFIED_REFERENCE_ONLY · NO_CLINICAL_REVIEW_CLAIM · NO_PRODUCT_UI · NO_SCHEDULE · PR2_CHRONIC8_84_TO_92
