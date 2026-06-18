#!/usr/bin/env python3
"""
integrate_pr1_antibiotic24_live_v1_4.py
MediStack v1.4 — **PR-1 antibiotic24 LIVE 통합** 스크립트 (dry-run 기본 / --apply 시 실제 v0.2 export 기록).

대상 24건 = F1 퀴놀론 18 + F2 테트라사이클린 5 + 시프로플록사신 × Al/Mg 함유 제산제 add-on 1.
relation_count 60 → 84. 신규 id = runtime max+1.

이 통합은 **PM-reviewed verified-reference integration** 이다(임상 검수 아님).
published=false / clinical_reviewed=false / reviewed_by 공란 / product_link_allowed=false /
requires_clinical_review=false / potassium_safety_card=false 를 전건 유지한다.

빌드 로직 재사용:
  - F1 18: integrate_f1_quinolone_batch_v1_4.build_subset (reverify 10렌즈 + guard_projected + draft_to_live)
  - F2 5 : integrate_f2_tetracycline_batch_v1_4.build_subset (family 재검증 + guard_projected + draft_to_live)
  - add-on 1: audit-cleanup final_reviewer_ready (독립 적대감사 AUDIT_PASS) → source pointer/quote 보존 통합.
  - id 순차 부여(runtime max+1): F1 → F2 → add-on.

게이트(--apply):
  - --pm-note PATH 가 check_pr1_antibiotic24_pm_note 를 PASS 해야 함.
  - --expected-base / --expected-final 일치, dup 0, ids disjoint, count==24.
  - --fail-on-protected-change: 비대상 보호셋(v0.1/full index/aliases/src/...) sha 불변(v0.2 만 대상).

사용:
  python3 scripts/integrate_pr1_antibiotic24_live_v1_4.py --dry-run --pm-note <note> --expected-base 60 --expected-final 84 --fail-on-protected-change
  python3 scripts/integrate_pr1_antibiotic24_live_v1_4.py --apply  --pm-note <note> --expected-base 60 --expected-final 84 --fail-on-protected-change
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
LOCK = os.path.join(DATA, "review", "pr1_antibiotic24_candidate_lock_v1_4.json")
ADDON = os.path.join(DATA, "review", "autofactory_v1_5_audit_cleanup_candidate_decisions.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "pr1_antibiotic24_live_dryrun_v1_4.json")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F1 = _load("f1mod", "integrate_f1_quinolone_batch_v1_4.py")
F2 = _load("f2mod", "integrate_f2_tetracycline_batch_v1_4.py")
chk = _load("pmchk", "check_pr1_antibiotic24_pm_note_v1_4.py")
guard = _load("guardmod", "guard_no_live_write_v1_3.py")
integ = F1.integ  # theme_map: draft_to_live / guard_projected / run_v0_2 / _sim_with

ADDON_CONFIRMED_AT = "2026-06-17"  # add-on 독립감사 fuller-quote 확정일(source pointer 보존)

# ── display copy_change (source fidelity) ───────────────────────────────────────
# 독립 적대검증(critic:action)이 적발: display 의 2번째 문장 "복용 시점을 분리하도록 안내하고 있으니"는
# 라벨이 '타이밍 분리 안내'를 제공한다고 단정한다. 인용에 명시적 타이밍 분리("투여 전후 N시간 이내 병용하지
# 않는 것이 바람직하다")가 있는 케이스(TIMING)에서는 충실하나,
#  - AVOID-only(라벨="병용을 피하는 것이 바람직하다", 간격 미명시)
#  - FACT-only(라벨=흡수저하 사실만, 지시어 없음)
# 에서는 라벨에 없는 separation guidance 를 노출 → CLAUDE.md '원문에 없으면 노출 금지/원문보다 강하면 금지' 위반 소지.
# 기존 live 선례(id40/41/42·id47/48·id61)는 display 에 라벨이 'separation 을 안내한다'고 단정하지 않는다.
# display = 흡수저하 사실(라벨귀속)만 두고, separation 은 management(MediStack 제안·hedged)에 둔다.
# 2차 적대검증에서 TIMING 케이스의 '복용 시점을 분리하도록 안내하고 있으니'(라벨이 분리를 능동 안내한다는 register)도
# 인용("…2시간 이내 병용하지 않는 것이 바람직하다"=회피권고)을 초과한다고 적발 → display 2번째 문장을 **전건** 보수 reframe.
#   - AVOID-only(라벨="병용을 피하는 것이 바람직하다"): 라벨의 회피권고를 충실히 진술(_TAIL_AVOID).
#   - 그 외 전건(TIMING·FACT·add-on): 라벨귀속 분리-안내 단정 제거, 복용 시점 상담 유도(_TAIL_FACT).
# separation 의 구체 안내는 management(hedged)·약사 상담으로 위임(live 선례 동형). relation/action(separation) 불변.
PR1_AVOID_ONLY = {"RF-F1-0040"}                                  # 발로플록사신 ×Al/Mg 제산제(라벨=회피권고)
_DISP_MARKER = "허가사항 문구가 있습니다."
_TAIL_AVOID = " 함께 복용을 피하는 것이 바람직하다고 안내하고 있으니, 약사 또는 의사와 상담하세요."
_TAIL_FACT = " 함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요."


def reframe_display(old, kind):
    """display 2번째 문장만 보수적 reframe. 1번째(counterpart별 흡수저하 사실·라벨귀속)는 보존."""
    assert _DISP_MARKER in old, f"display 템플릿 불일치(reframe 불가): {old[:40]}"
    head = old.split(_DISP_MARKER)[0] + _DISP_MARKER
    tail = _TAIL_AVOID if kind == "avoid" else _TAIL_FACT
    new = head + tail
    # 안전: reframe 결과는 '분리하도록 안내' 단정을 포함하지 않아야 함(fact/avoid)
    assert "분리하도록 안내" not in new, "reframe 후에도 separation-guidance 단정 잔존"
    return new


def non_target_protected_paths():
    """전체 보호셋에서 v0.2 export(이번 통합 대상)만 제외 → 비대상 보호셋."""
    target = os.path.relpath(EXPORT, REPO)
    return [p for p in guard.protected_paths() if p != target]


def load_lock():
    return json.load(open(LOCK, encoding="utf-8"))


def load_addon():
    d = json.load(open(ADDON, encoding="utf-8"))
    frr = d["final_reviewer_ready"]
    addon = [a for a in frr if a["id"].startswith("AFP-F1-시프로플록사신")][0]
    return addon


def addon_to_live(addon, new_id):
    """add-on(audit-cleanup) → live relation. source pointer/quote 보존(확인일 2026-06-17·fuller quote)."""
    src = addon["source"]
    quote = src["quote"].strip()
    pointer = src["pointer"]
    # 무결성: quote 가 pointer 부분문자열(허위 인용 차단)
    assert quote in pointer, "add-on quote 가 pointer 부분문자열 아님 — 인용 무결성 위반"
    assert re.search(r"itemSeq=\d+", src["url"]), "add-on source url 에 itemSeq 없음"
    assert "확인일 " + ADDON_CONFIRMED_AT in pointer, "add-on pointer 확인일 불일치"
    rel = {
        "id": new_id,
        "ingredient": addon["drug"],
        "nutrient": addon["counterpart"],
        "mechanism": addon["mechanism"],
        "recommended_action": addon["recommended_action"],
        "evidence_level": addon["evidence_level"],
        "display_text_ko": addon["display_text_ko"],
        "management_ko": addon["management_ko"],
        "product_link_allowed": False,
        "potassium_safety_card": False,
        "requires_clinical_review": False,
        "source": {"type": src["type"], "url": src["url"], "pointer": pointer},
        "counterpart_category": addon["counterpart_canon"],
    }
    return rel


def addon_row(addon):
    """guard_projected 가 기대하는 row 어댑터(add-on)."""
    return {
        "candidate_id": addon["id"],
        "drug_ingredient": addon["drug"],
        "counterpart": addon["counterpart"],
        "counterpart_type": "drug",
        "counterpart_category": addon["counterpart_canon"],
        "source": {"url": addon["source"]["url"]},
    }


def build_projected(exp0, lock):
    """F1 18 + F2 5 + add-on 1 → (entries, projected, violations). live 무수정(메모리 시뮬만)."""
    f1_ids = [c["candidate_id"] for c in lock["candidates"]
              if c["family"] == "F1" and c["origin"] == "reviewer_ready_batch_v1_4"]
    f2_ids = [c["candidate_id"] for c in lock["candidates"] if c["family"] == "F2"]
    addon_id = [c["candidate_id"] for c in lock["candidates"]
                if c["origin"] == "production_audit_cleanup"][0]
    viol = []
    entries = []

    # F1 18 (build_subset = reverify + guard_projected + draft_to_live + live-dedup)
    e1, v1 = F1.build_subset(exp0, f1_ids)
    viol += [f"F1: {x}" for x in v1]
    if len(e1) != len(f1_ids):
        viol.append(f"F1 entries {len(e1)} != 기대 {len(f1_ids)}")
    proj1 = [e["projected_live_relation"] for e in e1]
    entries += [dict(e, _family="F1") for e in e1]

    # F2 5 (exp + F1 통합분 기준으로 id 이어서 부여)
    exp1 = integ._sim_with(exp0, proj1)
    e2, v2 = F2.build_subset(exp1, f2_ids)
    viol += [f"F2: {x}" for x in v2]
    if len(e2) != len(f2_ids):
        viol.append(f"F2 entries {len(e2)} != 기대 {len(f2_ids)}")
    proj2 = [e["projected_live_relation"] for e in e2]
    entries += [dict(e, _family="F2") for e in e2]

    # add-on 1
    exp2 = integ._sim_with(exp1, proj2)
    addon = load_addon()
    if addon["id"] != addon_id:
        viol.append(f"add-on id {addon['id']} != lock {addon_id}")
    if addon.get("independent_audit") != "passed":
        viol.append(f"add-on independent_audit != passed ({addon.get('independent_audit')})")
    nid = max(r["id"] for r in exp2["relations"]) + 1
    arel = addon_to_live(addon, nid)
    arow = addon_row(addon)
    viol += [f"add-on: {x}" for x in integ.guard_projected(addon_id, arow, arel)]
    proj_addon = [arel]
    entries.append({"candidate_id": addon_id, "projected_id": nid, "_family": "F1_addon",
                    "counterpart_type": "drug", "counterpart_category": arel["counterpart_category"],
                    "recommended_action": arel["recommended_action"], "evidence_level": arel["evidence_level"],
                    "reverify_verdict": "audit_pass_5_5", "projected_live_relation": arel})

    # ── display copy_change (source fidelity reframe; 전건) ──
    for e in entries:
        cid = e["candidate_id"]
        kind = "avoid" if cid in PR1_AVOID_ONLY else "fact"
        rel = e["projected_live_relation"]
        old = rel["display_text_ko"]
        new = reframe_display(old, kind)
        if new != old:
            rel["display_text_ko"] = new
            e["_display_copy_change"] = {"kind": kind, "before": old, "after": new,
                                         "reason": "라벨에 없는 separation-guidance 단정 제거(원문 충실)"}
        # reframe 후 금칙어/지시 재스캔
        bad = F1.vfp.scan(f"{rel['display_text_ko']} {rel.get('management_ko','')}")
        if bad:
            viol.append(f"{cid}: reframe 후 금칙어 {bad}")

    projected = proj1 + proj2 + proj_addon
    return entries, projected, viol


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
    # 보호 플래그 전건
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
    return bad


def main():
    ap = argparse.ArgumentParser(description="PR-1 antibiotic24 live 통합")
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

    entries, projected, viol = build_projected(exp0, lock)
    viol += integrity_checks(exp0, projected, lock, args.expected_base, args.expected_final)

    # 제품/schedule pass-through 확인(projected 에 제품/schedule 필드 자체가 없음)
    PRODUCT_FIELDS = {"product", "products", "purchase_link", "affiliate", "buy_url", "price"}
    for r in projected:
        leaked = PRODUCT_FIELDS & set(r.keys())
        if leaked:
            viol.append(f"id{r['id']}: 제품 필드 누출 {sorted(leaked)}")
        if "schedule" in r:
            viol.append(f"id{r['id']}: schedule 필드 누출")

    before = len(exp0["relations"])
    after = before + len(projected)
    print(f"=== PR-1 antibiotic24 통합 ({mode}) — {len(projected)}건 ===")
    print(f"baseline {before} → {after} · 신규 id {[r['id'] for r in projected]}")
    fam = {}
    for e in entries:
        fam[e["_family"]] = fam.get(e["_family"], 0) + 1
    print(f"family: {fam}")
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

    # v0.2 validator 시뮬
    ok_sim, tail = integ.run_v0_2(integ._sim_with(exp0, projected))
    print(f"\n[validator] v0.2 sim PASS={ok_sim}")
    if not ok_sim:
        print(tail)
        print("[STOP] v0.2 validator sim 실패")
        return 1

    if not apply:
        # 드라이런 산출물 기록(live 무수정)
        artifact = {
            "meta": {
                "name": "pr1_antibiotic24_live_dryrun_v1_4",
                "status": "DRY-RUN — live 무수정 예상 산출물",
                "wave": "antibiotic24", "mode": mode,
                "baseline_relation_count": before, "expected_relation_count_after": after,
                "delta": len(projected), "new_ids": [r["id"] for r in projected],
                "candidate_ids": lock["candidate_ids"],
                "v0_2_sim_passed": ok_sim,
                "export_sha_before": sha_before,
                "published": False, "clinical_reviewed": False, "reviewed_by": "",
                "integration_class": "PM-reviewed verified-reference integration (NOT clinical review)",
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
        print(f"[dry-run] export sha 불변({sha_before[:8]}). 산출물: {os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
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
    # 보호 상태 불변 보증
    exp0["meta"]["published"] = False
    exp0["meta"]["clinical_reviewed"] = False
    exp0["meta"]["note"] = exp0["meta"].get("note", "") + (
        " | PR-1 antibiotic24 PM-reviewed verified-reference 통합: F1 퀴놀론 18 + F2 테트라사이클린 5 + "
        "시프로플록사신 × Al/Mg 함유 제산제 add-on 1 = 24건. relation %d→%d. "
        "published/clinical_reviewed=false·reviewed_by 미기재 유지(verified_reference 천장)." % (before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp0, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # post-write 검증
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
          f"비대상 보호셋 불변. INTEGRATE PR-1 ANTIBIOTIC24: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
