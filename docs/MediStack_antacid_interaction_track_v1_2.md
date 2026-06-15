# MediStack — antacid interaction 별도 트랙 설계 v1.2 (CQ-103 펙소페나딘×Mg)

작성일: 2026-06-14 · 상태: **DESIGN / HOLD (live·draft 승격 없음)** · 대상 AI 세션 핸드오프용 자기완결 문서

## 0. 결론 한 줄
CQ-103(펙소페나딘×마그네슘)은 **일반 absorption/separation 트랙으로 승격하지 않는다.** 라벨은 "Al/Mg 함유 제산제를 복용하지 마십시오"라는 **병용금지(avoid concomitant use)**이며, 상대는 **제산제(약물 카테고리)**이지 마그네슘 영양소 보충제가 아니다. 이 두 사실 때문에 별도 `antacid_interaction` 트랙 설계가 필요하다.

## 1. 왜 일반 separation으로 못 가는가 (적대검증 2/3 split 분석)

- 후보: CQ-103 펙소페나딘 × 마그네슘, mechanism=absorption, action=separation, source_status=source_confirmed(itemSeq 202202380, 노즈알연질캡슐 단일성분 경구).
- 적대검증 결과: confirm 2 / refute 1 → **만장일치 미달 → needs_review(보류)**. live·draft 미반영.
- 라벨 직접 문구(허가사항): "2. 이 약을 복용하는 동안 다음의 약을 복용하지 말 것 … 3) 제산제(수산화알루미늄·수산화마그네슘 함유제제)" / e약은요: "알루미늄 또는 마그네슘 함유 제제의 제산제를 복용하지 마십시오."

**refute한 evidence-literal 렌즈의 두 실패점(설계가 반드시 해소해야 할 것):**

| 실패 렌즈 | 내용 | 함의 |
|---|---|---|
| direction_correct=false | 라벨은 "복용하지 말 것"(절대적 병용금지). 흡수저해·"시간 간격 두기(separation)"를 명시·권장하지 않음. | separation(간격 두면 OK) 카피는 라벨 강도를 **약화**하고 방향을 재해석함 |
| copy_reads_as_reference=false | 제안 카피 "같은 시간대 복용 시 흡수에 영향… 시간 간격을 두는 것이 도움"은 '병용 자체 금지'를 '간격으로 관리 가능한 흡수 이슈'로 **다운그레이드** | 원문보다 약하면서 방향이 어긋남 |

confirm한 2개 렌즈도 동일 사실(동거어 실재·계열일반화 아님·국내 단일제·부정표현 부재)은 인정했다. 즉 **상호작용 자체는 실재**하나, **separation 프레이밍이 원문 충실성을 깬다**는 것이 핵심 쟁점이다.

## 2. 추가 쟁점 — "영양소(nutrient)" 모델과의 불일치

MediStack 핵심 모델은 **약물 × 영양소(철/칼슘/Mg/아연/칼륨) 보충제** 상호작용이다. 그러나 펙소페나딘 라벨이 지목하는 상대는 **Al/Mg 함유 제산제(OTC 위장약, 약물 카테고리)**이다.

- 마그네슘 **영양제** 복용 ≠ Al/Mg **제산제** 복용. 같은 다가양이온이라 개연은 있으나, **라벨은 제산제만 명시**한다.
- 따라서 CQ-103을 "펙소페나딘 × 마그네슘(영양소)" relation으로 박으면, 사용자에게 "마그네슘 영양제와의 문제"로 오인될 수 있다(라벨이 말하지 않은 범위로 확대).
- ⇒ antacid 트랙은 **영양소 트랙과 개념적으로 분리**되어야 한다. 상대는 "Al/Mg 함유 제산제"라는 약물 카테고리다.

## 3. relation type 후보 검토

| 후보 | 의미 | 라벨 충실성 | 표면 톤(비지시성) | 평가 |
|---|---|---|---|---|
| `antacid_avoid_concomitant` | 제산제와 동시복용 회피 | 높음(병용금지 직역) | 중(‘회피’가 약한 지시로 읽힐 수 있음) | 내부 강도 표현엔 정확 |
| `label_avoid_combination` | 라벨상 병용회피(일반) | 중(제산제 특정성 손실) | 중 | 너무 일반적 — 비제산제 병용까지 포괄 위험 |
| `antacid_interaction` | 제산제 상호작용 존재(중립) | 중(강도는 별도 필드로 보존) | **높음(존재 고지+상담 유도)** | **권장: 표면 트랙명** |

**권장 설계(레이어 분리):**
- **표면 relation_type = `antacid_interaction`** — 사용자 노출은 중립·참고정보 톤("상호작용 문구가 있습니다 + 상담").
- **내부 필드 `label_directive = "avoid_concomitant"`** + **`label_quote`** — 라벨의 강한 원문("복용하지 말 것")을 손실 없이 보존(충실성).
- **내부 필드 `counterpart_category = "antacid_al_mg"`** — 상대가 영양소 보충제가 아니라 Al/Mg 제산제임을 명시(영양소 트랙과 분리).
- product_link_allowed=false(제산제 제품 연결 금지), potassium_safety_card=false.

이 레이어 분리가 2/3 split의 두 실패점(방향·다운그레이드)을 동시에 해소한다: 표면은 비지시 중립 톤, 내부는 원문 강도 보존.

## 4. 안전 문구 설계 (제안)

### display (권장)
```
일부 알루미늄·마그네슘 함유 제산제와 함께 사용할 때 약물 흡수에 영향을 줄 수 있다는
허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.
```

### 설계 근거 / 금지선
- **"허가사항 문구가 있습니다"**(출처 귀속): 앱이 지시("복용하지 마세요")하지 않고 **라벨에 그런 문구가 있다는 사실만 전달** → 비지시성 확보(copy_reads_as_reference 회복).
- **"함께 사용할 때 … 영향"**(병용 프레이밍 유지): "시간 간격 두면 됨"으로 약화하지 않음 → 라벨 강도 보존(direction 회복). separation 톤 회피.
- **"함께 사용하는 경우에는 … 확인하세요"**: 분리복용 권장 대신 **상담 트리거**로 종결(전문가 판단에 위임).
- 상대를 "제산제"로 명시(영양소 보충제로 오인 차단). 마그네슘 **보충제** 일반화 금지.
- 금지: 복용하지 마세요(직접지시) / 시간 간격을 두세요(약화) / 추천·구매·제휴 / 제산제 제품 링크 / 마그네슘 영양제로의 확대 해석.

### (대안) 더 강한 원문 보존이 필요할 경우
PM/임상 검토가 "병용금지"의 강도를 더 보존하길 원하면:
```
허가사항에 일부 알루미늄·마그네슘 함유 제산제와 함께 복용하지 않도록 안내하는 문구가 있습니다.
함께 사용하고 있다면 약사 또는 의사에게 확인하세요.
```
("함께 복용하지 않도록 안내하는 문구가 있다" = 라벨 사실 귀속 형태로 강도 보존, 여전히 앱 자신의 지시는 아님.)

## 5. CQ-103 재검토 체크리스트

- [ ] **트랙 분리 결정**: antacid_interaction을 영양소 relation과 별도 surface로 구현할지, CQ-103을 surface 설계 전까지 hold할지 PM 결정.
- [ ] **relation_type 확정**: 표면 `antacid_interaction` + 내부 `label_directive=avoid_concomitant` + `counterpart_category=antacid_al_mg` 레이어 채택 여부.
- [ ] **문구 확정**: §4 display(또는 강한 대안) 중 택1 → forbidden phrase scanner 0 확인.
- [ ] **충실성 재검증**: 적대검증 재실행 시 evidence-literal 렌즈의 direction_correct·copy_reads_as_reference 가 신규 카피로 통과하는지(병용 프레이밍 유지·비지시성).
- [ ] **영양소 오인 차단**: 카피·메타에 "마그네슘 영양제"로 읽히는 표현 없음(상대=제산제 명시).
- [ ] **동류 후보 일괄 적용성**: 동일 패턴(Al/Mg 제산제 병용금지 라벨) 약물 — 예: 아지트로마이신, 일부 퀴놀론/세팔로스포린(위산의존 흡수), 비스포스포네이트 — 이 트랙으로 모일 수 있으므로 tracke 정의를 재사용 가능하게.
- [ ] **scope 한계 명시**: 이 트랙은 "약물 × Al/Mg 제산제" 이며 영양소 결핍/보충과 무관(보충 권유 0).
- [ ] live·draft 승격 금지 유지(본 작업 범위).

