# MediStack — 공개 전 법적 안전장치 체크리스트 (Public Release Legal Safety Gate)

> 작성일: 2026-06-13. **일반 공개(general/public release) 전 반드시 통과해야 하는 게이트.** v1.1-beta(`8289b8c`)는 **내부 안정판 스냅샷**일 뿐, 본 게이트 미완료 상태에서 일반 공개는 금지.
> 동반 문서: 면책/이용약관 초안 `MediStack_disclaimer_and_terms_draft.md` · 출처 설계 `MediStack_source_attribution_design.md` · 개인정보/피드백 `MediStack_privacy_and_feedback_policy_draft.md` · 렌더 고지 검증 `scripts/smoke_disclaimer_render.py`.

---

## 0. 이 문서의 한계 (중요)

- **본 문서·스모크·초안 작업은 "공개 가능성"을 점검하는 준비일 뿐, 공개 허가나 합법성 보장을 의미하지 않는다.**
- 약사법·의료기기법·의약품 정보제공 해당성에 대한 **전문가(변호사/약무) 자문 또는 식약처 문의 완료 전에는 일반 공개 금지.**
- `published` / `clinical_reviewed` 는 계속 **false** 유지(본 트랙은 clinical reviewer 트랙이 아니다).
- 현재 라이브(`yoonspower.github.io/medistack`)는 베타 참고정보 상태로 존재하나, **본 게이트는 "적극적 일반 공개/홍보/배포"의 전제조건**이다.

---

## 1. 공개 전 STOP 조건 (전부 충족 전 일반 공개 금지)

| # | STOP 조건 | 현재 상태 |
|---|---|---|
| 1 | **규제 자문 완료** — 약사법/의료기기법/의약품 정보제공 해당성에 대한 전문가 자문 또는 식약처 문의 | ❌ 미완 (외부 의존) |
| 2 | relation 30건 **source confirmed** 전 relation_card 공개 금지 | ⏳ source 데이터는 30/30 존재, `source_status=confirmed` 승격 절차 미정의(설계만) |
| 3 | `source_status` missing/needs_review relation은 public release에서 **숨김 또는 name_only 강등 설계** 전 공개 금지 | ✅ 설계 완료(`MediStack_source_attribution_design.md`), 구현 미적용 |
| 4 | **disclaimer smoke PASS** 전 공개 금지 | ✅ `smoke_disclaimer_render.py` PASS(S1~S9) |
| 5 | 이용약관/면책/개인정보 처리방침 **초안 완료** 전 공개 금지 | ✅ 초안 작성(법률 검토 전·DRAFT) |
| 6 | 피드백 폼 **개인정보/건강정보 수집 차단 설계** 전 피드백 폼 공개 금지 | ✅ 정책 설계 완료, 폼 미구현 |
| 7 | `published` / `clinical_reviewed` true 전환 금지 | ✅ 둘 다 false 유지 |
| 8 | 본 문서 작업이 공개 허가/합법 보장이 **아님**을 명시 | ✅ §0 명시 |

→ **현 시점 일반 공개 판정: 불가(NO-GO).** 차단 사유 = ①규제 자문 미완(외부 사람 의존) + ②relation source confirmed 승격 절차 미정의. 나머지(③~⑧) 문서/설계/스모크 레일은 본 세션에서 정비 완료.

---

## 2. 게이트 항목 체크리스트

### 2-A. 법적 문서 (초안 — 법률 검토 전)
- [x] 이용약관/면책 초안 (`MediStack_disclaimer_and_terms_draft.md`) — 의료행위 아님·복용판단 금지·119·미성년자·개인정보 입력금지·준거법 KR 포함
- [x] 개인정보/피드백 정책 초안 (`MediStack_privacy_and_feedback_policy_draft.md`) — GitHub Pages 호스팅 로그 고지·피드백 약명누락만·건강정보 차단
- [ ] **변호사/약무 전문가 법률 검토** (외부) — 초안→확정
- [ ] 관할/준거법 조항 법률 확정
- [ ] **GitHub 국외 이전(개인정보) 해당성** 법률 검토 — 미국 호스팅 IP/UA 이전 고지·근거(개인정보보호법 제28조의8 계열)
- [ ] 개인정보 처리방침 **처리자 신원·연락처·보호책임자** 기재 확정

