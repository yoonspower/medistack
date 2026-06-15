# MediStack — 후보 백로그 (harvester 2차 online run, v1.3)

작성일: 2026-06-15 · 상태: **분석/백로그 · 실행 금지(승격 0)** · 자기완결

> 이 문서는 harvester bot v1.3 **2차 online run**(2026-06-15)의 PM review queue 를 분석해, 이미 트리아지된 항목을
> 제거하고 **남은 신규 후보를 분류·우선순위화**한 백로그다. 모든 항목 `do_not_implement_yet=true` · `live_integration_forbidden=true` ·
> `published=false` · `clinical_reviewed=false`. **이 라운드에서 코드·데이터·export·DATA_URL 를 승격 방향으로 바꾸지 않는다.**
> 산출물은 문서 + `data/review/harvest_run2_summary_v1_3.json`(요약 artifact)뿐. runtime `data/harvest_queue/` 는 커밋 제외(재현가능).

---

## 0. run 개요 (2026-06-15 online)

| 항목 | 값 |
|---|---|
| mode | **online** (실 nedrug 라벨) |
| SDK | network **0** · cache **68** · fixture 0 · offline_miss **0** · error **0** (전부 캐시 적중 → 결정적) |
| live relation 생성 / 승격 / deploy | **0 / 0 / none** |
| no-live-write 가드 | PASS(보호셋 sha256 불변 · write-scope=`data/harvest_queue/` 한정 · direct-http 신규 0) |
| harvest queue validator | PASS(스키마 · no-live-promote · 금칙어 0 · PM smoke) |

**분포**: harvest 78 · source-check 29 → draft 6 · needs_review 11 · reject 12 · already_covered 7 · hold 46 · rejected_precheck 52 · KPI 60.

**2차 online vs 1차 offline 베이스라인(2026-06-14)**: harvest 77→78 · draft 3→**6** · needs_review 24→**11** · reject 2→**12** · already_covered 6→7.
해석: online 이 offline_miss 23→0 을 해소 → 실 라벨로 **직접근거 확인(draft↑)** · **문헌-only deny(reject↑)** · **fail-closed 감소(needs_review↓)**.
hold(46)/rejected_precheck(52)는 KPI·carry 결정적 입력이라 **불변**(라벨 fetch 무관).

---

## 1. dedup — draft 6건 전부 기존 트리아지와 동일 (신규 draft-ready 0)

bot 의 draft_eligible 6건은 **전부** clinical reviewer handoff(`docs/MediStack_clinical_reviewer_handoff_v1_2.md`)에서 이미 트리아지한 항목이다. itemSeq 대조로 동일성 확인.

| bot id | relation | itemSeq | 기존 트리아지 | 상태 |
|---|---|---|---|---|
| D-CORT-03 | 메틸프레드니솔론 × 칼륨 | 199800324(+199701131) | **DF01** | PM-ready (dry-run 준비 완료) |
| D-CORT-04 | 덱사메타손 × 칼륨 | 196300064;199401023 | **DF02** | wording-review (보류) |
| D-CORT-06 | 플루드로코르티손 × 칼륨 | 199907231 | **DF03** | hold (국내 유통 적음) |
| D-CA-01 | 아세타졸아미드 × 칼륨 | 201403403 | **DF04** | PM-ready (dry-run 준비 완료) |
| D-LOOP-04 | 아조세미드 × 칼륨 | 199001306 | **DF05** | PM-ready (dry-run 준비 완료) |
| AT-FEX-01 | 펙소페나딘 × Al/Mg 제산제 | 199801016 | **AT-FEX** | dry-run 준비 완료 |

또한 `already_covered` 7건에는 **AT-ITZ 이트라코나졸**(live id61, 6/15 통합 완료)이 포함된다.

> **결론: 이번 online run 으로 새로 생긴 draft-ready 후보는 0.** 따라서 신규 draft-only batch 를 만들지 않는다(없는 후보를 지어내지 않음).
> 기존 AT-ITZ(live)·AT-FEX(dry-run)·칼륨 PM-ready 3건(dry-run) 준비 상태는 그대로 유지(export sha `62df9284…` 불변).

---

## 2. 신규 후보 분류 (트리아지되지 않은 것만)

### 2-A. needs_review (10건) — fail-closed: 국내 경구 단일성분 대표 품목 미확보(검색 0건)

