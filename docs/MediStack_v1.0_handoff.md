# MediStack v1.0 — handoff (다음 세션 인계 문서)

> 자기완결 인계 문서. v1.0 = 안정판 트랙(A clinical reviewer checklist / B full drug index 설계 / C 검색 회귀 smoke). 다음 세션은 이 문서만 읽고 이어갈 수 있다.
> 마감 판정 = `MediStack_v1.0_beta_release_readiness.md`.

## 1. 현재 repo / local / live 상태
- repo: `github.com/yoonspower/medistack` (PAT push 만 가능 · repo생성/Pages/재실행 403)
- local: `/Users/mac/AI work/medistack` · live: `https://yoonspower.github.io/medistack` (HTTP 200)
- 정적 SPA(ES module · 빌드 없음 · package.json 없음) + GitHub Actions(validate→deploy 게이트, main push 시 자동 deploy)

## 2. 최신 커밋 / 태그 / 라이브
- 최신: `e75f65c` Add v1.0 search regression smoke coverage (+ 본 마감 docs 커밋)
- **태그: v0.9·v1.0 미생성**(현 세션 금지). 누적 = v0.1/v0.2/v0.3/v0.5/v0.6/v0.7/v0.8-beta.
- 라이브 = main 자동배포(alias 621). 수동 deploy / 무단 tag 금지.

## 3. 현재 데이터 수치 (621 기준)
| 항목 | 값 |
|---|---|
| alias_count (meta) | **621** |
| ingredient_aliases | 38 |
| product_aliases | 583 (단일 + 복합제 110 + brand_core 14 + HCTZ 112 + 표면형 3) |
| verified_item_seqs | 545 entries / **13 canonical** |
| relations (v0.2 export) | 30 (+ excluded_v0_1 1) |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| export md5 | `401b097a1bd812b6da983b7f3dfc6d20` (불변) |
| published / clinical_reviewed | false / false (봉인) · lifecycle = verified_reference |

## 4. v1.0 트랙 산출물 (전부 문서/테스트, 데이터·src 무변경)
| 트랙 | 산출물 | commit |
|---|---|---|
| 계획 | `docs/MediStack_v1.0_plan.md` | `2edbdcc` |
| A | `docs/MediStack_v1.0_clinical_reviewer_checklist.md` | `fa6aab3` |
| B | `docs/MediStack_v1.0_full_drug_search_index_design.md` | `a3a8272` |
| C | `scripts/smoke_search_regression_v1_0.py` · `scripts/fixtures/search_regression_v1_0.json` · `docs/MediStack_v1.0_search_regression_smoke_report.md` | `e75f65c` |
| D | `docs/MediStack_v1.0_beta_release_readiness.md` · 본 handoff | (이번 커밋) |

## 5. 실행 가능한 주요 스크립트 (전부 repo 보존)
- **검증** `validate_medistack_v0_1_export.py`(12) · `validate_medistack_v0_2_export.py`(15) · `validate_medistack_v0_3_aliases.py`(16) · `validate_alias_surface_forms.py`(5) · `test_validate_v0_3_typeB.py`(7) · `test_validate_v0_3_combo.py`(9) · `test_validate_combo_ar.py`(13) · `validate_combo_approved_ready.py`(13) · `validate_bulk_alias_candidates.py`(152).
- **smoke** `smoke_alias_regression.py`(브랜드 회귀 7) · `smoke_hctz_disclosure.py`(칼륨 반전 고지) · **`smoke_search_regression_v1_0.py`(검색/고지/empty/degrade ~70, 실제 guards.js+render.js)**.
- ⚠️ guards/render ES module smoke 는 `/tmp` 복사 + `{"type":"module"}` 후 node(package.json 없음). render.js 는 guards.js 를 import → 둘 다 복사.
- ⚠️ alias 실제 반영은 스크립트화 안 함 — PM 승인 후 ephemeral `/tmp/ms_incorporate_*.py`(미커밋).

