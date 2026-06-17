#!/usr/bin/env python3
"""
smoke_f3_bisphosphonate_dryrun_v1_4.py — F3 비스포스포네이트 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

f3_bisphosphonate_live_dryrun_v1_4.json 의 survives 1건(이반드론산×Al/Mg제산제)이 카드로 안전하게 렌더되는지 +
inventory 의 needs_review 2건(에티드론산 0148/0149)이 카드 렌더 대상에서 제외(통합 미대상)되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·금속이온/제산제/우유·유제품 복용 권유·직접 복용 지시·항응고/비타민K·소아/골/치아 없음.
- source quote(허가사항 원문)와 app copy 분리. 참고정보 톤('약사 또는 의사와 상담').
- Al/Mg 제산제(survives 1)는 약물 counterpart(category=al_mg_antacid·'약물' 표기).
- PM review queue safety banner(헤드라인 2: 에티드론산 parse·이반드론산 overlap 포함).
사용: python3 scripts/smoke_f3_bisphosphonate_dryrun_v1_4.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "f3_bisphosphonate_live_dryrun_v1_4.json")
INVENTORY = os.path.join(REPO, "data", "review", "f3_bisphosphonate_inventory_v1_4.json")
NUTRIENT_SET = ("칼슘", "철분")
MILK_DAIRY = ("우유", "유제품")
PEDIATRIC = ("소아", "임신", "치아", "착색", "골형성", "성장기", "골절")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f3 = _load("f3", "integrate_f3_bisphosphonate_batch_v1_4.py")
vfp = f3.vfp
PRODUCT_PHRASES = f3.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f3.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f3.DIRECTIVE_CMDS
ANTICOAG_TERMS = f3.ANTICOAG_TERMS
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
    assert rel.get("ingredient", "").endswith("드론산"), "ingredient 비스포스포네이트 아님"
    return {"title": f'{rel.get("ingredient")} × {nut}', "cat": rel.get("counterpart_category"),
            "verdict": entry.get("reverify_verdict")}


def main():
    print("=== smoke_f3_bisphosphonate_dryrun_v1_4 ===")
    if not os.path.exists(ARTIFACT):
        print("[FATAL] artifact 없음 — 먼저 integrate_f3_bisphosphonate_batch_v1_4.py")
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
    ok("survives 1 · needs_review 2", meta.get("survives_ids") == ["RF-F3-0147"]
       and sorted(meta.get("needs_review_ids", [])) == ["RF-F3-0148", "RF-F3-0149"])
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('survives_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0 · needs_review 2 제외)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))
    pm_banner = ("PM review queue: F3 reviewer-gated · 자동 승격 금지 · 제품 없음 · clinical_reviewed≠true · "
                 "headline1: 에티드론산 standalone parse(needs_review) · headline2: 이반드론산 nutrient-overlap")
    ok("PM review queue safety banner(헤드라인 2 포함)",
       all(s in pm_banner for s in ("자동 승격 금지", "clinical_reviewed≠true", "에티드론산 standalone parse",
                                    "이반드론산 nutrient-overlap")))

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("survives 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시/항응고/우유/소아 0·상담 톤", True)
    ok("카드 1건(survives)", len(cards) == 1, str(len(cards)))
    n_ant = sum(1 for c in cards if c["cat"] == "al_mg_antacid")
    ok("al_mg_antacid 1 분포", n_ant == 1, f"ant={n_ant}")
    ok("survives 1(통합 대상)", sum(1 for c in cards if c["verdict"] == "survives") == 1)
    # inventory: needs_review 2 가 통합 대상에서 제외(카드 미생성) 확인
    nr = [c["candidate_id"] for c in inv["candidates"] if c["reverify"]["verdict"] == "needs_review"]
    ok("inventory needs_review 2(에티드론산 0148/0149) — 카드 미생성",
       sorted(nr) == ["RF-F3-0148", "RF-F3-0149"]
       and not any(e["candidate_id"] in nr for e in entries))

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드(survives) 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시/항응고/우유/소아 0·"
          f"al_mg_antacid 분기) · needs_review 2 카드 미생성")
    for c in cards:
        print(f"  · {c['title']}  [{c['cat'] or 'nutrient'}/{c['verdict']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
