#!/usr/bin/env python3
"""
integrate_potassium_pm_ready_v1_2.py
MediStack — 칼륨 depletion **PM-ready 4건(DF01 메틸프레드니솔론·DF04 아세타졸아미드·DF05 아조세미드·
DF-PRED-01 프레드니솔론[소론도정 199602982, 2026-06-15 needs_review 재확인 발견])**
live 통합 **준비/드라이런** 스크립트. integrate_antacid_fex_v1_2.py 패턴 승계(칼륨 트랙 특수 가드 추가).
DF-PRED-01 은 data/review/prednisolone_potassium_draft_recheck_v1_3.json 에서 병합(나머지 3건은 PM 파일).

⚠️⚠️ 기본값 = **--dry-run(쓰기 0)**. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있을 때만.
  - --reviewer-note 노트는 **구조적+의미적** 둘 다 충족해야 한다(구조: 존재+비공란 / 의미: 승인 토큰 'approved'|'승인'
    + 승격 대상 draft_id 전건 명시 — '검수자가 승인한 행만 승격' 정책. 미충족 시 --pm-approved 가 있어도 STOP).
  - 본 세션(준비 라운드)에서는 둘 다 사용하지 않는다(절대 live 통합 금지).
  - --pm-approved 없이 실행하면 어떤 보호/live 데이터도 쓰지 않고, 예상 통합 결과(live-shape relations + 예상 카운트)만
    계산해 **data/review/potassium_pm_ready_dryrun_v1_2.json**(리뷰 산출물, live 아님)에 기록한다.

대상 = **draft_id whitelist 3건만**. 파일이 아니라 draft_id 로 필터(DF02/CQF03/DF03 보류, DF06/DF07 비-칼륨 동반승격 방지).

매핑(PM-ready 산출물 = 카피 단일 진실원. factory draft 의 옛 카피가 아니라 승인된 통일문구를 쓴다):
  - display_text_ko = item.final_display_text_ko_named  (약물명 + 장기/고용량 맥락. 기존 live 칼륨행도 약물명 노출)
  - management_ko   = item.final_management_ko          (anti-supplement: '임의로 보충하지 말고…상담해 결정')
  - nutrient=칼륨 · mechanism=depletion · recommended_action=monitoring · evidence_level=high
  - product_link_allowed=False · potassium_safety_card=True · requires_clinical_review=False
  - source = {type:'허가사항', url: itemSeq 로 구성, pointer: item.source_pointer(확인일 포함)}
  - 큐 전용 플래그(pm_readiness/promotion_candidate/live_integration_forbidden/source_confirmed/
    adversarial_verified/classification_reason/itemseq/final_* …) 는 live 로 옮기지 않는다.

⚠️ live 통합(--pm-approved) 가드(전건 충족 못 하면 STOP):
  - draft_id ∈ {DF01,DF04,DF05} · pm_readiness=PM-ready · promotion_candidate=true.
  - DF02·CQF03·DF03·DF06·DF07 차단(whitelist 밖 = STOP).
  - nutrient=칼륨 · potassium_safety_card=true · product_link_allowed=false 강제.
  - management_ko == 통일 문자열 정확 일치 · display(named) 장기/고용량·칼륨영향·문의 종결 포함.
  - 칼륨 보충 권유/결핍 단정 카피 0.
  - published=false · clinical_reviewed=false · reviewed_by 공란.
  - source itemSeq 보유 · source_pointer 에 itemseq 일치.
  - clinical reviewer 노트(--reviewer-note) 존재+비공란.
멱등: (ingredient, nutrient=칼륨) 가 이미 live 에 있으면 그 item 은 skip(중복 추가 안 함).

사용:
  python3 scripts/integrate_potassium_pm_ready_v1_2.py                                   # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_potassium_pm_ready_v1_2.py --pm-approved --reviewer-note X    # live 기록(reviewer 후·본 세션 금지)
종료코드: 0 DONE/skip/dry, 1 STOP(가드 위반).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
PM = os.path.join(DATA, "review", "potassium_depletion_pm_ready_v1_2.json")
# DF-PRED-01(프레드니솔론×칼륨, 소론도정 199602982)은 needs_review 재확인(2026-06-15)에서 발견돼
# 별도 draft 파일에 보관 — 칼륨 PM-ready 통합 준비 그룹에 4번째로 합류(draft_id 로 병합).
PRED_DRAFT = os.path.join(DATA, "review", "prednisolone_potassium_draft_recheck_v1_3.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "potassium_pm_ready_dryrun_v1_2.json")

WHITELIST = ["DF01", "DF04", "DF05", "DF-PRED-01"]   # PM-ready 승격 후보 4건(draft_id 기준)
EXCLUDED = {"DF02", "CQF03", "DF03", "DF06", "DF07"}  # 보류/비-칼륨 — 들어오면 STOP
NUTRIENT = "칼륨"
# 통일 문구(byte-동일 강제). 단일 실패점이므로 정확 일치를 가드한다.
UNIFIED_MGMT = "칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요."
DISPLAY_MUST = ["장기간 복용하거나 고용량", "칼륨 상태에 영향", "확인이 필요한지 문의"]
# 칼륨 카피 금지(보충 권유·결핍 단정·제품/치료 톤). 어근형(결핍/부족)으로 활용형 변종까지 차단
# (예: '결핍일 수 있습니다'가 '결핍입니다'를 우회하는 것 방지). 통일 카피엔 어근 미포함이라 오탐 0.
COPY_FORBIDDEN = ["칼륨을 보충", "칼륨제를", "칼륨 섭취를 늘", "결핍", "부족", "빠집니다",
                  "복용하세요", "반드시 드", "구매", "제휴", "추천 영양제", "치료", "예방"]
# clinical reviewer 노트 승인 토큰(의미적 게이트).
APPROVAL_TOKENS = ("approved", "승인")


def item_to_live(it, new_id):
    src_url = f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={it['itemseq']}"
    return {
        "id": new_id,
        "ingredient": it["ingredient"],
        "nutrient": NUTRIENT,
        "mechanism": it["mechanism"],                       # depletion
        "recommended_action": it["recommended_action"],     # monitoring
        "evidence_level": it["evidence_level"],             # high
        "display_text_ko": it["final_display_text_ko_named"],
        "management_ko": it["final_management_ko"],
        "product_link_allowed": False,
        "potassium_safety_card": True,
        "requires_clinical_review": False,
        "source": {"type": "허가사항", "url": src_url, "pointer": it["source_pointer"]},
    }


def guard_item(it):
    """live 통합 자격 가드. 위반 메시지 리스트(빈=통과)."""
    bad = []
    did = it.get("draft_id")
    if did in EXCLUDED:
        bad.append(f"{did}: 보류/비-칼륨 후보 — 통합 금지")
    if did not in WHITELIST:
        bad.append(f"{did}: whitelist({WHITELIST}) 밖")
    if it.get("pm_readiness") != "PM-ready":
        bad.append(f"{did}: pm_readiness != PM-ready ({it.get('pm_readiness')})")
    if it.get("promotion_candidate") is not True:
        bad.append(f"{did}: promotion_candidate != true")
    if it.get("nutrient") != NUTRIENT:
        bad.append(f"{did}: nutrient != 칼륨 ({it.get('nutrient')})")
    if it.get("potassium_safety_card") is not True:
        bad.append(f"{did}: potassium_safety_card != true")
    if it.get("product_link_allowed") is not False:
        bad.append(f"{did}: product_link_allowed != false")
    if it.get("published") is not False or it.get("clinical_reviewed") is not False:
        bad.append(f"{did}: published/clinical_reviewed 봉인 위반")
    if (it.get("reviewed_by") or "") != "":
        bad.append(f"{did}: reviewed_by 비공란")
    if it.get("final_management_ko") != UNIFIED_MGMT:
        bad.append(f"{did}: management_ko 통일문구 불일치")
    dispn = it.get("final_display_text_ko_named", "")
    if not dispn.startswith(it.get("ingredient", "\0")):
        bad.append(f"{did}: named display 가 약물명으로 시작하지 않음")
    for m in DISPLAY_MUST:
        if m not in dispn:
            bad.append(f"{did}: named display 통일문구 누락('{m}')")
    for fb in COPY_FORBIDDEN:
        if fb in dispn or fb in it.get("final_management_ko", ""):
            bad.append(f"{did}: 칼륨 카피 금지어 '{fb}'")
    if not str(it.get("itemseq", "")).strip():
        bad.append(f"{did}: itemseq 없음")
    elif str(it["itemseq"]) not in (it.get("source_pointer") or ""):
        bad.append(f"{did}: source_pointer 에 itemseq 불일치")
    return bad


def main():
    pm_approved = "--pm-approved" in sys.argv
    reviewer_note = None
    if "--reviewer-note" in sys.argv:
        i = sys.argv.index("--reviewer-note")
        if i + 1 < len(sys.argv):
            reviewer_note = sys.argv[i + 1]

    exp = json.load(open(EXPORT, encoding="utf-8"))
    pm = json.load(open(PM, encoding="utf-8"))
    items = {i["draft_id"]: i for i in pm.get("items", [])}
    # DF-PRED-01 을 별도 draft 파일에서 병합(칼륨 PM-ready 그룹 4번째).
    if os.path.exists(PRED_DRAFT):
        for i in json.load(open(PRED_DRAFT, encoding="utf-8")).get("items", []):
            items.setdefault(i["draft_id"], i)

    # whitelist 대상만 추출(파일 전체 아님 — DF02/CQF03/DF03 보류, DF06/DF07 비-칼륨 미존재)
    targets = []
    for did in WHITELIST:
        if did not in items:
            print(f"[STOP] whitelist draft {did} 가 PM-ready 파일에 없음"); return 1
        targets.append(items[did])

    # 자격 가드(전건). idempotency 로 skip 될 항목도 검증해 둔다.
    def live_exists(ing):
        return any(r.get("ingredient") == ing and r.get("nutrient") == NUTRIENT for r in exp["relations"])

    violations = {}
    for it in targets:
        bad = guard_item(it)
        if bad:
            violations[it["draft_id"]] = bad

    baseline = len(exp["relations"])
    baseline_max_id = max(r["id"] for r in exp["relations"])
    projected = []
    projected_ids = []          # 실제 통합 대상 draft_id(스킵 제외) — reviewer 노트 per-row 확인용
    nid = baseline_max_id
    skipped = []
    for it in targets:
        if live_exists(it["ingredient"]):
            skipped.append(it["draft_id"])
            continue
        nid += 1
        projected.append(item_to_live(it, nid))
        projected_ids.append(it["draft_id"])
    projected_count = baseline + len(projected)

    print(f"=== 칼륨 PM-ready {len(WHITELIST)}건 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {baseline} · whitelist: {WHITELIST} · skip(이미존재): {skipped}")
    print(f"예상 relations: {baseline} → {projected_count} (신규 {len(projected)}건)")
    for r in projected:
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, evidence={r['evidence_level']}, "
              f"link={r['product_link_allowed']}, kcard={r['potassium_safety_card']})")
    if violations:
        print("\n[가드 위반]")
        for did, bad in violations.items():
            for b in bad:
                print(f"   X {b}")

    if not pm_approved:
        # ── DRY-RUN: live 무수정. 예상 결과를 리뷰 산출물에 기록(검증기 입력) ──
        artifact = {
            "meta": {
                "name": "potassium_pm_ready_dryrun_v1_2",
                "status": "DRY-RUN — NOT LIVE / live_integration_forbidden=true / clinical reviewer 노트 전 승격 금지",
                "purpose": "칼륨 PM-ready 3건(DF01·DF04·DF05) live 통합 예상 산출물(드라이런). 실제 export 무수정. "
                           "validate_potassium_dryrun_v1_2.py 가 이 relations 로 시뮬레이션 export 를 만들어 검증.",
                "whitelist": WHITELIST,
                "excluded_from_whitelist": sorted(EXCLUDED),
                "baseline_relations": baseline,
                "baseline_max_id": baseline_max_id,
                "projected_relation_count": projected_count,
                "skipped_already_live": skipped,
                "guard_violations": violations,         # 빈 dict 여야 통합 자격
                "live_promotion": 0,
                "published": False,
                "clinical_reviewed": False,
                "reviewed_by": "",
                "data_url": "v0.2 (불변)",
                "relation_count_validators_bump": "live 통합 시 relation-count 하드코딩 validator 들을 "
                                                  f"+{len(projected)}(=>{projected_count}) 갱신 필요(AT-FEX 통합 순서에 따라 baseline 조정).",
                "note": "본 산출물은 드라이런 예상치일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 --pm-approved + --reviewer-note + 별도 PM + clinical reviewer.",
            },
            "projected_live_relations": projected,
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"\n[dry-run] live export 무수정. 예상 산출물 기록: {os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print("[dry-run] live 기록은 --pm-approved + --reviewer-note 필요(clinical reviewer 전까지 금지).")
        return 0

    # ── LIVE 기록(--pm-approved): 별도 PM 승인 + clinical reviewer 노트 전까지 본 세션에서 호출 금지 ──
    if violations:
        for did, bad in violations.items():
            for b in bad:
                print(f"[STOP] {b}")
        return 1
    # 구조적 게이트: 노트 존재 + 비공란
    note_content = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note_content = f.read()
    if not note_content.strip():
        print(f"[STOP] clinical reviewer 노트 필요(--reviewer-note PATH, 비공란). 받은 값: {reviewer_note!r}")
        return 1
    # 의미적 게이트: 승인 토큰 + 승격 대상 draft_id 전건 명시('검수자가 승인한 행만 승격')
    low = note_content.lower()
    if not any(tok in low or tok in note_content for tok in APPROVAL_TOKENS):
        print(f"[STOP] reviewer 노트에 승인 표기({'/'.join(APPROVAL_TOKENS)}) 없음 — 검수 승인 미확인")
        return 1
    missing = [d for d in projected_ids if d not in note_content]
    if missing:
        print(f"[STOP] reviewer 노트에 승격 대상 draft_id 미명시: {missing} — 검수자가 승인한 행만 승격")
        return 1
    if not projected:
        print("[skip] 통합할 신규 칼륨 행 없음(전건 이미 live)")
        return 0
    exp["relations"] = exp["relations"] + projected
    exp["meta"]["relation_count"] = len(exp["relations"])
    names = ", ".join(f"{r['ingredient']}(id{r['id']})" for r in projected)
    exp["meta"]["note"] = exp["meta"].get("note", "") + \
        (f" | 칼륨 depletion PM-ready {len(projected)}건 live 통합: {names} (nutrient=칼륨·monitoring/depletion·"
         f"허가사항 출처·적대검증 survives·clinical reviewer 노트 확보). relation {baseline}→{projected_count}. "
         "potassium_safety_card=true·product_link_allowed=false. full index/aliases 무변경. "
         "published/clinical_reviewed=false·reviewed_by 미기재 유지.")
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n[write] export 기록 완료(full index/aliases 무변경). INTEGRATE POTASSIUM PM-READY: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
