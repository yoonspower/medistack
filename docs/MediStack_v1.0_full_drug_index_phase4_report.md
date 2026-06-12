# MediStack v1.0 — Full Drug Name Index Phase 4 확장 리포트

> 목표: "검색했는데 안 나오는 약" 체감 축소를 위해 full drug name index를 **1,000 → 5,000+** 로 확장.
> 원칙: relation/의학 정보 확장 0. relation 없는 약은 name_only(품목명 확인)만. 상호작용/영양소/제품/구매 정보 금지.
> 일자: 2026-06-12 수집 · 작업폴더 `/Users/mac/AI work/medistack` · 선행 커밋 `178b607`.

## 1. 수집 방법

- 도구: `scripts/collect_full_drug_name_index_sample.py --augment` (Phase 2 수집기 확장).
- **augment 모드(신규)**: 기존 1,000 출력(`data/full_drug_name_index_sample_v1_0.json`)을 파일에서 로드해
  **그대로 보존**(itemSeq/품목명/날짜 불변), 신규 name_only만 append. → "기존 1,000개 seed 유지" 충실.
- 성분 풀 확장: `DIVERSE_INGREDIENTS` **94 → 309** (base 94 + ext 215, 중복 0).
  - ext = 다양 클래스 상용 경구약(진통/항생/항진균/심혈관/당뇨/소화기/알레르기/호흡기/정신·신경/비뇨/통풍/골대사/인지/항혈전/안과).
  - **제외 유지(안전)**: 13 canonical 성분 · 에스오메프라졸 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄(relation 얽힘).
- 파라미터: `--target 5500 --per-cap 30 --max-pages 5 --sleep 0.15`.
- 수집원: nedrug `searchDrug`(식약처). 품목명/itemSeq/주성분/업체명만 채록(약학적 해석 없음).
- 필터(기존 동일): 수출용 · 원료 · 취소/취하 · 에스오메/넥시움/forbidden itemSeq · 13성분 · dup · relation pool 제외.

## 2. 기존 1,000개와의 차이

| 구분 | Phase 2 (1,000) | Phase 4 (5,500) | 차이 |
|---|---|---|---|
| total | 1,000 | **5,500** | +4,500 |
| relation_card | 558 | 558 | **0 (불변, alias pool 고정)** |
| name_only | 442 | **4,942** | +4,500 |
| 성분 풀 | 94 | 309 | +215 |
| 고유 성분 문자열(name_only) | — | 713 | — |
| 고유 제조사(name_only) | — | 237 | — |

- 기존 1,000 엔트리는 **바이트 단위 보존**(augment). 신규 4,500은 전량 name_only.
- relation_card는 alias pool(verified 545 + product 583 → 고유 558) 기반이라 **구조적으로 558 고정**. 이번에 미변경.

## 3. 최종 index 수

- **total = 5,500** (목표 5,000 floor 초과 · validator Phase 4 게이트 `total>=5,000` PASS).
- 파일: `data/full_drug_name_index_sample_v1_0.json` (2.71MB, indent=1) + `.csv` (5,500행).

## 4. covered_by_relation 수

- **558** (display_mode=relation_card, covered_by_relation=true, no_relation_notice_required=false).
- 전부 relation-covered pool itemSeq(날조 0). itemSeq∈pool 위반 0.

## 5. name_only 수

- **4,942** (display_mode=name_only, covered_by_relation=false, no_relation_notice_required=true).
- 전수 점검: 의학/제품 금지 필드 0 · 13 canonical 성분 0 · itemSeq∈pool 0 · eso/넥시움 0.

## 6. 제외 / 보류 수 (이번 신규 수집 기준)

| 사유 | 건수 |
|---|---|
| 수출용(export) | 1,188 |
| 원료 | 417 |
| 취소/취하 | 1,349 |
| 에스오메프라졸/넥시움/forbidden | 11 |
| 13 canonical 성분(relation 트랙) | 206 |
| relation pool 중복 | 111 |
| 일반 중복(dup) | 786 |
| **kept(신규 name_only)** | **4,500** |
| rows_seen(총 파싱 행) | 8,568 |
| ingredients_searched | 287 / 309 (cap 4,500 도달로 조기 종료) |
| 네트워크 실패(ing_fail) | **0** |

- 보류(manual review): 없음. 애매/위험 항목은 위 필터에서 즉시 제외(report에 사유 집계).

## 7. 중복 제거 수

