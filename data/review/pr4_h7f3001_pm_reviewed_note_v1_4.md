# PR-4 H7-F3-001 — PM-reviewed verified-reference integration note (v1.4)

> 이 문서는 **PM-reviewed verified-reference integration note** 이다. **임상 검수 완료 아님.**
> published=false / clinical_reviewed=false / reviewed_by 공란 을 그대로 유지한다.
> 통합 등급 = verified_reference (천장). 사용자 노출 문구에 검수 완료 단정·전문가 확인 단정·
> 식약처 무이슈 단정·복용 권유 단정 같은 표현을 추가하지 않는다.

검토자(PM): PM-001 (PM-reviewed, 별도 AI PM 세션)   검토일 2026-06-19   검토시각 2026-06-19 18:00 KST
검토 패키지: autofactory v1.7 online harvest v1.4 (H7-F3-001) / base commit 7f07df4
target branch: live/pr4-h7f3001
wave: PR-4 h7f3001

## PM approval tokens
- PM_REVIEWED_VERIFIED_REFERENCE_ONLY
- NO_CLINICAL_REVIEW_CLAIM
- NO_PRODUCT_UI
- NO_SCHEDULE
- PR4_H7F3001_94_TO_95

## scope (1건 = F3 1)
- F3 리세드론산 × Al/Mg 함유 제산제(약물): 1건 (absorption/separation · al_mg_antacid)

scope(wave=h7f3001) 승인(approved): 아래 candidate 1건을 verified_reference 노출로 live 통합 승인.

### 승인 candidate_id 전건 (1건)
  - H7-F3-001  리세드론산 × Al/Mg 함유 제산제(약물)

## relation count
relation delta: +1 (94 → 95, 신규 id = runtime max+1 = 96).

## grouping
grouping 승인: h7f3001 단건 통합. (rollback 단위 = 본 wave.)

## source fidelity
출처(source) fidelity: 식약처 허가사항(nedrug getItemDetail) 인용과 일치 보존 확인. 비공식/쇼핑몰/블로그 출처 0건.
itemSeq 200713889 (리골다정35밀리그램, 무수리세드론산나트륨2.5수화물 — 단일성분·경구) / 6. 상호작용 /
인용(source quote): "칼슘보충제, 제산제 및 다가 양이온(칼슘, 마그네슘, 철, 알루미늄 등)을 함유한 경구투여 약물의 병용 투여는 이 약의 흡수를 방해한다."
한국 IP autofactory v1.7 online harvest 가 실제 fetch 한 정본. PM 이 fixture·온라인 교차 확인.

## display copy_change (source fidelity · PR-4 copy 원칙)
F3 = absorption/separation · al_mg_antacid(drug counterpart). copy 는 main(7f07df4) 의 fix된
safe_app_copy('Al/Mg 함유 제산제(약물)','separation') 로 신규 생성(오염 산출 브랜치 미사용).
- 리세드론산(H7-F3-001): 라벨 인용은 흡수 **방해** 사실만 진술(효과 미언급) → display 에 '효과가 감소' **비노출**
  (라벨 흡수만 명시 → 효과 단정은 source-additive 라 제거). '흡수가 저하될 수 있다' FACT-only 로 보수, 라벨귀속
  '분리하도록 안내' 단정도 비노출 → '함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요' 유도. 기존 live
  al_mg_antacid 선례(PR-1 id72·PR-3 id94)와 동형. relation/action(separation) 유지.
- counterpart scope: 라벨이 칼슘·마그네슘·철·알루미늄 을 verbatim 명시 → Al/Mg 함유 제산제 counterpart 정당(과확장 아님).
record: data/review/pr4_h7f3001_display_copy_change_v1_4.json

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
F1/F2(PR-1)·F6/F9(PR-2)·F3 이반드론산(PR-3)·F4 레보티록신(PR-3) family 후보는 PR-4 제외 — 이미 live → 재추가/재통합 금지(중복 0) 확인.
항생제 minor 3건(id67 자보플록사신×아연·id71 페플록사신×아연 scope·id75 발로플록사신 register)은 별도 copyfix 라운드 대상이라 본 PR-4 비포함.

## rollback
rollback 가능(wave 단위 git revert <PR4_COMMIT> 또는 pre-live tag reset) 확인.

## 비고 (정책)
- 이 통합은 "PM-reviewed verified-reference integration" 이며 임상 검수 완료 아님.
- 사용자/앱/문서 어디에도 의료 단정·복약 지시·구매 유도 문구를 추가하지 않음.
- MediStack 은 식약처 허가사항 기반 약-영양소 참고정보(베타)이며 복약 안내가 아님.
