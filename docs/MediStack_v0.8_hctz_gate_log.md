# MediStack v0.8 — HCTZ 복합제 개방 구현 게이트 로그 (H-G1~H-G4)

> 정책: `MediStack_v0.8_hctz_safety_review.md` · 설계: `MediStack_v0.8_hctz_combo_design.md`
> PM 자동진행 모드(2026-06-12): H-G1~H-G3 정상조건 자동 진행, **H-G4 실제 alias 반영은 별도 PM 승인 후**.
> 불변: alias JSON·queue·relation·DATA_URL·data export 무변경. 칼륨보존이뇨제 파트너 영구차단. 에스오메프라졸/15행 차단.

---

## H-G1 — combo validator 가드 (alias 무변경) ✅

**변경 파일(코드/테스트/픽스처만, data/src 무변경):**
- `scripts/validate_combo_approved_ready.py` (combo AR validator)
  - #6 basis allowlist 에 **히드로클로로티아지드 추가**(에스오메프라졸 계속 차단).
  - **신규 #12**: 칼륨보존이뇨제 파트너 하드차단(`KSPARING_RE` = 트리암테렌/아밀로라이드/스피로노락톤/에플레레논/칸레논, 영문 포함). `ingr_name` 성분 토큰 매칭. **염이름 '칼륨'(로사르탄칼륨·피마사르탄칼륨)은 토큰에 없어 미매칭(V5 분리).**
  - **신규 #13**: canonical=HCTZ 면 칼륨 반전 고지 파생조건 정합(is_combination·basis=HCTZ·notice=true) — render 트리거 보장.
- `scripts/validate_medistack_v0_3_aliases.py` (라이브 alias validator)
  - #15 basis allowlist 에 **히드로클로로티아지드 추가**.
  - **신규 #16**: 라이브 복합제 alias 표시 문자열에 칼륨보존이뇨제 토큰 금지(라이브엔 `ingr_name` 부재 → alias 문자열 방어). 염이름 칼륨 미매칭.
- 픽스처: combo AR(`v0_7_combo_ar/`) — 신규 `allow_hctz_arb`·`allow_hctz_arb_ccb`·`reject_C6_basis_blocked`·`reject_C12_kspare`·`reject_C13_hctz_notice`, 폐기 `reject_C6_hctz`. aliases(`v0_7_combo/`) — 신규 `allow_hctz_combo`·`reject_C15_basis_blocked`·`reject_C16_kspare`, 폐기 `reject_C1_hctz_combo`.
- 테스트: `test_validate_combo_ar.py`(9→13 케이스), `test_validate_v0_3_combo.py`(7→9 케이스).

**검증 결과:**
| 검사 | 결과 |
|---|---|
| combo AR 테스트 | PASS 13/13 (HCTZ+ARB·3성분 PASS, K보존#12·반전고지#13 reject 단언) |
| v0_3 combo 가드 테스트 | PASS 9/9 (HCTZ PASS, 토라세미드#15·K보존#16 reject 단언) |
| v0.1 export | PASS 12/12 |
| v0.2 export | PASS 15/15 |
| v0.3 aliases (live) | PASS **16/16** (기존 15 + #16, 회귀 0) |
| bulk | PASS 152/152 |
| TypeB 단위 | PASS 7/7 (회귀 0) |
| combo AR (live v0.7) | PASS **13/13** (기존 11 + #12/#13, 회귀 0) |

**불변(무변경) 확인:** alias_count 506 · product_aliases 468 · verified_item_seqs 430/12 · relations 30 · DATA_URL `./data/medistack_v0.2_beta_export.json`. data/ src/ 추적파일 diff 0.

**회귀:** 기존 combo 110·brand_core 14 라이브 — 새 검사(#12/#13/#16)는 HCTZ-canonical/K보존 토큰이 없어 모두 inert → PASS 유지(회귀 0).
