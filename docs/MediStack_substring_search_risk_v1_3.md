# MediStack — substring 검색 위험 광역 탐색 (v1.3, 2026-06-15 round3 후속)

> 분석/탐색 산출물. **live/protected 무수정 · live 승격 0 · SDK-only.** 신규 후보는 draft-only(review artifact)로만 정리.
> 근거 데이터: `data/review/substring_search_risk_v1_3.json` · 스크립트 `scripts/analyze_substring_search_risk_v1_3.py`.

## 0. 목적 / baseline

직전 라운드(`analyze_substring_domination_v1_3.py`, universe theme∪carried∪live∪KPI=366)에서 **프레드니솔론 ⊂ 메틸프레드니솔론** false-negative 를 deep fallback 으로 해소하고, 같은 패턴인 **오메프라졸 ⊂ 에스오메프라졸 · 란소프라졸 ⊂ 덱스란소프라졸**(둘 다 이미 live, base itemSeq 정확)을 확인했다. 본 라운드는 universe 를 **full drug name index 의 distinct ingredient 전체**까지 확대해 "짧은 성분명이 더 긴 성분명에 묻혀 `search_itemseqs` 가 놓칠 수 있는" 케이스를 더 찾는다.

- **baseline(처리 완료, 재탐색 불필요)**: 프레드니솔론 · 오메프라졸 · 란소프라졸.

## 1. universe / 방법

- scan universe = full index distinct ingredient **2,225** ∪ alias(한글) **27** ∪ seed(theme∪carried∪live∪KPI∪antacid) **367** = **2,292**(단일성분 스캔 **922**, '/'·',' 복합제·1~2글자 제외).
- proper-substring 쌍 A ⊊ B(A≠B, len(A)≥3) 산출 → `idx=B.find(A)` 로 분류:
  - `idx==0` → B=A+접미사(염/수화물/제형) = **같은 약물** → **salt_or_formulation_trap**.
  - B[idx-1] 한글이고 접두사가 **형태기술**(무수/미분화/미세/미세화/주사용/제피/장용/서방…) → 같은 활성성분(형태변형) → **salt_or_formulation_trap**.
  - B[idx-1] 한글이고 접두사가 **다른 활성성분**(메틸/에스/덱스/레보/데스/레미/수/알…) → 진짜 지배 위험.
  - 그 외(구분자 뒤) → 복합제 동거성분 → no_action.
- 위험도: **high_risk_substring**(diff-active 접두사 + seed 범위) / **medium_risk_substring**(diff-active 접두사 + seed 밖) / **salt_or_formulation_trap** / **no_action**.
- deep-check(SDK, cache-first): high(diff-active+seed)만 `search_itemseqs` 실행 → exact_ingredient_found / **shallow_miss_confirmed** / **shallow_already_safe** / no_domestic_product / ambiguous.

## 2. 분류 결과

| 분류 | 건수 | 의미 |
|---|---|---|
| high_risk_substring | **10** | diff-active 접두사 superset + seed 범위 — deep-check 대상 |
| medium_risk_substring | **14** | diff-active 접두사 superset + seed 밖 — 미래 관찰(현재 relation 트랙 무관) |
| salt_or_formulation_trap | **143** | 염/수화물/형태접두사(무수·미세 등) = 같은 약물 · 무위험 |
| no_action | 2 | 복합제 동거/사소 |

## 3. high_risk deep-check 결과 (핵심)

| 성분 | diff-active superset | deep-check | nutrient 트랙 | 판정 |
|---|---|---|---|---|
| 프레드니솔론 | 메틸프레드니솔론 등 | **shallow_miss_confirmed** → 199602982(소론도정) | ○ (DF-PRED-01 draft) | baseline·처리완료 |
| 오메프라졸 | 에스오메프라졸 | **shallow_miss_confirmed** → 199202074 | ○ (id13/14 live) | baseline·live 정확 |
| 란소프라졸 | 덱스란소프라졸 | **shallow_miss_confirmed** → 200301515 | ○ (id36/37 live) | baseline·live 정확 |
| 로라타딘 | 데스로라타딘 | shallow_already_safe → 199701227 | ✕ (항히스타민) | 위험 미발현 |
| 세티리진염산염 | 레보세티리진염산염 | shallow_already_safe | ✕ | 위험 미발현 |
| 세팔렉신 | 메틸올세팔렉신리시네이트 | shallow_already_safe → 198701854 | △ (세파계×철=reject) | 위험 미발현 |
| 암로디핀베실산염 | 에스암로디핀베실산염 | shallow_already_safe | ✕ (CCB) | 위험 미발현 |
| 졸피뎀 | (combo) | shallow_already_safe | ✕ (수면) | 위험 미발현 |
| 펜타닐 | 레미/수/알펜타닐 | shallow_already_safe | ✕ (오피오이드·sensitive) | 위험 미발현 |
| 펜타닐시트르산염 | 수펜타닐시트르산염 | shallow_already_safe | ✕ | 위험 미발현 |

