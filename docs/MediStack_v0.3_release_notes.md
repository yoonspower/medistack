# MediStack v0.3 beta — 릴리즈 노트

- **릴리즈명:** MediStack v0.3 beta
- **릴리즈 날짜:** 2026-06-08
- **라이브 URL:** https://yoonspower.github.io/medistack/
- **태그:** `v0.3-beta` → `d450081` (Wire v0.3 alias search into app + 합류 설계문서)
- **성격:** 식약처 허가사항 원문 기반 약-영양소 참고 정보 베타. 진단·처방·복약지시 아님. **이번 버전은 검색 UX 확장(상품명/영문 성분명 alias)** 중심이며, 관계 데이터(30건)·의학 내용은 v0.2와 동일.

---

## 1. 주요 변경사항
- **제품명/성분명 alias 검색 도입** — 상품명("타리비드"·"포사맥스"·"토렘"·"라식스"…)·영문 INN("levofloxacin"·"HCTZ"…)으로도 검색되게 런타임 alias 인덱스 추가. 결과는 검증된 성분 relation으로 연결.
- **alias 안내 1줄** — alias로만 매칭됐을 때 결과 상단에 `'{검색어}' 검색어는 {성분명} 관련 정보로 연결됩니다.` 표시(직접 성분/영양소 검색이면 미표시). 제품 정보/추천 아님.
- **운영 alias 데이터 신설** — `data/medistack_v0.3_aliases.json` (성분 29 + 제품 24 = **53개**, live 14성분 중 13성분 제품 커버). relation JSON과 **별도 파일**, 앱이 독립 fetch.
- **alias validator 신설** — `scripts/validate_medistack_v0_3_aliases.py` (11 checks): canonical_ingredient 실재, relation_id 15·excluded 연결 금지, 에스오메프라졸 제품 alias 금지, 중복/빈 alias 금지, 제품 필드 금지 등.
- **CI 게이트 강화** — `validate.yml`(PR)·`deploy.yml`(배포 전) 둘 다 v0.1+v0.2+**v0.3 alias** 3종 검증. 셋 다 PASS여야 배포.
- **운영위생** — GitHub Actions Pages 액션 Node24 상향(configure-pages@v6 / upload-pages-artifact@v5 / deploy-pages@v5), Node20 deprecation 경고 소거(2026-06-16 데드라인 선제 대응).

## 2. alias 동작 / 안전 설계
- **검색 보조 전용** — alias는 의학정보가 아니며 alias만으로 relation을 새로 만들지 않는다.
- **prefix(startsWith) 매칭** — alias 표면형은 접두 매칭. (QA 중 "ofloxacin"이 substring으로 levo/ciprofloxacin에 오매칭되던 버그를 prefix로 차단. canonical은 정확 일치로 relation 매칭.) 직접 ingredient/nutrient 검색은 기존 substring 유지.
- **풀 불확장(우회 차단)** — 검색 후보는 항상 `getRenderableRelations` 결과뿐. alias는 "무엇을 질의로 칠지"만 넓힐 뿐 풀을 못 넓힘 → **excluded_v0_1/15행은 alias로도 진입 불가**(구조적). + alias 파일에 15행·에스오메프라졸 제품 alias 부재(validator 강제).
- **fail-soft** — alias 파일 fetch/파싱 실패 시 relation-only 검색으로 graceful degrade(앱 에러 없음, console.warn만).

## 3. 유지 / 보류 사항
- **relation 데이터 30건 불변** — v0.2 export 그대로(`DATA_URL`=v0.2). 건수·내용·md5 변화 없음.
- **15행(에스오메프라졸×비타민B12) excluded 유지** — alias로도 미노출.
- **에스오메프라졸 alias 보류** — 제품 alias 금지 확정. 성분 alias(esomeprazole→id 16 Mg, live)도 v0.3 보류(id 15 혼선 우려). id 16은 "에스오메프라졸"/"마그네슘" 직접 검색으로만 도달. 15행 재검토 또는 후속 alias policy 정리 후 재판정.
- **published / clinical_reviewed 미사용** — 천장 = verified_reference(봉인).
- **제품 / 제휴 UI 없음** — 제품 링크·구매·예시·제품 필드 전면 금지. alias도 제품 추천 표현 아님.

## 4. 안전 고지 (v0.2와 동일 유지)
- 칼륨 행 [17, 19, 30]: `potassium_safety_card=true`, `product_link_allowed=false`, potassium_notice 표시, 제품 UI 없음.
- 공통 면책문구(disclaimers.common) 모든 상세 표시(fail-safe).
- 의료 단정·복용 지시·위험 확정·구매 유도 표현 없음. 검색 0건은 "안전"이 아니라 미수록 안내로 표시.

## 5. 라이브 QA 결과 (https://yoonspower.github.io/medistack/, 2026-06-08)
- HTTP 200 / 콘솔 에러 0 / DATA_URL=v0.2 / 목록 30건.
- alias 검색: "타리비드"→오플록사신 3건 · "포사맥스"→알렌드론산 1건 · "토렘"→토라세미드 2건. 안내 1줄 정상.
- "넥시움"→0건(에스오메프라졸 보류). 직접 검색("오플록사신")은 안내 미표시.
- `#/r/15`→fail-safe error(B12/에스오메프라졸 누출 없음).
- 제품/구매/제휴 UI 없음. 칼륨 고지 정상.
- deploy run `27110184181` success(validate v0.1+v0.2+v0.3 alias 3종 PASS).

## 6. 태그 정보
- `v0.3-beta` → `d450081`
- 직전: `v0.2-beta` → `10ef892` · `v0.1-beta` → `b330c59`
- v0.3 커밋 범위(10ef892..d450081): roadmap → alias 설계/seed/운영seed → sample+validator → 운영 alias JSON → CI 게이트 → Node24 → 앱 합류(코드+설계문서).

## 7. 다음 버전(v0.4) 후보
- **alias 운영 확장** — 53 → 100~150(운영 seed plan §3). 교차확인 2번째 품목 alias 포함 여부.
- **제네릭 대량 alias** — 전체 품목 alias 수집(300 밴드는 v0.4 궤도).
- **에스오메프라졸/15행 재검토** — 성분 alias 편입 정책 확정.
- **미등록 약 안내 UX 강화(UX-B)** — 검색 0건이 "안전"으로 오인되지 않게 전용 안내·요청 경로.

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지.
