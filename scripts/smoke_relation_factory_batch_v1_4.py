#!/usr/bin/env python3
"""
smoke_relation_factory_batch_v1_4.py — Relation Factory v1.4 draft batch **카드 렌더 smoke**(네트워크 0, live 무관).

draft 후보가 카드로 안전 렌더되는지 시뮬:
- 배너: 'LIVE 아님 · draft-only · 자동 승격 금지'.
- 사용자 카피 금칙어·제품/구매/제휴·보충 권유·직접 복용 지시 0.
- source quote(허가사항 원문)와 app copy 분리.
- 참고정보 톤('약사 또는 의사와 상담').
- PM review queue 안전 마커(LIVE 아님·reviewer 전 live 금지·제품 없음).
종료코드: 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BATCH = os.path.join(REPO, "data", "drafts", "relation_factory_draft_batch_v1_4.json")
PMQ = os.path.join(REPO, "data", "review", "relation_factory_pm_review_queue_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "보충하세요", "섭취하세요", "끊으세요", "중단하세요"]
CONSULT = "약사 또는 의사"

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def render(d):
    disp = (d.get("display_copy") or "").strip()
    mng = (d.get("management_copy") or "").strip()
    copy = f"{disp} {mng}"
    assert disp, "empty display"
    assert not vfp.scan(copy), f"forbidden {vfp.scan(copy)}"
    assert not any(p in copy for p in PRODUCT_PHRASES), "product/affiliate"
    assert not any(p in copy for p in SUPPLEMENT_RECO_PHRASES), "supplement reco"
    assert not any(c in copy for c in DIRECTIVE), "직접 복용/보충 지시"
    q = (d.get("source_quote") or "").strip()
    assert q and q != disp, "source quote not separated from app copy"
    assert CONSULT in copy, "참고정보 상담 톤 없음"
    assert d.get("product_link_allowed") is False, "product_link != false"
    assert d.get("live_integration_forbidden") is True, "live_integration_forbidden != true"
    return {"title": f'{d.get("drug_ingredient")} × {d.get("counterpart")}', "family": d.get("family")}


def main():
    print("=== smoke_relation_factory_batch_v1_4 ===")
    if not os.path.exists(BATCH):
        print("[FATAL] batch 없음 — 먼저 relation_factory_bot_v1_4.py --online-source-check")
        return 1
    batch = json.load(open(BATCH, encoding="utf-8"))
    meta = batch["meta"]
    drafts = batch["draft_relations"]

    ok("batch status 'NOT LIVE'", "NOT LIVE" in meta.get("status", ""))
    ok("meta published/clinical=false·reviewed_by 공란",
       meta.get("published") is False and meta.get("clinical_reviewed") is False and (meta.get("reviewed_by") or "") == "")
    banner = "LIVE 아님 · draft-only · 자동 승격 금지 · 제품/구매/제휴 없음"
    ok("배너 LIVE 아님·draft-only·자동 승격 금지",
       all(s in banner for s in ("LIVE 아님", "draft-only", "자동 승격 금지")))

    cards = []
    for d in drafts:
        try:
            cards.append(render(d))
        except AssertionError as ex:
            ok(f"카드 렌더 {d.get('candidate_id')}", False, str(ex))
    if len(cards) == len(drafts):
        ok(f"{len(cards)}건 카드 렌더-safe·copy-safe·출처분리·제품/보충/지시 0·상담 톤", True)
    ok("카드 ≥10", len(cards) >= 10, str(len(cards)))

    # PM queue 안전 마커
    if os.path.exists(PMQ):
        pm = json.load(open(PMQ, encoding="utf-8"))
        st = pm.get("meta", {}).get("status", "")
        ok("PM queue: LIVE 아님·승격 금지·제품 없음",
           all(s in st for s in ("LIVE 아님", "자동 승격 금지")) and "제품" in st)

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print(f"RESULT: PASS — {len(cards)} draft 카드 렌더-safe(LIVE아님·draft-only·출처분리·제품/보충/지시 0·상담 톤)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
