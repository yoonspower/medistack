# MediStack — 다음 라운드 프롬프트 (2026-06-15 핸드오프)

작성일: 2026-06-15 · 상태: **핸드오프 / 실행 금지(차기 PM 라운드용)** · 자기완결

이 문서는 다음 두 작업의 **실행 프롬프트 초안**이다. 둘 다 **별도 PM 승인 + clinical reviewer 가 전제**이며, 이번 라운드에서 실행하지 않는다. 현재 라이브 상태(2026-06-15): main HEAD = clinical reviewer 핸드오프 준비 커밋, relations 60(AT-ITZ id61 live), AT-FEX 미통합, 칼륨 PM-ready 6건 미승격(3건 통합 드라이런 완료), published/clinical_reviewed=false, DATA_URL v0.2, 제품/제휴 UI 0.

> **갱신(2026-06-15)**: 프롬프트 2가 '칼륨 PM-ready **재검토**'였으나 재검토는 완료됐다(6건 확정·6/6 survives·`data/review/potassium_depletion_pm_ready_v1_2.json` `meta.rereview_2026_06_15`). 또한 PM-ready 3건(DF01·DF04·DF05)의 **live 통합 준비(드라이런·검증기)**까지 끝났다. 그래서 프롬프트 2를 다음 실제 작업인 **'칼륨 PM-ready 3건 live 통합'**으로 교체한다. reviewer 핸드오프: `docs/MediStack_clinical_reviewer_handoff_v1_2.md`.

> **갱신(2026-06-15, reviewer-gated 하드닝 라운드)**: 두 통합 스크립트 모두 **의미적 reviewer-note 인터록**(`check_reviewer_note`) 보강 완료 — 칼륨=승인 토큰+draft_id 4건 전건, AT-FEX=승인 토큰+candidate_id+itemSeq 202202380+evidence moderate, 공통=**SAMPLE 토큰·미기입 placeholder 거부**. 복붙 reviewer note 템플릿은 핸드오프 §8, SAMPLE 주의는 §9, 회귀는 `scripts/test_reviewer_note_gate_v1_3.py`(invalid 거부+valid 통과+live export sha256 불변). 그래서 아래 프롬프트 1(AT-FEX)·2(칼륨)는 **`--pm-approved --reviewer-note <노트>` 둘 다** 전제로 갱신. 또한 **프롬프트 6(harvester schedule 활성화 검토)** 신설(아직 실행 아님). 본 라운드에서 실제 통합·schedule 활성화는 0.

> **갱신(2026-06-15, theme map expansion 라운드)**: 프롬프트 7(새 theme map 확장)을 **실행** — 신규 family 3종 설계 + SDK source-check 로 **draft-only 6건**(오르리스타트·콜레스티라민 × 지용성비타민, 세프포독심·세프디토렌 × 제산제/H2, 페니실라민 × 철분·아연) 확정. 정본 `docs/MediStack_theme_map_expansion_v1_3.md`. 남은 일은 **프롬프트 8(적대검증+2차 source-check)** · **프롬프트 9(harvester 편입 PR)**. 본 라운드 live 통합·schedule 활성화·workflow·src/export/index/alias 수정 0. ↓이전 라운드:

> **갱신(2026-06-15, reviewer package + schedule PR-ready 라운드)**: ①reviewer 배포용 **독립 패키지 2종** 작성 — `docs/MediStack_reviewer_package_potassium_v1_3.md`(칼륨 4건) · `docs/MediStack_reviewer_package_antacid_fex_v1_3.md`(AT-FEX). 각 패키지에 후보별 상세·source quote·제외 항목·검증 절차·note 템플릿·인터록 요건 자기완결. 프롬프트 1·2 는 이 패키지를 reviewer 핸드오프 정본으로 쓴다. ②**운영자 runbook** `docs/MediStack_operator_runbook_v1_3.md`(일상/주간 흐름·승인 기준·rollback·알림 설정법). ③**schedule 활성화 PR-ready 설계** `docs/MediStack_harvester_schedule_activation_v1_3.md` + 미리보기 `data/review/harvester_schedule_activation_patch_preview_v1_3.json` + 구조 검증기 `scripts/validate_harvester_schedule_safety_v1_3.py`(9규칙+결함주입). 프롬프트 6 갱신. ④**프롬프트 7(새 theme map 확장)** 신설. 본 라운드에서 live 통합·schedule 활성화·workflow 수정 0.

