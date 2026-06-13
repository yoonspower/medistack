# MediStack v1.2 — 계획 / 마일스톤 정의

> 작성일: 2026-06-14. **계획 문서 전용 — 데이터/코드/인덱스/DATA_URL 무변경.** 본 문서는 v1.2 마일스톤의 목표·산출물·성공기준·위험을 정의한다. 실제 데이터/렌더 변경은 각 항목별 별도 PM 승인 라운드에서만 수행한다.
> 선행(자기완결 인계): `CLAUDE.md` · `MediStack_v1.1_handoff.md` · `MediStack_v1.1_plan.md` · `MediStack_ppi_calcium_combo_reclassification_v1_1.md` · `MediStack_relation_card_coverage_analysis.md` · `MediStack_popular_drug_coverage_match.md` · `MediStack_monetization_strategy_v1_1.md` · `MediStack_next_relation_source_check_queue.md` · `MediStack_source_attribution_design.md` · 법적 게이트 `MediStack_public_release_legal_safety_checklist.md`.

---

## 0. 정체성 (불변 전제)

MediStack 은 **식약처 허가사항 기반 약-영양소 참고정보 베타**다. 진단·처방·복약지시·영양제 추천·구매 동선이 아니다. v1.2 의 모든 항목은 이 정체성과 **충돌하지 않는 범위에서만** 진행하며, 정보 신뢰성·면책 톤·published/clinical_reviewed=false 봉인을 깨지 않는다.

---

## 1. 현재 기준선 (이번 세션 종료 시점)

| 항목 | 값 |
|---|---|
| relations (v0.2 export) | **41** (+ excluded_v0_1 1) |
| relation_card | **1,072** |
| name_only | **16,508** |
| full drug name index total | **17,580** (불변) |
| product_aliases | 679 |
| alias_count (meta) | **717** |
| verified_item_seqs | 1,059 entries / **20 canonical** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| published / clinical_reviewed | **false / false** (봉인 · 천장 = verified_reference) |
| live | `https://yoonspower.github.io/medistack` (HTTP 200) |

> v1.1-beta(full index 17,580 · relation 30) 이후, A/B/D 복합제 배너 통합 + A티어 source 확인 11건(ids 32–42) 라이브 통합 + C(PPI+침강탄산칼슘 18건) buffer_combo 재분류·flip 까지 반영된 상태다. relation 은 30 → **41**, relation_card 는 558 → **1,072** 로 증가했다. (예전 문서의 "relation 30 고정"은 v1.1 시점 값이며, v1.2 기준선은 41이다.)

---

## 2. v1.2 목표 (우선순위 순)

> 우선순위: ①C buffer_combo 최종화(거의 완료) → ②source queue Top10 확인 → ③내 약 목록 저장 MVP 설계 → ④Free/Plus 기능 분리 → ⑤relation source 표시 UI 설계 → ⑥영양제 앱 분리 기획. 나머지(coverage 확장·인기약 gap·name_only UX·법적 링크 정리)는 동반 트랙.

---

### 목표 1 (1순위·동반) — relation_card coverage 확장

