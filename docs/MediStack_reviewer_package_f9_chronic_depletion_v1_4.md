# MediStack — Clinical Reviewer Package: F9 만성복용 depletion (v1.4)

> **상태: reviewer 검토용 — NOT LIVE.** 본 패키지는 reviewer 가 F9 후보를 **verified_reference** 수준으로 승인할지 판단하기 위한 자료.
> reviewer note ≠ `clinical_reviewed=true`. 승인 후에도 천장은 verified_reference(published/clinical 전환 금지).
> 단일 소스: `data/review/f9_chronic_depletion_inventory_v1_4.json` · 드라이런 `data/review/f9_chronic_depletion_live_dryrun_v1_4.json`.

## 0. 한눈에 — 통합 가능 7건 (품질 게이트가 1건을 reviewer 로 되돌림 + 비타민D 3건 카피 보수화)

| candidate | relation | 적대검증 | **F9 family 재검증(작업 C)** | 통합 |
|---|---|---|---|---|
| RF-F9-0269 | 설파살라진 × 엽산 | survives | **survives** | ✅ 가능 |
| RF-F9-0272 | 트리메토프림 × 엽산 | survives | **survives** | ✅ 가능 |
| RF-F9-0246 | 카르바마제핀 × 비타민D | survives_with_copy_change | **survives** | ✅ 가능 |
| RF-F9-0242 | 페니토인 × 엽산 | survives | **survives_with_copy_change** (quote hygiene) | ✅ 가능 |
| RF-F9-0252 | 페노바르비탈 × 비타민D | survives | **survives_with_copy_change** (display reframe) | ✅ 가능 |
| RF-F9-0243 | 페니토인 × 비타민D | survives | **survives_with_copy_change** (display reframe) | ✅ 가능 |
| RF-F9-0255 | 프리미돈 × 비타민D | survives | **survives_with_copy_change** (display reframe) | ✅ 가능 |
| RF-F9-0245 | 카르바마제핀 × 엽산 | survives_with_copy_change | **needs_review** ⬇ | ⛔ 저신호 열거 — 근거 확정 전 불가 |

**reverify counts: survives 3 · copy_change 4 · needs_review 1 · hold 0 · reject 0.** 통합 가능 = **7건**, 60→67.

## 1. 범위
- **포함**: F9 만성복용 depletion reviewer-ready 후보 **8** (적대검증). family 재검증 후 **통합 가능 7**·**needs_review 1**(0245).
- **제외**: 기존 live 60(F9 성분/영양소 미존재 — §3), pending(F1 18·F2 5·F3 1·F4/F6/F10·페니실라민 2·theme 6·칼륨 4·AT-FEX 1), 타 family.
- relation: 약물 × **엽산/비타민D**, mechanism=**depletion**, action=**monitoring**, evidence=moderate. counterpart_category 없음(영양소).
- **렌더 선례**: live 메트포르민×비타민B12(id12, depletion/monitoring) — 동일 shape, src 변경 0.

## 2. 안전 원칙
- **복용지시 아님** — "복용하세요/검사받으세요/투여하세요" 류 없음. 참고/모니터링(걱정되면 약사·의사 상담).
- **엽산/비타민D 보충 권유 아님** — 영양제 복용/섭취 권장 문구 없음(라벨 quote 의 '보충한다'는 카드에 비노출).
- **제품 추천 아님** — 제품/구매/제휴 링크·예시·필드 없음(`product_link_allowed=false`).
- **모니터링 톤** — 검사 지시·처방 단정 아님("정기적인 확인이 필요할 수 있습니다 · 상담").
- **소아/임신/골/치아 알람어 카드 비노출** — 라벨 quote 에는 구루병/골연화증/치아형성부전이 있으나(특히 비타민D 3건) **display 에는 비노출**.
- **계열 일반화 금지** — 효소유도제(페노바르비탈/페니토인/프리미돈/카르바마제핀) 라벨 개별 근거로만. family 일반화로 draft 생성 금지.

