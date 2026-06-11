# MediStack v0.5 — bulk alias pipeline Phase 3 보고서 (getItemDetail 상세확정, dry-run)

작성/실행일: **2026-06-11** / 단계: **Phase 3 상세확정 완료, alias JSON 미반영 / approved 0** / 상위: `MediStack_v0.5_bulk_alias_pipeline_plan.md`, `..._phase2_report.md`

> PM 판정(Phase 3): pending 32 대상 getItemDetail 상세확인 · alias JSON 미수정 · approved status 미생성 · approved-ready는 **별도 파일**로만 · 실제 반영은 다음 PM 게이트 · 복합제/brand_core/에스오메프라졸 approved-ready 금지 · 단일성분 원문 일치만 approved-ready · confidence high 상향 가능.
> 산출물: 상세확정기(`scripts/confirm_nedrug_item_details.py`) + 검증기 보강(18→31체크) + queue 갱신(detail 필드) + **approved-ready 별도 파일**(`bulk_alias_approved_ready_v0_5.json/csv`, **27건**) + 본 보고서. alias_count 66·relation 30·DATA_URL 불변, **approved 0**.

---

## 1. 작업 목적
Phase 2가 수집한 **pending product_full_name 32건**을 식약처 nedrug getItemDetail 원문으로 확인하여 품목명·단일 주성분 일치를 확정하고, **실제 alias 반영 직전의 approved-ready 후보 목록**을 만든다. alias JSON은 절대 수정하지 않으며, approved status도 만들지 않는다(approved-ready는 별도 파일).

## 2. Phase 2와의 차이
| 항목 | Phase 2(수집) | Phase 3(이번, 상세확정) |
|---|---|---|
| 소스 | nedrug searchDrug(목록) | **nedrug getItemDetail(상세 원문)** |
| 확인 깊이 | 목록 행의 주성분 | 상세 페이지 품목명(title) + distinct 주성분(ingrName) |
| confidence | medium | **high**(원문 확인 성공 시) |
| 산출 | pending 후보 추가 | detail_confirmed 표시 + **approved-ready 별도 파일** |
| status 변화 | — | 상세 불일치/복합제는 deferred 강등(이번엔 0), 나머지 pending 유지 |

## 3. pending 32건 상세확정 대상
- Phase 2가 만든 **status=pending 且 candidate_type=product_full_name 且 item_seq 보유** 후보 32건(단일성분 추정).
- 복합제 deferred 14·brand_core deferred 14·rejected 2는 **대상 아님**(미변경).

## 4. getItemDetail 확인 방식
1. `https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq=<seq>` (쿠키 jar + 리다이렉트 follow). 호출부 별도 함수(`get_item_detail`).
2. 원문에서 **품목명**(`<title>…상세보기-품목명`) + **distinct 주성분**(임베디드 JSON `"ingrName"`, 유니코드 이스케이프 디코드) 추출.
3. **확정 조건(전부 충족)**: ①품목명 base(괄호·공백 제거) == 후보 base ②주성분 distinct **1개(단일성분)** ③canonical ⊆ 그 주성분. ④표면형에 개행/제어공백 없음 ⑤에스오메프라졸/넥시움/itemSeq 201600209 아님.
4. 불충족 처리: 복합제(주성분 ≥2)·성분 불일치 → **deferred 강등**(이유 기록). 품목명 base 불일치/표면형 개행/네트워크·파싱 실패 → **pending 유지**(approved-ready 제외).

## 5. 확인 성공/실패/보류 수 (대상 32)
| 결과 | 수 | 처리 |
|---|---|---|
| **confirmed** | **31** | detail_confirmed=true, source_method=nedrug.getItemDetail, confidence=high, **status=pending 유지** |
| surface_form_whitespace | 1 | 표면형에 개행(신일모노독시엠캡슐) → pending 유지, approved-ready 제외 |
| combo_detected | 0 | (해당 없음 — Phase 2에서 복합제는 이미 deferred) |
| ingredient_mismatch | 0 | |
| name_mismatch | 0 | |
| fetch_failed / parse_failed | 0 | |
- 확정 31건 중 **4건은 기존 alias가 동일 itemSeq(동일 제품) 보유** → 중복 제품이라 approved-ready 제외(detail_confirmed=true·pending 유지).

