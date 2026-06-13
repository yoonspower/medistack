# MediStack v1.1-beta — Release Readiness (안정판 마감 판정)

> 작성일: 2026-06-13. v1.1-beta 안정판 마감 판정 문서. full drug name index **10,000 → 17,580**(20k 시도 후 공급 천장) 확정값을 v1.1 기준선으로 굳히는 release readiness 판정.
> **문서만 작성**(데이터·CSV·alias·relation·export·src·validator 로직 무변경). 운영 인계 = 동반 문서 `MediStack_v1.1_handoff.md`. 확장 경위 상세 = `MediStack_v1.1_20k_expansion_gate.md` §7.

---

## 1. v1.1-beta 기준선

| 항목 | 값 |
|---|---|
| latest commit | `cac9e03` Expand full drug index to 17,580 (20k attempt, supply ceiling) + 본 마감 docs 커밋 |
| full drug name index | **17,580** (relation_card 558 + name_only 17,022) |
| full index md5 | `654d3e859e4a10213c0fa132094e2bfb` |
| target_total / target_attempted | **17,580 / 20,000** (천장 — 위장 라벨 없음) |
| alias_count | **621** (product 583 + ingredient 38) |
| verified_item_seqs | **545 entries / 13 canonical** |
| relations | **30** (+ excluded_v0_1 1, 렌더 금지) |
| DATA_URL | `./data/medistack_v0.2_beta_export.json` (불변) |
| export md5 | `401b097a1bd812b6da983b7f3dfc6d20` (불변) |
| alias md5 | `03fb21378da3c4520667350e03130866` (불변) |
| published / clinical_reviewed | **false / false** (봉인 · 천장 = verified_reference) |
| live | `https://yoonspower.github.io/medistack` HTTP 200 (site + 3 data files) |
| 누적 태그 | v0.1/v0.2/v0.3/v0.5/v0.6/v0.7/v0.8/v1.0-beta · **v0.9·Phase2~6 무태그** |

v1.1-beta = "데이터를 무리하게 더 쌓는 버전"이 아니라 **"검색 체감 커버리지를 17,580까지 확장한 뒤, 공급 천장에서 품질을 보존하고 정직하게 굳힌 버전."** 17,580은 *"20k 실패"가 아니라 "20k 시도 후 공급 천장에 따른 품질 보존 확정값"* 이다.

---

## 2. 17,580 확정 경위 (20,000 목표 → 공급 천장)

PM 20k 승인 → gate(`MediStack_v1.1_20k_expansion_gate.md`) 준수 실행 → **17,580 도달에서 공급 천장**(force-fill 회피).

| 단계 | per-cap / max-pages | 결과 | 증분 |
|---|---|---|---|
| seed (v1.0 / 10k) | — | 10,000 (rc 558 + name_only 9,442) | — |
| **pass 1** | 45 / 12 | 10,000 → **14,471** | **+4,471** |
| **pass 2** (resumable) | 80 / 25 | 14,471 → **17,580** | **+3,109** |
| 누적 name_only | — | 9,442 → **17,022** | **+7,580** |

- **20,000까지 2,420 부족.** 억지로 채우지 않음.
- **천장 근거**: pass 2 `rows_seen 30,096` 중 `excl_dup 16,829` = **중복률 56%**. 같은 성분의 깊은 페이지가 이미 수집된 품목을 재출현시킴 → 더 깊은 grinding 은 force-fill(gate §2 금지). 신규 성분(EXT4) 추가는 합법 경로지만 성분이 점점 희귀(저빈도)해져 20k 도달 비용 대비 효익이 낮음 → **PM 판정으로 17,580 확정.** `capped_at_target=false`(20k cap 미도달 = 천장).
- **방법**: 성분 풀 485 → **696**(`DIVERSE_INGREDIENTS_EXT3` 211종: 지혈·편두통 triptan·구충·종양 경구·HIV/HCV/CMV·마취/근이완·호르몬·추가 외용/점안/이비인후·정신/신경·항부정맥·면역/류마티스·추가 NSAID). **4-shard 병렬 수집**(`collect_full_drug_name_index_sample.py --shard I/K --seed --out --progress` + `merge_full_index_shards.py`) — 단일 스트림 대비 대폭 단축, 서버 부하 문제 없음(2-pass 통틀어 `ing_fail` 1~2 = 전송 블립).

> 메타 기록: `target_total=17,580`, `target_attempted=20,000`, `expansion_note`(천장 사유). 검증기 Phase 6 게이트(`target>=20000 → total>=20000`)는 target 17,580 이라 **미발동**, Phase 5 게이트(`>=10000`)는 통과.

