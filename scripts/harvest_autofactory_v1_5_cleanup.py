#!/usr/bin/env python3
"""
harvest_autofactory_v1_5_cleanup.py
MediStack AutoFactory v1.5 — needs_review / source_pending **cleanup 재harvest** (실 MFDS · NO-LIVE-WRITE).

production harvest 는 약물당 라벨 1개만 보고 quote 를 못 찾으면 source_pending 으로 떨어뜨렸다. cleanup 은:
  - 약물당 **여러 itemSeq** 라벨을 fetch(완제/정상 상위 N) → broaden 한 토큰으로 verbatim quote 재탐색
  - production 의 검증된 classify()(F3 미네랄-제산제 트랩·F9 임신맥락 가드 포함) 재사용
  - 기존 needs_review 4(에티드론산 0148/0149·카르바마제핀 0245·케토코나졸 0275)도 정밀 재검
허위 인용 0 · source 없는 후보 승격 0 · live/protected 무수정.

산출: data/review/autofactory_v1_5_cleanup_{reviewed,source_confirmed,reviewer_ready,still_needs_review,hold_reject}.json
      + audit 입력용 candidate 목록(이후 adversarial workflow 가 독립 검증).
종료코드 0 PASS / 1 FAIL.
"""
import argparse
import hashlib
import importlib.util
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

PROTECTED = ["medistack_v0.1_beta_export.json", "medistack_v0.2_beta_export.json",
             "medistack_v0.3_aliases.json", "full_drug_name_index_sample_v1_0.json"]
OUT = "autofactory_v1_5_cleanup_"
RUN_DATE = "2026-06-17"


