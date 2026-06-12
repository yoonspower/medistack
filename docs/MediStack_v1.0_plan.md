# MediStack v1.0 — 계획 문서 (plan)

> 자기완결 계획 문서. v0.9 마감(alias 621 라이브·commit `b99f527`·tag 미생성) 직후 작성.
> **이 문서는 방향만 정리한다.** 코드·데이터·alias·queue·validator·src·relation·DATA_URL·export·tag 는 본 작업에서 일절 건드리지 않는다.
> 다음 세션은 이 문서만 읽고 v1.0 트랙을 이어갈 수 있다.

---

## 1. 현재 기준선 (v0.9 마감 스냅샷)

검증 일자 기준 라이브/로컬이 아래 수치와 **완전 일치**함을 확인하고 기록한다.

| 항목 | 값 | 비고 |
|---|---|---|
| latest commit | `b99f527` | Incorporate v0.9 surface aliases (618→621) |
| v0.8-beta tag | `030ee26` | 누적 태그 = v0.1/v0.2/v0.3/v0.5/v0.6/v0.7/v0.8-beta. **v0.9 무태그** |
| alias_count (meta) | **621** | = ingredient 38 + product 583 |
| ingredient_aliases | **38** | v0.4 Type A 확정 후 불변 |
| product_aliases | **583** | 단일 + 복합제 110 + brand_core 14 + HCTZ 112 + 표면형 3 |
| verified_item_seqs | **545 entries / 13 canonical** | 알렌드론산·토라세미드·목시플록사신·미노사이클린·독시사이클린·레보티록신·레보플록사신·메트포르민·시프로플록사신·오플록사신·푸로세미드·오메프라졸·히드로클로로티아지드 |
| relations (v0.2 export) | **30** | + excluded_v0_1 1 (렌더 금지) |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` | 불변 |
| export md5 | `401b097a1bd812b6da983b7f3dfc6d20` | 불변 |
| repo / local / live | `yoonspower/medistack` · `/Users/mac/AI work/medistack` · `https://yoonspower.github.io/medistack` | PAT push만 (repo생성/Pages/재실행 403) |

**v0.9 신규 3건 (표면형 개행 정제 → 실제 편입):**
- 신일모노독시엠캡슐 → 독시사이클린
- 레보펙신정250밀리그램 → 레보플록사신
- 레보펙신정500밀리그램 → 레보플록사신

**queue 표면형 개행 후보 = 0** (풀 소진). 복합제 deferred = 0.

**검증 상태 (v1.0 계획 작성 시점, 전부 PASS):**
```
v0.1 export ............... 12/12   v0.2 export ............... 15/15
v0.3 aliases .............. 16/16   surface forms (v0.9) ......  5/5
TypeB suite ...............  7/7    combo suite ...............  9/9
combo AR suite ............ 13/13   bulk candidates ........... 152/152
combo approved_ready ...... 13/13   smoke alias regression ....  7/7
smoke HCTZ disclosure ..... PASS    live HTTP ................. 200
```

---

## 2. v0.1 ~ v0.9 완료 요약

핵심은 **alias 진행이 단조 증가하며 풀이 소진된 곡선**이라는 점이다. v1.0은 이 곡선의 자연스러운 종착(=안정판)이다.

| 버전 | 핵심 | alias 누계 | 비고 |
|---|---|---|---|
| v0.1 | verified_reference 관계 **19건** | — | 봉인. 천장 = verified_reference |
| v0.2 | relation 19→**30**, 검색/필터 UX | — | 식약처 nedrug 원문 검증 |
| v0.3-beta | alias / 검색 안정화 | 53→66 | 제품명·성분명 alias, prefix 매칭, fail-soft |
| v0.4 | Type A/B alias + verified_item_seqs 화이트리스트 | 66 | validator#8 일반화 |
| v0.5 | bulk alias pipeline (수집→검증→승인→batch) | **206** | nedrug 페이지네이션·incorporation-aware |
| v0.6 | **단일성분 천장 382** | **382** | batch1~9 소진 |
| v0.7 | combo tier B1 (메트/알렌/오메 **110** + brand_core **14**) | **506** | 복합제 부분정보 고지 동반 |
| v0.8 | **HCTZ combo 112** (ARB 98 + ARB+CCB 14) | **618** | 칼륨 반전 고지·칼륨보존이뇨제 영구 차단 |
| v0.9 | 표면형 개행 정제 **3건** | **621** | nedrug 개행 품목명 정규화, queue 소진 |

곡선 해석: 단일성분(382) → 복합제(+124) → 표면형(+3). **deferred 0 · queue 표면형 후보 0** → alias 대량 확장 트랙은 사실상 한계에 도달. relation은 v0.2 이후 **30 고정**(임상판단 행은 reviewer 전까지 봉인).

---

## 3. v1.0 후보 트랙