bot 이 source-check 에서 **fail-closed DENY** 한 행. 라벨 직접근거가 아니라 "대표 itemSeq 미확보"가 사유 → 승격 전 **source 재확인 필요**(국내 경구 단일성분 완제 품목과 itemSeq 확정).

| candidate_id | relation | mechanism/action | 비고 |
|---|---|---|---|
| D-CORT-01 | 프레드니솔론 × 칼륨 | depletion/monitoring | 코르티코스테로이드(시장 큼). 대표 경구품목 itemSeq 재확인 필요 |
| D-CORT-02 | 프레드니솔론 × 칼슘 | absorption/monitoring | 칼슘 방향은 라벨 직접 동거어 별도 확인(약신호 약할 수 있음) |
| D-LOOP-01 | 부메타니드 × 칼륨 | depletion/monitoring | loop 이뇨제. 국내 유통/대표품목 재확인 |
| D-LOOP-02 | 부메타니드 × 마그네슘 | depletion/monitoring | Mg 방향 라벨 직접 동거어 확인 필요 |
| D-LOOP-03 | 피레타니드 × 칼륨 | depletion/monitoring | loop 이뇨제. 국내 유통 재확인 |
| D-THZ-01 | 메토라존 × 칼륨 | depletion/monitoring | thiazide-유사. 국내 유통/대표품목 재확인 |
| D-THZ-02 | 메토라존 × 마그네슘 | depletion/monitoring | Mg 방향 확인 필요 |
| D-THZ-03 | 트리클로르메티아지드 × 칼륨 | depletion/monitoring | thiazide. 대표품목 재확인 |
| D-THZ-04 | 트리클로르메티아지드 × 마그네슘 | depletion/monitoring | Mg 방향 확인 필요 |
| D-THZ-05 | 벤드로플루메티아지드 × 칼륨 | depletion/monitoring | thiazide. 국내 유통 재확인 |

> 분류 근거(작업 D 기준): itemSeq 불확실 · 단일 경구 완제품목 불명 → **needs_review**. 고위험군(항암/항응고/정신건강) 아님이고
> 칼륨 **고갈(depletion)** 방향(상승 아님)이라 hold 가 아니라 source 재확인 트랙. 계열 일반화로 채택 금지 — 품목별 라벨 직접 동거어 필수.

(중복 1건: **D-CORT-05 하이드로코르티손 × 칼륨** = 기존 **CQF03**(히드로코르티손, wording-review·correctness 선결). 신규 아님 — 표기만 다름.)

### 2-B. reject (12건) — 실 라벨 기반 clean deny (literature-only / 방향성 동거어 부재)

online 실 라벨 fetch 로 **직접근거 부재**가 확인돼 reject. 계열 유추 채택 금지 원칙이 작동.

| candidate_id | relation | reject 사유 |
|---|---|---|
| F-CEPH-01 ~ F-CEPH-10 | 세파계 10종(세파클러·세푸록심·세프포독심·세프프로질·세픽심·세프라딘·세프카펜·세프디토렌·세팔렉신·세프록사딘) × 철분 | 한국 허가사항 상호작용/주의/이상반응에 **철분 방향성 동거어 부재**(literature-only 가능). 계열 유추 금지 |
| D-CORT-07 | 메틸프레드니솔론 × 칼슘 | 라벨에 칼슘 방향성 동거어 부재(칼륨은 별개로 DF01 = depletion 확인됨) |
| D-LOOP-05 | 아조세미드 × 마그네슘 | 라벨에 Mg 방향성 동거어 부재(칼륨은 DF05 로 확인됨) |

> 세파계×철분은 **흡수 분리(separation)** 가설이 이차문헌엔 있으나 **한국 허가사항 미기재** → 베타 천장(원문 없으면 노출 금지) 위반이라 reject 확정.

### 2-C. hold (정책 대기 — notable)

precheck/carry 단계에서 hold 된 46건 중 **정책 결정이 필요한 notable** 항목(나머지는 민감군·문헌only·near-zero coverage 의 통상 hold):

