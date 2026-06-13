# MediStack — 버퍼-콤보 고지 배너 + relation_card flip (케이스 C: PPI+침강탄산칼슘 18건) 라이브 통합 v1.1

> 작성일: 2026-06-14. **라이브 통합 완료.** PM 승인(장기 작업 지시 2026-06-14, 작업3 조건 전부 충족). 선행: `MediStack_ppi_calcium_combo_review_v1_1.md`(source 확인), `MediStack_ppi_calcium_combo_reclassification_v1_1.md`(buffer_combo 재분류 결정), `MediStack_combo_banner_a_integration_v1_1.md`·`MediStack_combo_banner_bd_integration_v1_1.md`(동일 패턴 선례).
>
> **src 변경 0.** 배너 렌더는 render.js v0.7 `.combobox` + v1.1 `otherLabel` 경로로 이미 라이브. 통합기: `scripts/integrate_combo_banner_c_v1_1.py`. DATA_URL=v0.2 in-place. **신규 relation 0.**

---

## 0. 변경 요약

| 항목 | 통합 전(A 후) | 통합 후 | 비고 |
|---|---|---|---|
| relation_card | 1,054 | **1,072** | **+18** (란소프라졸 12·라베프라졸 6 flip) |
| name_only | 16,526 | **16,508** | −18 |
| full index total | 17,580 | **17,580** | **유지** |
| product_aliases | 661 | **679** | **+18** (is_combination=true·other_label=완충성분) |
| alias_count | 699 | **717** | +18 |
| verified_item_seqs | 1,041 / 20 | **1,059 / 20** | +18 (란소프라졸 39→51·라베프라졸 209→215) |
| relations (export) | 41 | **41** | **불변**(신규 relation 0) |
| DATA_URL | v0.2 | **v0.2** | **불변** |
| published / clinical_reviewed | false | **false** | 봉인 유지 |

> **버퍼-콤보 고지 배너 적용 = 18건. relation_card 증가 = +18.** E(라베+산화Mg) 1건은 name_only 유지(미접촉).

---

## 1. 왜 buffer_combo 인가 (재분류 근거 승계)

C 18품목은 전부 **PPI 성분(란소프라졸/라베프라졸) + 침강탄산칼슘** 복합제다. 침강탄산칼슘은 라벨상 *"약알칼리성 약물로서 위산을 중화"* 하는 **완충/제산 성분**이며 영양 칼슘이 아니다. 따라서:

- **PPI×칼슘 흡수 relation 은 만들지 않는다**(허가사항 출처 0/22 — `ppi_calcium_combo_review_v1_1.md`). 신규 relation 0.
- 표시 카드는 **제품에 실재하는 PPI 성분 기준**(란소프라졸 ×B12·×Mg = id36/37, 라베프라졸 ×B12·×Mg = id32/33)만.
- 공존 성분(침강탄산칼슘)은 **버퍼-콤보 배너로 고지**하되, "칼슘"이 아니라 **기능명**으로 표기 → 영양 칼슘/칼슘 보충 오독 차단.

기능상 C 는 B(라베+탄산수소나트륨 완충)와 **동일 범주**다. B/D·A 가 통과한 *"공존 성분은 카드 영양소가 아님을 배너로 분리"* 패턴을 그대로 승계한다.

---

## 2. ★C 고유 설계 — other_label 은 "칼슘"이 아니라 완충 기능명

MediStack 은 *다른 약*에 대해 칼슘 흡수 relation(퀴놀론·테트라·비스포 ×칼슘)을 이미 보유한다. C 배너에 단순히 "칼슘"이라 쓰면 (ㄱ) 영양 칼슘 오인, (ㄴ) 다른 화면의 칼슘 경고와 혼선 위험이 있다.

→ 채택: **`combination_other_label = "위산 중화 완충 성분(침강탄산칼슘)"`**. 칼슘을 *기능*으로 규정해 보충 권유 오독을 사전 차단한다(라벨 원문 "위산을 중화" 승계 — 원문 초과 없음).

라이브 배너 실제 렌더(검증됨):

