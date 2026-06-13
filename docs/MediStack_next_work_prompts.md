# MediStack — 다음 세션 실행 프롬프트 모음

> 작성일: 2026-06-14. **프롬프트 모음 전용 — 코드/데이터 무변경.** 각 프롬프트(A~F)는 **자기완결**이다: 새 AI 세션이 이 문서의 해당 프롬프트 하나만 읽고도 정책 가드레일·성공기준·STOP 조건을 알고 안전하게 실행할 수 있도록, 매 프롬프트마다 핵심 금지·성공기준·STOP·산출물을 **반복** 기재한다.
>
> 사용법: 다음 세션 시작 시, PM이 아래 A~F 중 하나를 골라 그 블록을 그대로(또는 거의 그대로) 새 세션 프롬프트로 붙여넣는다. 각 프롬프트는 시작 시 `CLAUDE.md` + `docs/MediStack_v1.1_handoff.md` + 해당 선행자료를 먼저 읽도록 지시한다.

---

## 0. 전(全) 프롬프트 공통 가드레일 (각 프롬프트가 자체 재기술하지만, 한 번 더 박제)

이 가드레일은 MediStack 정체성에서 나오며 **어떤 작업에서도 불변**이다:

- ❌ **제품/구매/제휴/영양제 추천 동선 금지** — 링크·버튼·제품 예시·제품 필드·영양제 보충 권유 표현 0.
- ❌ **복용 지시 / 진단 / 처방 / 치료 / 위험 확정 / "드세요·보충하세요·중단하세요" 금지.**
- ❌ **"식약처 승인" / "법적 문제없음 확정" / "약사 검수 완료" 표현 금지.**
- ❌ **신규 relation 구현 금지** (relation 41 불변). 출처는 **허가사항 우선 gate**(문헌만으로는 미채택).
- ❌ **published / clinical_reviewed 전환 금지** — 천장 = `verified_reference`. 봉인 유지.
- ❌ **v0.1 데이터 직접 수정 금지** · **DATA_URL(v0.2) 변경 금지** · **무단 deploy / 무단 tag 금지.**
- ✅ relation 없는 약은 **name_only** 로만 표시. name_only 에 의학정보 부착 금지.
- ✅ 칼륨 정책 유지(`product_link_allowed=false` + `potassium_safety_card=true`).
- ✅ 복합제는 **부분정보 고지 동반**(HCTZ 는 칼륨 반전 고지) · 칼슘 완충 복합제는 other_label 을 **"칼슘"이 아니라 완충 기능명**으로.
- ✅ **데이터 변경 시 CI 전체 세트(validator + smoke)를 로컬에서 선실행** 후에만 진행(surface-forms / v0.1 / potassium selftest 포함).

### 현재 라이브 기준선(2026-06-14, 작업11 시점 · 모든 프롬프트의 회귀 기준)

| 항목 | 값 |
|---|---|
| relations (export) | **41** (불변) |
| relation_card | **1,072** |
| name_only | **16,508** |
| full index total | **17,580** |
| product_aliases | **679** |
| alias_count (meta) | **717** |
| verified_item_seqs | **1,059 / 20** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (v0.2, 불변) |
| published / clinical_reviewed | **false / false** (봉인) |

> 이 숫자는 작업11 직전 세션에서 C(PPI+침강탄산칼슘 18건)를 buffer_combo 트랙으로 flip 한 결과다(`scripts/integrate_combo_banner_c_v1_1.py`). 데이터를 건드리지 않는 프롬프트(A·B·C·D·E)는 이 숫자가 **그대로 유지**되어야 하고, 데이터 회귀 프롬프트(F)는 이 숫자를 **재확인**한다.

---

## A. source 확인 큐 Top10 — 출처 확인 전용 프롬프트

> **목표:** 다음 relation 확장 후보(Q1~Q9 + 필요 시 추가 1)의 **식약처 허가사항 출처 확인만** 수행하고, 결과를 `source_confirmed / needs_review / missing / reject` 로 분류·문서화한다. **relation 추가/수정/flip 은 하지 않는다.**

