# MediStack — Supabase 마이그레이션 전략 v1.2 (설계 문서)

> 작성일: 2026-06-14. **설계 문서 전용 — 실제 마이그레이션/스키마 생성/import/배선 0.** Supabase 프로젝트 생성·테이블 DDL·RLS 정책 적용·import 스크립트 실행은 **본 문서 범위 밖**이며, 별도 PM 승인 + 개인정보 처리방침/동의/보안 선행 라운드에서만 수행한다.
>
> 선행(자기완결 인계): `CLAUDE.md`(리포 가드레일) · `MediStack_v1.2_plan.md` · `MediStack_saved_stack_mvp_design_v1_2.md`(저장 MVP·데이터 모델 10필드·`local_only=true`) · `MediStack_free_plus_plan_v1_2.md`(Free/Plus 경계·"건강정보 판매 없음") · `MediStack_privacy_and_feedback_policy_draft.md` · `MediStack_disclaimer_and_terms_draft.md` · 법적 게이트 `MediStack_public_release_legal_safety_checklist.md`.
>
> 전제(불변): MediStack 은 **식약처 허가사항 기반 약-영양소 참고정보 베타**다. 진단·처방·복약지시·영양제 추천·구매 동선이 아니다. **published / clinical_reviewed = false 봉인 유지.** 백엔드를 도입한다 해도 이 정체성·면책·출처 톤은 절대 바뀌지 않는다.

---

## 0. 한 줄 결론

**지금은 옮기지 않는다.** 현재 **단일 진실원(source of truth) = GitHub 리포의 정적 JSON**(`data/*.json`)이고, 앱은 정적 HTML/CSS/JS + GitHub Pages로 백엔드·계정이 없다. Supabase 도입은 **v1.3~v1.4 이후**, 그것도 **공용 참고정보(public)가 아니라 "사용자 본인 기능"(saved stack 동기화 등)이 실제로 필요해질 때** 한정으로 검토한다. 사용자 건강 관련 데이터(복용약·메모)는 **local-only 우선**이며, 서버 저장은 마지막 단계다.

> 한 줄 테스트(전략 문서 §1 승계): "이 변경이 **공용 참고정보 접근**을 서버 의존으로 바꾸거나, **사용자 건강정보를 서버에 모으는가**?" → 둘 중 하나라도 예이면 신중·후순위·별도 승인. Supabase 는 "도구 편의(기기 간 동기화)"를 위해서만 검토하지, 정보 신뢰·운영 단순성을 깨면서까지 도입하지 않는다.

---

## 1. 지금 옮기지 않는 이유 (왜 GitHub JSON 이 계속 source of truth 인가)

1. **현재 구조가 이미 잘 맞는다.** 공용 참고정보(relations / relation_card / name_only index / alias / source)는 **읽기 전용·전역 공통·저빈도 갱신** 데이터다. 정적 JSON + CDN(Pages) 으로 충분하며, DB 가 주는 쿼리·조인·동시쓰기 이점이 거의 필요 없다.
2. **append-only 버저닝·CI 게이트가 안전장치다.** 데이터 변경이 PR → validator(`scripts/validate_*`) → `deploy.yml` 게이트를 통과해야만 라이브가 된다(`CLAUDE.md` §2·§5). 이 "검증 없으면 배포 없음" 보증은 정적 JSON + Git 히스토리에서 자연스럽게 얻어진다. DB 로 옮기면 이 게이트를 **다시 직접 구축**해야 한다(마이그레이션·롤백·검증 파이프라인).
3. **운영 부담 0 유지.** 개인 개발자 1인 운영 전제(수익화 전략 §3.1)에서 DB·인증·RLS·백업은 **상시 유지보수·보안 책임**을 만든다. 베타 단계에서 이를 지는 것은 가치 대비 부담이 크다.
4. **개인정보 표면이 작다.** 현재 서버가 없으니 "건강정보 수집·국외 이전·유출" 표면이 원천적으로 작다(저장은 `local_only=true`, saved_stack MVP §5). Supabase 도입은 이 표면을 **키운다** — 그래서 사용자 기능이 정말 필요해질 때까지 미룬다.