---

## 프롬프트 1 — AT-FEX(펙소페나딘 · avoid_concomitant) live 통합

> **선행 충족 필수(전부)**: ①clinical reviewer 노트 확보(핸드오프 §7-1 질문 답, §8-2 템플릿) ②source 202202380(avoid_concomitant '…제산제를 복용하지 마십시오') directive 재대조 + `source.checked_at` 갱신 ③evidence_level=moderate PM 승인(또는 조정) ④round4 적대검증 재확인(카피/표면 변경 시).
>
> **작업**: AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, **avoid_concomitant**) **1건만** v0.2 export 에 멱등 append-only 통합하라 — `python3 scripts/integrate_antacid_fex_v1_2.py --pm-approved --reviewer-note <노트>`(멱등: 이미 있으면 skip). **reviewer 노트 인터록(보강 완료)**: 노트가 비공란 + 승인 토큰('approved'|'승인') + **candidate_id(AT-FEX-01/AT-01)** + **primary itemSeq 202202380** + **evidence_level 'moderate'** 를 전건 명시하고, **SAMPLE 토큰·미기입 placeholder 가 없어야** 통과(미충족 시 STOP — `check_reviewer_note`). 드라이런 검증은 `scripts/validate_antacid_fex_dryrun_v1_2.py` 로 이미 통과(시뮬 export v0.2 PASS·전용 chip·facet 제외·live 무수정), 게이트 회귀는 `scripts/test_reviewer_note_gate_v1_3.py`.
>
> **예상 변경**: relations 60→61(id 62), meta.relation_count 61, recommended_action=avoid_concomitant, mechanism=absorption, evidence_level=moderate, counterpart_category=al_mg_antacid, product_link_allowed=false, potassium_safety_card=false, requires_clinical_review=false. **full index/aliases 무변경**(펙소페나딘 name_only). 전용 chip '병용금지(허가사항)' + kicker 'Al/Mg 함유 제산제 관련 참고정보'.
>
> **불변**: v0.1/v0.2 봉인 외 직접수정 금지(integrate 스크립트만 export 기록)·counterpart_category=al_mg_antacid(영양소 facet 제외)·published/clinical_reviewed=false 유지(reviewer 트랙 별도)·reviewed_by 는 reviewer 만·DATA_URL v0.2·제품/제휴 UI 0·앱 카피 비지시('복용하지 마세요' 직접 명령 금지)·Mg 영양제 relation 으로 저장 금지.
>
> **통합 후 검증(전수 PASS 필수)**: relation-count 하드코딩 validator **60→61 갱신**(AT-ITZ 때 59→60 한 9종: full index·factory_integration·cqf02_integration·relation_draft[ANTACID_IDS]·coverage_queue_integration/draft_batch/batch3/batch4·factory_draft_batch) + `validate_antacid_itz_integration_v1_2.py` id 집합 baseline + 신규 `validate_antacid_fex_integration_v1_2.py`(드라이런 검증기를 live 대상으로 전환) → v0.2 export validator(16/16) · antacid validator/smoke · forbidden 0 · full smoke 9종 · no-live-write guard · deploy 게이트 · **live HTTP 200** · git clean.
>
> **금지**: 칼륨·needs_review/reject 후보 동시 통합 금지. evidence_level 임의 상향 금지(moderate 근거 = confidence low + 대표 itemSeq 분기). clinical_reviewed=true·published=true·reviewed_by 작성 금지.

근거/상세: `docs/MediStack_antacid_interaction_track_v1_2.md` §17(round4 적대검증)·§19(통합 준비·드라이런).

---

