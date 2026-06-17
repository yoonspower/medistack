# MediStack — F4/F6/F10 small-family bundle reviewer package (v1.4)

> **NOT LIVE / reviewer-gated.** 단일 소스: `data/review/f4_f6_f10_small_family_inventory_v1_4.json` +
> `data/review/f4_f6_f10_small_family_live_dryrun_v1_4.json`. 생성/검증:
> `integrate_f4_f6_f10_small_family_batch_v1_4.py`(dry-run) · `validate_…` · `test_…reviewer_note_gate_…` · `smoke_…`.
> live 승격은 **별도 PM 승인 + clinical reviewer note + 별도 PR** 전까지 금지(published/clinical_reviewed=false 유지).

## §0. 요약 — 통합 가능 2 (60→62)

| 항목 | 값 |
|---|---|
| audited (reviewer-ready) | **3** (각 family 1: RF-F4-0173 · RF-F6-0201 · RF-F10-0275) |
| survives | 0 |
| survives_with_copy_change | **2** (RF-F4-0173 · RF-F6-0201) |
| needs_review | **1** (RF-F10-0275) |
| hold / reject | 0 / 0 (reviewer-ready 3 기준) |
| **통합 가능(integrable)** | **2** = F4 1 + F6 1 + F10 0 → **60→62** |
| split | al_mg_antacid 1(F4) + 비타민B12(nutrient) 1(F6) |
| ingredients (integrable) | 레보티록신 · 에스오메프라졸 |
| counterparts | 알루미늄 함유 제산제(약물·al_mg_antacid) · 비타민B12(nutrient) |
| F10 family context | 0276 hold(H2-blocker 주어 불일치) · 0277 reject(=live id61 중복) |

**id 배정**: runtime max+1(현 live max 61) → 62·63. F1/F2/F3/F9 먼저 통합되면 자동 조정.

## §1. source fidelity 요약 — 헤드라인 3

### ① RF-F10-0275 케토코나졸×제산제 — **route/availability 강등(needs_review)** ★family-specific catch
- 소스: **더마졸정(케토코나졸)(수출용)** itemSeq 199101243 — oral tablet, 그러나 **export-only(수출용)**.
- full index 국내 케토코나졸 **10품목 전부 외용**(나졸액/니조랄액/니트나졸크림 등 — 액/크림/외용액). **국내 oral 제품 0.**
- 경구 흡수 의존(제산제→위산분비↓→흡수↓) relation 을 ingredient(케토코나졸)에 붙이면 **외용 제품에 경구 상호작용 카드 오부착**.
- 광역 10-lens 의 L8(formulation/route)은 *소스가 tablet* 이라 pass 했으나, family 재검증의
  **L6_route_domestic_availability**(full index 형태 분류)가 국내 oral 0 → **fail → needs_review**.
- live 선례 id61(이트라코나졸×Al/Mg 제산제)은 동일 mechanism 이나 **국내 제품** 사용 → 케토코나졸과 구분.
- **reviewer 결정 사항**: (a) 국내 oral 케토코나졸 존재 여부 확인, (b) formulation-scoping(경구 한정 카드) 도입 여부,
  (c) 수출용 source 수용 여부. 셋 중 해소 시 통합 가능(60→63).

### ② RF-F4-0173 레보티록신×제산제 — **aluminum-only copy_change**
- 소스: 씬지로이드정0.1밀리그램(레보티록신나트륨수화물) itemSeq 197400278. quote: "콜레스티라민, 철분제제,
  **알루미늄** 함유 제산제와 병용투여시 이 약의 흡수가 지연 또는 감소될 수 있으므로 투여간격에 주의하며 신중히 투여한다."
- 라벨은 **알루미늄** 함유 제산제만 명시(Mg 미명시). al_mg_antacid category/display 는 Mg 도 포함 → display '마그네슘' 단정은 **source 보다 강함**.
- **copy_change(display_reframe)**: counterpart/display 를 '알루미늄 함유 제산제(약물)'로 좁히고 Mg 비단정 + '효과 감소'→'흡수 지연/감소'(라벨 충실).
  category bucket(al_mg_antacid)은 id61 선례대로 유지.
- ⚠️ **live id61(이트라코나졸)도 수산화알루미늄→'Al/Mg 함유 제산제' 일반화** — 동일 latent 이슈를 reviewer 에 surface.
- **reviewer 결정**: al_mg_antacid bucket 재사용 vs 'Al 함유 제산제' 한정 표기.

### ③ RF-F6-0201 에스오메프라졸×B12 — **PPI×B12 톤 정합 copy_change**
- 소스: 낙소졸정500/20밀리그램(나프록센,에스오메프라졸) itemSeq 201308928 — **복합제**(quote 가 에스오메프라졸 명시).
  quote: "에스오메프라졸은 저위산증 또는 무위산증으로 인한 비타민 B12(시아노코발라민)의 흡수를 감소시킬 수 있으므로, 장기간 치료에서 …충분한 주의가 요구된다."
- 에스오메프라졸=오메프라졸(id13 live)의 **S-거울상** → PPI×B12 5건(id13/32/34/36/38) + 메트포르민(id12) live depletion/monitoring 계열에 합류.
- **copy_change(display_reframe)**: draft('수치 변화와 관련된 문구') → **live PPI×B12 표준 템플릿**(아래 §4) 으로 정합(측정치 단정 회피·장기복용+상태확인 조건 보존).
- **reviewer 결정**: (a) 복합제(낙소졸) 대신 단일성분 에스오메프라졸 라벨로 근거 보강 가능 여부, (b) evidence_level 확정.