> 결론: **public 참고정보는 v1.3~v1.4 시점에도 굳이 DB 로 옮길 이유가 약하다.** Supabase 의 진짜 후보 용도는 (a) saved stack **기기 간 동기화**(현재 localStorage 한계 §4.2) (b) 피드백/문의 수집 같은 **사용자-생성 데이터**다. public 전환은 그보다 더 뒤다(§4 6단계).

---

## 2. 스키마 설계 (도입 시점에 만들 테이블 — 지금은 설계만)

**두 영역을 물리적·정책적으로 분리한다.** public(공용 참고정보, 모두 읽기) vs private/user(본인만 접근). 이 분리가 RLS·프라이버시의 1차 방어선이다.

### 2.1 public tables (공용 참고정보 — read-only mirror)

> 이 테이블들은 **GitHub JSON 을 미러링**한 것이다(§3 import). **source of truth 는 여전히 JSON.** Supabase 는 읽기 사본일 뿐이며, 쓰기는 import 파이프라인을 통해서만 일어난다(앱·사용자가 직접 쓰지 않음). 모두 **익명 read 허용**(공개 참고정보이므로), 단 RLS 로 **쓰기는 전면 차단**(service_role/import 만).

| 테이블 | 의미 | JSON 출처(현재) | 비고 |
|---|---|---|---|
| `drugs` | 약(품목) 마스터 — item_seq·품목명·표시모드 | `full_drug_name_index_sample_v1_0.json`(relation_card + name_only) | `display_mode`(relation_card \| name_only) 보존. **name_only 행엔 의학정보 미부착 규칙 그대로**(CLAUDE.md). |
| `ingredients` | 성분 마스터 — 성분명·식별자 | relations/`verified_item_seqs` 파생 | 약-성분 매칭 보조 |
| `relations` | 약-영양소 참고 관계(현 라이브 55건, ids 1–14·16–56) | `medistack_v0.2_beta_export.json` → `relations[]` | `published`/`clinical_reviewed` **컬럼은 두되 값은 false 봉인**. 칼륨행 `product_link_allowed=false`·`potassium_safety_card=true` 플래그 보존. |
| `relation_sources` | 관계별 출처(원문 링크·확인일·source_status) | source UI 설계(`..._relation_source_ui_design_v1_2.md`) / source queue 산출 | `source_status` 도메인(needs_source/candidate_only/source_check_needed/source_confirmed…) 보존. **자동 승격 금지 규칙 유지**(import 가 status 를 임의 격상하지 않음). |
| `drug_relation_cards` | 약↔관계 카드 매핑(relation_card 표시 단위, 현 라이브 1,077) | full index `relation_card` 부분 | 한 약에 연결된 카드들. 모아보기(Plus)·검색 결과 렌더 입력. |
| `aliases` | 검색용 별칭(현 라이브 alias_count 717) | `medistack_v0.3_aliases.json` | 런타임 검색 보조. 의학정보 아님. |
| `combo_notices` | 복합제 배너 고지(buffer_combo 등) | combo banner 통합 문서들(A/B/D/C) | 면책·배너 톤 보존. "성분" 미세중복 등은 기존 PM 트랙. |

**public 불변 규칙(컬럼·정책에 강제):**
- `published` / `clinical_reviewed` **컬럼 존재 + 값 false 고정**(reviewer 확보 전 true 전환 금지 — CLAUDE.md §1·§6). import 가 이 값을 바꾸지 않는다.
- 칼륨 안전 플래그·복합제 배너·면책(`disclaimers.common`) **누락 없이 미러**. 미러가 원문보다 약하거나 강하면 import 실패(검증 게이트 §3).
- `excluded_v0_1` 등 **앱 비표시 데이터는 public 미러에 넣지 않거나, 넣더라도 `is_rendered=false`** 로 격리(앱이 절대 읽지 않게).
- 제품/구매/제휴 필드 **컬럼 자체를 만들지 않는다**(v0.2 제품 필드 전면 금지 승계).

