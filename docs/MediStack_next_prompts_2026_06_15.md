# MediStack — 다음 라운드 프롬프트 (2026-06-15 핸드오프)

작성일: 2026-06-15 · 상태: **핸드오프 / 실행 금지(차기 PM 라운드용)** · 자기완결

이 문서는 다음 두 작업의 **실행 프롬프트 초안**이다. 둘 다 **별도 PM 승인 + clinical reviewer 가 전제**이며, 이번 라운드에서 실행하지 않는다. 현재 라이브 상태(2026-06-15): main HEAD = clinical reviewer 핸드오프 준비 커밋, relations 60(AT-ITZ id61 live), AT-FEX 미통합, 칼륨 PM-ready 6건 미승격(3건 통합 드라이런 완료), published/clinical_reviewed=false, DATA_URL v0.2, 제품/제휴 UI 0.

> **갱신(2026-06-17, F4/F6/F10 small-family bundle reviewer-gated 통합 준비 라운드)**: remaining unpackaged 3 family(F4/F6/F10·각 reviewer-ready 1)를 small-family bundle 로 family-specific 재검증(작업 B/C·16 렌즈·refute-by-default) → **survives 0 · survives_with_copy_change 2 · needs_review 1**. **통합 가능 2건(60→62)** = 레보티록신×알루미늄제산제(absorption/separation/al_mg_antacid) + 에스오메프라졸×비타민B12(depletion/monitoring). 🔑 **헤드라인 3건**: ①**케토코나졸×제산제(0275) route/availability 강등** — 소스 더마졸정 **수출용**(export-only) oral tablet 이나 full index 국내 케토코나졸 10품목 **전부 외용(액/크림)** → 경구 흡수×제산제 카드를 ingredient 에 붙이면 외용 제품 오부착. 광역 10-lens L8(소스가 tablet→pass)이 놓친 것을 family **L6_route_domestic_availability**(full index 형태 분류)가 국내 oral 0 → fail → **needs_review**. live 선례 id61(이트라코나졸)은 국내 제품 사용·동일 mechanism 이나 케토코나졸은 국내 외용 전용. ②**레보티록신×제산제(0173) Al-only copy_change** — 라벨 '**알루미늄** 함유 제산제'만 명시(Mg 미명시) → al_mg_antacid display 의 Mg 단정은 source 보다 강함 → counterpart/display 를 '알루미늄 함유 제산제(약물)'로 좁히고 Mg 비단정·'효과 감소'→'흡수 지연/감소'(라벨 충실). live id61 도 수산화알루미늄→'Al/Mg' 일반화(동일 latent reviewer surface). ③**에스오메프라졸×B12(0201) PPI 톤 정합 copy_change** — 오메프라졸(id13) S-거울상 → PPI×B12 5건(id13/32/34/36/38)+메트포르민(id12) live depletion/monitoring 계열 합류·draft '수치 변화'→**live PPI×B12 표준 템플릿** reframe(소스는 복합제 낙소졸정·quote 가 에스오메프라졸 명시→reviewer 단일성분 보강). **선행조건 0**(id61·id12/id13 렌더 선례·src 무수정)·index 자동 flip 0·**latent 0**(레보티록신 covered·에스오 standalone 색인 0·케토 외용·relation_card 1168/name_only 16412 불변). 신규: `scripts/integrate_f4_f6_f10_small_family_batch_v1_4.py`(dry-run·`--scope integrable/all/family:F4/F6/F10`·`--candidate-ids`·`--base-count`·needs_review STOP·`--pm-approved --reviewer-note` 전제) → `data/review/f4_f6_f10_small_family_{inventory,live_dryrun,index_impact}_v1_4.json`(60→62·id 62~63·sha 불변·F1+F2+F3+F9 후 91→93·conditional 0275 60→63/91→94) · `validate_f4_f6_f10_small_family_dryrun_v1_4.py`(결함주입 14·needs_review 통합 차단·F4 Mg 비단정·0275 dosing 차단) · `test_f4_f6_f10_small_family_reviewer_note_gate_v1_4.py`(temp write integrable 60→62·family:F4/F6 60→61·needs_review block·idempotency·live sha 불변) · `smoke_f4_f6_f10_small_family_dryrun_v1_4.py`(2 카드·F10 family context) · docs `MediStack_{inventory,grouping_strategy,index_impact}_f4_f6_f10_small_family_v1_4.md`·`reviewer_package_f4_f6_f10_small_family_v1_4.md`·`MediStack_factory_v1_5_trigger_policy_v1_4.md`. **글로벌 reviewer-ready 37 계획 갱신**: F4/F6/F10 pending→reverified → family map F1 18✅/F2 5✅/F3 1✅/F9 7✅/F4 1✅/F6 1✅/F10 0✅(needs_review) = **통합 가능 31→33 · pending 3→0 · needs_review 3→4(+F10 0275)**. 조합(disjoint·dedup 0): F4 60→61·F6 60→61·F4+F6 60→62·**F1+F2+F3+F9+F4+F6 60→93**(combined v0.2 sim PASS). `integrate_reviewer_ready_global_batch_v1_4.py`/`validate_global_reviewer_ready_dryrun_v1_4.py`/`MediStack_reviewer_ready_global_plan_v1_4.md` F4/F6/F10 반영. **Factory v1.5 = 보류 유지**(packaging 조건 **충족**(remaining unpackaged 0)이나 통합 가능 33 reviewer note·live PR 미완 + needs_review 4 미정리). F10 family context: 0276 hold(H2-blocker 주어 불일치)·0277 reject(=live id61 중복). ↓이전:
> **갱신(2026-06-17, F9 만성복용 depletion reviewer-gated 통합 준비 라운드)**: factory reviewer-ready 37 중 **F9 만성복용 depletion 8건**을 family-specific 재검증(작업 C·16 렌즈·refute-by-default) → **survives 3 · survives_with_copy_change 4 · needs_review 1**. **통합 가능 7건(60→67)**. 항전간제(페노바르비탈·페니토인·프리미돈·카르바마제핀)·설파살라진·트리메토프림 × **엽산/비타민D**(mechanism=depletion·action=monitoring·counterpart_category 없음, live 렌더 선례 메트포르민×비타민B12 id12). 🔑 **헤드라인 3건**: ①**카르바마제핀×엽산(0245) 강등** — 인용 '드물게 ... 엽산 결핍증'은 이상반응 열거 안 bare 항목으로 흡수/대사 기전 동사·혈청엽산치 level-direction·연용-remedy framing **모두 없음**('드물게' 빈도) → F9 **저신호 이상반응 열거**(adversarial 옥스카르바제핀 강등 패턴 동형) → needs_review(카르바마제핀은 ×비타민D 0246 으로 coverage 유지·약물 누락 아님). ②**항전간제×비타민D 3건(0252/0243/0255) copy_change** — 라벨이 연용 골연화증 + 비타민D **섭취/투여(remedy)**만 적시(vitD '수치 저하' 미명시) → display '비타민D 수치 변화'→'비타민D와 관련된 주의 문구' reframe(측정치 단정·골질환 알람어 비노출). ③**페니토인×엽산(0242) copy_change** — '혈청엽산치 저하' 명시(strong)·quote 끝 stray ' 1' 트림(F1 stray '1' 동형). **선행조건 0**·index 자동 flip 0(6개 약물 전부 name_only·alias decoupled·relation_card 1168/name_only 16412 불변·통합분 alias-enrich 시 조건부 latent ≤18 별도). 신규: `scripts/integrate_f9_chronic_depletion_batch_v1_4.py`(dry-run·`--scope integrable/survives/copy_change/folate/vitd`·`--base-count`·needs_review STOP·`--pm-approved --reviewer-note` 전제) → `data/review/f9_chronic_depletion_{inventory,live_dryrun,index_impact}_v1_4.json`(60→67·id 62~68·sha 불변·F1+F2+F3 후 84→91) · `validate_f9_chronic_depletion_dryrun_v1_4.py`(결함주입 13·needs_review 통합 차단) · `test_f9_chronic_depletion_reviewer_note_gate_v1_4.py`(temp write integrable 60→67·folate 60→63·needs_review block·idempotency·live sha 불변) · `smoke_f9_chronic_depletion_dryrun_v1_4.py`(7 카드) · docs `MediStack_f9_chronic_depletion_{inventory,grouping_strategy,index_impact}_v1_4.md`·`reviewer_package_f9_chronic_depletion_v1_4.md`. **글로벌 reviewer-ready 37 계획 갱신**: F9 pending→integrable → family map F1 18✅/F2 5✅/F3 1✅/F9 7✅/F4 1⏳/F6 1⏳/F10 1⏳ = **통합 가능 24→31 · pending 11→3(F4/F6/F10)**. 조합(disjoint·dedup 0): F9 60→67·F3+F9 60→68·**F1+F2+F3+F9 60→91**(combined v0.2 sim PASS). `integrate_reviewer_ready_global_batch_v1_4.py`/`validate_global_reviewer_ready_dryrun_v1_4.py`/`MediStack_reviewer_ready_global_plan_v1_4.md` F9 반영. **Factory v1.5 = 보류 유지**(통합 가능 31 reviewer note·live PR 미완 + F4/F6/F10 family 재검증 미수행 + needs_review 3 미정리). 프롬프트 26(글로벌 wave) 통합 가능 31·60→91 반영 · 프롬프트 28(family 재검증) 범위 **F4/F6/F9/F10→F4/F6/F10** · **프롬프트 29 신설(F9 live 통합)**. ↓이전:
>
> **갱신(2026-06-17, F3 비스포스포네이트 + 글로벌 reviewer-ready 계획 라운드)**: factory reviewer-ready 37 중 **F3 비스포스포네이트 3건**을 family-specific 재검증(작업 C·14 렌즈·refute-by-default) → **survives 1 · needs_review 2 · copy_change 0**. 🔑 **헤드라인 발견 2건**: ①**에티드론산 0148/0149 강등** — 인용 "칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제"는 문법상 양이온이 **제산제에 결속**(제산제 함유 성분)이라 standalone 칼슘/철분 **보충제** 근거 취약(L3 fail) + 병용금기 **목록 fragment**라 흡수기전 동사 없음(L5 fail) → needs_review. live 알렌/리세/이반×칼슘 선례는 **타 약물 라벨** 근거라 적용 시 **계열 일반화(금지)**. ②**이반드론산 0147**(통합 가능 1건)은 live 에 ×칼슘(id41)/철분(id51)/마그네슘(id52) 이미 존재 → Al/Mg 제산제(약물·al_mg_antacid·id61 선례) 추가는 exact dup 0이나 정보가치 vs 중복 reviewer 판단. **F3 통합 가능 = 1건(0147)·60→61**. index: 이반드론산 covered(자동 flip 0·현 scope latent 0·relation_card 1168/name_only 16412 불변), 에티드론산 조건부 latent 1. 신규: `scripts/integrate_f3_bisphosphonate_batch_v1_4.py`(dry-run·`--scope survives/antacid1`·needs_review STOP·`--pm-approved --reviewer-note` 전제) → `data/review/f3_bisphosphonate_{inventory,live_dryrun,index_impact}_v1_4.json` · `validate_f3_bisphosphonate_dryrun_v1_4.py`(결함주입 12·needs_review 통합 차단) · `test_f3_bisphosphonate_reviewer_note_gate_v1_4.py`(temp write 60→61·needs_review block·idempotency·live sha 불변) · `smoke_f3_bisphosphonate_dryrun_v1_4.py`(1 카드) · docs `MediStack_f3_bisphosphonate_{inventory,grouping_strategy,index_impact}_v1_4.md`·`reviewer_package_f3_bisphosphonate_v1_4.md`. **+글로벌 reviewer-ready 37 계획**: `scripts/integrate_reviewer_ready_global_batch_v1_4.py`(no-live-write planner·`--families`) + `validate_global_reviewer_ready_dryrun_v1_4.py` → `data/review/reviewer_ready_global_plan_v1_4.json` · doc `MediStack_reviewer_ready_global_plan_v1_4.md`. **family map**: F1 18✅/F2 5✅/F3 3→1✅/F4 1⏳/F6 1⏳/F9 8⏳/F10 1⏳ = **통합 가능 24 · pending 11**(F4/F6/F9/F10 family 재검증 선행). **조합 시나리오**(disjoint·dedup 0): F1 60→78·F2 60→65·F3 60→61·F1+F2 60→83·F1+F3 60→79·F2+F3 60→66·**F1+F2+F3 60→84**(combined v0.2 sim PASS). **Factory v1.5 = 보류 권장**(통합 가능 24 reviewer note·live PR 미완 + pending family 재검증 미수행 + backlog 미정리). 프롬프트 23(F2)·**26~28** 신설(F3 live·글로벌 wave·F4/F6/F9/F10 family 재검증). ↓이전:
>
> **갱신(2026-06-17, F2 테트라사이클린 reviewer-gated 통합 준비 라운드)**: factory reviewer-ready 37 중 **F2 테트라사이클린 5건**(survives 5/5)을 reviewer-gated subset 으로 분리해 통합 준비 완료(live 0). split = nutrient 2(테트라사이클린×철분·아연) + al_mg_antacid 3(독시·미노·테트라사이클린 × Al/Mg 제산제). **작업 C family 재검증**(12+3 렌즈·refute-by-default): **survives 5 · copy_change 0 · 강등 0**. 🔑 family 차이: ①원문 '철ㆍ아연'이라 **철분→토큰 '철' 매핑**(F1 은 '철분' 리터럴). ②**독시/미노사이클린은 live 에 ×칼슘/철분/마그네슘/아연(영양소) 이미 존재** → Al/Mg 제산제(약물) relation 추가는 별도 counterpart(al_mg_antacid·id61 선례)로 **exact dup 0**이나 "정보 가치 vs 중복"은 **headline reviewer 결정**(gate 강제). ③**테트라사이클린 1건 index name_only 존재** → relation-only 통합 **자동 flip 0**(pool=aliases 와 decoupled·relation_card 1168/name_only 16412 불변), alias 등록 시에만 latent flip 1(1169/16411·별도 작업). **선행조건 0**(양 렌더 경로 live 검증: 독시/미노×광물·id61). 신규: `scripts/integrate_f2_tetracycline_batch_v1_4.py`(dry-run·`--scope all5/nutrient2/antacid3/top2/top3`·`--pm-approved --reviewer-note` 전제) → `data/review/f2_tetracycline_{inventory,live_dryrun,index_impact}_v1_4.json`(60→65·id 62~66·sha 불변·F1 후 78→83) · `test_f2_tetracycline_reviewer_note_gate_v1_4.py`(temp write all5/nutrient2/antacid3·idempotency·live sha 불변) · `validate_f2_tetracycline_dryrun_v1_4.py`(결함주입 12·재실행 reverify) · `smoke_f2_tetracycline_dryrun_v1_4.py`(5 카드) · docs `MediStack_f2_tetracycline_inventory_v1_4.md`·`_grouping_strategy_v1_4.md`·`reviewer_package_f2_tetracycline_v1_4.md`·`_index_impact_v1_4.md`. 권고 grouping = **all5 once(60→65)** 또는 overlap 격리 시 **by-counterpart 2-wave**(nutrient2 60→62 → antacid3 62→65). 프롬프트 20 완료·**23~25** 신설(F2 live 통합·F1+F2 antibiotic-mineral wave·F3 비스포스포네이트 package). ↓이전:
>
> **갱신(2026-06-16, F1 퀴놀론 reviewer-gated 통합 준비 라운드)**: factory reviewer-ready 37 중 **F1 플루오로퀴놀론 18건**(survives 18/18)을 reviewer-gated subset 으로 분리해 통합 준비 완료(live 0). **작업 C family 재검증**: 17 survives + **1 copy_change**(RF-F1-0020 오플록사신 끝 stray '1' 트림=verbatim 부분문자열) · 강등 0. **선행조건 0**(al_mg_antacid=id61 선례·일반 영양소=live FQ×광물 둘 다 현행 v0.2+src 지원) · **index/alias 무변경**(레보/오플 covered·신규 6 성분 sample 부재 → relation_card 1168/name_only 16412 불변). 신규: `scripts/integrate_f1_quinolone_batch_v1_4.py`(dry-run·`--scope all18/nutrient10/antacid8`·`--pm-approved --reviewer-note` 전제) → `data/review/f1_quinolone_{inventory,live_dryrun,index_impact}_v1_4.json`(60→78·id 62~79·sha 불변) · `test_f1_quinolone_reviewer_note_gate_v1_4.py`(temp write all18/nutrient10/antacid8·idempotency·live sha 불변) · `validate_f1_quinolone_dryrun_v1_4.py`(결함주입 12) · `smoke_f1_quinolone_dryrun_v1_4.py`(18 카드) · docs `MediStack_f1_quinolone_inventory_v1_4.md`·`_grouping_strategy_v1_4.md`·`reviewer_package_f1_quinolone_v1_4.md`·`_index_impact_v1_4.md`. 권고 grouping = **by-counterpart 2-wave**(nutrient10 60→70 → antacid8 70→78). 아래 **프롬프트 17~19** 신설. ↓이전:
>
> **갱신(2026-06-16, 페니실라민 reviewer decision 하드닝 라운드)**: reviewer note 실물 **없음 확인 → live 0** 유지. subset 통합기에 **부분 승인 시나리오**(`meta.partial_approval_scenarios`: both 60→62·id 62,63 / FE_only·ZN_only 60→61·**id 62=max+1** / neither 60) + `--only` STOP(미구현·both-approval 전제) 추가. validator 결함주입 **10종**(ZN_only id 오기 추가)·부분승인 일관성 검증. reviewer package **§8 결정 체크리스트·§9 PM decision table·§10 FE-only/ZN-only 근거·§11 rollback·post-live 검증** + mechanism doc **§5 Option 체크박스** 보강. **full-6 중복 생성 불가 실증**(FE/ZN live 인 temp 에 full-6 build → 2 violation→STOP). 프롬프트 14·15 갱신. ↓이전:
>
> **갱신(2026-06-16, 페니실라민 FE/ZN subset 통합 준비 라운드)**: theme map 6건 중 **페니실라민 × 철분/아연 2건만** subset 으로 분리해 reviewer-gated 준비 완료(승격 0). 둘 다 **counterpart_category=null(일반 영양소) → live 선행조건 0**(현행 v0.2 PASS 실증·src/facet/chip/validator/full index/aliases 변경 불필요) → theme map 6건 중 **가장 먼저 안전 통합 가능**. 신규: `scripts/integrate_penicillamine_subset_v1_3.py`(dry-run·`--pm-approved --reviewer-note` 전제) → `data/review/penicillamine_subset_live_dryrun_v1_3.json`(**60→62**·id 62~63·sha 불변·prerequisites []) · `test_penicillamine_reviewer_note_gate_v1_3.py` · `validate_penicillamine_subset_dryrun_v1_3.py`(결함주입 9) · `smoke_penicillamine_subset_v1_3.py` · docs `MediStack_reviewer_package_penicillamine_subset_v1_3.md` · `MediStack_penicillamine_mechanism_decision_v1_3.md`. **ZN mechanism 결정 = Option A**(absorption 추론 유지·confidence moderate·user 카피 '효과 감소' 충실 — Option B interaction 은 v0.2 ALLOWED_MECHANISM 밖이라 validator PR 선행 필요라 비채택). subset 게이트와 full-6 게이트는 **상호 배타**(노트 교차 거부)·dry-run artifact 분리. 아래 **프롬프트 14~16** 신설. ↓이전:

