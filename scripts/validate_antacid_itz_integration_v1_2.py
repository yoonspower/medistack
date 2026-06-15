#!/usr/bin/env python3
"""
validate_antacid_itz_integration_v1_2.py
MediStack — antacid_interaction **첫 live relation(AT-05 이트라코나졸×Al/Mg 제산제)** 통합 검증(읽기전용).

검사:
  1) export relations == 60 · meta.relation_count == 60 · published/clinical_reviewed=false.
  2) AT-ITZ live relation(이트라코나졸 × 'Al/Mg 함유 제산제(약물)') 정확히 1건:
     counterpart_category=al_mg_antacid · recommended_action=separation · mechanism=absorption ·
     evidence_level=high · product_link_allowed=false · potassium_safety_card=false ·
     requires_clinical_review=false · draft-전용/금지 필드 미누출 · reviewed_by 미기재 ·
     source itemSeq url + pointer 확인일 · display_text_ko == draft AT-05 verbatim.
  3) 기존 59 relation(ids) 보존.
  4) full index 무변경(relation_card/name_only/total counts 유지 · 이트라코나졸 name_only).
  5) (node) getFacets 가 'Al/Mg 함유 제산제(약물)' 를 영양소 facet 에서 제외 ·
     renderDetail/renderRow 가 AT-ITZ 를 안전 렌더(separation chip·제산제 명시·제품0·면책).
사용: python3 scripts/validate_antacid_itz_integration_v1_2.py
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

ING = "이트라코나졸"
NUT = "Al/Mg 함유 제산제(약물)"
# full index 무변경 baseline(AT-ITZ 는 name_only 유지 → flip 0)
FULL_RELATION_CARD = 1168
FULL_NAME_ONLY = 16412
DRAFT_ONLY = {"draft_id", "harvester_candidate_id", "surface", "source_basis", "copy_risk_level",
              "confidence", "risk_level", "published", "clinical_reviewed", "reviewed_by",
              "review_required", "source_required", "do_not_implement_yet", "live_integration_forbidden",
              "adversarial_verified", "adversarial_verification", "representative_itemseq_policy",
              "live_candidate_rank", "live_candidate_note", "online_reconcile", "note",
              "label_quote", "label_directive_type", "status", "source_confirmed"}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def main():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    draft = json.load(open(DRAFT, encoding="utf-8"))
    rels = exp["relations"]

    # 1) count + 봉인
    ck(len(rels) == 60, f"relations != 60 ({len(rels)})")
    ck(exp["meta"].get("relation_count") == 60, f"meta.relation_count != 60 ({exp['meta'].get('relation_count')})")
    ck(exp["meta"].get("published") is False, "published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "clinical_reviewed != false")

    # 2) AT-ITZ live relation 정확히 1건
    itz = [r for r in rels if r.get("ingredient") == ING and r.get("counterpart_category") == "al_mg_antacid"]
    ck(len(itz) == 1, f"AT-ITZ live relation {len(itz)}건(정확히 1 기대)")
    if len(itz) == 1:
        r = itz[0]
        ck(r.get("nutrient") == NUT, f"nutrient != '{NUT}' ({r.get('nutrient')})")
        ck(r.get("recommended_action") == "separation", f"action != separation ({r.get('recommended_action')})")
        ck(r.get("mechanism") == "absorption", f"mechanism != absorption ({r.get('mechanism')})")
        ck(r.get("evidence_level") == "high", f"evidence != high ({r.get('evidence_level')})")
        ck(r.get("product_link_allowed") is False, "product_link_allowed != false")
        ck(r.get("potassium_safety_card") is False, "potassium_safety_card != false")
        ck(r.get("requires_clinical_review") is False, "requires_clinical_review != false")
        leaked = DRAFT_ONLY & set(r.keys())
        ck(not leaked, f"draft-전용/금지 필드 누출: {sorted(leaked)}")
        ck("reviewed_by" not in r, "reviewed_by 기재됨(미기재 필수)")
        src = r.get("source") or {}
        ck(bool(re.search(r"itemSeq=\d+", src.get("url", ""))), "source url itemSeq 없음")
        ck("확인일" in (src.get("pointer") or ""), "source pointer 확인일 없음")
        ck(src.get("checked_at") is None, "source.checked_at 누출(라이브 스키마 아님)")
        # display 는 draft AT-05 verbatim
        at05 = next((d for d in draft["draft_relations"] if d["draft_id"] == "AT-05"), None)
        if at05:
            ck(r.get("display_text_ko") == at05["display_text_ko"], "display_text_ko != draft AT-05 verbatim")
            ck(at05.get("adversarial_verified") is True, "draft AT-05 adversarial_verified != true(통합 자격)")

    # 3) 기존 59 보존(신규 id 외 1-60 동일 집합)
    ids = sorted(r["id"] for r in rels)
    new_ids = [r["id"] for r in itz]
    old = set(ids) - set(new_ids)
    ck(old == (set(range(1, 61)) - {15}), f"기존 id 집합 변형(old={sorted(old)[:5]}...)")

    # 4) full index 무변경(이트라코나졸 name_only 유지)
    full = json.load(open(FULL, encoding="utf-8"))
    counts = full.get("meta", {}).get("counts", {})
    ck(counts.get("relation_card") == FULL_RELATION_CARD, f"full relation_card {counts.get('relation_card')} != {FULL_RELATION_CARD}")
    ck(counts.get("name_only") == FULL_NAME_ONLY, f"full name_only {counts.get('name_only')} != {FULL_NAME_ONLY}")
    itz_entries = [e for e in full.get("entries", []) if ING in (e.get("ingredient_name") or "")]
    not_nameonly = [e.get("item_seq") for e in itz_entries if e.get("display_mode") != "name_only"]
    ck(not not_nameonly, f"이트라코나졸 full index entry 가 name_only 아님: {not_nameonly[:3]}")

    # 5) node: facet 제외 + 안전 렌더
    node_fail = run_node(exp)

    print(f"=== antacid AT-ITZ integration validator: relations {len(rels)} · AT-ITZ {len(itz)}건 ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails or node_fail:
        print(f"RESULT: FAIL — {len(fails)}건 + node({node_fail})")
        return 1
    print("RESULT: PASS — AT-ITZ 첫 live antacid relation 안전 통합(영양소 facet 제외·separation 렌더·제품0·봉인·full index 무변경)")
    return 0


NODE = r"""
import { readFileSync } from 'node:fs';
import { getFacets, getRenderableRelations, findRelation, canShowProduct, showPotassiumNotice } from './guards.js';
import { renderDetail, renderRow } from './render.js';
const [,, expPath] = process.argv;
const data = JSON.parse(readFileSync(expPath, 'utf-8'));
let fails = 0;
const ck = (n, c) => { console.log((c?'[PASS] ':'[FAIL] ')+n); if(!c) fails++; };