### 2.2 private / user tables (본인만 접근 — RLS 강제)

> 이 영역이 **Supabase 도입의 진짜 동기**다(기기 간 동기화·피드백 수집). **모두 `auth.uid()` 기준 RLS** — 본인 행만 select/insert/update/delete. §5 의 건강정보 하드라인이 컬럼 설계를 지배한다.

| 테이블 | 의미 | 컬럼(요지) | 프라이버시 등급 |
|---|---|---|---|
| `user_profiles` | 사용자/가족 프로필(호칭 라벨) | `user_id`(auth), `profile_id`, `profile_label`(호칭만), `created_at` | 라벨은 **호칭**("나"/"어머니"), 실명·주민번호·연락처·질환 **금지**(saved_stack §6). |
| `saved_drugs` | 저장한 약 목록(= saved_stack 동기화 대상) | `user_id`, `profile_id`, `saved_item_seq`, `saved_item_name`, `ingredient_name`, `display_mode`, `relation_summary_available`, `created_at`, `updated_at` | **건강 관련.** 컬럼은 saved_stack MVP §3 의 10필드에서 `local_only` 제외분과 1:1. 복용량/진단명/질환명 **컬럼 없음**(입력 경로 자체를 안 만듦). |
| `saved_notes` | 사용자 자유 메모 | `user_id`, `saved_drug_id`(FK), `user_note`(자유 텍스트), `updated_at` | **건강 관련(최고 민감).** 자유 텍스트라 사용자가 증상·복용량을 적을 위험 → 입력 화면 안내 + 서버 저장은 명시 동의 후에만(§5). |
| `search_history` | 검색 이력(편의 기능) | `user_id`, `query`, `searched_at` | 행동 데이터. 보관 한도·자동 만료(예: N일) 권장. 광고·타겟팅 사용 금지(전략 §4). |
| `plus_entitlements` | Plus 결제 권한 상태 | `user_id`, `product_id`, `purchased_at`, `platform`(appstore/web), `status` | 결제 메타. 영수증 원문은 저장 최소화. |

**private/user 불변 규칙:**
- **건강정보(복용량·진단명·질환명·증상) 컬럼을 만들지 않는다.** `saved_drugs` 는 약명·품목식별자·표시모드까지만(saved_stack §5). `saved_notes.user_note` 만 자유 텍스트이며, 거기엔 **민감정보 입력 금지 안내**가 붙는다.
- **서버 저장은 옵트인.** 기본은 local-only(§5). 서버 동기화를 켤 때만 이 테이블에 행이 생기고, 그 전제로 **개인정보 처리방침·동의·보안**이 선행되어야 한다(`local_only` true→false 전환은 saved_stack §5 가드 재통과).
- **삭제권 보장.** 본인 행 즉시 삭제(account 삭제 시 cascade). "언제든 완전히 지울 수 있다"는 saved_stack §7 강점을 서버에서도 유지.

---

## 3. import 스크립트 (JSON → Supabase, 미러 채우기 — 설계만)

> 목적: public 테이블을 **GitHub JSON 으로부터 단방향 채운다.** source of truth 는 JSON, Supabase 는 사본. 사람이 손으로 DB 를 안 고친다(드리프트 방지).

설계 요지(구현 아님):