> **갱신(2026-06-15)**: 프롬프트 2가 '칼륨 PM-ready **재검토**'였으나 재검토는 완료됐다(6건 확정·6/6 survives·`data/review/potassium_depletion_pm_ready_v1_2.json` `meta.rereview_2026_06_15`). 또한 PM-ready 3건(DF01·DF04·DF05)의 **live 통합 준비(드라이런·검증기)**까지 끝났다. 그래서 프롬프트 2를 다음 실제 작업인 **'칼륨 PM-ready 3건 live 통합'**으로 교체한다. reviewer 핸드오프: `docs/MediStack_clinical_reviewer_handoff_v1_2.md`.

> **갱신(2026-06-15, reviewer-gated 하드닝 라운드)**: 두 통합 스크립트 모두 **의미적 reviewer-note 인터록**(`check_reviewer_note`) 보강 완료 — 칼륨=승인 토큰+draft_id 4건 전건, AT-FEX=승인 토큰+candidate_id+itemSeq 202202380+evidence moderate, 공통=**SAMPLE 토큰·미기입 placeholder 거부**. 복붙 reviewer note 템플릿은 핸드오프 §8, SAMPLE 주의는 §9, 회귀는 `scripts/test_reviewer_note_gate_v1_3.py`(invalid 거부+valid 통과+live export sha256 불변). 그래서 아래 프롬프트 1(AT-FEX)·2(칼륨)는 **`--pm-approved --reviewer-note <노트>` 둘 다** 전제로 갱신. 또한 **프롬프트 6(harvester schedule 활성화 검토)** 신설(아직 실행 아님). 본 라운드에서 실제 통합·schedule 활성화는 0.