- relation pool 중복 111 + 일반 중복 786 = **897 제외**. 최종 itemSeq **5,500 전부 고유**(중복 0).

## 8. 대표 샘플 30개 (name_only)

| # | 품목명 | 주성분 | 제조사 |
|---|---|---|---|
| 1 | 건트라셋서방정 | 아세트아미노펜/트라마돌염산염 | 건일바이오팜 |
| 2 | 넬악손주2그램(세프트리악손나트륨수화물) | 세프트리악손나트륨수화물 | 한국넬슨제약 |
| 3 | 리피듀정(심바스타틴) | 심바스타틴 | 에스케이케미칼 |
| 4 | 리도펜연질캡슐(이부프로펜) | 이부프로펜 | 메디카코리아 |
| 5 | 로나펜정(록소프로펜나트륨수화물) | 록소프로펜나트륨수화물 | 이든파마 |
| 6 | 비알클래건조시럽250mg/5mL | 클래리트로마이신제피과립 | 보령바이오파마 |
| 7 | 노마로크정5밀리그램(암로디핀베실산염) | 암로디핀베실산염 | 하나제약 |
| 8 | 세비루카정5/20밀리그램 | 올메사르탄메독소밀/암로디핀베실산염 | 대웅바이오 |
| 9 | 뉴토젯정10/20밀리그램 | 아토르바스타틴칼슘삼수화물/에제티미브 | 대한뉴팜 |
| 10 | 판타릴정20밀리그램 | 판토프라졸나트륨세스키히드레이트 | 아주약품 |
| 11 | 이토라제정(이토프리드염산염) | 이토프리드염산염 | 환인제약 |
| 12 | 다시디엠정10/100밀리그램 | 시타글립틴인산염수화물/다파글리플로진 | 동화약품 |
| 13 | 알레펙정60밀리그램(펙소페나딘염산염) | 펙소페나딘염산염 | 이든파마 |
| 14 | 레드로피정(레보드로프로피진) | 레보드로프로피진 | 셀트리온제약 |
| 15 | 가바론틴캡슐300밀리그램(가바펜틴) | 가바펜틴 | 씨엘팜 |
| 16 | 삼성탐스로신서방정 | 탐스로신염산염 | 삼성제약 |
| 17 | 롱맥스정5밀리그램(타다라필) | 타다라필 | 케이엠에스제약 |
| 18 | 메가페손정(에페리손염산염) | 에페리손염산염 | 엘앤씨바이오 |
| 19 | 세파난건조시럽(세프포독심프록세틸) | 세프포독심프록세틸 | 제이더블유신약 |
| 20 | 노바론크림(테르비나핀염산염) | 테르비나핀염산염 | 한솔신약 |
| 21 | 바스핀지속정(펠로디핀) | 펠로디핀 | 한국휴텍스제약 |
| 22 | 미카클로정40/12.5밀리그램 | 텔미사르탄/클로르탈리돈 | 유한양행 |
| 23 | 마겐정(알마게이트) | 알마게이트 | 시어스제약 |
| 24 | 겔포스엘현탁액 | 인산알루미늄겔/수산화마그네슘/시메티콘 | 보령 |
| 25 | 파나벤정(케토티펜푸마르산염) | 케토티펜푸마르산염 | 한국넬슨제약 |
| 26 | 풀미코트터부헬러200㎍/dose | 부데소니드(미분화) | 한국아스트라제네카 |
| 27 | 파마멀타자핀정15밀리그램 | 미르타자핀 | 한국파마 |
| 28 | 리스달정3밀리그램(리스페리돈) | 리스페리돈 | 한림제약 |
| 29 | 트루패스정4밀리그램(실로도신) | 실로도신 | 제이더블유중외제약 |
| 30 | 유니페릭정(페북소스타트) | 페북소스타트 | 한국유니온제약 |

## 9. validator 결과

- `validate_full_drug_name_index.py`: **PASS (30/30)** — Phase 4 게이트 `total>=5,000` 포함.
  구조/필드/enum/일관성/name_only 순도/relation_card pool 정합/eso 제외/교차 불변 전수 통과.
- `--selftest`: **PASS** (음성 11종 포착, 정상 base clean).
- 신규 CI 배선: `deploy.yml`·`validate.yml`에 full index validator 단계 추가(라이브 name_only 데이터 보호).

## 10. smoke / QA 결과