1. **입력 = 라이브 JSON 파일들**(현행): `medistack_v0.2_beta_export.json`(relations) + `full_drug_name_index_sample_v1_0.json`(drugs·relation_card·name_only) + `medistack_v0.3_aliases.json`(aliases). **이 파일들은 import 의 입력이지 수정 대상이 아니다**(읽기만).
2. **검증 선행 = 기존 validator 재사용.** import 전에 `scripts/validate_medistack_v0_2_export.*` 가 PASS 해야 한다. **validator PASS 없으면 import 금지**(CLAUDE.md §5 의 "검증 없으면 배포 없음"을 DB import 에 그대로 확장).
3. **단방향·멱등.** import 는 JSON → DB 방향만. 멱등(같은 입력 재실행 시 동일 결과) — upsert by 자연키(item_seq, relation id). **DB → JSON 역류 없음.**
4. **불변값 보존 검사.** import 후 어서션: `published=false`·`clinical_reviewed=false` 전부, 칼륨 플래그 보존, 면책 누락 0, relation 개수·alias 개수·verified seqs 가 JSON 메타와 일치. **하나라도 어긋나면 import 실패 + 롤백**(원문보다 약/강 금지 — 안전 원칙).
5. **버전 태깅.** import 한 JSON 버전·커밋 해시를 DB 메타 테이블에 기록(어느 라이브 스냅샷의 미러인지 추적). 라이브 HEAD 와 미러가 다르면 stale 경고.
6. **재import 트리거.** 라이브 JSON 이 PR 머지로 바뀌면(상시는 아님) import 재실행. CI 와 분리된 수동/배치 잡으로 시작(자동화는 미러를 실제로 쓰기 시작한 뒤).

> import 는 **public 미러 전용**이다. private/user 테이블은 import 대상이 아니다(사용자가 앱에서 직접 생성하는 데이터).

---

## 4. 마이그레이션 6단계 (단계별 게이트 — 되돌릴 수 있게)

각 단계는 **이전 단계를 깨지 않고 추가**된다. 어느 단계에서 멈춰도 앱이 동작한다(점진·가역).

| 단계 | 내용 | 끝나는 시점에 보장되는 것 | 게이트(다음으로 넘어가는 조건) |
|---|---|---|---|
| **1. JSON 유지(현재)** | 현 상태 그대로. source of truth = GitHub JSON, 앱 = 정적 Pages, 저장 = localStorage(`local_only=true`). | 백엔드 0·계정 0·건강정보 서버 저장 0. | (해당 없음 — 기본 상태) |
| **2. schema 설계** | §2 의 public/private 스키마를 **문서로만** 확정(DDL 초안·RLS 정책 초안). 실제 프로젝트 생성 안 함. | 무엇을 어떻게 옮길지 합의. 코드·DB 변경 0. | PM 승인 + 개인정보 처리방침/동의/보안 설계 착수. |
| **3. import script** | §3 스크립트 작성 + **별도 Supabase 프로젝트**에 public 미러 채우기(검증·멱등·불변보존). **앱은 아직 JSON 만 본다.** | DB 에 public 사본 존재. 라이브 앱 영향 0(앱이 DB 를 안 읽음). | import 불변검사 전부 PASS. |
| **4. read-only mirror** | 앱이 **선택적으로** public 데이터를 Supabase 에서 읽을 수 있게(피처 플래그). 기본은 여전히 JSON. **public 의 source of truth 는 그대로 JSON.** | DB 읽기 경로 검증. 문제 시 JSON 으로 즉시 폴백. | 미러 일관성·성능·폴백 검증. |
| **5. user feature 만 Supabase** | **여기서 처음 사용자 데이터가 서버에 닿는다.** private/user 테이블(saved_drugs/saved_notes 등) + auth + RLS 도입. **명시 옵트인 한정.** 옵트인 안 한 사용자는 계속 local-only. | 기기 간 동기화·피드백 수집 가능(원하는 사용자만). 미동의자는 §1 상태 유지. | 개인정보 처리방침·동의 UI·RLS 감사·보안 점검 **전부 통과**(§5·법적 게이트). |
| **6. public 전환(나중)** | (선택·가장 뒤) public 참고정보의 source of truth 를 JSON → DB 로 옮기는 것까지 검토. **현재 계획상 불필요에 가깝고, 가장 마지막.** | (검토 대상일 뿐 — 강행 안 함) | append-only 게이트·validator·롤백을 DB 위에서 **동등 이상**으로 재현 가능할 때만. 아니면 영구 5단계 유지. |

