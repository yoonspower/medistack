# MediStack — F3 비스포스포네이트 인벤토리 + family 재검증 (v1.4)

> NOT LIVE. 단일 소스 = `data/review/f3_bisphosphonate_inventory_v1_4.json`. 생성: `integrate_f3_bisphosphonate_batch_v1_4.py`(dry-run).

## 1. 후보 (적대검증 reviewer-ready 3 · audited 4)

| candidate | 성분 | counterpart | type | itemSeq / 품목 | section |
|---|---|---|---|---|---|
| RF-F3-0147 | 이반드론산 | Al/Mg 함유 제산제(약물) | drug(al_mg_antacid) | 201207007 / 드로반정150mg | 상호작용 |
| RF-F3-0148 | 에티드론산 | 칼슘 | nutrient | 198802519 / 다이놀정 | 병용금기 |
| RF-F3-0149 | 에티드론산 | 철분 | nutrient | 198802519 / 다이놀정 | 병용금기 |
| (audited, reviewer-ready 아님) RF-F3-0139 | 알렌드론산 | Al/Mg 제산제 | drug | 199800180 / 마빌정 | 병용투여 (generic '제산제'·칼슘만 명시→적대검증서 이미 needs_review) |

## 2. family 재검증 (작업 C · 14 렌즈 · refute-by-default)

| candidate | 적대검증 | **재검증 verdict** | 핵심 렌즈 |
|---|---|---|---|
| RF-F3-0147 | survives | **survives** | L2/L3 pass(제산제+Al/Mg 명시·흡수 저해 동사) |
| RF-F3-0148 | survives_with_copy_change | **needs_review** | L3_standalone_nutrient_support **fail**(칼슘이 '함유된 제산제'에 결속) · L5_direction **fail**(병용금기 fragment·기전 동사 없음) |
| RF-F3-0149 | survives_with_copy_change | **needs_review** | 동일(철분) |

**counts: survives 1 · survives_with_copy_change 0 · needs_review 2 · hold 0 · reject 0.**

핵심 family 렌즈 **L3_standalone_nutrient_support**: nutrient counterpart 토큰이 정규식 `(고농도로 )?함유(…)? 제산제` 앞쪽에만 등장하고(제산제 결속) standalone 단서(`{token}보충제`/`{token} 제제`/`{token} 함유 식품` 등)가 없으면 fail. 에티드론산 인용이 정확히 이 패턴 → 강등.

## 3. live 비스포스포네이트 컨텍스트 (dup/overlap 판단 근거)

| 성분 | live relations | F3 영향 |
|---|---|---|
| 알렌드론산 | ×칼슘(id29) | F3 후보 아님(0139 needs_review) |
| 리세드론산 | ×칼슘(id40)·철분(id49)·마그네슘(id50) | F3 후보 없음 |
| 이반드론산 | ×칼슘(id41)·철분(id51)·마그네슘(id52) | **0147 = ×Al/Mg제산제(약물) 추가 → overlap reviewer 판단(headline B)** |
| 에티드론산 | (live 없음·신규) | 0148/0149 needs_review(standalone parse) |

- **exact dup vs live: 0.** 이반드론산×al_mg_antacid 는 별도 counterpart(id61 선례)라 ×칼슘/철분/마그네슘(nutrient)과 중복 아님.
- **헤드라인 1(에티드론산 parse)** = §2 L3/L5. **헤드라인 2(이반드론산 overlap)** = 위 표 이반드론산 행.

## 4. 교훈 (family 재검증이 광역검증을 보완)
- F1: stray '1' 트림(RF-F1-0020). F2: 철→철 토큰 매핑. **F3: 에티드론산 인용의 cation→제산제 결속 + 병용금기 fragment(기전 동사 부재)** → 광역 적대검증이 survives_with_copy_change 로 통과시킨 2건을 needs_review 로 정정. family 재검증 없이 통합했으면 원문 근거 취약한 standalone nutrient relation 2건이 live 진입할 뻔.
