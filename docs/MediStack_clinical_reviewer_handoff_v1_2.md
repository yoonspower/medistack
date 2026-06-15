# MediStack — Clinical Reviewer Handoff (v1.2 준비분, 2026-06-15)

작성일: 2026-06-15 · 상태: **핸드오프 / 검수 대기 · 실행 금지(승격 0)** · 자기완결

> 이 문서는 현재 **live 통합 준비(드라이런)까지 끝났으나 clinical reviewer 노트가 없어 승격하지 않은** 후보들을
> 면허 검수자(약사/의사)에게 넘기기 위한 핸드오프다. relation-level **검수 스키마·플로우·`review` 블록 설계**는
> 기존 `docs/MediStack_v1.0_clinical_reviewer_checklist.md`(§3 review 스키마·§4 clinical_reviewed 기준·§7 1건당 체크리스트)에
> 정의돼 있으며 **여기서 중복하지 않는다**. 이 문서는 그 위에 **이번에 검수 대기 중인 구체 후보**와 **검수자 질문**을 얹는다.
>
> **이 라운드에서 코드·데이터·export·validator·DATA_URL·tag 를 승격 방향으로 바꾸지 않는다.** 산출물은 문서/드라이런뿐.

---

## 0. 봉인 스냅샷 (2026-06-15 라이브 실측)

| 위치 | 값 | 의미 |
|---|---|---|
| `meta.published` | `false` | 공개 승격 0 |
| `meta.clinical_reviewed` | `false` | 검수 완료 0 |
| `meta.relation_count` | `60` | 라이브 relation(AT-ITZ id61 포함, 1-based id max 61) |
| 전 relation `reviewed_by` | 부재/공란 | 검수 서명 0 |
| `lifecycle` 천장 | `verified_reference` | clinical 승격 전 한계(CLAUDE.md §1/§6) |
| 제품/구매/제휴 UI | 없음 | 영구 금지 |

검수자 미확보 동안 위가 **영구 기본값**이다(검수자 부재 ≠ 결함 — 앱은 참고정보 베타로 안전 동작). 아래 후보는 전부
이 천장 아래에서 **드라이런으로만** 통합 가능성을 입증해 둔 상태다(실제 export 무변경).

---

## 1. 검수 대기 후보 — 두 트랙

### 1-A. antacid_interaction 트랙 — AT-FEX (1건)

| 항목 | 값 |
|---|---|
| 관계 | 펙소페나딘 × Al/Mg 함유 제산제(약물) |
| directive | `avoid_concomitant`(라벨 '병용금지') — 라이브 enum 에 **처음** 등장 |
| 근거 | 식약처 허가사항(nedrug), 대표 itemSeq 분기(202202380 병용금지 / 199801016 상의) |
| evidence_level | `moderate` (**PM 판단지점**: confidence=low 이나 허가사항 출처 → low 아님, itemSeq 분기 → high 아님) |
| 적대검증 | round4 survives(`adversarial_verified=true` 후보) |
| 준비물 | `scripts/integrate_antacid_fex_v1_2.py`(dry-run) + `scripts/validate_antacid_fex_dryrun_v1_2.py`(PASS) |
| 통합 시 | relations 60→61(id 62), 전용 chip '병용금지(허가사항)', product_link=false, full index/aliases 무변경 |

상세: `docs/MediStack_antacid_interaction_track_v1_2.md` §17(적대검증)·§19(통합 준비·드라이런).

### 1-B. potassium depletion 트랙 — 7건 (PM-ready 4 / wording-review 2 / hold 1)

원천: `data/review/potassium_depletion_pm_ready_v1_2.json`(2026-06-15 독립 적대 재검토 완료, 6/6 survives) +
`data/review/prednisolone_potassium_draft_recheck_v1_3.json`(DF-PRED-01, 2026-06-15 needs_review 재확인 발견).
전건 `nutrient=칼륨`·`potassium_safety_card=true`·`product_link_allowed=false`·published/clinical=false·reviewed_by 공란·`live_integration_forbidden=true`.

