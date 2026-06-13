#!/usr/bin/env python3
"""
verify_ppi_calcium_combo_sources.py
MediStack — 복합제 검토 케이스 C(PPI/침강탄산칼슘 18건)의 가설 relation 테마
"PPI × 칼슘(흡수)"가 MFDS nedrug 허가사항(getItemDetail) 원문에 실재하는지 **출처 존재 여부만** 확인한다.

⚠️ 이 스크립트는 relation/full index/alias/export/src 를 한 줄도 수정하지 않는다(읽기 전용 + 네트워크 fetch).
   relation 을 추가/승격하지 않는다. C 18건을 flip 하지 않는다. 출력은 증거·분류 CSV 뿐이다.
   제품추천/복용지시/영양제 추천 문구를 생성하지 않는다(허가사항 원문 인용만).

검증 질문(A티어 방법론 승계 — 허가사항 우선 source gate):
  Q1. 이 PPI/탄산칼슘 복합제(또는 단일성분 PPI) 허가사항에 "PPI 가 칼슘 흡수를 저해/감소"한다는
      상호작용·주의가 **명시**되어 있는가?  → 있으면 PPI×칼슘(흡수) relation 의 source 후보.
  Q2. 라벨이 침강탄산칼슘을 어떻게 규정하는가(영양 칼슘 vs 제산/완충)?  → 카드 오도 위험 판단용.
  Q3. 칼슘 관련해 라벨에 무엇이 있는가(골절 위험 / 저칼슘혈증)?  → relation 모델 적합성 판단용.

신호어:
  ca_absorption : '칼슘'+'흡수' 근접(상호작용 문맥) — 단, 탄산칼슘 조성/B12·철 흡수 문맥은 배제
  fracture      : '골절'
  hypocalcemia  : '저칼슘'
  antacid_role  : 탄산칼슘이 '중화/제산/완충/약알칼리' 문맥에 등장(완충 성분 규정)

사용: python3 scripts/verify_ppi_calcium_combo_sources.py [--no-write]
출력: data/ppi_calcium_source_verification_v1_1.csv  (분석 산출물만)
"""
import csv
import html as htmllib
import http.cookiejar
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
OUT_CSV = os.path.join(DATA, "ppi_calcium_source_verification_v1_1.csv")
CHECKED_AT = "2026-06-13"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

# 케이스 C 18건(복합제) — data/combo_relation_review_v1_1.csv case==C 에서 추출
COMBO_C = [
    ("202300167", "란소앤정30/600밀리그램", "란소프라졸"),
    ("202300168", "란탄듀오정30/600밀리그램", "란소프라졸"),
    ("202300169", "란사톤듀오정30/600밀리그램", "란소프라졸"),
    ("202300170", "란소듀오정30/600밀리그램", "란소프라졸"),
    ("202300171", "뉴란소엑스정30/600밀리그램", "란소프라졸"),
    ("202300177", "란스타정30/600밀리그램", "란소프라졸"),
    ("202301789", "라베가드정20/600밀리그램", "라베프라졸"),
    ("202400481", "라베가드정10/600밀리그램", "라베프라졸"),
    ("202401498", "라베드온정10/600mg", "라베프라졸"),
    ("202401499", "라베드온정20/600mg", "라베프라졸"),
    ("202500561", "란소앤정15/600밀리그램", "란소프라졸"),
    ("202500562", "란탄듀오정15/600밀리그램", "란소프라졸"),
    ("202500563", "란사톤듀오정15/600밀리그램", "란소프라졸"),
    ("202500564", "란스타정15/600밀리그램", "란소프라졸"),
    ("202500565", "란소듀오정15/600밀리그램", "란소프라졸"),
    ("202500566", "뉴란소엑스정15/600밀리그램", "란소프라졸"),
    ("202600357", "라베피드정20/600밀리그램", "라베프라졸"),
    ("202600358", "라베피드정10/600밀리그램", "라베프라졸"),
]
# 교차확인용 단일성분 PPI 대표 품목(A티어에서 fetch 성공 seq 재사용)
SINGLE_PPI = [
    ("201308978", "란소프라졸 단일(대표)", "란소프라졸"),
    ("201308053", "란소프라졸 단일(대표2)", "란소프라졸"),
    ("201405854", "경보라베프라졸정10mg", "라베프라졸"),
    ("201308942", "라베프라졸 단일(대표2)", "라베프라졸"),
]


def make_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch_text(opener, seq):
    url = DETAIL_URL.format(seq)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    last = None
    for _ in range(3):
        try:
            with opener.open(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
            t = re.sub(r"<[^>]+>", " ", raw)
            t = htmllib.unescape(t)
            t = re.sub(r"\s+", " ", t)
            return t, url
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5)
    raise last


def snip(text, i, pad=90):
    return text[max(0, i - pad):i + pad].strip()


