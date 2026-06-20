#!/usr/bin/env python3
"""
test_depletion_promotion_guard_v1_8.py — 승격 가드(DB1-7) + 🔑칼륨 invariant **거부 경로** 단위 테스트.

추출/harvest 성공(auto_pass)이라도 audit 가 다음을 거부함을 검증(refute-by-default):
  - 🔑 칼륨인데 potassium_safety_card 누락 → reject (A7)
  - wrong-direction(고칼륨혈증·칼륨 상승) → reject (A4)
  - B2 임부/태아 맥락 → reject (A5)
  - copy 보충/검사 지시 → reject (A8)
  - 미정의 영양소 → reject (A6)
  - live 중복 → reject (A9)
  - false_auto_pass 탐지(harvest reviewer_ready ↔ audit reject)
종료: 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def ck(cond, label):
    print(("  PASS " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


au = load("au", "audit_depletion_fidelity_v1_8.py")
GOOD_Q = "대사 : 때때로 저칼륨혈증, 저나트륨혈증이 나타날 수 있다."
DISP, MNG = au.safe_depletion_copy("칼륨")


def cand(**kw):
    nut = kw.get("nutrient", "칼륨")
    rel = {"id": 999, "ingredient": kw.get("ingredient", "테스트약"), "nutrient": nut,
           "mechanism": "depletion", "recommended_action": "monitoring",
           "display_text_ko": kw.get("disp", DISP), "management_ko": kw.get("mng", MNG),
           "product_link_allowed": kw.get("link", False),
           "potassium_safety_card": kw.get("kcard", nut == "칼륨"),
           "requires_clinical_review": False, "counterpart_category": None}
    c = {"candidate_id": kw.get("cid", "T"), "ingredient": rel["ingredient"], "nutrient": nut,
         "itemSeq": kw.get("seq", "201403403"), "source_section": kw.get("sec", "4. 이상반응"),
         "source_quote": kw.get("q", GOOD_Q), "evidence_kind": kw.get("kind", "deficiency_state"),
         "projected_relation": rel, "harvest_verdict": kw.get("hv", "reviewer_ready")}
    return c


def v(c, live=None):
    return au.fidelity_audit(c, label_html=None, live_pairs=live)["verdict"]


def main():
    print("=== depletion 승격 가드(DB1-7)·🔑칼륨 invariant 거부 경로 ===")
    ck(v(cand()) == "reviewer_ready", "정상 칼륨 결핍 후보 → reviewer_ready")
    ck(v(cand(kcard=False)) == "reject", "🔑 칼륨인데 potassium_safety_card 누락 → reject(A7)")
    ck(v(cand(link=True)) == "reject", "🔑 칼륨인데 product_link_allowed=true → reject(A7)")
    ck(v(cand(q="고칼륨혈증이 나타날 수 있다.")) == "reject", "wrong-direction 고칼륨혈증 → reject(A4)")
    ck(v(cand(q="임부에서 저칼륨혈증이 보고되었다.", sec="7. 임부 및 수유부에 대한 투여")) == "reject",
       "B2 임부 맥락 → reject(A5/A3)")
    ck(v(cand(disp="칼륨을 보충하세요.")) == "reject", "copy 보충 지시 → reject(A8)")
    ck(v(cand(nutrient="니켈", kcard=False)) == "reject", "미정의 영양소 → reject(A6)")
    ck(v(cand(ingredient="푸로세미드"), live={("푸로세미드", "칼륨")}) == "reject", "live 중복 → reject(A9)")
    ck(v(cand(sec="6. 상호작용")) == "reject", "상호작용(약-약) off-scope → reject(A3)")
    ck(v(cand(q="두통, 발진이 나타날 수 있다.", kind="deficiency_state")) == "reject",
       "결핍 명시 없는 quote → reject(A4)")

    # false_auto_pass 탐지: harvest reviewer_ready 인데 audit reject
    corpus = [cand(cid="OK"), cand(cid="BADK", kcard=False)]
    res = au.audit_corpus(corpus, {}, None)
    ck("BADK" in res["false_auto_pass"], "false_auto_pass 탐지(harvest RR ↔ audit reject)")
    ck(res["counts"]["reject"] >= 1, "audit_corpus reject 카운트")

    # 비칼륨(마그네슘) 정상 — kcard=false (v1.8 범위=칼륨/마그네슘)
    ck(v(cand(nutrient="마그네슘", kcard=False, q="저마그네슘혈증이 나타날 수 있다.", kind="deficiency_state")) == "reviewer_ready",
       "비칼륨(마그네슘) kcard=false 정상 → reviewer_ready")
    ck(v(cand(nutrient="마그네슘", kcard=True, q="저마그네슘혈증이 나타날 수 있다.")) == "reject",
       "비칼륨(마그네슘)인데 potassium_safety_card=true → reject(A7)")
    ck(v(cand(nutrient="엽산", kcard=False, q="엽산결핍이 나타날 수 있다.")) == "reject",
       "v1.8 범위 밖 영양소(엽산) → reject(A6)")

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}"); return 1
    print("RESULT: PASS — 칼륨 invariant·방향·B2·copy·영양소·live·false_auto_pass 가드 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
