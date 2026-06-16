# MediStack — Relation Factory v1.4 Reviewer Package (적대검증 통과분)

> **clinical reviewer / PM 핸드오프 문서. live 아님.** factory 43 draft → 적대검증(refute-by-default 10-lens) 후
> **reviewer-ready 37**(survives 31 + survives_with_copy_change 6)만 본 패키지에 포함. 강등 6(needs_review 5·hold 1)은 §6.
> 정본 데이터: `data/drafts/relation_factory_reviewer_ready_batch_v1_4.json` · 판정 근거 `data/review/relation_factory_adversarial_verify_v1_4.json`.
>
> ⚠️ **`reviewer_ready` 는 자동 검증 렌즈 통과를 의미하며 `clinical_reviewed=true`·식약처 승인·약사 검수 완료·법적 문제 없음 을 의미하지 않는다.**
> ⚠️ 본 패키지의 어떤 항목도 제품/구매/제휴·보충제 추천·복용 지시가 아니다. 전건 `published=false`·`reviewed_by` 공란.

## 1. 범위·제외

| 구분 | 수 | 비고 |
|---|---|---|
| reviewer-ready (survives) | 31 | 라벨 직접 quote·방향 일치·중복 0 |
| reviewer-ready (survives_with_copy_change) | 6 | quote 정비/카테고리 note 후 유지 |
| **소계(본 패키지)** | **37** | reviewer note 후 dry-run integrator → 별도 PR |
| 강등(제외) | 6 | needs_review 5 · hold 1 (§6) |

전건 `live_integration_forbidden=true` · `do_not_implement_yet=true`.

## 2. family 별 후보

### F1 Fluoroquinolone × mineral/antacid (18, 전건 survives)
| 약물 | counterpart | id | section |
|---|---|---|---|
| 노르플록사신 | 철분 / 칼슘 / 아연 / Al·Mg제산제 | 0021/0022/0024/0025 | 병용투여 |
| 레보플록사신 | Al/Mg제산제 | 0010 | 병용투여 |
| 로메플록사신 | Al/Mg제산제 | 0035 | 병용투여 |
| 발로플록사신 | Al/Mg제산제 | 0040 | 상호작용 |
| 오플록사신 | Al/Mg제산제 | 0020 | 병용투여 |
| 자보플록사신 | 철분 / 칼슘 / 아연 / Al·Mg제산제 | 0041/0042/0044/0045 | 병용투여 |
| 토수플록사신 | 철분 / 칼슘 / Al·Mg제산제 | 0066/0067/0070 | 병용투여 |
| 페플록사신 | 철분 / 아연 / Al·Mg제산제 | 0026/0029/0030 | 병용투여 |

근거: 전건 라벨이 해당 금속이온/제산제를 직접 명시 + "흡수 저하·효과 저하·투여 전후 N시간 분리" verbatim. mechanism=absorption, action=separation.

### F2 Tetracycline × mineral/antacid (5, 전건 survives)
| 약물 | counterpart | id |
|---|---|---|
| 독시사이클린 | Al/Mg제산제 | 0105 |
| 미노사이클린 | Al/Mg제산제 | 0110 |
| 테트라사이클린 | 철분 / 아연 / Al·Mg제산제 | 0111/0114/0115 |

근거: "칼슘·마그네슘·알루미늄 함유 제산제 또는 이들 양이온…철·아연 함유 제제…테트라사이클린계 약물의 흡수 저하" verbatim.

### F3 Bisphosphonate × mineral/antacid (3)
| 약물 | counterpart | id | verdict |
|---|---|---|---|
| 이반드론산 | Al/Mg제산제 | 0147 | survives (라벨 "알루미늄,마그네슘,철" 명시) |
| 에티드론산 | 칼슘 | 0148 | copy_change (quote 끝 '○ 파제트병' 제거) |
| 에티드론산 | 철분 | 0149 | copy_change (동) |

### F4 Thyroid (1)
| 약물 | counterpart | id | verdict |
|---|---|---|---|
| 레보티록신 | Al/Mg제산제 | 0173 | copy_change (라벨은 '알루미늄 함유 제산제'만 — Al/Mg 통합 category note) |

### F6 Acid-reducer × B12 (1)
| 약물 | counterpart | id | verdict |
|---|---|---|---|
| 에스오메프라졸 | 비타민B12 | 0201 | survives (저위산증 인한 B12 흡수 감소, monitoring) |

→ live 의 타 PPI × B12(란소·라베·오메·판토·덱스란소프라졸) 라인 보완. 톤 일치 확인 요망.

### F9 Chronic-use depletion (8)
| 약물 | counterpart | id | verdict |
|---|---|---|---|
| 카르바마제핀 | 엽산 / 비타민D | 0245 / 0246 | copy_change (표 raw → 핵심부 발췌) |
| 트리메토프림 | 엽산 | 0272 | survives (약한 antifolate — 고위험 MTX/피리메타민과 구분) |
| 페노바르비탈 | 비타민D | 0252 | survives (연용 골연화증) |
| 페니토인 | 엽산 / 비타민D | 0242 / 0243 | survives (혈청엽산치 저하 / 연용 골연화증) |
| 프리미돈 | 비타민D | 0255 | survives (연용 골연화증) |
| 설파살라진 | 엽산 | 0269 | survives (엽산 흡수 저하·결핍) |

mechanism=depletion, action=monitoring. 카드 톤 "장기간 복용 시 수치 변화 가능·상담"(결핍 단정 아님).

