# MediStack — Relation Factory v1.4 중복방지 인벤토리

> 읽기전용 통합(live/pending/draft/needs_review/hold/reject). `relation_factory_bot_v1_4` 가 candidate 중복 차단에 사용.
> 정본 JSON `data/review/relation_factory_inventory_v1_4.json` · dedup 키 **87**개. live 승격 0.

## 1. live relations
- live pairs: **60** (id1~61, count 60)

## 2. pending reviewer-gated (live 미존재)
- 페니실라민: ['TM-CHEL-01-FE', 'TM-CHEL-01-ZN']
- theme map: ['TM-CEPH-AC-01', 'TM-CEPH-AC-02', 'TM-LIP-01', 'TM-LIP-02']
- 칼륨 PM-ready: ['DF01', 'DF04', 'DF05']
- AT-FEX: ['AT-FEX']

## 3. reject / no_domestic_product / high-risk hold (재후보화 금지)
- reject(세파계×철분 등): 10
- no_domestic_product(미유통 다이유레틱): 5
- high-risk permanent hold(K-sparing·warfarin×vitK): 5
- hold(약신호 약함): 3

## 4. dedup 정책
- 키 = `canon_drug(약물)|canon_counterpart(상대)`. 염/수화물/제형 접미 제거 + counterpart 정규화(철분/철→fe 등).
- candidate 가 이 키 집합과 충돌하면 REJECT_PRECHECK(중복) 또는 HOLD(상대 카테고리만 충돌).
- **계열 일반화 금지**: reject/hold 는 약물별 확정 — 같은 계열이라도 미확정 품목은 source-check 후보로만.
