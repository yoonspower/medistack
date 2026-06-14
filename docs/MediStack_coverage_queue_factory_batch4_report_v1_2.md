# MediStack — coverage-queue factory batch4 리포트 (Top201-300) v1.2

작성일: 2026-06-14 · 상태: **분석 산출물 / 라이브 통합 0** · 대상 AI 세션 핸드오프용 자기완결 문서

## 0. 요약 (TL;DR)
- 범위: coverage KPI **Top201-300**(precheck 대역 cap 100) → precheck → 안전후보 nedrug source-check → 역방향 적대검증.
- **batch4 결과: source_confirmed 0건 → draft 0건(count=0).** 라이브 relation/full index/alias/export/src 무변경(relations 59 그대로).
- 의미: Top201-300은 ①복합제 ②스타틴 칼슘염/ARB 칼륨염 짝이온 트랩 ③ARB 고칼륨 고위험 ④민감 전문약(항암/항혈전/마취/정신) ⑤국소·주사 제형으로 구성되어 **새 단일성분 영양소 relation 0**. batch3(Top101-200) 2건 → batch4 0건으로 **수확체감** 확인.

## 1. precheck (band 201-300, 100건)

| precheck_class | 건수 |
|---|---|
| rejected_precheck | 71 |
| sensitive_hold | 14 |
| already_covered_or_drafted | 8 |
| source_check_candidate | 7 |

- 발굴: 약물클래스 추론(흡수킬레이션/산분비/고갈/완전성비평) 기반 union → high recall, deterministic source-check 가 최종 판정.
- **함정 적발(후보 제외)**:
  - **스타틴 칼슘염 트랩**: 로수바스타틴칼슘/아토르바스타틴칼슘 — '칼슘'은 짝이온염이지 칼슘 보충제 상호작용 아님 → reject(계열·짝이온 일반화 금지).
  - **ARB 칼륨염/고칼륨 트랩**: 피마사르탄칼륨 짝이온 + ARB 고칼륨혈증 방향(고위험 상승) → reject/hold.
  - **제산제 함유 복합제**: 파모티딘/수산화마그네슘/침강탄산칼슘 — 제품 자체가 제산제(Mg/Ca 함유)지 약물×영양소 보충제 상호작용 아님 → reject.
- sensitive_hold 14: KPI 분류 3(졸피뎀·클로피도그렐/아스피린·에독사반) + '기타'로 새던 11(에베로리무스·엘로티닙·팔보시클립·티카그렐러·펜타닐·프로포폴·덱스메데토미딘·메틸페니데이트·보티옥세틴·테노포비르·데노수맙) 회수.
- cap: Top301+ 미precheck(차기 이월·명시).

## 2. source-check (nedrug 실측, source_check_candidate 7건)

| 결과 | 건수 | 후보 |
|---|---|---|
| source_confirmed | **0** | — |
| reject | 5 | 세프프로질(209·231)·세프라딘(229)·아지트로마이신(233)·트리암시놀론(274) |
| needs_review | 2 | 플루오르화나트륨(241)·레보도파(280) |

source check 효율: 7 후보 fetch → 0 confirmed (precheck 100건 → source-check 7건으로 좁힘, 최종 채택 0).

## 3. 역방향 적대검증 (reject/needs_review 라벨 직접 재대조)

confirmed 0이라 통상 적대검증(confirmed refute) 대상 없음. 대신 **false-reject(detector miss) 여부를 라벨 실측으로 역검증**:

| 후보 | 판정 | 라벨 재대조 결론 |
|---|---|---|
| 세프프로질·세프라딘 ×철분 | reject | 라벨에 철/철염 직접 동거어 없음. 세팔로스포린 철킬레이션은 성분특이(세프디니르)·계열 일반화 아님(batch3 입증). **true reject** |
| 아지트로마이신 ×Mg | reject | 라벨 '마그네슘'은 (a)스테아르산마그네슘=첨가제 (b)'저마그네슘혈증 환자'=전해질 경고뿐. 실제 상호작용은 "6.상호작용 1)제산제: 동시투여 시 **생체이용율 영향 없음**, 최고혈청농도 24%↓, 동시복용 금지" → **제산제(antacid)** 대상, Mg 보충제 아님. **true reject**(영양소 트랙). antacid_interaction 트랙(CQ-103 동형) 후보이나 생체이용율 불변으로 강도 약함 |
| 트리암시놀론 ×칼륨 | reject | itemSeq 200804589 = **구강점막 부착정**(아프타구내염 국소치료). 전신 경구정 아님, 라벨에 칼륨/전해질 없음. 전신 K고갈 가설은 제형(국소/주사/관절강)으로 미성립. **true reject** |
| 플루오르화나트륨 ×칼슘 | needs_review | 국내 단일 경구 완제품목 미확보(치과용 국소제형 위주). 칼슘-불화물 흡수간섭은 교과서적이나 actionable 경구 제품 없음 |
| 레보도파 ×철분 | needs_review | 국내 단일 경구 완제품목 미확보(카르비도파±엔타카폰 복합제만). 철-레보도파 킬레이션 라벨 개연하나 단일성분 정책상 미성립 |

