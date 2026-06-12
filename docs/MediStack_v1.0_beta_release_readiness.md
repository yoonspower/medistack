# MediStack v1.0-beta — Release Readiness (안정판 마감 판정)

> v1.0-D 트랙. v1.0-beta 안정판 마감을 위한 release readiness 판정 문서. **문서만 작성**(코드·데이터·alias·queue·validator·src·relation·DATA_URL·export·tag 무변경).
> 운영 인계는 동반 문서 `MediStack_v1.0_handoff.md` 참조.

---

## 1. v1.0-beta 기준선

| 항목 | 값 |
|---|---|
| latest commit | `e75f65c` Add v1.0 search regression smoke coverage |
| 누적 태그 | v0.1/v0.2/v0.3/v0.5/v0.6/v0.7/v0.8-beta · **v0.9·v1.0 무태그** |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| export md5 | `401b097a1bd812b6da983b7f3dfc6d20` (불변) |
| 성격 | **안정판** — medical claim 무확장, 데이터 무확장, 회귀 가드 정비 |

v1.0 = "데이터를 더 쌓는 버전"이 아니라 **"있는 데이터를 안전하게 굳히고 다음 단계(검수자·full index) 레일을 깐 버전."**

---

## 2. v0.1 ~ v0.9 완료 요약

| 버전 | 핵심 | alias 누계 |
|---|---|---|
| v0.1 | verified_reference 관계 **19건** | — |
| v0.2 | relation 19→**30**, 검색/필터 UX | — |
| v0.3-beta | alias / 검색 안정화 | 53→66 |
| v0.4 | Type A/B alias + verified_item_seqs 화이트리스트 | 66 |
| v0.5 | bulk alias pipeline | **206** |
| v0.6 | 단일성분 천장 | **382** |
| v0.7 | combo tier B1(메트/알렌/오메 110 + brand_core 14) | **506** |
| v0.8 | HCTZ combo 112(칼륨 반전 고지) | **618** |
| v0.9 | 표면형 개행 정제 3건 | **621** |

곡선: 단일성분(382) → 복합제(+124) → 표면형(+3). **deferred 0 · queue 표면형 후보 0** → alias 확장 트랙 한계 도달.

---

## 3. v1.0-A/B/C 완료 요약

| 트랙 | 산출물 | commit | 성격 |
|---|---|---|---|
| **v1.0-A** clinical reviewer checklist | `MediStack_v1.0_clinical_reviewer_checklist.md` | `fa6aab3` | 검수자 플로우 설계(승격 금지·레일만) |
| **v1.0-B** full drug search index 설계 | `MediStack_v1.0_full_drug_search_index_design.md` | `a3a8272` | relation 없는 약 → 별도 fail-soft `full_drug_name_index`·name_only(인덱스 미생성) |
| **v1.0-C** search regression smoke | `scripts/smoke_search_regression_v1_0.py` + `scripts/fixtures/search_regression_v1_0.json` + report | `e75f65c` | 실제 guards.js+render.js 로 검색/고지/empty/degrade ~70체크 고정(src 수정 0) |

계획 문서: `MediStack_v1.0_plan.md`(`2edbdcc`).

---

## 4. 현재 라이브 수치

| 항목 | 값 |
|---|---|
| alias_count | **621** (product 583 + ingredient 38) |
| verified_item_seqs | **545 entries / 13 canonical** |
| relations | **30** (+ excluded_v0_1 1, 렌더 금지) |
| published | **false** (봉인) |
| clinical_reviewed | **false** (봉인) |
| lifecycle_status_included | **verified_reference** (천장) |
| live | `https://yoonspower.github.io/medistack` HTTP 200 |

---

## 5. validator / smoke 현황 (전종 PASS)

```
v0.1 export ............ 12/12     v0.2 export ............ 15/15
v0.3 aliases ........... 16/16     surface forms ..........  5/5
TypeB suite ............  7/7      combo suite ............  9/9
combo AR suite ......... 13/13     combo approved_ready ... 13/13
bulk candidates ........ 152/152
smoke_alias_regression .  7/7      smoke_hctz_disclosure .. PASS
smoke_search_regression_v1_0 ..... PASS (~70 체크)
```

