#!/usr/bin/env python3
"""
run_depletion_harvest_dryrun_v1_8.py — depletion 추출기 **bounded dry-run harvest**(PHASE 4).

큐(data/harvest_queue/harvest_candidates.csv)의 depletion source_check_candidate(16건)을
online(nedrug, 검증된 v1.7 client)으로 채굴한다. **live/보호 무수정 · reviewer-ready 패키지만**.

흐름(후보별):
  1) 검색(별칭) → 단일성분·경구 + 주성분 정확매칭(부분매칭 오탐 차단) 제품
  2) 상세 fetch(raw 상한 ≤300) → extract_label_depletion_v1_8.extract_depletions
  3) 후보 nutrient 결핍 finding 선택(deficiency_state>excretion_increase, 헤지 회피)
  4) safe_app_copy(depletion) + 🔑 칼륨 invariant 강제 + projected live relation(스키마=live)
  5) 독립 fidelity-audit(DB6) → reviewer_ready / needs_review / reject
  6) live (ingredient,nutrient) dedup · needs_review/reject 보존

산출(data/review/, live 무수정):
  depletion_extractor_reviewer_ready_v1_8.json   reviewer-ready(미live·PR-3/4 스키마)
  depletion_extractor_dryrun_v1_8.json           funnel/needs_review/reject/projected/가드/dedup/v0.2 증거
  depletion_extractor_report_v1_8.md             PM 보고 요약

사용: python3 scripts/run_depletion_harvest_dryrun_v1_8.py   (online·dry-run·쓰기=data/review/ 한정)
종료: 0 정상, 1 STOP(가드 위반/false_auto_pass).
"""
import csv
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
QUEUE = os.path.join(DATA, "harvest_queue", "harvest_candidates.csv")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
REVIEW = os.path.join(DATA, "review")
RR_OUT = os.path.join(REVIEW, "depletion_extractor_reviewer_ready_v1_8.json")
DRY_OUT = os.path.join(REVIEW, "depletion_extractor_dryrun_v1_8.json")
REPORT_OUT = os.path.join(REVIEW, "depletion_extractor_report_v1_8.md")
CACHE = os.path.join(DATA, "harvest_cache_v1_7")
CONFIRMED_AT = "2026-06-20"
RAW_CAP = 300
MAX_PRODUCTS_PER_DRUG = 5     # 약물당 상세 fetch 상한(raw 절약)


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cli = _load("cli", "nedrug_online_client_v1_7.py")
dp = _load("dp", "extract_label_depletion_v1_8.py")
au = _load("au", "audit_depletion_fidelity_v1_8.py")

# 큐 약물명 → (검색명, 정규 성분명=라벨/relation 표기). nedrug 철자 정합.
SEARCH_ALIAS = {
    "하이드로코르티손": ("히드로코르티손", "히드로코르티손"),
}
# 결정성(reproducibility): PHASE 0 에서 검증한 대표 itemSeq 를 우선 선택(커밋 fixture·선행 적대패키지 정합).
# 검색결과에 있으면 이 제품을 먼저 평가 — 없으면 일반 검색순서로 폴백.
VERIFIED_PREFER = {
    "메틸프레드니솔론": "199800324", "덱사메타손": "196300064", "히드로코르티손": "200703172",
    "플루드로코르티손": "199907231", "아세타졸아미드": "201403403", "아조세미드": "199001306",
}
RANK = {"deficiency_state": 3, "excretion_increase": 2, "level_decrease": 1}


def alias(drug):
    return SEARCH_ALIAS.get(drug, (drug, drug))


