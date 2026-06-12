# MediStack v0.8 — H-G4 HCTZ 복합제 반영 계획 (실행 전 · PM 승인 대기)

> **상태**: 계획 문서. **이 문서 작성 시점에 alias/data/queue 는 전혀 변경되지 않았다.**
> **H-G4 실제 반영(alias_count 506→618)은 별도 PM 명시 승인 후에만 수행한다.** 자동 진행 금지(자동범위 H-G1~H-G3 종료).
> 선행: 정책 `..._hctz_safety_review.md` · 설계 `..._hctz_combo_design.md` · 게이트로그 `..._hctz_gate_log.md`(H-G1~H-G3 완료).
> 입력: `data/candidates/bulk_alias_approved_ready_combo_v0_8_hctz.json` (112건·combo AR validator 13/13 PASS·incorporated=false).

---

## 1. 반영 대상 / 델타

| 항목 | 현재(반영 전) | 반영 후 | Δ |
|---|---|---|---|
| alias_count (meta) | 506 | **618** | +112 |
| product_aliases | 468 | **580** | +112 |
| ingredient_aliases | 38 | 38 | 0 |
| verified_item_seqs entries | 430 | **542** | +112 |
| verified_item_seqs canonical | 12 | **13** | +1 (**히드로클로로티아지드 키 신규**) |
| queue status | deferred 112 | **approved 112(incorporated=true)** | deferred −112 / approved +112 |
| AR incorporated | false ×112 | **true ×112** | — |
| relations / DATA_URL / data export | 30 / 불변 / 불변 | **불변** | 0 |

- **verified 화이트리스트 필수 근거**: 112 AR itemSeq 는 HCTZ relation 인용 itemSeq(196000008·다이크로짇 단일)와 **0건 겹침** → validator #8(product alias item_seq ∈ 성분 relation itemSeq ∪ 검증 화이트리스트)을 통과하려면 112건을 `verified_item_seqs["히드로클로로티아지드"]` 에 동반 등재해야 함(= v0.7 combo G4 의 product+verified 동반확장 패턴 승계).

---

## 2. 반영 절차 (5개 변경 · ephemeral 스크립트 · 미커밋)

v0.7 G4 패턴 승계: **ephemeral `/tmp/ms_incorporate_hctz.py`(전제/사후 assert 내장, 커밋하지 않음)** 로 수행. 5개 변경:

1. **product_aliases +112**: 각 AR 항목 → `{alias, canonical_ingredient: 히드로클로로티아지드, kind: product, lang: ko, item_seq, source_relation_ids:[19], is_combination:true, combination_basis_ingredient:히드로클로로티아지드, combination_notice_required:true}`.
   - alias 표면형 = AR 의 `item_name`(getItemDetail 원문 품목명). source_relation_ids 는 HCTZ 칼륨 relation id 19(+옵션 20).
2. **verified_item_seqs["히드로클로로티아지드"] 신규 +112**: `{item_seq, item_name, verified_at:2026-06-12, method:nedrug.getItemDetail}`.
3. **meta.alias_count**: 506 → 618.
4. **queue flip**: 해당 112 itemSeq 후보 status deferred→approved, reviewer 설정, incorporated 표시(큐 스키마). **detail_confirmed 미설정 유지**(bulk #19 회피, v0.7 combo 전례).
5. **AR incorporated**: 112 항목 incorporated=true + meta.incorporated=true(옵션 A #10/#11 실반영 검증 대상화).

---

## 3. 전제(pre) / 사후(post) assert — ephemeral 스크립트 내장

**전제(반영 시작 전 반드시 성립):**
- alias_count == 506 · product_aliases == 468 · verified == 430/12 · `히드로클로로티아지드` 키 부재
- 라이브 alias 에 is_combination basis=HCTZ 항목 0건(미반영 상태)
- AR 112건 전부 incorporated=false · combo AR validator 13/13 PASS
- queue: 해당 112 itemSeq status==deferred
- relations 30 · DATA_URL · data export md5 불변

**사후(반영 후 반드시 성립, 하나라도 실패 시 롤백):**
- alias_count == 618 · product == 580 · verified == 542/13(HCTZ 112)
- 신규 112 product alias 전부 is_combination=true·basis=HCTZ·notice=true·**K보존 토큰 0**(#16)·염이름 칼륨 미오인
- queue: 112 deferred→approved(incorporated) · pending/rejected 불변
- AR incorporated=true ×112 · meta.incorporated=true
- **전 validator PASS**: v0.1 12/12·v0.2 15/15·v0.3 **16/16**·bulk 152/152·typeB 7/7·combo 가드 9/9·combo AR 테스트 13/13·**AR(v0.8 HCTZ) #10/#11 옵션A 실반영 13/13**
- relations 30·DATA_URL·data export 불변(md5 0diff)·ingredient_aliases 38 불변
- 금지 불변: 에스오메프라졸/15행 0 · 칼륨보존이뇨제 파트너 0 · 제품/구매/제휴 필드 0 · published/clinical_reviewed 불변

---

## 4. 반영 후 검증/배포 (G4 완료 게이트)

- 위 전 validator + `smoke_hctz_disclosure.py` PASS.
- **라이브 활성화 확인**: 반영 후 HCTZ 복합제(예: "코자플러스") 검색 → HCTZ×칼륨 행 + **칼륨 반전 고지(.combonotice) 표시**(G2 렌더가 실데이터로 처음 활성). 단일 HCTZ("다이크로짇")는 미표시 회귀 확인.
- 커밋(예: "Incorporate v0.8 HCTZ combo aliases (506->618)") → push → Actions(validate→deploy) success → 라이브 HTTP 200 · live alias_count 618.
- 게이트로그 H-G4 섹션 + 필요 시 v0.8 release notes/handoff.

---

## 5. H-G4 실행을 위해 필요한 PM 승인 문구

> **"v0.8 H-G4 반영 승인: HCTZ 복합제 112건을 alias 에 반영(alias_count 506→618, product 468→580, verified +112 신규 히드로클로로티아지드 키, queue 112 deferred→approved+incorporated, AR incorporated=true). 전제/사후 assert 통과 시에만 커밋·deploy."**

- 위 문구(또는 동등 명시 승인) 없이는 **§2 의 어떤 변경도 수행하지 않는다.**
- 승인 시: ephemeral `/tmp/ms_incorporate_hctz.py` 작성 → 전제 assert → 5개 변경 → 사후 assert → 전 validator/smoke → 커밋/push/Actions → 라이브 618 확인.
- 부결 시: H-G1~H-G3 산출물(validator 가드·고지 렌더·AR 후보 풀)만 유지, alias 506 동결.

---

> 본 문서는 계획이며 alias/data/queue 를 변경하지 않았다. STOP — H-G4 실행은 PM 승인 대기.
