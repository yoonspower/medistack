# MediStack — F1 플루오로퀴놀론 18건 Clinical Reviewer Package (v1.4)

> **상태: REVIEWER-GATED · NOT LIVE.** 이 패키지는 clinical reviewer 의 판단을 받기 위한 자료다.
> reviewer note(§6) 실물 + 별도 PM 승인 + 별도 PR 전까지 **live 통합·published·clinical_reviewed=true 전환 금지.**
> 단일 소스: `data/review/f1_quinolone_inventory_v1_4.json` · dry-run: `data/review/f1_quinolone_live_dryrun_v1_4.json`. 확인일 2026-06-16.

## 1. 범위

- **포함**: F1 퀴놀론 reviewer-ready 후보 **18건** (적대검증 verdict=survives + 작업 C family 재검증 통과).
- **제외**: 기존 live 60 · pending(페니실라민 2 · theme map 6 · 칼륨 4 · AT-FEX 1) · 다른 factory family(F2 테트라사이클린 5 · F3 비스포스포네이트 3 · F9 만성 depletion 8 · F10 azole 1 · F4 · F6).
- relation 60 → (all18) 78 / (nutrient10) 70 / (antacid8) 68. id = runtime max+1.

## 2. 안전 원칙 (reviewer 확인)

- **항생제 복용 지시 아님** — 퀴놀론 복용/중단을 지시하지 않음. "허가사항에 이런 문구가 있다"는 참고정보.
- **금속이온/제산제 복용 권유 아님** — 철분·칼슘·아연·제산제 복용을 권하지 않음.
- **제품 추천 아님** — 제품·구매·제휴 UI/문구 없음. product_link_allowed=false.
- **source quote 기반** — 모든 카드는 식약처 허가사항 원문 quote 에 근거.
- **reviewer note ≠ clinical_reviewed=true** — 노출 천장은 verified_reference. 임상 검수 완료/식약처 승인/법적 문제 없음 을 의미하지 않음.

## 3. Family-level risk (공통)

1. **mineral vs antacid confusion** — Al/Mg 함유 제산제(약물 8건)를 마그네슘 영양제로 오인 금지. category=al_mg_antacid·counterpart 에 '약물' 표기. (영양소 10건은 철분/칼슘/아연.)
2. **direct instruction risk** — separation 을 "함께 복용하지 마세요" 같은 명령으로 강화 금지. 카드는 "복용 시점을 분리하도록 안내"+"약사와 상담".
3. **quote boundary risk** — 번호목록/표 raw 가 다른 문장을 끌어오지 않도록. RF-F1-0020 은 끝 stray '1' 트림(verbatim 부분문자열·작업 C).
4. **계열 일반화 금지** — 각 후보는 해당 itemSeq 허가사항 quote 로 개별 확인(계열 추론으로 만든 draft 아님).
5. **action 입도** — 원문이 '병용 회피'(발로, 간격 미명시)여도 카드는 separation(원문보다 강하지 않음). reviewer 가 입도 확정.
6. **formulation scope** — 오플록사신 '(단, 경구제에 한함)'(경구 한정·주사제 제외).

## 4. 후보 카드 (18) — 성분별

각 카드: itemSeq · source quote(허가사항 원문·verbatim) · mechanism/action · app display copy · management copy · evidence/confidence/risk.
공통: mechanism=absorption · action=separation · evidence=moderate · confidence=moderate · risk=known_safe · product_link=false.
display copy 패턴(nutrient): "이 약은 〈영양소〉과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요."
management copy 패턴: "〈영양소〉과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
(al_mg_antacid 8건은 〈영양소〉 자리에 "Al/Mg 함유 제산제(약물)".)

### 노르플록사신 (itemSeq 198500810 · 병용투여)
- **RF-F1-0021 ×철분** / **0024 ×아연** — quote: "아연 또는 철분이 함유된 제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다."
- **RF-F1-0022 ×칼슘** / **0025 ×Al/Mg제산제(al_mg_antacid)** — quote: "알루미늄 또는 마그네슘 함유 제산제, 칼슘 함유 제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 4시간 이내에는 병용하지 않는 것이 바람직하다."

### 자보플록사신 (itemSeq 201501455 · 병용투여)
- **RF-F1-0041 ×철분 / 0042 ×칼슘 / 0044 ×아연 / 0045 ×Al/Mg제산제** — quote: "알루미늄 또는 마그네슘 함유 제산제, 철분 함유 제제, 칼슘 함유 제제, 아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 3시간 이내에는 병용하지 않는다."

### 토수플록사신 (itemSeq 200501778 · 병용투여)
- **RF-F1-0066 ×철분 / 0067 ×칼슘 / 0070 ×Al/Mg제산제** — quote: "알루미늄 또는 마그네슘 함유 제산제, 철분 함유 제제, 칼슘 함유 제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다."

### 페플록사신 (itemSeq 199202246 · 병용투여)
- **RF-F1-0026 ×철분 / 0029 ×아연** — quote: "철분 함유 제제, 아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저해되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다."
- **RF-F1-0030 ×Al/Mg제산제** — quote: "알루미늄 또는 마그네슘 함유 제산제와의 병용에 의해 흡수가 저해되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 4시간 이내에는 병용하지 않는 것이 바람직하다."

