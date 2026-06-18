# PR-2 chronic8 — PM-reviewed verified-reference integration note (v1.4)

> 이 문서는 **PM-reviewed verified-reference integration note** 이다. **임상 검수(clinical review)가 아니다.**
> published=false / clinical_reviewed=false / reviewed_by 공란 을 그대로 유지한다.
> 통합 등급 = verified_reference (천장). 사용자 노출 문구에 검수 완료 단정·전문가 확인 단정·
> 식약처 무이슈 단정·복용 권유 단정 같은 표현을 추가하지 않는다.

검토자(PM): PM-LIVEPR-002 (PM-reviewed, 별도 AI PM 세션)   검토일 2026-06-18   검토시각 2026-06-18 09:20 KST
검토 패키지: f9_chronic_depletion v1.4 + f4_f6_f10_small_family v1.4(F6 only) / base commit 1a354d0
target branch: live/pr2-chronic8
wave: PR-2 chronic8

## PM approval tokens
- PM_REVIEWED_VERIFIED_REFERENCE_ONLY
- NO_CLINICAL_REVIEW_CLAIM
- NO_PRODUCT_UI
- NO_SCHEDULE
- PR2_CHRONIC8_84_TO_92

## scope (8건 = F9 7 + F6 1)
- F9 만성복용 depletion × 엽산/비타민D: 7건 (엽산 3 + 비타민D 4)
- F6 에스오메프라졸 × 비타민B12 (depletion·monitoring): 1건

scope(wave=chronic8) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.

### 승인 candidate_id 전건 (8건)
[F9 — 엽산 depletion] (3)
  - RF-F9-0269  설파살라진 × 엽산
  - RF-F9-0272  트리메토프림 × 엽산
  - RF-F9-0242  페니토인 × 엽산
[F9 — 비타민D depletion] (4)
  - RF-F9-0246  카르바마제핀 × 비타민D
  - RF-F9-0252  페노바르비탈 × 비타민D
  - RF-F9-0243  페니토인 × 비타민D
  - RF-F9-0255  프리미돈 × 비타민D
[F6 — 에스오메프라졸 × 비타민B12] (1)
  - RF-F6-0201

## relation count
relation delta: +8 (84 → 92, 신규 id = runtime max+1 = 86..93).

## grouping
grouping 승인: chronic8 wave 단위 한 번에 통합. (rollback 단위 = 본 wave.)

## source fidelity
출처(source) fidelity: 식약처 허가사항(nedrug getItemDetail) 인용과 일치 보존 확인. 비공식/쇼핑몰/블로그 출처 0건.
F9 7건 + F6 1건 전건 itemSeq + 인용(source quote) 보존.

## display copy_change (source fidelity · PR-2 copy 원칙)
F9/F6 = 만성복용 depletion(영양소 결핍/감소) 모니터링 계열. PR-2 copy 원칙 반영(copy_change·reframe):
- 엽산·비타민D·B12 '수치 저하' 는 원문(허가사항)이 직접 말하지 않으면 단정하지 않음(수치 단정 회피).
  display 에서 '수치 변화 / 수치가 걱정되면' 표현을 '관련된 허가사항 주의 문구 / 증상이 걱정되면' 으로 보수 reframe(F9 display 7건 통일).
- 비타민D 항전간제(페노바르비탈·페니토인·프리미돈)는 라벨이 연용 골연화증·구루병 + 비타민D 섭취·투여(remedy)만 적시 →
  골연화증·구루병 등 골질환 alarm phrase 는 사용자 display 에 비노출, '비타민D와 관련된 주의 문구' 수준으로 보수화.
- F6 에스오메프라졸×B12 display 는 live PPI×B12 표준 템플릿(상태 영향·상태 확인) 으로 정합.
record: data/review/pr2_chronic8_display_copy_change_v1_4.json

## management copy
관리 문구(management copy): 참고·문의 톤 보수성 유지 확인. '장기 복용 중이라면 정기 진료나 복약 상담 시 해당
영양소 상태 확인이 필요한지 문의해볼 수 있습니다' 수준(모니터링 톤)으로 8건 통일. 검사 지시나 복약 지시가
아니며 영양제 복용을 권유하지 않음. 원문(허가사항)보다 강한 표현 없음 확인.

## 보호 상태 유지 승인
published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.
제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.
통합 등급 천장 = verified_reference. 임상 검수 완료 아님.

## 제외 확인
needs_review 후보(RF-F9-0245 카르바마제핀×엽산, RF-F10-0275 케토코나졸, RF-F3-0148, RF-F3-0149)는 본 승인에서 제외.
F3/F4 family 후보는 PR-2 제외(PR-3 small2 92→94 에서 별도 처리).
RF-F9-0245(카르바마제핀×엽산)은 저신호 이상반응 열거로 needs_review 이며 본 wave 에서 제외 인지함.
(카르바마제핀은 ×비타민D RF-F9-0246 으로 coverage 유지 → 약물 누락 아님.)
PR-1 antibiotic24 후보(F1/F2/add-on)는 이미 live → 재추가/재통합 금지(중복 0) 확인.

## rollback
rollback 가능(wave 단위 git revert <PR2_COMMIT> 또는 pre-live tag reset) 확인.

## 비고 (정책)
- 이 통합은 "PM-reviewed verified-reference integration" 이며 임상 검수 완료 아님.
- 사용자/앱/문서 어디에도 의료 단정·복약 지시·구매 유도 문구를 추가하지 않음.
- MediStack 은 식약처 허가사항 기반 약-영양소 참고정보(베타)이며 복약 안내가 아님.