## 프롬프트 2 — 칼륨 depletion PM-ready 4건(DF01·DF04·DF05·DF-PRED-01) live 통합

> **갱신(2026-06-15, search-depth 라운드)**: DF-PRED-01 프레드니솔론×칼륨(소론도정 199602982)이 PM-ready 그룹에 4번째로 합류했다(dry-run 60→64·`scripts/validate_potassium_dryrun_v1_2.py` PASS). whitelist 는 이제 {DF01,DF04,DF05,DF-PRED-01}, reviewer 노트는 **4건 전건 명시** 필요. 아래 원안의 '3건'을 '4건'으로 읽을 것.

> **선행 충족 필수(전부)**: ①clinical reviewer 노트 확보(`verdict=approved`, `docs/MediStack_clinical_reviewer_handoff_v1_2.md` §2 질문 답) ②CQF03 등 correctness 항목은 이 통합과 무관(CQF03 는 wording-review 라 **대상 아님** — whitelist 밖) ③별도 PM 승인.
>
> **현재 상태**: 칼륨 6건 재검토 완료(6/6 survives·`meta.rereview_2026_06_15`). PM-ready 3건(DF01 메틸프레드니솔론·DF04 아세타졸아미드·DF05 아조세미드)은 **통합 드라이런·검증기까지 완료**(`scripts/integrate_potassium_pm_ready_v1_2.py` dry-run + `scripts/validate_potassium_dryrun_v1_2.py` PASS·시뮬 v0.2 PASS·칼륨 안전카드·anti-supplement·제품0). 라이브 미반영(relations 60 불변).
>
> **작업**: 칼륨 PM-ready **4건만**(whitelist {DF01,DF04,DF05,DF-PRED-01}) v0.2 export 에 **멱등 append-only** 통합하라 — `python3 scripts/integrate_potassium_pm_ready_v1_2.py --pm-approved --reviewer-note <노트파일>`(멱등: (성분,칼륨) 이미 있으면 skip). **reviewer 노트 게이트(구조+의미+SAMPLE/placeholder)**: 노트가 비공란이고 + 승인 토큰('approved' 또는 '승인')을 담고 + **승격 대상 draft_id(DF01·DF04·DF05·DF-PRED-01)를 전건 명시**하고 + **SAMPLE 토큰·미기입 placeholder 가 없어야** 통과한다(검수자가 승인한 행만 승격). 미충족 시 STOP(스크립트가 가드 — garbage/공백/일부 누락/SAMPLE/빈칸 노트 거부). 복붙 템플릿은 핸드오프 §8-1, 게이트 회귀는 `scripts/test_reviewer_note_gate_v1_3.py`.
>
> **예상 변경**: relations 60→**64**(AT-FEX 미통합 시 id 62~65. AT-FEX 먼저 통합됐으면 baseline 조정 — id 는 max+1 런타임 계산이라 자동 정합). 각 행 nutrient=칼륨·mechanism=depletion·recommended_action=monitoring·evidence_level=high·`potassium_safety_card=true`·`product_link_allowed=false`·`requires_clinical_review=false`. display=PM-ready `final_display_text_ko_named`(약물명+장기/고용량/문의 종결)·management=통일 anti-supplement 문구. **full index/aliases 무변경**.
>
> **제외(통합 금지)**: DF02 덱사메타손·CQF03 히드로코르티손(wording-review)·DF03 플루드로코르티손(hold)·DF06/DF07 리오티로닌×칼슘/철분(비-칼륨·product_link_allowed=TRUE — 같은 factory 파일이지만 whitelist 밖). 스크립트가 draft_id 로 필터해 강제 차단.
>
> **불변(칼륨 트랙 특수 규칙)**: `potassium_safety_card=true`·`product_link_allowed=false`(칼륨 제품링크 영구 금지)·**칼륨 보충 권유 0·결핍 단정 0**·`disclaimers.potassium_notice` 노출·장기/고용량 맥락은 '상담'으로 종결(임의 보충·중단 지시 금지)·management 통일 문자열 정확 일치. published/clinical_reviewed=false 유지(reviewer 트랙은 별도 — 통합이 곧 clinical_reviewed 가 아님). reviewed_by 는 reviewer 만.
>
> **통합 후 검증(전수 PASS 필수)**: relation-count 하드코딩 validator **+4 누적 갱신**(AT-FEX 통합 순서에 따라 baseline 조정·`docs/MediStack_antacid_interaction_track_v1_2.md` §19.7) + v0.2 export validator(칼륨 일관성 #11) + `validate_potassium_pm_ready_v1_2.py`(큐 계약 — 승격 후에도 큐 파일은 불변) + 신규 `validate_potassium_integration_v1_2.py`(드라이런 검증기를 live 대상으로 전환) + potassium name_only policy + forbidden 0 + full smoke 9종 + no-live-write guard + deploy 게이트 + **live HTTP 200** + git clean.
>
> **승격은 제한적**(reviewer 가 승인한 행만·일괄 승격 금지). **금지**: reviewer 노트 없이 통합·clinical_reviewed=true·published=true·reviewed_by 작성·칼륨 제품링크·보충 권유·결핍 단정·DF02/CQF03/DF03/DF06/DF07 동반 통합.

근거/상세: `data/review/potassium_depletion_pm_ready_v1_2.json`(items·`meta.rereview_2026_06_15`) · `scripts/integrate_potassium_pm_ready_v1_2.py` · `scripts/validate_potassium_dryrun_v1_2.py` · `scripts/validate_potassium_pm_ready_v1_2.py` · `scripts/smoke_potassium_pm_ready_v1_2.py` · `docs/MediStack_clinical_reviewer_handoff_v1_2.md`.

---

## 프롬프트 3 — needs_review 다이유레틱/코르티코스테로이드 source 재확인(승격 아님) → **완료(2026-06-15)**

> **완료(2026-06-15)**: SDK-only online 재확인 수행. 결과 **새 draft 1** — 프레드니솔론×칼륨(소론도정 199602982, DF-PRED-01, draft-only `data/review/prednisolone_potassium_draft_recheck_v1_3.json`). loop/thiazide 5성분 8건(부메타니드·피레타니드·메토라존·트리클로르메티아지드·벤드로플루메티아지드)은 `searchDrug` 0건+철자변형 0 = **국내 미유통 확정 → reject(not_marketed_kr)**, 프레드니솔론×칼슘 reject, **하이드로코르티손×칼륨만 needs_review 유지**(CQF03 correctness 선결). 상세 → `docs/MediStack_needs_review_source_recheck_v1_3.md` · `data/review/needs_review_source_recheck_v1_3.json`.
>
> **갱신(2026-06-15, search-depth 라운드 완료)**: DF-PRED-01 을 칼륨 PM-ready 통합 준비 그룹에 **dry-run 으로 합류 완료**(4건·whitelist {DF01,DF04,DF05,DF-PRED-01}·`validate_potassium_dryrun_v1_2.py` PASS·60→64). 또한 search-depth 한계를 **항구 개선**: `search_itemseqs` 가 exact 주성분 부재 + substring 지배 시 deep_max_pages=20 까지 deep fallback(exact_only) 을 수행하도록 함 → 프레드니솔론이 이제 자동 포착(reason='ok_deep_exact'). 회귀 테스트 `scripts/test_search_depth_v1_3.py` 추가. **다음**: 프롬프트 2(칼륨 4건 통합)로 일원화 — reviewer note 후 통합. 미유통 8건은 재후보화 금지(국내 시판 시에만).

---

## 프롬프트 4 — search-depth 정책 회귀/확장(승격 아님)

> **완료분(2026-06-15)**: `search_itemseqs(opener, ingredient, ..., deep_max_pages=20)` — 얕은검색에 정확 주성분(주성분==성분명) 후보가 없고 결과가 성분명을 부분문자열로 포함하는 더 긴 주성분에 점유되면(예: 프레드니솔론 ⊂ 메틸프레드니솔론), deep_max_pages 까지 1회 deep fallback(exact_only). theme map 78 스캔 결과 deep fallback 발동은 **프레드니솔론 1건뿐**(나머지 21종 무변경=회귀 0). 회귀 테스트 4종(`scripts/test_search_depth_v1_3.py`).
>
> **완료분(2026-06-15 round3)**: ①**substring 지배 성분 발굴 완료** — `scripts/analyze_substring_domination_v1_3.py` → `data/review/substring_domination_scan_v1_3.json`. universe 366 에서 proper-substring 쌍 40(접두사형 다른약물 5 / 접미사형 염·수화물 35). 접두사형 5 중 nutrient-scope = 프레드니솔론(처리)·오메프라졸·란소프라졸 — **오메프라졸/란소프라졸도 substring 지배지만 이미 live(base itemSeq 200411095/201308978 확정)라 조치 불필요**. ②**deep fallback 하드닝** — 발동 조건을 '연속 명칭 접두사(다른약물) 지배'로 한정(`_prefix_dominated`), 염/복합제는 deep 미발동. theme+PPI 스캔 deep 20→6(회귀 0, productive 3 보존). 회귀 테스트 5종으로 보강. ③**harvester full online run 재확인 완료** — D-CORT-01 프레드니솔론 자동 draft(source_confirmed 199602982) 반영 확인(`data/review/harvest_run3_summary_v1_3.json`, ops §10). runtime 큐 커밋 0.
>
> ↓아래는 완료 전 원안(보존).
>
> **(원안)** online run 이 draft-ready 신규는 0 이었으나, **needs_review 10건**(국내 경구 단일성분 대표 itemSeq 미확보로 fail-closed)을 backlog 로 남겼다. 상세 → `docs/MediStack_candidate_backlog_v1_3.md` §2-A · `data/review/harvest_run2_summary_v1_3.json`.
>
> **작업(준비 단계 — live 통합 아님)**: 아래 needs_review 후보의 **국내 경구·단일성분·정상 완제 대표 품목 + itemSeq** 를 SDK(`medistack_sdk`)로 재확인하고, 라벨에 **방향성 직접 동거어**(칼륨/마그네슘/칼슘 + 고갈 방향)가 실제 있는 품목만 draft 후보로 끌어올려라. 못 찾으면 needs_review 유지(fail-closed). **계열 일반화로 채택 금지 — 품목별 라벨 직접 확인 필수.**
>
> **대상**: 프레드니솔론×칼륨(D-CORT-01) · 부메타니드×칼륨(D-LOOP-01) · 피레타니드×칼륨(D-LOOP-03) · 메토라존×칼륨(D-THZ-01) · 트리클로르메티아지드×칼륨(D-THZ-03) · 벤드로플루메티아지드×칼륨(D-THZ-05). Mg/칼슘 방향(D-CORT-02·D-LOOP-02·D-THZ-02·D-THZ-04)은 라벨 직접 동거어가 확인될 때만(약신호 약할 수 있음).
>
> **우선순위**: 프레드니솔론(코르티코스테로이드, 시장 큼) > 부메타니드·피레타니드(loop) > 메토라존·트리클로르메티아지드·벤드로플루메티아지드(thiazide).
>
> **제외/주의**: K-sparing(스피로노락톤·에플레레논·아밀로라이드·트리암테렌)·SGLT2×Mg·thiazide×칼슘은 **칼륨/전해질 상승 방향**이라 depletion factory 와 정반대 — 절대 depletion 후보로 만들지 말 것(hold 유지, §2-C). 세파계×철분 10종은 한국 허가사항 미기재로 **reject 확정**(재후보화 금지).
>
> **불변**: 봇/스크립트는 `data/harvest_queue/` 밖 무수정 · live relation 생성 0 · published/clinical_reviewed=false · 칼륨 행 product_link=false·potassium_safety_card=true · 칼륨 보충 권유/결핍 단정 0. 산출물은 draft-only(`live_integration_forbidden=true`) — 실제 승격은 PM + clinical reviewer 후 별도.

근거/상세: `docs/MediStack_candidate_backlog_v1_3.md` · `data/review/harvest_run2_summary_v1_3.json` · `data/review/harvest_run3_summary_v1_3.json` · `data/review/substring_domination_scan_v1_3.json` · `scripts/harvest_relation_bot_v1_3.py` · `scripts/verify_factory_sources_v1_2.py`.

---

## 프롬프트 5 — substring 지배 후속 deep-check (선택 · 승격 아님)

> **완료(2026-06-15 round3 후속)**: ①full drug name index distinct ingredient 전체(2,225)∪alias(27)∪seed(367)=scan **2,292**(단일성분 922)로 universe 확대 재산출 완료(`scripts/analyze_substring_search_risk_v1_3.py`→`data/review/substring_search_risk_v1_3.json`·`docs/MediStack_substring_search_risk_v1_3.md`). **diff-active 접두사** vs **형태접두사(무수/미세/제피)** vs 염/수화물 분리 분류. high 10/medium 14/salt_trap 143/no_action 2. deep-check 결과 **shallow_miss = baseline 3종뿐(프레드니솔론·오메프라졸·란소프라졸)**, 신규 diff-active 7종 전부 shallow_already_safe + 영양소 트랙 밖 → **신규 substring false-negative 0·신규 draft 0**. ③오메/란소 live 대표 itemSeq(200411095/201308978)는 base 정확 확인, deep-pick(199202074/200301515)과 정합은 선택(둘 다 valid·미실시).
>
> **차기(필요 시)**: ①medium_risk 14종(트레티노인·프로게스테론·설피리드·페니토인·케타민 등)은 해당 성분이 relation 후보化될 때만 deep-check(재후보화 게이트). ②`_prefix_dominated` production 발동을 형태접두사(무수/미세/제피)까지 차단할지(현재 무해 1회 deep·보류 권장). ③오메/란소 대표 itemSeq deep-pick 정합(필수 아님).
>
> **불변**: 분석/탐색 산출물은 `data/review/` 만 · live/export/full index/aliases 무수정 · deep-check 는 SDK-only(직접 http 금지) · runtime 큐 커밋 0 · live 승격 0.
>
> 근거: `scripts/analyze_substring_search_risk_v1_3.py` · `data/review/substring_search_risk_v1_3.json` · `docs/MediStack_substring_search_risk_v1_3.md` · ops §11.

---

## 프롬프트 6 — harvester schedule 활성화 검토 (아직 실행 아님)

> **상태**: schedule 은 여전히 비활성(harvest.yml `cron:` 주석). 이 프롬프트는 **활성화 자체가 아니라 활성화 가부를 검토**하는 단계다. 본 라운드까지 활성화 0.
>
> **선행 점검(전건 통과 시에만 검토 진행 — ops §12 체크리스트)**: ①여러 회의 수동 `workflow_dispatch`(offline+online) run 이 큐 validator 무위반으로 안정 ②no-live-write guard 무위반 지속 ③runtime 큐 커밋 0 유지 ④direct-http allowlist 감소 ⑤PM review queue 피드백 반영.
>
> **작업(검토 단계 — live/자동 통합 아님)**: ops §12 의 schedule 켜기 전 체크리스트를 한 항목씩 점검하고, 통과하면 `.github/workflows/harvest.yml` 의 `schedule:`/`cron:` 주석 해제를 **PR 로만** 제안하라(직접 main push 금지). 최소 diff·PR 체크리스트·구조 검증은 **`docs/MediStack_harvester_schedule_activation_v1_3.md`**(+ 미리보기 `data/review/harvester_schedule_activation_patch_preview_v1_3.json`)에 정리돼 있으니 그대로 따른다. PR 본문에 §12 체크리스트 결과 + `python3 scripts/validate_harvester_schedule_safety_v1_3.py` 결과(활성화 PR 에선 R1 외 R2~R9 PASS)를 첨부한다. cron 초안 = KST 월 03:00(UTC 일 18:00). **schedule 을 켜더라도** 자동 run 은 `workflow_dispatch` 와 동일 경로(mode/commit 입력)·commit 기본 false·output=artifact only 여야 한다.
>
> **불변(켠 뒤에도)**: 자동 run 은 후보 수집·라우팅만 — **integrate_*.py / live 통합은 절대 자동 실행 금지**. 승격은 항상 사람 PM + source 재확인 + clinical reviewer 노트(핸드오프 §8 / reviewer 패키지) + `--pm-approved --reviewer-note` 수동 단계. 자동 run 실패는 알림/보고로만 처리(자동 재시도로 live 쓰기 시도 금지). 보호셋 sha256 불변·write-scope=`data/harvest_queue/` 한정·published/clinical_reviewed=false 유지.
>
> **금지**: schedule 활성화를 main 에 직접 push · 자동 integrate · 자동 커밋/자동 PR 머지 · runtime 큐 커밋 · live 승격.

근거/상세: `docs/MediStack_harvester_schedule_activation_v1_3.md` · `docs/MediStack_harvester_ops_v1_3.md` §4·§7·§12 · `scripts/validate_harvester_schedule_safety_v1_3.py` · `.github/workflows/harvest.yml` · `scripts/guard_no_live_write_v1_3.py`.

---

## 프롬프트 7 — 새 theme map / seed 확장으로 신규 relation family 후보 설계 (draft-only · 승격 아님) → **1차 실행 완료(2026-06-15)**

> **✅ 실행됨(2026-06-15, theme map expansion 라운드)**: 신규 family **3종** 설계 + SDK source-check 로 **draft-only 6건 확정**(승격 0). 산출물 = `docs/MediStack_theme_map_expansion_v1_3.md`(정본) · `data/review/theme_map_expansion_candidates_v1_3.json`(13후보) · `data/review/theme_map_source_check_queue_v1_3.json` · `data/review/theme_map_source_check_results_v1_3.json` · `data/drafts/theme_map_draft_batch_v1_3.json`(6 draft) · `scripts/sourcecheck_theme_map_expansion_v1_3.py` · `scripts/validate_theme_map_expansion_v1_3.py`(결함주입 6 PASS) · `scripts/smoke_theme_map_draft_render_v1_3.py`. **source-confirmed 6**: 오르리스타트×지용성비타민(200806047) · 콜레스티라민×지용성비타민A·D·K(198800813) · 세프포독심·세프디토렌×제산제/H2(199300168·199500901) · 페니실라민×철분·아연(198300142). hold 4 · needs_review 2 · source_check 1. **남은 일은 아래 프롬프트 8.** 아래 원문은 방법론 참고용으로 보존.
>
> **왜 이 프롬프트인가**: harvester 2차·3차 online run 이 입증했듯 **같은 theme map 을 반복 run 하면 draft 분포가 기존 트리아지로 수렴**하고 신규 draft-ready 는 0 이다(같은 seed → 같은 결과). substring 광역 탐색(universe 2,292)에서도 신규 위험 0. 따라서 신규 relation 확장은 **새 theme map/seed 의 수동 추가**가 선행돼야 한다(`docs/MediStack_candidate_backlog_v1_3.md` §3).
>
> **작업(준비 단계 — live 통합 아님)**: 새 약-영양소 relation **family 후보**를 설계하라. ①기존 트리아지/live/reject 와 겹치지 않는 **새 theme(예: 새 약물군 × 새 영양소 방향)** 를 1~2개 선정하고 근거 가설을 적는다. ②각 후보를 harvester source-check 경로(`verify_factory_sources_v1_2.py` / source_confirm_gate)로 돌려, **한국 허가사항 라벨에 방향성 직접 동거어가 실제 있는 품목만** draft 후보로 끌어올린다(SDK-only·fail-closed). ③산출물은 **draft-only**(`do_not_implement_yet=true`·`live_integration_forbidden=true`) `data/review/` 아티팩트 + 백로그 갱신.
>
> **선정 기준(중요)**: **source-confirmed only**(라벨 직접 동거어) · **계열 일반화 채택 금지**(품목별 라벨 직접 확인) · **high-risk hold**(K-sparing 칼륨 상승·SGLT2×Mg 등 방향 반대/민감군은 hold, depletion 카드로 만들지 말 것) · 미유통(`searchDrug` 0건)은 reject(재후보화는 국내 시판 시에만).
>
> **불변**: 봇/스크립트는 `data/harvest_queue/` 밖 무수정 · live relation 생성 0 · published/clinical_reviewed=false · 칼륨 행 product_link=false·potassium_safety_card=true · 칼륨 보충 권유/결핍 단정 0 · 제품/구매/제휴 UI 0. 실제 승격은 PM + clinical reviewer 후 별도. **draft-only 산출까지가 이 프롬프트의 범위.**

근거/상세: `docs/MediStack_candidate_backlog_v1_3.md` §3 · `docs/MediStack_relation_factory_source_check_v1_2.md` · `scripts/verify_factory_sources_v1_2.py` · `scripts/source_confirm_gate_v1_2.py` · `scripts/harvest_relation_bot_v1_3.py`.

## 프롬프트 8 — theme map expansion draft 6건 적대검증 + 후속 source-check (승격 아님)

> **상태**: 프롬프트 7 의 draft-only 6건(`data/drafts/theme_map_draft_batch_v1_3.json`)이 source-confirmed 로 대기. live 통합은 PM + clinical reviewer 후 별도 PR.
>
> **작업(준비 단계 — live 통합 아님)**: ①6건 사용자 카피를 **적대검증**(서로 다른 렌즈): (a) orlistat·cholestyramine 카피가 **비타민 보충 권유**로 읽히지 않는가(라벨은 권장하나 우리는 시점 분리만), (b) cholestyramine 의 **비타민K 언급이 항응고 맥락**으로 오인되지 않는가, (c) 세팔로스포린 counterpart 가 **약물(제산제/H2)** 임이 분명한가(Mg 영양제 혼동 0), (d) 원문보다 강하지 않은가. ②counterpart_category 정렬 결정: 세팔로스포린 antacid 를 id61 `al_mg_antacid` 통합 vs 신규 `acid_reducing_drug`. ③nutrient_group("지용성 비타민") 단일 카드 vs 비타민별 분리. ④2차 source-check: TM-LIP-03(콜레세벨람)·TM-CHEL-03(메틸도파)·TM-B6-01(이소니아지드, **copy 게이트 선결**) — `scripts/sourcecheck_theme_map_expansion_v1_3.py` 에 후보 추가(SDK-only·≤2 fetch).
>
> **불변**: live relation 생성 0 · published/clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 UI 0 · 보충 권유/결핍 단정 0 · high-risk hold(페니토인/마이코페놀레이트/레보도파×B6)는 draft 격상 금지. **검증**: `scripts/validate_theme_map_expansion_v1_3.py` + `scripts/smoke_theme_map_draft_render_v1_3.py`.

## 프롬프트 9 — harvester theme map 편입 PR (후속 · PM 승인 전제)

> **상태**: 신규 family(지용성비타민 흡수·세팔로스포린 antacid·페니실라민 킬레이트)는 현재 `vfs.SEARCH_INGREDIENTS`(25)/`ANTACID_CANDIDATES`(AT-ITZ만)에 **미편입**. 자동 run 대상 아님.
>
> **작업**: 신규 family seed 를 harvester theme map 에 편입할지 결정하는 **PR 설계**(편입 자체는 PM 승인 후). 편입 순서는 반드시 **source-check queue → PM review → draft-only → live 금지**. schedule 은 비활성 유지(프롬프트 6). runtime queue(`data/harvest_queue/`) 커밋 금지. 같은 theme map 반복 run 비효율(신규 0 수렴) 인지 — 신규 seed 만 가치.
>
> 근거: `docs/MediStack_theme_map_expansion_v1_3.md` §6 · `docs/MediStack_harvester_ops_v1_3.md` §13.