def load_depletion_queue():
    out = []
    with open(QUEUE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("mechanism") == "depletion" and row.get("precheck_class") == "source_check_candidate":
                out.append(row)
    return out


def pick_finding(findings, nutrient):
    """nutrient 결핍 finding 중 최선 선택(결핍STATE>배설증가, 비헤지 우선)."""
    cands = [f for f in findings if f["nutrient"] == nutrient]
    if not cands:
        return None
    cands.sort(key=lambda f: (RANK.get(f["evidence_kind"], 0), not au._is_hedged(f["source_quote"])),
               reverse=True)
    # 비헤지 우선: 헤지 아닌 finding 이 있으면 그것
    nonhedged = [f for f in cands if not au._is_hedged(f["source_quote"])]
    return (nonhedged or cands)[0]


def section_summary(nutrient, kind):
    k = {"deficiency_state": f"{nutrient} 결핍 상태 명시(저{nutrient}혈증/손실)",
         "excretion_increase": f"{nutrient} 배설 증가 명시",
         "level_decrease": f"{nutrient} 저하/감소 명시"}
    return k.get(kind, f"{nutrient} 결핍 명시")


def build_relation(canonical, nutrient, seq, item_name, section, kind, projected_id):
    disp, mng = au.safe_depletion_copy(nutrient)
    rel = {
        "id": projected_id,
        "ingredient": canonical,
        "nutrient": nutrient,
        "mechanism": "depletion",
        "recommended_action": "monitoring",
        "evidence_level": "moderate",       # reviewer-adjustable(선행 적대패키지는 high). 보수 기본값.
        "display_text_ko": disp,
        "management_ko": mng,
        "product_link_allowed": False,
        "potassium_safety_card": (nutrient == "칼륨"),
        "requires_clinical_review": False,
        "source": {
            "type": "허가사항",
            "url": f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={seq}",
            "pointer": f"식약처 허가사항(nedrug) / {item_name}({canonical}, itemSeq {seq}) / {section} / "
                       f"{section_summary(nutrient, kind)} / 확인일 {CONFIRMED_AT}",
        },
        "counterpart_category": None,
    }
    return rel


def main():
    queue = load_depletion_queue()
    exp = json.load(open(EXPORT, encoding="utf-8"))
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    max_id = max(r["id"] for r in exp["relations"])

    c = cli.NedrugOnlineClient(cache_dir=CACHE)
    raw_fetched = 0
    label_htmls = {}      # itemSeq -> html (audit verbatim 검증용)
    candidates = []       # 모든 후보(분류 포함)
    next_id = max_id

    for row in queue:
        cid = row["candidate_id"]
        drug = row["ingredient"]
        nut = row["nutrient"]
        search_name, canonical = alias(drug)
        rec = {"candidate_id": cid, "queue_drug": drug, "drug_ingredient": canonical,
               "nutrient": nut, "counterpart_type": "nutrient", "counterpart_category": None,
               "risk_level": row.get("risk_level")}

        # live 중복(이미 라이브면 harvest 대상 아님)
        if (canonical, nut) in live_pairs:
            rec.update(harvest_verdict="reject", reject_reason="already_live")
            candidates.append(rec); continue

        rows = c.search_rows(search_name, max_pages=2)
        if not rows:
            rec.update(harvest_verdict="reject", reject_reason="not_reachable(국내 미유통/검색0)",
                       search_rows=0)
            candidates.append(rec); continue
        products = [r for r in rows if dp.is_single_oral_depletion(r, canonical)]
        prefer = VERIFIED_PREFER.get(canonical)
        if prefer:                          # 검증 itemSeq 를 맨 앞으로(결정성)
            products.sort(key=lambda r: str(r.item_seq) != prefer)
        rec["search_rows"] = len(rows)
        rec["single_oral_exact"] = len(products)
        if not products:
            rec.update(harvest_verdict="reject", reject_reason="no_single_oral_exact(주성분 정확매칭 경구 0)")
            candidates.append(rec); continue

        # 제품 상세에서 nutrient 결핍 finding 탐색(raw cap)
        best = None
        for r in products[:MAX_PRODUCTS_PER_DRUG]:
            if raw_fetched >= RAW_CAP:
                break
            html = c.fetch_detail(r.item_seq)
            raw_fetched += 1
            if not html or len(html) < 5000:
                continue
            label_htmls[str(r.item_seq)] = html
            f = pick_finding(dp.extract_depletions(html), nut)
            if f:
                best = (r, f)
                # 결핍STATE(최강) 찾으면 즉시 채택
                if f["evidence_kind"] == "deficiency_state" and not au._is_hedged(f["source_quote"]):
                    break
        if not best:
            rec.update(harvest_verdict="reject",
                       reject_reason=f"no_{nut}_deficiency_in_label(라벨 {nut} 결핍 명시 없음/임부·상호작용 only)")
            candidates.append(rec); continue

        r, f = best
        next_id += 1
        rel = build_relation(canonical, nut, r.item_seq, r.item_name, f["section"],
                             f["evidence_kind"], next_id)
        rel, kviol = au.potassium_enforce(rel)
        rec.update({
            "itemSeq": r.item_seq, "item_name": r.item_name, "source_section": f["section"],
            "source_quote": f["source_quote"], "evidence_kind": f["evidence_kind"],
            "mechanism": "depletion", "recommended_action": "monitoring", "evidence_level": "moderate",
            "display_text_ko": rel["display_text_ko"], "management_ko": rel["management_ko"],
            "potassium_safety_card": rel["potassium_safety_card"], "product_link_allowed": False,
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "requires_clinical_review": False, "live_integration_forbidden": True,
            "projected_id": next_id, "projected_relation": rel,
            "source": rel["source"], "potassium_invariant_violations": kviol,
        })
        # 추출 성공(auto_pass) — 단 reviewer-ready 직행 금지(DB6: audit 가 결정)
        rec["harvest_verdict"] = "reviewer_ready"   # 잠정(audit 가 확정)
        candidates.append(rec)

    # ── DB6/DB7: 독립 fidelity-audit 전수 ──
    audit = au.audit_corpus(candidates, label_htmls, live_pairs)
    for rec in candidates:
        res = audit["per"].get(rec.get("candidate_id"))
        if res:
            rec["audit"] = res
            # audit 가 최종 verdict(추출 성공이라도 audit reject/needs_review 면 강등)
            if rec.get("harvest_verdict") == "reviewer_ready":
                rec["final_verdict"] = res["verdict"]
            else:
                rec["final_verdict"] = rec["harvest_verdict"]
        else:
            rec["final_verdict"] = rec.get("harvest_verdict")

    reviewer_ready = [r for r in candidates if r["final_verdict"] == "reviewer_ready"]
    needs_review = [r for r in candidates if r["final_verdict"] == "needs_review"]
    rejected = [r for r in candidates if r["final_verdict"] == "reject"]
    false_ap = audit["false_auto_pass"]

    # 🔑 칼륨 invariant 전수
    rr_rels = [r["projected_relation"] for r in reviewer_ready]
    kok, kviol = au.potassium_invariant_ok(rr_rels)

    funnel = {
        "raw_detail_fetched": raw_fetched, "raw_cap": RAW_CAP,
        "queue_depletion_candidates": len(queue),
        "reviewer_ready": len(reviewer_ready), "needs_review": len(needs_review),
        "rejected": len(rejected), "false_auto_pass": len(false_ap),
        "reject_reason_breakdown": {},
    }
    for r in rejected:
        rr = r.get("reject_reason", "?").split("(")[0]
        funnel["reject_reason_breakdown"][rr] = funnel["reject_reason_breakdown"].get(rr, 0) + 1

    # ── 산출물 기록(data/review/ 한정) ──
    os.makedirs(REVIEW, exist_ok=True)
    reviewer_ready_doc = {
        "meta": {
            "name": "depletion_extractor_reviewer_ready_v1_8",
            "status": "REVIEWER-READY(미live) — live_integration_forbidden=true. 승격은 PM 승인+clinical reviewer note+별도 PR.",
            "track": "depletion(칼륨/마그네슘) — extract_label_depletion_v1_8 online harvest",
            "confirmed_at": CONFIRMED_AT,
            "copy_source": "fix_harvester_display_template_v1_6.safe_app_copy(depletion) — live 86-93 선례 동형(보충/수치 단정 0)",
            "potassium_policy": "🔑 칼륨 행 potassium_safety_card=true·product_link_allowed=false 강제(invariant). 보충 권유 0·결핍 단정 0.",
            "evidence_level_note": "reviewer-ready 보수 기본값=moderate. 선행 적대패키지(potassium_depletion_pm_ready_v1_2)는 동일 약물 high — reviewer 가 확정.",
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "count": len(reviewer_ready),
            "potassium_invariant_ok": kok,
        },
        "candidates": reviewer_ready,
    }
    with open(RR_OUT, "w", encoding="utf-8") as f:
        json.dump(reviewer_ready_doc, f, ensure_ascii=False, indent=1); f.write("\n")

    dry_doc = {
        "meta": {
            "name": "depletion_extractor_dryrun_v1_8",
            "status": "DRY-RUN — live/보호 무수정. write-scope=data/review/.",
            "confirmed_at": CONFIRMED_AT,
            "extractor": "extract_label_depletion_v1_8", "audit": "audit_depletion_fidelity_v1_8",
            "gold": ["메틸프레드니솔론 199800324", "아조세미드 199001306", "아세타졸아미드 201403403"],
            "live_baseline_relations": len(exp["relations"]), "live_max_id": max_id,
            "funnel": funnel, "potassium_invariant_ok": kok, "potassium_invariant_violations": kviol,
            "false_auto_pass": false_ap,
        },
        "reviewer_ready_projected": [r["projected_relation"] for r in reviewer_ready],
        "candidates_all": candidates,
        "audit_counts": audit["counts"],
        "live_dedup_note": "live (ingredient,nutrient) 중복은 already_live reject. 신규 projected id=runtime max+1.",
    }
    with open(DRY_OUT, "w", encoding="utf-8") as f:
        json.dump(dry_doc, f, ensure_ascii=False, indent=1); f.write("\n")

    # ── 보고 markdown ──
    lines = [f"# depletion 추출기 v1.8 dry-run 보고 ({CONFIRMED_AT})", "",
             f"- 큐 depletion source_check_candidate: **{len(queue)}건**",
             f"- raw 상세 fetch: {raw_fetched} (cap {RAW_CAP})",
             f"- **reviewer-ready: {len(reviewer_ready)}** · needs_review: {len(needs_review)} · reject: {len(rejected)}",
             f"- false_auto_pass: {len(false_ap)} · 🔑 칼륨 invariant: {'OK' if kok else 'VIOLATION '+str(kviol)}", "",
             "## reviewer-ready"]
    for r in reviewer_ready:
        rel = r["projected_relation"]
        lines.append(f"- `{r['candidate_id']}` {rel['ingredient']} × {rel['nutrient']} "
                     f"(itemSeq {r['itemSeq']}, kcard={rel['potassium_safety_card']}, ev={rel['evidence_level']}) — {r['source_section']}")
        lines.append(f"    - quote: {r['source_quote']}")
    lines += ["", "## reject (사유별)"]
    for r in rejected:
        lines.append(f"- `{r['candidate_id']}` {r['drug_ingredient']} × {r['nutrient']} — {r.get('reject_reason')}")
    if needs_review:
        lines += ["", "## needs_review"]
        for r in needs_review:
            lines.append(f"- `{r['candidate_id']}` {r['drug_ingredient']} × {r['nutrient']} — {r.get('audit',{}).get('flags')}")
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # ── 콘솔 funnel ──
    print("=== depletion 추출기 v1.8 dry-run ===")
    print(f"queue={len(queue)} raw_fetched={raw_fetched} | reviewer_ready={len(reviewer_ready)} "
          f"needs_review={len(needs_review)} reject={len(rejected)} false_auto_pass={len(false_ap)}")
    print(f"칼륨 invariant: {'OK' if kok else 'VIOLATION '+str(kviol)}")
    print(f"audit_counts={audit['counts']}")
    for r in reviewer_ready:
        rel = r["projected_relation"]
        print(f"  RR id{rel['id']} {rel['ingredient']}×{rel['nutrient']} kcard={rel['potassium_safety_card']} "
              f"link={rel['product_link_allowed']} <{r['source_section']}>")
    print(f"reject breakdown: {funnel['reject_reason_breakdown']}")
    print(f"stats: {c.stats}")
    print(f"written: {os.path.relpath(RR_OUT, REPO)} · {os.path.relpath(DRY_OUT, REPO)} · {os.path.relpath(REPORT_OUT, REPO)}")

    if false_ap or not kok:
        print("STOP: false_auto_pass 또는 칼륨 invariant 위반 — batch 재검 필요")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
