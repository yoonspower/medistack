#!/usr/bin/env python3
"""
test_autofactory_orchestrator_guards_v1_7.py — v1.7 가드 회귀(읽기전용·live 무수정).

적대 시나리오로 가드(B1~B8 + no-live-write + 추출 견고성)가 실제 막는지 검증:
  1) --allow-live-write 거부(exit 1).
  2) write_out 접두사 = autofactory_v1_7_.
  3) PROTECTED 구성(v0.2/aliases/full index/app/css/index/data).
  4) B1: 알루미늄 standalone nutrient quarantine · 마그네슘 depletion 정당.
  5) B7 audit: 미재현 quote → audit_fail·false_auto_pass.
  6) B7 audit: 방향 other_lowered → audit_fail.
  7) B7 audit: 정상 al_mg_antacid separation → reviewer_ready.
  8) 추출 견고성: 라벨 전용 줄('2) 칼슘보충제/제산제') 글루 0 + 모든 quote 줄바꿈/잘림 0.
  9) off-scope: 이상반응 섹션 흡수 동거어 미추출.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FX = os.path.join(ROOT, "tests", "fixtures", "nedrug")
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    print("=== AutoFactory Orchestrator v1.7 guard tests ===")
    o = load("orch", os.path.join(HERE, "run_medistack_autofactory_orchestrator_v1_7.py"))
    a16 = load("a16", os.path.join(HERE, "audit_fidelity_v1_6.py"))
    a17 = load("a17", os.path.join(HERE, "audit_fidelity_v1_7.py"))
    ex = load("ex", os.path.join(HERE, "extract_label_interaction_v1_7.py"))
    fix = load("fix", os.path.join(HERE, "fix_harvester_display_template_v1_6.py"))

    # 1) --allow-live-write 거부
    r = subprocess.run([sys.executable, os.path.join(HERE, "run_medistack_autofactory_orchestrator_v1_7.py"),
                        "--allow-live-write"], capture_output=True, text=True)
    ck(r.returncode == 1 and "no-live-write" in r.stdout, "--allow-live-write 거부(exit 1)")

    # 2) 접두사
    ck(o.OUT_PREFIX == "autofactory_v1_7_", "write 산출물 접두사 = autofactory_v1_7_")

    # 3) PROTECTED
    pnames = [os.path.basename(p) for p in o.PROTECTED]
    ck(all(x in pnames for x in ["medistack_v0.2_beta_export.json", "medistack_v0.3_aliases.json",
                                 "full_drug_name_index_sample_v1_0.json", "app.js", "data.js",
                                 "index.html", "styles.css"]), "PROTECTED 구성")

    # 4) B1
    rel_al = {"nutrient": "알루미늄", "counterpart_category": None, "mechanism": "depletion",
              "recommended_action": "monitoring", "source": {}}
    ck(any("B1:aluminum" in x for x in a16.promotion_guards(rel_al, {"counterpart": "알루미늄"})),
       "B1: 알루미늄 standalone nutrient quarantine")
    rel_mg = {"nutrient": "마그네슘", "counterpart_category": None, "mechanism": "depletion",
              "recommended_action": "monitoring", "source": {}}
    ck(not any("B1" in x for x in a16.promotion_guards(rel_mg, {"counterpart": "마그네슘"})),
       "B1: 마그네슘 depletion 정당(미위반)")

    # 5~7) B7 audit harvested
    html = open(os.path.join(FX, "detail_200713889.html"), encoding="utf-8").read()
    findings = ex.extract_interactions(html)
    good_q = next(f["source_quote"] for f in findings if f["counterpart_category"] == "al_mg_antacid"
                  and f["direction"] == "this_drug_lowered")
    disp, mgmt = fix.safe_app_copy("Al/Mg 함유 제산제(약물)", "separation")
    base = {"candidate_id": "T", "family": "F3", "ingredient": "리세드론산",
            "counterpart": "Al/Mg 함유 제산제(약물)", "counterpart_category": "al_mg_antacid",
            "mechanism": "absorption", "action": "separation", "evidence_level": "moderate",
            "source_pointer": "itemSeq 200713889", "item_seq": "200713889",
            "display_text_ko": disp, "management_ko": mgmt, "already_live_on_base": False}

    # 5) 미재현 quote
    miss = {**base, "source_quote": "라벨에 없는 날조 문장이다."}
    rm = a17.audit_harvested(miss, html)
    ck(rm["audit_pass"] is False and rm["false_auto_pass"] is True and rm["verdict"] == "audit_fail_quote_not_reproduced",
       "B7: 미재현 quote → audit_fail·false_auto_pass")

    # 6) 방향 other_lowered (합성 HTML)
    other_html = ('<p class="title">6. 상호작용</p><div>'
                  '<p class="indent0">이 약은 제산제의 흡수를 저해할 수 있다.</p></div>')
    of = ex.extract_interactions(other_html)
    od = next((f for f in of if "흡수를 저해" in f["source_quote"]), None)
    ck(od is not None and od["direction"] == "other_lowered",
       "방향 판정: '이 약은 제산제의 흡수를 저해' → other_lowered")
    oc = {**base, "source_quote": "이 약은 제산제의 흡수를 저해할 수 있다."}
    ro = a17.audit_harvested(oc, other_html)
    ck(ro["audit_pass"] is False and ro["verdict"] == "audit_fail_direction", "B7: other_lowered → audit_fail_direction")

    # 7) 정상 → reviewer_ready
    rg = a17.audit_harvested({**base, "source_quote": good_q}, html)
    ck(rg["audit_pass"] is True and rg["verdict"] in ("reviewer_ready", "reviewer_ready_corrected"),
       "B7: 정상 al_mg_antacid separation → reviewer_ready")

    # 7b) counterpart 과확장(일반 제산제를 Al/Mg 로 좁힘) → audit_fail_counterpart_overclaim
    al_html = open(os.path.join(FX, "detail_199800180.html"), encoding="utf-8").read()
    al_q = next(f["source_quote"] for f in ex.extract_interactions(al_html)
                if f["counterpart_category"] == "al_mg_antacid" and f["direction"] == "this_drug_lowered")
    ck("알루미늄" not in al_q and "마그네슘" not in al_q, "알렌드론산 quote=일반 제산제(Al/Mg 미명명)")
    over = {**base, "ingredient": "알렌드론산", "counterpart": "Al/Mg 함유 제산제(약물)",
            "item_seq": "199800180", "source_pointer": "itemSeq 199800180", "source_quote": al_q}
    ro = a17.audit_harvested(over, al_html)
    ck(ro["audit_pass"] is False and ro["verdict"] == "audit_fail_counterpart_overclaim" and ro["false_auto_pass"] is True,
       "B7: 일반 제산제 → Al/Mg 과확장 → audit_fail_counterpart_overclaim")
    # scope helper 직접
    ck(not ex.counterpart_scope_justified("Al/Mg 함유 제산제(약물)", al_q),
       "counterpart_scope_justified: Al/Mg 표시명 vs 일반-제산제 quote → False")
    ck(ex.counterpart_scope_justified("Al/Mg 함유 제산제(약물)", good_q),
       "counterpart_scope_justified: Al/Mg 표시명 vs Al+Mg quote → True")

    # 8) 추출 견고성: 알렌드론산 라벨 전용 줄 글루 0
    al_html = open(os.path.join(FX, "detail_199800180.html"), encoding="utf-8").read()
    alq = [f["source_quote"] for f in ex.extract_interactions(al_html)]
    ck(all("\n" not in q for q in alq), "alendronate quote 줄바꿈 0(라벨줄 글루 없음)")
    ck(all(fix.quote_truncation_ok(q) for q in alq), "alendronate quote 전건 완전 문장")
    ck(any("칼슘보충제나 제산제 및 일부 경구용 약물들은 이 약의 흡수를 방해하는 것으로 알려져 있다." == q for q in alq),
       "alendronate clean 문장 추출(라벨 라벨줄 제외)")

    # 9) off-scope
    ris = open(os.path.join(FX, "detail_201903166.html"), encoding="utf-8").read()
    rq = [f["source_quote"] for f in ex.extract_interactions(ris)]
    ck(not any("음식물은 이 약의 흡수를 방해하기 때문에" in q for q in rq), "off-scope: 용법 '음식물' 줄 미추출")
    ck(all(ex.is_interaction_scope(f["section"]) for f in ex.extract_interactions(ris)),
       "모든 finding 이 상호작용 scope")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — live-write 거부·PROTECTED·B1·B7(미재현/방향/정상)·추출 견고·off-scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
