#!/usr/bin/env python3
"""
smoke_search_regression_v1_0.py
MediStack v1.0 검색 회귀 smoke (라이브 데이터 읽기 전용). v1.0-C 기준선 + Phase 3 name_only UX.

목적:
  검색·고지·empty·degrade 동작 + Phase 3 name_only(relation 없는 약 '품목명 확인') 동작을
  실제 guards.js + render.js 로 고정한다. relation 검색 동작은 Phase 3 후에도 **불변**이어야 하고,
  name_only 는 relation 0건일 때만 보조로 동작해야 한다. 깨지면 이 smoke 가 FAIL.

테스트 레이어(전부 라이브 데이터 기준 ground-truth):
  E. 배선       : data.js 가 full index/name_only 배선(Phase 3) + app.js 라우팅 + 샘플 데이터 존재
  A. behavior   : filterRelations 결과 수 + aliasHint 플래그 (relation 검색 — Phase 3 후 불변)
  B. render     : renderAliasHint HTML(복합제 배지 / 칼륨 주의 / alias 안내 / empty)
  C. list       : renderListResults HTML(0건 → 카드 없음 / N건 → 카드 존재)
  D. id15       : relation id15(에스오메프라졸×B12) 렌더 풀 미포함
  F. degrade    : alias 인덱스 부재(null/빈/garbage) → relation-only 정상 degrade
  G. name_only  : buildNameOnlyIndex + searchNameOnly (relation 없는 약 커버 / 여전히 empty)
  H. nameRender : renderNameOnlyResults HTML(참고정보 없음 안내·품목명 카드 / 상호작용·제품 없음)

기대값 소스: scripts/fixtures/search_regression_v1_0.json (실제 guards.js 측정 ground-truth).

guards.js/render.js 는 ES module 이고 repo 에 package.json 이 없으므로,
두 파일을 임시 디렉토리에 복사하고 package.json {"type":"module"} 를 둔 뒤 node 로 import 한다.
(render.js 는 './guards.js' 를 import 하므로 두 파일 모두 복사한다.)

사용: python3 scripts/smoke_search_regression_v1_0.py
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
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
FIXTURE = os.path.join(HERE, "fixtures", "search_regression_v1_0.json")
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")

TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { buildAliasIndex, filterRelations, aliasHint, getRenderableRelations, buildNameOnlyIndex, searchNameOnly } from './guards.js';
import { renderAliasHint, renderListResults, renderNameOnlyResults } from './render.js';

const [,, exportPath, aliasPath, fixturePath, fullPath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const alias = JSON.parse(readFileSync(aliasPath, 'utf-8'));
const fx = JSON.parse(readFileSync(fixturePath, 'utf-8'));
const full = JSON.parse(readFileSync(fullPath, 'utf-8'));
const rels = getRenderableRelations(data);
const idx = buildAliasIndex(alias);
const nameIdx = buildNameOnlyIndex(full);
const notice = full.meta && full.meta.name_only_notice;

let fails = 0;
const check = (name, cond, extra) => {
  console.log((cond ? '[PASS] ' : '[FAIL] ') + name + (extra !== undefined ? `  (${extra})` : ''));
  if (!cond) fails++;
};
const sorteq = (a, b) => JSON.stringify([...(a || [])].sort()) === JSON.stringify([...(b || [])].sort());
const hintOf = (q) => aliasHint(filterRelations(rels, { query: q }, idx), { query: q }, idx);
const countOf = (q) => filterRelations(rels, { query: q }, idx).length;

// A. behavior — count + aliasHint flags
for (const c of fx.behavior) {
  const n = countOf(c.query);
  check(`A[${c.group}] "${c.query}" count=${c.count}`, n === c.count, `got ${n}`);
  const h = hintOf(c.query);
  if (c.hintNull) check(`A[${c.group}] "${c.query}" hint=null`, h === null, `got ${JSON.stringify(h)}`);
  if (c.ingredients) check(`A[${c.group}] "${c.query}" ingredients ${JSON.stringify(c.ingredients)}`, !!h && sorteq(h.ingredients, c.ingredients), JSON.stringify(h && h.ingredients));
  if (c.comboBases) check(`A[${c.group}] "${c.query}" comboBases ${JSON.stringify(c.comboBases)}`, !!h && sorteq(h.comboBases, c.comboBases), JSON.stringify(h && h.comboBases));
  if (c.hctzPotassiumNotice !== undefined) check(`A[${c.group}] "${c.query}" hctzPotassiumNotice=${c.hctzPotassiumNotice}`, !!(h && h.hctzPotassiumNotice) === c.hctzPotassiumNotice);
}

// B. render — renderAliasHint HTML
for (const c of fx.render) {
  const html = renderAliasHint(hintOf(c.query));
  for (const s of (c.contains || [])) check(`B[${c.group}] "${c.query}" contains ${JSON.stringify(s)}`, html.includes(s));
  for (const s of (c.notContains || [])) check(`B[${c.group}] "${c.query}" NOT ${JSON.stringify(s)}`, !html.includes(s));
}

// C. list_results — renderListResults HTML (empty → no card row)
for (const c of (fx.list_results || [])) {
  const filtered = filterRelations(rels, { query: c.query }, idx);
  check(`C[${c.group}] "${c.query}" filtered=${c.filteredCount}`, filtered.length === c.filteredCount, `got ${filtered.length}`);
  const html = renderListResults(filtered, rels.length);
  for (const s of (c.contains || [])) check(`C[${c.group}] "${c.query}" contains ${JSON.stringify(s)}`, html.includes(s));
  for (const s of (c.notContains || [])) check(`C[${c.group}] "${c.query}" NOT ${JSON.stringify(s)}`, !html.includes(s));
}

// D. id15 fail-safe
check(`D[failsafe] relation id15 렌더 풀 미포함`, rels.some((r) => r.id === 15) === fx.id15_failsafe.expectPresent);

// F. degrade — alias 인덱스 부재/garbage → []  (relation-only 유지)
for (const bad of [null, undefined, {}, { ingredient_aliases: 'x', product_aliases: 5 }]) {
  const e = buildAliasIndex(bad);
  check(`F[degrade] buildAliasIndex(${JSON.stringify(bad)}) → 빈 인덱스`, Array.isArray(e) && e.length === 0, `len ${e && e.length}`);
}
for (const c of fx.degrade) {
  const n = filterRelations(rels, { query: c.query }, []).length;
  check(`F[degrade] "${c.query}" empty-index count=${c.emptyIndexCount} (${c.kind})`, n === c.emptyIndexCount, `got ${n}`);
}

// G. name_only — searchNameOnly (relation 없는 약 커버 / 여전히 empty). relation 검색과 독립.
check(`G[index] buildNameOnlyIndex size=${fx.name_only_index_size}`, nameIdx.length === fx.name_only_index_size, `got ${nameIdx.length}`);
for (const c of (fx.name_only || [])) {
  const n = searchNameOnly(c.query, nameIdx, 30).length;
  if (c.count !== undefined) check(`G[${c.group}] "${c.query}" name_only count=${c.count}`, n === c.count, `got ${n}`);
  if (c.minCount !== undefined) check(`G[${c.group}] "${c.query}" name_only >=${c.minCount}`, n >= c.minCount, `got ${n}`);
}

// H. name_only render — renderNameOnlyResults HTML(참고정보 없음 안내 + 품목명 카드, 상호작용/제품 없음).
for (const c of (fx.name_only_render || [])) {
  const html = renderNameOnlyResults(searchNameOnly(c.query, nameIdx, 30), notice);
  for (const s of (c.contains || [])) check(`H[${c.group}] "${c.query}" contains ${JSON.stringify(s)}`, html.includes(s));
  for (const s of (c.notContains || [])) check(`H[${c.group}] "${c.query}" NOT ${JSON.stringify(s)}`, !html.includes(s));
}

console.log('');
if (fails) { console.log('NODE SECTION (A~H): FAIL (' + fails + ')'); process.exit(1); }
console.log('NODE SECTION (A~H): PASS');
"""


