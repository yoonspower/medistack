# MediStack — F9 만성복용 depletion Inventory (v1.4)

> NOT LIVE / no-live-write. 단일 소스: `data/review/f9_chronic_depletion_inventory_v1_4.json`.
> 생성: `scripts/integrate_f9_chronic_depletion_batch_v1_4.py`(dry-run) · 검증: `validate_f9_chronic_depletion_dryrun_v1_4.py`.

## family
**F9 Chronic-use depletion × 엽산/비타민D** — mechanism=depletion · recommended_action=monitoring · counterpart_type=nutrient(약물 category 없음).
F1/F2/F3(흡수 차단·separation)와 달리 **만성/장기복용에 따른 결핍·수치 변화 모니터링** 계열. live 렌더 선례 = 메트포르민×비타민B12(id12).

## 감사 8건 → family 재검증 결과

| candidate | drug | nutrient | itemSeq | section | 적대검증 | **재검증** | 비고 |
|---|---|---|---|---|---|---|---|
| RF-F9-0269 | 설파살라진 | 엽산 | 199803482 | 상호작용 | survives | **survives** | '엽산의 흡수가 저하...엽산결핍증' 명시 |
| RF-F9-0272 | 트리메토프림 | 엽산 | 197000049 | 주의사항 | survives | **survives** | '폴산결핍을 악화'+폴산대사길항제(DHFR) |
| RF-F9-0246 | 카르바마제핀 | 비타민D | 198401121 | 병용투여 | copy_change | **survives** | '25-hydroxy-콜레칼시페롤의 감소' 명시 |
| RF-F9-0242 | 페니토인 | 엽산 | 197000104 | 주의사항 | survives | **copy_change** | '혈청엽산치 저하' 명시 · quote 끝 stray ' 1' 트림 |
| RF-F9-0252 | 페노바르비탈 | 비타민D | 197000212 | 주의사항 | survives | **copy_change** | 연용 골연화증+비타민D 섭취(remedy) → display reframe |
| RF-F9-0243 | 페니토인 | 비타민D | 197000104 | 주의사항 | survives | **copy_change** | 연용 골연화증+비타민D 투여(remedy) → display reframe |
| RF-F9-0255 | 프리미돈 | 비타민D | 198000160 | 주의사항 | survives | **copy_change** | 연용 골연화증+비타민D 투여(remedy) → display reframe |
| RF-F9-0245 | 카르바마제핀 | 엽산 | 198401121 | 병용투여 | copy_change | **needs_review ⬇** | '드물게...엽산 결핍증' 저신호 이상반응 열거 |

**reverify counts: survives 3 · survives_with_copy_change 4 · needs_review 1 · hold 0 · reject 0.**
- **통합 가능 = 7** (survives 3 + copy_change 4) → 60→67.
- ingredients(통합 가능): 설파살라진·트리메토프림·카르바마제핀·페노바르비탈·페니토인·프리미돈 (6종).
- counterpart 분리: 엽산 3(0269·0272·0242) · 비타민D 4(0246·0252·0243·0255).

## family 재검증 렌즈(16, refute-by-default) — 핵심
- **L3_nutrient_depletion_support**: nutrient 토큰 인근 저하/감소/결핍(direct) **또는** 연용+섭취/투여(remedy framing). remedy-only 면 copy_change.
- **L4_not_low_signal_enumeration**(★ 0245 강등): '드물게' 등 빈도 부사 + 기전 동사 없음 + level-direction 없음 + remedy framing 없음 → fail.
- **L15_display_no_pediatric_bone**: display(카드)에 소아/구루병/골연화증/치아 알람어 비노출(라벨 quote 에는 허용).
- 그 외: source fidelity·direct co-occurrence·depletion direction·special-population 일반화·quote boundary·복용/검사/처방 지시·제품/보충·live dup·타 family overlap·금칙어·상담 톤·항응고/비타민K·영양소 counterpart.

## copy_change 2종
- **quote_trim**(0242): source_quote 끝 stray ' 1' 트림 — cleaned 는 original_full 의 verbatim 부분문자열(위조 차단).
- **display_reframe**(0252·0243·0255): "비타민D 수치 변화" → "비타민D와 관련된 허가사항 주의 문구"(측정치 단정·골질환 알람어 제거). 관계 유효(효소유도제 vitD depletion).

## 안전 플래그(전건)
published=false · clinical_reviewed=false · reviewed_by 공란 · product_link_allowed=false · potassium_safety_card=false · requires_clinical_review=false · live_integration_forbidden=true.
> 통합 가능 = 자동 적대검증 + F9 family 재검증 통과를 의미하며 임상 검수 완료·식약처 승인·법적 문제 없음 을 의미하지 않는다.
