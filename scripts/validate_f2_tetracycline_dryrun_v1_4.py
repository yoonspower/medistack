#!/usr/bin/env python3
"""
validate_f2_tetracycline_dryrun_v1_4.py
MediStack — F2 테트라사이클린 5건 **live 통합 드라이런 검증**(읽기전용). export/full index/aliases/src 무수정.
integrate_f2_tetracycline_batch_v1_4.py(dry-run)가 만든 산출물 3종이 통합 시 안전·계약을 만족하는지 검증 +
결함주입 12종으로 검증기 자체 입증.

검사:
  0) 안전 불변: live export 무변경(relations==60·meta 60·published/clinical=false·테트라사이클린 미존재·
     사이클린×제산제 미존재).
  1) dryrun 메타: live_write_performed=false·promotion=0·published/clinical=false·reviewed_by 공란·
     export_sha_after_same=true·expected 60→65·full 5·F1 후 78→83·prerequisites 빈(선행조건 0)·scope_scenarios 일관.
  2) projected 5 계약: id 62~66(live disjoint·무중복)·필수 live 필드·draft 누출 0·product/potassium/clinical=false·
     reviewed_by 부재·source itemSeq·ingredient 사이클린·al_mg_antacid(약물)는 category=al_mg_antacid·nutrient(철분/아연) category 키 부재·
     live 60 무중복·F1/페니실라민/칼륨/theme/AT-FEX 무충돌·금칙어/제품/보충 0·항응고/비타민K 0·복용지시 0.
  3) inventory(작업 B/C): 5건·reverify(survives 5·copy_change 0·downgrade 0)·재실행 reverify 일치(소스 fidelity).
  4) index impact(작업 K): 자동 flip 0·alias 변경 false·relation_card 1168/name_only 16412 불변·테트라 latent flip 1.
  5) v0.2 validator: 5건 시뮬 export PASS(재실행) → 선행조건 0.
  6) 결함주입 12종 → 전건 검출.
사용: python3 scripts/validate_f2_tetracycline_dryrun_v1_4.py
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
DRYRUN = os.path.join(DATA, "review", "f2_tetracycline_live_dryrun_v1_4.json")
INVENTORY = os.path.join(DATA, "review", "f2_tetracycline_inventory_v1_4.json")
INDEX_IMPACT = os.path.join(DATA, "review", "f2_tetracycline_index_impact_v1_4.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60
F2_COUNT = 5
ANTACID_CATEGORY = "al_mg_antacid"
RELATION_CARD = 1168
NAME_ONLY = 16412
NUTRIENT_SET = ("철분", "아연")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f2 = _load("f2", "integrate_f2_tetracycline_batch_v1_4.py")
integ = f2.integ
vfp = f2.vfp
PRODUCT_PHRASES = f2.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f2.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f2.DIRECTIVE_CMDS
ANTICOAG_TERMS = f2.ANTICOAG_TERMS
DRAFT_ONLY = integ.DRAFT_ONLY

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def validate_artifact(art, exp):
    bad = []
    meta = art.get("meta", {})
    entries = art.get("projected_entries", [])
    live_ids = {r["id"] for r in exp["relations"]}
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    live_count = len(exp["relations"])

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
        bad.append(f"expected_before({before}) != live({live_count})")
    if meta.get("expected_relation_count_after_full") != live_count + F2_COUNT:
        bad.append("expected_after_full != 60+5")
    sf1 = meta.get("scenario_if_f1_already_live", {})
    if sf1.get("baseline") != 78 or sf1.get("expected_after_full") != 83:
        bad.append("scenario_if_f1_already_live != 78→83")
    if meta.get("live_integration_prerequisites") != []:
        bad.append(f"F2 선행조건은 0이어야: {meta.get('live_integration_prerequisites')}")
    if len(meta.get("all_f2_candidate_ids", [])) != F2_COUNT:
        bad.append(f"all_f2_candidate_ids != {F2_COUNT}")
    # scope_scenarios 일관(all5 60→65·nutrient2 60→62·antacid3 60→63)
    ss = meta.get("scope_scenarios", {})
    if ss.get("all5", {}).get("expected_count") != live_count + F2_COUNT:
        bad.append("scope all5 expected_count != 65")
    if ss.get("nutrient2", {}).get("expected_count") != live_count + 2:
        bad.append("scope nutrient2 expected_count != 62")
    if ss.get("antacid3", {}).get("expected_count") != live_count + 3:
        bad.append("scope antacid3 expected_count != 63")

    # projected 계약(요청 scope 기준 — 기본 all5=5)
    ids = [e.get("projected_id") for e in entries]
    if meta.get("requested_scope") == "all5" and len(entries) != F2_COUNT:
        bad.append(f"all5 projected_entries != {F2_COUNT} ({len(entries)})")
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 중복")
    seen = set()
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
            bad.append(f"{cid}: draft-전용 누출 {sorted(leaked)}")
        src = rel.get("source", {})
        if not re.search(r"itemSeq=\d+", src.get("url", "")):
            bad.append(f"{cid}: source url itemSeq 없음")
        if "itemSeq" not in src.get("pointer", "") or "'" not in src.get("pointer", ""):
            bad.append(f"{cid}: source pointer 라벨 quote 없음")
        if not rel.get("ingredient", "").endswith("사이클린"):
            bad.append(f"{cid}: ingredient 테트라사이클린계 아님({rel.get('ingredient')})")
        if rel.get("mechanism") != "absorption":
            bad.append(f"{cid}: mechanism != absorption")
        if rel.get("recommended_action") not in ("separation",):
            bad.append(f"{cid}: recommended_action != separation")
        # al_mg_antacid(약물) vs 영양소 category 분기
        nut = rel.get("nutrient", "")
        if "제산제" in nut:
            if rel.get("counterpart_category") != ANTACID_CATEGORY:
                bad.append(f"{cid}: 제산제(약물)인데 category != al_mg_antacid")
            if "약물" not in nut:
                bad.append(f"{cid}: 약물 counterpart 표기에 '약물' 없음")
        else:
            if "counterpart_category" in rel:
                bad.append(f"{cid}: 영양소인데 counterpart_category 키 존재(null→키 부재여야)")
            if nut not in NUTRIENT_SET:
                bad.append(f"{cid}: 영양소 counterpart 비정상({nut})")
        pair = (rel.get("ingredient"), nut)
        if pair in live_pairs:
            bad.append(f"{cid}: 기존 live 60 과 중복 {pair}")
        if pair in seen:
            bad.append(f"{cid}: 배치 내 중복 {pair}")
        seen.add(pair)
        # pending/타 트랙 충돌(F1 퀴놀론 성분 혼입·칼륨·AT-FEX·페니실라민)
        if rel.get("ingredient") in ("펙소페나딘", "페니실라민") or rel.get("ingredient", "").endswith("록사신") \
                or nut == "칼륨" or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: F1/AT-FEX/페니실라민/칼륨 트랙 충돌")
        copy_txt = f'{rel.get("display_text_ko", "")} {rel.get("management_ko", "")}'
        for b in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {b}")
        if any(p in copy_txt for p in PRODUCT_PHRASES):
            bad.append(f"{cid}: 제품 문구")
        if any(p in copy_txt for p in SUPPLEMENT_RECO_PHRASES):
            bad.append(f"{cid}: 보충 권유")
        if any(c in copy_txt for c in DIRECTIVE_CMDS):
            bad.append(f"{cid}: 복용 지시")
        if any(t in copy_txt for t in ANTICOAG_TERMS):
            bad.append(f"{cid}: 항응고/비타민K 혼입")
    return bad


def validate_inventory(inv):
    bad = []
    meta = inv.get("meta", {})
    cands = inv.get("candidates", [])
    if len(cands) != F2_COUNT:
        bad.append(f"inventory candidates != {F2_COUNT} ({len(cands)})")
    rc = meta.get("reverify_counts", {})
    if rc.get("survives") != 5 or rc.get("survives_with_copy_change") != 0:
        bad.append(f"reverify counts != survives5/copy0 ({rc})")
    if (rc.get("needs_review", 0) + rc.get("hold", 0) + rc.get("reject", 0)) != 0:
        bad.append(f"reverify 강등 != 0 ({rc})")
    if meta.get("published") is not False or meta.get("clinical_reviewed") is not False:
        bad.append("inventory published/clinical != false")
    # 재실행 reverify — 소스 fidelity(quote/quote-boundary/pediatric/antacid 분류) 위변조 검출
    for c in cands:
        rec = {
            "candidate_id": c["candidate_id"], "drug_ingredient": c["drug_ingredient"],
            "counterpart": c["counterpart"], "counterpart_type": c["counterpart_type"],
            "counterpart_category": c.get("counterpart_category"), "itemSeq": c["itemSeq"],
            "source_section": c["source_section"], "source_quote": c["source_quote"],
            "mechanism": c["mechanism"], "recommended_action": c["recommended_action"],
            "evidence_level": c["evidence_level"], "display_copy": c["display_copy"],
            "management_copy": c.get("management_copy", ""),
        }
        _L, verdict, _f = f2.reverify(rec)
        if verdict not in ("survives", "survives_with_copy_change"):
            bad.append(f"{c['candidate_id']}: 재실행 reverify verdict={verdict} ({[k for k,v in _L.items() if str(v).startswith('fail')]})")
        stored = c.get("reverify", {}).get("verdict")
        if stored != verdict:
            bad.append(f"{c['candidate_id']}: 저장 verdict({stored}) != 재실행({verdict})")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_f2_val_")
    p = os.path.join(tmp, "sim.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, V0_2_VALIDATOR, p], capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr)[-300:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for p, n in ((DRYRUN, "dryrun"), (INVENTORY, "inventory"), (INDEX_IMPACT, "index_impact")):
        if not os.path.exists(p):
            print(f"[FATAL] {n} 산출물 없음: {p}\n  먼저 `python3 scripts/integrate_f2_tetracycline_batch_v1_4.py`")
            return 1
    art = json.load(open(DRYRUN, encoding="utf-8"))
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    imp = json.load(open(INDEX_IMPACT, encoding="utf-8"))["impact"]
    exp = json.load(open(EXPORT, encoding="utf-8"))

    # 0) 안전 불변
    ck(len(exp["relations"]) == LIVE_RELATIONS, f"라이브 relations != {LIVE_RELATIONS}")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, "라이브 meta != 60")
    ck(exp["meta"].get("published") is False, "라이브 published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "라이브 clinical_reviewed != false")
    ck(not any(r.get("ingredient") == "테트라사이클린" for r in exp["relations"]),
       "테트라사이클린 이미 라이브 — 드라이런 전제 위반")
    ck(not any("제산제" in (r.get("nutrient") or "") and r.get("ingredient", "").endswith("사이클린")
               for r in exp["relations"]), "테트라사이클린계×제산제 이미 라이브 — 전제 위반")

    art_bad = validate_artifact(art, exp)
    ck(not art_bad, f"dryrun 계약 위반: {art_bad}")
    inv_bad = validate_inventory(inv)
    ck(not inv_bad, f"inventory 계약 위반: {inv_bad}")

    # 4) index impact
    ck(imp.get("relation_card_flip_required") == 0, f"index 자동 flip != 0 ({imp.get('relation_card_flip_required')})")
    ck(imp.get("automatic_flip_from_relation_integration") == 0, "automatic_flip != 0")
    ck(imp.get("alias_change_required") is False, "alias 변경 필요 != false")
    ck(imp.get("index_change_required") is False, "index 변경 필요 != false")
    ck(imp.get("full_index_counts_current", {}).get("relation_card") == RELATION_CARD, "relation_card != 1168")
    ck(imp.get("full_index_counts_current", {}).get("name_only") == NAME_ONLY, "name_only != 16412")
    ck(imp.get("latent_flip_if_alias_enriched") == 1, f"테트라 latent flip != 1 ({imp.get('latent_flip_if_alias_enriched')})")
    ck(imp.get("per_ingredient", {}).get("테트라사이클린", {}).get("name_only") == 1, "테트라사이클린 name_only != 1")
    ck(imp.get("per_ingredient", {}).get("독시사이클린", {}).get("covered_by_relation", 0) > 0, "독시사이클린 covered=0")
    ck(imp.get("per_ingredient", {}).get("미노사이클린", {}).get("covered_by_relation", 0) > 0, "미노사이클린 covered=0")

    # 5) v0.2 sim PASS
    sim = copy.deepcopy(exp)
    sim["relations"] += [e["projected_live_relation"] for e in art["projected_entries"]]
    sim["meta"]["relation_count"] = len(sim["relations"])
    ok, _ = run_v0_2(sim)
    ck(ok, "F2 5건 sim export v0.2 validator FAIL(선행조건 0 입증 실패)")
    ck(art["meta"].get("v0_2_validator_evidence", {}).get("sim_all_passed") is True,
       "artifact sim_all_passed != true")
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 relations 변경됨")

    # 6) 결함주입(12종)
    print("--- 결함주입(검출되어야 PASS) ---")
    inj_fail = []

    def inject(label, mutate):
        a = copy.deepcopy(art)
        mutate(a)
        b = validate_artifact(a, exp)
        ok2 = len(b) > 0
        print(("  PASS " if ok2 else "  FAIL ") + label + ("" if ok2 else "  [검출 실패]"))
        if not ok2:
            inj_fail.append(label)

    def inject_inv(label, mutate):
        a = copy.deepcopy(inv)
        mutate(a)
        b = validate_inventory(a)
        ok2 = len(b) > 0
        print(("  PASS " if ok2 else "  FAIL ") + label + ("" if ok2 else "  [검출 실패]"))
        if not ok2:
            inj_fail.append(label)

    def _antacid_idx(a):
        return next(i for i, e in enumerate(a["projected_entries"])
                    if "제산제" in e["projected_live_relation"].get("nutrient", ""))

    def _nutrient_cand_id(a):
        return next(c["candidate_id"] for c in a["candidates"] if c["counterpart_type"] == "nutrient")

    inject("published=true", lambda a: a["meta"].update(published=True))
    inject("reviewed_by 작성", lambda a: a["meta"].update(reviewed_by="RPH-X"))
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("expected_after_full 오기(70)", lambda a: a["meta"].update(expected_relation_count_after_full=70))
    inject("제품 카피 삽입", lambda a: a["projected_entries"][0]["projected_live_relation"].update(
        display_text_ko=a["projected_entries"][0]["projected_live_relation"]["display_text_ko"] + " 지금 구매하세요"))
    inject("보충 권유 카피 삽입", lambda a: a["projected_entries"][0]["projected_live_relation"].update(
        management_ko="철분을 매일 드시는 것이 좋습니다"))
    inject("itemSeq 합성값", lambda a: a["projected_entries"][0]["projected_live_relation"]["source"].update(
        url="https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?seq=합성"))
    inject("existing live 중복 삽입(독시×철분)", lambda a: a["projected_entries"][2]["projected_live_relation"].update(
        ingredient="독시사이클린", nutrient="철분") or a["projected_entries"][2]["projected_live_relation"].pop("counterpart_category", None))
    inject("antacid를 Mg 영양소로 변조", lambda a: (
        a["projected_entries"][_antacid_idx(a)]["projected_live_relation"].update(nutrient="마그네슘"),
        a["projected_entries"][_antacid_idx(a)]["projected_live_relation"].pop("counterpart_category", None)))
    inject("candidate 누락(projected 4건)", lambda a: a["projected_entries"].pop())
    inject_inv("source_quote 누락(재실행 reverify L2 fail)",
               lambda a: a["candidates"].__setitem__(
                   next(i for i, c in enumerate(a["candidates"]) if c["candidate_id"] == _nutrient_cand_id(a)),
                   {**next(c for c in a["candidates"] if c["counterpart_type"] == "nutrient"), "source_quote": ""}))
    inject_inv("bone/teeth/pregnancy 문맥 오인(재실행 reverify L6 fail)",
               lambda a: a["candidates"][0].update(source_quote=a["candidates"][0]["source_quote"] + " 소아 치아 착색 주의"))
    fails.extend(inj_fail)

    print(f"=== F2 테트라사이클린 dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 예상 "
          f"{art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} "
          f"(full 60→{art['meta'].get('expected_relation_count_after_full')} · F1 후 78→83) ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — F2 5건 계약 안전(60→65·id 62~66·al_mg_antacid/영양소 분기·draft누출0·제품/보충/지시/항응고 0·"
          "live·F1·pending 무충돌·라이브 무수정) · inventory reverify(survives5·강등0·재실행 일치) · index 자동 flip 0/테트라 latent 1 · "
          "sim v0.2 PASS(선행조건 0) · 결함주입 12종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