**입력 / 선행자료 (먼저 읽기):**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_next_relation_source_check_queue.md` (큐 전략 · §1 분류 · §2 Q1~Q9 우선순위 · §3 source-policy 권고)
- `data/next_relation_source_check_queue_v1_1.csv` (Q1~Q9 권위 목록)
- source 확인 방법 승계: `scripts/verify_atier_relation_sources.py` 패턴 — 후보 성분별 단일성분 대표 2~3품목 nedrug `getItemDetail` fetch → 테마 신호어 검색.

**허용 범위:**
- 후보별 nedrug 허가사항 fetch + 신호어 검색 + 상태 분류(읽기/확인/문서화).
- 결과를 **문서 + CSV(읽기전용 산출물)** 로 기록. 우선순위(묶음 A enrichment → B 치아지드 → C 스타틴×CoQ10)는 큐 문서 §2~§3 승계.
- 스타틴×CoQ10·H2×B12 는 "missing 예상"으로 **보수 표기**(허가사항 미기재 관행).

**금지:**
- ❌ relation 신규/수정/flip · export(relations 41)·full index·alias·DATA_URL·src 변경.
- ❌ `do_not_implement_yet`: **어떤 후보도 이 단계에서 "확정"하지 않는다.** 전부 *source 확인 대기 후보* 로만 기재.
- ❌ 문헌만 있는 후보를 source_confirmed 로 올리지 않는다(허가사항 우선 gate). published/clinical false 유지.
- ❌ 제품/구매/영양제 추천 표현, 복용지시, "승인/검수 완료" 표현.

**성공기준:**
- Q1~Q9 각 후보가 `source_confirmed / needs_review / missing / reject` 중 하나로 **근거(인용 위치)와 함께** 분류됨.
- 라이브 보호데이터 `git status` clean(데이터 무변경). 기준선 숫자(relations 41 등) 불변.
- "다음 레버 = source-policy 결정" 권고가 갱신된 근거로 재확인 또는 정정됨.

**STOP 조건 (멈추고 PM에 보고):**
- 어떤 후보가 source_confirmed 로 보이더라도 **relation 신설/flip 은 PM 승인 + source 확정 전까지 do_not_implement_yet.** 확인 결과만 보고하고 멈춘다.
- 허가사항에 "원문보다 강한" 표현(복용량·위험 확정)이 보이면 채택 후보에서 제외하고 기록.
- nedrug 응답 구조가 바뀌어 신호어 검색이 불가하면 중단·보고(추측 분류 금지).

**산출물:** 갱신된 source 확인 상태 문서(또는 `..._source_check_queue` 후속 리포트) + 읽기전용 CSV. 라이브 무변경.

---

## B. "내 약 목록 저장" MVP — 설계 전용 프롬프트

> **목표:** 유료화 1순위 후보인 **"내 약 목록 저장"** 기능의 MVP를 **설계만** 한다(로컬 우선 저장, 의학 조언 없음, 제품 동선 없음). 코드/UI/스키마 구현 0.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_monetization_strategy_v1_1.md` (§2 "내 약-영양소 관리 도구" · §3 Free/Plus · §5 단계 제언: "내 약 목록 저장 + 약사 질문 생성"을 MVP 1순위로 지목).

**허용 범위:**
- **로컬 우선(local-first) 저장 설계**: 정적 SPA + GitHub Pages 환경에 맞춰 `localStorage`/IndexedDB 등 클라이언트 보관 위주. 서버 계정·DB는 MVP 범위 밖으로 명시(필요 시 후속 라운드).
- 저장 단위(약 검색 결과를 내 목록에 추가/삭제), 데이터 형태(품목명·item_seq·메모 등 보관 필드), 비움/내보내기, 프라이버시(기기 보관·외부 전송 없음) 설계.
- Free 제한(예: 5개) ↔ Plus 무제한 경계는 **C 프롬프트(기능 분리)와 정합**하도록 표기만.

**금지:**
- ❌ 실제 구현(코드/UI/스키마/결제). 데이터·src·DATA_URL 변경 0.
- ❌ 앱이 저장된 약을 **해석·지시**하는 기능("이 약엔 X 보충") — 보관/표시까지만, 복용지시·의학 단정 금지.
- ❌ 제품/구매/제휴/영양제 추천. 신규 relation. published/clinical flip.
- ❌ "식약처 승인/약사 검수 완료/법적 문제없음" 표현.

**성공기준:**
- MVP 범위(무엇이 들어가고 무엇이 후속인지)·로컬 저장 모델·프라이버시 경계·면책 정렬이 한 문서로 자기완결.
- 모든 기능이 "정보 정리/상담 준비" 성격임을 명시(의학 판단 강화 아님). 라이브 무변경(`git status` clean).

**STOP 조건:**
- 설계가 "복용 지시·진단" 또는 "제품 추천" 으로 번지면 즉시 멈추고 범위 재조정.
- 서버·계정·동기화가 MVP에 필수로 보이면 그 부분은 **후속 라운드**로 분리하고 MVP는 로컬 우선으로 유지.

**산출물:** `docs/MediStack_my_medications_mvp_design.md`(신규 설계 문서) 1개. 코드/데이터 무변경.

