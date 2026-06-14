#!/usr/bin/env python3
"""
harvest_relation_bot_v1_3.py
MediStack **relation harvester bot v1.3** — 후보 자동 수집/분류/검증 큐 생성 오케스트레이터.

수작업 relation 확장을 줄이기 위해, 흩어진 배치 스크립트(harvest/precheck/source-check/gate)를
하나의 안전한 파이프라인으로 묶는다. **봇은 live relation 을 만들지도 배포하지도 않는다.**
역할: candidate harvest → precheck → source fetch(SDK) → detector → adversarial preflight
       → source_confirm gate(단일 판정) → PM review queue 생성. 끝.

⚠️ 안전 불변(위반 시 STOP):
  - 보호/live 데이터(export·full index·alias·src·.github·validator)를 한 줄도 쓰지 않는다.
    봇이 쓰는 경로는 오직 data/harvest_queue/ 하위.
  - 어떤 후보도 published/clinical_reviewed=true, live relation, source_confirmed 최종확정을 만들지 않는다.
    confirm 되어도 draft(do_not_implement_yet=true·live_integration_forbidden=true)까지만.
  - 모든 외부 조회는 medistack_sdk.NedrugClient(SDK) 를 통해서만(직접 http 호출 금지).
  - 판정은 source_confirm_gate 단일 게이트 + detector 가 수행. 봇은 라우팅/큐 생성만.

기본은 **offline dry-run**(fixtures, 네트워크 0, 결정론). 실 PM 런은 --online.
사용:
  python3 scripts/harvest_relation_bot_v1_3.py                # offline dry-run(fixtures)
  python3 scripts/harvest_relation_bot_v1_3.py --ingredients 세파클러,프레드니솔론,아세타졸아미드,레보티록신
  python3 scripts/harvest_relation_bot_v1_3.py --online       # 실 nedrug fetch(SDK cache)
종료코드: 0 정상 / 1 안전 위반(STOP).
"""
import argparse
import csv
import datetime
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
QUEUE = os.path.join(DATA, "harvest_queue")
SDK_DIR = os.path.join(QUEUE, "_sdk")
FIXTURES = os.path.join(REPO, "medistack_sdk", "fixtures")

sys.path.insert(0, REPO)
from medistack_sdk import NedrugClient  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


vfs = _load("vfs", "verify_factory_sources_v1_2.py")
kpi = _load("kpi", "analyze_coverage_kpi_v1_2.py")
gate = _load("gate", "source_confirm_gate_v1_2.py")
antacid = _load("antacid", "collect_antacid_interaction_evidence_v1_2.py")
vfp = _load("vfp", "validate_forbidden_phrases_v1_2.py")  # 권위있는 금지어 스캐너 재사용

EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
KPI_CSV = os.path.join(DATA, "coverage_kpi_top_candidates_v1_2.csv")

# antacid 트랙 후보(약물 × Al/Mg 제산제 — 영양소 트랙 아님). 소규모 curated; 신규는 PM 이 추가.
ANTACID_CANDIDATES = [
    ("AT-LVX-01", "레보플록사신", "레보플록사신"),
    ("AT-FEX-01", "펙소페나딘", "펙소페나딘"),
    ("AT-ITZ-01", "이트라코나졸", "이트라코나졸"),  # PM 지시 추가(v1.2 antacid 트랙 AT-05 근거): 아졸계 흡수 저해.
]

# 짝이온염(counter-ion salt) 트랩: 약물 염의 양이온(나트륨/칼륨/칼슘/마그네슘)을 영양소로 오인 방지.
import re  # noqa: E402
COUNTER_ION_RE = re.compile(r"(나트륨|칼륨|칼슘|마그네슘|아연|염산염|황산염|인산염|브롬화|메실산|푸마르산|말레산)$")
NONORAL_FORM_RE = re.compile(r"(주사|점안|점이|점비|연고|크림|로션|외용|흡입|패치|좌제|좌약|관장|가글|스프레이)")


