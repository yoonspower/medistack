#!/usr/bin/env python3
"""
build_relation_factory_inventory_v1_4.py
MediStack Relation Factory Bot v1.4 — 중복 방지 인벤토리 빌더(읽기전용·네트워크 0).

live/pending/draft/needs_review/hold/reject 를 모두 읽어 (drug, counterpart) 정규화 dedup 키 +
카테고리별 ledger 를 만든다. relation_factory_bot_v1_4 가 candidate 중복 차단에 재사용.
산출(둘 다 data/review·docs): relation_factory_inventory_v1_4.json · MediStack_relation_factory_inventory_v1_4.md
실제 export/full index/aliases/src 무수정. live 승격 0.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
REVIEW = os.path.join(DATA, "review")
DRAFTS = os.path.join(DATA, "drafts")
OUT_JSON = os.path.join(REVIEW, "relation_factory_inventory_v1_4.json")
OUT_MD = os.path.join(REPO, "docs", "MediStack_relation_factory_inventory_v1_4.md")

# counterpart 정규화 — 같은 영양소/약물카테고리는 한 토큰으로(철분/철/철제 → fe 등).
COUNTERPART_CANON = [
    ("fe", ["철분", "철제", "황산철", "구연산제일철", "철·아연", "철ㆍ아연", "철 ", "철,", "iron"]),
    ("ca", ["칼슘", "calcium"]),
    ("mg", ["마그네슘", "magnesium"]),
    ("zn", ["아연", "zinc"]),
    ("al", ["알루미늄", "aluminum", "aluminium"]),
    ("k", ["칼륨", "potassium"]),
    ("na", ["나트륨", "sodium"]),
    ("b12", ["b12", "비타민b12", "코발라민", "시아노코발라민"]),
    ("b6", ["b6", "비타민b6", "피리독신"]),
    ("folate", ["엽산", "폴산", "folate", "folic"]),
    ("vitd", ["비타민d", "비타민 d", "vitamind"]),
    ("fatsol_vit", ["지용성비타민", "지용성 비타민", "a·d·e·k", "a,d,e,k", "fat-soluble", "fat soluble"]),
    ("al_mg_antacid", ["al/mg", "al·mg", "제산제", "antacid", "수산화마그네슘", "수산화알루미늄"]),
    ("acid_reducing_drug", ["h2", "ppi", "프로톤펌프", "양성자펌프", "산분비억제", "acid_reducing", "제산제·h2"]),
]


def canon_counterpart(s):
    low = (s or "").lower().replace(" ", "")
    for tok, keys in COUNTERPART_CANON:
        for k in keys:
            if k.replace(" ", "").lower() in low:
                return tok
    return low[:24] or "?"


def canon_drug(s):
    """약물명 → 정규화 토큰: 염/수화물/제형 접미 제거 + 소문자."""
    t = (s or "").strip()
    t = re.sub(r"\s+", "", t)
    # 흔한 염·수화물 접미 제거
    for suf in ["염산염수화물", "나트륨수화물", "염산염", "수화물", "나트륨", "칼륨", "황산염",
                "말레산염", "푸마르산염", "토실산염", "메실산염", "베실산염", "이나트륨"]:
        t = t.replace(suf, "")
    return t.lower() or "?"


def key(drug, counterpart):
    return f"{canon_drug(drug)}|{canon_counterpart(counterpart)}"


def _load(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def main():
    inv = {
        "meta": {
            "name": "relation_factory_inventory_v1_4",
            "purpose": "Relation Factory v1.4 중복방지 인벤토리(읽기전용). live/pending/draft/needs_review/hold/reject 통합.",
            "live_relations": 0, "do_not_implement_yet": True, "live_integration_forbidden": True,
        },
        "live_pairs": [], "pending_reviewer_gated": {}, "source_confirmed_draft": [],
        "needs_review": [], "hold": [], "reject": [], "no_domestic_product": [],
        "high_risk_permanent_hold": [], "dedup_keys": [],
    }
    keys = set()

    def add(bucket, drug, counterpart, src, extra=None):
        rec = {"drug": drug, "counterpart": counterpart, "key": key(drug, counterpart), "src": src}
        if extra:
            rec.update(extra)
        inv[bucket].append(rec)
        keys.add(rec["key"])

    # 1) live export
    exp = _load(os.path.join(DATA, "medistack_v0.2_beta_export.json"))
    for r in (exp.get("relations", []) if exp else []):
        nut = r.get("nutrient") or r.get("counterpart_category") or "?"
        add("live_pairs", r.get("ingredient", "?"), nut, f"live id{r.get('id')}",
            {"id": r.get("id"), "counterpart_category": r.get("counterpart_category")})
    inv["meta"]["live_relations"] = len(inv["live_pairs"])

    # 2) pending reviewer-gated
    pend = {"penicillamine": [], "theme_map": [], "potassium": [], "at_fex": []}
    tm = _load(os.path.join(DRAFTS, "theme_map_draft_batch_v1_3.json"))
    for d in (tm.get("drafts", []) if tm else []):
        cid = d.get("candidate_id", "")
        bucket = "penicillamine" if "CHEL" in cid else "theme_map"
        pend[bucket].append(cid)
        add("pending_penmark", d.get("drug_ingredient", "?"), d.get("counterpart", "?"),
            f"pending {cid}") if False else None
        keys.add(key(d.get("drug_ingredient", "?"), d.get("counterpart", "?")))
    pot = _load(os.path.join(REVIEW, "potassium_depletion_pm_ready_v1_2.json"))
    POT_WL = {"DF01", "DF04", "DF05", "DF-PRED-01"}
    for it in (pot.get("items", []) if pot else []):
        did = it.get("draft_id") or it.get("id") or ""
        if did in POT_WL:
            pend["potassium"].append(did)
            keys.add(key(it.get("drug_ingredient") or it.get("ingredient", "?"), "칼륨"))
    fex = _load(os.path.join(DRAFTS, "antacid_interaction_draft_batch_v1_2.json"))
    for d in (fex.get("draft_relations", []) if fex else []):
        ing = d.get("drug_ingredient") or d.get("ingredient", "?")
        if "펙소페나딘" in ing:
            pend["at_fex"].append(d.get("candidate_id") or "AT-FEX")
        keys.add(key(ing, d.get("counterpart") or "al_mg_antacid"))
    inv["pending_reviewer_gated"] = {k: sorted(set(v)) for k, v in pend.items()}

    # 3) reject/hold ledger — 확정 사실(docs/메모리 근거). 재후보화 금지.
    # 세파계 × 철분 10종 reject(한국 허가사항 미기재) — 약물명 토큰만 기록.
    CEPH_FE_REJECT = ["세파클러", "세파드록실", "세팔렉신", "세픽심", "세프카펜", "세프디니르",
                      "세프테람", "세프포독심", "세프록심", "세프디토렌"]
    for d in CEPH_FE_REJECT:
        add("reject", d, "철분", "cephalosporin×Fe 한국 라벨 미기재 reject(재후보화 금지)",
            {"reason": "label_not_found_confirmed"})
    # 미유통 다이유레틱 8건(loop/thiazide × 칼륨) — not_marketed_kr
    NOT_MARKETED = ["부메타니드", "피레타니드", "메토라존", "트리클로르메티아지드", "벤드로플루메티아지드"]
    for d in NOT_MARKETED:
        add("no_domestic_product", d, "칼륨", "loop/thiazide not_marketed_kr(searchDrug 0)",
            {"reason": "not_marketed_kr"})
    # K-sparing × 칼륨 — depletion 절대 금지(상승 방향). high-risk permanent hold.
    for d in ["스피로노락톤", "에플레레논", "아밀로라이드", "트리암테렌"]:
        add("high_risk_permanent_hold", d, "칼륨",
            "K-sparing: 칼륨 상승 방향 → depletion 카드 금지", {"reason": "k_raising_not_depletion"})
    # SGLT2 × Mg / thiazide × 칼슘 방향 민감 — hold
    for d in ["다파글리플로진", "엠파글리플로진", "이프라글리플로진"]:
        add("hold", d, "마그네슘", "SGLT2×Mg 방향 민감 hold(라벨 직접근거 필요)", {"reason": "weak_signal"})
    # warfarin × vitamin K — clinical judgment, 영구 제외(antagonism)
    add("high_risk_permanent_hold", "와파린", "비타민K",
        "항응고×비타민K: 임상판단(antagonism) — reviewer 전 제외", {"reason": "anticoagulant_clinical"})

    # 4) theme_map_expansion hold 들(reaffirmed) — 재후보화 금지
    tme = _load(os.path.join(REVIEW, "theme_map_expansion_candidates_v1_3.json"))
    for h in (tme.get("reaffirmed_existing_holds_out_of_scope", []) if tme else []):
        if isinstance(h, dict):
            add("hold", h.get("drug") or h.get("ingredient", "?"),
                h.get("counterpart", "?"), "theme_map_expansion reaffirmed hold",
                {"reason": h.get("reason", "out_of_scope")})

    inv["dedup_keys"] = sorted(keys)
    inv["meta"]["dedup_key_count"] = len(keys)
    inv["meta"]["counts"] = {b: len(inv[b]) for b in
                             ("live_pairs", "source_confirmed_draft", "needs_review", "hold",
                              "reject", "no_domestic_product", "high_risk_permanent_hold")}

    os.makedirs(REVIEW, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # markdown
    pend_g = inv["pending_reviewer_gated"]
    md = [
        "# MediStack — Relation Factory v1.4 중복방지 인벤토리",
        "",
        "> 읽기전용 통합(live/pending/draft/needs_review/hold/reject). `relation_factory_bot_v1_4` 가 candidate 중복 차단에 사용.",
        f"> 정본 JSON `data/review/relation_factory_inventory_v1_4.json` · dedup 키 **{len(keys)}**개. live 승격 0.",
        "",
        "## 1. live relations",
        f"- live pairs: **{inv['meta']['live_relations']}** (id1~61, count 60)",
        "",
        "## 2. pending reviewer-gated (live 미존재)",
        f"- 페니실라민: {pend_g.get('penicillamine')}",
        f"- theme map: {pend_g.get('theme_map')}",
        f"- 칼륨 PM-ready: {pend_g.get('potassium')}",
        f"- AT-FEX: {pend_g.get('at_fex')}",
        "",
        "## 3. reject / no_domestic_product / high-risk hold (재후보화 금지)",
        f"- reject(세파계×철분 등): {len(inv['reject'])}",
        f"- no_domestic_product(미유통 다이유레틱): {len(inv['no_domestic_product'])}",
        f"- high-risk permanent hold(K-sparing·warfarin×vitK): {len(inv['high_risk_permanent_hold'])}",
        f"- hold(약신호 약함): {len(inv['hold'])}",
        "",
        "## 4. dedup 정책",
        "- 키 = `canon_drug(약물)|canon_counterpart(상대)`. 염/수화물/제형 접미 제거 + counterpart 정규화(철분/철→fe 등).",
        "- candidate 가 이 키 집합과 충돌하면 REJECT_PRECHECK(중복) 또는 HOLD(상대 카테고리만 충돌).",
        "- **계열 일반화 금지**: reject/hold 는 약물별 확정 — 같은 계열이라도 미확정 품목은 source-check 후보로만.",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"inventory: live {inv['meta']['live_relations']} · dedup keys {len(keys)} · "
          f"reject {len(inv['reject'])} · no_domestic {len(inv['no_domestic_product'])} · "
          f"highrisk_hold {len(inv['high_risk_permanent_hold'])}")
    print(f"  → {os.path.relpath(OUT_JSON, REPO)} · {os.path.relpath(OUT_MD, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
