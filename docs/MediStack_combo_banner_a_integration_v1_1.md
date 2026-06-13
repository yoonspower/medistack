# MediStack — 복합제 고지 배너(공존성분 명시) + relation_card flip (2순위 A 43건) 라이브 통합 v1.1

> 작성일: 2026-06-13. **라이브 통합 완료.** PM 승인(복합제 검토 v1.1 로드맵 **2순위**: A 비스포스포네이트(리세드론산/이반드론산) + 비타민D3 복합제 **43건**). 선행: `MediStack_combo_relation_review_v1_1.md`, `MediStack_combo_banner_bd_integration_v1_1.md`(1순위).
>
> B/D(1순위)와 달리 **배너 문구에 공존 성분(비타민D)을 명시하는 최소 src 변경 포함**(PM 선택). 통합기: `scripts/integrate_combo_banner_a_v1_1.py`. DATA_URL=v0.2 in-place.

---

## 0. 변경 요약

| 항목 | 통합 전(B/D 후) | 통합 후 | 비고 |
|---|---|---|---|
| relation_card | 1,011 | **1,054** | **+43** (리세드론산 42·이반드론산 1 flip) |
| name_only | 16,569 | **16,526** | −43 |
| full index total | 17,580 | **17,580** | **유지** |
| product_aliases | 618 | **661** | **+43** (is_combination=true·other_label=비타민D) |
| alias_count | 656 | **699** | +43 |
| verified_item_seqs | 998 / 20 | **1,041 / 20** | +43 (리세드론산 76→118·이반드론산 72→73) |
| relations (export) | 41 | **41** | **불변**(신규 relation 0) |
| DATA_URL | v0.2 | **v0.2** | **불변** |
| published / clinical_reviewed | false | **false** | 봉인 유지 |

> **복합제 고지 배너 적용 = 43건. relation_card 증가 = +43.**

---

## 1. 안전 게이트 — 무조건 flip 하지 않고 2단계 검증

A 는 base 의 relation 이 ×칼슘인데 복합제 공존 성분은 비타민D3(칼슘 아님)라, **카드 "칼슘"을 제품 속 D3로 오인**할 소지가 1순위와 다른 리스크였다. 그래서 무조건 flip 하지 않고 적대적 안전 검증을 2회 돌렸다.

**1차(기존 일반 배너 "다른 성분"):** 3관점 중 2(일반 사용자·규제/표시)가 **medium 오인위험** → flip 보류. 검토 문서 §2-A 의 "별도 복용 칼슘 제품임을 명확화하는 문구 필요" 판정과 일치.

**조치(PM 선택 = 배너에 공존성분 명시):** render.js 배너가 공존 성분이 있으면 "다른 성분" 대신 그 라벨(비타민D)을 명시하도록 최소 변경. 카드의 "칼슘"과 배너의 "비타민D"를 서로 다른 명사로 병치 → 융합 차단.

**2차(공존성분 '비타민D' 명시 배너):**
- 일반 사용자 → **resolved·low·flip_now** (D≠칼슘 명사 구분으로 융합 끊김. 남는 의문은 잘못된 복약행동 유발 안 함).
- 규제/표시 → **resolved·low·flip_now** (부분정보 오인 차단. 원문초과·추천성 표현 없음).
- ⚠️ **skeptic(신규 적대 렌즈) → still_needs_more·medium** (반대의견, 아래 §1-A).

원래 A 를 막았던 두 관점이 모두 해소되어 **진행**하되, skeptic 반대의견을 본 문서에 명시해 PM 이 검토·되돌릴 수 있게 한다(되돌림=git revert).

### 1-A. skeptic 반대의견 (PM 검토용, 비차단 기록)
- **핵심**: 배너가 공존성분을 '비타민D'로 명시한 것은 D≠칼슘 토큰 구분엔 도움되나, **불변인 칼슘 카드(id40/41)에 "이 칼슘은 별도 복용 칼슘 제품을 가리킨다"는 맥락이 없다**. 사용자가 "내 약엔 칼슘이 아니라 D가 들었다(배너도 D 확인)→칼슘 경고는 나와 무관"이라 읽고 **실제 적용돼야 할 분리복용 권고를 버릴(under-application)** 소지를 medium 으로 봄.
- **부가**: D3는 칼슘 흡수를 높이는 짝성분(골다공증 '칼슘+D' 통상 병용)이라 배너의 'D' 노출이 D-칼슘 연상을 강화할 수 있다는 지적.
- **현 통합의 완화 근거**: 칼슘 카드의 분리복용 문구("칼슘이 함유된 제품을 같은 시간에 복용하면…시간 간격 권장")는 **화면에 그대로 노출**되며 배너가 그것을 무효화하지 않는다. 배너는 "정보 미포함" 범위에 머물 뿐 카드의 적용 여부를 부정하지 않는다.
- **후속 강화 옵션(미적용)**: 분리(separation)-action 카드가 복합제로 도달했을 때 카드/배너에 "위 영양소는 함께 복용하는 다른 제품 기준이며 이 제품 성분이 아님"을 명시. 카드 의미 수정이 필요해 별도 PM 결정으로 분리(이번 범위 밖).

