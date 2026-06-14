#!/usr/bin/env python3
"""
collect_antacid_interaction_evidence_v1_2.py
MediStack antacid_interaction 트랙 — Al/Mg **제산제(약물 카테고리)** 병용 directive 가 허가사항 원문에
실재하는지 라벨 직접 fetch 로 확인하고 **원문 인용(quote)** 을 추출한다(증거 ledger·라이브/draft 미반영).

⚠️ 이 트랙은 "약물 × Al/Mg 제산제"이며 **영양소(Mg) 보충제 relation 이 아니다**(antacid_interaction_track_v1_2.md).
   nutrient detector(mg_absorption 등)와 다른, **제산제 directive detector** 를 쓴다. 영양소 트랙 오인 방지.
⚠️ 보호 데이터(relation/full index/alias/export/src) 한 줄도 수정하지 않는다(읽기전용 + 네트워크 fetch).
   source_confirmed/draft 판정은 본 스크립트가 하지 않는다 — 증거만 산출하고 단일 게이트(source_confirm_gate)가 판정.

입력: 손큐레이션 후보(ingredient + 알려진 itemSeq 또는 검색). 출력: data/candidates/antacid_interaction_evidence_v1_2.json
사용: python3 scripts/collect_antacid_interaction_evidence_v1_2.py [--delay S]
종료코드: 0.
"""
import argparse
import importlib.util
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
OUT = os.path.join(DATA, "candidates", "antacid_interaction_evidence_v1_2.json")
CHECKED_AT = "2026-06-14"

_spec = importlib.util.spec_from_file_location("vfs", os.path.join(HERE, "verify_factory_sources_v1_2.py"))
vfs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfs)

# 후보: (candidate_id, ingredient, 검색stem, 알려진 itemSeq(있으면 우선)). itemSeq None 이면 단일 경구 검색.
CANDIDATES = [
    ("AT-01", "펙소페나딘", "펙소페나딘", "202202380"),   # 노즈알연질캡슐(=CQ-103 원천)
    ("AT-02", "아지트로마이신", "아지트로마이신", "200708447"),  # batch4 CQ-233 재확인
    ("AT-03", "클래리트로마이신", "클래리트로마이신", None),
    ("AT-04", "플루코나졸", "플루코나졸", None),
    ("AT-05", "이트라코나졸", "이트라코나졸", None),
    ("AT-06", "케토코나졸", "케토코나졸", None),
]

# Al/Mg 제산제 병용 directive detector. 첨가제(스테아르산마그네슘 등)·환자 전해질 경고(저마그네슘혈증)는 배제.
ANTACID_ANCHOR = re.compile(r"제산제|수산화알루미늄|수산화마그네슘|알루미늄[ㆍ·,/ ]*마그네슘|마그네슘[ㆍ·,/ ]*알루미늄|알루미늄\s*또는\s*마그네슘|함유\s*제산제")
DIRECTIVE_CTX = re.compile(r"복용하지|투여하지|병용\s*금지|동시\s*복용|동시\s*투여|함께\s*(복용|투여|사용)|간격|병용\s*시|투여\s*간격|2\s*시간|동시에")
EXCIPIENT_NEG = re.compile(r"스테아르산마그네슘|규산마그네슘|산화마그네슘\s*\(첨가|저마그네슘혈증\s*환자|저칼륨혈증")


def find_antacid_quote(text):
    """제산제 directive 동거 스니펫 추출. (found, quote, kind)."""
    best = None
    for m in ANTACID_ANCHOR.finditer(text):
        i = m.start()
        w = text[max(0, i - 90):i + 110]
        # 첨가제/환자경고 문맥이 anchor 바로 옆이면 skip(부형제·전해질경고 false positive)
        near = text[max(0, i - 15):i + 25]
        if EXCIPIENT_NEG.search(near):
            continue
        if DIRECTIVE_CTX.search(w):
            quote = re.sub(r"\s+", " ", w).strip()
            # directive 강도 분류
            if re.search(r"복용하지|투여하지|병용\s*금지", w):
                kind = "avoid_concomitant"   # 병용금지(강)
            elif re.search(r"간격|2\s*시간|투여\s*간격", w):
                kind = "separation_or_spacing"  # 간격(중)
            else:
                kind = "coadmin_caution"     # 동시복용 주의(중)
            return True, quote, kind
        if best is None:
            best = re.sub(r"\s+", " ", w).strip()
    return False, (best or ""), "co-occur_no_directive"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()
    opener = vfs.make_opener()
    out = {
        "meta": {
            "name": "antacid_interaction_evidence_v1_2",
            "created_at": CHECKED_AT,
            "status": "EVIDENCE LEDGER — NOT LIVE / NOT DRAFT (gate adjudicates)",
            "track": "antacid_interaction (약물 × Al/Mg 제산제 — 영양소 트랙 아님)",
            "live_integration_forbidden": True,
            "note": "허가사항 원문에서 Al/Mg 제산제 병용 directive 동거 인용만 추출. source_confirmed/draft 판정은 source_confirm_gate_v1_2.py 단일 게이트가 수행. nutrient(Mg) relation 으로 박지 않는다.",
        },
        "evidence": [],
    }
    for cid, ing, stem, seq in CANDIDATES:
        seqs = []
        if seq:
            seqs = [(seq, "", "")]
        else:
            found, why = vfs.search_itemseqs(opener, stem, max_n=2, max_pages=2)
            seqs = found if found else []
        rec = {"candidate_id": cid, "ingredient": ing, "itemseqs_checked": [], "found": False,
               "directive_kind": "", "quote": "", "url": "", "checked_at": CHECKED_AT}
        if not seqs:
            rec["note"] = "국내 단일 경구 완제 itemSeq 미확보 — 직접 지정 재확인 필요."
            out["evidence"].append(rec)
            print(f"  {cid} {ing}: NO itemSeq")
            continue
        for s, _, _ in seqs:
            try:
                text, url = vfs.fetch_detail(opener, s)
            except Exception as e:  # noqa
                continue
            rec["itemseqs_checked"].append(s)
            found, quote, kind = find_antacid_quote(text)
            if found:
                rec.update(found=True, directive_kind=kind, quote=quote[:400], url=url, seq_hit=s)
                break
            time.sleep(args.delay)
        out["evidence"].append(rec)
        print(f"  {cid} {ing}: found={rec['found']} kind={rec['directive_kind']} seqs={rec['itemseqs_checked']}")
        time.sleep(args.delay)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nfound = sum(1 for e in out["evidence"] if e["found"])
    print(f"\nantacid directive found: {nfound}/{len(out['evidence'])}")
    print(f"[write] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
