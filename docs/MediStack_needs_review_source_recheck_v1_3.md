# MediStack — needs_review 전해질 source 재확인 (2026-06-15)

작성일: 2026-06-15 · 상태: **분석 산출물 / live 승격 없음 / do_not_implement_yet** · 자기완결

대상: harvester needs_review 의 **다이유레틱·코르티코스테로이드 × 칼륨/Mg/Ca(depletion 방향)** 후보.
목적: 국내 경구 단일성분 정상 완제품 itemSeq 가 실제로 있는지, 라벨에 방향성 직접 동거어가 있는지
**SDK-only** 로 재확인하여 분류를 확정한다. **live relation 추가 0 · export/full index/aliases/src 무수정.**

방법: `medistack_sdk.NedrugClient(online)` + `scripts/verify_factory_sources_v1_2.py` 의
`search_itemseqs`(국내 완제·경구·정상·단일성분 대표 itemSeq 선별) / `fetch_detail`(SDK fetch_label) /
`classify_active`(방향성 detector) 를 **그대로 재사용**. 기존 online 캐시 재사용(결정적, network 0 cache 26)
+ 미캐시 깊은검색은 실 NEDRUG network fetch(프레드니솔론 6페이지·철자변형 11종). SDK 캐시/raw 는
`data/harvest_queue/_sdk/`(gitignored) 에만 기록, 직접 http 신규 호출 0.

---

## 0. 결론 요약

- **새 draft_candidate: 1** — 프레드니솔론×칼륨(D-CORT-01, 소론도정 itemSeq 199602982). draft-only(`live_integration_forbidden=true`, 승격 아님). 아티팩트 `data/review/prednisolone_potassium_draft_recheck_v1_3.json`.
- **needs_review 유지: 1** — 하이드로코르티손×칼륨(D-CORT-05=CQF03, 전신 경구 미확보 + correctness 선결).
- **reject: 9** — 프레드니솔론×칼슘(D-CORT-02) 1건 + **국내 미유통 확정(true negative) 8건**.
- **needs_review → reject 격상: 8건**(미유통 확정으로 '재확인 필요' 부담 제거).
- 비교용 기존 PM-ready 5건(DF01~DF05)은 실 itemSeq+실 라벨로 source_confirmed **재확인**(결정성 검증) — 이번 신규 산출 아님.
- K-sparing/상승방향은 **별도 정책 트랙 메모만**(depletion 혼입 금지) — §4.

> **적대 검증 교정(2026-06-15)**: 커밋 전 refute-by-default 3렌즈 적대 검증을 돌렸고, lens A 가 프레드니솔론 needs_review 분류를 의심했다. 1차 판단(seeded `ingrName1=프레드니솔론` max_pages=2/6 검색 → 수출용+원료만)은 메틸프레드니솔론 substring 에 지배된 **검색 깊이 한계**였다(미유통 아님). max_pages=20(200행) 깊은 검색 p7 에서 **소론도정(199602982)** 확인 → 실 라벨 `d_potassium=True`(칼륨손실·저칼륨성 알칼리혈증). 따라서 D-CORT-01 을 needs_review → **source_confirmed draft** 로 교정. 적대 검증이 거짓음성을 정확히 잡아냈다.
>
> **검색 정책 항구 개선(후속 라운드, 2026-06-15)**: 위 수동 깊은검색을 production 화했다 — `search_itemseqs` 가 **정확 주성분 부재 + substring 지배** 시 `deep_max_pages=20` 까지 deep fallback(exact_only) 을 자동 수행(`reason='ok_deep_exact'`). 이제 봇/재확인이 프레드니솔론을 **자동 포착**한다(수동 개입 불필요). 회귀 테스트 `scripts/test_search_depth_v1_3.py`, 정책 상세 `docs/MediStack_harvester_ops_v1_3.md` §9. theme map 78 스캔: deep fallback 발동 프레드니솔론 1건뿐(나머지 무변경=회귀 0). DF-PRED-01 은 칼륨 PM-ready 통합 준비 그룹에 dry-run 합류(4건, `validate_potassium_dryrun_v1_2.py` PASS·60→64).

---

## 1. 후보별 재확인 결과 (가용성 버킷 + 분류)

