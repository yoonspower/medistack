#!/usr/bin/env python3
"""
integrate_pr2_chronic8_live_v1_4.py
MediStack v1.4 — **PR-2 chronic8 LIVE 통합** 스크립트 (dry-run 기본 / --apply 시 실제 v0.2 export 기록).

대상 8건 = F9 만성복용 depletion 7 (엽산 3 + 비타민D 4) + F6 에스오메프라졸 × 비타민B12 1.
relation_count 84 → 92. 신규 id = runtime max+1 (86..93).

이 통합은 **PM-reviewed verified-reference integration** 이다(임상 검수 아님).
published=false / clinical_reviewed=false / reviewed_by 공란 / product_link_allowed=false /
requires_clinical_review=false / potassium_safety_card=false 를 전건 유지한다.

빌드 로직 재사용:
  - F9 7: integrate_f9_chronic_depletion_batch_v1_4.build_subset (16 렌즈 재검증 + guard_projected + draft_to_live)
  - F6 1: integrate_f4_f6_f10_small_family_batch_v1_4.build_subset (family:F6 only · F4 0173 은 PR-3)
  - id 순차 부여(runtime max+1): F9 → F6.

PR-2 copy 원칙(copy_change·source fidelity):
  - F9 display 7건: '수치 변화 / 수치가 걱정되면' → '관련된 허가사항 주의 문구 / 증상이 걱정되면' 으로 통일 reframe
    (영양소 '수치 저하' 단정 회피 · 골질환 alarm 비노출). 3건(vitD copy_change)은 이미 reframe 형 → no-op.
  - F9 management 7건: '장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다' 로 통일.
  - F6 display/management: live PPI×B12 표준 템플릿 + 표준 management(이미 동일) → 유지.

게이트(--apply):
  - --pm-note PATH 가 check_pr2_chronic8_pm_note 를 PASS 해야 함.
  - --expected-base / --expected-final 일치, dup 0, ids disjoint, count==8.
  - --fail-on-protected-change: 비대상 보호셋(v0.1/full index/aliases/src/...) sha 불변(v0.2 만 대상).

사용:
  python3 scripts/integrate_pr2_chronic8_live_v1_4.py --dry-run --pm-note <note> --expected-base 84 --expected-final 92 --fail-on-protected-change
  python3 scripts/integrate_pr2_chronic8_live_v1_4.py --apply  --pm-note <note> --expected-base 84 --expected-final 92 --fail-on-protected-change
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
LOCK = os.path.join(DATA, "review", "pr2_chronic8_candidate_lock_v1_4.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "pr2_chronic8_live_dryrun_v1_4.json")
COPY_CHANGE_ARTIFACT = os.path.join(DATA, "review", "pr2_chronic8_display_copy_change_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F9 = _load("f9mod", "integrate_f9_chronic_depletion_batch_v1_4.py")
F6 = _load("f6mod", "integrate_f4_f6_f10_small_family_batch_v1_4.py")
chk = _load("pmchk", "check_pr2_chronic8_pm_note_v1_4.py")
guard = _load("guardmod", "guard_no_live_write_v1_3.py")
integ = F9.integ  # theme_map: draft_to_live / guard_projected / run_v0_2 / _sim_with

# ── PR-2 copy_change (source fidelity · 사용자 PR-2 copy 원칙) ─────────────────────
# F9 display 는 영양소 '수치 변화/수치가 걱정되면' 을 노출했으나, 라벨이 영양소 '수치 저하' 를 직접
# 말하지 않는 케이스(remedy framing) 또는 골질환 alarm 우려가 있어, display 를 '관련된 허가사항 주의
# 문구/증상이 걱정되면' 으로 보수 통일(원문보다 약하게 — under-claim·safe). 골질환 alarm phrase 비노출.
# management 는 검사/복약 지시·영양제 권유로 들리지 않도록 보수 문의 톤으로 통일.
DISP_FOLATE = ("이 약을 장기간 복용할 때 엽산과 관련된 허가사항 주의 문구가 있습니다. "
               "증상이 걱정되면 약사 또는 의사와 상담하세요.")
DISP_VITD = ("이 약을 장기간 복용할 때 비타민D와 관련된 허가사항 주의 문구가 있습니다. "
             "증상이 걱정되면 약사 또는 의사와 상담하세요.")
# 기존(prep) display — survives 형('수치 변화') 과 이미 reframe 된 형(target). reframe 전 둘 중 하나여야 함.
_OLD_FOLATE_SURVIVES = ("이 약을 장기간 복용할 때 엽산 수치 변화와 관련된 허가사항 문구가 있습니다. "
                        "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
_OLD_VITD_SURVIVES = ("이 약을 장기간 복용할 때 비타민D 수치 변화와 관련된 허가사항 문구가 있습니다. "
                      "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
MGMT_F9 = ("장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 "
           "문의해볼 수 있습니다.")
_OLD_MGMT_F9 = "정기적인 확인이 필요할 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."

DISP_TARGET = {"엽산": DISP_FOLATE, "비타민D": DISP_VITD}
DISP_ALLOWED_OLD = {
    "엽산": {_OLD_FOLATE_SURVIVES, DISP_FOLATE},
    "비타민D": {_OLD_VITD_SURVIVES, DISP_VITD},
}
# display 에 절대 노출 금지(골질환 alarm)
BONE_ALARM = ["구루병", "골연화증", "골다공증", "골절", "치아형성", "치조골", "치아형성부전"]


def reframe_f9(rel):
    """F9 relation 의 display/management 를 PR-2 보수 통일 카피로 reframe. (changes: [dict])."""
    changes = []
    nutrient = rel["nutrient"]
    # display
    old_disp = rel["display_text_ko"]
    target_disp = DISP_TARGET.get(nutrient)
    if target_disp is None:
        raise AssertionError(f"F9 nutrient 예상 외: {nutrient}")
    assert old_disp in DISP_ALLOWED_OLD[nutrient], \
        f"F9 display 가 예상 템플릿 아님(reframe 위조 차단): {old_disp[:50]}"
    if old_disp != target_disp:
        rel["display_text_ko"] = target_disp
        changes.append({"field": "display_text_ko", "before": old_disp, "after": target_disp})
    # management
    old_mng = rel.get("management_ko", "")
    assert old_mng in (_OLD_MGMT_F9, MGMT_F9), \
        f"F9 management 가 예상 템플릿 아님(reframe 위조 차단): {old_mng[:50]}"
    if old_mng != MGMT_F9:
        rel["management_ko"] = MGMT_F9
        changes.append({"field": "management_ko", "before": old_mng, "after": MGMT_F9})
    # 골질환 alarm 비노출 사후 검증
    txt = rel["display_text_ko"]
    leaked = [w for w in BONE_ALARM if w in txt]
    assert not leaked, f"reframe 후 display 에 골질환 alarm 잔존: {leaked}"
    return changes


def non_target_protected_paths():
    target = os.path.relpath(EXPORT, REPO)
    return [p for p in guard.protected_paths() if p != target]


def load_lock():
    return json.load(open(LOCK, encoding="utf-8"))


def build_projected(exp0, lock):
    """F9 7 + F6 1 → (entries, projected, violations, copy_changes). live 무수정(메모리 시뮬만)."""
    f9_ids = [c["candidate_id"] for c in lock["candidates"] if c["family"] == "F9"]
    f6_ids = [c["candidate_id"] for c in lock["candidates"] if c["family"] == "F6"]
    viol, entries, copy_changes = [], [], []

    # F9 7
    e9, v9 = F9.build_subset(exp0, f9_ids)
    viol += [f"F9: {x}" for x in v9]
    if len(e9) != len(f9_ids):
        viol.append(f"F9 entries {len(e9)} != 기대 {len(f9_ids)}")
    proj9 = [e["projected_live_relation"] for e in e9]
    entries += [dict(e, _family="F9") for e in e9]

    # F6 1 (exp + F9 통합분 기준으로 id 이어서 부여)
    exp1 = integ._sim_with(exp0, proj9)
    e6, v6 = F6.build_subset(exp1, f6_ids)
    viol += [f"F6: {x}" for x in v6]
    if len(e6) != len(f6_ids):
        viol.append(f"F6 entries {len(e6)} != 기대 {len(f6_ids)}")
    proj6 = [e["projected_live_relation"] for e in e6]
    entries += [dict(e, _family="F6") for e in e6]

    # ── PR-2 copy_change: F9 display/management 보수 통일(F6 는 prep 카피 유지) ──
    for e in entries:
        rel = e["projected_live_relation"]
        if e["_family"] == "F9":
            chgs = reframe_f9(rel)
            if chgs:
                e["_copy_change"] = {"kind": "pr2_conservative_reframe", "changes": chgs}
                for c in chgs:
                    copy_changes.append({"candidate_id": e["candidate_id"], "id": rel["id"],
                                         "ingredient": rel["ingredient"], "nutrient": rel["nutrient"], **c})
        # reframe 후 금칙어/지시 재스캔(F9·F6 공통)
        bad = F9.vfp.scan(f"{rel['display_text_ko']} {rel.get('management_ko','')}")
        if bad:
            viol.append(f"{e['candidate_id']}: 카피 금칙어 {bad}")
        if any(d in (rel["display_text_ko"] + " " + rel.get("management_ko", ""))
               for d in F9.DIRECTIVE_CMDS + F9.TEST_TREAT_DIRECTIVE):
            viol.append(f"{e['candidate_id']}: 복용/검사/처방 지시 카피")

    projected = proj9 + proj6
    return entries, projected, viol, copy_changes


def integrity_checks(exp0, projected, lock, expected_base, expected_final):
    """통합 계약 검사. 위반 리스트(빈=통과)."""
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
    # ids disjoint + unique
    live_ids = {r["id"] for r in exp0["relations"]}
    new_ids = [r["id"] for r in projected]
    if set(new_ids) & live_ids:
        bad.append(f"신규 id 가 live id 와 충돌: {sorted(set(new_ids) & live_ids)}")
    if len(set(new_ids)) != len(new_ids):
        bad.append("신규 id 중복")
    if sorted(new_ids) != lock["expected_ids"]:
        bad.append(f"신규 id {sorted(new_ids)} != lock expected_ids {lock['expected_ids']}")
    # duplicate (ingredient, nutrient) vs live + 내부
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp0["relations"]}
    seen = set()
    for r in projected:
        k = (r.get("ingredient"), r.get("nutrient"))
        if k in live_pairs:
            bad.append(f"live 중복: {k}")
        if k in seen:
            bad.append(f"내부 중복: {k}")
        seen.add(k)
    # 보호 플래그 + depletion/monitoring/nutrient 전건
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
        if r.get("mechanism") != "depletion":
            bad.append(f"id{r['id']}: mechanism != depletion")
        if r.get("recommended_action") != "monitoring":
            bad.append(f"id{r['id']}: recommended_action != monitoring")
        if "counterpart_category" in r:
            bad.append(f"id{r['id']}: nutrient relation 인데 counterpart_category 존재")
        if r.get("nutrient") not in ("엽산", "비타민D", "비타민B12"):
            bad.append(f"id{r['id']}: nutrient 예상 외 {r.get('nutrient')}")
    return bad


def main():
    ap = argparse.ArgumentParser(description="PR-2 chronic8 live 통합")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="(기본) live 무수정 예상 산출물")
    g.add_argument("--apply", action="store_true", help="실제 v0.2 export 기록(--pm-note 필수)")
    ap.add_argument("--pm-note", help="PM-reviewed note 경로")
    ap.add_argument("--expected-base", type=int, default=None)
    ap.add_argument("--expected-final", type=int, default=None)
    ap.add_argument("--fail-on-protected-change", action="store_true",
                    help="비대상 보호셋(v0.1/index/aliases/src/...) sha 변경 시 STOP")
    ap.add_argument("--no-product-ui", action="store_true", help="제품 UI 추가 0 확인(pass-through)")
    ap.add_argument("--no-schedule", action="store_true", help="schedule 비활성 확인(pass-through)")
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
    print(f"=== PR-2 chronic8 통합 ({mode}) — {len(projected)}건 ===")
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

    # copy_change 기록(드라이런·apply 공통)
    os.makedirs(os.path.dirname(COPY_CHANGE_ARTIFACT), exist_ok=True)
    with open(COPY_CHANGE_ARTIFACT, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "pr2_chronic8_display_copy_change_v1_4",
                            "wave": "chronic8", "mode": mode,
                            "principle": "수치 저하 단정 회피 · 골질환 alarm 비노출 · 모니터링 톤 통일",
                            "f9_display_targets": {"엽산": DISP_FOLATE, "비타민D": DISP_VITD},
                            "f9_management_target": MGMT_F9,
                            "f6_note": "F6(에스오메프라졸×B12) display=live PPI×B12 템플릿·management=표준 유지(reframe 없음)",
                            "count_field_changes": len(copy_changes)},
                   "changes": copy_changes}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    if not apply:
        artifact = {
            "meta": {
                "name": "pr2_chronic8_live_dryrun_v1_4",
                "status": "DRY-RUN — live 무수정 예상 산출물",
                "wave": "chronic8", "mode": mode,
                "baseline_relation_count": before, "expected_relation_count_after": after,
                "delta": len(projected), "new_ids": [r["id"] for r in projected],
                "candidate_ids": lock["candidate_ids"],
                "v0_2_sim_passed": ok_sim,
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

    # ── APPLY (live write) ──
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
        " | PR-2 chronic8 PM-reviewed verified-reference 통합: F9 만성복용 depletion 7 (엽산 3 + 비타민D 4) + "
        "F6 에스오메프라졸 × 비타민B12 1 = 8건. relation %d→%d. "
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
          f"비대상 보호셋 불변. INTEGRATE PR-2 CHRONIC8: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
