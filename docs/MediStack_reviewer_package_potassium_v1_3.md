# MediStack — Clinical Reviewer 패키지: 칼륨 depletion PM-ready 4건 (v1.3)

작성일: 2026-06-15 · 상태: **검수 대기 / 승격 0 · 자기완결 reviewer 배포본** · 면허 검수자(약사/의사)용

> 이 문서는 칼륨 depletion PM-ready **4건(DF01·DF04·DF05·DF-PRED-01)** 의 검수에 필요한 모든 것을
> 한 장에 담은 **단일 진실원(reviewer 배포본)** 이다. 핸드오프 인덱스는 `docs/MediStack_clinical_reviewer_handoff_v1_2.md`,
> relation-level 검수 스키마/플로우는 `docs/MediStack_v1.0_clinical_reviewer_checklist.md` 가 정의하며 여기서 중복하지 않는다.
> **이 문서를 읽고 §5 note 템플릿을 채워 돌려주면, PM 라운드에서 `--pm-approved --reviewer-note` 로만 통합한다.**
> 원천 데이터: `data/review/potassium_depletion_pm_ready_v1_2.json`(DF01·DF04·DF05) + `data/review/prednisolone_potassium_draft_recheck_v1_3.json`(DF-PRED-01).

---

## 0. 검토 범위 & 공통 계약

