# MediStack v1.0-C — 검색/고지/empty/error 회귀 smoke 리포트

> v1.0-C 트랙. full drug name index / name_only UX 도입 **전에** 현행 검색·고지·empty·degrade 동작을 **실제 `guards.js` + `render.js`** 로 고정한 회귀 기준선.
> 이번 작업은 **테스트/픽스처/리포트만** 추가했다. 코드·데이터·alias·queue·validator·src·relation·DATA_URL·export·tag 무변경. **src 수정 0**(STOP 조건 미해당).

---

## 1. 목적

사용자가 약 이름을 검색했을 때 "안 나오는 약이 많다"는 체감 문제를 줄이기 위해 v1.0 이후 full drug name index / name_only UX 를 도입할 계획이다(설계 = `MediStack_v1.0_full_drug_search_index_design.md`).

**구현 전에**, 현재 검색·고지·empty·error 동작이 깨지지 않도록 회귀 smoke 를 만든다. 이후 full index 작업이 기존 동작을 바꾸면 이 smoke 가 FAIL 하여 회귀를 잡는다.

---

## 2. 추가 파일 (3건, 전부 신규)

| 파일 | 역할 |
|---|---|
| `scripts/smoke_search_regression_v1_0.py` | 회귀 smoke 러너 (Python 외부 + node mjs 내부) |
| `scripts/fixtures/search_regression_v1_0.json` | 선언적 기대값(실제 guards.js 측정 ground-truth) |
| `docs/MediStack_v1.0_search_regression_smoke_report.md` | 본 리포트 |

⚠️ **픽스처 위치:** PM 스펙은 `tests/fixtures/` 였으나, 리포 기존 컨벤션이 `scripts/fixtures/`(예: `v0_4_typeB`, `v0_7_combo`, `v0_7_combo_ar`)라 **일관성을 위해 `scripts/fixtures/` 로 배치**했다. 원하면 이동은 trivial.

기존 smoke(`smoke_alias_regression.py`, `smoke_hctz_disclosure.py`)는 **수정하지 않았다**(이미 통과 중 · 신규 smoke 가 상위집합).

---

## 3. 테스트 하네스

`guards.js`/`render.js` 는 ES module 이고 repo 에 `package.json` 이 없으므로, 두 파일을 임시 디렉토리에 복사 + `package.json {"type":"module"}` 후 node 로 import 한다. `render.js` 가 `./guards.js` 를 import 하므로 **두 파일 모두 복사**한다. 기대값 소스는 라이브 데이터(`medistack_v0.2_beta_export.json` relation 30 + `medistack_v0.3_aliases.json` alias 621).

**핵심:** 회귀 신호를 위해 로직을 재구현하지 않고 **실제 `guards.js`/`render.js` export 함수를 호출**한다. → src 가 바뀌면 smoke 가 잡는다.

---

## 4. 검증 레이어 / 케이스

| 레이어 | 대상 | 사용 함수 |
|---|---|---|
| **E. 기준선** | full drug index 데이터 파일 미존재 + `data.js` 에 `name_only`/`full_index`/`full_drug` 미배선 | (Python 파일/배선 검사) |
| **A. behavior** | 검색 결과 수 + `aliasHint` 플래그 | `getRenderableRelations`·`buildAliasIndex`·`filterRelations`·`aliasHint` |
| **B. render** | `renderAliasHint` HTML(복합제 배지 / 칼륨 주의 / alias 안내 / empty) | `renderAliasHint` |
| **C. list** | `renderListResults` HTML(0건 → 카드 없음 / N건 → 카드 존재) | `renderListResults` |
| **D. id15** | relation id15(에스오메프라졸×B12) 렌더 풀 미포함 | `getRenderableRelations` |
| **F. degrade** | alias 인덱스 부재(null/빈/garbage) → relation-only 정상 degrade | `buildAliasIndex`·`filterRelations` |

### 필수 smoke 케이스(PM 7종) ↔ 본 smoke 매핑