---

## 2. 한 일 (데이터 + 최소 src)

1. **render.js / guards.js(승인된 최소 src, +32/−2)**: 복합제 alias 에 `combination_other_label` 이 있으면 배너가 "함께 포함된 **{라벨}** 성분에 대한 정보는 포함하지 않습니다"로 명시. 라벨 부재 시 기존 "다른 성분"(메트포르민/알렌드론산/오메프라졸/HCTZ/라베프라졸 **257 combo 불변**·후방호환).
2. **full index flip (43)**: A 43건 name_only → relation_card. (relation_card⟺pool 불변식 충족)
3. **aliases**: verified_item_seqs[리세드론산]+42·[이반드론산]+1(pool 진입) + product_aliases +43(is_combination=true·basis=리세드론산/이반드론산·notice=true·**combination_other_label="비타민D"**·source_relation_ids=[40] 또는 [41]).

**배너 실측(라이브 데이터)**:
> 리세드론산 제품 → "표시된 약-영양소 참고 정보는 **리세드론산** 성분을 기준으로 하며, 함께 포함된 **비타민D** 성분에 대한 정보는 포함하지 않습니다."
> 이반드론산 제품 → "…**이반드론산** 성분을 기준으로 하며, 함께 포함된 **비타민D** 성분에 대한 정보는 포함하지 않습니다."

---

## 3. 금지 준수

- ✅ **A 43건만**(리세드론산 42·이반드론산 1). **E(라베+산화Mg 1)·C(라베+칼슘 6) name_only 유지 실측확인** — 절대 미변경.
- ✅ **신규 relation 0**(export relations 41 불변). DATA_URL=v0.2 불변. published/clinical_reviewed false 유지. **tag 없음**.
- ✅ **칼슘/비타민D 추천 0**: 배너는 "정보 미포함·허가사항 확인" 안내뿐. 복용지시·추천·구매·제품 0.
- ✅ src 변경은 **승인 범위(배너 공존성분 명시)뿐** — guards.js(otherLabel 파싱·라벨맵)·render.js(조건부 문구). 기존 combo·HCTZ·potassium 동작 불변(스모크 검증).

---

## 4. 검증 (전부 PASS)

| validator / smoke | 결과 |
|---|---|
| v0.1 / v0.2 export | PASS (export 무변경) |
| validate_medistack_v0_3_aliases | PASS (16/16, #14 other_label orphan 가드·#15 basis allowlist 리세드론산/이반드론산) |
| validate_alias_surface_forms | PASS (5/5, 신규 43 alias·verified item_name) |
| validate_full_drug_name_index | PASS (31/31, product 661·verified 1041/20·relations 41) |
| validate_potassium_name_only_policy | PASS (8/8, name_only 16,526·relation_card 1,054) + selftest PASS |
| smoke_search_regression | PASS (**combo_notice_a**: 리센플러스정 count 1·comboBases [리세드론산] + **combo_render_a**: 배너 "비타민D 성분에 대한 정보는 포함하지 않습니다"·일반 "다른 성분" 미노출) |
| smoke_disclaimer / alias / hctz | PASS (기존 combo·HCTZ 배너 무회귀 — 일반 "다른 성분" 유지) |
| test_validate_v0_3_combo / combo_ar / typeB | PASS (9/9 · 13/13 · 7/7) |

---

## 5. 갱신된 validator 상수

- `validate_medistack_v0_3_aliases.py`: `COMBO_ALLOWED_BASIS` += 리세드론산·이반드론산. #14 에 `combination_other_label` orphan/빈값 가드.
- `validate_full_drug_name_index.py`: product 618→661 · alias_count 656→699 · verified 998/20→1041/20.
- `validate_potassium_name_only_policy.py`: name_only 16,569→16,526 · relation_card 1,011→1,054.
- `fixtures/search_regression_v1_0.json`: size 16,569→16,526 + combo_notice_a/combo_render_a + data_basis.

---

## 6. 잔여 / 후속 (별도 PM)

- **로드맵 3순위 C(PPI+칼슘 18건)**: PPI×칼슘(저산성 탄산칼슘 흡수↓) relation 신규(허가사항 출처) 후 배선.
- **영구 금지 E(라베+산화Mg 1건)**: Mg 직접모순.
- **A skeptic 후속(선택)**: 분리-action 카드의 복합제 맥락 강화(§1-A). 카드 의미 수정 동반 → 별도 PM.

> 되돌림은 git revert(데이터 3 + src 2 + validator/fixture). in-place(DATA_URL v0.2 유지).