## 6. 상태
- CQ-103: **needs_review / HOLD**. live·draft 미반영. 본 문서는 설계안일 뿐 구현 지시가 아니다.
- 실제 트랙 구현·CQ-103 승격은 PM 결정 + (필요 시) clinical reviewer 검토 후 별도 단계.

---

> 아래 §7 이후는 v1.2 라운드 후보 수집·게이트 실행 결과를 반영한 **보강 섹션**이다. §0–6 설계 본문의 의미는 변경하지 않는다. 모든 판정은 앞단계 ledger(`data/review/source_confirm_gate_v1_2.json`)를 **읽기전용 ground truth**로 인용한 것이며, 본 문서가 새로 판정하지 않는다.

## 7. 후보 수집·게이트 결과 (v1.2 라운드)

이번 라운드에서 antacid_interaction 트랙으로 6개 후보(AT-01~AT-06)를 수집해 단일 fail-closed 게이트(`scripts/source_confirm_gate_v1_2.py` / `data/review/source_confirm_gate_v1_2.json`)에 통과시켰다. 게이트 판정 분포: **antacid_draft_confirmed 2 / reject 3 / needs_review 1**. 이번 라운드 **live 승격 0**, confirm 되어도 **draft(`live_integration_forbidden=true`)까지만**.

판정 원천: `data/review/source_confirm_gate_v1_2.json` 의 `antacid_track` 배열. 원문 quote 원천: `data/candidates/antacid_interaction_evidence_v1_2.json` 의 `evidence` 배열. 후보 행 요약은 `data/candidates/antacid_interaction_candidates_v1_2.csv`.

| id | ingredient | verdict | label_directive_type | itemSeq | 판정 이유 | 라벨 원문 quote(발췌) |
|---|---|---|---|---|---|---|
| AT-01 | 펙소페나딘 | **antacid_draft_confirmed** | avoid_concomitant | 202202380 | Al/Mg 제산제 directive 동거어+directive 문맥+부정문구 부재+단일 경구 itemSeq → antacid draft 후보(영양소 relation 아님, live 금지). | "…알루미늄 또는 마그네슘 함유 제제의 **제산제를 복용하지 마십시오.** 이 약을 복용하는 동안 케토코나졸이나 에리트로마이신과 함께 복용하지…" |
| AT-02 | 아지트로마이신 | reject | coadmin_caution | 200708447 | DENY: 제산제 동거어는 있으나 동일 문맥에 '흡수장애 일어나지 않음/영향 없음' 등 부정문구 → 상호작용 성립 불명확(과다해석 방지). | "…6. 상호작용 1) 제산제: 이 약과 제산제를 동시에 투여하는 경우…약동학 시험에서, **전반적인 생체이용율에는 영향을 미치지 않았으나** 최고 혈청 농도는 약 24%정도 감소하였다…" |
| AT-03 | 클래리트로마이신 | reject | (없음) | 201211101 / 201211108 | DENY: 라벨에 Al/Mg 제산제 병용 directive 동거어 미확인. | (해당 directive 동거어 미확인 — quote 없음) |
| AT-04 | 플루코나졸 | reject | coadmin_caution | 200202853 | DENY: 제산제 동거어는 있으나 동일 문맥에 '흡수장애 일어나지 않음/영향 없음' 등 부정문구 → 상호작용 성립 불명확(과다해석 방지). | "…상호작용시험은 이 약의 경구제와 음식, 시메티딘, **제산제,** 골수이식에 대한 전신방사선요법과의 병용 시 임상적으로 유의할만한 이 약의 **흡수장애가 일어나지 않음을 보였다.**…" |
| AT-05 | 이트라코나졸 | **antacid_draft_confirmed** | separation | 200404726 | Al/Mg 제산제 directive 동거어+directive 문맥+부정문구 부재+단일 경구 itemSeq → antacid draft 후보(영양소 relation 아님, live 금지). | "…**수산화알루미늄과 같은 위산중화제는 적어도 이 약 투여 2시간 전이나 2시간 후에** 투여하는 것을 권장함. 병용투여시 항진균효과를 관찰하고 필요한 경우 이트라코나졸 용량을…" |
| AT-06 | 케토코나졸 | needs_review | (없음) | (미확보) | DENY(fail-closed): 국내 단일 경구 완제 itemSeq 미확보 — 직접 지정 재확인 필요. | (itemSeq 미확보 — quote 없음) |

**reject 3건의 성격 구분(과다해석 방지):**
- AT-02 아지트로마이신 / AT-04 플루코나졸 — 제산제 **동거어는 실재**하나, 동일 문맥에 "생체이용율에 영향을 미치지 않았으나" / "흡수장애가 일어나지 않음" 같은 **부정문구**가 함께 있어 상호작용 성립이 불명확하다. 부정문구를 directive로 오독하지 않도록 reject.
- AT-03 클래리트로마이신 — 점검한 itemSeq(201211101·201211108) 라벨에서 Al/Mg 제산제 병용 **directive 동거어 자체가 미확인**되어 reject(근거 없음).

**needs_review 1건:** AT-06 케토코나졸 — 국내 단일 경구 완제 itemSeq를 확보하지 못해(no_domestic_single_oral_product) fail-closed로 보류. itemSeq 직접 지정 재확인 후 재게이트 필요.

## 8. 내부 필드 스키마 확정

draft batch(`data/drafts/antacid_interaction_draft_batch_v1_2.json`)는 §3 권장 레이어 분리 설계를 다음 필드로 구현한다(표면 중립 / 내부 원문 강도 보존):

| 필드 | 역할 | 값(이번 라운드) |
|---|---|---|
| `relation_type` | **표면** 트랙명(사용자 노출, 중립) | `antacid_interaction` |
| `counterpart_category` | **내부** 상대 카테고리 — 영양소 보충제 아님 | `al_mg_antacid` |
| `label_directive_type` | **내부** 라벨 지시 강도 보존 | `avoid_concomitant`(AT-01) / `separation`(AT-05) |
| `label_quote` | **내부** 라벨 원문 직역(충실성 검증용) | evidence json quote verbatim |
| `copy_risk_level` | **내부** 카피 위험도 | `high`(2건 모두) |
| `display_text_ko` | **표면** 사용자 노출 카피 | §4 PM 승인 템플릿 verbatim(아래) |

- **표면(surface) = `antacid_interaction`** — 사용자에게는 중립·참고정보 톤만 노출("상호작용 문구가 있습니다 + 상담").
- **내부(internal) = `label_directive_type` / `counterpart_category` / `label_quote`** — 라벨 원문 강도("복용하지 마십시오" 병용금지, "2시간 전·후" 간격)를 손실 없이 보존. AT-01은 `avoid_concomitant`(병용금지 직역), AT-05는 `separation`(라벨이 명시한 시간 간격) 으로 각 후보의 라벨 강도를 그대로 반영한다.
- **영양소(Mg) 트랙과 분리 재강조:** 상대(`counterpart_category=al_mg_antacid`)는 **Al/Mg 함유 제산제(약물 카테고리)**이며 마그네슘 **영양제(보충제)**가 아니다. 같은 다가양이온이라도 라벨은 제산제만 지목하므로, 본 트랙을 영양소(철/칼슘/Mg/아연/칼륨) relation 으로 박지 않는다(§2 결론 유지). 칼륨 보충 권유·결핍 단정은 본 트랙과 무관(0).
- draft batch 메타가 `do_not_implement_yet=true` · `live_integration_forbidden=true` · `published=false` · `clinical_reviewed=false` · `adversarial_verified=false` 를 모든 행에 보존함을 확인.

## 9. CQ-103(펙소페나딘 × Al/Mg 제산제) 재검토 결론

§0–2 분석과 v1.2 게이트 결과를 종합한 최종 결론:

- **일반 separation(영양소 Mg) 트랙으로 승격하지 않는다.** §1의 2/3 split(direction_correct·copy_reads_as_reference 실패)과 §2의 영양소-제산제 불일치가 그대로 유효하다. 펙소페나딘 라벨은 "복용하지 마십시오"라는 **병용금지(avoid_concomitant)**이며 상대는 **제산제(약물 카테고리)**이지 마그네슘 영양소 보충제가 아니다.
- **antacid_interaction 트랙 draft(AT-01)로 보관한다.** CQ-103의 실체는 본 라운드 AT-01(펙소페나딘 · itemSeq 202202380 · `avoid_concomitant`)로 게이트를 통과해 draft batch에 들어 있다(`antacid_draft_confirmed`, draft까지만).
- **surface = 중립 카피(§4 템플릿 verbatim):**
  > 일부 알루미늄·마그네슘 함유 제산제와 함께 사용할 때 약물 흡수에 영향을 줄 수 있다는 허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.
