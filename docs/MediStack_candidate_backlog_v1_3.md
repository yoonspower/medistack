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

### 2-A. needs_review (10건) → **source 재확인 완료 (2026-06-15)**: needs_review 2 · reject 8

> **갱신(2026-06-15, source 재확인)**: 아래 needs_review 10건을 SDK-only online 으로 재확인했다(상세 → `docs/MediStack_needs_review_source_recheck_v1_3.md` · `data/review/needs_review_source_recheck_v1_3.json`). 결과: **새 draft 1**(프레드니솔론×칼륨=소론도정, draft-only) · needs_review 유지 1 · reject 9. loop/thiazide 5성분 8건은 `searchDrug` **총 0건(+철자변형 0)** = **국내 미유통 확정(true negative)** → **reject(not_marketed_kr) 격상**. 적대 검증이 프레드니솔론 1차 보수판단을 교정(깊은검색 p7 소론도정 확인).

bot 이 source-check 에서 fail-closed DENY 한 행(라벨 직접근거가 아니라 "대표 itemSeq 미확보"가 사유). 재확인 verdict:

| candidate_id | relation | 재확인 결과(2026-06-15) | verdict |
|---|---|---|---|
| D-CORT-01 | 프레드니솔론 × 칼륨 | max_pages=20 깊은검색 p7 = **소론도정(199602982)** 단일·경구·완제. 라벨 칼륨손실·저칼륨성 알칼리혈증 | **draft(source_confirmed)** = DF-PRED-01, draft-only |
| D-CORT-02 | 프레드니솔론 × 칼슘 | 동 품목, 칼슘 흡수 동거어 없음 | **reject**(label_missing) |
| D-LOOP-01 | 부메타니드 × 칼륨 | searchDrug **0건**(+부메타나이드 0) | **reject**(not_marketed_kr) |
| D-LOOP-02 | 부메타니드 × 마그네슘 | 동상 | **reject**(not_marketed_kr) |
| D-LOOP-03 | 피레타니드 × 칼륨 | searchDrug **0건**(+피레타나이드 0) | **reject**(not_marketed_kr) |
| D-THZ-01 | 메토라존 × 칼륨 | searchDrug **0건**(메톨라존 1행=부적격) | **reject**(not_marketed_kr) |
| D-THZ-02 | 메토라존 × 마그네슘 | 동상 | **reject**(not_marketed_kr) |
| D-THZ-03 | 트리클로르메티아지드 × 칼륨 | searchDrug **0건**(+변형 3종 0) | **reject**(not_marketed_kr) |
| D-THZ-04 | 트리클로르메티아지드 × 마그네슘 | 동상 | **reject**(not_marketed_kr) |
| D-THZ-05 | 벤드로플루메티아지드 × 칼륨 | searchDrug **0건**(+변형 3종 0) | **reject**(not_marketed_kr) |

> **계열 일반화로 채택 금지** 원칙 유지 — 푸로세미드 id17·HCTZ id19 등 기존 라이브와 무관하게 품목 직접 라벨이 없으면 불가. 미유통 8건은 재후보화를 국내 시판 시로 한정.

(중복 1건: **D-CORT-05 하이드로코르티손 × 칼륨** = 기존 **CQF03**(히드로코르티손, wording-review). 재확인: 전신 경구 단일성분 0건(외용 위주) → **needs_review 유지** + correctness 선결.)

### 2-E. substring 지배 성분 탐색 + 3차 online run (2026-06-15 round3)

> 상세 → `data/review/substring_domination_scan_v1_3.json` · `data/review/harvest_run3_summary_v1_3.json` · ops §10.

**substring 지배 탐색(작업 C)**: ingredient universe(theme∪carried∪live∪KPI=**366**)에서 proper-substring 쌍 **40**건을 산출하고, 다른약물 점유(**접두사형 5**)와 염/수화물(**접미사형 35**, 같은 약물·무위험)로 분류했다(대량 네트워크 회피·cache-first SDK).

| short ⊊ superset | scope | 분류 | 비고 |
|---|---|---|---|
| 프레드니솔론 ⊊ 메틸프레드니솔론 | theme | **substring_risk_confirmed** | deep fallback 으로 소론도정(199602982) 복구 = DF-PRED-01(draft) |
| 오메프라졸 ⊊ 에스오메프라졸 | live·kpi | **substring_risk_confirmed** | **이미 live**(id13/14, itemSeq 200411095=오메라졸캡슐, base 단일·경구 확정). 조치 불필요 |
| 란소프라졸 ⊊ 덱스란소프라졸 | live | **substring_risk_confirmed** | **이미 live**(id36/37, itemSeq 201308978=뉴란소캡슐, base 단일·경구 확정). 조치 불필요 |
| 세티리진염산염 ⊊ 레보세티리진염산염 | kpi | no_risk(scope 밖) | 항히스타민 — 영양소 상호작용 트랙 아님 |
| 펜타닐 ⊊ 레미펜타닐 | kpi | no_risk(scope 밖) | 오피오이드·sensitive_hold |

