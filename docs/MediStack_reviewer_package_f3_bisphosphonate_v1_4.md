# MediStack — Clinical Reviewer Package: F3 비스포스포네이트 (v1.4)

> **상태: reviewer 검토용 — NOT LIVE.** 본 패키지는 reviewer 가 F3 후보를 **verified_reference** 수준으로 승인할지 판단하기 위한 자료.
> reviewer note ≠ `clinical_reviewed=true`. 승인 후에도 천장은 verified_reference(published/clinical 전환 금지).
> 단일 소스: `data/review/f3_bisphosphonate_inventory_v1_4.json` · 드라이런 `data/review/f3_bisphosphonate_live_dryrun_v1_4.json`.

## 0. 한눈에 — F3 는 통합 가능분이 1건뿐 (품질 게이트가 2건을 reviewer 로 되돌림)

| candidate | relation | 적대검증 | **F3 family 재검증(작업 C)** | 통합 |
|---|---|---|---|---|
| RF-F3-0147 | 이반드론산 × Al/Mg 함유 제산제(약물) | survives | **survives** | ✅ 가능(단 overlap 판단) |
| RF-F3-0148 | 에티드론산 × 칼슘 | survives_with_copy_change | **needs_review** ⬇ | ⛔ parse 확정 전 불가 |
| RF-F3-0149 | 에티드론산 × 철분 | survives_with_copy_change | **needs_review** ⬇ | ⛔ parse 확정 전 불가 |

**reverify counts: survives 1 · needs_review 2 · copy_change 0 · hold 0 · reject 0.** 통합 가능 = **1건(0147)**, 60→61.

## 1. 범위
- **포함**: F3 비스포스포네이트 reviewer-ready 후보 **3** (적대검증). family 재검증 후 **통합 가능 1**(0147)·**needs_review 2**(0148/0149).
- **제외**: 기존 live 60(비스포 포함 — §3), pending(F1 18·F2 5·페니실라민 2·theme 6·칼륨 4·AT-FEX 1·F4/F6/F9/F10), 타 family.
- relation: Bisphosphonate × Al/Mg 함유 제산제(약물), mechanism=absorption, action=separation, evidence=moderate.

## 2. 안전 원칙
- **비스포 복용지시 아님** — "복용하세요/끊으세요" 류 없음. 참고정보(복용 시점 분리 + 약사·의사 상담).
- **금속이온/제산제/우유·유제품 복용 권유 아님** — 보충/섭취 권장 문구 없음.
- **제품 추천 아님** — 제품/구매/제휴 링크·예시·필드 없음(`product_link_allowed=false`).
- **source quote 기반** — 카드는 허가사항 원문 verbatim 인용에 근거.
- **reviewer note ≠ clinical_reviewed=true** — 승인 시에도 verified_reference 천장 유지.
- **계열 일반화 금지** — 특히 에티드론산(§3.A)에 타 비스포 라벨 선례 적용 금지.

## 3. family-level risk (비스포스포네이트 특유) — **헤드라인 2건**

### A. 에티드론산(0148/0149) standalone parse — **needs_review 강등 사유**
에티드론산(다이놀정, itemSeq 198802519, **병용금기**) 인용 문장:
> "미네랄이 첨가된 비타민제나 칼슘, 아연, 철분, 마그네슘 또는 알루미늄이 고농도로 함유된 제산제" (원문 끝 '○ 파제트병' 섹션 헤딩 fragment 트림 = copy_change)

- **문법 분석**: "칼슘, 아연, 철분, 마그네슘 또는 알루미늄**이 고농도로 함유된 제산제**" → 양이온 목록은 **제산제의 함유 성분**(제산제에 결속). 즉 standalone 칼슘/철분 **보충제**가 아니라 **칼슘/철분 고함유 제산제**를 의미. 별도 standalone 항목은 "미네랄이 첨가된 비타민제"(종합비타민)뿐.
- **결론**: 에티드론산×**칼슘/철분(개별 영양소)** 분류는 본 인용 문장 근거가 **취약**(L3_standalone_nutrient_support fail). 추가로 이 인용은 병용금기 **목록 fragment**라 absorption 기전 동사("흡수 저하")가 없음(L5_direction fail) — 즉 quote 자체가 불완전.
- **live 선례는 적용 불가**: live 알렌드론산×칼슘(id29)·리세드론산×칼슘/철분(id40/49)·이반드론산×칼슘/철분(id41/51)은 **다른 약물 라벨**(포사맥스 등 '칼슘보충제' 명시)에 근거. 에티드론산에 그 선례를 적용하면 **계열 일반화(금지)**.
- **reviewer 결정 요청**: 에티드론산 라벨 전문에서 (i) standalone 칼슘/철분 흡수저하 근거를 확인하거나, (ii) "미네랄 첨가 비타민제"→종합비타민 counterpart 로 재매핑할지 확정. 확정 전까지 0148/0149 통합 불가.

