#!/usr/bin/env python3
"""
validate_f9_chronic_depletion_dryrun_v1_4.py
MediStack — F9 만성복용 depletion **live 통합 드라이런 검증**(읽기전용). export/full index/aliases/src 무수정.
integrate_f9_chronic_depletion_batch_v1_4.py(dry-run)가 만든 산출물 3종이 통합 시 안전·계약을 만족하는지 검증 +
결함주입 13종으로 검증기 자체 입증.

⚠️ 핵심: F9 reviewer-ready 8 중 **survives 3·copy_change 4·needs_review 1(0245 저신호 이상반응 열거)** → 통합 가능 7.
  validate_artifact 는 projected 전건이 **재실행 reverify∈{survives,copy_change}** 인지 추가 검증(needs_review 통합 차단).

검사:
  0) 안전 불변: live export 무변경(relations==60·meta 60·published/clinical=false·F9 약물/엽산/비타민D 미존재).
  1) dryrun 메타: live_write_performed=false·promotion=0·published/clinical=false·reviewed_by 공란·
     export_sha_after_same=true·integrable 60→67·survives 60→63·copy_change 60→64·conditional 60→68·F1F2F3 후 84→91·needs_review 1.
  2) projected 7 계약: id(live disjoint·무중복)·필수 live 필드·draft 누출 0·product/potassium/clinical=false·
     reviewed_by 부재·source itemSeq·mechanism=depletion·action=monitoring·nutrient∈{엽산,비타민D}·counterpart_category 부재·
     live 60 무중복·F1/F2/F3/페니실라민/칼륨/AT-FEX 무충돌·금칙어/제품/보충/검사지시 0·항응고 0·display 소아/골 0·
     **전건 재실행 reverify∈{survives,copy_change}(needs_review 통합 차단)**.
  3) inventory(작업 B/C): 8건·reverify(survives 3·copy_change 4·needs_review 1)·per-candidate 기대 verdict·재실행 일치(소스 fidelity·강등 보존).
  4) index impact(작업 K): 자동 flip 0·alias 변경 false·relation_card 1168/name_only 16412 불변·현 scope latent 18(조건부)·통합 가능 전체 latent 18.
  5) v0.2 validator: integrable 7건 시뮬 export PASS(재실행) → 선행조건 0.
  6) 결함주입 13종 → 전건 검출.
사용: python3 scripts/validate_f9_chronic_depletion_dryrun_v1_4.py
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
DRYRUN = os.path.join(DATA, "review", "f9_chronic_depletion_live_dryrun_v1_4.json")
INVENTORY = os.path.join(DATA, "review", "f9_chronic_depletion_inventory_v1_4.json")
INDEX_IMPACT = os.path.join(DATA, "review", "f9_chronic_depletion_index_impact_v1_4.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60
F9_REVIEWER_READY = 8
F9_INTEGRABLE = 7
F9_SURVIVES = 3
F9_COPY_CHANGE = 4
F9_CONDITIONAL_FULL = 8
TRUE_BASE = 84
RELATION_CARD = 1168
NAME_ONLY = 16412
LATENT_THIS_SCOPE = 18
NUTRIENT_SET = ("엽산", "비타민D")
EXPECTED_VERDICTS = {
    "RF-F9-0269": "survives", "RF-F9-0246": "survives", "RF-F9-0272": "survives",
    "RF-F9-0242": "survives_with_copy_change", "RF-F9-0252": "survives_with_copy_change",
    "RF-F9-0243": "survives_with_copy_change", "RF-F9-0255": "survives_with_copy_change",
    "RF-F9-0245": "needs_review",
}


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f9 = _load("f9", "integrate_f9_chronic_depletion_batch_v1_4.py")
integ = f9.integ
vfp = f9.vfp
PRODUCT_PHRASES = f9.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f9.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f9.DIRECTIVE_CMDS
TEST_TREAT_DIRECTIVE = f9.TEST_TREAT_DIRECTIVE
ANTICOAG_TERMS = f9.ANTICOAG_TERMS
PEDIATRIC_BONE_TERMS = f9.PEDIATRIC_BONE_TERMS
DRAFT_ONLY = integ.DRAFT_ONLY
_F9_BATCH = {r["candidate_id"]: r for r in f9.load_f9()[0]}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def _rerun_verdict(cid):
    """candidate_id 의 batch 원본 레코드를 재로딩해 reverify 재실행(needs_review 통합 차단·강등 보존)."""
    rec = _F9_BATCH.get(cid)
    if rec is None:
        return None
    _L, verdict, _f = f9.reverify(rec)
    return verdict


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
    if meta.get("expected_relation_count_after_integrable") != live_count + F9_INTEGRABLE:
        bad.append("expected_after_integrable != 60+7")
    if meta.get("expected_relation_count_after_survives") != live_count + F9_SURVIVES:
        bad.append("expected_after_survives != 60+3")
    if meta.get("expected_relation_count_after_copy_change") != live_count + F9_COPY_CHANGE:
        bad.append("expected_after_copy_change != 60+4")
    if meta.get("expected_relation_count_after_conditional_full") != live_count + F9_CONDITIONAL_FULL:
        bad.append("expected_after_conditional_full != 60+8")
    if meta.get("requested_scope") == "integrable" and after != live_count + F9_INTEGRABLE:
        bad.append(f"integrable scope after != 67 ({after})")
    if meta.get("live_integration_prerequisites") != []:
        bad.append(f"F9 선행조건은 0이어야: {meta.get('live_integration_prerequisites')}")
    if meta.get("needs_review_ids") != ["RF-F9-0245"]:
        bad.append(f"needs_review_ids != [0245] ({meta.get('needs_review_ids')})")
    if sorted(meta.get("integrable_ids", [])) != sorted(
            [c for c, v in EXPECTED_VERDICTS.items() if v != "needs_review"]):
        bad.append(f"integrable_ids != 기대 7 ({meta.get('integrable_ids')})")
    # scope_scenarios 일관
    ss = meta.get("scope_scenarios", {})
    if ss.get("integrable", {}).get("expected_count") != live_count + F9_INTEGRABLE:
        bad.append("scope integrable expected_count != 67")
    if ss.get("folate", {}).get("expected_count") != live_count + 3:
        bad.append("scope folate expected_count != 63")
    if ss.get("vitd", {}).get("expected_count") != live_count + 4:
        bad.append("scope vitd expected_count != 64")
    if ss.get("scenario_on_f1f2f3_true_base", {}).get("expected_after_integrable") != TRUE_BASE + F9_INTEGRABLE:
        bad.append("scenario_on_f1f2f3 integrable != 91")
    if ss.get("scenario_on_f1f2f3_true_base", {}).get("expected_after_conditional_full") != TRUE_BASE + F9_CONDITIONAL_FULL:
        bad.append("scenario_on_f1f2f3 conditional != 92")
    if ss.get("conditional_if_0245_resolved", {}).get("expected_count_after_with_integrable") != live_count + F9_CONDITIONAL_FULL:
        bad.append("conditional 0245 != 68")
    if meta.get("guard_checks", {}).get("no_needs_review_integrated") is not True:
        bad.append("guard no_needs_review_integrated != true")

    # projected 계약(요청 scope=integrable 기준 = 7)
    ids = [e.get("projected_id") for e in entries]
    if meta.get("requested_scope") == "integrable" and len(entries) != F9_INTEGRABLE:
        bad.append(f"integrable projected_entries != {F9_INTEGRABLE} ({len(entries)})")
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 중복")
    seen = set()
    for e in entries:
        cid = e.get("candidate_id", "?")
        rel = e.get("projected_live_relation", {})
        # ★ needs_review 통합 차단 — 재실행 reverify 가 통합 가능이어야(강등 후보 주입 검출)
        rv = _rerun_verdict(cid)
        if rv not in ("survives", "survives_with_copy_change"):
            bad.append(f"{cid}: projected 인데 재실행 reverify={rv} (needs_review 통합 금지)")
        if e.get("reverify_verdict") not in ("survives", "survives_with_copy_change"):
            bad.append(f"{cid}: reverify_verdict 비-통합가능")
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
        if rel.get("mechanism") != "depletion":
            bad.append(f"{cid}: mechanism != depletion ({rel.get('mechanism')})")
        if rel.get("recommended_action") != "monitoring":
            bad.append(f"{cid}: recommended_action != monitoring ({rel.get('recommended_action')})")
        nut = rel.get("nutrient", "")
        if nut not in NUTRIENT_SET:
            bad.append(f"{cid}: 영양소 counterpart 비정상({nut})")
        if "counterpart_category" in rel:
            bad.append(f"{cid}: 영양소인데 counterpart_category 키 존재(생략이어야)")
        pair = (rel.get("ingredient"), nut)
        if pair in live_pairs:
            bad.append(f"{cid}: 기존 live 60 과 중복 {pair}")
        if pair in seen:
            bad.append(f"{cid}: 배치 내 중복 {pair}")
        seen.add(pair)
        # pending/타 트랙 충돌(F1 록사신·F2 사이클린·F3 드론산·칼륨·AT-FEX·페니실라민)
        if rel.get("ingredient") in ("펙소페나딘", "페니실라민") or rel.get("ingredient", "").endswith("록사신") \
                or rel.get("ingredient", "").endswith("사이클린") or rel.get("ingredient", "").endswith("드론산") \
                or nut == "칼륨" or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: F1/F2/F3/AT-FEX/페니실라민/칼륨 트랙 충돌")
        copy_txt = f'{rel.get("display_text_ko", "")} {rel.get("management_ko", "")}'
        for b in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {b}")
        if any(p in copy_txt for p in PRODUCT_PHRASES):
            bad.append(f"{cid}: 제품 문구")
        if any(p in copy_txt for p in SUPPLEMENT_RECO_PHRASES):
            bad.append(f"{cid}: 보충 권유")
        if any(c in copy_txt for c in DIRECTIVE_CMDS + TEST_TREAT_DIRECTIVE):
            bad.append(f"{cid}: 복용/검사/처방 지시")
        if any(t in copy_txt for t in ANTICOAG_TERMS):
            bad.append(f"{cid}: 항응고/비타민K 혼입")
        if any(t in copy_txt for t in PEDIATRIC_BONE_TERMS):
            bad.append(f"{cid}: display 소아/골/치아 알람어")
    return bad


def validate_inventory(inv):
    bad = []
    meta = inv.get("meta", {})
    cands = inv.get("candidates", [])
    if len(cands) != F9_REVIEWER_READY:
        bad.append(f"inventory candidates != {F9_REVIEWER_READY} ({len(cands)})")
    rc = meta.get("reverify_counts", {})
    if rc.get("survives") != F9_SURVIVES or rc.get("survives_with_copy_change") != F9_COPY_CHANGE \
            or rc.get("needs_review") != 1:
        bad.append(f"reverify counts != survives3/copy4/needs1 ({rc})")
    if (rc.get("hold", 0) + rc.get("reject", 0)) != 0:
        bad.append(f"reverify hold/reject != 0 ({rc})")
    if meta.get("integrable_count") != F9_INTEGRABLE:
        bad.append(f"integrable_count != 7 ({meta.get('integrable_count')})")
    if meta.get("published") is not False or meta.get("clinical_reviewed") is not False:
        bad.append("inventory published/clinical != false")
    # 재실행 reverify — per-candidate 기대 verdict(강등 보존·소스 fidelity 위변조 검출)
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
        if c["candidate_id"] in f9.F9_COPY_CHANGES:
            rec["_copy_change"] = f9.F9_COPY_CHANGES[c["candidate_id"]]
        _L, verdict, _f = f9.reverify(rec)
        expected = EXPECTED_VERDICTS.get(c["candidate_id"])
        if expected and verdict != expected:
            bad.append(f"{c['candidate_id']}: 재실행 reverify verdict={verdict} (기대 {expected})")
        stored = c.get("reverify", {}).get("verdict")
        if stored != verdict:
            bad.append(f"{c['candidate_id']}: 저장 verdict({stored}) != 재실행({verdict})")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_f9_val_")
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
            print(f"[FATAL] {n} 산출물 없음: {p}\n  먼저 `python3 scripts/integrate_f9_chronic_depletion_batch_v1_4.py`")
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
    ck(not any(r.get("nutrient") in NUTRIENT_SET for r in exp["relations"]),
       "엽산/비타민D 이미 라이브 — 전제 위반")

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
    ck(imp.get("latent_flip_if_alias_enriched_this_scope") == LATENT_THIS_SCOPE,
       f"현 scope latent flip != {LATENT_THIS_SCOPE} ({imp.get('latent_flip_if_alias_enriched_this_scope')})")
    ck(imp.get("latent_flip_if_alias_enriched_all_integrable") == LATENT_THIS_SCOPE, "통합 가능 전체 latent != 18")
    for ing in ("설파살라진", "카르바마제핀", "트리메토프림", "페니토인", "프리미돈"):
        ck(imp.get("per_ingredient", {}).get(ing, {}).get("in_aliases") is False, f"{ing} in_aliases != false")

    # 5) v0.2 sim PASS
    sim = copy.deepcopy(exp)
    sim["relations"] += [e["projected_live_relation"] for e in art["projected_entries"]]
    sim["meta"]["relation_count"] = len(sim["relations"])
    ok, _ = run_v0_2(sim)
    ck(ok, "F9 integrable 7건 sim export v0.2 validator FAIL(선행조건 0 입증 실패)")
    ck(art["meta"].get("v0_2_validator_evidence", {}).get("sim_all_passed") is True,
       "artifact sim_all_passed != true")
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 relations 변경됨")

    # 6) 결함주입(13종)
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

    e0 = lambda a: a["projected_entries"][0]["projected_live_relation"]

    inject("published=true", lambda a: a["meta"].update(published=True))
    inject("reviewed_by 작성", lambda a: a["meta"].update(reviewed_by="RPH-X"))
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("expected_after_integrable 오기(68)", lambda a: a["meta"].update(expected_relation_count_after_integrable=68))
    inject("needs_review_ids 누락(빈)", lambda a: a["meta"].update(needs_review_ids=[]))
    inject("제품 카피 삽입", lambda a: e0(a).update(
        display_text_ko=e0(a)["display_text_ko"] + " 지금 구매하세요"))
    inject("보충 권유 카피 삽입", lambda a: e0(a).update(management_ko="엽산을 매일 보충하세요"))
    inject("검사 지시 카피 삽입", lambda a: e0(a).update(management_ko="정기적으로 혈액 검사를 받으세요"))
    inject("골질환 알람어 display 삽입", lambda a: e0(a).update(display_text_ko=e0(a)["display_text_ko"] + " 골연화증 위험"))
    inject("mechanism 위조(absorption)", lambda a: e0(a).update(mechanism="absorption"))
    inject("영양소에 약물 category 삽입", lambda a: e0(a).update(counterpart_category="al_mg_antacid"))
    inject("needs_review(0245) 통합 삽입", lambda a: a["projected_entries"].append({
        "candidate_id": "RF-F9-0245", "reverify_verdict": "survives",
        "projected_live_relation": {**copy.deepcopy(e0(a)), "id": 199, "ingredient": "카르바마제핀",
                                    "nutrient": "엽산", "display_text_ko": "x",
                                    "management_ko": "약사 또는 의사와 상담하세요"}}))
    inject_inv("0245 강등 위변조(needs_review→survives, 기전 토큰 주입)",
               lambda a: next(c for c in a["candidates"] if c["candidate_id"] == "RF-F9-0245").update(
                   source_quote="카르바마제핀은 엽산의 흡수가 저하되어 혈청엽산치 저하가 나타날 수 있다",
                   reverify={**next(c for c in a["candidates"] if c["candidate_id"] == "RF-F9-0245")["reverify"], "verdict": "survives"}))
    fails.extend(inj_fail)

    print(f"=== F9 만성복용 depletion dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 예상 "
          f"{art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} "
          f"(integrable 60→67 · survives 60→63 · copy_change 60→64 · conditional 60→68 · F1F2F3 후 84→91) ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — F9 integrable 7건 계약 안전(60→67·depletion/monitoring·영양소(엽산/비타민D)·category 부재·draft누출0·"
          "제품/보충/검사지시/항응고/골알람 0·live·F1·F2·F3·pending 무충돌·needs_review 통합 차단·라이브 무수정) · "
          "inventory reverify(survives3·copy4·needs1·per-candidate 기대 verdict·재실행 일치) · index 자동 flip 0/현 scope latent 18(조건부) · "
          "sim v0.2 PASS(선행조건 0) · 결함주입 13종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
