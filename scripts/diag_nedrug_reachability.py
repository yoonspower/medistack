#!/usr/bin/env python3
"""진단 전용 — nedrug 도달성 CI vs 로컬 대조 (autoharvest online raw 0 규명).

판정/추출/데이터쓰기 없음. 약물 3종에 대해:
  env 지문 → 검색 A(ingrName1, orchestrator 방식) → 검색 B(itemName, PM 챗 성공 방식)
  → 상세(getItemDetail, 302 추종) → orchestrator client 경유 재현.
각 단계 요약을 stdout 에 찍고, diag_nedrug_summary.json 으로 저장(artifact).
어떤 단계가 실패해도 STOP 하지 않고 결과를 기록하고 계속한다(전 구간 데이터 수집이 목적).

polite delay ≥1s · timeout 25s · UA 고정 · 약물 3종 · 재시도 루프 없음.
"""
from __future__ import annotations

import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
TIMEOUT = 25
DELAY = 1.0

SEARCH_A = "https://nedrug.mfds.go.kr/searchDrug?searchYn=Y&ingrName1={}&page=1"   # orchestrator
SEARCH_B = "https://nedrug.mfds.go.kr/searchDrug?itemName={}&searchYn=Y"           # PM 챗 성공
DETAIL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

DRUGS = ["리세드론산", "알렌드론산", "레보티록신"]
KNOWN_SEQS = {           # 알려진 fallback itemSeq
    "리세드론산": "200713889",
    "레보티록신": "197400278",
    "이반드론산": "201207007",
    "알렌드론산": "199800180",
}
ITEMSEQ_RE = re.compile(r"getItemDetail\?itemSeq=(\d+)")
COUNTERPART_TERMS = ["제산제", "다가양이온", "알루미늄", "마그네슘", "칼슘"]

_opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def _get(url):
    """GET → dict(status, bytes, text, signal). 예외도 신호로 기록(STOP 안 함)."""
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
        with _opener.open(req, timeout=TIMEOUT) as r:
            body = r.read()
            text = body.decode("utf-8", "replace")
            sig = "ok"
            if len(body) == 0:
                sig = "EMPTY_BODY"
            return {"status": r.status, "final_url": r.geturl(), "bytes": len(body),
                    "text": text, "signal": sig, "ms": int((time.time() - t0) * 1000)}
    except urllib.error.HTTPError as e:
        sig = {403: "BLOCKED_403", 429: "RATELIMIT_429"}.get(e.code, f"HTTP_{e.code}")
        return {"status": e.code, "final_url": url, "bytes": 0, "text": "", "signal": sig,
                "ms": int((time.time() - t0) * 1000)}
    except urllib.error.URLError as e:
        return {"status": None, "final_url": url, "bytes": 0, "text": "",
                "signal": f"URLERROR:{getattr(e, 'reason', e)}", "ms": int((time.time() - t0) * 1000)}
    except Exception as e:  # redirect loop 등
        return {"status": None, "final_url": url, "bytes": 0, "text": "",
                "signal": f"EXC:{type(e).__name__}", "ms": int((time.time() - t0) * 1000)}


def _seqs(html):
    out, seen = [], set()
    for m in ITEMSEQ_RE.findall(html or ""):
        if m not in seen:
            seen.add(m); out.append(m)
    return out


def _interaction_match(detail_html):
    """상세 본문에 counterpart 동거어 + '흡수' 근접 여부(요약). 원시 덤프 없음."""
    txt = re.sub(r"<[^>]+>", " ", detail_html or "")
    txt = re.sub(r"\s+", " ", txt)
    has_absorb = "흡수" in txt
    hits = [t for t in COUNTERPART_TERMS if t in txt]
    near = False
    if has_absorb and hits:
        for m in re.finditer("흡수", txt):
            window = txt[max(0, m.start() - 120):m.start() + 120]
            if any(t in window for t in COUNTERPART_TERMS):
                near = True; break
    return {"has_absorption": has_absorb, "counterpart_terms": hits, "absorption_near_counterpart": near}


def env_fingerprint():
    ip = None; ip_sig = "ok"
    for u in ("https://api.ipify.org", "https://ifconfig.me/ip"):
        r = _get(u)
        if r["signal"] == "ok" and r["text"].strip():
            ip = r["text"].strip()[:64]; break
        ip_sig = r["signal"]
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "http_lib": "urllib(stdlib)",
        "hostname": socket.gethostname(),
        "external_ip": ip, "ip_signal": ip_sig,
        "runner": "CI" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
    }