- `smoke_search_regression_v1_0.py`: **PASS** (relation_card / combo / HCTZ / empty / surface / degrade / name_only / 배선 불변).
  - fixture 갱신: `name_only_index_size` 442→**4942**, 노바스크 신규 커버, 이부프로펜/아세트아미노펜/암로디핀 깊이 강화.
  - ground-truth(실측 node guards): 게보린 3 · 이부프로펜 15 · 아세트아미노펜 12 · 암로디핀 30 · 노바스크 3.
  - **STOP 불변**: 넥시움 0 · 에스오메프라졸 name_only 0 · asdfqwer 0 · 타이레놀 0.
- 전종 회귀: v0.1 12/12 · v0.2 15/15 · v0.3 16/16 · surface 5/5 · TypeB 7/7 · combo 9/9 · combo AR 13/13 ·
  combo approved-ready 13/13 · HCTZ disclosure PASS · alias regression 7건 · bulk 152/152 · full index 30/30 — **전부 PASS**.
- 로컬 브라우저 QA(localhost:8011, 5,500 데이터):
  - **노바스크 → name_only 카드**: "참고 정보 없음" + "품목명 확인 3건" + 3종(품목명+제조사). #ms-results 내 href/복합제/칼륨 **0**.
  - **게보린 → name_only**: "참고 정보 없음"·"품목명 확인 3건".
  - **타리비드 → relation_card**: "조건 일치 3건" 오플록사신×칼슘/철분/마그네슘 + alias 안내(클릭형 행).
  - **미카르디스플러스 → HCTZ combo**: "복합제"·"칼륨 주의"·"히드로클로로티아지드 성분 기준"·"반대 방향" 반전고지 유지.
  - **asdfqwer/넥시움 → 결과 없음**(empty). 콘솔 에러 0.

## 11. 기존 alias / relation 불변 확인 (validator 교차 체크 PASS)

- alias_count **621** · product_aliases **583** · ingredient_aliases **38** · verified_item_seqs **545/13** · relations **30**.
- DATA_URL `./data/medistack_v0.2_beta_export.json` 불변 · published=false · clinical_reviewed=false 봉인.
- `data/medistack_v0.3_aliases.json` / relation export / candidate queue / data export **미변경**.

## 12. ⚠️ PM 판단 필요 — name_only "칼륨" salt-form 항목 (139건, 유지 결정)

- name_only 4,942 중 품목명/주성분에 "칼륨" 포함 **139건** 발견.
- 전수 확인 결과 **전부 약물의 염(salt) 짝이온**: 클라불란산칼륨(오구멘틴류 항생제 32) · 로사르탄칼륨/피마사르탄칼륨/
  아질사르탄칼륨(ARB 혈압약) · 글리시리진산이칼륨 · 비스무트시트르산염칼륨 등.
  **standalone 칼륨 보충제(염화칼륨·구연산칼륨 등) = 0건.**
- **유지 결정 근거**: (1) 정상 처방 약품(항생제/혈압약)이며 제외 시 PM 목표(검색 커버리지)에 역행, (2) name_only는
  링크/상호작용/영양소 정보가 전혀 없음(QA에서 href/칼륨 0 확인), (3) 기존 라이브 442(로사르탄 등 동일 필터)와 일관,
  (4) "칼륨 제품링크 금지"·"칼륨보존이뇨제 복합제 차단" 규칙은 **링크/relation** 대상이며 name_only 품목명 표시는 비해당.
- 참고: 텔미사르탄/클로르탈리돈 등 thiazide-유사 복합제도 name_only로 표시되나, **칼륨 주의는 미표시**(설계상 name_only는
  의학 판단 없음, "약사·의사 상담" 고지로 안내). HCTZ 칼륨 반전고지는 relation_card 경로에만 존재(불변).
- **PM이 제외를 원하면**: collect 스크립트에 칼륨 salt 제외 필터를 추가해 재수집 가능(별도 지시). 현재는 **유지**.

## 13. 10,000 확장 시 조건·위험 (요약 — 상세: `MediStack_v1.0_full_drug_index_10k_plan.md`)

- 조건: augment 재사용 + 성분 풀 309→~500 + per-cap/max-pages 상향 + (필요 시) itemSeq/제형 보완 수집축.
- 위험: 수집 천장(성분 부분일치 한계) · nedrug 부하 · 편중 · **클라이언트 로드 성능(10k≈4~5MB, fetch+buildNameOnlyIndex 측정 필수)** · name_only 순도 · 제외 누출.
- **10,000 실제 확장은 성능 사전 측정 + 별도 PM 승인 후 착수.** 본 Phase 4는 5,500에서 종료.
