#!/usr/bin/env python3
"""
smoke_antacid_interaction_v1_2.py
MediStack antacid_interaction 카피 **렌더 시뮬레이션 스모크**(읽기전용).
표면 카피가 (a)출처 귀속·비지시(앱이 '복용하지 마세요'라고 지시하지 않음), (b)directive 별 충실성
— avoid_concomitant=prohibition 보존('함께 복용하지 않도록')+weak neutral 다운그레이드 차단,
separation/coadmin_caution=중립 병용 프레이밍 / 공통으로 '시간 간격 두세요' 약화 금지 —,
(c)상담 종결, (d)상대=제산제 명시(Mg 영양제 오인 0)인지, 내부 directive/label_quote 가 원문 강도를
보존하는지 시뮬레이션 점검한다. node 렌더는 action chip(separation→'복용 간격'/monitoring→'상태 모니터링'/
avoid_concomitant→전용 '병용금지(허가사항)')도 directive 정합으로 검사한다 — avoid_concomitant 카드는 전용
chip/kicker 노출 + generic '상태 모니터링'/'복용 간격'/'장기 복용 시 상태 확인' 미노출(병용금지 모순 제거)을 입증.
종료코드: 0 PASS, 1 FAIL.
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
DRAFT = os.path.join(REPO, "data", "drafts", "antacid_interaction_draft_batch_v1_2.json")


def main():
    d = json.load(open(DRAFT, encoding="utf-8"))
    fails = []
    n = 0
    for r in d.get("draft_relations", []):
        did = r["draft_id"]
        disp = r.get("display_text_ko", "")
        directive = r.get("label_directive_type")
        n += 1
        # (a) 출처 귀속·비지시: '허가사항 문구가 있습니다' 포함, 직접 지시('복용하지 마세요') 없음
        if "허가사항 문구가 있습니다" not in disp:
            fails.append(f"{did}: 출처 귀속('허가사항 문구가 있습니다') 누락 — 비지시성 약화")
        if "복용하지 마세요" in disp:
            fails.append(f"{did}: 직접 지시('복용하지 마세요') 노출 — 앱 지시 금지")
        # (b) directive 별 프레이밍 충실성:
        #   avoid_concomitant → prohibition 보존('함께 복용하지 않도록'), weak neutral('흡수에 영향') 다운그레이드 금지
        #   separation/coadmin_caution → 중립 병용 프레이밍('함께 사용할 때')
        if directive == "avoid_concomitant":
            if "함께 복용하지 않도록" not in disp:
                fails.append(f"{did}: avoid_concomitant prohibition 보존('함께 복용하지 않도록') 누락 — 다운그레이드")
            if "흡수에 영향을 줄 수 있다는" in disp:
                fails.append(f"{did}: avoid_concomitant 에 weak neutral 카피('흡수에 영향') 노출 — prohibition 다운그레이드")
            if "함께 사용하는 경우에는" in disp:
                fails.append(f"{did}: avoid_concomitant 에 병용 옵션 전제('함께 사용하는 경우에는') 노출 — consult 다운그레이드")
        else:
            if "함께 사용할 때" not in disp:
                fails.append(f"{did}: 중립 병용 프레이밍('함께 사용할 때') 누락")
        if "시간 간격을 두세요" in disp or "간격을 두는 것이 도움" in disp:
            fails.append(f"{did}: separation 다운그레이드 표현 노출(라벨 강도 약화)")
        # (c) 상담 종결
        if "약사 또는 의사에게 확인" not in disp:
            fails.append(f"{did}: 상담 종결 누락")
        # (d) 상대=제산제 명시, Mg 영양제 오인 0
        if "제산제" not in disp:
            fails.append(f"{did}: 상대(제산제) 명시 누락")
        for bad in ("마그네슘 영양제", "마그네슘 보충제"):
            if bad in disp:
                fails.append(f"{did}: Mg 영양제 오인 표현 '{bad}'")
        # 내부 강도 보존: label_quote 비공란 + directive_type 유효
        if not (r.get("label_quote") or "").strip():
            fails.append(f"{did}: 내부 label_quote 공란(원문 강도 보존 실패)")
        if directive not in ("avoid_concomitant", "separation", "coadmin_caution"):
            fails.append(f"{did}: label_directive_type 부정")
    print(f"=== antacid_interaction smoke (1) 카피 시뮬레이션: {n}개 ===")
    for f in fails:
        print(f"[FAIL] {f}")
    print("(1) " + ("FAIL %d건" % len(fails) if fails else "PASS — 출처 귀속·비지시·병용 프레이밍 유지·상담 종결·제산제 명시(Mg 오인 0)·내부 강도 보존"))

    # (2) 실제 render.js 호출 렌더 smoke(generic 카드가 antacid 를 안전하게 표시하는지 — src 무수정 입증)
    print("")
    node_fail = run_node_render()

    print("")
    if fails or node_fail:
        print("ANTACID INTERACTION SMOKE: FAIL")
        return 1
    print("ANTACID INTERACTION SMOKE: PASS (카피 시뮬레이션 + 실제 render.js 렌더 모두 안전)")
    return 0


# ── (2) node 렌더 섹션: 기존 generic render.js/guards.js 가 antacid 표면을 안전하게 그리는지 ──
# 표면 매핑(surface.render_nutrient="Al/Mg 함유 제산제(약물)" + render_action="separation")으로
# generic relation 을 구성해 renderDetail/renderRow 를 실제 호출한다. src 는 수정하지 않는다.
# 앱 자체 카피의 비지시성은 '출처' 섹션 이전(heading/chip/bodytext)에서 검사한다 —
# source.pointer 는 라벨 원문 인용이라 directive 가 정당히 포함될 수 있다(forbidden 스캐너와 동일 원칙).
TEST_MJS = r"""
import { readFileSync } from 'node:fs';
import { isRenderable, canShowProduct, showPotassiumNotice } from './guards.js';
import { renderDetail, renderRow } from './render.js';