## 3. family-level 발견 (만성 depletion 특유) — **헤드라인 3건**

### A. 카르바마제핀×엽산(0245) 저신호 이상반응 열거 — **needs_review 강등 사유**
카르바마제핀(itemSeq 198401121, **병용투여** 섹션) 인용:
> "드물게 백혈구 증가, 임파절 장애, 엽산 결핍증"

- **분석**: '엽산 결핍증'은 혈액계 **이상반응 열거** 안의 bare 항목. (a) 흡수/대사/길항 **기전 동사 없음**, (b) '혈청엽산치 저하' 같은 **level-direction 없음**(질환명만), (c) **'드물게'** 빈도. → **F9 저신호 이상반응 열거**(adversarial 의 옥스카르바제핀 강등 패턴과 동형) → 모니터링 카드 근거 취약.
- **coverage 유지**: 카르바마제핀은 ×비타민D(0246, '25-hydroxy-콜레칼시페롤의 감소' 명시)로 통합 가능 → 약물 누락 아님.
- **reviewer 결정 요청**: 카르바마제핀 라벨 전문에서 **엽산 저하 standalone 근거**(혈청엽산치 저하·항엽산 기전)를 확정하거나 needs_review 유지. 확정 전까지 0245 통합 불가.

### B. 항전간제×비타민D(0252/0243/0255) — nutrient=remedy → **copy_change(display reframe)**
페노바르비탈/페니토인/프리미돈 × 비타민D 인용(공통 패턴):
> "근골격계 : 연용중/연용에 의해 구루병, 골연화증, 치아형성부전 ... ALP·혈청칼슘·무기인의 저하 ... 감량 또는 비타민 D를 섭취/투여한다."

- **분석**: 라벨은 **연용(장기)** 골대사 이상 + 비타민D **섭취/투여(remedy)**를 적시하나, **비타민D 자체의 '수치 저하'는 명시 안 함**(혈청칼슘·무기인 저하만). 효소유도제 → vitD 이화 촉진 → 골연화증 기전은 교과서적이고 라벨이 osteomalacia + vitD 관리를 직접 기술하므로 **관계는 유효**.
- **copy_change**: display 의 "비타민D 수치 변화"는 source 보다 강함 → **"비타민D와 관련된 허가사항 주의 문구"**로 reframe(측정치 단정 제거 + 구루병/골연화증 알람어 비노출). 카드는 보수적 모니터링 톤.
- **reviewer 확인**: 카드가 골질환 알람으로 읽히지 않는지 + '장기/연용' framing 이 라벨 근거와 일치하는지.

### C. 페니토인×엽산(0242) quote hygiene — **copy_change(quote-trim)**
페니토인(itemSeq 197000104, 주의사항) 인용 끝에 stray 섹션 마커 ' 1' 존재:
> "기타 : ... 다모, 혈청엽산치 저하가 나타날 수 있다(경구제에 한함.)~~. 1~~" → ' 1' 트림(F1 stray '1' 동형).

- '혈청엽산치 **저하**' 명시(level-direction 있음)라 관계 자체는 strong. 트림은 hygiene(원문 verbatim 부분문자열).

### D. 기타
- **트리메토프림×엽산(0272)** — '폴산대사길항제'(DHFR 억제) + '폴산결핍을 악화' 명시. 인용이 폴산결핍 특수군 caution 이나 **길항 기전은 약물 본연**(코트리목사졸 포함)이라 일반화 아님.
- **설파살라진×엽산(0269)** — '엽산의 흡수가 저하 ... 엽산결핍증' 명시(흡수 기전). 인용은 '병용투여 시'이나 설파살라진은 만성 IBD/RA 약 → '장기 복용' framing 일치. reviewer 확인 권장.
- **special-population 일반화 차단** — 임신/소아 한정 근거였던 페노바르비탈/프리미돈 ×엽산은 adversarial 에서 이미 needs_review(본 8건 아님).

