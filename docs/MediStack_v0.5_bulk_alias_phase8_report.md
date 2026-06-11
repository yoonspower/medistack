# MediStack v0.5 — bulk alias pipeline Phase 8 보고서 (batch 3 alias 반영, 123 → 153)

작성/실행일: **2026-06-11** / 단계: **Phase 8 batch 3 반영 완료(alias 123 → 153)** / 상위: `..._phase8_batch3_incorporation_plan.md`, `..._phase7_report.md`, `..._phase6_report.md`

> PM 판정(Phase 8): batch 3 approved-ready 30건을 **실제 alias JSON 반영**(product_aliases +30 AND verified_item_seqs +30 동반확장), alias_count 123 → **153**. validator **#74 옵션 A(incorporation-aware) 갱신** 승인. relation 30·DATA_URL·export·앱 불변.

---

## 1. 수정 파일
| 파일 | 변경 |
|---|---|
| `data/medistack_v0.3_aliases.json` | **product_aliases +30(85→115) · verified_item_seqs +30(61→91 entries, 12성분 유지) · meta.alias_count 123→153** |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 반영된 30건 status pending→**approved** + reviewer=v0.5-phase8-batch3 + incorporated_at(이력), meta.phase8_incorporation 추가 |
| `data/candidates/bulk_alias_approved_ready_batch3_v0_5.json/csv` | 30건 **incorporated=true** · incorporated_alias_batch=v0.5-batch3 · incorporated_at |
| `scripts/validate_bulk_alias_candidates.py` | **#74 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 #72에서 실제 반영 검증) |
| (불변) relation export(v0.1/v0.2)·batch1/batch2 AR·src/·index.html·.github/·DATA_URL | 무변경(md5 0-diff) |

## 2. alias_count 123 → 153 확인
- ingredient_aliases 38(불변) + product_aliases 85→**115** = **153**. meta.alias_count=153. ✓

## 3. product_aliases 증가 (+30)
- 85 → 115. 각 항목 `{alias, canonical_ingredient, kind:"product", lang:"ko", item_seq, source_relation_ids}`. source_relation_ids = 해당 canonical 라이브 relation id:
  - 독시사이클린[7,8,9]·레보티록신[10,11]·레보플록사신[1,2,3]·메트포르민[12]·시프로플록사신[4,5,6]·알렌드론산[29]·오메프라졸[13,14]·오플록사신[21,22,23]. (목시플록사신·에스오메프라졸 미포함 — batch 3 에 없음)

## 4. verified_item_seqs 증가 (+30 entries, 12성분 유지)
- 61 → **91 entries**. **8성분 전부 기존 canonical 키에 append**(Phase 6 와 달리 **신규 키 없음** — 오메프라졸 포함 8성분 모두 batch 2 까지에서 이미 생성됨) → verified canonical **12 → 12 유지**. 각 entry 추적정보 보존: `{item_seq, item_name, verified_at, method:"...v0.5-batch-3 ingrName=...", batch_id:"v0.5-batch-3", source_method, source_checked_at, detail_checked_at}`. 이 화이트리스트 동반확장으로 신규 product_alias 30건이 v0.3 #8(`item_seq ∈ relation itemSeq ∪ verified 화이트리스트`) 통과.

## 5. 반영된 30건 (canonical 균등분산 8성분)
- **독시사이클린**(2): 바이독시정·영풍독시사이클린정100밀리그램
- **레보티록신**(5): 씬지록신정 25/50/112/125/137 마이크로그램
- **레보플록사신**(5): 라이록사신정·레나신정·레노보정·레록신정·레보건정100밀리그램
- **메트포르민**(1): 글라비스정
- **시프로플록사신**(5): 미래시프로플록사신정·베아신정250/500밀리그램·사이톱신정·삼성시플로프록사신정
- **알렌드론산**(5): 비스본정·아렌맥스정·알드렌정70밀리그램·알레네정70밀리그램·알렌드로정70밀리그램
- **오메프라졸**(2): 바로메졸캡슐·바이넥스오메프라졸캡슐
- **오플록사신**(5): 서울오플록사신정·셀릭스오플록사신정100밀리그램·셀트리온오플록신정100밀리그램·안플레임정·에펙신정100밀리그램
> (전부 단일성분·완제·경구·getItemDetail 원문확정. 전체 표면형/itemSeq 는 product_aliases[85:115] 및 `..._phase7_report.md` §3 참조.)

## 6. validator #74 옵션 A 갱신 (PM 승인)
- pre-incorporation(Phase 7): #74 = "batch3 approved-ready 는 incorporated=false". 반영하면 incorporated=true → #74 FAIL(Phase 4 #16, Phase 6 #54 와 동일 충돌).
- **옵션 A 갱신**: #74 → "incorporated ∈ {false(미반영), true(반영)} 정합". incorporated=true 의 **실제 반영 검증은 base+12(#72)**(alias∈aliases ∧ itemSeq∈whitelist[canonical]). garbage 값은 #74 가 포착.
- 음성 테스트: garbage incorporated→#74 · 가짜 incorporated=true(alias 미존재)→#72 · 정상(all true)→PASS. (안전성 유지·강화)

## 7. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(incorporation-aware) | **PASS 62/62** (#16 alias_count==153·relation30 정합 · #72 batch3 incorporated 30 실제 반영검증 · #74 옵션 A) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (신규 30 product_alias + verified 화이트리스트 #8 통과) |
| Type B suite | **PASS 7/7** |
| 음성 테스트 | **3/3** (#74 garbage · #72 가짜반영 · 정상 PASS) |

## 8. smoke test 결과
- **신규 30건 30/30 라이브 PASS**: 각 alias → resolveAliasIngredients 정확히 해당 canonical 1종, filterRelations 결과가 그 canonical 의 relation 전부.
- **회귀 ALL PASS**: 타리비드→오플록사신 3 · 포사맥스→알렌드론산 1 · 토렘→토라세미드 2 · 넥시움→0 · #/r/15(excluded B12) fail-safe · alias_count 153 · product 115 · verified 91/12.

## 9. 불변 / 안전
- relation **30 유지**, DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**, v0.1/v0.2 export·앱 코드·CI·batch1/batch2 AR **무변경**(md5 0-diff).
- 30건 외 alias 미추가 · itemSeq 중복 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1 incorporated 27 · batch 2 incorporated 30 그대로(queue approved 57→**87**). alias 는 검색 보조(guards.js 는 ingredient_aliases+product_aliases만 인덱싱, verified_item_seqs 미참조).
- 반영 = ephemeral `/tmp/ms_incorporate_batch3.py`(전제/사후조건 assert 내장, **커밋 안 함**).

## 10. 다음 단계 (Phase 9 / batch 4)
1. **batch 4**: Phase 7 held 23(이미 detail_confirmed=true·v0.5-005)을 batch 3 반영 후 build → existing_seqs 가 batch3 itemSeq 30 제외 → 다음 23 자동 산출(153→176). `confirm --ar-only-batch v0.5-005 --ar-balanced --ar-batch-id v0.5-batch-4 --ar-limit 30`.
2. 추가 재수집(다른 페이지/성분, 미노사이클린/토라세미드/푸로세미드/HCTZ 단일 추가 탐색) 병행 → 200 도달(held 23 만으론 176, 추가 ~24건 필요).
3. 잔여: 복합제 deferred tier 판정 · 표면형 개행 정제 · brand_core tier.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / incorporated 후보는 alias JSON 실제 반영 검증(가짜 승인 금지).
