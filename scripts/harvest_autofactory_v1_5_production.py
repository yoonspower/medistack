#!/usr/bin/env python3
"""
harvest_autofactory_v1_5_production.py
MediStack AutoFactory v1.5 — **Production harvest** (실제 MFDS 원문 source · NO-LIVE-WRITE).

orchestrator 의 offline funnel 과 달리 이 모듈은 SDK(medistack_sdk.nedrug_client)로 **실제 허가사항 라벨을
fetch** 하고, 라벨에 **실재하는 verbatim 인용**만으로 source pointer/quote 를 채운다.
허위 인용 0 · source 없는 후보 승격 0 · live/protected 무수정 · actual integration 0.

분류(refute-by-default):
  auto_pass      : 실 인용 + 개별 성분/counterpart 명확 + 기전 동사 + 보수 카피 가능 + live/33 dup 0
  copy_change    : 관계는 가능하나 카피 보수화 필요(remedy-only·stray marker·vitD reframe)
  needs_review   : 인용 모호 / counterpart 가 'antacid 함유 성분' 목록에 결속(F3 교훈) / '드물게' 저신호 열거(F9 0245)
  hold           : 정책민감 family(F5/F7/F8/F11)
  reject         : 인용 없음(source_pending 와 구분) / live dup / 방향 오류(K-sparing)
모든 machine auto_pass/copy_change 는 independent_audit_pending=true (auditor agent + reviewer note 전까지 live 금지).

사용:
  python3 scripts/harvest_autofactory_v1_5_production.py --max-drugs 100 --max-runtime-minutes 120
  python3 scripts/harvest_autofactory_v1_5_production.py --offline   # SDK fixtures(네트워크 0·테스트)
종료코드 0 PASS / 1 FAIL(가드 위반·보호셋 드리프트).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, ROOT)

UNIVERSE = os.path.join(REV, "relation_family_universe_v1_4.json")
GLOBAL_PLAN = os.path.join(REV, "reviewer_ready_global_plan_v1_4.json")
LIVE = os.path.join(DATA, "medistack_v0.2_beta_export.json")

PROTECTED = ["medistack_v0.1_beta_export.json", "medistack_v0.2_beta_export.json",
             "medistack_v0.3_aliases.json", "full_drug_name_index_sample_v1_0.json"]
HOLD_FAMILIES = {"F5", "F7", "F8", "F11"}
REJECT_DRUGS = {"스피로노락톤"}
RUN_DATE = "2026-06-17"
OUT = "autofactory_v1_5_production_"

# 보수 카피 템플릿(기존 live relation 과 동일 — source 보다 강하지 않음).
TPL_ABS_DISPLAY = ("이 약은 {n}과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 "
                   "있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요.")
TPL_ABS_MGMT = "{n}과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
TPL_DEP_DISPLAY = ("이 약을 장기간 복용할 때 {n} 수치 변화와 관련된 허가사항 문구가 있습니다. "
                   "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
TPL_DEP_MGMT = "정기적인 확인이 필요할 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
TPL_DEP_DISPLAY_REFRAME = ("이 약을 장기간 복용할 때 {n}와(과) 관련된 허가사항 주의 문구가 있습니다. "
                           "증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")

# counterpart 신호 토큰(라벨 인용 탐지용).
CP_TOKENS = {
    "fe": ["철분", "철 함유", "철·", "철, "], "ca": ["칼슘"], "mg": ["마그네슘"], "zn": ["아연"],
    "al_mg_antacid": ["제산제", "알루미늄", "마그네슘"],
    "folate": ["엽산"], "vitd": ["비타민 D", "비타민D", "콜레칼시페롤", "골연화", "구루병"],
    "b12": ["비타민 B12", "비타민B12", "시아노코발라민"],
}
MECH_ABS = ["흡수가 저하", "흡수 저하", "흡수가 저해", "흡수를 저해", "흡수가 줄", "흡수가 감소",
            "흡수에 영향", "킬레이트", "흡수율이 저하", "흡수가 방해"]
MECH_DEP = ["결핍", "엽산결핍", "저하", "감소", "보충"]
NUTRIENT_CANON = {"fe": "철분", "ca": "칼슘", "mg": "마그네슘", "zn": "아연",
                  "al_mg_antacid": "Al/Mg 함유 제산제(약물)",
                  "folate": "엽산", "vitd": "비타민D", "b12": "비타민B12"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def snap():
    return {f: (sha(os.path.join(DATA, f)) if os.path.exists(os.path.join(DATA, f)) else "<MISSING>")
            for f in PROTECTED}


def J(p):
    return json.load(open(p, encoding="utf-8"))


def split_sentences(text):
    # 라벨 텍스트를 문장 후보로 분할(다./줄바꿈/번호 항목).
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=다\.)\s|(?<=다\))\s|;\s|\n", text)
    return [p.strip() for p in parts if p.strip()]


def find_quote(label, cp_canon):
    """라벨에서 counterpart 토큰 + 기전 토큰을 모두 포함한 verbatim 문장을 찾는다. 없으면 None."""
    toks = CP_TOKENS[cp_canon]
    mech = MECH_DEP if cp_canon in ("folate", "vitd", "b12") else MECH_ABS
    best = None
    for sent in split_sentences(label):
        if any(t in sent for t in toks) and any(m in sent for m in mech):
            # 너무 긴 문단은 counterpart 주변으로 트림(±140자, 문장 경계 보존 시도)
            if len(sent) > 320:
                idx = min((sent.find(t) for t in toks if t in sent), default=0)
                sent = sent[max(0, idx - 80): idx + 160].strip()
            if best is None or len(sent) < len(best):
                best = sent
    return best


def classify(cp_canon, quote, drug):
    """refute-by-default 분류 + 보수 카피 생성. (verdict, copy, reason)"""
    if quote is None:
        return "source_pending", None, "no_supporting_quote"
    nut = NUTRIENT_CANON[cp_canon]
    low_signal = "드물게" in quote and not any(m in quote for m in ["흡수가 저하", "흡수 저하", "흡수가 저해", "결핍증을 일으"])
    if low_signal:
        return "needs_review", None, "low_signal_adverse_enumeration('드물게')"

    if cp_canon in ("fe", "ca", "mg", "zn"):
        # F3 교훈(refute-by-default): nutrient 가 '…함유[하는/된] 제산제' 구성성분으로만 등장하면
        # standalone 보충제 근거가 아님 → needs_review. live 패턴은 명시적 '철분 함유 제제'/'칼슘 함유 제제'.
        standalone_forms = [f"{nut} 함유 제제", f"{nut}함유 제제", f"{nut} 함유된 제제",
                            f"{nut} 보충제", f"{nut}보충제", f"{nut}제제", f"{nut} 함유 제제와"]
        standalone = any(f in quote for f in standalone_forms)
        # antacid 구성성분 결속 형태(트랩)
        antacid_bound = bool(re.search(r"(알루미늄|마그네슘|칼슘|아연|철분?)[^.]{0,25}함유[^.]{0,10}제산제", quote))
        if not standalone:
            return "needs_review", None, "counterpart_not_standalone_supplement(F3_lesson)"
        if antacid_bound and not standalone:
            return "needs_review", None, "counterpart_bound_to_antacid_composition(F3_lesson)"
        if not any(m in quote for m in MECH_ABS):
            return "needs_review", None, "no_absorption_mechanism_verb"
        return "auto_pass", {"display_text_ko": TPL_ABS_DISPLAY.format(n=nut),
                             "management_ko": TPL_ABS_MGMT.format(n=nut)}, "absorption_standalone"

    if cp_canon == "al_mg_antacid":
        if not any(m in quote for m in MECH_ABS):
            return "needs_review", None, "no_absorption_mechanism_verb"
        return "auto_pass", {"display_text_ko": TPL_ABS_DISPLAY.format(n=nut),
                             "management_ko": TPL_ABS_MGMT.format(n=nut)}, "antacid_absorption"

    if cp_canon in ("folate", "b12"):
        # F9 교훈: 임신/태아/기형 맥락의 결핍 언급은 '약물 유발 depletion' 이 아님 → needs_review.
        pregnancy_ctx = any(k in quote for k in ["임신", "임부", "태아", "기형", "수유", "임산부"])
        # 약물 귀인 + level-direction 명시(설파살라진/페니토인 live 패턴: '흡수가 저하', '혈청엽산치 저하')
        drug_attributed = any(k in quote for k in
                              [f"{nut}의 흡수가 저하", f"{nut} 흡수가 저하", "혈청엽산치 저하", "혈청 엽산치 저하",
                               f"{nut}결핍증을 일으", f"{nut} 결핍증을 일으", "병용투여 시 엽산의 흡수"])
        if pregnancy_ctx and not drug_attributed:
            return "needs_review", None, "pregnancy_context_not_drug_depletion(F9_lesson)"
        if not drug_attributed:
            return "needs_review", None, "depletion_drug_attribution_absent(F9_lesson)"
        return "auto_pass", {"display_text_ko": TPL_DEP_DISPLAY.format(n=nut),
                             "management_ko": TPL_DEP_MGMT}, "depletion_drug_attributed"

    if cp_canon == "vitd":
        # F9 vitD 교훈: 골연화/구루병 + 비타민D 투여(remedy) 만 있고 '비타민D 수치 저하' 미명시 → copy_change reframe
        explicit = any(k in quote for k in ["비타민D 저하", "비타민 D 저하", "25-hydroxy", "콜레칼시페롤의 감소", "비타민D의 감소"])
        if explicit:
            return "auto_pass", {"display_text_ko": TPL_DEP_DISPLAY.format(n=nut),
                                 "management_ko": TPL_DEP_MGMT}, "vitd_explicit_decrease"
        if any(k in quote for k in ["골연화", "구루병", "비타민D 투여", "비타민D를 투여", "비타민D 섭취"]):
            return "copy_change", {"display_text_ko": TPL_DEP_DISPLAY_REFRAME.format(n=nut),
                                   "management_ko": TPL_DEP_MGMT}, "vitd_remedy_reframe(F9_lesson)"
        return "needs_review", None, "vitd_level_direction_absent"

    return "needs_review", None, "unhandled_counterpart"


def main():
    ap = argparse.ArgumentParser(description="AutoFactory v1.5 production harvest (real MFDS source)")
    ap.add_argument("--max-drugs", type=int, default=200)
    ap.add_argument("--max-runtime-minutes", type=int, default=120)
    ap.add_argument("--families", default="")
    ap.add_argument("--exclude-families", default="")
    ap.add_argument("--offline", action="store_true", help="SDK fixtures 모드(네트워크 0)")
    ap.add_argument("--no-live-write", action="store_true", default=True)
    ap.add_argument("--fail-on-protected-change", action="store_true", default=True)
    ap.add_argument("--cache-dir", default="/tmp/afprod/cache")
    args = ap.parse_args()

    from medistack_sdk.nedrug_client import NedrugClient
    os.makedirs(args.cache_dir, exist_ok=True)
    raw_dir = os.path.join(os.path.dirname(args.cache_dir), "raw")
    os.makedirs(raw_dir, exist_ok=True)
    client = NedrugClient(cache_dir=args.cache_dir, raw_dir=raw_dir,
                          log_path=os.path.join(os.path.dirname(args.cache_dir), "log.jsonl"),
                          offline=args.offline)

    universe = J(UNIVERSE)
    plan = J(GLOBAL_PLAN)
    live = J(LIVE)
    before = snap()
    t0 = time.time()

    live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in live["relations"])
    existing33 = set()
    for e in plan["combined_projected_entries"]:
        rel = e["projected_live_relation"]
        existing33.add((rel["ingredient"], rel["nutrient"]))

    fams = set(f.strip() for f in args.families.split(",") if f.strip())
    excl = set(f.strip() for f in args.exclude_families.split(",") if f.strip())

    print("=== AutoFactory v1.5 PRODUCTION harvest (real MFDS · NO-LIVE-WRITE) ===")
    print(f"offline={args.offline} max_drugs={args.max_drugs} max_runtime={args.max_runtime_minutes}m")

    raw, queue, results = [], [], []
    label_cache = {}
    drugs_done = 0
    deadline = t0 + args.max_runtime_minutes * 60

    for fam in universe["families"]:
        fid = fam["id"]
        if fams and fid not in fams:
            continue
        if excl and fid in excl:
            continue
        hold_fam = fid in HOLD_FAMILIES or not fam.get("source_check", False)
        for drug in fam["drugs"]:
            if drugs_done >= args.max_drugs or time.time() > deadline:
                break
            label_text, label_url, item_seq, item_name = "", "", "", ""
            if not hold_fam and drug not in REJECT_DRUGS:
                try:
                    rows = client.search_drug(drug, max_pages=1)
                    pick = next((r for r in rows if getattr(r, "finished", "") == "완제의약품"
                                 and getattr(r, "status_cancel", "") == "정상"), rows[0] if rows else None)
                    if pick:
                        item_seq, item_name = pick.item_seq, pick.item_name
                        label_text, label_url = client.fetch_label(pick.item_seq)
                        label_cache[drug] = bool(label_text)
                except Exception as e:
                    label_text = ""
                drugs_done += 1
            for cp_canon in fam["counterparts"]:
                nut = NUTRIENT_CANON.get(cp_canon, cp_canon)
                rid = f"AFP-{fid}-{drug}-{cp_canon}"
                raw.append({"raw_id": rid, "family": fid, "drug_ingredient": drug,
                            "counterpart": nut, "counterpart_canon": cp_canon})
                pair = (drug, nut)
                # 분기
                if pair in live_pairs:
                    results.append({"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                                    "verdict": "reject", "reason": "live_exact_duplicate"})
                    continue
                if pair in existing33:
                    results.append({"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                                    "verdict": "existing_prepared", "reason": "in_existing_33"})
                    continue
                if drug in REJECT_DRUGS:
                    results.append({"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                                    "verdict": "reject", "reason": "k_sparing_direction"})
                    continue
                if hold_fam:
                    results.append({"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                                    "verdict": "hold", "reason": "policy_sensitive_family"})
                    continue
                # source-check 대상
                quote = find_quote(label_text, cp_canon) if label_text else None
                queue.append({"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                              "item_seq": item_seq, "label_fetched": bool(label_text),
                              "source_status": "source_confirmed" if quote else "source_pending_no_quote"})
                verdict, copy, reason = classify(cp_canon, quote, drug)
                mech = "depletion" if cp_canon in ("folate", "vitd", "b12") else "absorption"
                action = "monitoring" if mech == "depletion" else "separation"
                rec = {"raw_id": rid, "family": fid, "drug_ingredient": drug, "counterpart": nut,
                       "counterpart_canon": cp_canon, "counterpart_type": "drug" if cp_canon == "al_mg_antacid" else "nutrient",
                       "mechanism": mech, "recommended_action": action, "evidence_level": "moderate",
                       "verdict": verdict, "verdict_reason": reason}
                if quote:
                    rec["source"] = {
                        "type": "허가사항", "title": item_name, "url": label_url,
                        "pointer": f"식약처 nedrug getItemDetail / {drug} / itemSeq {item_seq} / 상호작용 / '{quote}' / 확인일 {RUN_DATE}",
                        "quote": quote, "claim_scope": "label_interaction"}
                if copy:
                    rec.update(copy)
                    rec["product_link_allowed"] = False
                    rec["requires_clinical_review"] = False
                    rec["independent_audit_pending"] = True
                    rec["live_promotion_requires"] = ["independent_adversarial_audit", "clinical_reviewer_note"]
                results.append(rec)
    elapsed = round(time.time() - t0, 1)

    # 집계
    def by(v):
        return [r for r in results if r["verdict"] == v]
    auto_pass, copy_change = by("auto_pass"), by("copy_change")
    needs_review = by("needs_review")
    hold, reject = by("hold"), by("reject")
    existing_prepared = by("existing_prepared")
    source_pending = [r for r in queue if r["source_status"].startswith("source_pending")]
    confirmed_new = [r for r in queue if r["source_status"] == "source_confirmed"]

    # forbidden phrase 가드(신규 카피)
    FORB = ["구매", "최저가", "제휴", "광고", "처방", "추천", "안전하다", "복용해도 된다", "치료해"]
    forbidden = []
    for r in auto_pass + copy_change:
        blob = r.get("display_text_ko", "") + r.get("management_ko", "")
        forbidden += [(r["raw_id"], t) for t in FORB if t in blob]

    # dedup 가드: 신규 reviewer-ready 가 live/33 과 중복 없음
    ready = auto_pass + copy_change
    ready_pairs = [(r["drug_ingredient"], r["counterpart"]) for r in ready]
    live_dup = [p for p in ready_pairs if p in live_pairs]
    e33_dup = [p for p in ready_pairs if p in existing33]

    after = snap()
    protected_unchanged = before == after

    # family clusters / waves
    fam_ready = {}
    for r in ready:
        fam_ready.setdefault(r["family"], []).append(r["raw_id"])
    waves = {f"prod_{fid}_{len(ids)}": {"family": fid, "candidate_ids": ids, "delta": len(ids),
             "independent_audit_pending": True} for fid, ids in fam_ready.items()}

    dashboard = {
        "meta": {"name": OUT + "dashboard", "run_date": RUN_DATE, "mode": "offline" if args.offline else "online",
                 "status": "NO-LIVE-WRITE · real-source · machine-classified(independent audit pending)",
                 "live_write_performed": False, "elapsed_seconds": elapsed,
                 "drugs_fetched": drugs_done, "labels_with_text": sum(1 for v in label_cache.values() if v)},
        "harvest": {"raw": len(raw), "source_check_queue": len(queue),
                    "source_confirmed_new": len(confirmed_new), "source_pending": len(source_pending),
                    "hold": len(hold), "reject": len(reject), "existing_prepared": len(existing_prepared)},
        "auto_review": {"auto_pass": len(auto_pass), "copy_change": len(copy_change),
                        "needs_review": len(needs_review), "hold": len(hold), "reject": len(reject),
                        "reviewer_ready_new": len(ready)},
        "source_fidelity": {
            "source_pointer_coverage": f"{len(confirmed_new)}/{len(queue)} (queue 중 실인용 보유)",
            "quote_coverage": len(confirmed_new),
            "official_source_ratio": "100% (식약처 nedrug 허가사항만)",
            "weak_source_excluded": "비공식/블로그/쇼핑몰 source 0건 사용(SDK 게이트웨이 단일 출처)",
            "family_generalization_blocked": "계열 일반화 0 — 약물별 라벨 직접 인용만 승격"},
        "scenario": {"existing_prepared": 33, "new_reviewer_ready": len(ready),
                     "combined_future_scenario": f"60→93 (existing) + new_ready({len(ready)})",
                     "duplicate_vs_live": len(live_dup), "duplicate_vs_existing33": len(e33_dup),
                     "needs_review_exclusion_from_ready": True},
        "guards": {"live_write": False, "protected_hash_unchanged": protected_unchanged,
                   "forbidden_phrase_hits": forbidden, "ready_live_dup": live_dup, "ready_existing33_dup": e33_dup,
                   "all_ready_independent_audit_pending": all(r.get("independent_audit_pending") for r in ready)},
        "clusters": {"by_family": {f: len(ids) for f, ids in fam_ready.items()}},
        "next": {"hand_to_auditor": OUT + "auto_reviewed.json / " + OUT + "adversarial_results.json",
                 "needs_review_cleanup": len(needs_review) + len(source_pending),
                 "recommended_next_live_wave": "auditor 통과분 + reviewer note 확보 후 per-family integrator",
                 "factory_v1_6_needed": len(source_pending) > 0},
    }

    guard_ok = (protected_unchanged and not forbidden and not live_dup and not e33_dup
                and all(r.get("independent_audit_pending") for r in ready))

    # emit (planning area only)
    def w(name, obj):
        json.dump(obj, open(os.path.join(REV, OUT + name + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    w("raw_candidates", {"meta": {"name": OUT + "raw_candidates", "count": len(raw)}, "candidates": raw})
    w("source_check_queue", {"meta": {"name": OUT + "source_check_queue", "count": len(queue),
      "source_confirmed": len(confirmed_new), "source_pending": len(source_pending)}, "queue": queue})
    w("source_confirmed", {"meta": {"name": OUT + "source_confirmed", "count": len(confirmed_new)},
      "confirmed": [r for r in results if r.get("source")]})
    w("auto_reviewed", {"meta": {"name": OUT + "auto_reviewed", "auto_pass": len(auto_pass),
      "copy_change": len(copy_change), "needs_review": len(needs_review)}, "results": results})
    w("adversarial_results", {"meta": {"name": OUT + "adversarial_results",
      "method": "refute-by-default machine self-audit (independent auditor agent 후속 필수)"},
      "auto_pass": [r["raw_id"] for r in auto_pass], "copy_change": [r["raw_id"] for r in copy_change],
      "demoted_needs_review": [{"raw_id": r["raw_id"], "reason": r["verdict_reason"]} for r in needs_review]})
    w("family_clusters", {"meta": {"name": OUT + "family_clusters"}, "by_family": {f: ids for f, ids in fam_ready.items()}})
    w("reviewer_ready_waves", {"meta": {"name": OUT + "reviewer_ready_waves", "new_reviewer_ready": len(ready),
      "existing_prepared": 33, "independent_audit_pending": True}, "waves": waves,
      "candidates": ready})
    w("needs_review_quarantine", {"meta": {"name": OUT + "needs_review_quarantine",
      "needs_review": len(needs_review), "source_pending": len(source_pending)},
      "needs_review": needs_review, "source_pending": source_pending})
    w("dashboard", dashboard)

    # 보고
    h = dashboard["harvest"]; a = dashboard["auto_review"]
    print(f"  raw={h['raw']} queue={h['source_check_queue']} confirmed_new={h['source_confirmed_new']} "
          f"pending={h['source_pending']} hold={h['hold']} reject={h['reject']} existing_prepared={h['existing_prepared']}")
    print(f"  auto_pass={a['auto_pass']} copy_change={a['copy_change']} needs_review={a['needs_review']} "
          f"→ reviewer_ready_new={a['reviewer_ready_new']} (independent audit pending)")
    print(f"  drugs_fetched={drugs_done} labels_with_text={dashboard['meta']['labels_with_text']} elapsed={elapsed}s")
    print(f"  guards: protected_unchanged={protected_unchanged} forbidden={len(forbidden)} "
          f"live_dup={len(live_dup)} e33_dup={len(e33_dup)} → {'OK' if guard_ok else 'FAIL'}")

    if args.fail_on_protected_change and not protected_unchanged:
        print("RESULT: FAIL — 보호셋 드리프트"); return 1
    if not guard_ok:
        print("RESULT: FAIL — 가드 위반"); return 1
    print(f"RESULT: PASS — 실 source harvest · 신규 reviewer-ready {len(ready)}(audit pending) · "
          f"source_pending {len(source_pending)} · live write 0 · protected 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
