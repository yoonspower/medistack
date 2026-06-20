# PR-5 칼륨 depletion — PM-reviewed verified-reference integration note (v1.4)

> 이 문서는 **PM-reviewed verified-reference integration note** 이다. **임상 검수 완료 아님.**
> published=false / clinical_reviewed=false / reviewed_by 공란 을 그대로 유지한다.
> 통합 등급 = verified_reference (천장). 사용자 노출 문구에 검수 완료 단정·전문가 확인 단정·
> 식약처 무이슈 단정·복용/보충 권유 단정 같은 표현을 추가하지 않는다.

검토자(PM): PM-001 (PM-reviewed, 별도 AI PM 세션)   검토일 2026-06-20   검토시각 2026-06-20 16:00 KST
검토 패키지: depletion 추출기 v1.8 online harvest v1.4 (칼륨 depletion 6) / base commit 0342a6e
target branch: live/pr5-potassium-depletion
wave: PR-5 potassium_depletion

## PM approval tokens
- PM_REVIEWED_VERIFIED_REFERENCE_ONLY
- NO_CLINICAL_REVIEW_CLAIM
- NO_PRODUCT_UI
- NO_SCHEDULE
- PR5_POTASSIUM_DEPLETION_95_TO_101

## scope (6건 = depletion 6)
- depletion 칼륨 6건 (mechanism=depletion / recommended_action=monitoring / counterpart_category=null · 영양소 직접)

scope(wave=potassium_depletion) 승인(approved): 아래 candidate 6건을 verified_reference 노출로 live 통합 승인.

### 승인 candidate_id 전건 (6건)
  - D-CORT-03  메틸프레드니솔론 × 칼륨  (itemSeq 199800324 · 부작용 체액·전해질)
  - D-CORT-04  덱사메타손 × 칼륨        (itemSeq 196300064 · 부작용 체액·전해질)
  - D-CORT-05  히드로코르티손 × 칼륨    (itemSeq 200703172 · 부작용 체액·전해질)
  - D-CORT-06  플루드로코르티손 × 칼륨  (itemSeq 199907231 · 일반적 주의)
  - D-CA-01    아세타졸아미드 × 칼륨    (itemSeq 201403403 · 이상반응 대사)
  - D-LOOP-04  아조세미드 × 칼륨        (itemSeq 199001306 · 부작용 대사)

## relation count
relation delta: +6 (95 → 101, 신규 id = runtime max+1 = 97~102).

## grouping
grouping 승인: potassium_depletion 6건 단일 wave 통합. (rollback 단위 = 본 wave.)

## 🔑 칼륨 safety (이 PR 의 핵심 — production 최초 칼륨 safety 진입)
6건 전부 **potassium_safety_card=true · product_link_allowed=false** 강제 승인. 칼륨은 과다섭취(고칼륨혈증)
위험 때문에 결핍 행도 **보충 지시가 아니라 결핍 주의 참고**로만 노출한다. display/management 에 보충 지시
("보충하세요/드세요/복용하세요/섭취하세요") 0 · 수치 단정("수치가 낮아진다" 등 라벨 미명시) 0 · 능동 register 0 확인.
칼륨 경고는 potassium_safety_card=true UI 가 전달한다. requires_clinical_review=false 유지.
방향성: 6건 모두 약물이 칼륨을 낮추는(저칼륨혈증/칼륨손실/배설증가) depletion 이며, 고칼륨혈증(↑·칼륨보존성) 아님.

## source fidelity
출처(source) fidelity: 식약처 허가사항(nedrug getItemDetail) 인용과 일치 보존 확인. 비공식/쇼핑몰/블로그 출처 0건.
6건 각 itemSeq 실재 채움(199800324·196300064·200703172·199907231·201403403·199001306) / 섹션은 이상반응·부작용·일반적 주의
(in-scope) — 상호작용(약-약)·임부/태아(B2)·과량·고령자 섹션 인용 0. 한국 IP depletion 추출기 v1.8 online harvest 가
실제 fetch 한 정본. PM 이 fixture·온라인 교차 확인. GOLD 3/3 verbatim 재현.

## display copy (source fidelity · PR-5 copy 원칙)
depletion = monitoring · counterpart_category=null(영양소 직접). copy 는 main(0342a6e) 의 fix된
safe_app_copy(영양소,'depletion') 로 신규 생성(live 86-93 선례 동형). 6건 동일 보수 템플릿:
- display: "이 약을 장기간 복용할 때 칼륨과(와) 관련된 허가사항 주의 문구가 있습니다. 증상이 걱정되면 약사 또는 의사와 상담하세요."
- management: "장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다."
라벨 결핍 명시(저칼륨혈증/칼륨손실/배설증가)를 참고 톤으로만 진술 → 보충 단정·수치 단정·검사 명령 비노출.

## management copy
관리 문구(management copy): 참고·상담 톤 보수성 유지 확인. 정기 상태 확인 문의는 MediStack 제안 수준(약사 또는 의사와
상담)이며 복약/보충/검사 지시가 아님. 원문(허가사항)보다 강한 표현 없음 확인.

## 보호 상태 유지 승인
published=false 유지 승인. clinical_reviewed=false 유지 승인. reviewed_by 공란 유지 승인.
제품·구매·제휴 UI 추가 없음 확인. schedule 비활성(inactive) 유지 확인.
통합 등급 천장 = verified_reference. 임상 검수 완료 아님. evidence_level=moderate 유지(임의 상향 금지 — clinical reviewer 몫).

## 제외 확인
- not_reachable 5약물(부메타니드·피레타니드·메토라존·트리클로르메티아지드·벤드로플루메티아지드 — 국내 미유통·검색0) 관련 8후보 제외.
- 아조세미드×마그네슘(D-LOOP-05)은 라벨 마그네슘 특정 결핍 명시 없음 → 제외.
- 프레드니솔론×칼륨(D-CORT-01)은 순수 단일성분 경구 부재(검색 부분매칭) → 제외.
- 기존 live 칼륨 relation(푸로세미드 id17·히드로클로로티아지드 id19·토라세미드 id30·클로르탈리돈 id53·인다파미드 id55)는
  재추가/재통합 금지 — 중복 0 확인. 본 PR-5 신규 6약물은 기존 live 칼륨 5약물과 dedup(중복 0).
- PR-1/PR-2/PR-3/PR-4 후보 재추가 금지 확인(중복 0).

## rollback
rollback 가능(wave 단위 git revert <PR5_COMMIT> 또는 pre-live tag reset) 확인.

## 비고 (정책)
- 이 통합은 "PM-reviewed verified-reference integration" 이며 임상 검수 완료 아님.
- 사용자/앱/문서 어디에도 의료 단정·복약 지시·구매 유도·보충 권유 문구를 추가하지 않음.
- MediStack 은 식약처 허가사항 기반 약-영양소 참고정보(베타)이며 복약 안내가 아님.