## 6. approved-ready 후보 수
- **27건** = 확정 31 − itemSeq 중복 4. (전부 단일성분·완제·경구·원문 품목명 일치)

## 7. approved-ready 후보 목록 (27, 성분별)
- **독시사이클린** (3): 덴티스타캡슐(독시사이클린하이클레이트수화물), 독시정(독시사이클린수화물), 모노신정(독시사이클린하이클레이트수화물)
- **레보티록신** (5): 씬지로이드정0.05/0.15/0.1밀리그램(레보티록신나트륨수화물), 씬지록신정100/150마이크로그램(레보티록신나트륨수화물)
- **레보플록사신** (4): 글로비트정, 네보락신정, 노팍신정, 대웅레보플록사신정100밀리그램 (전부 (레보플록사신수화물))
- **메트포르민** (1): 구루메포민정500mg(메트포르민염산염)
- **목시플록사신** (1): 모벨록신정400밀리그램(목시플록사신염산염)
- **미노사이클린** (1): 미노클캡슐50밀리그램(미노사이클린염산염)
- **시프로플록사신** (2): 뉴록사신정, 로프신정250mg (전부 (시프로플록사신염산염수화물))
- **알렌드론산** (1): 보나드론정70밀리그램(알렌드론산나트륨수화물)
- **오플록사신** (4): 넬슨오플록사신정100밀리그램, 다비드정100밀리그램, 동광오플록사신정, 동화오플록사신정
- **토라세미드** (4): 세토람정10밀리그람, 세토람정2.5밀리그램, 토렘정10밀리그람, 토렘정2.5밀리그람 (전부 (토라세미드))
- **푸로세미드** (1): 후릭스정(푸로세미드)

> 전체 필드는 `data/candidates/bulk_alias_approved_ready_v0_5.json/csv`. 각 항목 approved_ready=true·reviewer_required=true(실제 반영은 사람 검토 후).

## 8. approved-ready 제외 사유 요약
| 사유 | 수 | 비고 |
|---|---|---|
| itemSeq 중복(동일 제품 기존 alias 보유) | 4 | 국제독시…캡슐100밀리그램(=기존 …캡슐100mg)·미노씬캡슐50mg(=미노씬)·토렘정5밀리그람(=토렘)·라식스정(=라식스). detail_confirmed=true이나 중복 제품 → 제외 |
| 표면형 개행(surface_form) | 1 | 신일모노독시엠캡슐 — nedrug 품목명 자체에 개행, 검색 alias 부적합 → Phase 2 정제 필요 |
| Phase 2 deferred(복합제+brand_core) | 28 | 이번 대상 아님(미변경) |
| Phase 1 rejected | 2 | 이번 대상 아님(미변경) |

## 9. queue status 분포 유지 여부
- **유지(Phase 2와 동일)**: pending **32** / approved **0** / rejected **2** / deferred **28** (total 62).
- 상세확정으로 status는 바뀌지 않음(확정 31·표면형 1 모두 pending 유지, 강등 0). detail_* 필드만 추가.

## 10. approved 0 유지 여부
- **유지(0).** approved-ready는 별도 파일에 approved_ready=true로만 표기, queue status는 pending. 검증기 #30이 queue approved=0을 강제.

## 11. alias JSON을 수정하지 않은 이유
1. PM 판정: 실제 alias 반영·approved 전환은 **다음 게이트**. 이번은 상세확정 + approved-ready 목록 작성까지.
2. approved-ready는 **사람 검토 필요**(reviewer_required=true). 자동 반영 금지.
3. 불변식 보호: alias_count 66·relation 30·DATA_URL 유지. 후보·approved-ready 모두 `data/candidates/`(앱 미참조).

