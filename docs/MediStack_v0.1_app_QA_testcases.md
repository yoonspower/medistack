# MediStack v0.1 — 앱 연동 QA 테스트 케이스

작성 기준일: 2026-06-07 / 대상: `medistack_v0.1_beta_export.json` 기반 베타 앱
검증 도구 연동: `validate_medistack_v0_1_export.py` / `.js` (자동 컨트랙트 검증)

## 전제 / 프레임
- v0.1은 **published가 아니라 verified_reference 기반 베타 참고정보**다. 진단·처방·복약지시가 아니다.
- clinical reviewer 부재 → **published / clinical_reviewed 사용 금지.** 앱에서 임상 승인처럼 보이는 요소 노출 금지.
- 앱 QA는 **JSON(`medistack_v0.1_beta_export.json`) 기준**으로 작성한다.
- 우선순위: **P0 = 배포 차단(blocker)**, **P1 = 수정 권장(다음 빌드)**.
- A 블록(데이터 shape, A1–A6)은 자동 검증 스크립트로 1회 확인 가능 → B 수동 QA 전에 통과시킨다.

---

## 테스트 케이스 표

| QA ID | 구분 | 테스트 목적 | 입력/전제조건 | 테스트 절차 | 기대 결과 | 판정 기준 | 우선순위 |
|---|---|---|---|---|---|---|---|
| A1 | A.데이터shape | top-level 컨트랙트 키 일치(드리프트 감지) | JSON + validator | validator 실행(#1) 또는 JSON 최상위 키 확인 | 키가 정확히 meta/disclaimers/relations/excluded_v0_1 | 4개 정확 일치 시 PASS. 누락 또는 예상외 키 FAIL | P1 |
| A2 | A.데이터shape | 베타 노출 대상 19건 보장 | JSON + validator | validator(#2) 또는 relations 배열 길이 확인 | relations 길이 = 19 | 19이면 PASS. 그 외 FAIL | P0 |
| A3 | A.데이터shape | 제외 1행(15) 보관 확인 | JSON + validator | validator(#3) 또는 excluded_v0_1 확인 | 1건, id15 에스오메프라졸×비타민B12 | 1건+성분/영양소 일치 PASS. 그 외 FAIL | P1 |
| A4 | A.데이터shape | 미검증 15행 노출 데이터 누출 차단 | JSON + validator | validator(#4) 또는 relations의 id 목록에 15 검색 | relations에 id 15 없음 | 없음 PASS. 존재 시 FAIL | P0 |
| A5 | A.데이터shape | relation에 lifecycle 필드 부재(필터 오용/드리프트 방지) | JSON + validator | validator(#7) 또는 relation 키 검사 | status/published/clinical_reviewed 키 모두 없음 | 전무 PASS. 하나라도 존재 FAIL | P1 |
| A6 | A.데이터shape | published/clinical 봉인값 확인 | JSON + validator | validator(#5,#6) 또는 meta 확인 | meta.published=false, meta.clinical_reviewed=false | 둘 다 false PASS. 그 외 FAIL | P0 |
| B7 | B.프론트 | 목록에 relations 19건만 렌더 | 베타 앱에 JSON 로드, 목록 화면 | 목록 진입 후 카드 수 카운트 | 정확히 19개 카드, 전부 relations 출처 | 19개+외부항목 없음 PASS. 개수 불일치/외부항목 FAIL | P0 |
| B8 | B.프론트 | 15행(에스오메프라졸×B12) 어디에도 미노출 | 목록/검색/딥링크 | 목록·검색·상세에서 에스오메프라졸+B12 조합 탐색 | 해당 카드 미표시(검색결과·딥링크 포함) | 미표시 PASS. 표시되면 FAIL(blocker) | P0 |
| B9 | B.프론트 | 모든 상세에 공통 면책문구 표시 | 대표 상세(각 action·칼륨 포함) | 상세 진입 후 disclaimers.common 텍스트 확인 | 모든 상세 화면에 common 문구 상시 표시 | 전 상세 표시 PASS. 한 곳이라도 누락 FAIL | P0 |
| B10 | B.프론트 | 칼륨 제품링크/예시 차단(고칼륨혈증 위험) | 칼륨 17·19 상세 | 17·19 상세 진입 후 제품링크·제품예시·구매버튼·제휴 UI 존재 확인 | 제품 관련 UI 일절 없음 | 없음 PASS. 하나라도 노출 FAIL(blocker) | P0 |
| B11 | B.프론트 | 칼륨 추가 고지 표시 | 칼륨 17·19 상세 | 17·19 상세에서 disclaimers.potassium_notice 표시 확인 | potassium_notice 표시(common과 별도) | 표시 PASS. 미표시 FAIL | P0 |
| B12 | B.프론트 | 비칼륨 행에 칼륨 고지 오노출 방지 | 비칼륨 행(예 1,12,18) 상세 | 비칼륨 상세 진입 후 potassium_notice 미표시 확인 | potassium_notice 없음 | 없음 PASS. 표시되면 FAIL | P1 |
| B13 | B.프론트 | published/clinical 승인 인상 차단(verified_reference 유지) | 전 화면 | published·임상검수·승인·체크뱃지 등 표시 여부 점검 | 임상 승인 인상 요소 없음. 표기는 '참고 정보' 수준만 | 그런 요소 없음 PASS. 노출 시 FAIL | P0 |
| B14 | B.프론트 | empty/error 문구가 의학적 판단/지시처럼 보이지 않기 | 관계 0건 약(empty), 로드 실패(error) | 두 상태 진입 후 문구 검토 | 정보부재·상담권유 수준 문구만. empty는 '관계 없음 보장 아님' 포함 | 의학 단정/지시 표현 0건 PASS. 존재 시 FAIL | P0 |
| B15 | B.프론트 | JSON 로드 실패 시 안전 처리 | JSON 누락 또는 깨진 JSON 주입 | 파일 제거/손상 후 앱 로드 | 안전한 오류 메시지(재시도 안내). 깨진/이전 데이터로 의학정보 렌더 금지 | 안전 오류 표시 & 의학콘텐츠 미렌더 PASS. 크래시/stale 렌더 FAIL | P1 |

---

## PASS 기준 요약

- **배포 게이트:** 모든 **P0 PASS가 필수**. P0 1건이라도 FAIL이면 베타 배포 불가.
- **P1:** 전부 PASS 권장. FAIL 시 PM 승인 하에만 보류 가능하며 다음 빌드에서 수정.
- **선행 조건:** A1–A6는 `validate_medistack_v0_1_export.py`로 자동 확인. validator가 FAIL이면 데이터부터 수정하고 B 수동 QA는 진행하지 않는다(앱이 아니라 데이터 문제).
- **P0 (10건):** A2, A4, A6, B7, B8, B9, B10, B11, B13, B14
- **P1 (5건):** A1, A3, A5, B12, B15

### 안전 핵심 4선 (절대 통과 못 하면 배포 금지)
- B8 — 미검증 15행 미노출
- B9 — 전 상세 공통 면책문구
- B10 — 칼륨 제품링크/예시 차단
- B14 — empty/error에 의학적 단정/지시 문구 금지

> 불변 원칙: 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지.