def run():
    env = env_fingerprint()
    print(f"=== ENV: runner={env['runner']} ip={env['external_ip']} py={env['python']} utc={env['utc']}")
    drugs_out = {}
    for drug in DRUGS:
        print(f"\n=== 약물: {drug} ===")
        rec = {}
        time.sleep(DELAY)
        a = _get(SEARCH_A.format(urllib.parse.quote(drug)))
        seqs_a = _seqs(a["text"])
        rec["search_A_ingrName1"] = {"status": a["status"], "bytes": a["bytes"], "signal": a["signal"],
                                     "itemseq_count": len(seqs_a), "first5": seqs_a[:5]}
        print(f"  [검색A ingrName1] HTTP {a['status']} {a['bytes']}B {a['signal']} | itemSeq {len(seqs_a)} {seqs_a[:5]}")

        time.sleep(DELAY)
        b = _get(SEARCH_B.format(urllib.parse.quote(drug)))
        seqs_b = _seqs(b["text"])
        rec["search_B_itemName"] = {"status": b["status"], "bytes": b["bytes"], "signal": b["signal"],
                                    "itemseq_count": len(seqs_b), "first5": seqs_b[:5]}
        print(f"  [검색B itemName ] HTTP {b['status']} {b['bytes']}B {b['signal']} | itemSeq {len(seqs_b)} {seqs_b[:5]}")
        only_a = sorted(set(seqs_a) - set(seqs_b)); only_b = sorted(set(seqs_b) - set(seqs_a))
        rec["search_diff"] = {"only_A": only_a[:5], "only_B": only_b[:5],
                              "A_count": len(seqs_a), "B_count": len(seqs_b)}
        print(f"  [집합차] A전용 {len(only_a)} / B전용 {len(only_b)}")

        seq = (seqs_a or seqs_b or [KNOWN_SEQS.get(drug)])[0]
        rec["detail_seq_used"] = seq
        if seq:
            time.sleep(DELAY)
            d = _get(DETAIL.format(seq))
            im = _interaction_match(d["text"])
            rec["detail"] = {"seq": seq, "status": d["status"], "final_url_tail": d["final_url"][-60:],
                             "bytes": d["bytes"], "signal": d["signal"], **im}
            print(f"  [상세 {seq}] HTTP {d['status']} {d['bytes']}B {d['signal']} | "
                  f"흡수={im['has_absorption']} 동거어={im['counterpart_terms']} 근접={im['absorption_near_counterpart']}")
        drugs_out[drug] = rec

    # 알려진 fallback seq 직접 상세(검색 무관 도달성)
    fb = {}
    for name, seq in [("리세드론산", "200713889"), ("레보티록신", "197400278"), ("이반드론산", "201207007")]:
        time.sleep(DELAY)
        d = _get(DETAIL.format(seq))
        im = _interaction_match(d["text"])
        fb[f"{name}:{seq}"] = {"status": d["status"], "bytes": d["bytes"], "signal": d["signal"], **im}
        print(f"  [fallback 상세 {name} {seq}] HTTP {d['status']} {d['bytes']}B {d['signal']} | "
              f"흡수={im['has_absorption']} 근접={im['absorption_near_counterpart']}")

    # orchestrator client 경유 재현
    client_out = {}
    try:
        import nedrug_online_client_v1_7 as cm
        c = cm.NedrugOnlineClient(offline=False)
        time.sleep(DELAY)
        cseqs = c.search_itemseqs("리세드론산")
        time.sleep(DELAY)
        chtml = c.fetch_detail("200713889")
        client_out = {"search_itemseqs_리세드론산_count": len(cseqs), "first5": list(cseqs)[:5],
                      "fetch_detail_200713889_bytes": len(chtml or ""),
                      "interaction": _interaction_match(chtml)}
        print(f"\n  [client] search_itemseqs(리세드론산)={len(cseqs)} {list(cseqs)[:5]} | "
              f"fetch_detail(200713889)={len(chtml or '')}B 근접={client_out['interaction']['absorption_near_counterpart']}")
    except Exception as e:
        client_out = {"error": f"{type(e).__name__}: {e}"}
        print(f"\n  [client] ERROR {client_out['error']}")

    summary = {"env": env, "drugs": drugs_out, "fallback_detail": fb, "client_path": client_out}
    out_path = os.path.join(os.getcwd(), "diag_nedrug_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n=== summary 저장: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
