# MediStack v1.4 — live PR reviewer note 실물 템플릿
> NO-LIVE-WRITE PLAN — live 통합 0 · reviewer note 실물 없이는 통합 금지 · published/clinical=false · DATA_URL v0.2 불변. 단일 소스: `data/review/per_family_live_pr_readiness_v1_4.json`.

## 모든 템플릿 공통 필수 항목
- reviewer_id
- reviewed_date
- reviewed_package_version_commit
- family_or_wave_scope
- candidate_ids_full
- relation_count_delta
- grouping_approval
- source_fidelity_approval
- management_copy_conservatism
- published_false_kept
- clinical_reviewed_false_kept
- reviewed_by_blank_kept
- no_product_purchase_affiliate_ui
- schedule_inactive
- needs_review_excluded
- rollback_feasible

## note 에 절대 포함 금지(검토자가 요구/허용해도 거부)
- clinical_reviewed=true 요구
- published=true 요구
- 제품 추천 허용
- 영양제 구매 권유
- 복용해도 된다
- 안전하다
- 진단/처방/치료 지시
- reviewer 실명/면허번호 강제 입력 요구

> checker: `python3 scripts/check_live_pr_reviewer_note_v1_4.py --wave <W> --reviewer-note <note>`

## wave별 템플릿 (승인 candidate 전건 명시)

### f1_nutrient10 (n=10, Δ+10, 60→70)
- 승인 candidate_id: `RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### f1_antacid8 (n=8, Δ+8, 60→68)
- 승인 candidate_id: `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### f2_all5 (n=5, Δ+5, 60→65)
- 승인 candidate_id: `RF-F2-0105`, `RF-F2-0110`, `RF-F2-0111`, `RF-F2-0114`, `RF-F2-0115`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### f3_single (n=1, Δ+1, 60→61)
- 승인 candidate_id: `RF-F3-0147`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### f9_all7 (n=7, Δ+7, 60→67)
- 승인 candidate_id: `RF-F9-0269`, `RF-F9-0246`, `RF-F9-0272`, `RF-F9-0252`, `RF-F9-0242`, `RF-F9-0243`, `RF-F9-0255`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### f4_f6_small2 (n=2, Δ+2, 60→62)
- 승인 candidate_id: `RF-F4-0173`, `RF-F6-0201`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### antibiotic23 (n=23, Δ+23, 60→83)
- 승인 candidate_id: `RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029`, `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030`, `RF-F2-0105`, `RF-F2-0110`, `RF-F2-0111`, `RF-F2-0114`, `RF-F2-0115`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### chronic8 (n=8, Δ+8, 60→68)
- 승인 candidate_id: `RF-F9-0269`, `RF-F9-0246`, `RF-F9-0272`, `RF-F9-0252`, `RF-F9-0242`, `RF-F9-0243`, `RF-F9-0255`, `RF-F6-0201`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

### all33 (n=33, Δ+33, 60→93)
- 승인 candidate_id: `RF-F1-0021`, `RF-F1-0022`, `RF-F1-0024`, `RF-F1-0041`, `RF-F1-0042`, `RF-F1-0044`, `RF-F1-0066`, `RF-F1-0067`, `RF-F1-0026`, `RF-F1-0029`, `RF-F1-0025`, `RF-F1-0010`, `RF-F1-0035`, `RF-F1-0040`, `RF-F1-0020`, `RF-F1-0045`, `RF-F1-0070`, `RF-F1-0030`, `RF-F2-0105`, `RF-F2-0110`, `RF-F2-0111`, `RF-F2-0114`, `RF-F2-0115`, `RF-F3-0147`, `RF-F9-0269`, `RF-F9-0246`, `RF-F9-0272`, `RF-F9-0252`, `RF-F9-0242`, `RF-F9-0243`, `RF-F9-0255`, `RF-F4-0173`, `RF-F6-0201`
- needs_review 제외(승인 대상 아님): `RF-F3-0148`, `RF-F3-0149`, `RF-F9-0245`, `RF-F10-0275`

## 채움 양식 예시 (antibiotic23)
```
검수자: RPH-<id> (PM 승인 근거 첨부)   검토일 YYYY-MM-DD
검토 패키지: per_family_live_pr_readiness v1.4 / commit <hash>
scope(wave=antibiotic23) 승인(approved): 아래 candidate 전건을 verified_reference 노출로 live 통합 승인.
승인 candidate_id 전건: <23 ids>.
relation delta: +23 (60 → 83, 신규 id = runtime max+1).
grouping 승인 / 출처 fidelity 일치 보존 / 관리 문구 보수성 유지 확인.
published=false·clinical_reviewed=false·reviewed_by 공란 유지 승인. 제품·구매·제휴 UI 없음. schedule 비활성.
needs_review <4 ids> 제외 확인. rollback 가능 확인.
```
> `검토일 YYYY-MM-DD`·`SAMPLE`·`PLACEHOLDER` 등은 placeholder 로 자동 거부된다(실날짜·실 commit 필요).