---

## C. Free / Plus 기능 분리 — 설계 전용 프롬프트

> **목표:** 유료화 Free / Plus **기능 경계**를 확정 설계한다. **Plus 가 의학 조언/복용량 영역으로 넘어가지 않도록** 안전 경계를 명시한다. 결제/상품 등록/구현 0.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_monetization_strategy_v1_1.md` (§1 유료화 불변 원칙 · §3 Free/Plus 표 · §3.1 가격 후보(있으면) · §4 제품/제휴는 별도 앱).
- (정합) B 프롬프트 산출물(있으면 `docs/MediStack_my_medications_mvp_design.md`).

**허용 범위:**
- Free / Plus 기능 표 정련: **Free 핵심 약속**(약 검색·name_only 품목명 확인·기본 relation_card·면책/출처/복합제 배너·제한적 내 목록 저장) = **항상 무료** 유지. 정보 접근을 페이월 뒤에 가두지 않음.
- Plus = "정리·보관·상담 준비" 가치(가족 프로필·참고정보 모아보기·약사/의사 질문 생성·PDF·메모·이력·알림 등). 각 Plus 기능에 **안전 정렬 근거** 부기.
- 가격/과금은 **후보까지만**(실제 결제 구현·상품 등록은 별도 승인 라운드).

**금지 (Plus 안전 경계 = 본 프롬프트 핵심):**
- ❌ **Plus 기능이 복용량·진단·치료·위험 확정·영양제 추천으로 넘어가는 것 금지.** 유료라고 "더 위험한 의학 판단을 대신"하지 않는다. 가치 축 = 개인화 + 정리/보관 + 상담 준비.
- ❌ 알림 기능은 "정보가 갱신됨" **사실 고지**까지만. "○○를 보충/중단하세요" 행동 유도 푸시 금지.
- ❌ 본체에 제품/구매/제휴 도입(분리 권장). 신규 relation. published/clinical flip. 결제 구현.

**성공기준:**
- Free/Plus 경계가 표로 확정 + 각 Plus 기능의 안전 근거 명시 + "Plus 가 의학 조언으로 넘어가지 않음" 이 명문화.
- 가격은 후보로만. 라이브 무변경(`git status` clean), 기준선 숫자 불변.

**STOP 조건:**
- 어떤 Plus 기능이 복용지시/진단/제품 추천 성격이면 **Plus 에서 제외**하고 그 사유를 기록.
- 결제/상품 등록 작업이 필요해 보이면 멈추고 "별도 승인 라운드" 로 분리.

**산출물:** Free/Plus 기능 분리 설계 문서(신규 또는 monetization 문서 §3 갱신 리포트). 코드/데이터/결제 무변경.

---

## D. relation source 표시 UI — 설계 전용 프롬프트

> **목표:** relation_card 에 **식약처 허가사항 출처(attribution)** 를 보여주는 UI를 설계한다(출처 유형·원문 링크·출처 상세 상속 표시 + 공개 차단 gate 설계). 실제 src 배선·강등·숨김 구현 0.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_source_attribution_design.md` (이미 존재 — 출처 부여 단위 = relation 단위(카드별 개별 출처 미관리, 카드는 상속) · 설계 필드 `relation_source_*`/`source_status` · 공개 차단 gate `publicRelationGate` 스펙 · fail-closed).
- 참고: 현 `render.js renderDetail()` 이 이미 `source.type` + `원문 보기↗`(url) + `<details>출처 상세</details>`(pointer) 를 상속 표시 중. `smoke_disclaimer_render.py` S4 가 출력 확인.

> ⚠️ 정정: `MediStack_source_attribution_design.md` 본문 숫자는 작성 시점(relation 30 / relation_card 558)이다. **현재는 relations 41 / relation_card 1,072.** 설계의 "relation 단위 부여 + 카드 상속" 원리는 그대로지만, 수치는 §0 기준선을 사용한다.

**허용 범위:**
- 출처 표시 UI 설계(상속 구조 형식화, `relation_source_title`/`source_checked_at`/`source_confidence`/`source_status` 등 **append-only** 필드 설계).
- 공개 차단 gate **스펙**: `source_status === 'confirmed'` 아니면 공개 모드에서 name_only 강등(fail-closed, 중간 "확인 중" 라벨 없음). 내부/현행 모드는 무변경 보증.

