#!/usr/bin/env python3
"""
validate_antacid_fex_dryrun_v1_2.py
MediStack — AT-FEX(펙소페나딘 × Al/Mg 함유 제산제, avoid_concomitant) **live 통합 드라이런 검증**(읽기전용).
실제 export 는 한 바이트도 건드리지 않는다. integrate_antacid_fex_v1_2.py(dry-run)가 만든
data/review/antacid_fex_dryrun_v1_2.json 의 예상 relation 으로 **시뮬레이션 export(live + AT-FEX)** 를
임시 파일에 구성해, 통합이 일어났을 때의 안전성·계약을 미리 입증한다.

검사:
  0) 안전 불변: 라이브 export 무변경(relations==60·meta 60·published/clinical_reviewed=false·펙소페나딘 미존재).
  1) dry-run artifact 메타(live_promotion=0·published/clinical_reviewed=false·reviewed_by 공란·guard 위반 0).
  2) 예상 relation 필드: avoid_concomitant · counterpart_category=al_mg_antacid · mechanism=absorption ·
     evidence_level∈{high,moderate} · product_link_allowed=false · potassium_safety_card=false ·
     requires_clinical_review=false · draft-전용/금지 필드 미누출 · reviewed_by 부재 · source itemSeq ·
     display_text_ko == draft AT-01 verbatim.
  3) 시뮬레이션 export 가 **v0.2 export validator PASS**(avoid_concomitant 가 #15 가드 하 허용됨을 입증).
  4) full index/aliases 무변경(펙소페나딘 name_only 유지 · relation_card 1168 · name_only 16412).
  5) (node) 시뮬레이션 export 에서:
       - getFacets.nutrients 가 'Al/Mg 함유 제산제(약물)' 제외(영양소 오인 차단), 실제 영양소는 유지.
       - getFacets.actions 에 avoid_concomitant 포함 + '분류' facet 정렬(ACTION_ORDER)에서 끝자리 렌더.
       - renderRow/renderDetail 가 **전용 chip '병용금지(허가사항)'** 사용, generic '복용 간격'/'상태 모니터링' 미사용.
       - kicker 'Al/Mg 함유 제산제 관련 참고정보', '장기 복용 시 상태 확인' 미노출(병용금지 모순 제거).
       - 앱 카피 비지시('복용하지 마' 미노출), 제산제 명시, Mg 영양제 오인 0, 제품 0, 공통 면책.
사용: python3 scripts/validate_antacid_fex_dryrun_v1_2.py
종료코드: 0 PASS, 1 FAIL.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
SRC = os.path.join(REPO, "src", "js")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ARTIFACT = os.path.join(DATA, "review", "antacid_fex_dryrun_v1_2.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")

ING = "펙소페나딘"
NUT = "Al/Mg 함유 제산제(약물)"
LIVE_RELATIONS = 60          # AT-FEX 통합 전 라이브 baseline(불변이어야)
FULL_RELATION_CARD = 1168
FULL_NAME_ONLY = 16412
DRAFT_ONLY = {"draft_id", "harvester_candidate_id", "surface", "source_basis", "copy_risk_level",
              "confidence", "risk_level", "published", "clinical_reviewed", "reviewed_by",
              "review_required", "source_required", "do_not_implement_yet", "live_integration_forbidden",
              "adversarial_verified", "adversarial_verification", "representative_itemseq_policy",
              "live_candidate_rank", "live_candidate_note", "online_reconcile", "note",
              "label_quote", "label_directive_type", "status", "source_confirmed", "relation_type"}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def main():
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] dry-run artifact 없음: {ARTIFACT}\n  먼저 `python3 scripts/integrate_antacid_fex_v1_2.py` 실행")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    rel = art.get("projected_live_relation") or {}
    meta = art.get("meta") or {}
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))

    # 0) 안전 불변 — 라이브 export 무변경
    ck(len(exp["relations"]) == LIVE_RELATIONS, f"라이브 relations != {LIVE_RELATIONS} ({len(exp['relations'])}) — 드라이런인데 변경됨")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, f"라이브 meta.relation_count != {LIVE_RELATIONS}")
    ck(exp["meta"].get("published") is False, "라이브 published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "라이브 clinical_reviewed != false")
    ck(not any(r.get("ingredient") == ING and r.get("counterpart_category") == "al_mg_antacid" for r in exp["relations"]),
       "펙소페나딘×al_mg_antacid 가 이미 라이브에 존재 — 드라이런 전제 위반(live 통합됨)")

    # 1) artifact 메타 안전
    ck(meta.get("live_promotion") == 0, f"artifact live_promotion != 0 ({meta.get('live_promotion')})")
    ck(meta.get("published") is False and meta.get("clinical_reviewed") is False, "artifact published/clinical_reviewed != false")
    ck((meta.get("reviewed_by") or "") == "", "artifact reviewed_by 비공란")
    ck(not meta.get("guard_target_violations"), f"통합 자격 가드 위반: {meta.get('guard_target_violations')}")

    # 2) 예상 relation 필드
    ck(rel.get("ingredient") == ING, f"ingredient != {ING}")
    ck(rel.get("nutrient") == NUT, f"nutrient != '{NUT}' ({rel.get('nutrient')})")
    ck(rel.get("recommended_action") == "avoid_concomitant", f"action != avoid_concomitant ({rel.get('recommended_action')})")
    ck(rel.get("counterpart_category") == "al_mg_antacid", f"counterpart_category != al_mg_antacid ({rel.get('counterpart_category')})")
    ck(rel.get("mechanism") == "absorption", f"mechanism != absorption ({rel.get('mechanism')})")
    ck(rel.get("evidence_level") in ("high", "moderate"), f"evidence_level enum 위반 ({rel.get('evidence_level')})")
    ck(rel.get("product_link_allowed") is False, "product_link_allowed != false")
    ck(rel.get("potassium_safety_card") is False, "potassium_safety_card != false")
    ck(rel.get("requires_clinical_review") is False, "requires_clinical_review != false")
    leaked = DRAFT_ONLY & set(rel.keys())
    ck(not leaked, f"draft-전용/금지 필드 누출: {sorted(leaked)}")
    ck("reviewed_by" not in rel, "reviewed_by 기재됨(미기재 필수)")
    src = rel.get("source") or {}
    ck(bool(re.search(r"itemSeq=\d+", src.get("url", ""))), "source url itemSeq 없음")
    ck("확인일" in (src.get("pointer") or ""), "source pointer 확인일 없음")
    at01 = next((d for d in draft["draft_relations"] if d["draft_id"] == "AT-01"), None)
    if at01:
        ck(rel.get("display_text_ko") == at01["display_text_ko"], "display_text_ko != draft AT-01 verbatim")
        ck(at01.get("adversarial_verified") is True, "draft AT-01 adversarial_verified != true(통합 자격)")

    # 시뮬레이션 export(live + AT-FEX) — 임시 파일(라이브 무수정)
    sim = json.loads(json.dumps(exp))
    sim["relations"] = sim["relations"] + [rel]
    sim["meta"]["relation_count"] = len(sim["relations"])
    tmp = tempfile.mkdtemp(prefix="ms_fex_dry_")
    sim_path = os.path.join(tmp, "sim_export.json")
    try:
        with open(sim_path, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)

        # 3) 시뮬레이션 export 가 v0.2 validator PASS
        p = subprocess.run([sys.executable, V0_2_VALIDATOR, sim_path], capture_output=True, text=True)
        ck(p.returncode == 0, f"시뮬레이션 export v0.2 validator FAIL\n{p.stdout[-400:]}")

        # 4) full index/aliases 무변경(펙소페나딘 name_only 유지)
        full = json.load(open(FULL, encoding="utf-8"))
        counts = full.get("meta", {}).get("counts", {})
        ck(counts.get("relation_card") == FULL_RELATION_CARD, f"full relation_card {counts.get('relation_card')} != {FULL_RELATION_CARD}")
        ck(counts.get("name_only") == FULL_NAME_ONLY, f"full name_only {counts.get('name_only')} != {FULL_NAME_ONLY}")
        fex_entries = [e for e in full.get("entries", []) if ING in (e.get("ingredient_name") or "")]
        not_nameonly = [e.get("item_seq") for e in fex_entries if e.get("display_mode") != "name_only"]
        ck(not not_nameonly, f"펙소페나딘 full index entry 가 name_only 아님: {not_nameonly[:3]}")

        # 5) node: facet 제외 + 전용 chip 렌더
        node_fail = run_node(sim_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"=== AT-FEX dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 시뮬 {len(sim['relations'])} ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails or node_fail:
        print(f"RESULT: FAIL — {len(fails)}건 + node({node_fail})")
        return 1
    print("RESULT: PASS — AT-FEX 통합 시 안전(시뮬 v0.2 PASS·영양소 facet 제외·avoid_concomitant 전용 chip·제품0·봉인) · 라이브 무수정")
    return 0


NODE = r"""
import { readFileSync } from 'node:fs';
import { getFacets, getRenderableRelations, findRelation, canShowProduct, showPotassiumNotice } from './guards.js';
import { renderDetail, renderRow, renderListControls } from './render.js';
const [,, expPath] = process.argv;
const data = JSON.parse(readFileSync(expPath, 'utf-8'));
let fails = 0;
const ck = (n, c) => { console.log((c?'[PASS] ':'[FAIL] ')+n); if(!c) fails++; };

