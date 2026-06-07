# MediStack v0.2 — 스코프 / 정책 / 작업계획

작성 기준일: 2026-06-07 / 단계: **준비(계획만, 코드 수정 없음)**
현행: v0.1 베타 라이브(https://yoonspower.github.io/medistack/) · relations 19 · validator PASS 12/12 · 15행 excluded/draft · published·clinical 미사용 · 제품 UI 없음

## 0. 절대 유지 원칙 (v0.2 내내 불변)
v0.1 데이터 직접 수정 금지 / clinical reviewer 확보 전 published·clinical_reviewed 금지 / verified_reference 기준 유지 / excluded_v0_1 앱 노출 금지 / 제품 링크·구매 유도 금지 / 의료 단정·복용 지시 금지 / validator PASS 없으면 배포 금지 / 공통 면책문구 유지 / 칼륨 추가 고지 유지.

---

## 1. v0.2 목표 정의
v0.1의 안전 프레임을 **그대로 유지하면서** 신뢰성·커버리지·탐색성을 끌어올린다. 핵심:
- 데이터 **커버리지 확대**(20→목표 50, verified_reference 기준 충족분만)
- **탐색성**(검색 + 약물/영양소 필터) — 행 수 증가 대비
- **15행 해소 시도**(에스오메프라졸×B12 직접 라벨 확인 시 승격)
- **운영 현행화**(CLAUDE.md, GitHub Actions Node24 버전업)
- 표시 문구 **명료화**(원문보다 강해지지 않는 선에서)
- clinical reviewer 없이 **천장 = verified_reference 유지**(published 계속 봉인)

---

## 2. 포함 / 제외 범위

### 포함 (In)
- CLAUDE.md (리포 가드레일 문서)
- GitHub Actions 버전업: checkout v4→v5, setup-python v5→v6 (둘 다 Node24)
- 검색 + 약물명/영양소명 필터 (클라이언트, 정적 유지)
- 15행 재검토(데이터 트랙)
- 데이터 20→50 확장(데이터 트랙, 단계적)
- 표시 문구 UX 개선(데이터 트랙, phrasing gate 재적용)

### 제외 / 보류 (Out)
- **제품/제휴 트랙 — v0.2 보류 권장**(v0.3+ 결정). 이유: 비판단 정보 ↔ 수익화 충돌 재유입, 행별 안전 게이트·고지 부담, v0.2는 데이터/UX 집중이 우선.
- published / clinical_reviewed — reviewer 확보 전 금지(구조적)
- antagonism 등급 행(예: 와파린×비타민K) — 임상검수 필요 → reviewer 없으면 제외 유지
- 질환/증상 입력 — v0.1에서 이미 out, 유지
- 백엔드/검색 서버 — 정적 구조 유지(클라이언트 인메모리)

---

## 3. 우선순위
- **P0 (안전·기반, 선행)**: CLAUDE.md / v0.2 데이터·validator 버저닝 구조 확정 / Actions 버전업(검증 후)
- **P1 (핵심)**: 15행 재검토 / 데이터 확장(단계적) / 검색+필터 / 문구 UX
- **P2 (여력)**: 추가 카테고리 확장 / 접근성·PWA 등

> 의존성: 데이터 버저닝 구조(P0)가 서면 15행·확장·문구가 그 위에서 진행. 검색/필터는 데이터가 늘수록 가치 ↑.

---

## 4. 작업 단계 (phase)
- **Phase 0 — 거버넌스**: CLAUDE.md 작성 + v0.2 데이터/validator 버저닝 규칙 확정(v0.1 봉인 유지).
- **Phase 1 — CI 현행화**: Actions Node24 버전업(별도 브랜치 CI green 확인 후 머지) + Pages 액션 버전 점검.
- **Phase 2 — 데이터 트랙**: 15행 재검토 → (성공 시 20행) → 확장 후보 큐레이션 → 식약처 원문 SOP 검증 → `medistack_v0.2_beta_export.json` 생성 → v0.2 validator PASS.
- **Phase 3 — 앱 트랙**: 검색/필터 구현(data/guards/render/states 레이어 유지) + 문구 UX 렌더 반영.
- **Phase 4 — 통합 QA/배포**: v0.2 데이터로 QA(P0 + 신규 케이스) → deploy gate(validate→deploy) → 배포 + 앱 data 포인터 v0.2 전환.

Phase 2(데이터)와 Phase 3(앱)는 분리돼 **병렬 진행 가능**.

---

## 5. 데이터 작업 ↔ 앱 작업 분리

### 데이터 트랙 (v0.1 봉인 유지)
- v0.1 JSON은 절대 편집 안 함. v0.2 = **신규 버전 파일** `medistack_v0.2_beta_export.json`.
- v0.2 validator = `validate_medistack_v0_2_export.(py/js)` — **구조 규칙 동일**, 상수만 갱신(예상 relations 수, 칼륨 id 집합, excluded 집합). v0.1 validator는 그대로 둠(혼동 방지).
- 15행 승격·신규 행·문구 수정 **전부 데이터 트랙**. 문구(display_text/management)는 데이터 소속이지 앱 아님.
- 스키마는 **append-only**(필드 추가 가능, 기존 필드 의미 불변) → 검색 인덱스는 런타임 생성(데이터에 안 박음).

### 앱 트랙
- 코드(검색/필터/문구 렌더)만. 데이터 버전에 독립.
- 앱이 어느 export를 fetch할지는 **config 한 줄**(DATA_URL). v0.2 배포 시 v0.2 파일로 전환, v0.1 파일은 아카이브 보존(삭제 금지, traceability).

---

## 6. 위험요소
- **확장 품질 저하**(검증 누락) → 행별 식약처 원문 SOP 강제 + v0.2 validator 행수·규칙으로 게이트.
- **문구 개선이 원문보다 강해지거나 지시문화** → phrasing gate(Step4: 단정/복용량/시간숫자/제품유도 금지) 재통과 필수.
- **antagonism·임상판단 행 유입**(와파린×K 등) → reviewer 없으면 제외 유지.
- **15행 무리한 승격** → 에스오메프라졸 품목 허가사항 B12 직접 문구 미확인 시 excluded 유지(승격 금지).
- **Actions 버전업 breaking** → Node24 전환은 우리 워크플로(checkout+setup-python+python 실행)에 입력 breaking 없음. 단 별도 브랜치서 CI green 확인 후 머지. Pages 액션도 Node24 지원 버전 확인. (결정성 위해 정확 태그/ SHA 핀 옵션)
- **validator 버전 혼동**(v0.1용으로 v0.2 검증, 반대도) → 파일명·상수 분리, CI에서 버전 명시.
- **검색 빈 결과 오인**("관계 없음 = 안전") → empty_state 문구 유지/강화, 검색 0건도 동일 안내.
- **신규 칼륨/모니터링류 추가** → 신규 칼륨 행도 product_link_allowed=NO + potassium_safety_card 처리, v0.2 validator에 id 반영.
- **제품 트랙 조기 도입 압력** → 보류 결정 문서화로 방어.

---

## 7. 필요한 산출물 목록
- `CLAUDE.md` (가드레일: 불변원칙·데이터 봉인·validator 게이트·프레임·실행법)
- v0.2 데이터 버저닝/검증 정책(본 문서 또는 별도)
- `medistack_v0.2_beta_export.json` (신규 버전 데이터)
- `validate_medistack_v0_2_export.(py/js)` (상수 갱신본)
- v0.2 확장 후보 큐레이션 워크테이블(SOP 검증용)
- 15행 재검토 결과 메모(승격 여부 + 근거/출처)
- 문구 UX 변경 diff + phrasing gate 체크 결과
- 검색/필터 구현(app src) + 신규 QA 케이스
- v0.2 QA 테스트케이스(기존 15건 + 검색/필터/확장 반영)
- 워크플로 버전업 반영(validate.yml / deploy.yml)

---

## 8. GPT PM 판정 필요 결정사항
1. **제품/제휴 트랙 v0.2 보류 확정?** (권장: 보류 → v0.3+)
2. **데이터 확장 목표·방식**: 50 확정 vs 단계적(20→30→50)? 카테고리 우선순위(예: 추가 항생제/비스포스포네이트×칼슘/갑상선/스타틴 등)?
3. **15행 승격 기준 재확인**: 에스오메프라졸 품목 허가사항 B12 직접 문구 확인 필수 + 실패 시 excluded 유지 동의?
4. **문구 UX 개선 범위**: 어디까지 손대나 + phrasing gate 재적용 동의?
5. **Actions 버전업 타이밍**: 별도 PR 선행(Phase 1 단독) vs 데이터/앱과 묶어서?
6. **v0.2 천장 = verified_reference 유지 확정?** (published 계속 봉인 = reviewer 미확보 전제)
7. **검색/필터 v0.2 포함 확정** vs 데이터 우선 후 후순위?
8. **antagonism 행 확장 후보에서 제외 유지 확정?** (와파린×K 등, reviewer 전까지)
9. **clinical reviewer 확보 트랙을 v0.2에서 착수할지**(별도 거버넌스 — 확보 시 v0.3 published 경로 열림)?

---

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
