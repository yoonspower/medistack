# MediStack — relation_card 근거/출처 표시 UI 설계 (v1.2, DESIGN ONLY)

> 작성일: 2026-06-14. **설계 문서 단독 — `src/` 코드·데이터·CSS 한 줄도 변경하지 않는다.**
> 본 문서는 `MediStack_source_attribution_design.md`(source 상속 + 공개 차단 gate 설계)를 **UI 표현 수준으로 구체화**한 것이다. 실부여(`source_status`)·gate 실배선·렌더 변경은 전부 **별도 구현 단계**(PM 승인)다.
> published / clinical_reviewed = **false 유지**(이 문서는 그 전환을 전제하지 않는다).

---

## 0. 한 줄 요약

relation_card 상세 하단에 **relation(41) 단위 source 를 상속 표시**한다(카드 1,072건은 자기 relation 의 출처를 그대로 물려받음). 표시는 "근거/출처" 라벨 + 출처 유형 + 원문 링크 + 접기/펼치기(`<details>`) 출처 상세로 구성한다. 공개(public) 모드에서 source 가 confirmed 가 **아닌** relation 은 **fail-closed 로 노출하지 않고 name_only 로 강등**한다. clinical_reviewed=false 인 만큼 모든 문구는 **과신을 유발하지 않는 면책 톤**을 유지한다.

---

## 1. 현재 상태 (출발점 — 이미 구현되어 있음)

- 데이터: `data/medistack_v0.2_beta_export.json` 의 relation **41/41** 이 `source` 객체 보유.
  - `source.type` = `"허가사항"`
  - `source.url` = 식약처 nedrug `getItemDetail?itemSeq=…`
  - `source.pointer` = `식약처 허가사항(nedrug) / 품목명(itemSeq …) / 사용상의 주의사항-상호작용 / 내용 / 확인일 YYYY-MM-DD`
- 렌더: `src/js/render.js` `renderDetail()` 의 `.src` 블록이 이미 다음을 출력한다 — `<span class="lab">출처</span>` + `source.type` + `원문 보기 ↗`(url 있을 때) + `<details><summary>출처 상세</summary>`(pointer 있을 때).
- 상속: relation_card(1,072)는 별도 출처 필드를 가지지 않으며, 라우팅된 relation(41)의 `rel.source` 를 그대로 표시한다 → **상속은 신규 발명이 아니라 현 코드에 이미 구현**. (`scripts/smoke_disclaimer_render.py` 가 출처 출력 검증.)

→ 본 설계는 **이 기존 동작을 깨지 않는 범위에서** ① 표현(라벨/문구/접기·펼치기)을 개선하고, ② 공개 모드 강등 UX 를 스펙으로 고정한다.

### 현 `renderDetail` `.src` 블록 (변경 대상 아님 — 참조용)

```
[출처] · 허가사항   원문 보기 ↗
  ▸ 출처 상세                       ← <details> 접힘 기본
      식약처 허가사항(nedrug) / 레보플록사신수화물정(itemSeq …) /
      사용상의 주의사항-상호작용 / … / 확인일 2026-06-07
```

CSS 클래스(기존, 변경 없음): `.src` / `.src .lab` / `.src a` / `.src details` / `.src summary` / `.src .ptr`.

---

## 2. 부여 단위 — relation(41) 상속 (불변 원칙)

- 출처는 **relation 41건 단위로 부여**하고 relation_card 1,072건은 **상속**한다.
- **카드별 1,072건 개별 출처 블록을 신설하지 않는다.** (1,072 = alias/품목 풀에서 파생된 표시 단위 — 의학적 근거는 relation 41에 있다.)
- 이유: 같은 relation 을 공유하는 수십~수백 개 카드가 동일 출처를 갖는데 카드마다 출처를 따로 두면 정합성 붕괴·과표시 위험. 상속이 단일 진실원(single source of truth)을 보장한다.

---

## 3. 표시 위치 / 레이아웃 (설계)

### 3.1 위치
- relation_card 상세 화면에서 **본문(display_text) → 참고 안내(management) → 칼륨 주의(해당 시) → 근거/출처 → 공통 면책** 순서 중 **공통 면책 바로 위**에 둔다(현 `renderDetail` 의 `.src` 위치 그대로).
- 근거/출처는 **상세의 보조 정보**다. 화면 상단(제목·분류·본문)을 밀어내지 않고 하단에 배치해 시각적 위계를 유지한다.

### 3.2 라벨 문구 개선안: "출처" → "근거/출처"
- 현 라벨 `출처` → **`근거/출처`** 로 변경 제안.
- 이유: 사용자에게 "이 카드의 내용이 어디서 왔는가"를 더 명확히 전달. 단, "근거"가 임상적 단정으로 읽히지 않도록 **바로 아래 한 줄 면책**(아래 §5)을 동반한다.
- (구현 시) `<span class="lab">근거/출처</span>` 로 텍스트만 교체. 클래스·구조 불변.

