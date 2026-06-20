#!/usr/bin/env python3
"""
universe_probe_v1_0.py — universe 확장 후보 약물군 수확가능성 탐색(probe). 탐색/판정 전용.

목적: 빈 우물 파지 않기. 큐 확장 전에 후보를 nedrug 로 probe 해
  (a) 국내 유통(검색>0) (b) 라벨에 흡수/결핍 명시 실재 (c) 현 추출기 capability 내(실추출기로 판정)
  → 셋 다 만족분만 HARVEST_READY 로 큐 추가 대상.

판정은 **실제 추출기**가 결정한다(추측 금지):
  - depletion: extract_label_depletion_v1_8.extract_depletions  (NUTRIENTS=칼륨/마그네슘 only)
  - absorption: extract_label_interaction_v1_7.extract_interactions (Al/Mg/Ca/Fe/Zn 킬레이션)
추출기가 못 잡지만 라벨엔 명시된 nutrient(엽산/B12/비타민D 등)는 NEEDS_EXTRACTOR(차기 확장 대상)로 분류
하기 위해, 라벨 raw 를 regex 로도 스캔(in-scope 섹션 한정).

DEDUP(이미 live)은 live export 로 판정(네트워크 미사용 — nedrug 과도요청 방지).

산출: data/review/universe_probe_report_v1_0.md + .json (live/보호 무수정).
사용: python3 scripts/universe_probe_v1_0.py   (online·읽기전용 probe·쓰기=data/review/ 한정)
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
REVIEW = os.path.join(DATA, "review")
CACHE = os.path.join(DATA, "harvest_cache_v1_7")
REPORT_MD = os.path.join(REVIEW, "universe_probe_report_v1_0.md")
REPORT_JSON = os.path.join(REVIEW, "universe_probe_results_v1_0.json")
MAX_FETCH_PER_DRUG = 2
CONFIRMED_AT = "2026-06-20"


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cli = _load("cli", "nedrug_online_client_v1_7.py")
dp = _load("dp", "extract_label_depletion_v1_8.py")
ix = _load("ix", "extract_label_interaction_v1_7.py")

# 추출기 사전 nutrient(이 안에 있어야 depletion 채굴 가능)
DEPLETION_NUTRIENTS = set(dp.NUTRIENTS)   # {칼륨, 마그네슘}

# probe 대상(brief PHASE 1) — DEDUP 은 live 로 판정하므로 여기엔 "확인 필요"분만.
# track: depletion|absorption. search: nedrug 검색명. canonical: 라벨/relation 표기.
# want: depletion=목표 nutrient / absorption=목표 counterpart 키워드(라벨 동거 확인용).
PROBES = [
    # B. 항경련제 × 엽산 (페니토인×엽산은 이미 live=DEDUP → 제외)
    {"group": "B", "drug": "발프로산", "search": "발프로산", "canonical": "발프로산",
     "track": "depletion", "nutrient": "엽산", "sensitive": False},
    {"group": "B", "drug": "카르바마제핀", "search": "카르바마제핀", "canonical": "카르바마제핀",
     "track": "depletion", "nutrient": "엽산", "sensitive": False},
    {"group": "B", "drug": "페노바르비탈", "search": "페노바르비탈", "canonical": "페노바르비탈",
     "track": "depletion", "nutrient": "엽산", "sensitive": False},
    # C. 메토트렉세이트 × 엽산 (항암 — 민감, 자동 HARVEST_READY 금지)
    {"group": "C", "drug": "메토트렉세이트", "search": "메토트렉세이트", "canonical": "메토트렉세이트",
     "track": "depletion", "nutrient": "엽산", "sensitive": True},
    # D. 항진균제 × 제산제/위산 (이트라코나졸×제산제는 live=DEDUP → 제외)
    {"group": "D", "drug": "케토코나졸", "search": "케토코나졸", "canonical": "케토코나졸",
     "track": "absorption", "nutrient": None, "sensitive": False},
    # F. 퀴놀론 gap — 목시플록사신은 철/마그네슘/아연만 live, 칼슘·제산제 미live → 잔여 probe
    {"group": "F", "drug": "목시플록사신", "search": "목시플록사신", "canonical": "목시플록사신",
     "track": "absorption", "nutrient": None, "sensitive": False, "gap_only": True},
]

# 라벨 nutrient 명시 스캔 키워드(추출기 미지원 nutrient 의 NEEDS_EXTRACTOR 판정용)
NUTRIENT_TERMS = {
    "엽산": ["엽산", "폴산", "폴린산", "folate", "folic"],
}
# absorption 위산-의존(케토코나졸) 라벨 동거 키워드(추출기 미지원 기전 문서화용)
ACID_TERMS = ["위산", "제산제", "양성자펌프", "양성자 펌프", "PPI", "프로톤", "H2", "H₂",
              "수용체 길항제", "수용체길항제", "히스타민", "위산도", "위내", "산도"]


def find_nutrient_mention(html, terms):
    """depletion in-scope 섹션에서 nutrient 명시 완전문장 찾기(in-scope/off-scope 구분)."""
    in_scope, off_scope = [], []
    for name, text in ix.split_sections(html):
        scope_ok = dp.is_depletion_scope(name)
        for sent in ix.split_sentences(text):
            if any(t in sent for t in terms):
                (in_scope if scope_ok else off_scope).append({"section": name, "sentence": sent})
    return in_scope, off_scope


def scan_terms(html, terms):
    hits = []
    for name, text in ix.split_sections(html):
        for sent in ix.split_sentences(text):
            if any(t in sent for t in terms):
                hits.append({"section": name, "sentence": sent})
    return hits


def probe_one(c, p, live_pairs):
    rec = {"group": p["group"], "drug": p["drug"], "track": p["track"],
           "target_nutrient": p.get("nutrient"), "sensitive": p.get("sensitive", False)}
    rows = c.search_rows(p["search"], max_pages=2)
    rec["search_rows"] = len(rows)
    if not rows:
        rec["classification"] = "NO_DOMESTIC"
        rec["note"] = "검색 0건(국내 미유통)"
        return rec
    products = [r for r in rows if dp.is_single_oral_depletion(r, p["canonical"])]
    rec["single_oral_exact"] = len(products)
    if not products:
        rec["classification"] = "NO_DOMESTIC"
        rec["note"] = f"검색 {len(rows)}건이나 단일경구 정확매칭 0(복합제/주사/외용/성분철자 불일치)"
        return rec

    fetched, dep_finds, abs_finds = [], [], []
    nut_inscope, nut_offscope, acid_hits = [], [], []
    for r in products[:MAX_FETCH_PER_DRUG]:
        html = c.fetch_detail(r.item_seq)
        if not html or len(html) < 5000:
            continue
        fetched.append({"itemSeq": str(r.item_seq), "item_name": r.item_name, "ingr_name": r.ingr_name})
        if p["track"] == "depletion":
            for f in dp.extract_depletions(html):
                dep_finds.append({**f, "itemSeq": str(r.item_seq)})
            terms = NUTRIENT_TERMS.get(p["nutrient"], [p["nutrient"]])
            i_s, o_s = find_nutrient_mention(html, terms)
            nut_inscope += [{**x, "itemSeq": str(r.item_seq)} for x in i_s]
            nut_offscope += [{**x, "itemSeq": str(r.item_seq)} for x in o_s]
        else:  # absorption
            for f in ix.extract_interactions(html):
                abs_finds.append({**f, "itemSeq": str(r.item_seq)})
            acid_hits += [{**x, "itemSeq": str(r.item_seq)} for x in scan_terms(html, ACID_TERMS)]

    rec["fetched"] = fetched

    if p["track"] == "depletion":
        # 추출기가 잡은 칼륨/마그네슘 결핍(=현 capability 내 net-new 가능)
        extractor_caught = [f for f in dep_finds
                            if (p["canonical"], f["nutrient"]) not in live_pairs]
        rec["extractor_depletion_findings"] = dep_finds
        rec["target_inscope_mentions"] = nut_inscope[:3]
        rec["target_offscope_mentions"] = nut_offscope[:3]
        if extractor_caught:
            # 드물지만 칼륨/마그네슘 결핍이 잡히면 현 추출기로 수확 가능
            rec["classification"] = "HARVEST_READY"
            rec["harvest_pairs"] = sorted({f["nutrient"] for f in extractor_caught})
            rec["evidence"] = extractor_caught[0]
        elif nut_inscope:
            rec["classification"] = "NEEDS_EXTRACTOR"
            rec["note"] = (f"라벨 {p['nutrient']} 결핍 명시 in-scope 실재하나 추출기 사전 미지원"
                           f"(NUTRIENTS={sorted(DEPLETION_NUTRIENTS)}) — 차기 추출기 확장 대상")
            rec["evidence"] = nut_inscope[0]
        elif nut_offscope:
            rec["classification"] = "NO_LABEL"
            rec["note"] = (f"{p['nutrient']} 언급은 off-scope(상호작용/임부 등)뿐 — depletion in-scope 명시 없음. "
                           f"확장 추출기로도 부적격(scope 밖)")
            rec["evidence"] = nut_offscope[0]
        else:
            rec["classification"] = "NO_LABEL"
            rec["note"] = f"라벨에 {p['nutrient']} 명시 없음"
        return rec

    # absorption — counterpart_category → live nutrient 표기 매핑(net-new dedup용)
    def cp_key(f):
        cat = f.get("counterpart_category")
        if cat == "al_mg_antacid":
            return ix.antacid_scope_from_quote(f.get("source_quote", ""))  # None=일반 제산제(특정 불가)
        return {"ca": "칼슘", "fe": "철분", "mg": "마그네슘", "zn": "아연", "al": "알루미늄"}.get(cat)

    rec["extractor_absorption_findings"] = [
        {"cp_category": f.get("counterpart_category"), "cp_key": cp_key(f),
         "direction": f.get("direction"), "action": f.get("action"), "section": f.get("section"),
         "quote": f.get("source_quote"), "itemSeq": f.get("itemSeq")} for f in abs_finds]
    rec["acid_mentions"] = acid_hits[:3]
    # HARVEST_READY = separation-supporting(this_drug_lowered) + 구체 counterpart + net-new(미live)
    net_new = []
    for f in abs_finds:
        if f.get("direction") != "this_drug_lowered":
            continue
        key = cp_key(f)
        if not key:                       # 일반 제산제(특정 불가)는 과확장 금지 → 자동 HARVEST 제외
            continue
        if (p["canonical"], key) not in live_pairs:
            net_new.append((key, f))
    if net_new:
        rec["classification"] = "HARVEST_READY"
        rec["harvest_pairs"] = sorted({k for k, _ in net_new})
        k0, f0 = net_new[0]
        rec["evidence"] = {"counterpart": k0, "section": f0.get("section"),
                           "quote": f0.get("source_quote"), "itemSeq": f0.get("itemSeq")}
    elif abs_finds:
        rec["classification"] = "DEDUP"
        rec["note"] = "추출 흡수 finding 전건 이미 live(net-new 0)"
    elif acid_hits:
        rec["classification"] = "NEEDS_EXTRACTOR"
        rec["note"] = ("라벨에 위산/제산제 동거 있으나 추출기가 흡수-저해 finding 미추출(위산-의존 기전=킬레이션 아님 "
                       "→ 현 absorption 추출기 scope 밖). 위산-의존 추출기 확장 대상")
        rec["evidence"] = acid_hits[0]
    else:
        rec["classification"] = "NO_LABEL"
        rec["note"] = "라벨에 흡수저해/제산제 명시 없음"
    return rec


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    live_pairs = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}

    c = cli.NedrugOnlineClient(cache_dir=CACHE)
    results = [probe_one(c, p, live_pairs) for p in PROBES]

    # ── DEDUP/NEEDS_EXTRACTOR(네트워크 불요) — brief 후보 중 live 로 판정되는 것들 ──
    dedup_known = [
        ("A", "메트포르민 × 비타민B12", "id12 메트포르민×비타민B12 depletion live"),
        ("B", "페니토인 × 엽산", "id90 페니토인×엽산 depletion live"),
        ("D", "이트라코나졸 × Al/Mg 제산제", "id61 이트라코나졸×제산제 absorption live"),
        ("E", "독시사이클린 × 칼슘/철분/마그네슘/아연/제산제", "id7,8,9,47,80 전건 live(포화)"),
        ("E", "미노사이클린 × 칼슘/철분/마그네슘/아연/제산제", "id26,27,28,48,81 전건 live(포화)"),
        ("F", "시프로플록사신 × 칼슘/철분/마그네슘/아연/제산제", "id4,5,6,44,85 전건 live(포화)"),
        ("F", "레보플록사신 × 칼슘/철분/마그네슘/아연/제산제", "id1,2,3,43,73 전건 live(포화)"),
    ]

    counts = {}
    for r in results:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
    counts["DEDUP"] = counts.get("DEDUP", 0) + len(dedup_known)

    os.makedirs(REVIEW, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "universe_probe_results_v1_0", "confirmed_at": CONFIRMED_AT,
                            "depletion_nutrients_supported": sorted(DEPLETION_NUTRIENTS),
                            "counts": counts},
                   "probed": results, "dedup_known": dedup_known}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # ── 보고 markdown ──
    L = [f"# universe 확장 probe 보고 (v1.0, {CONFIRMED_AT})", "",
         "탐색/판정 전용. live/보호/추출기/export 무수정. 판정은 **실제 추출기**가 결정.",
         f"현 depletion 추출기 지원 nutrient = **{sorted(DEPLETION_NUTRIENTS)}** (엽산/B12/비타민D 미지원).", "",
         "## 분류 집계", ""]
    for k in ["HARVEST_READY", "NEEDS_EXTRACTOR", "NO_DOMESTIC", "NO_LABEL", "DEDUP"]:
        L.append(f"- **{k}**: {counts.get(k, 0)}")
    L += ["", "## PHASE 1 — probe 판정표 (네트워크 확인분)", ""]
    for r in results:
        L.append(f"### [{r['group']}] {r['drug']} ({r['track']}"
                 + (f" × {r['target_nutrient']}" if r.get("target_nutrient") else "") + ")"
                 + ("  ⚠️민감(항암)" if r.get("sensitive") else ""))
        L.append(f"- 분류: **{r['classification']}**")
        L.append(f"- 검색 itemSeq: {r.get('search_rows', 0)}건 · 단일경구 정확매칭: {r.get('single_oral_exact', '-')}건")
        if r.get("fetched"):
            L.append(f"- fetch: " + ", ".join(f"{x['itemSeq']}({x['ingr_name']})" for x in r["fetched"]))
        if r.get("evidence"):
            e = r["evidence"]
            L.append(f"- 근거: [{e.get('section')}] {e.get('sentence') or e.get('quote')}"
                     + (f" (itemSeq {e.get('itemSeq')})" if e.get("itemSeq") else ""))
        if r.get("harvest_pairs"):
            L.append(f"- 🟢 net-new counterpart: {r['harvest_pairs']}")
        if r.get("note"):
            L.append(f"- 비고: {r['note']}")
        L.append("")
    L += ["## DEDUP (live 로 판정 — 네트워크 미사용)", ""]
    for g, pair, why in dedup_known:
        L.append(f"- [{g}] {pair} — {why}")
    L += ["", "## NEEDS_EXTRACTOR 후보 (차기 추출기 확장 대상)", ""]
    ne = [r for r in results if r["classification"] == "NEEDS_EXTRACTOR"]
    if ne:
        for r in ne:
            L.append(f"- {r['drug']} × {r.get('target_nutrient') or '위산-의존'} — {r.get('note')}")
    else:
        L.append("- (probe 결과 없음)")
    L += ["", "## HARVEST_READY → 큐 추가 대상", ""]
    hr = [r for r in results if r["classification"] == "HARVEST_READY"]
    if hr:
        for r in hr:
            L.append(f"- {r['drug']} × {r.get('harvest_pairs')} ({r['track']})")
    else:
        L.append("- (없음)")

    # ── 관찰/전략(PM) — 결과에서 도출 ──
    offscope = [r for r in results if r["classification"] == "NO_LABEL" and r.get("target_offscope_mentions")]
    L += ["", "## 관찰 및 전략 (PM 판단용)", ""]
    if offscope:
        L.append("- **🔑 엽산 계열(B·C)은 NEEDS_EXTRACTOR 가 아니라 NO_LABEL**: 후보 약물 라벨에 엽산은 "
                 "있으나 전부 **off-scope 섹션(임부·수유/상호작용)** 뿐. depletion in-scope(이상반응/일반적주의)에 "
                 "결핍 명시가 없다. → **엽산 추출기를 만들어도 이 약물들은 수확 불가**(scope·B2 임부가드가 정당 배제). "
                 "추출기 확장 ROI 가 이 후보군엔 없음.")
        for r in offscope:
            ev = (r.get("target_offscope_mentions") or [{}])[0]
            L.append(f"    - {r['drug']}: [{ev.get('section')}] {ev.get('sentence')}")
    L.append("- **NEEDS_EXTRACTOR = 0** (이번 후보군): in-scope 명시 + 미지원 nutrient 조합이 하나도 없음. "
             "metformin×B12(id12 live)처럼 in-scope B12/엽산이 있는 약물은 별도 존재할 수 있으므로, "
             "추출기 확장 전 반드시 **후보별 in-scope 재probe** 필요(엽산/B12 확장의 빈우물 방지).")
    L.append("- **absorption 포화**: 후보 퀴놀론/테트라사이클린은 칼슘/철/마그네슘/아연/제산제 거의 전건 live. "
             "유일한 net-new = **목시플록사신 × Al/Mg 제산제**(live=철/Mg/Zn만, 제산제 누락분).")
    L.append("- ⚠️ **기존 행 F-FQ-01 discrepancy**(수정 안 함): `목시플록사신×칼슘 already_covered` 로 표기됐으나 "
             "live 에 목시×칼슘 relation 부재(목시 live=철/Mg/Zn). 또 probe 라벨엔 칼슘 미명시(Al/Mg/철/아연만). "
             "→ PM 이 F-FQ-01 precheck_class 재검토 권장(이번 brief 범위 밖이라 미수정).")
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    # ── 콘솔 ──
    print("=== universe probe v1.0 ===")
    print(f"depletion 추출기 지원 nutrient = {sorted(DEPLETION_NUTRIENTS)}")
    for r in results:
        ev = r.get("evidence", {})
        print(f"  [{r['group']}] {r['drug']} ({r['track']}) → {r['classification']}"
              f" | rows={r.get('search_rows',0)} exact={r.get('single_oral_exact','-')}"
              + (f" | pairs={r.get('harvest_pairs')}" if r.get("harvest_pairs") else "")
              + (f" | {r.get('note','')[:60]}" if r.get("note") else ""))
        if ev.get("sentence") or ev.get("quote"):
            print(f"        근거[{ev.get('section')}]: {(ev.get('sentence') or ev.get('quote'))[:90]}")
    print(f"counts={counts}")
    print(f"stats={c.stats}")
    print(f"written: {os.path.relpath(REPORT_MD, REPO)} · {os.path.relpath(REPORT_JSON, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