## 12. 검증 결과
- **후보 검증기 31체크: PASS 31/31** (#19 detail_confirmed 무결성, #20~#30 approved-ready 파일 검증, **#31 approved-ready item_seq ∉ 기존 alias itemSeq**[중복 제품 금지] 신규).
- 음성 테스트: #19(detail 필드 누락·canonical∉detail_ingr), #22(큐 부재), #24(기존66 중복), #26(에스오메프라졸), #27(복합제), #29(approved_ready≠true), #30(queue approved), #31(itemSeq 중복) — 전부 정확 포착.
- **v0.3 alias validator 13/13 · Type B suite 7/7** (회귀 0).
- 무결성: approved-ready 27 전부 high·단일주성분·비복합·itemSeq 기존중복 0·queue에서 pending+detail_confirmed=true. queue approved 0.

## 13. 네트워크/API 한계
- getItemDetail은 품목명·주성분(성분코드 포함)은 주지만, 이번 확정은 **주성분 동일성**까지(허가사항 '사용상의 주의사항' 원문 대조는 relation 트랙의 몫). 따라서 approved-ready는 "검색 alias로서 단일성분·완제·경구 확정"이지 새 relation 근거가 아님.
- 일부 nedrug 품목명에 개행/제어문자 포함(신일모노…) → 검색 표면형 정제 필요.
- 네트워크 의존: 실패 시 해당 후보 pending 유지(이번 실패 0).

## 14. Phase 4에서 해야 할 일
1. **사람 검토 → approved 전환**: approved-ready 27을 PM/검토자가 확인 후 reviewer 채우고 status=approved 전환(별도 게이트).
2. **approved → alias JSON 반영**: product_full_name alias 추가 + alias_count 갱신 + (필요 시 verified_item_seqs는 이미 #8 화이트리스트로 처리되므로 product alias의 item_seq가 relation 대표 또는 화이트리스트에 있어야 #8 통과 — Phase 4에서 검토). **batch 30** 단위. 반영 시 v0.3 validator + Type B suite + 후보 검증기 전종 재통과.
3. 표면형 개행 후보(신일모노…) 정제 또는 제외 확정.
4. 상한 상향 재수집(Phase 2 상한 5 → 15~20)으로 후보 풀 확대 → 200 도달.

> ⚠️ Phase 4 주의: approved-ready의 product alias가 v0.3 validator #8(item_seq ∈ relation itemSeq ∪ verified_item_seqs)을 통과하려면, 각 itemSeq를 **verified_item_seqs 화이트리스트에 추가**해야 함(현재 화이트리스트는 4성분만). 즉 alias 반영 시 verified_item_seqs 확장이 동반(Phase 4 설계 포인트).

## 15. PM 판정 필요사항
1. **approved-ready 27 승인 범위**: 전체 승인 vs 성분별 상한(예: 성분당 2~3) 적용.
2. **verified_item_seqs 확장**: Phase 4에서 approved 27건 itemSeq를 화이트리스트에 추가하는 방식(일괄 vs 검토단위).
3. **itemSeq 중복 4·표면형 1 처리**: 폐기 vs 보류 기록 유지.
4. **상한 상향 재수집 시점**: Phase 4(반영) 먼저 vs 재수집 먼저(후보 풀 확대 후 일괄).
5. **batch 구성**: 27을 1 batch로 반영 vs 성분 균형 맞춰 분할.

## 16. batch 30 반영 가능성 평가
- approved-ready **27 < batch 30** → **1 batch로 반영 가능**(승인 시 alias_count 66 → 최대 93).
- 200 목표까지: 93 + (상한 상향 재수집 후 추가 batch). 상한 15~20 재수집 시 성분당 단일성분 ~10 확보 → 추가 ~100 후보 → batch 30 × 약 3~4회로 200 도달.
- 품질: 27건 전부 원문 확정(high)이라 1차 batch 신뢰도 높음. 단, Phase 4에서 verified_item_seqs 동반 확장 필요(§14 주의).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / **칼륨 행은 검색→안전카드 노출만, 구매·제품 링크 금지** / clinical 검수 전 published 금지 / validator PASS 없으면 배포·반영 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증 alias·itemSeq 금지 / 복합제는 단일성분 확정 전 approved-ready 금지 / 동일 제품(itemSeq) 중복 alias 금지 / approved-ready는 사람 검토(reviewer_required) 전까지 미반영.