### 3.3 접기/펼치기(collapse/expand) 패턴
- **1단계(항상 보임)**: `근거/출처 · 허가사항` + `원문 보기 ↗`(url 있을 때).
- **2단계(접힘 기본, `<details>`)**: `출처 상세` summary → 펼치면 `source.pointer`(품목명·항목·확인일 포함).
- 패턴 유지 이유: pointer 는 길다(품목명+itemSeq+항목+인용+확인일). 항상 펼치면 면책·본문보다 출처 텍스트가 더 길어져 위계가 뒤집힌다. **요약은 항상, 상세는 요청 시**가 정보 밀도·신뢰의 균형점.
- 모바일에서도 `<details>` 는 네이티브 토글이라 추가 JS 불필요(현 구조 유지).

### 3.4 와이어(텍스트) — 개선 후 목표 화면
```
─────────────────────────────  (상단 구분선, .src)
근거/출처 · 허가사항            원문 보기 ↗
이 정보는 일반 참고용입니다.     ← (신규) 한 줄 면책, .src 내 보조문
  ▸ 출처 상세
      식약처 허가사항(nedrug) / ○○정(itemSeq …) /
      사용상의 주의사항-상호작용 / … / 확인일 2026-06-07
─────────────────────────────
[공통 면책 disclaimers.common]   ← 기존, 불변
```

---

## 4. source_status / source_checked_at 표시 정책 (설계)

### 4.1 source_checked_at(확인일)
- **표시함.** 단, **별도 강조 배지로 만들지 않고** `<details>` 의 pointer 안에 있는 `확인일 YYYY-MM-DD` 를 그대로 둔다(현 구조).
- 이유: 확인일은 "허가사항을 마지막으로 대조한 날짜"라는 사실 기록일 뿐, 정확성·최신성 보증이 아니다. 1단계(항상 보임) 영역에 큰 글씨로 올리면 "검증된 최신 정보"로 과신될 수 있어 **상세 영역에 유지**한다.
- 확인일이 오래된 경우의 "갱신 지연 가능" 고지는 공통 면책/이용약관(`갱신이 지연될 수 있습니다`)이 커버한다 — 카드별 "오래됨" 경고는 만들지 않는다(과잉 신호 방지).

### 4.2 source_status(confirmed / needs_review / missing)
- **사용자 화면에 status 문자열을 그대로 출력하지 않는다.** (`confirmed`/`needs_review` 라벨 노출 = 사용자 혼란 + 과신/불신 양극화.)
- status 는 **공개 모드 라우팅의 내부 게이트 입력**으로만 쓴다(§6). 즉:
  - `confirmed` → relation_card 정상 표시(출처 블록 그대로).
  - `confirmed` 아님(`needs_review`·`missing`·부재) → **그 relation 을 노출하지 않고 name_only 로 강등**(아래 §6). 이 경우 사용자는 출처 블록 자체를 보지 못한다(애매한 "출처 확인 중" 라벨 없음).
