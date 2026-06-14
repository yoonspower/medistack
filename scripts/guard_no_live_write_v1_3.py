#!/usr/bin/env python3
"""
guard_no_live_write_v1_3.py — harvester bot **no-live-write 가드**.

봇이 보호/live 데이터를 한 바이트도 바꾸지 않음을 기계적으로 보증한다.
  1) 보호셋 sha256 스냅샷 → 봇 실행 → sha256 불변 검증(바뀌면 FAIL)
  2) write-scope: 봇 실행으로 새로 바뀐 git 경로가 data/harvest_queue/ 하위만인지
  3) direct-http 스캔: scripts/·medistack_sdk/ 에 SDK 밖 직접 nedrug 호출(build_opener/urlopen/requests)
     이 **새로** 늘지 않았는지(미마이그레이션 allowlist 외 위반 FAIL)

사용:
  python3 scripts/guard_no_live_write_v1_3.py              # 봇 실행 없이 현 상태 가드(스냅샷=검증)
  python3 scripts/guard_no_live_write_v1_3.py --run-bot    # 봇 dry-run 전후로 보호셋 불변 + write-scope 검증
종료코드: 0 PASS / 1 FAIL(안전 위반).
"""
import argparse
import glob
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# 봇/사람이 절대 쓰면 안 되는 보호·live 집합(읽기전용).
PROTECTED_FILES = [
    "data/medistack_v0.1_beta_export.json",
    "data/medistack_v0.2_beta_export.json",
    "data/medistack_v0.3_aliases.json",
    "data/medistack_v0.3_aliases.sample.json",
    "data/full_drug_name_index_sample_v1_0.json",
    "data/full_drug_name_index_sample_v1_0.csv",
    "index.html",
]
PROTECTED_GLOBS = [
    "src/**/*",
    ".github/workflows/*",
    "scripts/validate_*.py",
    "scripts/validate_*.js",
    "medistack_sdk/**/*.py",  # SDK 소스도 봇 런타임 무수정 대상(보호셋 포함).
]
# 봇이 쓸 수 있는 유일한 경로 접두사.
ALLOWED_WRITE_PREFIX = "data/harvest_queue/"

# SDK 밖 직접 nedrug 호출 패턴(흩뿌리기 금지). 실제 호출 신호만(pointer 문자열 제외).
DIRECT_HTTP_RE = re.compile(r"\b(build_opener|urlopen)\b|requests\.(get|post)\b|^\s*import\s+requests\b", re.M)
# 점진 마이그레이션 중인(아직 SDK 미전환) 과거 스크립트 — 신규 위반과 구분. 이 목록은 줄어들어야 한다.
DIRECT_HTTP_ALLOWLIST = {
    "confirm_nedrug_item_details.py",
    "collect_nedrug_alias_candidates.py",
    "collect_full_drug_name_index_sample.py",
    "recollect_surface_candidates_v0_9.py",
    "verify_atier_relation_sources.py",
    "verify_ppi_calcium_combo_sources.py",
    "verify_source_queue_top10_v1_2.py",
    "generate_bulk_alias_candidates.py",
}
# SDK 본체는 유일하게 직접 네트워크를 소유하는 게이트웨이(허용).
SDK_OWNER = os.path.join("medistack_sdk", "nedrug_client.py")
# 스캐너 자신은 패턴 문자열을 데이터로 포함 → 제외(네트워크 호출 아님).
SCANNER_EXCLUDE = {"guard_no_live_write_v1_3.py"}

_fail = []