| draft | 약물 | itemSeq | 분류 | 검수자에게 |
|---|---|---|---|---|
| **DF01** | 메틸프레드니솔론 | 199800324 | **PM-ready** | 라벨 직접근거(칼륨손실+저칼륨성 알칼리혈증) 명확 |
| **DF04** | 아세타졸아미드 | 201403403 | **PM-ready** | 이상반응(대사) 저칼륨혈증 직접 listing. ⚠️동일 라벨에 금기('저칼륨혈증 환자 투여금지') 공존 — 추출 포인터를 '이상반응(대사)' 섹션으로 한정(금기→depletion 오독 방지) |
| **DF05** | 아조세미드 | 199001306 | **PM-ready** | 루프이뇨제, 부작용(대사) 저칼륨혈증 직접 |
| **DF-PRED-01** | 프레드니솔론 | 199602982 | **PM-ready** | 글루코코르티코이드(소론도정). 라벨 직접근거(칼륨손실+저칼륨성 알칼리혈증, DF01과 동일 패턴). ⚠️seeded `ingrName1` 검색이 메틸프레드니솔론 substring 에 지배돼 1차 누락 → search-depth 개선(deep_max_pages fallback) 후 자동 포착. 계열 유추가 아니라 품목 라벨 직접 hit |
| DF02 | 덱사메타손 | 202203949 | wording-review | 5건 중 유일하게 직접 칼륨손실 동사 부재('저칼륨성 알칼리혈증' 결과어만) → 추론적 약신호. 문구 강도 검수 |
| CQF03 | 히드로코르티손 | 200703172 | wording-review | **correctness 선결**(아래 §3) |
| DF03 | 플루드로코르티손 | 199907231 | hold | 강한 MC이나 국내 유통 적음(플로리네프정 1품목) — 품목 가용성 재확인 후 |

이번에 **live 통합 준비(드라이런)를 끝낸 대상은 PM-ready 4건(DF01·DF04·DF05·DF-PRED-01)**이다:
`scripts/integrate_potassium_pm_ready_v1_2.py`(dry-run, whitelist {DF01,DF04,DF05,DF-PRED-01}) + `scripts/validate_potassium_dryrun_v1_2.py`(PASS·시뮬 60→64).
통합 시 relations → +4(id 62~65 또는 AT-FEX 통합 순서에 따라 조정), 칼륨 안전카드 노출, 제품 0. **reviewer 노트는 승인 토큰 + DF01/DF04/DF05/DF-PRED-01 전건 명시 필요**(미명시 시 STOP — 검증됨).

---

## 2. 검수자에게 묻는 질문 (verdict: approved / revise / reject + notes)

각 후보 1건마다 기존 v1.0 §7 체크리스트를 적용하고, 추가로 트랙별 아래를 확인한다.

**공통(전 후보):**
1. `source.url` 식약처 원문 접근 가능 + `source.pointer` 섹션/itemSeq/확인일 정확한가?
2. `display_text_ko` 가 원문 **이하** 강도이고 단정·복용지시·위험확정이 없는가?
3. `management_ko` 가 지시형 단정이 아니라 '상담' 종결인가?

**AT-FEX(병용금지) 전용:**
4. `avoid_concomitant`(병용금지) directive 를 앱이 **'병용금지(허가사항)'** chip + 비지시 카피로 옮기는 것이 적정한가, 아니면 더 낮은 강도(separation)로 내려야 하는가?
5. `evidence_level=moderate` 가 타당한가(대표 itemSeq 분기 고려)? 상향/하향 의견.
6. 라이브에 avoid_concomitant 가 처음 들어오는 것에 대한 안전 우려가 있는가?