def find_ca_absorption(text):
    """'칼슘'이 '흡수'와 근접(±40자)하면서 상호작용/저해 문맥인 신호.
       조성표(분량/단위/규격)·B12·철 흡수 문맥은 배제. 반환 (found, snippet)."""
    for m in re.finditer("칼슘", text):
        i = m.start()
        window = text[max(0, i - 45):i + 45]
        if "흡수" not in window:
            continue
        # 조성/함량/완충 규정 문맥 배제
        if re.search(r"분량|단위|규격|첨가제|중화|약알칼리|함유하고", window):
            continue
        # B12/철의 흡수 문맥(공존)인 경우 배제
        if re.search(r"B\s*12|시아노코발라민|철염|철분", window):
            continue
        # '칼슘 흡수 저해/감소/방해' 류만 신호로
        if re.search(r"칼슘.{0,12}흡수.{0,8}(저해|감소|방해|장애|줄)|흡수.{0,12}칼슘", window):
            return True, snip(text, i)
    return False, ""


def context_hits(text, kw, pad=90, limit=2):
    out = []
    for m in list(re.finditer(re.escape(kw), text))[:limit]:
        out.append(snip(text, m.start(), pad))
    return out


def antacid_role(text):
    """탄산칼슘을 제산/완충 성분으로 규정하는 문맥."""
    for m in re.finditer("탄산칼슘", text):
        i = m.start()
        w = text[max(0, i - 30):i + 80]
        if re.search(r"중화|제산|약알칼리|위내\s*산도|위산을", w):
            return True, snip(text, i)
    # '중화' 단독 문맥
    for m in re.finditer("중화", text):
        w = text[max(0, m.start() - 60):m.start() + 30]
        if "칼슘" in w or "위산" in w:
            return True, snip(text, m.start())
    return False, ""


def verify(items, group):
    opener = make_opener()
    rows = []
    for seq, name, base in items:
        try:
            t, url = fetch_text(opener, seq)
        except Exception as e:  # noqa
            rows.append({"group": group, "item_seq": seq, "item_name": name, "base": base,
                         "fetched": "0", "ca_absorption_signal": "FETCH_ERR",
                         "fracture_mention": "", "hypocalcemia_mention": "",
                         "antacid_role": "", "ca_absorption_evidence": str(e)[:120],
                         "fracture_evidence": "", "antacid_evidence": "",
                         "source_url": url if 'url' in dir() else "", "source_checked_at": CHECKED_AT})
            print(f"  [ERR] {seq} {name}: {type(e).__name__}")
            time.sleep(0.5)
            continue
        ca_found, ca_ev = find_ca_absorption(t)
        frac = context_hits(t, "골절", limit=1)
        hypo = context_hits(t, "저칼슘", limit=1)
        ant_found, ant_ev = antacid_role(t)
        rows.append({
            "group": group, "item_seq": seq, "item_name": name, "base": base,
            "fetched": "1",
            "ca_absorption_signal": "YES" if ca_found else "no",
            "fracture_mention": "YES" if frac else "no",
            "hypocalcemia_mention": "YES" if hypo else "no",
            "antacid_role": "YES" if ant_found else "no",
            "ca_absorption_evidence": ca_ev[:200],
            "fracture_evidence": (frac[0][:200] if frac else ""),
            "antacid_evidence": ant_ev[:200],
            "source_url": url, "source_checked_at": CHECKED_AT,
        })
        print(f"  {seq} {name[:24]:24s} ca_absorb={'YES' if ca_found else 'no':3s} "
              f"fracture={'Y' if frac else '-'} hypoCa={'Y' if hypo else '-'} "
              f"antacid={'Y' if ant_found else '-'}")
        time.sleep(0.7)
    return rows


COLS = ["group", "item_seq", "item_name", "base", "fetched", "ca_absorption_signal",
        "fracture_mention", "hypocalcemia_mention", "antacid_role",
        "ca_absorption_evidence", "fracture_evidence", "antacid_evidence",
        "source_url", "source_checked_at"]


def main():
    write = "--no-write" not in sys.argv
    print("=== 케이스 C 복합제 18건 ===")
    rows = verify(COMBO_C, "combo_C")
    print("=== 교차확인 단일성분 PPI ===")
    rows += verify(SINGLE_PPI, "single_PPI")

    n_fetch = sum(1 for r in rows if r["fetched"] == "1")
    n_ca = sum(1 for r in rows if r["ca_absorption_signal"] == "YES")
    n_frac = sum(1 for r in rows if r["fracture_mention"] == "YES")
    n_ant = sum(1 for r in rows if r["antacid_role"] == "YES")
    print("\n=== 요약 ===")
    print(f"  fetch 성공: {n_fetch}/{len(rows)}")
    print(f"  PPI×칼슘(흡수) 신호 있는 품목: {n_ca}/{n_fetch}  ← source gate 핵심")
    print(f"  골절(fracture) 언급 품목: {n_frac}/{n_fetch}  (임상 위험 진술)")
    print(f"  탄산칼슘=제산/완충 규정 품목: {n_ant}/{n_fetch}  (오도 위험 판단)")
    if n_ca == 0:
        print("\n  => 결론: PPI×칼슘(흡수) 상호작용은 fetch 품목 허가사항에 미기재 "
              "(literature only 가능) → A티어 H2×B12 와 동일하게 'missing' 성격.")
    if write:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)}  ({len(rows)} rows)")
    else:
        print("\n(--no-write)")
    print("\nVERIFY PPI×CALCIUM COMBO SOURCES: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
