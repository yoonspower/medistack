# MediStack — relation factory 대량 source check + draft batch 보고 (v1.2+)

> 작성일: 2026-06-14. **데이터/코드/렌더/DATA_URL/validator(기존) 무변경.** 본 라운드는 factory 후보 75건의 **대량 source check + 적대적 검증 + draft batch 생성 + 검증 자동화 강화**까지만 수행했고 **라이브 relation 통합은 0**이다(relations **55 그대로**).
>
> 선행/연계(자기완결 인계): `CLAUDE.md` · `MediStack_relation_factory_design_v1_2.md` · `MediStack_relation_factory_candidates_v1_2.md` · `MediStack_source_queue_top10_verification_v1_2.md` · `MediStack_v1_2_release_readiness.md`.
>
> **정체성(불변):** MediStack 은 식약처 허가사항 기반 약-영양소 **참고정보 베타**. 진단·처방·복약지시·영양제 추천·구매 동선 아님. published / clinical_reviewed = **false 봉인 유지**.

---

## 0. 한 줄 요약

factory 후보 **75건 전건 1차 스캔 → source-checkable 33건 nedrug 허가사항 fetch 검증 → 적대적 검증(독립 agent 라벨 재fetch·4렌즈 반증)**. 결과 **source_confirmed 7 · reject 15 · needs_review 11 · hold 42.** confirmed 7건만 **draft batch(DF01–DF07)** 로 생성(라이브 미반영·`live_integration_forbidden=true`). **어떤 라이브 데이터도 변경하지 않았다**(relations 55 · relation_card 1,077 · alias 717 · DATA_URL v0.2 · published/clinical false 전부 불변).

> 🎯 **우선순위 지시 반영(PM, 2026-06-14):** 유료화/결제/구독/프리미엄은 **전면 보류**. 최우선 = **relation coverage 확장**(목표 relation ≥1,000 · relation_card ≥10,000 · 검색 UX 안정화 전까지 유료화 구현 금지). 본 라운드는 그 목표를 위한 **factory → source check → draft → live 승격 파이프라인 강화**에 집중했다(§7).

---

## 1. 처리 결과 (75건)

| 분류 | 수 | 의미 | 다음 |
|---|---|---|---|
| **source_confirmed** | **7** | 허가사항 동거어 + **적대적 검증 4렌즈 통과** | draft batch(DF01–DF07) → PM 승인 시 live 승격 후보 |
| **reject** | **15** | 허가사항 미기재 / 방향 불일치 / 과다해석 | 채택 금지(literature 또는 근거 어긋남) |
| **needs_review** | **11** | 국내 단일 경구 완제품목 미확보(검색 0건) | 차기 batch에서 itemSeq 직접 지정·재확인 |
| **hold** | **42** | 고위험·범위밖·방향반대·미기재확정·저인덱스·index트랙 | 검토만(승격 금지) |

산출 CSV: `data/relation_factory_source_check_v1_2.csv`(75행, 사용자 요구 필드 + 적대적 verdict 컬럼).

### 1.1 source_confirmed 7건 (→ draft DF01–DF07)

| draft | 후보 | 관계 | 기전 | 칼륨카드 | 근거(허가사항) |
|---|---|---|---|---|---|
| DF01 | D-CORT-03 | 메틸프레드니솔론 × 칼륨 | depletion/monitoring | ✅ | 이상반응 "칼륨손실, 저칼륨성 알칼리혈증"(메니솔론정 199800324 등 3품목) |
| DF02 | D-CORT-04 | 덱사메타손 × 칼륨 | depletion/monitoring | ✅ | 이상반응 "저칼륨성 알칼리혈증"(덱사하이정 202203949 등 3품목) |
| DF03 | D-CORT-06 | 플루드로코르티손 × 칼륨 | depletion/monitoring | ✅ | 이상반응 "칼륨소실, 저칼륨성 알칼리혈증"(플로리네프정 199907231) |
| DF04 | D-CA-01 | 아세타졸아미드 × 칼륨 | depletion/monitoring | ✅ | 이상반응(대사) "때때로 저칼륨혈증…전해질평형실조"(아세타졸정 201403403) |
| DF05 | D-LOOP-04 | 아조세미드 × 칼륨 | depletion/monitoring | ✅ | 부작용(대사) "때때로 저칼륨혈증…"(유레틴정 199001306) |
| DF06 | D-THY-02 | 리오티로닌 × 칼슘 | absorption/separation | — | 상호작용 "탄산칼슘…병용투여시 이 약의 흡수가 지연 또는 감소"(테트로닌정 201503196) |
| DF07 | D-THY-03 | 리오티로닌 × 철분 | absorption/separation | — | 상호작용 "철분제제…병용투여시 이 약의 흡수가 지연 또는 감소"(테트로닌정 201503196) |

