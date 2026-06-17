# PR-1 antibiotic24 — PM-reviewed verified-reference integration note (v1.4)

> 이 문서는 **PM-reviewed verified-reference integration note** 이다. **임상 검수(clinical review)가 아니다.**
> published=false / clinical_reviewed=false / reviewed_by 공란 을 그대로 유지한다.
> 통합 등급 = verified_reference (천장). 사용자 노출 문구에 검수 완료 단정·전문가 확인 단정·
> 식약처 무이슈 단정·복용 권유 단정 같은 표현을 추가하지 않는다.

검토자(PM): PM-LIVEPR-001 (PM-reviewed, 별도 AI PM 세션)   검토일 2026-06-18   검토시각 2026-06-18 07:38 KST
검토 패키지: per_family_live_pr_readiness v1.4 + autofactory_v1_5_audit_cleanup / base commit 9267740
target branch: live/pr1-antibiotic24
wave: PR-1 antibiotic24

## PM approval tokens
- PM_REVIEWED_VERIFIED_REFERENCE_ONLY
- NO_CLINICAL_REVIEW_CLAIM
- NO_PRODUCT_UI
- NO_SCHEDULE
- PR1_ANTIBIOTIC24_60_TO_84

## scope (24건 = F1 18 + F2 5 + add-on 1)
- F1 퀴놀론 × 미네랄/Al·Mg 함유 제산제: 18건
- F2 테트라사이클린 × 금속/Al·Mg 함유 제산제: 5건
- 시프로플록사신 × Al/Mg 함유 제산제(add-on, production·independent audit AUDIT_PASS): 1건

scope(wave=antibiotic24) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.

### 승인 candidate_id 전건 (24건)
[F1 — 퀴놀론 × 미네랄/제산제] (18)
  - RF-F1-0021
  - RF-F1-0022
  - RF-F1-0024
  - RF-F1-0041
  - RF-F1-0042
  - RF-F1-0044
  - RF-F1-0066
  - RF-F1-0067
  - RF-F1-0026
  - RF-F1-0029
  - RF-F1-0025
  - RF-F1-0010
  - RF-F1-0035
  - RF-F1-0040
  - RF-F1-0020
  - RF-F1-0045
  - RF-F1-0070
  - RF-F1-0030
[F2 — 테트라사이클린 × 금속/제산제] (5)
  - RF-F2-0105
  - RF-F2-0110
  - RF-F2-0111
  - RF-F2-0114
  - RF-F2-0115
[add-on — production·audit-cleanup AUDIT_PASS] (1)
  - AFP-F1-시프로플록사신-al_mg_antacid

## relation count
relation delta: +24 (60 → 84, 신규 id = runtime max+1).

## grouping
grouping 승인: antibiotic24 wave 단위 한 번에 통합. (rollback 단위 = 본 wave.)

## source fidelity
출처(source) fidelity: 식약처 허가사항(nedrug getItemDetail) 인용과 일치 보존 확인. 비공식/쇼핑몰/블로그 출처 0건.
audit-cleanup(독립 적대감사 53 agents) 결과 반영: add-on(시프로플록사신×Al/Mg 제산제)은 fuller quote 로 AUDIT_PASS 5/5 확정.
fuller quote 반영 여부: 반영함 — add-on 의 source.quote 는 분리복용 안내 문장("이 약 투여 전 1~2시간 및 투여 후
4시간 이내에는 병용하지 않는 것이 바람직하다")까지 포함하는 전체 인용(fuller quote)으로 저장됨.

## management copy
관리 문구(management copy): 참고·상담 톤 보수성 유지 확인. 분리복용/정기확인 문의 안내이며 복약 지시가 아님.
원문(허가사항)보다 강한 표현 없음 확인. 사용자 노출 문구는 함께 복용 시 흡수가 줄어 효과가 감소할 수 있다는
허가사항 문구 안내 / 복용 시점 분리 / 약사 또는 의사와 상담 수준의 참고 톤.

## 보호 상태 유지 승인
published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.
제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.
통합 등급 천장 = verified_reference. 임상 검수 완료 아님.

## 제외 확인
needs_review 4건(RF-F3-0148, RF-F3-0149, RF-F9-0245, RF-F10-0275) 및 F3/F9/F4/F6 family 후보는 본 승인에서 제외 확인.


## display copy_change (source fidelity · 적대검증 반영)
독립 적대검증(3차·48 lenses)에서 display 2번째 문장 '복용 시점을 분리하도록 안내하고 있으니'가 일부 인용(회피권고/흡수저하 사실)을
초과(라벨이 분리를 능동 안내한다는 단정)한다고 적발 → 24건 전건 display 2번째 문장을 보수 reframe.
- 발로플록사신×제산제(RF-F1-0040): 라벨 '병용을 피하는 것이 바람직하다'를 충실히 진술.
- 그 외 23건: 라벨귀속 분리-안내 단정 제거, '복용 시점에 대해 약사 또는 의사와 상담하세요'로 상담 유도.
display 1번째 문장(흡수저하 사실·라벨귀속)과 management(hedged 제안)는 유지. relation/action(separation) 불변.
기존 live 선례(id40/42/47/48/61)와 동형. 원문보다 강한 표현 제거(보수화). 최종 적대검증 CLEAR_TO_APPLY(refutation 0).
record: data/review/pr1_antibiotic24_display_copy_change_v1_4.json

## rollback
rollback 가능(wave 단위 git revert <PR1_COMMIT> 또는 pre-live tag reset) 확인.

## 비고 (정책)
- 이 통합은 "PM-reviewed verified-reference integration" 이며 임상 검수 완료 아님.
- 사용자/앱/문서 어디에도 의료 단정·복약 지시·구매 유도 문구를 추가하지 않음.
- MediStack 은 식약처 허가사항 기반 약-영양소 참고정보(베타)이며 복약 안내가 아님.

---

## 부록 — 이 note 의 의미와 한계 (검토자/PM 핸드오프용)

**무엇인가:** PR-1 antibiotic24 wave(F1 18 + F2 5 + 시프로 add-on 1 = 24건)를 라이브 v0.2 export 에
verified_reference 등급으로 통합하기 위한 PM 검토 승인 기록.

**무엇이 아닌가:** 임상 검수(clinical review) 승격이 아니다. clinical_reviewed/published 플래그 전환 없음.
reviewed_by 미기입(공란 유지). 사용자 노출 문구에 검수 완료 단정·식약처 무이슈 단정·복용 권유 단정 표현 추가 없음.

**왜 보수적으로 안전한가(source fidelity):** 24건 전부 식약처 허가사항 인용 기반. F1/F2 23건은 reviewer-ready batch
(적대검증 survives) + family 재검증. add-on 1건은 독립 적대감사(53 agents)에서 fuller quote 로 AUDIT_PASS 5/5.
표현은 모두 원문보다 약하거나 동등(참고·상담 톤). 분리복용 안내는 원문 "투여 전 1~2시간/후 4시간 병용 회피 바람직"
근거.

**체커:** `scripts/check_pr1_antibiotic24_pm_note_v1_4.py --note <this>` PASS 시에만
`scripts/integrate_pr1_antibiotic24_live_v1_4.py --apply --pm-note <this>` 가 live write 를 수행한다.

**rollback:** wave 단위 `git revert 9267740..HEAD` 또는 pre-live tag 로 reset → relation_count 84→60 복귀.