> **갱신(2026-06-16, theme map reviewer-gated 통합 준비 라운드)**: 프롬프트 9 PR #3 **main merge 완료**(81e8ec6, deploy success, live 200). 이어 theme map 6건의 **live 통합 reviewer-gated 준비** 완료(승격 0): ①reviewer 패키지 `docs/MediStack_reviewer_package_theme_map_v1_3.md`(후보별 카드·reviewer-note 템플릿) ②category 정책 `docs/MediStack_counterpart_category_policy_v1_3.md` ③grouping 전략 `docs/MediStack_theme_map_grouping_strategy_v1_3.md` ④**dry-run integrator** `scripts/integrate_theme_map_draft_batch_v1_3.py`(기본 dry-run·`--pm-approved --reviewer-note` 전제·멱등) → `data/review/theme_map_live_dryrun_v1_3.json`(60→66·id 62~67·export sha 불변·live_write 0) ⑤reviewer-note 게이트 `scripts/test_theme_map_reviewer_note_gate_v1_3.py`(6건+category+grouping+mechanism+verified_reference·SAMPLE/promo 거부·temp write 60→66·live sha 불변) ⑥dry-run validator `scripts/validate_theme_map_live_dryrun_v1_3.py`(계약+결함주입 9) ⑦smoke `scripts/smoke_theme_map_live_dryrun_v1_3.py`. **핵심 발견(live 선행조건)**: v0.2 validator 검사 #15(avoid_concomitant⇒al_mg_antacid)가 TM-CEPH-AC-02(acid_reducing_drug+avoid_concomitant)를 차단 → separation 5건은 현행 v0.2 PASS, 6건 전체는 validator #15 확장 + src(getFacets nutrient_categories 포함·acid_reducing_drug chip) 선행조건 필요(별도 PR). live 통합·schedule·자동 integrate·export/index/alias/src 수정 0. 아래 **프롬프트 10~13** 신설. ↓이전:

