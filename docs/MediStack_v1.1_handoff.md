# MediStack v1.1 — handoff (다음 세션 인계 문서)

> 자기완결 인계 문서. v1.1-beta = full drug name index **10,000 → 17,580**(20k 시도 후 공급 천장) 확정 + 안정판 마감. 다음 세션은 이 문서만 읽고 이어갈 수 있다.
> 마감 판정 = `MediStack_v1.1_beta_release_readiness.md` · 확장 경위 = `MediStack_v1.1_20k_expansion_gate.md` §7 · 계획/후보 = `MediStack_v1.1_plan.md`.

## 1. 현재 repo / local / live 상태
- repo: `github.com/yoonspower/medistack` (PAT **push 만** 가능 · repo생성/Pages/재실행 403)
- local: `/Users/mac/AI work/medistack` · live: `https://yoonspower.github.io/medistack` (HTTP 200)
- 정적 SPA(ES module · 빌드 없음 · package.json 없음) + GitHub Actions(validate→deploy 게이트, **main push 시 자동 deploy** · **tag push 는 deploy 미발동**).

## 2. 최신 커밋 / 태그 / 라이브
- 최신: `cac9e03` Expand full drug index to 17,580 (20k attempt, supply ceiling) + 본 마감 docs 커밋.
- **태그: `v1.1-beta`** = 본 마감 docs 커밋 HEAD 에 annotated 생성(`full index 17,580 supply-ceiling stable snapshot`). 누적 = v0.1/v0.2/v0.3/v0.5/v0.6/v0.7/v0.8/v1.0-beta. v0.9·Phase2~6 무태그.
- 라이브 = main 자동배포. 수동 deploy / 무단 tag 금지.

## 3. 현재 데이터 수치 (v1.1-beta 기준선)
| 항목 | 값 |
|---|---|
| full drug name index | **17,580** (relation_card 558 + name_only 17,022) |
| full index md5 | `654d3e859e4a10213c0fa132094e2bfb` |
| target_total / target_attempted | 17,580 / 20,000 |
| alias_count (meta) | **621** (product 583 + ingredient 38) |
| verified_item_seqs | 545 entries / **13 canonical** |
| relations (v0.2 export) | **30** (+ excluded_v0_1 1) |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| export md5 | `401b097a1bd812b6da983b7f3dfc6d20` (불변) |
| alias md5 | `03fb21378da3c4520667350e03130866` (불변) |
| published / clinical_reviewed | false / false (봉인) · lifecycle = verified_reference |

## 4. 17,580 확장 요약 (Phase 6)
- 20,000 목표 → **17,580 공급 천장**(2,420 부족, force-fill 회피). pass1(45/12) +4,471 → 14,471 / pass2(80/25) +3,109 → 17,580. 누적 name_only +7,580.
- 천장 근거: pass2 중복률 **56%**(`rows_seen 30,096` / `excl_dup 16,829`) · `capped_at_target=false`.
- 방법: 성분 풀 485→**696**(EXT3 211종) · **4-shard 병렬**(`--shard I/K` + `merge_full_index_shards.py`). 원본 10,000 byte-identical 보존 · 편중 1.175% · blocked_standalone 0.

## 5. v1.1 트랙 산출물 (전부 데이터+문서, src 무변경)
| 트랙 | 산출물 | commit |
|---|---|---|
| 계획 | `docs/MediStack_v1.1_plan.md` | `ff5f363` |
| 20k 게이트 | `docs/MediStack_v1.1_20k_expansion_gate.md`(§7 실행 결과 포함) | `ff5f363`/`cac9e03` |
| Phase 6 확장 | `data/full_drug_name_index_sample_v1_0.json`(+.csv) 17,580 · `scripts/collect_full_drug_name_index_sample.py`(EXT3+shard 인자) · `scripts/merge_full_index_shards.py`(신규) · validator Phase 6 게이트·potassium 핀·fixture | `cac9e03` |
| 마감 | `docs/MediStack_v1.1_beta_release_readiness.md` · 본 handoff · `MediStack_v1.1_17580_release_notes.md` | (이번 커밋) |