- **internal = `label_directive_type=avoid_concomitant`** + `label_quote` 로 원문 강도("복용하지 마십시오")를 손실 없이 보존.
- **라이브·일반 relation 미반영(`live_integration_forbidden=true`).** v0.2 데이터 export·일반 relation 배열에 반영하지 않는다. AT-05 이트라코나졸도 동일하게 antacid draft(separation)로만 보관한다.

## 10. 상태

- 본 라운드 **live 승격 0 · 일반 relation(영양소) draft 0.** published=false / clinical_reviewed=false 유지.
- antacid 전용 draft **2건(AT-01 펙소페나딘 · AT-05 이트라코나졸)** 은 `data/drafts/antacid_interaction_draft_batch_v1_2.json` 에 보관 상태. 모두 `do_not_implement_yet=true` · `adversarial_verified=false`.
- 다음 단계(별도 PM 단계): surface(`antacid_interaction`) 구현 여부 결정 → **적대검증(카피 충실성: 병용 프레이밍 유지·비지시성·영양소 오인 차단)** → forbidden phrase scanner 0 확인 → (필요 시) clinical reviewer. 본 문서는 설계·기록일 뿐 구현 지시가 아니다.
- reject 3(AT-02·AT-03·AT-04)·needs_review 1(AT-06)은 승격 대상 아님. AT-06은 itemSeq 재확보 후 재게이트 대상.

---

> 아래 §11 은 v1.3 relation harvester bot 의 **첫 운영 online manual run(2026-06-14, main `c88edc5`)** 결과를 §0–10 설계에 reconcile 한 **보강 섹션**이다. §0–10 의 설계·판정 의미는 변경하지 않는다. **live·draft 승격 없음**(`live_integration_forbidden=true` 유지). 본 섹션은 기록/설계이며 구현 지시가 아니다.

## 11. v1.3 harvester online reconcile + surface/render 상태

### 11.1 트랙 정의 재확인 (영양소 Mg relation 과의 차이)
antacid_interaction 은 **`약물 × Al/Mg 함유 제산제(약물 카테고리)`** 트랙이다. MediStack 의 핵심 모델인 **`약물 × 영양소(철/칼슘/Mg/아연/칼륨) 보충제`** relation 과 **개념적으로 분리**된다.

| 구분 | 영양소 Mg relation | antacid_interaction |
|---|---|---|
| 상대(counterpart) | 마그네슘 **영양제/보충제**(nutrient) | **Al/Mg 함유 제산제**(OTC 위장약, 약물 카테고리) |
| 데이터 키 | `nutrient="마그네슘"` | `counterpart_category="al_mg_antacid"` (`nutrient` 필드 **미사용**) |
| surface 표시 | nutrient 슬롯 = "마그네슘" | render_nutrient 슬롯 = **"Al/Mg 함유 제산제(약물)"** |
| 보충 권유 | 해당(영양소 트랙) | **0**(제산제는 보충 대상 아님) |

→ 같은 다가양이온이라 약리 개연은 있으나 라벨은 **제산제만** 지목하므로, 본 트랙을 Mg 영양소 relation 으로 저장하지 않는다. validator 가 `nutrient` 필드 존재·`surface.render_nutrient` 의 영양소 단독값·Mg 영양제 오인 표현을 fail 시킨다.

### 11.2 AT-FEX / AT-ITZ online itemSeq reconcile

harvester 첫 운영 run 이 두 후보를 `antacid_draft_confirmed` 로 확정했고, 기존 v1.2 draft(AT-01/AT-05)와 **다른 대표 itemSeq** 를 사용했다. 기존 근거를 폐기하지 않고 각 draft 의 `online_reconcile` 로 provenance 보강했다.

| draft_id | harvester id | 약물 | 기존 itemSeq(directive) | online itemSeq(directive) | online conf | 분류 | 처리 |
|---|---|---|---|---|---|---|---|
| AT-01 | AT-FEX-01 | 펙소페나딘 | 202202380 (avoid_concomitant · "…제산제를 복용하지 마십시오") | 199801016 (coadmin_caution · "…의사 또는 약사와 상의") | low | **대표 itemSeq 선택 차이**(기존 오류 아님) | 보수적으로 강한 directive(avoid_concomitant) primary 유지 + online provenance 보강 |
| AT-05 | AT-ITZ-01 | 이트라코나졸 | 200404726 (separation · "2시간 전/후") | 200401453 (separation · "2시간 전/후") | high | **대표 itemSeq 차이 + directive 일치** | 기존 유지 + online high-confidence 로 강도 재확인, provenance 보강 |

판정: 두 건 모두 **기존 itemSeq 가 틀린 것이 아니라 다른 유효 품목**(대표 itemSeq 선택 차이)이다. 펙소페나딘은 품목별 라벨 directive 강도가 갈리므로(202202380=병용금지 / 199801016=상의) 보수적으로 강한 쪽을 primary 로 두고 둘 다 provenance 에 남겼다. 이트라코나졸은 directive 가 일관(separation)되어 reconcile 충돌 없음. **confidence(AT-FEX low / AT-ITZ high)·counterpart_category(al_mg_antacid)·live_integration_forbidden·published/clinical_reviewed=false·reviewed_by 공란 모두 유지.**

### 11.3 render / surface 현재 상태 (src 무수정)
- **판단: 기존 generic relation 카드(`src/js/render.js renderDetail`/`renderRow`)가 antacid_interaction 을 안전하게 표시 가능 → `src/` 수정하지 않는다.**
- 표면 매핑(draft 의 `surface` 필드): `render_nutrient="Al/Mg 함유 제산제(약물)"` + `render_action="separation"`. 기존 카드의 nutrient 슬롯에 들어가면 **"마그네슘(영양소)"이 아니라 "Al/Mg 함유 제산제(약물)"** 로 표시되어 영양소 카드와 구분된다. action 은 기존 `separation` chip("복용 간격") 재사용(라벨 강도는 내부 `label_directive_type` 보존).
- guard 자동 차단: `product_link_allowed=false → canShowProduct=false`(제품/구매/제휴 UI 0), `potassium_safety_card=false → 칼륨 카드 미표시`.
- **입증**: `scripts/smoke_antacid_interaction_v1_2.py` 가 (1) 카피 시뮬레이션 + (2) **실제 render.js 호출** 로 두 draft 가 — 제산제 명시·영양소 오인 0·앱 카피 비지시('복용하지 마' 미노출, 출처 인용은 허용)·참고정보 프레이밍·상담 종결·공통 면책·제품 0·separation chip — 안전 렌더됨을 검증(PASS).
- **(선택, 미구현) 향후 src 강화안**: antacid 전용 chip/label(예: "제산제 관련 참고정보")로 영양소 카드와 시각적으로 더 분명히 구분. 이번 라운드는 generic 렌더로 충분하다고 판단해 **구현하지 않음**(애매할 때 docs/smoke 까지만 원칙). live 승격 단계에서 PM 결정.

### 11.4 live 승격 전 PM 체크리스트 (전부 미충족 — 이번 라운드 범위 밖)
- [ ] 적대검증(카피 충실성: 병용 프레이밍 유지·비지시성·영양소 오인 차단) 통과 → `adversarial_verified=true`
- [ ] 펙소페나딘 대표 itemSeq 정책 확정(강한 directive 품목 vs online 약한 품목 중 surface 근거로 무엇을 쓸지)
- [ ] surface 통합 방식 결정: 기존 generic 카드 재사용 vs antacid 전용 label(`src/render.js` 최소 변경) — 후자 선택 시 기존 relation 카드 회귀 smoke + antacid smoke + forbidden + live HTTP 200 동반
- [ ] clinical reviewer 확보 후 `clinical_reviewed` 전환 검토(현재 천장 = verified_reference)
- [ ] 별도 integrate 스크립트(멱등) + 새 버전 export/validator 상수 연쇄(칼륨/relation 승격 패턴 준용)

### 11.5 향후 live 통합 조건 (요약)
antacid_interaction 을 라이브에 노출하려면: ① 적대검증 통과, ② surface 표현(영양소 분리) 최종 확정, ③ clinical reviewer, ④ 멱등 integrate + validator 연쇄, ⑤ deploy 게이트(validator PASS) — **전부 별도 PM 단계**. 현재 상태는 **draft + surface 설계 + render 안전성 입증까지**이며 **live 승격 0**.

---

