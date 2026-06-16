# MediStack — F1 플루오로퀴놀론 18건 인벤토리 + 작업 C 재검증 (v1.4)

> **상태: DRAFT-ONLY — NOT LIVE.** `live_integration_forbidden=true` · `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란.
> 본 문서는 Relation Factory v1.4 적대검증(survives) F1 18건의 감사 + **작업 C family-specific 재검증** 결과다.
> survives/copy_change 는 **자동 렌즈 통과**를 의미하며 임상 검수 완료·식약처 승인·법적 문제 없음 을 의미하지 **않는다.**
> 단일 소스: `data/review/f1_quinolone_inventory_v1_4.json` (integrator dry-run 생성). 확인일 2026-06-16.

## 1. 범위 / 분포

- **family**: F1 = Fluoroquinolone × metal cation / Al·Mg 함유 제산제 (mechanism=absorption · action=separation · evidence=moderate · risk=known_safe)
- **count**: 18 (적대검증 verdict 전건 `survives`)
- **counterpart split**: nutrient 10 (철분 4 · 칼슘 3 · 아연 3) · al_mg_antacid 8 (약물 counterpart)
- **drug ingredient (8)**: 노르플록사신·레보플록사신·로메플록사신·발로플록사신·오플록사신·자보플록사신·토수플록사신·페플록사신
  - 레보·오플록사신은 live 에 ×광물(nutrient)만 존재 → Al/Mg 제산제(약물)는 **별도 counterpart**(id61 이트라코나졸 선례)
  - 나머지 6 성분은 신규(live·full index sample 부재)

| ingredient | itemSeq | 철분 | 칼슘 | 아연 | Al/Mg제산제 | 소계 |
|---|---|:-:|:-:|:-:|:-:|:-:|
| 노르플록사신 | 198500810 | 0021 | 0022 | 0024 | 0025 | 4 |
| 자보플록사신 | 201501455 | 0041 | 0042 | 0044 | 0045 | 4 |
| 토수플록사신 | 200501778 | 0066 | 0067 | — | 0070 | 3 |
| 페플록사신 | 199202246 | 0026 | — | 0029 | 0030 | 3 |
| 레보플록사신 | 199901759 | — | — | — | 0010 | 1 |
| 로메플록사신 | 199903690 | — | — | — | 0035 | 1 |
| 발로플록사신 | 199300319 | — | — | — | 0040 | 1 |
| 오플록사신 | 198900665 | — | — | — | 0020 | 1 |

## 2. 후보별 감사

| candidate_id | relation | type | category | mech/action | ev/conf/risk | adv | reverify |
|---|---|---|---|---|---|---|---|
| RF-F1-0021 | 노르플록사신 × 철분 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0022 | 노르플록사신 × 칼슘 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0024 | 노르플록사신 × 아연 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0025 | 노르플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0010 | 레보플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0035 | 로메플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0040 | 발로플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives* |
| RF-F1-0020 | 오플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | **copy_change** |
| RF-F1-0041 | 자보플록사신 × 철분 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0042 | 자보플록사신 × 칼슘 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0044 | 자보플록사신 × 아연 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0045 | 자보플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0066 | 토수플록사신 × 철분 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0067 | 토수플록사신 × 칼슘 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0070 | 토수플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0026 | 페플록사신 × 철분 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0029 | 페플록사신 × 아연 | nutrient | null | absorption/separation | moderate/moderate/known_safe | survives | survives |
| RF-F1-0030 | 페플록사신 × Al/Mg 제산제(약물) | drug | al_mg_antacid | absorption/separation | moderate/moderate/known_safe | survives | survives |

`*` RF-F1-0040 = survives + reviewer 결정 note(아래 §4).

## 3. 작업 C — family-specific 재검증 (refute-by-default 10 렌즈)

`reverify()` (integrator) 가 후보별로 결정론 인코딩. 렌즈:

1. **L1 source fidelity** — itemSeq 8자리+·source_section 존재
2. **L2 direct co-occurrence** — nutrient 는 quote 에 해당 영양소(철분/칼슘/아연) 직접 언급 · 제산제는 '제산제' + ('알루미늄' 또는 '마그네슘')
3. **L3 Al/Mg 제산제 vs Mg 영양제** — al_mg_antacid 는 counterpart 에 '약물' 표기·'마그네슘'(영양소) 아님 / nutrient 는 {철분,칼슘,아연}
4. **L4 quote boundary / hygiene** — 끝 stray marker 없음
5. **L5 negation / 항응고·비타민K** — 와파린·항응고·비타민K·INR·프로트롬빈 혼입 없음
6. **L6 방향** — 흡수 + (저하/저해/감소) 또는 킬레이트
7. **L7 복용 지시 금지** — 명령형(복용하지 마/드세요/반드시 등) 없음
8. **L8 제품/보충** — 제품·구매·제휴 phrase + 보충 권유 phrase 없음
9. **L9 금칙어** — vfp.scan 0
10. **L10 상담 톤** — '약사 또는 의사' 참고정보 톤

**결과: survives 17 · survives_with_copy_change 1 · needs_review 0 · hold 0 · reject 0** (강등 0).

### survives_with_copy_change — RF-F1-0020 오플록사신 × Al/Mg 제산제

- **L4 quote hygiene**: 원문 끝에 stray footnote marker `' 1'` 가 붙어 있었음(`...병용하지 않는 것이 바람직하다(단, 경구제에 한함). 1`).
- **copy_change**: source_quote 끝 `' 1'` 트림 → `...(단, 경구제에 한함).` (원문 **verbatim 부분문자열** — `assert cleaned in original` 보증). display/management 카피 **불변**(pointer hygiene 만).
- 적대검증 광역 라운드(프롬프트 14)는 이 stray marker 를 놓쳤음 → **family-specific 재검증이 추가로 잡은 정비**(후보 손실 0).
- **추가 reviewer note(L8 formulation)**: 원문 `'(단, 경구제에 한함)'` = 경구 제형 한정(주사제 제외). display copy '함께 복용'(경구)과 정합 — 카드/노트에 경구 scope 를 남길지 reviewer 확정.

## 4. reviewer 결정 note (다운그레이드 아님)

- **RF-F1-0040 발로플록사신**: 원문 `'병용을 피하는 것이 바람직하다'`(간격 미명시) → 카드는 일반 `separation`. **원문보다 강하지 않음**(separation < avoid_concomitant) · 안전. reviewer 가 action 입도 확정 — separation 유지(권고) vs avoid_concomitant(al_mg_antacid 에서 schema 허용). 카드 카피는 영향 없음.
- **separation 간격(2~4시간)**: 원문은 후보별 2/3/4시간 상이(노르 4h·자보 3h·토수/페/레보 2h·발로 미명시). 현재 카드는 일반 '분리' 안내(구체 시간 비노출). reviewer 가 간격 노출 여부 결정.
- **al_mg_antacid(8건)**: live 에 동일 약물 ×광물(nutrient)이 있어도(레보/오플) Al/Mg 제산제(약물)는 별도 counterpart 유지 — id61 이트라코나졸 선례. reviewer 확정.

## 5. 안전

- live_integration_forbidden=true · do_not_implement_yet=true · published=false · clinical_reviewed=false · reviewed_by 공란.
- product_link_allowed=false · potassium_safety_card=false (전건).
- live 60 / pending(페니실라민·theme·칼륨·AT-FEX) / 다른 factory family 와 **중복·충돌 0** (§dryrun conflict_summary).
- 실제 live 통합은 **별도 PM + clinical reviewer note + 별도 PR** (이번 작업 범위 밖).
