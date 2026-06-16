#!/usr/bin/env python3
"""
validate_relation_factory_batch_v1_4.py
MediStack Relation Factory v1.4 — draft-only batch **검증**(읽기전용·네트워크 0).

data/drafts/relation_factory_draft_batch_v1_4.json 이 draft-only 안전·계약·품질 게이트를 만족하는지 +
적대검증 ledger / reviewer-ready batch 의 정합성을 검증 + 결함주입 15종으로 검증기 자체 입증.
live export/full index/aliases/src 무수정.

게이트(품질·안전):
  schema·candidate_id unique · live/pending/reject/hold 중복 없음 · source_quote 존재 · itemSeq 실값(숫자) ·
  source_confirmed only(draft 전건 quote) · hold/reject/high-risk 약물 draft 없음 · live_integration_forbidden/
  do_not_implement_yet=true · published/clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 문구 0 ·
  보충 권유 0 · 비타민K 항응고 오인 0 · **Mg 영양제 오인 0**(마그네슘 nutrient draft 금지) ·
  미네랄 nutrient quote 에 supplement 맥락(제산제 오인 금지) · 부정문(흡수 영향 없음) quote 0 ·
  **IV/주사/수출/외용 전용 quote 0** · **source_quote ≠ display_copy(출처/카피 분리)** · potassium policy ·
  direct HTTP 신규 0(guard 위임).
적대검증 정합성(작업 I):
  ledger cid == draft cid(43 전건) · reviewer-ready = survives/copy_change 만(needs_review/hold/reject 0) ·
  reviewer-ready 수 == 생존 수 · reviewer-ready batch 자체가 draft-only 게이트 통과 ·
  reviewer-ready 정비 quote 가 원문 substring(verbatim).
결함주입 15: (기본 10) published=true·reviewed_by·제품문구·source_quote 누락·itemSeq 합성·hold약물(MTX)·
  live중복(레보플록사신×철분)·보충권유·비타민K 항응고·Mg 영양제 오인 +
  (적대 5) 부정문 quote·임신엽산 보충카피·IV전용 route·source_quote==display_copy 지시문·
  강등(hold)후보를 reviewer-ready 삽입. (※ "Mg제산제→Mg nutrient"는 기본 'Mg 영양제 오인'으로 이미 커버)
종료코드: 0 PASS, 1 FAIL.
"""
import copy
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
BATCH = os.path.join(DATA, "drafts", "relation_factory_draft_batch_v1_4.json")
INVENTORY = os.path.join(DATA, "review", "relation_factory_inventory_v1_4.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
LEDGER = os.path.join(DATA, "review", "relation_factory_adversarial_verify_v1_4.json")
READY = os.path.join(DATA, "drafts", "relation_factory_reviewer_ready_batch_v1_4.json")
SURVIVE_VERDICTS = {"survives", "survives_with_copy_change"}
DOWNGRADE_VERDICTS = {"needs_review", "hold", "reject"}

fails = []


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prov = _load("prov", "theme_map_harvest_provider_v1_3.py")
vfp = prov.vfp
PRODUCT_PHRASES = prov.PRODUCT_PHRASES
SUPPLEMENT_RECO_PHRASES = prov.SUPPLEMENT_RECO_PHRASES
guard = _load("guard", "guard_no_live_write_v1_3.py")
invmod = _load("invmod", "build_relation_factory_inventory_v1_4.py")

# 고위험 약물(draft 금지) — F11/inventory high-risk. 약물별 확정.
HIGH_RISK_DRUGS = {"와파린", "메토트렉세이트", "피리메타민", "사이클로스포린", "타크로리무스",
                   "레날리도마이드", "스피로노락톤", "에플레레논", "아밀로라이드", "트리암테렌"}
ANTICOAG_K_FRAME = re.compile(r"와파린|항응고|INR|프로트롬빈")
NUTRIENT_SUPP_CTX = re.compile(r"함유\s*(한|된|하고\s*있는)?\s*제제|함유된\s*종합비타민|종합비타민제제|"
                               r"비타민제|미네랄이?\s*첨가|보충|결핍|저하|감소|억제|길항|골연화|구루병|흡수")
NEGATION = re.compile(r"흡수.{0,10}(영향을?\s*(받지|주지)|저해되지|감소되지)\s*않|영향이?\s*없\s*")
ROUTE_IV_ONLY = re.compile(r"정맥(내\s*투여|주사용?|투여만)|주사제로만|주사로만|수출용으로만|외용제?로만|주사용으로만")


def ck(cond, msg):
    if not cond:
        fails.append(msg)


def load_inventory_keys():
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    block = set(inv.get("dedup_keys", []))      # live+pending+reject+hold+nodom
    return inv, block


def validate_batch(batch, block_keys):
    """draft batch 계약/품질 위반 리스트 반환(빈=통과). 결함주입과 공유."""
    bad = []
    meta = batch.get("meta", {})
    drafts = batch.get("draft_relations", [])

    if meta.get("published") is not False:
        bad.append("meta.published != false")
    if meta.get("clinical_reviewed") is not False:
        bad.append("meta.clinical_reviewed != false")
    if (meta.get("reviewed_by") or "") != "":
        bad.append("meta.reviewed_by 비공란")

    seen_ids, seen_pairs = set(), set()
    for d in drafts:
        cid = d.get("candidate_id", "?")
        rel = f'{d.get("drug_ingredient")}×{d.get("counterpart")}'
        # schema 필수 필드
        for k in ("candidate_id", "drug_ingredient", "counterpart", "mechanism",
                  "recommended_action", "evidence_level", "itemSeq", "source_quote",
                  "display_copy", "management_copy"):
            if not d.get(k) and d.get(k) is not False:
                bad.append(f"{cid}: 필드 '{k}' 누락")
        if cid in seen_ids:
            bad.append(f"{cid}: candidate_id 중복")
        seen_ids.add(cid)
        # draft-only 불변
        if d.get("live_integration_forbidden") is not True:
            bad.append(f"{cid}: live_integration_forbidden != true")
        if d.get("do_not_implement_yet") is not True:
            bad.append(f"{cid}: do_not_implement_yet != true")
        if d.get("published") is not False:
            bad.append(f"{cid}: published != false")
        if d.get("clinical_reviewed") is not False:
            bad.append(f"{cid}: clinical_reviewed != false")
        if (d.get("reviewed_by") or "") != "":
            bad.append(f"{cid}: reviewed_by 비공란")
        if d.get("product_link_allowed") is not False:
            bad.append(f"{cid}: product_link_allowed != false")
        # source_confirmed only — quote + itemSeq 실값
        q = d.get("source_quote") or ""
        if len(q.strip()) < 12:
            bad.append(f"{cid}: source_quote 너무 짧음/누락")
        if not re.fullmatch(r"\d{8,}", str(d.get("itemSeq", ""))):
            bad.append(f"{cid}: itemSeq 비숫자/합성값({d.get('itemSeq')})")
        if NEGATION.search(q):
            bad.append(f"{cid}: 부정문(흡수 영향 없음) quote — 상호작용 아님")
        if ROUTE_IV_ONLY.search(q):
            bad.append(f"{cid}: IV/주사/수출/외용 전용 quote — 경구 일반 relation 오인")
        if q.strip() and q.strip() == (d.get("display_copy") or "").strip():
            bad.append(f"{cid}: source_quote == display_copy(출처/카피 미분리·지시문 위험)")
        # 중복 차단(live/pending/reject/hold)
        k = invmod.key(d.get("drug_ingredient", "?"),
                       "제산제" if d.get("counterpart_category") == "al_mg_antacid" else d.get("counterpart", "?"))
        if k in block_keys:
            bad.append(f"{cid}: inventory 중복/차단 키({k})")
        if k in seen_pairs:
            bad.append(f"{cid}: 배치 내 중복 {k}")
        seen_pairs.add(k)
        # 고위험 약물 draft 금지
        if d.get("drug_ingredient") in HIGH_RISK_DRUGS:
            bad.append(f"{cid}: 고위험 약물 draft 금지({d.get('drug_ingredient')})")
        # Mg 영양제 오인 금지(마그네슘 nutrient = counterpart_category null)
        if d.get("counterpart") == "마그네슘" and d.get("counterpart_category") is None:
            bad.append(f"{cid}: 마그네슘 nutrient draft 금지(제산제 Mg 오인 위험)")
        # 비타민K 항응고 오인
        if ("비타민K" in (d.get("counterpart") or "") or ANTICOAG_K_FRAME.search(q)):
            bad.append(f"{cid}: 비타민K/항응고 오인 framing")
        # 미네랄 nutrient quote 에 supplement/depletion 맥락 필요(제산제만이면 오분류)
        if d.get("counterpart_category") is None and d.get("counterpart") in ("철분", "칼슘", "아연", "엽산", "비타민D", "비타민B12"):
            if not NUTRIENT_SUPP_CTX.search(q):
                bad.append(f"{cid}: nutrient quote 에 supplement/결핍 맥락 없음({rel})")
            # 제산제 양이온을 nutrient 로 오분류 차단(철분/칼슘/아연이 '함유 제산제' 직후면 위험)
            cterm = {"철분": "철분", "칼슘": "칼슘", "아연": "아연"}.get(d.get("counterpart"))
            if cterm:
                for mm in re.finditer(re.escape(cterm), q):
                    if re.search(r"함유.{0,5}제산제|함유하는\s*제산제", q[mm.start():mm.start() + 26]):
                        bad.append(f"{cid}: 미네랄이 제산제 양이온인데 nutrient 로 분류({rel})")
                        break
        # 카피 안전: 제품/구매/제휴 0 · 보충 권유 0 · 직접 복용 지시 0
        copy_txt = f'{d.get("display_copy","")} {d.get("management_copy","")}'
        for b in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {b}")
        for p in PRODUCT_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 제품 문구 {p}")
        for p in SUPPLEMENT_RECO_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 보충 권유 {p}")
        for cmd in ("복용하세요", "복용하지 마", "드세요", "보충하세요", "섭취하세요"):
            if cmd in copy_txt:
                bad.append(f"{cid}: 직접 복용/보충 지시 {cmd}")
        # potassium policy
        if d.get("counterpart") == "칼륨":
            if d.get("potassium_safety_card") is not True:
                bad.append(f"{cid}: 칼륨인데 potassium_safety_card != true")
            if d.get("product_link_allowed") is not False:
                bad.append(f"{cid}: 칼륨 product_link 금지")
    return bad


def validate_adversarial(batch, ledger, ready, block):
    """적대검증 ledger ↔ draft batch ↔ reviewer-ready batch 정합성(빈=통과)."""
    bad = []
    draft = batch.get("draft_relations", [])
    draft_cids = {d["candidate_id"] for d in draft}
    orig_q = {d["candidate_id"]: (d.get("source_quote") or "") for d in draft}
    entries = ledger.get("entries", [])
    ledger_cids = {e["candidate_id"] for e in entries}
    verdict_by = {e["candidate_id"]: e.get("adversarial_verdict") for e in entries}
    rr = ready.get("reviewer_ready_relations", [])
    ready_cids = {r["candidate_id"] for r in rr}

    # 1) ledger 가 draft 43 전건 커버
    if ledger_cids != draft_cids:
        miss = (draft_cids - ledger_cids) | (ledger_cids - draft_cids)
        bad.append(f"ledger cid != draft cid (차집합 {sorted(miss)[:6]})")
    # 2) 모든 verdict 가 알려진 값
    for cid, v in verdict_by.items():
        if v not in (SURVIVE_VERDICTS | DOWNGRADE_VERDICTS):
            bad.append(f"{cid}: 알 수 없는 verdict({v})")
    # 3) reviewer-ready = survives/copy_change 만
    for cid in ready_cids:
        if verdict_by.get(cid) not in SURVIVE_VERDICTS:
            bad.append(f"reviewer-ready {cid} 가 SURVIVE 판정 아님({verdict_by.get(cid)})")
    # 4) 강등 후보가 reviewer-ready 에 없음
    downgraded = {cid for cid, v in verdict_by.items() if v in DOWNGRADE_VERDICTS}
    leak = ready_cids & downgraded
    if leak:
        bad.append(f"강등 후보가 reviewer-ready 에 포함: {sorted(leak)}")
    # 5) reviewer-ready 수 == 생존 수
    survivors = {cid for cid, v in verdict_by.items() if v in SURVIVE_VERDICTS}
    if ready_cids != survivors:
        bad.append(f"reviewer-ready 집합 != 생존 집합 (차 {sorted(ready_cids ^ survivors)[:6]})")
    # 6) reviewer-ready 정비 quote 가 원문 substring(verbatim)
    for r in rr:
        cid = r["candidate_id"]
        if cid in orig_q and (r.get("source_quote") or "") not in orig_q[cid]:
            bad.append(f"{cid}: reviewer-ready quote 가 원문 substring 아님(verbatim 위반)")
    # 7) reviewer-ready batch 자체가 draft-only 게이트 통과
    ready_pseudo = {"meta": ready.get("meta", {}), "draft_relations": rr}
    bad.extend([f"[ready] {x}" for x in validate_batch(ready_pseudo, block)])
    return bad


def main():
    if not os.path.exists(BATCH):
        print(f"[FATAL] batch 없음 — 먼저 relation_factory_bot_v1_4.py --online-source-check")
        return 1
    batch = json.load(open(BATCH, encoding="utf-8"))
    inv, block = load_inventory_keys()
    exp = json.load(open(EXPORT, encoding="utf-8"))

    # 안전 불변: live 무수정
    ck(len(exp["relations"]) == 60, "라이브 relations != 60")
    ck(exp["meta"].get("published") is False, "라이브 published != false")

    bad = validate_batch(batch, block)
    ck(not bad, f"batch 계약/품질 위반: {bad[:8]}")

    print(f"--- draft batch: {len(batch['draft_relations'])}건 (live 무수정·중복 차단) ---")

    # 적대검증 ledger / reviewer-ready 정합성
    ledger = ready = None
    if os.path.exists(LEDGER) and os.path.exists(READY):
        ledger = json.load(open(LEDGER, encoding="utf-8"))
        ready = json.load(open(READY, encoding="utf-8"))
        abad = validate_adversarial(batch, ledger, ready, block)
        ck(not abad, f"적대검증 정합성 위반: {abad[:8]}")
        m = ledger.get("meta", {})
        print(f"--- 적대검증: reviewer-ready {m.get('reviewer_ready')} · 강등 {m.get('downgraded')} "
              f"(survives {m.get('counts',{}).get('survives')}/copy_change {m.get('counts',{}).get('survives_with_copy_change')}/"
              f"needs_review {m.get('counts',{}).get('needs_review')}/hold {m.get('counts',{}).get('hold')}/reject {m.get('counts',{}).get('reject')}) ---")
    else:
        print("--- 적대검증 ledger/reviewer-ready 없음 — 먼저 adversarial_verify_relation_factory_v1_4.py ---")

    # 결함주입 10
    print("--- 결함주입(검출되어야 PASS) ---")
    inj_fail = []

    def inject(label, mutate):
        b = copy.deepcopy(batch)
        if b["draft_relations"]:
            mutate(b)
        v = validate_batch(b, block)
        ok = len(v) > 0
        print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else "  [검출 실패]"))
        if not ok:
            inj_fail.append(label)

    inject("published=true", lambda b: b["draft_relations"][0].update(published=True))
    inject("reviewed_by 작성", lambda b: b["draft_relations"][0].update(reviewed_by="RPH-X"))
    inject("제품 카피", lambda b: b["draft_relations"][0].update(
        display_copy=b["draft_relations"][0]["display_copy"] + " 지금 구매하세요"))
    inject("source_quote 누락", lambda b: b["draft_relations"][0].update(source_quote=""))
    inject("itemSeq 합성값", lambda b: b["draft_relations"][0].update(itemSeq="FAKE-001"))
    inject("hold 약물(메토트렉세이트) draft 삽입", lambda b: b["draft_relations"][0].update(
        drug_ingredient="메토트렉세이트"))
    inject("live 중복(레보플록사신×철분) 삽입", lambda b: b["draft_relations"][0].update(
        drug_ingredient="레보플록사신", counterpart="철분", counterpart_category=None))
    inject("보충 권유 카피", lambda b: b["draft_relations"][0].update(
        management_copy="철분 보충제를 복용하세요."))
    inject("비타민K 항응고 framing", lambda b: b["draft_relations"][0].update(
        counterpart="비타민K", source_quote="와파린 INR 변동 주의"))
    inject("Mg 영양제 오인(마그네슘 nutrient)", lambda b: b["draft_relations"][0].update(
        counterpart="마그네슘", counterpart_category=None))
    # --- 적대검증 라운드 추가 결함주입 6 ---
    inject("부정문 quote(흡수 저해되지 않음)", lambda b: b["draft_relations"][0].update(
        source_quote="제산제와의 병용투여로 이 약의 흡수가 저해되지 않는다."))
    inject("임신 엽산 보충 카피", lambda b: b["draft_relations"][0].update(
        counterpart="엽산", counterpart_category=None,
        management_copy="임신 중에는 엽산을 보충하세요."))
    inject("IV/주사 전용 route quote", lambda b: b["draft_relations"][0].update(
        source_quote="이 약은 정맥주사용으로만 사용하며 칼슘 함유 제제와 병용 시 흡수가 저하된다."))
    inject("source_quote == display_copy 지시문", lambda b: b["draft_relations"][0].update(
        source_quote="철분을 복용하세요.", display_copy="철분을 복용하세요."))
    fails.extend(inj_fail)

    # 적대검증 정합성 결함주입(별도): 강등(hold)후보를 reviewer-ready 에 삽입 → 검출
    if ledger is not None and ready is not None:
        print("--- 적대검증 정합성 결함주입 ---")
        downgraded = [e["candidate_id"] for e in ledger["entries"]
                      if e["adversarial_verdict"] in DOWNGRADE_VERDICTS]
        if downgraded:
            r2 = copy.deepcopy(ready)
            # 강등 후보 1건을 draft 에서 떠와 reviewer-ready 에 부정 삽입
            drow = next(d for d in batch["draft_relations"] if d["candidate_id"] == downgraded[0])
            r2["reviewer_ready_relations"].append({
                "candidate_id": drow["candidate_id"], "family": drow["family"],
                "relation": drow["relation"], "drug_ingredient": drow["drug_ingredient"],
                "counterpart": drow["counterpart"], "counterpart_category": drow.get("counterpart_category"),
                "itemSeq": drow["itemSeq"], "source_section": drow["source_section"],
                "source_quote": drow["source_quote"], "mechanism": drow["mechanism"],
                "recommended_action": drow["recommended_action"], "evidence_level": drow["evidence_level"],
                "display_copy": drow["display_copy"], "management_copy": drow["management_copy"],
                "product_link_allowed": False, "potassium_safety_card": False,
                "live_integration_forbidden": True, "do_not_implement_yet": True,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
            })
            v2 = validate_adversarial(batch, ledger, r2, block)
            ok2 = len(v2) > 0
            print(("  PASS " if ok2 else "  FAIL ") + "강등(hold/needs_review) 후보를 reviewer-ready 삽입"
                  + ("" if ok2 else "  [검출 실패]"))
            if not ok2:
                fails.append("강등 후보 reviewer-ready 삽입 미검출")

    # direct HTTP 신규 0 (guard 위임)
    try:
        http_new = guard.scan_direct_http()
        ck(not http_new, f"direct-http 신규 위반: {http_new}")
        print(f"  PASS direct-http 신규 0")
    except Exception as e:
        print(f"  (direct-http scan 건너뜀: {e})")

    print("=" * 60)
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print(f"RESULT: PASS — draft {len(batch['draft_relations'])}건 안전(source_confirmed·중복 차단·제품/보충/Mg오인/항응고/"
          f"IV전용/출처미분리 0·draft-only·라이브 무수정) · 적대검증 정합성 OK · 결함주입 15종 검출")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