- **칼륨 행 5건** 전부 `product_link_allowed=false`·`potassium_safety_card=true`(HCTZ id19 / 클로르탈리돈·인다파미드 D11/D13 동일 안전정책 승계).
- evidence_level 전건 high(이상반응/상호작용 직접 listing 확인). 스테로이드 칼륨은 **장기/고용량 맥락** → 참고정보 톤("상태 확인이 필요할 수 있습니다")·monitoring 으로 한정(복용지시 아님).
- **적대적 검증이 잡은 강화**: D-CA-01·D-LOOP-04 는 스크립트가 처음 **금기(저칼륨혈증 환자 투여금지)** 신호로 잡았으나, agent 가 라벨 재fetch 해 별도 **이상반응 listing**(약 자체가 저칼륨혈증 유발)을 찾아 confirm 으로 강화. 리오티로닌은 itemSeq 201503196 이 **레보티록신 복합이 아니라 리오티로닌나트륨 단일제**(테트로닌정)임을 확인.

### 1.2 reject 15건 (채택 금지)

- **세팔로스포린 × 철분 10종**(F-CEPH-01~10): 허가사항 상호작용란에 철분 동거어 없음. 세프디니르(id42)의 적색 비흡수복합은 **성분특이** — 계열 일반화 근거 없음. 직접 라벨 미기재 → reject.
- **D-CORT-07 메틸프레드니솔론 × 칼슘**: 골대사 문맥(골다공증)만, 칼슘 흡수 직접 문구 없음 → 과다해석 방지 reject.
- **D-LOOP-05 아조세미드 × 마그네슘**: 라벨에 저칼륨은 있으나 저마그네슘 동거어 없음 → reject(칼륨만 confirmed).
- **D-THY-01 레보티록신 × 아연 / F-FQ-02 레보티록신 × 마그네슘**: 허가사항 미기재(Q08 Mg reject 전례 재확인). 아연도 동거어 없음 → reject.
- **F-FQ-01 목시플록사신 × 칼슘 🔴(적대적 검증이 뒤집음)**: 스크립트는 "칼슘 보충제…흡수율 감소"로 confirmed 판정했으나, agent 가 전체 문장을 읽어 **"흡수 정도(extent)는 영향을 받지 않았다 · 임상적으로 관련성이 없는 것으로 보인다"** 를 확인 → 흡수저하 주장 성립 안 함 → **reject 강등.** (regex 단독의 한계를 적대적 검증이 보정한 대표 사례.)

### 1.3 needs_review 11건 (국내 단일 경구 완제품목 미확보)

프레드니솔론·하이드로코르티손·부메타니드·피레타니드·메토라존·트리클로르메티아지드·벤드로플루메티아지드(칼륨/마그네슘). nedrug `searchDrug` 에서 **국내 완제·경구·정상·단일성분 대표 품목**을 못 찾음(원료/복합/수출/취하만, 또는 0건). 일부는 표기 불일치(메**톨**라존·부메타**나이드**)로 검색 자체가 0건이었고, 재탐색에서도 **국내 유통 단일 경구 정제 부재**가 확인됨(예: 메톨라존=원료만, 프레드니솔론=단일 경구정 6페이지 0건). → 진짜 부재 가능성이 높아 **억지 통과 대신 needs_review 보존**. 차기 batch에서 ①itemSeq 직접 지정 ②복합제 처리 방침(단일 relation 범위 밖) 결정.

### 1.4 hold 42건 (검토만 — 승격 금지)

