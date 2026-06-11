# MediStack v0.5 — handoff (다음 세션 인계 문서)

작성일: **2026-06-11** / 대상: 다음 작업 세션(Claude Code/PM) / 상위: `MediStack_v0.5_release_notes.md`, `..._bulk_alias_pipeline_plan.md`

> v0.5 bulk alias pipeline 1차 마감 시점의 자기완결적 인계 문서. **alias 206 라이브, v0.5 목표 200 달성.** 코드/데이터는 안정 상태이며 다음 단계는 선택적.

---

## 1. 현재 repo / local / live 상태
- **repo**: `yoonspower/medistack` (public, GitHub), 브랜치 `main`. push = fine-grained PAT(push 전용 — repo 생성/Pages/워크플로우 재실행은 403, 사용자 웹 또는 빈 커밋으로 우회).
- **local**: `/Users/mac/AI work/medistack` (git clean, main == origin/main).
- **live**: https://yoonspower.github.io/medistack/ (GitHub Pages, Source=GitHub Actions). HTTP 200.
- **배포**: main push → `.github/workflows/deploy.yml`(validate 게이트 → deploy). `validate.yml`(PR 검증). **수동 deploy 금지**(Actions만).

## 2. 최신 커밋 / Actions / 라이브
- latest commit: **`995ce2d`** "Add v0.5 approved-ready product aliases batch 5".
- Actions run: **`27336943120`** success (validate + deploy).
- 라이브 alias_count: **206** (이 문서 커밋 후엔 문서만 추가되어 alias 불변).
- tag: `v0.1-beta` · `v0.2-beta` · `v0.3-beta` 만 존재. **v0.5 태그 미생성**(PM 별도 지시 대기).

