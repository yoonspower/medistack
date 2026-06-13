# MediStack v1.0 — 10k Full Drug Index Handoff

> 다음 세션(AI/사람)이 자기완결적으로 이어받기 위한 핸드오프. 상세는
> `MediStack_v1.0_full_drug_index_10k_stability_report.md` + `..._10k_plan.md` + `CLAUDE.md`.
> 작성일: 2026-06-13.

## 현재 상태 (라이브)

- **full drug name index 10,000** = relation_card 558 + name_only 9,442. name_only = 품목명 확인만(의학정보 0).
- 앱 배선(Phase 3) 그대로: data.js `loadFullIndex` fail-soft → guards.js `buildNameOnlyIndex`/`searchNameOnly`
  → app.js 3상태 라우팅(relation_card / name_only / empty). **src/app UX 미변경**(이번 확장은 데이터+검증만).
- 데이터: `data/full_drug_name_index_sample_v1_0.json`(4.79MB, md5 `5fb8ee96…`) + `.csv`(10,000 rows).
- 성능: gzip 278KB · 모바일 로드 ~58ms · 검색 ≤0.31ms. **20k까지 성능 여유**(외삽 검증).

## 종단 불변 (변경 금지)

alias_count 621 · product_aliases 583 · ingredient_aliases 38 · verified_item_seqs 545/13 · relations 30 ·
DATA_URL `./data/medistack_v0.2_beta_export.json` · export md5 `401b097a` · published=false · clinical_reviewed=false.
**name_only에 상호작용/영양소/제품/구매/제휴/관리 필드 절대 금지**(검증기 `FORBIDDEN_NAMEONLY_FIELDS` 강제).
제외 유지: 13 canonical · 에스오메프라졸/넥시움 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄.

## 재현 / 재실행

```bash
# 확장(augment): 기존 보존 + 신규 name_only 추가. target=현재총수 면 no-op.
python3 scripts/collect_full_drug_name_index_sample.py --augment --target 10000 \
    --per-cap 45 --max-pages 7 --checked-at 2026-06-13 --sleep 0.2
# 검증(필수)
python3 scripts/validate_full_drug_name_index.py data/full_drug_name_index_sample_v1_0.json   # 31/31
python3 scripts/validate_potassium_name_only_policy.py data/full_drug_name_index_sample_v1_0.json  # 8/8
python3 scripts/smoke_search_regression_v1_0.py            # A~H PASS
# 성능(리포트용, CI 하드게이트 아님)
python3 scripts/measure_full_index_performance.py data/full_drug_name_index_sample_v1_0.json
```

CI(`deploy.yml` validate job + `validate.yml`)가 main push마다 full-index + potassium validator 실행 → 게이트.
성능 측정은 CI 하드게이트 아님(리포트 권장). 검증기 게이트: `target_total>=10000 → total>=10000`(Phase 5).

## 20k 확장 시 (다음 트랙, 별도 PM 승인)

1. `DIVERSE_INGREDIENTS_EXT3` 추가(485 → ~700): 미수록 치료군 더 보강. **수집 천장 주의** — searchDrug
   부분일치만으로 +10,000 신규는 어려울 수 있음. 양 미달 시 **억지 충족 금지·중단 보고**(plan §4-1).
2. 필요 시 보완 수집축(getItemDetail/제형/업체). 단 품목명/itemSeq 중심, 약학 해석 금지.
3. 성능: 20k 외삽 gzip ~556KB·모바일 ~115ms(임계 내). 30k+는 재측정 후 §4-4 대응(지연 로드/분할) 검토.
4. `validate_full_drug_name_index.py`에 `target_total>=20000 → total>=20000` 게이트 추가(Phase 5와 동형).
5. smoke fixture `name_only_index_size`·`data_basis` 갱신. **넥시움/에스오메/asdfqwer=0 불변 유지.**

## 함정 / 주의

- **collect 스크립트는 nedrug 실수집**(네트워크 필수). 환경에 네트워크 없으면 `--no-network`는 name_only 생략(확장 불가).
- Python stdout 버퍼링 → 장시간 수집은 진행률 안 보임(시작/종료만). background 권장.
- **augment는 출력 파일을 seed로 재사용** → 재실행 시 누적(idempotent-ish). 잘못되면 `git checkout data/full_drug_name_index_sample_v1_0.json`로 복구.
- 일부 품목명에 nedrug 공식명 줄바꿈(`{브랜드}\n(주성분)`) — 검색(normalized)·표시(HTML 병합) 무영향. 정규화 말 것(의미 변경 위험).
- potassium 검증기는 `total==10000`/`name_only==9442` sanity 상수 핀 — 확장 시 함께 갱신.
- `scripts/__pycache__/` 커밋 금지. **수동 deploy·무단 tag 금지**(PAT push만, main push가 deploy 트리거).

## 재개 트리거

- "메디스택 20k" → 20k 확장(위 절차, 별도 승인 게이트).
- "메디스택 clinical reviewer" → reviewer 트랙(published/clinical 봉인 해제는 reviewer 확보 후).
- "메디스택 v1.1 문서화" → 본 10k 확장+안정화를 v1.1-beta로 정리(태그는 PM 승인 시).
