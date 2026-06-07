# Claude Code Kickoff — MediStack v0.2

이 repo를 Claude Code로 이어서 작업한다. **먼저 `CLAUDE.md`를 읽고 시작.**

## 0. 먼저 읽기 (순서)
1. `CLAUDE.md` — 리포 가드레일·불변원칙 (작업 전 필수)
2. `docs/MediStack_v0.2_scope_and_plan.md` — v0.2 스코프 + PM 승인 결정
3. `docs/MediStack_v0.2_phase1_search_filter_design.md` — 검색/필터 설계
4. `docs/MediStack_v0.1_card_render_spec.md`, `docs/MediStack_v0.1_app_QA_testcases.md`

## 1. 현재 상태 (2026-06-07)
- v0.1 라이브: https://yoonspower.github.io/medistack/ (repo yoonspower/medistack). v0.1 데이터 봉인.
- **Phase 0 done**: CLAUDE.md / Actions 버전업(checkout v5·setup-python v6) / v0.2 버저닝 구조(`data/medistack_v0.2_beta_export.json` + `scripts/validate_medistack_v0_2_export.py|js`).
- **Phase 1 done**: 검색/필터 구현(`src/js/guards.js,render.js,states.js,app.js` + `src/css/styles.css`). **단, 브라우저 상호작용(클릭/입력/포커스) 수동 QA는 미완** → 로컬 서버 띄워 확인 필요.
- validator: v0.1 PASS 12/12, v0.2 PASS 15/15.

## 2. 다음 = Phase 2 (데이터 트랙)
- **15행 에스오메프라졸×B12 재검토**: 식약처 nedrug 에스오메프라졸 대표 품목(넥시움 등) 허가사항에서 B12 흡수장애 **직접 문구** 확인 → 있으면 verified 승격 + `direct_item_label_confirmed=YES` → relations 편입. 없으면 **excluded 유지**(published 승격 아님).
- **20→50 확장**: 신규 약-영양소 행. 행별 **식약처 원문 SOP 검증**(허가사항 원문 > e약은요 > 해외 라벨, DUR 1차 출처 금지). **evidence high/moderate만, antagonism 금지.**
- 작업 대상 = **`data/medistack_v0.2_beta_export.json`** (v0.1 직접 수정 금지). 행 추가 시 `meta.relation_count`/`excluded_count` 갱신.
- 신규 칼륨류 추가 시: `product_link_allowed=false` + `potassium_safety_card=true`.
- 이후 **Phase 3**: v0.2 validator/QA/배포. 라이브 전환 = `src/js/data.js`의 `DATA_URL`을 v0.2로 + `deploy.yml` 검증대상을 v0.2로.

## 3. 불변 (위반 금지)
`data/*` 직접수정 금지(v0.2 신규 파일) / relations-only(`excluded_v0_1`·row_id 15 노출 금지) / 제품·제휴·published·clinical 뱃지·문구 금지 / 상세 `disclaimers.common` fail-safe / 칼륨 `potassium_notice`+제품차단 / **validator PASS 없으면 커밋·배포 금지** / 의료 단정·복용 지시·구매 유도 금지.

## 4. 실행 / 게이트
```
# 로컬 (fetch라 file:// 불가)
python3 -m http.server 8000   # http://localhost:8000

# 배포 전 필수 (둘 다 PASS여야 함)
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json
```
- CI: `.github/workflows/validate.yml`(PR, 두 버전 검증) / `deploy.yml`(main push, validate→deploy 게이트, Pages Source=GitHub Actions).
- v0.2 validator는 relations 수를 `meta.relation_count`와 대조하므로, 행 추가 시 meta도 같이 갱신해야 PASS.

> 안전 원칙: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