| candidate | relation | 가용성 버킷 | 검색/라벨 결과 | 분류 |
|---|---|---|---|---|
| D-CORT-01 | 프레드니솔론 × 칼륨 | **국내 경구 단일성분 확인** | max_pages=20 깊은검색 p7 = **소론도정(199602982)** 단일·경구·완제·정상. 라벨 `d_potassium=True`(칼륨손실·저칼륨성 알칼리혈증) | **draft(source_confirmed, high)** — DF-PRED-01, draft-only |
| D-CORT-02 | 프레드니솔론 × 칼슘 | 동 품목(소론도정) | 라벨 칼슘 흡수 방향 동거어 없음(`d_calcium_absorption=False`) | **reject**(label_missing) |
| D-CORT-05 | 하이드로코르티손 × 칼륨 | **외용/비경구 위주** | 정확 단일성분 0건, 크림/연고/로션 위주 — 전신 경구 단일 완제 미확보 | **needs_review 유지**(=CQF03 correctness 선결) |
| D-LOOP-01 | 부메타니드 × 칼륨 | **true negative(미유통)** | searchDrug **0건**(+변형 부메타나이드 0) | **reject**(not_marketed_kr) |
| D-LOOP-02 | 부메타니드 × 마그네슘 | true negative(미유통) | 동상 | **reject**(not_marketed_kr) |
| D-LOOP-03 | 피레타니드 × 칼륨 | true negative(미유통) | searchDrug **0건**(+변형 피레타나이드 0) | **reject**(not_marketed_kr) |
| D-THZ-01 | 메토라존 × 칼륨 | true negative(미유통) | searchDrug **0건**(변형 메톨라존 1행=경구단일 부적격) | **reject**(not_marketed_kr) |
| D-THZ-02 | 메토라존 × 마그네슘 | true negative(미유통) | 동상 | **reject**(not_marketed_kr) |
| D-THZ-03 | 트리클로르메티아지드 × 칼륨 | true negative(미유통) | searchDrug **0건**(+변형 3종 0) | **reject**(not_marketed_kr) |
| D-THZ-04 | 트리클로르메티아지드 × 마그네슘 | true negative(미유통) | 동상 | **reject**(not_marketed_kr) |
| D-THZ-05 | 벤드로플루메티아지드 × 칼륨 | true negative(미유통) | searchDrug **0건**(+변형 3종 0) | **reject**(not_marketed_kr) |

**가용성 버킷 집계**: domestic_single_oral_found **1성분(프레드니솔론=소론도정 199602982)** · shallow-search 한계로 1차 누락됐던 건(프레드니솔론, 깊은검색으로 해소) ·
topical_or_nonoral_only **1성분(하이드로코르티손, D-CORT-05)** · true_negative(미유통) **5성분 8후보** · needs_further_check **1(하이드로코르티손 전신 경구 유통 + CQF03 correctness)**.

**분류 집계**: draft_candidate **1**(DF-PRED-01) · needs_review **1**(D-CORT-05) · reject **9** · hold_new **0**.

---

## 2. 미유통 true negative 확정 (needs_review → reject 격상)

`searchDrug?ingrName1=<성분>` 가 **"총 0건 / 없습니다"** 무결과 페이지를 반환 = NEDRUG 색인에 해당 성분 품목 없음.
철자 변형까지 0건이면 국내 미유통으로 확정한다(전해질 고갈 방향이라도 **한국 허가사항이 없으면 근거 불가**).

- 부메타니드 / 부메타나이드 — 0
- 피레타니드 / 피레타나이드 — 0
- 메토라존 / 메톨라존(1행, 경구단일 부적격) — 0
- 트리클로르메티아지드 / 트리클로르메치아짓 / 트리클로르메치아지드 / 트리클로메티아지드 — 0
- 벤드로플루메티아지드 / 벤드로플루메치아짓 / 벤드로플루메치아지드 / 벤즈플루아짓 — 0

→ **D-LOOP-01·02·03, D-THZ-01·02·03·04·05 (8건)** 을 needs_review(ambiguous '재확인 필요')에서 **reject(not_marketed_kr)** 로 격상.
live 결과는 동일(영구 제외)이나 backlog 의 재확인 부담을 제거한다. **계열 일반화로 채택 금지** 원칙 유지(푸로세미드 id17·HCTZ id19 등 기존 라이브와 무관하게 품목 직접 라벨이 없으면 불가).

---

## 3. draft 승격 1건 (draft-only) + needs_review 유지 1건

