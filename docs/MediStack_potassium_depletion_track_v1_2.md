# MediStack — 칼륨 depletion/monitoring 트랙 문구 통일 v1.2

작성일: 2026-06-14 · 상태: **DESIGN / HOLD (live 승격 없음)** · 대상 AI 세션 핸드오프용 자기완결 문서

## 0. 목적과 범위

칼륨(potassium) 고갈/모니터링 방향 draft relation 6건의 **사용자 노출 문구(display/management)를 단일 템플릿으로 통일**하고,
각 draft의 승격 준비도와 보류 사유를 정리한다. **이번 작업에서 어떤 칼륨 draft도 live 승격하지 않는다.**

- 대상: DF01 메틸프레드니솔론 · DF02 덱사메타손 · DF03 플루드로코르티손 · DF04 아세타졸아미드 · DF05 아조세미드 · CQF03 히드로코르티손
- 모두 `nutrient=칼륨`, `mechanism=depletion`, `recommended_action=monitoring`, `evidence_level=high`, `source_confirmed=true`.
- 정책 불변: `potassium_safety_card=true` · `product_link_allowed=false` · `published=false` · `clinical_reviewed=false` · `reviewed_by` 공란.
- 칼륨 트랙은 **고/저칼륨혈증 양방향 임상 위험**이 커서, 근거가 충족되어도 트랙 단위로 보수적 hold(통일 문구 + PM 승인 + clinical reviewer 노트 확보 전까지).

> 비대상(혼동 주의): DF06 리오티로닌×칼슘 / DF07 리오티로닌×철분 은 **칼슘/철분 absorption** 트랙이며 이미 live(id 57·58). 본 문서와 무관.

## 1. 확정 문구 템플릿 (potassium depletion/monitoring 전용)

장기·고용량·진료/복약상담 맥락을 유지하고, 보충 권유·결핍 단정·제품 연결을 하지 않는다.

### display (상태 영향 고지)
```
이 약을 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어,
진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.
```

### management (관리 안내)
```
칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요.
```

### 약물명 삽입 변형(렌더 시 주어 명시가 필요한 경우)
display 앞에 약물명을 두는 변형도 동일 의미로 허용한다(엔진 카피 규칙과 일치하는 형태 택1, 트랙 내 일관 유지):
```
{약물명}을(를) 장기간 복용하거나 고용량으로 사용하는 경우 칼륨 상태에 영향이 있을 수 있어,
진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다.
```

### 설계 근거 / 금지선
- **"장기간·고용량" 조건절 추가**: 코르티코스테로이드·이뇨제의 칼륨 영향은 용량·기간 의존적이다. 무조건적 "영향이 있습니다"는 원문보다 강함 → 조건절로 충실성 확보.
- **"확인이 필요한지 문의해볼 수 있습니다"**(단정 회피): 모니터링 필요를 단정하지 않고 상담 트리거만 제공.
- **management는 "임의 보충 금지 + 상담 결정"**: 칼륨 과보충은 고칼륨혈증 위험 → 보충 권유/제품 연결을 명시적으로 차단.
- 금지: 복용하세요 / 반드시 드세요 / 추천합니다 / 영양제를 드세요 / 결핍입니다(단정) / 구매·제휴·제품추천 / 칼륨 제품 링크.
- 금지어 스캐너(`validate_forbidden_phrases_v1_2.py`) 통과 전제.

### 현재 draft 문구와의 차이(승격 시 정규화 대상)
현행 DF01-05·CQF03 draft의 display/management는 아래 구문이라 **승격 시 위 통일 템플릿으로 교체**해야 한다(현 draft JSON은 본 작업에서 미변경).

| 항목 | 현행 draft 문구 | 통일 템플릿(승격 시 적용) |
|---|---|---|
| display | "…복용하는 경우 칼륨 상태에 영향이 있을 수 있어, 상태 확인이 필요할 수 있습니다." | "…**장기간 복용하거나 고용량으로 사용하는 경우** 칼륨 상태에 영향이 있을 수 있어, **진료나 복약상담 시 칼륨 상태 확인이 필요한지 문의해볼 수 있습니다**." |
| management | "칼륨은 임의로 **보충하면 위험할 수 있으므로**, 보충 여부는 **반드시** 의사 또는 약사와 상담하세요." | "칼륨은 임의로 **보충하지 말고**, 보충 여부는 의사 또는 약사와 **상담해 결정하세요**." |

차이 핵심: ①조건절(장기/고용량) 신설 ②모니터링 단정 완화(필요 → 필요한지 문의) ③management 군더더기 완화(동일 의미, 톤 정돈).

## 2. draft별 승격 가능 / 보류 사유 표

근거(evidence)는 6건 모두 충족(허가사항 직접 동거어 + 저칼륨 방향 일치, source_confirmed high). **현재 상태는 전건 HOLD**이며 사유는 트랙 정책(칼륨 양방향 위험)이다. 근거 부족으로 인한 보류는 없다.