const rels = getRenderableRelations(data);
const facets = getFacets(rels);
ck("getFacets.nutrients 에 'Al/Mg 함유 제산제(약물)' 미포함(영양소 오인 차단)", !facets.nutrients.includes('Al/Mg 함유 제산제(약물)'));
ck("getFacets.nutrients 는 실제 영양소만(마그네슘 등 포함)", facets.nutrients.includes('마그네슘'));
ck("getFacets.actions 에 avoid_concomitant 포함", facets.actions.includes('avoid_concomitant'));
ck("getFacets.actions 에 separation 포함(기존 보존)", facets.actions.includes('separation'));

// '분류' facet 정렬: ACTION_ORDER 에 avoid_concomitant 추가 → 전용 label '병용금지(허가사항)' 렌더(미상시 raw 키 노출 안 함)
const controls = renderListControls(facets, {});
ck("[facet] '분류' 그룹에 전용 label '병용금지(허가사항)' 렌더(raw 'avoid_concomitant' 미노출)",
   controls.includes('병용금지(허가사항)') && !controls.includes('>avoid_concomitant<'));

const fex = rels.find(r => r.ingredient === '펙소페나딘' && r.counterpart_category === 'al_mg_antacid');
ck("AT-FEX renderable 포함", !!fex);
if (fex) {
  ck("findRelation(id) 동작", !!findRelation(data, fex.id));
  ck("canShowProduct=false(제품 UI 미표시)", canShowProduct(fex) === false);
  ck("showPotassiumNotice=false(칼륨 카드 미표시)", showPotassiumNotice(fex) === false);
  const html = renderDetail(fex, data);
  const row = renderRow(fex);
  const appCopy = html.split('<div class="src"')[0];
  ck("[row] 전용 chip '병용금지(허가사항)' 표시", row.includes('병용금지(허가사항)'));
  ck("[row] generic chip('복용 간격'/'상태 모니터링') 미사용", !row.includes('복용 간격') && !row.includes('상태 모니터링'));
  ck("[detail] 전용 kicker 'Al/Mg 함유 제산제 관련 참고정보' 표시", html.includes('Al/Mg 함유 제산제 관련 참고정보'));
  ck("[detail] '장기 복용 시 상태 확인' 미노출(병용+장기 모순 제거)", !html.includes('장기 복용 시 상태 확인'));
  ck("[detail] 'Al/Mg 함유 제산제' 표시(제산제 명시)", html.includes('Al/Mg 함유 제산제') && html.includes('제산제'));
  ck("[detail] 펙소페나딘 표시", html.includes('펙소페나딘'));
  ck("[detail] 영양소 '× 마그네슘' 단독 미표시", !html.includes('>마그네슘<'));
  ck("[appcopy] avoid prohibition 보존('함께 복용하지 않도록') 노출", appCopy.includes('함께 복용하지 않도록'));
  ck("[appcopy] weak neutral('흡수에 영향') 미노출(다운그레이드 차단)", !appCopy.includes('흡수에 영향을 줄 수 있다는'));
  ck("[appcopy] 병용 옵션 전제('함께 사용하는 경우에는') 미노출", !appCopy.includes('함께 사용하는 경우에는'));
  ck("[appcopy] Mg 영양제 오인 미노출", !appCopy.includes('마그네슘 영양제') && !appCopy.includes('마그네슘 보충제'));
  ck("[appcopy] 직접 지시('복용하지 마') 미노출(앱 카피)", !appCopy.includes('복용하지 마'));
  ck("[appcopy] 상담 종결('약사 또는 의사에게 확인') 노출", appCopy.includes('약사 또는 의사에게 확인'));
  ck("[detail] 공통 면책 출력", html.includes(data.disclaimers.common));
  ck("[detail] 제품/구매/제휴 미노출", !html.includes('구매') && !html.includes('제휴') && !html.includes('affiliate'));
}
if (fails) { console.log('NODE: FAIL ('+fails+')'); process.exit(1); }
console.log('NODE: PASS');
"""


def run_node(sim_path):
    if not shutil.which("node"):
        print("[FATAL] node 미설치"); return 1
    print("--- node: facet 제외 + AT-FEX avoid_concomitant 전용 chip 렌더(시뮬 export) ---")
    tmp = tempfile.mkdtemp(prefix="ms_fex_node_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        json.dump({"type": "module"}, open(os.path.join(tmp, "package.json"), "w"))
        open(os.path.join(tmp, "t.mjs"), "w", encoding="utf-8").write(NODE)
        p = subprocess.run(["node", os.path.join(tmp, "t.mjs"), sim_path], capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
