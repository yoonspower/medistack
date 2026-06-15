#!/usr/bin/env python3
"""theme map draft-only 배치 렌더 smoke (네트워크 0, live 무관).

draft 카드가 앱 안전 규칙대로 렌더 가능한지 시뮬레이션:
- 사용자 카피(display/management) 존재 + forbidden/제품 문구 없음
- 출처(itemSeq·url·section) 표시 가능
- 제품/구매/제휴 UI 필드 부재
- 칼륨 아닌 행은 potassium_safety_card 미표시
- 라벨 원문(source_quote)과 사용자 카피가 분리(원문 그대로 노출 아님)
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(ROOT, "data/drafts/theme_map_draft_batch_v1_3.json")
_spec = importlib.util.spec_from_file_location(
    "fp", os.path.join(ROOT, "scripts/validate_forbidden_phrases_v1_2.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

PRODUCT_FIELDS = ["product", "product_link", "buy_url", "affiliate", "price", "purchase_url"]
PRODUCT_PHRASES = ["구매", "구입", "제휴", "할인", "쿠폰", "최저가", "바로가기"]
ANTICOAGULANT_TERMS = ["와파린", "항응고", "항혈소판", "INR", "혈액응고", "프로트롬빈"]
SUPPLEMENT_RECO_PHRASES = ["권장합니다", "권장됩니다", "복용을 권", "보충을 권", "섭취하세요",
                           "섭취하십시오", "드시는 것이 좋", "복용하는 것이 좋습니다", "보충제를 드"]


def chip_for(d):
    """카드 chip 라벨 시뮬 — antacid 약물이면 '약물' 표시, 영양소면 영양소명."""
    if d.get("counterpart_type") == "antacid_drug":
        return f'{d["nutrient"]}'  # 이미 '…약물' 문자열
    return d.get("nutrient", "")


def render_card(d):
    """앱 카드 렌더 시뮬 — 안전 규칙 적용한 표시 dict 반환(예외 시 raise)."""
    disp = (d.get("display_text_ko_draft") or "").strip()
    mng = (d.get("management_copy_draft") or "").strip()
    assert disp and mng, "empty user copy"
    copy = f"{disp} {mng}"
    bad = fp.scan(copy)
    assert not bad, f"forbidden phrase {bad}"
    assert not any(p in copy for p in PRODUCT_PHRASES), "product/affiliate phrase"
    assert not any(f in d for f in PRODUCT_FIELDS), "product field present"
    assert d.get("product_link_allowed") is False, "product_link_allowed not false"
    # 추천/보충 권유 카피 금지
    sup = [p for p in SUPPLEMENT_RECO_PHRASES if p in copy]
    assert not sup, f"supplement recommendation phrase {sup}"
    # 출처
    assert str(d.get("source_itemseq", "")).isdigit(), "no itemSeq"
    assert d.get("source_url", "").startswith("https://nedrug.mfds.go.kr"), "bad source url"
    # 라벨 원문과 사용자 카피 분리(원문 통째 노출 아님)
    assert d.get("source_quote", "") != disp, "user copy == raw label quote"
    # chip/kicker
    nut = d.get("nutrient", "")
    chip = chip_for(d)
    kicker = d.get("recommended_action", "")
    if d.get("counterpart_type") == "antacid_drug":
        assert "약물" in chip, "antacid chip must read as 약물 (not Mg 영양제)"
    # 지용성 비타민/비타민 K → 항응고 문맥 금지
    if ("지용성 비타민" in nut) or ("비타민 K" in nut):
        assert not any(t in copy for t in ANTICOAGULANT_TERMS), "vitamin-K anticoagulant framing"
    # 칼륨 카드 정책
    card = "potassium" if ("칼륨" in nut and d.get("potassium_safety_card")) else None
    return {"title": f'{d["ingredient"]} × {nut}', "display": disp, "management": mng,
            "chip": chip, "kicker": kicker, "source": d["source_itemseq"], "card": card}


def main():
    draft = json.load(open(DRAFT))
    cards = []
    for d in draft["drafts"]:
        try:
            cards.append(render_card(d))
        except AssertionError as e:
            print(f"RESULT: FAIL — {d.get('candidate_id')}: {e}")
            sys.exit(1)
    assert all(c["card"] is None for c in cards), "unexpected potassium card (no 칼륨 in batch)"
    print(f"RESULT: PASS ({len(cards)} draft cards render-safe, "
          f"copy-safe, product-UI-free, source-attributed)")
    for c in cards:
        print(f"  · {c['title']}  (itemSeq {c['source']})")


if __name__ == "__main__":
    main()
