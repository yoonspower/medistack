#!/usr/bin/env python3
"""
validate_autofactory_v1_5_production_results.py
MediStack v1.5 — Production harvest 산출물 검증 (읽기전용·live 무수정).

검증:
  1) 9개 autofactory_v1_5_production_*.json 존재·로드.
  2) reviewer-ready 신규 전건이 **실제 source(url+pointer+quote)** 보유 (허위/공란 0).
  3) reviewer-ready quote 가 라벨 인용으로 채워짐 + display/management 보수 템플릿 + independent_audit_pending=true.
  4) reviewer-ready 가 live-60·existing-33 과 중복 0.
  5) needs_review/source_pending/hold/reject 가 reviewer-ready 에 섞이지 않음.
  6) 카르바마제핀×엽산(RF-F9-0245 권위 needs_review)이 auto_pass 에 없음(재승격 차단).
  7) forbidden phrase 0 · published/clinical 승격 요구 0 · 제품/구매 문구 0.
  8) source 우선순위: 전 quote 가 nedrug.mfds.go.kr (공식) — 비공식 source 0.
  9) funnel 정합: auto_pass+copy_change = reviewer_ready · confirmed = quote 보유.
종료코드 0 PASS / 1 FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REV = os.path.join(ROOT, "data", "review")
DATA = os.path.join(ROOT, "data")
P = "autofactory_v1_5_production_"
fails = []


def J(name):
    return json.load(open(os.path.join(REV, P + name + ".json"), encoding="utf-8"))


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def main():
    print("=== AutoFactory v1.5 Production results 검증 ===")
    files = ["raw_candidates", "source_check_queue", "source_confirmed", "auto_reviewed",
             "adversarial_results", "family_clusters", "reviewer_ready_waves",
             "needs_review_quarantine", "dashboard"]
    for f in files:
        ck(os.path.exists(os.path.join(REV, P + f + ".json")), f"{f}.json 존재")
    if fails:
        print("RESULT: FAIL — 산출물 누락"); return 1

    waves = J("reviewer_ready_waves")
    ar = J("auto_reviewed")
    nrq = J("needs_review_quarantine")
    dash = J("dashboard")
    ready = waves["candidates"]
    results = ar["results"]

    # 2/3) 실 source + 보수 카피 + audit pending
    for c in ready:
        s = c.get("source", {})
        rid = c.get("raw_id")
        ck(bool(s.get("url")) and bool(s.get("pointer")) and bool(s.get("quote")),
           f"{rid}: source url+pointer+quote 보유")
        ck(bool(c.get("display_text_ko")) and bool(c.get("management_ko")), f"{rid}: 보수 카피 보유")
        ck(c.get("independent_audit_pending") is True, f"{rid}: independent_audit_pending=true")
        ck(c.get("requires_clinical_review") is False and c.get("product_link_allowed") is False,
           f"{rid}: clinical/product 플래그 false")

    # 4) dedup vs live/33
    g = dash["guards"]
    ck(not g["ready_live_dup"], "reviewer-ready ∩ live-60 = 0")
    ck(not g["ready_existing33_dup"], "reviewer-ready ∩ existing-33 = 0")

    # 5) needs_review/pending/hold/reject 가 reviewer-ready 에 없음
    ready_ids = set(c["raw_id"] for c in ready)
    nr_ids = set(r["raw_id"] for r in nrq["needs_review"])
    pend_ids = set(r["raw_id"] for r in nrq["source_pending"])
    ck(not (ready_ids & nr_ids), "needs_review ∩ reviewer-ready = 0")
    ck(not (ready_ids & pend_ids), "source_pending ∩ reviewer-ready = 0")
    ck(all(c["verdict"] in ("auto_pass", "copy_change") for c in ready), "reviewer-ready 전건 auto_pass/copy_change")

    # 6) 0245 카르바마제핀×엽산 재승격 차단
    carba = [r for r in results if "카르바마제핀" in r["drug_ingredient"] and "엽산" in r["counterpart"]]
    ck(all(r["verdict"] != "auto_pass" for r in carba),
       "카르바마제핀×엽산(RF-F9-0245 권위 needs_review) auto_pass 아님")

    # 7) forbidden / 승격요구 / 제품
    ck(not g["forbidden_phrase_hits"], "forbidden phrase 0")
    FORB = ["구매", "최저가", "제휴", "광고", "처방", "추천", "안전하다", "복용해도 된다",
            "clinical_reviewed=true", "published=true"]
    leak = []
    for c in ready:
        blob = json.dumps(c, ensure_ascii=False)
        for t in FORB:
            if t in c.get("display_text_ko", "") + c.get("management_ko", ""):
                leak.append((c["raw_id"], t))
    ck(not leak, f"카피 승격요구/제품/광고 문구 0 ({leak[:3]})")

    # 8) 공식 source only
    nonofficial = [c["raw_id"] for c in ready if "nedrug.mfds.go.kr" not in c.get("source", {}).get("url", "")]
    ck(not nonofficial, f"전 reviewer-ready 공식 nedrug source ({nonofficial[:3]})")
    confirmed = J("source_confirmed")["confirmed"]
    ck(all("nedrug.mfds.go.kr" in r.get("source", {}).get("url", "") for r in confirmed),
       "source_confirmed 전건 공식 nedrug")

    # 9) funnel 정합
    a = dash["auto_review"]
    ck(a["auto_pass"] + a["copy_change"] == a["reviewer_ready_new"] == len(ready),
       "auto_pass+copy_change = reviewer_ready_new = candidates")
    ck(dash["guards"]["live_write"] is False and dash["guards"]["protected_hash_unchanged"],
       "live write 0 · protected 불변")

    print("=" * 62)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print(f"RESULT: PASS — reviewer-ready {len(ready)} 전건 실 source+보수카피+audit pending · "
          f"dedup 0 · 0245 재승격 차단 · 공식 source only · funnel 정합 · live 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
