#!/usr/bin/env python3
"""
validate_pr5_potassium_depletion_post_integration_v1_4.py
PR-5 칼륨 depletion **통합 후** v0.2 export 검증 (읽기전용·live 무수정).

검증:
  - relation_count == 101 (meta + len)
  - baseline(base commit 0342a6e) 95건 한 건도 변경/삭제 없이 보존
  - 신규 6건 = lock candidates, ids = 97~102
  - PR-5 범위 외 신규 0
  - published/clinical_reviewed=false · reviewed_by 부재(전건)
  - 🔑 신규 6건 전부 potassium_safety_card=true · product_link_allowed=false · requires_clinical_review=false
  - 신규 depletion/monitoring · counterpart_category=null
  - source itemSeq + pointer · 제품/schedule 누출 0
  - display/management 금칙어·지시·보충 단정·수치 단정 0 · 알람어 0
  - 기존 live 칼륨 ids 17/19/30/53/55 invariant(kcard=true·plink=false) 보존(회귀 0)
  - DATA_URL == v0.2
사용: python3 scripts/validate_pr5_potassium_depletion_post_integration_v1_4.py [--base 0342a6e]
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
LOCK = os.path.join(REPO, "data", "review", "pr5_potassium_depletion_candidate_lock_v1_4.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")
DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "보충하세요",
             "섭취하세요", "검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요"]
ALARM = ["소아", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아", "분리하도록 안내", "수치 변화", "수치가 걱정"]
EXISTING_K_IDS = [17, 19, 30, 53, 55]
_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def git_show(ref, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="0342a6e")
    args = ap.parse_args()
    tpl = load("tpl", "fix_harvester_display_template_v1_6.py")
    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    after = lock["expected_relation_count_after"]
    base_count = lock["baseline_relation_count"]
    new_ids = set(lock["expected_ids"])

    print("=== PR-5 칼륨 depletion post-integration validator ===")
    ok("relation_count == %d (len)" % after, len(rels) == after, f"len={len(rels)}")
    ok("meta.relation_count == %d" % after, exp["meta"].get("relation_count") == after,
       str(exp["meta"].get("relation_count")))

    base = git_show(args.base, "data/medistack_v0.2_beta_export.json")
    if base is None:
        ok("baseline(base commit) 로드", False, f"git show {args.base} 실패")
    else:
        base_rels = {r["id"]: r for r in base["relations"]}
        ok("baseline relation_count == %d" % base_count, len(base["relations"]) == base_count)
        live_by_id = {r["id"]: r for r in rels}
        unchanged = all(json.dumps(live_by_id.get(i), ensure_ascii=False, sort_keys=True) ==
                        json.dumps(base_rels[i], ensure_ascii=False, sort_keys=True) for i in base_rels)
        ok("baseline 95건 변경/삭제 0 (verbatim)", unchanged)
        ok("신규 id = live − baseline (정확히 6)", set(live_by_id) - set(base_rels) == new_ids,
           str(sorted(set(live_by_id) - set(base_rels))))
        # 기존 live 칼륨 invariant 보존
        kreg = [i for i in EXISTING_K_IDS if not (base_rels.get(i, {}).get("potassium_safety_card") is True
                and live_by_id.get(i, {}).get("potassium_safety_card") is True
                and live_by_id.get(i, {}).get("product_link_allowed") is False)]
        ok("기존 live 칼륨 17/19/30/53/55 invariant 보존(회귀 0)", not kreg, str(kreg))

    expected_pairs = {(c["drug_ingredient"], c["counterpart"]) for c in lock["candidates"]}
    new_rels = [r for r in rels if r["id"] in new_ids]
    ok("신규 relation 수 == 6", len(new_rels) == 6, str(len(new_rels)))
    got_pairs = {(r["ingredient"], r["nutrient"]) for r in new_rels}
    ok("신규 6쌍 == lock 후보쌍", got_pairs == expected_pairs, str(got_pairs ^ expected_pairs))
    ok("PR-5 범위 외 신규 0", len(new_ids) == 6)

    ok("published == false", exp["meta"].get("published") is False)
    ok("clinical_reviewed == false", exp["meta"].get("clinical_reviewed") is False)
    ok("meta.reviewed_by 부재", "reviewed_by" not in exp["meta"])

    # 🔑 칼륨 invariant 신규 전수 (kcard=true·plink=false)
    kbad = [r["id"] for r in new_rels if r.get("potassium_safety_card") is not True
            or r.get("product_link_allowed") is not False or r.get("requires_clinical_review") is not False
            or "reviewed_by" in r]
    ok("🔑 신규 6건 kcard=true·plink=false·clinical=false·reviewed_by 부재", not kbad, str(kbad))

    bad_enum = [r["id"] for r in new_rels if r.get("mechanism") != "depletion"
                or r.get("recommended_action") != "monitoring" or r.get("counterpart_category") is not None
                or r.get("nutrient") != "칼륨" or r.get("evidence_level") != "moderate"]
    ok("신규 depletion/monitoring·counterpart_category=null·칼륨·moderate", not bad_enum, str(bad_enum))

    nosrc = [r["id"] for r in new_rels if not re.search(r"itemSeq=\d+", r.get("source", {}).get("url", ""))
             or not r.get("source", {}).get("pointer")]
    ok("신규 source url itemSeq + pointer", not nosrc, str(nosrc))

    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    leakf = [r["id"] for r in new_rels if (PRODUCT_FIELDS & set(r.keys())) or "schedule" in r]
    ok("신규 제품/schedule 필드 누출 0", not leakf, str(leakf))

    bad_copy, bad_alarm = [], []
    for r in new_rels:
        disp, mng = r.get("display_text_ko", ""), r.get("management_ko", "")
        sq = r.get("source", {}).get("pointer", "")
        if tpl.copy_lint(disp, sq) or tpl.copy_lint(mng, sq) or any(d in disp + " " + mng for d in DIRECTIVE):
            bad_copy.append(r["id"])
        if any(a in disp for a in ALARM):
            bad_alarm.append(r["id"])
    ok("신규 display/management 금칙어·지시·보충/수치 단정 0", not bad_copy, str(bad_copy))
    ok("신규 display 알람어/라벨귀속/수치 비노출", not bad_alarm, str(bad_alarm))

    if os.path.exists(DATA_JS):
        js = open(DATA_JS, encoding="utf-8").read()
        m = re.search(r"DATA_URL\s*=\s*'([^']*)'", js)
        ok("DATA_URL == v0.2", bool(m) and "v0.2_beta_export" in m.group(1), m.group(1) if m else "미발견")
    else:
        ok("src/js/data.js 존재", False)

    print("=" * 60)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}"); return 1
    print("RESULT: PASS — PR-5 95→101 · 🔑칼륨 invariant 신규6+기존5 · baseline 보존 · copy/소스 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