> §12 는 v1.3 round 의 **독립 적대검증(2026-06-14)** 결과를 §0–11 에 reconcile 한 보강 섹션이다. 자기확증 방지를 위해 독립 회의론자 서브에이전트가 raw 근거(라벨 원문 + 제안 카피)만 받아 refute-by-default 로 판정했다. **live 승격 0**(`live_integration_forbidden=true` 전건 유지). 감사 기록: `data/review/antacid_interaction_adversarial_verify_v1_3.json`.

## 12. 적대검증 결과 + AT-ITZ 1순위 + AT-FEX representative itemSeq 정책

### 12.1 검증 렌즈 / 방법
독립 회의론자 5인(refute-by-default)이 AT-ITZ/AT-FEX draft 를 다음 렌즈로 판정: ① fidelity(라벨 directive 강도 과약화/방향왜곡 없는가) ② non-directive(앱이 직접 지시 안 하는가) ③ Mg 영양제 오인 없는가 ④ track 구분(counterpart_category=al_mg_antacid) ⑤ 제품/구매/제휴 없는가. fidelity 는 카드 일부(body)가 아니라 **풀 렌더 카드(chip+kicker+출처 인용)** 기준으로 재검증.

### 12.2 결과 요약

| draft | 약물 | directive | 안전 4렌즈 | fidelity | 종합 | adversarial_verified |
|---|---|---|---|---|---|---|
| **AT-05** | 이트라코나졸 | separation | 전부 pass | **pass**(풀카드) | **survives** | **true(후보)** · **live 1순위** |
| AT-01 | 펙소페나딘 | avoid_concomitant | 전부 pass | **fail**(현 basis) | conditional_fail | **false** · 정책 결정 대기 |

### 12.3 AT-ITZ(이트라코나졸) — adversarial_verified=true · live 통합 1순위
- separation directive 가 풀 렌더 카드에서 방향 일치로 충실 표현됨: **chip "복용 간격" + kicker "같은 시간대 복용 주의" + 출처 인용의 "수산화알루미늄과 같은 위산중화제는 적어도 이 약 투여 2시간 전이나 2시간 후" 라벨 원문**. 앱이 "2시간 간격을 두세요"를 직접 명령하는 것은 비지시 제약 위반이므로, 현 구성이 **비지시 제약 하 최대 충실**.
- 초기 단일 렌즈의 fidelity refute("2시간 지침 생략")는 body 만 본 부분 컨텍스트 오류였고, 풀카드 재검증서 **기각**(direction error 없음 = co-use 허용 암시 0).
- **adversarial_verified=true 후보 + `live_candidate_rank=1`**. 단 `live_integration_forbidden=true` 유지 — rank 는 우선순위 표시일 뿐 승격 아님.
- (선택·비차단) 출처의 "2시간" 인용을 body 에 attributed quote 로 승격하면 가시성↑.

### 12.4 AT-FEX(펙소페나딘) — adversarial_verified=false · representative itemSeq 정책
- 안전 4렌즈(비지시·Mg오인·트랙·제품)는 통과하나, **fidelity 미통과**: 현 primary basis 인 **202202380(avoid_concomitant "…제산제를 복용하지 마십시오")** 에 대해 중립 카피("흡수 영향 + 확인")가 **prohibition 을 'co-use 가능 + 상담'으로 방향 왜곡(다운그레이드)**. 중립 카피는 **199801016(coadmin_caution "상의")** 에만 충실.
- **representative itemSeq 정책(PM 결정 대기):**

  | 옵션 | 내용 | 평가 |
  |---|---|---|
  | **A (권장)** | 강한 품목(202202380 avoid_concomitant) basis 유지 + **directive_type 별 템플릿** 도입: avoid_concomitant → §4 강한대안("…함께 복용하지 않도록 안내하는 문구가 있습니다…") / separation·coadmin_caution → 현 중립 템플릿 | 가장 강한 라벨 보존 + 충실 + 비지시. validator 템플릿 검사 확장 + 재적대검증 동반(차기 라운드) |
  | B | display basis 를 199801016(coadmin_caution)로 설정 → 현 중립 카피 충실 | low-confidence 약한 품목을 카피에 맞춰 선택하는 **integrity 우려**(에이전트 지적) |

- **권장 = Option A**(강한 라벨 보존). 단 템플릿/validator/재검증 동반이라 **차기 PM 라운드**. 그때까지 AT-FEX draft 유지·미승격(`adversarial_verified=false`).
- 두 itemSeq(202202380·199801016)와 verbatim quote·directive_type 는 `source`/`online_reconcile` 에 **모두 보존(폐기 0)**.

### 12.5 안전 불변(이번 라운드)
live 승격 0 · `live_integration_forbidden=true`(전건) · published/clinical_reviewed=false · reviewed_by 공란 · counterpart_category=al_mg_antacid · 제품/제휴 UI 0 · DATA_URL v0.2 · src 무수정 · export/full index/aliases 무변경. validator 에 "adversarial_verified=true 여도 자동 승격 금지" 불변 추가. **본 적대검증은 카피/안전 검증일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.**

---

> §13 은 **Option A 채택(2026-06-14)** 에 따른 directive 별 카피 구현 + AT-FEX(펙소페나딘) **재적대검증 round2** 결과를 §0–12 에 reconcile 한 보강 섹션이다. §0–12 의 의미는 변경하지 않는다. **live 승격 0**(`live_integration_forbidden=true` 전건 유지). 본 섹션은 기록/설계이며 구현 지시가 아니다.

## 13. Option A 채택 + directive 별 카피 + AT-FEX 재적대검증(round2)

### 13.1 Option A 채택 — directive_type 별 display 템플릿
§12.4 의 representative itemSeq 정책에서 권고된 **Option A(강한 품목 basis 유지 + directive 별 카피)** 를 이번 라운드 draft 에 반영했다(`representative_itemseq_policy.status=option_A_adopted_2026-06-14_draft_recopy`). live 승격이 아니라 **draft 카피/검증 계약**에 반영한 것이다.

| directive_type | display 템플릿 | 근거 |
|---|---|---|
| `avoid_concomitant`(AT-01 펙소페나딘) | **prohibition-보존형**: "일부 알루미늄·마그네슘 함유 제산제와 함께 **복용하지 않도록 안내하는** 허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요." | 라벨 '복용하지 마십시오'(병용금지) 강도를 출처 귀속형으로 보존(비지시). 중립 '흡수 영향' 템플릿은 다운그레이드라 금지. |
| `separation`(AT-05 이트라코나졸) / `coadmin_caution` | 기존 중립 템플릿("…함께 사용할 때 약물 흡수에 영향을 줄 수 있다는…") | separation/상담 directive 에는 중립 톤이 충실. |

구현 변경(이번 라운드):
- AT-01 `display_text_ko` → avoid_concomitant 전용 prohibition-보존 카피.
- AT-01 `surface.render_action` **separation→monitoring**: generic 카드의 separation chip '복용 간격'은 '간격 두면 병용 가능'으로 prohibition 을 다운그레이드(직전 라운드 fidelity 지적) → 제거.
- `scripts/validate_antacid_interaction_v1_2.py`: directive_type 별 템플릿 verbatim 검사 + avoid_concomitant 의 weak neutral 카피 금지 + directive↔render_action 정합(avoid_concomitant 에 '복용 간격' chip 금지).
- `scripts/smoke_antacid_interaction_v1_2.py`: directive-aware — avoid_concomitant 는 prohibition 보존('함께 복용하지 않도록')·weak neutral 미노출, separation 은 중립 프레이밍; node 렌더는 action chip(separation→'복용 간격'/monitoring→'상태 모니터링') 정합 검사.

### 13.2 AT-FEX 재적대검증 round2 — 결과: **conditional_fail(needs_copy_review)**
신규 Option A 카피 + monitoring chip 구성을 **독립 회의론자 7인(general-purpose) refute-by-default** 로 재검증(raw 근거: 라벨 원문 202202380/199801016 + 신규 카피 + 실제 풀 렌더 카드). 자기확증 방지를 위해 작성자 논리 미주입. 감사: `data/review/antacid_interaction_adversarial_verify_v1_3.json` 의 `results[AT-01].reverify_round2_option_A`.