## 3. 현재 데이터 수치
| 항목 | 값 |
|---|---|
| meta.alias_count | 206 |
| product_aliases | 168 |
| ingredient_aliases | 38 |
| verified_item_seqs | 144 entries / 12 canonical |
| relations (v0.2 export) | 30 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` |
| queue 총 | 319 (pending 58 · approved 140 · rejected 2 · deferred 119) |
| held(batch6 가능) | 51 |
| deferred | 119 (복합제 combo ~105 + brand_core 14) |

## 4. 실행 가능한 주요 스크립트
- **수집** `scripts/collect_nedrug_alias_candidates.py` — nedrug searchDrug 후보 수집(외부 네트워크). 핵심 옵션: `--max-per-ingredient N` · `--max-pages N`(페이지당 15행) · `--batch-id <id>` · `--phase N` · `--no-network`(병합/정규화만) · `--limit-ingredients N`. 중복제거: surface∉alias·∉queue·itemSeq∉alias·item_name∉alias. **alias JSON 미수정**(dry-run 기본).
- **상세확정** `scripts/confirm_nedrug_item_details.py` — getItemDetail 원문확정 + approved-ready 생성. 옵션: `--target-batch <id>`(해당 batch 신규만) · `--no-network` · `--ar-only-batch <id>` · `--ar-balanced`(canonical 라운드로빈) · `--ar-limit N` · `--ar-batch-id <id>` · `--ar-incorporated false` · `--approved-ready-json/csv <path>` · `--phase N`. 멱등(같은 checked_at 재확정 생략). **alias JSON 미수정**.
- **생성기** `scripts/generate_bulk_alias_candidates.py` — Phase 1 skeleton(내부 데이터만, 외부 API 0).
- **검증** `scripts/validate_bulk_alias_candidates.py`(bulk) · `validate_medistack_v0_1_export.py` · `validate_medistack_v0_2_export.py` · `validate_medistack_v0_3_aliases.py` · `test_validate_v0_3_typeB.py`.
- ⚠️ **alias 실제 반영은 스크립트화하지 않음** — PM 승인 후 ephemeral `/tmp/ms_incorporate_batchN.py`(전제/사후 assert 내장, 미커밋)로 수행. 패턴: product_aliases append + verified_item_seqs append(동반확장) + queue status→approved + AR incorporated=true + alias_count 갱신.
- ⚠️ **package.json 없음** → guards.js(ES module) 단위 smoke 는 `/tmp/*.mjs` 복사 후 `node` import.

## 5. validator 명령과 기대 결과
```
python3 scripts/validate_bulk_alias_candidates.py                                              # → PASS 92/92
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json         # → PASS 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json         # → PASS 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # → PASS 13/13
python3 scripts/test_validate_v0_3_typeB.py                                                    # → PASS 7/7
```
- bulk validator 는 batch1~5 approved-ready 파일을 base_no 20/40/60/80/100 으로 검증(파일 존재 시). incorporation-aware: 반영된 batch 는 #(base+12)에서 alias 실제 반영 검증, incorporated 옵션 A(#54/#74/#94/#114 = {false,true} 정합).

## 6. 후보 queue / approved-ready 파일 구조
- **queue** `data/candidates/bulk_alias_review_queue_v0_5.json`(+`.csv`): `{meta, candidates[]}`. candidate = candidate_alias·candidate_type(product_full_name)·canonical_ingredient·item_seq·ingr_name·source_url·source_method·source_checked_at·status(pending/approved/rejected/deferred)·batch_id·detail_confirmed·detail_*·reviewer·incorporated_at. batch_id: v0.5-001/002(Phase2)·v0.5-005(Phase5)·v0.5-006(Phase11).
- **approved-ready** `bulk_alias_approved_ready_v0_5.json`(batch1) · `..._batch2~5_v0_5.json`(+`.csv`): `{meta, approved_ready[]}`. entry = candidate_alias·canonical_ingredient·item_seq·item_name·ingr_name·source/detail_*·confidence·risk_level·batch_id(v0.5-batch-N)·approved_ready=true·**incorporated**(false=미반영/true=반영)·reviewer_required·incorporated_alias_batch·incorporated_at.
- **alias(라이브)** `data/medistack_v0.3_aliases.json`: `{meta(alias_count), ingredient_aliases[], product_aliases[], verified_item_seqs{canonical:[entries]}}`. product alias = {alias·canonical_ingredient·kind:product·lang:ko·item_seq·source_relation_ids[]}. **guards.js 는 ingredient+product alias만 인덱싱**(verified_item_seqs 는 #8 화이트리스트 검증용).

## 7. batch 1~5 incorporated 상태 요약
| batch | 건수 | alias | source_relation_ids(성분→relation id) | reviewer |
|---|---|---|---|---|
| batch1 | 27 | 66→93 | 11성분 | v0.5-phase4(incorporated) |
| batch2 | 30 | 93→123 | 9성분(오메프라졸 verified 신규) | v0.5-phase6-batch2 |
| batch3 | 30 | 123→153 | 8성분 | v0.5-phase8-batch3 |
| batch4 | 23 | 153→176 | 5성분 | v0.5-phase10-batch4 |
| batch5 | 30 | 176→206 | 6성분 | v0.5-phase12-batch5 |
- 누적 product alias +140. verified_item_seqs 4→144 entries(동반확장). queue approved 140.

## 8. 절대 건드리면 안 되는 것 (불변)
- `data/medistack_v0.3_aliases.json` 임의 수정 금지(반영은 PM 명시 승인 batch만).
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · **DATA_URL** `./data/medistack_v0.2_beta_export.json` 불변 · data export 수정 금지.
- 앱 코드/UI(`src/`) 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- **에스오메프라졸 alias 금지**(id16 ×Mg 정상 live·id15 ×B12 excluded 혼동주의) · **15행(id15) excluded·재편입 금지**.
- **복합제/brand_core approved-ready·alias 진입 금지** · 미검증 itemSeq·동일 itemSeq 중복 alias 금지.
- published/clinical_reviewed 봉인(천장 verified_reference) · 수동 deploy 금지 · 무단 tag 생성 금지.

## 9. 다음 세션 선택지
- **A. v0.5 태그 생성**: `v0.5-beta` 태그(현 `995ce2d` 또는 본 문서 커밋). alias 206 동결 스냅샷. (CI 영향 없음 — 태그는 push만.)
- **B. batch6 계속(206→236)**: held 51 → `confirm --no-network --ar-only-batch v0.5-006 --ar-balanced --ar-batch-id v0.5-batch-6 --ar-limit 30` → batch6 approved-ready 생성 → PM 승인 → 반영. 네트워크 0.
- **C. v0.6 alias 500 계획**: 성분 확대(neword 성분군) + 깊은 페이지 재수집 + brand_core/복합제 tier 판정 설계 문서.
- **D. 전체 품목명 검색 인덱스 분리 설계**: 1만+ 품목명 인덱스를 alias 파일과 분리(런타임 생성·lazy load), 검색 UX 확장 설계.

## 10. 다음 세션 시작 프롬프트 초안
> "MediStack v0.5 마감 완료(alias 206 라이브, commit 995ce2d). 다음 중 [A: v0.5-beta 태그 생성 / B: batch6 계속 206→236 / C: v0.6 alias 500 계획 문서 / D: 품목명 검색 인덱스 분리 설계] 진행. 불변: alias 반영은 명시 승인 batch만, relation 30·DATA_URL·앱 UI·에스오메프라졸/15행 제외 유지, 복합제/brand_core 금지, 수동 deploy/무단 tag 금지. 현재 held 51·deferred 119. handoff=docs/MediStack_v0.5_handoff.md 참조."

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지.
