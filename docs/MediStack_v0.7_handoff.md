# MediStack v0.7 — handoff (다음 세션 인계 문서)

작성일: **2026-06-12** / 대상: 다음 작업 세션(Claude Code/PM) / 상위: `MediStack_v0.7_release_notes.md`, `MediStack_v0.7_combo_tier_policy.md`, `MediStack_v0.7_combo_tier_design.md`

> v0.7 마감 시점의 자기완결적 인계 문서. **alias 506 라이브 (복합제 tier B1 110 + brand_core 14 + 단일성분 382), 🎯 목표 500 달성.** 코드/데이터/alias 안정 상태이며, 본 마감은 **문서 전용**(alias/queue/validator/app 무변경)이다. **`v0.7-beta` 태그는 아직 생성하지 않음**(PM 별도 지시 대기).

---

## 1. 현재 repo / local / live 상태
- **repo**: `yoonspower/medistack` (public, GitHub), 브랜치 `main`. push = fine-grained PAT(push 전용 — repo 생성/Pages/워크플로우 재실행은 403, 사용자 웹 또는 빈 커밋으로 우회).
- **local**: `/Users/mac/AI work/medistack` (git clean, main == origin/main).
- **live**: https://yoonspower.github.io/medistack/ (GitHub Pages, Source=GitHub Actions). HTTP 200.
- **배포**: main push → `.github/workflows/deploy.yml`(validate 게이트 → deploy). `validate.yml`(PR 검증). **수동 deploy 금지**(Actions만).

## 2. 최신 커밋 / 태그 / 라이브
- latest data commit: **`113a79b`** "Incorporate v0.7 G5 brand_core aliases (492->506), incorporation-aware bulk #10/#11/#30".
- 마감 문서 커밋(본 문서 + release notes): "Document v0.7 alias 500 milestone" (문서 전용, alias 불변).
- **tag**: `v0.1-beta` · `v0.2-beta` · `v0.3-beta` · `v0.5-beta` · `v0.6-beta`(=`b168179`, alias 382). **`v0.7-beta` 미생성**(PM 지시 대기 — 생성 시 alias 506 동결 스냅샷).
- 라이브 alias_count: **506** (문서 커밋 후에도 alias 불변).

