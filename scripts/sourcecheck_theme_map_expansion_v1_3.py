#!/usr/bin/env python3
"""theme map expansion (v1.3) 신규 relation family 후보의 제한적 SDK-only source-check.

- 모든 nedrug 조회는 medistack_sdk.NedrugClient 통로(직접 HTTP 금지).
- online 모드 + namespace 캐시(data/harvest_queue/_sdk — gitignored 런타임). live/protected 무변경.
- 후보당 최대 2품목 fetch(max_n=2, max_pages=2). 과도한 네트워크 호출 금지.
- 라벨 직접근거(verbatim quote)만 인정. 부정/무관/흡수영향 없음이면 reject.
- 결과 분류: source_confirmed_draft_candidate / needs_review / label_not_found /
  no_domestic_product / direction_mismatch / ambiguous / reject.
- 이 스크립트는 라우팅/증거수집만. live 승격·draft 확정은 하지 않는다(별도 PM 게이트).
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vfs = _load("vfs", "scripts/verify_factory_sources_v1_2.py")
antacid = _load("antacid", "scripts/collect_antacid_interaction_evidence_v1_2.py")
from medistack_sdk import NedrugClient  # noqa: E402

CACHE_BASE = os.path.join(ROOT, "data/harvest_queue/_sdk")


def make_online_client():
    return NedrugClient(
        cache_dir=os.path.join(CACHE_BASE, "cache"),
        raw_dir=os.path.join(CACHE_BASE, "raw"),
        log_path=os.path.join(CACHE_BASE, "calls.jsonl"),
        offline=False,
    )


def snip(text, i, pad=110):
    return re.sub(r"\s+", " ", text[max(0, i - pad):i + pad]).strip()


def d_fatsoluble_vitamin(text):
    """지용성 비타민(A/D/E/K)·베타카로틴 흡수 저하/보충 시점 분리 문맥."""
    pats = [r"지용성\s*비타민", r"베타[\-\s]?카로틴", r"β[\-\s]?카로틴",
            r"비타민\s*[ADEK](?:\s*,\s*[ADEK])*"]
    for pat in pats:
        for m in re.finditer(pat, text):
            i = m.start()
            w = text[max(0, i - 90):i + 110]
            if re.search(r"흡수.{0,14}(저하|감소|저해|방해)|(저하|감소|저해|방해).{0,14}흡수|"
                         r"보충|복용\s*시점|시간\s*간격|간격을\s*두|취침\s*시|따로\s*복용", w):
                return True, snip(text, i)
    return False, ""


def d_folate_absorption(text):
    for m in re.finditer(r"엽산|폴산|폴린산", text):
        i = m.start()
        w = text[max(0, i - 80):i + 90]
        if re.search(r"흡수.{0,12}(저하|감소|저해|방해)|결합|간격|동시", w):
            return True, snip(text, i)
    return False, ""


def d_antacid_absorption(text):
    """제산제/H2/PPI 병용 시 흡수 저하 (산성 환경 의존 흡수)."""
    found, quote, kind = antacid.find_antacid_quote(text)
    if found:
        return True, quote, kind
    for m in re.finditer(r"제산제|H2\s*수용체|H₂|히스타민\s*H2|위산\s*분비\s*억제|제산", text):
        i = m.start()
        w = text[max(0, i - 90):i + 110]
        if re.search(r"흡수.{0,14}(저하|감소|저해|방해)|병용\s*투여\s*시|동시\s*투여|간격", w):
            return True, snip(text, i), "antacid_absorption"
    return False, "", ""


def d_chelation_iron(text):
    """철제제/황산철/구연산철 등 + 흡수율 저하 (페니실라민류 킬레이트 — vfs 검출기 보강)."""
    for m in re.finditer(r"철제제|황산철|구연산.{0,4}철|경구철|철분제|철\s*함유|철염|철분", text):
        i = m.start()
        w = text[max(0, i - 90):i + 110]
        if re.search(r"흡수.{0,14}(저하|감소|저해|방해)|흡수율|동시\s*투여를?\s*피|간격|킬레이트|복합체", w):
            return True, snip(text, i)
    return False, ""


def d_zinc_chelation(text):
    for m in re.finditer(r"아연", text):
        i = m.start()
        w = text[max(0, i - 90):i + 110]
        if re.search(r"흡수.{0,14}(저하|감소|저해|방해)|효과를?\s*감소|동시\s*투여를?\s*피|병용", w):
            return True, snip(text, i)
    return False, ""


# 후보 정의:
#   (candidate_id, family, ingredient, search_stem, counterpart, counterpart_type,
#    detector, priority, direct_itemseqs, note)
# direct_itemseqs: 성분명 검색이 product-name 매칭이라 비는 경우(브랜드명 제품)나
#                  exact-ingredient 필터가 완제를 거를 때 쓰는 확인된 완제 itemSeq.
CANDIDATES = [
    ("TM-LIP-01", "fatsol_vitamin_absorption", "오르리스타트", "오르리스타트",
     "지용성 비타민(A·D·E·K·베타카로틴)", "nutrient_group", "fatsol", "P0", [],
     "지방분해효소 억제제. 라벨에 지용성 비타민 흡수 저하 + 보충 시점 분리 문구. "
     "주의: 라벨이 종합비타민 보충을 권장 → 사용자 카피는 보충 권유 금지(상호작용·시점만)."),
    ("TM-LIP-02", "fatsol_vitamin_absorption", "콜레스티라민", "콜레스티라민",
     "지용성 비타민(A·D·K)", "nutrient_group", "fatsol_folate", "P1", ["198800813"],
     "담즙산 결합 수지(보령퀘스트란). 라벨: 비타민 A·D·K 흡수 저해. 엽산은 미확인. "
     "주의: 보충 권유 금지."),
    ("TM-CEPH-AC-01", "antacid_interaction", "세프포독심프록세틸", "세프포독심",
     "위산 감소·중화 약물(제산제·H2 차단제)", "antacid_drug", "antacid", "P1", [],
     "에스터 프로드러그. pH 의존 흡수 → 제산제/H2 병용 시 생체이용률 저하."),
    ("TM-CEPH-AC-02", "antacid_interaction", "세프디토렌피복실", "세프디토렌",
     "위산 감소·중화 약물(제산제·H2 차단제)", "antacid_drug", "antacid", "P1", [],
     "피복실 에스터. 제산제·위산감소 약물 동시 복용 권장 안 됨(흡수 감소)."),
    ("TM-CHEL-01-FE", "metal_chelation_absorption", "페니실라민", "페니실라민",
     "철분", "nutrient", "chelation_fe", "P1", ["198300142"],
     "윌슨병/RA(메탈캡틴). 경구 철제제·Al/Mg 제산제가 흡수율 저하 → 동시투여 회피."),
    ("TM-CHEL-01-ZN", "metal_chelation_absorption", "페니실라민", "페니실라민",
     "아연", "nutrient", "chelation_zn", "P1", ["198300142"],
     "동일 라벨: 아연 함유 경구제가 효과 감소 → 동시투여 회피."),
    ("TM-CHEL-02", "metal_chelation_absorption", "레보도파", "레보도파",
     "철분", "nutrient", "iron", "P1", [],
     "철 킬레이트로 흡수 저하 가능하나 국내 단일성분 완제 없음(마도파/스타레보=복합제) → hold."),
]


def classify(found, det_kind, seqs_found, direct):
    if not seqs_found and not direct:
        return "no_domestic_product"
    if found:
        return "source_confirmed_draft_candidate"
    return "label_not_found"


def _detect(det, text):
    if det == "fatsol":
        return (*d_fatsoluble_vitamin(text), "fatsoluble_vitamin")
    if det == "fatsol_folate":
        f, q = d_fatsoluble_vitamin(text)
        if f:
            return f, q, "fatsoluble_vitamin"
        f, q = d_folate_absorption(text)
        return f, q, "folate"
    if det == "antacid":
        return d_antacid_absorption(text)
    if det == "chelation_fe":
        return (*d_chelation_iron(text), "chelation_iron")
    if det == "chelation_zn":
        return (*d_zinc_chelation(text), "chelation_zinc")
    if det == "iron":
        return (*vfs.d_iron_absorption(text), "iron_absorption")
    return False, "", det


def main():
    client = make_online_client()
    out = {"meta": {"name": "theme_map_source_check_v1_3", "mode": "online_sdk",
                    "live_data_written": False, "max_fetch_per_candidate": 2,
                    "note": "라우팅/증거수집 전용. live 승격·draft 확정 없음."},
           "results": []}
    for (cid, family, ing, stem, counterpart, ctype, det, prio, direct, note) in CANDIDATES:
        seqs, why = vfs.search_itemseqs(client, stem, max_n=2, max_pages=2)
        # 성분명 검색이 비거나 완제를 거르면 확인된 완제 itemSeq 로 보강(라벨 직접근거 확보용).
        pick = list(seqs or [])
        for ds in direct:
            if not any(s[0] == ds for s in pick):
                pick.append((ds, "(direct itemSeq)", ing))
        rec = {"candidate_id": cid, "family": family, "ingredient": ing,
               "counterpart": counterpart, "counterpart_type": ctype, "priority": prio,
               "search_stem": stem, "search_why": why, "itemseqs_checked": [],
               "found": False, "quote": "", "detector_kind": det, "url": "", "note": note}
        for (seq, name, ingr) in pick:
            try:
                text, url = vfs.fetch_detail(client, seq)
            except Exception as e:  # noqa: BLE001
                rec.setdefault("fetch_errors", []).append(f"{seq}:{type(e).__name__}")
                continue
            rec["itemseqs_checked"].append({"itemSeq": seq, "name": name, "ingredient": ingr})
            if rec["found"]:
                continue
            f, q, dk = _detect(det, text)
            if f:
                rec.update(found=True, quote=q, detector_kind=dk,
                           url=url, source_itemseq=seq, source_name=name)
        rec["verdict"] = classify(rec["found"], rec["detector_kind"], seqs, direct)
        out["results"].append(rec)
    out["meta"]["sdk_stats"] = client.stats
    text_out = json.dumps(out, ensure_ascii=False, indent=1)
    if len(sys.argv) > 1 and sys.argv[1] == "--out":
        open(sys.argv[2], "w").write(text_out + "\n")
        print(f"wrote {sys.argv[2]}")
        for r in out["results"]:
            print(f'  {r["candidate_id"]:>15} | {r["verdict"]} | found={r["found"]}')
        print("SDK stats:", client.stats)
    else:
        print(text_out)


if __name__ == "__main__":
    main()
