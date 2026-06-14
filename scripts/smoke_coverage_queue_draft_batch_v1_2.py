#!/usr/bin/env python3
"""
smoke_coverage_queue_draft_batch_v1_2.py
MediStack — coverage-queue draft batch(CQFxx) **render 안전성 사전검증** smoke
(실제 src/js/render.js + guards.js 사용). smoke_factory_draft_batch_v1_2.py 패턴 승계.

목적: 이 draft 들이 **승격될 경우** 앱에서 안전하게 렌더되는지 미리 확인(라이브 미반영).
검증(각 draft): 본문 노출 · 출처(nedrug) 노출 · 공통 면책 노출 · 금지어휘 0 · 외부링크=nedrug만 ·
  칼륨 행→칼륨주의/임의보충위험/link=false · absorption 행→영양소·'흡수' 문맥.
count=0 이면 자동 PASS(렌더 대상 없음 — 잘못된 relation 차단이 처리량보다 우선).

사용: python3 scripts/smoke_coverage_queue_draft_batch_v1_2.py
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
BATCH = os.path.join(DATA, "coverage_queue_draft_batch_v1_2.json")

TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { renderDetail } from './render.js';

const [,, exportPath, batchPath] = process.argv;
const data = JSON.parse(readFileSync(exportPath, 'utf-8'));
const batch = JSON.parse(readFileSync(batchPath, 'utf-8'));
const drafts = batch.draft_relations;

let fails = 0;
const check = (name, cond, extra) => {
  if (!cond) { console.log('[FAIL] ' + name + (extra !== undefined ? `  (${extra})` : '')); fails++; }
};
const BANNED = ['드세요', '복용하세요', '피하세요', '추천', '구매', '제품 추천', '구입', '클릭', '할인', '쿠폰', '치료합니다', '예방합니다'];

if (drafts.length === 0) {
  console.log('COVERAGE-QUEUE DRAFT BATCH v1.2 SMOKE: PASS (count=0, 렌더 대상 없음 — 정상)');
  process.exit(0);
}
for (const r of drafts) {
  const html = renderDetail(r, data);
  const tag = `${r.draft_id} ${r.ingredient}×${r.nutrient}`;
  check(`${tag} 본문 노출`, html.includes(r.display_text_ko));
  check(`${tag} 출처 nedrug`, html.includes('출처') && html.includes('nedrug.mfds.go.kr'));
  check(`${tag} 공통 면책`, html.includes('class="disc"'));
  for (const b of BANNED) check(`${tag} 금지어휘 없음 ${JSON.stringify(b)}`, !html.includes(b));
  const ext = [...html.matchAll(/href="(https?:[^"]+)"/g)].map((m) => m[1]);
  check(`${tag} 외부링크=nedrug만`, ext.every((u) => u.includes('nedrug.mfds.go.kr')), JSON.stringify(ext));
  if (r.nutrient === '칼륨') {
    check(`${tag} 칼륨 주의 박스`, html.includes('칼륨 주의'));
    check(`${tag} product_link_allowed=false`, r.product_link_allowed === false);
    check(`${tag} 임의 보충 위험 고지`, html.includes('임의로 보충하면 위험'));
  }
  if (r.mechanism === 'absorption') {
    check(`${tag} 흡수 문맥`, html.includes('흡수') && html.includes(r.nutrient));
  }
}

console.log('');
if (fails) { console.log('COVERAGE-QUEUE DRAFT BATCH v1.2 SMOKE: FAIL (' + fails + ')'); process.exit(1); }
console.log('COVERAGE-QUEUE DRAFT BATCH v1.2 SMOKE: PASS (' + drafts.length + ' drafts render-safe)');
"""


def main():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — ES module smoke 불가")
        return 1
    tmp = tempfile.mkdtemp(prefix="ms_cq_draft_v1_2_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(["node", os.path.join(tmp, "test.mjs"), EXPORT, BATCH],
                           capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
