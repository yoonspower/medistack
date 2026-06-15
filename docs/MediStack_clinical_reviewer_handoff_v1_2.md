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
3. PM 라운드: `approved` 행만 whitelist 로 `--pm-approved --reviewer-note` 통합(AT-FEX 는 `integrate_antacid_fex_v1_2.py`, 칼륨은 `integrate_potassium_pm_ready_v1_2.py`). **칼륨 스크립트의 reviewer-note 게이트는 의미적**이다 — 노트가 승인 토큰('approved'|'승인')과 **승격 대상 draft_id 를 전건 명시**해야 통과(garbage/공백/일부 누락 노트 거부). AT-FEX 통합 시에도 동일한 노트 인터록을 적용할 것(현 `integrate_antacid_fex_v1_2.py` 는 `--pm-approved` 만 — 통합 직전 같은 패턴 보강 권장).
4. relation-count 하드코딩 validator 갱신(통합 건수만큼) + 전수 PASS + deploy 게이트 + live 200.
5. `revise`/`reject` 는 별도 버전 게이트에서 문구 반영(검수자 직접 데이터 수정 금지).

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / 칼륨 보충 권유·결핍 단정 금지 / clinical 검수 전 published 금지 / 검수자는 판정·로그만(데이터 직접 수정 금지) / 승격은 per-row·제한적(일괄 금지).