> **갱신(2026-06-16, harvester 편입 PR 라운드)**: 프롬프트 9 **실행**(branch `harvester-theme-map-v1.3` + PR) — 신규 theme map 6건을 harvester 에 **candidate-only 편입**(manual flag `--include-theme-map-expansion`, 기본 비활성, config-driven 격리 provider). seed config `data/config/theme_map_seeds_v1_3.json` + provider `scripts/theme_map_harvest_provider_v1_3.py` → PM review queue(draft 6 + hold 7). 신규 category(acid_reducing_drug·fat_soluble_vitamin) review-level 처리. validator(17+결함주입 9)·smoke·guard(flag run) PASS. runtime `data/harvest_queue/theme_map_*` gitignore(커밋 0), 요약만 `data/review/theme_map_harvest_incorporation_v1_3.json` 커밋. **live 통합·schedule 활성화·자동 integrate·main push/merge 0.** 정본 ops §14. ↓이전:

> **갱신(2026-06-16, theme map 적대검증 라운드)**: 프롬프트 8 **실행** — draft 6건 refute-by-default 적대검증(8 렌즈) + 2차 source-check. 6건 전부 survives(3 clean / 3 copy_change), source quote 6/6 verbatim 정정·확인. counterpart_category 확정(acid_reducing_drug 신규). 2차 source-check 신규 draft 0(콜레세벨람·메틸도파 미유통·이소니아지드 B6=AE 치료 지시 → 전부 hold). validator 17 검사군·결함주입 9·smoke 6 카드 PASS. 정본 ledger `theme_map_adversarial_verify_v1_3.json`. live 통합·schedule·workflow·export/index/alias 수정 0. ↓이전:

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

## 프롬프트 8 — theme map expansion draft 6건 적대검증 + 후속 source-check (승격 아님) → **실행 완료(2026-06-16)**

> **✅ 실행됨(2026-06-16)**: refute-by-default 8 렌즈 적대검증 완료. **6건 전부 survives**(3 survives / 3 survives_with_copy_change), source quote **6/6 라벨 verbatim 대조**. 정정 = TM-LIP-01 quote verbatim·TM-CEPH-AC-02 counterpart PPI 확장·TM-CHEL-01-ZN mechanism 추론 플래그+confidence moderate. counterpart_category 확정(세팔로=acid_reducing_drug 신규·지용성비타민=fat_soluble_vitamin·페니실라민=null). 2차 source-check: 콜레세벨람·메틸도파 미유통→hold·이소니아지드 B6=이상반응 치료 지시→hold(신규 draft 0). validator 17 검사군+결함주입 9 PASS·smoke 6 카드. ledger `data/review/theme_map_adversarial_verify_v1_3.json`. **남은 일은 프롬프트 9 + clinical reviewer.** 아래 원문은 참고용 보존.
>
> **상태**: 프롬프트 7 의 draft-only 6건(`data/drafts/theme_map_draft_batch_v1_3.json`)이 source-confirmed·adversarial_verified 로 대기. live 통합은 PM + clinical reviewer 후 별도 PR.
>
> **작업(준비 단계 — live 통합 아님)**: ①6건 사용자 카피를 **적대검증**(서로 다른 렌즈): (a) orlistat·cholestyramine 카피가 **비타민 보충 권유**로 읽히지 않는가(라벨은 권장하나 우리는 시점 분리만), (b) cholestyramine 의 **비타민K 언급이 항응고 맥락**으로 오인되지 않는가, (c) 세팔로스포린 counterpart 가 **약물(제산제/H2)** 임이 분명한가(Mg 영양제 혼동 0), (d) 원문보다 강하지 않은가. ②counterpart_category 정렬 결정: 세팔로스포린 antacid 를 id61 `al_mg_antacid` 통합 vs 신규 `acid_reducing_drug`. ③nutrient_group("지용성 비타민") 단일 카드 vs 비타민별 분리. ④2차 source-check: TM-LIP-03(콜레세벨람)·TM-CHEL-03(메틸도파)·TM-B6-01(이소니아지드, **copy 게이트 선결**) — `scripts/sourcecheck_theme_map_expansion_v1_3.py` 에 후보 추가(SDK-only·≤2 fetch).
>
> **불변**: live relation 생성 0 · published/clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 UI 0 · 보충 권유/결핍 단정 0 · high-risk hold(페니토인/마이코페놀레이트/레보도파×B6)는 draft 격상 금지. **검증**: `scripts/validate_theme_map_expansion_v1_3.py` + `scripts/smoke_theme_map_draft_render_v1_3.py`.

## 프롬프트 9 — harvester theme map 편입 PR (후속 · PM 승인 전제) → **실행 완료(2026-06-16, branch+PR)**

> **✅ 실행됨(2026-06-16, harvester-theme-map-v1.3 브랜치)**: 신규 family 6건을 harvester 에 **candidate-only 로 편입**. 방식 = **manual flag `--include-theme-map-expansion`(기본 비활성)** + config-driven 격리 provider. live 통합·schedule 활성화·자동 integrate 0. main push/merge 0(브랜치+PR only).
> - **편입 흐름**: seed config(`data/config/theme_map_seeds_v1_3.json`, 읽기 전용) → provider(`scripts/theme_map_harvest_provider_v1_3.py`)가 draft batch/candidates/adversarial ledger 읽어 PM review queue 생성 → draft-only 6 + hold 7. 순서 **source-check queue → PM review → draft-only → live 금지** 준수.
> - **신규 category 처리**: acid_reducing_drug(세팔로 acid-reducer·id61 al_mg_antacid 와 구분) · fat_soluble_vitamin(지용성 비타민군). validator 가 약물/영양소 category 혼동·al_mg_antacid 축소·항응고 framing 차단.
> - **runtime 산출물**(`data/harvest_queue/theme_map_*`)은 `.gitignore` → **커밋 0**. 커밋되는 건 review summary(`data/review/theme_map_harvest_incorporation_v1_3.json`)뿐.
> - **검증**: `scripts/validate_harvester_theme_map_v1_3.py`(17 검사군+결함주입 9) · `scripts/smoke_harvester_theme_map_v1_3.py`(PM queue·6 카드) · guard `--run-bot --include-theme-map-expansion`(보호셋 sha256 불변·write-scope 한정·direct-http 0) 전부 PASS. 기본 run(무플래그)은 byte-동일·무변경.
> - **남은 일(PM/clinical reviewer 게이트)**: reviewer 가 ①acid_reducing_drug category 채택 ②TM-CHEL-01-ZN mechanism(absorption vs interaction) ③지용성비타민 group-split ④페니실라민 FE/ZN 묶음 확정 → **live 통합은 clinical reviewer note + 수동 단계 후 별도 PR**(provider/harvester 자동 승격 없음).
>
> 정본: `docs/MediStack_harvester_ops_v1_3.md` §14 · `docs/MediStack_theme_map_expansion_v1_3.md` §6 · `data/review/theme_map_harvest_incorporation_v1_3.json`. 아래 원문은 참고용 보존.

