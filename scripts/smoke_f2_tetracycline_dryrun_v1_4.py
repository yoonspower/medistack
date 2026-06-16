#!/usr/bin/env python3
"""
smoke_f2_tetracycline_dryrun_v1_4.py — F2 테트라사이클린 5건 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

f2_tetracycline_live_dryrun_v1_4.json 예상 relation 5건이 카드로 안전하게 렌더되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·금속이온/제산제/우유·유제품 복용 권유·직접 복용 지시·항응고/비타민K 없음.
- source quote(허가사항 원문)와 app copy 분리.
- 참고정보 톤('약사 또는 의사와 상담').
- Al/Mg 제산제(3)는 약물 counterpart(category=al_mg_antacid·'약물' 표기) — Fe/Zn nutrient(2)는 supplement 추천처럼 보이지 않음.
- 우유/유제품·소아/임신/골/치아 문맥이 카피에 노출되지 않음(보수적 batch — 해당 후보 0).
- separation 표현이 직접 지시처럼 보이지 않음.
- PM review queue safety banner(독시/미노 nutrient-overlap headline 질문 포함).
사용: python3 scripts/smoke_f2_tetracycline_dryrun_v1_4.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "f2_tetracycline_live_dryrun_v1_4.json")
INVENTORY = os.path.join(REPO, "data", "review", "f2_tetracycline_inventory_v1_4.json")
NUTRIENT_SET = ("철분", "아연")
MILK_DAIRY = ("우유", "유제품")
PEDIATRIC = ("소아", "임신", "치아", "착색", "골형성", "성장기")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f2 = _load("f2", "integrate_f2_tetracycline_batch_v1_4.py")
vfp = f2.vfp
PRODUCT_PHRASES = f2.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f2.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f2.DIRECTIVE_CMDS
ANTICOAG_TERMS = f2.ANTICOAG_TERMS
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
    assert not any(m in copy for m in MILK_DAIRY), "우유/유제품 섭취 권유 노출"
    assert not any(p in copy for p in PEDIATRIC), "소아/임신/골/치아 문맥 노출"
    assert src_quote and src_quote.strip() != disp, "source quote not separated"
    assert CONSULT in copy, "참고정보 상담 톤 없음"
    assert rel.get("product_link_allowed") is False, "product_link != false"
    nut = rel.get("nutrient", "")
    if "제산제" in nut:
        assert rel.get("counterpart_category") == "al_mg_antacid", "제산제(약물) category != al_mg_antacid"
        assert "약물" in nut, "약물 counterpart 표기 없음"
    else:
        assert "counterpart_category" not in rel, "영양소인데 counterpart_category 존재"
        assert nut in NUTRIENT_SET, f"영양소 비정상 {nut}"
    assert rel.get("ingredient", "").endswith("사이클린"), "ingredient 테트라사이클린계 아님"
    return {"title": f'{rel.get("ingredient")} × {nut}', "cat": rel.get("counterpart_category"),
            "verdict": entry.get("reverify_verdict")}


def main():
    print("=== smoke_f2_tetracycline_dryrun_v1_4 ===")
    if not os.path.exists(ARTIFACT):
        print("[FATAL] artifact 없음 — 먼저 integrate_f2_tetracycline_batch_v1_4.py")
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
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('all_f2_candidate_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))
    pm_banner = ("PM review queue: F2 reviewer-gated · 자동 승격 금지 · 제품 없음 · clinical_reviewed≠true · "
                 "headline: 독시/미노 nutrient-overlap 판단")
    ok("PM review queue safety banner(overlap headline 포함)",
       all(s in pm_banner for s in ("자동 승격 금지", "clinical_reviewed≠true", "nutrient-overlap")))

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("5 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시/항응고/우유/소아 0·상담 톤", True)
    ok("카드 5건", len(cards) == 5, str(len(cards)))
    n_nut = sum(1 for c in cards if c["cat"] is None)
    n_ant = sum(1 for c in cards if c["cat"] == "al_mg_antacid")
    ok("nutrient 2 / al_mg_antacid 3 분포", n_nut == 2 and n_ant == 3, f"nut={n_nut} ant={n_ant}")
    ok("copy_change 0(survives 5)",
       sum(1 for c in cards if c["verdict"] == "survives_with_copy_change") == 0
       and sum(1 for c in cards if c["verdict"] == "survives") == 5)

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시/항응고/우유/소아 0·"
          f"nutrient2/al_mg_antacid3 분기)")
    for c in cards:
        print(f"  · {c['title']}  [{c['cat'] or 'nutrient'}/{c['verdict']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