| 트랙 | 내용 | 상태 / 게이트 |
|---|---|---|
| **A. clinical reviewer / 검수자 플로우** | reviewer 요건·`review_log` 스키마·`reviewed_by`/`reviewed_at` 설계 문서화. **승격은 금지, 준비만.** | 외부 검수자 확보 = 선행 조건. v1.0은 레일만 깐다 |
| **B. relation 30 유지 상태 UX 안정화** | 검색/고지/empty/error UX 회귀 테스트 강화, 접근성·문구 점검. relation 불변. | data/relation 무변경. src 변경 시 별도 게이트 |
| **C. 전체 품목명 검색 인덱스 분리 설계** | 표면형 전체 품목명 검색을 alias 풀과 분리한 **런타임 인덱스** 설계 (데이터에 박지 않음, append-only 원칙). | **설계 문서만**. 구현은 별도 게이트 |
| **D. 루프이뇨제 복합제 가능성 검토** | 푸로세미드·토라세미드 복합제 실재 여부 범위 검토. 존재 시 HCTZ 칼륨 반전 고지 틀 재사용. | **검토만**. 편입은 PM 명시 승인 + 안전 게이트 |
| **E. published / clinical_reviewed 전환** | **외부 검수 전까지 보류.** 천장 = verified_reference 유지. | 영구 봉인 (reviewer 확보 전) |
| **F. 제품 / 구매 / 제휴 UI** | **계속 금지.** 제품 링크·구매 버튼·제휴·제품 예시·제품 필드 일절 추가 금지. | 영구 금지 |

---

## 4. 추천 v1.0 방향

**“서비스 안정판(stability release)” 우선 — alias 대량 확장보다 품질·신뢰·문서화 강화.**

근거:
1. **alias 풀 소진** — 단일성분 천장(382)·복합제(+124)·표면형(+3) 모두 한계. deferred 0, queue 표면형 후보 0. 추가 확장은 한계효용이 급감하고 노이즈·오매칭 위험이 커진다.
2. **진짜 잠금 해제는 clinical reviewer** — relation 확장·published 승격은 외부 검수자가 게이트다. v1.0에서 할 수 있는 건 **레일 깔기**(체크리스트·스키마·review_log 설계)뿐, 실제 승격은 금지.
3. **안정판의 정의** — medical claim 확장 없이: ① 검색 UX / 고지 UX 회귀 테스트 강화, ② 전체 품목명 검색 인덱스 분리 **설계**, ③ clinical reviewer 준비 문서화, ④ 검증 문서 정비.

v1.0 불변 고정:
- **relation 30 유지** · **DATA_URL 유지** · **data export 유지**.
- **medical claim 확장 금지** (published/clinical_reviewed 임의 전환 금지).
- alias는 검색 보조일 뿐 의학 정보가 아니라는 위치 유지.

즉 v1.0 = **“데이터를 더 쌓는 버전”이 아니라 “있는 데이터를 안전하게 굳히고 다음 단계(검수자) 레일을 까는 버전.”**

---

## 5. 절대 금지 (v1.0 불변)

- **relation 확장 금지** (relation 30 고정 · 신규 생성·풀 확장 금지).
- **DATA_URL 변경 금지** (`./data/medistack_v0.2_beta_export.json`).
- **data export 변경 금지** (v0.1 봉인 · v0.2 export md5 `401b097a` 불변).
- **published / clinical_reviewed 임의 변경 금지** (천장 = verified_reference, reviewer 확보 전 영구 봉인).
- **제품 / 구매 / 제휴 UI 추가 금지** (제품 링크·구매 버튼·제휴·제품 예시·제품 필드).
- **칼륨 제품 링크 금지** · 칼륨 행 `product_link_allowed=false` + 고지 유지.
- **에스오메프라졸 / 15행(id15) 재편입 금지** (alias·relation 모두). id16(×Mg)은 정상 live이므로 혼동 주의.
- **칼륨보존이뇨제 복합제 영구 차단** · HCTZ 외 복합제 basis 추가 금지.
- **alias / queue 임의 수정 금지** (반영은 PM 명시 승인 batch만).
- **tag 생성 금지** (본 작업 · 무단 tag 금지).
- **수동 deploy 금지** (main push 자동 배포만).
- **scripts/__pycache__ 커밋 금지**.

---

## 6. 다음 단계 제안 (v1.0 로드맵)

순차 실행 권장. 각 단계는 PM 게이트 후 진행하며, **문서/설계 단계는 코드·데이터 무변경**, 구현·테스트 강화 단계는 별도 게이트.

| 단계 | 작업 | 매핑 트랙 | 산출물 | 변경 범위 |
|---|---|---|---|---|
| **v1.0-A** | clinical reviewer checklist 문서 | A | reviewer 요건·`review_log` 스키마·`reviewed_by`/`reviewed_at` 설계 (승격 금지) | 문서만 |
| **v1.0-B** | 전체 품목명 검색 인덱스 분리 설계 | C | 런타임 인덱스 설계 문서 (데이터 미변경, append-only) | 문서만 |
| **v1.0-C** | 앱 UX 고지 / 검색 회귀 테스트 강화 | B | 검색·고지·empty·error 회귀 테스트 보강 + smoke 확장 | src/scripts (별도 게이트) |
| **v1.0-D** | v1.0-beta 릴리즈 준비 | — | release notes · handoff · (PM 승인 시) `v1.0-beta` 태그 스냅샷 | 문서 + 태그(승인 시) |

각 단계 진입 시 본 문서 §1 기준선과 §5 금지를 재확인한다. v1.0-D의 태그는 **PM 명시 승인 시에만** `b99f527`(또는 이후 마감 커밋) 스냅샷으로 생성하며 deploy를 발동하지 않는다.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전 고지).