---

## 3. 품질 지표 (천장이지 결함 아님)

| 지표 | 10k (Phase 5) | **17,580 (Phase 6)** | 판정 |
|---|---|---|---|
| 최대 단일 성분 비율 | 0.90% | **1.175%** | 편중 미미(< Phase 4 1.21%) |
| 고유 성분 수 | — | **2,213** | 폭넓은 분산 |
| 제조사 수 | — | **420** | — |
| name_only 의학필드 누수 | 0 | **0** | 구조적 미반입(11키 단일 셋) |
| potassium blocked_standalone | 0 | **0** | 안전(allowed 589 / manual_review 44 비차단) |
| 원본 10,000 prefix | — | **byte-identical 보존** | seed 무손실 |
| relation_card | 558 | **558** | 고정(verified itemSeq) |
| name_only | 9,442 | **17,022** | 신규 +7,580 |

- name_only 엔트리는 `item_seq / item_name / normalized_item_name / ingredient_name / company_name / covered_by_relation / display_mode / no_relation_notice_required / source / source_method / source_checked_at` **11개 키만** (전 17,580 엔트리 단일 키셋). 상호작용·영양소·복용·제품·구매·제휴 필드 **구조적으로 없음** — `buildNameOnlyIndex`가 item_seq/이름/정규화/회사명만 복사하므로 있어도 버려짐.

---

## 4. 성능 지표 (17,580, 실측 · gate 임계 내)

| 지표 | 17,580 실측 | 임계 | 판정 |
|---|---|---|---|
| JSON 원본 | 8.47MB (8,877,997B) | — | — |
| **gzip 전송**(Pages) | **497.71KB** (509,658B) | < 1.43MB | ✅ |
| JSON.parse 중앙값 | 21.39ms | — | — |
| **buildNameOnlyIndex** | 4.17ms | < 100ms | ✅ |
| 초기 로드(parse+build) 데스크톱 | 25.56ms | — | — |
| 저사양 모바일 추정(×4) | **~102ms** | 체감 임계 내 | ✅ |
| **searchNameOnly** 최악(전체스캔) | **0.566ms** | < 5ms | ✅ |
| CSV(배포 비반입) | 3.92MB / 17,580행 | — | 데이터 산출물 |

재현: `python3 scripts/measure_full_index_performance.py data/full_drug_name_index_sample_v1_0.json`. 원본 JSON 은 크지만(품목명 반복) **gzip ~17배 압축** → 전송·체감 부담 작음. 검색은 normalized 사전 1회 + 상한 30 → 선형이어도 sub-ms.

> **향후 20k/30k 확장 시**: gzip 외삽 ~566KB(20k)는 여전히 임계 내지만, 30k+ 또는 임계 초과 신호 발생 시 압축/분할 로딩(plan §B) 검토.

---

## 5. validator / smoke 현황 (전종 PASS)

```
full_drug_name_index ... 31/31  (+ selftest PASS · Phase 6 게이트 조건부 미발동)
potassium_name_only .....  8/8   (blocked_standalone 0 · allowed 589 · manual_review 44 · + selftest PASS)
v0.1 export ............. 12/12  v0.2 export ............ 15/15
v0.3 aliases(REAL 621) .. 16/16  surface forms ..........  5/5
TypeB suite ............  7/7    v0.3 combo suite .......  9/9
combo AR suite ......... 13/13   combo approved_ready ... 13/13
bulk candidates ........ 152/152
smoke_alias_regression .  PASS(7) smoke_hctz_disclosure .. PASS
smoke_search_regression_v1_0 ... PASS (A~H · relation_card/combo/HCTZ/empty/surface/degrade/name_only/배선 불변)
```

- full index validator: `target_total=17,580` 이라 Phase 6 게이트(20k 조건부)는 미발동, Phase 5(>=10000) 통과. 불변값·금지필드 전부 PASS.
- potassium: standalone 칼륨보충제 차단 0건, name_only 금지필드 0, 검사대상 = allowed + manual_review(blocked 0).
- CI 게이트(deploy.yml) = v0.1/v0.2/v0.3/surface + full-index + potassium. smoke 3종은 커밋된 수동 회귀.

---

## 6. 라이브 QA 결과 (실측)

라이브 데이터 3종 **전부 live md5 == local md5**(full `654d3e85` / export `401b097a` / alias `03fb2137`) → 검색 표면 전체 byte-identical → 로컬 smoke(PASS)가 라이브에 그대로 성립. 추가로 실제 `guards.js`로 라이브 fetch 데이터 직접 검색:

