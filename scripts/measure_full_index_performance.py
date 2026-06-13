#!/usr/bin/env python3
"""
measure_full_index_performance.py
MediStack v1.0 — full drug name index 클라이언트 로드/검색 성능 측정(리포트용, CI 하드게이트 아님).

배경(docs/MediStack_v1.0_full_drug_index_10k_plan.md §6 — 10k 진입 성능 사전 게이트):
  앱은 full index 를 loadFullIndex(fetch 1회) → buildNameOnlyIndex(전체 1회 순회) →
  searchNameOnly(선형 includes, 상한 limit) 로 사용한다. 인덱스가 커질수록 빌드/검색/페이로드
  비용이 늘어 모바일 체감에 영향. 이 스크립트는 **실제 src/js/guards.js 함수**(Python 재구현 아님)를
  node 로 호출해 빌드/검색 시간을 측정하고, JSON 파일/gzip(Pages 기본 압축) 크기와 20k 외삽을 낸다.

원칙:
  - 측정만 한다. 데이터/소스/CI 변경 없음. guards.js 를 임시 복사해 import(smoke 와 동일 패턴).
  - 임계(권장): buildNameOnlyIndex 중앙값 > 100ms 또는 gzip 전송 > ~1.5MB 면 경고(WARN).
    임계 초과는 자동 실패가 아니라 **리포트에 기록 + 대응 검토 신호**(plan §4-4).

사용: python3 scripts/measure_full_index_performance.py [data/full_drug_name_index_sample_v1_0.json] [--json]
종료 코드: 0(측정 성공, 임계 초과해도 0) / 1(측정 불가: node 미설치/파일 없음/하네스 오류)
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "src", "js")
DEF_INDEX = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")
CSV_INDEX = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.csv")

BUILD_WARN_MS = 100.0       # buildNameOnlyIndex 중앙값 임계(권장)
GZIP_WARN_BYTES = 1_500_000  # gzip 전송 페이로드 임계(권장)
APP_SEARCH_LIMIT = 30        # 앱 name_only 결과 상한(현행)

# node 하네스: 실제 guards.js 의 buildNameOnlyIndex/searchNameOnly 를 측정.
# - build: warm-up 후 N회 중앙값(ms)
# - search: 인덱스 1회 빌드 후, 대표 질의별 M회 중앙값(ms). 무매치 질의 = 전체 스캔(최악).
HARNESS_MJS = r"""
import { readFileSync } from 'node:fs';
import { buildNameOnlyIndex, searchNameOnly } from './guards.js';

const [,, fullPath] = process.argv;
const raw = readFileSync(fullPath, 'utf-8');

const median = (xs) => {
  const a = [...xs].sort((p, q) => p - q);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};
const timeIt = (fn, iters) => {
  const ts = [];
  for (let i = 0; i < iters; i++) { const t = process.hrtime.bigint(); fn(); ts.push(Number(process.hrtime.bigint() - t) / 1e6); }
  return median(ts);
};

// parse: 초기 로드 지배항(fetch 후 JSON.parse 원본). warm-up 2 + 측정 10회 중앙값(데스크톱 V8).
for (let i = 0; i < 2; i++) JSON.parse(raw);
const parseMs = timeIt(() => JSON.parse(raw), 10);
const full = JSON.parse(raw);

// build: warm-up 3 + 측정 15회 중앙값
for (let i = 0; i < 3; i++) buildNameOnlyIndex(full);
const buildMs = timeIt(() => buildNameOnlyIndex(full), 15);
const idx = buildNameOnlyIndex(full);

// search: 대표 질의(브랜드 조회=소수매치 ≈ 전체스캔) + 흔한 부분일치(다수매치=조기종료) + 무매치(최악).
const queries = [
  ['브랜드(게보린)', '게보린'],
  ['브랜드(노바스크)', '노바스크'],
  ['브랜드(타이레놀)', '타이레놀'],
  ['흔한부분일치(정)', '정'],
  ['흔한부분일치(캡슐)', '캡슐'],
  ['무매치-최악(전체스캔)', '존재하지않는약물xyzqwer'],
];
const search = {};
for (const [label, q] of queries) {
  const ms = timeIt(() => searchNameOnly(q, idx, 30), 50);
  search[label] = { ms, hits: searchNameOnly(q, idx, 30).length };
}

