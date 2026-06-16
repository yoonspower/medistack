# MediStack — Clinical Reviewer Package: F2 테트라사이클린 5건 (v1.4)

> **상태: reviewer 검토용 — NOT LIVE.** 본 패키지는 reviewer 가 F2 후보를 **verified_reference** 수준으로 승인할지 판단하기 위한 자료.
> reviewer note ≠ `clinical_reviewed=true`. 승인 후에도 천장은 verified_reference(published/clinical 전환 금지).
> 단일 소스: `data/review/f2_tetracycline_inventory_v1_4.json` · 드라이런 `data/review/f2_tetracycline_live_dryrun_v1_4.json`.

## 1. 범위
- **포함**: F2 테트라사이클린 reviewer-ready 후보 **5** (성분 3: 독시·미노·테트라사이클린).
- **제외**: 기존 live 60, pending 13(F1 18·페니실라민 2·theme map 6·칼륨 4·AT-FEX 1 — 별 트랙), F1/F3/F9/F10 등 다른 family.
- relation: Tetracycline계 × 철분/아연(영양소) · Al/Mg 함유 제산제(약물), mechanism=absorption, action=separation, evidence=moderate.

## 2. 안전 원칙
- **항생제 복용지시 아님** — "복용하세요/끊으세요" 류 없음. 참고정보(복용 시점 분리 안내 + 약사·의사 상담).
- **금속이온/제산제/우유·유제품 복용 권유 아님** — 보충/섭취 권장 문구 없음.
- **제품 추천 아님** — 제품/구매/제휴 링크·예시·필드 없음(`product_link_allowed=false`).
- **source quote 기반 참고정보** — 모든 카드는 허가사항 원문(병용투여) verbatim 인용에 근거.
- **reviewer note ≠ clinical_reviewed=true** — 승인 시에도 verified_reference 천장 유지.

## 3. family-level risk (테트라사이클린 특유)
1. **milk/calcium/mineral/antacid confusion** — 테트라사이클린은 우유·칼슘·철·아연·Al/Mg 제산제와 킬레이트. 본 batch 는 라벨 문장이 명시한 **철·아연(제제=영양소)** 과 **Al/Mg/Ca(제산제=약물)** 만 후보화 — 우유/유제품 counterpart 는 **생성 안 함**(보수적). reviewer 는 영양소(철분/아연) vs 약물(al_mg_antacid) 분류가 맞는지 확인.
2. **Al/Mg 제산제 vs Mg 영양제** — 제산제는 **약물(al_mg_antacid·id61 선례)**, Mg 영양제 아님. 카드는 약물 counterpart kicker 로 렌더.
3. **pediatric/pregnancy/bone/teeth context confusion** — 테트라사이클린 라벨에는 소아 치아착색·골형성 경고가 별도로 존재하나, **본 5건의 인용 문장은 흡수저하(absorption)만** 다룸. 그 문맥을 absorption relation 으로 오인하지 않았음(L6 pass). reviewer 는 계열 일반화 금지.
4. **direct instruction risk** — separation 은 "복용 시점 분리" 일반 안내로만 표현(구체 시간·명령형 없음).
5. **quote boundary risk** — 단일 라벨 문장 근거. 약물별 국내 품목(itemSeq) 매칭은 reviewer 확정 대상(공통 문장이라 품목 정합성 별도 확인 필요).
6. **계열 일반화 금지** — 5건은 reviewer-ready batch 기존 후보만. 신규 성분/관계 임의 생성 금지.

## 4. 후보별 카드 (verbatim quote 포함)

공통 인용 문장(허가사항 · 병용투여):
> "칼슘, 마그네슘, 알루미늄을 함유하는 제산제 또는 이들 양이온을 함유하는 다른 약물들, 철ㆍ아연을 함유하고 있는 제제와 약용탄, 카올린, 펙틴 또는 비스무트(bismuth)염 제제에 의해 테트라사이클린계 약물의 흡수가 저하되어 효과가 저하될 수 있다."
> (미노사이클린 RF-F2-0110 은 '비스무스(bismuth)' 철자 — 품목 라벨 verbatim)

---
### RF-F2-0105 · 독시사이클린 × Al/Mg 함유 제산제(약물)
- itemSeq 198000105 · al_mg_antacid(약물) · absorption/separation · moderate.
- **display**: "이 약은 Al/Mg 함유 제산제(약물)과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- **management**: "Al/Mg 함유 제산제(약물)과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
- **reviewer Q**: 독시사이클린은 live 에 ×칼슘/철분/마그네슘/아연 영양소 relation 보유 → 제산제(약물) relation 추가가 정보 가치 vs 중복? 국내 품목(itemSeq) 매칭 정확?

