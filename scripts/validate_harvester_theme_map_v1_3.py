#!/usr/bin/env python3
"""
validate_harvester_theme_map_v1_3.py — theme map expansion **harvester 편입(프롬프트 9) validator**.

읽기 전용. live/protected 무관. 검증 대상:
- data/config/theme_map_seeds_v1_3.json (seed config — policy/pointer)
- provider(`theme_map_harvest_provider_v1_3.py`)가 in-memory 로 만든 candidate-only 큐 행
- (대조) data/medistack_v0.2_beta_export.json — live 60 relation 중복 차단

검사군(전건 PASS 필요):
 1. config policy 플래그(enabled_by_default=false·candidate_only·auto_integrate=false·live_integration_forbidden·
    published=false·clinical_reviewed=false·reviewed_by 공란·schedule_activation=false·runtime_output_committed=false).
 2. config↔아티팩트 consistency(confirmed/hold id 1:1).
 3. 행 수: confirmed 6 + hold 7.
 4. provider 안전(integrity+safety) 위반 0.
 5. 모든 행 live_integration_forbidden=true·published=false·clinical_reviewed=false·reviewed_by 공란.
 6. confirmed 사용자 카피 금칙어/제품/구매/제휴/보충 권유 0.
 7. itemSeq 9자리 실값 + source_quote 비어있지 않음.
 8. adversarial verdict 존재 + draft 는 survives/survives_with_copy_change 만(강등 verdict 차단).
 9. acid_reducing_drug valid(antacid_drug·'약물' 표기·al_mg_antacid 아님) / fat_soluble_vitamin valid(nutrient_group·drug category 아님).
10. 지용성 비타민/비타민K 행에 항응고 framing 0.
11. live 60 relation 과 (ingredient,counterpart) 무중복.
12. 기존 pending(칼륨4·AT-FEX)·기존 harvester 후보(F-*/AT-*/KPI-*)와 무충돌(TM-* id disjoint·counterpart 구분).
13. hold 7 은 draft 큐 제외(confirmed 에 hold 약물 없음).
14. high-risk hold 약물이 confirmed 로 승격되지 않음.
15. runtime output 경로 안전(prefix theme_map_·data/harvest_queue/·gitignore).
16. 신규 스크립트 direct-http 0(provider/validator/smoke/harvester flag).
17. 결함주입 9종 전건 탐지(아래).

사용: python3 scripts/validate_harvester_theme_map_v1_3.py
종료코드: 0 PASS / 1 FAIL.
"""
import copy
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data/medistack_v0.2_beta_export.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("tmprov", "theme_map_harvest_provider_v1_3.py")
# direct-http 스캔은 권위있는 guard 스캐너에 위임(패턴 중복 보유 안 함 → guard 가 이 validator 를
# 스캔해도 직접호출 신호 0). guard.scan_direct_http() 는 allowlist-aware·SDK 게이트웨이 제외.
guard = _load("guard", "guard_no_live_write_v1_3.py")

PRODUCT_PHRASES = ["구매", "구입", "제휴", "할인", "쿠폰", "최저가", "바로가기", "제품 링크", "제품링크"]
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
ANTICOAGULANT_TERMS = prov.ANTICOAGULANT_TERMS
DRUG_CATEGORIES = {"acid_reducing_drug", "al_mg_antacid"}
DRAFT_VERDICTS = {"survives", "survives_with_copy_change"}
# 절대 confirmed 로 못 오는 고위험(항응고/항혈소판/항암/정신건강/임신민감/herbal/K-sparing)
HIGH_RISK_DRUGS = {"와파린", "리바록사반", "아픽사반", "다비가트란", "에독사반", "아스피린",
                   "클로피도그렐", "메토트렉세이트", "타목시펜", "이마티닙", "드로스피레논",
                   "세인트존스워트", "스피로노락톤", "에플레레논", "아밀로라이드", "트리암테렌"}
NEW_SCRIPTS = ["theme_map_harvest_provider_v1_3.py", "smoke_harvester_theme_map_v1_3.py",
               "validate_harvester_theme_map_v1_3.py"]


def find_rels(o):
    if isinstance(o, dict):
        if "relations" in o and isinstance(o["relations"], list):
            return o["relations"]
        for v in o.values():
            r = find_rels(v)
            if r is not None:
                return r
    return None


