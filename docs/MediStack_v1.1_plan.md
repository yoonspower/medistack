# MediStack v1.1 — 계획 / 기준선 핸드오프

> 작성일: 2026-06-13. v1.0/10k 완료 직후의 v1.1 기준선·후보·우선순위 정리.
> **문서 전용**(데이터/코드/인덱스 무변경). 20k 상세 게이트 = `MediStack_v1.1_20k_expansion_gate.md`.
> 선행: `MediStack_v1.0_full_drug_index_10k_stability_report.md` + `..._10k_handoff.md` + `CLAUDE.md`.

---

## 1. 현재 기준선 (v1.0 / 10k, 라이브)

| 항목 | 값 |
|---|---|
| HEAD | `6fb8046` (Document v1.0 full index 10k stability) |
| full drug name index | **17,580** (v1.1 Phase 6 — 10,000 → 17,580, 20k 시도 후 공급 천장) |
| relation_card | **558** (고정) |
| name_only | **17,022** |
| alias_count | **621** (product 583 + ingredient 38) |
| product_aliases | 583 |
| verified_item_seqs | 545 / 13성분 |
| relations | **30** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| export md5 | `401b097a` (불변) |
| full index md5 | `5fb8ee96` |
| published / clinical_reviewed | **false / false** (봉인) |
| live | HTTP 200 (site · full index · alias · export 전부) |
| tag | `v1.0-beta = 51b3442` (Phase 2~5는 무태그) |

## 2. 10k에서 완료된 것

- **name_only UX** (Phase 3, src 5파일): data.js fail-soft `loadFullIndex` → guards.js `buildNameOnlyIndex`/`searchNameOnly`(의학필드 미반입) → render.js 비클릭 정보카드 → app.js 3상태 라우팅(relation_card / name_only / empty).
- **full index validator** (`validate_full_drug_name_index.py`, 31체크): 불변값·금지필드·Phase 5 게이트(`target_total>=10000 → total>=10000`).
- **potassium name_only blocklist validator** (`validate_potassium_name_only_policy.py`, 8체크 + selftest): standalone 칼륨보충제 차단. 10k에서 blocked 0 / manual_review 6 / allowed 283.
- **search regression smoke** (`smoke_search_regression_v1_0.py`, A~H): 실제 guards.js + render.js, relation_card / combo / HCTZ / empty / surface / degrade / name_only / 배선 불변.
- **10k stability report + handoff** (`..._10k_stability_report.md`, `..._10k_handoff.md`).
- **성능 측정** (`measure_full_index_performance.py`): gzip 278KB · 모바일 ~58ms · 검색 ≤0.31ms (리포트용, CI 하드게이트 아님).
- **라이브 QA**: 게보린/노바스크/이부/아세트 → name_only, 타리비드 3/포사맥스 1/토렘 2 → relation_card, HCTZ combo 칼륨 고지, 넥시움/에스오메/asdfqwer → 0.

## 3. v1.1 후보

- **A. 20k full index 확장** — name_only 9,442 → ~19,442. 성능상 여유(외삽). 단 수집 천장·다양성·nedrug 부하 별도 검토. 상세 게이트 = `MediStack_v1.1_20k_expansion_gate.md`.
- **B. full index 압축 / 분할 로딩 설계** — 30k+ 또는 임계 초과 신호 발생 시. 지연 로드(검색 시 fetch) / 샤딩 / 사전 gzip 자산.
- **C. clinical reviewer 트랙** — relation / 의학정보 확장은 reviewer 확보 후. published/clinical 봉인 해제는 **이 트랙에서만**.
- **D. 정식 v1.1-beta 문서 / 태그** — 10k 확장 + 안정화를 v1.1 마일스톤으로 확정(태그는 PM 승인 시에만).
- **E. 외부 피드백 폼 / 사용자 문의 동선** — 정적 SPA 내 비침습 피드백 경로(제품/구매 UI 아님, 단순 mailto/폼 링크 수준).

## 4. 추천 우선순위

1. **20k 확장 전 gate 문서화** — 본 v1.1 세트(완료).
2. **20k 확장** — gate 통과 + 별도 PM 승인 시.
3. **성능 부담 발생 시 압축 / 분할 로딩** — 20k에서 임계 초과 신호 없으면 보류.
4. **clinical reviewer** — 별도 트랙, 의학 검수 자원 필요.

## 5. 절대 금지 (v1.1 공통 불변)

- **relation 확장 금지** (30 고정 · 신규 생성 금지 · 풀 확장 금지).
- **alias JSON(`medistack_v0.3_aliases.json`) 수정 금지** (621 고정).
- **DATA_URL 변경 금지** (`./data/medistack_v0.2_beta_export.json`).
- **data export 변경 금지** (md5 `401b097a`).
- **clinical_reviewed / published 임의 변경 금지** (봉인 · 천장 = verified_reference).
- **제품 / 구매 / 제휴 UI 금지.**
- **name_only에 의학적 판단(상호작용/영양소/복용지시/관리/칼륨 보충안내) 표시 금지** — 품목명 확인 보조일 뿐.
- 추가 불변: 15행(에스오메프라졸×B12 id15) 미노출·재편입 금지 / 에스오메프라졸 alias 금지(id16×Mg는 정상 live) / 칼륨 제품링크 금지 / 칼륨보존이뇨제 복합제 영구 차단(HCTZ 외 복합제 basis 금지).
- 운영: 수동 deploy·무단 tag 금지(PAT push만, main push가 deploy 트리거) · `scripts/__pycache__/` 커밋 금지.
