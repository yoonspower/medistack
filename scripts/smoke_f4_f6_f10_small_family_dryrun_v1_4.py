#!/usr/bin/env python3
"""
smoke_f4_f6_f10_small_family_dryrun_v1_4.py — F4/F6/F10 small-family 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

f4_f6_f10_small_family_live_dryrun_v1_4.json 의 통합 가능 2건(레보티록신×알루미늄제산제·에스오메프라졸×B12)이
카드로 안전하게 렌더되는지 + inventory 의 needs_review 1건(케토코나졸×제산제 0275)이 카드 렌더 대상에서 제외되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·B12 보충 권유·직접 복용/검사/처방 지시·구체 dosing(2시간/콜라)·항응고·소아/골 알람어 없음.
- source quote(허가사항 원문)와 app copy 분리. 참고/모니터링 톤(상담).
- F4: absorption/separation·al_mg_antacid·display 'Mg' 비단정(Al-only) / F6: depletion/monitoring·B12·counterpart_category 부재.
- scope all/integrable/family/candidate-ids 동작(통합 가능만 카드, needs_review 제외).
- PM review queue safety banner(헤드라인 3: 0275 route 강등·0173 Al-only copy_change·0201 PPI×B12 톤 정합).
사용: python3 scripts/smoke_f4_f6_f10_small_family_dryrun_v1_4.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "f4_f6_f10_small_family_live_dryrun_v1_4.json")
INVENTORY = os.path.join(REPO, "data", "review", "f4_f6_f10_small_family_inventory_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


b = _load("bundle", "integrate_f4_f6_f10_small_family_batch_v1_4.py")
vfp = b.vfp
PRODUCT_PHRASES = b.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = b.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = b.DIRECTIVE_CMDS
TEST_TREAT_DIRECTIVE = b.TEST_TREAT_DIRECTIVE
ANTICOAG_TERMS = b.ANTICOAG_TERMS
PEDIATRIC_BONE_TERMS = b.PEDIATRIC_BONE_TERMS
DOSING_DETAIL_TERMS = b.DOSING_DETAIL_TERMS
CONSULT_MARKERS = b.CONSULT_MARKERS

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
    assert not any(t in copy for t in DOSING_DETAIL_TERMS), "구체 dosing(2시간/콜라) 노출"
    assert not any(t in copy for t in ANTICOAG_TERMS), "항응고/비타민K 혼입"
    assert not any(p in copy for p in PEDIATRIC_BONE_TERMS), "소아/골/치아 알람어 노출"
    assert src_quote and src_quote.strip() != disp, "source quote not separated"
    assert any(c in copy for c in CONSULT_MARKERS), "참고/모니터링 상담 톤 없음"
    assert rel.get("product_link_allowed") is False, "product_link != false"
    nut = rel.get("nutrient", "")
    mech, action = rel.get("mechanism"), rel.get("recommended_action")
    if "제산제" in nut:   # F4 antacid
        assert mech == "absorption" and action == "separation", f"antacid mech/action {mech}/{action}"
        assert rel.get("counterpart_category") == "al_mg_antacid", "antacid category != al_mg_antacid"
        assert "약물" in nut, "antacid 표기에 '약물' 없음"
        assert "마그네슘" not in disp, "Al-only relation 인데 display 'Mg' 단정"
    elif nut == "비타민B12":   # F6 nutrient
        assert mech == "depletion" and action == "monitoring", f"B12 mech/action {mech}/{action}"
        assert "counterpart_category" not in rel, "영양소(B12)인데 counterpart_category 존재"
    else:
        raise AssertionError(f"counterpart 분류 불명 {nut}")
    return {"title": f'{rel.get("ingredient")} × {nut}', "nut": nut, "family": entry.get("family"),
            "verdict": entry.get("reverify_verdict"), "cc": bool(entry.get("copy_change"))}


def main():
    print("=== smoke_f4_f6_f10_small_family_dryrun_v1_4 ===")
    if not os.path.exists(ARTIFACT):
        print("[FATAL] artifact 없음 — 먼저 integrate_f4_f6_f10_small_family_batch_v1_4.py")
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
    ok("integrable 2 · needs_review 1(0275)",
       len(meta.get("integrable_ids", [])) == 2 and meta.get("needs_review_ids") == ["RF-F10-0275"])
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('integrable_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0 · needs_review 1 제외)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))
    pm_banner = ("PM review queue: F4/F6/F10 small-family reviewer-gated · 자동 승격 금지 · 제품 없음 · clinical_reviewed≠true · "
                 "headline1: 케토코나졸×제산제 route/availability 강등(needs_review) · headline2: 레보티록신×제산제 Al-only copy_change · "
                 "headline3: 에스오메프라졸×B12 PPI 톤 정합 copy_change")
    ok("PM review queue safety banner(헤드라인 3 포함)",
       all(s in pm_banner for s in ("자동 승격 금지", "clinical_reviewed≠true", "route/availability 강등",
                                    "Al-only copy_change", "PPI 톤 정합")))

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("integrable 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시/dosing/항응고/소아골 0·상담 톤", True)
    ok("카드 2건(integrable)", len(cards) == 2, str(len(cards)))
    n_ant = sum(1 for c in cards if "제산제" in c["nut"])
    n_b12 = sum(1 for c in cards if c["nut"] == "비타민B12")
    ok("al_mg_antacid 1(F4) · B12 1(F6) 분포", n_ant == 1 and n_b12 == 1, f"antacid={n_ant} b12={n_b12}")
    ok("copy_change 2(survives_with_copy_change)",
       sum(1 for c in cards if c["verdict"] == "survives_with_copy_change") == 2)
    # F4 Al-only display reframe — '알루미늄' 노출 + '마그네슘' 비노출
    for e in entries:
        rel = e["projected_live_relation"]
        if "제산제" in rel["nutrient"]:
            d = rel.get("display_text_ko", "")
            ok(f"{rel['ingredient']}×제산제 display Al-only('알루미늄' 노출·'마그네슘' 비노출)",
               "알루미늄" in d and "마그네슘" not in d)
    # F6 B12 — live PPI×B12 템플릿 톤('상태에 영향'·'상태 확인')
    for e in entries:
        rel = e["projected_live_relation"]
        if rel["nutrient"] == "비타민B12":
            d = rel.get("display_text_ko", "")
            ok(f"{rel['ingredient']}×B12 display PPI×B12 템플릿 톤", "비타민 B12 상태에 영향" in d and "상태 확인" in d)
    # inventory: needs_review 1(0275) 카드 미생성 + F10 family context 보존
    nr = [c["candidate_id"] for c in inv["candidates"] if c["reverify"]["verdict"] == "needs_review"]
    ok("inventory needs_review 1(케토코나졸×제산제 0275) — 카드 미생성",
       nr == ["RF-F10-0275"] and not any(e["candidate_id"] in nr for e in entries))
    fctx = inv.get("f10_family_context", {})
    ok("F10 family context(0276 hold · 0277 reject) 보존",
       fctx.get("RF-F10-0276", {}).get("status") == "hold"
       and fctx.get("RF-F10-0277", {}).get("status") == "reject_duplicate_live")

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드(integrable) 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시/dosing/항응고/소아골 0·"
          f"F4 absorption/separation·Al-only / F6 depletion/monitoring·B12) · needs_review 1(0275 route) 카드 미생성 · F10 context 보존")
    for c in cards:
        print(f"  · {c['title']}  [{c['family']}/{c['verdict']}{'/cc' if c['cc'] else ''}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