CI 게이트(deploy.yml) = v0.1/v0.2/v0.3/surface 4종. smoke 3종은 커밋된 수동 회귀(CI 미배선).

---

## 6. 법적 / 의학적 안전선

- **참고 정보 베타** — 진단·처방·복약지시 아님. 모든 상세에 `disclaimers.common` 표시.
- **천장 = verified_reference** — `clinical_reviewed`/`published` 전환은 외부 면허 검수자 확보 전까지 봉인.
- **원문 원칙** — 식약처 허가사항에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지.
- **칼륨** — 제품 링크 금지 · 복합제(HCTZ)는 칼륨 반전 고지 동반.
- **제품/구매/제휴 UI 부재** — 수익화 UI 없음(데이터에 제품 필드 자체 없음).
- **alias / full index = 검색 보조**, 의학 정보 아님.

---

## 7. 아직 하지 않을 것 (v1.0-beta 범위 밖)

- ❌ **relation 확장** — relation 30 고정. 신규 생성·풀 확장 금지.
- ❌ **published / clinical_reviewed 전환** — 외부 검수자 확보 전 봉인.
- ❌ **제품 / 구매 / 제휴 UI** — 영구 금지.
- ❌ **full drug index 실제 구현** — v1.0-B 는 **설계만**. 인덱스 데이터 파일·name_only UX 미구현.

---

## 8. v1.0-beta 릴리즈 전 최종 QA 체크리스트

릴리즈(=태그) 직전 확인:

- [ ] validator 전종 PASS — v0.1 12 / v0.2 15 / v0.3 16 / surface 5 / TypeB 7 / combo 9 / combo_AR 13 / combo_approved_ready 13 / bulk 152
- [ ] smoke 전종 PASS — alias_regression 7 / hctz_disclosure / search_regression ~70
- [ ] 불변 수치 — alias 621(583+38) / verified_item_seqs 545/13 / relation 30
- [ ] DATA_URL `./data/medistack_v0.2_beta_export.json` / export md5 `401b097a`
- [ ] 봉인 — `published=false` / `clinical_reviewed=false` / `lifecycle_status_included=verified_reference`
- [ ] live HTTP 200 (`/` + 데이터 fetch)
- [ ] 앱 수동 QA — 검색 / alias 안내 / empty / error / 칼륨 안전카드 / 복합제 부분정보 / HCTZ 칼륨 반전 고지
- [ ] docs — plan·clinical_reviewer_checklist·full_drug_search_index_design·search_regression_report·handoff 존재
- [ ] git status clean (`scripts/__pycache__` untracked만)

---

## 9. 다음 트랙

| 트랙 | 내용 | 게이트 |
|---|---|---|
| **full drug index 1,000 샘플** | `full_drug_name_index` Phase 2(nedrug searchDrug 수집 → getItemDetail 보수적 확정) + 신 validator | 설계(v1.0-B) 확정 후 · PM 승인 · 회귀 smoke 통과 |
| **clinical reviewer 확보** | 면허 검수자 섭외 → review_log 스키마 적용(별도 버전) → relation 단위 승격 | 외부 사람 의존(가장 큰 잠금 해제) |
| **v1.0-beta tag 생성** | `e75f65c`(또는 v1.0-D 마감 커밋) lightweight 스냅샷 | **PM 명시 승인 시에만** · deploy 미발동 |

---

## 10. v1.0-beta tag 생성 가능 여부 (판정)

**판정: tag-ready (생성 가능).** 단 **본 세션은 tag 생성 금지** → PM 명시 승인 시 다음 단계에서 생성.

근거:
- 전 validator·smoke PASS · 불변 수치 일치 · 봉인 유지 · live HTTP 200 · Actions/deploy success.
- 안정판 정의 충족(medical claim·데이터 무확장, 회귀 가드 정비 완료).
- pending 변경 없음(working tree clean, `__pycache__` untracked만).

태그 생성 시: `git tag v1.0-beta <commit>` (lightweight) — main push 자동 deploy와 무관, **deploy 미발동**. 누적 태그에 v0.9 가 없으므로 v1.0-beta 가 v0.8-beta 다음 태그가 된다(v0.9 는 무태그로 남김).

> 다음 세션 인계 = `MediStack_v1.0_handoff.md`.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전 고지) / 수동 deploy·무단 tag 금지.