| draft | 약물 | itemSeq | 허가사항 직접 근거(요지) | 근거 상태 | 승격 준비도 | per-draft 주의 |
|---|---|---|---|---|---|---|
| DF01 | 메틸프레드니솔론 | 199800324 | 체액·전해질: "칼륨손실, 저칼륨성 알칼리혈증" | confirmed high | ready | 글루코코르티코이드, 라벨 직접근거 명확 |
| DF02 | 덱사메타손 | 202203949 | 체액·전해질: "저칼륨성 알칼리혈증" | confirmed high | ready | 미네랄코르티코이드 작용 약하나 **라벨 직접 동거어 보유** → 채택 가능 |
| DF03 | 플루드로코르티손 | 199907231 | 체액·전해질: "칼륨소실, 저칼륨성 알칼리혈증" | confirmed high | ready(주의) | 강한 MC. **국내 유통 적음**(플로리네프정 1품목) → 품목 가용성 재확인 후 승격 |
| DF04 | 아세타졸아미드 | 201403403 | 대사: "저칼륨혈증 … 전해질평형실조" | confirmed high | ready | 탄산탈수효소억제 이뇨작용. 녹내장/고산병 적응증 |
| DF05 | 아조세미드 | 199001306 | 대사: "저칼륨혈증 … 전해질평형실조" | confirmed high | ready | 루프이뇨제(유레틴정). 국내 유통 명확 |
| CQF03 | 히드로코르티손 | 200703172 | 체액·전해질: "칼륨배설증가에 의한 저칼륨혈증", "칼륨손실" | confirmed high | ready | 래피손정 단일 경구 tablet. 외용 비중 큰 성분이라 전신 제형 한정 |

보류(HOLD) 공통 사유: **칼륨 트랙 정책** — (a) 통일 문구 미적용, (b) PM 승인 미확보, (c) clinical reviewer 노트 미확보, (d) 고칼륨/저칼륨 양방향 임상 위험으로 absorption 트랙보다 보수적 게이트 적용.

## 3. 다음 PM 승인 시 live 승격 프롬프트 초안

> ⚠️ 초안일 뿐 실행 지시가 아니다. PM 승인 + clinical reviewer 노트 확보 후에만 사용.

```
MediStack 칼륨 depletion/monitoring 트랙 live 승격 (PM 승인 후).

전제(미충족 시 STOP):
- clinical reviewer 노트 확보(칼륨 행은 reviewer 트랙 천장).
- 통일 문구 템플릿(docs/MediStack_potassium_depletion_track_v1_2.md §1) 적용.
- potassium_safety_card=true · product_link_allowed=false · published=false · clinical_reviewed=false · reviewed_by 공란 유지.

대상(승격 순서 = 근거·유통 명확도 순): DF01 메틸프레드니솔론 → DF04 아세타졸아미드 → DF05 아조세미드 → CQF03 히드로코르티손 → DF02 덱사메타손 → DF03 플루드로코르티손(유통 재확인 후).

수행:
1) 멱등 통합기(integrate_coverage_queue_cqf02_v1_2.py / CQF01 패턴 승계, 칼륨 가드 분기):
   - 각 draft를 export relations에 append(연속 id). draft-전용 필드 strip, source {type,url,pointer(+확인일)} 정합.
   - ⚠️ 칼륨 행이므로 absorption 가드(potassium 차단)를 **칼륨 허용 + depletion 전용 가드**로 교체:
     mechanism=depletion · nutrient=칼륨 · potassium_safety_card=true · product_link_allowed=false · adversarial_verified=true · source_confirmed=true · source itemSeq 보유.
   - display/management는 §1 통일 템플릿으로 기록(현행 draft 문구 정규화).
2) full index: 각 약물 단일성분 name_only → relation_card flip(복합·변형 성분명은 보수적 name_only 유지). counts·verified_item_seqs 갱신.
3) 신규 칼륨 통합 validator(validate_*_integration) + potassium_name_only_policy + forbidden phrase scanner + 회귀 전수.
4) 회귀 baseline(relations·relation_card·name_only·verified) 갱신, CQF_IDS/DF 승격분 반영.
5) live HTTP 200 / deploy success / git clean / commit.

금지: published/clinical 전환 · reviewed_by 기재 · 칼륨 제품 링크 · 보충 권유 · 결핍 단정 · 구매/제휴.
```

## 4. 검증 체크리스트(승격 시)
- [ ] clinical reviewer 노트 확보(칼륨 천장 해제 근거)
- [ ] §1 통일 문구로 display/management 정규화
- [ ] potassium_safety_card=true · product_link_allowed=false 전건
- [ ] forbidden phrase scanner 0 (보충 권유/결핍 단정/제품 0)
- [ ] DF03 플루드로코르티손 국내 단일 경구 품목 가용성 재확인
- [ ] 회귀 전수 PASS · DATA_URL v0.2 불변 · published/clinical false 유지
