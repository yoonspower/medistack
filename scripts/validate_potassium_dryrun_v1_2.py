#!/usr/bin/env python3
"""
validate_potassium_dryrun_v1_2.py
MediStack — 칼륨 PM-ready 4건(DF01·DF04·DF05·DF-PRED-01 프레드니솔론) **live 통합 드라이런 검증**(읽기전용).
실제 export 는 한 바이트도 건드리지 않는다. integrate_potassium_pm_ready_v1_2.py(dry-run)가 만든
data/review/potassium_pm_ready_dryrun_v1_2.json 의 예상 relations 로 **시뮬레이션 export(live + 4)** 를
임시 파일에 구성해, 통합이 일어났을 때의 안전성·계약을 미리 입증한다.
(DF-PRED-01 은 data/review/prednisolone_potassium_draft_recheck_v1_3.json 에서 병합.)

검사:
  0) 안전 불변: 라이브 export 무변경(relations==60·meta 60·published/clinical=false·3성분 미존재).
  1) dry-run artifact 메타(live_promotion=0·published/clinical=false·reviewed_by 공란·guard_violations 0·whitelist).
  2) 예상 relations(3건) 필드: nutrient=칼륨 · mechanism=depletion · action=monitoring · evidence=high ·
     product_link_allowed=false · potassium_safety_card=true · requires_clinical_review=false ·
     counterpart_category 부재(칼륨은 영양소 — antacid 아님) · draft-전용 필드 미누출 · reviewed_by 부재 ·
     management_ko 통일문자열 정확 일치 · display(named) 약물명+장기/고용량/문의 종결 · source itemSeq.
  3) 시뮬레이션 export 가 **v0.2 export validator PASS**(칼륨 일관성 #11 등 전 검사 통과).
  4) full index/aliases 무변경(relation_card 1168 · name_only 16412 — 본 라운드는 full index 미수정).
  5) (node) 시뮬레이션 export 에서 각 칼륨 행:
       - getFacets.nutrients 가 '칼륨' 포함(영양소 facet 유지 — antacid 와 달리 제외 아님).
       - showPotassiumNotice=true · canShowProduct=false.
       - renderDetail 가 '칼륨 주의' 안전카드 + potassium_notice 노출 · '상태 모니터링' 라벨.
       - bodytext=비단정 상담문구(장기/고용량·문의) · 참고안내=anti-supplement(임의 보충 말고·상담 결정).
       - 칼륨 보충 권유/결핍 단정/제품/구매/제휴 0 · 공통 면책 출력.
사용: python3 scripts/validate_potassium_dryrun_v1_2.py
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
PM = os.path.join(DATA, "review", "potassium_depletion_pm_ready_v1_2.json")
PRED_DRAFT = os.path.join(DATA, "review", "prednisolone_potassium_draft_recheck_v1_3.json")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
ARTIFACT = os.path.join(DATA, "review", "potassium_pm_ready_dryrun_v1_2.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")

LIVE_RELATIONS = 60
FULL_RELATION_CARD = 1168
FULL_NAME_ONLY = 16412
# DF-PRED-01 프레드니솔론(소론도정) 합류 → 통합 준비 그룹 4건.
EXPECT_INGREDIENTS = {"메틸프레드니솔론", "아세타졸아미드", "아조세미드", "프레드니솔론"}
EXPECT_DRAFT_IDS = {"DF01", "DF04", "DF05", "DF-PRED-01"}
# 통합 대상 아님 — 시뮬 relations 에 절대 누출되면 안 됨(DF02 덱사메타손·CQF03 히드로코르티손·
# DF03 플루드로코르티손 = wording-review/hold, DF06/DF07 리오티로닌 = 비-칼륨·product_link_allowed=TRUE).
EXCLUDED_INGREDIENTS = {"덱사메타손", "히드로코르티손", "플루드로코르티손", "리오티로닌"}
UNIFIED_MGMT = "칼륨은 임의로 보충하지 말고, 보충 여부는 의사 또는 약사와 상담해 결정하세요."
DISPLAY_MUST = ["장기간 복용하거나 고용량", "칼륨 상태에 영향", "확인이 필요한지 문의"]
COPY_FORBIDDEN = ["칼륨을 보충", "칼륨제를", "칼륨 섭취를 늘", "결핍", "부족", "빠집니다",
                  "복용하세요", "구매", "제휴", "추천 영양제", "치료", "예방"]
# live relation 에 들어오면 안 되는 큐/드래프트 전용 키.
DRAFT_ONLY = {"draft_id", "source_confirmed", "adversarial_verified", "itemseq", "pm_readiness",
              "promotion_candidate", "long_term_high_dose_context", "final_display_text_ko",
              "final_display_text_ko_named", "final_management_ko", "published", "clinical_reviewed",
              "reviewed_by", "live_integration_forbidden", "classification_reason", "source_pointer",
              "counterpart_category", "status", "review_required", "source_required", "do_not_implement_yet"}

fails = []


def ck(ok, msg):
    if not ok:
        fails.append(msg)


def main():
    if not os.path.exists(ARTIFACT):
        print(f"[FATAL] dry-run artifact 없음: {ARTIFACT}\n  먼저 `python3 scripts/integrate_potassium_pm_ready_v1_2.py` 실행")
        return 1
    art = json.load(open(ARTIFACT, encoding="utf-8"))
    rels_new = art.get("projected_live_relations") or []
    meta = art.get("meta") or {}
    exp = json.load(open(EXPORT, encoding="utf-8"))
    pm = {i["draft_id"]: i for i in json.load(open(PM, encoding="utf-8")).get("items", [])}
    if os.path.exists(PRED_DRAFT):
        for i in json.load(open(PRED_DRAFT, encoding="utf-8")).get("items", []):
            pm.setdefault(i["draft_id"], i)

    # 0) 안전 불변 — 라이브 export 무변경
    ck(len(exp["relations"]) == LIVE_RELATIONS, f"라이브 relations != {LIVE_RELATIONS} ({len(exp['relations'])}) — 드라이런인데 변경됨")
    ck(exp["meta"].get("relation_count") == LIVE_RELATIONS, f"라이브 meta.relation_count != {LIVE_RELATIONS}")
    ck(exp["meta"].get("published") is False, "라이브 published != false")
    ck(exp["meta"].get("clinical_reviewed") is False, "라이브 clinical_reviewed != false")
    live_pot = {r.get("ingredient") for r in exp["relations"] if r.get("nutrient") == "칼륨"}
    ck(not (EXPECT_INGREDIENTS & live_pot), f"PM-ready 칼륨 성분이 이미 라이브에 존재(드라이런 전제 위반): {EXPECT_INGREDIENTS & live_pot}")

    # 0.5) 베이스라인 무결성 — 시뮬은 라이브 export 를 상속하므로, 시뮬 검증 전에 라이브 자체가 v0.2 계약을
    #      충족하는지 먼저 입증한다(손상된 베이스라인이 시뮬에 상속돼 우회되는 것 차단).
    p0 = subprocess.run([sys.executable, V0_2_VALIDATOR, EXPORT], capture_output=True, text=True)
    ck(p0.returncode == 0, f"라이브 export v0.2 validator FAIL(pre-check — 베이스라인 손상)\n{p0.stdout[-500:]}")

    # 1) artifact 메타 안전
    ck(meta.get("live_promotion") == 0, f"artifact live_promotion != 0 ({meta.get('live_promotion')})")
    ck(meta.get("published") is False and meta.get("clinical_reviewed") is False, "artifact published/clinical_reviewed != false")
    ck((meta.get("reviewed_by") or "") == "", "artifact reviewed_by 비공란")
    ck(not meta.get("guard_violations"), f"통합 자격 가드 위반: {meta.get('guard_violations')}")
    ck(set(meta.get("whitelist", [])) == EXPECT_DRAFT_IDS, f"whitelist != {sorted(EXPECT_DRAFT_IDS)} ({meta.get('whitelist')})")

    # 2) 예상 relations 필드
    ck(len(rels_new) == 4, f"예상 relations 4건 아님({len(rels_new)})")
    seen = set()
    for rel in rels_new:
        ing = rel.get("ingredient")
        seen.add(ing)
        tag = ing or "?"
        ck(rel.get("nutrient") == "칼륨", f"{tag}: nutrient != 칼륨 ({rel.get('nutrient')})")
        ck(rel.get("mechanism") == "depletion", f"{tag}: mechanism != depletion ({rel.get('mechanism')})")
        ck(rel.get("recommended_action") == "monitoring", f"{tag}: action != monitoring ({rel.get('recommended_action')})")
        ck(rel.get("evidence_level") == "high", f"{tag}: evidence != high ({rel.get('evidence_level')})")
        ck(rel.get("product_link_allowed") is False, f"{tag}: product_link_allowed != false")
        ck(rel.get("potassium_safety_card") is True, f"{tag}: potassium_safety_card != true")
        ck(rel.get("requires_clinical_review") is False, f"{tag}: requires_clinical_review != false")
        ck("counterpart_category" not in rel, f"{tag}: counterpart_category 누출(칼륨은 영양소)")
        leaked = DRAFT_ONLY & set(rel.keys())
        ck(not leaked, f"{tag}: draft-전용 필드 누출: {sorted(leaked)}")
        ck("reviewed_by" not in rel, f"{tag}: reviewed_by 기재됨")
        ck(rel.get("management_ko") == UNIFIED_MGMT, f"{tag}: management_ko 통일문구 불일치")
        disp = rel.get("display_text_ko") or ""
        ck(disp.startswith(ing or "\0"), f"{tag}: display 가 약물명으로 시작 안 함")
        for m in DISPLAY_MUST:
            ck(m in disp, f"{tag}: display 통일문구 누락('{m}')")
        for fb in COPY_FORBIDDEN:
            ck(fb not in disp and fb not in (rel.get("management_ko") or ""), f"{tag}: 칼륨 금지어 '{fb}'")
        src = rel.get("source") or {}
        ck(bool(re.search(r"itemSeq=\d+", src.get("url", ""))), f"{tag}: source url itemSeq 없음")
        ck("확인일" in (src.get("pointer") or ""), f"{tag}: source pointer 확인일 없음")
        # PM-ready 원본 named 카피와 verbatim 일치
        did = next((k for k, v in pm.items() if v["ingredient"] == ing), None)
        if did:
            ck(disp == pm[did]["final_display_text_ko_named"], f"{tag}: display != PM-ready named verbatim")
            ck(did in EXPECT_DRAFT_IDS, f"{tag}: draft_id {did} whitelist 밖")
    ck(seen == EXPECT_INGREDIENTS, f"성분 집합 불일치: {seen} != {EXPECT_INGREDIENTS}")
    leaked_excluded = EXCLUDED_INGREDIENTS & seen
    ck(not leaked_excluded, f"제외 대상(DF02/CQF03/DF03/DF06/DF07) 통합 누출: {leaked_excluded}")

    # 시뮬레이션 export(live + 3) — 임시 파일(라이브 무수정)
    sim = json.loads(json.dumps(exp))
    sim["relations"] = sim["relations"] + rels_new
    sim["meta"]["relation_count"] = len(sim["relations"])
    tmp = tempfile.mkdtemp(prefix="ms_pot_dry_")
    sim_path = os.path.join(tmp, "sim_export.json")
    node_fail = 1
    try:
        with open(sim_path, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)

        # 3) 시뮬레이션 export 가 v0.2 validator PASS
        p = subprocess.run([sys.executable, V0_2_VALIDATOR, sim_path], capture_output=True, text=True)
        ck(p.returncode == 0, f"시뮬레이션 export v0.2 validator FAIL\n{p.stdout[-500:]}")

        # 4) full index 무변경
        full = json.load(open(FULL, encoding="utf-8"))
        counts = full.get("meta", {}).get("counts", {})
        ck(counts.get("relation_card") == FULL_RELATION_CARD, f"full relation_card {counts.get('relation_card')} != {FULL_RELATION_CARD}")
        ck(counts.get("name_only") == FULL_NAME_ONLY, f"full name_only {counts.get('name_only')} != {FULL_NAME_ONLY}")

        # 5) node: 칼륨 안전카드 + 비단정 + 제품 0
        node_fail = run_node(sim_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"=== 칼륨 PM-ready dry-run 검증: 라이브 relations {len(exp['relations'])}(불변) · 시뮬 {len(sim['relations'])} ===")
    for f in fails:
        print(f"[FAIL] {f}")
    if fails or node_fail:
        print(f"RESULT: FAIL — {len(fails)}건 + node({node_fail})")
        return 1
    print(f"RESULT: PASS — 칼륨 {len(rels_new)}건 통합 시 안전(시뮬 v0.2 PASS·칼륨 안전카드·anti-supplement·제품0·봉인) · 라이브 무수정")
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
ck("getFacets.nutrients 에 '칼륨' 포함(영양소 facet 유지)", facets.nutrients.includes('칼륨'));

const TARGET = ['메틸프레드니솔론','아세타졸아미드','아조세미드','프레드니솔론'];
for (const ing of TARGET) {
  const r = rels.find(x => x.ingredient === ing && x.nutrient === '칼륨');
  ck(`[${ing}] renderable 포함`, !!r);
  if (!r) continue;
  ck(`[${ing}] findRelation(id) 동작`, !!findRelation(data, r.id));
  ck(`[${ing}] canShowProduct=false(제품 UI 미표시)`, canShowProduct(r) === false);
  ck(`[${ing}] showPotassiumNotice=true(칼륨 안전카드 표시)`, showPotassiumNotice(r) === true);
  const html = renderDetail(r, data);
  const row = renderRow(r);
  const appCopy = html.split('<div class="src"')[0];
  ck(`[${ing}][row] '상태 모니터링' chip`, row.includes('상태 모니터링'));
  ck(`[${ing}][detail] '칼륨 주의' 안전카드 노출`, html.includes('칼륨 주의'));
  ck(`[${ing}][detail] potassium_notice 본문 노출`, html.includes(data.disclaimers.potassium_notice));
  ck(`[${ing}][detail] 장기/고용량 비단정 본문`, html.includes('장기간 복용하거나 고용량') && html.includes('문의해볼 수 있습니다'));
  ck(`[${ing}][detail] anti-supplement 참고안내(임의 보충 말고·상담 결정)`, html.includes('임의로 보충하지 말고') && html.includes('상담해 결정'));
  ck(`[${ing}][appcopy] 보충 권유('칼륨을 보충하세요') 미노출`, !appCopy.includes('칼륨을 보충하세요'));
  ck(`[${ing}][appcopy] 결핍 단정('부족합니다'/'결핍입니다') 미노출`, !appCopy.includes('부족합니다') && !appCopy.includes('결핍입니다'));
  ck(`[${ing}][appcopy] 직접 지시('복용하세요'/'드세요') 미노출`, !appCopy.includes('복용하세요') && !appCopy.includes('드세요'));
  ck(`[${ing}][detail] 제품/구매/제휴 미노출`, !html.includes('구매') && !html.includes('제휴') && !html.includes('affiliate'));
  ck(`[${ing}][detail] 공통 면책 출력`, html.includes(data.disclaimers.common));
}
if (fails) { console.log('NODE: FAIL ('+fails+')'); process.exit(1); }
console.log('NODE: PASS');
"""


def run_node(sim_path):
    if not shutil.which("node"):
        print("[FATAL] node 미설치"); return 1
    print("--- node: 칼륨 안전카드 + 비단정 + anti-supplement + 제품0(시뮬 export) ---")
    tmp = tempfile.mkdtemp(prefix="ms_pot_node_")
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