- 즉 **"출처 확인 중" 같은 중간 라벨은 화면에 없다.** confirmed 면 정상, 아니면 강등 — 단일 경로.
- ※ 현 데이터는 41/41 이 source 객체를 가지나, **confirmed 승격은 규제 자문·검토(게이트 STOP #1·#2) 이후**다. 임의 confirmed 자동 부여 금지.

---

## 5. 과신 방지 문구 (clinical_reviewed=false 전제)

근거/출처 블록 안/주변에 쓸 **권장 문구**:

- 라벨: **"근거/출처"**
- 보조 한 줄(신규, `.src` 내): **"이 정보는 일반 참고용입니다."**
- 공통 면책(기존 `disclaimers.common`, 출처 블록 바로 아래 유지)에 이미 포함: "진단, 처방, 복약 지시가 아니며, 실제 복용 여부나 시간 간격은 의사 또는 약사와 상담하세요."
- 필요 시 추가 권장 문구: **"복용 판단은 약사 또는 의사와 상담하세요."**

### 금지 표현 (이 문서·구현 어디에도 사용 금지)
- "검증 완료"
- "의학적으로 확정"
- "약사 검수 완료"
- "식약처 승인"

→ 출처가 식약처 허가사항이라는 사실은 표시하되(`근거/출처 · 허가사항`), "승인/검수 완료/확정" 같은 **권위 단정**으로 번지지 않게 한다. "허가사항을 바탕으로 정리한 참고 정보"라는 톤(공통 면책과 동일)을 유지한다.

---

## 6. 공개 차단 Gate (fail-closed) — UX 스펙

`MediStack_source_attribution_design.md` §4 의 `publicRelationGate` 를 재인용한다(**스펙만, src 배선 금지**).

```js
// 공개 모드 전용. mode='public' 일 때만 게이트 적용. 'internal'(현행 라이브)은 전체 표시 유지.
// 반환: 'relation_card'(정상 표시) | 'name_only_demote'(품목명만).
// fail-closed: source_status 가 'confirmed' 가 아니면(needs_review·missing·부재 전부) 무조건 강등.
function publicRelationGate(rel, mode) {
  if (mode !== 'public') return 'relation_card';            // 내부/현행: 무변경
  return (rel && rel.source_status === 'confirmed')
    ? 'relation_card'
    : 'name_only_demote';                                   // confirmed 아니면 전부 품목명 강등
}
```

### 6.1 정책 (OR 선택지 제거 — fail-closed)
- 출처 **미확정 relation 은 공개 모드 화면에서 노출하지 않는다.**
- **"출처 확인 중" 라벨로 노출하지 않는다**(중간 노출 금지).
- 강등은 **표시 라우팅**일 뿐 — **relation 41건 데이터는 한 건도 삭제되지 않는다**(핵심 자산 무손실). 추후 confirmed 승격 시 자동 복귀.
- 어떤 보조 플래그(예: `source_required_for_public_release`)도 이 강등을 우회하지 못한다(우회 분기 없음).

### 6.2 강등 시 사용자가 보는 화면 (UX)
공개 모드에서 미확정 relation 에 매핑된 약을 검색하면, 사용자는 relation_card 가 아니라 **name_only(품목명 확인) 화면**을 본다 — 즉 `renderNameOnlyResults()` 경로(`MediStack_name_only_ux_improvement_v1_2.md` 의 개선 문구 적용 대상).
- 상호작용/영양소/복용지시/근거·출처 블록 **전부 미표시**(의학정보 0).
- 사용자는 "출처가 보류된 카드"라는 사실을 **알 필요가 없다** — 그냥 "현재 등록된 약-영양소 참고정보 없음(품목명만 확인)"으로 보인다. (보류 상태를 노출하면 오히려 "숨겨진 정보가 있다"는 추측·과신 유발.)

### 6.3 내부 모드(현행 라이브) 무변경 보증
- `mode !== 'public'` 이면 항상 `relation_card` → **현 라이브(내부 모드) 동작 무변경.** relation 41 데이터·relation_card 1,072 렌더 1줄도 안 건드린다.
- 즉 본 게이트는 **공개 전환 시점에만** 의미를 가지며, 그 전환은 `source_status` 실부여 + gate 실배선이 전제(둘 다 v1.2 범위 밖).

### 6.4 상태표 (source_attribution_design 과 정합)

| source_status | 공개(public) 모드 | 내부(현행 라이브) |
|---|---|---|
| `confirmed` | relation_card 정상 표시(근거/출처 블록 포함) | relation_card |
| `needs_review` | **name_only 강등**(품목명만) | relation_card |
| `missing` / 부재 | **name_only 강등**(품목명만) | relation_card |

---

## 7. 기존 렌더 구조와의 정합 (호환성 체크)

- `renderDetail()` 의 `if (rel.source)` 분기, `.src` 클래스, `<details>` 패턴 = **그대로 유지**. 본 설계의 표현 개선은 (구현 시) ① 라벨 텍스트 `출처`→`근거/출처`, ② `.src` 내 한 줄 면책 추가 두 가지뿐 — 구조·클래스 불변.
- `isRenderable()`(필수 필드 가드)·`commonDisclaimer()` fail-safe·칼륨 고지 플래그 로직 = **무관·무변경**.
- `smoke_disclaimer_render.py` 의 출처 출력 검증 = 라벨 텍스트 변경 시 **기대 문자열만 갱신**(구현 단계에서 동반). pointer/url 출력 형식은 불변.
- 공개 모드 게이트는 `renderNameOnlyResults()` 경로를 재사용(신규 렌더 컴포넌트 불필요).

---

## 8. 이번 단계 경계 (금지 / 허용)

- ✅ 허용: 본 설계 문서 + 표현 개선안(라벨/문구/접기·펼치기) + 공개 모드 강등 UX 스펙 + `publicRelationGate` 스펙 재인용.
- ❌ 금지: relation 41 데이터 수정 / `source_status`·`source_checked_at` 실부여 / gate 함수 `src/` 배선 / `render.js` `.src` 블록·라벨 실변경 / relation_card 1,072 렌더 변경 / 실제 강등·삭제·숨김 / DATA_URL·export 변경 / published·clinical_reviewed 전환.

### 향후 별도 구현 작업 (이 문서가 아닌, 승인 후 별개 태스크)
1. relation 41 에 `source_status` / `source_checked_at` 필드 **append-only 부여**(confirmed 승격은 규제 자문·검토 후) → 새 버전 export + validator.
2. `render.js` `.src` 라벨 `근거/출처` + 한 줄 면책 텍스트 변경 → `smoke_disclaimer_render.py` 기대문자열 갱신.
3. `publicRelationGate` 를 라우팅 경로에 배선(`mode` 도입, name_only 강등 분기) → search regression smoke 갱신.

> 공개 게이트(STOP #2·#3): relation source confirmed 승격 + 미확정 강등 설계 완료 전 relation_card 일반 공개 금지. 승격 절차는 규제 자문(STOP #1) 이후. 본 문서는 **설계까지만**이며, 데이터·코드 무손실(라우팅 기반)을 보증한다.
