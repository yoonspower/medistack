#!/usr/bin/env python3
"""
integrate_pr5_potassium_depletion_live_v1_4.py
MediStack v1.4 — **PR-5 칼륨 depletion LIVE 통합** (dry-run 기본 / --apply 시 v0.2 export 기록).

대상 6건 = 스테로이드·이뇨제 × 칼륨 depletion. mechanism=depletion · recommended_action=monitoring ·
counterpart_category=null(영양소 직접). relation_count 95 → 101. 신규 id 97~102 (runtime max+1..).

🚨 이 PR = **production 최초 칼륨 safety 진입.** 🔑 칼륨 invariant 강제(위반 시 abort):
  6건 전부 potassium_safety_card=true · product_link_allowed=false. copy 보충 단정 0·수치 단정 0·능동 register 0.

PM-reviewed verified-reference integration (임상 검수 아님).
published=false / clinical_reviewed=false / reviewed_by 공란 / requires_clinical_review=false 유지.
copy 는 main(0342a6e) 의 fix된 safe_app_copy(영양소,'depletion') 로 신규 생성(lock 저장 copy 와 일치 assert).

게이트(--apply): --pm-note 가 check_pr5 PASS · --expected-base/--expected-final · dup 0(기존 live 칼륨 포함) ·
  ids disjoint · count==6 · 🔑칼륨 invariant · --fail-on-protected-change(비대상 보호셋 sha 불변).
사용:
  python3 scripts/integrate_pr5_potassium_depletion_live_v1_4.py --dry-run --expected-base 95 --expected-final 101 --fail-on-protected-change
  python3 scripts/integrate_pr5_potassium_depletion_live_v1_4.py --apply --pm-note data/review/pr5_potassium_depletion_pm_reviewed_note_v1_4.md --expected-base 95 --expected-final 101 --fail-on-protected-change
종료코드: 0 DONE/dry, 1 STOP(가드/노트/계약 위반).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
LOCK = os.path.join(DATA, "review", "pr5_potassium_depletion_candidate_lock_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "pr5_potassium_depletion_live_dryrun_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


integ = _load("integ", "integrate_theme_map_draft_batch_v1_3.py")   # run_v0_2 / _sim_with
guard = _load("guardmod", "guard_no_live_write_v1_3.py")            # protected_paths / sha_snapshot
chk = _load("pmchk", "check_pr5_potassium_depletion_pm_note_v1_4.py")  # check_pm_note
fh = _load("fh", "fix_harvester_display_template_v1_6.py")          # safe_app_copy / copy_lint / vfp

DIRECTIVE = ["복용하세요", "복용하지 마", "드세요", "드십시오", "끊으세요", "중단하세요", "보충하세요",
             "섭취하세요", "검사를 받으세요", "검사받으세요", "처방받으세요", "투여하세요"]
DISPLAY_ALARM = ["소아", "임신", "수유", "치아", "구루병", "골연화증", "골다공증", "골절", "신생아", "분리하도록 안내"]


def non_target_protected_paths():
    target = os.path.relpath(EXPORT, REPO)
    return [p for p in guard.protected_paths() if p != target]


def build_relations(exp0, lock):
    """6건 칼륨 depletion relation 생성. (relations, viol). copy=fix된 safe_app_copy(depletion)·lock 일치 assert."""
    viol = []
    base_max = max(r["id"] for r in exp0["relations"])
    rels = []
    for i, c in enumerate(lock["candidates"]):
        disp, mng = fh.safe_app_copy(c["counterpart"], "depletion")
        cid = c["candidate_id"]
        # copy 게이트
        cl = fh.copy_lint(disp, c.get("source_quote")) + fh.copy_lint(mng, c.get("source_quote"))
        if cl:
            viol.append(f"{cid}: copy_lint {cl}")
        if any(d in disp + " " + mng for d in DIRECTIVE):
            viol.append(f"{cid}: 보충/지시 단정")
        if any(a in disp for a in DISPLAY_ALARM):
            viol.append(f"{cid}: display 알람어/라벨귀속 단정")
        bad = fh.vfp.scan(f"{disp} {mng}")
        if bad:
            viol.append(f"{cid}: 카피 금칙어 {bad}")
        if disp != c.get("display_text_ko"):
            viol.append(f"{cid}: safe_app_copy display != lock(drift)")
        if mng != c.get("management_ko"):
            viol.append(f"{cid}: safe_app_copy management != lock(drift)")
        if c.get("evidence_level") != "moderate":
            viol.append(f"{cid}: evidence_level != moderate(임의 상향 금지)")
        new_id = base_max + 1 + i
        quote = c["source_quote"]
        pointer = (f"식약처 허가사항(nedrug getItemDetail) / {c['drug_ingredient']}({c.get('item_name','')}) / "
                   f"itemSeq {c['itemSeq']} / {c['source_section']} / '{quote}' / 확인일 {c['source_checked_at']}")
        is_k = c["counterpart"] == "칼륨"
        rel = {
            "id": new_id,
            "ingredient": c["drug_ingredient"],
            "nutrient": c["counterpart"],
            "mechanism": c["mechanism"],
            "recommended_action": c["recommended_action"],
            "evidence_level": c["evidence_level"],
            "display_text_ko": disp,
            "management_ko": mng,
            "product_link_allowed": False,
            "potassium_safety_card": bool(is_k),
            "requires_clinical_review": False,
            "source": {
                "type": "허가사항",
                "url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={c['itemSeq']}",
                "pointer": pointer,
            },
            "counterpart_category": c.get("counterpart_category"),
        }
        # 🔑 칼륨 invariant 강제(lock 도 칼륨 → 강제 true)
        if is_k and (rel["potassium_safety_card"] is not True or rel["product_link_allowed"] is not False):
            viol.append(f"{cid}: 🔑 칼륨 invariant 위반(kcard/plink)")
        if c.get("potassium_safety_card") is not True and is_k:
            viol.append(f"{cid}: lock 칼륨인데 potassium_safety_card!=true")
        rels.append(rel)
    return rels, viol


def integrity_checks(exp0, projected, lock, expected_base, expected_final):
    bad = []
    before = len(exp0["relations"])
    after = before + len(projected)
    if expected_base is not None and before != expected_base:
        bad.append(f"baseline {before} != --expected-base {expected_base}")
    if expected_final is not None and after != expected_final:
        bad.append(f"after {after} != --expected-final {expected_final}")
    if before != lock["baseline_relation_count"]:
        bad.append(f"baseline {before} != lock {lock['baseline_relation_count']}")
    if after != lock["expected_relation_count_after"]:
        bad.append(f"after {after} != lock {lock['expected_relation_count_after']}")
    if len(projected) != lock["total"] or len(projected) != lock["relation_delta"]:
        bad.append(f"projected {len(projected)} != lock total/delta {lock['total']}/{lock['relation_delta']}")
    live_ids = {r["id"] for r in exp0["relations"]}
    new_ids = [r["id"] for r in projected]
    if set(new_ids) & live_ids:
        bad.append(f"신규 id 충돌: {sorted(set(new_ids) & live_ids)}")
    if len(set(new_ids)) != len(new_ids):
        bad.append("신규 id 중복")
    if sorted(new_ids) != lock["expected_ids"]:
        bad.append(f"신규 id {sorted(new_ids)} != lock expected_ids {lock['expected_ids']}")
    # dedup: 기존 live (ingredient,nutrient) — 기존 live 칼륨 5약물 포함
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp0["relations"]}
    seen = set()
    for r in projected:
        k = (r.get("ingredient"), r.get("nutrient"))
        if k in live_pairs:
            bad.append(f"live 중복: {k}")
        if k in seen:
            bad.append(f"내부 중복: {k}")
        seen.add(k)
    # 스키마 + 🔑 칼륨 invariant 전수
    for r in projected:
        if r.get("product_link_allowed") is not False:
            bad.append(f"id{r['id']}: product_link_allowed != false")
        if r.get("requires_clinical_review") is not False:
            bad.append(f"id{r['id']}: requires_clinical_review != false")
        if r.get("nutrient") == "칼륨" and r.get("potassium_safety_card") is not True:
            bad.append(f"id{r['id']}: 🔑 칼륨인데 potassium_safety_card != true")
        if r.get("nutrient") != "칼륨" and r.get("potassium_safety_card") is not False:
            bad.append(f"id{r['id']}: 비칼륨인데 potassium_safety_card != false")
        if "reviewed_by" in r:
            bad.append(f"id{r['id']}: reviewed_by 누출")
        if not re.search(r"itemSeq=\d+", r.get("source", {}).get("url", "")):
            bad.append(f"id{r['id']}: source itemSeq 없음")
        if not r.get("source", {}).get("pointer"):
            bad.append(f"id{r['id']}: source pointer 없음")
        if r.get("mechanism") != "depletion":
            bad.append(f"id{r['id']}: mechanism != depletion")
        if r.get("recommended_action") != "monitoring":
            bad.append(f"id{r['id']}: recommended_action != monitoring")
        if r.get("counterpart_category") is not None:
            bad.append(f"id{r['id']}: counterpart_category != null")
    return bad


def main():
    ap = argparse.ArgumentParser(description="PR-5 칼륨 depletion live 통합")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--pm-note")
    ap.add_argument("--expected-base", type=int, default=None)
    ap.add_argument("--expected-final", type=int, default=None)
    ap.add_argument("--fail-on-protected-change", action="store_true")
    args = ap.parse_args()
    apply = args.apply
    mode = "APPLY(LIVE)" if apply else "DRY-RUN"

    lock = json.load(open(LOCK, encoding="utf-8"))
    exp0 = json.load(open(EXPORT, encoding="utf-8"))
    with open(EXPORT, "rb") as f:
        sha_before = hashlib.sha256(f.read()).hexdigest()
    ntp = non_target_protected_paths()
    snap_before = guard.sha_snapshot(ntp)

    projected, viol = build_relations(exp0, lock)
    viol += integrity_checks(exp0, projected, lock, args.expected_base, args.expected_final)
    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    for r in projected:
        if PRODUCT_FIELDS & set(r.keys()):
            viol.append(f"id{r['id']}: 제품 필드 누출")
        if "schedule" in r:
            viol.append(f"id{r['id']}: schedule 필드 누출")

    before = len(exp0["relations"])
    after = before + len(projected)
    print(f"=== PR-5 칼륨 depletion 통합 ({mode}) — {len(projected)}건 ===")
    print(f"baseline {before} → {after} · 신규 id {[r['id'] for r in projected]}")
    for r in projected:
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, ev={r['evidence_level']}, "
              f"🔑kcard={r['potassium_safety_card']}, plink={r['product_link_allowed']}, "
              f"clin={r['requires_clinical_review']})")

    if viol:
        print(f"\n[STOP] 계약/가드 위반 {len(viol)}건:")
        for b in viol:
            print("  -", b)
        return 1

    ok_sim, tail = integ.run_v0_2(integ._sim_with(exp0, projected))
    print(f"\n[validator] v0.2 sim PASS={ok_sim}")
    if not ok_sim:
        print(tail); print("[STOP] v0.2 validator sim 실패"); return 1

    if not apply:
        artifact = {
            "meta": {
                "name": "pr5_potassium_depletion_live_dryrun_v1_4", "status": "DRY-RUN — live 무수정 예상 산출물",
                "wave": "potassium_depletion", "mode": mode,
                "baseline_relation_count": before, "expected_relation_count_after": after,
                "delta": len(projected), "new_ids": [r["id"] for r in projected],
                "candidate_ids": lock["candidate_ids"], "v0_2_sim_passed": ok_sim,
                "export_sha_before": sha_before,
                "potassium_invariant": "6/6 kcard=true·plink=false",
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "integration_class": "PM-reviewed verified-reference integration (NOT clinical review)",
                "non_target_protected_snapshot_count": len(snap_before),
            },
            "projected_relations": projected,
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1); f.write("\n")
        with open(EXPORT, "rb") as f:
            sha_after = hashlib.sha256(f.read()).hexdigest()
        if sha_after != sha_before:
            print("[FATAL] 드라이런인데 export sha 변경됨 — 중단"); return 1
        if args.fail_on_protected_change:
            drift = [p for p in ntp if snap_before[p] != guard.sha_snapshot(ntp)[p]]
            if drift:
                print(f"[STOP] 비대상 보호셋 변경: {drift}"); return 1
        print(f"[dry-run] export sha 불변({sha_before[:8]}). 산출물: {os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print("[dry-run] live 기록은 --apply + --pm-note(checker PASS) 필요.")
        return 0

    # ── APPLY ──
    if not args.pm_note:
        print("[STOP] --apply 에는 --pm-note PATH 필수"); return 1
    ok_note, problems = chk.check_pm_note(args.pm_note, lock)
    if not ok_note:
        print(f"[STOP] PM note 거부 ({len(problems)}건):")
        for p in problems:
            print("  -", p)
        return 1
    print(f"[gate] PM note PASS: {os.path.relpath(args.pm_note, REPO)}")

    exp0["relations"] = exp0["relations"] + projected
    exp0["meta"]["relation_count"] = len(exp0["relations"])
    exp0["meta"]["published"] = False
    exp0["meta"]["clinical_reviewed"] = False
    exp0["meta"]["note"] = exp0["meta"].get("note", "") + (
        " | PR-5 칼륨 depletion PM-reviewed verified-reference 통합: 스테로이드·이뇨제 × 칼륨 6건. "
        "relation %d→%d. 6건 전부 potassium_safety_card=true·product_link_allowed=false(production 최초 칼륨 safety). "
        "published/clinical_reviewed=false·reviewed_by 미기재 유지(verified_reference 천장)." % (before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp0, f, ensure_ascii=False, indent=1); f.write("\n")

    chk_exp = json.load(open(EXPORT, encoding="utf-8"))
    if len(chk_exp["relations"]) != after or chk_exp["meta"]["relation_count"] != after:
        print(f"[FATAL] 기록 후 count 불일치"); return 1
    if chk_exp["meta"].get("published") is not False or chk_exp["meta"].get("clinical_reviewed") is not False:
        print("[FATAL] published/clinical_reviewed 플래그 위반"); return 1
    # 🔑 신규 칼륨 invariant 재확인
    kbad = [r["id"] for r in chk_exp["relations"] if r["id"] in lock["expected_ids"]
            and (r.get("potassium_safety_card") is not True or r.get("product_link_allowed") is not False)]
    if kbad:
        print(f"[FATAL] 🔑 기록 후 칼륨 invariant 위반: {kbad}"); return 1
    if args.fail_on_protected_change:
        drift = [p for p in ntp if snap_before[p] != guard.sha_snapshot(ntp)[p]]
        if drift:
            print(f"[FATAL] 비대상 보호셋 변경됨: {drift}"); return 1
    ok_final, tail2 = integ.run_v0_2(chk_exp)
    if not ok_final:
        print(tail2); print("[FATAL] 기록 후 v0.2 validator 실패"); return 1
    print(f"\n[write] export 기록 완료(relations {before}→{after}). v0.2 validator PASS. "
          f"🔑 신규 6건 칼륨 invariant OK. 비대상 보호셋 불변. INTEGRATE PR-5 칼륨 depletion: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