### B. 이반드론산(0147) nutrient-overlap — **통합 가능하나 reviewer 가치 판단**
이반드론산(드로반정, itemSeq 201207007, **상호작용**) 인용 문장:
> "칼슘보조제, 제산제, 다가 양이온(알루미늄, 마그네슘, 철)을 포함한 경구투여 약물은 이 약의 흡수를 저해할 수 있다."

- 인용이 "제산제" + "알루미늄, 마그네슘"을 **명시** → al_mg_antacid(약물·id61 선례) 분류 **명확**(L2/L3 pass, 흡수 저해 동사 존재).
- **단, 이반드론산은 live 에 ×칼슘(id41)/철분(id51)/마그네슘(id52) 이미 존재.** 따라서 Al/Mg 제산제(약물) relation 추가는 **정보 가치(제산제 제품 맥락 명시) vs 중복**인지 reviewer 판단(id61·F2 독시/미노 선례). exact dup 아님(별도 counterpart). 카드는 약물 counterpart kicker 로 영양소와 구분.

### C. 기타
- **Al/Mg 제산제 vs Mg 영양제** — 제산제는 약물(al_mg_antacid), Mg 영양제 아님.
- **소아/골/치아 문맥** — 본 인용 문장에 없음(L6 pass). 비스포 골다공증 적응증 문맥을 absorption relation 으로 오인 금지.
- **direct instruction risk** — separation 은 일반 안내(구체 시간·명령형 없음).

## 4. 통합 가능 카드 (verbatim quote)

**RF-F3-0147 · 이반드론산 × Al/Mg 함유 제산제(약물)** — al_mg_antacid · absorption/separation · evidence moderate
- 출처: 식약처 허가사항(nedrug) / 드로반정150밀리그램(이반드론산나트륨일수화물, itemSeq 201207007) / 상호작용
- quote: "칼슘보조제, 제산제, 다가 양이온(알루미늄, 마그네슘, 철)을 포함한 경구투여 약물은 이 약의 흡수를 저해할 수 있다."
- display(앱): "이 약은 Al/Mg 함유 제산제(약물)과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- ⚠️ reviewer: 이반드론산 nutrient-overlap(§3.B) 판단 + 국내 품목(itemSeq) 매칭 확정.

## 5. needs_review 카드 (통합 보류 — reviewer parse 확정 대상)
- **RF-F3-0148 · 에티드론산 × 칼슘** — §3.A 참조. standalone 칼슘 근거 확정 전 보류.
- **RF-F3-0149 · 에티드론산 × 철분** — §3.A 참조. standalone 철분 근거 확정 전 보류.

## 6. decision table
| 항목 | 값 |
|---|---|
| 통합 가능 | 1 (RF-F3-0147) → 60→61 (id runtime max+1) |
| needs_review | 2 (RF-F3-0148/0149 에티드론산 parse) |
| 선행조건 | 0 (al_mg_antacid id61 렌더·v0.2 PASS) |
| full index/aliases | 자동 flip 0 · relation_card 1168/name_only 16412 불변(이반드론산 covered) · 에티드론산 조건부 latent 1 |
| F1 후 | 78→79(survives) | F1+F2 후 | 83→84(survives) |

## 7. reviewer-note (gate 호환 — 이 형식이어야 통합기 통과)
`integrate_f3_bisphosphonate_batch_v1_4.py --pm-approved --reviewer-note PATH --scope survives` 가 요구하는 항목:
```
검수자: <실명/RPH ID> (PM 승인 근거)  검토일: <YYYY-MM-DD 실제값>
승인(approved): F3 비스포스포네이트 survives 후보를 verified_reference 노출로 승인.
scope: survives 범위. 승인 candidate_id 전건: RF-F3-0147.
grouping: survives subset 한 번에 통합.
category 결정: Al/Mg 함유 제산제는 al_mg_antacid(약물 counterpart·id61 선례) — 마그네슘 영양제 아님.
이반드론산 nutrient-overlap 판단: 기존 ×칼슘/철분/마그네슘 영양소 relation 과 정보 중복 아닌 제산제 제품 맥락으로 추가 노출 승인.
separation 간격(예: 30분/2시간) 카드 노출: 일반 '분리' 안내 유지.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 금속이온·제산제·우유·유제품 복용 권유 없음.
에티드론산 0148/0149 standalone 칼슘/철분 parse 는 본 승인 대상 아님(needs_review 유지).
verified_reference 노출 동의.
```
게이트 거부: 빈/SAMPLE/placeholder · 승인/candidate/scope/grouping/al_mg_antacid/overlap/간격/verified_reference 누락 · clinical=true·제품추천·금속이온/제산제/우유 복용 권유·**에티드론산 standalone 계열 일반화** 허용 문구.