| PM 케이스 | 본 smoke | 기대값(측정 ground-truth) |
|---|---|---|
| 1. relation_card | A.relation_card | 타리비드→오플록사신 **3** · 포사맥스→알렌드론산 **1** · 토렘→토라세미드 **2** |
| 2. excluded/fail-safe | A.excluded_failsafe + D | 넥시움 **0** · relation id15 미렌더 |
| 3. combo notice | A.combo_notice + B.combo_render | 가드메트정…(메트포르민) / 대웅알렌드로네이트디정 → `comboBases` 표시 + 렌더 "복합제" 배지, "칼륨 주의" 없음 |
| 4. HCTZ potassium | A.hctz_potassium + B.hctz_render | 미카르디스플러스정40/12.5 → `hctzPotassiumNotice=true` + 렌더 "칼륨 주의" · 단일 HCTZ 직접검색 → 오작동 없음(hint=null) |
| 5. empty result | A.empty + B.empty_render + C.empty_list | 존재하지않는약물xyz / asdfqwer → **0** · `renderAliasHint`="" · 카드 row 없음 |
| 6. alias surface | A.alias_surface | 신일모노독시엠캡슐→독시사이클린 **3** · 레보펙신정250/500밀리그램→레보플록사신 **3** |
| 7. full index future baseline | E + A.full_index_future_baseline + F | 아세트아미노펜/타이레놀 → **0**(relation-only degrade) · name_only 미활성 · 인덱스 부재 시 정상 degrade |

---

## 5. 실행 / 결과

```
python3 scripts/smoke_search_regression_v1_0.py
```

**결과: SEARCH REGRESSION: PASS** — 전 케이스 불변(약 70 체크).
- E 기준선 4/4 · A behavior(15 쿼리) · B render 15 · C list 6 · D failsafe 1 · F degrade 6 전부 PASS.

전체 검증 배터리(동시 PASS):
```
v0.1 12/12 · v0.2 15/15 · v0.3 16/16 · surface 5/5
TypeB 7/7 · combo 9/9 · combo_AR 13/13 · combo_approved_ready 13/13 · bulk 152/152
smoke_alias_regression 7/7 · smoke_hctz_disclosure PASS · search_regression PASS
```

불변 수치: alias_count **621**(product 583·ingredient 38) · verified_item_seqs **545/13** · relation **30** · DATA_URL `./data/medistack_v0.2_beta_export.json` · published **false** · clinical_reviewed **false**.

---

## 6. full drug index 작업 시 이 기준선의 역할

`full_index_future_baseline` 그룹(아세트아미노펜·타이레놀 → 0)은 **name_only UX 도입 시 기대값이 바뀌는 미래 신호**다. full index/name_only 가 구현되면:
1. 이 그룹의 기대값을 `count 0` → `name_only 표시`로 **의도적으로 갱신**해야 한다(픽스처 수정).
2. 그 외 그룹(relation_card·combo·HCTZ·empty·surface·degrade)은 **계속 불변**이어야 한다 — 하나라도 바뀌면 회귀.
3. E 기준선 체크는 name_only 배선 후 **반대로** 갱신(미배선 → 배선 확인)된다.

즉 본 smoke 는 "무엇이 바뀌어도 되고(미래 신호 1그룹), 무엇은 절대 안 바뀌어야 하는지(나머지 전부)"를 코드로 못박는다.

---

## 7. 준수 / STOP 조건

- **src 수정 0.** 모든 케이스가 기존 export 함수(`filterRelations`/`aliasHint`/`renderAliasHint`/`renderListResults`/`buildAliasIndex`/`getRenderableRelations`)로 테스트 가능 → 테스트 보조 export 불필요 → STOP 미발동.
- data/alias/queue/export/relation/DATA_URL/clinical_reviewed/published 무변경.
- full drug index 파일 미생성(설계만) · app UX 기능 변경 없음 · tag 미생성 · `scripts/__pycache__` 미커밋.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / relation 없는 약은 (도입 후) name_only 로만 표시 / 회귀 smoke 는 실제 guards.js·render.js 를 호출해 고정한다.