## 4. 통합 가능 카드 (verbatim quote)

**RF-F9-0269 · 설파살라진 × 엽산** — depletion/monitoring · evidence moderate · survives
- 출처: 식약처 허가사항(nedrug) / 설파살라진(itemSeq 199803482) / 상호작용
- quote: "엽산과 병용투여 시 엽산의 흡수가 저하되고, 거대적혈모구증, 범혈구감소를 초래하는 엽산결핍증을 일으킬 수 있으므로 엽산결핍증이 의심되는 경우에는 엽산을 보충한다."
- display(앱): "이 약을 장기간 복용할 때 엽산 수치 변화와 관련된 허가사항 문구가 있습니다. 증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요."

**RF-F9-0272 · 트리메토프림 × 엽산** — depletion/monitoring · survives
- 출처: 트리메토프림(itemSeq 197000049) / 주의사항
- quote: "폴산결핍 또는 대사이상 환자(이미 위적출술을 받은 환자, 다른 폴산대사길항제를 투여받고 있는 환자, 선천성 폴산대사이상 환자 등)(폴산결핍을 악화시켜 거대적아구성빈혈을 일으킬 수 있다.)"
- display(앱): "이 약을 장기간 복용할 때 엽산 수치 변화와 관련된 허가사항 문구가 있습니다. 증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요."

**RF-F9-0246 · 카르바마제핀 × 비타민D** — depletion/monitoring · survives
- 출처: 카르바마제핀(itemSeq 198401121) / 병용투여
- quote: "혈장 칼슘과 혈중25-hydroxy-콜레칼시페롤의 감소와 같은 골대사 장애로 인한 골연화증 및 골다공증"
- display(앱): "이 약을 장기간 복용할 때 비타민D 수치 변화와 관련된 허가사항 문구가 있습니다. 증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요." (25-OH-vitD 감소 명시 → '수치 변화' 유지)

**RF-F9-0242 · 페니토인 × 엽산** — depletion/monitoring · survives_with_copy_change(quote-trim)
- 출처: 페니토인(itemSeq 197000104) / 주의사항
- quote(트림 후): "기타 : 결절성 동맥주위염, 다발성 관절증, 과혈당, 드물게 발열, 갑상샘기능검사치(혈청 T3, T4치 등)이상, 다모, 혈청엽산치 저하가 나타날 수 있다(경구제에 한함.)"
- display(앱): "이 약을 장기간 복용할 때 엽산 수치 변화와 관련된 허가사항 문구가 있습니다. 증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요."

**RF-F9-0252 · 페노바르비탈 × 비타민D** — depletion/monitoring · survives_with_copy_change(display reframe)
- 출처: 페노바르비탈(itemSeq 197000212) / 주의사항
- quote: "근골격계 : 연용중에 구루병, 골연화증, 치아형성부전 등이 나타날 수 있으므로 관찰을 충분히 하고 이상(혈청 ALP, 혈청칼슘, 무기인의 저하)이 나타나는 경우에는 감량 또는 비타민 D를 섭취하는 등 주의한다."
- display(앱·reframe): "이 약을 장기간 복용할 때 비타민D와 관련된 허가사항 주의 문구가 있습니다. 증상이 걱정되면 약사 또는 의사와 상담하세요."

**RF-F9-0243 · 페니토인 × 비타민D** — depletion/monitoring · survives_with_copy_change(display reframe)
- 출처: 페니토인(itemSeq 197000104) / 주의사항
- quote: "근골격계 : 연용에 의해 구루병, 골연화증, 치아형성부전 등이 나타날 수 있으므로 관찰을 충분히 하고 이상(ALP, 혈청 칼슘 저하 및 무기인 저하 등)이 나타나는 경우에는 감량 또는 비타민D를 투여하는 등 적절히 조치한다."
- display(앱·reframe): "이 약을 장기간 복용할 때 비타민D와 관련된 허가사항 주의 문구가 있습니다. 증상이 걱정되면 약사 또는 의사와 상담하세요."