### F10 Azole × antacid (1)
| 약물 | counterpart | id | verdict |
|---|---|---|---|
| 케토코나졸 | Al/Mg제산제 | 0275 | copy_change (기전=위산도 의존 흡수·category note) |

## 3. family 별 공통 위험(reviewer 확인 포인트)

- **F1/F2/F3 antacid-drug vs mineral-nutrient 중복**: live 에 동일 약물 × 마그네슘/철분/칼슘(nutrient)이 있는 경우가 많음. Al/Mg 제산제(약물)는 **별도 counterpart**(id61 이트라코나졸 선례). reviewer 가 "antacid-drug relation 을 별도로 유지" 승인 필요.
- **F3 칼슘/철분 nutrient vs antacid 양이온**: 라벨이 "미네랄 첨가 비타민제(보충) / 함유 제산제"를 혼합 서술. live 리세드론산·이반드론산·알렌드론산 × 칼슘(nutrient) 선례로 nutrient 분류 채택 — reviewer 가 분리(또는 antacid 추가) 여부 판단.
- **F4 Al-only 라벨 → Al/Mg category**: 레보티록신 라벨은 알루미늄만 명시. 통합 category 적정성 확인.
- **F6/F9 depletion 프레이밍**: "장기간/연용" 맥락이 라벨 근거와 일치하는지, 결핍 단정 없이 monitoring 톤인지(현재 충족).
- **F9 트리메토프림 antifolate**: 고위험 antifolate(MTX·피리메타민, F11 hold)와 명확히 구분 — 일반 항생제로 monitoring 적정성 확인.
- **F10 기전**: Al/Mg 킬레이션이 아니라 위산도 의존 흡수. 향후 `acid_reducing_drug` category 도입 시 재분류 후보.

## 4. grouping 제안 / subset 통합 우선순위

| 우선 | 그룹 | 후보 | 근거 강도 | 선행조건 |
|---|---|---|---|---|
| 1 | F1/F2 FQ·tetracycline × mineral/antacid | 23 | 강(verbatim·live 동계열 다수) | 없음(중복 0 확인됨) |
| 2 | F9 페니토인/설파살라진 × 엽산·비타민D | 3 | 강(직접 수치저하·연용) | depletion 카드 톤 reviewer 승인 |
| 3 | F3 이반드론산/에티드론산 × mineral/antacid | 3 | 중(에티드론산 quote 정비) | nutrient vs antacid 분리 결정 |
| 4 | F6 에스오메프라졸 × B12 | 1 | 중(저위산증 흡수감소) | live PPI×B12 톤 일치 |
| 5 | F9 카르바마제핀/페노바르비탈/프리미돈/트리메토프림 | 6 | 중(표 발췌·연용·antifolate) | quote 정비·evidence_level 확정 |
| 6 | F4 레보티록신 × Al/Mg · F10 케토코나졸 × Al/Mg | 2 | 중(category note) | category 결정(Al/Mg vs acid_reducing) |

## 5. 선행 PR 필요 여부

- **불필요(즉시 통합 가능 후보)**: F1/F2 — al_mg_antacid category·schema 는 id61 로 이미 live 에 존재. 중복 0.
- **선행 결정 필요**: F10/F4 의 `acid_reducing_drug` category 신설 여부(현재는 al_mg_antacid 로 우회). 신설 시 별도 schema PR.
- **공통**: 본 37건의 live 통합은 **clinical reviewer note + dry-run integrator(예상 count/ids 산출) + 별도 PR** 절차. 본 라운드 live 0.

## 6. 제외(강등) 후보 — 통합 금지

| id | relation | verdict | 사유 |
|---|---|---|---|
| 0139 | 알렌드론산 × Al/Mg제산제 | needs_review | quote 가 generic '제산제'(Al/Mg 미명시), 명시 양이온=칼슘뿐(이미 live). Al/Mg 직접 명시 라벨 재검색 필요 |
| 0260 | 라모트리진 × 엽산 | needs_review | 근거가 랫트 시험 + 임신 한정 — 인체 만성 depletion 일반화 불가 |
| 0257 | 옥스카르바제핀 × 엽산 | needs_review | 엽산 결핍이 저나트륨혈증 이상반응 나열문에 매몰(저신호) |
| 0251 | 페노바르비탈 × 엽산 | needs_review | quote '임신중 투여 엽산 저하' — 임신 한정, 카드 '장기복용' 과일반화 |
| 0254 | 프리미돈 × 엽산 | needs_review | 동(임신 한정 근거 일반화) |
| 0276 | 포사코나졸 × Al/Mg제산제 | hold | quote 가 'H2 수용체 억제제'만 서술 — al_mg_antacid 매핑 불가. acid_reducing_drug category 트랙으로 이관 |

## 7. reviewer note 템플릿(초안)

```
candidate_id:
relation:
reviewer_decision:  approve | approve_with_edit | hold | reject
counterpart_classification_ok:  yes | no(→ )
evidence_level_confirmed:  weak | moderate | high
copy_edit (있으면):
category_decision (F4/F10):  al_mg_antacid | acid_reducing_drug(신설) | nutrient
notes:
reviewed_by:        (확보 후에만 — 현재 공란 유지)
reviewed_at:
```

> 본 패키지로 `clinical_reviewed`/`published` 전환 금지. 실제 승격은 reviewer note 확보 후 별도 버전 PR(CLAUDE.md §6).