| 항목 | 값 |
|---|---|
| 검토 대상 | DF01 메틸프레드니솔론 · DF04 아세타졸아미드 · DF05 아조세미드 · DF-PRED-01 프레드니솔론 (× 칼륨) |
| 관계 유형(4건 공통) | `nutrient=칼륨(영양소)` · `mechanism=depletion` · `recommended_action=monitoring` · `evidence_level=high` |
| 안전 플래그(4건 공통) | `potassium_safety_card=true` · `product_link_allowed=false` · `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란 |
| 사용자 표시 | **약물명 + 장기/고용량 조건절 + 칼륨 상태 영향 + 상담 시 확인 문의**(통일 카피, 약물명만 다름) |
| 관리 문구(4건 byte-동일) | "칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요." (anti-supplement) |
| 통합 시 변화 | relations 60 → **64**(id 62~65, 런타임 max+1 재계산) · full index/aliases 무변경 |
| 근거 출처 | 전건 식약처 허가사항(nedrug) 라벨의 **칼륨 고갈 방향 직접 동거어**(`칼륨손실`/`저칼륨혈증`/`저칼륨성 알칼리혈증`) |

**왜 depletion/monitoring 인가** — 각 품목 허가사항에 칼륨 고갈 방향 동거어가 직접 있고, 앱은 보충이 아니라 **상태 확인(monitoring)** 만 권한다.
**왜 product_link_allowed=false** — 칼륨 트랙 영구 규칙(CLAUDE.md §1). 칼륨 노출이 보충제 구매 유도로 오인될 위험을 원천 차단.
**왜 potassium_safety_card=true** — 칼륨 관련 카드는 '임의 보충 말고 상담' 안전 고지를 항상 동반해야 함(렌더 게이트).

---

## 1. 후보별 상세 카드

### 1-1. DF01 — 메틸프레드니솔론 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분 / itemSeq | DF01 / 메틸프레드니솔론 / **199800324** |
| 대표 품목 | **메니솔론정4mg**(국내 경구 단일성분 완제) |
| source section | 이상반응(체액ㆍ전해질) |
| source quote(요약) | "체액ㆍ전해질 : 부종, 나트륨저류, **칼륨손실**, 체액저류, **저칼륨성 알칼리혈증**, 감수성 환자에 있어서 울혈성 심부전, 고혈압 등이 나타날 수 있다." — 기전어(칼륨손실)+결과어 동거 |
| 사용자 표시 문구(verbatim) | "메틸프레드니솔론을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| reviewer 질문 | 글루코코르티코이드 class 대표 · 라벨 직접근거 가장 명확. 표시 강도가 적정한가?(계열 유추 아님, 품목 라벨 직접 hit) |

### 1-2. DF04 — 아세타졸아미드 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분 / itemSeq | DF04 / 아세타졸아미드 / **201403403** |
| 대표 품목 | **아세타졸정**(탄산탈수효소억제 이뇨, 국내 유통) |
| source section | 이상반응(대사)·일반적 주의 |
| source quote(요약) | "2) 대사 : 때때로 **저칼륨혈증**, 저나트륨혈증을 포함한 대사성 산증 등의 전해질평형실조, 장기치료로 인한 골연화증, 고혈당/저혈당이 나타날 수 있다." |
| 사용자 표시 문구(verbatim) | "아세타졸아미드을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| ⚠️ reviewer 질문 | **동일 라벨에 금기('저칼륨혈증 환자 투여금지')도 공존** — 추출 포인터를 **이상반응(대사) 섹션**으로 한정했다(금기→depletion 오독 방지). 이 한정이 적절한가? 신호어가 기전어 아닌 **결과어(저칼륨혈증)** 임을 표시에 반영해야 하나? |

### 1-3. DF05 — 아조세미드 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분 / itemSeq | DF05 / 아조세미드 / **199001306** |
| 대표 품목 | **유레틴정**(루프이뇨제, 국내 유통) |
| source section | 부작용(대사)·고령자 주의 |
| source quote(요약) | "3. 부작용 1) 대사 : 때때로 **저칼륨혈증**, 저나트륨혈증, 저염소혈증성 알칼리증 등의 전해질평형실조, 고뇨산혈증, BUN·혈청크레아티닌의 상승, 드물게 고혈당이 나타날 수 있으므로 충분히 관찰하고…" |
| 사용자 표시 문구(verbatim) | "아조세미드을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| reviewer 질문 | 루프이뇨제 — 칼륨 손실은 약리학적으로 잘 알려짐. 표시 강도가 과하지 않은가(상담 라우팅 수준)? |

### 1-4. DF-PRED-01 — 프레드니솔론 × 칼륨

| 필드 | 값 |
|---|---|
| draft_id / 성분 / itemSeq | DF-PRED-01 (candidate D-CORT-01) / 프레드니솔론 / **199602982** |
| 대표 품목 | **소론도정**(국내 경구 단일성분 완제) |
| source section | 사용상의 주의사항 > 이상반응 > 체액ㆍ전해질 |
| source quote(verbatim) | "체액ㆍ전해질 : 부종, 체액저류, 나트륨저류, **칼륨손실**, 감수성환자에 있어서 울혈성 심부전, 혈압상승, **저칼륨성 알칼리혈증** 등이 나타날 수 있다." |
| 사용자 표시 문구(verbatim) | "프레드니솔론을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어, 진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다." |
| 관리 문구 | (통일 anti-supplement 문자열) |
| ⚠️ reviewer 질문 | seeded `ingrName1` 검색이 **메틸프레드니솔론 substring 에 지배돼 1차 누락** → search-depth 개선(deep fallback) 후 자동 포착. DF01 과 동일 라벨 패턴이나 **계열 유추가 아니라 소론도정 품목 라벨 직접 hit**. 프레드니솔론을 DF01 수준 단독 PM-ready 로 인정하는가, 아니면 글루코코르티코이드 class 일괄 검수를 원하는가? |

---

## 2. 검토 범위에서 제외(이 패키지 대상 아님)

> 아래 4종은 **이 통합/검수 패키지의 대상이 아니다**(스크립트 whitelist 밖 — `EXCLUDED={DF02,CQF03,DF03,DF06,DF07}`). 별도 트랙에서 다룬다.

| 항목 | 약물 / 관계 | 제외 사유 |
|---|---|---|
| **DF02** | 덱사메타손 × 칼륨 | **wording-review**: 5건 중 유일하게 직접 칼륨손실 동사 부재('저칼륨성 알칼리혈증' 결과어만) → 추론적 약신호. 문구 강도 별도 검수 |
| **CQF03** | 히드로코르티손 × 칼륨 | **correctness 선결**: ①외용 비중 큰 성분에 전신(경구 래피손정) 근거 일반화 시 외용 사용자 오적용 → 전신 제형 한정 필수 ②source_pointer 섹션 표기('상호작용(병용 신중)')가 부정확 — 실제 인용은 신중투여(④ 전해질이상)+이상반응(7 체액ㆍ전해질). 정정 후 검수 |
| **DF03** | 플루드로코르티손 × 칼륨 | **hold**: 강한 MC 이나 국내 유통 적음(플로리네프정 1품목) — 품목 가용성 재확인 후 |
| **DF06/DF07** | 리오티로닌 × 칼슘/철분 | **비-칼륨**(`product_link_allowed=TRUE`·separation). 같은 factory 파일에 동거하나 칼륨 트랙 아님 — draft_id whitelist 로 동반승격 차단 |

> ⚠️ DF02 와 CQF03 은 **보류 사유가 서로 다르다**(DF02=약신호 / CQF03=제형+섹션). 한 묶음으로 판정하지 말 것.

---

## 3. 검증 절차 (PM/AI 가 통합 전 재현 — reviewer 가 직접 실행 불필요)

```bash
# (1) dry-run — live 무수정, 예상 산출물만 기록(60→64 시뮬)
python3 scripts/integrate_potassium_pm_ready_v1_2.py
# (2) dry-run 산출물 검증(4건 전건·제외 누출검사·anti-supplement·칼륨카드·published/clinical false)
python3 scripts/validate_potassium_dryrun_v1_2.py
# (3) PM-ready 큐 계약 검증(승격 후에도 큐 파일 불변)
python3 scripts/validate_potassium_pm_ready_v1_2.py
# (4) reviewer-note 게이트 회귀(invalid 거부 + valid 통과 + live export sha256 불변)
python3 scripts/test_reviewer_note_gate_v1_3.py
```

- 통합(`--pm-approved --reviewer-note <노트>`)은 **§5 note 가 §4 요건 전건 충족 시에만** 동작한다. 미충족이면 STOP.
- 실제 승격 시 relation-count 하드코딩 validator 들을 **+4(=>64)** 갱신해야 한다(AT-FEX 통합 순서에 따라 baseline 조정).

---

## 4. reviewer note 인터록 요건 (이 패키지의 통과 조건)

`integrate_potassium_pm_ready_v1_2.py` 의 `--reviewer-note` 게이트(`check_reviewer_note`)는 아래를 **전건** 요구한다(미충족 시 STOP):

1. **비공란**(노트 파일 존재 + 내용 있음).
2. **승인 토큰** `approved` 또는 `승인` 포함.
3. **승격 대상 draft_id 4건 전건 명시**: `DF01` · `DF04` · `DF05` · `DF-PRED-01`(하나라도 누락 시 STOP).
4. **SAMPLE/예시 토큰 거부**: `SAMPLE`/`샘플`/`NOT-VALID`/`NOT A REAL APPROVAL`/`NOT_FOR_PROMOTION`/`TEMPLATE-ONLY`/`PLACEHOLDER` 가 있으면 STOP(승인 토큰보다 우선 검사).
5. **미기입 placeholder 거부**: `____`/`YYYY-MM-DD`/`<검수자`/`<reviewer`/`<날짜`/`<date` 가 남아 있으면 STOP.

> 즉 §5 템플릿을 **그대로 제출하면 거부된다.** 실제 승인 시 (a) 예시 토큰 `APPROVED-SAMPLE-NOT-VALID` → `approved`/`승인` 으로 교체, (b) 빈칸을 실제 값으로 채워야 통과한다.

---

## 5. reviewer note 템플릿 (복붙용 — 채워서 돌려주세요)

```text
[MediStack 칼륨 depletion PM-ready — clinical reviewer 승인 노트]