## §2. decision cards (통합 가능 2 + needs_review 1)

| candidate | relation | mech/action | category | verdict | display(요약) |
|---|---|---|---|---|---|
| RF-F4-0173 | 레보티록신 × 알루미늄 함유 제산제(약물) | absorption/separation | al_mg_antacid | copy_change | "…알루미늄 함유 제산제(약물)와 함께 복용할 때 약물 흡수가 지연되거나 감소…복용 시점 분리…약사 또는 의사에게 확인" |
| RF-F6-0201 | 에스오메프라졸 × 비타민B12 | depletion/monitoring | (없음·영양소) | copy_change | "에스오메프라졸을(를) 장기간 복용하는 경우 비타민 B12 상태에 영향이 있을 수 있다는 보고가 있어, 상태 확인이 필요할 수 있습니다." |
| RF-F10-0275 | 케토코나졸 × Al/Mg 함유 제산제(약물) | absorption/separation | al_mg_antacid | **needs_review** | (카드 미생성 — route/availability) |

## §3. 통합 가능 2건 display/management 전문 (verbatim, 카드 렌더용)

**RF-F4-0173 레보티록신 × 알루미늄 함유 제산제(약물)** — absorption/separation/al_mg_antacid · evidence moderate
- display_text_ko: `이 약은 알루미늄 함유 제산제(약물)와 함께 복용할 때 약물 흡수가 지연되거나 감소될 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점 분리에 대해 약사 또는 의사에게 확인하세요.`
- management_ko: `알루미늄 함유 제산제(약물)와는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요.`
- ✔ Mg 비단정 ✔ 구체 시간·용량 없음 ✔ "안전/치료/처방/추천" 없음.

**RF-F6-0201 에스오메프라졸 × 비타민B12** — depletion/monitoring · evidence moderate (live PPI×B12 템플릿 = id13)
- display_text_ko: `에스오메프라졸을(를) 장기간 복용하는 경우 비타민 B12 상태에 영향이 있을 수 있다는 보고가 있어, 상태 확인이 필요할 수 있습니다.`
- management_ko: `장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다.`
- ✔ '수치 변화' 단정 회피 ✔ 측정치 단정 없음 ✔ 보충 권유 없음.

## §4. needs_review 후보 재검색 지침 (RF-F10-0275)
- 국내 oral 케토코나졸 품목 직접 조회(있으면 그 itemSeq 의 허가사항 상호작용 재확인).
- 없으면: (a) relation 을 **경구 formulation-scoped** 로 한정하는 메커니즘 도입 후 재평가, 또는 (b) 외용 전용이면 **reject/hold**.
- 0275 의 quote '콜라/2시간' dosing 은 어떤 경우에도 display 비노출(id61 선례).

## §5. live 통합 전 필수 PM 판단
1. RF-F4-0173: al_mg_antacid bucket 재사용 vs Al 한정 표기. (live id61 동일 latent 확인.)
2. RF-F6-0201: 복합제 source 수용 vs 단일성분 라벨 보강. evidence_level 확정.
3. RF-F10-0275: 통합 제외 유지(route/availability) — reviewer 가 국내 oral 존재/scoping 확정 전까지.
4. grouping: integrable 2 한 번에(60→62) vs family별(F4·F6 각 60→61). §6 권고.

## §6. grouping recommendation
- **권고 = integrable 2 한 번에**(60→62). F4(absorption/al_mg_antacid)·F6(depletion/B12) 두 렌더 경로 모두 live 선례 존재 → 동시 통합 안전.
- 또는 family별 순차(F4 → F6). F10 은 어느 경우에도 제외(needs_review).
- antibiotic-mineral wave(F1/F2/F3) · chronic-depletion(F9) 와 disjoint → 어느 wave 와도 합칠 수 있음(F1+F2+F3+F9+F4+F6 = 60→93).

## §reviewer-note (템플릿 — 게이트 통과 형식)
```
검수자: <이름/RPH-ID> (PM 승인 근거)  검토일 <YYYY-MM-DD 채움>
승인(approved): F4/F6/F10 small-family integrable 후보를 verified_reference 노출로 승인.
scope: integrable 범위. 승인 candidate_id 전건: RF-F4-0173, RF-F6-0201.
grouping: integrable subset(small-family bundle) 한 번에 통합.
category 결정: 레보티록신×제산제 = al_mg_antacid(알루미늄 함유 제산제). 영양소: 에스오메프라졸×비타민B12(약물 category 없음).
mechanism/action: absorption/separation(F4) · depletion/monitoring(F6). 모니터링 톤(참고정보·정기 확인 문의, 검사 지시 아님·처방 아님) 유지.
RF-F4-0173: 라벨이 알루미늄 함유 제산제만 명시(Mg 미명시) — Al-only copy_change 인지·display Mg 비단정.
케토코나졸(F10): 국내 외용 전용·수출용 source → route/availability needs_review, 본 승인 대상 아님(통합 제외).
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. B12 보충 권유 없음.
verified_reference 노출 동의.
```
> ⚠️ placeholder(`<...>`/`YYYY-MM-DD`)·SAMPLE·승격요구·제품/보충 추천 허용·검사 지시 허용·외용→경구 일반화 허용 문구가 있으면 게이트 STOP.