def baseline_checks():
    """E. name_only UX 배선 확인 (Python: 파일/배선 레벨).

    Phase 3: data.js 가 full drug index / loadFullIndex 를 배선하고, app.js 가 name_only
    라우팅(searchNameOnly/renderNameOnlyResults)을 한다. full index 샘플 데이터도 존재해야 한다.
    (relation 검색 동작 불변은 behavior 케이스 A 가 계속 고정한다.)
    """
    fails = 0

    def chk(name, cond, extra=""):
        nonlocal fails
        print(("[PASS] " if cond else "[FAIL] ") + name + (f"  ({extra})" if extra else ""))
        if not cond:
            fails += 1

    with open(os.path.join(SRC, "data.js"), encoding="utf-8") as f:
        djs = f.read().lower()
    chk("E[wired] data.js 가 full_drug_name_index URL 배선", "full_drug_name_index" in djs)
    chk("E[wired] data.js 에 loadFullIndex fail-soft 로더", "loadfullindex" in djs)

    with open(os.path.join(SRC, "app.js"), encoding="utf-8") as f:
        ajs = f.read()
    chk("E[wired] app.js 가 name_only 라우팅(searchNameOnly+renderNameOnlyResults)",
        "searchNameOnly" in ajs and "renderNameOnlyResults" in ajs)

    chk("E[wired] full drug index 샘플 데이터 존재",
        os.path.exists(os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")))

    return fails


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module smoke 불가")
        return 1

    print("=== E. name_only UX 배선 확인 (파일/배선) ===")
    base_fails = baseline_checks()

    print("=== A~H. 검색/고지/empty/degrade/name_only (실제 guards.js + render.js) ===")
    tmp = tempfile.mkdtemp(prefix="ms_search_regression_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(
            ["node", os.path.join(tmp, "test.mjs"), EXPORT, ALIASES, FIXTURE, FULL_INDEX],
            capture_output=True, text=True,
        )
        print(p.stdout + p.stderr, end="")
        node_fail = p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if base_fails or node_fail:
        print(f"SEARCH REGRESSION: FAIL (baseline {base_fails}, behavior {'FAIL' if node_fail else 'PASS'})")
        return 1
    print("SEARCH REGRESSION: PASS (relation_card / combo / HCTZ / empty / surface / degrade / name_only / 배선 전부 불변)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
