# MediStack v0.6 — alias 확장 릴리스 노트 (단일성분 트랙 마감) 🏁

작성일: **2026-06-12** / 상태: **v0.6 마감 — 단일성분 트랙 천장 alias 382 도달, 옵션 A(382 마감) 채택** / 라이브: https://yoonspower.github.io/medistack/

> v0.6 의 목표는 **검색 보조 alias 를 206 → 500 으로 확장**하는 것이었다. relation(약-영양소 의료 데이터)·DATA_URL·앱 UI 는 v0.6 에서도 **전부 불변**이며, alias 는 검색 보조일 뿐 의학정보가 아니다. 실측 결과 **단일성분 제품 풀의 천장이 382** 임이 확인되어(500 미달), PM 결정으로 **382 에서 단일성분 트랙을 마감**한다(옵션 A). 500 잔여분은 복합제 tier(옵션 B·별도 정책 결정)로만 도달 가능하며 v0.6 범위 밖이다.

---

## 1. v0.6 목표 (계획)
- **alias_count 206 → 500**: 제품/성분 표면형 확장으로 검색 적중률 향상.
- **확장 우주 = relation 30 의 13 canonical 성분뿐**: relation 약물 14종 중 13종은 이미 alias 커버, 유일 미커버는 **에스오메프라졸(영구 alias 금지)**. relation 동결이므로 신규 성분 트랙 없음 — 500 은 *기존 13성분의 단일성분 제품을 더 모으는 것*으로만 시도.
- **의료 데이터 비확장**: relation 30 유지, alias 로 relation 신규 생성·풀 확장 금지.

## 2. 최종 결과 (실측)
| 항목 | 값 |
|---|---|
| **meta.alias_count** | **382** 🏁 (단일성분 천장 — 목표 500 미달, 사유 §3) |
| product_aliases | 344 |
| ingredient_aliases | 38 |
| verified_item_seqs | 320 entries / 12 canonical 성분 |
| relations | **30 (불변)** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| latest commit | `67724a4` (Incorporate v0.6 batch 9 product aliases (356->382)) |
| queue 총 | 561 (approved 316 · pending 7 · rejected 2 · deferred 236) |
| 라이브 | HTTP 200 |

- alias 증가 경로: **206 → 256 → 306 → 356 → 382** (batch 6~9, v0.6 누적 product alias **+176**).
- 검색 대상 canonical 12성분(v0.5 와 동일·불변): 독시사이클린·레보티록신·레보플록사신·메트포르민·목시플록사신·미노사이클린·시프로플록사신·알렌드론산·오메프라졸·오플록사신·토라세미드·푸로세미드.
- v0.6 에서 신규 alias 가 붙은 성분: **레보플록사신·시프로플록사신·오메프라졸·메트포르민·알렌드론산·오플록사신**(단일성분 완제 잔여 공급). 나머지 6성분은 v0.5 에서 이미 소진·공급 얕음.

## 3. 🏁 왜 382 에서 마감하는가 (단일성분 천장)
- **13 relation 약물의 단일성분·완제·경구 제품 풀이 batch9 에서 소진**됨. Phase 19 주력 심층 재수집(`--max-pages 35`)에서도 신규 단일성분이 18건뿐이었고 batch9(26건)로 전량 흡수 → 이후 **신규 단일성분 0**.
- **500 까지 잔여 118 은 복합제뿐**: 미사용 deferred 가 **복합제 236**(HCTZ 112·메트포르민 77·알렌드론산 30·오메프라졸 6 등)인데, `복합제 금지` 불변규칙(단일성분 매핑 부적합)에 막혀 단일성분 트랙으로는 편입 불가.
- v0.5 계획의 "단일성분 +~240 추정"은 **과대평가**였고, 실측 수율은 **+176**(206→382)으로 확정.
- 따라서 **단일성분 기준 천장 = 382**. 옵션 A(382 마감) 채택 — 검색 커버리지 충분·불변규칙/안전선 전부 유지·추가 위험 0.