- **신규 live-eligible 후보 0** — 오메프라졸/란소프라졸은 신규 relation 이 아니라 기존 live 의 검색 robustness 확인(deep fallback 이 재harvest 시 base 자동 복구). 35 접미사형(`세파클러수화물`·`라베프라졸나트륨` 등)은 같은 약물이라 무위험.
- **미유통/외용 true negative 재확인(작업 D)**: loop/thiazide 5성분 8 relation 은 개선된 검색으로도 `searchDrug` 0건 = 미유통 유지(substring 지배 아님 — deep 발동/복구 불가). 하이드로코르티손은 외용중심(경구 단일 희소)으로 needs_deep_check=CQF03. **반복 조사 금지, 근거만 유지.**
- **3차 online run**: draft 6→7(프레드니솔론 false-negative 복구)·needs_review 11→9·reject 12→13(프레드니솔론×칼슘 fail-closed→확정 reject). AT-ITZ already_covered 유지. 분포 그 외 불변(회귀 0).

### 2-F. substring 검색 위험 광역 탐색 (2026-06-15 round3 후속)

> 상세 → `docs/MediStack_substring_search_risk_v1_3.md` · `data/review/substring_search_risk_v1_3.json` · ops §11.

§2-E(universe 366)를 **full drug name index distinct ingredient 전체**(2,225)∪alias(27)∪seed(367)=scan **2,292**(단일성분 922)까지 확대해 substring 지배 위험을 더 찾음. proper-substring 쌍을 **diff-active 접두사**(다른약물·진짜 위험)·**형태접두사**(무수/미세/제피=같은약물)·**염/수화물 접미사**·복합제로 분류.

- **분류**: high_risk **10** · medium_risk **14**(seed 밖) · salt_or_formulation_trap **143** · no_action 2.
- **deep-check(cache-first·SDK-only)**: high(diff-active+seed) 10종 → **shallow_miss_confirmed = baseline 3종뿐**(프레드니솔론·오메프라졸·란소프라졸). 신규 diff-active 7종(로라타딘·세티리진·세팔렉신·암로디핀·졸피뎀·펜타닐·펜타닐시트르산염) **전부 shallow_already_safe**(지배 미발현)+영양소 트랙 밖.
- **신규 draft/relation 후보 0** — full index 광역에서도 신규 substring 지배 false-negative 없음. artifact 가 draft-only 기록. **live 무반영.**
- medium_risk 14(트레티노인·프로게스테론·설피리드·페니토인·케타민 등)는 현재 relation 트랙 무관 → 해당 성분이 후보化될 때만 deep-check(재후보화 게이트).

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

**현재 상태 요약(2026-06-15)**: relations **60** · antacid live **1**(AT-ITZ id61) · 칼륨 PM-ready **4건 pending**(DF01·DF04·DF05·DF-PRED-01, dry-run 60→64) · AT-FEX **1건 pending**(dry-run 60→61) · 전건 **reviewer-gated**(승인 토큰+대상 전건 명시 + SAMPLE/placeholder 거부 인터록). harvester 검색 품질 개선 완료(deep fallback·하드닝·회귀 5종) · substring 신규 위험 **0**(universe 2,292 광역까지 확인). published/clinical_reviewed=false · schedule 비활성.

> ⚠️ **무작정 같은 theme map 을 반복 online run 하는 것은 효율이 낮다.** 2차·3차 online run 이 입증했듯(§0·§2-E) draft 분포는 기존 트리아지로 수렴했고 신규 draft-ready 는 0 이다(같은 seed/theme map → 같은 결과). **다음 relation 확장은 다음 중 하나가 선행돼야 의미가 있다**: ①reviewer note 확보 → 기존 pending(칼륨 4·AT-FEX 1) live 승격, ②**새 theme map/seed 수동 추가**(신규 relation family — `next_prompts` 프롬프트 7), ③medium-risk 성분이 relation 후보化될 때만 deep-check(재후보화 게이트·§2-F), ④clinical reviewer 확보(봉인 천장 상향), ⑤harvester schedule PR 준비(ops §12 게이트). 이 중 어느 것도 없는 반복 run 은 새 정보를 만들지 못한다.

### 3-G. 새 theme map family 확장 — **1차 실행 완료(2026-06-15 theme map expansion 라운드)**

위 ②(새 seed 수동 추가)를 실행했다. 기존 theme map(25 성분) **밖에서** 신규 family **3종**을 설계하고, **SDK source-check 로 국내 허가사항 직접근거를 확인**해 **draft-only 6건**을 만들었다(승격 0, live 무변경). 정본 = `docs/MediStack_theme_map_expansion_v1_3.md`.