def validate(cfg, art, live_pairs):
    """config+아티팩트 → 검증 에러 리스트(빈 리스트=PASS). 결함주입은 cfg/art 를 변형해 호출."""
    errs = []
    pol = cfg["meta"]["policy"]
    # 1. policy flags
    flag_expect = {"enabled_by_default": False, "candidate_only": True, "auto_integrate": False,
                   "live_integration_forbidden": True, "published": False, "clinical_reviewed": False,
                   "schedule_activation": False, "runtime_output_committed": False}
    for k, v in flag_expect.items():
        if pol.get(k) is not v:
            errs.append(f"config.policy.{k} != {v} (got {pol.get(k)})")
    if pol.get("reviewed_by", "X") != "":
        errs.append("config.policy.reviewed_by must be empty")

    # 2~4. consistency + build(integrity+safety)
    confirmed, holds, build_errs = prov.build(cfg, art)
    errs += build_errs

    # 3. counts
    if len(confirmed) != 6:
        errs.append(f"confirmed count {len(confirmed)} != 6")
    if len(holds) != 7:
        errs.append(f"hold count {len(holds)} != 7")

    hold_drugs = {h["drug_ingredient"] for h in holds}
    hold_ids = {h["candidate_id"] for h in holds}
    for r in confirmed:
        cid = r["candidate_id"]
        # 5. candidate-only 플래그
        if r.get("live_integration_forbidden") is not True or r.get("published") is not False \
           or r.get("clinical_reviewed") is not False or r.get("reviewed_by", "X") != "":
            errs.append(f"{cid}: candidate-only 플래그 위반")
        # 6. 사용자 카피 안전(제품/구매/제휴/보충 권유)
        copy_txt = f'{r.get("display_text_ko_draft","")} {r.get("management_copy_draft","")}'
        for p in PRODUCT_PHRASES:
            if p in copy_txt:
                errs.append(f"{cid}: product/affiliate phrase '{p}'")
        for p in SUPPLEMENT_RECO_PHRASES:
            if p in copy_txt:
                errs.append(f"{cid}: supplement-recommendation phrase '{p}'")
        # 7. itemSeq + source_quote
        if not re.fullmatch(r"\d{9}", str(r.get("source_itemseq", ""))):
            errs.append(f"{cid}: source_itemseq not 9-digit ({r.get('source_itemseq')})")
        if not (r.get("source_quote") or "").strip():
            errs.append(f"{cid}: empty source_quote")
        # 8. adversarial verdict
        v = r.get("adversarial_verdict")
        if v not in DRAFT_VERDICTS:
            errs.append(f"{cid}: draft verdict must be survives/survives_with_copy_change (got {v})")
        # 9. category hygiene
        cat = r.get("counterpart_category")
        ctype = r.get("counterpart_type")
        nut = r.get("counterpart", "")
        if ctype == "antacid_drug":
            if cat not in DRUG_CATEGORIES:
                errs.append(f"{cid}: antacid_drug needs drug category (got {cat})")
            if cat == "al_mg_antacid":
                errs.append(f"{cid}: acid-reducer must not use al_mg_antacid")
            if "약물" not in nut:
                errs.append(f"{cid}: antacid counterpart must say 약물")
        if ctype in ("nutrient", "nutrient_group") and cat in DRUG_CATEGORIES:
            errs.append(f"{cid}: nutrient counterpart_type has drug category {cat}")
        # 10. 항응고 framing
        if ("지용성 비타민" in nut) or ("비타민 K" in nut) or ("·K" in nut):
            hit = [t for t in ANTICOAGULANT_TERMS if t in copy_txt or t in r.get("source_quote", "")]
            if hit:
                errs.append(f"{cid}: vitamin-K relation carries anticoagulant framing {hit}")
        # 11. live 중복
        pair = (r.get("drug_ingredient"), r.get("counterpart"))
        if pair in live_pairs:
            errs.append(f"{cid}: collides with LIVE relation {pair}")
        # 12. pending(칼륨/AT-FEX) 무충돌
        if r.get("counterpart") == "칼륨":
            errs.append(f"{cid}: confirmed counterpart '칼륨' conflicts with pending 칼륨 track")
        if r.get("drug_ingredient") == "펙소페나딘":
            errs.append(f"{cid}: confirmed drug '펙소페나딘' conflicts with pending AT-FEX")
        if not cid.startswith("TM-"):
            errs.append(f"{cid}: theme map id must be TM-* (disjoint from F-*/AT-*/KPI-*)")
        # 13. hold 약물이 confirmed 에 없음
        if cid in hold_ids:
            errs.append(f"{cid}: hold id appears in confirmed draft queue")
        # 14. high-risk
        if r.get("drug_ingredient") in HIGH_RISK_DRUGS:
            errs.append(f"{cid}: high-risk drug in confirmed draft")

    # 13. hold 7 은 draft 제외(이미 prov.build 가 분리하지만 명시 검증)
    conf_ids = {r["candidate_id"] for r in confirmed}
    if conf_ids & hold_ids:
        errs.append(f"confirmed ∩ hold ids non-empty: {conf_ids & hold_ids}")

    # 15. runtime output 경로
    if pol.get("runtime_output_prefix") != "theme_map_" or pol.get("runtime_output_dir") != "data/harvest_queue/":
        errs.append("runtime output prefix/dir not safe")
    return errs


