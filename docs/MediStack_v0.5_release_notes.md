# MediStack v0.5 — bulk alias pipeline 릴리스 노트 (1차 목표 완료) 🎯

작성일: **2026-06-11** / 상태: **v0.5 bulk alias pipeline 1차 마감 — alias 목표 200 달성·초과(206)** / 라이브: https://yoonspower.github.io/medistack/

> v0.5 의 목표는 **검색 보조 alias 확장**(제품명/성분명 → canonical 성분 매핑)이며, **의료 판단 데이터(relation)는 확장하지 않는다**. relation 30 · DATA_URL · 앱 UI 전부 불변. alias 는 검색 보조일 뿐 의학정보가 아니다.

---

## 1. v0.5 목표
- **bulk alias pipeline 구축**: 수작업 불가능한 대량 alias 를 **자동 후보생성(nedrug searchDrug) → getItemDetail 원문확정 → 사람(PM) 승인 → batch 반영** 파이프라인으로 전환.
- **alias_count 200 달성**: v0.4 의 66 → v0.5 200+ 로 검색 alias 확장.
- **검색 alias 확장만**: 제품/성분 표면형을 늘려 검색 적중률 향상. relation(약-영양소 상호작용 의료 데이터)은 **30 그대로 유지**.
- **의료 판단 데이터 비확장**: alias 로 relation 신규 생성·풀 확장 금지. 식약처 허가사항 원문 검증 범위 안에서만.

## 2. 최종 결과
| 항목 | 값 |
|---|---|
| **meta.alias_count** | **206** 🎯 (목표 200 달성·초과) |
| product_aliases | 168 |
| ingredient_aliases | 38 |
| verified_item_seqs | 144 entries / 12 canonical 성분 |
| relations | **30 (불변)** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| latest commit | `995ce2d` (Add v0.5 approved-ready product aliases batch 5) |
| GitHub Actions | run `27336943120` success (validate→deploy) |
| 라이브 | HTTP 200 |

- alias 증가 경로: **66 → 93 → 123 → 153 → 176 → 206** (batch 1~5, 누적 product alias +140).
- 검색 대상 canonical 12성분: 독시사이클린·레보티록신·레보플록사신·메트포르민·목시플록사신·미노사이클린·시프로플록사신·알렌드론산·오메프라졸·오플록사신·토라세미드·푸로세미드. (히드로클로로티아지드는 product alias 2건, 신규 후보는 대부분 복합제로 deferred.)

## 3. 완료 Phase 요약 (12단계)
| Phase | 내용 | alias |
|---|---|---|
| 1 | bulk alias 후보 생성기 skeleton(`generate_bulk_alias_candidates.py`·validator·review queue) | 66 |
| 2 | nedrug searchDrug 수집(`collect_nedrug_alias_candidates.py`) | 66 |
| 3 | getItemDetail 상세확정(`confirm_nedrug_item_details.py`) | 66 |
| 4 | **batch1 27건 반영** | 66→**93** |
| 5 | batch2 후보 생성(페이지네이션 추가) | 93 |
| 6 | **batch2 30건 반영** | 93→**123** |
| 7 | batch3 후보 생성 | 123 |
| 8 | **batch3 30건 반영** | 123→**153** |
| 9 | batch4 후보 생성 | 153 |
| 10 | **batch4 23건 반영** | 153→**176** |
| 11 | batch5 후보 재수집(외부 nedrug, held 소진 후) | 176 |
| 12 | **batch5 30건 반영** | 176→**206** 🎯 |

- 패턴: **홀수 Phase(또는 후보 단계)=생성**(alias 무반영·incorporated=false), **짝수 Phase=PM 명시 승인 후 반영**(product_aliases + verified_item_seqs **동반 확장**, alias 실제 증가). 생성↔반영 분리로 안전 게이트 유지.
- 각 batch 반영은 ephemeral `/tmp/ms_incorporate_batchN.py`(전제/사후조건 assert 내장, 커밋 안 함)로 원자적 수행.

## 4. 검증 결과 (최종)
| validator | 결과 |
|---|---|
| bulk candidate validator | **92/92 PASS** |
| v0.1 export validator | **12/12 PASS** |
| v0.2 export validator | **15/15 PASS** |
| v0.3 alias validator | **13/13 PASS** |
| Type B suite | **7/7 PASS** |
| smoke (신규 batch5) | **30/30 라이브 PASS** |

**회귀 (전 batch 라이브 유지)**:
- 타리비드 → 오플록사신 **3건**
- 포사맥스 → 알렌드론산 **1건**
- 토렘 → 토라세미드 **2건**
- 넥시움 → **0건 유지**(에스오메프라졸 제외)
- `#/r/15` (에스오메프라졸×B12, excluded_v0_1) **fail-safe 유지**(렌더 차단)

## 5. 안전선 (v0.5 전 과정 불변)
- **에스오메프라졸 alias 금지** 유지(id16 ×Mg 는 정상 live relation 이나 id15 ×B12 혼선 방지로 alias 보류).
- **15행(에스오메프라졸×B12, id15) excluded 유지** — 앱 렌더 금지·재편입 금지.
- **relation 확장 없음**(30 불변) · **DATA_URL 변경 없음** · **data export 변경 없음** · **앱 UI 변경 없음**.
- **제품/구매/제휴 UI 없음** · **칼륨 제품 링크 금지** 유지.
- **published/clinical_reviewed 봉인** 유지(천장 verified_reference, clinical reviewer 확보 전 승격 금지).
- **복합제/brand_core 자동 편입 금지**(별도 tier, approved-ready 진입 차단).
- alias 는 **검색 보조**(guards.js 는 ingredient_aliases+product_aliases만 인덱싱, verified_item_seqs 는 화이트리스트 검증용·미인덱싱)이며 **의학정보가 아님**. alias 로 relation 신규 생성 금지.
- 모든 itemSeq 는 nedrug getItemDetail 원문 확정(미검증 itemSeq·동일 itemSeq 중복 alias 금지).

## 6. 남은 후보 / 다음 단계 (선택)
- **held 51**(Phase 11 confirmed·미반영) → batch 6 즉시 가능(206→236, 네트워크 0).
- **deferred 119**(복합제 combo ~105 + brand_core 14) — 복합제는 단일성분 매핑 부적합으로 보류, brand_core 는 별도 tier 판정 필요.
- **표면형 개행 제외 후보**(nedrug 품목명에 개행 포함, 검색 표면형 정제 필요).
- **v0.6 alias 500 목표** 가능(추가 성분 확대 + 깊은 페이지 재수집).
- **전체 품목명 검색 인덱스 1만+** 는 장기 목표(별도 인덱스 분리 설계 필요, 현 alias 파일과 분리).

## 7. v0.5 에서 하지 않은 것 (범위 밖·의도적 제외)
- relation 확장(의료 상호작용 데이터 추가) — clinical reviewer 트랙.
- DATA_URL 변경 · data export 변경.
- published/clinical_reviewed 전환 · clinical claim 추가.
- 제품 추천 / 구매 / 제휴 UI.
- 전체 의약품 DB화.
- 10,000 alias 인덱스 분리(장기 목표).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·동일 itemSeq 중복 alias 금지.
