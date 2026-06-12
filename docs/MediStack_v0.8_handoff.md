# MediStack v0.8 — handoff (다음 세션 인계 문서)

> 자기완결 인계 문서. v0.8 = HCTZ 복합제 개방(alias 506→618). 다음 세션은 이 문서만 읽고 이어갈 수 있다.

## 1. 현재 repo / local / live 상태
- repo: `github.com/yoonspower/medistack` (PAT push 만 가능 · repo생성/Pages/재실행 403)
- local: `/Users/mac/AI work/medistack` · live: `https://yoonspower.github.io/medistack`
- 정적 SPA(ES module·빌드 없음) + GitHub Actions(validate→deploy 게이트, main push 시 자동 deploy)

## 2. 최신 커밋 / 태그 / 라이브
- 최신: `56ed71b` Incorporate v0.8 HCTZ combo aliases (506->618) (+ 본 마감 docs 커밋)
- **태그: v0.8 미생성**(현 세션 금지). 누적 태그 = v0.1/v0.2/v0.3/v0.5/v0.6/v0.7-beta.
- 라이브 = main 자동배포(alias 618). 수동 deploy/무단 tag 금지.

## 3. 현재 데이터 수치 (618 기준)
| 항목 | 값 |
|---|---|
| alias_count (meta) | **618** |
| ingredient_aliases | 38 |
| product_aliases | 580 (단일 + 복합제 110 + brand_core 14 + HCTZ 112) |
| verified_item_seqs | 542 entries / **13 canonical** (HCTZ 키 112 포함) |
| relations (v0.2 export) | 30 |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| queue (bulk_alias_review_queue_v0_5) | approved 552 · pending 7 · rejected 2 · **deferred 0** |
| 복합제 product (live) | 222 (메트76·알렌28·오메6 + **HCTZ 112**[ARB 98·ARB+CCB 14]) |
| brand_core (live) | 14 |