- **shallow_miss_confirmed = baseline 3건뿐**(프레드니솔론·오메프라졸·란소프라졸, 전부 처리/확인 완료).
- 신규 diff-active 후보 7종은 **전부 shallow_already_safe** — 다른 활성성분(이성질체/유도체) superset 이 존재해도, base 약물이 자체 국내 단일·경구 품목을 얕은 페이지에 충분히 노출해 **지배가 발현되지 않음**. 게다가 7종 모두 영양소 상호작용 트랙(depletion/absorption) 밖.
- **shallow_miss 인데 형태접두사(같은 약물)인 케이스**(무수리세드론산나트륨·제피미르타자핀·미세화페노피브레이트 등)는 salt_or_formulation_trap 으로 분류 — deep fallback 이 정확 base 를 무해 복구하고 relation(활성성분 단위)에 영향 없음. 리세드론산·이반드론산 bisphosphonate live relation(itemSeq 201903166=건토넬정 무수리세드론산나트륨 · 201306285=경보이반드로네이트정) 은 base 활성성분 단일·경구로 read-only 확인됨.

## 4. medium_risk (seed 밖 · 미래 관찰)

diff-active 접두사 superset 을 가지나 현재 relation factory/harvester seed 와 무관(영양소 상호작용 트랙 아님): 트레티노인(⊂이소/알리트레티노인) · 프로게스테론(⊂메드록시프로게스테론) · 설피리드(⊂레보설피리드) · 페니토인(⊂포스페니토인) · 케타민(⊂에스케타민) · 클로니딘(⊂아프라클로니딘) · 미로데나필 · 메칠프레드니솔론(⊂아세폰산메칠프레드니솔론) 등 14종. 또한 살리실산·에탄올·과산화벤조일·라미프릴 등은 product-name-as-ingredient 또는 용매/첨가제 잡음. **현 트랙에서 후보화 대상 아님** — 향후 해당 성분이 relation 후보가 될 때만 deep-check.

## 5. 결론

- **신규 substring 지배 false-negative 위험 0.** full index(2,225) 까지 확대한 광역 스캔에서도, deep fallback 이 필요한(=얕은검색이 정확 base 를 놓치는) 케이스는 **이미 처리된 baseline 3종**뿐이다.
- 신규 diff-active 후보는 전부 shallow_already_safe(지배 미발현) + 영양소 트랙 밖 → **신규 draft/relation 후보 없음.**
- 본 산출물(`data/review/substring_search_risk_v1_3.json`)이 review artifact = draft-only 기록. **live/relation 무반영.**
- deep fallback 하드닝(round3, `_prefix_dominated`: 형태접두사·염·복합제 발동 제외)이 광역 universe 에서도 과다 호출 없이 정확히 동작함을 재확인.

## 6. 다음 PM 판단사항

1. medium_risk 14종은 현재 무관 — 해당 성분이 relation 후보가 될 때만 deep-check(재후보화 게이트).
2. `_prefix_dominated` 형태접두사 allowlist(무수/미세/제피…)는 분류 정직성용 — production search_itemseqs 의 deep 발동은 여전히 '연속명 접두사' 기준이라 형태변형에도 1회 deep 발동 가능(무해). 비용 문제 시 production 에도 형태접두사 차단 추가 검토(현재는 무해·보류 권장).
3. live 승격(칼륨 4건·AT-FEX)은 여전히 clinical reviewer note 게이트 대기.
