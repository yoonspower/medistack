# MediStack v0.9 — 표면형 보류 후보 재채록(manual review) 리포트

작성: 2026-06-12 / 트랙: v0.9 표면형 잔여 (PM "보류 3건 재채록 자동 진행 모드" 승인)
기준 상태: HEAD `3dc7a87` 위, 라이브 alias 618 · v0.8-beta(030ee26).

## 0. 목적 / 범위
v0.9 표면형 트랙에서 **manual review 로 보류**했던 queue pending 후보 3건(idx 9/64/65)을
nedrug **getItemDetail 원문으로 재채록**한다. 올바른 단일 품목명 표면형을 확인하고, 안전하면
**approved-ready 후보 파일로 분리**한다.
**🔴 이번 단계에서 alias JSON 실제 반영은 절대 하지 않는다(incorporated=false). 실제 반영은 다음 PM 승인 단계.**

## 1. 재채록 대상 3건 (queue pending · candidate_alias 개행)

| queue idx | item_seq | canonical | candidate_alias (개행 포함) |
|---|---|---|---|
| 9  | 199602155 | 독시사이클린 | `신일모노독시엠캡슐\n(독시사이클린수화물)` |
| 64 | 200710882 | 레보플록사신 | `레보펙신정250밀리그램\n(레보플록사신수화물)` |
| 65 | 200703280 | 레보플록사신 | `레보펙신정500밀리그램\n(레보플록사신수화물)` |

## 2. getItemDetail 재채록 결과 (네트워크 원문)

| item_seq | getItemDetail title (raw) | distinct 주성분 | 단일? | canonical⊆주성분 |
|---|---|---|---|---|
| 199602155 | `신일모노독시엠캡슐\n(독시사이클린수화물)` | 독시사이클린수화물 | ✅ | ✅ |
| 200710882 | `레보펙신정250밀리그램\n(레보플록사신수화물)` | 레보플록사신수화물 | ✅ | ✅ |
| 200703280 | `레보펙신정500밀리그램\n(레보플록사신수화물)` | 레보플록사신수화물 | ✅ | ✅ |

**핵심 발견: getItemDetail 원문 title 자체가 개행을 포함한다.** 즉 개행은 searchDrug 파싱 오류가
아니라 **nedrug 공식 품목명의 `{브랜드}\n(주성분)` 줄바꿈**이다(브랜드명과 주성분 주석 사이 line break).

## 3. 표면형 결정 — 개행만 제거(→ 제거), `{브랜드}(주성분)`

| item_seq | 정제 표면형(개행 제거) |
|---|---|
| 199602155 | `신일모노독시엠캡슐(독시사이클린수화물)` |
| 200710882 | `레보펙신정250밀리그램(레보플록사신수화물)` |
| 200703280 | `레보펙신정500밀리그램(레보플록사신수화물)` |

**개행 제거가 순수 표면형 정규화임의 근거(의미 불변):**
- 라이브 동일성분 alias 의 **지배적 표기가 이미 `{브랜드}(주성분)`** 형식이다:
  레보플록사신 89개 중 **85개**(예 `글로비트정(레보플록사신수화물)`), 독시사이클린 10개 중 **8개**
  (예 `독시정(독시사이클린수화물)`, `바이독시정(독시사이클린수화물)`). 괄호 앞 공백 없음.
- 즉 개행만 제거하면 이 3건은 **기존 라이브 alias 와 완전 동형**이 된다. 문자는 개행만 빠지고
  나머지(브랜드·주성분 주석)는 공식명 그대로 → 약품명 의미 변화 없음.
- 따라서 v0.9 1차에서 "내용 재추출=의미변경"으로 보았던 우려는 재채록으로 해소됨(재추출 불필요,
  개행 단일 제거로 충분). 이전 단계는 "재채록 없이 자동정제 금지" 였고, 지금 재채록을 마쳤다.

## 4. 판정 — 3건 전부 approved-ready (보류 0)