## 4. 실행 가능한 주요 스크립트 (전부 repo 보존)
- **수집** `scripts/collect_nedrug_alias_candidates.py` — nedrug searchDrug 후보 수집(네트워크).
- **상세확정** `scripts/confirm_nedrug_item_details.py` — getItemDetail 원문확정 + AR 생성. opt-in `--combo`(basis allowlist={메트,알렌,오메,**히드로클로로티아지드**}·**칼륨보존이뇨제 파트너 필터**). `--combo-ar-json/csv` 로 출력 파일 분리. 멱등·alias 미수정.
- **검증** `validate_combo_approved_ready.py`(combo AR·**13 checks**·#12 K보존·#13 HCTZ고지) · `validate_medistack_v0_3_aliases.py`(**16 checks**·#15 allowlist+HCTZ·#16 K보존토큰) · `validate_bulk_alias_candidates.py`(incorporation-aware·152) · `validate_medistack_v0_1/2_export.py` · `test_validate_v0_3_combo.py`(9) · `test_validate_combo_ar.py`(13) · `test_validate_v0_3_typeB.py`(7).
- **render smoke** `scripts/smoke_hctz_disclosure.py` — 칼륨 반전 고지 (guards/render ES module → /tmp 복사 + node, 10 시나리오).
- ⚠️ **alias 실제 반영은 스크립트화 안 함** — PM 승인 후 ephemeral `/tmp/ms_incorporate_*.py`(전제/사후 assert·**미커밋**). HCTZ 패턴=product+verified 동반확장(verified 키 신규)·큐 flip(approved·reviewer·incorporated_at·detail_confirmed 미설정)·AR incorporated=true.
- ⚠️ **package.json 없음** → guards/render ES module smoke 는 `/tmp` 복사 + `{"type":"module"}` 후 node.

## 5. validator 명령과 기대 결과 (618 기준)
```
python3 scripts/validate_medistack_v0_1_export.py data/medistack_v0.1_beta_export.json   # PASS 12/12
python3 scripts/validate_medistack_v0_2_export.py data/medistack_v0.2_beta_export.json   # PASS 15/15
python3 scripts/validate_medistack_v0_3_aliases.py data/medistack_v0.3_aliases.json data/medistack_v0.2_beta_export.json  # PASS 16/16
python3 scripts/validate_bulk_alias_candidates.py                                          # PASS 152/152
python3 scripts/validate_combo_approved_ready.py data/candidates/bulk_alias_approved_ready_combo_v0_8_hctz.json  # PASS 13/13
python3 scripts/test_validate_v0_3_combo.py     # 9/9
python3 scripts/test_validate_combo_ar.py       # 13/13
python3 scripts/test_validate_v0_3_typeB.py     # 7/7
python3 scripts/smoke_hctz_disclosure.py        # SMOKE PASS 10/10
```
- ⚠️ v0.1/v0.2/v0.3 validator 는 인자 없이 돌리면 sample 찾다 FATAL → 라이브 파일 인자 필수.

## 6. v0.8 게이트 H-G1~H-G4 요약
| 게이트 | 건수 | alias | commit |
|---|---|---|---|
| 정책+설계 | — | 506 | `beb7663`·`5dc78ff` |
| H-G1 validator | — | 506 | `e23f59e` |
| H-G2 render | — | 506 | `17deee3` |
| H-G3 confirm+AR | 112 confirmed | 506 | `a973b1f` |
| H-G4 plan | — | 506 | `d347932` |
| **H-G4 반영** | 112 | **618** | `56ed71b` |
- combo_confirmed 112/112 · K보존 파트너 0 · 2성분 98·3성분 14.

## 7. 절대 건드리면 안 되는 것 (불변)
- `data/medistack_v0.3_aliases.json` · queue 임의 수정 금지(반영은 PM 명시 승인 batch만).
- relation export(v0.1/v0.2) 수정 금지 · relation 30 불변 · **DATA_URL** `./data/medistack_v0.2_beta_export.json` 불변 · data export 불변.
- 앱 코드/UI(`src/`) 제품/구매/제휴 UI 금지 · **칼륨 제품링크 금지**.
- **HCTZ 외 복합제 basis 추가 금지**(에스오메프라졸 하드차단) · **칼륨보존이뇨제 파트너 복합제 영구 차단**(#12/#16/confirm 필터) · **15행(id15)·에스오메프라졸 alias 금지**.
- 복합제는 **PM 명시 승인 + 검증된 itemSeq + incorporation-aware 게이트** 통과분만 편입 · 복합제는 부분정보 고지 동반(HCTZ 는 칼륨 반전 고지 추가).
- published/clinical_reviewed 봉인 · 수동 deploy·무단 tag 금지.

## 8. 다음 세션 선택지 (v0.8 이후)
- **C. 표면형 개행 정제**: nedrug 품목명 개행 포함분 표면형 정리.
- **D. clinical reviewer 트랙**: relation 확장·published 승격(reviewer 확보 선행).
- **루프이뇨제 복합제**: 푸로세미드·토라세미드 복합제 존재 시 동일 칼륨 반전 고지 틀 확장(범위 검토 선행).
- **v0.8-beta 태그**: PM 명시 승인 시 `56ed71b` 스냅샷 생성(lightweight·deploy 미발동).

## 9. 다음 세션 시작 프롬프트 초안
> "MediStack v0.8 마감(alias 618 라이브·commit `56ed71b`·tag 미생성). 618 = 단일382 + 복합제110(메트/알렌/오메) + brand_core14 + HCTZ복합제112. 다음 [C 표면형 개행 / D clinical reviewer / 루프이뇨제 복합제 / v0.8-beta 태그] 중 선택. 불변: alias/queue 반영은 PM 명시 승인 batch만, relation 30·DATA_URL·data export·앱 UI 불변, 칼륨보존이뇨제 복합제·HCTZ외 basis·에스오메/15행 금지, 복합제는 부분정보+(HCTZ)칼륨 반전 고지 동반, 수동 deploy·무단 tag 금지. handoff=docs/MediStack_v0.8_handoff.md · release notes=..._release_notes.md · 게이트로그=..._hctz_gate_log.md."

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 전 published 금지 / validator PASS 없으면 배포 금지 / alias 는 검색 보조 / relation 신규·풀확장 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반.