## 6. validator / smoke 명령과 기대 결과 (17,580 기준)
```
python3 scripts/validate_full_drug_name_index.py                                          # 31/31 (+ --selftest PASS)
python3 scripts/validate_potassium_name_only_policy.py                                    # 8/8 blocked 0 (+ --selftest PASS)
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json    # 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json    # 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # 16/16
python3 scripts/validate_alias_surface_forms.py data/medistack_v0.3_aliases.json          # 5/5
python3 scripts/test_validate_v0_3_typeB.py    # 7/7      python3 scripts/test_validate_v0_3_combo.py   # 9/9
python3 scripts/test_validate_combo_ar.py      # 13/13    python3 scripts/validate_combo_approved_ready.py  # 13/13
python3 scripts/validate_bulk_alias_candidates.py         # 152/152
python3 scripts/smoke_search_regression_v1_0.py           # SEARCH REGRESSION PASS (A~H)
python3 scripts/smoke_hctz_disclosure.py                  # SMOKE PASS
python3 scripts/smoke_alias_regression.py                 # 회귀 7
python3 scripts/measure_full_index_performance.py data/full_drug_name_index_sample_v1_0.json  # gzip 497KB·build 4ms
```
- ⚠️ v0.1/v0.2/v0.3 validator 는 인자 없이 돌리면 sample 찾다 FATAL(default 경로에 `data/` 접두어 없음) → **라이브 파일 인자 필수**.
- ⚠️ guards/render ES module smoke·성능측정 은 `/tmp` 복사 + `.mjs`(또는 `{"type":"module"}`) 후 node(package.json 없음). guards.js 는 self-contained(import 0).

## 7. 절대 건드리면 안 되는 것 (불변)
- `data/full_drug_name_index_sample_v1_0.json`(+.csv) · `data/medistack_v0.3_aliases.json` · relation export(v0.1/v0.2) · queue 임의 수정 금지.
- relation 30 불변 · **DATA_URL** 불변 · data export(md5 `401b097a`) 불변 · alias(md5 `03fb2137`) 불변 · full index(md5 `654d3e85`) 불변.
- 앱 코드/UI(`src/`) 제품/구매/제휴 UI 금지 · **칼륨 제품링크 금지** · **name_only UX 문구 변경 금지** · name_only 의학정보 부착 금지.
- **HCTZ 외 복합제 basis 추가 금지** · **칼륨보존이뇨제 복합제 영구 차단** · **15행(id15)·에스오메프라졸 alias 금지**(id16×Mg 정상 live · 혼동 주의).
- 복합제는 부분정보 고지 동반(HCTZ 는 칼륨 반전 고지) · published/clinical_reviewed 봉인 · **full index 추가 확장은 별도 PM 승인.**
- 수동 deploy · 무단 tag(v1.1-beta 외) 금지 · `scripts/__pycache__` 커밋 금지 · commit 끝 Co-Authored-By trailer.

## 8. 다음 세션 선택지 (v1.1-beta 이후 · 각각 별도 PM 승인)
- **A. clinical reviewer 트랙** — 면허 검수자 확보 → `review_log`/`reviewed_by`/`reviewed_at` 플로우(설계=`MediStack_v1.0_clinical_reviewer_checklist.md`). published/clinical 봉인 해제는 **이 트랙에서만**. (가장 큰 잠금 해제 · 외부 사람 의존)
- **B. full index 20k 재시도(EXT4)** — 미수록 저빈도 성분 ~150-200개 추가 1-2패스. 17,580 → 20k. **수익 체감**(천장 근처). 트리거 "메디스택 20k 재시도".
- **C. full index 압축 / 분할 로딩 설계** — 30k+ 또는 gzip 임계 초과 신호 시. 지연 로드(검색 시 fetch) / 샤딩 / 사전 gzip 자산(plan §B).
- **D. 사용자 피드백 폼 / 문의 동선** — 정적 SPA 내 비침습 경로(제품/구매 UI 아님, mailto/폼 링크 수준).
- **E. v1.2 계획 수립** — 위 트랙 중 택1 + 차기 마일스톤 정의.

## 9. 다음 세션 시작 프롬프트 초안
> "MediStack v1.1-beta: full index 17,580, name_only 17,022, relation_card 558, alias 621, relation 30, DATA_URL 유지, 20k 시도 후 공급 천장으로 17,580 확정, live 200, validators PASS, published/clinical_reviewed false. tag `v1.1-beta` 생성됨(마감 docs HEAD). 다음 [A clinical reviewer / B 20k 재시도 EXT4 / C 압축·분할 로딩 / D 피드백 동선 / E v1.2 계획] 중 선택. 불변: full index/alias/queue 반영은 PM 명시 승인 batch만, relation 30·DATA_URL·data export·alias·full index md5 불변, 칼륨보존이뇨제 복합제·HCTZ외 basis·에스오메/15행 금지, name_only 의학정보 부착 금지, 복합제는 부분정보+(HCTZ)칼륨 반전 고지, published/clinical_reviewed 봉인, 수동 deploy·무단 tag 금지. handoff=docs/MediStack_v1.1_handoff.md · readiness=..._beta_release_readiness.md."

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / name_only 의학정보 부착 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전 고지) / relation 없는 약은 name_only 로만 표시 / full index 추가 확장은 별도 PM 승인.