- **목표**: source-confirmed relation 만 추가해 relation_card 커버리지(현재 1,072 / full index 17,580 = 6.1%)를 신뢰선 안에서 점진 확장한다. 무리한 풀 확장이 아니라 "허가사항 출처가 확인된 후보만" 승격.
- **왜**: name_only 비율이 여전히 ~94%(16,508/17,580)라 임의 검색의 정보 표시 확률이 낮다. 사용자 체감 가치 향상의 핵심 레버. 단, 확장은 **출처 게이트** 안에서만 안전하다(과장·오도 리스크).
- **산출물**: 확장 후보별 source 확인 로그(`verify_atier_relation_sources.py` 패턴) + 통합 시 데이터-only 배치(A/B/D·A티어 통합기 패턴 승계) + 갱신 coverage 스냅샷(`analyze_relation_card_coverage.py` 재실행 CSV). 문서: 본 항목 진행 로그.
- **성공기준(검증가능)**: (a) 신규 relation 은 전부 `source.type=허가사항` + url + pointer(확인일) 보유. (b) 통합 후 `validate_medistack_v0_2_export` / `validate_full_drug_name_index` / `validate_potassium_name_only_policy` / surface-forms / search regression smoke **전부 PASS**. (c) `relations ≥ 41` & `meta.relation_count` 일치. (d) full index total 17,580 불변(name_only ↔ relation_card 재배분만). (e) published/clinical_reviewed false 유지.
- **위험·의존성**: 출처 미확인 후보의 성급한 승격 = 오도 리스크. 묶음 A enrichment(아래 목표2)는 카드 증가 0(기존 covered 약 테마 보강). 큰 커버리지 레버(스타틴×CoQ10·H2×B12)는 허가사항 미기재 → source-policy 결정(목표2 §전략) 전까지 막힘. 데이터 변경 시 **CI 전체 세트 로컬 선실행 필수**(이번 세션 교훈).

---

### 목표 2 (2순위) — source queue 기반 Top 후보 source 확인

- **목표**: `MediStack_next_relation_source_check_queue.md` 의 큐(Q1–Q9) + 잔여 후보를 묶어 **Top10 후보의 허가사항 출처를 확인**하고 `source_confirmed / needs_review / missing / reject` 로 분류한다. 확인 결과만으로 통합 여부를 결정한다(확인=통합 아님).
- **왜**: 다음 커버리지 확장의 실질 입력. "개별 후보 확인보다 source-policy 결정이 ROI 가 크다"는 v1.1 결론을 검증/구체화한다. 묶음 A(퀴놀론·테트라×아연, 레보티록신×Mg)는 출처 확실·안전(단 신규 covered 0), 묶음 B(클로르탈리돈·인다파미드)는 칼륨 안전정책 선행 필수, 묶음 C(스타틴×CoQ10)는 허가사항 미기재 예상.
- **산출물**: Top10 source 확인 로그 + 갱신 큐 CSV(`next_relation_source_check_queue_v1_1.csv` 후속) + **source-policy 결정 입력 메모**(이차문헌 허용 여부를 PM/임상검토 트랙으로). reject 사유(예: PPI×칼슘 0/22) 기록.
- **성공기준(검증가능)**: (a) Top10 전건이 4상태 중 하나로 **명시 분류**되고 근거(fetch 품목 itemSeq·신호어·확인일) 기록. (b) `source_confirmed` 만 목표1 통합 후보로 넘어감. (c) 허가사항 미기재(스타틴×CoQ10·H2×B12 등)는 "missing 확정 → source-policy 대기"로 박제, **임의 통합 금지**. (d) 어떤 후보도 본 단계에서 flip/통합되지 않음(확인만).
- **위험·의존성**: 묶음 C 결과가 거의 확실히 missing → 커버리지 최대 레버(스타틴 944건)는 source-policy 미결 시 영구 보류. 묶음 B 는 칼륨 정책 승계(product_link_allowed=false·potassium_safety_card=true) 선행 없이는 승격 금지. nedrug fetch 부하·rate.

---

### 목표 3 (3순위) — 내 약 목록 저장 MVP 설계

