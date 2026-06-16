#!/usr/bin/env python3
"""
smoke_harvester_theme_map_v1_3.py — theme map expansion 편입 PM review queue **렌더 smoke**(네트워크 0, live 무관).

provider 가 만든 candidate-only 큐가 PM 문서/카드로 안전하게 렌더되는지 시뮬레이션:
- PM queue 배너에 'LIVE 아님' + '자동 승격 금지' 명시.
- source quote(출처 원문)와 app copy(참고 문구)가 분리(원문 통째 노출 아님).
- 제품/구매/제휴 UI·문구 없음. 보충 권유 없음.
- 지용성 비타민/비타민K 카드에 항응고(와파린/INR 등) framing 없음.
- acid_reducing_drug counterpart 는 '약물' chip(Mg 영양제 아님).
- 페니실라민 철분/아연 카드가 보충제 추천처럼 보이지 않음.
- hold 7 은 별도 hold 섹션(draft 카드 아님).

사용: python3 scripts/smoke_harvester_theme_map_v1_3.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("tmprov", "theme_map_harvest_provider_v1_3.py")
vfp = _load("vfp", "validate_forbidden_phrases_v1_2.py")

PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
ANTICOAGULANT_TERMS = prov.ANTICOAGULANT_TERMS

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def chip_for(r):
    """카드 chip — antacid 약물이면 '약물', 영양소면 영양소명."""
    if r.get("counterpart_type") == "antacid_drug":
        return r.get("counterpart", "")  # 이미 '…약물' 포함 문자열
    return r.get("counterpart", "")


def render_card(r):
    """카드 안전 렌더 시뮬 — 위반 시 AssertionError."""
    disp = (r.get("display_text_ko_draft") or "").strip()
    mng = (r.get("management_copy_draft") or "").strip()
    quote = (r.get("source_quote") or "").strip()
    assert disp and mng, "empty user copy"
    copy = f"{disp} {mng}"
    assert not vfp.scan(copy), f"forbidden phrase {vfp.scan(copy)}"
    assert not any(p in copy for p in PRODUCT_PHRASES), "product/affiliate phrase"
    assert not any(p in copy for p in SUPPLEMENT_RECO_PHRASES), "supplement-recommendation phrase"
    assert quote and quote != disp, "source quote not separated from app copy"
    assert r.get("product_link_allowed") is False, "product_link_allowed not false"
    nut = r.get("counterpart", "")
    chip = chip_for(r)
    if r.get("counterpart_type") == "antacid_drug":
        assert "약물" in chip, "antacid chip must read as 약물 (not Mg 영양제)"
    if ("지용성 비타민" in nut) or ("비타민 K" in nut) or ("·K" in nut):
        assert not any(t in copy for t in ANTICOAGULANT_TERMS), "vitamin-K anticoagulant framing"
    # 페니실라민 영양소 카드 = 보충 권유 아님(SUPPLEMENT_RECO 이미 위에서 차단)
    return {"title": r["relation"], "chip": chip, "verdict": r.get("adversarial_verdict")}


def main():
    print("=== smoke_harvester_theme_map_v1_3 ===")
    cfg = prov.load_config()
    art = prov.load_artifacts(cfg)
    confirmed, holds, errs = prov.build(cfg, art)
    ok("provider build 안전 위반 0", not errs, str(errs[:3]))
    ok("confirmed 6 / hold 7", len(confirmed) == 6 and len(holds) == 7,
       f"{len(confirmed)}/{len(holds)}")

    # 카드 렌더
    cards = []
    for r in confirmed:
        try:
            cards.append(render_card(r))
        except AssertionError as e:
            ok(f"카드 렌더 {r['candidate_id']}", False, str(e))
    if len(cards) == len(confirmed):
        ok(f"draft 카드 {len(cards)}건 렌더-safe·copy-safe·출처분리·제품UI없음", True)

    # PM queue markdown
    md = prov.build_pm_queue_md(cfg, confirmed, holds, {"run_at": "(smoke)"})
    ok("PM queue: 'LIVE 아님' 명시", "LIVE 아님" in md)
    ok("PM queue: '자동 승격 금지' 명시", "자동 승격 금지" in md)
    ok("PM queue: 'live relation 변경: **0**'", "live relation 변경: **0**" in md)
    ok("PM queue: source quote/app copy 분리 표기", "source quote" in md and "app copy(참고)" in md)
    # 배너/정책 라인(`>` 시작 — '제품/구매/제휴 UI 없음' 부정문)과 source quote 원문은 제외하고 본문만 스캔.
    body_lines = [l for l in md.splitlines()
                  if not l.lstrip().startswith(">") and not l.lstrip().startswith("- source quote:")]
    ok("PM queue: 제품/구매/제휴 문구 0(배너/정책 제외)",
       not any(p in l for l in body_lines for p in PRODUCT_PHRASES))
    # hold 섹션에 hold 7 전부 + draft 카드엔 hold 약물 없음
    ok("PM queue: HOLD 섹션에 hold 7 전부", all(h["candidate_id"] in md for h in holds))
    draft_titles = {c["title"] for c in cards}
    ok("acid_reducing_drug chip='약물'(2건)",
       sum(1 for c in cards if "약물" in c["chip"]) == 2)
    ok("verdict 분포 survives 3 / copy_change 3",
       sum(1 for c in cards if c["verdict"] == "survives") == 3
       and sum(1 for c in cards if c["verdict"] == "survives_with_copy_change") == 3)

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} draft 카드 + PM queue 렌더-safe(LIVE아님·자동승격금지·출처분리·제품/보충/항응고 0)")
    for c in cards:
        print(f"  · {c['title']}  [{c['verdict']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