| 카테고리 | 수 | 후보 |
|---|---|---|
| high_risk(항응고/항혈소판/항암/정신건강/여성·소아) | 18 | F-WAR·F-DOAC×4·F-APL×3·F-ONC×3·F-SSRI×2·F-BZD×2·F-AP·F-OC·F-PED |
| literature_only(스타틴×CoQ10) | 5 | F-STA-01~05 |
| wrong_direction_high_risk(칼륨보존이뇨제 상승방향) | 4 | H-KSPAR-01~04 |
| label_missing_confirmed(H2×B12) | 3 | F-H2-01~03 |
| out_of_scope(허브-약물) | 3 | F-HERB-01~03 |
| low_index(일라프라졸·테트라사이클린 원성분) | 3 | F-PPI-01·02·F-TET-01 |
| direction_uncertain(SGLT2×Mg 상승 우세) | 2 | D-SGLT2-01·02 |
| wrong_direction(치아지드×칼슘 retention) | 1 | D-THZ-06 |
| drug_drug_out_of_scope(KSPAR+RAAS) | 1 | H-WARN-01 |
| not_marketed_kr(부포르민) | 1 | D-BIG-01 |
| relation_exists(세프디니르 index트랙) | 1 | F-CEPH-IDX-01 |

- **항응고/항혈소판 × 비타민K = high_risk hold 유지**(CLAUDE.md 영구 금지·임상판단). source 확인조차 하지 않음.
- **칼륨 관련 standalone 제품/추천 연결 금지 유지** — 칼륨보존이뇨제(상승방향)도 hold, 칼륨 confirmed 행도 `product_link_allowed=false`.

---

## 2. 방법론 (재현 가능 — 커버리지 스케일링 자산)

source 확인을 **2단 게이트**로 자동화했다. 향후 batch도 동일 파이프라인으로 확장한다(relation 1,000 목표의 반복 엔진).

1. **결정론적 source check** — `scripts/verify_factory_sources_v1_2.py`
   - 성분명 → nedrug `searchDrug` 로 **국내 완제·경구·정상·단일성분 대표 itemSeq** 해결.
   - `getItemDetail` HTML fetch → 태그제거·정규화 → **영양소 동거어 detector**(첨가제/조성 배제, **방향성 가드**: depletion 후보는 저칼륨/저마그네슘 고갈 방향 신호 필수).
   - 분류: source_confirmed / reject / needs_review / hold. 산출 = `data/relation_factory_source_check_v1_2.csv`.
2. **적대적 검증** — `scripts/factory-source-adversarial-verify`(워크플로우, 독립 agent 8)
   - confirmed 후보별 agent가 **같은 itemSeq 라벨을 독립 재fetch** 후 4렌즈 반증: ①첨가제 아님(상호작용/이상반응 문맥) ②방향 정확(고갈/흡수저하, "흡수 정도 영향 없음"이면 reject) ③**국내 단일 경구 완제품목 실재**(복합/수출/원료 아님) ④계열 과확장 아님(해당 성분 자체 라벨).
   - 불확실하면 **refute 기본**. 산출 = `data/relation_factory_adversarial_verify_v1_2.json`(verdict 전건 audit).
   - 결과: 8 confirmed 중 **7 생존 · 1 반증**(F-FQ-01).

> 진실원은 **허가사항 원문 + 결정론적 detector**, 안전 게이트는 **적대적 재fetch**. LLM 추정이 아니라 라벨 인용이 근거다.

---

## 3. 생성 산출물 (전부 신규 파일 · 라이브 무변경)

| 파일 | 내용 |
|---|---|
| `scripts/verify_factory_sources_v1_2.py` | 대량 source check 엔진(searchDrug→getItemDetail→detector→분류) |
| `data/relation_factory_source_check_v1_2.csv` | 75건 verdict + evidence + 적대적 verdict 컬럼 |
| `data/relation_factory_adversarial_verify_v1_2.json` | 적대적 검증 8건 verdict audit |
| `scripts/build_factory_draft_batch_v1_2.py` | confirmed→draft batch 생성기 |
| `data/relation_factory_draft_batch_v1_2.json` | draft DF01–DF07(라이브 미반영·`live_integration_forbidden=true`) |
| `data/relation_factory_draft_batch_preflight_v1_2.csv` | 승격 전 점검표 |
| `scripts/validate_forbidden_phrases_v1_2.py` | 금지어/위험문구 스캐너(재사용 게이트) |
| `scripts/validate_factory_draft_batch_v1_2.py` | draft batch 정합·안전 검증기 |
| `scripts/smoke_factory_draft_batch_v1_2.py` | draft batch render 안전성 사전검증(실제 render.js) |

