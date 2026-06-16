#!/usr/bin/env python3
"""
validate_penicillamine_subset_dryrun_v1_3.py
MediStack — 페니실라민 FE/ZN 2건 subset **live 통합 드라이런 검증**(읽기전용). export/full index/aliases/src 무수정.
integrate_penicillamine_subset_v1_3.py(dry-run)가 만든 data/review/penicillamine_subset_live_dryrun_v1_3.json 이
통합 시 안전·계약을 만족하는지 검증 + 결함주입 9종으로 검증기 자체 입증.

검사:
  0) 안전 불변: 라이브 export 무변경(relations==60·meta 60·published/clinical=false·페니실라민 미존재).
  1) artifact 메타: live_write_performed=false·live_promotion=0·published/clinical=false·reviewed_by 공란·
     export_sha_after_same=true·expected 60→62·included FE/ZN 2·excluded theme map 4·itemSeq 198300142·
     zn_mechanism_decision_required·**live_integration_prerequisites 빈(선행조건 0)**.
  2) 예상 2건 계약: id 62~63(라이브 disjoint·무중복)·필수 live 필드·**counterpart_category 키 부재(null)**·draft-전용 누출 0·
     product_link/potassium/clinical=false·reviewed_by 부재·source itemSeq 198300142·라벨 quote pointer·
     FE confidence high / ZN inference flag·confidence moderate·기존 live 60·칼륨·AT-FEX 무중복·금칙어/제품/보충권유 0.
  3) v0.2 validator 증거: subset 2건 시뮬 export **PASS**(재실행 확인) → 선행조건 0.
  4) 결함주입 9종(published=true·reviewed_by 작성·제품 카피·FE 또는 ZN 누락·다른 theme map 포함·live_write=true·
     잘못된 count·itemSeq 변조·ZN mechanism decision 누락) → 전건 검출.
사용: python3 scripts/validate_penicillamine_subset_dryrun_v1_3.py
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
ARTIFACT = os.path.join(DATA, "review", "penicillamine_subset_live_dryrun_v1_3.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")
LIVE_RELATIONS = 60
SUBSET_IDS = ["TM-CHEL-01-FE", "TM-CHEL-01-ZN"]
ITEMSEQ = "198300142"


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
    before, after = meta.get("expected_relation_count_before"), meta.get("expected_relation_count_after")
    if before != live_count:
        bad.append(f"expected_before({before}) != live({live_count})")
    if after != (before or 0) + 2:
        bad.append(f"expected_after({after}) != before+2")
    if sorted(meta.get("included_candidate_ids", [])) != sorted(SUBSET_IDS):
        bad.append("included_candidate_ids != FE/ZN 2건")
    if sorted(meta.get("excluded_theme_map_candidate_ids", [])) != sorted(
            ["TM-LIP-01", "TM-LIP-02", "TM-CEPH-AC-01", "TM-CEPH-AC-02"]):
        bad.append("excluded_theme_map_candidate_ids != 나머지 4건")
    if meta.get("itemSeq") != ITEMSEQ:
        bad.append(f"itemSeq != {ITEMSEQ}")
    if meta.get("zn_mechanism_decision_required") is not True:
        bad.append("zn_mechanism_decision_required != true")
    if "zn_mechanism_decision" not in meta:
        bad.append("zn_mechanism_decision 미기록")
    if meta.get("live_integration_prerequisites") != []:
        bad.append(f"subset 선행조건은 0이어야: {meta.get('live_integration_prerequisites')}")

    if len(entries) != 2:
        bad.append(f"projected_entries != 2 ({len(entries)})")
    ids = [e.get("projected_id") for e in entries]
    if set(ids) & live_ids:
        bad.append("projected id 가 live 와 충돌")
    if len(set(ids)) != len(ids):
        bad.append("projected id 중복")
    seen = set()
    by_cid = {}
    for e in entries:
        cid = e.get("candidate_id", "?")
        by_cid[cid] = e
        if cid not in SUBSET_IDS:
            bad.append(f"{cid}: subset(FE/ZN) 밖 후보 포함")
        rel = e.get("projected_live_relation", {})
        for k in ("id", "ingredient", "nutrient", "mechanism", "recommended_action",
                  "evidence_level", "display_text_ko", "source"):
            if rel.get(k) in (None, ""):
                bad.append(f"{cid}: live 필드 '{k}' 누락")
        if "counterpart_category" in rel:
            bad.append(f"{cid}: counterpart_category 키 존재(일반 영양소=null→키 부재여야)")
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
        if ITEMSEQ not in src.get("url", ""):
            bad.append(f"{cid}: source url itemSeq {ITEMSEQ} 없음")
        if "itemSeq" not in src.get("pointer", "") or "'" not in src.get("pointer", ""):
            bad.append(f"{cid}: source pointer 라벨 quote 없음")
        if rel.get("ingredient") != "페니실라민":
            bad.append(f"{cid}: ingredient != 페니실라민")
        if rel.get("mechanism") != "absorption":
            bad.append(f"{cid}: mechanism != absorption")
        if rel.get("recommended_action") != "separation":
            bad.append(f"{cid}: recommended_action != separation")
        pair = (rel.get("ingredient"), rel.get("nutrient"))
        if pair in live_pairs:
            bad.append(f"{cid}: 기존 live 60 과 중복 {pair}")
        if pair in seen:
            bad.append(f"{cid}: 배치 내 중복 {pair}")
        seen.add(pair)
        if rel.get("ingredient") == "펙소페나딘" or rel.get("nutrient") == "칼륨" \
                or rel.get("potassium_safety_card") is True:
            bad.append(f"{cid}: AT-FEX/칼륨 트랙 충돌")
        copy_txt = f'{rel.get("display_text_ko", "")} {rel.get("management_ko", "")}'
        for b in vfp.scan(copy_txt):
            bad.append(f"{cid}: 금칙어 {b}")
        for p in PRODUCT_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 제품 문구 {p}")
        for p in SUPPLEMENT_RECO_PHRASES:
            if p in copy_txt:
                bad.append(f"{cid}: 보충 권유 {p}")
    # FE/ZN 개별 속성
    fe = by_cid.get("TM-CHEL-01-FE")
    zn = by_cid.get("TM-CHEL-01-ZN")
    if not fe or fe.get("confidence") != "high":
        bad.append("TM-CHEL-01-FE confidence != high")
    if not fe or fe.get("projected_live_relation", {}).get("nutrient") != "철분":
        bad.append("TM-CHEL-01-FE nutrient != 철분")
    if not zn or zn.get("confidence") != "moderate":
        bad.append("TM-CHEL-01-ZN confidence != moderate")
    if not zn or zn.get("projected_live_relation", {}).get("nutrient") != "아연":
        bad.append("TM-CHEL-01-ZN nutrient != 아연")
    # ZN inference flag 반영(risk_flags 또는 mechanism decision)
    zn_inf = (zn and (any("INFERRED" in str(f) for f in zn.get("risk_flags", []))
              or meta.get("zn_mechanism_decision", {}).get("inference_flag") is True))
    if not zn_inf:
        bad.append("TM-CHEL-01-ZN absorption 추론 flag 미반영")
    return bad


def run_v0_2(sim):
    tmp = tempfile.mkdtemp(prefix="ms_pen_val_")
    p = os.path.join(tmp, "sim.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, V0_2_VALIDATOR, p], capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr)[-300:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] artifact 없음: {ARTIFACT}\n  먼저 `python3 scripts/integrate_penicillamine_subset_v1_3.py`")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))

    ck(len(exp["relations"]) == LIVE_RELATIONS, f"라이브 relations != {LIVE_RELATIONS}")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, "라이브 meta != 60")
    ck(exp["meta"].get("published") is False, "라이브 published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "라이브 clinical_reviewed != false")
    ck(not any(r.get("ingredient") == "페니실라민" for r in exp["relations"]),
       "페니실라민 이미 라이브 — 드라이런 전제 위반")

    art_bad = validate_artifact(art, exp)
    ck(not art_bad, f"artifact 계약 위반: {art_bad}")

    sim = copy.deepcopy(exp)
    sim["relations"] += [e["projected_live_relation"] for e in art["projected_entries"]]
    sim["meta"]["relation_count"] = len(sim["relations"])
    ok2, _ = run_v0_2(sim)
    ck(ok2, "subset 2건 sim export v0.2 validator FAIL(선행조건 0 입증 실패)")
    ck(art["meta"].get("v0_2_validator_evidence", {}).get("sim_subset_2_passed") is True,
       "artifact sim_subset_2_passed != true")
    exp2 = json.load(open(EXPORT, encoding="utf-8"))
    ck(len(exp2["relations"]) == LIVE_RELATIONS, "검증 중 라이브 relations 변경됨")

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
    inject("제품 카피 삽입", lambda a: a["projected_entries"][0]["projected_live_relation"].update(
        display_text_ko=a["projected_entries"][0]["projected_live_relation"]["display_text_ko"] + " 지금 구매하세요"))
    inject("FE 누락(entries 1건)", lambda a: a["projected_entries"].pop(0))
    inject("다른 theme map 후보 포함(TM-LIP-01)",
           lambda a: a["meta"].update(included_candidate_ids=["TM-CHEL-01-FE", "TM-LIP-01"]))
    inject("live_write_performed=true", lambda a: a["meta"].update(live_write_performed=True))
    inject("잘못된 expected count(after=70)", lambda a: a["meta"].update(expected_relation_count_after=70))
    inject("itemSeq 변조", lambda a: [e["projected_live_relation"]["source"].update(
        url=e["projected_live_relation"]["source"]["url"].replace(ITEMSEQ, "999999999"))
        for e in a["projected_entries"]])
    inject("ZN mechanism decision 누락",
           lambda a: (a["meta"].pop("zn_mechanism_decision", None),
                      [e.update(risk_flags=[]) for e in a["projected_entries"]
                       if e.get("candidate_id") == "TM-CHEL-01-ZN"]))
    fails.extend(inj_fail)

    print(f"=== 페니실라민 subset dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 예상 {art['meta'].get('expected_relation_count_before')}→{art['meta'].get('expected_relation_count_after')} ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건")
        return 1
    print("RESULT: PASS — FE/ZN 2건 계약 안전(60→62·counterpart_category=null·draft누출0·제품/보충 0·라이브 무수정) · "
          "sim v0.2 PASS(선행조건 0) · 결함주입 9종 검출")
    return 0


if __name__ == "__main__":
    sys.exit(main())
