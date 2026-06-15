#!/usr/bin/env python3
"""
integrate_antacid_fex_v1_2.py
MediStack — antacid_interaction 트랙의 **AT-01(펙소페나딘 × Al/Mg 함유 제산제, avoid_concomitant)**
live 통합 **준비/드라이런** 스크립트. integrate_antacid_itz_v1_2.py 패턴 승계.

⚠️⚠️ 이 스크립트는 기본값이 **--dry-run(쓰기 0)** 이다. live export 기록은 **--pm-approved + --reviewer-note PATH**
둘 다 있어야만 수행된다(별도 PM 승인 + clinical reviewer 전까지 절대 금지). --pm-approved 없이 실행하면
어떤 보호/live 데이터도 쓰지 않고, 예상 통합 결과(live-shape relation + 예상 카운트)만 계산해
**data/review/antacid_fex_dryrun_v1_2.json** (리뷰 산출물, live 아님)에 기록한다.
  - --reviewer-note 노트는 **구조+의미+SAMPLE/placeholder** 게이트를 통과해야 한다(칼륨 스크립트와 동일 인터록):
    구조=존재+비공란 / 의미=승인 토큰('approved'|'승인') + AT-FEX candidate_id(AT-FEX-01|AT-01) + primary itemSeq
    202202380 + evidence_level 'moderate' 승인 문구 전부 명시 / SAMPLE·예시 토큰·미기입 placeholder 잔존 시 거부
    (docs handoff §C-FEX 템플릿 그대로 제출 차단). 미충족 시 --pm-approved 가 있어도 STOP.

dry-run 산출물 용도:
  - validate_antacid_fex_dryrun_v1_2.py 가 이 artifact 로 시뮬레이션 export(live+AT-FEX)를 구성해
    v0.2 validator·node 렌더(전용 chip·facet 제외)를 검증한다(live 무수정).

draft → live 매핑(AT-ITZ 패턴 준용, full index/alias 무수정):
  - nutrient = surface.render_nutrient ("Al/Mg 함유 제산제(약물)")
  - recommended_action = surface.render_action ("avoid_concomitant")  ← AT-ITZ 와 다른 점(병용금지 directive)
  - mechanism = "absorption"(Al/Mg 제산제가 펙소페나딘 흡수에 영향)
  - evidence_level = MODERATE  ← ⚠️ PM 판단지점. AT-FEX confidence=low 이나 evidence_level 은 별개:
      식약처 허가사항(고품질 규제 출처)이라 'low'가 아니고, 대표 itemSeq 강도 분기(202202380 병용금지 /
      199801016 상의)로 인한 불확실성 때문에 'high'(AT-ITZ)도 아님 → 'moderate'. v0.2 enum {high,moderate} 충족.
  - counterpart_category = al_mg_antacid (비-영양소 마커 — getFacets 가 영양소 facet 에서 제외)
  - product_link_allowed=false · potassium_safety_card=false · requires_clinical_review=false
  - draft-전용/금지 필드 strip. source 는 {type,url,pointer(+확인일)} 라이브 스키마.

⚠️ live 통합(--pm-approved + --reviewer-note) 가드(AT-ITZ 가드 + avoid_concomitant 확장):
  - AT-01(펙소페나딘·avoid_concomitant) 외 통합 금지.
  - counterpart_category=al_mg_antacid · adversarial_verified=true · source itemSeq 보유.
  - render_action=avoid_concomitant(병용금지 전용) 일치.
  - 칼륨/금지성분/제품링크/reviewed_by 차단 · published/clinical_reviewed false 불변.
  - 기존 relation·excluded·disclaimers·DATA_URL·full index·aliases 불변.
  - reviewer 노트 인터록(승인 토큰 + AT-FEX candidate_id + itemSeq 202202380 + evidence moderate + SAMPLE/placeholder 거부).
멱등: 펙소페나딘×al_mg_antacid relation 이 이미 export 에 있으면 skip.

사용:
  python3 scripts/integrate_antacid_fex_v1_2.py                                  # (기본) dry-run — 쓰기 0, 예상 결과만 artifact 기록
  python3 scripts/integrate_antacid_fex_v1_2.py --pm-approved --reviewer-note X  # live 기록(reviewer 노트 후·본 세션 금지)
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
DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "antacid_fex_dryrun_v1_2.json")

BASELINE_RELATIONS = 60            # AT-ITZ(id61) 통합 후 현재 라이브 baseline
TARGET_DRAFT_ID = "AT-01"          # 펙소페나딘 × Al/Mg 제산제(avoid_concomitant)
COUNTERPART = "al_mg_antacid"
EVIDENCE = "moderate"              # ⚠️ PM 판단지점(상단 docstring 참조). v0.2 enum {high,moderate} 충족.
FORBIDDEN_RE = re.compile(r"(에스오메프라졸|esomeprazole|넥시움|nexium|와파린|warfarin)", re.IGNORECASE)

# ── reviewer 노트 인터록(칼륨 스크립트 패턴 승계 + AT-FEX 특수 요건) ──
APPROVAL_TOKENS = ("approved", "승인")
# SAMPLE/예시 노트 거부 — docs handoff §C-FEX 템플릿 그대로 제출 차단(예시 토큰은 SAMPLE 마커 포함).
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date")
NOTE_CANDIDATE_IDS = ("AT-FEX-01", "AT-01")   # harvester candidate_id / draft_id — 둘 중 하나 명시 필요
NOTE_PRIMARY_ITEMSEQ = "202202380"            # avoid_concomitant primary 대표 itemSeq(reviewer 가 승인할 근거)


def check_reviewer_note(reviewer_note):
    """AT-FEX live 통합 reviewer 노트 게이트(구조+의미+SAMPLE/placeholder 거부).
    (note_content, violations) 반환 — violations 빈 리스트 = 통과. main() 과 테스트가 공유."""
    bad = []
    note_content = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note_content = f.read()
    if not note_content.strip():
        bad.append(f"노트 비공란 필요(--reviewer-note PATH). 받은 값: {reviewer_note!r}")
        return note_content, bad
    up = note_content.upper()
    for s in NOTE_SAMPLE_SENTINELS:
        if s.upper() in up:
            bad.append(f"SAMPLE/예시 토큰 감지('{s}') — 템플릿 그대로는 승격 거부(실제 검수 노트로 교체 필요)")
            break
    for m in NOTE_PLACEHOLDER_MARKERS:
        if m in note_content:
            bad.append(f"미기입 placeholder 감지('{m}') — 검수자 식별자/검토일 등 빈칸 채우기 필요")
            break
    low = note_content.lower()
    if not any(tok in low or tok in note_content for tok in APPROVAL_TOKENS):
        bad.append(f"승인 표기({'/'.join(APPROVAL_TOKENS)}) 없음 — 검수 승인 미확인")
    if not any(c in note_content for c in NOTE_CANDIDATE_IDS):
        bad.append(f"AT-FEX candidate_id({'/'.join(NOTE_CANDIDATE_IDS)}) 미명시 — 승인 대상 불명확")
    if NOTE_PRIMARY_ITEMSEQ not in note_content:
        bad.append(f"primary itemSeq {NOTE_PRIMARY_ITEMSEQ} 미명시 — 대표 근거 승인 미확인")
    if "moderate" not in low:
        bad.append("evidence_level 'moderate' 승인 문구 미명시 — 강도 판단 미확인")
    return note_content, bad


def draft_to_live(d, new_id):
    surf = d.get("surface", {})
    src = d["source"]
    pointer = src["pointer"]
    chk = src.get("checked_at")
    if chk and "확인일" not in pointer:
        pointer = f"{pointer} / 확인일 {chk}"
    return {
        "id": new_id,
        "ingredient": d["ingredient"],
        "nutrient": surf.get("render_nutrient"),             # "Al/Mg 함유 제산제(약물)"
        "counterpart_category": d["counterpart_category"],   # 비-영양소 마커(영양소 facet 제외)
        "mechanism": "absorption",
        "recommended_action": surf.get("render_action"),     # "avoid_concomitant"
        "evidence_level": EVIDENCE,
        "display_text_ko": d["display_text_ko"],
        "management_ko": d.get("management_ko", ""),
        "product_link_allowed": False,
        "potassium_safety_card": False,
        "requires_clinical_review": False,
        "source": {"type": src["type"], "url": src["url"], "pointer": pointer},
    }


def guard_target(t):
    """live 통합 자격 가드(AT-ITZ 가드 + avoid_concomitant). 위반 메시지 리스트 반환(빈=통과)."""
    bad = []
    if t.get("counterpart_category") != COUNTERPART:
        bad.append(f"counterpart_category != {COUNTERPART}: {t.get('counterpart_category')}")
    if t.get("label_directive_type") != "avoid_concomitant":
        bad.append(f"AT-01 은 avoid_concomitant 만(현 {t.get('label_directive_type')})")
    if (t.get("surface") or {}).get("render_action") != "avoid_concomitant":
        bad.append(f"render_action != avoid_concomitant: {(t.get('surface') or {}).get('render_action')}")
    if t.get("adversarial_verified") is not True:
        bad.append(f"adversarial_verified != true: {TARGET_DRAFT_ID}")
    if t.get("potassium_safety_card") is True or "칼륨" in (t.get("surface") or {}).get("render_nutrient", ""):
        bad.append("칼륨/안전카드 건 통합 금지")
    if FORBIDDEN_RE.search(t["ingredient"]):
        bad.append(f"금지 성분: {t['ingredient']}")
    if not re.search(r"itemSeq=\d+", (t.get("source") or {}).get("url", "")):
        bad.append("source itemSeq 없음")
    if "제산제" not in ((t.get("surface") or {}).get("render_nutrient") or ""):
        bad.append("render_nutrient 에 '제산제' 명시 없음")
    if (t.get("reviewed_by") or "") != "":
        bad.append("reviewed_by 비공란 — clinical reviewer 전 공란 필수")
    return bad


def main():
    pm_approved = "--pm-approved" in sys.argv
    reviewer_note = None
    if "--reviewer-note" in sys.argv:
        i = sys.argv.index("--reviewer-note")
        if i + 1 < len(sys.argv):
            reviewer_note = sys.argv[i + 1]
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))

    drafts = {d["draft_id"]: d for d in draft["draft_relations"]}
    if TARGET_DRAFT_ID not in drafts:
        print(f"[STOP] draft {TARGET_DRAFT_ID} 없음"); return 1
    t = drafts[TARGET_DRAFT_ID]

    def is_fex(r):
        return r.get("ingredient") == t["ingredient"] and r.get("counterpart_category") == COUNTERPART
    already = any(is_fex(r) for r in exp["relations"])

    bad = guard_target(t)
    if bad and not already:
        for b in bad:
            print(f"[STOP] {b}")
        return 1

    nid = max(r["id"] for r in exp["relations"]) + 1 if not already else \
        next(r["id"] for r in exp["relations"] if is_fex(r))
    rel = draft_to_live(t, nid)
    projected_count = len(exp["relations"]) + (0 if already else 1)

    print(f"=== AT-FEX(펙소페나딘 × Al/Mg 제산제, avoid_concomitant) 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {len(exp['relations'])} (기대 {BASELINE_RELATIONS}) · 이미 통합됨: {already}")
    print(f"예상 신규 id: {nid} · 예상 relations: {len(exp['relations'])} → {projected_count}")
    print(f"   id{rel['id']} {rel['ingredient']} × {rel['nutrient']} "
          f"({rel['mechanism']}/{rel['recommended_action']}, evidence={rel['evidence_level']}, "
          f"counterpart={rel.get('counterpart_category')}, link={rel['product_link_allowed']}, "
          f"kcard={rel['potassium_safety_card']}, clinical_review={rel['requires_clinical_review']})")

    if not pm_approved:
        # ── DRY-RUN: live 무수정. 예상 결과를 리뷰 산출물에 기록(검증기 입력) ──
        artifact = {
            "meta": {
                "name": "antacid_fex_dryrun_v1_2",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "AT-FEX(펙소페나딘·avoid_concomitant) live 통합 예상 산출물(드라이런). 실제 export 무수정. "
                           "validate_antacid_fex_dryrun_v1_2.py 가 이 relation 으로 시뮬레이션 export 를 만들어 검증.",
                "baseline_relations": len(exp["relations"]),
                "baseline_max_id": max(r["id"] for r in exp["relations"]),
                "projected_relation_count": projected_count,
                "evidence_level_decision": f"{EVIDENCE} (PM 판단지점 — confidence=low 이나 허가사항 출처+대표 itemSeq 분기)",
                "live_promotion": 0,
                "published": False,
                "clinical_reviewed": False,
                "reviewed_by": "",
                "data_url": "v0.2 (불변)",
                "guard_target_violations": bad,  # 빈 리스트여야 통합 자격
                "reviewer_note_interlock": {
                    "required": True,
                    "approval_tokens": list(APPROVAL_TOKENS),
                    "candidate_id_any_of": list(NOTE_CANDIDATE_IDS),
                    "primary_itemseq": NOTE_PRIMARY_ITEMSEQ,
                    "evidence_level_phrase": EVIDENCE,
                    "rejects": "SAMPLE/예시 토큰 · 미기입 placeholder · 빈 노트 · 토큰/candidate_id/itemSeq/evidence 누락",
                    "note": "live 통합은 --pm-approved + --reviewer-note PATH 둘 다 필요. 노트가 위 의미 요건을 전건 충족해야 STOP 없이 통과(check_reviewer_note 가 강제).",
                },
                "note": "본 산출물은 드라이런 예상치일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 --pm-approved + --reviewer-note + 별도 PM + clinical reviewer.",
            },
            "projected_live_relation": rel,
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"\n[dry-run] live export 무수정. 예상 산출물 기록: "
              f"{os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print("[dry-run] live 기록은 --pm-approved + --reviewer-note 필요(별도 PM 승인 + clinical reviewer 전까지 금지).")
        return 0

    # ── LIVE 기록(--pm-approved + --reviewer-note): 별도 PM 승인 전까지 본 세션에서 호출 금지 ──
    if already:
        print("[skip] export 이미 통합(펙소페나딘×al_mg_antacid relation 존재)")
        return 0
    # reviewer 노트 게이트(구조+의미+SAMPLE/placeholder) — 승인 토큰·candidate_id·itemSeq·evidence moderate 요구.
    _note, note_bad = check_reviewer_note(reviewer_note)
    if note_bad:
        for b in note_bad:
            print(f"[STOP] reviewer 노트: {b}")
        return 1
    if len(exp["relations"]) != BASELINE_RELATIONS:
        print(f"[STOP] export relations {len(exp['relations'])} != {BASELINE_RELATIONS} baseline"); return 1
    exp["relations"] = exp["relations"] + [rel]
    exp["meta"]["relation_count"] = len(exp["relations"])
    exp["meta"]["note"] = exp["meta"].get("note", "") + \
        (" | antacid_interaction 2번째 live relation 통합: AT-01 펙소페나딘 × Al/Mg 함유 제산제(약물) "
         "absorption/avoid_concomitant 1건(id %d, 허가사항 출처·round4 적대검증 survives·전용 chip). relation %d→%d. "
         "counterpart_category=al_mg_antacid(영양소 facet 제외). full index/aliases 무변경. "
         "published/clinical_reviewed=false·reviewed_by 미기재 유지." % (nid, BASELINE_RELATIONS, projected_count))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\n[write] export 기록 완료(full index/aliases 무변경). INTEGRATE ANTACID AT-FEX: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