def now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def load_covered_bases():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    return sorted({r["ingredient"] for r in exp.get("relations", [])})


def is_covered(ing, covered_bases):
    return any(c and (c in ing or ing in c) for c in covered_bases)


# ----------------- stage A: candidate harvest -----------------
def harvest_candidates(ing_filter, covered_bases):
    """theme map(nutrient) + CARRIED(hold/reject) + antacid + KPI 스캔 → 후보 universe."""
    cands = []
    # 1) nutrient theme map (grounded active themes)
    for ingredient, items in vfs.SEARCH_INGREDIENTS.items():
        if ing_filter and ingredient not in ing_filter:
            continue
        for (cid, nutrient, mech, action, det_key, ksafe, risk, note) in items:
            cands.append({
                "candidate_id": cid, "track": "nutrient", "ingredient": ingredient,
                "nutrient": nutrient, "mechanism": mech, "relation_type": action,
                "detector_key": det_key, "potassium_safety": "true" if ksafe else "false",
                "risk_level": risk, "candidate_source": "theme_map.SEARCH_INGREDIENTS",
                "note": note, "source_status": "needs_source", "do_not_implement_yet": "true",
            })
    # 2) CARRIED holds/rejects (fetch 없이 분류만)
    for (cid, ing, nut, rtype, status, strength, risk, reason, note) in vfs.CARRIED:
        if ing_filter and ing not in ing_filter:
            continue
        cands.append({
            "candidate_id": cid, "track": "nutrient", "ingredient": ing, "nutrient": nut,
            "mechanism": "", "relation_type": rtype, "detector_key": "", "potassium_safety": "false",
            "risk_level": risk, "candidate_source": f"carry_forward:{strength}", "note": note,
            "source_status": "needs_source", "do_not_implement_yet": "true",
            "_carry_status": status, "_carry_strength": strength, "_carry_reason": reason,
        })
    # 3) antacid track
    for (cid, ing, stem) in ANTACID_CANDIDATES:
        if ing_filter and ing not in ing_filter:
            continue
        cands.append({
            "candidate_id": cid, "track": "antacid", "ingredient": ing, "nutrient": "Al/Mg 제산제(약물)",
            "mechanism": "antacid_interaction", "relation_type": "antacid_interaction", "detector_key": "antacid",
            "potassium_safety": "false", "risk_level": "low", "candidate_source": "antacid_track",
            "note": "약물 × Al/Mg 제산제 directive. 영양소 relation 아님.", "_stem": stem,
            "source_status": "needs_source", "do_not_implement_yet": "true",
        })
    return cands


def scan_kpi(covered_bases, limit):
    """KPI Top 후보 universe 를 precheck 트랩으로 스캔(rejected/hold/already 분류 데모, fetch 없음)."""
    rows = []
    if not os.path.exists(KPI_CSV):
        return rows
    for i, r in enumerate(csv.DictReader(open(KPI_CSV, encoding="utf-8"))):
        if limit and i >= limit:
            break
        ing = r.get("ingredient_name", "")
        pc, reason = precheck_kpi_row(ing, r, covered_bases)
        rows.append({"rank": r.get("rank", ""), "ingredient": ing,
                     "product_count": r.get("product_count", ""),
                     "therapeutic_class": r.get("therapeutic_class", ""),
                     "precheck_class": pc, "reason": reason})
    return rows


def precheck_kpi_row(ing, kpi_row, covered_bases):
    if (kpi_row.get("relation_covered") == "yes") or is_covered(ing, covered_bases):
        return "already_covered", "이미 relation 보유 — 재후보화 불필요."
    if kpi_row.get("sensitive_hold") == "yes" or kpi.classify(ing) in kpi.SENSITIVE_CLASSES:
        return "sensitive_hold", "민감/고위험군(정신건강·항혈전·항암/면역) — clinical reviewer 트랙 전 hold."
    if "/" in ing:
        return "rejected_precheck", "복합제(2성분 이상) — 단일 성분-영양소 모델 부적합·조성 트랩."
    if COUNTER_ION_RE.search(ing):
        return "rejected_precheck", "짝이온염 트랩 — 약물 염의 양이온(나트륨/칼륨/칼슘/Mg)을 영양소로 오인 방지."
    return "rejected_precheck", ("허가사항 6대 영양소 직접 동거어 개연 낮음(품목수만으로 후보화 금지·계열 일반화 금지). "
                                 "grounded theme map 부재 — 후보 아님.")