- **source-confirmed 6**(draft-only): 오르리스타트×지용성비타민(A·D·E·K, 200806047) · 콜레스티라민×지용성비타민(A·D·K, 198800813) · 세프포독심프록세틸×제산제·H2(199300168) · 세프디토렌피복실×제산제·H2(199500901) · 페니실라민×철분(198300142) · 페니실라민×아연(198300142).
- **hold 4**: 레보도파×철분(국내 단일성분 완제 없음) · 페니토인×엽산/비타민D(양방향·신경계) · 마이코페놀레이트×제산제/철분(이식·임상판단) · 레보도파×비타민B6(복합제 무력화 오인).
- **needs_review 2 / source_check 1**: 메틸도파×철분 · 이소니아지드×비타민B6(보충 권유 오인 — copy 게이트 선결) · 콜레세벨람×지용성비타민(2차).
- ⚠️ **카피 안전**: orlistat·cholestyramine 라벨이 종합비타민 보충을 권장 → 우리 카피는 보충 권유 금지(흡수·시점 분리만). cholestyramine 의 비타민K는 항응고 오인 금지. 세팔로스포린 counterpart 는 약물(제산제/H2)로 Mg 영양제 혼동 금지.
- **다음**: 적대검증 + counterpart_category 정렬 + 2차 source-check(`next_prompts` 프롬프트 8) → harvester 편입 PR(프롬프트 9). **live 통합은 clinical reviewer note 후 별도 PR.**

1. **AT-FEX live 통합** — reviewer note 후. dry-run·검증기 준비 완료(`docs/MediStack_next_prompts_2026_06_15.md` 프롬프트 1, 패키지 `docs/MediStack_reviewer_package_antacid_fex_v1_3.md`).
2. **칼륨 PM-ready 4건(DF01·DF04·DF05·DF-PRED-01) live 통합** — reviewer note(승인토큰+4건 전건 명시) 후. dry-run·검증기 준비 완료(프롬프트 2, 패키지 `docs/MediStack_reviewer_package_potassium_v1_3.md`). DF-PRED-01 은 2026-06-15 round2 에 dry-run 합류(60→64). DF02 wording / DF03 hold 는 별도.
3. ~~needs_review 다이유레틱/코르티코스테로이드 source 재확인~~ → **완료(2026-06-15)**: 새 draft **1**(프레드니솔론×칼륨=소론도정 199602982, DF-PRED-01). loop/thiazide 5성분 8건=국내 미유통 reject 격상, 하이드로코르티손×칼륨만 needs_review 유지(CQF03 correctness 선결). **후속 라운드(2026-06-15)**: DF-PRED-01 을 칼륨 PM-ready 통합 준비 그룹에 **dry-run 합류 완료**(4건·whitelist {DF01,DF04,DF05,DF-PRED-01}·`validate_potassium_dryrun_v1_2.py` PASS·60→64, 실제 통합 0). search-depth 항구 개선(`search_itemseqs` deep fallback·`test_search_depth_v1_3.py`·ops §9). 상세 `docs/MediStack_needs_review_source_recheck_v1_3.md`.
4. **CQF03(히드로코르티손) correctness 선결**: 전신 제형 한정 + source_pointer 섹션 정정(handoff §3).
5. **K-sparing 칼륨 상승 holds**: depletion 과 반대 방향 — 별도 정책 트랙이 필요한지 PM 판단(현재 hold 유지).
6. **세파계×철분 10종 reject 확정**: 한국 허가사항 미기재 → 재후보화 금지(계열 일반화 금지 재확인).

---

## 4. 안전 확인 (이 라운드)

- live relation 변경 **0** · export/full index/aliases/DATA_URL 무변경(`62df9284…` 불변) · published/clinical_reviewed=false · reviewed_by 공란 유지.
- schedule **비활성 유지** · harvester 자동 실행 0 · 제품/구매/제휴 UI 0 · 칼륨 보충 권유/결핍 단정 0.
- runtime `data/harvest_queue/` 커밋 제외(offline 베이스라인 유지) · 요약은 `data/review/harvest_run2_summary_v1_3.json`·`harvest_run3_summary_v1_3.json`·`substring_domination_scan_v1_3.json` 에만.
- theme map expansion(§3-G)은 전부 `data/review/theme_map_*_v1_3.json`·`data/drafts/theme_map_draft_batch_v1_3.json`·`scripts/(sourcecheck|validate|smoke)_theme_map*_v1_3.py` (draft-only·live_integration_forbidden=true). SDK source-check 는 namespace 캐시(direct HTTP 0). live relation 0 추가.
- round3(2026-06-15) 변경분 = scripts(`verify_factory_sources_v1_2.py` 하드닝·`test_search_depth_v1_3.py` 보강·신규 `analyze_substring_domination_v1_3.py`) + data/review 요약/탐색 + docs 만. 보호셋 49 sha 불변(guard PASS).
