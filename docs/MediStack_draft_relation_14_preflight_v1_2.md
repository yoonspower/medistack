# MediStack v1.2 — draft relation 14건 통합 전 재검증(preflight)

작성일 2026-06-14 · 대상 `data/relation_expansion_draft_v1_2.json` (D01–D14)
교차 출처 `data/source_queue_top10_verification_v1_2.csv` · `docs/MediStack_source_queue_top10_verification_v1_2.md`
검증 스크립트 `scripts/integrate_relation_draft_v1_2.py --dry-run` (가드 내장) · `/tmp` recon

## 0. 결론

**14건 전부 `pass_to_integrate`.** 제외 0건. needs_review/reject/hold 후보 혼입 0건.
단 **D12·D14(치아지드유사 × 마그네슘)는 evidence `high`→`moderate` 일관성 조정** 후 통합(아래 §3).

| 판정 | 건수 | draft |
|---|---|---|
| pass_to_integrate | 14 | D01–D14 |
| exclude_needs_review | 0 | — |
| exclude_duplicate | 0 | — |
| exclude_risk | 0 | — |
| exclude_source_missing | 0 | — |

## 1. source_status 재확인 (전건 source_confirmed)

draft 14건은 source queue 6개 source_confirmed 항목에서만 파생 — 재대조 결과 전부 일치.

| queue_id | 테마 | source_status | draft |
|---|---|---|---|
| Q06 | Fluoroquinolone × 아연 | source_confirmed | D01–D04 |
| Q07 | Tetracycline × 아연 | source_confirmed | D05–D06 |
| Q04 | Bisphosphonate × 철/Mg (enrichment) | source_confirmed | D07–D10 |
| Q10 | 클로르탈리돈 × 칼륨/Mg | source_confirmed | D11–D12 |
| Q11 | 인다파미드 × 칼륨/Mg | source_confirmed | D13–D14 |

**정직 제외 확인(draft 미포함이 정답):**
- Q02 오메프라졸 잔여 — source_confirmed지만 relation13(B12)·14(Mg) **이미 라이브** → 신규 relation 아님(인덱스/alias 트랙). 미포함 정상.
- Q03 알렌드론산 Ca/Fe/Mg — **reject**(허가사항 다가양이온 라벨 미기재). 미포함 정상.
- Q08 레보티록신 Mg — **reject**(미기재). 미포함 정상.
- Q01 에스오메(needs_review)·Q05 세팔로 class(needs_review)·Q12–14 스타틴 CoQ10(needs_review)·Q09 메트포르민(hold)·Q15 H2×B12(hold)·Q16 와파린×K(영구금지 hold)·Q17 항암(hold)·Q18 민감군(hold) — 전부 draft 미포함 정상.

각 draft 행: `published=false · clinical_reviewed=false · review_required=true · source_required=true · do_not_implement_yet=true` 확인. 통합 시 draft-전용 필드는 strip(아래 §4).

## 2. 중복/충돌 재확인

- 라이브 relation 41건과 (ingredient, nutrient) 쌍 대조 → **14건 모두 신규 쌍**(중복 0).
  - FQ/테트라 6성분: 기존 칼슘/철/Mg relation 보유, **아연은 신규**.
  - 리세드론산·이반드론산: 기존 칼슘(40/41)만, **철/Mg 신규**.
  - 클로르탈리돈·인다파미드: **성분 자체 신규**(라이브 relation 없음).
- 신규 relation id 43–56 — 기존 1–42(15 제외) 및 excluded id15와 충돌 없음.

## 3. 위험/문구/evidence 재확인

- **고위험군 가드**: 와파린·항응고/항혈소판·항암·임신/소아/정신건강 후보 **0건**(전부 source queue에서 hold/영구금지로 분리, draft에 미유입). 통합 스크립트 `FORBIDDEN_*` 가드로 이중 차단.
- **칼륨 안전정책**: D11·D13(칼륨) `product_link_allowed=false` · `potassium_safety_card=true` 승계 확인(HCTZ relation19 동일 모델). v0.2 validator #11이 강제(칼륨 ⇒ link=false ∧ card=true). D12·D14(Mg)는 칼륨 아님 → 일반 모델.
- **문구 검사**: 전 14건 display_text_ko/management_ko에 "드세요/복용하세요/피하세요/추천/구매/제품" 류 **0건**. 톤 = 기존 라이브 relation과 동일("…함유된 제품을 같은 시간에 복용하면 … 가능성", "…상담하세요"). 참고정보 톤 유지.
- **source 보존**: 각 행 source.url(itemSeq)·pointer·checked_at(2026-06-14) 보존. 통합 시 pointer 끝에 "/ 확인일 2026-06-14" 부착(라이브 관례).

### evidence 일관성 조정 (D12 · D14)

라이브 evidence 선례(mechanism × nutrient):
- `absorption × {칼슘/철/Mg}` → 전부 **high** → D01–D10 "high" 정합(유지).
- `depletion × 칼륨` → 17/19/30 전부 **high** → D11·D13 "high" 정합(유지).
- `depletion × 마그네슘` → 혼재. 그러나 draft가 "**동일 모델**"로 명시한 **HCTZ × Mg(relation 20)은 `moderate`**.

→ **D12(클로르탈리돈×Mg)·D14(인다파미드×Mg)는 draft "high"를 `moderate`로 하향** 후 통합.
근거: ①직접 선례(relation20)와 일치 ②원문보다 강하지 않게(D14 라벨 "드물게 저마그네슘혈증") ③display_text는 이미 동일한 신중 톤이라 사용자 표시 영향 없음(메타데이터 정합만). `EVIDENCE_OVERRIDE`로 적용.

## 4. 통합 영향(예측 = dry-run 실측)

| 지표 | 통합 전 | 통합 후 | 변화 |
|---|---|---|---|
| relations | 41 | 55 | +14 (ids 43–56) |
| relation_card (full index) | 1,072 | 1,077 | +5 |
| name_only (full index) | 16,508 | 16,503 | −5 |
| full index total | 17,580 | 17,580 | 불변 |
| verified_item_seqs | 1,059 / 20성분 | 1,064 / 22성분 | +5 / +2(클로르탈리돈·인다파미드) |
| alias_count | 717 | 717 | 불변 |
| product_aliases | 679 | 679 | 불변 |
| ingredient_aliases | 38 | 38 | 불변 |
| DATA_URL | v0.2 | v0.2 | 불변 |
| published / clinical_reviewed | false / false | false / false | 불변 |

**full index flip = 클로르탈리돈 단일 2 + 인다파미드 단일 3 = 5건만.** FQ/테트라/비스포 8성분은 이미 전건 relation_card(enrichment only, flip 0). 복합제(클로르탈리돈 62·인다파미드 13)는 v1.1 7성분 패턴 승계로 **name_only 유지**(보수적·CANONICAL_13 미등재).

draft → live 변환: `id` 신규 부여 + LIVE_KEEP 10필드 유지 + source 재구성. strip = draft_id/source_queue_id/published/clinical_reviewed/review_required/source_required/do_not_implement_yet/note/source.checked_at.

## 5. 통합 후 검증 대상(§Task 5/12)

CI 게이트 7 + 로컬 smoke. 갱신 필요 상수: full index validator(verified 1064/22·relations 55), potassium validator(name_only 16503·relation_card 1077), search fixture(타리비드/신일모노독시엠캡슐/레보펙신정250·500 3→4·리센플러스정 1→3·name_only_index_size 16503).