| 검색어 | 결과 | 경로 |
|---|---|---|
| 게보린 | **name_only 3** (게보린브이정 등) | name_only |
| 노바스크 | **name_only 3** (노바스크정10밀리그램 등) | name_only |
| 타이레놀 | **name_only 1** (타이레놀콜드-에스정) | name_only · **Phase 6 신규 커버** |
| 이부프로펜 | name_only 30 (상한) | name_only |
| 아세트아미노펜 | name_only 30 (상한) | name_only |
| 트라넥삼산 | name_only 14 | name_only |
| 수마트립탄 | name_only 7 | name_only |
| 벤지다민 / 미녹시딜 | name_only 12 / 30 | name_only |
| 타리비드 | **relation_card 3** (오플록사신) | relation_card |
| 포사맥스 / 토렘 | relation_card 1 / 2 | relation_card |
| 미카르디스플러스정40/12.5밀리그램 | relation_card 2 + **HCTZ 칼륨 반전 고지** | relation_card + combo |
| 넥시움 / 에스오메프라졸 | **0** (index 제외) | empty |
| asdfqwer | **0** | empty |

- name_only 카드는 비클릭 정보카드("참고 정보 없음 · 품목명 확인 · 상담") — 의학 판단/상호작용/제품 링크 없음(render smoke 확인).
- 넥시움·에스오메프라졸 = full index 에서 제외(relation id16×Mg 는 별도 live, name_only 무관) → 0 불변.

---

## 7. 법적 / 의학적 안전선 (불변)

- **참고 정보 베타** — 진단·처방·복약지시 아님. 모든 상세에 `disclaimers.common` 표시.
- **천장 = verified_reference** — `clinical_reviewed`/`published` 전환은 외부 면허 검수자 확보 전까지 봉인.
- **relation 30 유지** · **alias JSON 621 유지** · **DATA_URL 유지** · **data export 불변**(md5 `401b097a`).
- **relation 없는 약 = name_only 만 표시.** name_only 에 상호작용/영양소/복용지도/제품/구매/제휴 표시 금지(검색 보조이지 의학 정보 아님).
- **칼륨** — salt-form 을 보충제로 취급하지 않음 · 제품 링크 금지 · standalone 칼륨보충제 blocklist validator 유지 · 복합제(HCTZ)는 칼륨 반전 고지 동반.
- **에스오메프라졸 / 15행(id15×B12) 재편입 금지**(id16×Mg 정상 live · 혼동 주의) · **칼륨보존이뇨제 복합제 영구 차단**(HCTZ 외 복합제 basis 금지).
- 제외 유지: 13 canonical · 에스오메프라졸/넥시움 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄.

---

## 8. v1.1-beta tag 생성 판정

**판정: tag-ready.** 본 마감 문서 커밋(release readiness + handoff + release notes)이 포함된 **최종 HEAD** 에 `v1.1-beta` annotated tag 생성.

근거:
- 전 validator(11종)·smoke(3종) PASS · 불변 수치 전수 일치 · 봉인 유지 · live HTTP 200 + 3-file md5 일치 · Actions/deploy success.
- 안정판 정의 충족: 17,580 확정(force-fill 없음·byte-identical seed 보존), 의학정보 무확장, 회귀 가드 정비.
- pending 변경 없음(working tree clean, `scripts/__pycache__` untracked 만).

태그: `git tag -a v1.1-beta -m "v1.1-beta: full index 17,580 supply-ceiling stable snapshot"` (annotated) — main push 자동 deploy 와 무관, **태그 push 는 deploy 미발동**. 태그 생성 후 코드/데이터 추가 수정 금지.

> 다음 세션 인계 = `MediStack_v1.1_handoff.md` · 확장 경위 = `MediStack_v1.1_20k_expansion_gate.md` §7.

---

> **안전 원칙(불변):** 원문에 없으면 노출 금지 / 원문보다 강하면 금지 / 복용량·제품추천 금지 / 칼륨 제품링크 금지 / clinical 검수 전 published 금지 / validator·smoke PASS 없으면 배포 금지 / alias·full index는 검색 보조이지 의학 정보 아님 / relation 신규·풀 확장 금지 / name_only 의학정보 부착 금지 / 15행·에스오메프라졸 우회 금지 / 칼륨보존이뇨제 복합제 영구 차단 / 복합제는 부분정보 고지 동반(HCTZ는 칼륨 반전 고지) / 수동 deploy·무단 tag 금지.