→ **confirmed_before_adversarial 0 · confirmed_after_adversarial 0.** false-reject 없음(detector 판정과 라벨 실측 일치).

## 4. draft batch
- `data/coverage_queue_draft_batch4_v1_2.json` **count=0** (빈 batch). live_integration_forbidden=true·published/clinical false.
- count=0 은 정상(잘못된 relation 차단이 처리량보다 우선). validator PASS(8/8).

## 5. coverage KPI (live = relations 59, CQF02 반영 후 현재)

| KPI | 직전(live 58) | **현재(live 59, CQF02)** | batch4 draft 승격 시 | (참고)CQF03 칼륨 hold 해제 시 |
|---|---|---|---|---|
| ① Top300 성분 coverage | 24/300 = 8.00% | **25/300 = 8.33%** | **+0 → 25/300 = 8.33%** | 26/300 = 8.67% |
| ② Top300 품목수가중 coverage | 1098/13268 = 8.28% | **1135/13268 = 8.56%** | **+0 → 1135/13268 = 8.56%** | 1153/13268 = 8.69% |

- CQF02(테고프라잔, +1 성분/+37 품목)로 ① +0.33%p · ② +0.28%p 상승.
- **batch4 기여 = 0**(confirmed 0). KPI 변화 없음.
- relation 보유 base 성분: 26 / 고유 성분 2,225.

### 여전히 미커버인 Top300 주요 성분 (상위 품목수, 미커버)
대부분 **영양소 상호작용 근거 자체가 없는** 고빈도 약물이거나 민감군:
- 프레가발린(200)·가바펜틴(137)·토피라메이트·메만틴(신경/뇌) — 미네랄 상호작용 없음
- 피나스테리드(193)·탐스로신(160)·타다라필(150)·솔리페나신(비뇨/전립선) — 없음
- 몬테루카스트(186)·레보드로프로피진(호흡기) — 없음
- 모사프리드(160)·레바미피드(149)(소화/위장) — 없음
- 도네페질(146)(치매) — 없음
- 쿠에티아핀(130)·플루옥세틴(110) — 정신건강 sensitive_hold
- 클래리트로마이신(144)·세파클러(134)·플루코나졸(156)·테르비나핀(항생/항진균) — 일부 antacid-direction(antacid_interaction 트랙 후보)이나 영양소 보충제 직접 상호작용 아님

→ **coverage 공백의 대다수는 relation 대상이 아님**(상호작용 근거 부재). 남은 진성 후보는 antacid_interaction 트랙(별도 설계) 또는 단일성분 미유통(needs_review)으로 수렴.

## 6. limitation (불변 유지)
- 품목수 proxy는 실제 검색량/복용량이 아님(인지도·약가·만성/급성 차이 미반영).
- coverage 공백 ≠ relation 대상(상호작용 근거 없는 성분 다수).
- source-check confirmed 도 "다음 단계 검토 대상"일 뿐 구현 지시가 아님.

## 7. 산출물
- `data/coverage_queue_precheck_batch4_v1_2.csv` (precheck 100)
- `data/coverage_queue_source_check_batch4_v1_2.csv` (source-check 7)
- `data/coverage_queue_adversarial_verify_batch4_v1_2.json` (역검증, verifications=[])
- `data/coverage_queue_draft_batch4_v1_2.json` + `_preflight_v1_2.csv` (count=0)
- `scripts/build_coverage_queue_precheck_batch4.py` · `scripts/validate_coverage_queue_draft_batch4_v1_2.py`

## 8. 다음 PM 판단 필요사항
- antacid_interaction 트랙 구현 여부(아지트로마이신·클래리트로마이신·플루코나졸·이트라코나졸 등이 이 트랙으로 수렴) — `docs/MediStack_antacid_interaction_track_v1_2.md` 참조.
- 칼륨 depletion/monitoring 트랙(DF01-05·CQF03) 승격 여부 — `docs/MediStack_potassium_depletion_track_v1_2.md` 참조.
- Top301+ 정밀 precheck 진행 여부(수확체감 가속 예상 — Top300 진성 후보 거의 소진).
