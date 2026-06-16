#!/usr/bin/env python3
"""
smoke_f1_quinolone_dryrun_v1_4.py — F1 퀴놀론 18건 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

f1_quinolone_live_dryrun_v1_4.json 예상 relation 18건이 카드로 안전하게 렌더되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·금속이온/제산제 복용 권유·직접 복용 지시·항응고/비타민K 없음.
- source quote(허가사항 원문)와 app copy 분리.
- 참고정보 톤('약사 또는 의사와 상담').
- Al/Mg 제산제(8)는 약물 counterpart(category=al_mg_antacid·'약물' 표기) — Ca/Fe/Zn nutrient(10)는 supplement 추천처럼 보이지 않음.
- separation 표현이 직접 지시처럼 보이지 않음.
- PM review queue safety banner.
사용: python3 scripts/smoke_f1_quinolone_dryrun_v1_4.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "f1_quinolone_live_dryrun_v1_4.json")
INVENTORY = os.path.join(REPO, "data", "review", "f1_quinolone_inventory_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f1 = _load("f1", "integrate_f1_quinolone_batch_v1_4.py")
vfp = f1.vfp
PRODUCT_PHRASES = f1.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f1.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f1.DIRECTIVE_CMDS
ANTICOAG_TERMS = f1.ANTICOAG_TERMS
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
    assert not any(c in copy for c in DIRECTIVE_CMDS), "직접 복용/보충 지시"
    assert not any(t in copy for t in ANTICOAG_TERMS), "항응고/비타민K 혼입"
    assert src_quote and src_quote.strip() != disp, "source quote not separated"
    assert CONSULT in copy, "참고정보 상담 톤 없음"
    assert rel.get("product_link_allowed") is False, "product_link != false"
    nut = rel.get("nutrient", "")
    if "제산제" in nut:
        assert rel.get("counterpart_category") == "al_mg_antacid", "제산제(약물) category != al_mg_antacid"
        assert "약물" in nut, "약물 counterpart 표기 없음"
    else:
        assert "counterpart_category" not in rel, "영양소인데 counterpart_category 존재"
        assert nut in ("철분", "칼슘", "아연"), f"영양소 비정상 {nut}"
    return {"title": f'{rel.get("ingredient")} × {nut}', "cat": rel.get("counterpart_category"),
            "verdict": entry.get("reverify_verdict")}


def main():
    print("=== smoke_f1_quinolone_dryrun_v1_4 ===")
    if not os.path.exists(ARTIFACT):
        print("[FATAL] artifact 없음 — 먼저 integrate_f1_quinolone_batch_v1_4.py")
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
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('all_f1_candidate_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))
    pm_banner = "PM review queue: F1 reviewer-gated · 자동 승격 금지 · 제품 없음 · clinical_reviewed≠true"
    ok("PM review queue safety banner", all(s in pm_banner for s in ("자동 승격 금지", "clinical_reviewed≠true")))

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("18 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시/항응고 0·상담 톤", True)
    ok("카드 18건", len(cards) == 18, str(len(cards)))
    n_nut = sum(1 for c in cards if c["cat"] is None)
    n_ant = sum(1 for c in cards if c["cat"] == "al_mg_antacid")
    ok("nutrient 10 / al_mg_antacid 8 분포", n_nut == 10 and n_ant == 8, f"nut={n_nut} ant={n_ant}")
    ok("copy_change 1건 반영(survives_with_copy_change)",
       sum(1 for c in cards if c["verdict"] == "survives_with_copy_change") == 1)

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시/항응고 0·"
          f"nutrient10/al_mg_antacid8 분기)")
    for c in cards:
        print(f"  · {c['title']}  [{c['cat'] or 'nutrient'}/{c['verdict']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