# ----------------- stage B: precheck (theme/carry/antacid 후보) -----------------
def precheck(cands, covered_bases):
    """후보를 source_check / sensitive_hold / hold / rejected_precheck / already_covered 로 분류."""
    for c in cands:
        ing = c["ingredient"]
        if c["track"] == "nutrient" and "_carry_status" in c:
            # CARRIED: 이미 hold/reject 확정
            strength = c.get("_carry_strength", "")
            if c["_carry_status"] == "reject":
                c["precheck_class"], c["precheck_reason"] = "rejected_precheck", c["_carry_reason"]
            elif strength in ("high_risk", "out_of_scope") or c["risk_level"] == "high":
                c["precheck_class"], c["precheck_reason"] = "sensitive_hold", c["_carry_reason"]
            else:
                c["precheck_class"], c["precheck_reason"] = "literature_only_hold", c["_carry_reason"]
            continue
        if is_covered(ing, covered_bases):
            c["precheck_class"], c["precheck_reason"] = "already_covered", "이미 relation 보유 — 재후보화 불필요."
        elif kpi.classify(ing) in kpi.SENSITIVE_CLASSES:
            c["precheck_class"], c["precheck_reason"] = "sensitive_hold", \
                f"민감군({kpi.classify(ing)}) — clinical reviewer 트랙 전 hold."
        elif "/" in ing:
            c["precheck_class"], c["precheck_reason"] = "rejected_precheck", "복합제 트랩 — 단일 성분 모델 부적합."
        else:
            c["precheck_class"], c["precheck_reason"] = "source_check_candidate", \
                "grounded theme(라벨 직접 동거어 검증 대상). 외용/주사제 trap 은 source-fetch 경구필터가 차단."
    return cands


# ----------------- stage C+D: source fetch(SDK) + detector + adversarial + gate -----------------
def adversarial_preflight(row, fetched_texts):
    """적대 검증: (1)인용이 실제 라벨에 존재 (2)카피가 라벨보다 강하지 않음 (3)복용지시/추천 아님.
    실패 항목을 list 로 반환(빈 list=통과)."""
    fails = []
    quote = (row.get("evidence_snippet") or "").strip()
    if quote:
        # (1) 인용 핵심 토막이 실제 fetched 라벨 원문에 실재하는지(환각/오인용 방지)
        core = quote[:24]
        if core and not any(core in t for t in fetched_texts):
            fails.append("quote_not_in_label")
    # (2) safe copy 가 참고정보 톤 위반(복용지시·추천·구매·의료단정)인지 — 권위있는 FORBIDDEN 재사용
    copy = row.get("safe_user_copy") or ""
    for bad in vfp.scan(copy):
        fails.append(f"copy_forbidden:{bad}")
    return fails


def run_nutrient_sourcecheck(client, source_check_cands, log):
    """source_check 후보를 성분 단위로 fetch → classify_active → gate → 행 산출."""
    # 성분 → items(classify_active 입력 튜플) 재구성
    by_ing = {}
    for c in source_check_cands:
        if c["track"] != "nutrient":
            continue
        items = vfs.SEARCH_INGREDIENTS.get(c["ingredient"], [])
        by_ing.setdefault(c["ingredient"], items)
    results = []
    for ingredient, items in by_ing.items():
        exclude = "메틸프레드니솔론" if ingredient == "프레드니솔론" else None
        seqs, why = vfs.search_itemseqs(client, ingredient, exclude_ingr=exclude, max_n=2, max_pages=2)
        fetched = []
        if seqs:
            for seq, name, ingr in seqs:
                try:
                    text, url = vfs.fetch_detail(client, seq)
                    fetched.append((seq, name, ingr, text, url))
                except Exception as e:  # noqa: BLE001
                    log.append(f"fetch_err {ingredient} {seq}: {type(e).__name__}")
        fetched_texts = [f[3] for f in fetched]
        rows = vfs.classify_active(ingredient, items, fetched, client)
        for r in rows:
            verdict = gate.gate_nutrient(r, "harvest_nutrient")
            adv = adversarial_preflight(r, fetched_texts)
            results.append(_merge(r, verdict, adv, track="nutrient", ingredient=ingredient))
    return results


