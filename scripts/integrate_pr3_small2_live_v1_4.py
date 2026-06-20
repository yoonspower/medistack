#!/usr/bin/env python3
"""
integrate_pr3_small2_live_v1_4.py
MediStack v1.4 — **PR-3 small2 LIVE 통합** 스크립트 (dry-run 기본 / --apply 시 실제 v0.2 export 기록).

대상 2건 = F3 이반드론산 × Al/Mg 함유 제산제 1 + F4 레보티록신 × 알루미늄 함유 제산제 1.
둘 다 absorption/separation · counterpart_category=al_mg_antacid (drug counterpart).
relation_count 92 → 94. 신규 id = runtime max+1 (94..95).

PM-reviewed verified-reference integration (임상 검수 아님).
published=false / clinical_reviewed=false / reviewed_by 공란 / product_link_allowed=false /
requires_clinical_review=false / potassium_safety_card=false 전건 유지.

빌드 로직 재사용:
  - F3 1: integrate_f3_bisphosphonate_batch_v1_4.build_subset (survives=RF-F3-0147)
  - F4 1: integrate_f4_f6_f10_small_family_batch_v1_4.build_subset (family:F4=RF-F4-0173)
  - id 순차 부여(runtime max+1): F3 → F4.

PR-3 copy 원칙(copy_change·source fidelity):
  - 이반드론산(F3): 인용이 흡수저하 FACT-only(타이밍 미명시) → display 의 라벨귀속 '복용 시점을 분리하도록 안내하고
    있으니' 단정 제거 → '복용 시점에 대해 약사 또는 의사와 상담' FACT reframe(PR-1 live al_mg_antacid 선례 동형).
  - 레보티록신(F4): F4 prep 단계에서 Al-only(Mg 미명시) display_reframe 적용됨 + 인용에 '투여간격 주의' 근거 →
    PR-3 추가 reframe 없음(유지).

게이트(--apply): --pm-note 가 check_pr3_small2_pm_note PASS · --expected-base/--expected-final · dup 0 ·
  ids disjoint · count==2 · --fail-on-protected-change(비대상 보호셋 sha 불변).

사용:
  python3 scripts/integrate_pr3_small2_live_v1_4.py --dry-run --pm-note <note> --expected-base 92 --expected-final 94 --fail-on-protected-change
  python3 scripts/integrate_pr3_small2_live_v1_4.py --apply  --pm-note <note> --expected-base 92 --expected-final 94 --fail-on-protected-change
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
LOCK = os.path.join(DATA, "review", "pr3_small2_candidate_lock_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "pr3_small2_live_dryrun_v1_4.json")
COPY_CHANGE_ARTIFACT = os.path.join(DATA, "review", "pr3_small2_display_copy_change_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F3 = _load("f3mod", "integrate_f3_bisphosphonate_batch_v1_4.py")
F4 = _load("f4mod", "integrate_f4_f6_f10_small_family_batch_v1_4.py")
chk = _load("pmchk", "check_pr3_small2_pm_note_v1_4.py")
guard = _load("guardmod", "guard_no_live_write_v1_3.py")
integ = F3.integ

# ── 이반드론산 FACT reframe (PR-1 live al_mg_antacid 선례 동형) ──
# 인용("…경구투여 약물은 이 약의 흡수를 저해할 수 있다.")은 흡수저하 FACT-only(타이밍/분리/회피 미명시).
# display 의 '복용 시점을 분리하도록 안내하고 있으니'는 라벨귀속 separation-guidance 단정 → 원문 초과.
# → 1번째 문장(흡수저하 사실)은 보존, 2번째 문장만 _TAIL_FACT(복용 시점 상담 유도)로 reframe. separation 은 management(hedged).
_DISP_MARKER = "허가사항 문구가 있습니다."
_TAIL_FACT = " 함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요."
F3_FACT_REFRAME = {"RF-F3-0147"}


def reframe_fact(old):
    assert _DISP_MARKER in old, f"display 템플릿 불일치(reframe 불가): {old[:40]}"
    head = old.split(_DISP_MARKER)[0] + _DISP_MARKER
    new = head + _TAIL_FACT
    assert "분리하도록 안내" not in new, "reframe 후에도 separation-guidance 단정 잔존"
    return new


def non_target_protected_paths():
    target = os.path.relpath(EXPORT, REPO)
    return [p for p in guard.protected_paths() if p != target]


def load_lock():
    return json.load(open(LOCK, encoding="utf-8"))


def build_projected(exp0, lock):
    """F3 1 + F4 1 → (entries, projected, violations, copy_changes). live 무수정(메모리 시뮬만)."""
    f3_ids = [c["candidate_id"] for c in lock["candidates"] if c["family"] == "F3"]
    f4_ids = [c["candidate_id"] for c in lock["candidates"] if c["family"] == "F4"]
    viol, entries, copy_changes = [], [], []

    # F3 1
    e3, v3 = F3.build_subset(exp0, f3_ids)
    viol += [f"F3: {x}" for x in v3]
    if len(e3) != len(f3_ids):
        viol.append(f"F3 entries {len(e3)} != 기대 {len(f3_ids)}")
    proj3 = [e["projected_live_relation"] for e in e3]
    entries += [dict(e, _family="F3") for e in e3]

    # F4 1 (exp + F3 통합분 기준 id 이어서)
    exp1 = integ._sim_with(exp0, proj3)
    e4, v4 = F4.build_subset(exp1, f4_ids)
    viol += [f"F4: {x}" for x in v4]
    if len(e4) != len(f4_ids):
        viol.append(f"F4 entries {len(e4)} != 기대 {len(f4_ids)}")
    proj4 = [e["projected_live_relation"] for e in e4]
    entries += [dict(e, _family="F4") for e in e4]

    # ── PR-3 copy_change: F3 이반드론산 FACT reframe (F4 는 prep Al-only reframe 유지) ──
    for e in entries:
        rel = e["projected_live_relation"]
        cid = e["candidate_id"]
        if cid in F3_FACT_REFRAME:
            old = rel["display_text_ko"]
            new = reframe_fact(old)
            if new != old:
                rel["display_text_ko"] = new
                e["_copy_change"] = {"kind": "fact_reframe", "field": "display_text_ko",
                                     "before": old, "after": new,
                                     "reason": "라벨귀속 '분리하도록 안내' 단정 제거(인용 흡수저하 FACT-only·PR-1 선례)"}
                copy_changes.append({"candidate_id": cid, "id": rel["id"], "ingredient": rel["ingredient"],
                                     "kind": "fact_reframe", "field": "display_text_ko",
                                     "before": old, "after": new})
        else:
            # F4: prep reframe 유지 — 라벨귀속 분리-안내 단정이 없어야 함(안전 확인)
            assert "분리하도록 안내" not in rel["display_text_ko"], \
                f"{cid}: display 에 라벨귀속 분리-안내 단정 잔존"
        # reframe 후 금칙어/지시 재스캔
        bad = F3.vfp.scan(f"{rel['display_text_ko']} {rel.get('management_ko','')}")
        if bad:
            viol.append(f"{cid}: 카피 금칙어 {bad}")

    projected = proj3 + proj4
    return entries, projected, viol, copy_changes


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
        if r.get("mechanism") != "absorption":
            bad.append(f"id{r['id']}: mechanism != absorption")
        if r.get("recommended_action") != "separation":
            bad.append(f"id{r['id']}: recommended_action != separation")
        if r.get("counterpart_category") != "al_mg_antacid":
            bad.append(f"id{r['id']}: counterpart_category != al_mg_antacid")
    return bad


def main():
    ap = argparse.ArgumentParser(description="PR-3 small2 live 통합")
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

    entries, projected, viol, copy_changes = build_projected(exp0, lock)
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
    print(f"=== PR-3 small2 통합 ({mode}) — {len(projected)}건 ===")
    print(f"baseline {before} → {after} · 신규 id {[r['id'] for r in projected]}")
    fam = {}
    for e in entries:
        fam[e["_family"]] = fam.get(e["_family"], 0) + 1
    print(f"family: {fam} · copy_change: {len(copy_changes)} 필드")
    for r in projected:
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, ev={r['evidence_level']}, "
              f"cat={r.get('counterpart_category')}, plink={r['product_link_allowed']}, "
              f"clin={r['requires_clinical_review']})")

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
        json.dump({"meta": {"name": "pr3_small2_display_copy_change_v1_4", "wave": "small2", "mode": mode,
                            "principle": "라벨귀속 '분리하도록 안내' 단정 제거(FACT-only) · 레보티록신 Al-only(Mg 미명시)",
                            "f3_fact_reframe": list(F3_FACT_REFRAME),
                            "f4_note": "RF-F4-0173 = F4 prep 단계 Al-only display_reframe 유지(투여간격 라벨 근거)·PR-3 추가 변경 없음",
                            "count_field_changes": len(copy_changes)},
                   "changes": copy_changes}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    if not apply:
        artifact = {
            "meta": {
                "name": "pr3_small2_live_dryrun_v1_4", "status": "DRY-RUN — live 무수정 예상 산출물",
                "wave": "small2", "mode": mode,
                "baseline_relation_count": before, "expected_relation_count_after": after,
                "delta": len(projected), "new_ids": [r["id"] for r in projected],
                "candidate_ids": lock["candidate_ids"], "v0_2_sim_passed": ok_sim,
                "export_sha_before": sha_before,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "integration_class": "PM-reviewed verified-reference integration (NOT clinical review)",
                "copy_change_field_count": len(copy_changes),
                "non_target_protected_snapshot": snap_before,
            },
            "projected_entries": [
                {k: v for k, v in e.items() if k != "projected_live_relation"} | {
                    "projected_live_relation": e["projected_live_relation"]} for e in entries],
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
        " | PR-3 small2 PM-reviewed verified-reference 통합: F3 이반드론산 × Al/Mg 함유 제산제 1 + "
        "F4 레보티록신 × 알루미늄 함유 제산제 1 = 2건. relation %d→%d. "
        "published/clinical_reviewed=false·reviewed_by 미기재 유지(verified_reference 천장)." % (before, after))
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
          f"비대상 보호셋 불변. INTEGRATE PR-3 SMALL2: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
