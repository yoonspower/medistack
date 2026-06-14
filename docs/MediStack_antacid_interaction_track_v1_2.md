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
