# MediStack v1.1-beta — Release Notes (full index 17,580)

> 작성일: 2026-06-13. v1.0-beta(10k) → **v1.1-beta(17,580)** 변경 요지. 상세 = `MediStack_v1.1_beta_release_readiness.md` / 경위 = `MediStack_v1.1_20k_expansion_gate.md` §7 / 인계 = `MediStack_v1.1_handoff.md`.

## 한 줄
검색 체감 커버리지를 위해 full drug name index 를 **10,000 → 17,580** 확장(20,000 시도 후 공급 천장에서 품질 보존 확정). **의학정보·relation·alias 무확장**, 안전선·봉인 그대로.

## 무엇이 바뀌었나
- **full drug name index 10,000 → 17,580** (relation_card 558 고정 + name_only 9,442 → **17,022**). 신규 name_only +7,580.
- 신규 브랜드/성분 커버 예: 타이레놀(타이레놀콜드-에스정) · 수마트립탄 · 트라넥삼산 · 벤지다민 등. relation 없는 약은 여전히 **name_only(품목명 확인만)** — 의학 판단/상호작용/영양소/제품/구매 정보 없음.
- 성분 풀 485 → **696**(`DIVERSE_INGREDIENTS_EXT3` 211종) · **4-shard 병렬 수집** + `merge_full_index_shards.py`(신규).
- 메타: `target_total=17,580` / `target_attempted=20,000` / `expansion_note`(천장 사유). **20k 라벨 위장 없음.**

## 무엇이 안 바뀌었나 (불변)
- relation **30** · alias **621**(product 583 + ingredient 38) · verified **545/13성분** · DATA_URL · data export(md5 `401b097a`) · alias(md5 `03fb2137`).
- published / clinical_reviewed **false**(봉인 · 천장 verified_reference). 제품/구매/제휴 UI 없음.
- 원본 10,000 prefix **byte-identical 보존** · name_only 의학필드 **0** · potassium standalone blocked **0**.

## 왜 17,580에서 멈췄나
20,000 목표 시도 → pass2 deep-page 중복률 **56%**(같은 성분 깊은 페이지가 이미 수집분 재출현) = **공급 천장**. 더 깊은 grinding 은 force-fill(gate 금지), 신규 저빈도 성분 추가는 효익 체감 → PM 판정으로 **17,580 확정**(force-fill 회피). 17,580 = *"20k 실패"가 아니라 "20k 시도 후 공급 천장에 따른 품질 보존 확정값."*

## 성능 (17,580)
JSON 8.47MB / **gzip 497.71KB** / parse 21.4ms / build 4.2ms / 모바일 ~102ms / 검색 ≤0.566ms — 전부 임계 내(gzip < 1.43MB · build < 100ms).

## 검증
full-index 31/31 · potassium 8/8(blocked 0) · v0.1 12 · v0.2 15 · v0.3-alias 16 · surface 5 · typeB 7 · combo 9 · combo-AR 13 · combo-ready 13 · bulk 152 · smoke 3종(search/HCTZ/alias) PASS · live HTTP 200 · 3-file live md5 == local.

## 태그
`v1.1-beta` (annotated) = 본 마감 docs 커밋 HEAD · `full index 17,580 supply-ceiling stable snapshot`. tag push 는 deploy 미발동.

## 다음
A clinical reviewer / B 20k 재시도(EXT4, 수익 체감) / C 압축·분할 로딩 / D 피드백 동선 / E v1.2 계획 — 각각 별도 PM 승인.
