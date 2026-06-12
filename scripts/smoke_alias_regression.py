#!/usr/bin/env python3
"""
smoke_alias_regression.py
MediStack v0.9 — 브랜드 alias → 성분 relation 회귀 검색 smoke (라이브 데이터 읽기 전용).

표면형 정제(v0.9) 전후로 검색 결과가 불변임을 실제 guards.js 로 고정한다.
이전엔 각 phase 마다 ad-hoc /tmp .mjs 로만 돌리던 회귀를 커밋된 테스트로 승격.

guards.js/render.js 는 ES module 이고 repo 에 package.json 이 없으므로,
guards.js 를 임시 디렉토리에 복사하고 package.json {"type":"module"} 를 둔 뒤 node 로 import 한다.

회귀 시나리오(기대값은 라이브 relation 30 + alias 618 기준 ground-truth):
  타리비드 → 오플록사신 3건
  포사맥스 → 알렌드론산 1건
  토렘   → 토라세미드 2건
  넥시움 → 0건 (에스오메프라졸 제품 alias 금지 → 브리지 없음)
  #r15   → 15행(에스오메프라졸×B12)은 렌더 풀에 없음(excluded_v0_1)
  미카르디스플러스정40/12.5밀리그램 → HCTZ 복합제 칼륨 반전 고지 표시
  히드로클로로티아지드 직접검색 → 칼륨 반전 고지 미오작동(복합제 전용)

사용: python3 scripts/smoke_alias_regression.py
종료 코드: 0 PASS, 1 FAIL
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "src", "js")
EXPORT = os.path.join(REPO, "data", "medistack_v0.2_beta_export.json")
ALIASES = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")

TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { buildAliasIndex, filterRelations, aliasHint, getRenderableRelations } from './guards.js';

const [,, exportPath, aliasPath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const liveAlias = JSON.parse(readFileSync(aliasPath, 'utf-8'));
const rels = getRenderableRelations(data);
const idx = buildAliasIndex(liveAlias);

let fails = 0;
const check = (name, cond, extra) => {
  console.log((cond ? '[PASS] ' : '[FAIL] ') + name + (extra !== undefined ? `  (got ${extra})` : ''));
  if (!cond) fails++;
};
const count = (q) => filterRelations(rels, { query: q }, idx).length;
const hint = (q) => aliasHint(filterRelations(rels, { query: q }, idx), { query: q }, idx);

// 브랜드 alias → 성분 relation 회귀 (불변 기대값)
check('타리비드 → 오플록사신 3건', count('타리비드') === 3, count('타리비드'));
check('포사맥스 → 알렌드론산 1건', count('포사맥스') === 1, count('포사맥스'));
check('토렘 → 토라세미드 2건', count('토렘') === 2, count('토렘'));
check('넥시움 → 0건(에스오메프라졸 alias 금지)', count('넥시움') === 0, count('넥시움'));

// #r15 fail-safe: 15행(에스오메프라졸×B12)은 렌더 대상이 아님
check('#r15 fail-safe: relation id 15 미렌더', !rels.some((r) => r.id === 15));

// HCTZ 복합제 칼륨 반전 고지 (라이브)
const micHint = hint('미카르디스플러스정40/12.5밀리그램');
check('미카르디스플러스정40/12.5밀리그램 → HCTZ combo 칼륨 반전고지', !!(micHint && micHint.hctzPotassiumNotice));

// 단일 HCTZ 직접검색 → combo 고지 오작동 없어야 (반전고지는 복합제 전용)
const singleHint = hint('히드로클로로티아지드');
check('단일 HCTZ 직접검색 → 칼륨 반전고지 미오작동', !(singleHint && singleHint.hctzPotassiumNotice));

console.log('');
if (fails) { console.log('SMOKE: FAIL (' + fails + ')'); process.exit(1); }
console.log('SMOKE: PASS (회귀 7건 모두 불변)');
"""


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module smoke 불가")
        return 1
    tmp = tempfile.mkdtemp(prefix="ms_alias_regression_")
    try:
        shutil.copy(os.path.join(SRC, "guards.js"), os.path.join(tmp, "guards.js"))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(["node", os.path.join(tmp, "test.mjs"), EXPORT, ALIASES],
                           capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
