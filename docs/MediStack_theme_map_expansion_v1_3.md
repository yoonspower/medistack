# MediStack Theme Map Expansion (v1.3) — 신규 relation family 후보

> **상태: draft-only / review artifact. live 승격 0. schedule 무관.**
> 기존 theme map(`vfs.SEARCH_INGREDIENTS` 25개: 세팔로스포린10·코르티코스테로이드5·CA억제제1·루프3·치아지드유사3·갑상선2·FQ1)
> 반복 online run 이 **신규 0 으로 수렴**(run3: draft_eligible 3, 대부분 needs_review/hold) → 새 family 발굴이 필요.
> 이 문서는 그 결과물의 **단일 진실원**. 데이터: `data/review/theme_map_expansion_candidates_v1_3.json`(설계),
> `data/review/theme_map_source_check_results_v1_3.json`(SDK 확인), `data/drafts/theme_map_draft_batch_v1_3.json`(draft).

## 0. 한 줄 요약
국내 허가사항 직접근거가 **SDK 로 확인된** 신규 family 후보 **6건을 draft-only** 로 정리했다(승격 0). 1건은 hold(국내 단일성분 완제 없음), 6건은 needs_review/source_check/high-risk hold.

## 1. 신규 family (3종)
1. **fatsol_vitamin_absorption** — 지용성 비타민(A·D·E·K) 흡수저해. 지방분해효소 억제제(오르리스타트)·담즙산 결합 수지(콜레스티라민). 기존 absorption/separation 프레임에 정합.
2. **antacid_interaction 확장** — 경구 세팔로스포린 에스터 프로드러그(세프포독심·세프디토렌) × 위산 감소·중화 약물. id61(이트라코나졸) 트랙의 동류이나 기전이 pH 의존(↔ id61 cation chelation) — counterpart_category 정렬은 reviewer 판단.
3. **metal_chelation_absorption** — 페니실라민 × 철분·아연. 기존 FQ/테트라사이클린/비스포스포네이트 × 금속이온과 다른 약물.

## 2. source-confirmed draft 후보 (6건 — SDK 확인 완료, 라벨 직접근거)

| candidate_id | 약물 | counterpart | 기전/조치 | itemSeq | 라벨 근거(verbatim 일부) |
|---|---|---|---|---|---|
| TM-LIP-01 | 오르리스타트 | 지용성 비타민(A·D·E·K·베타카로틴) | absorption/separation | 200806047 (리피다운캡슐60mg) | "몇몇 지용성 비타민 및 베타카로틴의 흡수가 감소될 수 있으므로…비타민 보충제는 이 약 투여 최소 2시간 후…" |
| TM-LIP-02 | 콜레스티라민 | 지용성 비타민(A·D·K) | absorption/separation | 198800813 (보령퀘스트란현탁용산) | "담즙산과 결합하므로…비타민 A, D, K와 같은 지용성 비타민의 흡수를 저해할 수 있다" |
| TM-CEPH-AC-01 | 세프포독심프록세틸 | 위산 감소·중화 약물(제산제·H2) | absorption/separation | 199300168 (바난정) | "위장 내의 pH를 올리게 되는 약물(제산제, H2-길항제)은 생체이용률을 떨어뜨리고…" |
| TM-CEPH-AC-02 | 세프디토렌피복실 | 위산 감소·중화 약물(제산제·H2) | absorption/avoid_concomitant | 199500901 (보령메이액트정100mg) | "제산제나 위산을 감소시키는 다른 약물과 동시에 복용하는 것은 권장되지 않는다(흡수가 감소)" |
| TM-CHEL-01-FE | 페니실라민 | 철분 | absorption/separation | 198300142 (알타민캡슐250mg, 디-페니실라민) | "경구철제제(…황산철 등)…는 이 약의 흡수율을 저하…동시투여를 피한다" |
| TM-CHEL-01-ZN | 페니실라민 | 아연 | absorption/separation | 198300142 (동일) | "아연을 함유하는 경구제는 이 약의 효과를 감소…동시투여를 피한다" |

> 표의 라벨 인용은 **출처(원문)**. 사용자 노출 카피는 `theme_map_draft_batch_v1_3.json` 의 `display_text_ko_draft`/`management_copy_draft`(원문보다 강하지 않게, 보충 권유 없이 재작성).

### ⚠️ 핵심 안전 주의 (orlistat·cholestyramine)
허가사항이 **종합비타민 보충을 "권장"** 한다. MediStack 은 보충을 **권유하지 않는다**. 사용자 카피는
"흡수가 감소될 수 있다 + (보충제를 복용 중이라면) 복용 시점 분리 + 약사/의사 상담"까지만. 칼륨 보충 권유 금지 원칙과 동일.

