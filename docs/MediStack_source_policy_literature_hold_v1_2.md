# MediStack — source-policy: literature_only hold 정책 + 향후 선택지 (v1.2+)

> 작성일: 2026-06-14. **정책 문서 전용 — 데이터/코드/relation 한 줄도 변경하지 않는다.** 현재 정책 = **Option A(허가사항 직접근거만)** 유지. 본 문서는 literature_only 후보를 왜 hold 하는지, 향후 어떤 선택지가 있는지 자기완결적으로 기록한다.
>
> 선행: `CLAUDE.md` · `MediStack_relation_factory_design_v1_2.md` §4(source-policy 게이트) · `MediStack_relation_factory_source_check_v1_2.md` §6(PM 판단). 정체성(불변): 식약처 허가사항 기반 약-영양소 **참고정보 베타**.

---

## 0. 한 줄 요약

MediStack 의 source 천장은 **식약처 허가사항(nedrug `getItemDetail`) 원문 동거어**다. 이차문헌(임상 가이드라인·메타분석·교과서)만 근거인 후보(스타틴×CoQ10, H2차단제×B12 등)는 **현재 정책상 draft/live 승격하지 않고 hold** 한다. coverage 영향이 커도(스타틴 name_only 합 다수) 게이트를 못 넘는다. 본 문서는 이 hold 의 근거와 **Option A/B/C** 를 정리하고, 현재 기본 = **Option A** 임을 명시한다.

---

## 1. literature_only hold 대상 (현재 hold·승격 금지)

| 후보군 | 관계(문헌상) | 허가사항(MFDS) 상태 | 비고 |
|---|---|---|---|
| **스타틴 × CoQ10** | 스타틴이 메발론산 경로로 CoQ10 합성 감소(문헌) | 국내 허가사항에 CoQ10 동거어 **미기재** | name_only 합 큰 coverage 레버이나 허가사항 근거 없음 |
| **H2차단제 × B12** | 위산 저하 → B12 흡수 감소(문헌) | 허가사항 B12 동거어 **미기재**(파모티딘·니자티딘·라푸티딘 확인) | + B12 = 결정론적 detector 부재(5영양소 밖) |
| (참고) PPI × B12 | 동 기전(문헌) | B12 자체는 detector 부재 | PPI 의 Mg/철 흡수는 별도(허가사항 동거 가능) |

- 이번 batch2 Top100 precheck 에서도 스타틴(31·52·76·combo)·H2(30·88·89) 는 **rejected_precheck(literature_only)** 로 분리. fetch 하지 않음(허가사항에 동거어 없을 것이 확실 + B12/CoQ10 detector 부재).
- **detector 부재 영양소(B12·엽산·CoQ10·비타민D·비타민C·나트륨 등)는 결정론적 source check 자체가 불가** → literature_only 와 별개로도 현재 트랙에서 confirmed 될 수 없다.

---

## 2. 왜 hold 인가 (정체성·안전)

1. **정체성:** MediStack 은 "식약처 허가사항 기반" 참고정보다. 이차문헌을 근거로 relation 을 만들면 **천장이 바뀐다**(허가사항 → 문헌). 이는 제품 정체성·신뢰·법적 노출에 영향을 주는 **정책 결정**이지 데이터 작업이 아니다.
2. **검증 가능성:** 허가사항은 단일 공식 출처(nedrug)로 결정론적 재검증이 가능하다. 이차문헌은 출처·등급·해석이 다양해 자동 게이트가 어렵다.
3. **과다해석 위험:** 문헌의 "연관" 을 사용자에게 "이 약이 이 영양소를 고갈시킨다" 로 강하게 전달할 위험. 참고정보 톤·안전선과 충돌 여지.

---

## 3. 향후 선택지 (Option A / B / C)

| Option | 정의 | coverage 영향 | 정체성/리스크 | 상태 |
|---|---|---|---|---|
| **A (현재 기본)** | **허가사항 직접근거만** 허용. 이차문헌만이면 hold | 보수적(작음) | 정체성 유지·리스크 최저 | ✅ **현재 적용** |
| **B** | 공신력 있는 **이차문헌까지 draft 허용**(예: AHFS·식약처 의약품안전사용정보·동료심사 메타분석) | 큼(스타틴/H2 등 해금) | 정체성 변경("허가사항 기반"→"근거 기반")·출처 등급 체계 필요 | 미채택(PM 결정) |
| **C** | 허가사항은 그대로, **이차문헌은 약사/임상 검수 후 별도 `reviewed_reference` 트랙**으로만 분리 표기 | 중간(검수 병목) | 정체성 보존 + 확장 여지·reviewer 확보 전제 | 미채택(PM 결정) |

### 각 Option 채택 시 선결 조건

- **B:** ①허용 이차문헌 출처 화이트리스트 정의 ②출처 등급 필드(evidence_tier) 스키마 ③문헌 인용 검증 절차 ④사용자 카피에 "허가사항 기반" 문구 정정 ⑤법적 검토(참고정보 책임 범위).
- **C:** ①`reviewed_reference` 트랙 스키마(reviewed_by/reviewed_at/source_tier) ②clinical reviewer 확보 ③허가사항 트랙과 UI 분리 표기("허가사항" vs "검수된 참고문헌") ④published/clinical 천장 정책과 정합.

---

## 4. 현재 정책 (불변 · 본 라운드 적용)

- **기본 = Option A.** 허가사항 직접 동거어만 source_confirmed → draft → (PM 승인 시) live.
- 이차문헌만 근거인 후보 = **hold**(스타틴×CoQ10·H2×B12 등). impact 가 커도 승격 금지.
- detector 부재 영양소(B12·CoQ10·비타민D 등) = 현재 트랙에서 source check 불가 → 자동 hold.
- Option B/C 전환은 **PM + (C는 clinical reviewer) 별도 결정** 후에만. 본 라운드는 정책 변경 0.

---

## 5. PM 판단 필요사항

1. literature_only 레버(스타틴×CoQ10·H2/PPI×B12)에 **이차문헌 허용 여부** — Option A 유지 vs B vs C.
2. B/C 채택 시 §3 선결조건(출처 화이트리스트·evidence_tier 스키마·reviewer) 착수 여부.
3. detector 확장(B12·비타민D 등) 은 source 천장 정책과 묶인 문제 — Option 결정 후 검토.

> **안전 원칙:** 허가사항에 없으면 노출 금지(현재) / 이차문헌 근거는 정책 결정 전 hold / "허가사항 기반" 정체성은 Option 변경 없이는 불변 / 사용자 카피에 근거 등급 과장 금지.
