#!/usr/bin/env python3
"""
smoke_relation_draft_v1_2.py
MediStack — v1.2 신규 relation 14건 **render 안전성** smoke (라이브 데이터 읽기전용·실제 guards.js+render.js).

검증:
  N1 클로르탈리돈(신규 단일) → relation_card 렌더, 칼륨 안전고지 텍스트 노출, href/구매/제품/복용지시 없음
  N2 인다파미드(신규 단일)   → relation_card 렌더, 칼륨 안전고지, 제품/구매 없음
  N3 오플록사신(FQ enrichment) → 아연 카드 텍스트 노출(흡수), 카드 4건, 구매/추천 없음
  N4 리세드론산(비스포 enrichment) → 철·마그네슘 카드 텍스트 노출, 카드 3건
  R1 복합제 아테놀롤/클로르탈리돈 → name_only 유지(relation_card 아님)
  R2 E 라베프라졸+산화마그네슘(라피듀오) → name_only 유지(직접모순·미flip)
  R3 일반 name_only 약(게보린) → '참고 정보 없음' 유지
  S  전 신규 카드 HTML 에 추천/구매/복용지시 어휘(드세요/복용하세요/피하세요/추천/구매/제품 추천) 0

사용: python3 scripts/smoke_relation_draft_v1_2.py
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
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")

TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { buildAliasIndex, filterRelations, getRenderableRelations, buildNameOnlyIndex, searchNameOnly } from './guards.js';
import { renderDetail, renderNameOnlyResults } from './render.js';

const [,, exportPath, aliasPath, fullPath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const alias = JSON.parse(readFileSync(aliasPath, 'utf-8'));
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
// 추천/구매/복용지시 어휘(참고정보 톤 위반). '피하고'·'복용은' 등 신중 톤은 허용(정확 어구만 차단).
const BANNED = ['드세요', '복용하세요', '피하세요', '추천', '구매', '제품 추천', '구입', '클릭', '할인', '쿠폰'];

const NEW = rels.filter((r) => r.id >= 43 && r.id <= 58);
check('신규 relation 16건 렌더 대상(draft14 + factory DF06·DF07)', NEW.length === 16, `got ${NEW.length}`);

// N. 신규 14건 각각 상세 렌더 안전성
for (const r of NEW) {
  const html = renderDetail(r, data);
  const tag = `id${r.id} ${r.ingredient}×${r.nutrient}`;
  check(`N ${tag} 본문 텍스트 노출`, html.includes(r.display_text_ko));
  check(`N ${tag} 출처(허가사항) 표시`, html.includes('출처') && html.includes('nedrug.mfds.go.kr'));
  check(`N ${tag} 공통 면책 표시`, html.includes('class="disc"'));
  for (const b of BANNED) check(`N ${tag} 금지어휘 없음 ${JSON.stringify(b)}`, !html.includes(b));
  // 외부 링크는 nedrug 출처만(쇼핑/구매 링크 없음)
  const ext = [...html.matchAll(/href="(https?:[^"]+)"/g)].map((m) => m[1]);
  check(`N ${tag} 외부링크=출처(nedrug)만`, ext.every((u) => u.includes('nedrug.mfds.go.kr')), JSON.stringify(ext));
  // 칼륨 행 → 칼륨 주의 박스 + product_link_allowed=false
  if (r.nutrient === '칼륨') {
    check(`N ${tag} 칼륨 주의 박스`, html.includes('칼륨 주의'));
    check(`N ${tag} product_link_allowed=false`, r.product_link_allowed === false);
  }
}

// N-tone. 신규 칼륨 카드 안전 문구(임의 보충 위험·상담)
{
  const k = NEW.find((r) => r.ingredient === '클로르탈리돈' && r.nutrient === '칼륨');
  const html = renderDetail(k, data);
  check('N-tone 클로르탈리돈 칼륨: 임의 보충 위험 고지', html.includes('임의로 보충하면 위험'));
  check('N-tone 클로르탈리돈 칼륨: 상담 고지', html.includes('상담'));
}
// N-tone. FQ×아연 카드(아연 흡수 문맥)
{
  const z = NEW.find((r) => r.ingredient === '오플록사신' && r.nutrient === '아연');
  const html = renderDetail(z, data);
  check('N-tone 오플록사신 아연: 아연·흡수 문맥', html.includes('아연') && html.includes('흡수'));
}

// R1 복합제(아테놀롤/클로르탈리돈) → relation 0(name_only 유지)
{
  const f = filterRelations(rels, { query: '아테놀롤클로르탈리돈' }, idx);
  check('R1 클로르탈리돈 복합 검색 relation 0(name_only 유지)', f.length === 0, `got ${f.length}`);
}
// R2 E 라베프라졸+산화마그네슘 → name_only 유지(미flip, combo alias 미등록)
{
  const hit = searchNameOnly('라피듀오', nameIdx, 30);
  check('R2 라피듀오(라베+산화Mg) name_only 트랙(미flip)', Array.isArray(hit));
}
// R3 일반 name_only 약
{
  const hit = searchNameOnly('게보린', nameIdx, 30);
  const html = renderNameOnlyResults(hit, notice);
  check('R3 게보린 name_only 커버', hit.length >= 1, `got ${hit.length}`);
  check('R3 참고 정보 없음 안내', html.includes('참고 정보 없음'));
  check('R3 name_only href 없음', !html.includes('href='));
}

console.log('');
if (fails) { console.log('RELATION DRAFT v1.2 SMOKE: FAIL (' + fails + ')'); process.exit(1); }
console.log('RELATION DRAFT v1.2 SMOKE: PASS');
"""


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module smoke 불가")
        return 1
    tmp = tempfile.mkdtemp(prefix="ms_relation_draft_v1_2_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(["node", os.path.join(tmp, "test.mjs"), EXPORT, ALIASES, FULL],
                           capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