> *"이 제품은 둘 이상의 성분을 가진 복합제입니다. 표시된 약-영양소 참고 정보는 **란소프라졸/라베프라졸** 성분을 기준으로 하며, 함께 포함된 **위산 중화 완충 성분(침강탄산칼슘)** 성분에 대한 정보는 포함하지 않습니다. 전체 성분은 의약품 허가사항(첨부문서)을 확인하세요."*

> ⚠️ 렌더 템플릿이 라벨 뒤에 " 성분에 대한 정보"를 덧붙이므로 "…완충 성분(침강탄산칼슘) **성분**에 대한…"으로 '성분'이 한 번 더 나온다. 의미상 정확하나 미세한 중복. 향후 다듬으려면 render.js 템플릿(src) 수정이 필요하므로 **별도 PM 라운드**로 둔다(이번 통합은 src 무변경 원칙 유지).

---

## 3. 수행 내역 (데이터-only, A/B·D 패턴 승계)

권위 목록 = `data/ppi_calcium_combo_reclassification_v1_1.csv`(18 item_seq · 란소 12 / 라베 6). 통합기 `scripts/integrate_combo_banner_c_v1_1.py`(idempotent · `--dry-run` 지원).

1. **full index**: 18건 `name_only → relation_card`(`covered_by_relation=true`·`no_relation_notice_required=false`). meta.counts 갱신.
2. **verified_item_seqs[PPI] += 18**(pool 진입·alias #8 충족): 란소프라졸 +12, 라베프라졸 +6.
3. **product_aliases += 18**: `is_combination=true`·`combination_basis_ingredient=PPI`·`combination_notice_required=true`·`source_relation_ids=[36,37]`(란소)/`[32,33]`(라베)·`combination_other_label="위산 중화 완충 성분(침강탄산칼슘)"`.
4. **validator 상수 동기화**(scripts/ 한정·라이브 src 무변경):
   - `validate_medistack_v0_3_aliases.py`: `COMBO_ALLOWED_BASIS` 에 **란소프라졸** 개방(라베프라졸은 B/D 로 기개방).
   - `validate_full_drug_name_index.py`: 불변 핀 alias_count 699→717·product 661→679·vis 1041→1059.
   - `validate_potassium_name_only_policy.py`: 카운트 핀 name_only 16,526→16,508·relation_card 1,054→1,072.
   - `fixtures/search_regression_v1_0.json`: name_only_index_size 16,526→16,508 + `combo_notice_c`·`combo_render_c` 신규 픽스처.

---

## 4. 검증 (전부 PASS)

배포 게이트 7 + smoke 4 + validator 단위테스트 3 + 비게이트 combo = **전부 exit 0**.

- 게이트: v0_1 / v0_2 / v0_3_aliases / alias_surface_forms / full_drug_name_index / potassium_policy / potassium_selftest — **PASS**.
- smoke: search_regression / disclaimer_render / hctz_disclosure / alias_regression — **PASS**.
- C 픽스처(`combo_notice_c` 8건 + `combo_render_c` 18건) — **PASS**. 배너에 `위산 중화 완충 성분(침강탄산칼슘)` 표시 확인, `칼슘 보충`·`구매`·`제품 추천`·`칼륨 주의` 미표시 확인.
- 회귀: A(비타민D 43)·B/D(라베 None-label 35·메트/알렌/오메/HCTZ)·E(라피듀오 name_only·pool 미진입) **불변**.

---

## 5. 안전 준수 / 되돌리기

- ✅ 신규 relation 0 · relations 41 불변 · DATA_URL v0.2 불변 · src 무변경 · published/clinical false.
- ✅ 제품/구매/제휴/영양제 추천 0. 칼슘 보충 권유 표현 0(오히려 그 오독 방지를 설계 원칙으로 명시).
- ✅ E(라베+산화Mg) name_only 유지. 칼륨 정책 무관(C 에 칼륨 없음).
- **되돌리기**: 데이터-only 통합이므로 `git revert <commit>` 로 full index/aliases/validator 핀이 함께 원복된다. 통합기는 idempotent 라 재실행해도 중복 추가 없음.