---

## 4. 검증 결과 (전수 PASS · 라이브 무변경)

- **신규 게이트**: 금지어 스캐너 PASS(사용자 노출 카피 159문자열 위반 0) · draft batch validator PASS(130/130) · factory draft smoke PASS(7건 render-safe).
- **기존 CI·smoke 회귀**: v0.1·v0.2 export validator · v0.3 alias · alias surface forms · full drug name index · potassium name-only(+selftest) · relation draft v1.2 validator · 라이브 relation draft smoke · disclaimer/alias/hctz/search-regression smoke · unit(combo_ar·v0_3_combo·v0_3_typeB) **전부 PASS**.
- **라이브 데이터 무변경**: `git diff --stat` 빈 결과(tracked 0). 변경은 전부 **신규 untracked 파일**. relations 55 / relation_card 1,077 / name_only 16,503 / total 17,580 / alias 717 / verified 1,064/22 / DATA_URL v0.2 / published·clinical false **전부 불변**.
- **위험문구·제품 UI 0**: 카피 금지어 0, 외부링크=nedrug 출처만, 제품/구매/제휴 UI 0.

---

## 5. 금지선 준수 (본 라운드)

- ✅ **live relation 통합 0**(relations 55 그대로) · export/full index/alias 실데이터 변경 0 · DATA_URL v0.2 유지.
- ✅ published / clinical_reviewed **false 유지** · src 앱 기능 변경 0(validator/smoke/script/docs만 추가).
- ✅ source_confirmed 없는 후보 draft/live 승격 0 · **high_risk hold draft/live 혼입 0**(검증기 강제).
- ✅ 항응고/항혈소판×비타민K hold 유지 · 칼륨 standalone 제품/추천 연결 0 · 칼륨 confirmed 행 `link=false`·`card=true`.
- ✅ "식약처 승인 / 법적 문제없음 / 약사 검수 완료 / 추천 영양제 / 복용하세요 / 치료 / 예방 / 구매 / 제휴" 어휘 0(스캐너 PASS).

---

## 6. PM 판단 필요사항 (다음 단계 게이트)

1. **draft batch DF01–DF07 live 승격 여부**(7건). 승격 시 relations 55→62, relation_card 일부 flip(아세타졸아미드·아조세미드·리오티로닌 등 단일 품목). 칼륨 5행 안전정책 승계.
   - 참고: 스테로이드×칼륨(DF01–03)은 **장기/고용량 맥락 부작용** — 참고정보 톤이라 베타 적합하나, clinical reviewer 트랙에서 용량 맥락 문구 재확인 권장.
2. **needs_review 11건 처리 방침**: 국내 단일 경구 완제품목 미확보. (a) itemSeq 직접 지정 재검증 (b) 복합제는 단일 relation 범위 밖 — 별도 트랙 여부.
3. **source-policy 결정**: literature_only hold(스타틴×CoQ10 5건 = name_only 472+267+… 최대 커버리지 레버 · H2×B12 3건)에 **이차문헌 허용 여부**. 허용 시 coverage 대폭 확장 가능하나 "허가사항 기반" 정체성 변경 — 별도 정책 결정.
4. **칼륨보존이뇨제(H-KSPAR) 상승방향 후보**: depletion factory 범위 밖. 별도 "주의(병용금기)" 트랙 신설 여부.

---

## 7. 커버리지 우선 로드맵 (유료화 보류 반영)

현재 relation **55** / relation_card **1,077**. 목표 relation **≥1,000** / relation_card **≥10,000**. 격차가 크므로 **factory → source check → draft → 승격** 파이프라인의 **반복 처리량**이 관건이다.