| 렌즈 | 결과 | 핵심 |
|---|---|---|
| fidelity #1 다운그레이드(med) | **refuted** | 첫 문장은 prohibition 보존(중립보다 강함, 인정)이나 **둘째 문장 '함께 사용하는 경우에는…확인하세요'가 병용을 옵션으로 전제** → consult-grade 다운그레이드. |
| fidelity #2 강·약 품목 대조(high) | **refuted** | primary=강한 품목인데 body 2문장 + monitoring chip/kicker 가 **약한 품목(199801016 '상의') 강도에만 대응**. AT-05 풀카드 구제 논리 적용 불가(chip/kicker 가 directive 와 모순). |
| fidelity #3 풀카드(high) | **refuted** | monitoring chip '상태 모니터링' + kicker '**장기 복용 시** 상태 확인'이 병용금지에 모순 — '장기 복용'은 병용금지 관계에 성립 불가 시나리오 전제(적극적 방향 왜곡). |
| 비지시성(high) | survives | 앱 자체 카피 직접 명령 부재, 금지는 '문구가 있습니다' 귀속형, 상담 트리거만 명령형(허용). |
| Mg 영양제 오인(high) | survives | '마그네슘'은 항상 '함유 제산제' 수식, 제목 '(약물)' 태그로 영양소 단독 미노출. |
| 트랙 구분(high) | survives | 제목 '펙소페나딘 × Al/Mg 함유 제산제(약물)' 약물 명시, nutrient 필드 금지. |
| 제품/제휴(high) | survives | 제품/구매/제휴 0, 외부링크는 식약처 원문(출처 귀속)뿐. |

**판정: fidelity 3/3 refuted → AT-FEX `adversarial_verified=false` 유지, `status=needs_copy_review`.** 안전 4렌즈는 전부 통과. Option A 첫 문장의 prohibition 보존은 직전 중립 카피 대비 **개선**으로 확인됐으나, ①둘째 문장의 consult 다운그레이드와 ②generic 카드 chip/kicker 의 구조적 모순이 남아 풀 충실성 미달.

### 13.3 핵심 발견 — generic 카드는 avoid_concomitant 를 충실히 렌더할 수 없다
직전 라운드(separation chip '복용 간격' = spacing-OK 다운그레이드)와 round2(monitoring chip '상태 모니터링' + '장기 복용' = 병용+감시 다운그레이드)를 종합하면, **generic 카드의 두 action(separation·monitoring) 모두 avoid_concomitant(병용금지)와 방향이 모순**된다. separation 트랙(AT-05 이트라코나졸)에서는 chip/kicker 가 directive 와 일치해 generic 카드가 충실하지만, avoid_concomitant 는 그렇지 못하다. → **전용 chip 이 근본적으로 필요**(§15).

### 13.4 AT-FEX 차기 라운드 필요조건(2종, 함께 랜딩 + 재검증 후에만 verified)
> ✅ **해소됨(2026-06-15, §17): 두 조건(전용 chip src 구현 + copy 비-병용-전제)을 적용해 round4 적대검증 survives → AT-FEX `adversarial_verified=true` 후보(live 미승격).**
1. **copy v2 — 둘째 문장 비-병용-전제화.** 제안: "복용 중인 제산제가 있다면 약사 또는 의사와 상담하세요"(병용을 권하지 않으면서 기존 복용 상황을 상담으로 라우팅). consult-close 표현 변경 시 validator/smoke 상담 종결 검사 동반 수정.
2. **전용 avoid_concomitant chip(src 변경, §15).** 비-병용-전제 chip/kicker.

두 수정이 **함께** 적용되고 재적대검증을 통과해야 `adversarial_verified=true` 후보. 그때도 live 승격은 별도 PM + clinical reviewer.

### 13.5 안전 불변(이번 라운드)
live 승격 0 · `live_integration_forbidden=true`(전건) · published/clinical_reviewed=false · reviewed_by 공란 · counterpart_category=al_mg_antacid · 제품/제휴 UI 0 · DATA_URL v0.2 · **src 무수정** · export/full index/aliases 무변경. AT-05 adversarial_verified=true 후보(미승격)·AT-01 false(needs_copy_review). **본 적대검증은 카피/안전 검증일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.**

---

> §14 는 AT-ITZ(이트라코나졸) **live 통합 준비 문서**다. **실제 통합은 하지 않는다**(이번 라운드 `live_integration_forbidden=true` 유지). 통합 전 체크리스트·멱등 integrate 계획·validator 연쇄·통합 프롬프트 초안만 작성한다.

## 14. AT-ITZ(이트라코나졸) live 통합 준비 — 문서/프롬프트만(통합 0)

AT-ITZ 는 round1 적대검증 survives → `adversarial_verified=true` 후보 + `live_candidate_rank=1`(separation directive, generic 카드 충실). 단 **이번 라운드 live 통합은 수행하지 않는다.** 아래는 향후 별도 PM 라운드용 준비물이다.

### 14.1 live 통합 전 체크리스트(전부 충족돼야 통합 착수)
- [ ] **clinical reviewer 확보** → `clinical_reviewed` 전환 검토. 현재 천장 = `verified_reference`(미충족). reviewer 전까지 `published=false`/`clinical_reviewed=false`/`reviewed_by` 공란 유지.
- [ ] **source 재확인**: itemSeq 200404726(기존) + 200401453(online) 라벨 directive(separation '2시간 전/후') 재대조, `source.checked_at` 갱신.
- [ ] **surface 표현 최종 확정**: 영양소 분리(상대=Al/Mg 제산제 '약물'). separation directive 는 generic 카드(chip '복용 간격' + kicker '같은 시간대 복용 주의')로 충실 입증(round1 풀카드 survives) → **전용 chip 불요**(avoid_concomitant 와 다름).
- [ ] **적대검증 재확인**(통합 직전 1회 더, 카피 변경 시).
- [ ] forbidden phrase scanner 0 · antacid validator/smoke PASS.

### 14.2 멱등(idempotent) integrate 계획
칼륨/relation 승격 패턴(`integrate_*_v1_2.py`) 준용:
- **신규 버전 export 에 append-only** 추가(v0.1/v0.2 봉인 — 직접 수정 금지). 새 relation 1건(이트라코나졸 × "Al/Mg 함유 제산제(약물)") + 표면 매핑(render_nutrient/render_action) + source + 면책. `relation_count` +1 갱신.
- **멱등 가드**: integrate 스크립트가 동일 id 존재 시 no-op(재실행 안전). 입력=draft AT-05, 출력=신규 버전 export. 기존 relation 무변경(read-modify-write 시 diff=정확히 1행 추가).
- product 필드 0(제품/제휴 금지) · potassium_safety_card=false · counterpart_category=al_mg_antacid.

### 14.3 validator 연쇄(통합 시 PASS 필수)
1. 신규 버전 export validator(v0.2 validator 일반화 준용: relations≥기존+1, meta.relation_count 일치, 제품 필드 금지, requires_clinical_review 차단).
2. `validate_antacid_interaction_v1_2.py`(draft 계약 유지).
3. `validate_forbidden_phrases_v1_2.py`(신규 버전 export 의 display/management 스캔 포함).
4. `smoke_antacid_interaction_v1_2.py`(렌더 안전성) + 기존 relation 회귀 smoke(`smoke_relation_draft_v1_2.py` 등).
5. deploy 게이트(`deploy.yml` validate job) + live HTTP 200 + DATA_URL 교체 시 검증대상 동기화.

### 14.4 live 통합 프롬프트 초안(차기 라운드용 — 실행 금지)
> AT-ITZ(이트라코나졸 × Al/Mg 함유 제산제, separation) 1건만 신규 버전 export 에 **멱등 append-only** 통합하라. 전제: clinical reviewer 확보 + source 재확인 + 적대검증 재통과. 불변: v0.1/v0.2 봉인 무수정 · 제품/제휴 0 · counterpart_category=al_mg_antacid · published/clinical_reviewed=false 유지(reviewer 트랙 별도) · reviewed_by 는 reviewer 만 · DATA_URL/deploy 검증대상 동기 교체. 통합 후 validator 연쇄(§14.3) 전수 PASS + live HTTP 200 + git clean 확인. AT-FEX(needs_copy_review)·needs_review/reject 후보는 통합 금지.

### 14.5 generic card 충분성 재명시
AT-ITZ(separation)는 **generic 카드로 충분**(round1 풀카드 fidelity survives, 전용 chip 불요). 이는 avoid_concomitant(AT-FEX, 전용 chip 필요 — §15)와 구분되는 결론이다.

---

> §15 는 **antacid 전용 label 최소 UI 검토**다. 원칙상 **src 는 수정하지 않는다**(이번 라운드). 전용 label 필요성 판단과 src 변경안(프롬프트)까지만 문서화한다.

## 15. antacid 전용 label 최소 UI 검토 — src 무수정(문서/프롬프트만)