**RF-F9-0255 · 프리미돈 × 비타민D** — depletion/monitoring · survives_with_copy_change(display reframe)
- 출처: 프리미돈(itemSeq 198000160) / 주의사항
- quote: "근골격계 : 연용시 구루병, 골연화증, 치조골형성부전이 나타날 수 있으므로 이상(ALP, 혈청칼슘, 무기질저하 등)이 나타나면 감량 또는 비타민 D를 투여하는 등 적절한 처치를 한다."
- display(앱·reframe): "이 약을 장기간 복용할 때 비타민D와 관련된 허가사항 주의 문구가 있습니다. 증상이 걱정되면 약사 또는 의사와 상담하세요."

> 공통 management(앱): "정기적인 확인이 필요할 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."

## 5. needs_review 카드 (통합 보류 — reviewer 근거 확정 대상)
- **RF-F9-0245 · 카르바마제핀 × 엽산** — §3.A 참조. 저신호 이상반응 열거('드물게...엽산 결핍증'). standalone 엽산 저하 근거 확정 전 보류. (카르바마제핀은 ×비타민D 0246 으로 coverage 유지.)

## 6. decision table
| 항목 | 값 |
|---|---|
| 통합 가능 | 7 (survives 3 + copy_change 4) → 60→67 (id runtime max+1) |
| needs_review | 1 (RF-F9-0245 카르바마제핀×엽산 저신호 열거) |
| counterpart 분리 | 엽산 3(설파살라진·트리메토프림·페니토인) · 비타민D 4(카르바마제핀·페노바르비탈·페니토인·프리미돈) |
| 선행조건 | 0 (depletion/monitoring 렌더 = 메트포르민×B12 선례·v0.2 PASS) |
| full index/aliases | 자동 flip 0 · relation_card 1168/name_only 16412 불변 · 통합분 alias-enrich 시 조건부 latent ≤18(별도) |
| F1+F2+F3 후(84) | 84→91(integrable) · 조건부(0245) 84→92 |

## 7. reviewer-note (gate 호환 — 이 형식이어야 통합기 통과)
`integrate_f9_chronic_depletion_batch_v1_4.py --pm-approved --reviewer-note PATH --scope integrable` 가 요구하는 항목:
```
검수자: <실명/RPH ID> (PM 승인 근거)  검토일: <YYYY-MM-DD 실제값>
승인(approved): F9 만성복용 depletion integrable 후보를 verified_reference 노출로 승인.
scope: integrable 범위. 승인 candidate_id 전건: RF-F9-0269, RF-F9-0272, RF-F9-0246, RF-F9-0242, RF-F9-0252, RF-F9-0243, RF-F9-0255.
grouping: integrable subset 한 번에 통합(또는 by-nutrient 2-wave: 엽산 3 → 비타민D 4).
영양소 대상: 엽산·비타민D(영양소 — 약물 category 없음). 모니터링 톤(참고정보·정기 확인 문의, 검사 지시 아님·처방 아님) 유지.
장기/연용 복용 framing: 라벨 연용 근거와 일치 확인(설파살라진은 '병용투여 시'이나 만성 IBD/RA 약 맥락).
카르바마제핀×엽산(저신호 이상반응 열거)은 needs_review — 본 승인 대상 아님.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 엽산·비타민D 보충 권유 없음.
verified_reference 노출 동의.
```
게이트 거부: 빈/SAMPLE/placeholder · 승인/candidate/scope/grouping/영양소/모니터링톤/장기framing/0245 ack/verified_reference 누락 · clinical=true·제품추천·엽산/비타민D 보충 권유·검사/처방 지시·소아/골/치아·family/효소유도제 **계열 일반화** 허용 문구.
