# MediStack — F2 테트라사이클린 인벤토리 & family 재검증 (작업 B/C · v1.4)

> **상태: DRAFT-ONLY — NOT LIVE.** `live_integration_forbidden=true` · `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란.
> survives = 자동 적대검증 + F2 family 재검증 통과를 의미할 뿐 **임상 검수 완료·식약처 승인·법적 문제 없음을 의미하지 않는다.**
> live 승격은 별도 PM + clinical reviewer note + 별도 PR.
> 산출 단일 소스: `data/review/f2_tetracycline_inventory_v1_4.json` (본 문서 = 사람 가독 요약).

## 0. 범위
- family **F2 = Tetracycline계 × 금속 양이온(영양소) / Al·Mg 함유 제산제(약물)**, mechanism=absorption, action=separation.
- 후보 **5건** (`data/drafts/relation_factory_reviewer_ready_batch_v1_4.json` · family==F2 · adversarial_verdict==survives).
- 성분 3종: 독시사이클린 · 미노사이클린 · 테트라사이클린.
- counterpart split: **nutrient 2** (테트라사이클린×철분·아연) + **al_mg_antacid 3** (독시·미노·테트라사이클린 × Al/Mg 함유 제산제(약물)).

## 1. 후보 5건 감사표

| candidate_id | relation | counterpart_type / category | itemSeq | mechanism / action | evidence/confidence/risk | verdict |
|---|---|---|---|---|---|---|
| RF-F2-0105 | 독시사이클린 × Al/Mg 함유 제산제(약물) | drug / `al_mg_antacid` | 198000105 | absorption / separation | moderate / moderate / known_safe | **survives** |
| RF-F2-0110 | 미노사이클린 × Al/Mg 함유 제산제(약물) | drug / `al_mg_antacid` | 198501028 | absorption / separation | moderate / moderate / known_safe | **survives** |
| RF-F2-0111 | 테트라사이클린 × 철분 | nutrient / null | 196000001 | absorption / separation | moderate / moderate / known_safe | **survives** |
| RF-F2-0114 | 테트라사이클린 × 아연 | nutrient / null | 196000001 | absorption / separation | moderate / moderate / known_safe | **survives** |
| RF-F2-0115 | 테트라사이클린 × Al/Mg 함유 제산제(약물) | drug / `al_mg_antacid` | 196000001 | absorption / separation | moderate / moderate / known_safe | **survives** |

- 전건 `product_link_allowed=false` · `potassium_safety_card=false` · `requires_clinical_review=false`.

### 1.1 공통 라벨 문장(허가사항 원문 — verbatim)
5건 모두 **단일 테트라사이클린계 라벨 문장** 근거:

> "칼슘, 마그네슘, 알루미늄을 함유하는 제산제 또는 이들 양이온을 함유하는 다른 약물들, 철ㆍ아연을 함유하고 있는 제제와 약용탄, 카올린, 펙틴 또는 비스무트(bismuth)염 제제에 의해 테트라사이클린계 약물의 흡수가 저하되어 효과가 저하될 수 있다."

- 미노사이클린(RF-F2-0110)은 원문 표기가 **"비스무스(bismuth)"** — 각 품목 라벨 verbatim 차이(철자 변형). hygiene 문제 아님.
- ⚠️ **단일 문장 근거** → reviewer 는 약물별 국내 품목(itemSeq) 매칭 정확성을 확정해야 함(headline reviewer_question).

## 2. 작업 C — F2 family-specific 재검증 (refute-by-default · 12+3 렌즈)
`reverify()` 가 후보별로 적용한 15 렌즈. 결과 **survives 5 · copy_change 0 · needs_review 0 · hold 0 · reject 0** (강등 0).

| 렌즈 | 내용 | F2 적용 결과 |
|---|---|---|
| L1 source_fidelity | itemSeq 실값(≥8자리)+section | pass (실제 국내 품목 매칭은 reviewer Q) |
| L2 direct_cooccurrence | counterpart 직접 언급. **철분→토큰 '철'**(원문 '철ㆍ아연'으로 '철분' 아님 — F1 와의 family 차이) / 아연→'아연' / 제산제→'제산제'+Al·Mg | pass |
| L3 context_discrimination | 철·아연 = standalone '제제'(영양소) vs Al·Mg·Ca = '제산제' 절 구분 | pass |
| L4 antacid_vs_mg_nutrient | Al/Mg 제산제(약물)를 Mg 영양제로 혼동 안 함 | pass |
| L5 nutrient_vs_antacid_ctx | 영양소 후보는 칼슘/마그네슘(제산제 절 전용 cation) 아님 — 철분/아연만 | pass |
| L6 no_pediatric_bone | 소아/임신/골/치아/착색/성장기 문맥 혼입 없음 | pass (라벨 문장에 부재) |
| L7 direction | 흡수 저하/저해/감소·킬레이트 방향 | pass |
| L8 quote_boundary | stray marker·다른 번호목록/문장 끌어옴 없음(단일 종결) | pass |
| L9 no_directive | 복용 명령형(복용하세요/드세요/반드시) 없음 | pass |
| L10 product_supplement | 제품/구매/제휴·보충 권유 문구 없음 | pass |
| L11 no_live_dup | 기존 live 60 **exact** 중복 없음 | pass (아래 §3) |
| L12 no_f1_overlap | F1 퀴놀론(록사신) 성분 혼입/혼동 없음 | pass |
| L13 forbidden_phrase | vfp 금칙어 스캔 | pass |
| L14 consult_tone | '약사 또는 의사와 상담' 참고정보 톤 | pass |
| L15 negation_anticoag | 항응고/비타민K 혼입 없음 | pass |

### 2.1 copy_change
- **0건.** F1(RF-F1-0020 끝 stray '1' 트림)과 달리 F2 라벨 문장은 깨끗(trailing marker·문장 경계 이상 없음).

### 2.2 soft-flag (다운그레이드 아님 · reviewer note)
- **RF-F2-0105/0110 (독시·미노 × 제산제)**: live 에 동일 약물 ×칼슘/철분/마그네슘/아연(영양소)이 **이미 존재** → Al/Mg 제산제(약물) relation 추가가 **정보 가치(제산제 제품 맥락) vs 중복**인지 reviewer 판단(id61 선례). exact dup 은 아니므로 fidelity 강등 아님 — curation 판단(§3, headline question).
- **RF-F2-0110**: 원문 '비스무스' 철자 변형 note(verbatim·hygiene 아님).
- **RF-F2-0115 (테트라 × 제산제)**: 신규 성분·cleanly additive. 참고 — 테트라사이클린은 현재 ×칼슘/×마그네슘 영양소 relation 미보유(독시/미노 대비 완전성 격차) → 차후 확장 후보(본 scope 외).
- **전건**: 공통 라벨 문장 → 약물별 itemSeq 매칭 reviewer 확정.

## 3. live 중복 / overlap (작업 L 요약 · 상세는 dryrun 산출물)
- **exact dup 0.** F2 5건 (ingredient, counterpart) 쌍 전부 live 60 에 없음.
- live 독시사이클린: ×칼슘(id7)·철분(id8)·마그네슘(id9)·아연(id47). live 미노사이클린: ×칼슘(id26)·철분(id27)·마그네슘(id28)·아연(id48).
- **headline reviewer_question**: 독시/미노는 위 4개 영양소 relation 보유 → **Al/Mg 제산제(약물) relation** 추가는 별도 counterpart(`al_mg_antacid`·id61 선례)로 exact dup 아니나, "제산제 제품 맥락" 정보 가치 vs 중복은 reviewer 결정.
- 테트라사이클린은 신규 성분(live 미존재).

## 4. 금지/안전
- 본 인벤토리는 **draft-only**. live relation 추가·export/index/aliases 수정·schedule 활성화·제품/구매/제휴 UI·보충/복용 권유 일절 없음.
- 계열 일반화로 신규 draft 생성 금지(본 5건은 reviewer-ready batch 의 기존 후보만).
