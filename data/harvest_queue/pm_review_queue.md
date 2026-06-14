# MediStack Relation Harvester — PM Review Queue (v1.3)

- 생성: 2026-06-14T16:44:04  |  모드: **offline_dryrun(fixtures)**  |  봇: harvest_relation_bot_v1_3
- ⚠️ **live 승격 금지**: 모든 항목 do_not_implement_yet=true · live_integration_forbidden=true · published=false · clinical_reviewed=false
- live relation 변경: **0** (봇은 큐만 생성). PM 검토·source 재확인 후 별도 통합 스크립트로만 승격.

## 분포
- 후보 수집(harvest): 77
- source-check 시도: 29  → draft 후보: **3**, needs_review: 24, reject: 2
- precheck: already_covered 6, sensitive/literature hold 46, rejected_precheck 52
- KPI 트랩 스캔: 60건 분류

## A. DRAFT 승인 후보 (PM 판단 필요 · live 금지)

### D-CORT-01 — 프레드니솔론 × 칼륨 (depletion/monitoring)
- relation 후보: 프레드니솔론 × 칼륨 (depletion/monitoring)
- source quote: "프레드니솔론정5밀리그램 이 약을 장기간 또는 고용량으로 투여하는 경우 전해질 변화로 저칼륨혈증이 나타날 수 있다. 코르티코스테로이드는 칼륨 배설을 증가시킬 수 있으므로 주의한다."
- itemSeq: 100001
- confidence: high  |  risk_level: moderate
- recommended_action: REVIEW→DRAFT 승인 후보(직접근거+적대검증 통과, live 금지)
- reject/hold 이유: 허가사항 직접 동거어+방향 일치+단일 경구 itemSeq 확보(verify 결정론). 적대검증 후 draft only.
- safe copy 초안: 프레드니솔론을(를) 복용하는 경우 칼륨 상태에 영향이 있을 수 있어, 상태 확인이 필요할 수 있습니다. / 칼륨은 임의로 보충하면 위험할 수 있으므로, 보충 여부는 반드시 의사 또는 약사와 상담하세요.
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CA-01 — 아세타졸아미드 × 칼륨 (depletion/monitoring)
- relation 후보: 아세타졸아미드 × 칼륨 (depletion/monitoring)
- source quote: "아세타졸아미드정250밀리그램 탄산탈수효소 억제에 의한 이뇨작용으로 저칼륨혈증 및 대사성 산증이 나타날 수 있어 칼륨 상태를 모니터링한다."
- itemSeq: 100002
- confidence: high  |  risk_level: moderate
- recommended_action: REVIEW→DRAFT 승인 후보(직접근거+적대검증 통과, live 금지)
- reject/hold 이유: 허가사항 직접 동거어+방향 일치+단일 경구 itemSeq 확보(verify 결정론). 적대검증 후 draft only.
- safe copy 초안: 아세타졸아미드을(를) 복용하는 경우 칼륨 상태에 영향이 있을 수 있어, 상태 확인이 필요할 수 있습니다. / 칼륨은 임의로 보충하면 위험할 수 있으므로, 보충 여부는 반드시 의사 또는 약사와 상담하세요.
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### AT-FEX-01 — 펙소페나딘 × Al/Mg 제산제(약물) (antacid_interaction/antacid_interaction)
- relation 후보: 펙소페나딘 × Al/Mg 제산제(약물) (antacid_interaction/antacid_interaction)
- source quote: "펙소페나딘염산염정120밀리그램 수산화알루미늄 또는 수산화마그네슘을 함유하는 제산제와 동시에 복용하면 이 약의 흡수가 저하될 수 있으므로 2시간 간격을 두고 투여한다."
- itemSeq: 100006
- confidence: high  |  risk_level: low
- recommended_action: REVIEW→DRAFT 승인 후보(직접근거+적대검증 통과, live 금지)
- reject/hold 이유: Al/Mg 제산제 directive 동거어+directive 문맥+부정문구 부재+단일 경구 itemSeq → antacid draft 후보(영양소 relation 아님, live 금지).
- safe copy 초안: 펙소페나딘과(와) 알루미늄·마그네슘이 함유된 제산제를 같은 시간에 함께 복용하면 펙소페나딘의 흡수가 줄어들 가능성이 있습니다. / 같은 시간대 복용은 피하고 시간 간격을 두는 것이 도움이 될 수 있으며, 구체적인 간격은 약사 또는 의사와 상담하세요.
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

