# MediStack — 케이스 C(PPI+침강탄산칼슘 18건) 재분류 + 향후 배너 설계 정책 v1.1

> **⏩ 후속(2026-06-14): 본 문서의 §3 "향후 flip" 이 PM 승인으로 실행됨 → C 18건 relation_card flip 완료. 통합 내역·검증은 `MediStack_combo_banner_c_integration_v1_1.md` 참조.** 본 문서는 재분류 *결정* 기록(아래 §0~§5 는 결정 당시 "flip 0" 기준 원문 보존).

> 작성일: 2026-06-14. **문서/CSV/정책 정리 전용 — 라이브 데이터 무변경.** PM 결정(옵션 나): C 18건을 *PPI×칼슘 relation_card 후보*가 아니라 **"칼슘 완충/제산 성분이 포함된 복합제(buffer_combo)" 트랙**으로 재분류한다. **단 이번 단계는 flip 금지·name_only 유지**, 향후 combo banner/notice 설계 필요 여부만 문서화.
>
> 선행 근거: `MediStack_ppi_calcium_combo_review_v1_1.md`(source 확인 — PPI×칼슘 흡수 신호 0/22, 칼슘=완충제 18/18). 산출물 = 본 문서 + `data/ppi_calcium_combo_reclassification_v1_1.csv`(18행). **export/full index/alias/relation/src/DATA_URL 수정 0. flip 0. published/clinical_reviewed false 유지.**

---

## 0. 한 줄 결론

**C 18건 = "칼슘 완충/제산 성분 복합제(buffer_combo)" 로 재분류 확정.** PPI×칼슘 relation 은 더 이상 전환 전제가 아니다(허가사항 출처 없음·칼슘은 영양소가 아니라 위산 중화 완충제). C 는 기능상 **B(PPI+탄산수소나트륨 완충) 계열**이다. **이번 단계는 name_only 유지(flip 0).** 향후 flip 은 PM 승인 시 **버퍼-콤보 배너**(기존 인프라·신규 relation 0)로 가능하며, 그때 `combination_other_label` 은 **"칼슘"이 아니라 "위산 중화 완충 성분(침강탄산칼슘)"** 으로 표기해야 한다.

---

## 1. 재분류 — 무엇이 바뀌나

| 항목 | 기존(복합제 검토 v1.1) | 재분류(본 문서) |
|---|---|---|
| C 분류 | 3순위 hold, 전제 = **"PPI×칼슘 흡수↓ relation 신규(허가사항 출처)"** | **buffer_combo 트랙**(B/D 계열) — 신규 relation **불필요** |
| 전제의 상태 | 미충족(보류) | **폐기**(전제 자체가 틀림: 허가사항 PPI×칼슘 0/22 + 칼슘=완충제) |
| 현재 표시 | name_only | **name_only 유지(불변)** |
| 향후 전환 경로 | PPI×칼슘 relation 작성(불가) | 버퍼-콤보 배너 배선(PM 승인 시·신규 relation 0) |

**근거(요지)**: 18품목 전부 라벨이 침강탄산칼슘을 *"약알칼리성 약물로서 위산을 중화"* 하는 **완충/제산 성분**으로 규정. 영양 칼슘이 아니므로 "PPI가 칼슘 흡수를 줄인다"는 카드는 (ㄱ) 허가사항 근거가 없고 (ㄴ) 제품 맥락과 어긋나며 (ㄷ) "칼슘 추가복용" 오독을 부른다. → C 는 B(완충 탄산수소나트륨)와 **동일 기능 범주**이며, B 처럼 *공존 성분은 완충제이고 PPI 기준 정보만 표시* 하는 트랙이 맞다.

> 즉 C 의 전환은 "새 의학정보(relation) 생성"이 아니라 "복합제임을 고지하는 배너 배선" 문제로 정정된다. 이는 B·D 가 이미 통과한 길과 동일하다.

---

## 2. 향후 combo banner/notice 설계 — 필요한가?

PM 질문("사용자가 검색했을 때 복합제임을 오해하지 않도록 향후 배너/notice 설계가 필요한지")에 대한 답:

### 2-1. 지금(name_only 유지) — **배너 불필요(현행 안전)**

- C 18건은 `product_aliases` pool 에 **0/18 진입**(검증 확인) → 제품명 검색 시 **relation 카드 미표시 + name_only 고지**만 노출:
  > *"이 약은 MediStack의 약-영양소 참고정보 DB에 아직 등록된 항목이 없습니다. 현재는 품목명 확인만 가능합니다. 복용 판단은 약사 또는 의사와 상담하세요."*
- 이 고지는 **중립적**이라 "복합제를 단일성분으로 오인"시키지 않는다(애초에 어떤 성분 정보도 단정하지 않음). → **현 단계에 추가 배너/notice 불필요.**
- (참고) 성분명 "란소프라졸/라베프라졸" 직접 검색 시엔 기존대로 PPI ×B12·×Mg 카드가 뜨며, 이는 C 제품에도 실재하는 PPI 성분 기준이라 거짓이 아니다. C 제품 자체는 name_only 로 남아 별도 오인 없음.

### 2-2. 향후 flip 시(PM 승인) — **배너 필수 + 설계 확정**

C 를 relation_card 로 전환한다면(별도 PM 라운드), B/D 와 **동일한 버퍼-콤보 배너가 필수 전제**다. 설계(기존 인프라 재사용·신규 relation 0):

