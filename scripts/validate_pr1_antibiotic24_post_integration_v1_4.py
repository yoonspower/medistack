#!/usr/bin/env python3
"""
validate_pr1_antibiotic24_post_integration_v1_4.py
PR-1 antibiotic24 **통합 후** v0.2 export 검증 (읽기전용·live 무수정).

검증:
  - relation_count == 84 (meta + len)
  - baseline(base commit) 60건이 한 건도 변경/삭제 없이 보존
  - 신규 24건 = lock candidate 와 정확히 일치(ingredient×counterpart), id = 62..85
  - PR-1 범위 외 신규 relation 0
  - needs_review 4 / F3·F9·F4·F6 family counterpart 없음
  - published=false · clinical_reviewed=false · reviewed_by 부재(전건)
  - product_link_allowed/requires_clinical_review/potassium_safety_card == false (신규 전건)
  - source.url itemSeq + pointer 존재(신규 전건) · 제품 필드/schedule 필드 누출 0
  - display/management 금칙어(vfp.scan) 0 · 복용 지시 명령형 0
  - DATA_URL == v0.2 (src/js/data.js)
사용: python3 scripts/validate_pr1_antibiotic24_post_integration_v1_4.py [--base 9267740]
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
LOCK = os.path.join(REPO, "data", "review", "pr1_antibiotic24_candidate_lock_v1_4.json")
DRYRUN = os.path.join(REPO, "data", "review", "pr1_antibiotic24_live_dryrun_v1_4.json")
DATA_JS = os.path.join(REPO, "src", "js", "data.js")

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
    ap.add_argument("--base", default="9267740", help="baseline commit (통합 전 60건)")
    args = ap.parse_args()

    exp = json.load(open(EXPORT, encoding="utf-8"))
    lock = json.load(open(LOCK, encoding="utf-8"))
    rels = exp["relations"]
    after = lock["expected_relation_count_after"]
    base_count = lock["baseline_relation_count"]
    new_ids = set(lock["expected_ids"])

    print("=== PR-1 antibiotic24 post-integration validator ===")
    ok("relation_count == %d (len)" % after, len(rels) == after, f"len={len(rels)}")
    ok("meta.relation_count == %d" % after, exp["meta"].get("relation_count") == after,
       str(exp["meta"].get("relation_count")))

    # baseline 60 보존
    base = git_show(args.base, "data/medistack_v0.2_beta_export.json")
    if base is None:
        ok("baseline(base commit) 로드", False, f"git show {args.base} 실패")
    else:
        base_rels = {r["id"]: r for r in base["relations"]}
        ok("baseline relation_count == %d" % base_count, len(base["relations"]) == base_count)
        live_by_id = {r["id"]: r for r in rels}
        unchanged = all(json.dumps(live_by_id.get(i), ensure_ascii=False, sort_keys=True) ==
                        json.dumps(base_rels[i], ensure_ascii=False, sort_keys=True) for i in base_rels)
        ok("baseline 60건 변경/삭제 0 (verbatim 보존)", unchanged)
        ok("신규 id = live − baseline (정확히 24)",
           set(live_by_id) - set(base_rels) == new_ids,
           str(sorted(set(live_by_id) - set(base_rels))))

    # 신규 24 = lock 후보와 일치
    expected_pairs = {}
    for c in lock["candidates"]:
        expected_pairs[(c["drug_ingredient"], c["counterpart"])] = c
    new_rels = [r for r in rels if r["id"] in new_ids]
    ok("신규 relation 수 == 24", len(new_rels) == 24, str(len(new_rels)))
    got_pairs = {(r["ingredient"], r["nutrient"]) for r in new_rels}
    ok("신규 24쌍 == lock 후보쌍", got_pairs == set(expected_pairs.keys()),
       str(got_pairs ^ set(expected_pairs.keys())))

    # PR-1 범위 외 신규 0 (이미 new_ids==24 로 보장되나 명시)
    ok("PR-1 범위 외 신규 relation 0", len(new_ids) == 24)

    # needs_review / 제외 family counterpart 없음 (id 기반은 export 에 없으므로 ingredient/counterpart 휴리스틱)
    forbidden_pairs = [("에티드론산", "칼슘"), ("에티드론산", "철분"),
                       ("카르바마제핀", "엽산"), ("케토코나졸", "제산제")]
    leak = [p for p in forbidden_pairs if any(r["ingredient"] == p[0] and p[1] in r["nutrient"] for r in new_rels)]
    ok("needs_review 쌍(에티드론산/카르바마제핀×엽산/케토코나졸) 신규 0", not leak, str(leak))

    # 보호 플래그
    ok("published == false", exp["meta"].get("published") is False)
    ok("clinical_reviewed == false", exp["meta"].get("clinical_reviewed") is False)
    ok("meta.reviewed_by 부재", "reviewed_by" not in exp["meta"])
    bad_flag = [r["id"] for r in new_rels if r.get("product_link_allowed") is not False
                or r.get("requires_clinical_review") is not False
                or r.get("potassium_safety_card") is not False or "reviewed_by" in r]
    ok("신규 전건 product/clinical/potassium=false · reviewed_by 부재", not bad_flag, str(bad_flag))

    # source 무결성
    nosrc = [r["id"] for r in new_rels if not re.search(r"itemSeq=\d+", r.get("source", {}).get("url", ""))
             or not r.get("source", {}).get("pointer")]
    ok("신규 전건 source url itemSeq + pointer", not nosrc, str(nosrc))

    # 제품/schedule 필드 누출
    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    leakf = [r["id"] for r in new_rels if (PRODUCT_FIELDS & set(r.keys())) or "schedule" in r]
    ok("신규 전건 제품/schedule 필드 누출 0", not leakf, str(leakf))

    # 금칙어 / 복용 지시
    vfp = load_vfp().vfp
    DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "반드시 복용"]
    bad_copy = []
    for r in new_rels:
        txt = f"{r.get('display_text_ko','')} {r.get('management_ko','')}"
        fb = vfp.scan(txt)
        if fb:
            bad_copy.append((r["id"], "forbidden", fb))
        if any(d in txt for d in DIRECTIVE):
            bad_copy.append((r["id"], "directive"))
    ok("신규 전건 display/management 금칙어·복용지시 0", not bad_copy, str(bad_copy[:3]))

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
    print("RESULT: PASS — PR-1 antibiotic24 통합 후 60→84 · 범위 정확 · 보호상태 유지 · source/금칙 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