> ⚠️ **업데이트(2026-06-15): §15.3 전용 chip 은 이후 라운드에서 실제 src 에 구현되었고 round4 적대검증을 통과했다 — §17 참조.** 아래 §15.1~15.4 는 구현 직전(설계·근거) 기록으로 보존한다.

### 15.1 결론: separation 은 generic 충분, avoid_concomitant 는 전용 chip 필요
- **separation/coadmin_caution(AT-ITZ 등)**: generic 카드(chip '복용 간격'/'상태 모니터링' + kicker)가 directive 와 방향 일치 → **src 무수정 유지**. node render smoke 가 안전성 입증.
- **avoid_concomitant(AT-FEX 등)**: §13.3 — generic 두 action 모두 prohibition 과 모순(separation=spacing-OK / monitoring=병용+장기감시) → **전용 chip 이 필요**. (이 판단 시점엔 src 미구현 → 이후 §17 에서 구현.)

### 15.2 src 미구현 이유
- live 승격 전 UI 변경은 기존 relation 카드 **회귀 위험**(현 node render smoke 가 generic 카드 안전성을 입증 중).
- 이번 라운드 avoid_concomitant 후보(AT-FEX)는 **live 승격 0 · needs_copy_review** — 당장 전용 chip 없이도 draft 안전(미렌더/미승격).
- "애매하면 docs/smoke 까지" 원칙(§11.3 후속).

### 15.3 전용 chip 변경안(src — 차기 라운드, 실행 금지)
`src/js/render.js` ACTION 맵에 avoid_concomitant 전용 항목 추가(예):
```
avoid_concomitant: { label: '병용 주의', chip: 'chip-avoid', aClass: 'avoid', kicker: '함께 복용 권장 안 함' }
```
- 비-병용-전제: '복용 간격'(spacing-OK)·'장기 복용'(co-use 지속) 어휘 배제.
- renderRow/renderDetail 가 `recommended_action='avoid_concomitant'` 를 받도록 매핑(draft surface.render_action 확장 동반).
- 동반 필수: 기존 relation 카드 회귀 smoke + antacid smoke(directive-aware) + forbidden + live HTTP 200. validator 의 render_action enum 에 'avoid_concomitant' 추가.
- CSS `.chip-avoid`/`.alabel.avoid` 추가(중립 톤, 경고색 과장 금지).

### 15.4 변경안 프롬프트 초안(차기 라운드용 — 실행 금지)
> avoid_concomitant 전용 chip 을 `src/js/render.js`(+styles.css) 에 최소 추가하라. chip '병용 주의' / kicker '함께 복용 권장 안 함'(병용·간격·장기복용 전제 어휘 금지). draft surface.render_action='avoid_concomitant' 매핑 + validator render_action enum 확장 + smoke directive-aware 갱신. 불변: 기존 relation 카드 회귀 0(회귀 smoke PASS) · 제품/제휴 0 · 면책 유지 · live HTTP 200 · DATA_URL 무변경. 적용 후 AT-FEX copy v2 와 함께 재적대검증.

---

## 16. harvester 운영(별도 문서)
relation harvester bot v1.3 의 첫 운영 run 기록·manual run 루틴·schedule(비활성) 상태·커밋 제외 원칙은 **`docs/MediStack_harvester_ops_v1_3.md`** 로 분리했다(antacid 트랙과 별개 관심사). 요지: schedule 비활성(수동 dispatch 전용) · 봇 write-scope=`data/harvest_queue/` · live/배포/승격 0 · online run 산출물 커밋 제외.

---

> §17 은 **avoid_concomitant 전용 chip/surface 의 실제 src 구현 + AT-FEX round3/round4 재적대검증(2026-06-15)** 기록이다. §15 가 설계까지만 했던 전용 chip 을 src 에 구현하고 카피를 반복 개선해 **AT-FEX 가 round4 적대검증을 통과(`adversarial_verified=true` 후보)** 했다. **live 승격은 여전히 0**(`live_integration_forbidden=true` 유지). 본 섹션은 기록이며 구현 지시가 아니다.

## 17. avoid_concomitant 전용 chip 구현 + AT-FEX round3/round4

### 17.1 전용 chip 도입 이유 (round1~3 누적 근거)
generic relation 카드의 두 action 이 avoid_concomitant(병용금지)와 **방향 모순**임이 라운드별로 입증됐다:
- **round1**: separation chip '복용 간격' = '간격 두면 병용 가능' → spacing-OK 다운그레이드.
- **round2**: monitoring chip '상태 모니터링' + kicker '장기 복용 시 상태 확인' = '병용+장기감시' → 병용금지 관계에 성립 불가한 시나리오 전제(방향 왜곡).
→ generic 카드로는 병용금지를 충실히 렌더할 수 없음 → **전용 chip 필요**(§13.3 결론).

### 17.2 src 구현 (최소변경·additive)
`src/js/render.js` ACTION 맵에 avoid_concomitant 전용 항목 **추가**(기존 separation/monitoring 무변경):
```
avoid_concomitant: { label: '병용금지(허가사항)', chip: 'chip-avoid', aClass: 'avoid', kicker: 'Al/Mg 함유 제산제 관련 참고정보' }
```
`src/css/styles.css` 에 `.chip-avoid` / `.alabel.avoid`(clay 주의 톤, 기존 `--clay-deep`/`--clay-soft` 변수 재사용) 추가. **기존 relation/separation/monitoring/potassium/제품 카드 회귀 0**(full smoke 9종 PASS). 어떤 live relation 도 render_action=avoid_concomitant 를 쓰지 않으므로 production 동작 불변(전용 코드 경로는 draft smoke·향후 live 통합에서만 작동).

### 17.3 AT-FEX 카피·chip 반복 개선(round3 → round4)
| 라운드 | chip | 둘째 문장 | fidelity 결과 |
|---|---|---|---|
| round2 | (generic) 상태 모니터링 | 함께 사용하는 경우에는…확인하세요 | 3/3 refuted(chip 모순 + 둘째문장 consult 전제) |
| round3 | 제산제 동시 사용 주의 | 해당 제산제를 함께 사용해야 하는 상황이라면…확인하세요 | **2/3 refuted** — 전용 chip 이 generic 모순은 제거(generic_chip_contradiction_removed survives)했으나 chip '**주의**' 레지스터가 절대 병용금지보다 약함(f2·f3) |
| round4 | **병용금지(허가사항)** | **이미 복용 중인 제산제가 있다면**…확인하세요 | **survives(0/3 refuted)** |

- **chip '병용금지(허가사항)'**: prohibition 어휘('병용금지')를 전면에 두되 '(허가사항)' 출처 귀속으로 비지시 유지(round3 fidelity 지적: '주의' 레지스터는 금지보다 약함). '병용금지'는 한국어 의약 directive 최강 레지스터로 라벨 '복용하지 마십시오'와 등급 일치.
- **copy v3 둘째 문장 '이미 복용 중인 제산제가 있다면 약사 또는 의사에게 확인하세요'**: 미래 병용을 옵션으로 권하지 않고 **기존(이미 발생한) 병용 상황을 발견해 전문가로 라우팅**(round2/round3 의 consult 다운그레이드 해소).

### 17.4 round4 재적대검증 결과 — survives
독립 회의론자 8인(fidelity 3인 패널 + 비지시·Mg오인·generic chip 모순제거·제품·source구분), refute-by-default, **회의론자가 실제 `src/js/render.js`·draft·smoke 코드를 직접 검증**. 감사: `data/review/antacid_interaction_adversarial_verify_v1_3.json` 의 `results[AT-01].reverify_round4`.

| 렌즈 | 결과 |
|---|---|
| fidelity #1 다운그레이드(high) | survives — 둘째문장 기존-상황 라우팅, prohibition 보존 |
| fidelity #2 강·약 품목(med) | survives — chip '병용금지'+body+출처가 강한 품목(202202380)에 대응 |
| fidelity #3 풀카드(high) | survives — '병용금지' 최강 레지스터·'(허가사항)' 귀속, 표면 모순 0 |
| 비지시성(high) | survives — chip 은 directive 분류 라벨('(허가사항)' 귀속), 앱 명령 아님 |
| Mg 영양제 오인(high) | survives — '마그네슘'은 항상 '함유 제산제' 수식, 제목 '(약물)' 태그 |
| generic chip 모순 제거(high) | survives — separation/monitoring 신호 0 |
| 제품/제휴(high) | survives — 외부링크는 식약처 원문뿐 |
| 출처 인용 vs 앱 카피(high) | survives — directive 인용은 접힘 details(식약처 귀속), 본문은 보고형 |

