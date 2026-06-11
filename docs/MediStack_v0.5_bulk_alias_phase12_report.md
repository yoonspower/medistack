# MediStack v0.5 — bulk alias pipeline Phase 12 보고서 (batch 5 alias 반영, 176 → 206) 🎯 v0.5 목표 200 도달

작성/실행일: **2026-06-11** / 단계: **Phase 12 batch 5 반영 완료(alias 176 → 206)** / 상위: `..._phase12_batch5_incorporation_plan.md`, `..._phase11_report.md`, `..._phase10_report.md`

> PM 판정(Phase 12): batch 5 approved-ready 30건 **실제 alias JSON 반영**(product +30 AND verified +30 동반확장), alias_count 176 → **206**. validator **#114 옵션 A 갱신** 승인. relation 30·DATA_URL·export·앱 불변. **🎯 alias 206 = v0.5 목표 200 도달·초과.**

---

## 1. 수정 파일
| 파일 | 변경 |
|---|---|
| `data/medistack_v0.3_aliases.json` | **product_aliases +30(138→168) · verified_item_seqs +30(114→144 entries, 12성분 유지) · meta.alias_count 176→206** |
| `data/candidates/bulk_alias_review_queue_v0_5.json/csv` | 반영된 30건 status pending→**approved** + reviewer=v0.5-phase12-batch5 + incorporated_at, meta.phase12_incorporation 추가 |
| `data/candidates/bulk_alias_approved_ready_batch5_v0_5.json/csv` | 30건 **incorporated=true** · incorporated_alias_batch=v0.5-batch5 · incorporated_at |
| `scripts/validate_bulk_alias_candidates.py` | **#114 옵션 A 갱신**(incorporated ∈ {false,true} 정합, true는 #112에서 실제 반영 검증) |
| (불변) relation export(v0.1/v0.2)·batch1~4 AR·src/·index.html·.github/·DATA_URL | 무변경(md5 0-diff) |

## 2. alias_count 176 → 206 확인 🎯
- ingredient_aliases 38(불변) + product_aliases 138→**168** = **206**. **v0.5 목표 alias 200 도달·초과**(206). ✓

## 3. product_aliases 증가 (+30)
- 138 → 168. source_relation_ids = 레보플록사신[1,2,3]·메트포르민[12]·시프로플록사신[4,5,6]·알렌드론산[29]·오메프라졸[13,14]·오플록사신[21,22,23].

## 4. verified_item_seqs 증가 (+30 entries, 12성분 유지)
- 114 → **144 entries**. **6성분 전부 기존 키 append**(신규 키 없음) → verified canonical **12 → 12 유지**. method=`...v0.5-batch-5 ingrName=...`·batch_id=v0.5-batch-5.

## 5. 반영된 30건 (canonical 6성분)
- **레보플록사신**(6): 레보건정250밀리그램·레보나정100/500밀리그램·레보박터정·레보사신정250밀리그램·레보스타정
- **메트포르민**(5): 그리코민서방정500밀리그램·글라비스정1000밀리그램·글로포민서방정·글루메트정·글루세라정500밀리그램
- **시프로플록사신**(5): 시프로투정250밀리그램·시프록스정·시프록신정·시프사신정250밀리그램·시플로뉴정250밀리그램
- **알렌드론산**(5): 알레드론정70mg·알렌다정·알렌산정70밀리그램·알렌스타정·알로네이트정
- **오메프라졸**(4): 셀트리온오메프라졸캡슐20밀리그램·아메졸캡슐·아주오메프라졸캡슐·애니시드캡슐
- **오플록사신**(5): 오플로정·오플록정100밀리그램·옥타신정·제뉴원오플록사신정·지엘오플록사신정100밀리그램
> (전부 단일성분·완제·경구·getItemDetail 원문확정. 전체 itemSeq 는 product_aliases[138:168] 및 `..._phase11_report.md` §4 참조.)

## 6. validator #114 옵션 A 갱신 (PM 승인)
- pre-incorporation(Phase 11): #114 = "batch5 는 incorporated=false". 반영하면 true → #114 FAIL(Phase 4/6/8/10 와 동일 충돌).
- **옵션 A 갱신**: #114 → "incorporated ∈ {false,true} 정합". true 의 **실제 반영 검증은 base+12(#112)**(alias∈aliases ∧ itemSeq∈whitelist[canonical]). garbage 는 #114 가 포착.
- 음성 테스트: garbage→#114 · 가짜 incorporated=true(alias 미존재)→#112 · 정상→PASS.

## 7. 검증 결과
| validator | 결과 |
|---|---|
| bulk candidate(incorporation-aware) | **PASS 92/92** (#16 alias_count==206·relation30 정합 · #112 batch5 incorporated 30 실제 반영검증 · #114 옵션 A) |
| v0.1 export | **PASS 12/12** |
| v0.2 export | **PASS 15/15** |
| v0.3 alias | **PASS 13/13** (신규 30 product_alias + verified 화이트리스트 #8 통과) |
| Type B suite | **PASS 7/7** |
| 음성 테스트 | **3/3** (#114 garbage · #112 가짜반영 · 정상 PASS) |

## 8. smoke test 결과
- **신규 30건 30/30 라이브 PASS**: 각 alias → resolveAliasIngredients 정확히 해당 canonical 1종, filterRelations 결과가 그 canonical relation 전부.
- **회귀 ALL PASS**: 타리비드→3 · 포사맥스→1 · 토렘→2 · 넥시움→0 · #/r/15 fail-safe · alias_count 206 · product 168 · verified 144/12.

## 9. 불변 / 안전
- relation **30 유지**, DATA_URL **불변**, v0.1/v0.2 export·앱·CI·batch1~4 AR **무변경**(md5 0-diff).
- 30건 외 alias 미추가 · itemSeq 중복 0 · 복합제/brand_core/에스오메프라졸/15행 0 · published/clinical_reviewed 봉인 · 제품 UI 없음 · 신규 tag 없음 · 수동 deploy 없음.
- batch 1~4 incorporated 110 그대로(queue approved 110→**140**). alias 는 검색 보조(guards.js 는 ingredient+product alias만 인덱싱).
- 반영 = ephemeral `/tmp/ms_incorporate_batch5.py`(전제/사후조건 assert 내장, **커밋 안 함**).

## 10. 🎯 v0.5 목표 200 도달 — 다음 방향
- **alias 206 라이브** = v0.5 목표(200) 달성·초과. nedrug 식약처 허가사항 기반 13성분 product/ingredient alias 검색 보조.
- **선택지(PM 판정)**:
  1. **v0.5 마감·릴리스 노트**(alias 206 동결, v0.5 태그/문서 정리).
  2. **batch 6 계속**: held 51(Phase 11) → 다음 30 자동(206→236), 추가 재수집으로 확장.
- 잔여 tier(미진행): 복합제 deferred(91 누적) · 표면형 개행 정제 · brand_core 14.

---
> 안전 원칙(불변): 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천이면 금지 / 칼륨 행 구매·제품링크 금지 / clinical 검수 전 published 금지 / validator PASS 없으면 배포 금지 / alias는 검색 보조이지 의학정보 아님 / alias로 relation 신규생성·풀확장 금지 / 15행·excluded·에스오메프라졸 alias 우회 금지 / 미검증 alias·itemSeq 금지 / 복합제·동일 제품(itemSeq) 중복 alias 금지 / incorporated 후보는 alias JSON 실제 반영 검증(가짜 승인 금지).