> 핵심: **사용자 건강 관련 데이터(saved_drugs/saved_notes)는 5단계에서야 서버에 닿고, 그것도 옵트인뿐.** public 참고정보 DB 전환(6단계)은 "할 수도 있다" 수준이며 우선순위 최하. 1~4단계까지는 **어떤 건강정보도 서버에 가지 않는다.**

---

## 5. 프라이버시 / RLS / 건강정보 리스크 (하드 라인)

본 절은 **불변 가드**다. Supabase 를 도입하는 순간 이 모두가 코드·정책·DB 정책으로 강제되어야 한다.

### 5.1 RLS (Row Level Security)
- **모든 private/user 테이블에 RLS 활성 필수.** 기본 deny, `auth.uid() = user_id` 인 행만 select/insert/update/delete 허용. RLS 미적용 테이블에 사용자 데이터를 두지 않는다.
- **public 테이블은 read 만 익명 허용·write 전면 차단**(import service_role 만). 사용자/앱이 public 참고정보를 쓰지 못하게 한다(데이터 무결성 = JSON 게이트가 단일 출처).
- RLS 정책은 **도입 전 감사**(정책 누락·과허용 점검). "RLS 켰다고 가정"하지 말고 실제 정책 테스트.

### 5.2 건강정보 리스크 (가장 중요)
- **저장하는 사용자 데이터는 "약 목록 메모" 수준**이지 의료기록이 아니다(saved_stack §7·§9). 복용량·진단명·질환명·증상 **컬럼을 만들지 않는다** — 입력 경로를 안 만드는 것이 1차 방어선.
- `saved_notes.user_note` 자유 텍스트는 사용자가 민감정보를 적을 위험이 있으므로: (a) 입력 화면에 **민감정보 입력 금지 안내** (b) 서버 저장은 **명시 동의 후에만** (c) 플레이스홀더가 복용량/진단을 유도하지 않게(중립 문구).
- **건강정보 판매·공유·광고 타겟팅 영구 금지**(전략 §4). 서버에 모인 데이터를 제3자 제공·광고에 쓰지 않는다. 분석조차 최소화·익명.
- **국외 이전 주의.** Supabase 리전·데이터 보관 위치가 개인정보 처리방침 고지 대상. 한국 사용자 건강 관련 데이터의 국외 저장은 동의·고지 사안(법적 게이트 확인).

### 5.3 local-only 우선 전략
- **기본은 항상 local-only.** 서버 동기화는 **사용자가 명시적으로 켜는 옵트인 기능**이지 기본값이 아니다. 옵트인 안 하면 앱은 §1(localStorage·`local_only=true`) 그대로 동작한다.
- `local_only` true→false(서버 업로드) 전환은 saved_stack §5 가드를 **다시 통과**해야 한다(개인정보 처리방침·동의·보안 선행).
- **내보내기/가져오기(로컬 파일)가 1차 동기화 수단**으로 계속 유효(saved_stack §7.2). 서버 동기화는 그 위의 편의 옵션이지, 로컬 백업을 대체하지 않는다.
- **삭제권.** 서버 저장 시에도 본인 데이터 즉시·완전 삭제(account 삭제 cascade) 보장.

### 5.4 봉인 불변
- **published / clinical_reviewed = false 유지.** DB 컬럼에도 false 고정, import 가 바꾸지 않는다. "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현 금지(DB·앱·문서 공통).
- **면책·출처 톤 불변.** DB 로 옮겨도 `disclaimers.common`·출처·칼륨 고지·복합제 배너는 약화·은폐 없이 유지.

---

## 6. 정합성 / 의존 (다른 설계 문서와의 관계)