**potassium(칼륨 depletion) 전용:**
7. 통일 display 문구 "**장기간 복용하거나 고용량**으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의" — 각 약물 라벨 근거에 비추어 **과하지도 약하지도** 않은가?
8. 통일 management "칼륨은 **임의로 보충하지 말고**, 보충 여부는 의사 또는 약사와 상담해 결정" — anti-supplement 방향이 적정한가? (DF01·CQF03 라벨 원문에는 '칼륨보충이 필요할 수 있다'는 보충 시사 문장이 있으나 앱은 의도적으로 anti-supplement 로 다운그레이드함 — 이 다운그레이드를 승인하는가?)
9. **DF02(덱사메타손)**: '저칼륨성 알칼리혈증'만 있는 약신호로 depletion 카드를 띄우는 것이 정당한가, 아니면 reject/문구 약화인가?
10. **DF-PRED-01(프레드니솔론, 소론도정 199602982)**: 라벨 근거(칼륨손실+저칼륨성 알칼리혈증)는 DF01 메틸프레드니솔론과 동일 패턴이다. 글루코코르티코이드 class 4종(프레드니솔론·메틸프레드니솔론·덱사메타손·플루드로코르티손)을 한 묶음으로 승격/검수하는 게 적정한가, 아니면 프레드니솔론을 DF01 수준 PM-ready 로 단독 인정하는가? (계열 유추가 아니라 각 품목 라벨 직접 hit 임을 전제.)
10. **wording-review 2건(DF02·CQF03)은 보류 사유가 서로 다르다**(DF02=약신호 / CQF03=제형+섹션). 한 묶음으로 판정하지 말 것.

---

## 3. ⚠️ 승격 전 선결(correctness) — reviewer 판단 필요

데이터 재검토(`meta.rereview_2026_06_15`)에서 식별한, **단순 wording 이 아닌** 정확성 항목:

- **CQF03(히드로코르티손) — 제형 일반화 위험**: 외용 제형 비중이 큰 성분에 전신(경구 래피손정) depletion 경고를 일반화하면 외용 사용자 오적용(false attribution). 승격 시 **전신 제형 한정** 필수. 또한 source_pointer 섹션 표기 '상호작용(병용 신중)'은 부정확 — 실제 인용은 **신중투여(④ 전해질이상 환자) + 이상반응(7 체액ㆍ전해질)**. 정정 후 검수.
- **공유 템플릿 단일 실패점**: 6건 `management_ko` 가 byte-동일. anti-supplement 안전마진 전체가 한 문자열에 의존. 승격 검증기는 통일 문자열 **정확 일치**를 assert(현 `integrate_potassium_pm_ready_v1_2.py` 가 가드).
- **DF06/DF07 동반승격 방지**: 칼륨 후보와 같은 factory 파일에 비-칼륨 리오티로닌×칼슘/철분(product_link_allowed=TRUE)이 동거. 승격은 **파일이 아니라 draft_id whitelist {DF01,DF04,DF05}** 로만(스크립트가 강제).

---

## 4. 검수자 노트가 와도 — 자동 승격하지 않는다 (정책)

- reviewer 노트(`verdict=approved`)는 **승격의 필요조건일 뿐 충분조건이 아니다.** 노트가 와도 `clinical_reviewed=true`·`published=true` 로 **즉시 전환하지 않는다.**
- 우선 **`verified_reference` 천장을 유지**한 채, reviewer 노트를 받아 **per-row(행 단위)·제한적**으로만 승격을 검토한다(일괄 승격 금지). `meta.clinical_reviewed=true` 는 전 relation 검수 완료 시에만 후보(집계 결과, 임의 설정 금지 — v1.0 §4/§5).
- 실제 승격은 별도 PM 라운드에서 `--pm-approved --reviewer-note <파일>` + 전수 validator/smoke/deploy + live 200 으로만. **앱이 하지 않는 것**(불변): 진단 · 처방 · 복용 지시 · 칼륨 보충 권유 · 결핍 단정 · 제품 추천/구매/제휴.

---

## 5. 검수 산출물 → 승격 경로 (요약)