| 요소 | 값 | 비고 |
|---|---|---|
| display flip | name_only → relation_card | full index 18건(란소 12·라베 6) |
| `combination_basis_ingredient` | 란소프라졸 / 라베프라졸 | 제품의 PPI 성분 |
| `source_relation_ids` | 란소=[36,37] · 라베=[32,33] | 기존 PPI ×B12·×Mg(신규 0) |
| `combination_notice_required` | true | 복합제 배너 표시 |
| **`combination_other_label`** | **"위산 중화 완충 성분(침강탄산칼슘)"** | ★핵심 설계 — 아래 §2-3 |
| 표시 카드 | PPI ×B12·×Mg 만 | 칼슘 카드 노출 금지(PPI×칼슘 relation 자체가 없음) |
| 배너 문구(기존 render.js) | *"표시된 약-영양소 참고 정보는 [PPI] 성분을 기준으로 하며, 함께 포함된 위산 중화 완충 성분(침강탄산칼슘) 성분에 대한 정보는 포함하지 않습니다. 전체 성분은 의약품 허가사항(첨부문서)을 확인하세요."* | A 의 `comboOtherLabels` 경로 그대로 |

### 2-3. ★C 고유 설계 주의 — other_label 은 "칼슘"이 아니라 기능명으로

A(비타민D3)는 `combination_other_label="비타민D"` 로 충분했다. **C 는 더 신중해야 한다**: 공존 성분이 칼슘이고, MediStack 은 *다른 약*에 대해 칼슘 relation(퀴놀론·테트라·비스포 × 칼슘 흡수)을 이미 보유한다. 배너에 단순히 **"칼슘"** 이라고 쓰면:
- 사용자가 영양 칼슘으로 오인 → "칼슘 보충해야 하나?" / "내 칼슘은 흡수 안 되나?" 오독.
- 다른 화면의 칼슘 경고와 혼선.

→ **권고: `combination_other_label = "위산 중화 완충 성분(침강탄산칼슘)"`** (또는 "제산 완충 성분"). 칼슘을 **기능**으로 규정해 영양 칼슘 오해를 사전 차단한다. (라벨 원문 "위산을 중화" 표현 승계 — 원문보다 강하지 않음.)

> 이 한 가지가 C 가 A·B 보다 까다로운 유일한 지점이며, src 변경 없이 **alias 데이터의 라벨 문자열 선택만으로** 해결된다(render.js/guards.js 의 otherLabel 경로 그대로).

---

## 3. 향후 flip 이 요구할 변경 범위 (스코핑용 — 이번 단계 미실행)

PM 이 후속 라운드에서 C flip 을 승인할 경우의 작업(전부 **데이터-only**, B/D·A 통합기 패턴 승계):

1. full index 18건 `name_only → relation_card`(+18) ↔ name_only −18 (total 17,580 유지).
2. `product_aliases` +18: is_combination=true·basis=PPI·source_relation_ids=[36,37]/[32,33]·notice=true·**other_label="위산 중화 완충 성분(침강탄산칼슘)"**.
3. `verified_item_seqs[란소프라졸/라베프라졸]` +18(pool 진입, alias #8 충족).
4. validator 상수 갱신: `COMBO_ALLOWED_BASIS` 에 **란소프라졸 개방**(라베프라졸은 B/D 로 기개방)·full-index/potassium 상수·#14 other_label 가드·search fixture(combo_notice_c/combo_render_c).
5. **신규 relation 0 · export relations 41 불변 · DATA_URL v0.2 in-place.**

> 예상 효과: relation_card 1,054 → 1,072(+18) / name_only 16,526 → 16,508. **이번 단계는 어느 것도 하지 않는다.**

---

## 4. 금지 / 안전 준수 (본 단계)

- ✅ **flip 0 · name_only 18건 유지**. export/full index/alias/relation/src/DATA_URL 수정 0. 신규 relation 0.
- ✅ **제품/구매/영양제 추천 0**: 칼슘 보충 권유 표현 없음. 오히려 그 오독 방지를 설계 원칙으로 명시(other_label=완충성분).
- ✅ **복용지시/의학 단정/위험 확정 0**. published/clinical_reviewed false 유지. tag 없음.
- ✅ 칼륨 정책 무관(C 에 칼륨 없음). E(라베+산화Mg)·기타 보류군 미접촉.
- ✅ 본 문서는 향후 설계를 **확정하지 않는다** — flip 자체는 PM 승인 게이트. "필요 여부"와 "설계안"까지만.

---

## 5. 다음 단계 (PM 의사결정용)

1. **재분류 확정**(본 문서): C = buffer_combo 트랙. PPI×칼슘 relation 전제 폐기. ← 이번 단계 완료.
2. **flip 여부**(후속·PM 승인): §3 데이터-only 작업으로 C 18건을 버퍼-콤보 배너로 전환할지. 미승인 시 name_only 영구 유지.
3. flip 시 **other_label 문구 최종 확정**(권고 "위산 중화 완충 성분(침강탄산칼슘)") + 적대 렌더 리뷰.

> 산출물: 본 문서 + `data/ppi_calcium_combo_reclassification_v1_1.csv`(18행). 라이브 무변경(`git status` 보호데이터 clean).