> **상태(원문, 보존)**: 신규 family(지용성비타민 흡수·세팔로스포린 antacid·페니실라민 킬레이트)는 현재 `vfs.SEARCH_INGREDIENTS`(25)/`ANTACID_CANDIDATES`(AT-ITZ만)에 **미편입**. 자동 run 대상 아님.
>
> **작업**: 신규 family seed 를 harvester theme map 에 편입할지 결정하는 **PR 설계**(편입 자체는 PM 승인 후). 편입 순서는 반드시 **source-check queue → PM review → draft-only → live 금지**. schedule 은 비활성 유지(프롬프트 6). runtime queue(`data/harvest_queue/`) 커밋 금지. 같은 theme map 반복 run 비효율(신규 0 수렴) 인지 — 신규 seed 만 가치.
>
> 근거: `docs/MediStack_theme_map_expansion_v1_3.md` §6 · `docs/MediStack_harvester_ops_v1_3.md` §13.

---

## 프롬프트 10 — theme map 6건 reviewer/category/grouping 결정 (승격 아님)

> **선행**: PR #3 merge 완료(theme map candidate-only 편입 live). reviewer 패키지·category 정책·grouping 전략 문서 ready.
>
> **작업(결정 단계 — live 통합 아님)**: clinical reviewer / PM 이 `docs/MediStack_reviewer_package_theme_map_v1_3.md` §3 후보별 카드를 검토하고 **4가지 결정**을 내려 reviewer note(§8 템플릿)를 작성하라. ①**acid_reducing_drug** category 채택(세팔로 acid-reducer, id61 al_mg_antacid 와 구분) vs 통합 — 근거 `docs/MediStack_counterpart_category_policy_v1_3.md` §3. ②**fat_soluble_vitamin** group 채택. ③**grouping**: 지용성 비타민 group 단일(권고) vs 비타민별 분리 · 페니실라민 FE/ZN 개별(권고) vs 묶음 — `docs/MediStack_theme_map_grouping_strategy_v1_3.md`. ④**TM-CHEL-01-ZN mechanism**: absorption(권고) vs interaction(user 카피 영향 없음). reviewer note 는 게이트(`integrate_theme_map_draft_batch_v1_3.check_reviewer_note`)가 강제하는 요건(승인 토큰·6건 전건·category 2종·grouping·mechanism·verified_reference·clinical_reviewed=true 아님·제품/보충 추천 아님)을 전건 충족해야 한다.
>
> **불변**: live relation 0 · published/clinical_reviewed=false · reviewed_by 공란 · 제품/보충 UI 0. **결정·노트 작성까지가 범위.**

근거: `docs/MediStack_reviewer_package_theme_map_v1_3.md` · `docs/MediStack_counterpart_category_policy_v1_3.md` · `docs/MediStack_theme_map_grouping_strategy_v1_3.md`.

---

## 프롬프트 11 — theme map 6건 live 통합 (reviewer note + 선행조건 전제)

> **선행 충족 필수(전부)**: ①프롬프트 10 reviewer note 확보(실물·게이트 통과). ②**v0.2 validator #15 확장**(별도 작업): `avoid_concomitant` 허용 counterpart_category 에 `acid_reducing_drug` 추가(TM-CEPH-AC-02) — 또는 reviewer 가 TM-CEPH-AC-02 를 separation 으로 하향. ③**src 선행**: `src/js/guards.js getFacets`(fat_soluble_vitamin facet 포함·drug category 제외) + `src/js/render.js`(acid_reducing_drug 전용 chip/kicker). ④별도 PM 승인.
>
> **작업**: theme map **6건**(또는 reviewer 가 승인한 subset)을 v0.2 export 에 멱등 append-only 통합하라 — `python3 scripts/integrate_theme_map_draft_batch_v1_3.py --pm-approved --reviewer-note <노트>`. id 는 runtime max+1(현재 60→66·id 62~67. AT-FEX/칼륨 먼저면 자동 조정). 각 행: display=draft `display_text_ko_draft`·management=`management_copy_draft`·product_link_allowed=false·potassium_safety_card=false·requires_clinical_review=false·counterpart_category(fat_soluble_vitamin 2·acid_reducing_drug 2·생략 2)·source={허가사항,url,pointer(itemSeq+quote+확인일)}. **full index/aliases 무변경.**
>
> **통합 후 검증(전수 PASS)**: relation-count 하드코딩 validator **+6 누적 갱신**(AT-FEX/칼륨 통합 순서 따라 baseline 조정) + 신규 `validate_theme_map_live_integration_v1_3.py`(드라이런 검증기를 live 대상 전환) + v0.2 export validator(python+node) + facet/chip node 렌더(신규 category) + forbidden 0 + full smoke + no-live-write guard + deploy 게이트 + **live HTTP 200** + git clean.
>
> **금지**: reviewer note 없이 통합 · hold 7건 동반 · clinical_reviewed=true · published=true · reviewed_by 작성 · 제품/제휴 UI · 보충 권유 · 비타민K 항응고 framing · acid_reducing_drug 를 al_mg_antacid 로 축소 · 제산제/H2/PPI 를 Mg 영양제로 표기 · src 선행조건 없이 통합(facet/chip 깨짐).

근거: `data/review/theme_map_live_dryrun_v1_3.json`(선행조건·예상치) · `scripts/integrate_theme_map_draft_batch_v1_3.py` · `scripts/validate_theme_map_live_dryrun_v1_3.py` · `docs/MediStack_reviewer_package_theme_map_v1_3.md` §7.

---

## 프롬프트 12 — theme map subset 통합 (예: 지용성 2건만 / 페니실라민 2건만 / 세팔로 2건만)

