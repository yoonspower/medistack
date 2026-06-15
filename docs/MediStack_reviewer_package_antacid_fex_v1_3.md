# MediStack — Clinical Reviewer 패키지: AT-FEX (펙소페나딘 × Al/Mg 함유 제산제) (v1.3)

작성일: 2026-06-15 · 상태: **검수 대기 / 승격 0 · 자기완결 reviewer 배포본** · 면허 검수자(약사/의사)용

> 이 문서는 antacid_interaction 트랙의 **AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, `avoid_concomitant`)** 1건 검수에
> 필요한 모든 것을 한 장에 담은 **단일 진실원(reviewer 배포본)** 이다. 핸드오프 인덱스는 `docs/MediStack_clinical_reviewer_handoff_v1_2.md` §7,
> 적대검증/통합준비 상세는 `docs/MediStack_antacid_interaction_track_v1_2.md` §17·§19 가 정의한다.
> **이 문서를 읽고 §5 note 템플릿을 채워 돌려주면, PM 라운드에서 `--pm-approved --reviewer-note` 로만 통합한다.**
> 원천 데이터: `data/drafts/antacid_interaction_draft_batch_v1_2.json`(AT-01).

---

## 0. 검토 범위 & 계약

| 항목 | 값 |
|---|---|
| candidate_id / draft_id | **AT-FEX-01 / AT-01** |
| 관계 | 펙소페나딘 × **Al/Mg 함유 제산제(약물)** — 영양소(Mg 보충제) relation **아님** |
| directive / action | `avoid_concomitant`(라벨 '병용금지') — **라이브 enum 에 처음** 등장 |
| mechanism | `absorption`(Al/Mg 제산제가 펙소페나딘 흡수에 영향) |
| confidence / evidence_level | confidence **low** / evidence_level **moderate** (⚠️ PM 판단지점) |
| primary itemSeq(근거) | **202202380** — avoid_concomitant 강한 directive("…제산제를 복용하지 마십시오") |
| online provenance itemSeq | **199801016** — coadmin_caution 약한 directive("…의사 또는 약사와 상의하십시오") |
| counterpart_category | `al_mg_antacid`(비-영양소 마커 — getFacets 영양소 facet 에서 제외) |
| 안전 플래그 | `product_link_allowed=false` · `potassium_safety_card=false` · `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란 |
| 통합 시 변화 | relations 60 → **61**(id 62) · 전용 chip '병용금지(허가사항)' · full index/aliases 무변경 |
| 적대검증 | round4 독립 회의론자 8인 survives(`adversarial_verified=true` 후보) |

### evidence_level=moderate 근거 (⚠️ PM/reviewer 판단지점)

- confidence=low 이나 **식약처 허가사항(고품질 규제 출처)** 이라 'low' 가 아니다.
- 대표 itemSeq **강도 분기**(202202380 병용금지 / 199801016 상의)로 인한 불확실성 때문에 'high'(AT-ITZ 수준)도 아니다.
- → **'moderate'**. v0.2 enum {high, moderate} 충족.

---

## 1. source quote vs 앱 카피 (구분 — 원문과 표시 문구를 분리 검토)

**① primary 라벨 원문(verbatim, itemSeq 202202380):**
> "이 약을 복용하는 동안 피부질환용약, 비염용 내복약을 포함한 다른 알레르기용약, 항히스타민제를 함유한 내복약 등, **알루미늄 또는 마그네슘 함유 제제의 제산제를 복용하지 마십시오.** 이 약을 복용하는 동안 케토코나졸이나 에리트로마이신과 함께 복용하지 마십시오. …"

**② online provenance 라벨 원문(verbatim, itemSeq 199801016):**
> "…알루미늄, 수산화마그네슘을 함유한 제산제, 아팔루타마이드와 같은 P-gp 유도제와 함께 사용 시 **의사 또는 약사와 상의하십시오.** …"

> 두 품목 모두 유효한 **다른 대표품목**(대표 itemSeq 선택 차이, 기존 itemSeq 오류 아님). 보수적으로 **강한 directive(202202380)** 를 primary 로 유지하고, 약한 쪽(199801016)은 provenance 로 **보존(폐기 0)**.

**③ 앱 사용자 표시 문구(verbatim — 앱이 실제로 보여주는 카피):**
> "일부 알루미늄·마그네슘 함유 제산제와 함께 복용하지 않도록 안내하는 허가사항 문구가 있습니다. 이미 복용 중인 제산제가 있다면 약사 또는 의사에게 확인하세요."

**④ 앱 표면(chip/kicker):**
- 전용 chip **'병용금지(허가사항)'** + kicker **'Al/Mg 함유 제산제 관련 참고정보'**.
- generic '복용 간격'(separation)·'상태 모니터링'(monitoring) 은 **미사용**(병용금지와 모순이라 제거).
- 앱은 직접 "복용하지 마세요" 라고 **명령하지 않는다**(비지시) — prohibition 강도는 **출처 귀속('허가사항')** 으로 운반.

> 즉 **원문은 "복용하지 마십시오"(명령형 라벨 문구)** 이고, **앱 카피는 "…문구가 있습니다 / …확인하세요"(비지시·출처 귀속)** 다. 강도는 보존하되 앱이 직접 지시하지 않는 분리 구조를 검토 대상으로 본다.

---

## 2. 적대검증 요약 (round4 survives)

독립 회의론자 refute-by-default(자기확증 방지)로 4라운드 진행, round4 에서 8인 전원 survives(0 refuted):

| 렌즈 | 결과 |
|---|---|
| fidelity_no_overweaken(원문보다 약화 안 함) | pass |
| non_directive(앱 비지시) | pass |
| mg_supplement_confusion(Mg 영양제 오인 방지) | pass |
| generic_chip_contradiction_removed(generic monitoring/separation 모순 제거) | pass |
| no_product_affiliate(제품/제휴 0) | pass |
| source_quote_vs_appcopy(원문 인용 vs 앱 카피 구분) | pass |

상세 ledger: `data/review/antacid_interaction_adversarial_verify_v1_3.json`.

---

## 3. 검증 절차 (PM/AI 가 통합 전 재현 — reviewer 가 직접 실행 불필요)

```bash
# (1) dry-run — live 무수정, 예상 산출물만 기록(60→61 시뮬)
python3 scripts/integrate_antacid_fex_v1_2.py
# (2) dry-run 산출물 검증(시뮬 export v0.2 PASS·전용 chip·facet 제외)
python3 scripts/validate_antacid_fex_dryrun_v1_2.py
# (3) reviewer-note 게이트 회귀(invalid 거부 + valid 통과 + live export sha256 불변)
python3 scripts/test_reviewer_note_gate_v1_3.py
```

- 통합(`--pm-approved --reviewer-note <노트>`)은 **§5 note 가 §4 요건 전건 충족 시에만** 동작한다. 미충족이면 STOP.
- 실제 승격 시 relation-count 하드코딩 validator 들을 **60→61** 갱신 + 신규 `validate_antacid_fex_integration_v1_2.py`(드라이런 검증기를 live 대상으로 전환).

---

## 4. reviewer note 인터록 요건 (이 패키지의 통과 조건)

`integrate_antacid_fex_v1_2.py` 의 `--reviewer-note` 게이트(`check_reviewer_note`)는 아래를 **전건** 요구한다(미충족 시 STOP):

1. **비공란**(노트 파일 존재 + 내용 있음).
2. **승인 토큰** `approved` 또는 `승인` 포함.
3. **candidate_id 명시**: `AT-FEX-01` 또는 `AT-01` 중 하나 이상.
4. **primary itemSeq 명시**: `202202380`(대표 근거 승인 확인).
5. **evidence_level 'moderate' 승인 문구 명시**.
6. **SAMPLE/예시 토큰 거부** + **미기입 placeholder 거부**(칼륨 패키지와 동일 마커).

> 즉 §5 템플릿을 **그대로 제출하면 거부된다.** 실제 승인 시 (a) 예시 토큰 `APPROVED-SAMPLE-NOT-VALID` → `approved`/`승인` 으로 교체, (b) 빈칸을 실제 값으로 채워야 통과한다.

---

## 5. reviewer note 템플릿 (복붙용 — 채워서 돌려주세요)

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

## 6. 검수자에게 묻는 질문 (verdict: approved / revise / reject + notes)

1. **primary itemSeq 202202380**(avoid_concomitant)을 대표 근거로 써도 되는가(더 약한 199801016 대신)?
2. **199801016의 약한 문구**와 **202202380의 강한 문구**를 provenance 로 **함께 보존**하는 정책이 적절한가?
3. **'병용금지(허가사항)' chip** 이 앱의 직접 지시가 아니라 **출처 귀속**으로 충분히 이해되는가?
4. user-facing copy 가 prohibition(병용금지)을 **과소표현하지 않는가**(약사 확인 라우팅으로 강도 보존)?
5. **confidence low / evidence moderate** 로 `verified_reference` 수준 live 노출이 가능한가?
6. avoid_concomitant 가 라이브 enum 에 **처음** 들어오는 것에 대한 안전 우려가 있는가?

---

## 7. 안전 원칙 (불변)

원문에 없으면 노출 금지 / 원문보다 강하면 금지(반대로 **과소표현도 금지** — 강도 보존) / 앱은 직접 복용지시 금지(비지시·출처 귀속) /
**Mg 영양제 relation 으로 저장 금지**(counterpart_category=al_mg_antacid·영양소 facet 제외) / 제품·구매·제휴 0 /
clinical 검수 전 published 금지 / reviewer 노트가 와도 **자동으로 `clinical_reviewed=true`·`published=true` 전환하지 않는다**(핸드오프 §4) /
evidence_level 임의 상향 금지(moderate 근거 = confidence low + 대표 itemSeq 분기) /
"식약처 승인 / 법적 문제 없음 / 약사 검수 완료" 표현 0.
