#!/usr/bin/env python3
"""
validate_theme_map_live_dryrun_v1_3.py
MediStack — theme map 6건 **live 통합 드라이런 검증**(읽기전용). 실제 export/full index/aliases/src 무수정.
integrate_theme_map_draft_batch_v1_3.py(dry-run)가 만든 data/review/theme_map_live_dryrun_v1_3.json 의
예상 산출물이 **통합 시 안전·계약**을 만족하는지 검증하고, 결함주입 9종으로 검증기 자체를 입증한다.

검사:
  0) 안전 불변: 라이브 export 무변경(relations==60·meta 60·published/clinical=false·theme map 6 미존재).
  1) artifact 메타 안전: live_write_performed=false·live_promotion=0·published/clinical=false·reviewed_by 공란·
     export_sha_after_same=true·expected 60→66·included 6·excluded hold 7·선행조건 문서화.
  2) 예상 6건 계약: id 62..67(라이브와 disjoint·배치 내 무중복)·필수 live 필드·draft-전용 필드 미누출·
     product_link/potassium/clinical=false·reviewed_by 부재·source itemSeq·라벨 quote pointer·
     counterpart_category(fat_soluble_vitamin 2·acid_reducing_drug 2·null 2)·acid_reducing_drug⇒'약물' 표기·
     기존 live 60/칼륨/AT-FEX 와 무중복·금칙어/제품/보충권유/비타민K 항응고 framing 0·TM-CHEL-01-ZN mechanism flag 보존.
  3) v0.2 validator 증거: separation 5건 시뮬 export PASS(재실행 확인) · 6건 전체는 검사 #15(acid_reducing_drug
     +avoid_concomitant) 선행조건으로 차단(artifact 기록 일치). 라이브 export 무수정 재확인.
  4) 결함주입 9종(published=true·reviewed_by 작성·hold 포함·제품 카피·비타민K 항응고 카피·acid_reducing_drug→nutrient·
     live_write_performed=true·candidate 누락·잘못된 count) → 전건 검출.
사용: python3 scripts/validate_theme_map_live_dryrun_v1_3.py
종료코드: 0 PASS, 1 FAIL.
"""
import copy
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
ARTIFACT = os.path.join(DATA, "review", "theme_map_live_dryrun_v1_3.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


integ = _load("integ", "integrate_theme_map_draft_batch_v1_3.py")
prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
ANTICOAGULANT_TERMS = prov.ANTICOAGULANT_TERMS
DRAFT_ONLY = integ.DRAFT_ONLY
CONFIRMED_IDS = integ.CONFIRMED_IDS

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def validate_artifact(art, exp):
    """artifact 계약 검증 → 위반 리스트(빈=통과). 실제 검증·결함주입이 공유."""
    bad = []
    meta = art.get("meta", {})
    entries = art.get("projected_entries", [])
    live_ids = {r["id"] for r in exp["relations"]}
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    live_count = len(exp["relations"])

    # 1) 메타 안전
    if meta.get("live_write_performed") is not False:
        bad.append("live_write_performed != false")
    if meta.get("live_promotion") != 0:
        bad.append("live_promotion != 0")
    if meta.get("published") is not False:
        bad.append("published != false")
    if meta.get("clinical_reviewed") is not False:
        bad.append("clinical_reviewed != false")
    if (meta.get("reviewed_by") or "") != "":
        bad.append("reviewed_by 비공란")
    if meta.get("export_sha_after_same") is not True:
        bad.append("export_sha_after_same != true")
    before = meta.get("expected_relation_count_before")
    after = meta.get("expected_relation_count_after")
    if before != live_count:
        bad.append(f"expected_before({before}) != live count({live_count})")
    if after != (before or 0) + 6:
        bad.append(f"expected_after({after}) != before+6")
    if sorted(meta.get("included_candidate_ids", [])) != sorted(CONFIRMED_IDS):
        bad.append("included_candidate_ids != 6 전건")
    if len(meta.get("excluded_hold_ids", [])) != 7:
        bad.append(f"excluded_hold_ids != 7 ({len(meta.get('excluded_hold_ids', []))})")
    if not meta.get("live_integration_prerequisites"):
        bad.append("live_integration_prerequisites 미문서화")
    if "zinc_mechanism" not in meta.get("category_decisions_required", {}):
        bad.append("category_decisions_required.zinc_mechanism 미기록")

    # 2) 예상 6건 계약
    if len(entries) != 6:
        bad.append(f"projected_entries != 6 ({len(entries)})")
    ids = [e.get("projected_id") for e in entries]
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 배치 내 중복")
    cat_counts = {"fat_soluble_vitamin": 0, "acid_reducing_drug": 0, "null": 0}
    seen_pairs = set()
    for e in entries:
        cid = e.get("candidate_id", "?")
        rel = e.get("projected_live_relation", {})
        for k in ("id", "ingredient", "nutrient", "mechanism", "recommended_action",
                  "evidence_level", "display_text_ko", "source"):
            if rel.get(k) in (None, ""):
                bad.append(f"{cid}: live 필드 '{k}' 누락")
        if rel.get("product_link_allowed") is not False:
            bad.append(f"{cid}: product_link_allowed != false")
        if rel.get("potassium_safety_card") is not False:
            bad.append(f"{cid}: potassium_safety_card != false")
        if rel.get("requires_clinical_review") is not False:
            bad.append(f"{cid}: requires_clinical_review != false")
        if "reviewed_by" in rel:
            bad.append(f"{cid}: reviewed_by 누출")
        leaked = DRAFT_ONLY & set(rel.keys())
        if leaked:
            bad.append(f"{cid}: draft-전용 필드 누출 {sorted(leaked)}")
        src = rel.get("source", {})
        if not re.search(r"itemSeq=\d+", src.get("url", "")):
            bad.append(f"{cid}: source url itemSeq 없음")
        if "itemSeq" not in src.get("pointer", "") or "'" not in src.get("pointer", ""):
            bad.append(f"{cid}: source pointer 에 itemSeq/라벨 quote 없음")
        pair = (rel.get("ingredient"), rel.get("nutrient"))
        if pair in live_pairs:
            bad.append(f"{cid}: 기존 live 60 과 중복 {pair}")
        if pair in seen_pairs:
            bad.append(f"{cid}: 배치 내 중복 {pair}")
        seen_pairs.add(pair)
        if rel.get("ingredient") == "펙소페나딘":
            bad.append(f"{cid}: AT-FEX(펙소페나딘)와 충돌")
        if rel.get("nutrient") == "칼륨" or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: 칼륨 트랙과 충돌")
        cat = rel.get("counterpart_category")
        if cat not in (None, "fat_soluble_vitamin", "acid_reducing_drug"):
            bad.append(f"{cid}: counterpart_category 비허용 {cat!r}")
        cat_counts["null" if cat is None else cat] = cat_counts.get("null" if cat is None else cat, 0) + 1
        if cat == "acid_reducing_drug" and "약물" not in rel.get("nutrient", ""):
            bad.append(f"{cid}: acid_reducing_drug 인데 nutrient 에 '약물' 표기 없음")
        if cat == "acid_reducing_drug" and rel.get("counterpart_category") == "al_mg_antacid":
            bad.append(f"{cid}: acid-reducer 를 al_mg_antacid 로 축소")
        copy_txt = f'{rel.get("display_text_ko", "")} {rel.get("management_ko", "")}'
        for b in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {b}")
        for p in PRODUCT_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 제품 문구 {p}")
        for p in SUPPLEMENT_RECO_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 보충 권유 {p}")
        nut = rel.get("nutrient", "")
        if cat == "fat_soluble_vitamin" or "지용성 비타민" in nut or "비타민 K" in nut or "·K" in nut:
            for t in ANTICOAGULANT_TERMS:
                if t in copy_txt:
                    bad.append(f"{cid}: 비타민K 항응고 framing {t}")
    if cat_counts.get("fat_soluble_vitamin") != 2:
        bad.append(f"fat_soluble_vitamin != 2 ({cat_counts.get('fat_soluble_vitamin')})")
    if cat_counts.get("acid_reducing_drug") != 2:
        bad.append(f"acid_reducing_drug != 2 ({cat_counts.get('acid_reducing_drug')})")
    if cat_counts.get("null") != 2:
        bad.append(f"null(페니실라민 FE/ZN) != 2 ({cat_counts.get('null')})")
    zn = next((e for e in entries if e.get("candidate_id") == "TM-CHEL-01-ZN"), None)
    if not zn or zn.get("adversarial_verdict") != "survives_with_copy_change":
        bad.append("TM-CHEL-01-ZN mechanism flag(verdict survives_with_copy_change) 미보존")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_tm_val_")
    p = os.path.join(tmp, "sim.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, V0_2_VALIDATOR, p], capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr)[-400:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] dry-run artifact 없음: {ARTIFACT}\n  먼저 `python3 scripts/integrate_theme_map_draft_batch_v1_3.py`")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))

    # 0) 안전 불변 — 라이브 export 무변경
    ck(len(exp["relations"]) == LIVE_RELATIONS, f"라이브 relations != {LIVE_RELATIONS} ({len(exp['relations'])})")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, "라이브 meta.relation_count != 60")
    ck(exp["meta"].get("published") is False, "라이브 published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "라이브 clinical_reviewed != false")
    tm_ings = {"오르리스타트", "콜레스티라민", "세프포독심프록세틸", "세프디토렌피복실", "페니실라민"}
    ck(not any(r.get("ingredient") in tm_ings for r in exp["relations"]),
       "theme map 성분이 이미 라이브에 존재 — 드라이런 전제 위반")

    # 1+2) artifact 계약
    art_bad = validate_artifact(art, exp)
    ck(not art_bad, f"artifact 계약 위반: {art_bad}")

    # 3) v0.2 validator 증거 재현
    entries = art["projected_entries"]
    sep5 = [e["projected_live_relation"] for e in entries if e["recommended_action"] == "separation"]
    all6 = [e["projected_live_relation"] for e in entries]
    sim5 = copy.deepcopy(exp); sim5["relations"] += sep5; sim5["meta"]["relation_count"] = len(sim5["relations"])
    sim6 = copy.deepcopy(exp); sim6["relations"] += all6; sim6["meta"]["relation_count"] = len(sim6["relations"])
    ok5, _ = run_v0_2(sim5)
    ok6, _ = run_v0_2(sim6)
    ck(len(sep5) == 5, f"separation 5건 아님 ({len(sep5)})")
    ck(ok5, "separation 5건 시뮬 export v0.2 validator FAIL(파이프라인 준비 입증 실패)")
    ck(not ok6, "6건 전체 시뮬이 v0.2 PASS — TM-CEPH-AC-02 #15 선행조건이 사라짐(검증 가정 변경 확인 필요)")
    ev = art["meta"].get("v0_2_validator_evidence", {})
    ck(ev.get("sim_separation_5_passed") is True, "artifact 기록 sim_separation_5_passed != true")
    ck(ev.get("sim_all_6_passed") is False, "artifact 기록 sim_all_6_passed != false")
    # 라이브 무수정 재확인(시뮬은 deepcopy)
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 relations 변경됨")

    # 4) 결함주입 9종 — validate_artifact 가 검출해야 함
    print("--- 결함주입(검출되어야 PASS) ---")
    inj_fail = []

    def inject(label, mutate):
        a = copy.deepcopy(art)
        mutate(a)
        b = validate_artifact(a, exp)
        ok = len(b) > 0
        print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else "  [검출 실패]"))
        if not ok:
            inj_fail.append(label)

    inject("published=true", lambda a: a["meta"].update(published=True))
    inject("reviewed_by 작성", lambda a: a["meta"].update(reviewed_by="RPH-X"))
    inject("hold candidate 포함(included 에 TM-CHEL-02)",
           lambda a: a["meta"].update(included_candidate_ids=CONFIRMED_IDS[:5] + ["TM-CHEL-02"]))
    inject("제품 카피 삽입",
           lambda a: a["projected_entries"][0]["projected_live_relation"].update(
               display_text_ko=a["projected_entries"][0]["projected_live_relation"]["display_text_ko"] + " 지금 구매하세요"))
    inject("비타민K 항응고 카피 삽입(TM-LIP-01)",
           lambda a: a["projected_entries"][0]["projected_live_relation"].update(
               management_ko=a["projected_entries"][0]["projected_live_relation"]["management_ko"] + " 와파린 INR 주의"))
    inject("acid_reducing_drug → nutrient(category 제거)",
           lambda a: [e["projected_live_relation"].pop("counterpart_category", None)
                      for e in a["projected_entries"] if e.get("candidate_id") == "TM-CEPH-AC-01"])
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("candidate 누락(entries 5건)", lambda a: a["projected_entries"].pop())
    inject("잘못된 expected count(after=70)", lambda a: a["meta"].update(expected_relation_count_after=70))
    fails.extend(inj_fail)

    print(f"=== theme map dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · "
          f"예상 {art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — 6건 계약 안전(60→66·category 2/2/2·draft누출0·제품/보충/항응고0·라이브 무수정) · "
          f"separation5 v0.2 PASS · 6건 #15 선행조건 문서화 · 결함주입 9종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