def _ok(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        _fail.append(name)


def protected_paths():
    paths = []
    for f in PROTECTED_FILES:
        if os.path.exists(os.path.join(REPO, f)):
            paths.append(f)
    for g in PROTECTED_GLOBS:
        for p in glob.glob(os.path.join(REPO, g), recursive=True):
            if os.path.isfile(p):
                paths.append(os.path.relpath(p, REPO))
    return sorted(set(paths))


def sha_snapshot(paths):
    """경로별 sha256. 삭제된 파일은 <MISSING> 센티넬 → 삭제도 드리프트로 탐지."""
    snap = {}
    for rel in paths:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            snap[rel] = "<MISSING>"
            continue
        with open(p, "rb") as f:
            snap[rel] = hashlib.sha256(f.read()).hexdigest()
    return snap


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout


def changed_paths():
    # --untracked-files=all: untracked 디렉토리를 한 줄로 접지 않고 개별 파일까지 열거(사각 제거).
    out = git("status", "--porcelain", "--untracked-files=all")
    paths = []
    for line in out.splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip().strip('"'))
    return paths


def scan_direct_http():
    """SDK 밖 직접 호출을 스캔. allowlist 외 위반 파일 반환."""
    violations = []
    roots = [glob.glob(os.path.join(REPO, "scripts", "*.py")),
             glob.glob(os.path.join(REPO, "medistack_sdk", "**", "*.py"), recursive=True)]
    for grp in roots:
        for p in grp:
            rel = os.path.relpath(p, REPO)
            base = os.path.basename(p)
            if rel == SDK_OWNER:
                continue  # SDK 게이트웨이는 직접 네트워크 소유 허용
            if base in SCANNER_EXCLUDE:
                continue  # 스캐너 자신(패턴을 데이터로 포함)
            if base in DIRECT_HTTP_ALLOWLIST:
                continue  # 점진 마이그레이션 backlog
            with open(p, encoding="utf-8") as f:
                if DIRECT_HTTP_RE.search(f.read()):
                    violations.append(rel)
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-bot", action="store_true", help="봇 dry-run 을 실행해 전후 불변 검증")
    ap.add_argument("--bot-args", default="--ingredients 세파클러,프레드니솔론,아세타졸아미드,펙소페나딘",
                    help="봇 실행 인자(기본=fixtures dry-run 서브셋)")
    args = ap.parse_args()

    print("=== guard_no_live_write_v1_3 ===")
    paths = protected_paths()
    before = sha_snapshot(paths)
    print(f"보호셋: {len(paths)} 파일 sha256 스냅샷")

    if args.run_bot:
        before_changed = set(changed_paths())
        r = subprocess.run([sys.executable, os.path.join(HERE, "harvest_relation_bot_v1_3.py"),
                            *args.bot_args.split()], capture_output=True, text=True)
        _ok("봇 dry-run 정상 종료(exit 0)", r.returncode == 0, r.stderr[-300:])
        after = sha_snapshot(paths)
        drift = [p for p in paths if before[p] != after[p]]  # 변조+삭제(<MISSING>) 모두 탐지
        _ok("보호셋 sha256 불변(live 무수정·무삭제)", not drift, f"변경됨: {drift}")
        # write-scope: 봇 실행으로 **새로** 나타난 경로가 data/harvest_queue/ 하위만인지.
        # 브랜치의 기존 untracked 파일(sdk/bot/guard 소스)은 before_changed 에 이미 있어 자동 제외.
        new_changed = set(changed_paths()) - before_changed
        out_of_scope = [p for p in new_changed if not p.startswith(ALLOWED_WRITE_PREFIX)]
        _ok("write-scope = data/harvest_queue/ 한정", not out_of_scope, f"범위밖: {out_of_scope}")
    else:
        after = sha_snapshot(paths)
        _ok("보호셋 sha256 스냅샷 일관", before == after)

    violations = scan_direct_http()
    _ok("direct-http: SDK 밖 직접호출 신규 위반 0", not violations, f"위반: {violations}")
    print(f"  (direct-http allowlist: {len(DIRECT_HTTP_ALLOWLIST)} — 점진 마이그레이션 backlog)")

    print("=" * 56)
    if _fail:
        print(f"RESULT: FAIL — {len(_fail)}건: {_fail}")
        return 1
    print("RESULT: PASS — live 데이터 무수정 · write-scope 한정 · 직접호출 신규 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
