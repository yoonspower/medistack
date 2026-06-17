#!/usr/bin/env python3
"""
validate_f3_bisphosphonate_dryrun_v1_4.py
MediStack — F3 비스포스포네이트 **live 통합 드라이런 검증**(읽기전용). export/full index/aliases/src 무수정.
integrate_f3_bisphosphonate_batch_v1_4.py(dry-run)가 만든 산출물 3종이 통합 시 안전·계약을 만족하는지 검증 +
결함주입 12종으로 검증기 자체 입증.

⚠️ F2 대비 핵심 차이: F3 reviewer-ready 3 중 **survives 1(0147)·needs_review 2(0148/0149 에티드론산 standalone parse 취약)**.
  → 통합 가능분 = 1건뿐. validate_artifact 는 projected 전건이 **재실행 reverify=survives** 인지 추가 검증(needs_review 통합 차단).

검사:
  0) 안전 불변: live export 무변경(relations==60·meta 60·published/clinical=false·이반드론산×제산제 미존재).
  1) dryrun 메타: live_write_performed=false·promotion=0·published/clinical=false·reviewed_by 공란·
     export_sha_after_same=true·survives 60→61·conditional 60→63·F1 후 78→79·F1+F2 후 83→84·prerequisites 빈·needs_review 2.
  2) projected 1 계약: id(live disjoint·무중복)·필수 live 필드·draft 누출 0·product/potassium/clinical=false·
     reviewed_by 부재·source itemSeq·ingredient 드론산·al_mg_antacid(약물) category·live 60 무중복·F1/F2/페니실라민/칼륨/AT-FEX 무충돌·
     금칙어/제품/보충 0·항응고 0·복용지시 0·**전건 재실행 reverify=survives(needs_review 통합 차단)**.
  3) inventory(작업 B/C): 3건·reverify(survives 1·needs_review 2)·per-candidate 기대 verdict(0147 survives·0148/0149 needs_review)·
     재실행 reverify 일치(소스 fidelity·강등 보존).
  4) index impact(작업 K): 자동 flip 0·alias 변경 false·relation_card 1168/name_only 16412 불변·현 scope latent 0(이반드론산 covered)·
     에티드론산 조건부 latent 1.
  5) v0.2 validator: survives 1건 시뮬 export PASS(재실행) → 선행조건 0.
  6) 결함주입 12종 → 전건 검출.
사용: python3 scripts/validate_f3_bisphosphonate_dryrun_v1_4.py
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
DRYRUN = os.path.join(DATA, "review", "f3_bisphosphonate_live_dryrun_v1_4.json")
INVENTORY = os.path.join(DATA, "review", "f3_bisphosphonate_inventory_v1_4.json")
INDEX_IMPACT = os.path.join(DATA, "review", "f3_bisphosphonate_index_impact_v1_4.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60
F3_REVIEWER_READY = 3
F3_SURVIVES = 1
ANTACID_CATEGORY = "al_mg_antacid"
RELATION_CARD = 1168
NAME_ONLY = 16412
NUTRIENT_SET = ("칼슘", "철분")
EXPECTED_VERDICTS = {"RF-F3-0147": "survives", "RF-F3-0148": "needs_review", "RF-F3-0149": "needs_review"}


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


f3 = _load("f3", "integrate_f3_bisphosphonate_batch_v1_4.py")
integ = f3.integ
vfp = f3.vfp
PRODUCT_PHRASES = f3.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = f3.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = f3.DIRECTIVE_CMDS
ANTICOAG_TERMS = f3.ANTICOAG_TERMS
DRAFT_ONLY = integ.DRAFT_ONLY
_F3_BATCH = {r["candidate_id"]: r for r in f3.load_f3()[0]}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def _rerun_verdict(cid):
    """candidate_id 의 batch 원본 레코드를 재로딩해 reverify 재실행(needs_review 통합 차단·강등 보존)."""
    rec = _F3_BATCH.get(cid)
    if rec is None:
        return None
    _L, verdict, _f = f3.reverify(rec)
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
    if meta.get("expected_relation_count_after_survives") != live_count + F3_SURVIVES:
        bad.append("expected_after_survives != 60+1")
    if meta.get("expected_relation_count_after_conditional_full") != live_count + F3_REVIEWER_READY:
        bad.append("expected_after_conditional_full != 60+3")
    if meta.get("requested_scope") == "survives" and after != live_count + F3_SURVIVES:
        bad.append(f"survives scope after != 61 ({after})")
    if meta.get("live_integration_prerequisites") != []:
        bad.append(f"F3 선행조건은 0이어야: {meta.get('live_integration_prerequisites')}")
    if sorted(meta.get("needs_review_ids", [])) != ["RF-F3-0148", "RF-F3-0149"]:
        bad.append(f"needs_review_ids != [0148,0149] ({meta.get('needs_review_ids')})")
    if meta.get("survives_ids") != ["RF-F3-0147"]:
        bad.append(f"survives_ids != [0147] ({meta.get('survives_ids')})")
    # scope_scenarios 일관
    ss = meta.get("scope_scenarios", {})
    if ss.get("survives", {}).get("expected_count") != live_count + F3_SURVIVES:
        bad.append("scope survives expected_count != 61")
    if ss.get("scenario_if_f1_already_live", {}).get("expected_after_survives") != 79:
        bad.append("scenario_if_f1 survives != 79")
    if ss.get("scenario_if_f1_and_f2_already_live", {}).get("expected_after_survives") != 84:
        bad.append("scenario_if_f1_and_f2 survives != 84")
    if ss.get("conditional_if_etidronate_parse_resolved", {}).get("expected_count_after_with_survives") != live_count + F3_REVIEWER_READY:
        bad.append("conditional full != 63")
    if meta.get("guard_checks", {}).get("no_needs_review_integrated") is not True:
        bad.append("guard no_needs_review_integrated != true")

    # projected 계약(요청 scope=survives 기준 = 1)
    ids = [e.get("projected_id") for e in entries]
    if meta.get("requested_scope") == "survives" and len(entries) != F3_SURVIVES:
        bad.append(f"survives projected_entries != {F3_SURVIVES} ({len(entries)})")
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 중복")
    seen = set()
    for e in entries:
        cid = e.get("candidate_id", "?")
        rel = e.get("projected_live_relation", {})
        # ★ needs_review 통합 차단 — 재실행 reverify 가 survives 여야(강등 후보 주입 검출)
        rv = _rerun_verdict(cid)
        if rv not in ("survives", "survives_with_copy_change"):
            bad.append(f"{cid}: projected 인데 재실행 reverify={rv} (needs_review 통합 금지)")
        if e.get("reverify_verdict") not in ("survives", "survives_with_copy_change"):
            bad.append(f"{cid}: reverify_verdict 비-survives")
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
        if not rel.get("ingredient", "").endswith("드론산"):
            bad.append(f"{cid}: ingredient 비스포스포네이트 아님({rel.get('ingredient')})")
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
        # pending/타 트랙 충돌(F1 록사신·F2 사이클린·칼륨·AT-FEX·페니실라민)
        if rel.get("ingredient") in ("펙소페나딘", "페니실라민") or rel.get("ingredient", "").endswith("록사신") \
                or rel.get("ingredient", "").endswith("사이클린") or nut == "칼륨" or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: F1/F2/AT-FEX/페니실라민/칼륨 트랙 충돌")
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
    if len(cands) != F3_REVIEWER_READY:
        bad.append(f"inventory candidates != {F3_REVIEWER_READY} ({len(cands)})")
    rc = meta.get("reverify_counts", {})
    if rc.get("survives") != 1 or rc.get("needs_review") != 2:
        bad.append(f"reverify counts != survives1/needs_review2 ({rc})")
    if (rc.get("hold", 0) + rc.get("reject", 0)) != 0:
        bad.append(f"reverify hold/reject != 0 ({rc})")
    if meta.get("survives_count") != 1:
        bad.append(f"survives_count != 1 ({meta.get('survives_count')})")
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
        if c["candidate_id"] in f3.F3_COPY_CHANGES:
            rec["_copy_change"] = f3.F3_COPY_CHANGES[c["candidate_id"]]
        _L, verdict, _f = f3.reverify(rec)
        expected = EXPECTED_VERDICTS.get(c["candidate_id"])
        if expected and verdict != expected:
            bad.append(f"{c['candidate_id']}: 재실행 reverify verdict={verdict} (기대 {expected})")
        stored = c.get("reverify", {}).get("verdict")
        if stored != verdict:
            bad.append(f"{c['candidate_id']}: 저장 verdict({stored}) != 재실행({verdict})")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_f3_val_")
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
            print(f"[FATAL] {n} 산출물 없음: {p}\n  먼저 `python3 scripts/integrate_f3_bisphosphonate_batch_v1_4.py`")
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
    ck(not any("제산제" in (r.get("nutrient") or "") and r.get("ingredient", "").endswith("드론산")
               for r in exp["relations"]), "비스포×제산제 이미 라이브 — 전제 위반")

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
    ck(imp.get("latent_flip_if_alias_enriched_this_scope") == 0,
       f"현 scope latent flip != 0 ({imp.get('latent_flip_if_alias_enriched_this_scope')})")
    ck(imp.get("latent_flip_if_etidronate_resolved_and_enriched") == 1, "에티드론산 조건부 latent != 1")
    ck(imp.get("per_ingredient", {}).get("이반드론산", {}).get("covered_by_relation", 0) > 0, "이반드론산 covered=0")
    ck(imp.get("per_ingredient", {}).get("에티드론산", {}).get("name_only") == 1, "에티드론산 name_only != 1")
    ck(imp.get("per_ingredient", {}).get("에티드론산", {}).get("in_aliases") is False, "에티드론산 in_aliases != false")

    # 5) v0.2 sim PASS
    sim = copy.deepcopy(exp)
    sim["relations"] += [e["projected_live_relation"] for e in art["projected_entries"]]
    sim["meta"]["relation_count"] = len(sim["relations"])
    ok, _ = run_v0_2(sim)
    ck(ok, "F3 survives 1건 sim export v0.2 validator FAIL(선행조건 0 입증 실패)")
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

    e0 = lambda a: a["projected_entries"][0]["projected_live_relation"]

    inject("published=true", lambda a: a["meta"].update(published=True))
    inject("reviewed_by 작성", lambda a: a["meta"].update(reviewed_by="RPH-X"))
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("expected_after_survives 오기(63)", lambda a: a["meta"].update(expected_relation_count_after_survives=63))
    inject("needs_review_ids 누락(0148만)", lambda a: a["meta"].update(needs_review_ids=["RF-F3-0148"]))
    inject("제품 카피 삽입", lambda a: e0(a).update(
        display_text_ko=e0(a)["display_text_ko"] + " 지금 구매하세요"))
    inject("보충 권유 카피 삽입", lambda a: e0(a).update(management_ko="칼슘을 매일 드시는 것이 좋습니다"))
    inject("itemSeq 합성값", lambda a: e0(a)["source"].update(
        url="https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?seq=합성"))
    inject("existing live 중복 삽입(이반드론산×칼슘)", lambda a: (
        e0(a).update(ingredient="이반드론산", nutrient="칼슘"), e0(a).pop("counterpart_category", None)))
    inject("needs_review(에티드론산 0148) 통합 삽입", lambda a: a["projected_entries"].append({
        "candidate_id": "RF-F3-0148", "reverify_verdict": "survives",
        "projected_live_relation": {**copy.deepcopy(e0(a)), "id": 99, "ingredient": "에티드론산",
                                    "nutrient": "칼슘", "display_text_ko": "x", "management_ko": "약사 또는 의사와 상담하세요"}}) or a["projected_entries"][-1]["projected_live_relation"].pop("counterpart_category", None))
    inject_inv("0148 강등 위변조(needs_review→survives, parse 토큰 제거)",
               lambda a: next(c for c in a["candidates"] if c["candidate_id"] == "RF-F3-0148").update(
                   source_quote="에티드론산은 칼슘보충제와 함께 복용 시 흡수가 저하될 수 있다",
                   reverify={**next(c for c in a["candidates"] if c["candidate_id"] == "RF-F3-0148")["reverify"], "verdict": "survives"}))
    inject_inv("survives_count 위조(3)", lambda a: a["meta"].update(survives_count=3))
    fails.extend(inj_fail)

    print(f"=== F3 비스포스포네이트 dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 예상 "
          f"{art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} "
          f"(survives 60→61 · conditional 60→63 · F1 후 78→79 · F1+F2 후 83→84) ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — F3 survives 1건 계약 안전(60→61·al_mg_antacid·draft누출0·제품/보충/지시/항응고 0·"
          "live·F1·F2·pending 무충돌·needs_review 통합 차단·라이브 무수정) · inventory reverify(survives1·needs_review2·"
          "per-candidate 기대 verdict·재실행 일치) · index 자동 flip 0/현 scope latent 0/에티드론산 조건부 latent 1 · "
          "sim v0.2 PASS(선행조건 0) · 결함주입 12종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
