# MediStack — 칼륨 depletion/monitoring 6건 PM-ready 최종화 (v1.2)

> 작성일: 2026-06-14 · 상태: **PM-READY 분류 / HOLD (이번 라운드 live 승격 0)** · 대상 AI 세션 핸드오프용 자기완결 문서
> 본 문서는 칼륨 depletion/monitoring 트랙 draft 6건(DF01·DF04·DF05·DF02·CQF03·DF03)의 **PM 준비도 분류·통일 문구·승격 후보 플래그**를 PM 승인 단계로 넘기기 위해 자기완결적으로 정리한다.
> **이번 라운드 어떤 칼륨 행도 live 승격하지 않는다.** `published=false` · `clinical_reviewed=false` 유지. 제품/구매/제휴/추천 UI·문구 0.
>
> 데이터/게이트 판정은 앞단계에서 종료됨. 본 문서는 그 ledger를 **읽기전용 ground truth**로 인용만 한다(데이터/코드/렌더/DATA_URL/validator/smoke 한 줄도 변경하지 않는다).
>
> ground truth(읽기 전용):
> - `data/review/potassium_depletion_pm_ready_v1_2.json` (분류·통일문구·승격 후보 — 이미 결정됨)
> - `data/review/potassium_depletion_pm_ready_v1_2.csv`
> - `docs/MediStack_potassium_depletion_track_v1_2.md` (§1 통일문구·§2 표·§3 승격 프롬프트 초안)
> - `docs/MediStack_potassium_draft_hold_review_v1_2.md` (보류 사유·금지어휘)
>
> **정체성(불변):** MediStack 은 식약처 허가사항 기반 약-영양소 **참고정보 베타**. 진단·처방·복약지시·영양제 추천·구매 동선 아님.

---

## 0. 한 줄 요약

칼륨 depletion/monitoring 6건은 모두 `source_confirmed` high(적대검증 통과)로 **근거 부족 보류는 없다.** PM 준비도 기준으로 **PM-ready 3건(DF01·DF04·DF05) / needs_clinical_wording_review 2건(DF02·CQF03) / hold_continue 1건(DF03)** 로 분류한다. 통일 문구 템플릿(track doc §1)을 전건 적용하고, `potassium_safety_card=true`·`product_link_allowed=false`·published/clinical_reviewed=false 를 유지한다. 승격 후보(DF01·DF04·DF05)는 **플래그일 뿐 이번 라운드 승격 아님.** 칼륨 보충 권유 0·결핍 단정 0·제품 링크 0·구매 유도 0.

---

## 1. 6건 source_basis 재확인 표 (json verbatim 인용)

전건 `nutrient=칼륨` · `mechanism=depletion` · `recommended_action=monitoring` · `evidence_level=high` · `source_confirmed=true` · `adversarial_verified=true`.