def run_antacid_sourcecheck(client, antacid_cands, log):
    results = []
    for c in antacid_cands:
        ing, stem = c["ingredient"], c.get("_stem", c["ingredient"])
        seqs, why = vfs.search_itemseqs(client, stem, max_n=2, max_pages=2)
        rec = {"candidate_id": c["candidate_id"], "ingredient": ing, "itemseqs_checked": [],
               "found": False, "directive_kind": "", "quote": "", "url": ""}
        fetched_texts = []
        for seq, name, ingr in (seqs or []):
            try:
                text, url = vfs.fetch_detail(client, seq)
            except Exception as e:  # noqa: BLE001
                log.append(f"antacid fetch_err {ing} {seq}: {type(e).__name__}")
                continue
            rec["itemseqs_checked"].append(seq)
            fetched_texts.append(text)
            found, quote, kind = antacid.find_antacid_quote(text)
            if found:
                rec.update(found=True, directive_kind=kind, quote=quote[:400], url=url)
                break
        verdict = gate.gate_antacid(rec)
        # antacid safe copy(중립 템플릿) — gate 통과 시에만
        row = {
            "candidate_id": rec["candidate_id"], "drug_ingredient": ing, "nutrient": "Al/Mg 제산제(약물)",
            "relation_type": "antacid_interaction", "mechanism": "antacid_interaction",
            "source_status": verdict["verdict"], "itemseqs_checked": ";".join(rec["itemseqs_checked"]),
            "evidence_snippet": rec["quote"], "source_url_or_basis": rec.get("url", ""),
            "evidence_strength": verdict.get("copy_strength", ""), "risk_level": "low",
            "potassium_safety_card": "false",
            "pass_to_draft": "true" if verdict["draft_eligible"] else "false",
            "rejection_or_needs_review_reason": "" if verdict["draft_eligible"] else verdict["gate_reason"],
            "safe_user_copy": (antacid_safe_copy(ing) if verdict["verdict"] == "antacid_draft_confirmed" else ""),
            "internal_note": c["note"],
        }
        adv = adversarial_preflight(row, fetched_texts)
        results.append(_merge(row, verdict, adv, track="antacid", ingredient=ing))
    return results


def antacid_safe_copy(ingredient):
    return (f"{ingredient}과(와) 알루미늄·마그네슘이 함유된 제산제를 같은 시간에 함께 복용하면 "
            f"{ingredient}의 흡수가 줄어들 가능성이 있습니다. / 같은 시간대 복용은 피하고 시간 간격을 두는 것이 "
            f"도움이 될 수 있으며, 구체적인 간격은 약사 또는 의사와 상담하세요.")


