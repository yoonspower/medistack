#!/usr/bin/env python3
"""
validate_pr2_chronic8_post_integration_v1_4.py
PR-2 chronic8 **통합 후** v0.2 export 검증 (읽기전용·live 무수정).

검증:
  - relation_count == 92 (meta + len)
  - baseline(base commit 1a354d0) 84건이 한 건도 변경/삭제 없이 보존 (PR-1 ids 62-85 포함)
  - 신규 8건 = lock candidate 와 정확히 일치(ingredient×counterpart), id = 86..93
  - PR-2 범위 외 신규 relation 0
  - needs_review(카르바마제핀×엽산 등) 신규 0 · F3/F4 신규 0
  - published=false · clinical_reviewed=false · reviewed_by 부재(전건)
  - product_link_allowed/requires_clinical_review/potassium_safety_card == false (신규 전건)
  - 신규 전건 depletion/monitoring · nutrient(엽산/비타민D/비타민B12) · counterpart_category 부재
  - source.url itemSeq + pointer 존재(신규 전건) · 제품 필드/schedule 필드 누출 0
  - display/management 금칙어(vfp.scan) 0 · 복용/검사/처방 지시 0 · display 골질환 alarm 0
  - DATA_URL == v0.2 (src/js/data.js)
사용: python3 scripts/validate_pr2_chronic8_post_integration_v1_4.py [--base 1a354d0]
종료코드 0 PASS / 1 FAIL.
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
LOCK = os.path.join(REPO, "data", "review", "pr2_chronic8_candidate_lock_v1_4.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

BONE_ALARM = ["구루병", "골연화증", "골다공증", "골절", "치아형성", "치조골"]
DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "반드시 복용",
             "검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요"]

_fail = []


def ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def git_show(ref, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def load_vfp():
    spec = importlib.util.spec_from_file_location(
        "prov", os.path.join(HERE, "theme_map_harvest_provider_v1_3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="1a354d0", help="baseline commit (통합 전 84건·PR-1 머지)")
    args = ap.parse_args()

    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    after = lock["expected_relation_count_after"]
    base_count = lock["baseline_relation_count"]
    new_ids = set(lock["expected_ids"])

    print("=== PR-2 chronic8 post-integration validator ===")
    ok("relation_count == %d (len)" % after, len(rels) == after, f"len={len(rels)}")
    ok("meta.relation_count == %d" % after, exp["meta"].get("relation_count") == after,
       str(exp["meta"].get("relation_count")))

    # baseline 84 보존(PR-1 ids 62-85 포함)
    base = git_show(args.base, "data/medistack_v0.2_beta_export.json")
    if base is None:
        ok("baseline(base commit) 로드", False, f"git show {args.base} 실패")
    else:
        base_rels = {r["id"]: r for r in base["relations"]}
        ok("baseline relation_count == %d" % base_count, len(base["relations"]) == base_count)
        live_by_id = {r["id"]: r for r in rels}
        unchanged = all(json.dumps(live_by_id.get(i), ensure_ascii=False, sort_keys=True) ==
                        json.dumps(base_rels[i], ensure_ascii=False, sort_keys=True) for i in base_rels)
        ok("baseline 84건 변경/삭제 0 (verbatim 보존·PR-1 62-85 포함)", unchanged)
        ok("신규 id = live − baseline (정확히 8)",
           set(live_by_id) - set(base_rels) == new_ids,
           str(sorted(set(live_by_id) - set(base_rels))))
        pr1_ids = [i for i in range(62, 86)]
        ok("PR-1 ids 62-85 전건 보존", all(i in live_by_id for i in pr1_ids))

    # 신규 8 = lock 후보와 일치
    expected_pairs = {(c["drug_ingredient"], c["counterpart"]): c for c in lock["candidates"]}
    new_rels = [r for r in rels if r["id"] in new_ids]
    ok("신규 relation 수 == 8", len(new_rels) == 8, str(len(new_rels)))
    got_pairs = {(r["ingredient"], r["nutrient"]) for r in new_rels}
    ok("신규 8쌍 == lock 후보쌍", got_pairs == set(expected_pairs.keys()),
       str(got_pairs ^ set(expected_pairs.keys())))
    ok("PR-2 범위 외 신규 relation 0", len(new_ids) == 8)

    # needs_review / 제외 family 신규 0
    forbidden_pairs = [("카르바마제핀", "엽산"), ("케토코나졸", "제산제"),
                       ("에티드론산", "칼슘"), ("에티드론산", "철분"), ("레보티록신", "제산제")]
    leak = [p for p in forbidden_pairs if any(r["ingredient"] == p[0] and p[1] in r["nutrient"] for r in new_rels)]
    ok("needs_review/F3/F4 쌍(카르바마제핀×엽산·케토코나졸·에티드론산·레보티록신) 신규 0", not leak, str(leak))

    # 보호 플래그
    ok("published == false", exp["meta"].get("published") is False)
    ok("clinical_reviewed == false", exp["meta"].get("clinical_reviewed") is False)
    ok("meta.reviewed_by 부재", "reviewed_by" not in exp["meta"])
    bad_flag = [r["id"] for r in new_rels if r.get("product_link_allowed") is not False
                or r.get("requires_clinical_review") is not False
                or r.get("potassium_safety_card") is not False or "reviewed_by" in r]
    ok("신규 전건 product/clinical/potassium=false · reviewed_by 부재", not bad_flag, str(bad_flag))

    # depletion/monitoring · nutrient · category 부재
    bad_enum = [r["id"] for r in new_rels if r.get("mechanism") != "depletion"
                or r.get("recommended_action") != "monitoring"]
    ok("신규 전건 depletion/monitoring", not bad_enum, str(bad_enum))
    bad_nut = [r["id"] for r in new_rels if r.get("nutrient") not in ("엽산", "비타민D", "비타민B12")
               or "counterpart_category" in r]
    ok("신규 전건 nutrient(엽산/비타민D/B12)·counterpart_category 부재", not bad_nut, str(bad_nut))

    # source 무결성
    nosrc = [r["id"] for r in new_rels if not re.search(r"itemSeq=\d+", r.get("source", {}).get("url", ""))
             or not r.get("source", {}).get("pointer")]
    ok("신규 전건 source url itemSeq + pointer", not nosrc, str(nosrc))

    # 제품/schedule 필드 누출
    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    leakf = [r["id"] for r in new_rels if (PRODUCT_FIELDS & set(r.keys())) or "schedule" in r]
    ok("신규 전건 제품/schedule 필드 누출 0", not leakf, str(leakf))

    # 금칙어 / 복용·검사 지시 / display 골질환 alarm
    vfp = load_vfp().vfp
    bad_copy, bad_alarm = [], []
    for r in new_rels:
        disp = r.get("display_text_ko", "")
        txt = f"{disp} {r.get('management_ko','')}"
        if vfp.scan(txt):
            bad_copy.append((r["id"], "forbidden", vfp.scan(txt)))
        if any(d in txt for d in DIRECTIVE):
            bad_copy.append((r["id"], "directive"))
        a = [w for w in BONE_ALARM if w in disp]
        if a:
            bad_alarm.append((r["id"], a))
    ok("신규 전건 display/management 금칙어·복용/검사/처방 지시 0", not bad_copy, str(bad_copy[:3]))
    ok("신규 전건 display 골질환 alarm(구루병/골연화증 등) 비노출", not bad_alarm, str(bad_alarm[:3]))

    # DATA_URL v0.2
    if os.path.exists(DATA_JS):
        js = open(DATA_JS, encoding="utf-8").read()
        m = re.search(r"DATA_URL\s*=\s*'([^']*)'", js)
        ok("DATA_URL == v0.2", bool(m) and "v0.2_beta_export" in m.group(1),
           m.group(1) if m else "DATA_URL 미발견")
    else:
        ok("src/js/data.js 존재", False)

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print("RESULT: PASS — PR-2 chronic8 통합 후 84→92 · 범위 정확 · 보호상태 유지 · source/금칙/alarm OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
