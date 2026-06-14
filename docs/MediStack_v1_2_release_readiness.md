# MediStack v1.2 — 릴리스 준비도(release readiness)

> 작성일: 2026-06-14. **현황 보고 문서 — 데이터/코드/렌더/DATA_URL 무변경.** 본 문서는 v1.2 마일스톤의 현재 상태를 한 곳에 집계하고, 공개 여부(go/no-go)를 명시한다.
> 선행(자기완결 인계): `MediStack_v1.2_plan.md` · `MediStack_relation_expansion_v1_2_live_integration.md`(draft 14건 통합 보고) · `MediStack_free_plus_plan_v1_2.md` · `MediStack_v1_2_relation_release_notes.md` · 법적 게이트 `MediStack_public_release_legal_safety_checklist.md`.
>
> **정체성(불변 전제):** MediStack 은 **식약처 허가사항 기반 약-영양소 참고정보 베타**다. 진단·처방·복약지시·영양제 추천·구매 동선이 아니다. published/clinical_reviewed = **false** 봉인 유지.

---

## 0. 한 줄 요약

v1.2 = **draft 14건 라이브 통합(relation 41→55) + combo A~E 정착 + 설계/기획 6종 문서화** 가 완료된 상태다. **베타 운영(내부 모드)은 OK.** **일반 공개는 NO-GO** — 규제 자문(STOP #1)·relation source confirmed 승격 절차(STOP #2)가 외부/별도 트랙 의존으로 미완이며 published/clinical_reviewed=false 봉인이 유지되기 때문이다.

---

## 1. 현재 기준선 (실측 · 2026-06-14)

아래 수치는 라이브 데이터 파일에서 실측 검증했다.

| 지표 | 값 | 검증 출처 |
|---|---|---|
| relations / `meta.relation_count` | **55** (ids 1–14, 16–56) | `data/medistack_v0.2_beta_export.json` |
| relation_card (full index) | **1,077** | `data/full_drug_name_index_sample_v1_0.json` `meta.counts` |
| name_only (full index) | **16,503** | 동상 |
| full drug name index total | **17,580** (불변) | 동상 (`target_total`=17,580 일치) |
| alias_count (meta) | **717** | `data/medistack_v0.3_aliases.json` `meta.alias_count` |
| verified_item_seqs | **1,064 entries / 22 canonical** | aliases `verified_item_seqs`(22 canonical) + relation 통합 보고 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) | `src/js/data.js` |
| published / clinical_reviewed | **false / false** (봉인) | export `meta` 실측 |
| live | `https://yoonspower.github.io/medistack` | GitHub Pages |

> 15행(에스오메프라졸×B12 id15)은 **미노출/봉인 유지** — relation id 시퀀스에서 15가 빠진 것은 정상(우회·재편입 금지).

---

## 2. v1.2 통합 관계 — draft 14건 승격 (relation 43–56)

이번 v1.2 라운드에서 PM 승인 하에 draft 14건(D01–D14, 전건 source_confirmed)을 라이브 relation **43–56** 으로 통합했다. 통합기 `scripts/integrate_relation_draft_v1_2.py`(idempotent), 선행 게이트 `MediStack_draft_relation_14_preflight_v1_2.md`(14건 전부 pass_to_integrate), 상세 보고 `MediStack_relation_expansion_v1_2_live_integration.md`.

| 그룹 | 관계 | live id | mechanism | evidence |
|---|---|---|---|---|
| FQ × 아연 (Q06) | 레보/시프로/오플록/목시플록사신 × 아연 | 43–46 | absorption/separation | high |
| 테트라 × 아연 (Q07) | 독시사이클린·미노사이클린 × 아연 | 47–48 | absorption/separation | high |
| 비스포 × 철·Mg enrichment (Q04) | 리세드론산·이반드론산 × 철분/마그네슘 | 49–52 | absorption/separation | high |
| 치아지드유사 × K (Q10·Q11) | 클로르탈리돈·인다파미드 × 칼륨 | 53·55 | depletion/monitoring | high · `card=true`/`link=false` |
| 치아지드유사 × Mg (Q10·Q11) | 클로르탈리돈·인다파미드 × 마그네슘 | 54·56 | depletion/monitoring | **moderate** (HCTZ×Mg id20 선례 일치·evidence 하향) |

