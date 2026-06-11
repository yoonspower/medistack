# MediStack v0.5 — bulk alias pipeline Phase 10 보고서 (batch 4 alias 반영, 153 → 176)

작성/실행일: **2026-06-11** / 단계: **Phase 10 batch 4 반영 완료(alias 153 → 176)** / 상위: `..._phase10_batch4_incorporation_plan.md`, `..._phase9_report.md`, `..._phase8_report.md`

> PM 판정(Phase 10): batch 4 approved-ready 23건을 **실제 alias JSON 반영**(product_aliases +23 AND verified_item_seqs +23 동반확장), alias_count 153 → **176**. validator **#94 옵션 A(incorporation-aware) 갱신** 승인. relation 30·DATA_URL·export·앱 불변.

---

## 1. 수정 파일
| 파일 | 변경 |
|---|---|
| `data/medistack_v0.3_aliases.json` | **product_aliases +23(115→138) · verified_item_seqs +23(91→114 entries, 12성분 유지) · meta.alias_count 153→176** |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 반영된 23건 status pending→**approved** + reviewer=v0.5-phase10-batch4 + incorporated_at, meta.phase10_incorporation 추가 |
| `data/candidates/bulk_alias_approved_ready_batch4_v0_5.json/csv` | 23건 **incorporated=true** · incorporated_alias_batch=v0.5-batch4 · incorporated_at |
| `scripts/validate_bulk_alias_candidates.py` | **#94 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 #92에서 실제 반영 검증) |
| (불변) relation export(v0.1/v0.2)·batch1/2/3 AR·src/·index.html·.github/·DATA_URL | 무변경(md5 0-diff) |

## 2. alias_count 153 → 176 확인
- ingredient_aliases 38(불변) + product_aliases 115→**138** = **176**. meta.alias_count=176. ✓

## 3. product_aliases 증가 (+23)
- 115 → 138. source_relation_ids = 해당 canonical 라이브 relation id: 레보티록신[10,11]·레보플록사신[1,2,3]·시프로플록사신[4,5,6]·알렌드론산[29]·오플록사신[21,22,23].

## 4. verified_item_seqs 증가 (+23 entries, 12성분 유지)
- 91 → **114 entries**. **5성분 전부 기존 canonical 키에 append**(신규 키 없음) → verified canonical **12 → 12 유지**. method=`...v0.5-batch-4 ingrName=...`·batch_id=v0.5-batch-4. 이 화이트리스트 동반확장으로 신규 product_alias 23건이 v0.3 #8 통과.

## 5. 반영된 23건 (canonical 5성분)
- **레보티록신**(2): 씬지록신정 75/88 마이크로그램
- **레보플록사신**(6): 레보건정500밀리그램·레보라신정·레보미신정·레보바이정·레보바이정250/500밀리그램
- **시프로플록사신**(7): 시록신정250mg·시폭사신정250밀리그람·시푸로신정·시프라신정250밀리그램·시프로사정·시프로신정·신일시프로플록사신염산염수화물정
- **알렌드론산**(1): 알렌맥스정70밀리그램
- **오플록사신**(7): 엑센정·영풍오플록사신정100밀리그램·오라록신정100mg·오로신정100밀리그램·오록사신정100밀리그램·오비드정·오플라정
> (전부 단일성분·완제·경구·getItemDetail 원문확정. 전체 표면형/itemSeq 는 product_aliases[115:138] 및 `..._phase9_report.md` §3 참조.)

## 6. validator #94 옵션 A 갱신 (PM 승인)
- pre-incorporation(Phase 9): #94 = "batch4 는 incorporated=false". 반영하면 incorporated=true → #94 FAIL(Phase 4 #16·Phase 6 #54·Phase 8 #74 와 동일 충돌).
- **옵션 A 갱신**: #94 → "incorporated ∈ {false,true} 정합". true 의 **실제 반영 검증은 base+12(#92)**(alias∈aliases ∧ itemSeq∈whitelist[canonical]). garbage 값은 #94 가 포착.
- 음성 테스트: garbage→#94 · 가짜 incorporated=true(alias 미존재)→#92 · 정상→PASS.

## 7. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(incorporation-aware) | **PASS 77/77** (#16 alias_count==176·relation30 정합 · #92 batch4 incorporated 23 실제 반영검증 · #94 옵션 A) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (신규 23 product_alias + verified 화이트리스트 #8 통과) |
| Type B suite | **PASS 7/7** |
| 음성 테스트 | **3/3** (#94 garbage · #92 가짜반영 · 정상 PASS) |

## 8. smoke test 결과
- **신규 23건 23/23 라이브 PASS**: 각 alias → resolveAliasIngredients 정확히 해당 canonical 1종, filterRelations 결과가 그 canonical 의 relation 전부.
- **회귀 ALL PASS**: 타리비드→오플록사신 3 · 포사맥스→알렌드론산 1 · 토렘→토라세미드 2 · 넥시움→0 · #/r/15 fail-safe · alias_count 176 · product 138 · verified 114/12.

## 9. 불변 / 안전
- relation **30 유지**, DATA_URL `./data/medistack_v0.2_beta_export.json` **불변**, v0.1/v0.2 export·앱 코드·CI·batch1/2/3 AR **무변경**(md5 0-diff).
- 23건 외 alias 미추가 · itemSeq 중복 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품/구매/제휴 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1/2/3 incorporated 87 그대로(queue approved 87→**110**). alias 는 검색 보조(guards.js 는 ingredient_aliases+product_aliases만 인덱싱).
- 반영 = ephemeral `/tmp/ms_incorporate_batch4.py`(전제/사후조건 assert 내장, **커밋 안 함**).

## 10. 다음 단계 (Phase 11 / batch 5 — 재수집 필요)
1. **🔑 held 풀 소진(0)**: v0.5-005 confirmed 단일성분 83건 전부 반영 완료(batch2 30 + batch3 30 + batch4 23). **추가 alias 는 네트워크 재수집 필수.**
2. **batch 5 재수집**: 미노사이클린/토라세미드/푸로세미드/HCTZ 단일 + 기존 13성분의 다른 페이지(searchDrug `&page=N`, `--max-pages` 상향) → getItemDetail 확정 → approved-ready batch5. **200 도달엔 ~24건 추가 필요**(현재 176).
3. 잔여 tier: 복합제 deferred(32) 판정 · 표면형 개행 정제 · brand_core(14 deferred).

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / incorporated 후보는 alias JSON 실제 반영 검증(가짜 승인 금지).