1. 검수자 자격·익명화 ID 기록 → `review` 블록(v1.0 §3) **별도 버전 파일**에 append-only.
2. 후보 1건당 verdict + `source_rechecked` + notes(특히 §3 correctness 항목).
3. PM 라운드: `approved` 행만 whitelist 로 `--pm-approved --reviewer-note <노트>` 통합(AT-FEX 는 `integrate_antacid_fex_v1_2.py`, 칼륨은 `integrate_potassium_pm_ready_v1_2.py`). **두 스크립트 모두 의미적 reviewer-note 인터록**(`check_reviewer_note`)을 갖춘다(2026-06-15 보강): **칼륨** = 승인 토큰('approved'|'승인') + 승격 대상 draft_id 4건(DF01·DF04·DF05·DF-PRED-01) 전건 명시. **AT-FEX** = 승인 토큰 + candidate_id(AT-FEX-01/AT-01) + primary itemSeq 202202380 + evidence_level 'moderate' 명시. **공통** = 빈/garbage/일부 누락 노트 + **SAMPLE 토큰 + 미기입 placeholder 거부**(§9). 복붙 템플릿은 §8, SAMPLE 주의는 §9, 회귀 보증은 `scripts/test_reviewer_note_gate_v1_3.py`.
4. relation-count 하드코딩 validator 갱신(통합 건수만큼) + 전수 PASS + deploy 게이트 + live 200.
5. `revise`/`reject` 는 별도 버전 게이트에서 문구 반영(검수자 직접 데이터 수정 금지).

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / 칼륨 보충 권유·결핍 단정 금지 / clinical 검수 전 published 금지 / 검수자는 판정·로그만(데이터 직접 수정 금지) / 승격은 per-row·제한적(일괄 금지).

---

## 6. 칼륨 PM-ready 4건 — 검수자용 상세 카드 (행 단위 핸드오프)

> 4건 공통: `nutrient=칼륨(영양소)` · `mechanism=depletion` · `recommended_action=monitoring` · `evidence_level=high` ·
> `potassium_safety_card=true` · `product_link_allowed=false` · `requires_clinical_review`는 큐 전용(live 매핑 안 함) ·
> `published=false`·`clinical_reviewed=false`·`reviewed_by` 공란. 사용자 표시 문구는 **약물명을 앞에 둔 통일 카피**,
> 관리 문구는 **anti-supplement 통일 문자열**(byte-동일). 드라이런 시뮬 id 62~65(통합 순서 따라 런타임 max+1 재계산).
>
> 공통 근거(전 행 동일): **왜 칼륨 depletion/monitoring인가** = 각 품목 허가사항에 칼륨 고갈 방향의 직접 동거어
> (`칼륨손실`/`칼륨소실`/`저칼륨혈증`/`저칼륨성 알칼리혈증`)가 있고, 앱은 보충이 아니라 **상태 확인(monitoring)** 만 권한다.
> **왜 제품 링크 금지** = 칼륨 트랙 영구 규칙(CLAUDE.md §1) — 칼륨 노출이 보충제 구매 유도로 오인될 위험을 원천 차단.
> **왜 potassium_safety_card=true** = 칼륨 관련 카드는 '임의 보충 말고 상담' 안전 고지를 항상 동반해야 함(렌더 게이트).

### 6-1. DF01 — 메틸프레드니솔론 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분명 | DF01 / 메틸프레드니솔론 |
| 관계 | 메틸프레드니솔론 × 칼륨(영양소) · depletion · monitoring · evidence=high |
| itemSeq / 대표 품목 | 199800324 / **메니솔론정4mg**(국내 경구 단일성분 완제) |
| source section | 이상반응(체액ㆍ전해질) |
| source quote 요약 | "체액ㆍ전해질 : 부종, 나트륨저류, **칼륨손실**, 체액저류, **저칼륨성 알칼리혈증** …" — 기전어(칼륨손실)+결과어 동거 |
| 사용자 표시 문구 | "메틸프레드니솔론을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | "칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요." |
| reviewer 질문 | 글루코코르티코이드 class 대표. 라벨 직접근거 가장 명확 — 표시 강도 적정? (계열 유추 아님, 품목 라벨 직접 hit) |