## 3. hold / needs_review / source_check (7건)
| candidate_id | 약물 × counterpart | 상태 | 이유 |
|---|---|---|---|
| TM-CHEL-02 | 레보도파 × 철분 | **hold** | 국내 단일성분 완제 없음(마도파=+벤세라지드, 스타레보=+카르비도파, 대신레보도파=원료). 복합제 기전 복잡. |
| TM-LIP-03 | 콜레세벨람 × 지용성 비타민 | source_check_candidate(P2) | 동류이나 라벨 직접근거 미확인. 결합 선택성↑로 영향 약할 수 있음. 2차 확인 필요. |
| TM-CHEL-03 | 메틸도파 × 철분 | needs_review | 철염이 흡수 저하 가능하나 국내 완제·라벨 미확인. 임신 사용 약물 → 임신 카피 번짐 금지. |
| TM-B6-01 | 이소니아지드 × 비타민B6 | needs_review | depletion 방향은 안전하나 라벨/임상이 B6 병용 동반 → **보충 권유 오인 위험 큼**. copy 게이트 선결. |
| TM-HOLD-PHENYTOIN | 페니토인 × 엽산·비타민D | hold | 엽산↔페니토인 **양방향**(엽산이 약물농도↓) → 단순 depletion 오도. 신경계·임상판단. |
| TM-HOLD-MYCO | 마이코페놀레이트 × 제산제·철분 | hold | 이식 면역억제제·거부반응 위험·임상판단. clinical reviewer 트랙에서만. |
| TM-HOLD-LDOPA-B6 | 레보도파 × 비타민B6 | hold | 국내 유통 복합제(카르비도파)가 상호작용 무력화 → "B6 피하라" 카드는 오정보. |

### 재확인된 기존 high-risk hold(재제안 안 함)
항응고/항혈소판×비타민K(영구 금지)·항암×엽산/비타민D·정신건강×Mg/비타민D·경구피임×엽산·소아×비타민D·herbal·K-sparing×칼륨 상승(고칼륨혈증 방향·약-약)·statin×CoQ10(문헌)·H2×B12(label-missing)·SGLT2×Mg(방향 불확실). (`vfs.CARRIED` 42건 참조.)

## 4. source-check 방법론(재현 가능)
`scripts/sourcecheck_theme_map_expansion_v1_3.py` — online SDK-only(`medistack_sdk.NedrugClient`, namespace 캐시, 직접 HTTP 0), 후보당 ≤2 fetch.
교훈: **nedrug 검색은 product-name 매칭** — 성분명("오를리스타트")이 비어도 실제 철자("오르리스타트")·브랜드(리피다운)로 존재. exact-ingredient 필터가 완제를 거를 때는 확인된 itemSeq 직접 지정(`direct_itemseqs`). zero-result 를 곧장 no_domestic_product 로 단정하지 말 것.

## 5. 검증
- `scripts/validate_theme_map_expansion_v1_3.py` — schema/중복/live무중복/published·clinical false/forbidden/제품·제휴/itemSeq 실값/high-risk hold 차단/potassium·antacid 위생/**vitamin-K 항응고 차단·보충 권유 차단·약물/영양소 category 분리·adversarial verdict 강제**/cross-check (PASS, 17 검사군, 결함주입 9종 전건 탐지).
- `scripts/smoke_theme_map_draft_render_v1_3.py` — draft 카드 렌더·copy 안전·**chip/kicker(antacid=약물 표기·비타민K 항응고 차단)**·보충 권유 차단·제품 UI 부재·출처 표시 (PASS, 6 카드).

## 6. 적대검증 결과 (프롬프트 8 · 2026-06-16 · refute-by-default 8 렌즈)
정본 ledger = `data/review/theme_map_adversarial_verify_v1_3.json`. **6건 전부 survives**(3 survives / 3 survives_with_copy_change). source quote **6/6 라벨 verbatim 대조**(네트워크 0, 캐시).

| candidate | verdict | 반증→조치 |
|---|---|---|
| TM-LIP-01 오르리스타트 | survives_with_copy_change | source_quote 가 시점 문구를 압축/변형 → **라벨 verbatim 정정**('최소 2시간 전 또는 취침 시와 같이 이 약 투여 최소 2시간 후에 복용해야 한다') |
| TM-LIP-02 콜레스티라민 | survives | 비타민K 항응고 언급 0·엽산 미확장·콜레스티라민은 id57/58 source.pointer 의 binder(역방향·무충돌) |
| TM-CEPH-AC-01 세프포독심 | survives | 라벨이 제산제·H2 명시(PPI 미명시) → counterpart 그대로·category=acid_reducing_drug |
| TM-CEPH-AC-02 세프디토렌 | survives_with_copy_change | 라벨 '위산을 감소시키는 다른 약물'(광의) → counterpart 를 **PPI 포함 확장**('제산제·위산 감소 약물(H2 차단제·PPI 등)') |
| TM-CHEL-01-FE 페니실라민×철분 | survives | 라벨 '흡수율 저하' 명시 → absorption 정확 |
| TM-CHEL-01-ZN 페니실라민×아연 | survives_with_copy_change | 라벨이 아연엔 '효과 감소'만(흡수 미명시) → **mechanism=absorption 은 추론 플래그**·confidence high→moderate·user copy 는 '효과 감소'로 라벨 충실 |