- **saved_stack MVP(`..._saved_stack_mvp_design_v1_2.md`)**: 본 문서 §2.2 의 `saved_drugs`/`saved_notes`/`user_profiles` 컬럼은 saved_stack §3 의 10필드 스키마(`local_only` 제외분)와 1:1 대응. 저장 정체성("약 목록 메모"·건강정보 입력 경로 0)·삭제권·내보내기/가져오기는 그 문서가 정본이며 본 문서는 그것을 **서버로 옮길 때의 조건**만 추가한다(§4 5단계·§5).
- **free_plus(`..._free_plus_plan_v1_2.md`)**: `plus_entitlements` 는 그 문서의 "저가 평생 구매 1상품"·Plus 경계와 정합. 기기 간 동기화는 **Plus 의 편의 후보**이지 정보 접근을 페이월에 가두지 않는다(free_plus §1). "건강정보 판매 없음"(§4)은 본 문서 §5.2 와 동일 하드라인.
- **CLAUDE.md(리포 가드)**: append-only·validator 게이트·published/clinical false·칼륨/복합제/면책 보존·제품 필드 금지를 DB 미러·import 에 그대로 확장(§2.1·§3).
- **수치 정합:** 본 문서는 라이브 현황(relations 55·full index 17,580〔relation_card 1,077·name_only 16,503〕·alias 717·verified seqs 1,064/22)을 **미러 검증 기준값**으로 참조한다. 실제 import 시점의 라이브 메타와 대조(§3 4번).

---

## 7. 이 전략이 **아닌 것** (What this is NOT)

- ❌ **즉시 마이그레이션이 아니다.** v1.2 에서 DB 를 만들지 않는다. 본 문서는 **설계·조건·순서**일 뿐. 실행은 v1.3~v1.4 이후 + PM 승인 + 법적/보안 선행.
- ❌ **public 참고정보의 DB 전환을 전제하지 않는다.** source of truth 는 GitHub JSON 으로 유지가 기본. DB public 전환(§4 6단계)은 우선순위 최하·선택.
- ❌ **건강정보를 서버에 모으는 설계가 아니다.** local-only 가 기본·옵트인만 서버(§5.3). 복용량/진단명/질환명 컬럼 없음.
- ❌ **건강정보 판매·광고·제휴 동선이 아니다.** 서버에 데이터가 있어도 제3자 제공·타겟팅 0(전략 §4 영구).
- ❌ **계정 강제가 아니다.** 로그인 없이도 앱 전부(검색·참고정보·로컬 저장) 그대로 쓴다. auth 는 동기화 옵트인 사용자에게만.
- ❌ **"승인/검수 완료/법적 문제없음"을 표방하지 않는다.** published/clinical_reviewed = false 봉인 유지.

---

## 8. 범위 / 금지 (본 문서)

- ✅ **설계 문서 뿐** — Supabase 프로젝트·DDL·RLS·import 실행·앱 배선·DATA_URL·결제 변경 0. `docs/` 신규 1파일만.
- ✅ source of truth = **GitHub JSON 유지**. Supabase 는 v1.3~v1.4 이후·사용자 기능 한정 검토.
- ✅ public/private 테이블 **분리** + 모든 user 테이블 **RLS** + 건강정보 **컬럼 없음**(약 목록 메모 수준).
- ✅ **local-only 우선** — 서버 저장은 옵트인·개인정보 처리방침/동의/보안 선행. `local_only` true→false 는 saved_stack §5 가드 재통과.
- ✅ 건강정보 판매·공유·광고·제휴·구매 동선 **영구 0**(서버 도입과 무관).
- ✅ import 는 단방향·멱등·validator PASS 선행·불변값(published/clinical false·칼륨·면책) 보존검사·실패 시 롤백.
- ✅ published / clinical_reviewed **false 유지**. "식약처 승인 / 법적 문제없음 / 약사 검수 완료" 표현 0.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / source of truth = GitHub JSON(Supabase 는 사본·후순위) / 사용자 건강 관련 데이터는 local-only 우선·옵트인만 서버·복용량/진단명/질환명 컬럼 없음 / 모든 user 테이블 RLS·public 은 read-only / 건강정보 판매·공유·광고·제휴 0 / "약 목록 메모"이지 의료기록 아님 / 일반 공개·서버 도입은 개인정보 처리방침·동의·보안·규제 자문 전 NO-GO.
