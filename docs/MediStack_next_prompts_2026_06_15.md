# MediStack — 다음 라운드 프롬프트 (2026-06-15 핸드오프)

작성일: 2026-06-15 · 상태: **핸드오프 / 실행 금지(차기 PM 라운드용)** · 자기완결

이 문서는 다음 두 작업의 **실행 프롬프트 초안**이다. 둘 다 **별도 PM 승인 + clinical reviewer 가 전제**이며, 이번 라운드에서 실행하지 않는다. 현재 라이브 상태(2026-06-15): main HEAD = clinical reviewer 핸드오프 준비 커밋, relations 60(AT-ITZ id61 live), AT-FEX 미통합, 칼륨 PM-ready 6건 미승격(3건 통합 드라이런 완료), published/clinical_reviewed=false, DATA_URL v0.2, 제품/제휴 UI 0.

> **갱신(2026-06-15)**: 프롬프트 2가 '칼륨 PM-ready **재검토**'였으나 재검토는 완료됐다(6건 확정·6/6 survives·`data/review/potassium_depletion_pm_ready_v1_2.json` `meta.rereview_2026_06_15`). 또한 PM-ready 3건(DF01·DF04·DF05)의 **live 통합 준비(드라이런·검증기)**까지 끝났다. 그래서 프롬프트 2를 다음 실제 작업인 **'칼륨 PM-ready 3건 live 통합'**으로 교체한다. reviewer 핸드오프: `docs/MediStack_clinical_reviewer_handoff_v1_2.md`.

---

## 프롬프트 1 — AT-FEX(펙소페나딘 · avoid_concomitant) live 통합

> **선행 충족 필수(전부)**: ①clinical reviewer 확보 ②source 202202380(avoid_concomitant '…제산제를 복용하지 마십시오') directive 재대조 + `source.checked_at` 갱신 ③evidence_level=moderate PM 승인(또는 조정) ④round4 적대검증 재확인(카피/표면 변경 시).
>
> **작업**: AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, **avoid_concomitant**) **1건만** v0.2 export 에 멱등 append-only 통합하라 — `python3 scripts/integrate_antacid_fex_v1_2.py --pm-approved`(멱등: 이미 있으면 skip). 드라이런 검증은 `scripts/validate_antacid_fex_dryrun_v1_2.py` 로 이미 통과(시뮬 export v0.2 PASS·전용 chip·facet 제외·live 무수정).
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

## 프롬프트 2 — 칼륨 depletion PM-ready 3건(DF01·DF04·DF05) live 통합