## B. NEEDS_REVIEW (근거/적대검증 불충분 — source 재확인)

### F-CEPH-02 — 세푸록심 × 철분 (absorption/separation)
- relation 후보: 세푸록심 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-03 — 세프포독심 × 철분 (absorption/separation)
- relation 후보: 세프포독심 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-04 — 세프프로질 × 철분 (absorption/separation)
- relation 후보: 세프프로질 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-05 — 세픽심 × 철분 (absorption/separation)
- relation 후보: 세픽심 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-06 — 세프라딘 × 철분 (absorption/separation)
- relation 후보: 세프라딘 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-07 — 세프카펜 × 철분 (absorption/separation)
- relation 후보: 세프카펜 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-08 — 세프디토렌 × 철분 (absorption/separation)
- relation 후보: 세프디토렌 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-09 — 세팔렉신 × 철분 (absorption/separation)
- relation 후보: 세팔렉신 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### F-CEPH-10 — 세프록사딘 × 철분 (absorption/separation)
- relation 후보: 세프록사딘 × 철분 (absorption/separation)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CORT-03 — 메틸프레드니솔론 × 칼륨 (depletion/monitoring)
- relation 후보: 메틸프레드니솔론 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CORT-07 — 메틸프레드니솔론 × 칼슘 (absorption/monitoring)
- relation 후보: 메틸프레드니솔론 × 칼슘 (absorption/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CORT-04 — 덱사메타손 × 칼륨 (depletion/monitoring)
- relation 후보: 덱사메타손 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CORT-05 — 하이드로코르티손 × 칼륨 (depletion/monitoring)
- relation 후보: 하이드로코르티손 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-CORT-06 — 플루드로코르티손 × 칼륨 (depletion/monitoring)
- relation 후보: 플루드로코르티손 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-LOOP-01 — 부메타니드 × 칼륨 (depletion/monitoring)
- relation 후보: 부메타니드 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-LOOP-02 — 부메타니드 × 마그네슘 (depletion/monitoring)
- relation 후보: 부메타니드 × 마그네슘 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-LOOP-03 — 피레타니드 × 칼륨 (depletion/monitoring)
- relation 후보: 피레타니드 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-LOOP-04 — 아조세미드 × 칼륨 (depletion/monitoring)
- relation 후보: 아조세미드 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-LOOP-05 — 아조세미드 × 마그네슘 (depletion/monitoring)
- relation 후보: 아조세미드 × 마그네슘 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-THZ-01 — 메토라존 × 칼륨 (depletion/monitoring)
- relation 후보: 메토라존 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-THZ-02 — 메토라존 × 마그네슘 (depletion/monitoring)
- relation 후보: 메토라존 × 마그네슘 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-THZ-03 — 트리클로르메티아지드 × 칼륨 (depletion/monitoring)
- relation 후보: 트리클로르메티아지드 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-THZ-04 — 트리클로르메티아지드 × 마그네슘 (depletion/monitoring)
- relation 후보: 트리클로르메티아지드 × 마그네슘 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: low
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

### D-THZ-05 — 벤드로플루메티아지드 × 칼륨 (depletion/monitoring)
- relation 후보: 벤드로플루메티아지드 × 칼륨 (depletion/monitoring)
- source quote: ""
- itemSeq: —
- confidence: no_product  |  risk_level: moderate
- recommended_action: 재확인 필요(근거/적대검증 불충분)
- reject/hold 이유: DENY(fail-closed): 국내 완제·경구·정상·단일성분 대표 품목 미확보(검색 0건/네트워크) — 재확인 필요.
- safe copy 초안: —
- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true

## C. HOLD / REJECT 요약 (자동 분류 — 상세는 CSV)
- sensitive/literature hold → `sensitive_hold.csv` (46)
- rejected_precheck → `rejected_precheck.csv` (52)
- source-check reject → `needs_review.csv` 내 verdict=reject

## PM 판단사항
1. DRAFT 후보의 safe_copy 가 라벨 강도와 일치하는지 최종 확인 후 draft 채택 여부 결정.
2. NEEDS_REVIEW 의 source 재확인(국내 단일 경구 itemSeq / 동거어).
3. 승격은 별도 integrate 스크립트 + clinical reviewer 확보 후(봇 범위 밖).