1. 본 batch(7) 승격 + needs_review 11 itemSeq 보강 → 차기 batch 후보군 확대.
2. factory 후보 재생성(`harvest_relation_candidates.py`)으로 신규 성분군 발굴(이뇨제 복합·추가 항생제·골다공증제 등 라벨 명시 동거어 풍부 영역 우선).
3. source-policy 결정 시 literature_only 레버 해금(스타틴×CoQ10 등) — coverage 최대 영향.
4. 검색 UX 안정화(name_only 16,503 → relation_card 전환 비율 제고)와 병행.
5. **유료화/결제/구독/saved_stack/Supabase = 커버리지·UX 목표 달성 전까지 보류**(설계 문서만 유지, 구현 0).

---

## 8. 다음 Claude Code 프롬프트 (2개)

### 프롬프트 1 — draft batch 일부/전체 live 승격 (PM 승인 후)

```
메디스택 relation factory draft batch(DF01–DF07)를 live 승격한다.

현재: relations 55, HEAD=<현재 main>, draft=data/relation_factory_draft_batch_v1_2.json (live_integration_forbidden=true).
선행 필독: docs/MediStack_relation_factory_source_check_v1_2.md, CLAUDE.md, MediStack_draft_relation_14_preflight_v1_2.md(승격 패턴).

작업:
1. PM 승인 범위 확정(7건 전부 vs 칼륨 5건만 vs T3 2건만). 승인되지 않은 행은 승격 금지.
2. integrate_relation_draft_v1_2.py 패턴 승계한 멱등 통합기 작성:
   - 신규 relation id = 57부터 순차(라이브 id 공간), draft 전용 필드(draft_id/source_*/published/clinical_reviewed/
     do_not_implement_yet/live_integration_forbidden/note 등) 미누출.
   - 칼륨 행 product_link_allowed=false·potassium_safety_card=true 승계, evidence_level 일관성.
   - 단일 품목(아세타졸아미드/아조세미드/리오티로닌 등) full index flip(relation_card)·verified_item_seqs 키 추가, 복합제 name_only 유지.
3. meta.relation_count 갱신, published/clinical_reviewed false 유지, DATA_URL v0.2 유지.
4. 통합 후 validator(v0.2 export·relation draft·factory draft·금지어)·smoke 전수 + 신규 통합 검증기 + CI 세트 로컬 선실행. 전부 PASS 아니면 commit 금지.
5. live HTTP 200, git clean 확인 후 commit/push/deploy.

금지: 미승인 행 승격, high_risk/needs_review 혼입, 칼륨 product link, published/clinical 전환, src 기능 변경.
```

### 프롬프트 2 — 커버리지 확장: 차기 factory batch + source check 스케일업

```
메디스택 relation coverage 확장: 차기 factory batch source check.

목표: relation ≥1,000 / relation_card ≥10,000 향한 다음 후보군 처리. 유료화/saved_stack/Supabase는 보류(구현 금지).
선행 필독: docs/MediStack_relation_factory_source_check_v1_2.md(§7 로드맵), CLAUDE.md.

작업:
1. needs_review 11건(프레드니솔론·하이드로코르티손·부메타니드·피레타니드·메토라존·트리클로르메티아지드·벤드로플루메티아지드)
   itemSeq 직접 지정으로 재검증 — 국내 단일 경구 완제품목 실재 여부 확정(없으면 hold 전환).
2. harvest_relation_candidates.py로 신규 성분군 후보 재생성(라벨 동거어 풍부 영역: 추가 이뇨제·골다공증제·항생제·제산제 등).
   source_status 기본값 needs_source, do_not_implement_yet=true, 고위험 hold 분류만.
3. verify_factory_sources_v1_2.py 확장(신규 후보 + 성분명 alias 매핑으로 검색 false-negative 감소) → 적대적 검증 워크플로우 재실행.
4. confirmed만 build_factory_draft_batch로 차기 draft batch 생성(라이브 미반영). validator/smoke 전수 PASS.
5. 라이브 데이터 무변경 git diff 확인 후 commit/push.

금지: live 통합(별도 승인), source_confirmed 없는 승격, high_risk hold 승격, 유료화/결제/saved_stack/Supabase 구현.
```

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / source_confirmed 없으면 draft·live 승격 금지 / high_risk hold 승격 금지 / live relation 통합은 PM 승인 별도 단계 / 유료화·결제·saved_stack·Supabase는 coverage·UX 목표 달성 전 구현 보류.