- **full index flip = 5건**(클로르탈리돈 단일 2 + 인다파미드 단일 3). FQ·테트라·비스포 8성분은 이미 전건 relation_card → **enrichment only(flip 0)**. 복합제(클로르탈리돈·인다파미드)는 **name_only 유지**(v1.1 7성분 패턴 승계).
- **칼륨 행(53·55)**: `product_link_allowed=false` + `potassium_safety_card=true` + 임의 칼륨보충 위험 고지. standalone 칼륨보충제 차단 정책 무영향(8/8 유지).
- **정직 제외**: 알렌드론산(라벨 다가양이온 미기재)·오메프라졸(기존 relation 13/14 존재). needs_review 5 / reject 2 / hold 5 후보 혼입 0.
- **수치 변화**: relations 41→55(+14) · relation_card 1,072→1,077(+5) · name_only 16,508→16,503(−5) · total 17,580 불변 · verified 1,059/20→1,064/22 · alias 717 불변 · published/clinical false 불변.

---

## 3. combo(복합제) 처리 상태 (A/B/C/D/E)

복합제 배너·재분류 트랙의 현황. 전 트랙 **라이브 정착·회귀 방지 가드 유지**(상세 `MediStack_combo_*` 문서군).

| 트랙 | 내용 | 상태 |
|---|---|---|
| **A** | combo 배너 통합 (`combo_banner_a`) | 라이브 정착 — 회귀 PASS 유지 |
| **B** | combo 배너 통합 (`combo_banner_bd`) | 라이브 정착 — 회귀 PASS 유지 |
| **C** | PPI + 침강탄산칼슘 18건 → buffer_combo flip (기존 PPI relation 기준) | **완료/유지** — `combination_other_label="위산 중화 완충 성분(침강탄산칼슘)"`(영양 칼슘 오독 차단), PPI×칼슘 신규 relation 0(허가사항 0/22) |
| **D** | combo 배너 통합 (B와 동일 배치) | 라이브 정착 — 회귀 PASS 유지 |
| **E** | 라베프라졸 + 산화마그네슘 | **name_only 유지** — relation 미승격(회귀에서 name_only 유지 확인) |

- 불변 가드: 복합제는 **부분정보 고지 동반**. HCTZ 는 칼륨 반전 고지 / 버퍼콤보(C 포함)는 `combination_other_label` 을 **기능명**으로 표기(영양소 오독 차단). 칼륨보존이뇨제 복합제는 **영구 차단**.
- v1.2 draft 통합 후 회귀: A/B/C/D/E 전부 유지 확인(통합 보고 §4).

---

## 4. source / draft / factory 상태

- **source 확인(목표2)**: source queue Top10 **허가사항 재fetch 확인 완료** — source_confirmed **6**(Q06·Q07·Q02·Q04·Q10·Q11) / needs_review 5 / reject 2 / hold 5. 전건 근거(nedrug itemSeq·신호어·확인일) 기록(`MediStack_source_queue_top10_verification_v1_2.md` + CSV). reject(PPI×칼슘 0/22 등)·hold(고위험군) 박제.
- **draft(목표1)**: source_confirmed 6 중 신규/enrichment **14건 draft 화** → 이번 라운드 PM 승인으로 **전건 라이브 승격(relation 43–56)**. 승격 후 draft 큐의 미승격 잔여 = needs_review/reject/hold 후보(통합 금지 박제).
- **factory(다음 후보 생성)**: relation factory 다음 후보는 **draft/queue/문서까지만, 라이브 통합 금지**. 신규 후보는 source_status 기본값 = `needs_source / candidate_only / source_check_needed`(source_confirmed 자동 승격 금지), `do_not_implement_yet=true`. 고위험(와파린×K·항응고/항혈소판×K·항암제·임신/소아/정신건강)은 high_risk/hold 분류만.
- **허가사항 미기재 후보 박제**: 스타틴×CoQ10(최대 커버리지 레버)·H2×B12 등은 **missing 확정 → source-policy 결정 전 영구 보류**(임의 통합 금지).
- **검증(통합 시)**: CI 게이트 7 + 로컬 smoke/unit 11 전부 PASS(통합 보고 §4). 데이터 변경 시 **CI 전체 세트 로컬 선실행 필수**(세션 교훈).
- **factory 대량 source check 라운드(2026-06-14, 신규)**: 후보 75건 전건 스캔 → source-checkable 33건 nedrug 허가사항 fetch + **적대적 검증(독립 agent 라벨 재fetch·4렌즈)** → **source_confirmed 7 · reject 15 · needs_review 11 · hold 42.** confirmed 7건만 **draft batch DF01–DF07**(`relation_factory_draft_batch_v1_2.json`, `live_integration_forbidden=true`, **라이브 미반영**). 적대적 검증이 F-FQ-01(목시플록사신×칼슘)을 "흡수 정도 영향 없음"으로 **reject 강등**(regex 단독 한계 보정). 상세·다음 프롬프트 = `MediStack_relation_factory_source_check_v1_2.md`. 신규 게이트(금지어 스캐너·draft batch validator·factory draft smoke) 추가, 라이브 데이터 무변경(relations 55 불변).