def _merge(row, verdict, adv, track, ingredient):
    """source-check 행 + gate verdict + adversarial 결과를 PM 큐 통합행으로."""
    v = verdict["verdict"]
    draft_ok = verdict["draft_eligible"] and not adv
    if verdict["draft_eligible"] and adv:
        v = "needs_review"  # 적대검증 실패 → draft 강등
    return {
        "candidate_id": row["candidate_id"], "track": track, "ingredient": ingredient,
        "nutrient": row.get("nutrient", ""), "mechanism": row.get("mechanism", ""),
        "relation_type": row.get("relation_type", ""),
        "verdict": v, "draft_eligible": draft_ok,
        "itemseqs_checked": row.get("itemseqs_checked", ""),
        "source_quote": row.get("evidence_snippet", ""),
        "source_url_or_basis": row.get("source_url_or_basis", ""),
        "confidence": row.get("evidence_strength", "") or verdict.get("copy_strength", ""),
        "risk_level": row.get("risk_level", ""),
        "potassium_safety_card": row.get("potassium_safety_card", "false"),
        "gate_reason": verdict.get("gate_reason", ""),
        "adversarial_fails": ";".join(adv),
        "safe_copy": row.get("safe_user_copy", ""),
        "do_not_implement_yet": "true", "live_integration_forbidden": "true",
        "published": "false", "clinical_reviewed": "false",
    }


# ----------------- stage E: outputs -----------------
SC_COLS = ["candidate_id", "track", "ingredient", "nutrient", "mechanism", "relation_type",
           "verdict", "draft_eligible", "itemseqs_checked", "confidence", "risk_level",
           "potassium_safety_card", "gate_reason", "adversarial_fails", "source_quote", "safe_copy",
           "live_integration_forbidden"]


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def recommended_action(r):
    if r["draft_eligible"]:
        return "REVIEW→DRAFT 승인 후보(직접근거+적대검증 통과, live 금지)"
    if r["verdict"] == "needs_review":
        return "재확인 필요(근거/적대검증 불충분)"
    return "REJECT(근거 없음)"


def build_pm_queue_md(sc_results, holds, rejects, already, kpi_rows, meta):
    L = []
    L.append("# MediStack Relation Harvester — PM Review Queue (v1.3)\n")
    L.append(f"- 생성: {meta['run_at']}  |  모드: **{meta['mode']}**  |  봇: harvest_relation_bot_v1_3")
    L.append(f"- ⚠️ **live 승격 금지**: 모든 항목 do_not_implement_yet=true · live_integration_forbidden=true · published=false · clinical_reviewed=false")
    L.append(f"- live relation 변경: **0** (봇은 큐만 생성). PM 검토·source 재확인 후 별도 통합 스크립트로만 승격.\n")
    L.append("## 분포")
    L.append(f"- 후보 수집(harvest): {meta['counts']['harvest_total']}")
    L.append(f"- source-check 시도: {meta['counts']['source_checked']}  → draft 후보: **{meta['counts']['draft_eligible']}**, "
             f"needs_review: {meta['counts']['needs_review']}, reject: {meta['counts']['source_reject']}")
    L.append(f"- precheck: already_covered {len(already)}, sensitive/literature hold {len(holds)}, rejected_precheck {len(rejects)}")
    L.append(f"- KPI 트랩 스캔: {len(kpi_rows)}건 분류\n")

    drafts = [r for r in sc_results if r["draft_eligible"]]
    needs = [r for r in sc_results if r["verdict"] == "needs_review"]

    L.append("## A. DRAFT 승인 후보 (PM 판단 필요 · live 금지)\n")
    if not drafts:
        L.append("_(없음)_\n")
    for r in drafts:
        _pm_block(L, r)
    L.append("## B. NEEDS_REVIEW (근거/적대검증 불충분 — source 재확인)\n")
    if not needs:
        L.append("_(없음)_\n")
    for r in needs:
        _pm_block(L, r)

    L.append("## C. HOLD / REJECT 요약 (자동 분류 — 상세는 CSV)")
    L.append(f"- sensitive/literature hold → `sensitive_hold.csv` ({len(holds)})")
    L.append(f"- rejected_precheck → `rejected_precheck.csv` ({len(rejects)})")
    L.append(f"- source-check reject → `needs_review.csv` 내 verdict=reject\n")
    L.append("## PM 판단사항")
    L.append("1. DRAFT 후보의 safe_copy 가 라벨 강도와 일치하는지 최종 확인 후 draft 채택 여부 결정.")
    L.append("2. NEEDS_REVIEW 의 source 재확인(국내 단일 경구 itemSeq / 동거어).")
    L.append("3. 승격은 별도 integrate 스크립트 + clinical reviewer 확보 후(봇 범위 밖).")
    return "\n".join(L) + "\n"


