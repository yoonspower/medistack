# MediStack v0.6 — handoff (다음 세션 인계 문서)

작성일: **2026-06-12** / 대상: 다음 작업 세션(Claude Code/PM) / 상위: `MediStack_v0.6_release_notes.md`, `MediStack_v0.6_alias_500_plan.md`

> v0.6 마감 시점의 자기완결적 인계 문서. **alias 382 라이브, 단일성분 트랙 천장 도달·마감(옵션 A).** 코드/데이터/alias 안정 상태이며, 다음 작업은 **500 방향(복합제 tier 개방 = 옵션 B) 여부의 PM 정책 결정**이 선행되어야 한다.

---

## 1. 현재 repo / local / live 상태
- **repo**: `yoonspower/medistack` (public, GitHub), 브랜치 `main`. push = fine-grained PAT(push 전용 — repo 생성/Pages/워크플로우 재실행은 403, 사용자 웹 또는 빈 커밋으로 우회).
- **local**: `/Users/mac/AI work/medistack` (git clean, main == origin/main).
- **live**: https://yoonspower.github.io/medistack/ (GitHub Pages, Source=GitHub Actions). HTTP 200.
- **배포**: main push → `.github/workflows/deploy.yml`(validate 게이트 → deploy). `validate.yml`(PR 검증). **수동 deploy 금지**(Actions만).

## 2. 최신 커밋 / 태그 / 라이브
- latest data commit: **`67724a4`** "Incorporate v0.6 batch 9 product aliases (356->382)".
- 마감 문서 커밋: 본 문서 + release notes + plan 마감 갱신(문서 전용, alias 불변).
- **tag**: `v0.1-beta` · `v0.2-beta` · `v0.3-beta` · `v0.5-beta` · **`v0.6-beta`**(이 마감 커밋, alias 382 동결 스냅샷, lightweight).
- 라이브 alias_count: **382** (문서 커밋 후에도 alias 불변).

