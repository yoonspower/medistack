# MediStack — Source Attribution 설계 (relation 30 단위 + 공개 차단 Gate)

> 작성일: 2026-06-13. **설계 + 공개 모드 gate 설계까지만.** relation 30건 데이터·relation_card 558건 렌더는 한 줄도 변경하지 않으며, 실제 강등/삭제/숨김 구현은 별도 단계(PM 승인). 게이트 = `MediStack_public_release_legal_safety_checklist.md`.

---

## 1. 부여 단위 — relation 30건 (NOT 558건)

- 출처는 **relation 30건 단위로 부여**한다. relation_card 558건은 relation 30건의 source metadata를 **상속**한다.
- 카드별 558건 출처를 **별도로 관리하지 않는다.** (558 = alias/verified_item_seqs 풀에서 파생된 표시 단위. 의학적 근거는 relation 30에 있다.)

### 현재 구조 (이미 존재 — 본 설계의 출발점)
- `data/medistack_v0.2_beta_export.json`의 relation 30건은 **전부(30/30)** 다음 `source` 객체를 가진다:
  - `source.type` = `"허가사항"` (30/30)
  - `source.url` = 식약처 nedrug `getItemDetail?itemSeq=…` (30/30)
  - `source.pointer` = 상세 인용문 — `식약처 허가사항(nedrug) / 품목명(itemSeq …) / 사용상의 주의사항-상호작용 / 내용 / 확인일 YYYY-MM-DD` (30/30, 확인일 포함)
- 렌더: `render.js renderDetail()`이 `rel.source.type` + `원문 보기↗`(url) + `<details>출처 상세</details>`(pointer)를 상세 하단에 출력 → **relation_card는 이미 relation source를 상속 표시**한다(코드 변경 불필요, `smoke_disclaimer_render.py` S4가 전 30건 출력 확인).

→ 즉 "상속 구조"는 신규 발명이 아니라 **현 코드에 이미 구현**되어 있다. 본 설계는 이를 **공식 필드로 형식화 + 공개 게이트(source_status)를 부가**한다.

---

## 2. 설계 필드 (relation 단위)

| 필드 | 의미 | 현재 매핑 |
|---|---|---|
| `relation_id` | 관계 식별자 | 기존 `rel.id` (1~31, 15 제외) |
| `relation_source_type` | 출처 유형 | 기존 `source.type` = `허가사항` |
| `relation_source_title` | 출처 제목(품목명/문서명) | `source.pointer` 내 품목명 — 형식화 시 분리 |
| `relation_source_url` / `citation` | URL 또는 인용 | 기존 `source.url` / `source.pointer` |
| `source_checked_at` | 출처 확인일 | `source.pointer` 내 `확인일 YYYY-MM-DD` — 형식화 시 필드화 |
| `source_confidence` | 출처 신뢰도 | 신규(현 데이터 `evidence_level` high25/moderate5 와 별개 — 출처 정합 신뢰도) |
| `source_required_for_public_release` | 공개 전 출처 필수 여부 | **상수 `true`** (모든 relation · 문서용 정책 상수 · §4 게이트를 우회하지 않음) |
| `source_status` | `confirmed` / `missing` / `needs_review` | **신규 — 공개 게이트의 핵심** |