| 기준 | 199602155 | 200710882 | 200703280 |
|---|---|---|---|
| getItemDetail 원문 itemName 확인 | ✅ | ✅ | ✅ |
| candidate_alias ≈ itemName(개행 제외 동일) | ✅ | ✅ | ✅ |
| 개행 제거 후 의미 불변 | ✅ | ✅ | ✅ |
| 단일성분(distinct=1) | ✅ | ✅ | ✅ |
| canonical 명확·⊆ 주성분 | ✅ 독시사이클린 | ✅ 레보플록사신 | ✅ 레보플록사신 |
| itemSeq 고유(라이브 555 itemSeq 중 부재) | ✅ | ✅ | ✅ |
| 정제 표면형 라이브 618 중복 0 | ✅ | ✅ | ✅ |
| 복합제/HCTZ/brand_core 정책 무관 | ✅ 단일성분 | ✅ | ✅ |
| confidence high · reviewer_required=true · incorporated=false | ✅ | ✅ | ✅ |

의학적/성분 해석 애매 0건 → **manual review 잔여 보류 0**. 3건 모두 approved-ready.

## 5. 산출물 (전부 additive · 라이브 alias·queue 0 diff)

1. **`data/candidates/bulk_alias_approved_ready_surface_v0_9.json` / `.csv`** (신규) — approved-ready 3건
   (기존 단일성분 AR 스키마와 동형 · `approved_ready=true` · `incorporated=false` · `reviewer_required=true` · batch_id `v0.9-surface-1`).
2. **`scripts/recollect_surface_candidates_v0_9.py`** (신규) — 재채록 생성기 + `--validate` 정적 검증기.
   - 기본: getItemDetail 재채록 → AR 생성(개행만 제거·단일성분·canonical·고유·중복 검증).
   - `--validate`: 네트워크 없이 AR 안전기준 정적 재검증(suite/CI 용). 음성 6/6 검출 확인.
   - confirm 모듈(get_item_detail/parse_detail/uniqueness) + v0.9 surface validator(surface_anomalies) 재사용.
3. **본 리포트** `docs/MediStack_v0.9_surface_manual_review_report.md`.

**`data/medistack_v0.3_aliases.json`·queue·export·src 무수정**(alias md5 `250c25b8` 불변).

## 6. 검증 결과 (전부 PASS)

**스위트 13/13 PASS:** v0.1·v0.2·v0.3·bulk·combo AR(v0.7)·combo AR(v0.8 HCTZ)·test combo_ar·
test v0_3_combo·test v0_3_typeB·smoke HCTZ·smoke regression·surface forms(live)·**surface AR(v0.9 신규)**.
**surface AR validator 음성 6/6:** incorporated=true·itemSeq=라이브기존·복합제필드·개행·canonical=에스오메·alias≠item_name 각각 FAIL 검출.

## 7. 불변 조건 확인

| 항목 | 기대 | 결과 |
|---|---|---|
| 라이브 alias md5 | 불변 | `250c25b899ab75c9f01ed7ce6c705246` |
| alias_count / product / ingredient / verified | 618 / 580 / 38 / 542·13 | 전부 불변 |
| relation / DATA_URL | 30 / `./data/medistack_v0.2_beta_export.json` | 불변 |
| queue 파일 | 무변경(3건 여전히 pending) | git diff 0 |

## 8. 실제 alias 반영 — ✅ 완료 (PM 승인 2026-06-12)

approved-ready 3건을 alias JSON 에 반영: **product_aliases +3(580→583)** +
**verified_item_seqs +3**(독시사이클린 +1·레보플록사신 +2 — 둘 다 기존 verified 키 append, 13성분 유지) +
**alias_count 618→621**. source_relation_ids = 독시사이클린 [7,8,9]·레보플록사신 [1,2,3].
- 반영 = ephemeral `/tmp/ms_incorporate_v0_9_surface.py`(전제/사후 assert 내장·**미커밋**, alias md5 250c25b8→03fb2137).
- queue 3건 status pending→approved(reviewer `v0.9-surface-1`·incorporated_at·candidate_alias 개행 제거)·AR `incorporated="true"`.
- **validator `recollect_surface_candidates_v0_9.py --validate` incorporation-aware 갱신**(incorporated∈{false,true},
  true→라이브 실제 반영[alias∈live·itemSeq∈verified] 검증 — Phase4 #16·Phase6 #54 패턴).
- **무결성: 기존 product 580·ingredient 38·verified 542 전부 byte 보존**(HEAD 대조), alias diff 삭제줄=`alias_count` 1줄뿐, queue 정확히 3건만 변경.
- 검증 ALL PASS(13/13)·relation 30·DATA_URL·export·src·v0.1/v0.2 불변. 라이브 alias **621**.
