# MediStack v0.8 — HCTZ 복합제 개방 릴리스 노트 (alias 618)

> 트랙: B(HCTZ) / 결정: **H1 조건부 개방** (PM 승인 2026-06-12)
> 라이브: `yoonspower.github.io/medistack` · 최신 커밋 `56ed71b` · **tag 미생성**(현 세션 금지)

---

## 1. v0.8 목표 (계획)

v0.7 에서 "이중 위험(부분정보+칼륨 오도)"으로 **제외**했던 HCTZ 복합제 deferred 112 를 재검토. 정책 재분석 결과 **진짜 위험군(칼륨보존이뇨제 복합제) 0건**을 확인 → **고지·validator 안전조건 하에 조건부 개방(H1)**.

## 2. 최종 결과 (실측)

| 항목 | v0.7 마감 | v0.8 마감 | Δ |
|---|---|---|---|
| **alias_count** | 506 | **618** | +112 |
| product_aliases | 468 | 580 | +112 |
| verified_item_seqs | 430 / 12 | 542 / 13 | +112 / +1(HCTZ 키) |
| relations / DATA_URL / data export | 30 / 불변 / 불변 | **30 / 불변 / 불변** | 0 |
| queue | deferred 112 | **approved 552·deferred 0** | flip 112 |

- **alias 618 = 단일성분 382 + 복합제 110(메트76·알렌28·오메6) + brand_core 14 + HCTZ 복합제 112.**
- HCTZ 112 = 2성분 ARB+HCTZ **98** + 3성분 ARB+CCB+HCTZ **14**. 파트너: 로사르탄칼륨·발사르탄·올메사르탄·칸데사르탄·텔미사르탄·피마사르탄(+암로디핀).

## 3. 개방 경로 (506 → 618)

| 게이트 | 내용 | alias | commit |
|---|---|---|---|
| 정책 | HCTZ 안전성 재검토(칼륨보존 0건 발견) | 506 | `beb7663` |
| 설계 | 반전 고지 + validator V1~V6 | 506 | `5dc78ff` |
| H-G1 | combo validator 가드(#12 K보존·#13 HCTZ고지·#16 라이브방어) | 506 | `e23f59e` |
| H-G2 | 칼륨 반전 고지 render(app.js 무변경) | 506 | `17deee3` |
| H-G3 | confirm `--combo` HCTZ + 112 상세확정 → AR | 506 | `a973b1f` |
| H-G4 plan | 반영 계획 + 전제/사후 assert | 506 | `d347932` |
| **H-G4 반영** | 112 alias 반영(product+verified+큐 flip) | **618** | `56ed71b` |

## 4. 핵심 안전 설계 (HCTZ 고유)

- **칼륨 반전 고지(신규)**: HCTZ 복합제의 칼륨 행에 "표시 정보는 HCTZ 성분 기준, 함께 든 ARB 계열은 칼륨을 **반대 방향(보존)**으로 움직일 수 있음, 임의보충 위험·상담" 1줄. **render 파생**(is_combination + basis=HCTZ + 칼륨행[potassium_safety_card 플래그]) — **스키마/relation/DATA_URL 무변경·app.js 무변경**. 단일 HCTZ 엔 미표시.
- **칼륨보존이뇨제 파트너 영구 하드차단(V2·#12·confirm 필터·#16)**: 트리암테렌/아밀로라이드/스피로노락톤/에플레레논/칸레논. 현재 0건이나 future-proof. 진짜 "칼륨 역전" 위험군 영구 봉쇄.
- **염이름 칼륨 분리(V5)**: `로사르탄칼륨`·`피마사르탄칼륨` 의 '칼륨'(짝이온 염)은 K보존 토큰 매칭 대상 아님 — 약물명 토큰으로만 판정.
- **기존 칼륨 안전장치 유지**: id 19(HCTZ×칼륨) `potassium_safety_card=true`·`product_link_allowed=false`·"임의보충 위험·상담" 불변(칼륨 제품링크 금지).

## 5. validator / render 진화

- **combo AR validator**(`validate_combo_approved_ready.py`): 11 → **13 checks**. #6 allowlist+HCTZ, **#12** K보존 파트너 하드차단, **#13** HCTZ 칼륨 반전 고지 파생조건.
- **aliases validator**(`validate_medistack_v0_3_aliases.py`): 15 → **16 checks**. #15 allowlist+HCTZ, **#16** 라이브 복합제 alias K보존 토큰 방어.
- **confirm `--combo`**: COMBO_ALLOWED_BASIS+HCTZ, classify_combo 에 K보존 파트너 필터.
- **render/guards/css**: `aliasHint` hctzPotassiumNotice 플래그 + `renderAliasHint` 반전 고지 1줄 + `.combonotice` (app.js 무변경).

## 6. 검증 결과 (최종, 반영 후)

- v0.1 12/12 · v0.2 15/15 · v0.3 **16/16** · bulk **152/152** · combo AR(v0.8 HCTZ) **13/13**(incorporated=true·#11 실반영) · typeB 7/7 · combo가드 9/9 · comboAR테스트 13/13 · **smoke 10/10**.
- **라이브 end-to-end**: 실제 복합제(미카르디스플러스정·텔미사르탄+HCTZ) 검색 → 복합제 배지 + 칼륨 반전 고지 표시. 단일 HCTZ 미표시(회귀 0).
- Actions validate→deploy success · 라이브 HTTP 200 · alias 618.

## 7. 안전선 (v0.8 전 과정 불변)

원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / **칼륨 제품링크 금지** / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias 는 검색 보조이지 의학정보 아님 / relation 신규생성·풀확장 금지(relation 30 불변) / 15행·excluded·**에스오메프라졸 alias 우회 금지** / **칼륨보존이뇨제 복합제 영구 차단** / 복합제는 부분정보+반전 고지 동반 / 복합제 자동편입 금지(PM 명시 승인 batch만) / 수동 deploy·무단 tag 금지.

## 8. 잔여 / 다음 단계

- **복합제 deferred 0** — HCTZ 트랙으로 nedrug ARB+HCTZ 풀 소진. 단일성분 천장(382)·복합제(메트/알렌/오메 110 + HCTZ 112)·brand_core(14) 전부 반영.
- v0.9 후보: **C 표면형 개행 정제** / **D clinical reviewer 트랙**(reviewer 확보 선행) / 루프이뇨제(푸로세미드·토라세미드) 복합제 존재 시 동일 반전 고지 틀 확장 검토.
- **tag**: v0.8 태그 미생성(현 세션 금지). PM 명시 승인 시 `v0.8-beta` 생성 가능.

## 9. v0.8 에서 하지 않은 것 (범위 밖·의도적)

- 칼륨보존이뇨제 복합제 편입(영구 차단) · 에스오메프라졸/15행(봉인) · 푸로세미드/토라세미드 복합제(범위 밖) · 표면형 개행(C) · clinical 승격(D) · relation 신규 · 제품/구매/제휴 UI · tag 생성.
