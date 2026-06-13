#!/usr/bin/env python3
"""
smoke_disclaimer_render.py
MediStack 공개 전 법적 안전장치: 상태별 필수 면책/고지 문구 렌더 검증(라이브 데이터 읽기 전용).

목적:
  "면책 문구가 소스 파일 어딘가에 존재" 만으로는 PASS 시키지 않는다. 실제 렌더 함수
  (render.js renderDetail / renderNameOnlyResults, states.js renderEmpty / renderNoResults /
  renderError)를 node 에서 직접 호출해 **반환 HTML** 에 필수 고지가 실제로 포함되는지 확인한다.
  상태별(relation_card / name_only / empty / no-result / error) 누락 여부를 검사한다.

  기대 면책 문구는 라이브 데이터에서 런타임 로드(데이터-구동) → 렌더 함수가 그 문구를
  실제 출력하는지 본다. 따라서 문구가 바뀌어도, 렌더가 데이터 면책을 떨구면 즉시 FAIL.

검사 상태:
  S1 relation_card  : renderDetail 이 전 30 renderable 관계에서 disclaimers.common 출력(load-bearing)
  S2 relation_card  : 칼륨 행(17/19/30)에서 potassium_notice + '칼륨 주의' 출력 / 비칼륨 행엔 미출력
  S3 fail-safe      : commonDisclaimer(data) truthy · common 제거 시 null (mountDetail 가드 발동 근거)
  S4 source 상속    : renderDetail 이 관계 source(출처 + url) 출력(relation_card 558 → relation 30 상속)
  S5 name_only      : renderNameOnlyResults 가 name_only_notice + '참고 정보 없음' 출력, 의학/제품/링크/출처 0
  S6 empty          : renderEmpty 가 disclaimers.empty_state 출력
  S7 no_results     : renderNoResults 가 무매치 안내 출력(‘안전/안심’ 류 금지)
  S8 error          : renderError 가 재시도 안내 출력
  S9 coverage       : 렌더 가능한 모든 상태에 필수 고지 1개 이상 — 누락 0

  render.js/states.js/guards.js 는 ES module 이고 repo 에 package.json 이 없으므로 임시 디렉토리에
  복사 + package.json {"type":"module"} 후 node import. (states.js→render.js→guards.js 의존 → 3개 모두 복사)

사용: python3 scripts/smoke_disclaimer_render.py
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
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
FIXTURE = os.path.join(HERE, "fixtures", "disclaimer_render_v1_1.json")

TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { getRenderableRelations, commonDisclaimer, potassiumNotice, showPotassiumNotice,
         buildNameOnlyIndex, searchNameOnly } from './guards.js';
import { renderDetail, renderNameOnlyResults } from './render.js';
import { renderEmpty, renderNoResults, renderError } from './states.js';

const [,, exportPath, fullPath, fixturePath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const full = JSON.parse(readFileSync(fullPath, 'utf-8'));
const fx = JSON.parse(readFileSync(fixturePath, 'utf-8'));

let fails = 0;
const check = (name, cond, extra) => {
  console.log((cond ? '[PASS] ' : '[FAIL] ') + name + (extra !== undefined ? `  (${extra})` : ''));
  if (!cond) fails++;
};

const rels = getRenderableRelations(data);
const common = data.disclaimers.common;
const kNotice = data.disclaimers.potassium_notice;
const emptyText = data.disclaimers.empty_state;
const nameNotice = full.meta && full.meta.name_only_notice;

// ── S0. precondition: common 면책이 비어있지 않아야 S1/S9 의 includes(common) 이 vacuous(빈문자열→항상참) 하지 않다 ──
check(`S0[precondition] common 면책 non-empty(빈문자열이면 includes 항상참 → vacuous 방지)`,
  typeof common === 'string' && common.trim().length > 10, `len ${common ? common.length : 0}`);
check(`S0[precondition] commonDisclaimer(data) === data.disclaimers.common (가드 일치)`, commonDisclaimer(data) === common);

// ── S1. relation_card detail: 전 30 renderable 관계 HTML 에 common 면책 포함(load-bearing) ──
let s1miss = 0;
for (const r of rels) { if (!renderDetail(r, data).includes(common)) s1miss++; }
check(`S1[relation_card] renderDetail 전 ${rels.length}건에 common 면책 포함`, s1miss === 0, `누락 ${s1miss}`);

// ── S2. 칼륨 행: potassium_notice + '칼륨 주의' 출력 / 비칼륨 행엔 '칼륨 주의' 미출력 ──
const kRels = rels.filter(showPotassiumNotice);
const nkRels = rels.filter((r) => !showPotassiumNotice(r));
check(`S2[potassium] 칼륨 행 ${kRels.length}건 식별(id ${kRels.map(r=>r.id).join('/')})`, kRels.length > 0);
// 분할 합 == 전체 & 비칼륨 > 0 — showPotassiumNotice 가 always-true 로 붕괴하면 비칼륨 누출 루프가 vacuous 해지는 것 방지
check(`S2[precondition] 칼륨+비칼륨 합 == 전체 ${rels.length} · 비칼륨 > 0`,
  (kRels.length + nkRels.length === rels.length) && nkRels.length > 0, `k${kRels.length}+nk${nkRels.length}`);
let s2kmiss = 0;
for (const r of kRels) { const h = renderDetail(r, data); if (!(h.includes(kNotice) && h.includes('칼륨 주의'))) s2kmiss++; }
check(`S2[potassium] 칼륨 행 전건 potassium_notice + '칼륨 주의' 출력`, s2kmiss === 0, `누락 ${s2kmiss}`);
let s2nleak = 0;
for (const r of nkRels) { if (renderDetail(r, data).includes('칼륨 주의')) s2nleak++; }
check(`S2[potassium] 비칼륨 행 ${nkRels.length}건에 '칼륨 주의' 미출력`, s2nleak === 0, `누출 ${s2nleak}`);

// ── S3. fail-safe: common 은 load-bearing — 제거 시 commonDisclaimer null(mountDetail 가드 발동) ──
check(`S3[failsafe] commonDisclaimer(data) truthy`, !!commonDisclaimer(data));
const stripped = { ...data, disclaimers: { ...data.disclaimers, common: '' } };
check(`S3[failsafe] common 제거 → commonDisclaimer null(상세 렌더 차단 근거)`, commonDisclaimer(stripped) === null);

// ── S4. source 상속: renderDetail 이 관계 source(출처 + url) 출력 → relation_card 558 가 relation 30 source 상속 ──
// precondition: 전 relation 에 source.url 존재해야 url 상속 검사가 vacuous(OR 단락) 하지 않다
check(`S4[precondition] 전 ${rels.length} relation 에 source.url 존재(url 검사 non-vacuous)`,
  rels.filter((r) => r.source && r.source.url).length === rels.length, `${rels.filter((r)=>r.source&&r.source.url).length}/${rels.length}`);
let s4miss = 0;
for (const r of rels) {
  const h = renderDetail(r, data);
  const okUrl = !r.source || !r.source.url || h.includes(r.source.url);
  if (!(h.includes('출처') && okUrl)) s4miss++;
}
check(`S4[source] renderDetail 전건 '출처' + source.url 출력(상속 구조)`, s4miss === 0, `누락 ${s4miss}`);

// ── S5. name_only: notice + '참고 정보 없음' 출력, 의학/상호작용/영양소/제품/링크/출처 0 ──
const matches = searchNameOnly(fx.name_only_query_covered, buildNameOnlyIndex(full), 30);
check(`S5[name_only] '${fx.name_only_query_covered}' name_only 매치 존재`, matches.length > 0, `got ${matches.length}`);
const noHtml = renderNameOnlyResults(matches, nameNotice);
check(`S5[name_only] name_only_notice 출력`, !!nameNotice && noHtml.includes(nameNotice));
for (const s of fx.name_only_required) check(`S5[name_only] 필수 '${s}' 출력`, noHtml.includes(s));
for (const s of fx.name_only_forbidden) check(`S5[name_only] 금지 '${s}' 미출력`, !noHtml.includes(s));
// notice 부재(빈문자열)여도 fallback 으로 상담 안내 유지
const noHtmlFb = renderNameOnlyResults(matches, '');
check(`S5[name_only] notice 부재 → fallback 상담 안내 유지`, noHtmlFb.includes('상담') && noHtmlFb.includes('참고 정보 없음'));
// 무매치 → 카드 없음(빈 문자열)
check(`S5[name_only] 무매치 → 빈 출력(카드 없음)`, renderNameOnlyResults([], nameNotice) === '');

// ── S6. empty: empty_state 출력 + 안심/안전 류 금지 ──
const emptyHtml = renderEmpty(data);
check(`S6[empty] renderEmpty 에 empty_state 출력`, emptyHtml.includes(emptyText));
for (const s of fx.reassurance_forbidden) check(`S6[empty] 금지 '${s}' 미출력`, !emptyHtml.includes(s));

// ── S7. no_results: 무매치 안내 + 안심/안전 금지 ──
const nrHtml = renderNoResults();
check(`S7[no_results] 무매치 안내 출력`, nrHtml.includes('참고 정보가 없습니다'));
for (const s of fx.reassurance_forbidden) check(`S7[no_results] 금지 '${s}' 미출력`, !nrHtml.includes(s));

// ── S8. error: 재시도 안내 ──
const errHtml = renderError();
check(`S8[error] 재시도 안내 출력`, errHtml.includes('다시 시도') && errHtml.includes('불러오지 못했'));

// ── S9. coverage: 핵심 상태 필수 고지 누락 0 종합 ──
const cov = (s1miss === 0) && (s2kmiss === 0) && renderEmpty(data).includes(emptyText) &&
            renderNameOnlyResults(matches, nameNotice).includes('참고 정보 없음');
check(`S9[coverage] relation_card·name_only·empty 필수 고지 누락 0`, cov);

console.log('');
if (fails) { console.log('NODE SECTION (S1~S9): FAIL (' + fails + ')'); process.exit(1); }
console.log('NODE SECTION (S1~S9): PASS');
"""


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module 렌더 smoke 불가")
        return 1
    print("=== 상태별 필수 면책/고지 렌더 검증 (실제 render.js + states.js + guards.js) ===")
    tmp = tempfile.mkdtemp(prefix="ms_disclaimer_render_")
    try:
        for fn in ("guards.js", "render.js", "states.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(
            ["node", os.path.join(tmp, "test.mjs"), EXPORT, FULL_INDEX, FIXTURE],
            capture_output=True, text=True,
        )
        print(p.stdout + p.stderr, end="")
        node_fail = p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if node_fail:
        print("DISCLAIMER RENDER SMOKE: FAIL")
        return 1
    print("DISCLAIMER RENDER SMOKE: PASS (relation_card / name_only / empty / no-result / error 상태별 필수 고지 실제 렌더 확인)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