| draft | 약물 | itemSeq | evidence_strength | risk_level(트랙) | source_pointer (허가사항 직접근거, json verbatim) |
|---|---|---|---|---|---|
| DF01 | 메틸프레드니솔론 | 199800324 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 메니솔론정4mg(메틸프레드니솔론), itemSeq 199800324 / 이상반응(체액ㆍ전해질) / '1) 체액ㆍ전해질 : 부종, 나트륨저류, 칼륨손실, 체액저류, 저칼륨성 알칼리혈증, 감수성 환자에 있어서 울혈성 심부전, 고혈압 등이 나타날 수 있다.' / 확인일 2026-06-14 |
| DF04 | 아세타졸아미드 | 201403403 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 아세타졸정(아세타졸아미드), itemSeq 201403403 / 이상반응(대사)·일반적 주의 / '2) 대사 : 때때로 저칼륨혈증, 저나트륨혈증을 포함한 대사성 산증 등의 전해질평형실조, 장기치료로 인한 골연화증, 고혈당/저혈당이 나타날 수 있다.' / 확인일 2026-06-14 |
| DF05 | 아조세미드 | 199001306 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 유레틴정(아조세미드), itemSeq 199001306 / 부작용(대사)·고령자 주의 / '3. 부작용 1) 대사 : 때때로 저칼륨혈증, 저나트륨혈증, 저염소혈증성 알칼리증 등의 전해질평형실조, 고뇨산혈증, BUN·혈청크레아티닌의 상승, 드물게 고혈당이 나타날 수 있으므로 충분히 관찰하고' / 확인일 2026-06-14 |
| DF02 | 덱사메타손 | 202203949 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 덱사하이정4밀리그램(덱사메타손), itemSeq 202203949 / 이상반응(체액ㆍ전해질) / '7) 체액ㆍ전해질 : 부종, 고혈압, 혈압상승, 저칼륨성 알칼리혈증, 나트륨저류, 체액저류, 종양용해증후군 등이 나타날 수 있다.' / 확인일 2026-06-14 |
| CQF03 | 히드로코르티손 | 200703172 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 래피손정(히드로코르티손), itemSeq 200703172 / 상호작용(병용 신중) / '④ 전해질이상 환자(전해질대사 장애작용에 의한 나트륨 저류, 부종, 칼륨배설증가에 의한 저칼륨혈증 등이 나타나는 경우가 있다); 7) 체액ㆍ전해질 : 부종, 혈압상승, 칼륨손실, 저칼륨성 알칼리혈증, 나트륨 저류 ... 등이 나타날 수 있다.' / 확인일 2026-06-14 |
| DF03 | 플루드로코르티손 | 199907231 | high | 칼륨 양방향(고/저) 민감 | 식약처 허가사항(nedrug) / 플로리네프정(미분화플루드로코르티손아세테이트), itemSeq 199907231 / 이상반응(체액과 전해질 장애) / '1) 체액과 전해질 장애 : 나트륨ㆍ체액 저류, 울혈성 심부전, 칼륨소실, 저칼륨성 알칼리혈증, 고혈압, 부종, 심확대' / 확인일 2026-06-14 |

> 6건 모두 허가사항 이상반응/부작용/상호작용란에 저칼륨혈증·칼륨손실 동거어가 **이상반응·부작용 문맥**으로 직접 listing됨(첨가제/조성 아님). 적대적 검증 verdict = 전건 confirm. 인용은 ground truth json의 source_pointer 원문이며 새로 작문하지 않았다.

---

## 2. PM 준비도 분류 표 (json classification_reason verbatim)

근거(evidence)는 6건 모두 충족(source_confirmed high). 아래 분류는 **승격 준비도**이며 근거 부족 보류는 없다.

| 분류 | draft | 약물 | classification_reason (json verbatim) |
|---|---|---|---|
| **PM-ready** | DF01 | 메틸프레드니솔론 | 라벨 직접근거 명확(칼륨손실+저칼륨성 알칼리혈증). 글루코코르티코이드 대표. 통일문구 적용 시 승격 후보. |
| **PM-ready** | DF04 | 아세타졸아미드 | 탄산탈수효소억제 이뇨·저칼륨혈증 직접 listing·국내 유통(아세타졸정). 승격 후보. |
| **PM-ready** | DF05 | 아조세미드 | 루프이뇨제(유레틴정)·저칼륨혈증 직접·국내 유통 명확. 승격 후보. |
| **needs_clinical_wording_review** | DF02 | 덱사메타손 | 미네랄코르티코이드 작용 약함·라벨은 '저칼륨성 알칼리혈증'만(칼륨손실 직접어 없음) → wording 강도 임상 검수 권장. |
| **needs_clinical_wording_review** | CQF03 | 히드로코르티손 | 외용 비중 큰 성분·전신 제형(래피손정) 한정 wording 필요 → 임상 검수 권장. |
| **hold_continue** | DF03 | 플루드로코르티손 | 강한 MC이나 국내 유통 적음(플로리네프정 1품목) — 품목 가용성 재확인 후 검토. 보류 지속. |

분포(json meta): PM-ready 3 / needs_clinical_wording_review 2 / hold_continue 1. 합계 6.

---

## 3. 장기·고용량 맥락 표시 (long_term_high_dose_context)

전건 `long_term_high_dose_context=true` — **장기·고용량 맥락이 필요한 부작용**이다. 스테로이드(DF01·DF02·CQF03·DF03)의 칼륨 영향은 전신·장기·고용량 사용 맥락의 부작용이고, 이뇨제(DF04·DF05)는 전해질 소실 기전이라 용량·기간에 따라 임상적 의미가 달라진다. 통일 문구의 "장기간 복용하거나 고용량으로 사용하는 경우" 조건절은 이 맥락을 충실히 반영한다.

