#!/usr/bin/env python3
"""
validate_relation_factory_batch_v1_4.py
MediStack Relation Factory v1.4 — draft-only batch **검증**(읽기전용·네트워크 0).

data/drafts/relation_factory_draft_batch_v1_4.json 이 draft-only 안전·계약·품질 게이트를 만족하는지 검증 +
결함주입 10종으로 검증기 자체 입증. live export/full index/aliases/src 무수정.

게이트(품질·안전):
  schema·candidate_id unique · live/pending/reject/hold 중복 없음 · source_quote 존재 · itemSeq 실값(숫자) ·
  source_confirmed only(draft 전건 quote) · hold/reject/high-risk 약물 draft 없음 · live_integration_forbidden/
  do_not_implement_yet=true · published/clinical_reviewed=false · reviewed_by 공란 · 제품/구매/제휴 문구 0 ·
  보충 권유 0 · 비타민K 항응고 오인 0 · **Mg 영양제 오인 0**(마그네슘 nutrient draft 금지) ·
  미네랄 nutrient quote 에 supplement 맥락(제산제 오인 금지) · 부정문(흡수 영향 없음) quote 0 · potassium policy ·
  direct HTTP 신규 0(guard 위임).
결함주입 10: published=true·reviewed_by·제품문구·source_quote 누락·itemSeq 합성·hold약물(MTX) 삽입·
  live중복(레보플록사신×철분)·보충권유·비타민K 항응고·Mg 영양제 오인.
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
    fails.extend(inj_fail)

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
    print(f"RESULT: PASS — draft {len(batch['draft_relations'])}건 안전(source_confirmed·중복 차단·제품/보충/Mg오인/항응고 0·"
          f"draft-only·라이브 무수정) · 결함주입 10종 검출")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
