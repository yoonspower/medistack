#!/usr/bin/env python3
"""
validate_f4_f6_f10_small_family_dryrun_v1_4.py
MediStack — F4/F6/F10 small-family bundle **live 통합 드라이런 검증**(읽기전용). export/full index/aliases/src 무수정.
integrate_f4_f6_f10_small_family_batch_v1_4.py(dry-run)가 만든 산출물 3종이 통합 시 안전·계약을 만족하는지 검증 +
결함주입 14종으로 검증기 자체 입증.

⚠️ 핵심: reviewer-ready 3 중 **survives 0·copy_change 2(0173/0201)·needs_review 1(0275 route/availability)** → 통합 가능 2.
  validate_artifact 는 projected 전건이 **재실행 reverify∈{survives,copy_change}** 인지 + (route 강등)0275 미통합인지 추가 검증.

검사:
  0) 안전 불변: live export 무변경(relations==60·meta 60·published/clinical=false·레보티록신×제산제/에스오메프라졸×B12 미존재).
  1) dryrun 메타: live_write_performed=false·promotion=0·published/clinical=false·reviewed_by 공란·sha 동일·
     integrable 60→62·conditional(0275) 60→63·F1F2F3F9 후 91→93/94·needs_review 1(0275).
  2) projected 2 계약: id disjoint·필수 live 필드·draft 누출 0·product/potassium/clinical=false·reviewed_by 부재·source itemSeq·
     mechanism∈{absorption,depletion}·action∈{separation,monitoring}·antacid⇒al_mg_antacid·B12⇒category 부재·
     F4 display 'Mg' 비단정·0275 dosing(2시간/콜라) display 비노출·live 60 무중복·F1/F2/F3/F9 무충돌·금칙어/제품/보충/검사지시 0·
     **전건 재실행 reverify∈{survives,copy_change}(needs_review 통합 차단)**.
  3) inventory(작업 B/C): 3건·reverify(survives0·copy2·needs1)·per-candidate 기대 verdict·재실행 일치(route 강등·Al-only·PPI 톤 보존).
  4) index impact: 자동 flip 0·alias 변경 false·relation_card 1168/name_only 16412 불변·latent 0(레보티록신 covered·에스오 색인0·케토 외용).
  5) v0.2 validator: integrable 2건 시뮬 export PASS(재실행) → 선행조건 0.
  6) 결함주입 14종 → 전건 검출.
사용: python3 scripts/validate_f4_f6_f10_small_family_dryrun_v1_4.py
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
DRYRUN = os.path.join(DATA, "review", "f4_f6_f10_small_family_live_dryrun_v1_4.json")
INVENTORY = os.path.join(DATA, "review", "f4_f6_f10_small_family_inventory_v1_4.json")
INDEX_IMPACT = os.path.join(DATA, "review", "f4_f6_f10_small_family_index_impact_v1_4.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60
REVIEWER_READY = 3
INTEGRABLE = 2
SURVIVES = 0
COPY_CHANGE = 2
NEEDS_REVIEW = 1
CONDITIONAL_FULL = 3      # integrable 2 + needs_review 1
TRUE_BASE = 91           # F1 18 + F2 5 + F3 1 + F9 7 모두 live
RELATION_CARD = 1168
NAME_ONLY = 16412
LATENT_THIS_SCOPE = 0    # 레보티록신 covered(name_only 0)·에스오메프라졸 색인 0·케토 외용(미통합) → latent 0
LATENT_ALL = 0
EXPECTED_VERDICTS = {
    "RF-F4-0173": "survives_with_copy_change",
    "RF-F6-0201": "survives_with_copy_change",
    "RF-F10-0275": "needs_review",
}


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


b = _load("bundle", "integrate_f4_f6_f10_small_family_batch_v1_4.py")
integ = b.integ
vfp = b.vfp
PRODUCT_PHRASES = b.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = b.SUPPLEMENT_RECO_PHRASES
DIRECTIVE_CMDS = b.DIRECTIVE_CMDS
TEST_TREAT_DIRECTIVE = b.TEST_TREAT_DIRECTIVE
ANTICOAG_TERMS = b.ANTICOAG_TERMS
PEDIATRIC_BONE_TERMS = b.PEDIATRIC_BONE_TERMS
DOSING_DETAIL_TERMS = b.DOSING_DETAIL_TERMS
DRAFT_ONLY = integ.DRAFT_ONLY
_BATCH = {r["candidate_id"]: r for r in b.load_bundle()[0]}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def _rerun_verdict(cid):
    rec = _BATCH.get(cid)
    if rec is None:
        return None
    _L, verdict, _f = b.reverify(rec)
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
    if meta.get("expected_relation_count_after_integrable") != live_count + INTEGRABLE:
        bad.append("expected_after_integrable != 60+2")
    if meta.get("requested_scope") == "integrable" and after != live_count + INTEGRABLE:
        bad.append(f"integrable scope after != 62 ({after})")
    if meta.get("live_integration_prerequisites") != []:
        bad.append(f"선행조건은 0이어야: {meta.get('live_integration_prerequisites')}")
    if meta.get("needs_review_ids") != ["RF-F10-0275"]:
        bad.append(f"needs_review_ids != [0275] ({meta.get('needs_review_ids')})")
    if sorted(meta.get("integrable_ids", [])) != sorted(
            [c for c, v in EXPECTED_VERDICTS.items() if v != "needs_review"]):
        bad.append(f"integrable_ids != 기대 2 ({meta.get('integrable_ids')})")
    if sorted(meta.get("copy_change_ids", [])) != ["RF-F4-0173", "RF-F6-0201"]:
        bad.append(f"copy_change_ids != [0173,0201] ({meta.get('copy_change_ids')})")
    # scope_scenarios 일관
    ss = meta.get("scope_scenarios", {})
    if ss.get("integrable", {}).get("expected_count") != live_count + INTEGRABLE:
        bad.append("scope integrable expected_count != 62")
    if ss.get("conditional_if_0275_resolved", {}).get("expected_count_after_with_integrable") != live_count + CONDITIONAL_FULL:
        bad.append("conditional 0275 != 63")
    tb = ss.get("scenario_on_f1f2f3f9_true_base", {})
    if tb.get("expected_after_integrable") != TRUE_BASE + INTEGRABLE:
        bad.append("true_base integrable != 93")
    if tb.get("expected_after_conditional_full") != TRUE_BASE + CONDITIONAL_FULL:
        bad.append("true_base conditional != 94")
    if ss.get("family_F10", {}).get("count") != 0:
        bad.append("family_F10 count != 0(needs_review)")
    if meta.get("guard_checks", {}).get("no_needs_review_integrated") is not True:
        bad.append("guard no_needs_review_integrated != true")
    if meta.get("guard_checks", {}).get("f4_no_magnesium_assertion") is not True:
        bad.append("guard f4_no_magnesium_assertion != true")

    ids = [e.get("projected_id") for e in entries]
    if meta.get("requested_scope") == "integrable" and len(entries) != INTEGRABLE:
        bad.append(f"integrable projected_entries != {INTEGRABLE} ({len(entries)})")
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 중복")
    seen = set()
    for e in entries:
        cid = e.get("candidate_id", "?")
        rel = e.get("projected_live_relation", {})
        # ★ needs_review 통합 차단 — 재실행 reverify 가 통합 가능이어야(route 강등 후보 주입 검출)
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
        mech = rel.get("mechanism")
        action = rel.get("recommended_action")
        if mech not in ("absorption", "depletion"):
            bad.append(f"{cid}: mechanism 비허용 ({mech})")
        if action not in ("separation", "monitoring"):
            bad.append(f"{cid}: action 비허용 ({action})")
        nut = rel.get("nutrient", "")
        cat = rel.get("counterpart_category")
        if "제산제" in nut:   # antacid drug counterpart (F4)
            if mech != "absorption" or action != "separation":
                bad.append(f"{cid}: 제산제 relation 인데 absorption/separation 아님({mech}/{action})")
            if cat != "al_mg_antacid":
                bad.append(f"{cid}: 제산제 relation counterpart_category != al_mg_antacid ({cat})")
            if "약물" not in nut:
                bad.append(f"{cid}: 약물 counterpart 표기에 '약물' 없음")
            # F4 Al-only — display 에 '마그네슘' 단정 금지
            if "알루미늄 함유 제산제" in nut and "마그네슘" in rel.get("display_text_ko", ""):
                bad.append(f"{cid}: Al-only relation 인데 display 에 '마그네슘' 단정")
        elif nut == "비타민B12":   # nutrient counterpart (F6)
            if mech != "depletion" or action != "monitoring":
                bad.append(f"{cid}: B12 relation 인데 depletion/monitoring 아님({mech}/{action})")
            if "counterpart_category" in rel:
                bad.append(f"{cid}: 영양소(B12)인데 counterpart_category 키 존재(생략이어야)")
        else:
            bad.append(f"{cid}: counterpart 분류 불명({nut})")
        pair = (rel.get("ingredient"), nut)
        if pair in live_pairs:
            bad.append(f"{cid}: 기존 live 60 과 중복 {pair}")
        if pair in seen:
            bad.append(f"{cid}: 배치 내 중복 {pair}")
        seen.add(pair)
        ing = rel.get("ingredient", "")
        if ing.endswith("록사신") or ing.endswith("사이클린") or ing.endswith("드론산") \
                or ing in ("설파살라진", "카르바마제핀", "트리메토프림", "페노바르비탈", "페니토인", "프리미돈") \
                or nut in ("엽산", "비타민D", "칼륨") or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: F1/F2/F3/F9/칼륨 트랙 충돌")
        copy_txt = f'{rel.get("display_text_ko", "")} {rel.get("management_ko", "")}'
        for fb in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {fb}")
        if any(p in copy_txt for p in PRODUCT_PHRASES):
            bad.append(f"{cid}: 제품 문구")
        if any(p in copy_txt for p in SUPPLEMENT_RECO_PHRASES):
            bad.append(f"{cid}: 보충 권유")
        if any(c in copy_txt for c in DIRECTIVE_CMDS + TEST_TREAT_DIRECTIVE):
            bad.append(f"{cid}: 복용/검사/처방 지시")
        if any(t in copy_txt for t in DOSING_DETAIL_TERMS):
            bad.append(f"{cid}: display 구체 dosing(2시간/콜라 등)")
        if any(t in copy_txt for t in ANTICOAG_TERMS):
            bad.append(f"{cid}: 항응고/비타민K 혼입")
        if any(t in copy_txt for t in PEDIATRIC_BONE_TERMS):
            bad.append(f"{cid}: display 소아/골/치아 알람어")
    return bad


def validate_inventory(inv):
    bad = []
    meta = inv.get("meta", {})
    cands = inv.get("candidates", [])
    if len(cands) != REVIEWER_READY:
        bad.append(f"inventory candidates != {REVIEWER_READY} ({len(cands)})")
    rc = meta.get("reverify_counts", {})
    if rc.get("survives") != SURVIVES or rc.get("survives_with_copy_change") != COPY_CHANGE \
            or rc.get("needs_review") != NEEDS_REVIEW:
        bad.append(f"reverify counts != survives0/copy2/needs1 ({rc})")
    if (rc.get("hold", 0) + rc.get("reject", 0)) != 0:
        bad.append(f"reverify hold/reject != 0 ({rc})")
    if meta.get("integrable_count") != INTEGRABLE:
        bad.append(f"integrable_count != 2 ({meta.get('integrable_count')})")
    if meta.get("published") is not False or meta.get("clinical_reviewed") is not False:
        bad.append("inventory published/clinical != false")
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
        if c["candidate_id"] in b.BUNDLE_COPY_CHANGES:
            rec["_copy_change"] = b.BUNDLE_COPY_CHANGES[c["candidate_id"]]
        _L, verdict, _f = b.reverify(rec)
        expected = EXPECTED_VERDICTS.get(c["candidate_id"])
        if expected and verdict != expected:
            bad.append(f"{c['candidate_id']}: 재실행 reverify verdict={verdict} (기대 {expected})")
        stored = c.get("reverify", {}).get("verdict")
        if stored != verdict:
            bad.append(f"{c['candidate_id']}: 저장 verdict({stored}) != 재실행({verdict})")
    # F10 family context 보존
    fctx = inv.get("f10_family_context", {})
    if fctx.get("RF-F10-0276", {}).get("status") != "hold":
        bad.append("f10_family_context 0276 hold 누락")
    if fctx.get("RF-F10-0277", {}).get("status") != "reject_duplicate_live":
        bad.append("f10_family_context 0277 reject 누락")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_sf_val_")
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
            print(f"[FATAL] {n} 산출물 없음: {p}\n  먼저 `python3 scripts/integrate_f4_f6_f10_small_family_batch_v1_4.py`")
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
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    ck(("레보티록신", "알루미늄 함유 제산제(약물)") not in live_pairs, "레보티록신×제산제 이미 라이브 — 전제 위반")
    ck(("에스오메프라졸", "비타민B12") not in live_pairs, "에스오메프라졸×B12 이미 라이브 — 전제 위반")

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
    ck(imp.get("latent_flip_if_alias_enriched_all_integrable") == LATENT_ALL, "통합 가능 전체 latent != 0")
    ck(imp.get("per_ingredient", {}).get("케토코나졸", {}).get("oral_present") is False,
       "케토코나졸 oral_present != false(route 근거)")

    # 5) v0.2 sim PASS
    sim = copy.deepcopy(exp)
    sim["relations"] += [e["projected_live_relation"] for e in art["projected_entries"]]
    sim["meta"]["relation_count"] = len(sim["relations"])
    ok, _ = run_v0_2(sim)
    ck(ok, "integrable 2건 sim export v0.2 validator FAIL(선행조건 0 입증 실패)")
    ck(art["meta"].get("v0_2_validator_evidence", {}).get("sim_all_passed") is True,
       "artifact sim_all_passed != true")
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 relations 변경됨")

    # 6) 결함주입(14종)
    print("--- 결함주입(검출되어야 PASS) ---")
    inj_fail = []

    def inject(label, mutate):
        a = copy.deepcopy(art)
        mutate(a)
        b2 = validate_artifact(a, exp)
        ok2 = len(b2) > 0
        print(("  PASS " if ok2 else "  FAIL ") + label + ("" if ok2 else "  [검출 실패]"))
        if not ok2:
            inj_fail.append(label)

    def inject_inv(label, mutate):
        a = copy.deepcopy(inv)
        mutate(a)
        b2 = validate_inventory(a)
        ok2 = len(b2) > 0
        print(("  PASS " if ok2 else "  FAIL ") + label + ("" if ok2 else "  [검출 실패]"))
        if not ok2:
            inj_fail.append(label)

    def ent(a, idx=0):
        return a["projected_entries"][idx]["projected_live_relation"]

    def f4_ent(a):
        for e in a["projected_entries"]:
            if "제산제" in e["projected_live_relation"]["nutrient"]:
                return e["projected_live_relation"]
        return ent(a)

    def b12_ent(a):
        for e in a["projected_entries"]:
            if e["projected_live_relation"]["nutrient"] == "비타민B12":
                return e["projected_live_relation"]
        return ent(a)

    inject("published=true", lambda a: a["meta"].update(published=True))
    inject("reviewed_by 작성", lambda a: a["meta"].update(reviewed_by="RPH-X"))
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("expected_after_integrable 오기(63)", lambda a: a["meta"].update(expected_relation_count_after_integrable=63))
    inject("needs_review_ids 누락(빈)", lambda a: a["meta"].update(needs_review_ids=[]))
    inject("제품 카피 삽입", lambda a: f4_ent(a).update(display_text_ko=f4_ent(a)["display_text_ko"] + " 지금 구매하세요"))
    inject("B12 보충 권유 삽입", lambda a: b12_ent(a).update(management_ko="비타민B12를 매일 보충하세요"))
    inject("검사 지시 삽입", lambda a: b12_ent(a).update(management_ko="정기적으로 혈액 검사를 받으세요"))
    inject("F4 마그네슘 단정 삽입(Al-only 위반)", lambda a: f4_ent(a).update(
        display_text_ko=f4_ent(a)["display_text_ko"] + " 마그네슘 함유 제산제도 동일"))
    inject("0275 dosing(2시간/콜라) display 삽입", lambda a: f4_ent(a).update(
        display_text_ko=f4_ent(a)["display_text_ko"] + " 2시간 간격으로 콜라와 함께"))
    inject("F4 mechanism 위조(depletion)", lambda a: f4_ent(a).update(mechanism="depletion"))
    inject("B12 에 약물 category 삽입", lambda a: b12_ent(a).update(counterpart_category="al_mg_antacid"))
    inject("needs_review(0275) 통합 삽입", lambda a: a["projected_entries"].append({
        "candidate_id": "RF-F10-0275", "reverify_verdict": "survives",
        "projected_live_relation": {**copy.deepcopy(f4_ent(a)), "id": 199, "ingredient": "케토코나졸",
                                    "nutrient": "알루미늄 함유 제산제(약물)", "counterpart_category": "al_mg_antacid",
                                    "display_text_ko": "x", "management_ko": "약사 또는 의사와 상담하세요"}}))
    inject_inv("0275 route 강등 위변조(needs_review→survives, 경구 품목 위장 불가능 — verdict 위조 검출)",
               lambda a: next(c for c in a["candidates"] if c["candidate_id"] == "RF-F10-0275").update(
                   reverify={**next(c for c in a["candidates"] if c["candidate_id"] == "RF-F10-0275")["reverify"], "verdict": "survives"}))
    fails.extend(inj_fail)

    print(f"=== F4/F6/F10 small-family dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 예상 "
          f"{art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} "
          f"(integrable 60→62 · conditional(0275) 60→63 · F1F2F3F9 후 91→93/94) ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — small-family integrable 2건 계약 안전(60→62 · F4 absorption/separation/al_mg_antacid·Mg 비단정 · "
          "F6 depletion/monitoring/B12·category 부재 · draft누출0 · 제품/보충/검사지시/dosing/항응고/골알람 0 · live·F1·F2·F3·F9 무충돌 · "
          "needs_review(0275 route) 통합 차단 · 라이브 무수정) · inventory reverify(survives0·copy2·needs1·per-candidate 기대·재실행 일치·"
          "F10 context) · index 자동 flip 0/latent 0 · sim v0.2 PASS(선행조건 0) · 결함주입 14종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