### 6-2. DF04 — 아세타졸아미드 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분명 | DF04 / 아세타졸아미드 |
| 관계 | 아세타졸아미드 × 칼륨(영양소) · depletion · monitoring · evidence=high |
| itemSeq / 대표 품목 | 201403403 / **아세타졸정**(탄산탈수효소억제 이뇨, 국내 유통) |
| source section | 이상반응(대사)·일반적 주의 |
| source quote 요약 | "2) 대사 : 때때로 **저칼륨혈증**, 저나트륨혈증을 포함한 대사성 산증 등의 전해질평형실조 …" |
| 사용자 표시 문구 | "아세타졸아미드을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| reviewer 질문 | ⚠️ **동일 라벨에 금기('저칼륨혈증 환자 투여금지')도 공존** — 추출 포인터를 **이상반응(대사) 섹션**으로 한정했다(금기→depletion 오독 방지). 이 한정이 적절한가? 신호어가 기전어 아닌 결과어(저칼륨혈증)임을 표시에 반영해야 하나? |

### 6-3. DF05 — 아조세미드 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분명 | DF05 / 아조세미드 |
| 관계 | 아조세미드 × 칼륨(영양소) · depletion · monitoring · evidence=high |
| itemSeq / 대표 품목 | 199001306 / **유레틴정**(루프이뇨제, 국내 유통) |
| source section | 부작용(대사)·고령자 주의 |
| source quote 요약 | "3. 부작용 1) 대사 : 때때로 **저칼륨혈증**, 저나트륨혈증, 저염소혈증성 알칼리증 등의 전해질평형실조 …" |
| 사용자 표시 문구 | "아조세미드을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| reviewer 질문 | 루프이뇨제 — 칼륨 손실은 약리학적으로 잘 알려짐. 표시 강도가 과하지 않은가(상담 라우팅 수준)? |

### 6-4. DF-PRED-01 — 프레드니솔론 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분명 | DF-PRED-01 (candidate D-CORT-01) / 프레드니솔론 |
| 관계 | 프레드니솔론 × 칼륨(영양소) · depletion · monitoring · evidence=high |
| itemSeq / 대표 품목 | 199602982 / **소론도정**(국내 경구 단일성분 완제) |
| source section | 사용상의 주의사항 > 이상반응 > 체액ㆍ전해질 |
| source quote 요약 | "체액ㆍ전해질 : 부종, 체액저류, 나트륨저류, **칼륨손실**, … 혈압상승, **저칼륨성 알칼리혈증** 등이 나타날 수 있다." |
| 사용자 표시 문구 | "프레드니솔론을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| reviewer 질문 | ⚠️ seeded `ingrName1` 검색이 **메틸프레드니솔론 substring 에 지배돼 1차 누락** → search-depth 개선(deep fallback) 후 자동 포착. DF01과 동일 라벨 패턴이나 **계열 유추가 아니라 소론도정 품목 라벨 직접 hit**. 프레드니솔론을 DF01 수준 단독 PM-ready 로 인정하는가, 아니면 글루코코르티코이드 class 일괄 검수를 원하는가? |

### 6-5. 검수자 질문 (칼륨 4건 — verdict: approved / revise / reject + notes)

1. 이 근거(허가사항 직접 동거어)가 **사용자 참고정보 수준**으로 표시 가능한가?
2. **장기/고용량 조건절**("장기간 복용하거나 고용량으로 사용하는 경우")이 충분히 보수적인가(과확대 아님)?
3. **칼륨 보충 권유 없이** '상담 시 확인 문의' 프레이밍으로 충분한가(anti-supplement 다운그레이드 승인)?
4. 특정 **제형/외용/주사/복합제 오적용** 위험은 없는가(4건 모두 국내 경구 단일성분 완제를 대표로 선정)?
5. 이 항목을 **`verified_reference` 수준**으로 live 에 둘 수 있는가(published/clinical_reviewed=false 천장 유지 하)?

---

## 7. AT-FEX — 검수자용 상세 카드

