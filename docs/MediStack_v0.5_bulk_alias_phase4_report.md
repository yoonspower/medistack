# MediStack v0.5 — bulk alias pipeline Phase 4 보고서 (approved-ready batch 1 alias 반영)

작성/실행일: **2026-06-11** / 단계: **Phase 4 batch 1 반영 완료(alias 66 → 93)** / 상위: `..._pipeline_plan.md`, `..._phase3_report.md`

> PM 판정(Phase 4): approved-ready 27건을 1 batch로 **실제 alias JSON 반영**. product_aliases 추가 + **verified_item_seqs 동반 확장** 필수. relation 30·DATA_URL 불변, alias_count 66 → **93**. itemSeq 중복 4·표면형 개행 1·복합제·brand_core·에스오메프라졸 반영 금지.
> PM 추가 판정(반영 중 충돌 해소): bulk candidate validator가 pre-incorporation 게이트(#16 alias_count==66 하드코딩, #7/#24/#31 "후보는 기존 alias에 없어야")라 반영 후 충돌 → **incorporation-aware로 갱신** 채택.

---

## 1. 수정 파일
| 파일 | 변경 |
|---|---|
| `data/medistack_v0.3_aliases.json` | **product_aliases +27(28→55) · verified_item_seqs +27(4→31 entries, 11성분) · meta.alias_count 66→93** |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 반영된 27건 status pending→**approved** + incorporated_at·reviewer 표시(이력) |
| `data/candidates/bulk_alias_approved_ready_v0_5.json/csv` | 27건 incorporated=true·incorporated_alias_batch=v0.5-batch1 표시 |
| `scripts/validate_bulk_alias_candidates.py` | **incorporation-aware** 갱신(아래 §7) |
| (불변) relation export(v0.1/v0.2)·src/·index.html·.github/·DATA_URL | 무변경 |

## 2. alias_count 66 → 93 확인
- ingredient_aliases 38(불변) + product_aliases 28→**55** = **93**. meta.alias_count=93. ✓

## 3. product_aliases 증가 수
- **+27**(28 → 55). 각 항목 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}` (기존 스키마 동일). source_relation_ids = 해당 canonical 의 라이브 relation id.

## 4. verified_item_seqs 증가 수
- **+27 entries**(4 → 31). 11성분(기존 4성분 확장 + 신규 7성분). 각 entry에 추적정보 보존: `{item_seq, item_name, verified_at, method, batch_id, source_method, source_checked_at, detail_checked_at}`. 이 화이트리스트 확장으로 신규 product_alias 27건이 v0.3 validator #8(`item_seq ∈ relation itemSeq ∪ verified_item_seqs`)을 통과.

## 5. 반영된 27건 (성분별)
- **독시사이클린**(3): 덴티스타캡슐·독시정·모노신정
- **레보티록신**(5): 씬지로이드정0.05/0.15/0.1밀리그램·씬지록신정100/150마이크로그램
- **레보플록사신**(4): 글로비트정·네보락신정·노팍신정·대웅레보플록사신정100밀리그램
- **메트포르민**(1): 구루메포민정500mg
- **목시플록사신**(1): 모벨록신정400밀리그램
- **미노사이클린**(1): 미노클캡슐50밀리그램
- **시프로플록사신**(2): 뉴록사신정·로프신정250mg
- **알렌드론산**(1): 보나드론정70밀리그램
- **오플록사신**(4): 넬슨오플록사신정100밀리그램·다비드정100밀리그램·동광오플록사신정·동화오플록사신정
- **토라세미드**(4): 세토람정10밀리그람·세토람정2.5밀리그램·토렘정10밀리그람·토렘정2.5밀리그람
- **푸로세미드**(1): 후릭스정
> (전부 단일성분·완제·경구·getItemDetail 원문확정. 전체 표면형은 alias JSON product_aliases[28:] 참조.)

## 6. 제외 유지된 항목 (반영 안 함)
- itemSeq 기존중복 4(국제독시…캡슐100밀리그램·미노씬캡슐50mg·토렘정5밀리그람(토라세미드)·라식스정(푸로세미드)) — queue pending 유지.
- 표면형 개행 1(신일모노독시엠캡슐) — queue pending 유지.
- 복합제 deferred 14 · brand_core deferred 14 · rejected 2 — 미반영.
- 에스오메프라졸/15행 — 영구 제외. (id 16 ×Mg는 기존 live relation으로 Phase 4와 무관.)

## 7. validator incorporation-aware 갱신 (PM 승인)
pre-incorporation 게이트가 반영 후 정상 상태를 FAIL로 보던 문제를 해소(안전성은 유지·강화):
- **#16**: `alias_count==66` 하드코딩 → `alias_count==항목수 ∧ relation==30 ∧ alias_count≥66(단조)`. (변조·불일치는 여전히 탐지)
- **#7 / #24 / #31**: incorporated(status=approved / incorporated=true) 후보는 "기존 alias와 같아야 정상"이므로 중복검사에서 제외. 미반영 후보는 여전히 중복 차단.
- **#23**: approved-ready의 queue 후보 status pending **또는 approved(incorporated)** 허용.
- **#30(신규 의미)**: `approved status 0` → **queue approved 후보는 alias JSON에 실제 반영됨**(alias∈aliases ∧ itemSeq∈whitelist[canonical]). 가짜 승인 차단.
- **#32(신규)**: approved-ready incorporated 후보는 alias JSON에 실제 반영됨(동일 검증). 체크 31→**32개**.
- 음성 테스트(ephemeral) 5/5: 변조 alias_count→#16, approved 미반영→#30, 비승인 중복→#7, AR incorporated 미반영→#22·#32. (가짜 incorporation·tampering 정확 포착)

## 8. 검증 결과
| validator | 결과 |
|---|---|
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (신규 27 alias + verified 화이트리스트 #8 통과) |
| Type B suite | **PASS 7/7** |
| bulk candidate(incorporation-aware) | **PASS 32/32** |

## 9. smoke test 결과
- **신규 27건 27/27 PASS**: 각 alias → resolveAliasIngredients 정확히 해당 canonical 1종, filterRelations 결과가 그 canonical 의 relation 전부.
- **회귀 ALL PASS**: 타리비드→오플록사신 3 · 포사맥스→알렌드론산 1 · 토렘→토라세미드 2 · 넥시움→0 · #/r/15(excluded B12) fail-safe(renderable 미노출).
- (검색풀 getRenderableRelations 30건, id 15 미노출. 에스오메프라졸 alias 0.)

## 10. 불변/안전
- relation **30 유지**, DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**, v0.1/v0.2 export·앱 코드·CI **무변경**.
- 27건 외 alias 미추가 · itemSeq 중복 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음.
- alias는 검색 보조(앱 guards.js는 ingredient_aliases+product_aliases만 인덱싱, verified_item_seqs 미참조). relation 신규생성 없음.

## 11. 다음 단계 (Phase 5)
1. **상한 상향 재수집**: Phase 2 collect `--max-per-ingredient` 5 → 15~20 으로 재수집 → 추가 product_full_name 후보 풀 확대(현재 라이브 93, 200까지 +107).
2. **Phase 3 상세확정 → Phase 4 batch 반영** 반복: batch 30 단위. 약 3~4 batch로 200 도달.
3. 잔여 처리: 표면형 개행 1(정제), itemSeq 중복 4(폐기/보류), 복합제 deferred 14·brand_core deferred 14(별도 tier 판정).
4. (선택) data.go.kr OpenAPI 보강.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / incorporated 후보는 alias JSON 실제 반영 검증(가짜 승인 금지).