## 3. 현재 데이터 수치
| 항목 | 값 |
|---|---|
| meta.alias_count | 506 |
| product_aliases | 468 (복합제 110 + 단일성분 358) |
| ingredient_aliases | 38 |
| verified_item_seqs | 430 entries / 12 canonical |
| relations (v0.2 export) | 30 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` |
| data export md5 | `401b097a1bd812b6da983b7f3dfc6d20` |
| queue 총 | 561 (approved 440 · pending 7 · rejected 2 · **deferred 112**) |
| deferred(전량 HCTZ 복합제) | 112 — B1 제외(칼륨 상충), 추가 안전 검토 선행 필요 |
| 복합제 product (live) | 110 (메트76·알렌28·오메6) |
| brand_core (live) | 14 (메트1·목시3·미노3·시프로1·알렌2·오플1·토라3) |

## 4. 실행 가능한 주요 스크립트 (전부 repo 보존)
- **수집** `scripts/collect_nedrug_alias_candidates.py` — nedrug searchDrug 후보 수집(외부 네트워크). `--max-per-ingredient` · `--max-pages` · `--batch-id` · `--phase` · `--no-network`. 중복제거 4중.
- **상세확정** `scripts/confirm_nedrug_item_details.py` — getItemDetail 원문확정 + approved-ready 생성. 단일흐름 옵션(`--target-batch`·`--ar-only-batch`·`--ar-balanced`·`--ar-limit`·`--ar-batch-id`·`--ar-incorporated`) + **opt-in `--combo` 모드**(복합제 getItemDetail distinct → relation 정확히 1개 = canonical ∈ {메트·알렌·오메} 확정 → combo AR). 멱등. **alias JSON 미수정**.
- **검증** `scripts/validate_bulk_alias_candidates.py`(bulk·incorporation-aware) · `validate_combo_approved_ready.py`(combo AR·CMB #1~11) · `validate_medistack_v0_1_export.py` · `validate_medistack_v0_2_export.py` · `validate_medistack_v0_3_aliases.py`(combo 가드 #14/#15 포함) · `test_validate_v0_3_typeB.py` · `test_validate_v0_3_combo.py` · `test_validate_combo_ar.py`.
- ⚠️ **alias 실제 반영은 스크립트화하지 않음** — PM 승인 후 ephemeral `/tmp/ms_incorporate_*.py`(전제/사후 assert 내장, **미커밋**)로 수행. 복합제 패턴=product+verified 동반확장+큐 flip; brand_core 패턴=product 만(+14)·**verified 미확장**(itemSeq 이미 #8 허용집합)·큐 flip(incorporated=true).
- ⚠️ **package.json 없음** → guards.js/render.js(ES module) smoke 는 `/tmp/*.mjs`(+`package.json {"type":"module"}`) 복사 후 `node` import.

## 5. validator 명령과 기대 결과 (506 기준)
```
python3 scripts/validate_bulk_alias_candidates.py                                              # → PASS 152/152
python3 scripts/validate_combo_approved_ready.py                                               # → PASS 11/11
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json         # → PASS 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json         # → PASS 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # → PASS 15/15
python3 scripts/test_validate_v0_3_typeB.py                                                    # → PASS 7/7
python3 scripts/test_validate_v0_3_combo.py                                                    # → PASS 7/7
python3 scripts/test_validate_combo_ar.py                                                      # → PASS 9/9
```
- ⚠️ v0.1/v0.2/v0.3 validator 는 **인자 없이 돌리면 sample 파일을 찾다 FATAL** — 반드시 라이브 파일 인자로(v0.1 은 전용 `medistack_v0.1_beta_export.json`, 버전 혼동 금지).
- **bulk incorporation-aware**: brand_core approved 는 #10/#11 에서 incorporated=true & alias 실반영 시에만 허용(미반영 하드차단), #30 은 brand_core itemSeq ∈ whitelist ∪ relation-cited 허용. combo/단일 batch 는 옵션 A(incorporated ∈ {false,true}, true 는 base+12 에서 실제 반영 검증).

## 6. v0.7 게이트 G1~G5 요약
| 게이트 | 건수 | alias | commit | 비고 |
|---|---|---|---|---|
| 정책/설계 | — | 382 | `bd4d47a`·`548aea5` | B1·HCTZ 제외·UX 고지·validator 설계 |
| G1 | — | 382 | `752052e` | v0.3 validator #14/#15 (combo 라이브 가드) |
| G2 | — | 382 | `f33c4c1` | 앱 고지 렌더 + append-only 3필드 (라이브 inert) |
| G3 | 110 confirmed | 382 | `a3e8a6f` | confirm `--combo` + combo AR + combo AR validator |
| G4 | 복합제 +110 | 382→**492** | `0962e44` | product+110·verified+110·큐 flip |
| G5 | brand_core +14 | 492→**506** | `113a79b` | product+14·verified 불변·incorporation-aware #10/#11/#30 |
- 누적: **382 → 492 → 506**. combo 110(메트76·알렌28·오메6) · brand_core 14. verified 320→430(G4 +110) → 430(G5 불변). canonical 12 유지.

## 7. 절대 건드리면 안 되는 것 (불변)
- `data/medistack_v0.3_aliases.json` · `data/candidates/bulk_alias_review_queue_v0_5.*` 임의 수정 금지(반영은 PM 명시 승인 batch 만).
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · **DATA_URL** `./data/medistack_v0.2_beta_export.json` 불변 · data export 수정 금지(md5 `401b097a…`).
- 앱 코드/UI(`src/`) 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- **HCTZ 복합제 편입 금지** · **에스오메프라졸 alias 금지**(id16 ×Mg 정상 live·id15 ×B12 excluded 혼동주의) · **15행(id15) excluded·재편입 금지**.
- 복합제/brand_core 는 **PM 명시 승인 + 검증된 itemSeq + incorporation-aware 게이트** 통과분만 편입(자동 편입 금지) · 미검증·동일 itemSeq 중복 alias 금지(단, brand_core 는 검증된 형제 itemSeq 재사용 허용) · 복합제는 **부분정보 고지 동반**.
- published/clinical_reviewed 봉인(천장 verified_reference) · 수동 deploy 금지 · **무단 tag 생성 금지**.

## 8. 다음 세션 선택지 (v0.7 이후)
- **A. v0.7-beta 태그 생성**: alias 506 동결 스냅샷(lightweight·deploy 미발동). PM 지시 시.
- **B. HCTZ 복합제 추가 개방(112)**: 칼륨 상충 안전 검토(potassium 고지 강화) 선행 필수. 안전 사안 — 정책 결정 전 코드/데이터 착수 금지.
- **C. 표면형 개행 후보 정제**: nedrug 품목명 개행 포함분 검색 표면형 정리.
- **D. clinical reviewer 트랙**: relation 확장·published 승격(별도 버전·reviewer 확보 후).

## 9. 다음 세션 시작 프롬프트 초안
> "MediStack v0.7 마감 완료(alias 506 라이브, commit 113a79b, 🎯목표 500 달성 = 단일382+복합제110+brand_core14, tag 미생성). 다음 [A: v0.7-beta 태그 생성 / B: HCTZ 복합제 개방→안전검토 선행 / C: 표면형 개행 정제 / D: clinical reviewer 트랙] 중 [선택] 진행. 불변: alias/queue 반영은 명시 승인 batch만, relation 30·DATA_URL·data export·앱 UI 불변, HCTZ/에스오메프라졸/15행 금지, 복합제는 부분정보 고지 동반, 복합제/brand_core 자동편입 금지, 수동 deploy/무단 tag 금지. 함정: bulk #7(graduate=status=approved)·#10/#11/#30(brand_core approved=incorporation-aware: incorporated=true+alias반영시만)·#19(combo는 detail_confirmed 미설정). handoff=docs/MediStack_v0.7_handoff.md·release notes=..._release_notes.md·정책=..._combo_tier_policy.md·설계=..._combo_tier_design.md."

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / HCTZ 복합제·미검증·동일 itemSeq 중복 alias 금지(brand_core 형제 itemSeq 재사용은 예외) / 복합제는 부분정보 고지 동반.