**판정: round4 전 렌즈 survives → AT-FEX `adversarial_verified=true` 후보.** round2→round3→round4 는 회의론자가 제시한 수정을 적용하고 **신규 독립 패널**로 재검증한 정당한 반복 개선(게이밍 아님 — 회의론자가 실코드 검증). 단 **live 승격은 별도 PM + clinical reviewer**(`live_integration_forbidden=true` 유지).

### 17.5 AT-ITZ vs AT-FEX — live 준비 상태 차이
| | AT-ITZ(이트라코나졸) | AT-FEX(펙소페나딘) |
|---|---|---|
| directive | separation | avoid_concomitant |
| surface | generic 카드(chip '복용 간격') 충분 | **전용 chip '병용금지(허가사항)'** 필요(구현됨) |
| adversarial_verified | true 후보(round1 survives) | **true 후보(round4 survives)** |
| confidence | high | low(품목별 directive 강도 갈림 — 강한 품목 202202380 primary) |
| live_candidate_rank | 1 | (미지정) |
| 공통 | live 승격 0 · clinical_reviewed=false · reviewed_by 공란 · published=false | 동일 |

→ 둘 다 `adversarial_verified=true` 후보지만 **live 미승격**. AT-ITZ 가 confidence high·rank 1 로 통합 우선순위가 높다.

### 17.6 live 통합 전 체크리스트(AT-FEX, 전부 미충족 — 이번 라운드 범위 밖)
- [ ] clinical reviewer 확보 → `clinical_reviewed` 전환 검토(현재 천장=verified_reference).
- [ ] source 재확인(강한 품목 202202380 avoid_concomitant directive 재대조, `source.checked_at` 갱신).
- [ ] live 통합 시 §14 패턴(신규 버전 export 멱등 append-only + validator 연쇄 + deploy 게이트 + live HTTP 200). avoid_concomitant render_action 이 live export relation 에 처음 등장하므로 facet 정렬(ACTION_ORDER) 보강 검토.
- [ ] 통합 직전 적대검증 1회 더(카피/표면 변경 시).
- [ ] 별도 PM 승인. **본 verified 는 카피/표면 충실성·안전성 검증일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.**

### 17.7 안전 불변(이번 라운드)
live 승격 0 · `live_integration_forbidden=true`(전건) · published/clinical_reviewed=false · reviewed_by 공란 · counterpart_category=al_mg_antacid · 제품/제휴 UI 0 · DATA_URL v0.2 · export/full index/aliases/harvest_queue 무변경 · 기존 relation 카드 회귀 0. **src 변경은 avoid_concomitant 전용 ACTION 항목 + CSS 2줄 additive 뿐**(generic/live 카드 무영향). AT-05 이트라코나졸 상태 무변경(separation·adversarial_verified=true 후보·rank 1).

---

> §18 은 **AT-05(이트라코나졸 × Al/Mg 함유 제산제)의 라이브 통합(2026-06-15)** — antacid_interaction **트랙 첫 live relation** 기록이다. §14 의 통합 계획을 실행했다. **AT-FEX(펙소페나딘·avoid_concomitant)는 통합하지 않는다**(별도). published/clinical_reviewed=false·reviewed_by 공란 유지.

## 18. AT-ITZ(이트라코나졸) 라이브 통합 — antacid_interaction 첫 live relation

### 18.1 통합 결정·범위
PM 승인으로 **AT-05(이트라코나졸 × Al/Mg 함유 제산제, separation)만** v0.2 export 에 통합했다(id 61). antacid_interaction 트랙 **첫 live relation**. AT-ITZ 는 round1 적대검증 survives(separation·generic 카드 충실·high confidence)로 통합 자격. **AT-FEX(펙소페나딘·avoid_concomitant)는 통합하지 않음**(confidence low·별도 라운드).

### 18.2 멱등 integrate(`scripts/integrate_antacid_itz_v1_2.py`) — export only
- v0.2 export: relations **59 → 60**(id 61 append), `meta.relation_count` 60. 멱등(이트라코나졸×al_mg_antacid 이미 있으면 skip — 재실행 검증 완료).
- draft surface → live 매핑: `nutrient`='Al/Mg 함유 제산제(약물)'(render_nutrient), `recommended_action`='separation'(render_action), `mechanism`='absorption', `evidence_level`='high'. draft-전용 필드(draft_id/surface/adversarial_*/published/clinical_reviewed/reviewed_by/live_integration_forbidden 등) strip.
- 안전 필드: `product_link_allowed`=false · `potassium_safety_card`=false · `requires_clinical_review`=false · `counterpart_category`='al_mg_antacid'(비-영양소 마커). source={type,url(itemSeq 200404726),pointer(+확인일)}.
- **full index/aliases 무변경**: 이트라코나졸은 CANONICAL_13 아님 + alias verified_item_seqs pool 부재 → **name_only 유지**(flip 불필요). full index relation_card 1168·name_only 16412 불변. (CQF01/CQF02 가 nutrient relation 이라 full index flip 한 것과 구분 — antacid 는 영양소 트랙 아님.)

### 18.3 검색 facet 처리(src 최소변경) — 영양소 오인 차단
antacid relation 의 `nutrient` 슬롯은 영양소가 아니라 '제산제(약물)'이므로, 검색 '영양소' 필터에 노출되면 안 된다(round4 회의론자 지적). `src/js/guards.js`의 `getFacets` 를 **counterpart_category 가 있는 relation 은 nutrients facet 에서 제외**하도록 1줄 수정(`rels.filter((r) => !r.counterpart_category)`). 기존 영양소 relation 은 counterpart_category 가 없어 영향 0. → 검색 '영양소' 필터엔 실제 영양소 6종만, 'Al/Mg 함유 제산제(약물)'는 미노출(node 검증 PASS). AT-ITZ 는 기본 목록·검색('이트라코나졸'/'제산제')·분류 필터(separation)로 발견 가능.

### 18.4 렌더(generic separation 카드)
이트라코나졸 × Al/Mg 함유 제산제(약물) 카드: kicker '같은 시간대 복용 주의' + chip '복용 간격'(separation) + 본문(중립 카피) + 출처(itemSeq 200404726, 접힘) + 공통 면책. round1 풀카드 fidelity survives 그대로. 검색 시 relation 매치이므로 name_only fallback 미표시(이중노출 0).

### 18.5 검증(전수 PASS)
- 신규 `scripts/validate_antacid_itz_integration_v1_2.py`: relations 60·AT-ITZ 1건·필드/안전 플래그·draft-전용 미누출·reviewed_by 미기재·source itemSeq·display verbatim·full index 무변경·(node) facet 제외·separation 렌더·제품0·면책.
- relation-count 하드코딩 validator 9종 59→60 갱신(full index·factory_integration·cqf02_integration·relation_draft[ANTACID_IDS={61}]·coverage_queue_integration/draft_batch/batch3/batch4·factory_draft_batch).
- 배포 게이트(v0.1 12/12·v0.2 15/15·v0.3 aliases·alias surface·full index·potassium policy+selftest) · antacid validator/smoke · forbidden 0 · no-live-write guard · full smoke 9종 전부 PASS.

### 18.6 안전 불변
relations 59→60(AT-ITZ 1건만)·published/clinical_reviewed=false·reviewed_by 공란·제품/제휴 UI 0·DATA_URL v0.2·**full index/aliases/harvest_queue/excluded 무변경**·기존 59 relation 보존·src 변경=getFacets 1줄(facet 제외)뿐. AT-FEX 미통합. **본 통합은 verified_reference 천장의 참고정보 노출일 뿐 clinical_reviewed(임상 검수)·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.** clinical reviewer 확보 시 별도 `clinical_reviewed` 트랙.

---

> §19 는 **AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, avoid_concomitant) live 통합 *준비*(2026-06-15)** 기록이다. **실제 통합은 하지 않는다**(`live_integration_forbidden=true` 유지·live 승격 0). avoid_concomitant 가 라이브 enum 에 처음 등장하는 데 필요한 validator/action-order 선행작업 + 통합 드라이런 + 안전검증까지만 수행했다. AT-FEX 는 confidence=low 이고, live 승격은 별도 PM + clinical reviewer 가 전제다.

## 19. AT-FEX(펙소페나딘·avoid_concomitant) live 통합 준비 — 드라이런·선행작업만(통합 0)