| draft | 약물 | long_term_high_dose_context |
|---|---|---|
| DF01 | 메틸프레드니솔론 | true |
| DF04 | 아세타졸아미드 | true |
| DF05 | 아조세미드 | true |
| DF02 | 덱사메타손 | true |
| CQF03 | 히드로코르티손 | true |
| DF03 | 플루드로코르티손 | true |

---

## 4. 최종 display / management 문구 (통일 템플릿 — json verbatim)

전건 동일 통일 템플릿을 사용한다(track doc §1 통일 문구 승계). 아래는 ground truth json의 `final_display_text_ko` · `final_management_ko` verbatim이며, 새 카피를 발명하지 않았다.

### display (상태 영향 고지) — `final_display_text_ko`
```
이 약을 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.
```

### 약물명 삽입 변형 — `final_display_text_ko_named` (렌더 시 주어 명시가 필요한 경우, 트랙 내 일관 유지)
```
{약물명}을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.
```
(예: 메틸프레드니솔론을(를) … / 아세타졸아미드을(를) … / 아조세미드을(를) … / 덱사메타손을(를) … / 히드로코르티손을(를) … / 플루드로코르티손을(를) …)

### management (관리 안내) — `final_management_ko`
```
칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요.
```

### 플래그(전건 유지 명시)
- `potassium_safety_card = true` — 칼륨 고지는 이 플래그 기준 렌더(nutrient 문자열 매칭 금지).
- `product_link_allowed = false` — 제품 링크·구매·제휴 0.
- `published = false` · `clinical_reviewed = false` · `reviewed_by` 공란 유지.
- 통일 템플릿 외 문구를 추가하지 않는다(새 칼륨 카피 발명 금지). management는 칼륨 보충 권유 0·결핍 단정 0을 충족한다.

---

## 5. 승격 후보 표시 (플래그일 뿐 — 이번 라운드 승격 아님)

`promotion_candidate=true` 는 **명백히 안전·PM-ready** 인 행에만 부여된 플래그이며, **이번 라운드 승격을 의미하지 않는다.**

| draft | 약물 | promotion_candidate | 의미 |
|---|---|---|---|
| DF01 | 메틸프레드니솔론 | true | **승격 후보(플래그일 뿐 — 이번 라운드 승격 아님)** |
| DF04 | 아세타졸아미드 | true | **승격 후보(플래그일 뿐 — 이번 라운드 승격 아님)** |
| DF05 | 아조세미드 | true | **승격 후보(플래그일 뿐 — 이번 라운드 승격 아님)** |
| DF02 | 덱사메타손 | false | 승격 후보 아님(통일 문구 강도 임상 검수 후 재평가) |
| CQF03 | 히드로코르티손 | false | 승격 후보 아님(전신 제형 한정 wording 임상 검수 후 재평가) |
| DF03 | 플루드로코르티손 | false | 승격 후보 아님(국내 단일 품목 가용성 재확인 후 재평가, 보류 지속) |

---

## 6. 이번 라운드 정책 재확인 (불변)

