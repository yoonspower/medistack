#!/usr/bin/env python3
"""
integrate_pr4_h7f3001_live_v1_4.py
MediStack v1.4 — **PR-4 H7-F3-001 LIVE 통합** 스크립트 (dry-run 기본 / --apply 시 실제 v0.2 export 기록).

대상 1건 = F3 리세드론산 × Al/Mg 함유 제산제(약물). absorption/separation · counterpart_category=al_mg_antacid.
relation_count 94 → 95. 신규 id = runtime max+1 (96).

PM-reviewed verified-reference integration (임상 검수 아님).
published=false / clinical_reviewed=false / reviewed_by 공란 / product_link_allowed=false /
requires_clinical_review=false / potassium_safety_card=false 유지.

🚨 copy 오염 차단: display/management 는 **현재 main(7f07df4)의 fix된 fix_harvester_display_template_v1_6.safe_app_copy**
로 신규 생성한다(오염 산출 브랜치 autofactory-auto-* 의 '효과가 감소' copy 미사용). 생성 결과가 lock 저장 copy 와
일치하는지 assert(단일 진실원). 최종 display 에 '효과가 감소' 0 · '분리하도록 안내' 0 · copy_lint=[] · vfp scan clean.

게이트(--apply): --pm-note 가 check_pr4_h7f3001_pm_note PASS · --expected-base/--expected-final · dup 0 ·
  ids disjoint · count==1 · --fail-on-protected-change(비대상 보호셋 sha 불변).

사용:
  python3 scripts/integrate_pr4_h7f3001_live_v1_4.py --dry-run --expected-base 94 --expected-final 95 --fail-on-protected-change
  python3 scripts/integrate_pr4_h7f3001_live_v1_4.py --apply --pm-note data/review/pr4_h7f3001_pm_reviewed_note_v1_4.md --expected-base 94 --expected-final 95 --fail-on-protected-change
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
LOCK = os.path.join(DATA, "review", "pr4_h7f3001_candidate_lock_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "pr4_h7f3001_live_dryrun_v1_4.json")
COPY_CHANGE_ARTIFACT = os.path.join(DATA, "review", "pr4_h7f3001_display_copy_change_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


integ = _load("integ", "integrate_theme_map_draft_batch_v1_3.py")   # run_v0_2 / _sim_with
guard = _load("guardmod", "guard_no_live_write_v1_3.py")            # protected_paths / sha_snapshot
chk = _load("pmchk", "check_pr4_h7f3001_pm_note_v1_4.py")           # check_pm_note
fh = _load("fh", "fix_harvester_display_template_v1_6.py")          # safe_app_copy / copy_lint / vfp


def non_target_protected_paths():
    target = os.path.relpath(EXPORT, REPO)
    return [p for p in guard.protected_paths() if p != target]


def load_lock():
    return json.load(open(LOCK, encoding="utf-8"))


def build_relation(exp0, lock):
    """단건 H7-F3-001 relation 을 lock 필드 + fix된 safe_app_copy 로 직접 build. (rel, copy_change, viol)."""
    viol = []
    c = lock["candidates"][0]
    # copy: 오염 미사용 — fix된 생성기로 신규 생성
    disp, mng = fh.safe_app_copy(c["counterpart"], c["recommended_action"])
    # copy 게이트
    if "효과가 감소" in disp or "효과가 감소" in mng:
        viol.append("copy: '효과가 감소' 재출현")
    if "분리하도록 안내" in disp or "분리하도록 안내" in mng:
        viol.append("copy: 라벨귀속 '분리하도록 안내' 단정")
    if fh.copy_lint(disp) or fh.copy_lint(mng):
        viol.append(f"copy_lint 위반: disp={fh.copy_lint(disp)} mng={fh.copy_lint(mng)}")
    bad = fh.vfp.scan(f"{disp} {mng}")
    if bad:
        viol.append(f"카피 금칙어 {bad}")
    # lock 저장 copy 와 일치(단일 진실원 — drift STOP)
    if disp != c.get("display_text_ko"):
        viol.append("safe_app_copy display != lock 저장 copy(drift)")
    if mng != c.get("management_ko"):
        viol.append("safe_app_copy management != lock 저장 copy(drift)")

    new_id = max(r["id"] for r in exp0["relations"]) + 1
    quote = c["source_quote"]
    pointer = (f"식약처 nedrug getItemDetail / {c['drug_ingredient']} / itemSeq {c['itemSeq']} / "
               f"{c['source_section']} / '{quote}' / 확인일 {c['source_checked_at']}")
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
        "potassium_safety_card": False,
        "requires_clinical_review": False,
        "source": {
            "type": "허가사항",
            "url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={c['itemSeq']}",
            "pointer": pointer,
        },
        "counterpart_category": c["counterpart_category"],
    }
    copy_change = {"candidate_id": c["candidate_id"], "id": new_id, "ingredient": rel["ingredient"],
                   "kind": "generated_clean", "field": "display_text_ko/management_ko",
                   "display_text_ko": disp, "management_ko": mng,
                   "reason": "main fix된 safe_app_copy 로 신규 생성(오염 산출 미사용). 라벨 흡수-방해만 명시 → '효과가 감소' 비노출."}
    return rel, copy_change, viol


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
    if len(projected) != lock["total"]:
        bad.append(f"projected {len(projected)} != lock total {lock['total']}")
    if len(projected) != lock["relation_delta"]:
        bad.append(f"delta {len(projected)} != lock {lock['relation_delta']}")
    live_ids = {r["id"] for r in exp0["relations"]}
    new_ids = [r["id"] for r in projected]
    if set(new_ids) & live_ids:
        bad.append(f"신규 id 가 live id 와 충돌: {sorted(set(new_ids) & live_ids)}")
    if len(set(new_ids)) != len(new_ids):
        bad.append("신규 id 중복")
    if sorted(new_ids) != lock["expected_ids"]:
        bad.append(f"신규 id {sorted(new_ids)} != lock expected_ids {lock['expected_ids']}")
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp0["relations"]}
    seen = set()
    for r in projected:
        k = (r.get("ingredient"), r.get("nutrient"))
        if k in live_pairs:
            bad.append(f"live 중복: {k}")
        if k in seen:
            bad.append(f"내부 중복: {k}")
        seen.add(k)
    for r in projected:
        if r.get("product_link_allowed") is not False:
            bad.append(f"id{r['id']}: product_link_allowed != false")
        if r.get("requires_clinical_review") is not False:
            bad.append(f"id{r['id']}: requires_clinical_review != false")
        if r.get("potassium_safety_card") is not False:
            bad.append(f"id{r['id']}: potassium_safety_card != false")
        if "reviewed_by" in r:
            bad.append(f"id{r['id']}: reviewed_by 누출")
        if not re.search(r"itemSeq=\d+", r.get("source", {}).get("url", "")):
            bad.append(f"id{r['id']}: source itemSeq 없음")
        if not r.get("source", {}).get("pointer"):
            bad.append(f"id{r['id']}: source pointer 없음")
        if r.get("mechanism") != "absorption":
            bad.append(f"id{r['id']}: mechanism != absorption")
        if r.get("recommended_action") != "separation":
            bad.append(f"id{r['id']}: recommended_action != separation")
        if r.get("counterpart_category") != "al_mg_antacid":
            bad.append(f"id{r['id']}: counterpart_category != al_mg_antacid")
    return bad


def main():
    ap = argparse.ArgumentParser(description="PR-4 H7-F3-001 live 통합")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--pm-note")
    ap.add_argument("--expected-base", type=int, default=None)
    ap.add_argument("--expected-final", type=int, default=None)
    ap.add_argument("--fail-on-protected-change", action="store_true")
    ap.add_argument("--no-product-ui", action="store_true")
    ap.add_argument("--no-schedule", action="store_true")
    args = ap.parse_args()
    apply = args.apply
    mode = "APPLY(LIVE)" if apply else "DRY-RUN"

    lock = load_lock()
    exp0 = json.load(open(EXPORT, encoding="utf-8"))
    with open(EXPORT, "rb") as f:
        sha_before = hashlib.sha256(f.read()).hexdigest()

    ntp = non_target_protected_paths()
    snap_before = guard.sha_snapshot(ntp)

    rel, copy_change, viol = build_relation(exp0, lock)
    projected = [rel]
    viol += integrity_checks(exp0, projected, lock, args.expected_base, args.expected_final)

    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    for r in projected:
        leaked = PRODUCT_FIELDS & set(r.keys())
        if leaked:
            viol.append(f"id{r['id']}: 제품 필드 누출 {sorted(leaked)}")
        if "schedule" in r:
            viol.append(f"id{r['id']}: schedule 필드 누출")

    before = len(exp0["relations"])
    after = before + len(projected)
    print(f"=== PR-4 H7-F3-001 통합 ({mode}) — {len(projected)}건 ===")
    print(f"baseline {before} → {after} · 신규 id {[r['id'] for r in projected]}")
    for r in projected:
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, ev={r['evidence_level']}, "
              f"cat={r.get('counterpart_category')}, plink={r['product_link_allowed']}, "
              f"clin={r['requires_clinical_review']})")
        print(f"      display: {r['display_text_ko']}")

    if viol:
        print(f"\n[STOP] 계약/가드 위반 {len(viol)}건:")
        for b in viol:
            print("  -", b)
        return 1

    ok_sim, tail = integ.run_v0_2(integ._sim_with(exp0, projected))
    print(f"\n[validator] v0.2 sim PASS={ok_sim}")
    if not ok_sim:
        print(tail)
        print("[STOP] v0.2 validator sim 실패")
        return 1

    os.makedirs(os.path.dirname(COPY_CHANGE_ARTIFACT), exist_ok=True)
    with open(COPY_CHANGE_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "pr4_h7f3001_display_copy_change_v1_4", "wave": "h7f3001", "mode": mode,
                            "principle": "main fix된 safe_app_copy 로 신규 생성(오염 미사용). 리세드론산 라벨 흡수-방해만 → '효과가 감소' 비노출 · '분리하도록 안내' 비노출.",
                            "count_field_changes": 1},
                   "changes": [copy_change]}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    if not apply:
        artifact = {
            "meta": {
                "name": "pr4_h7f3001_live_dryrun_v1_4", "status": "DRY-RUN — live 무수정 예상 산출물",
                "wave": "h7f3001", "mode": mode,
                "baseline_relation_count": before, "expected_relation_count_after": after,
                "delta": len(projected), "new_ids": [r["id"] for r in projected],
                "candidate_ids": lock["candidate_ids"], "v0_2_sim_passed": ok_sim,
                "export_sha_before": sha_before,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "integration_class": "PM-reviewed verified-reference integration (NOT clinical review)",
                "copy_change_field_count": 1,
                "non_target_protected_snapshot": snap_before,
            },
            "projected_relations": projected,
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")
        with open(EXPORT, "rb") as f:
            sha_after = hashlib.sha256(f.read()).hexdigest()
        if sha_after != sha_before:
            print("[FATAL] 드라이런인데 export sha 변경됨 — 중단")
            return 1
        if args.fail_on_protected_change:
            drift = [p for p in ntp if snap_before[p] != guard.sha_snapshot(ntp)[p]]
            if drift:
                print(f"[STOP] 비대상 보호셋 변경: {drift}")
                return 1
        print(f"[dry-run] export sha 불변({sha_before[:8]}). 산출물: "
              f"{os.path.relpath(DRYRUN_ARTIFACT, REPO)} · {os.path.relpath(COPY_CHANGE_ARTIFACT, REPO)}")
        print("[dry-run] live 기록은 --apply + --pm-note(checker PASS) 필요.")
        return 0

    # ── APPLY ──
    if not args.pm_note:
        print("[STOP] --apply 에는 --pm-note PATH 필수")
        return 1
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
        " | PR-4 H7-F3-001 PM-reviewed verified-reference 통합: F3 리세드론산 × Al/Mg 함유 제산제 1건. "
        "relation %d→%d. published/clinical_reviewed=false·reviewed_by 미기재 유지(verified_reference 천장)." % (before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp0, f, ensure_ascii=False, indent=1)
        f.write("\n")

    chk_exp = json.load(open(EXPORT, encoding="utf-8"))
    if len(chk_exp["relations"]) != after or chk_exp["meta"]["relation_count"] != after:
        print(f"[FATAL] 기록 후 count 불일치: {len(chk_exp['relations'])}/{chk_exp['meta']['relation_count']} != {after}")
        return 1
    if chk_exp["meta"].get("published") is not False or chk_exp["meta"].get("clinical_reviewed") is not False:
        print("[FATAL] published/clinical_reviewed 플래그 위반")
        return 1
    if args.fail_on_protected_change:
        snap_after = guard.sha_snapshot(ntp)
        drift = [p for p in ntp if snap_before[p] != snap_after[p]]
        if drift:
            print(f"[FATAL] 비대상 보호셋 변경됨: {drift}")
            return 1
    ok_final, tail2 = integ.run_v0_2(chk_exp)
    if not ok_final:
        print(tail2)
        print("[FATAL] 기록 후 v0.2 validator 실패")
        return 1
    print(f"\n[write] export 기록 완료(relations {before}→{after}). v0.2 validator PASS. "
          f"비대상 보호셋 불변. INTEGRATE PR-4 H7-F3-001: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