> **선행 충족 필수(전부)**: ①clinical reviewer 노트 확보(`verdict=approved`, `docs/MediStack_clinical_reviewer_handoff_v1_2.md` §2 질문 답) ②CQF03 등 correctness 항목은 이 통합과 무관(CQF03 는 wording-review 라 **대상 아님** — whitelist 밖) ③별도 PM 승인.
>
> **현재 상태**: 칼륨 6건 재검토 완료(6/6 survives·`meta.rereview_2026_06_15`). PM-ready 3건(DF01 메틸프레드니솔론·DF04 아세타졸아미드·DF05 아조세미드)은 **통합 드라이런·검증기까지 완료**(`scripts/integrate_potassium_pm_ready_v1_2.py` dry-run + `scripts/validate_potassium_dryrun_v1_2.py` PASS·시뮬 v0.2 PASS·칼륨 안전카드·anti-supplement·제품0). 라이브 미반영(relations 60 불변).
>
> **작업**: 칼륨 PM-ready **3건만**(whitelist {DF01,DF04,DF05}) v0.2 export 에 **멱등 append-only** 통합하라 — `python3 scripts/integrate_potassium_pm_ready_v1_2.py --pm-approved --reviewer-note <노트파일>`(멱등: (성분,칼륨) 이미 있으면 skip). **reviewer 노트 게이트(구조+의미)**: 노트가 비공란이고 + 승인 토큰('approved' 또는 '승인')을 담고 + **승격 대상 draft_id(DF01·DF04·DF05)를 전건 명시**해야 통과한다(검수자가 승인한 행만 승격). 미충족 시 STOP(스크립트가 가드 — garbage/공백/일부 누락 노트 거부).
>
> **예상 변경**: relations 60→63(AT-FEX 미통합 시 id 62~64. AT-FEX 먼저 통합됐으면 baseline 조정 — id 는 max+1 런타임 계산이라 자동 정합). 각 행 nutrient=칼륨·mechanism=depletion·recommended_action=monitoring·evidence_level=high·`potassium_safety_card=true`·`product_link_allowed=false`·`requires_clinical_review=false`. display=PM-ready `final_display_text_ko_named`(약물명+장기/고용량/문의 종결)·management=통일 anti-supplement 문구. **full index/aliases 무변경**.
>
> **제외(통합 금지)**: DF02 덱사메타손·CQF03 히드로코르티손(wording-review)·DF03 플루드로코르티손(hold)·DF06/DF07 리오티로닌×칼슘/철분(비-칼륨·product_link_allowed=TRUE — 같은 factory 파일이지만 whitelist 밖). 스크립트가 draft_id 로 필터해 강제 차단.
>
> **불변(칼륨 트랙 특수 규칙)**: `potassium_safety_card=true`·`product_link_allowed=false`(칼륨 제품링크 영구 금지)·**칼륨 보충 권유 0·결핍 단정 0**·`disclaimers.potassium_notice` 노출·장기/고용량 맥락은 '상담'으로 종결(임의 보충·중단 지시 금지)·management 통일 문자열 정확 일치. published/clinical_reviewed=false 유지(reviewer 트랙은 별도 — 통합이 곧 clinical_reviewed 가 아님). reviewed_by 는 reviewer 만.
>
> **통합 후 검증(전수 PASS 필수)**: relation-count 하드코딩 validator **+3 누적 갱신**(AT-FEX 통합 순서에 따라 baseline 조정·`docs/MediStack_antacid_interaction_track_v1_2.md` §19.7) + v0.2 export validator(칼륨 일관성 #11) + `validate_potassium_pm_ready_v1_2.py`(큐 계약 — 승격 후에도 큐 파일은 불변) + 신규 `validate_potassium_integration_v1_2.py`(드라이런 검증기를 live 대상으로 전환) + potassium name_only policy + forbidden 0 + full smoke 9종 + no-live-write guard + deploy 게이트 + **live HTTP 200** + git clean.
>
> **승격은 제한적**(reviewer 가 승인한 행만·일괄 승격 금지). **금지**: reviewer 노트 없이 통합·clinical_reviewed=true·published=true·reviewed_by 작성·칼륨 제품링크·보충 권유·결핍 단정·DF02/CQF03/DF03/DF06/DF07 동반 통합.

근거/상세: `data/review/potassium_depletion_pm_ready_v1_2.json`(items·`meta.rereview_2026_06_15`) · `scripts/integrate_potassium_pm_ready_v1_2.py` · `scripts/validate_potassium_dryrun_v1_2.py` · `scripts/validate_potassium_pm_ready_v1_2.py` · `scripts/smoke_potassium_pm_ready_v1_2.py` · `docs/MediStack_clinical_reviewer_handoff_v1_2.md`.

---

## 프롬프트 3 — needs_review 다이유레틱/코르티코스테로이드 source 재확인(승격 아님)

> **추가(2026-06-15, harvester 2차 online run 산물)**: online run 이 draft-ready 신규는 0 이었으나, **needs_review 10건**(국내 경구 단일성분 대표 itemSeq 미확보로 fail-closed)을 backlog 로 남겼다. 상세 → `docs/MediStack_candidate_backlog_v1_3.md` §2-A · `data/review/harvest_run2_summary_v1_3.json`.
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

근거/상세: `docs/MediStack_candidate_backlog_v1_3.md` · `data/review/harvest_run2_summary_v1_3.json` · `scripts/harvest_relation_bot_v1_3.py` · `scripts/verify_factory_sources_v1_2.py`.
