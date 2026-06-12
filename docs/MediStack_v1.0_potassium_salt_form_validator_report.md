# MediStack v1.0 — Potassium name_only Blocklist Validator 리포트

> 상태: **validator/test/docs/CI 구현 완료.** full index 데이터·src·alias·relation·queue는 **변경하지 않았다.**
> 정책 근거: `docs/MediStack_v1.0_potassium_salt_form_policy.md` (단기 A 유지 / 중기 C 조건부 — 본 validator가 C의 코드 가드).
> 구현 파일: `scripts/validate_potassium_name_only_policy.py` · fixture `scripts/fixtures/potassium_name_only_policy.json`.
> 기준 커밋(직전): `cae2516` · 작성일: 2026-06-13.

---

## 1. validator 목적

10k 확장 **전에** full index `name_only` 항목의 **칼륨 안전선을 코드로 고정**한다. 현재 칼륨 포함
name_only는 전부 salt-form/짝이온/복합제 co-ingredient이고 standalone 칼륨보충제는 0건이다. 이 상태를
validator로 박아, 성분 풀이 커지는 향후 확장에서 **standalone 칼륨보충제/전해질 보충 목적 제품이 유입되면
배포 게이트에서 hard fail** 하게 한다. **데이터는 수정하지 않는다**(삭제·필터링 없음, 위반 보고만).

핵심 안전 설계 — **부분일치 함정 회피**: "칼륨" 단어 포함만으로 차단하지 않는다. `ingredient_name`(주성분)
기준으로 염을 분류하고, 단일 주성분 여부 + 보충 목적 키워드로 판정한다. 그래서 `로사르탄칼륨정`(품목명에
"칼륨정"이 들어가도) ARB 염 → 허용이고, `염화칼륨`이 단일 주성분이면 → 차단이다.

## 2. 검사 대상 범위

- 대상: `covered_by_relation=false`(name_only) 항목 중 `item_name` 또는 `ingredient_name`에
  칼륨/포타슘/KCl 트리거가 있는 건.
- 제외: relation_card(`covered_by_relation=true`)는 기존 relation/full-index validator가 우선 관할하며,
  본 정책과 충돌하지 않는다(name_only 전용 검사).
- 무수정: 검사 대상을 분류·집계할 뿐 데이터 파일을 건드리지 않는다.

## 3. item_name 기준 칼륨 건수

**79건** — 화면 표시 품목명(`item_name`)에 "칼륨"이 노출되는 name_only. 앱 검색 인덱스가 실제 반입하는
필드(item_seq/item_name/normalized/company)에 해당하므로 **사용자 UI 실노출 칼륨 = 79**.

## 4. ingredient_name 기준 칼륨 건수

**139건** — 주성분(`ingredient_name`) 문자열까지 포함한 칼륨 건(품목명엔 브랜드만, 성분에만 칼륨염인 경우
포함). `ingredient_name`은 앱 검색 인덱스에 **미반입**이므로 139는 **데이터 감사 상한**이다. validator는
**139건 전수를 분류**한다(검사 대상 = 139).

## 5. salt-form allowlist

칼륨이 **비-칼륨 활성성분의 염(짝이온)** 이거나 **복합제 부수 성분**이면 허용. 사전:

| 토큰 | 분류 |
|---|---|
| 로사르탄칼륨 · 피마사르탄칼륨 · 아질사르탄메독소밀칼륨 · 아질사르탄칼륨 | ARB(고혈압) 염 |
| 클라불란산칼륨 · 묽은클라불란산칼륨 (오타변형 묽은클라불라산칼륨) | 아목시실린 복합 항생제 |
| 비스무트시트르산염칼륨 | 위장약 복합 |
| 글리시리진산이칼륨 · 글리시리진산디칼륨 | 감초 유래 항염 co-ingredient |
| 구아야콜설폰산칼륨 | 진해거담 복합 |
| 요오드화칼륨 | 종합비타민(활성=요오드) |
| 제일인산칼륨 · 제이인산칼륨 · 인산칼륨 | 완충/구강용품 |
| 황산칼륨 | 장 정결 복합 |

## 6. standalone potassium blocklist

칼륨 **보충/전해질 repletion** 목적이면 차단. 두 경로:

- **보충형 염이 단일 주성분(sole active)** → 차단: 염화칼륨 · 구연산칼륨(시트르산칼륨) · 글루콘산칼륨 ·
  아스파르트산칼륨 · 중탄산칼륨(탄산수소칼륨) · KCl/potassium chloride(라틴).
- **보충/전해질/저칼륨 보충 목적 키워드**(복합 여부 무관) → 차단: `칼륨보충` · `포타슘보충` ·
  `potassium supplement` · `전해질보충`/`전해질 보충` · `저칼륨혈증`.