- **이번 라운드 live 승격 0.** 전건 `live_integration_forbidden=true`. 승격은 PM 승인 + clinical reviewer 노트 확보 후 별도 단계에서만.
- `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란 유지.
- 칼륨 보충 권유 0 · 부족·결핍 단정 0 · 제품 링크 0 · 구매 유도 0 · 제휴/추천 UI 0.
- `potassium_safety_card=true` · `product_link_allowed=false` 전건 유지.
- DATA_URL v0.2 불변. 데이터/코드/렌더/validator/smoke 무변경.

---

## 7. PM 승인 시 live 승격 프롬프트 초안 (track doc §3 승계)

> ⚠️ **초안일 뿐 실행 지시가 아니다.** 아래는 track doc §3 초안을 승계한 것이며, PM 승인 + clinical reviewer 노트 확보 후에만 사용한다. 본 문서는 승격을 실행하지 않는다.

**전제(미충족 시 STOP):**
- (a) clinical reviewer 노트 확보(칼륨 행은 reviewer 트랙 천장 = verified_reference).
- (a) 통일 문구 템플릿(§4 / track doc §1) 적용 — display/management를 통일 템플릿으로 정규화.
- potassium_safety_card=true · product_link_allowed=false · published=false · clinical_reviewed=false · reviewed_by 공란 유지.

**(b) 승격 순서 (근거·유통 명확도 + PM 준비도 순):**
```
DF01 메틸프레드니솔론 → DF04 아세타졸아미드 → DF05 아조세미드 → DF02 덱사메타손 → CQF03 히드로코르티손 → DF03 플루드로코르티손(유통 재확인 후)
```

**(c) 금지선 (명시):**
- published/clinical 전환 금지 · reviewed_by 기재 금지.
- 칼륨 제품 링크 금지 · 칼륨 보충 권유 금지 · 결핍 단정 금지 · 구매/제휴/추천 금지.
- 통일 템플릿 외 문구 추가 금지(새 칼륨 카피 발명 금지).
- 원문에 없으면 노출 금지 · 원문보다 강하면 금지.

**승격 시 수행(초안 — 실행 지시 아님):**
1. 멱등 통합기(CQF01/DF06·DF07 ids 57/58 패턴 승계, 칼륨 가드 분기): 각 draft를 export relations에 연속 id append. draft-전용 필드 strip, source {type,url,pointer(+확인일)} 정합. absorption 가드(potassium 차단)를 **칼륨 허용 + depletion 전용 가드**(mechanism=depletion·nutrient=칼륨·potassium_safety_card=true·product_link_allowed=false·adversarial_verified=true·source_confirmed=true·itemSeq 보유)로 교체. display/management는 §4 통일 템플릿으로 기록(현행 draft 문구 정규화).
2. full index: 각 약물 단일성분 name_only → relation_card flip(복합·변형 성분명은 보수적 name_only 유지). counts·verified_item_seqs 갱신.
3. 신규 칼륨 통합 validator + potassium_name_only_policy + forbidden phrase scanner(`scripts/validate_forbidden_phrases_v1_2.py`) + 회귀 전수.
4. 회귀 baseline(relations·relation_card·name_only·verified) 갱신, CQF_IDS/DF 승격분 반영.
5. live HTTP 200 / deploy success / git clean / commit. validator·smoke 전수 PASS 아니면 commit 금지.

---

## 8. 승격 전 PM / 임상 체크리스트

PM 승인 + (가능 시) clinical reviewer 트랙에서 아래를 통과해야 승격한다. 하나라도 미충족이면 **보류 유지.**

- [ ] **clinical reviewer 노트 확보** (칼륨 천장 = verified_reference 해제 근거).
- [ ] **§4 통일 문구로 display/management 정규화** (현행 draft 문구 → 통일 템플릿 교체). 통일 템플릿 외 문구 추가 0.
- [ ] **wording 강도 임상 검수** — DF02 덱사메타손(라벨 '저칼륨성 알칼리혈증'만, 칼륨손실 직접어 없음) · CQF03 히드로코르티손(외용 비중 큰 성분, 전신 제형 한정 wording) 채택안 확정.
- [ ] **DF03 플루드로코르티손 국내 단일 경구 품목(플로리네프정) 가용성 재확인** — 미충족 시 hold_continue 유지.
- [ ] **칼륨 안전정책 승계 확인** — `potassium_safety_card=true`·`product_link_allowed=false` 전건 · management 통일 문구 적용.
- [ ] **적대적 검증 재확인** — 6건 verdict confirm 유지 여부, 인용이 이상반응·부작용·상호작용 문맥(첨가제/조성 아님)인지 재확인. 라벨 변경 가능성 있으면 itemSeq 재fetch.
- [ ] **금지어 게이트** — 채택 문구를 `scripts/validate_forbidden_phrases_v1_2.py` 로 스캔(복용하세요/반드시 드세요/치료/예방/진단/식약처 승인/법적 문제 없음/약사 검수 완료/추천 영양제/구매/제휴/칼륨 보충 권유/결핍 단정 등) — 위반 0 확인.
- [ ] **published/clinical false 유지** 및 라이브 데이터 무변경(승격은 별도 통합 단계).
- [ ] **회귀 전수 PASS · DATA_URL v0.2 불변.**

---

> **안전 원칙(불변):** 칼륨 보충 권유 금지 / 부족·결핍 단정 금지 / 장기·고용량 맥락만 한정 표기 / PM 승인 전 live 승격 금지 / published·clinical_reviewed=false 유지 / `potassium_safety_card=true`·`product_link_allowed=false` 승계 / 통일 템플릿 외 문구 추가 금지 / 원문에 없으면 노출 금지·원문보다 강하면 금지 / 제품·구매·제휴·추천 UI·문구 0.