| candidate_id | relation | hold 사유 |
|---|---|---|
| H-KSPAR-01 | 스피로노락톤 × 칼륨 | **칼륨 상승(고칼륨혈증) 방향 — depletion 반대**. 칼륨 보충 병용 금기 방향. 별도 정책 필요 |
| H-KSPAR-02 | 에플레레논 × 칼륨 | 칼륨 상승 방향. PM 정책 대기 |
| H-KSPAR-03 | 아밀로라이드 × 칼륨 | 칼륨 상승 방향(국내 주로 복합제) |
| H-KSPAR-04 | 트리암테렌 × 칼륨 | 칼륨 상승 방향(엽산 길항은 별도 트랙) |
| H-WARN-01 | 스피로노락톤(+ACEi/ARB) × 칼륨 | 약-약 상호작용(칼륨 상승) — 약-영양소 factory 범위 밖 |
| D-THZ-06 | 히드로클로로티아지드 × 칼슘 | thiazide 는 칼슘 배설 **감소**(고칼슘혈증 방향) — depletion 아님(혼동방지 hold) |
| D-SGLT2-01/02 | 다파글리플로진·엠파글리플로진 × 마그네슘 | SGLT2 는 혈청 Mg **상승** 보고 우세 — depletion 가정 부적합 가능 |
| F-STA-01 | 로수바스타틴 × 코엔자임Q10 | 한국 허가사항 미기재 예상 — source-policy(이차문헌 허용) 결정 전 보류 |
| F-PPI-01/02 | 일라프라졸 × 마그네슘·비타민B12 | PPI class 패턴은 있으나 index 2품목뿐 — 우선순위 hold |
| F-TET-01 | 테트라사이클린 × 칼슘 | 원성분 index 1품목 — near-zero coverage |
| D-BIG-01 | 부포르민 × 비타민B12 | 국내 미유통 가능성 — 시장 의미 0(현행 비구아나이드 = 메트포르민 단일, id12 live) |

> ⚠️ **칼륨 상승(K-sparing) 방향은 depletion factory 와 정반대다.** depletion 카드(칼륨 영향 모니터링)로 절대 섞지 말 것 —
> 오히려 칼륨 병용 주의(고칼륨혈증) 방향이라 별도 정책/카피 설계가 필요하며, 그 전까지 영구 hold.

### 2-D. rejected_precheck (52건, 결정적·불변)

KPI 트랩 스캔 결과: 허가사항 6대 영양소 직접 동거어 개연 낮음 35 · 짝이온염 트랩 14 · 복합제 트랩 3. (라벨 fetch 무관, 1차와 동일)

---

## 3. 다음 확장 우선순위 (PM 게이트 — 승격은 별도 라운드)

1. **AT-FEX live 통합** — reviewer note 후. dry-run·검증기 준비 완료(`docs/MediStack_next_prompts_2026_06_15.md` 프롬프트 1).
2. **칼륨 PM-ready 3건(DF01·DF04·DF05) live 통합** — reviewer note 후. dry-run·검증기 준비 완료(프롬프트 2).
3. **needs_review 다이유레틱/코르티코스테로이드 source 재확인**(프롬프트 3 신규): 국내 경구 단일성분 대표 itemSeq 확보 시 칼륨 depletion factory 후보化.
   우선순위: **프레드니솔론**(코르티코스테로이드, 시장 큼) > **부메타니드·피레타니드**(loop) > **메토라존·트리클로르메티아지드·벤드로플루메티아지드**(thiazide). Mg/칼슘 방향은 라벨 직접 동거어 별도 확인.
4. **CQF03(히드로코르티손) correctness 선결**: 전신 제형 한정 + source_pointer 섹션 정정(handoff §3).
5. **K-sparing 칼륨 상승 holds**: depletion 과 반대 방향 — 별도 정책 트랙이 필요한지 PM 판단(현재 hold 유지).
6. **세파계×철분 10종 reject 확정**: 한국 허가사항 미기재 → 재후보화 금지(계열 일반화 금지 재확인).

---

## 4. 안전 확인 (이 라운드)

- live relation 변경 **0** · export/full index/aliases/DATA_URL 무변경(`62df9284…` 불변) · published/clinical_reviewed=false · reviewed_by 공란 유지.
- schedule **비활성 유지** · harvester 자동 실행 0 · 제품/구매/제휴 UI 0 · 칼륨 보충 권유/결핍 단정 0.
- runtime `data/harvest_queue/` 커밋 제외(offline 베이스라인 유지) · 요약은 `data/review/harvest_run2_summary_v1_3.json` 에만.