### 19.0 범위
AT-FEX 는 round4 적대검증 survives(`adversarial_verified=true` 후보, §17). 단 ① avoid_concomitant 가 라이브 export relation 에 **처음** 등장하므로 v0.2 export validator·facet 정렬이 이를 안전하게 받을 수 있어야 하고, ② confidence=low + clinical reviewer 미확보라 **이번 라운드 live 통합은 금지**. 따라서 "통합 준비 상태"만 만든다(드라이런 + 검증 + 문서/프롬프트).

### 19.1 선행작업 — avoid_concomitant 안전 허용(validator/action-order)
이미 배포된 `src/js/render.js` ACTION 맵의 전용 chip(`avoid_concomitant: '병용금지(허가사항)'`, §17.2)에 더해, **라이브 데이터가 avoid_concomitant 를 담을 수 있도록** 두 곳을 보강했다. 현 라이브엔 avoid_concomitant relation 0건이라 **production 동작 불변**(아래 둘 다 inert).

| 파일 | 변경 | 효과 |
|---|---|---|
| `scripts/validate_medistack_v0_2_export.py` | `ALLOWED_ACTION` 에 `avoid_concomitant` 추가 + **신규 check #15**: ①avoid_concomitant ⇒ counterpart_category=al_mg_antacid(없으면 fail — 영양소 relation 의 avoid_concomitant 차단) ②antacid relation(al_mg_antacid) ⇒ product_link_allowed=false ③reviewed_by 전건 공란 | 검사 15→16. 라이브 export 계속 **PASS 16/16**(avoid_concomitant 0건·AT-ITZ link=false·reviewed_by 부재). 음성 5종(문맥밖 avoid / 영양소 avoid / antacid product_link=true / reviewed_by 작성 / evidence=low) 전부 FAIL 확인. |
| `src/js/render.js` | `ACTION_ORDER` 에 `avoid_concomitant` 추가(끝자리) | '분류' facet 정렬에만 영향. 라이브 facets.actions 에 avoid_concomitant 부재라 정렬 무변화. live 통합 시 전용 label('병용금지(허가사항)')로 끝자리 노출(raw 키 미노출). |

> ⚠️ **product_link_allowed 가드는 antacid(al_mg_antacid) relation 에만** 적용한다. 라이브 일반 relation 60건 중 **54건이 product_link_allowed=true**(v0.2 정책상 제품 데이터 부재라 canShowProduct=false — 정상)이므로, 글로벌 금지로 만들면 배포 게이트가 깨진다. antacid relation 만 추가 잠금(false 강제).

### 19.2 AT-FEX 통합 드라이런 결과(`integrate_antacid_fex_v1_2.py`)
- 스크립트는 **기본값이 dry-run(쓰기 0)**. live 기록은 `--pm-approved` 플래그가 있어야만 수행(별도 PM 승인 전까지 금지·본 세션 미사용). AT-ITZ 가드 + avoid_concomitant 가드 승계.
- 드라이런 산출물(예상 통합 결과): `data/review/antacid_fex_dryrun_v1_2.json`(리뷰 산출물·live 아님).

| 항목 | 드라이런 예상값 | 비고 |
|---|---|---|
| 신규 id | **62** | max(id)=61 +1 |
| relations | **60 → 61** | meta.relation_count 61 |
| relation_card / name_only | **1168 / 16412 (무변경)** | 펙소페나딘 44건 전부 name_only·covered_by_relation=false → flip 불필요(AT-ITZ 패턴) |
| full index / aliases | **무변경** | 펙소페나딘 CANONICAL_13 아님·alias pool 부재 |
| nutrient(슬롯) | "Al/Mg 함유 제산제(약물)" | 영양소 아님 |
| recommended_action | **avoid_concomitant** | 전용 chip '병용금지(허가사항)' |
| mechanism / evidence_level | absorption / **moderate** | ⚠️ **evidence_level=moderate 는 PM 판단지점**: confidence=low 이나 evidence 는 별개 — 식약처 허가사항(규제 출처)이라 low 아니고, 대표 itemSeq 강도 분기(202202380 병용금지 / 199801016 상의)로 high(AT-ITZ)도 아님 → moderate. v0.2 enum {high,moderate} 충족. |
| counterpart_category | al_mg_antacid | getFacets 영양소 facet 제외 |
| product_link_allowed / potassium_safety_card / requires_clinical_review | false / false / false | |

### 19.3 드라이런 안전검증(`validate_antacid_fex_dryrun_v1_2.py`)
시뮬레이션 export(live + AT-FEX, 임시파일)로 통합 시 안전성을 미리 입증(라이브 무수정):
- 시뮬 export **v0.2 validator PASS**(avoid_concomitant 가 #15 가드 하 허용됨 입증).
- (node) getFacets.nutrients 에 'Al/Mg 함유 제산제(약물)' **제외**(영양소 오인 0)·실제 영양소 유지. getFacets.actions 에 avoid_concomitant 포함. '분류' facet 에 전용 label '병용금지(허가사항)' 렌더(raw 키 미노출).
- (node) renderRow/renderDetail **전용 chip '병용금지(허가사항)'** 사용·generic('복용 간격'/'상태 모니터링') 미사용·kicker 'Al/Mg 함유 제산제 관련 참고정보'·'장기 복용 시 상태 확인' 미노출(병용금지 모순 제거). 앱 카피 비지시('복용하지 마' 미노출)·prohibition 보존('함께 복용하지 않도록')·제산제 명시·Mg 오인 0·제품 0·공통 면책.
- 라이브 export **relations 60·펙소페나딘 미존재 불변**(sha256 동일).

### 19.4 안전 불변(이번 라운드)
live 승격 0 · `live_integration_forbidden=true` · published/clinical_reviewed=false · reviewed_by 공란 · counterpart_category=al_mg_antacid · 제품/제휴 UI 0 · DATA_URL v0.2 · **live export/full index/aliases/harvest_queue/excluded 무변경**. src 변경=ACTION_ORDER 1줄(facet 정렬·inert). validator 변경=v0.2 export validator avoid_concomitant 허용 + #15(라이브 계속 16/16 PASS). **본 준비는 카피/표면 충실성·안전성 검증일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.**

### 19.5 AT-FEX live 통합 전 체크리스트(전부 미충족 — 범위 밖)
- [ ] **clinical reviewer 확보** → `clinical_reviewed` 전환 검토(현 천장=verified_reference). reviewer 전까지 published/clinical_reviewed=false·reviewed_by 공란.
- [ ] **source 재확인**: 강한 품목 202202380(avoid_concomitant) directive 재대조, `source.checked_at` 갱신.
- [ ] **evidence_level 확정**: moderate(드라이런 기본) PM 승인 또는 조정.
- [ ] **별도 PM 승인** → `integrate_antacid_fex_v1_2.py --pm-approved` 1회(멱등).
- [ ] **relation-count 하드코딩 validator 60→61 갱신**(AT-ITZ 때 59→60 한 9종: full index·factory_integration·cqf02_integration·relation_draft[ANTACID_IDS]·coverage_queue_integration/draft_batch/batch3/batch4·factory_draft_batch) + `validate_antacid_itz_integration_v1_2.py` 의 id 집합 baseline + 신규 `validate_antacid_fex_integration_v1_2.py`(드라이런 검증기를 live 대상으로 전환).
- [ ] **통합 직전 적대검증 1회 더**(카피/표면 변경 시).
- [ ] **deploy 게이트 PASS + live HTTP 200 + git clean**.

### 19.6 AT-FEX live 통합 프롬프트 초안(차기 라운드용 — 실행 금지)
> AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, **avoid_concomitant**) 1건만 v0.2 export 에 **멱등 append-only** 통합하라(`scripts/integrate_antacid_fex_v1_2.py --pm-approved`). **전제(전부 충족돼야)**: clinical reviewer 확보 + source(202202380) 재확인 + evidence_level(moderate) PM 승인 + round4 적대검증 재확인. **불변**: v0.1/v0.2 봉인 외 직접수정 금지(integrate 스크립트만)·relations 60→61(id 62)·counterpart_category=al_mg_antacid·전용 chip '병용금지(허가사항)'·product_link_allowed=false·published/clinical_reviewed=false 유지(reviewer 트랙 별도)·reviewed_by 는 reviewer 만·full index/aliases 무변경(펙소페나딘 name_only)·DATA_URL v0.2 유지. **통합 후**: relation-count 하드코딩 validator 60→61 갱신 + v0.2 export validator(16/16) + antacid validator/smoke + forbidden 0 + full smoke 9종 + 신규 AT-FEX integration 검증기 + no-live-write guard 전수 PASS + deploy 게이트 + live HTTP 200 + git clean. 칼륨 5건·needs_review/reject 후보는 통합 금지.
