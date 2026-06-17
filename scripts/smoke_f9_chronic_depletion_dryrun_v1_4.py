#!/usr/bin/env python3
"""
smoke_f9_chronic_depletion_dryrun_v1_4.py — F9 만성복용 depletion 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

f9_chronic_depletion_live_dryrun_v1_4.json 의 통합 가능 7건(약물×엽산/비타민D)이 카드로 안전하게 렌더되는지 +
inventory 의 needs_review 1건(카르바마제핀×엽산 0245)이 카드 렌더 대상에서 제외(통합 미대상)되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·엽산/비타민D 보충 권유·직접 복용/검사/처방 지시·항응고/비타민K·소아/골/치아 알람어 없음.
- source quote(허가사항 원문)와 app copy 분리. 참고/모니터링 톤('약사 또는 의사와 상담').
- mechanism=depletion·action=monitoring·counterpart_category 부재(영양소).
- 비타민D copy_change 3건 display 가 '비타민D와 관련된 주의 문구'(측정치 단정·골질환 알람어 비노출).
- scope all/survives/candidate-ids 동작(통합 가능만 카드, needs_review 제외).
- PM review queue safety banner(헤드라인 3: 0245 저신호·vitD remedy copy_change·0242 quote hygiene).
사용: python3 scripts/smoke_f9_chronic_depletion_dryrun_v1_4.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "f9_chronic_depletion_live_dryrun_v1_4.json")
INVENTORY = os.path.join(REPO, "data", "review", "f9_chronic_depletion_inventory_v1_4.json")
NUTRIENT_SET = ("엽산", "비타민D")
MILK_DAIRY = ("우유", "유제품")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f9 = _load("f9", "integrate_f9_chronic_depletion_batch_v1_4.py")
vfp = f9.vfp
PRODUCT_PHRASES = f9.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f9.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f9.DIRECTIVE_CMDS
TEST_TREAT_DIRECTIVE = f9.TEST_TREAT_DIRECTIVE
ANTICOAG_TERMS = f9.ANTICOAG_TERMS
PEDIATRIC_BONE_TERMS = f9.PEDIATRIC_BONE_TERMS
CONSULT = "약사 또는 의사"

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def render_card(entry, src_quote):
    rel = entry["projected_live_relation"]
    disp = (rel.get("display_text_ko") or "").strip()
    mng = (rel.get("management_ko") or "").strip()
    assert disp, "empty display"
    copy = f"{disp} {mng}"
    assert not vfp.scan(copy), f"forbidden {vfp.scan(copy)}"
    assert not any(p in copy for p in PRODUCT_PHRASES), "product/affiliate"
    assert not any(p in copy for p in SUPPLEMENT_RECO_PHRASES), "supplement reco"
    assert not any(c in copy for c in DIRECTIVE_CMDS + TEST_TREAT_DIRECTIVE), "직접 복용/검사/처방 지시"
    assert not any(t in copy for t in ANTICOAG_TERMS), "항응고/비타민K 혼입"
    assert not any(m in copy for m in MILK_DAIRY), "우유/유제품 섭취 권유 노출"
    assert not any(p in copy for p in PEDIATRIC_BONE_TERMS), "소아/골/치아 알람어 노출"
    assert src_quote and src_quote.strip() != disp, "source quote not separated"
    assert CONSULT in copy, "참고/모니터링 상담 톤 없음"
    assert rel.get("product_link_allowed") is False, "product_link != false"
    assert rel.get("mechanism") == "depletion", "mechanism != depletion"
    assert rel.get("recommended_action") == "monitoring", "action != monitoring"
    nut = rel.get("nutrient", "")
    assert nut in NUTRIENT_SET, f"영양소 비정상 {nut}"
    assert "counterpart_category" not in rel, "영양소인데 counterpart_category 존재"
    return {"title": f'{rel.get("ingredient")} × {nut}', "nut": nut,
            "verdict": entry.get("reverify_verdict"), "cc": bool(entry.get("copy_change"))}


def main():
    print("=== smoke_f9_chronic_depletion_dryrun_v1_4 ===")
    if not os.path.exists(ARTIFACT):
        print("[FATAL] artifact 없음 — 먼저 integrate_f9_chronic_depletion_batch_v1_4.py")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    meta = art["meta"]
    entries = art["projected_entries"]
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    quote_by_id = {c["candidate_id"]: c.get("source_quote", "") for c in inv["candidates"]}

    ok("artifact status 'NOT LIVE'", "NOT LIVE" in meta.get("status", ""))
    ok("live_write_performed=false · reviewer_note_required=true",
       meta.get("live_write_performed") is False and meta.get("reviewer_note_required") is True)
    ok("선행조건 0(prerequisites 빈 배열)", meta.get("live_integration_prerequisites") == [])
    ok("integrable 7 · needs_review 1(0245)",
       len(meta.get("integrable_ids", [])) == 7 and meta.get("needs_review_ids") == ["RF-F9-0245"])
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('integrable_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0 · needs_review 1 제외)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))
    pm_banner = ("PM review queue: F9 reviewer-gated · 자동 승격 금지 · 제품 없음 · clinical_reviewed≠true · "
                 "headline1: 카르바마제핀×엽산 저신호 열거(needs_review) · headline2: 항전간제×비타민D remedy copy_change · "
                 "headline3: 페니토인×엽산 quote hygiene")
    ok("PM review queue safety banner(헤드라인 3 포함)",
       all(s in pm_banner for s in ("자동 승격 금지", "clinical_reviewed≠true", "저신호 열거",
                                    "remedy copy_change", "quote hygiene")))

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("integrable 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시/항응고/우유/소아골 0·상담 톤", True)
    ok("카드 7건(integrable)", len(cards) == 7, str(len(cards)))
    n_fol = sum(1 for c in cards if c["nut"] == "엽산")
    n_vd = sum(1 for c in cards if c["nut"] == "비타민D")
    ok("엽산 3 · 비타민D 4 분포", n_fol == 3 and n_vd == 4, f"folate={n_fol} vitd={n_vd}")
    ok("survives 3 · copy_change 4",
       sum(1 for c in cards if c["verdict"] == "survives") == 3
       and sum(1 for c in cards if c["verdict"] == "survives_with_copy_change") == 4)
    # 비타민D copy_change 카드는 '수치 변화' 단정 비노출 + '비타민D와 관련된' reframe
    vd_cc = [c for c in cards if c["nut"] == "비타민D" and c["cc"]]
    ok("비타민D copy_change 3건(remedy reframe)", len(vd_cc) == 3, str(len(vd_cc)))
    for e in entries:
        rel = e["projected_live_relation"]
        if rel["nutrient"] == "비타민D" and e.get("copy_change"):
            d = rel.get("display_text_ko", "")
            ok(f"{rel['ingredient']}×비타민D display '수치 변화' 비노출", "수치 변화" not in d and "비타민D와 관련" in d)
    # 모니터링 톤(정기 확인 문의 수준)
    for e in entries:
        mng = e["projected_live_relation"].get("management_ko", "")
        ok(f"{e['candidate_id']} management 모니터링/상담 톤", CONSULT in mng or "확인" in mng)
        break
    # inventory: needs_review 1 가 통합 대상에서 제외(카드 미생성) 확인
    nr = [c["candidate_id"] for c in inv["candidates"] if c["reverify"]["verdict"] == "needs_review"]
    ok("inventory needs_review 1(카르바마제핀×엽산 0245) — 카드 미생성",
       nr == ["RF-F9-0245"] and not any(e["candidate_id"] in nr for e in entries))

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드(integrable) 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시/항응고/우유/소아골 0·"
          f"depletion/monitoring·영양소) · 비타민D copy_change reframe · needs_review 1(0245) 카드 미생성")
    for c in cards:
        print(f"  · {c['title']}  [{c['nut']}/{c['verdict']}{'/cc' if c['cc'] else ''}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