검수자 식별자(익명 ID): ____________
검토일(YYYY-MM-DD): ____________
승인 토큰: APPROVED-SAMPLE-NOT-VALID      ← 실제 승인 시 "approved" 또는 "승인" 으로 교체(SAMPLE 표기 제거)

승인 대상 draft_id (4건 전건 명시 — 누락 시 통합 거부):
  - DF01  메틸프레드니솔론 × 칼륨 (itemSeq 199800324, 메니솔론정4mg)
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

---

## 6. 검수자에게 묻는 질문 (verdict: approved / revise / reject + notes)

1. 이 근거(허가사항 직접 동거어)가 **사용자 참고정보 수준**으로 표시 가능한가?
2. **장기/고용량 조건절**("장기간 복용하거나 고용량으로 사용하는 경우")이 충분히 보수적인가(과확대 아님)?
3. **칼륨 보충 권유 없이** '상담 시 확인 문의' 프레이밍으로 충분한가(anti-supplement 다운그레이드 승인)? (DF01 등 일부 라벨 원문엔 '칼륨보충이 필요할 수 있다'는 시사 문장이 있으나 앱은 의도적으로 anti-supplement 로 다운그레이드함 — 이 다운그레이드를 승인하는가?)
4. 특정 **제형/외용/주사/복합제 오적용** 위험은 없는가(4건 모두 국내 경구 단일성분 완제를 대표로 선정)?
5. 이 항목을 **`verified_reference` 수준**으로 live 에 둘 수 있는가(published/clinical_reviewed=false 천장 유지 하)?

---

## 7. 안전 원칙 (불변)

원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / 칼륨 보충 권유·결핍 단정 금지 /
clinical 검수 전 published 금지 / 검수자는 판정·로그만(데이터 직접 수정 금지) / 승격은 per-row·제한적(일괄 금지) /
reviewer 노트가 와도 **자동으로 `clinical_reviewed=true`·`published=true` 전환하지 않는다**(핸드오프 §4).
"식약처 승인 / 법적 문제 없음 / 약사 검수 완료" 표현 0.