- 키워드는 **반드시 phrase-level**이다. `칼륨정`·`칼륨` 단독은 키워드로 쓰지 않는다
  (`로사르탄칼륨정` 등 allowlist 염 오판 방지).

## 7. 현재 데이터 PASS 근거

`python3 scripts/validate_potassium_name_only_policy.py` → **RESULT: PASS (8/8)**.

| stats | 값 |
|---|---|
| name_only | 4,942 |
| 칼륨(item_name 기준) | 79 |
| 칼륨(ingredient_name 기준) | 139 |
| subject(검사 대상) | 139 |
| allowed_saltform | **138** |
| manual_review | **1** (점안액 co-ingredient) |
| **blocked_standalone** | **0** |
| 금지 필드 위반 | **0** |

→ subject 139 = allowed 138 + manual_review 1 + blocked 0. **standalone 칼륨보충제 0건** 확정. 전수 분류
결과 차단 0이므로 현재 5,500 데이터는 통과한다(데이터 무변경).

## 8. negative fixture FAIL 근거

`python3 scripts/validate_potassium_name_only_policy.py --selftest` → **SELFTEST: PASS (0 failures)**.

- positive 10건(로사르탄/피마사르탄/아질사르탄메독소밀/클라불란산/비스무트시트르산염/글리시리진산이·디/
  구아야콜설폰산/요오드화/황산 칼륨) → 전부 `allowed_saltform`.
- negative 9건(염화칼륨 서방정·브랜드·구연산칼륨·글루콘산칼륨·L-아스파르트산칼륨 단일·포타슘보충·
  전해질보충·저칼륨혈증·KCl) → 전부 `blocked_standalone`.
- **non-no-op(음성) 통합 검증**: 합성 인덱스에 `염화칼륨`(단일) 1건 주입 → 데이터 검사가 blocked=1로 FAIL.
  주입 없으면 blocked=0. → validator가 no-op이 아님(진짜로 standalone을 잡음)을 증명.

## 9. manual-review 기준

자동 차단하지 않고 사람 검토로 넘기는 경계(현재 데이터를 FAIL시키지 않음):

- 보충형 염(염화/구연산/글루콘산/아스파르트산칼륨 등)이 **복합제 co-ingredient**이고 보충 목적 키워드가 없는 경우.
- 칼륨은 있으나 **인식된 염 토큰이 없는** 경우(미래 신규 표기).

현재 데이터 manual-review **1건**: `뉴브이로토이엑스점안액`(8성분 복합 점안액, L-아스파르트산칼륨이
미량 co-ingredient) — 칼륨 보충제가 아니므로 비차단. req 9의 "점안액 다성분 co-ingredient = PASS 또는
manual-review" 경로에 해당. 동일 토큰이 **단일 주성분**(예 `엘아스파라진칼륨정/L-아스파르트산칼륨`)이면 차단.

## 10. 10k 확장 전 적용 효과

- 확장 전/후 **모든 push가 CI(deploy.yml validate job + validate.yml PR job)에서** 본 validator + selftest를
  통과해야 한다 → standalone 칼륨보충제가 name_only로 유입되면 **배포가 막힌다**.
- 성분 풀이 커져도 salt-form allowlist는 그대로 통과, 보충제는 차단, 경계는 manual-review로 분리되어
  **사람이 데이터 확장 PR에서 확인**할 수 있다(자동 삭제 없음).
- 정책 문서(A/C)의 "중기 C 조건부 유지"가 **코드 가드로 실체화**됨 — 10k 진입 게이트의 칼륨 항목 충족.

## 11. 향후 개선점

- **allowlist/blocklist 사전 확장**: 10k 수집에서 신규 칼륨염(예 신규 ARB 염·신규 복합제)이 나오면
  allowlist에 토큰 추가. manual-review 리포트가 그 신호가 된다.
- **단일/복합 판정 정교화**: 현재는 `ingredient_name` 구분자(`/·,+;` 등) 기반. nedrug 표기가 불규칙하면
  `is_combination` 같은 데이터 플래그(append-only)와 교차 검증 가능(별도 PM 승인).
- **manual-review 워크플로**: 현재는 리포트 출력. 건수가 늘면 별도 큐/리뷰 로그로 승격 고려(별도 승인).
- **app UX 연계는 범위 밖**: name_only는 "참고 정보 없음"만 표시(칼륨 주의 문구 금지). validator는 데이터
  계층 가드일 뿐, UI는 변경하지 않는다.

---

> 무변경 확인: 본 작업은 validator/fixture/docs/CI만 추가했다. full index(5,500)·alias(621)·product(583)·
> verified(545/13)·relation(30)·DATA_URL·src/app·queue를 변경하지 않았다. published/clinical_reviewed false 봉인 유지.
