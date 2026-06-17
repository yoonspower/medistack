# MediStack — F4/F6/F10 small-family bundle inventory (v1.4)

> 감사 인벤토리. 단일 소스 JSON: `data/review/f4_f6_f10_small_family_inventory_v1_4.json`. NOT LIVE.

## family
- **F4** Thyroid hormone × mineral/antacid (absorption)
- **F6** Acid-reducer (H2/PPI) × Fe/B12/antacid
- **F10** Azole antifungal × antacid (pH-dependent absorption)

각 family reviewer-ready(적대검증 survives/copy_change) **1건** → small-family bundle 3건 감사.

## 후보 표준화 + family 재검증(16 렌즈, refute-by-default)

| candidate | family | ingredient | counterpart | type/category | mech/action | itemSeq · source product | prev(adversarial) | **재검증** |
|---|---|---|---|---|---|---|---|---|
| RF-F4-0173 | F4 | 레보티록신 | 알루미늄 함유 제산제(약물) | drug/al_mg_antacid | absorption/separation | 197400278 · 씬지로이드정0.1mg | survives_with_copy_change | **survives_with_copy_change** |
| RF-F6-0201 | F6 | 에스오메프라졸 | 비타민B12 | nutrient/(없음) | depletion/monitoring | 201308928 · 낙소졸정(복합제) | survives | **survives_with_copy_change** |
| RF-F10-0275 | F10 | 케토코나졸 | Al/Mg 함유 제산제(약물) | drug/al_mg_antacid | absorption/separation | 199101243 · 더마졸정(수출용) | survives_with_copy_change | **needs_review** |

재검증 counts: survives 0 · survives_with_copy_change 2 · **needs_review 1** · hold 0 · reject 0 → **통합 가능 2**.

## 핵심 렌즈
- **L6_route_domestic_availability**(★0275 강등): mechanism=absorption + drug antacid 인데 full index 국내 oral 제품 0(외용 전용) → fail.
  - 레보티록신 17품목 전부 oral(정) → pass. 케토코나졸 10품목 전부 외용(액/크림) → **fail**.
- **L5_category_clarity**: antacid drug ⇒ al_mg_antacid + '약물' 표기 / nutrient ⇒ category 없음 + B12.
- **L8_no_dosing_detail_in_display**: 0275 quote 의 '2시간/콜라' 가 display 로 새지 않아야(id61 선례대로 strip).
- L1 source fidelity · L2 cooccurrence · L3 mechanism · L9 product/supplement · L10 live dup · L11 타 family overlap ·
  L12 forbidden · L13 consult tone(al_mg=약사/의사·B12=복약 상담/정기 진료) · L15 display 소아/골 비노출 · L16 enum.

## copy_change (multi-field display_reframe)
- **RF-F4-0173**: counterpart "Al/Mg 함유 제산제(약물)"→"알루미늄 함유 제산제(약물)" · display/management Al-only reframe(Mg 비단정·'효과 감소'→'흡수 지연/감소').
- **RF-F6-0201**: display/management → live PPI×B12 표준 템플릿(id13 정합).
- 무결성: 각 field 의 batch 원문 == 기록 original(위조 차단). live 무수정 — projected 에만 반영.

## F10 family context (reviewer-ready 3 밖 · 완결성 기록)
- **RF-F10-0276** 포사코나졸×Al/Mg제산제 — **hold**: quote 가 'H2 수용체 억제제'만 언급(제산제 미명시·주어 불일치) → al_mg_antacid 매핑 불가(acid_reducing_drug category 설계 트랙).
- **RF-F10-0277** 이트라코나졸×Al/Mg제산제 — **reject**: 이미 live(id61) duplicate_live.

## live 선례(선행조건 0)
- absorption/separation·al_mg_antacid: **id61 이트라코나졸×Al/Mg 제산제**(위산도 의존 흡수·display 가 콜라/2시간 dosing strip).
- depletion/monitoring·B12: **id12 메트포르민×B12** + PPI×B12 5건(id13 오메프라졸·32 라베프라졸·34 판토프라졸·36 란소프라졸·38 덱스란소프라졸).
- src 변경 불필요.