**금지:**
- ❌ relation 41 데이터 수정 · `source_status` **실부여** · gate 함수 `src/` 배선 · relation_card 렌더 변경 · 실제 강등/삭제/숨김 · DATA_URL/export 변경.
- ❌ `source_status` 임의 `confirmed` 자동 부여(승격은 규제 자문/검토 후 별도 단계).
- ❌ "식약처 승인/검수 완료" 표현(출처는 "허가사항 출처" 까지만 — 승인·검수 단정 아님). published/clinical flip.

**성공기준:**
- 출처 표시 UI(상속) + append-only 필드 + 공개 gate 스펙이 한 문서로 자기완결. "relation 데이터 무손실(라우팅 기반)" 보증 명시.
- 현 라이브(내부 모드) 동작 무변경임이 설계에 보증됨. 라이브 데이터 무변경(`git status` clean).

**STOP 조건:**
- gate 를 실제 src 에 배선하거나 `source_status` 를 데이터에 부여하려는 시점에 멈춘다(이 프롬프트는 **설계까지만**).
- 공개 노출(relation_card 일반 공개)은 규제 자문(STOP #1) + source confirmed 승격 전까지 금지 — 설계만 하고 멈춘다.

**산출물:** 출처 표시 UI 설계 문서(신규 또는 `MediStack_source_attribution_design.md` 후속 갱신). src/데이터 무변경.

---

## E. 별도 영양제 앱 기획 — 분리 전제 프롬프트

> **목표:** 제품/제휴 수익을 추구할 경우의 **별도 영양제 앱**을 기획한다. **MediStack 본체와 데이터·브랜드·동선이 완전히 분리**됨을 전제로 한다(MediStack 본체에는 제품/구매/제휴를 넣지 않는다).

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_supplement_app_separation_strategy.md` — **존재(2026-06-14 작성됨).** 분리 경계 계약(데이터·UX·브랜드 비공유)이 정의돼 있다. 추가 근거는 `docs/MediStack_monetization_strategy_v1_1.md` §4("제품 판매/제휴는 별도 앱으로 분리"). 본 프롬프트는 그 분리 전략을 **실행 기획(기능 우선순위·MVP)으로 구체화**하되, 분리 경계 계약(§5)을 절대 위반하지 않는다.

**허용 범위 (전부 기획 문서 — 구현 0):**
- 별도 앱의 정체성·데이터 출처·브랜드·수익 모델(제품/제휴 허용은 *별도 앱에서만*) 기획.
- **분리 경계 명문화**: MediStack 본체와 코드/데이터/브랜드/사용자 동선이 섞이지 않음. MediStack 은 "한국용 약-영양소 참고정보 베타"로 순수 유지.

**금지 (분리 원칙 = 본 프롬프트 핵심):**
- ❌ **MediStack 본체에 제품/구매/제휴/영양제 추천을 끌어들이는 모든 설계 금지.** 두 앱의 동선·데이터·브랜드 혼합 금지.
- ❌ MediStack relation 데이터를 영양제 앱의 "추천 근거" 로 재사용(참고정보를 판매 정당화로 전용) 금지 — 신뢰·규제 리스크.
- ❌ MediStack 쪽 코드/데이터/DATA_URL/relation/published 변경. 신규 relation.
- ❌ "식약처 승인/약사 검수 완료/법적 문제없음" 표현.

**성공기준:**
- 별도 영양제 앱 기획이 한 문서로 자기완결 + **MediStack 과의 분리 경계가 명문화**(혼합 금지 항목 명시).
- MediStack 본체는 어떤 변경도 받지 않음(`git status` clean, 기준선 숫자 불변).

**STOP 조건:**
- 기획이 MediStack 본체에 제품/구매 동선을 추가하는 방향으로 흐르면 즉시 멈추고 "별도 앱으로 분리" 로 되돌린다.
- 영양제 앱이 MediStack relation/면책 톤을 판매 근거로 쓰려 하면 멈추고 분리 원칙 재확인.

**산출물:** `docs/MediStack_supplement_app_separation_strategy.md`(신규) 또는 별도 영양제 앱 기획 문서. MediStack 본체 무변경.

---

## F. C buffer_combo 추가 회귀 — 검증 + (신규 후보 시) 데이터-only 패턴 프롬프트

> **목표:** C(buffer_combo) flip 이후 상태에 대해 **validator/smoke 전체 세트를 재실행**하여 기준선이 유지됨을 확인한다. 그리고 **새로운 buffer_combo 후보가 나타나면** 기존 C 통합기와 **동일한 데이터-only 패턴**(PM 승인·신규 relation 0·other_label 은 완충 기능명)으로만 처리하도록 가드를 재기술한다.

**입력 / 선행자료:**
- `CLAUDE.md`, `docs/MediStack_v1.1_handoff.md`
- `docs/MediStack_ppi_calcium_combo_reclassification_v1_1.md` (C = buffer_combo 재분류 정책 · §2-3 other_label 설계 주의 · §3 데이터-only 작업 범위).
- 통합기(권위 패턴): `scripts/integrate_combo_banner_c_v1_1.py` (idempotent flip · `PPI_RID={란소프라졸:[36,37], 라베프라졸:[32,33]}` · `OTHER_LABEL="위산 중화 완충 성분(침강탄산칼슘)"` · 신규 relation 0).
- validator/smoke 명령 세트: `docs/MediStack_v1.1_handoff.md` §6.

**허용 범위:**
- **회귀 실행(읽기/검증)**: validator + smoke 전체 세트를 라이브 파일 인자로 실행하고 결과를 기록.
  - 데이터 변경 시 CI 전체 세트를 로컬 선실행(교훈): surface-forms / v0.1 / potassium selftest 포함.
- (신규 후보가 있을 때만) C 와 동일한 **데이터-only** flip: full index name_only→relation_card(total 17,580 유지) + `verified_item_seqs` += + `product_aliases` +=(is_combination=true·basis=PPI·notice=true·source_relation_ids=기존 PPI relation·**other_label=완충 기능명**) + validator 상수 갱신. **신규 relation 0.**

**검증 기대값 (회귀 성공 = 아래 전부 일치):**
- `relation_card = 1,072` · `name_only = 16,508` · `full index total = 17,580`
- `relations(export) = 41` · `alias_count = 717` · `product_aliases = 679` · `verified_item_seqs = 1,059/20`
- `published = false` · `clinical_reviewed = false` · `DATA_URL = v0.2`(불변)
- 모든 validator/smoke PASS(handoff §6 기대치). 보호데이터 `git status` clean(회귀 단독 실행 시).

**금지:**
- ❌ **신규 relation 생성 금지** — PPI×칼슘 nutrient relation 포함 절대 금지(허가사항 출처 없음·칼슘=완충제). relations 41 불변.
- ❌ buffer_combo other_label 을 **"칼슘"** 으로 쓰는 것 금지 — 반드시 **완충 기능명**("위산 중화 완충 성분(...)" 류). 영양 칼슘 오독 차단이 핵심.
- ❌ 칼슘 추천/보충 표현 · 제품/구매 · E(라베+산화Mg) 등 보류군 접촉 · DATA_URL/export relations 변경 · published/clinical flip.
- ❌ PM 승인 없는 신규 후보 flip. 데이터 변경은 **PM 명시 승인 batch** 에서만.

**성공기준:**
- (회귀) 위 "검증 기대값" 전부 일치 + 전 validator/smoke PASS.
- (신규 후보 처리 시) C 패턴 그대로: 신규 relation 0 · other_label=완충 기능명 · idempotent · CI 전체 세트 로컬 선실행 PASS · 적대 렌더 리뷰(칼슘 오독·부분정보 오인) 통과.

**STOP 조건:**
- 검증 기대값 중 하나라도 어긋나면 **즉시 멈추고** 원인 보고(데이터 오염·통합기 재실행 흔적 의심). 임의 수정 금지.
- 새 buffer_combo 후보가 **PM 승인 없이** 발견되면 flip 하지 말고 **후보로만 보고**(do_not_implement_yet).
- other_label 후보가 "칼슘" 단독이거나, 카드에 PPI×칼슘 nutrient 정보가 끼면 멈추고 정정.

**산출물:** 회귀 검증 리포트(전 validator/smoke 결과 + 기준선 숫자 일치 확인). 신규 후보 처리 시에만 데이터-only 통합 + 통합 문서. 그 외 라이브 무변경.

---

## 7. 공통 마무리 (모든 프롬프트)

- 작업 종료 시 보호데이터 `git status` 확인: **설계/문서 프롬프트(A·B·C·D·E)는 데이터/ src clean** 이어야 한다. **데이터 회귀 프롬프트(F)** 만 PM 승인 batch 에서 데이터를 만질 수 있다.
- 어떤 프롬프트도 **git commit / deploy / tag 를 자동 수행하지 않는다.** 그 단계는 PM 명시 지시에서만.
- 커밋이 승인되면 메시지 끝에 Co-Authored-By trailer.

> **안전 원칙(불변, 재게시):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / relation 신규·풀 확장 금지 / name_only 의학정보 부착 금지 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전, 칼슘 완충 복합제는 other_label=완충 기능명) / relation 없는 약은 name_only 로만 / 제품·제휴는 별도 앱으로 분리 / 수동 deploy·무단 tag 금지.