### 2-B. 고지 렌더 (코드 게이트)
- [x] disclaimer smoke (`smoke_disclaimer_render.py`) — relation_card/name_only/empty/no-result/error 상태별 필수 고지 실제 렌더 검증(소스 grep 아님)
- [x] relation_card 상세: 공통 면책(`disclaimers.common`) load-bearing — 누락 시 상세 렌더 차단(mountDetail fail-safe) 확인
- [x] name_only: '참고 정보 없음' + 상담 안내 출력 · 의학/상호작용/제품/링크/출처 chrome 0
- [ ] (구현 시) 온보딩/약관 동의 화면에 면책 노출 — 본 세션 범위 밖

### 2-C. 출처 (relation 30 단위)
- [x] source attribution 설계 (`MediStack_source_attribution_design.md`) — relation 30 단위 부여, relation_card 558 상속
- [x] 출처 미확정 relation 공개 차단 정책 (숨김/name_only 강등, "출처 확인 중" 라벨 노출 금지)
- [ ] `source_status` 필드 실데이터 부여 + confirmed 승격 절차 운영 — **별도 단계(데이터 변경, PM 승인 필요)**
- [ ] 공개 모드 gate 함수 실배선 — **별도 단계(렌더 변경, PM 승인 필요)**

### 2-D. 규제
- [ ] **약사법/의료기기법/의약품 정보제공 해당성 규제 자문** (전문가 또는 식약처) — 최우선 외부 잠금
- [ ] 자문 결과 반영(필요 시 문구/기능 조정)

### 2-E. 봉인 유지(불변)
- [x] `published=false` / `clinical_reviewed=false`
- [x] 제품/구매/제휴 UI 없음
- [x] relation 30 / relation_card 558 / full index 17,580 / alias 621 데이터·렌더 무변경

---

## 3. 데이터/렌더 무변경 보증 (본 세션)

본 세션은 **문서·스모크·설계만** 추가한다. 다음은 한 줄도 변경하지 않는다:
- `data/medistack_v0.2_beta_export.json`(relation 30) · relation_card 558 렌더 · `data/full_drug_name_index_sample_v1_0.json`(17,580) · `data/medistack_v0.3_aliases.json`(621) · `src/` 렌더 경로 · DATA_URL · export md5 `401b097a`.
- 출처 미확정 relation의 **실제 삭제/강등/숨김 구현 금지** — gate 설계와 문서만.

---

## 4. 공개 진행 시 권장 순서 (게이트 통과 후)

1. **규제 자문**(최우선·외부) → 해당성 판정 + 필요 조정.
2. relation 30 `source_status` 부여 + confirmed 승격(데이터 단계, PM 승인).
3. 공개 모드 gate 함수 실배선 + 회귀 smoke(렌더 단계, PM 승인).
4. 법률 검토로 약관/면책/개인정보 처리방침 확정 → 약관 동의/온보딩 화면.
5. (선택) 피드백 폼 — 약명 누락 제보 한정·건강정보 차단 검증 후.
6. 최종 NO-GO/GO 재판정 → 공개.

> 안전 원칙(불변): 원문에 없으면 노출 금지 / 진단·처방·복약지시 금지 / 복용 시작·중단·변경 판단 금지 / 칼륨 제품링크 금지 / published·clinical_reviewed 봉인 / relation·alias·full index 무확장 / 출처 미확정 relation 공개 금지 / 규제 자문 완료 전 일반 공개 금지 / 본 문서는 합법 보장 아님.
