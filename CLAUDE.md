# CLAUDE.md — MediStack 리포 작업 가드레일

이 리포에서 코드/데이터를 다루는 모든 AI 세션(Claude Code 포함)이 **먼저 읽고 지켜야 할 규칙.**
사람 검토자(PM은 별도 AI 세션)에게 핸드오프되는 산출물이라 자기완결적으로 작성한다.

## 0. 제품 한 줄
MediStack은 **식약처 허가사항 기반 약-영양소 참고 정보** 베타 앱. 진단·처방·복약지시가 아니다.
정적 HTML/CSS/JS(ES module) + GitHub Pages. 빌드 없음.

## 1. 절대 불변 원칙 (위반 금지)
- **v0.1 데이터(`data/medistack_v0.1_beta_export.json`) 직접 수정 금지.** 봉인 상태.
- **새 데이터 = 새 버전 파일 + 새 validator.** (v0.2 → `medistack_v0.2_beta_export.json` + `validate_medistack_v0_2_export.*`)
- **published / clinical_reviewed 전환 금지.** clinical reviewer 확보 전까지 **천장 = verified_reference.**
- **excluded_v0_1 은 앱 렌더 금지** (내부 QA/관리용).
- **제품/제휴 금지**(v0.2): 제품 링크·구매 버튼·제휴 UI·제품 예시·제품 필드 추가 금지.
- **의료 단정 / 복용 지시 / 위험 확정 / 구매 유도 표현 금지.**
- **칼륨 행**: `product_link_allowed=false` + `potassium_safety_card=true` + 추가 고지 유지.
- **공통 면책문구**(`disclaimers.common`) 모든 상세에 유지.
- **validator PASS 없으면 배포 금지.**
- **antagonism / 임상판단 행 금지**(예: 와파린×비타민K). reviewer 전까지 제외.

## 2. 데이터 / 앱 / 검증 버저닝
- 데이터와 앱은 분리. 앱(`src/js/*`)은 데이터 버전에 독립.
- 앱이 fetch하는 파일은 `src/js/data.js`의 `DATA_URL` 한 곳에서 결정.
- **현재 라이브 = v0.1.** v0.2 전환은 Phase 3에서 `DATA_URL` 교체 + deploy.yml 검증 대상 교체로 수행.
- 스키마 변경은 **append-only**(필드 추가 가능, 기존 필드 의미 불변). 검색 인덱스 등은 런타임 생성, 데이터에 박지 않는다.
- validator는 버전별 분리:
  - `scripts/validate_medistack_v0_1_export.py|js` — v0.1 (고정 12항목, relations=19 고정).
  - `scripts/validate_medistack_v0_2_export.py|js` — v0.2 (일반화: relations≥19 + meta.relation_count 일치, 제품 필드 전면 금지, enum 경계, requires_clinical_review 차단 등).
- **버전 혼동 금지**: v0.1 데이터는 v0.1 validator로, v0.2 데이터는 v0.2 validator로만 검증.

## 3. 파일 구조
```
index.html · .nojekyll · README.md · CLAUDE.md
data/   medistack_v0.1_beta_export.json (봉인) · medistack_v0.2_beta_export.json (작업중)
src/css/styles.css
src/js/  app.js(라우터) · data.js(fetch+가드) · guards.js(렌더 규칙) · render.js · states.js
scripts/ validate_medistack_v0_1_export.(py|js) · validate_medistack_v0_2_export.(py|js)
docs/    card_render_spec.md · app_QA_testcases.md · (v0.2 계획서 등)
.github/workflows/ validate.yml(PR 검증) · deploy.yml(게이트 배포)
```

## 4. 렌더 규칙 (앱 수정 시 준수)
- `relations`만 렌더. `excluded_v0_1` 절대 안 건드림.
- 칼륨 고지: `potassium_safety_card === true` 플래그 기준(nutrient 문자열 매칭 금지).
- 제품 영역: v0.2는 없음. (게이트는 `product_link_allowed === true && 제품데이터` 인데 v0.2 데이터엔 제품 필드 자체가 없음)
- `disclaimers.common` 없으면 상세 렌더 차단(fail-safe).
- 로딩 실패/0건/필드 누락 → 안전 error/empty. "안전합니다/복용하세요" 류 금지.
- `status/published/clinical_reviewed` 필드는 읽지도 출력하지도 않는다.

## 5. 실행 / 검증 / 배포
- 로컬: `python3 -m http.server 8000` → http://localhost:8000 (fetch라 file:// 불가)
- 검증(배포 전 필수):
  - v0.1: `python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json`
  - v0.2: `python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json`
- CI: `.github/workflows/validate.yml`(PR, 두 버전 검증) / `.github/workflows/deploy.yml`(main push, validate→deploy 게이트, Pages Source=GitHub Actions).
- GitHub Actions 러너 Node24 전환 대응: `actions/checkout@v5`, `actions/setup-python@v6` 사용. Pages 액션은 현행 최신 major(configure-pages@v5 / upload-pages-artifact@v3 / deploy-pages@v4), Node24 경고 시 상향.

## 6. clinical reviewer 트랙 (v0.2 = 준비만)
- reviewer 요건·`review_log` 스키마·`reviewed_by`/`reviewed_at` 설계까지만 가능.
- **`clinical_reviewed=true` 전환·`published` 전환은 금지.** 실제 승격은 reviewer 확보 후 별도 버전.

## 7. v0.2 진행 상태 (승인됨)
- **Phase 0 ✅ done** — CLAUDE.md + Actions 버전업(checkout v5·setup-python v6) + v0.2 버저닝 구조.
- **Phase 1 ✅ done** — 검색/필터 앱 UX(guards/render/states/app + css). 브라우저 상호작용 수동 QA 미완.
- **Phase 2 ▶ next** — 15행 재검토 + 50건 확장 후보(데이터 트랙, `data/medistack_v0.2_beta_export.json`).
- **Phase 3** — v0.2 validator/QA/배포(라이브 DATA_URL·deploy 검증대상 v0.2 전환).

> Claude Code로 이어서 작업: **`docs/CLAUDE_CODE_KICKOFF.md`** 부터 보고 Phase 2 진행.

> 안전 원칙: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