| 필드 | 값 |
|---|---|
| candidate / draft | AT-FEX-01 / AT-01 |
| 관계 | 펙소페나딘 × **Al/Mg 함유 제산제(약물)** — 영양소(Mg 보충제) relation 아님 |
| directive / action | `avoid_concomitant`(병용금지) — 라이브 enum 에 **처음** 등장 |
| confidence / evidence_level | confidence **low** / evidence_level **moderate** (⚠️ PM 판단지점) |
| primary itemSeq / 근거 | **202202380** — avoid_concomitant 강한 directive("…제산제를 복용하지 마십시오") |
| online provenance itemSeq | **199801016** — coadmin_caution 약한 directive("…의사 또는 약사와 상의하십시오"). **둘 다 유효한 다른 대표품목**(기존 itemSeq 오류 아님) — 보수적으로 강한 쪽을 primary, 약한 쪽은 provenance 보존(폐기 0) |
| counterpart_category | `al_mg_antacid`(비-영양소 마커 — getFacets 영양소 facet 에서 제외) |
| product_link_allowed | false |
| 사용자 표시 문구 | "일부 알루미늄·마그네슘 함유 제산제와 함께 복용하지 않도록 안내하는 허가사항 문구가 있습니다. 이미 복용 중인 제산제가 있다면 약사 또는 의사에게 확인하세요." |
| 앱 표면 | 전용 chip **'병용금지(허가사항)'** + kicker 'Al/Mg 함유 제산제 관련 참고정보'. generic '복용 간격'/'상태 모니터링' 미사용(병용금지와 모순 제거). 앱은 직접 "복용하지 마세요" 명령 안 함(비지시·출처 귀속) |
| 적대검증 | round4 독립 회의론자 8인 survives(`adversarial_verified=true` 후보, fidelity 3/3 + 비지시·Mg오인·generic chip 모순제거·제품·source 구분) |

### 7-1. 검수자 질문 (AT-FEX — verdict: approved / revise / reject + notes)

1. **primary itemSeq 202202380**(avoid_concomitant)을 대표 근거로 써도 되는가(더 약한 199801016 대신)?
2. **199801016의 약한 문구**와 **202202380의 강한 문구**를 provenance 로 **함께 보존**하는 정책이 적절한가?
3. **'병용금지(허가사항)' chip** 이 앱의 직접 지시가 아니라 **출처 귀속**으로 충분히 이해되는가?
4. user-facing copy 가 prohibition(병용금지)을 **과소표현하지 않는가**(약사 확인 라우팅으로 강도 보존)?
5. **confidence low / evidence moderate** 로 `verified_reference` 수준 live 노출이 가능한가?

---

## 8. reviewer note 템플릿 (복붙용)

> 통합 스크립트(`integrate_potassium_pm_ready_v1_2.py` / `integrate_antacid_fex_v1_2.py`)의 `--reviewer-note` 게이트는
> **의미적 인터록**이다(`check_reviewer_note`). 아래 템플릿을 **그대로 제출하면 거부**된다 — 아래 §9 참조. 실제 검수 시:
> ① `APPROVED-SAMPLE-NOT-VALID` 를 실제 승인 토큰(`approved` 또는 `승인`)으로 교체, ② `____`·`YYYY-MM-DD` 빈칸을 실제 값으로 채움.

### 8-1. 칼륨 4건 reviewer note 템플릿