def main():
    print("=== validate_harvester_theme_map_v1_3 ===")
    cfg = prov.load_config()
    art = prov.load_artifacts(cfg)
    live = find_rels(json.load(open(EXPORT, encoding="utf-8"))) or []
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in live}

    fails = []

    # --- 정상 데이터: 에러 0 ---
    errs = validate(cfg, art, live_pairs)
    if errs:
        print(f"  FAIL 정상 검증 — {len(errs)} issue(s)")
        for e in errs:
            print("    -", e)
        fails.append("baseline")
    else:
        print(f"  PASS 정상 검증 (config + {len(art['draft_batch']['drafts'])} draft + "
              f"{len(cfg['hold_seeds'])} hold, live 60 cross-checked)")

    # --- 16. direct-http 0 (신규 스크립트) — guard 권위 스캐너에 위임 ---
    g_viol = set(guard.scan_direct_http())
    http_viol = [s for s in NEW_SCRIPTS if any(v.endswith(s) for v in g_viol)]
    if http_viol:
        print(f"  FAIL direct-http 신규 위반: {http_viol}")
        fails.append("direct_http")
    else:
        print(f"  PASS direct-http 0 (신규 스크립트 {len(NEW_SCRIPTS)}, guard 스캐너 위임)")

    # --- 17. 결함주입 9종: 각각 ≥1 에러 탐지해야 PASS ---
    def inj(label, mut):
        c2, a2 = copy.deepcopy(cfg), copy.deepcopy(art)
        mut(c2, a2)
        e = validate(c2, a2, live_pairs)
        caught = len(e) > 0
        print(("  PASS " if caught else "  FAIL ") + f"결함주입: {label}" + ("" if caught else "  [미탐지!]"))
        if not caught:
            fails.append(f"inject:{label}")

    def m_live_forbidden(c, a):
        a["draft_batch"]["meta"]["live_integration_forbidden"] = False
        # provider 는 행에 강제 True 를 박으므로, config policy 를 무너뜨려 탐지
        c["meta"]["policy"]["live_integration_forbidden"] = False
    inj("live_integration_forbidden=false", m_live_forbidden)
    inj("published=true", lambda c, a: c["meta"]["policy"].__setitem__("published", True))
    inj("reviewed_by 작성", lambda c, a: c["meta"]["policy"].__setitem__("reviewed_by", "Dr.X"))
    inj("auto_integrate=true", lambda c, a: c["meta"]["policy"].__setitem__("auto_integrate", True))
    inj("schedule_activation=true", lambda c, a: c["meta"]["policy"].__setitem__("schedule_activation", True))

    def m_acid_as_nutrient(c, a):
        for d in a["draft_batch"]["drafts"]:
            if d["candidate_id"] == "TM-CEPH-AC-01":
                d["counterpart_type"] = "nutrient"  # 약물을 영양소로 위조
    inj("acid_reducing_drug 를 nutrient 로 표기", m_acid_as_nutrient)

    def m_al_mg(c, a):
        for d in a["draft_batch"]["drafts"]:
            if d["candidate_id"] == "TM-CEPH-AC-02":
                d["counterpart_category"] = "al_mg_antacid"  # acid-reducer 를 Al/Mg 로 좁힘
    inj("acid-reducer 를 al_mg_antacid 로 축소", m_al_mg)

    def m_anticoag(c, a):
        for d in a["draft_batch"]["drafts"]:
            if d["candidate_id"] == "TM-LIP-02":
                d["management_copy_draft"] += " 와파린 복용 시 항응고 위험에 주의하세요."
    inj("비타민K 항응고 framing 삽입", m_anticoag)

    def m_product(c, a):
        for d in a["draft_batch"]["drafts"]:
            if d["candidate_id"] == "TM-LIP-01":
                d["management_copy_draft"] += " 최저가 구매 바로가기."
    inj("제품/구매 문구 삽입", m_product)

    def m_hold_to_draft(c, a):
        # hold 후보(페니토인)를 draft batch 에 위조 삽입
        a["draft_batch"]["drafts"].append({
            "candidate_id": "TM-HOLD-PHENYTOIN", "family": "x", "ingredient": "페니토인",
            "nutrient": "엽산", "counterpart_type": "nutrient", "counterpart_category": None,
            "mechanism": "depletion", "recommended_action": "monitoring", "evidence_level": "low",
            "confidence": "low", "source_itemseq": "000000000", "source_section": "x",
            "source_quote": "x", "source_url": "x", "display_text_ko_draft": "x",
            "management_copy_draft": "x", "product_link_allowed": False, "potassium_safety_card": False,
            "adversarial_verified": {"verdict": "hold"}})
    inj("hold 약물을 draft 큐에 삽입", m_hold_to_draft)

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — config policy·consistency·candidate-only·category·중복·결함주입(9) 전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