### RF-F2-0110 · 미노사이클린 × Al/Mg 함유 제산제(약물)
- itemSeq 198501028 · al_mg_antacid(약물) · absorption/separation · moderate.
- display/management: 독시사이클린과 동형(counterpart 명만 동일 패턴).
- **reviewer Q**: 미노사이클린도 ×칼슘/철분/마그네슘/아연 영양소 relation 보유 → overlap 판단 동일. '비스무스' 철자 변형(verbatim·문제 아님).

### RF-F2-0111 · 테트라사이클린 × 철분
- itemSeq 196000001 · 영양소(category null) · absorption/separation · moderate.
- **display**: "이 약은 철분과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
- **management**: "철분과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
- **reviewer Q**: 신규 성분·cleanly additive(live 독시/미노×철분 동일 렌더). 원문 '철ㆍ아연' = 철분 매핑 적정?

### RF-F2-0114 · 테트라사이클린 × 아연
- itemSeq 196000001 · 영양소(category null) · absorption/separation · moderate.
- display/management: 철분과 동형(아연).
- **reviewer Q**: 신규 성분·cleanly additive(live ×아연 렌더 동일).

### RF-F2-0115 · 테트라사이클린 × Al/Mg 함유 제산제(약물)
- itemSeq 196000001 · al_mg_antacid(약물) · absorption/separation · moderate.
- display/management: 독시사이클린과 동형(제산제).
- **reviewer Q**: 신규 성분·al_mg_antacid(id61 선례). 참고 — 테트라사이클린은 현재 ×칼슘/×마그네슘 영양소 relation 미보유(독시/미노 대비 완전성 격차) → 차후 확장 여부(본 scope 외).

## 5. reviewer decision table

| 결정 | scope | 예상 count | 비고 |
|---|---|---|---|
| approve all 5 | all5 | 60→65 | 기본 추천. overlap 결정 1건 명시 필요 |
| approve subset (nutrient) | nutrient2 / top2 | 60→62 | 테트라×철분/아연 — 최저 위험 선행 |
| approve subset (antacid) | antacid3 | 60→63 | 독시·미노·테트라×제산제 — overlap 판단 필요 |
| approve by ingredient | 독시/미노/테트라 | 단계별 | 성분별 PR |
| approve by counterpart 2-wave | nutrient2 → antacid3 | 60→62→65 | overlap 결정 격리 |
| hold selected | — | — | 독시/미노 antacid 보류 가능(overlap 우려 시) |

- F1 이후 통합 시 baseline 78 → all5 83.

## 6. reviewer note 템플릿 (gate `check_reviewer_note` 호환)
아래 항목을 **모두** 채워야 `--pm-approved --reviewer-note PATH` live 통합 게이트를 통과한다(SAMPLE/placeholder 토큰·미기입 시 거부).

```
검수자: <RPH 또는 PM 식별자> (PM 승인 근거 첨부)   검토일 <YYYY-MM-DD를 실제 날짜로>
승인(approved): F2 테트라사이클린 <scope> 후보를 verified_reference 노출로 승인.
scope: <all5 | nutrient2 | antacid3 | top2 | top3 | 명시 ids> 범위.
승인 candidate_id 전건: <해당 scope 의 candidate_id 전부 나열>.
grouping: <한 번에 통합 | by-counterpart subset | 성분별 ...>.
category 결정: Al/Mg 함유 제산제는 al_mg_antacid(약물 counterpart·id61 선례) — 마그네슘 영양제 아님.
독시/미노 nutrient-overlap 판단: <기존 ×칼슘/철분/마그네슘/아연 영양소 relation 대비 제산제(약물) relation 의 정보 가치/중복 결정>.
separation 간격(2~4시간) 카드 노출: <일반 '분리' 안내 유지 | 구체 시간 노출 결정>.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 금속이온·제산제·우유·유제품 복용 권유 없음.
```

- 게이트 거부 사유(요약): 빈 노트 · 승인 토큰 없음 · candidate_id 일부 누락(scope 전건 필요) · scope/grouping/al_mg_antacid/overlap/간격/verified_reference 누락 · reviewer 식별자 없음 · SAMPLE/placeholder · clinical_reviewed=true 승격 요구 · 제품 추천 허용 · 금속이온/제산제/우유 복용 권유 허용 · 소아/계열 일반화 허용.
- ⚠️ 본 패키지·노트는 source_confirmed 최종확정·식약처 승인·약사 검수 완료·법적 문제 없음을 의미하지 않는다.