const [,, draftPath] = process.argv;
const d = JSON.parse(readFileSync(draftPath, 'utf-8'));
const data = { disclaimers: { common: '본 정보는 일반적인 참고용이며 의학적 진단·처방·복약지시가 아닙니다. 복용 판단은 약사 또는 의사와 상담하세요.' } };

let fails = 0;
const check = (name, cond, extra) => {
  console.log((cond ? '[PASS] ' : '[FAIL] ') + name + (extra !== undefined ? `  (${extra})` : ''));
  if (!cond) fails++;
};

for (const r of d.draft_relations) {
  const did = r.draft_id, ing = r.ingredient, s = r.surface || {};
  const directive = r.label_directive_type;
  // 표면 매핑으로 generic 렌더 relation 구성(nutrient 슬롯 = Al/Mg 제산제 '약물' — 영양소 아님)
  const rel = {
    id: did, ingredient: ing, nutrient: s.render_nutrient, recommended_action: s.render_action,
    display_text_ko: r.display_text_ko, product_link_allowed: r.product_link_allowed,
    potassium_safety_card: r.potassium_safety_card, source: r.source,
  };
  check(`${did}(${ing})[renderable] generic 렌더 필수필드 충족`, isRenderable(rel));
  check(`${did}(${ing})[guard] canShowProduct=false(제품 UI 미표시)`, canShowProduct(rel) === false);
  check(`${did}(${ing})[guard] showPotassiumNotice=false(칼륨 카드 미표시)`, showPotassiumNotice(rel) === false);
  const html = renderDetail(rel, data);
  const row = renderRow(rel);
  const appCopy = html.split('<div class="src"')[0];  // '출처' 섹션 이전 = 앱 자체 카피(heading/chip/bodytext)
  check(`${did}(${ing})[detail] 상대 'Al/Mg 함유 제산제' 표시(제산제 명시)`, html.includes('Al/Mg 함유 제산제') && html.includes('제산제'));
  check(`${did}(${ing})[detail] 약물명 표시`, html.includes(ing));
  check(`${did}(${ing})[detail] 영양소 카드 아님 — '× 마그네슘'(영양소) 단독 미표시`, !html.includes('>마그네슘<'));
  check(`${did}(${ing})[appcopy] Mg 영양제 오인 표현 미노출`, !appCopy.includes('마그네슘 영양제') && !appCopy.includes('마그네슘 보충제'));
  check(`${did}(${ing})[appcopy] 직접 복용 지시('복용하지 마') 미노출(앱 카피)`, !appCopy.includes('복용하지 마'));
  check(`${did}(${ing})[appcopy] 참고정보 프레이밍('허가사항 문구가 있습니다') 노출`, appCopy.includes('허가사항 문구가 있습니다'));
  check(`${did}(${ing})[appcopy] 상담 종결('약사 또는 의사에게 확인') 노출`, appCopy.includes('약사 또는 의사에게 확인'));
  // directive 별 카피 충실성(Option A): avoid_concomitant 는 prohibition 보존 + weak neutral 다운그레이드 차단
  if (directive === 'avoid_concomitant') {
    check(`${did}(${ing})[appcopy] avoid_concomitant prohibition 보존('함께 복용하지 않도록') 노출`, appCopy.includes('함께 복용하지 않도록'));
    check(`${did}(${ing})[appcopy] avoid_concomitant 에 weak neutral('흡수에 영향') 미노출(다운그레이드 차단)`, !appCopy.includes('흡수에 영향을 줄 수 있다는'));
    check(`${did}(${ing})[appcopy] avoid_concomitant 에 병용 옵션 전제('함께 사용하는 경우에는') 미노출`, !appCopy.includes('함께 사용하는 경우에는'));
    check(`${did}(${ing})[chip] avoid 전용 chip('병용금지(허가사항)') 노출`, html.includes('병용금지(허가사항)'));
    check(`${did}(${ing})[chip] generic monitoring('상태 모니터링') 미노출(모순 제거)`, !html.includes('상태 모니터링'));
    check(`${did}(${ing})[chip] generic separation('복용 간격') 미노출(다운그레이드 제거)`, !html.includes('복용 간격'));
    check(`${did}(${ing})[kicker] '장기 복용 시 상태 확인' 미노출(병용+장기 모순 제거)`, !html.includes('장기 복용 시 상태 확인'));
    check(`${did}(${ing})[kicker] avoid 전용 kicker('관련 참고정보') 노출`, html.includes('관련 참고정보'));
  } else {
    check(`${did}(${ing})[appcopy] 중립 병용 프레이밍('함께 사용할 때') 노출`, appCopy.includes('함께 사용할 때'));
  }
  check(`${did}(${ing})[detail] 공통 면책 출력(fail-safe)`, html.includes(data.disclaimers.common));
  check(`${did}(${ing})[detail] 출처 귀속(허가사항) 출력`, html.includes('출처'));
  check(`${did}(${ing})[detail] 제품/구매/제휴 미노출`, !html.includes('구매') && !html.includes('제휴') && !html.includes('affiliate') && !html.includes('buy_links'));
  // action chip: separation→'복용 간격' / monitoring→'상태 모니터링' / avoid_concomitant→전용 '제산제 동시 사용 주의'.
  const CHIP_BY_ACTION = { separation: '복용 간격', monitoring: '상태 모니터링', avoid_concomitant: '병용금지(허가사항)' };
  const chipLabel = CHIP_BY_ACTION[s.render_action] || '';
  check(`${did}(${ing})[row] action chip('${chipLabel}') 표시`, !!chipLabel && row.includes(chipLabel));
  if (directive === 'avoid_concomitant') {
    check(`${did}(${ing})[row] avoid_concomitant 에 generic chip(복용 간격/상태 모니터링) 미사용`, !row.includes('복용 간격') && !row.includes('상태 모니터링'));
  }
}

console.log('');
if (fails) { console.log('(2) NODE RENDER (antacid surface): FAIL (' + fails + ')'); process.exit(1); }
console.log('(2) NODE RENDER (antacid surface): PASS — generic 카드가 antacid 를 영양소와 구분해 안전 표시(제산제 명시·비지시·면책·제품 0)');
"""


def run_node_render():
    if not shutil.which("node"):
        print("[FATAL] node 미설치 — render.js 렌더 smoke 불가")
        return 1
    print("=== antacid_interaction smoke (2) 실제 render.js 렌더(generic 카드 안전성) ===")
    tmp = tempfile.mkdtemp(prefix="ms_antacid_render_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        with open(os.path.join(tmp, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"type": "module"}, f)
        with open(os.path.join(tmp, "test.mjs"), "w", encoding="utf-8") as f:
            f.write(TEST_MJS)
        p = subprocess.run(["node", os.path.join(tmp, "test.mjs"), DRAFT], capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
