# MediStack — 베타 앱 (v0.1)

식약처 허가사항을 바탕으로 정리한 **약-영양소 참고 정보** 베타 앱. 진단·처방·복약지시가 아니다.
빌드 없는 정적 ES module 앱. GitHub Pages 배포.

## 프레임 (불변)
- v0.1은 **verified_reference 기반 베타 참고정보**. clinical reviewer 부재 → **published/clinical_reviewed 사용·표시 금지.**
- 앱 노출 = **relations 19건만.** `excluded_v0_1`는 렌더 금지(내부 QA/관리용).
- v0.1은 **제품/제휴 UI 없음**(데이터에 제품 필드 0).
- 의학적 단정 / 복용 지시 / 구매 유도 카피 금지.

## 폴더 구조
```
medistack-app/
├─ index.html                # 앱 셸 (ES module 로드)
├─ .nojekyll                 # GitHub Pages Jekyll 우회
├─ README.md
├─ data/
│  └─ medistack_v0.1_beta_export.json   # v0.1 final package 복사본(직접 편집 금지)
├─ src/
│  ├─ css/styles.css
│  └─ js/
│     ├─ app.js              # entry + 해시 라우터(#/ , #/r/:id)
│     ├─ data.js             # fetch + shape 가드(실패 시 throw)
│     ├─ guards.js           # 렌더 규칙(relations-only/칼륨·제품 게이트/common fail-safe)
│     ├─ render.js           # list/detail 렌더
│     └─ states.js           # empty/error 렌더
├─ scripts/
│  ├─ validate_medistack_v0_1_export.py
│  └─ validate_medistack_v0_1_export.js
├─ docs/
│  ├─ MediStack_v0.1_card_render_spec.md
│  └─ MediStack_v0.1_app_QA_testcases.md
└─ .github/workflows/validate.yml
```

## 로컬 실행
fetch 기반이라 `file://` 직접 열기는 CORS로 안 됨. 로컬 서버 필요(빌드·npm 불필요):
```
cd medistack-app
python3 -m http.server 8000
# http://localhost:8000 접속
```
딥링크: `#/` 목록, `#/r/1` 1번 상세, `#/r/17` 칼륨 상세.

## 배포 전 검증
```
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json
```
PASS(exit 0) 아니면 데이터부터 수정, 배포 중단.

## GitHub Pages 배포 (Actions 소스, 게이트 포함)
1. repo 푸시(main).
2. Settings → Pages → Build and deployment → **Source → "GitHub Actions"**.
3. `deploy.yml` 이 main push 시 실행 → **validate 통과 후에만 deploy.** (Source 를 Actions 로 먼저 바꾼 뒤 push)
4. Actions 탭에서 deploy-pages 성공 시 라이브 URL: `https://<user>.github.io/<repo>/`.
- 앱은 상대경로라 서브패스 base 설정 불필요. `.nojekyll` 포함으로 src/·.github/ 정상 서빙.
- 단순 대안: Source 를 "Deploy from a branch"(main / root)로 두면 즉시 배포되지만 **데이터 검증 게이트가 없다.**

## 워크플로 (CI / 배포)
두 워크플로로 분리, 역할 명확(같은 이벤트 중복 실행 없음):
- `.github/workflows/validate.yml` — **PR 검증 전용.** data/·scripts/ 변경 PR에서 validator 실행. 브랜치 보호 required status check 로 사용 가능.
- `.github/workflows/deploy.yml` — **프로덕션 배포(게이트 포함).** main push 시 `validate` job 통과 후에만 `deploy` job 실행(`needs: validate`). Pages 표준 구성(configure-pages → upload-pages-artifact → deploy-pages), permissions(contents:read / pages:write / id-token:write), concurrency(group: pages).
- 비중복 원칙: **PR → validate.yml**, **main push → deploy.yml(자체 validate gate)**. validate.yml 은 main push 에 트리거되지 않아 검증이 두 번 돌지 않음.
- 로컬 사전 검증: `python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json`

## 배포 게이트
- validator PASS(12/12, exit 0).
- QA P0 10건 전부 PASS(`docs/MediStack_v0.1_app_QA_testcases.md`).
- 안전 핵심 4선 미통과 시 배포 금지: B8 15행 미노출 / B9 전 상세 공통 면책문구 / B10 칼륨 제품링크·예시 차단 / B14 empty·error 의학 단정 금지.

> 안전 원칙: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