- **목표**: "복용 중인 약을 검색해 내 목록에 저장"하는 최소기능(MVP)을 **설계**한다(구현 아님). 저장 위치(로컬), 데이터 모델, 면책/개인정보 경계, Free 제한(예: 5개) 까지 스펙으로 확정.
- **왜**: 유료화 전략(`MediStack_monetization_strategy_v1_1.md`)에서 "가장 안전하고 차별적"으로 지목된 첫 Plus 후보. "정보 정리/상담 준비" 가치 축에 정확히 부합하며 의학 단정을 강화하지 않는다.
- **산출물**: MVP 설계 문서(데이터 모델: 저장 항목 = item_seq/품목명/추가일 메모 정도 / 저장소 = `localStorage`(서버·계정 없음) / Free 한도 / "내 목록" 화면 와이어 스펙 / 면책·개인정보 문구). UI 구현 0.
- **성공기준(검증가능)**: (a) 저장 데이터에 **개인정보·건강정보 필드 없음**(증상·질환·복용이력·연락처 입력 경로 0 — 약명/품목 식별자만). (b) 저장은 **클라이언트 로컬 한정**(서버 전송·계정·백엔드 0). (c) "내 목록"은 복용 지시·해석 없이 **사용자 자가 기록 보관**임을 명시. (d) name_only 저장 항목에 의학정보 미부착 규칙 승계. (e) 설계 문서가 자기완결(다음 세션이 그 문서만으로 구현 착수 가능).
- **위험·의존성**: "내 약 목록"이 사실상 건강정보 컬렉션으로 비칠 수 있음 → 개인정보 정책(`..._privacy_and_feedback_policy_draft.md`)과 정합 필수, 입력 필드 최소화로 차단. localStorage 한계(기기/브라우저 종속·동기화 없음)는 MVP 범위로 수용. 결제/계정은 목표4 이후.

---

### 목표 4 (4순위) — Free / Plus 기능 분리 설계

- **목표**: `MediStack_monetization_strategy_v1_1.md` §3 의 Free/Plus 경계를 **기능 명세 수준으로 확정**한다(가격·결제 구현 아님). 무엇이 항상 무료인지, 무엇이 Plus 인지, 페이월 경계를 명문화.
- **왜**: 유료화 방향 합의의 다음 단계. 정보 접근(검색·name_only·기본 relation_card·면책/출처)은 항상 무료라는 신뢰 원칙을 기능 경계로 고정해야 이후 MVP 구현이 흔들리지 않는다.
- **산출물**: Free/Plus 기능 매트릭스 확정본(전략 문서 §3 표 승계·세분화) + 페이월 경계 정의 + "정보 접근은 페이월 뒤에 가두지 않는다" 원칙의 기능별 적용 명세. 가격은 후보 범위까지만.
- **성공기준(검증가능)**: (a) **약 검색·name_only 확인·기본 relation_card·면책/출처/복합제 배너 = 항상 Free** 가 명시적으로 고정됨. (b) Plus 기능은 전부 "정리/보관/상담 준비" 성격(의학 단정 강화 0, 복용지시 0)으로 분류. (c) 알림 기능은 "정보 갱신 사실 고지"까지만(행동 유도 푸시 금지)으로 경계 명시. (d) 제품/구매/제휴 동선 0(무료·유료 양쪽). (e) 결제/상품 등록은 **별도 승인 라운드**로 명시 분리.
- **위험·의존성**: 정보 핵심 가치를 페이월 뒤로 옮기면 참고정보 도우미 신뢰 훼손 → Free 핵심 약속을 하드 라인으로 고정. 결제 구현(StoreKit/웹 결제)은 본 문서 범위 밖. 가격 결정은 사용자·리텐션 데이터 확보 후가 안전(전략 §5).

---

### 목표 5 (5순위) — relation source 표시 UI 설계