### counterpart_category 정렬 결정(작업 G)
- **fat_soluble_vitamin** (nutrient_group): TM-LIP-01/02 — 그룹 표시 유지.
- **acid_reducing_drug** (antacid_drug): TM-CEPH-AC-01/02 — **신규 category 채택**. id61(이트라코나졸)의 `al_mg_antacid` 와 구분(세팔로스포린은 cation chelation 이 아닌 **pH 의존**·H2/PPI 포함). `antacid_h2_drug` 는 PPI 누락하므로 비채택. validator 가 acid-reducer 의 `al_mg_antacid` 사용을 **차단**(H2/PPI 를 Al/Mg 로 좁히지 못하게).
- **null category** (nutrient): TM-CHEL-01-FE/ZN — 기존 live 60 nutrient relation 이 전부 null 이라 동일 유지. `mineral_ion` 신규 category 불필요.

### 2차 source-check 결과(작업 H · `theme_map_source_check_round2_v1_3.json`) — 신규 draft 0
- **TM-LIP-03 콜레세벨람**: 콜레세벨람/염산염/웰콜 국내 검색 0 → **hold(미유통)**.
- **TM-CHEL-03 메틸도파**: 메틸도파/메칠도파/부광메칠도파/알도메트/수화물 국내 검색 0 → **hold(미유통·단종 추정)**.
- **TM-B6-01 이소니아지드**: 유한짓정(196200032)에 B6/피리독신 있으나 문맥이 **'말초신경병증 발생 시 피리독신 투여'(이상반응 치료 지시)** — depletion-monitoring relation 아님 → **hold**(소비자 카드 부적합·보충 권유 오인·clinical reviewer 트랙). raw=found 이나 adversarial_override=hold.

## 7. 다음 단계(전부 PM/clinical reviewer 게이트)
1. counterpart_category 최종 채택(acid_reducing_drug) + nutrient_group 단일 vs 분리 + ZN mechanism(absorption vs interaction) reviewer 확정.
2. 페니실라민 FE/ZN 다중 영양소 묶음 카드 여부·전문약 노출 가치.
3. **live 통합은 clinical reviewer note 후 별도 PR.** ~~harvester theme map 편입도 후속 PR(프롬프트 9).~~ → **편입 완료(아래 §8).**
4. 미유통 hold(콜레세벨람·메틸도파)는 국내 시판 시에만 재후보화. 이소니아지드 B6 는 clinical reviewer 전 대상 아님.

## 8. harvester 편입 (2026-06-16 · 프롬프트 9 · branch+PR · candidate-only)
신규 family 6건을 harvester 에 **candidate-only 로 편입**했다(branch `harvester-theme-map-v1.3`). **live 통합·schedule 활성화·자동 integrate 0.** 정본 절차 = `docs/MediStack_harvester_ops_v1_3.md` §14.
- **방식**: manual flag `--include-theme-map-expansion`(기본 비활성) + config-driven 격리 provider. flag 없으면 기존 78-후보 run 무변경(byte-동일).
- **단일 진실원**: `data/config/theme_map_seeds_v1_3.json`(읽기 전용 policy/pointer). provider(`scripts/theme_map_harvest_provider_v1_3.py`)가 draft batch/candidates/adversarial ledger 를 읽어 PM review queue(draft 6 + hold 7) 생성. SDK·네트워크 0.
- **신규 category 처리(review-level·src 무수정)**: acid_reducing_drug(세팔로 acid-reducer·id61 al_mg_antacid 구분) · fat_soluble_vitamin(지용성 비타민군). validator 가 약물/영양소 category 혼동·al_mg_antacid 축소·항응고 framing·보충 권유·제품 문구 차단.
- **runtime 산출물**(`data/harvest_queue/theme_map_*`)은 `.gitignore`(커밋 0). 커밋 = review summary `data/review/theme_map_harvest_incorporation_v1_3.json` 뿐.
- **검증**: `scripts/validate_harvester_theme_map_v1_3.py`(17 검사군+결함주입 9)·`scripts/smoke_harvester_theme_map_v1_3.py`(PM queue+6 카드)·guard flag run(보호셋 불변·write-scope·direct-http 0) PASS.
- **남은 일**: reviewer 가 §7-1·2 확정 → live 통합은 clinical reviewer note + 수동 단계 후 별도 PR(harvester 자동 승격 없음).