## 3. 현재 데이터 수치
| 항목 | 값 |
|---|---|
| meta.alias_count | 382 |
| product_aliases | 344 |
| ingredient_aliases | 38 |
| verified_item_seqs | 320 entries / 12 canonical |
| relations (v0.2 export) | 30 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` |
| queue 총 | 561 (approved 316 · pending 7 · rejected 2 · **deferred 236**) |
| deferred(복합제) | 236 (HCTZ112·메트77·알렌30·오메6·기타) — 옵션 B 진입 시 후보 풀 |
| brand_core | 14 (옵션 C) |

## 4. 실행 가능한 주요 스크립트 (전부 repo 보존)
- **수집** `scripts/collect_nedrug_alias_candidates.py` — nedrug searchDrug 후보 수집(외부 네트워크). 핵심 옵션: `--max-per-ingredient N` · `--max-pages N`(페이지당 15행) · `--batch-id <id>` · `--phase N` · `--no-network`(병합/정규화만). 중복제거 4중: surface∉alias·∉queue·itemSeq∉alias·item_name∉alias. **alias JSON 미수정**(dry-run 기본).
- **상세확정** `scripts/confirm_nedrug_item_details.py` — getItemDetail 원문확정 + approved-ready 생성. 옵션: `--target-batch <id>` · `--no-network` · `--ar-only-batch <id>` · `--ar-balanced`(canonical 라운드로빈) · `--ar-limit N` · `--ar-batch-id <id>` · `--ar-incorporated false` · `--phase N`. 멱등(같은 checked_at 재확정·이미 approved 후보 redundant 라벨 금지). **alias JSON 미수정**.
- **검증** `scripts/validate_bulk_alias_candidates.py`(bulk) · `validate_medistack_v0_1_export.py` · `validate_medistack_v0_2_export.py` · `validate_medistack_v0_3_aliases.py` · `test_validate_v0_3_typeB.py`.
- ⚠️ **alias 실제 반영은 스크립트화하지 않음** — PM 승인 후 ephemeral `/tmp/ms_incorporate_v0_6_batchN.py`(전제/사후 assert 내장, 미커밋)로 수행. 패턴: product_aliases append + verified_item_seqs append(동반확장) + queue status→approved + AR incorporated=true + alias_count 갱신.
- ⚠️ **package.json 없음** → guards.js(ES module) 단위 smoke 는 `/tmp/*.mjs` 복사 후 `node` import.

## 5. validator 명령과 기대 결과 (382 기준)
```
python3 scripts/validate_bulk_alias_candidates.py                                              # → PASS 152/152
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json         # → PASS 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json         # → PASS 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # → PASS 13/13
python3 scripts/test_validate_v0_3_typeB.py                                                    # → PASS 7/7
```
- bulk validator 는 batch1~9 approved-ready 파일을 base_no 20/40/.../180 으로 검증. incorporation-aware: 반영된 batch 는 #(base+12)에서 alias 실제 반영 검증, incorporated **옵션 A**(#…=incorporated ∈ {false,true} 정합, true 는 base+12 에서 실제 반영 검증).

## 6. batch 1~9 incorporated 상태 요약
| batch | 건수 | alias | 비고 |
|---|---|---|---|
| 1~5 (v0.5) | 27/30/30/23/30 | 66→206 | v0.5 마감(`9dae621`·v0.5-beta) |
| 6 | 50 | 206→256 | held 51 pickable→balanced 50 |
| 7 | 50 | 256→306 | 외부 심층 재수집(`--max-pages 25/28`) |
| 8 | 50 | 306→356 | held 57 네트워크 0 |
| 9 | 26 | 356→382 | 🏁 단일성분 최종 batch(신규18+held8) |
- v0.6 누적 product alias **+176**(206→382). verified_item_seqs 144→320 entries(동반확장). canonicals 12 유지. queue approved 140→316.

## 7. 절대 건드리면 안 되는 것 (불변)
- `data/medistack_v0.3_aliases.json` 임의 수정 금지(반영은 PM 명시 승인 batch 만).
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · **DATA_URL** `./data/medistack_v0.2_beta_export.json` 불변 · data export 수정 금지.
- 앱 코드/UI(`src/`) 수정 금지 · 제품/구매/제휴 UI 금지 · 칼륨 제품링크 금지.
- **에스오메프라졸 alias 금지**(id16 ×Mg 정상 live·id15 ×B12 excluded 혼동주의) · **15행(id15) excluded·재편입 금지**.
- **복합제 / brand_core approved-ready·alias 진입 금지**(옵션 B 정책 결정 전까지) · 미검증 itemSeq·동일 itemSeq 중복 alias 금지.
- published/clinical_reviewed 봉인(천장 verified_reference) · 수동 deploy 금지 · 무단 tag 생성 금지.

## 8. 다음 세션 선택지 (v0.7)
- **A. 382 마감 유지(현 상태)**: 추가 작업 없음. 검색 커버리지 충분·안전. v0.6 종료.
- **B. 복합제 tier 개방 → 500**: 유일한 500 경로. **선행 필수**: ① `복합제 금지` 불변규칙 PM 정책 완화 결정, ② combo sub-validator 신설(복합제 itemSeq → 다중 canonical 매핑 규칙·검증), ③ **의학적 불완전성 검토**(복합제인데 단일성분 relation 만 노출되는 UX 위험), ④ 후보 풀 = deferred 복합제 236(HCTZ112·메트77·알렌30·오메6). 안전 사안 — 정책 결정 전 코드/데이터 착수 금지.
- **C. brand_core(14)**: 소량·오매칭 위험, 500 미흡. 단독으로는 비권장.

## 9. 다음 세션 시작 프롬프트 초안
> "MediStack v0.6 마감 완료(alias 382 라이브, commit 67724a4, tag v0.6-beta, 단일성분 트랙 천장). v0.7 방향 [A: 382 유지·종료 / B: 복합제 tier 개방→500(정책완화+combo sub-validator+의학적 불완전성 검토 선행) / C: brand_core] 중 [선택] 진행. 불변: alias 반영은 명시 승인 batch만, relation 30·DATA_URL·앱 UI·에스오메프라졸/15행 제외 유지, 복합제/brand_core 정책 결정 전 금지, 수동 deploy/무단 tag 금지. 현재 deferred 복합제 236·brand_core 14. handoff=docs/MediStack_v0.6_handoff.md 참조."

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지.
