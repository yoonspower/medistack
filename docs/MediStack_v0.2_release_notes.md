# MediStack v0.2 beta — 릴리즈 노트

- **릴리즈명:** MediStack v0.2 beta
- **릴리즈 날짜:** 2026-06-07
- **라이브 URL:** https://yoonspower.github.io/medistack/
- **태그:** `v0.2-beta` → `10ef892` (Merge PR #1 `yoonspower/v0.2-dev` → `main`)
- **성격:** 식약처 허가사항 원문 기반 약-영양소 참고 정보 베타. 진단·처방·복약지시 아님.

---

## 1. 주요 변경사항
- **관계 데이터 19건 → 30건** (식약처 nedrug 허가사항 원문 검증 기반, evidence high/moderate, antagonism·임상판단 행 제외).
- **신규 11건 추가** (Phase 2-B: 플루오로퀴놀론·테트라사이클린·비스포스포네이트·루프이뇨제).
- **검색/필터 기능** — 목록 화면에 약물명·영양소명 검색 + 영양소/액션 facet 필터(데이터에서 동적 도출, 30건 기준 동작).
- **v0.2 validator 신설** (`scripts/validate_medistack_v0_2_export.*`) — relations≥19 + `meta.relation_count` 일치, 제품 필드 전면 금지, enum 경계, `requires_clinical_review` 차단, 칼륨 일관성 등 15항목.
- **v0.1 archived integrity 유지** — v0.1 데이터(19건)는 봉인·보존, deploy 게이트에서 무결성 계속 검증.
- **deploy gate 강화** — `deploy.yml` validate job이 v0.1(archived)+v0.2(live) **둘 다 PASS**여야 배포. PR 검증(`validate.yml`)도 두 버전 검사. (Actions: checkout@v5 / setup-python@v6)

## 2. 신규 추가 관계 (id 21~31)
| id | 약물 × 영양소 | action / mechanism / evidence | 대표품목 (itemSeq) |
|---|---|---|---|
| 21 | 오플록사신 × 칼슘 | separation / absorption / high | 제일타리비드정 (198600307) |
| 22 | 오플록사신 × 철분 | separation / absorption / high | 제일타리비드정 (198600307) |
| 23 | 오플록사신 × 마그네슘 | separation / absorption / high | 제일타리비드정 (198600307) |
| 24 | 목시플록사신 × 철분 | separation / absorption / high | 리목스정400mg (201402438) |
| 25 | 목시플록사신 × 마그네슘 | separation / absorption / high | 리목스정400mg (201402438) |
| 26 | 미노사이클린 × 칼슘 | separation / absorption / high | 미노씬캡슐50mg (198501028) |
| 27 | 미노사이클린 × 철분 | separation / absorption / high | 미노씬캡슐50mg (198501028) |
| 28 | 미노사이클린 × 마그네슘 | separation / absorption / high | 미노씬캡슐50mg (198501028) |
| 29 | 알렌드론산 × 칼슘 | separation / absorption / high | 포사맥스70밀리그램정 (200009061) |
| 30 | 토라세미드 × 칼륨 | monitoring / depletion / high | 토렘정5밀리그람 (200611522) |
| 31 | 토라세미드 × 마그네슘 | monitoring / depletion / moderate | 토렘정5밀리그람 (200611522) |

- 모든 신규 행은 **사용상의 주의사항 번호항 직접 문구**로 검증. 신규 클래스(비스포스포네이트)·안전민감(칼륨) 행은 **동일 성분 2번째 품목 교차확인** 수행.
- 검증 제외 사례: 목시플록사신 × 칼슘(라벨상 상호작용 없음 명시), 레보티록신 × 마그네슘(라벨에 마그네슘 직접 문구 없음) → 원문보다 강한 해석 방지 위해 미편입.

## 3. 유지 / 제외 사항
- **15행(에스오메프라졸 × 비타민B12) excluded 유지** — 대표 품목 2종(넥시움정 200009027, 에소메프라정 201600209) 확인 결과 B12는 이상반응 목록 수준이며 흡수장애·모니터링 주의사항 문구 부재. 승격 시 원문보다 강한 해석이 되어 제외 유지. (cf. 오메프라졸은 주의사항에 B12 흡수장애 문구 보유 → id 13 성립.)
- **published / clinical_reviewed 미사용** — clinical reviewer 확보 전까지 천장 = verified_reference (봉인 유지).
- **제품 / 제휴 UI 없음** — 제품 링크·구매 버튼·제품 예시·제품 필드 전면 금지(v0.2).
- **v0.1 데이터 봉인** — 직접 수정 없음(md5 불변), 아카이브 보존.

## 4. 안전 고지
- **칼륨 행 [17, 19, 30]** (푸로세미드·히드로클로로티아지드·토라세미드 × 칼륨): `potassium_safety_card=true`, `product_link_allowed=false`. 상세에 potassium_notice("칼륨은 임의로 보충하면 위험할 수 있습니다. 보충 여부는 반드시 의사 또는 약사와 상담하세요. (제품 예시 미제공)") 표시, 제품 링크/예시/구매 버튼 없음.
- **공통 면책문구(disclaimers.common)** 모든 상세에 표시(fail-safe): "이 정보는 식약처 허가사항 등을 바탕으로 정리한 참고 정보입니다. 진단, 처방, 복약 지시가 아니며, 실제 복용 여부나 시간 간격은 의사 또는 약사와 상담하세요."
- 의료 단정·복용 지시·위험 확정·구매 유도 표현 없음.

## 5. QA 결과 요약 (라이브 https://yoonspower.github.io/medistack/)
- 목록 30건 / 콘솔 에러 0 / v0.2 JSON HTTP 200
- 검색: 토라 2 · 오플 3 · 미노 3 · 목시 2 · 알렌 1
- 칼륨 필터 단독 → 3건(#/r/17·19·30)
- 신규 11건 상세: 본문 + 공통면책 + 출처(itemSeq) 표시, 제품/구매 UI 없음
- 칼륨 17·19·30: potassium_notice 표시, 제품 UI 없음
- excluded 15행: `#/r/15` error 화면(미노출)
- published/clinical 문구 없음
- **라이브 QA 전체 통과 / rollback 불필요**
- validator: v0.1 PASS 12/12 · v0.2 PASS 15/15
- deploy workflow run 27089854841 success

## 6. 태그 정보
- `v0.2-beta` → `10ef892` (Merge pull request #1 from yoonspower/v0.2-dev)
- 직전: `v0.1-beta` → `b330c59`

## 7. 다음 버전(v0.3) 후보
- **제품명 alias** — 상품명·브랜드명으로도 검색되도록 성분↔제품명 alias 인덱스(런타임 생성, 데이터 append-only).
- **미등록 약 안내 UX** — 검색 결과 없음이 "안전/관계 없음"으로 오인되지 않도록 미등록 약 전용 안내 문구·요청 경로.
- **100건 목표 확장** — 추가 약효군 단계 확장(행별 식약처 원문 SOP 유지, 품질 우선).
- **사용자 검색 기반 후보 관리** — 검색 로그(미등록·빈결과 쿼리)를 확장 후보 큐레이션에 활용하는 운영 트랙.

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지.