> **상태**: 현행 integrator 는 **6건 일괄**(reviewer note 도 6건 전건 요구). subset 통합은 별도 변형 필요.
>
> **작업(설계 단계)**: reviewer 가 일부만 우선 노출하려는 경우(예: 페니실라민 FE/ZN 2건만 — src 변경 불필요·일반 영양소라 가장 안전, 또는 지용성 2건만 — facet 선행만, 또는 세팔로 2건만 — chip+#15 선행), `integrate_theme_map_draft_batch_v1_3.py` 에 **`--only <candidate_id,...>` 필터**를 추가하고, reviewer-note 게이트의 candidate 요건을 subset 으로 좁히는 변형을 설계하라. **권고 우선순위**: ①페니실라민 FE/ZN(선행조건 0) → ②지용성 비타민(facet 선행) → ③세팔로 acid-reducer(chip+validator #15 선행). 각 subset 의 예상 count·선행조건을 dry-run 으로 별도 산출.
>
> **불변**: subset 도 reviewer note 전제 · live 0(설계까지) · 선행조건 미충족 category 는 통합 금지.

근거: `docs/MediStack_theme_map_grouping_strategy_v1_3.md` §4 · `data/review/theme_map_live_dryrun_v1_3.json`.

---

## 프롬프트 13 — category/grouping 정책 reviewer sign-off (문서 검토 · 승격 아님)

> **작업**: reviewer 가 `docs/MediStack_counterpart_category_policy_v1_3.md` 와 `docs/MediStack_theme_map_grouping_strategy_v1_3.md` 를 검토하고, ①category 카탈로그(nutrient_categories vs drug_categories 분기) ②al_mg_antacid vs acid_reducing_drug 분리 근거 ③§6 향후 src 검토사항(getFacets·render chip·validator #15)에 sign-off 하라. 이 sign-off 는 프롬프트 11 의 src/validator 선행조건 작업을 착수할 근거가 된다.
>
> **불변**: 문서 검토·sign-off 까지가 범위. src/validator/export 수정 0.

근거: `docs/MediStack_counterpart_category_policy_v1_3.md` · `docs/MediStack_theme_map_grouping_strategy_v1_3.md`.

---

## 프롬프트 14 — 페니실라민 FE/ZN 2건 reviewer decision (승격 아님)

> **선행**: subset reviewer 패키지·mechanism 결정 문서·dry-run(60→62·선행조건 0) ready.
>
> **작업(결정 단계)**: clinical reviewer / PM 이 `docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md` §3 두 카드 + §8 **결정 체크리스트**를 검토하고 reviewer note(§6 템플릿)를 작성하라. 결정: ①**승인 범위** = approve both(권고·60→62·id 62,63) / FE only(60→61·id 62) / ZN only(60→61·id 62·비권장) / reject(live 0) — §9 PM decision table(**단건 승인 시 id=max+1=62**, both 일 때만 FE=62·ZN=63). ②**TM-CHEL-01-ZN mechanism** = absorption(추론·Option A 권고) vs interaction(Option B — validator PR 선행) vs needs_review 보류(Option C) — mechanism doc §5 체크박스. ③FE/ZN **개별 카드** 확인. ④verified_reference 노출 동의. 게이트(`integrate_penicillamine_subset_v1_3.check_reviewer_note`)가 승인 토큰·FE/ZN 전건·ZN mechanism·grouping·verified_reference·clinical_reviewed=true 아님·제품 추천 아님·철분/아연 보충 권유 아님 을 강제(**현 통합기는 both-approval 전제**; 부분 승인이 실제 결정되면 `--only` 변형 PR 선행).
>
> **불변**: live relation 0 · published/clinical_reviewed=false · reviewed_by 공란 · 제품/보충 UI 0. 결정·노트 작성까지가 범위.

근거: `docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md` · `docs/MediStack_penicillamine_mechanism_decision_v1_3.md`.

---

## 프롬프트 15 — 페니실라민 FE/ZN 2건 live 통합 (reviewer note 전제 · 선행조건 0)

> **선행 충족 필수**: 프롬프트 14 reviewer note 확보(실물·게이트 통과). **별도 validator/src 선행조건 없음**(일반 영양소 — dry-run `live_integration_prerequisites: []` 실증). 별도 PM 승인.
>
> **작업**: 페니실라민 **2건**(TM-CHEL-01-FE·TM-CHEL-01-ZN)을 v0.2 export 에 멱등 append-only 통합 — `python3 scripts/integrate_penicillamine_subset_v1_3.py --pm-approved --reviewer-note <노트>`. id runtime max+1(현재 **60→62**·id 62~63. full-6/AT-FEX/칼륨 먼저면 자동 조정). 각 행: ingredient=페니실라민·nutrient=철분/아연·mechanism=absorption(ZN 추론)·action=separation·evidence=high·**counterpart_category 필드 생략(null)**·product_link/potassium/clinical=false·source={허가사항,url(itemSeq 198300142),pointer}. **full index/aliases/relation_card 1168·name_only 16412 무변경.**
>
> **통합 후 검증(전수 PASS)**: relation-count 하드코딩 validator **+2 갱신** + 신규 `validate_penicillamine_subset_integration_v1_3.py`(드라이런 검증기를 live 대상 전환) + v0.2 export validator(python+node·**선행조건 없이 PASS**) + 영양소 facet node 렌더(철분/아연 정상 노출·separation chip) + forbidden 0 + full smoke + no-live-write guard + deploy 게이트 + **live HTTP 200** + git clean.
>
> **rollback 준비**: merge 전=branch reset / merge 후=`git revert` → relation id 62/63 제거 시 `meta.relation_count` 동기화 + v0.2 validator 재검증(절차 = reviewer package §11). full index/aliases 무관.
>
> **subset 통합 후 full-6 중복 점검(필수)**: 통합 직후 full-6 dry-run(`integrate_theme_map_draft_batch_v1_3.py`)을 **naive 재실행하면 FE/ZN 이 이미 live → `이미 live 에 존재` violation → 전체 STOP**(중복 0, 2026-06-16 실증). 나머지 4건만 통합하려면 full-6 에 `--only`(잔여 4건) 변형이 **선행 필수**(프롬프트 16). subset 통합 전후로 full-6 통합기를 동시 실행하지 말 것.
>
> **금지**: reviewer note 없이 통합 · full-6 integrator 동시 사용(같은 후보 중복) · clinical_reviewed=true · published=true · reviewed_by 작성 · 제품/제휴 UI · 철분/아연 보충 권유 · ZN 을 interaction 으로 바꾸되 validator 미확장(enum FAIL) · `--only`(부분 승인)로 live 통합(미구현 STOP — both-approval 전제).

근거: `data/review/penicillamine_subset_live_dryrun_v1_3.json`(`meta.partial_approval_scenarios`) · `scripts/integrate_penicillamine_subset_v1_3.py` · `scripts/validate_penicillamine_subset_dryrun_v1_3.py` · `docs/MediStack_reviewer_package_penicillamine_subset_v1_3.md` §5·§7~§11.

---

## 프롬프트 16 — theme map full-6 선행조건 PR (페니실라민 외 4건 · live relation 0)

> **상태**: TM-LIP-01/02(fat_soluble_vitamin)·TM-CEPH-AC-01/02(acid_reducing_drug)는 live 통합 전 **validator/src 선행 PR** 필요(페니실라민 subset 은 불필요).
>
> **작업(선행 PR — live relation 0)**: ①`scripts/validate_medistack_v0_2_export.py` 검사 #15 의 `avoid_concomitant ⇒ counterpart_category==al_mg_antacid` 를 **acid_reducing_drug 포함**으로 확장(TM-CEPH-AC-02) + 결함주입 테스트. ②`src/js/guards.js getFacets`: `counterpart_category` 있는 relation 일괄 제외 → **nutrient_categories(fat_soluble_vitamin)은 facet 포함**, drug_categories 만 제외 분기 + node 렌더 테스트. ③`src/js/render.js`: **acid_reducing_drug 전용 chip/kicker**(제산제·H2/PPI 약물 표기). **이 PR 은 relation 추가 0**(validator/src 만). 검증: 기존 60 relation 회귀 0 + 신규 category 시뮬 렌더 PASS + deploy + live 200.
>
> **금지**: 이 PR 에서 theme map relation live 추가 · published/clinical=true · 제품 UI.
> → 이 PR 통과 후 프롬프트 11(full-6 live 통합·60→66 또는 subset 후 잔여)로 진행.

근거: `data/review/theme_map_live_dryrun_v1_3.json` `live_integration_prerequisites` · `docs/MediStack_reviewer_package_theme_map_v1_3.md` §7 · `docs/MediStack_counterpart_category_policy_v1_3.md` §6.

> **순서 권고**: 프롬프트 14·15(페니실라민 subset·선행조건 0) **먼저** → 프롬프트 13(category sign-off) → 프롬프트 16(선행 PR) → 프롬프트 11(나머지 4건 또는 full-6 잔여). 칼륨 4건(프롬프트 2)·AT-FEX(프롬프트 1)은 독립 트랙으로 병행 가능. **full-6 통합기와 subset 통합기는 동시 실행 금지**(같은 후보 중복 — subset 우선 시 full 은 잔여 4건만, 프롬프트 12 `--only`).

---

## Relation Factory v1.4 — 적대검증 후 다음 프롬프트 (2026-06-16 추가)

factory 43 draft → 적대검증(refute-by-default) → **reviewer-ready 37**(survives 31·copy_change 6) · 강등 6. live 0. 정본 `docs/MediStack_reviewer_package_relation_factory_v1_4.md`.

1. **factory reviewer-ready batch package** — reviewer-ready 37 을 family 그룹(F1/F2 우선)으로 clinical reviewer note 받기. 통합 0, note 수집만.
2. **factory high-yield 확장 batch 2** — F9 만성 depletion·F10 azole(최고 수확) + 미커버 약물 신규 seed. inventory dedup 선행 필수. live 0.
3. **factory reviewer-gated dry-run integrator** — reviewer note 확보분만 projected count/ids 산출(STOP guard). live write 0.
4. **selected subset live integration with reviewer note** — F1/F2 등 note 확보 subset 만 별도 PR(60→+N). dry-run 일치 확인 후.
5. **needs_review 5 재평가** — 알렌드론산(Al/Mg 직접 명시 라벨)·페노바르비탈/프리미돈(임신 외 엽산)·라모트리진·옥스카르바제핀 라벨 재검색.
6. **hold 1(포사코나졸)** — `acid_reducing_drug` category 설계 트랙(프롬프트 16과 합류 가능)에서 H2 차단제 relation 으로 재평가.
7. 기존 트랙 병행: 페니실라민(프롬프트 14·15)·theme map(16·11)·칼륨(2)·AT-FEX(1) — 전부 reviewer note 전제.

> **금지**: reviewer-ready/factory 후보 live 추가 · published/clinical=true · 제품/구매/제휴 UI · 강등분 승격 · 계열 일반화 draft.

---

## 프롬프트 17 — F1 퀴놀론 18건 reviewer decision (승격 아님)

> **전제**: clinical reviewer 가 `docs/MediStack_reviewer_package_f1_quinolone_v1_4.md` §5 decision table + §6 note 템플릿으로 판단. 통합 0.
>
> **작업**: F1 18건(reviewer package 카드)별로 reviewer 가 (a) 승인 범위(all18/nutrient10/antacid8/by-ingredient/일부 hold) (b) grouping (c) **al_mg_antacid category 채택**(id61 선례·Mg 영양제 아님) (d) separation 간격 노출 여부 (e) 발로플록사신 action 입도(separation vs avoid_concomitant) (f) 오플록사신 경구 scope 표기 (g) verified_reference 노출 동의 를 결정해 §6 노트로 회신. 신규 코드/데이터 0(reviewer 회신 수집만).
>
> **금지**: 통합·published/clinical=true·제품 UI·계열 일반화.

## 프롬프트 18 — F1 퀴놀론 live 통합 (reviewer note 실물 전제)

> **선행 충족 필수**: ①§6 reviewer note 실물(승인 토큰+scope 전건 candidate_id+al_mg_antacid+간격+grouping+verified_reference+clinical≠true+제품/복용권유 아님+reviewer 식별자) ②별도 PM 승인 ③별도 PR.
>
> **작업**: `python3 scripts/integrate_f1_quinolone_batch_v1_4.py --scope <all18|nutrient10|antacid8> --pm-approved --reviewer-note <노트>` (멱등: (ingredient,counterpart) 이미 있으면 skip). gate 가 scope 선언 ↔ 요청 scope 일치 + 전건 명시 강제. **예상**: all18 60→78(id 62~79) / nutrient10 60→70 / antacid8 60→68. nutrient=category 키 부재 · 제산제=al_mg_antacid·'약물' 표기 · product_link/potassium/clinical=false.
>
> **통합 후 검증(전수 PASS)**: relation-count 하드코딩 validator 갱신(60→target) + v0.2 export(16/16) + full index/aliases(무변경 확인) + forbidden 0 + full smoke 9종 + no-live-write guard 비대상 + deploy 게이트 + **live HTTP 200** + git clean. relation-count baseline 을 쓰는 다수 validator(factory_integration·coverage_queue 등) 동반 갱신 주의.
>
> **금지**: 강등/needs_review 후보 동시 통합 · evidence 임의 상향 · clinical_reviewed=true·published=true·reviewed_by 작성 · Mg 영양제 relation 으로 저장 · 제품 UI.

## 프롬프트 19 — F1 subset 통합 (top10 nutrient / top8 antacid / by-counterpart 2-wave)

> **전제**: 프롬프트 18 과 동일(reviewer note 실물). subset 만 별도 PR.
>
> **작업**: 권고 grouping = **by-counterpart 2-wave** — wave1 `--scope nutrient10`(60→70·live FQ×광물 동일 렌더·신규성 0), wave2 `--scope antacid8`(70→78·id61 렌더 경로). 또는 `--candidate-ids A,B,...` 로 임의 subset. 각 wave 는 자체 reviewer note(해당 scope 전건). dry-run(`data/review/f1_quinolone_live_dryrun_v1_4.json` scope_scenarios) 일치 확인 후 live.
>
> **금지**: 프롬프트 18 과 동일.

## 프롬프트 20 — F2 테트라사이클린 5건 reviewer package (승격 아님) → **실행 완료(2026-06-17)**

> **완료**: F2 5건(survives 5/5)을 F1 패턴으로 reviewer package + dry-run integrator + gate/validator/smoke + inventory 작성(통합 0). dedup 결과: live 독시/미노사이클린 ×칼슘/철분/마그네슘/아연 존재 → F2 antacid 는 별도 counterpart(al_mg_antacid·id61)·테트라사이클린 신규 성분 → **exact dup 0**. 산출물·재검증은 위 2026-06-17 갱신 참조. **남은 일 = 프롬프트 22(F2 reviewer decision)·23(F2 live 통합)·24(F1+F2 wave).**

## 프롬프트 20b — F2 테트라사이클린 5건 reviewer decision (승격 아님)

> **전제**: clinical reviewer 가 `docs/MediStack_reviewer_package_f2_tetracycline_v1_4.md` §5 decision table + §6 note 템플릿으로 판단. 통합 0.
>
> **작업**: F2 5건별로 reviewer 가 (a) 승인 범위(all5/nutrient2/antacid3/top2/top3/by-ingredient/일부 hold) (b) grouping (c) **al_mg_antacid category 채택**(id61 선례·Mg 영양제 아님) (d) **독시/미노 nutrient-overlap 판단**(기존 ×칼슘/철분/마그네슘/아연 대비 제산제 약물 relation 의 정보 가치 vs 중복 — F2 headline) (e) separation 간격 노출 (f) 약물별 itemSeq 매칭 확정(공통 라벨 문장) (g) verified_reference 노출 동의 를 결정해 §6 노트로 회신. 신규 코드/데이터 0.
>
> **금지**: 통합·published/clinical=true·제품 UI·계열 일반화·우유/유제품·소아/골/치아 문맥 일반화.

## 프롬프트 21 — F9 만성 depletion 확장 batch 2 (draft-only · 승격 아님)

> **작업**: F9 만성 depletion·F10 azole(최고 수확) + 미커버 약물 신규 seed 로 factory batch 2. inventory dedup 선행 필수. 적대검증(refute-by-default 10 렌즈) + source-check. live 0. F9 needs_review 5(임신 한정/동물/ADR 매몰) 라벨 재검색 동반.
>
> **금지**: 통합·schedule 활성화·harvester 자동 실행·계열 일반화.

## 프롬프트 22 — factory reviewer-ready 37 전체 dry-run integrator (승격 아님)

> **작업**: reviewer-ready 37(F1 18 + F2 5 포함) 전체를 단일 dry-run integrator 로 projected count/ids 산출 + family별 선행조건/충돌/dedup 매트릭스. **F1·F2 통합분 중복 생성 금지**(이미 live 면 (ingredient,counterpart/category-counterpart) 키로 skip). reviewer note 확보분만 STOP-guard 통과. live write 0.
>
> **금지**: 통합·published/clinical=true·제품 UI.

## 프롬프트 23 — F2 테트라사이클린 live 통합 (reviewer note 실물 전제)

> **선행 충족 필수**: ①§6 reviewer note 실물(승인 토큰+scope 전건 candidate_id+al_mg_antacid+**독시/미노 overlap 판단**+간격+grouping+verified_reference+clinical≠true+제품/복용권유 아님+reviewer 식별자+약물별 itemSeq 확정) ②별도 PM 승인 ③별도 PR.
>
> **작업**: `python3 scripts/integrate_f2_tetracycline_batch_v1_4.py --scope <all5|nutrient2|antacid3|top2|top3> --pm-approved --reviewer-note <노트>` (멱등: (ingredient,counterpart) 이미 있으면 skip). gate 가 scope 선언 ↔ 요청 scope 일치 + 전건 명시 + overlap 판단 강제. **예상**: all5 60→65(id 62~66) / nutrient2 60→62 / antacid3 60→63. **F1 먼저 live 면 78→83**(runtime max+1 자동 조정). nutrient(철분/아연)=category 키 부재 · 제산제=al_mg_antacid·'약물' 표기 · product_link/potassium/clinical=false.
>
> **통합 후 검증(전수 PASS)**: relation-count 하드코딩 validator 갱신(60→target) + v0.2 export(16/16) + full index/aliases(무변경 확인·테트라 latent flip 은 별도 alias 작업) + forbidden 0 + full smoke 9종 + no-live-write guard 비대상 + deploy 게이트 + **live HTTP 200** + git clean.
>
> **금지**: 강등 후보 동시 통합 · evidence 임의 상향 · clinical_reviewed=true·published=true·reviewed_by 작성 · Mg 영양제/우유·유제품 relation 오인 · 소아/골/치아 문맥 absorption 오인 · 제품 UI.

## 프롬프트 24 — F1+F2 antibiotic-mineral combined wave (reviewer note 전제)

> **전제**: F1·F2 reviewer note 실물(각 scope 전건). 별도 PR.
>
> **작업**: 항생제×금속/제산제 통합을 family 횡단 wave 로 묶음 — **nutrient wave** = F1 nutrient10 + F2 nutrient2 = 12건(전부 live 광물 렌더 동일), **antacid wave** = F1 antacid8 + F2 antacid3 = 11건(al_mg_antacid·id61). 두 integrator 를 순차 실행(`integrate_f1_quinolone_batch_v1_4.py` + `integrate_f2_tetracycline_batch_v1_4.py`, 각 scope+note). id 는 runtime max+1 누적. dry-run scope_scenarios(`antibiotic_mineral_wave_with_f1`)와 대조.
>
> **금지**: 프롬프트 18·23 과 동일. 두 family 의 reviewer note 를 교차/혼용 금지(각자 scope 전건).

## 프롬프트 25 — F3 비스포스포네이트 3건 reviewer package (draft-only · 승격 아님) → **실행 완료(2026-06-17)**

> **작업**: factory reviewer-ready F3 3건(비스포스포네이트 family)을 F1/F2 패턴으로 reviewer package + dry-run integrator + gate/validator/smoke + inventory 작성(통합 0). dedup: live 리세드론산/알렌드론산/이반드론산 ×광물 존재 여부 선검사 → 신규 성분/counterpart 만 projected.
>
> **결과**: family 재검증 **survives 1 · needs_review 2**(에티드론산 0148/0149 standalone parse 취약·계열 일반화 금지). 통합 가능 1(이반드론산×al_mg_antacid·60→61). 산출물 전부 생성·전수 검증 PASS. **금지 준수**: 통합·published/clinical=true·제품 UI·계열 일반화 0.

## 프롬프트 26 — F3 이반드론산(0147) live 통합 (reviewer note 실물 전제)

> **선행**: ①clinical reviewer note(`docs/MediStack_reviewer_package_f3_bisphosphonate_v1_4.md §7`) — **이반드론산 nutrient-overlap 판단**(기존 ×칼슘/철분/마그네슘 vs Al/Mg제산제 정보가치) 포함 · ②국내 품목(itemSeq 201207007) 매칭 확정.
>
> **작업**: `python3 scripts/integrate_f3_bisphosphonate_batch_v1_4.py --pm-approved --reviewer-note <노트> --scope survives` → relations 60→61(id runtime max+1·al_mg_antacid). relation-count 하드코딩 validator 60→61 갱신 + F3 integration validator + v0.2(16/16) + 전수 smoke/guard/deploy 게이트 + live 200 + git clean.
>
> **금지**: 에티드론산 0148/0149(needs_review) 동시 통합·계열 일반화·published/clinical=true·제품 UI.

## 프롬프트 27 — 글로벌 antibiotic/bisphosphonate-mineral wave (F1+F2+F3, reviewer note 전제)

> **작업**: reviewer note 확보 후 통합 가능 24건(F1 18·F2 5·F3 1)을 per-family integrator 로 순차/wave 통합. 계획 = `docs/MediStack_reviewer_ready_global_plan_v1_4.md`(조합 60→84·dedup 0·combined v0.2 PASS). 글로벌 도구는 planning 전용(live write 안 함) — 각 family integrator 의 reviewer-note 게이트로만 기록. nutrient wave(F1 10+F2 2=12) / antacid wave(F1 8+F2 3+F3 1=12) 분할 가능.
>
> **금지**: pending family(F4/F6/F9/F10) 동시 통합·글로벌 도구 직접 live write·계열 일반화.

## 프롬프트 28 — F4/F6/F9/F10 family 재검증 + per-family integrator (draft-only · 승격 아님)

> **작업**: pending 11건(F4 thyroid 1·F6 acid-reducer 1·F9 chronic-depletion 8·F10 azole 1)을 F1/F2/F3 패턴의 family-specific 재검증(refute-by-default) + per-family integrator/gate/validator/smoke 로 처리. F9 needs_review 4·F3 needs_review 2(에티드론산 parse) 재검색 병행. **family 재검증 전 통합 절대 금지**(품질 게이트).
>
> **금지**: 통합·published/clinical=true·제품 UI·계열 일반화·factory v1.5 신규 harvest(보류 권장).

> 기존 트랙 병행 유지: 페니실라민(14·15)·theme map(10~13·16·11)·칼륨(2)·AT-FEX(1)·F1(17~19)·F2(20b·23)·F3(26)·글로벌(27)·pending family(28) — 전부 reviewer note 전제.
