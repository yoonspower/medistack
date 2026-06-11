# MediStack v0.5 — bulk alias pipeline Phase 2 보고서 (nedrug 수집기, dry-run)

작성/실행일: **2026-06-11** / 단계: **Phase 2 dry-run 수집 완료, alias JSON 미반영** / 상위: `MediStack_v0.5_bulk_alias_pipeline_plan.md`, `MediStack_v0.5_bulk_alias_phase1_report.md`

> PM 판정(Phase 2): 수집소스=nedrug searchDrug 단독 · getItemDetail은 itemSeq 확정용 · 목표 200 · batch 30 · queue JSON+CSV · brand_core 14건 계속 deferred · rejected 2건 유지 · product_full_name **성분당 최대 5개 dry-run** · **alias JSON 반영 금지** · approved export는 다음 PM 게이트.
> 이 단계 산출물: 외부 수집기(`scripts/collect_nedrug_alias_candidates.py`) + 검증기 최소 보강(16→18체크) + review queue 갱신(Phase 1 16 → **62**) + 본 보고서. `data/medistack_v0.3_aliases.json` 미수정, alias_count 66·relation 30·DATA_URL 불변, **approved 0**.

---

## 1. 작업 목적
라이브 relation 30에 연결된 허용 canonical(에스오메프라졸 제외 13종)에 대해 식약처 nedrug `searchDrug`(주성분 검색) 결과에서 **완제·경구·정상** 품목명을 dry-run 수집하여 review queue에 **pending product_full_name** 후보로 추가한다. 목표 200 alias로 가는 대량 후보의 1차 수집 batch이며, **실제 alias 편입(approved export)은 다음 PM 게이트의 별도 단계**다.

## 2. Phase 1과의 차이
| 항목 | Phase 1 | Phase 2(이번) |
|---|---|---|
| 소스 | 내부 데이터(현행 alias) | **외부 nedrug searchDrug**(네트워크) |
| 생성 후보 유형 | brand_core(deferred)/rejected | **product_full_name pending**(단일성분) + deferred(복합제) |
| 외부 API | 0회 | 13성분 × searchDrug 1회 = 13회 |
| 신규 후보 | 16 | **46** |
| itemSeq | 검증 상속 | searchDrug 결과 itemSeq(상세 getItemDetail 미실행 → confidence medium) |
| 안전 | 모두 미승인 | 단일성분만 pending, 복합제·brand_core는 deferred, approved 0 |

## 3. 수집 소스
- **nedrug searchDrug**: `https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1=<성분>` (쿠키 jar + 리다이렉트 follow). 결과 행에서 **품목명·품목기준코드(itemSeq)·주성분·완제/원료구분·취소/취하구분**을 직접 파싱.
- getItemDetail은 이번 dry-run에서 미실행(Phase 3에서 pending 후보 원문 확정용). searchDrug 행의 주성분으로 보수적 매칭만 수행.
- 호출부는 별도 함수(`nedrug_search`)로 분리. 네트워크 실패/무응답/파싱실패 시 해당 성분을 **skipped**로 기록(전체 실패 아님).