- **append-only 원칙**: 형식화 시 기존 `source.{type,url,pointer}` 의미를 보존한 채 위 필드를 **추가**한다(기존 필드 제거·의미 변경 금지). 이번 단계는 **부여하지 않고 설계만** 한다.
- `source_status` 초기값 정책(설계): 현재 30건은 type+url+pointer 가 모두 있으므로 `needs_review` 후보지만, **confirmed 승격은 규제 자문/검토를 거친 뒤**에만(게이트 STOP #1·#2). 임의 confirmed 자동 부여 금지.

---

## 3. 화면 표시 (상속, 설계)

- relation_card 하단에 **relation 단위 source 를 상속 표시**한다(현 `renderDetail` 동작 유지).
- 표시: 출처 유형 + 원문 링크(있으면) + 출처 상세(pointer/citation). 카드별 개별 출처 블록을 새로 만들지 않는다.

---

## 4. 공개 차단 Gate (설계 — 구현 금지)

### 정책 (OR 선택지 제거)
- 출처 **미확정 relation 은 화면에서 노출하지 않는다.**
- **"출처 확인 중" 라벨로 노출하지 않는다.** (애매한 중간 노출 금지)
- `source_status` 가 `confirmed` 가 **아닌** relation 은 **public release 에서 relation_card 표시 금지.**
- 출처 미확정 relation 에 매핑된 약품은 **공개 모드에서 name_only 로 강등**한다(품목명 확인만, 의학정보 0).

### Gate 함수 (설계 스펙 — 실배선 금지)
순수 함수. 공개 모드에서 relation 단위 라우팅 결정만 반환한다. **이번 단계는 이 스펙/문서까지만 — `src/` 렌더 경로에 배선하지 않는다.**

```js
// 공개 모드 전용. mode='public' 일 때만 게이트 적용. 'internal'(현행)은 전체 표시 유지.
// 반환: 'relation_card'(정상 표시) | 'name_only_demote'(품목명만).
//       ※ 'hidden' 은 source 자체 부재 시를 위한 미구현 설계 옵션 — 본 함수는 반환하지 않는다(§5 주 참조).
// fail-closed: source_status 가 'confirmed' 가 아니면(needs_review·missing·부재 전부) 무조건 강등.
//   다른 플래그(예: source_required_for_public_release)는 이 강등을 절대 우회하지 못한다.
function publicRelationGate(rel, mode) {
  if (mode !== 'public') return 'relation_card';            // 내부/현행: 무변경
  return (rel && rel.source_status === 'confirmed')
    ? 'relation_card'
    : 'name_only_demote';                                   // confirmed 아니면 전부 품목명 강등
}
// source_required_for_public_release=true 는 '공개 전 출처 필수' 정책 상수(문서용)이며,
// 게이트 판정을 우회하는 입력으로 쓰지 않는다(우회 분기 의도적 제거 = fail-closed).
```

- **불변 보증**: `mode !== 'public'` 이면 항상 `relation_card` → 현 라이브(내부 모드) 동작은 **무변경**. relation 30 데이터·relation_card 558 렌더 1줄도 안 건드린다.
- **fail-closed 보증**: 공개 모드에서 `source_status` 가 `confirmed` 가 아닌 relation 은 어떤 플래그로도 relation_card 로 노출될 수 없다(우회 분기 없음).
- 강등은 **표시 라우팅**일 뿐 — relation 데이터 삭제가 아니다. **relation 30건은 한 건도 사라지지 않는다**(핵심 자산 보존).

---

## 5. 출처 미확정 relation 공개 정책 (요약)

| source_status | 공개 모드 동작 | 내부 모드(현행) |
|---|---|---|
| `confirmed` | relation_card 정상 표시 | relation_card |
| `needs_review` | **name_only 강등** (품목명만) | relation_card |
| `missing` | **name_only 강등** (품목명만) | relation_card |

- `confirmed` 외(needs_review·missing)는 §4 게이트가 **동일하게 name_only 강등**한다(단일 경로). 표와 의사코드 일치.
- `hidden`(완전 미노출)은 source 객체 자체가 없는 경우를 위한 **미구현 설계 옵션**으로만 보존 — 현 게이트는 반환하지 않으며, 데이터엔 30/30 source 가 존재해 해당 케이스가 없다.
- "출처 확인 중" 같은 **중간 라벨 노출 없음.**
- 강등 시에도 relation 데이터는 보존(라우팅만 변경). 추후 confirmed 승격 시 자동 복귀.

---

## 6. 이번 단계 경계 (금지/허용)

- ✅ 허용: 본 설계 문서 + gate 함수 **스펙**(위 코드 블록) + source_status 정책.
- ❌ 금지: relation 30 데이터 수정 / `source_status` 실부여 / gate 함수 `src/` 배선 / relation_card 558 렌더 변경 / 실제 강등·삭제·숨김 / DATA_URL·export 변경.
- **relation 데이터는 프로젝트 핵심 자산 — 한 건도 사라지면 안 된다.** 본 설계는 데이터 무손실(라우팅 기반).

> 공개 게이트(STOP #2·#3): relation 30 source confirmed 승격 + 미확정 강등/숨김 설계 완료 전 relation_card 일반 공개 금지. 승격 절차는 규제 자문(STOP #1) 이후.
