#!/usr/bin/env python3
"""
smoke_hctz_disclosure.py
v0.8 H-G2 — HCTZ 칼륨 반전 고지 render smoke (라이브 데이터 읽기 전용).

guards.js/render.js 는 ES module 이고 repo 에 package.json 이 없으므로,
두 파일을 임시 디렉토리에 복사하고 package.json {"type":"module"} 를 둔 뒤 node 로 import 한다.

시나리오:
  A 메트포르민 복합제(라이브)  → combobox O / combonotice X (inert·회귀)
  B HCTZ+ARB 복합제(합성)      → combobox O / combonotice O ('반대 방향' 문구)
  C HCTZ 복합제 + 마그네슘 필터 → combonotice X (칼륨 행 없음)
  D 단일 HCTZ(비복합제)         → combobox X / combonotice X (반전 고지는 복합제 전용)

사용: python3 scripts/smoke_hctz_disclosure.py
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
import { buildAliasIndex, aliasHint, filterRelations, getRenderableRelations } from './guards.js';
import { renderAliasHint } from './render.js';

const [,, exportPath, aliasPath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const liveAlias = JSON.parse(readFileSync(aliasPath, 'utf-8'));
const rels = getRenderableRelations(data);

let fails = 0;
const check = (name, cond) => { console.log((cond ? '[PASS] ' : '[FAIL] ') + name); if (!cond) fails++; };
function run(aliasIndex, query, extra) {
  const state = Object.assign({ query }, extra || {});
  const filtered = filterRelations(rels, state, aliasIndex);
  const info = aliasHint(filtered, state, aliasIndex);
  return { info, html: info ? renderAliasHint(info) : '' };
}

// A) 라이브 메트포르민 복합제 → combobox O, combonotice X (inert)
const liveIdx = buildAliasIndex(liveAlias);
const metCombo = (liveAlias.product_aliases || []).find(
  (p) => p.is_combination === true && p.combination_basis_ingredient === '메트포르민');
if (!metCombo) { console.log('[FAIL] 라이브 메트 복합제 alias 없음'); process.exit(1); }
const A = run(liveIdx, metCombo.alias);
check('A1 메트 복합제 combobox 표시', A.html.includes('combobox'));
check('A2 메트 복합제 칼륨 반전고지 미표시(inert)', !A.html.includes('combonotice'));
check('A3 메트 복합제 hctzPotassiumNotice 미설정', !(A.info && A.info.hctzPotassiumNotice));

// B) 합성 HCTZ+ARB 복합제 → combonotice O
const synth = { ingredient_aliases: [], product_aliases: [
  { alias: '코자플러스정', canonical_ingredient: '히드로클로로티아지드', kind: 'product',
    is_combination: true, combination_basis_ingredient: '히드로클로로티아지드', combination_notice_required: true } ] };
const B = run(buildAliasIndex(synth), '코자플러스정');
check('B1 HCTZ 복합제 combobox 표시', B.html.includes('combobox'));
check('B2 HCTZ 복합제 칼륨 반전고지 표시(반대 방향)', B.html.includes('combonotice') && B.html.includes('반대 방향'));
check('B3 hctzPotassiumNotice 설정', !!(B.info && B.info.hctzPotassiumNotice));

// C) HCTZ 복합제 + 마그네슘 필터 → 칼륨 행 없음 → combonotice X
const C = run(buildAliasIndex(synth), '코자플러스정', { nutrients: ['마그네슘'] });
check('C1 마그네슘 필터 시 칼륨 반전고지 미표시', !(C.info && C.info.hctzPotassiumNotice) && !C.html.includes('combonotice'));
check('C2 마그네슘 필터에도 복합제 배지는 표시', C.html.includes('combobox'));

// D) 단일 HCTZ(비복합제) → combobox X, combonotice X
const single = { ingredient_aliases: [
  { alias: '다이크로짇', canonical_ingredient: '히드로클로로티아지드', kind: 'ingredient' } ], product_aliases: [] };
const D = run(buildAliasIndex(single), '다이크로짇');
check('D1 단일 HCTZ 칼륨 반전고지 미표시(복합제 전용)', !D.html.includes('combonotice'));
check('D2 단일 HCTZ 복합제 배지 미표시', !D.html.includes('combobox'));

console.log('');
if (fails) { console.log('SMOKE: FAIL (' + fails + ')'); process.exit(1); }
console.log('SMOKE: PASS (모든 시나리오 통과)');
"""


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module smoke 불가")
        return 1
    tmp = tempfile.mkdtemp(prefix="ms_hctz_smoke_")
    try:
        shutil.copy(os.path.join(SRC, "guards.js"), os.path.join(tmp, "guards.js"))
        shutil.copy(os.path.join(SRC, "render.js"), os.path.join(tmp, "render.js"))
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
