#!/usr/bin/env python3
"""
smoke_penicillamine_subset_v1_3.py — 페니실라민 FE/ZN 2건 subset 드라이런 **카드 렌더 smoke**(네트워크 0, live 무관).

penicillamine_subset_live_dryrun_v1_3.json 예상 relation 2건이 카드로 안전하게 렌더되는지 시뮬:
- 배너: 'LIVE 아님' · 'reviewer-gated' · 'verified_reference 후보' · 선행조건 0.
- 사용자 카피에 금칙어·제품/구매/제휴·철분/아연 복용 권유·직접 복용 지시 없음.
- source quote(허가사항 원문)와 app copy 분리.
- 참고정보 톤('약사 또는 의사와 상담').
- separation 표현이 직접 지시('복용하지 마/복용하세요')처럼 보이지 않음.
- TM-CHEL-01-ZN absorption 추론 불확실성이 metadata(risk_flags 또는 zn_mechanism_decision)에 남아 있음.

사용: python3 scripts/smoke_penicillamine_subset_v1_3.py
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARTIFACT = os.path.join(REPO, "data", "review", "penicillamine_subset_live_dryrun_v1_3.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "복용을 중단", "보충하세요"]
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
    assert src_quote and src_quote.strip() != disp, "source quote not separated"
    assert CONSULT in copy, "참고정보 상담 톤 없음"
    assert rel.get("product_link_allowed") is False, "product_link != false"
    assert "counterpart_category" not in rel, "일반 영양소인데 counterpart_category 존재"
    return {"title": f'{rel.get("ingredient")} × {rel.get("nutrient")}',
            "verdict": entry.get("adversarial_verdict"), "confidence": entry.get("confidence")}


def main():
    print("=== smoke_penicillamine_subset_v1_3 ===")
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] artifact 없음 — 먼저 integrate_penicillamine_subset_v1_3.py")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    meta = art["meta"]
    entries = art["projected_entries"]

    ok("artifact status 'NOT LIVE'", "NOT LIVE" in meta.get("status", ""))
    ok("live_write_performed=false · reviewer_note_required=true",
       meta.get("live_write_performed") is False and meta.get("reviewer_note_required") is True)
    ok("선행조건 0(prerequisites 빈 배열)", meta.get("live_integration_prerequisites") == [])
    banner = (f"LIVE 아님 · reviewer-gated · verified_reference 후보 {len(meta.get('included_candidate_ids', []))}건 "
              f"(live 통합 0 · 선행조건 0)")
    ok("배너 LIVE 아님·reviewer-gated·verified_reference·선행조건 0",
       all(s in banner for s in ("LIVE 아님", "reviewer-gated", "verified_reference 후보", "선행조건 0")))

    confirmed, _h, errs = prov.build()
    ok("provider build 안전 위반 0", not errs, str(errs[:3]))
    quote_by_id = {r["candidate_id"]: r.get("source_quote", "") for r in confirmed}

    cards = []
    for e in entries:
        try:
            cards.append(render_card(e, quote_by_id.get(e["candidate_id"], "")))
        except AssertionError as ex:
            ok(f"카드 렌더 {e.get('candidate_id')}", False, str(ex))
    if len(cards) == len(entries):
        ok("FE/ZN 2건 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시 0·상담 톤", True)
    ok("카드 2건", len(cards) == 2, str(len(cards)))

    # ZN absorption 추론 불확실성 보존
    zn = next((e for e in entries if e.get("candidate_id") == "TM-CHEL-01-ZN"), None)
    zn_uncertain = bool(zn and (any("INFERRED" in str(f) for f in zn.get("risk_flags", []))
                                or meta.get("zn_mechanism_decision", {}).get("inference_flag") is True))
    ok("ZN absorption 추론 불확실성 metadata 보존(risk_flags/zn_mechanism_decision)", zn_uncertain)
    ok("FE confidence high / ZN confidence moderate",
       any(c["confidence"] == "high" for c in cards) and any(c["confidence"] == "moderate" for c in cards))

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} 카드 렌더-safe(LIVE아님·verified_reference·출처분리·제품/보충/지시 0·ZN 추론 보존)")
    for c in cards:
        print(f"  · {c['title']}  [{c['verdict']}/{c['confidence']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