def _load_prod():
    spec = importlib.util.spec_from_file_location(
        "prodh", os.path.join(HERE, "harvest_autofactory_v1_5_production.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def snap():
    return {f: (sha(os.path.join(DATA, f)) if os.path.exists(os.path.join(DATA, f)) else "<MISSING>")
            for f in PROTECTED}


def J(p):
    return json.load(open(p, encoding="utf-8"))


def find_quote_broad(prod, label, cp_canon):
    """production find_quote + b12/vitd 흡수 기전 broaden(산분비억제제 B12 흡수저하 등 포착)."""
    q = prod.find_quote(label, cp_canon)
    if q:
        return q
    # broaden: b12/vitd 흡수 기전(production MECH_DEP 에 '흡수' 없음)
    if cp_canon in ("b12", "vitd", "folate"):
        toks = prod.CP_TOKENS[cp_canon]
        for sent in prod.split_sentences(label):
            if any(t in sent for t in toks) and any(m in sent for m in ["흡수가 저하", "흡수 저하", "흡수를 저해", "흡수가 저해", "흡수율"]):
                if len(sent) > 320:
                    idx = min((sent.find(t) for t in toks if t in sent), default=0)
                    sent = sent[max(0, idx - 80): idx + 160].strip()
                return sent
    return None


def main():
    ap = argparse.ArgumentParser(description="AutoFactory v1.5 cleanup re-harvest")
    ap.add_argument("--max-items-per-drug", type=int, default=4, help="약물당 fetch 할 itemSeq 상한")
    ap.add_argument("--max-runtime-minutes", type=int, default=120)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache-dir", default="/tmp/afprod/cache")
    ap.add_argument("--fail-on-protected-change", action="store_true", default=True)
    args = ap.parse_args()

    prod = _load_prod()
    from medistack_sdk.nedrug_client import NedrugClient
    os.makedirs(args.cache_dir, exist_ok=True)
    raw_dir = os.path.join(os.path.dirname(args.cache_dir), "raw")
    os.makedirs(raw_dir, exist_ok=True)
    client = NedrugClient(cache_dir=args.cache_dir, raw_dir=raw_dir,
                          log_path=os.path.join(os.path.dirname(args.cache_dir), "log_cleanup.jsonl"),
                          offline=args.offline)

    before = snap()
    nrq = J(os.path.join(REV, "autofactory_v1_5_production_needs_review_quarantine.json"))
    live = J(os.path.join(DATA, "medistack_v0.2_beta_export.json"))
    plan = J(os.path.join(REV, "reviewer_ready_global_plan_v1_4.json"))
    live_pairs = set((r.get("ingredient"), r.get("nutrient")) for r in live["relations"])
    existing33 = set((e["projected_live_relation"]["ingredient"], e["projected_live_relation"]["nutrient"])
                     for e in plan["combined_projected_entries"])

    # cleanup 대상 = production needs_review 16 + source_pending 147 + 기존 needs_review 4
    targets = []
    for r in nrq["needs_review"] + nrq["source_pending"]:
        targets.append({"drug_ingredient": r["drug_ingredient"], "counterpart": r["counterpart"],
                        "counterpart_canon": r.get("counterpart_canon") or _canon_of(r["counterpart"]),
                        "family": r["family"], "prior": "production_needs_review" if r in nrq["needs_review"] else "source_pending",
                        "prior_reason": r.get("verdict_reason")})
    EXISTING4 = [("에티드론산", "칼슘", "ca", "F3", "RF-F3-0148"), ("에티드론산", "철분", "fe", "F3", "RF-F3-0149"),
                 ("카르바마제핀", "엽산", "folate", "F9", "RF-F9-0245"), ("케토코나졸", "Al/Mg 함유 제산제(약물)", "al_mg_antacid", "F10", "RF-F10-0275")]
    for d, cp, canon, fam, rid in EXISTING4:
        targets.append({"drug_ingredient": d, "counterpart": cp, "counterpart_canon": canon,
                        "family": fam, "prior": "existing_needs_review", "prior_id": rid})

    print("=== AutoFactory v1.5 CLEANUP re-harvest (real MFDS · NO-LIVE-WRITE) ===")
    print(f"offline={args.offline} targets={len(targets)} (prod_nr 16 + source_pending {len(nrq['source_pending'])} + existing 4) "
          f"max_items/drug={args.max_items_per_drug}")

    t0 = time.time()
    deadline = t0 + args.max_runtime_minutes * 60
    # 약물별 itemSeq 후보 캐시
    drug_items = {}
    reviewed = []
    fetch_count = 0

    for tg in targets:
        if time.time() > deadline:
            tg["verdict"] = "still_needs_review"; tg["verdict_reason"] = "runtime_budget_reached"; reviewed.append(tg); continue
        drug, cp_canon = tg["drug_ingredient"], tg["counterpart_canon"]
        if cp_canon is None:
            tg["verdict"] = "still_needs_review"; tg["verdict_reason"] = "unknown_counterpart"; reviewed.append(tg); continue
        # itemSeq 후보 수집(약물 1회)
        if drug not in drug_items:
            try:
                rows = client.search_drug(drug, max_pages=1)
                seqs = [(r.item_seq, r.item_name) for r in rows
                        if getattr(r, "finished", "") == "완제의약품" and getattr(r, "status_cancel", "") == "정상"]
                drug_items[drug] = seqs[:args.max_items_per_drug] if seqs else [(r.item_seq, r.item_name) for r in rows][:args.max_items_per_drug]
            except Exception:
                drug_items[drug] = []
        # 여러 라벨에서 best quote 탐색
        best = None; best_seq = ""; best_name = ""; best_url = ""
        for seq, name in drug_items[drug]:
            if time.time() > deadline:
                break
            try:
                label, url = client.fetch_label(seq)
                fetch_count += 1
            except Exception:
                label, url = "", ""
            if not label:
                continue
            q = find_quote_broad(prod, label, cp_canon)
            if q:
                # classify 로 pass 가능한 quote 를 우선 채택
                v, copy, reason = prod.classify(cp_canon, q, drug)
                if best is None or v in ("auto_pass", "copy_change"):
                    best, best_seq, best_name, best_url = q, seq, name, url
                if v in ("auto_pass", "copy_change"):
                    break
        # 최종 분류
        pair = (drug, tg["counterpart"])
        if pair in live_pairs:
            tg.update(verdict="reject", verdict_reason="live_exact_duplicate"); reviewed.append(tg); continue
        if pair in existing33:
            tg.update(verdict="reject", verdict_reason="existing_prepared_duplicate"); reviewed.append(tg); continue
        verdict, copy, reason = prod.classify(cp_canon, best, drug)
        mech = "depletion" if cp_canon in ("folate", "vitd", "b12") else "absorption"
        action = "monitoring" if mech == "depletion" else "separation"
        rec = {**tg, "mechanism": mech, "recommended_action": action, "evidence_level": "moderate",
               "verdict": verdict, "verdict_reason": reason, "labels_scanned": len(drug_items.get(drug, []))}
        if best:
            rec["source"] = {"type": "허가사항", "title": best_name, "url": best_url,
                             "pointer": f"식약처 nedrug getItemDetail / {drug} / itemSeq {best_seq} / 상호작용 / '{best}' / 확인일 {RUN_DATE}",
                             "quote": best, "claim_scope": "label_interaction"}
        if copy:
            rec.update(copy)
            rec["product_link_allowed"] = False
            rec["requires_clinical_review"] = False
            rec["independent_audit_pending"] = True
            rec["live_promotion_requires"] = ["independent_adversarial_audit", "clinical_reviewer_note"]
        # verdict 정규화: source_pending → still_needs_review(인용 미발견)
        if rec["verdict"] == "source_pending":
            rec["verdict"] = "still_needs_review"
            rec["verdict_reason"] = "no_supporting_quote_after_multi_label_search"
        reviewed.append(rec)
    elapsed = round(time.time() - t0, 1)

    def by(v):
        return [r for r in reviewed if r["verdict"] == v]
    auto_pass, copy_change = by("auto_pass"), by("copy_change")
    needs = by("needs_review") + by("still_needs_review")
    holds, rejects = by("hold"), by("reject")
    confirmed = [r for r in reviewed if r.get("source")]
    ready = auto_pass + copy_change

    # 가드
    FORB = ["구매", "최저가", "제휴", "광고", "처방", "추천", "안전하다", "복용해도 된다"]
    forbidden = []
    for r in ready:
        blob = r.get("display_text_ko", "") + r.get("management_ko", "")
        forbidden += [(r.get("raw_id") or f"{r['drug_ingredient']}×{r['counterpart']}", t) for t in FORB if t in blob]
    ready_pairs = [(r["drug_ingredient"], r["counterpart"]) for r in ready]
    live_dup = [p for p in ready_pairs if p in live_pairs]
    e33_dup = [p for p in ready_pairs if p in existing33]
    after = snap()
    protected_unchanged = before == after
    guard_ok = (protected_unchanged and not forbidden and not live_dup and not e33_dup
                and all(r.get("independent_audit_pending") for r in ready))

    # family clusters
    fam_ready = {}
    for r in ready:
        fam_ready.setdefault(r["family"], []).append(f"{r['drug_ingredient']}×{r['counterpart']}")

    def w(name, obj):
        json.dump(obj, open(os.path.join(REV, OUT + name + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    w("reviewed", {"meta": {"name": OUT + "reviewed", "reviewed": len(reviewed),
      "elapsed_seconds": elapsed, "label_fetches": fetch_count}, "results": reviewed})
    w("source_confirmed", {"meta": {"name": OUT + "source_confirmed", "count": len(confirmed)}, "confirmed": confirmed})
    w("reviewer_ready", {"meta": {"name": OUT + "reviewer_ready", "auto_pass": len(auto_pass),
      "copy_change": len(copy_change), "total": len(ready), "independent_audit_pending": True}, "candidates": ready})
    w("still_needs_review", {"meta": {"name": OUT + "still_needs_review", "count": len(needs)}, "items": needs})
    w("hold_reject", {"meta": {"name": OUT + "hold_reject"}, "hold": holds, "reject": rejects})

    print(f"  reviewed={len(reviewed)} confirmed={len(confirmed)} → auto_pass={len(auto_pass)} copy_change={len(copy_change)} "
          f"still_needs_review={len(needs)} hold={len(holds)} reject={len(rejects)}")
    print(f"  label_fetches={fetch_count} elapsed={elapsed}s")
    print(f"  guards: protected_unchanged={protected_unchanged} forbidden={len(forbidden)} live_dup={len(live_dup)} "
          f"e33_dup={len(e33_dup)} → {'OK' if guard_ok else 'FAIL'}")
    if args.fail_on_protected_change and not protected_unchanged:
        print("RESULT: FAIL — 보호셋 드리프트"); return 1
    if not guard_ok:
        print("RESULT: FAIL — 가드 위반"); return 1
    print(f"RESULT: PASS — cleanup reviewed {len(reviewed)} · mechanical reviewer-ready {len(ready)}(audit pending) · "
          f"source-confirmed {len(confirmed)} · live write 0 · protected 무수정")
    return 0


# counterpart 한글명 → canon (production CP 와 일치)
_CANON = {"철분": "fe", "칼슘": "ca", "마그네슘": "mg", "아연": "zn",
          "Al/Mg 함유 제산제(약물)": "al_mg_antacid", "엽산": "folate", "비타민D": "vitd", "비타민B12": "b12"}


def _canon_of(name):
    return _CANON.get(name)


if __name__ == "__main__":
    sys.exit(main())
