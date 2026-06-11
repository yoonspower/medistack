# MediStack v0.5 — bulk alias pipeline Phase 6 보고서 (batch 2 alias 반영, 93 → 123)

작성/실행일: **2026-06-11** / 단계: **Phase 6 batch 2 반영 완료(alias 93 → 123)** / 상위: `..._phase6_batch2_incorporation_plan.md`, `..._phase5_report.md`, `..._phase4_report.md`

> PM 판정(Phase 6): batch 2 approved-ready 30건을 **실제 alias JSON 반영**(product_aliases +30 AND verified_item_seqs +30 동반확장), alias_count 93 → **123**. validator **#54 옵션 A(incorporation-aware) 갱신** 승인. relation 30·DATA_URL·export·앱 불변.

---

## 1. 수정 파일
| 파일 | 변경 |
|---|---|
| `data/medistack_v0.3_aliases.json` | **product_aliases +30(55→85) · verified_item_seqs +30(31→61 entries, 11→12성분) · meta.alias_count 93→123** |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 반영된 30건 status pending→**approved** + reviewer=v0.5-phase6-batch2 + incorporated_at(이력) |
| `data/candidates/bulk_alias_approved_ready_batch2_v0_5.json/csv` | 30건 **incorporated=true** · incorporated_alias_batch=v0.5-batch2 · incorporated_at |
| `scripts/validate_bulk_alias_candidates.py` | **#54 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 #52에서 실제 반영 검증) |
| (불변) relation export(v0.1/v0.2)·batch1 AR·src/·index.html·.github/·DATA_URL | 무변경(git diff 0) |

## 2. alias_count 93 → 123 확인
- ingredient_aliases 38(불변) + product_aliases 55→**85** = **123**. meta.alias_count=123. ✓

## 3. product_aliases 증가 (+30)
- 55 → 85. 각 항목 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`(기존 스키마 동일). source_relation_ids = 해당 canonical 라이브 relation id:
  - 독시사이클린[7,8,9]·레보티록신[10,11]·레보플록사신[1,2,3]·메트포르민[12]·목시플록사신[24,25]·시프로플록사신[4,5,6]·알렌드론산[29]·오메프라졸[13,14]·오플록사신[21,22,23].

## 4. verified_item_seqs 증가 (+30 entries, 11→12성분)
- 31 → **61 entries**. 기존 8성분 append + **오메프라졸 신규 canonical 키 생성(12번째)**. 각 entry 추적정보 보존: `{item_seq, item_name, verified_at, method, batch_id:"v0.5-batch-2", source_method, source_checked_at, detail_checked_at}`. 이 화이트리스트 동반확장으로 신규 product_alias 30건이 v0.3 #8(`item_seq ∈ relation itemSeq ∪ verified 화이트리스트`) 통과.

## 5. 반영된 30건 (canonical 균등분산 9성분)
- **독시사이클린**(4): 독시라마이신캡슐100mg·독시메디정·독시엔디정·독시크정50밀리그램
- **레보티록신**(4): 씬지로이드정0.0375/0.075/0.112/0.2밀리그램
- **레보플록사신**(4): 동구레보플록사신수화물정100/250/500mg·동성레보플록사신정
- **메트포르민**(3): 그리코민정·그린페지정·글라비스서방정500밀리그람
- **목시플록사신**(3): 아벨록스정400밀리그람·조이록신정400밀리그램·퀴녹스정400밀리그램
- **시프로플록사신**(3): 록신정250밀리그램·메가록신정250밀리그램·메가시플록정
- **알렌드론산**(3): 본에이드정70밀리그램·본필정70밀리그램·비노스토발포정
- **오메프라졸**(3): 대한뉴팜오엠프라졸캡슐·라메졸캡슐20밀리그램·메프라졸캡슐 (verified 신규 성분)
- **오플록사신**(3): 리록신정·삼익오플록사신정·삼천당오플록사신정
> (전부 단일성분·완제·경구·getItemDetail 원문확정. 전체 표면형은 product_aliases[55:85] 참조.)

## 6. validator #54 옵션 A 갱신 (PM 승인)
- pre-incorporation: #54 = "batch2 approved-ready 는 incorporated=false". 반영하면 incorporated=true → #54 FAIL(Phase 4 #16/#7/#24/#31 와 동일 충돌).
- **옵션 A 갱신**: #54 → "incorporated ∈ {false(미반영), true(반영)} 정합". incorporated=true 의 **실제 반영 검증은 #52**(alias∈aliases ∧ itemSeq∈whitelist[canonical]). garbage 값은 #54 가 포착.
- 음성 테스트: garbage incorporated→#54 · 가짜 incorporated=true(alias 미존재)→#52 · 정상(all true)→PASS. (안전성 유지·강화)

## 7. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(incorporation-aware) | **PASS 47/47** (#30 queue approved 57건 반영검증 · #52 batch2 incorporated 반영검증 · #54 옵션 A) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (신규 30 product_alias + verified 화이트리스트 #8 통과) |
| Type B suite | **PASS 7/7** |
| 음성 테스트 | **3/3** (#54 garbage · #52 가짜반영 · 정상 PASS) |

## 8. smoke test 결과
- **신규 30건 30/30 PASS**: 각 alias → resolveAliasIngredients 정확히 해당 canonical 1종, filterRelations 결과가 그 canonical 의 relation 전부. **오메프라졸 신규 alias(라메졸캡슐 등) 라이브 확인**.
- **회귀 ALL PASS**: 타리비드→오플록사신 3 · 포사맥스→알렌드론산 1 · 토렘→토라세미드 2 · 넥시움→0 · #/r/15(excluded B12) fail-safe · renderable pool 30 · alias_count 123 · product 85.

## 9. 불변 / 안전
- relation **30 유지**, DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**, v0.1/v0.2 export·앱 코드·CI·batch1 AR **무변경**.
- 30건 외 alias 미추가 · itemSeq 중복 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1 incorporated 27건 그대로(approved 27→57). alias 는 검색 보조(guards.js 는 ingredient_aliases+product_aliases만 인덱싱, verified_item_seqs 미참조).

## 10. 다음 단계 (Phase 7 / batch 3)
1. **batch 3**: Phase 5 held 53(이미 detail_confirmed=true·v0.5-005)을 batch 2 반영 후 build → existing_seqs 가 batch2 itemSeq 30 제외 → 다음 30 자동 산출(123→153). `confirm --ar-only-batch v0.5-005 --ar-balanced --ar-batch-id v0.5-batch-3 --ar-limit 30` → Phase 6 패턴 반영.
2. 추가 재수집(다른 페이지/성분, 미노/토라세미드/푸로세미드/HCTZ 단일 추가 탐색) 병행 → 200 도달.
3. 잔여: 복합제 deferred tier 판정 · 표면형 개행 정제 · brand_core tier.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / incorporated 후보는 alias JSON 실제 반영 검증(가짜 승인 금지).