## 4. 완료 Phase 요약 (13~20)
| Phase | 내용 | alias | commit |
|---|---|---|---|
| 13 | batch6 후보 생성(held 51 pickable→balanced 50·네트워크 0·무반영) | 206 | `5a3b5b2` |
| 14 | **batch6 50건 반영** | 206→**256** | `580cc73` |
| 15 | batch7 후보 생성(외부 심층 재수집 `--max-pages 25/28`) | 256 | `442f6e1` |
| 16 | **batch7 50건 반영** | 256→**306** | `a564f91` |
| 17 | batch8 후보 생성(held 57·네트워크 0) | 306 | `43ebf7d` |
| 18 | **batch8 50건 반영** | 306→**356** | `bf6e40c` |
| 19 | batch9 후보 재수집(`--max-pages 35`) — **단일성분 공급 벽 도달** | 356 | `a679389` |
| 20 | **batch9 26건 반영 — 🏁 단일성분 트랙 마감** | 356→**382** | `67724a4` |

- 패턴(v0.5 계승): **생성 단계**=alias 무반영(approved-ready, incorporated=false), **반영 단계**=PM 명시 승인 후 product_aliases + verified_item_seqs **동반 확장**. 생성↔반영 분리 안전 게이트 유지.
- 각 batch 반영은 ephemeral `/tmp/ms_incorporate_v0_6_batchN.py`(전제/사후 assert 내장, **미커밋**)로 원자적 수행.

## 5. 검증 결과 (최종, batch9 반영 후)
| validator | 결과 |
|---|---|
| bulk candidate validator | **152/152 PASS** |
| v0.1 export validator | **12/12 PASS** |
| v0.2 export validator | **15/15 PASS** |
| v0.3 alias validator | **13/13 PASS** |
| Type B suite | **7/7 PASS** |
| smoke (신규 batch9) | **9/9 라이브 PASS** |

**회귀 (전 batch 라이브 유지)**:
- 타리비드 → 오플록사신 **3건** · 포사맥스 → 알렌드론산 **1건** · 토렘 → 토라세미드 **2건**
- 넥시움 → **0건 유지**(에스오메프라졸 제외) · `#/r/15`(에스오메프라졸×B12, excluded_v0_1) **fail-safe 유지**(렌더 차단)
- 무손실: 356 ⊆ 382 (직전 alias 전건 보존 + 신규 26).

## 6. 안전선 (v0.6 전 과정 불변)
- **relation 30 불변** · **DATA_URL 불변**(`./data/medistack_v0.2_beta_export.json`) · **data export 불변** · **앱 UI(`src/`) 불변**.
- **에스오메프라졸 alias 금지** 유지(id16 ×Mg 정상 live·id15 ×B12 excluded 혼동 방지) · **15행(id15) excluded 유지**(앱 렌더·재편입 금지).
- **복합제 / brand_core 자동 편입 금지**(별도 tier, approved-ready 진입 차단) · 미검증 itemSeq·동일 itemSeq 중복 alias 금지.
- **제품/구매/제휴 UI 없음** · **칼륨 제품 링크 금지** 유지.
- **published / clinical_reviewed 봉인** 유지(천장 = verified_reference).
- alias 는 **검색 보조**(guards.js 는 ingredient+product alias 만 인덱싱·verified_item_seqs 는 #8 화이트리스트 검증용)이며 **의학정보 아님**.

## 7. 잔여 / 다음 단계 (v0.7 결정 사항)
- **deferred 복합제 236**(HCTZ112·메트77·알렌30·오메6 등): 500 도달의 유일 경로지만 **복합제 tier 개방(옵션 B)** = PM 정책 완화 + combo sub-validator 신설 + **의학적 불완전성**(복합제인데 단일성분 relation 만 노출) 검토가 선행되어야 함. 안전 사안.
- **brand_core 14**(옵션 C): 용량/제형 제거 브랜드 어간 — 무검증 오매칭 위험, 500 엔 미흡.
- **표면형 개행 제외 후보**: nedrug 품목명 개행 포함분(검색 표면형 정제 필요).
- **파이프라인 자산 보존**: collect/confirm/validate 스크립트 · batch1~9 approved-ready · incorporation-aware validator(base_no 20~180·옵션 A) 전부 repo 유지 — 복합제 tier 또는 신규 relation 확장 시 재사용 가능.

## 8. v0.6 에서 하지 않은 것 (범위 밖·의도적 제외)
- relation 확장(의료 상호작용 데이터 추가) — clinical reviewer 트랙.
- DATA_URL 변경 · data export 변경 · 앱 UI 변경.
- published / clinical_reviewed 전환 · clinical claim 추가.
- 복합제 / brand_core / 에스오메프라졸 / 15행 편입.
- 제품 추천 / 구매 / 제휴 UI · 전체 의약품 DB화 · 10,000 alias 인덱스 분리(장기 트랙).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증·복합제·brand_core·동일 itemSeq 중복 alias 금지.