```text
[MediStack 칼륨 depletion PM-ready — clinical reviewer 승인 노트]

검수자 식별자(익명 ID): ____________
검토일(YYYY-MM-DD): ____________
승인 토큰: APPROVED-SAMPLE-NOT-VALID      ← 실제 승인 시 "approved" 또는 "승인" 으로 교체(SAMPLE 표기 제거)

승인 대상 draft_id (4건 전건 명시 — 누락 시 통합 거부):
  - DF01  메틸프레드니솔론 × 칼륨 (itemSeq 199800324, 소론도정 계열 글루코코르티코이드)
  - DF04  아세타졸아미드 × 칼륨 (itemSeq 201403403, 아세타졸정)
  - DF05  아조세미드 × 칼륨 (itemSeq 199001306, 유레틴정)
  - DF-PRED-01  프레드니솔론 × 칼륨 (itemSeq 199602982, 소론도정)

각 행 verdict (approved / revise / reject):
  - DF01: ____________
  - DF04: ____________
  - DF05: ____________
  - DF-PRED-01: ____________

명시 확인(체크):
  [ ] 이 승인은 clinical_reviewed=true 전환이 아니다(verified_reference 천장 유지).
  [ ] 제품 추천/구매 유도가 아니다(product_link_allowed=false 유지).
  [ ] 칼륨 보충 권유가 아니다(anti-supplement '임의 보충 말고 상담' 유지).
  [ ] 사용자 참고정보 수준 표시로 한정한다.

검수자 서명/비고: ____________
```

### 8-2. AT-FEX reviewer note 템플릿

```text
[MediStack AT-FEX(펙소페나딘 × Al/Mg 제산제, avoid_concomitant) — clinical reviewer 승인 노트]

검수자 식별자(익명 ID): ____________
검토일(YYYY-MM-DD): ____________
승인 토큰: APPROVED-SAMPLE-NOT-VALID      ← 실제 승인 시 "approved" 또는 "승인" 으로 교체(SAMPLE 표기 제거)

승인 대상(전부 명시 — 누락 시 통합 거부):
  - candidate_id: AT-FEX-01 (draft AT-01)
  - primary itemSeq: 202202380 (avoid_concomitant 강한 directive)
  - evidence_level: moderate (confidence low + 대표 itemSeq 분기 반영)

verdict (approved / revise / reject): ____________

명시 확인(체크):
  [ ] 이 승인은 clinical_reviewed=true 전환이 아니다(verified_reference 천장 유지).
  [ ] 제품 추천/구매 유도가 아니다(product_link_allowed=false 유지).
  [ ] Mg 영양제 relation 으로 저장하지 않는다(counterpart_category=al_mg_antacid).
  [ ] '병용금지(허가사항)' 표시는 앱 직접 지시가 아니라 출처 귀속이다.
  [ ] 사용자 참고정보 수준 표시로 한정한다.

검수자 서명/비고: ____________
```

---

## 9. ⚠️ SAMPLE 토큰 주의 — 통합 스크립트는 SAMPLE 을 승인으로 오인하지 않는다

- §8 템플릿의 예시 승인 토큰 `APPROVED-SAMPLE-NOT-VALID` 는 **승격용이 아니다(SAMPLE)**. `approved` 문자열을 포함하지만,
  통합 스크립트의 `check_reviewer_note` 가 **SAMPLE 마커**(`SAMPLE`/`샘플`/`NOT-VALID`/`NOT A REAL APPROVAL`/
  `NOT_FOR_PROMOTION`/`TEMPLATE-ONLY`/`PLACEHOLDER`)를 **승인 토큰보다 우선 검사**해 STOP 시킨다.
- 또한 **미기입 placeholder**(`____`·`YYYY-MM-DD`·`<검수자`·`<reviewer`·`<날짜`·`<date`)가 남아 있으면 STOP — 검수자 식별자/검토일 빈칸을 채워야 한다.
- 즉 §8 템플릿을 **그대로 제출하면 통합되지 않는다.** 실제 승격은 (1) SAMPLE 토큰을 실제 승인 토큰으로 교체, (2) 빈칸을 채우고,
  (3) 칼륨은 draft_id 4건 전건, AT-FEX 는 candidate_id+itemSeq 202202380+evidence moderate 를 명시해야 통과한다.
- 회귀 보증: `scripts/test_reviewer_note_gate_v1_3.py` — invalid(빈/토큰없음/일부 누락/SAMPLE/placeholder) **거부** + valid **통과** + valid 노트의
  `--pm-approved` 전체 write 는 **temp 복사본에서만** 동작하고 **live export sha256 불변**임을 검증(네트워크 0).
