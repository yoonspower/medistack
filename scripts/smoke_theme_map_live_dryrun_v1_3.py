#!/usr/bin/env python3
"""
smoke_theme_map_live_dryrun_v1_3.py — theme map 6건 live 통합 **드라이런 카드 렌더 smoke**(네트워크 0, live 무관).

dry-run 산출물(data/review/theme_map_live_dryrun_v1_3.json)의 예상 relation 6건이 카드로 안전하게
렌더되는지 시뮬레이션:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · live 통합 0 명시.
- 사용자 카피(display/management)에 금칙어·제품/구매/제휴·보충 권유·직접 복용 지시 없음.
- source quote(허가사항 원문)와 app copy 가 분리(원문 통째 노출 아님).
- acid_reducing_drug counterpart 는 '약물' chip(제산제·H2/PPI 약물 — Mg 영양제 아님).
- 지용성 비타민/비타민K 카드에 항응고(와파린/INR 등) framing 없음.
- 페니실라민 철분/아연 카드가 보충제 추천처럼 보이지 않음.

사용: python3 scripts/smoke_theme_map_live_dryrun_v1_3.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "theme_map_live_dryrun_v1_3.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
ANTICOAGULANT_TERMS = prov.ANTICOAGULANT_TERMS
DIRECTIVE_CMDS = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "복용을 중단"]

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def render_banner(meta):
    """드라이런 카드 리스트 배너(LIVE 아님·reviewer-gated·verified_reference 후보)."""
    n = len(meta.get("included_candidate_ids", []))
    return (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {n}건 "
            f"(live 통합 0 · 자동 승격 금지 · PM+clinical reviewer 노트 후 별도 PR)")


def render_card(entry, src_quote):
    """카드 안전 렌더 시뮬 — 위반 시 AssertionError."""
    rel = entry["projected_live_relation"]
    disp = (rel.get("display_text_ko") or "").strip()
    mng = (rel.get("management_ko") or "").strip()
    assert disp, "empty display copy"
    copy = f"{disp} {mng}"
    assert not vfp.scan(copy), f"forbidden phrase {vfp.scan(copy)}"
    assert not any(p in copy for p in PRODUCT_PHRASES), "product/affiliate phrase"
    assert not any(p in copy for p in SUPPLEMENT_RECO_PHRASES), "supplement-recommendation phrase"
    assert not any(c in copy for c in DIRECTIVE_CMDS), "직접 복용 지시"
    assert src_quote and src_quote.strip() != disp, "source quote not separated from app copy"
    assert rel.get("product_link_allowed") is False, "product_link_allowed not false"
    nut = rel.get("nutrient", "")
    cat = rel.get("counterpart_category")
    chip = "약물" if cat == "acid_reducing_drug" else (nut or "")
    if cat == "acid_reducing_drug":
        assert "약물" in nut, "acid_reducing_drug chip must read 약물 (제산제·H2/PPI 약물, not Mg 영양제)"
        assert "마그네슘 영양제" not in copy and "마그네슘 보충제" not in copy, "Mg 영양제 오인"
    if cat == "fat_soluble_vitamin" or "지용성 비타민" in nut or "비타민 K" in nut:
        assert not any(t in copy for t in ANTICOAGULANT_TERMS), "vitamin-K anticoagulant framing"
    return {"title": f'{rel.get("ingredient")} × {nut}', "cat": cat, "chip": chip,
            "verdict": entry.get("adversarial_verdict")}


def main():
    print("=== smoke_theme_map_live_dryrun_v1_3 ===")
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] artifact 없음: {ARTIFACT} — 먼저 integrate_theme_map_draft_batch_v1_3.py(dry-run)")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    meta = art["meta"]
    entries = art["projected_entries"]

    # 배너
    ok("artifact status 'NOT LIVE'", "NOT LIVE" in meta.get("status", ""))
    ok("live_write_performed=false · reviewer_note_required=true",
       meta.get("live_write_performed") is False and meta.get("reviewer_note_required") is True)
    banner = render_banner(meta)
    ok("배너: LIVE 아님 · reviewer-gated · verified_reference 후보 · live 통합 0 명시",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "live 통합 0")))

    # provider 원문 quote(app copy 분리 확인용)
    confirmed, _holds, errs = prov.build()
    ok("provider build 안전 위반 0", not errs, str(errs[:3]))
    quote_by_id = {r["candidate_id"]: r.get("source_quote", "") for r in confirmed}

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok(f"6건 카드 렌더-safe·copy-safe·출처분리·제품/보충/항응고/지시 0", True)

    ok("카드 6건", len(cards) == 6, str(len(cards)))
    ok("acid_reducing_drug chip='약물' 2건",
       sum(1 for c in cards if c["cat"] == "acid_reducing_drug" and "약물" in c["chip"]) == 2)
    ok("fat_soluble_vitamin 카드 2건(항응고 framing 0)",
       sum(1 for c in cards if c["cat"] == "fat_soluble_vitamin") == 2)
    ok("페니실라민 영양소(철분·아연) 카드 2건 — 보충 권유 아님",
       sum(1 for c in cards if c["cat"] is None) == 2)

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드 렌더-safe(LIVE아님·reviewer-gated·verified_reference·출처분리·"
          "제품/보충/항응고/복용지시 0·약물 chip 명확)")
    for c in cards:
        print(f"  · {c['title']}  [{c['cat']}/{c['verdict']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