### 레보플록사신 ×Al/Mg제산제 (RF-F1-0010 · itemSeq 199901759 · 병용투여)
- quote: "알루미늄 또는 마그네슘 함유 제산제, 수크랄페이트, 철분 함유 제제, 칼슘 함유 제제, 아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다."
- ⚠️ live id1·2·3·43 = 레보플록사신 ×칼슘/철분/마그네슘/아연(nutrient). 본 후보는 ×Al/Mg 제산제(약물)=별도 counterpart(id61 선례) → 중복 아님. **reviewer 확인.**

### 로메플록사신 ×Al/Mg제산제 (RF-F1-0035 · itemSeq 199903690 · 병용투여)
- quote: "수크랄페이트, 알루미늄 또는 마그네슘 함유 제산제와 병용 시 킬레이트 복합체를 형성하면서 이 약의 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다." (명시적 '킬레이트 복합체')

### 발로플록사신 ×Al/Mg제산제 (RF-F1-0040 · itemSeq 199300319 · 상호작용)
- quote: "알루미늄 또는 마그네슘을 함유하는 제산제와의 병용에 의해 이 약의 흡수가 저하되고 효과가 감소되는 경우가 있으므로 병용을 피하는 것이 바람직하다."
- ⚠️ 원문 '병용을 피하는 것이 바람직하다'(간격 미명시) → 카드 separation(원문보다 강하지 않음). **reviewer 가 action 입도(separation vs avoid_concomitant) 확정.**

### 오플록사신 ×Al/Mg제산제 (RF-F1-0020 · itemSeq 198900665 · 병용투여) — **copy_change**
- quote(트림 후·verbatim 부분문자열): "수크랄페이트, 알루미늄 또는 마그네슘 함유 제산제, 철분 함유 제제, 칼슘 함유 제제, 아연 또는 철분이 함유된 종합비타민제제와의 병용에 의해 흡수가 저하되어 효과가 저하되는 경우가 있으므로 이 약 투여 전후 2시간 이내에는 병용하지 않는 것이 바람직하다(단, 경구제에 한함)."
- 작업 C: 원문 끝 stray '1' 트림. ⚠️ '(단, 경구제에 한함)' = 경구 한정(주사제 제외). **reviewer 가 경구 scope 노출 여부 확정.**
- ⚠️ live id21·22·23·45 = 오플록사신 ×칼슘/철분/마그네슘/아연(nutrient). 본 후보는 ×Al/Mg 제산제(약물)=별도 counterpart → 중복 아님. **reviewer 확인.**

## 5. Reviewer decision table

| 결정 | 옵션 |
|---|---|
| 승인 범위 | (a) all18 / (b) nutrient10 먼저 / (c) antacid8 / (d) by-ingredient / (e) 일부 hold |
| grouping | all18 일괄 vs by-counterpart 2-wave(권고) vs by-ingredient |
| al_mg_antacid category | 채택(id61 선례·약물 counterpart) 확정 — Mg 영양제 아님 |
| separation 간격 | 일반 '분리' 안내 유지(현행) vs 후보별 2/3/4시간 노출 |
| 발로플록사신 action | separation 유지(권고) vs avoid_concomitant |
| 오플록사신 경구 scope | '(단, 경구제에 한함)' 카드/노트 표기 여부 |
| verified_reference 노출 | 동의 / 보류 |

## 6. Reviewer note 템플릿 (§reviewer-note)

> `check_reviewer_note(note, scope_ids)` 가 의미 수준으로 강제. 승인 scope 의 candidate_id **전건** + 아래 결정 전부 명시.
> SAMPLE/예시 토큰·placeholder(YYYY-MM-DD 등)·빈 노트·clinical_reviewed=true 요구·제품 추천 허용·금속이온/제산제 복용 권유 허용 → **거부.**

```
검수자: <RPH/검토자 식별자 또는 PM 승인 근거>   검토일 <YYYY-MM-DD 를 실제 날짜로>
승인(approved): F1 퀴놀론 <scope: all18 | nutrient10 | antacid8 | 명시 ids> 후보를 verified_reference 노출로 승인.
scope: <all18 | nutrient10 | antacid8> 범위. 승인 candidate_id 전건: RF-F1-0021, RF-F1-0022, ... (scope 전건 나열)
grouping: <all18 한 번에 | by-counterpart nutrient/al_mg subset | 성분별> 통합.
category 결정: Al/Mg 함유 제산제는 al_mg_antacid(약물 counterpart·id61 선례) — 마그네슘 영양제 아님.
separation 간격(2~4시간) 카드 노출: <일반 '분리' 안내 유지 | 후보별 시간 노출>.
발로플록사신 action: <separation 유지 | avoid_concomitant>. 오플록사신 경구 scope: <표기 | 비표기>.
clinical_reviewed=true 아님(verified_reference 천장 유지). 제품·구매·제휴 추천 없음. 금속이온·제산제 복용 권유 없음.
```