- **D-CORT-01 프레드니솔론 × 칼륨 → draft(DF-PRED-01)** — 국내 경구 단일성분 정상 완제 **소론도정(199602982)** 확인, 라벨 이상반응>체액·전해질에 "칼륨손실, 저칼륨성 알칼리혈증" 직접 동거어 + depletion 방향. 글루코코르티코이드 class(DF01/DF02/DF03 동일 패턴)이나 **계열 유추가 아니라 품목 라벨 직접 hit**. draft-only(`live_integration_forbidden=true`, potassium_safety_card=true, product_link_allowed=false, 통일 anti-supplement 문구). live 통합은 PM 승인 + clinical reviewer 노트 후 별도(DF 통합 화이트리스트 미포함). 아티팩트 `data/review/prednisolone_potassium_draft_recheck_v1_3.json` + validator `scripts/validate_prednisolone_draft_recheck_v1_3.py`.
- **D-CORT-05 하이드로코르티손 × 칼륨 (=CQF03) → needs_review 유지** — 국내 하이드로코르티손은 외용(크림/연고/로션) 위주, 전신 경구 단일성분 완제 미확보(max_pages=20 깊은검색에도 미확인). 기존 CQF03 는 correctness 선결(전신 제형 한정 + source_pointer 섹션 정정) 미해결 상태로 wording-review. 유지.

---

## 4. K-sparing / 상승방향 — 별도 정책 트랙 메모 (depletion 혼입 금지)

아래는 **칼륨/전해질 상승(또는 방향 반대)** 후보로, depletion factory 와 **정반대 방향**이다.
**절대 depletion 카드로 만들지 말 것.** 별도 "칼륨 상승/병용 주의" 정책 트랙 신설 여부는 PM 판단(현재 hold 유지). 제품/보충/치료 문구 금지.

- H-KSPAR-01 스피로노락톤 × 칼륨(rise) · H-KSPAR-02 에플레레논(rise) · H-KSPAR-03 아밀로라이드(rise·주로 복합제) · H-KSPAR-04 트리암테렌(rise)
- H-WARN-01 스피로노락톤(+ACEi/ARB) × 칼륨(rise·약-약 상호작용)
- D-SGLT2-01 다파글리플로진 × Mg · D-SGLT2-02 엠파글리플로진 × Mg (direction_uncertain·혈청 Mg 상승 보고 우세)
- D-THZ-06 히드로클로로티아지드 × 칼슘(retention·고칼슘 방향 — 치아지드는 칼슘 배설 감소)

---

## 5. 안전/불변 확인

- **live relation 추가 0** · relations 60 유지 · published/clinical_reviewed=false · reviewed_by 공란.
- export/full index/aliases/src/.github/validator **무수정**(읽기전용 + SDK fetch). SDK 캐시/raw 는 `data/harvest_queue/_sdk/`(gitignored).
- 칼륨 행 정책 불변: product_link_allowed=false · potassium_safety_card=true · **칼륨 보충 권유 0 · 결핍 단정 0**.
- Mg 후보는 영양제 relation 오인 금지(D-LOOP-02/05·D-THZ-02/04 전부 reject — 라벨 동거어 없음/미유통).
- 제품/구매/제휴 UI 0 · "식약처 승인/법적 문제 없음/약사 검수 완료" 표현 0.

---

## 6. 다음 PM 판단사항

1. **프레드니솔론×칼륨(DF-PRED-01)**: draft-only 확보 완료(소론도정 199602982·source_confirmed·high). live 통합은 **PM 승인 + clinical reviewer 노트** 후 별도 — DF01·DF04·DF05 칼륨 통합 라운드에 합류시킬지(통합 화이트리스트에 DF-PRED-01 추가) PM 판단. class 4종(프레드니솔론·메틸프레드니솔론·덱사메타손·플루드로코르티손) 묶음 가능.
2. **하이드로코르티손×칼륨(CQF03)**: 전신 경구 하이드로코르티손 국내 유통 확인 + correctness(전신 제형 한정·섹션 정정) 선결.
3. **미유통 8건**: reject(not_marketed_kr) 확정 — 재후보화는 국내 시판 시에만. 봇 시드에서 정리(harvest 잡음 감소) 여부 검토.
4. **search 깊이 정책**: production `search_itemseqs` max_pages=2 가 동명-substring(메틸프레드니솔론) 지배 성분에서 깊은 페이지의 단일품을 놓칠 수 있음 — exclude_ingr 적용 성분은 max_pages 상향 또는 exact-ingr 우선 정렬 검토(이번에 프레드니솔론에서 노출된 한계).
5. **K-sparing 별도 정책 트랙**: '칼륨 상승/병용 주의' 카드 트랙 신설 여부(현재 hold).

근거 데이터: `data/review/needs_review_source_recheck_v1_3.json` · `scripts/verify_factory_sources_v1_2.py` · `scripts/harvest_relation_bot_v1_3.py` · SDK 캐시 `data/harvest_queue/_sdk/cache/online/`.