## 6. validator / smoke 명령과 기대 결과 (621 기준)
```
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json   # 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json   # 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # 16/16
python3 scripts/validate_alias_surface_forms.py data/medistack_v0.3_aliases.json          # 5/5
python3 scripts/test_validate_v0_3_typeB.py            # 7/7
python3 scripts/test_validate_v0_3_combo.py            # 9/9
python3 scripts/test_validate_combo_ar.py              # 13/13
python3 scripts/validate_combo_approved_ready.py       # 13/13
python3 scripts/validate_bulk_alias_candidates.py      # 152/152
python3 scripts/smoke_alias_regression.py              # 회귀 7
python3 scripts/smoke_hctz_disclosure.py               # SMOKE PASS
python3 scripts/smoke_search_regression_v1_0.py        # SEARCH REGRESSION PASS
```
- ⚠️ v0.1/v0.2/v0.3 validator 는 인자 없이 돌리면 sample 찾다 FATAL → 라이브 파일 인자 필수.

## 7. 절대 건드리면 안 되는 것 (불변)
- `data/medistack_v0.3_aliases.json` · queue 임의 수정 금지(반영은 PM 명시 승인 batch만 · incorporation-aware).
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · **DATA_URL** 불변 · data export(md5 `401b097a`) 불변.
- 앱 코드/UI(`src/`) 제품/구매/제휴 UI 금지 · **칼륨 제품링크 금지**.
- **HCTZ 외 복합제 basis 추가 금지** · **칼륨보존이뇨제 복합제 영구 차단** · **15행(id15)·에스오메프라졸 alias 금지**(id16×Mg 는 정상 live·혼동 주의).
- 복합제는 부분정보 고지 동반(HCTZ 는 칼륨 반전 고지) · published/clinical_reviewed 봉인.
- 수동 deploy · 무단 tag 금지 · `scripts/__pycache__` 커밋 금지.

## 8. 다음 세션 선택지 (v1.0 이후)
- **full drug index Phase 2 (1,000 샘플)**: `full_drug_name_index` 데이터 생성(nedrug searchDrug→getItemDetail 보수적) + 신 validator. 설계=`MediStack_v1.0_full_drug_search_index_design.md`. 회귀 baseline=`search_regression_v1_0`(name_only 도입 시 `full_index_future_baseline` 그룹 기대값 갱신).
- **name_only UX 구현**: `src/` FULL_INDEX_URL fail-soft + 3-상태 라우팅(relation_card / name_only / empty). 별도 게이트 · 회귀 smoke 필수.
- **clinical reviewer 트랙**: 면허 검수자 확보 → review_log 스키마 별도 버전 적용 → relation 단위 승격. 설계=`MediStack_v1.0_clinical_reviewer_checklist.md`.
- **v1.0-beta 태그**: PM 명시 승인 시 `e75f65c`(또는 마감 커밋) lightweight 스냅샷(deploy 미발동). tag-ready 판정=readiness 문서 §10.

## 9. 다음 세션 시작 프롬프트 초안
> "MediStack v1.0 안정판 마감(alias 621 라이브 · commit `e75f65c` · tag 미생성). 621 = 단일382 + 복합제110(메트/알렌/오메) + brand_core14 + HCTZ112 + 표면형3. v1.0 트랙 A(clinical reviewer checklist)/B(full drug index 설계)/C(검색 회귀 smoke) 완료, D(release readiness+handoff) 마감. 다음 [full drug index Phase2 1000샘플 / name_only UX 구현 / clinical reviewer 확보 / v1.0-beta 태그] 중 선택. 불변: alias/queue 반영은 PM 명시 승인 batch만, relation 30·DATA_URL·data export 불변, 칼륨보존이뇨제 복합제·HCTZ외 basis·에스오메/15행 금지, 복합제는 부분정보+(HCTZ)칼륨 반전 고지, published/clinical_reviewed 봉인, 수동 deploy·무단 tag 금지. handoff=docs/MediStack_v1.0_handoff.md · readiness=..._beta_release_readiness.md."

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반 / relation 없는 약은 (도입 후) name_only 로만 표시.