const rels = getRenderableRelations(data);
const facets = getFacets(rels);
ck("getFacets.nutrients 에 'Al/Mg 함유 제산제(약물)' 미포함(영양소 오인 차단)", !facets.nutrients.includes('Al/Mg 함유 제산제(약물)'));
ck("getFacets.nutrients 는 실제 영양소만(마그네슘 등 포함)", facets.nutrients.includes('마그네슘'));
ck("getFacets.actions 에 separation 포함", facets.actions.includes('separation'));

const itz = rels.find(r => r.ingredient === '이트라코나졸' && r.counterpart_category === 'al_mg_antacid');
ck("AT-ITZ renderable 포함", !!itz);
if (itz) {
  ck("findRelation(id) 동작", !!findRelation(data, itz.id));
  ck("canShowProduct=false(제품 UI 미표시)", canShowProduct(itz) === false);
  ck("showPotassiumNotice=false(칼륨 카드 미표시)", showPotassiumNotice(itz) === false);
  const html = renderDetail(itz, data);
  const row = renderRow(itz);
  const appCopy = html.split('<div class="src"')[0];
  ck("[detail] 'Al/Mg 함유 제산제' 표시(제산제 명시)", html.includes('Al/Mg 함유 제산제') && html.includes('제산제'));
  ck("[detail] 이트라코나졸 표시", html.includes('이트라코나졸'));
  ck("[detail] 영양소 '× 마그네슘' 단독 미표시", !html.includes('>마그네슘<'));
  ck("[row] separation chip('복용 간격') 표시", row.includes('복용 간격'));
  ck("[appcopy] Mg 영양제 오인 미노출", !appCopy.includes('마그네슘 영양제') && !appCopy.includes('마그네슘 보충제'));
  ck("[appcopy] 직접 지시('복용하지 마') 미노출", !appCopy.includes('복용하지 마'));
  ck("[detail] 공통 면책 출력", html.includes(data.disclaimers.common));
  ck("[detail] 제품/구매/제휴 미노출", !html.includes('구매') && !html.includes('제휴') && !html.includes('affiliate'));
}
if (fails) { console.log('NODE: FAIL ('+fails+')'); process.exit(1); }
console.log('NODE: PASS');
"""


def run_node(exp):
    if not shutil.which("node"):
        print("[FATAL] node 미설치"); return 1
    print("--- node: facet 제외 + AT-ITZ 안전 렌더 ---")
    tmp = tempfile.mkdtemp(prefix="ms_itz_")
    try:
        for fn in ("guards.js", "render.js"):
            shutil.copy(os.path.join(SRC, fn), os.path.join(tmp, fn))
        json.dump({"type": "module"}, open(os.path.join(tmp, "package.json"), "w"))
        open(os.path.join(tmp, "t.mjs"), "w", encoding="utf-8").write(NODE)
        p = subprocess.run(["node", os.path.join(tmp, "t.mjs"), EXPORT], capture_output=True, text=True)
        print(p.stdout + p.stderr, end="")
        return p.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