---

## 5. Free / Plus 설계 상태

> 🎯 **우선순위 지시(2026-06-14):** **유료화/결제/구독/프리미엄·saved_stack 은 이번 단계 전면 보류.** 최우선 = **relation coverage 확장**(relation ≥1,000 · relation_card ≥10,000 · 검색 UX 안정화 전까지 유료화 구현 금지). 아래 Free/Plus·가격·기능 플래그는 **설계 동결 상태로 유지**하며 이번 라운드에 진척시키지 않는다. 작업 집중은 factory → source check → draft → live 승격 파이프라인(§4·§8).

설계 문서 = `MediStack_free_plus_plan_v1_2.md`(**설계 초안 전용 — 코드/UI/데이터/결제/스키마 변경 0**). 경계만 확정됐고, 기능 플래그·결제·계정은 별도 라운드.

- **Free 하드 약속(영구 무료·후퇴 금지)**: 약 검색(전체 인덱스) · `name_only` 품목명 확인 · 기본 `relation_card` 보기 · 면책/출처/복합제 배너 · 소수의 "내 목록 저장". → "내 약이 어떤 영양소 참고정보를 갖는지 확인"이라는 본질 가치는 결제 없이 완결.
- **Plus = 내 데이터 도구값**: 저장 무제한·가족 프로필·참고정보 모아보기(기존 카드 재집계)·약사/의사 질문 생성(답 X)·리포트/PDF·복용 메모·변경 이력·갱신 사실 알림. 전부 **§5 의학 경계 안**(답·진단·복용지시·위험 등급 0).
- **가격(후보·미확정)**: 저가 평생 구매 1상품 권장(4,900원 1순위 / 9,900원 대안). 월 구독 후순위 보류. 실제 금액·상품·결제는 별도 승인·심사 단계.
- **영구 배제(무료·유료 양쪽)**: 영양제 추천·구매 퍼널·제휴(쿠팡/iHerb/Amazon)·건강정보 판매·광고 수익. 제품/구매/제휴 수익은 **별도 영양제 앱 트랙으로만**(본체 영구 0).
- **상태**: 경계·기능 매트릭스·가격 후보 = 설계 완료. **기능 플래그·StoreKit/웹 결제·계정 = 미착수(별도 승인 라운드)**.

---

## 6. Supabase / 백엔드 상태

- **Supabase 미적용.** v1.2 는 정적 HTML/CSS/JS(ES module) + GitHub Pages, 빌드/백엔드 없음 유지.
- "내 약 목록 저장" MVP 설계(`MediStack_saved_stack_mvp_design_v1_2.md`)도 **localStorage 로컬 전용·무서버·무계정·민감정보 0**(약명/품목 식별자만). 서버·DB·동기화 없음.
- Supabase/계정/동기화 도입 시점은 **결제·다중 프로필·갱신 알림이 실제 필요해지는 별도 승인 라운드**로 분리(현 시점 의존성 0).

---

## 7. 공개 게이트 (go / no-go)

