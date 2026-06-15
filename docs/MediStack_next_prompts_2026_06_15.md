# MediStack — 다음 라운드 프롬프트 (2026-06-15 핸드오프)

작성일: 2026-06-15 · 상태: **핸드오프 / 실행 금지(차기 PM 라운드용)** · 자기완결

이 문서는 다음 두 작업의 **실행 프롬프트 초안**이다. 둘 다 **별도 PM 승인 + clinical reviewer 가 전제**이며, 이번 라운드에서 실행하지 않는다. 현재 라이브 상태(2026-06-15): main HEAD = avoid_concomitant 준비 커밋, relations 60(AT-ITZ id61 live), AT-FEX 미통합, 칼륨 PM-ready 6건 미승격, published/clinical_reviewed=false, DATA_URL v0.2, 제품/제휴 UI 0.

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

## 프롬프트 2 — 칼륨 depletion PM-ready 재검토

> **현재 상태(`data/review/potassium_depletion_pm_ready_v1_2.json`)**: 6건, 전건 source_confirmed high(적대검증 통과)·`live_integration_forbidden=true`(미승격). 분류 = **PM-ready 3**(DF01 메틸프레드니솔론·DF04 아세타졸아미드·DF05 아조세미드, `promotion_candidate=true`) / **needs_clinical_wording_review 2**(DF02 덱사메타손·CQF03 히드로코르티손) / **hold_continue 1**(DF03 플루드로코르티손). 전건 `potassium_safety_card=true`·`product_link_allowed=false`·published/clinical_reviewed=false·reviewed_by 공란.
> ⚠️ **카운트 확인 필요**: 핸드오프 지시는 "칼륨 5건"이라 했으나 PM-ready 파일은 **6건**이다(5 vs 6 불일치 — PM 가 대상 집합을 확정할 것. 아래 작업은 파일 6건 기준).
>
> **작업(clinical reviewer 전제)**: 칼륨 depletion 행의 live 승격은 **임상 검수 노트 확보 후에만** 진행한다. 이번 단계는 ①needs_clinical_wording_review 2건의 장기/고용량/상담 문구를 clinical reviewer 와 함께 확정 ②PM-ready 3건의 승격 가부를 reviewer 노트로 결정 ③hold_continue 1건은 근거 보강 여부 판단.
>
> **불변(칼륨 트랙 특수 규칙)**: `potassium_safety_card=true`(칼륨 고지 카드 필수)·`product_link_allowed=false`(칼륨 제품링크 영구 금지)·**칼륨 보충 권유 0·결핍 단정 0**·`disclaimers.potassium_notice` 노출·장기/고용량 맥락은 '상담'으로 종결(임의 보충·중단 지시 금지). published/clinical_reviewed=false 는 reviewer 노트 확보 전까지 유지.
>
> **승격 시(reviewer 후, 별도 라운드)**: 멱등 integrate(칼륨 행 패턴) + relations 수 갱신 + v0.2 validator(칼륨 일관성 #11: nutrient=칼륨 ⇒ link=false&card=true) + potassium policy validator + forbidden 0 + full smoke + deploy + live HTTP 200. **승격은 제한적**(reviewer 가 승인한 행만, 일괄 승격 금지).
>
> **금지**: reviewer 노트 없이 clinical_reviewed=true 전환·published=true·reviewed_by 작성·칼륨 제품링크·보충 권유·결핍 단정·일괄 자동 승격.

근거/상세: `data/review/potassium_depletion_pm_ready_v1_2.json`(policy/distribution/promotion_candidates) · `scripts/validate_potassium_pm_ready_v1_2.py` · `scripts/smoke_potassium_pm_ready_v1_2.py`.