console.log(JSON.stringify({
  entriesTotal: Array.isArray(full.entries) ? full.entries.length : null,
  nameOnlyCount: idx.length,
  parseMs, buildMs, search,
}));
"""


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.2f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024


def run_node(full_path):
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — 성능 측정 불가", file=sys.stderr)
        return None
    tmp = tempfile.mkdtemp(prefix="ms_perf_")
    try:
        shutil.copy(os.path.join(SRC, "guards.js"), os.path.join(tmp, "guards.js"))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "perf.mjs"), "w", encoding="utf-8") as f:
            f.write(HARNESS_MJS)
        p = subprocess.run(["node", os.path.join(tmp, "perf.mjs"), full_path],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print("[FATAL] node 하네스 오류:\n" + p.stdout + p.stderr, file=sys.stderr)
            return None
        return json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    path = args[0] if args else DEF_INDEX
    if not os.path.exists(path):
        print(f"[FATAL] 파일 없음: {path}", file=sys.stderr)
        return 1

    json_bytes = os.path.getsize(path)
    with open(path, "rb") as f:
        gz = len(gzip.compress(f.read(), 6))
    csv_bytes = os.path.getsize(CSV_INDEX) if os.path.exists(CSV_INDEX) else None

    m = run_node(path)
    if m is None:
        return 1

    total = m["entriesTotal"] or 1
    name_only = m["nameOnlyCount"] or 1
    # 20k 외삽(선형): 빌드/페이로드는 엔트리 수에 ~비례.
    scale20k = 20000 / total
    ext = {
        "json_20k": int(json_bytes * scale20k),
        "gzip_20k": int(gz * scale20k),
        "parse_20k_ms": m.get("parseMs", 0) * scale20k,
        "build_20k_ms": m["buildMs"] * scale20k,
    }
    MOBILE_X = 4  # 저사양 모바일 V8 ≈ 데스크톱 ×3~5. 보수적으로 ×4 추정.
    load_desktop = m.get("parseMs", 0) + m["buildMs"]
    load_mobile = load_desktop * MOBILE_X
    warns = []
    if m["buildMs"] > BUILD_WARN_MS:
        warns.append(f"buildNameOnlyIndex 중앙값 {m['buildMs']:.1f}ms > {BUILD_WARN_MS:.0f}ms")
    if gz > GZIP_WARN_BYTES:
        warns.append(f"gzip 전송 {human(gz)} > {human(GZIP_WARN_BYTES)}")

    if as_json:
        print(json.dumps({"path": path, "json_bytes": json_bytes, "gzip_bytes": gz,
                          "csv_bytes": csv_bytes, "measured": m, "extrapolate_20k": ext,
                          "warns": warns}, ensure_ascii=False, indent=2))
        return 0

    print("=" * 68)
    print("MediStack full index 성능 측정 (실제 guards.js · node)")
    print("=" * 68)
    print(f"파일            : {os.path.relpath(path, REPO)}")
    print(f"엔트리 총수     : {total:,}  (name_only {name_only:,})")
    print(f"JSON 크기       : {human(json_bytes)}  ({json_bytes:,}B)")
    print(f"  gzip(전송)    : {human(gz)}  ({gz:,}B)  ← Pages 기본 압축 기준")
    if csv_bytes:
        print(f"CSV 크기        : {human(csv_bytes)}  (배포 비반입 — 데이터 산출물)")
    print("-" * 68)
    print(f"JSON.parse 중앙값         : {m.get('parseMs', 0):.2f} ms  (초기 로드 지배항 · warm-up 2 + 10회)")
    print(f"buildNameOnlyIndex 중앙값 : {m['buildMs']:.2f} ms  (warm-up 3 + 15회)")
    print(f"초기 로드(parse+build)    : 데스크톱 {load_desktop:.2f} ms  →  저사양 모바일 추정 ~{load_mobile:.0f} ms (×{MOBILE_X})")
    print(f"searchNameOnly (limit {APP_SEARCH_LIMIT}, 50회 중앙값):")
    for label, v in m["search"].items():
        print(f"  {label:24s}: {v['ms']:.3f} ms  (hits {v['hits']})")
    print("-" * 68)
    print("20k 외삽(선형):")
    print(f"  JSON ~{human(ext['json_20k'])} / gzip ~{human(ext['gzip_20k'])} / parse ~{ext['parse_20k_ms']:.1f}ms / build ~{ext['build_20k_ms']:.1f}ms")
    print("-" * 68)
    if warns:
        print("WARN(임계 초과 — 리포트 기록 + 대응 검토 신호, 자동 실패 아님):")
        for w in warns:
            print("  ⚠️ " + w)
    else:
        print(f"OK: build < {BUILD_WARN_MS:.0f}ms · gzip < {human(GZIP_WARN_BYTES)} (모바일 체감 임계 내)")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
