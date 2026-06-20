# PR-3 small2 — PM-reviewed verified-reference integration note (v1.4)

> 이 문서는 **PM-reviewed verified-reference integration note** 이다. **임상 검수(clinical review)가 아니다.**
> published=false / clinical_reviewed=false / reviewed_by 공란 을 그대로 유지한다.
> 통합 등급 = verified_reference (천장). 사용자 노출 문구에 검수 완료 단정·전문가 확인 단정·
> 식약처 무이슈 단정·복용 권유 단정 같은 표현을 추가하지 않는다.

검토자(PM): PM-LIVEPR-003 (PM-reviewed, 별도 AI PM 세션)   검토일 2026-06-18   검토시각 2026-06-18 10:00 KST
검토 패키지: f3_bisphosphonate v1.4 + f4_f6_f10_small_family v1.4(F4 only) / base commit 3200edc
target branch: live/pr3-small2
wave: PR-3 small2

## PM approval tokens
- PM_REVIEWED_VERIFIED_REFERENCE_ONLY
- NO_CLINICAL_REVIEW_CLAIM
- NO_PRODUCT_UI
- NO_SCHEDULE
- PR3_SMALL2_92_TO_94

## scope (2건 = F3 1 + F4 1)
- F3 이반드론산 × Al/Mg 함유 제산제(약물): 1건 (absorption/separation · al_mg_antacid)
- F4 레보티록신 × 알루미늄 함유 제산제(약물): 1건 (absorption/separation · al_mg_antacid)

scope(wave=small2) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.

### 승인 candidate_id 전건 (2건)
  - RF-F3-0147  이반드론산 × Al/Mg 함유 제산제(약물)
  - RF-F4-0173  레보티록신 × 알루미늄 함유 제산제(약물)

## relation count
relation delta: +2 (92 → 94, 신규 id = runtime max+1 = 94..95).

## grouping
grouping 승인: small2 wave 단위 한 번에 통합. (rollback 단위 = 본 wave.)

## source fidelity
출처(source) fidelity: 식약처 허가사항(nedrug getItemDetail) 인용과 일치 보존 확인. 비공식/쇼핑몰/블로그 출처 0건.
F3 1건 + F4 1건 전건 itemSeq + 인용(source quote) 보존.

## display copy_change (source fidelity · PR-3 copy 원칙)
F3/F4 = absorption/separation · al_mg_antacid(drug counterpart). copy_change·reframe 반영:
- 이반드론산(RF-F3-0147): 인용은 흡수저하 사실만 진술(FACT-only·복용 시점 분리 등 타이밍 안내 미명시) → display 의 라벨귀속
  '복용 시점을 분리하도록 안내하고 있으니' **단정 제거**(reframe), '함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와
  상담하세요' 로 보수 유도. 기존 live al_mg_antacid 선례(PR-1 F1/F2 18건·id61)와 동형. relation/action(separation) 불변.
- 레보티록신(RF-F4-0173): 라벨이 알루미늄 함유 제산제만 명시(Mg 미명시) → counterpart 를 '알루미늄 함유 제산제'로 한정(Al-only·
  Mg 비단정). 인용에 '투여간격에 주의' 가 있어 복용 시점 분리에 대한 상담 유도는 라벨 근거 있음 → '복용 시점 분리에 대해
  약사 또는 의사에게 확인' 유지.
record: data/review/pr3_small2_display_copy_change_v1_4.json

## management copy
관리 문구(management copy): 참고·상담 톤 보수성 유지 확인. 복용 시간 분리는 MediStack 제안 수준(약사 또는 의사와 상담)
이며 복약 지시가 아님. 원문(허가사항)보다 강한 표현 없음 확인.

## 보호 상태 유지 승인
published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.
제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.
통합 등급 천장 = verified_reference. 임상 검수 완료 아님.

## 제외 확인
needs_review 후보(RF-F3-0148, RF-F3-0149 에티드론산, RF-F9-0245 카르바마제핀×엽산, RF-F10-0275 케토코나졸)는 본 승인에서 제외.
에티드론산(RF-F3-0148/0149)은 cation 결속 parse 미확정으로 needs_review 이며 본 wave 제외 인지함.
F1/F2(PR-1)·F6/F9(PR-2)·F10 family 후보는 PR-3 제외. PR-1 antibiotic24·PR-2 chronic8 후보는 이미 live → 재추가/재통합 금지(중복 0) 확인.

## rollback
rollback 가능(wave 단위 git revert <PR3_COMMIT> 또는 pre-live tag reset) 확인.

## 비고 (정책)
- 이 통합은 "PM-reviewed verified-reference integration" 이며 임상 검수 완료 아님.
- 사용자/앱/문서 어디에도 의료 단정·복약 지시·구매 유도 문구를 추가하지 않음.
- MediStack 은 식약처 허가사항 기반 약-영양소 참고정보(베타)이며 복약 안내가 아님.