## 4. 실행 옵션 (CLI)
| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--max-per-ingredient` | 5 | 성분당 수집 상한 |
| `--limit-ingredients` | (없음=전체) | 앞 N개 canonical만 |
| `--no-network` | off | 네트워크 없이 병합/정규화/구조 검증만 |
| `--dry-run` | on | dry-run(alias JSON 미수정·approved 미생성) |
| `--checked-at` | 2026-06-11 | source_checked_at(실행일) |
| `--queue-in/--out-json/--out-csv` | 기본 queue 경로 | 입출력 |

실행: `--no-network`로 병합/정규화 18/18 PASS 확인 → `--max-per-ingredient 5`로 dry-run 수집.

## 5. 수집 대상 canonical 수
- **13종**(라이브 14 − 에스오메프라졸): 독시사이클린·레보티록신·레보플록사신·메트포르민·목시플록사신·미노사이클린·시프로플록사신·알렌드론산·오메프라졸·오플록사신·토라세미드·푸로세미드·히드로클로로티아지드.
- Phase 1 생성기와 **동일 허용 로직 재사용**(라이브 − 에스오메프라졸 − excluded 전용).

## 6. 수집 성공/실패/스킵 성분 수
- **성공 13 / 실패 0 / 스킵 0.** (성분당 검색·파싱 모두 성공)
- 성분별 수집(단일 pending / 복합제 deferred):

| 성분 | pending(단일) | deferred(복합제) |
|---|---|---|
| 독시사이클린 | 5 | 0 |
| 레보티록신 | 5 | 0 |
| 레보플록사신 | 4 | 0 |
| 메트포르민 | 1 | 4 |
| 목시플록사신 | 1 | 0 |
| 미노사이클린 | 2 | 0 |
| 시프로플록사신 | 2 | 0 |
| 알렌드론산 | 1 | 3 |
| 오메프라졸 | 0 | 2 |
| 오플록사신 | 4 | 0 |
| 토라세미드 | 5 | 0 |
| 푸로세미드 | 2 | 0 |
| 히드로클로로티아지드 | 0 | 5 |
| **합계** | **32** | **14** |

> 복합제(예: 가브스메트정=빌다글립틴/메트포르민, 국제로잘탄플러스=로사르탄/히드로클로로티아지드)는 주성분에 canonical을 포함하나 **단일성분이 아니므로 pending 금지 → deferred**(사람 검토). Phase 1 itemSeq 채록 SOP(단일성분)와 PM 보수성 지시 준수.

## 7. 신규 후보 수
- **신규 46건** = pending(단일) 32 + deferred(복합제) 14.
- 제외(중복/필터): 기존 66 alias·현재 queue·verified_item_seqs(4)·원료/점안/주사/외용/시럽/수출용/취소품목 다수 제외. 성분당 상한 5 적용.

## 8. status 분포 (전체 queue 62)
| status | 수 | 구성 |
|---|---|---|
| pending | **32** | 단일성분 product_full_name(getItemDetail 확정 대기) |
| approved | **0** | 설계상 0(다음 PM 게이트) |
| rejected | 2 | Phase 1 자동거부(국제독시…×2) |
| deferred | 28 | brand_core 14(Phase 1) + 복합제 14(Phase 2) |
| **total** | **62** | |

## 9. 기존 queue 보존 여부
- **보존됨.** Phase 1의 brand_core 14 + rejected 2 = 16건 전부 유지(병합). candidate identity(alias/type/status/item_seq/reason) 불변.
- 단, 검증기 source_method 화이트리스트(#17) 충족을 위해 Phase 1 후보의 `source_method`를 **`internal.phase1`로 정규화**(서술형 유래는 `reason`·`item_name`·`item_seq`에 그대로 보존, 정보 손실 없음).

## 10. alias JSON을 수정하지 않은 이유
1. **PM 판정 #9·#10**: 이번 단계는 dry-run 수집만, 실제 alias 반영·approved export는 다음 게이트.
2. **승인 절차 분리**: 자동 수집 후보는 pending/deferred로만. approved 0 → alias에 넣을 것 없음.
3. **상세 미확정**: pending은 getItemDetail 원문 확정(Phase 3) 후에야 approved 가능. 미검증분을 alias에 넣지 않는다.
4. **불변식 보호**: alias_count 66·relation 30·DATA_URL 유지. 후보는 `data/candidates/`에만(앱·검색 인덱스 미참조).

## 11. 검증 결과
- **후보 검증기(보강 18체크): PASS 18/18.** (#17 source_method enum, #18 product_full_name pending/approved의 item_seq·source_method·source_checked_at 필수 신규)
- 음성 테스트(ephemeral): source_method 비허용→#17, pending product item_seq/checked_at 없음→#18, 둘 다 없음→#17·#18, deferred는 #18 면제 — 6/6 정확.
- **기존 v0.3 alias validator: 13/13 PASS** (회귀 0). **Type B test suite: 7/7 PASS** (회귀 0).
- 무결성: 전 pending 정/캡슐·canonical⊆주성분·숫자 itemSeq·source_checked_at 존재, 에스오메프라졸/넥시움/금지 itemSeq 0, 기존 66·queue 내부·verified(4) 중복 0, approved 0.

## 12. 네트워크/API 한계
- searchDrug는 **목록 페이지**라 주성분·완제/원료·취소상태는 주지만 **사용상의 주의사항 원문은 없음**. 따라서 confidence는 **medium 상한**(상세 미확정).
- searchDrug `ingrName1`은 부분일치라 점안액·주사·복합제·원료·수출용이 섞여 나옴 → 코드 필터(완제·경구·정상·단일성분 우선)로 보수적 선별.
- 성분당 상한 5라 실제 완제품 수보다 적게 수집(예: 레보플록사신은 결과에 정제만 10+종 존재). 200 도달엔 상한 상향 필요(§15).
- 네트워크 의존: 실패 시 해당 성분 skipped(0건 허용). data.go.kr OpenAPI는 미사용(serviceKey 미발급, PM #1=searchDrug 단독).

## 13. Phase 3에서 해야 할 일
1. **pending 32건 getItemDetail 원문 확정**: 품목명·주성분·성분코드 대조 → confidence 상향, 불일치는 deferred/rejected 강등.
2. **사람 검토 → approved**: reviewer·source 채움. 복합제 deferred 14·brand_core 14 tier 결정.
3. **approved batch(30) → alias JSON 반영**: 별도 PM 게이트. 반영 시 v0.3 validator + Type B suite + 후보 검증기 전종 재통과 후 커밋/배포.
4. 상한 상향 재수집(§15)으로 후보 풀 확대.

## 14. PM 판정 필요사항
1. **복합제 14건 처리**: deferred 유지(권장) / 일부 검토승격 / 일괄 rejected.
2. **상한 상향**: 다음 수집 batch에서 `--max-per-ingredient`를 5 → 15~20으로 올릴지(200 도달 속도).
3. **getItemDetail 확정 자동화**: Phase 3에서 pending 32건 자동 getItemDetail 대조 스크립트 추가 여부.
4. **approved 게이트**: pending → approved 승격을 (a)사람 수동 status 편집 후 export 스크립트 (b)검토 메타 입력 CLI 중 무엇으로.
5. **batch 파일**: 단일 queue status 갱신 유지(현행) vs batch별 파일 분리.

## 15. 200 alias 목표까지 예상 batch 수
- 현재: alias_count 66(라이브) + queue pending 32(단일·강후보) + deferred 42.
- 200 도달 = 라이브 66에서 **+134 approved** 필요.
- 상한 5로는 13성분 × 단일성분 ~2.5평균 = 32 수준. **상한 15~20 상향** 시 13성분 × 단일 ~10~15 ≈ 130~190 후보 확보 가능(레보플록사신·시프로플록사신·메트포르민 등 제네릭 다수).
- 검토·승인 후 batch 30 단위 반영 → **약 5 batch**(30×5=150)로 200 근접. 복합제·brand_core를 일부 승격하면 batch 수 감소.
- 현실 경로: ①상한 상향 재수집(1~2 batch 수집) → ②getItemDetail 확정 → ③batch 30씩 5회 반영.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / **칼륨 행은 검색→안전카드 노출만, 구매·제품 추천 링크 금지** / clinical 검수 전 published 금지 / validator PASS 없으면 배포·반영 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 숫자 위해 미검증 alias·itemSeq 금지 / 복합제는 단일성분 검증 전 pending 금지 / 후보는 사람 승인 전까지 미반영.
