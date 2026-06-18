# MediStack v1.4 — PR-3 small2 PM-reviewed verified-reference integration note (handoff)

기계 검증용 단일 진실원: `data/review/pr3_small2_pm_reviewed_note_v1_4.md`(checker 입력) +
`data/review/pr3_small2_candidate_lock_v1_4.json`(candidate lock). 본 문서는 사람 검토자용 요약.

## 핵심
- **PM-reviewed verified-reference integration** · **임상 검수 아님**.
- published=false / clinical_reviewed=false / reviewed_by 공란 **유지**.
- relation_count **92 → 94** (delta +2, 신규 id 94..95).

## scope (2건 · 둘 다 absorption/separation · al_mg_antacid)
| family | 약물 × counterpart | candidate_id | copy 처리 |
|---|---|---|---|
| F3 | 이반드론산 × Al/Mg 함유 제산제(약물) | RF-F3-0147 | FACT reframe(분리-안내 단정 제거) |
| F4 | 레보티록신 × 알루미늄 함유 제산제(약물) | RF-F4-0173 | Al-only(Mg 미명시) |

## copy 원칙(반영됨)
1. 이반드론산: 인용이 흡수저하 사실만 진술(타이밍 미명시) → 라벨귀속 '복용 시점을 분리하도록 안내하고 있으니'
   단정 제거 → '복용 시점에 대해 약사 또는 의사와 상담' 유도(PR-1 live al_mg_antacid 18건·id61 동형).
2. 레보티록신: 라벨 알루미늄 함유 제산제만 명시(Mg 미명시) → counterpart 'Al 함유 제산제' 한정. 인용 '투여간격에
   주의' 가 있어 복용 시점 분리 상담 유도는 라벨 근거 있음.
3. management: 복용 시간 분리는 MediStack 제안 수준(약사 상담)·복약 지시 아님.

## 제외
- needs_review: RF-F3-0148/0149(에티드론산·cation 결속), RF-F9-0245, RF-F10-0275.
- F1/F2(PR-1)·F6/F9(PR-2)·F10 → PR-3 제외. PR-1/PR-2 후보 이미 live, 재추가 금지.

## PM approval tokens
PM_REVIEWED_VERIFIED_REFERENCE_ONLY · NO_CLINICAL_REVIEW_CLAIM · NO_PRODUCT_UI · NO_SCHEDULE · PR3_SMALL2_92_TO_94