| 대상 | 판정 | 근거 |
|---|---|---|
| **베타 운영(내부 모드·현 라이브)** | **OK** | 면책/출처 모든 상세 노출, validator/smoke PASS, name_only 의학정보 미부착, 칼륨 정책 유지, 제품/구매/제휴 0 |
| **일반 공개(public release)** | **NO-GO (유지)** | 규제 자문(STOP #1) 미완 · relation source confirmed 승격 절차(STOP #2) 외부/별도 트랙 의존 · published/clinical_reviewed=false 봉인 |

**NO-GO 유지 조건(불변):**
- **published / clinical_reviewed = false** 봉인(천장 = verified_reference). "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 금지.
- **규제 자문(법률/약무) 미완** — 관할/준거법 확정 외부 의존, v1.2 에서 완결 불가.
- **공개 모드 source gate = fail-closed**(confirmed 아니면 무조건 name_only 강등 · 중간 라벨 노출 0 · relation 데이터 무손실) — 설계만 완료, **실배선·source_status 실부여는 v1.2 범위 밖**.
- 법적 문서 초안 3종(이용약관·면책 / 개인정보·피드백 / 게이트)은 **DRAFT(법률 검토 전)** 명시 — 합법 보장 아님.

> 본 문서·v1.2 설계는 **공개 허가·합법 보장이 아니다.** 일반 공개는 위 외부 의존 해소 전까지 NO-GO.

---

## 8. 다음 milestone (coverage 우선 · 유료화 보류)

**현재 최우선 = relation coverage 확장**(relation 55→≥1,000 · relation_card 1,077→≥10,000 · 검색 UX 안정화). 1–3 이 coverage 파이프라인, 4 는 정체성 게이트, 5–7 은 그 이후.

1. **factory draft batch DF01–DF07 live 승격(PM 승인 후)** — `relation_factory_draft_batch_v1_2.json` 7건(칼륨 5·T3 흡수 2). 멱등 통합기 + 신규 id 57~ + 칼륨 안전정책 승계 + flip·verified seqs. → `MediStack_relation_factory_source_check_v1_2.md` §8 프롬프트 1.
2. **차기 factory batch + source check 스케일업** — needs_review 11건 itemSeq 보강 + `harvest_relation_candidates.py` 신규 성분군 재생성 → `verify_factory_sources_v1_2.py` + 적대적 검증 반복. draft/queue/문서까지만, 라이브 통합 금지. → §8 프롬프트 2.
3. **source-policy 결정(PM/임상검토 트랙)** — 허가사항 미기재 hold(스타틴×CoQ10 5건 = 최대 커버리지 레버·H2×B12 3건)에 이차문헌 허용 여부. coverage 대폭 확장 vs "허가사항 기반" 정체성.
4. **공개 전 외부 트랙** — 규제 자문(STOP #1) + relation source confirmed 승격 절차(STOP #2) + clinical reviewer 확보. 이 3종 해소 전 일반 공개 NO-GO 불변.
5. **(보류) Saved-stack MVP 구현 검토** — 설계(`saved_stack_mvp_design_v1_2.md`)만 동결 유지. **coverage·UX 목표 달성 + 유료화 승인 전까지 착수 금지.**
6. **(보류) 기능 플래그 + 결제/계정 + Supabase** — Free 한도/Plus 해금·저가 평생 구매·StoreKit/웹 결제·동기화. **유료화 보류 지시로 본 단계 미착수**(설계 동결).
7. **영양제 앱 분리 실행 기획**(본체 제품/구매/제휴 영구 0, `supplement_app_separation_strategy.md` §5 경계계약 하).

> 재개 트리거: '메디스택 relation factory' 또는 '메디스택 v1.2 릴리스'.

---

## 9. 안전 준수 (본 문서)

- ✅ **현황 보고 문서 뿐** — 데이터/코드/렌더/DATA_URL/validator 변경 0. `docs/` 신규 1파일만.
- ✅ 수치 전건 라이브 파일 실측 검증(relations 55 · relation_card 1,077 · name_only 16,503 · total 17,580 · alias 717 · verified 1,064/22 · published/clinical false).
- ✅ published/clinical_reviewed=false 봉인·NO-GO 유지 명시. "식약처 승인/법적 문제없음/약사 검수 완료" 표현 0.
- ✅ 추천·구매·복용지시 어휘 0(드세요/복용하세요/피하세요/추천/구매/제품 미사용). 영양제 추천·구매 퍼널·제휴 영구 배제 재확인.
- ✅ factory 다음 후보 = draft/queue/문서까지만(라이브 통합 금지), 고위험군 hold 분류만.