def _pm_block(L, r):
    rel = f"{r['ingredient']} × {r['nutrient']} ({r['mechanism']}/{r['relation_type']})"
    L.append(f"### {r['candidate_id']} — {rel}")
    L.append(f"- relation 후보: {rel}")
    L.append(f"- source quote: \"{(r['source_quote'] or '').strip()[:200]}\"")
    L.append(f"- itemSeq: {r['itemseqs_checked'] or '—'}")
    L.append(f"- confidence: {r['confidence'] or '—'}  |  risk_level: {r['risk_level'] or '—'}")
    L.append(f"- recommended_action: {recommended_action(r)}")
    L.append(f"- reject/hold 이유: {r['gate_reason'] or '—'}"
             + (f"  | 적대검증 실패: {r['adversarial_fails']}" if r['adversarial_fails'] else ""))
    L.append(f"- safe copy 초안: {r['safe_copy'] or '—'}")
    L.append(f"- **live 승격 금지**: do_not_implement_yet=true · live_integration_forbidden=true\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true", help="실 nedrug fetch(SDK). 기본은 offline+fixtures dry-run.")
    ap.add_argument("--ingredients", default="", help="콤마구분 성분 필터(dry-run 권장 서브셋).")
    ap.add_argument("--kpi-limit", type=int, default=60, help="KPI 트랩 스캔 상한.")
    args = ap.parse_args()

    os.makedirs(QUEUE, exist_ok=True)
    os.makedirs(SDK_DIR, exist_ok=True)
    ing_filter = set(x.strip() for x in args.ingredients.split(",") if x.strip())

    client = NedrugClient(
        offline=not args.online, fixtures_dir=(None if args.online else FIXTURES),
        cache_dir=os.path.join(SDK_DIR, "cache"), raw_dir=os.path.join(SDK_DIR, "raw"),
        log_path=os.path.join(SDK_DIR, "calls.jsonl"),
    )
    log = []
    covered_bases = load_covered_bases()

    # A. harvest
    cands = harvest_candidates(ing_filter, covered_bases)
    # B. precheck
    precheck(cands, covered_bases)
    source_check = [c for c in cands if c["precheck_class"] == "source_check_candidate"]
    holds = [c for c in cands if c["precheck_class"] in ("sensitive_hold", "literature_only_hold")]
    rejects = [c for c in cands if c["precheck_class"] == "rejected_precheck"]
    already = [c for c in cands if c["precheck_class"] == "already_covered"]
    kpi_rows = scan_kpi(covered_bases, args.kpi_limit)
    # KPI 스캔 산출도 hold/reject 큐에 합류(분류 가시화)
    for kr in kpi_rows:
        if kr["precheck_class"] == "sensitive_hold":
            holds.append({"candidate_id": f"KPI-r{kr['rank']}", "ingredient": kr["ingredient"],
                          "track": "kpi_scan", "precheck_class": "sensitive_hold",
                          "precheck_reason": kr["reason"], "risk_level": "", "nutrient": ""})
        elif kr["precheck_class"] == "rejected_precheck":
            rejects.append({"candidate_id": f"KPI-r{kr['rank']}", "ingredient": kr["ingredient"],
                            "track": "kpi_scan", "precheck_class": "rejected_precheck",
                            "precheck_reason": kr["reason"], "risk_level": "", "nutrient": ""})

    # C+D. source fetch(SDK) + detector + adversarial + gate
    sc_nutrient = run_nutrient_sourcecheck(client, [c for c in source_check if c["track"] == "nutrient"], log)
    sc_antacid = run_antacid_sourcecheck(client, [c for c in source_check if c["track"] == "antacid"], log)
    sc_results = sc_nutrient + sc_antacid

    drafts = [r for r in sc_results if r["draft_eligible"]]
    needs = [r for r in sc_results if r["verdict"] == "needs_review"]
    sc_reject = [r for r in sc_results if r["verdict"] in ("reject",)]

    # 안전 게이트: 봇은 어떤 행도 live/published/clinical_reviewed 로 만들지 않는다.
    integrity = []
    for r in sc_results:
        if r["live_integration_forbidden"] != "true" or r["do_not_implement_yet"] != "true" \
           or r["published"] != "false" or r["clinical_reviewed"] != "false":
            integrity.append(r["candidate_id"])
    if integrity:
        sys.stderr.write(f"STOP: live-safety 플래그 위반 {integrity}\n")
        return 1

    # E. 출력
    meta = {
        "name": "harvest_relation_bot_v1_3", "run_at": now_iso(),
        "mode": "online" if args.online else "offline_dryrun(fixtures)",
        "live_relations_created": 0, "live_promotions": 0, "deploy": "none",
        "sdk_stats": client.stats, "fetch_errors": log,
        "counts": {
            "harvest_total": len(cands), "source_checked": len(sc_results),
            "draft_eligible": len(drafts), "needs_review": len(needs), "source_reject": len(sc_reject),
            "already_covered": len(already), "hold": len(holds), "rejected_precheck": len(rejects),
            "kpi_scanned": len(kpi_rows),
        },
        "safety": {"live_data_written": False, "write_scope": "data/harvest_queue/ only",
                   "judgment": "source_confirm_gate + detector (봇은 라우팅만)"},
    }

    write_csv(os.path.join(QUEUE, "harvest_candidates.csv"),
              ["candidate_id", "track", "ingredient", "nutrient", "mechanism", "relation_type",
               "detector_key", "risk_level", "candidate_source", "precheck_class", "precheck_reason",
               "do_not_implement_yet"], cands)
    write_csv(os.path.join(QUEUE, "source_check_results.csv"), SC_COLS, sc_results)
    write_csv(os.path.join(QUEUE, "rejected_precheck.csv"),
              ["candidate_id", "track", "ingredient", "nutrient", "precheck_class", "precheck_reason", "risk_level"], rejects)
    write_csv(os.path.join(QUEUE, "sensitive_hold.csv"),
              ["candidate_id", "track", "ingredient", "nutrient", "precheck_class", "precheck_reason", "risk_level"], holds)
    write_csv(os.path.join(QUEUE, "needs_review.csv"), SC_COLS, needs + sc_reject)

    draft_doc = {
        "meta": {"status": "DRAFT CANDIDATES — NOT LIVE / NOT DRAFT-APPROVED",
                 "do_not_implement_yet": True, "live_integration_forbidden": True,
                 "published": False, "clinical_reviewed": False, "live_promotions": 0,
                 "note": "gate=source_confirmed/antacid_draft_confirmed + 적대검증 통과 후보. PM 승인·source 재확인 전 통합 금지.",
                 "created_at": meta["run_at"]},
        "draft_candidates": drafts,
    }
    json.dump(draft_doc, open(os.path.join(QUEUE, "draft_candidates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    pm_md = build_pm_queue_md(sc_results, holds, rejects, already, kpi_rows, meta)
    open(os.path.join(QUEUE, "pm_review_queue.md"), "w", encoding="utf-8").write(pm_md)
    json.dump(meta, open(os.path.join(QUEUE, "run_meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("=== harvest_relation_bot_v1_3 ===")
    print(f"mode: {meta['mode']} | SDK stats: {client.stats}")
    print(f"harvest: {len(cands)} | source-check: {len(sc_results)} "
          f"(draft {len(drafts)} / needs_review {len(needs)} / reject {len(sc_reject)})")
    print(f"precheck: already {len(already)} / hold {len(holds)} / rejected {len(rejects)} | KPI scan {len(kpi_rows)}")
    print(f"live relations created: 0 | live promotions: 0 | deploy: none")
    if log:
        print(f"fetch errors: {len(log)}")
    print(f"[write] {os.path.relpath(QUEUE, REPO)}/  (7 artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
