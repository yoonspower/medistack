# MediStack AutoFactory v1.5 — Guard Policy

> 오케스트레이터가 기계적으로 강제하는 안전 가드. 하나라도 위반 시 실행 FAIL(exit 1).

## 하드 가드 (코드 강제)
| 가드 | 강제 위치 | 위반 시 |
|---|---|---|
| no-live-write | `--allow-live-write` 미지원 → 거부 | exit 1 |
| 보호셋 sha256 불변 | 실행 전후 snapshot 비교(`--fail-on-protected-change`) | exit 1 |
| write-scope = `data/review/autofactory_v1_5_*` | `write_out()` 접두사 assert | AssertionError |
| 허위 인용 0 | raw 후보 `source_pointer=null` 고정 | validator FAIL |
| 미검증 source 승격 0 | `new_reviewer_ready_total==0` 게이트 | guard_ok=False → FAIL |
| needs_review leak 0 | genuine 4 ∩ auto_pass = ∅ | guard_ok=False → FAIL |
| forbidden phrase 0 | reviewed 카피 토큰 스캔 | guard_ok=False → FAIL |

## 보호셋 (읽기전용)
`medistack_v0.1_beta_export.json` · `medistack_v0.2_beta_export.json` · `medistack_v0.3_aliases.json` ·
`full_drug_name_index_sample_v1_0.json`. (src/.github 는 planning 도구가 건드리지 않음 — 무수정 전제.)

## 분류 가드
- **source quote 없음/매우 약함 → 무조건 needs_review 이하.** raw 전건이 여기 해당(offline).
- **family 일반론만 → 개별 성분 relation 생성 금지.** raw 는 draft 가 아니라 source-check 후보.
- **live exact duplicate → reject** (queue 미진입).
- **HOLD family(F5/F7/F8/F11) → hold** (queue 미진입). risk_class high_risk/mixed 정책민감.
- **K-sparing(스피로노락톤) → reject** (depletion 방향 오류).

## 상태 불변 가드 (preflight=postflight)
published=false · clinical_reviewed=false · reviewed_by 공란 · schedule 비활성 · 제품/구매/제휴 UI 0 ·
DATA_URL = `./data/medistack_v0.2_beta_export.json` · live relations 60 · relation_card 1168 · name_only 16412.

## 점수 체계 (auto-review)
7지표 0~5: source_strength · ingredient_specificity · counterpart_specificity · mechanism_support ·
management_copy_safety · duplicate_risk · regulatory_safety. overall_confidence = round(100·Σ/35).
- auto_pass: overall ≥ 85 · major_fail 0
- copy_change: 75~84 또는 copy 이슈만
- needs_review: 50~74 또는 source parse 모호
- hold: 정책민감/맥락부족
- reject: source 불일치/중복/상업/미지지 주장

major_fail(무조건 auto_pass 불가): requires_clinical_review · product_link_allowed · source_strength=0 ·
상업 source · 미지지 주장 · "복용해도 됨/안전" 류 필요.