- **목표**: `MediStack_source_attribution_design.md` 의 source 상속 표시 + 공개 차단 gate 설계를 **UI 표현 수준으로 구체화**한다(배선 아님). 현재 `renderDetail` 이 이미 출처를 상속 표시하므로, 그 표현 개선과 공개 모드 강등 UX 의 스펙만 정의.
- **왜**: 공개 전 법적 게이트(STOP #2·#3)와 직결. 출처 표시는 신뢰의 핵심이고, 공개 모드에서 source 미확정 relation 의 name_only 강등 UX 를 미리 확정해 두면 공개 전환이 매끄럽다.
- **산출물**: source 표시 UI 스펙(출처 유형 + 원문 링크 + `<details>` 출처 상세 표현/문구 개선안) + 공개 모드 강등 UX 스펙(미확정 relation → name_only 강등 시 사용자에게 보이는 화면·문구) + `publicRelationGate` 스펙(설계 문서 §4 코드 재인용, fail-closed 유지). `src/` 배선 0.
- **성공기준(검증가능)**: (a) 표시는 **relation 단위 source 상속**(558→1,072 카드별 개별 출처 신설 금지) 원칙 유지. (b) "출처 확인 중" 같은 **중간 라벨 노출 0**(confirmed 아니면 강등, 단일 경로). (c) 강등은 **표시 라우팅만**(relation 데이터 무손실) — relation 41건 한 건도 사라지지 않음. (d) 내부 모드(현행 라이브)는 **무변경**(`mode!=='public'` → 항상 relation_card). (e) 스펙이 `smoke_disclaimer_render.py` 의 출처 출력 검증과 정합.
- **위험·의존성**: 공개 모드 강등은 `source_status` 실부여 + gate 실배선이 전제이나 **둘 다 v1.2 범위 밖**(설계만). 규제 자문(STOP #1)·source confirmed 승격 절차(STOP #2)는 외부/별도 트랙 의존. UI 문구가 "관계 없음 보장"으로 읽히지 않게 면책 톤 유지.

---

### 목표 6 (동반) — 인기약 coverage gap 보강

- **목표**: `MediStack_popular_drug_coverage_match.md` 의 공백(name_only_only 101건 / 큰 공백 카테고리: 혈압약·기타 만성질환·소화제·해열진통)을 **근거 있는 것만** 확장 후보로 정제한다. seed 는 인지도 추정이므로, 가능하면 외부 인기약 실데이터(`external_popular_drugs_top100.csv`)로 보완.
- **왜**: 코어 분석이 지목한 가장 큰 불확실성 = "558(현 1,072)이 실제 많이 검색되는 약을 얼마나 덮는가". 체감 가치 향상 여지가 가장 큰 구간.
- **산출물**: 공백 카테고리별 확장 후보 정제 목록(민감군 high_risk_hold 제외 유지) + 외부 인기약 매칭 보완 시 갱신 CSV + missing_from_full_index(에스오메프라졸·세레콕시브 등)의 full index 확장 트랙 분리 기록.
- **성공기준(검증가능)**: (a) 후보는 **확립된 약물-영양소 상호작용 근거가 있는 것만**(암로디핀·항히스타민·감기약 등 근거 없는 군은 제외 유지). (b) 정신건강·항응고·임신/피임 등 **민감군은 후보화 보류**(criterion 8). (c) 채택은 전부 목표2 source 확인 게이트를 거침(분석→확인→통합 순서 불변). (d) full index 미수록 항목은 별도 full index 확장 트랙으로 분리(혼동 금지).
- **위험·의존성**: seed 가 실측 검색량이 아님(confidence=low) → "인기약 Top N 확정"으로 표현 금지. 스타틴 등 고가치 공백은 허가사항 미기재로 source-policy 에 막힘(목표2와 동일 의존). full index 확장은 별도 PM 승인.

---

### 목표 7 (1순위·완료/유지) — C / PPI+칼슘 buffer_combo 정책 확정

- **목표**: C(PPI+침강탄산칼슘 18건)의 buffer_combo 트랙 처리를 **확정·유지(회귀 방지)** 하고, 향후 유사 버퍼콤보 후보 발견 시의 동일 패턴을 잔여로 명시한다.
- **상태**: **완료.** 이번 세션에서 C 18건을 기존 PPI relation(란소프라졸 id36/37, 라베프라졸 id32/33)을 source 로 하는 **buffer_combo relation_card 로 flip** 완료(신규 relation 0). `combination_other_label = "위산 중화 완충 성분(침강탄산칼슘)"`(영양 칼슘 오독 차단). 재분류 근거·설계 = `MediStack_ppi_calcium_combo_reclassification_v1_1.md`. 라이브 반영(relations 41 / relation_card 1,072).
- **산출물**: (완료) 재분류 문서 + CSV + flip 데이터-only 배치. (잔여) 향후 버퍼콤보 후보 발견 시 동일 패턴 적용 가이드(other_label = 영양소명이 아니라 **기능명**으로 표기) — 본 항목에 명시.
- **성공기준(검증가능)**: (a) C 18건이 PPI 기준 카드만 표시(PPI×칼슘 relation 신설 0 — 허가사항 0/22). (b) `combination_other_label` 이 "칼슘"이 아니라 **기능명("위산 중화 완충 성분(침강탄산칼슘)")** 으로 표기되어 다른 화면의 칼슘 경고와 혼선 0. (c) 복합제 배너로 부분정보 고지 동반. (d) 회귀 방지: 향후 데이터 변경 시 C 가 PPI×칼슘 relation 으로 되살아나지 않음(validator other_label 가드 유지). (e) published/clinical_reviewed false.
- **위험·의존성**: 향후 다른 버퍼콤보(예: PPI+탄산수소나트륨 외)를 발견하면 **반드시 기능명 라벨**로 처리(영양소 오독 재발 방지). source 는 항상 기존 PPI relation 만(신규 relation 0). 칼륨 정책과 무관(C 에 칼륨 없음).

---

### 목표 8 (동반) — name_only UX 강화

- **목표**: name_only(품목명 확인) 화면의 UX 를 **의학정보를 부착하지 않는 범위 내에서** 개선한다(문구 명료화·검색 보조 향상). 현행 name_only UX 의 핵심 약속(검색 보조일 뿐, 의학 정보 아님)을 깨지 않는다.
- **왜**: 검색의 ~94%가 name_only 로 귀결되므로, 이 화면의 명료성이 사용자 신뢰·이탈에 직접 영향. "정보 없음 = 안전 아님" 을 오해 없이 전달해야 한다.
- **산출물**: name_only UX 개선 스펙(고지 문구 점검·중립성 유지·"등록 정보 없음이 관계 없음 보장 아님" 명시·검색 보조 동선 개선안). 변경 시 `smoke_search_regression` name_only 케이스 갱신 스펙.
- **성공기준(검증가능)**: (a) name_only 에 **상호작용/영양소/복용지시/관리/칼륨 보충안내 등 의학정보 부착 0**(불변 규칙). (b) 문구가 "안전합니다/복용하세요" 류로 읽히지 않음(중립 면책 톤). (c) name_only 카드 **비클릭(상세 라우팅 없음)** 동작 유지. (d) 변경 시 search regression smoke(A~H) PASS. (e) 칼륨보충제 standalone 차단 정책(`validate_potassium_name_only_policy`) 무영향.
- **위험·의존성**: 문구 "개선"이 의학정보 부착·과장으로 번지기 쉬움 → 불변 가드(의학정보 미부착)를 하드 라인으로. 현 name_only UX 문구는 **함부로 변경 금지**였으므로(v1.1 handoff), 변경은 PM 승인 + smoke 재검증 동반.

---

### 목표 9 (동반) — 공개 전 약관 / 개인정보 / 면책 링크 정리

- **목표**: 이미 작성된 초안 3종(이용약관·면책 / 개인정보·피드백 / 법적 게이트)을 **공개 전 한 곳에서 접근 가능한 링크 동선으로 정리**한다(법률 검토는 외부 의존, 링크/표시 정리만). 면책 문구의 앱 내 노출 동선 점검.
- **왜**: 공개 전 법적 게이트(`MediStack_public_release_legal_safety_checklist.md`) STOP #5(법적 문서 초안)·#6(피드백 차단 설계)는 충족됐으나, 사용자에게 닿는 **링크 동선**이 정리돼야 공개 준비가 완결된다. 면책은 모든 상세에 이미 표시되나, 약관/개인정보 접근 경로는 별도.
- **산출물**: 약관/개인정보/면책 링크 동선 스펙(푸터·정보 페이지 링크 위치·문구) + 초안→확정 전환 체크리스트(법률 검토 항목 표시) + 면책 노출 점검(`smoke_disclaimer_render.py` 와 정합).
- **성공기준(검증가능)**: (a) 초안 3종이 **DRAFT(법률 검토 전)** 임을 사용자 노출 문구에서 명시(합법성 보장 아님). (b) `disclaimers.common` 모든 상세 노출 유지(smoke PASS). (c) 제품/구매/제휴 부재 고지 + 개인정보 입력 금지 고지 동선 확보. (d) "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현 0. (e) 일반 공개는 여전히 **NO-GO**(규제 자문 STOP #1·source confirmed STOP #2 외부/별도 의존) 임을 명시.
- **위험·의존성**: 링크 정리가 "공개 허가/합법 보장"으로 오인되지 않게 함(게이트 §0). 변호사/약무 법률 검토·관할/준거법 확정은 **외부 의존**으로 v1.2 에서 완결 불가. UI 배선(약관 동의 화면 등)은 별도 단계.

---

### 목표 10 (6순위) — 영양제 앱 분리 전략 확정

- **목표**: 제품 추천·판매·제휴 수익을 추구할 경우 **MediStack 본체와 분리된 별도 영양제 앱**으로 가는 전략을 확정한다(`MediStack_supplement_app_separation_strategy.md` **작성 완료(2026-06-14)** — 본 항목은 그 문서를 v1.2 마일스톤에 연결·참조).
- **왜**: 참고정보 도우미에 구매 동선이 섞이면 "영양제 팔려고 위험을 과장한다"는 신뢰·규제 리스크가 즉시 발생(전략 문서 §4). 본체 정체성을 보호하면서 수익 옵션을 별도 트랙으로 격리.
- **산출물**: 분리 전략 확정(별도 문서 `MediStack_supplement_app_separation_strategy.md` 참조) + 본체/분리앱 경계 정의(데이터·브랜드·도메인 구분) + 본체 불변 조항(제품/구매/제휴 0) 재확인.
- **성공기준(검증가능)**: (a) **MediStack 본체 = 제품/구매/제휴 UI 영구 0**(무료·유료·향후 어느 버전도). (b) 영양제/이커머스 수익은 **별도 앱 트랙으로만** 분리(데이터·브랜드 명확 구분). (c) 본체는 "한국용 약-영양소 참고정보 베타"로 순수 유지. (d) 분리 전략 문서가 본 마일스톤에 명시 연결됨.
- **위험·의존성**: 별도 앱은 그 자체로 영양제 추천/판매의 규제·심사 리스크를 가짐(본 문서 범위 밖, 분리앱 트랙에서 별도 평가). 본체와의 데이터·브랜드 혼선 방지가 핵심. 분리 전략 문서는 작성 완료됐으므로 본 항목의 다음 단계는 "경계 계약(§5) 준수하에 실행 기획 구체화".

---

## 3. 우선순위 요약

| 순위 | 항목 | 상태 | 비고 |
|---|---|---|---|
| 1 | 목표7 C buffer_combo 최종화 | **완료/유지** | flip 라이브 반영(relations 41·rc 1,072). 잔여 = 향후 버퍼콤보 동일 패턴 |
| 2 | 목표2 source queue Top10 확인 | 다음 | 확인만(통합 아님) · source-policy 결정 입력 |
| 3 | 목표3 내 약 목록 저장 MVP 설계 | 설계 | 로컬·무계정·개인정보 0 |
| 4 | 목표4 Free/Plus 기능 분리 | 설계 | 정보 접근 항상 Free · 결제 별도 라운드 |
| 5 | 목표5 relation source 표시 UI 설계 | 설계 | 상속 표시 + 공개 강등 UX(배선 0) |
| 6 | 목표10 영양제 앱 분리 기획 | 기획 | 본체 제품 0 · 별도 앱 트랙 |
| 동반 | 목표1 coverage 확장 / 목표6 인기약 gap / 목표8 name_only UX / 목표9 법적 링크 | 동반 | 전부 게이트·smoke 안에서만 |

> 설계/기획 항목(3·4·5·10·8·9)은 **문서·스펙까지만**. 데이터/렌더 변경(1·2·7 의 통합)은 항목별 **별도 PM 승인 + 데이터-only 배치**로만 수행한다.

---

## 4. 불변 가드 (v1.2 내내 유지)

- **relation ≥ 41 · 신규 relation 은 오직 PM 승인 + source(허가사항) 확인 게이트로만.** 풀 확장·근거 없는 추가 금지. 허가사항 미기재 후보(스타틴×CoQ10·H2×B12 등)는 source-policy 결정 전 통합 금지.
- **DATA_URL 불변** (`./data/medistack_v0.2_beta_export.json` · in-place). 새 데이터 = 의미 보존 append-only, 기존 필드 의미 불변.
- **published / clinical_reviewed = false 봉인** (천장 = verified_reference). "식약처 승인 / 법적 문제없음 확정 / 약사 검수 완료" 표현 금지.
- **제품 / 구매 / 제휴 / 영양제 추천 UI 0** (무료·유료·향후 어느 버전도). 영양제 수익은 별도 앱 트랙으로만.
- **validator PASS 없으면 배포 금지.** 데이터 변경 시 CI 전체 세트 **로컬 선실행**(v0.1/v0.2/v0.3 export·full index·potassium·surface-forms·search/HCTZ/alias smoke). ⚠️ v0.1/v0.2/v0.3 validator 는 라이브 파일 인자 필수.
- **full index total 17,580 불변** (relation_card ↔ name_only 재배분만). full index 추가 확장은 별도 PM 승인.
- **name_only 에 의학정보(상호작용·영양소·복용지시·관리·칼륨 보충안내) 부착 0.** name_only UX 문구 변경은 PM 승인 + smoke 재검증 동반.
- **복합제는 부분정보 고지 동반** — HCTZ 는 칼륨 반전 고지 / 버퍼콤보(C 포함)는 `combination_other_label` 을 **기능명**으로(영양소 오독 차단).
- **칼륨 정책 유지**: standalone 칼륨보충제 차단 · 칼륨 제품링크 금지 · `potassium_safety_card=true` · 칼륨보존이뇨제 복합제 영구 차단 · HCTZ 외 복합제 basis 금지.
- **15행(에스오메프라졸×B12 id15) 미노출·재편입 금지** / 에스오메프라졸 alias 금지(id16×Mg 정상 live · 혼동 주의).
- **공개 모드 source gate 는 fail-closed** (confirmed 아니면 무조건 name_only 강등 · 중간 라벨 노출 0 · relation 데이터 무손실). 내부 모드(현행 라이브)는 무변경.
- **일반 공개는 NO-GO 유지** — 규제 자문(STOP #1)·relation source confirmed 승격(STOP #2) 외부/별도 트랙 의존. 본 문서·설계는 공개 허가/합법 보장이 아니다.
- **운영**: 수동 deploy · 무단 tag 금지(PAT push 만 · main push 가 deploy 트리거) · `scripts/__pycache__/` 커밋 금지 · commit 끝 Co-Authored-By trailer.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index 는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지(source 게이트 외) / name_only 의학정보 부착 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ 칼륨 반전 · 버퍼콤보 기능명 라벨) / relation 없는 약은 name_only 로만 표시 / 영양제 수익은 별도 앱 / 일반 공개는 규제 자문·source confirmed 전 NO-GO.
