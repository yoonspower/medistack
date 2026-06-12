#!/usr/bin/env python3
"""
validate_potassium_name_only_policy.py
MediStack v1.0 — full drug name index 의 **potassium(칼륨) name_only 안전선** 검증기.

정책 근거: docs/MediStack_v1.0_potassium_salt_form_policy.md
원칙: full index name_only 는 검색 보조(품목명 확인)이지 의학/보충제 정보가 아니다.
      칼륨이 포함된 name_only 항목은 **salt-form/짝이온/복합제 co-ingredient 만 허용**하고,
      **standalone 칼륨보충제 / 전해질·저칼륨혈증 보충 목적 제품은 차단(FAIL)** 한다.
      이 검증기는 **데이터를 수정하지 않는다.** 위반을 보고만 한다(실제 삭제·필터링 없음).

핵심 안전(부분일치 함정 회피):
  - "칼륨" 단어 포함만으로 차단하지 않는다. ingredient_name(주성분) 기준으로 salt 를 분류한다.
  - 예) "로사르탄칼륨정"(품목명에 '칼륨정' 포함)은 ARB 염 → 허용. "염화칼륨"이 **단일 주성분**이면 → 차단.
  - 문맥이 애매하면(보충염이 복합제 co-ingredient) **자동 차단하지 않고 manual-review** 로 분류한다.

판정 4종:
  not_subject       — item_name/ingredient_name 에 칼륨/포타슘/KCl 없음 → 검사 제외(PASS)
  allowed_saltform  — 칼륨이 비-칼륨 활성성분의 염(ARB·클라불란산 등) 또는 복합제 부수 성분 → PASS
  blocked_standalone— standalone 칼륨보충제(보충염 단일 주성분) 또는 보충/전해질 목적 키워드 → FAIL
  manual_review     — 보충형 염이 복합제 co-ingredient 이거나 미인식 칼륨 토큰 → 비차단(리포트만)

검증(데이터 경로):
  - 현재 full index name_only 에 blocked_standalone == 0 이어야 PASS.
  - name_only 칼륨 항목에 영양소/보충제/제품/구매/복용/상호작용 류 금지 필드 0.
  - 카운트 sanity(total/name_only) — STOP 가드.

사용:
  python3 scripts/validate_potassium_name_only_policy.py [data/full_drug_name_index_sample_v1_0.json]
  python3 scripts/validate_potassium_name_only_policy.py --selftest   # positive/negative fixture + 음성(non-no-op)
종료 코드: 0 PASS, 1 FAIL
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEF_INDEX = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")
FIXTURE = os.path.join(HERE, "fixtures", "potassium_name_only_policy.json")

# ── 칼륨 salt 분류 사전 ─────────────────────────────────────────────────────
# allowlist: 칼륨이 비-칼륨 활성의 염(짝이온)이거나 복합제 부수 성분 — 항상 허용.
ALLOWLIST_SALTS = [
    "로사르탄칼륨", "피마사르탄칼륨", "아질사르탄메독소밀칼륨", "아질사르탄칼륨",  # ARB 염
    "클라불란산칼륨", "묽은클라불란산칼륨", "묽은클라불라산칼륨",                 # 아목시실린 복합 항생제(오타변형 포함)
    "비스무트시트르산염칼륨",                                                   # 위장약 복합
    "글리시리진산이칼륨", "글리시리진산디칼륨",                                  # 감초 유래 항염 co-ingredient
    "구아야콜설폰산칼륨",                                                       # 진해거담 복합
    "요오드화칼륨",                                                            # 종합비타민(활성=요오드)
    "제일인산칼륨", "제이인산칼륨", "인산칼륨",                                  # 완충/구강용품
    "황산칼륨",                                                                # 장정결 복합
]
# standalone 보충/전해질 repletion 염 — **단일 주성분**이거나 보충 목적 키워드 동반 시 차단.
SUPPLEMENT_SALTS = [
    "염화칼륨", "구연산칼륨", "시트르산칼륨", "글루콘산칼륨",
    "아스파르트산칼륨",          # L-아스파르트산칼륨 substring 포함(문맥 의존 — 단일이면 차단, 복합이면 manual)
    "중탄산칼륨", "탄산수소칼륨",
]
SUPPLEMENT_SALTS_LATIN = ["kcl", "potassium chloride"]  # 소문자 비교
# 명시적 보충/전해질/저칼륨 보충 목적 키워드. **반드시 phrase-level**(‘칼륨정’·‘칼륨’ 단독 금지 — allowlist 염 오판 방지).
SUPPLEMENT_KEYWORDS = [
    "칼륨보충", "포타슘보충", "potassium supplement",
    "전해질보충", "전해질 보충", "저칼륨혈증",
]
# 칼륨 검사 대상 트리거(어느 필드든 등장 시 정책 검사).
K_TRIGGERS_KO = ["칼륨", "염화k"]
K_TRIGGERS_LATIN = ["kcl", "potassium"]

# name_only 칼륨 항목에 있으면 안 되는 의학/보충제/제품 필드(있으면 FAIL).
FORBIDDEN_POTASSIUM_FIELDS = {
    "relation", "relations", "nutrient", "nutrients", "supplement", "supplements",
    "interaction", "interactions", "mechanism", "recommended_action", "management",
    "management_ko", "evidence_level", "potassium_safety_card", "potassium_notice",
    "product_links", "product_examples", "products", "affiliate_links", "buy_links",
    "purchase", "price", "dosage", "dose", "recommendation", "recommendations",
    "electrolyte", "repletion", "requires_clinical_review", "source_relation_ids",
}

SEP_RE = re.compile(r"[\/·,，+;；・‧]")


def split_ingredients(ing):
    """주성분 문자열을 성분 구분자로 분해. 단일 주성분 판정에 사용."""
    return [p.strip() for p in SEP_RE.split(ing or "") if p.strip()]


def is_potassium_subject(item_name, ingredient_name):
    text = f"{item_name or ''} {ingredient_name or ''}"
    low = text.lower()
    if any(t in text for t in K_TRIGGERS_KO):
        return True
    if any(t in low for t in K_TRIGGERS_LATIN):
        return True
    return False


def classify_potassium(item_name, ingredient_name):
    """칼륨 포함 항목을 not_subject/allowed_saltform/blocked_standalone/manual_review 로 분류."""
    text = f"{item_name or ''} {ingredient_name or ''}"
    low = text.lower()
    if not is_potassium_subject(item_name, ingredient_name):
        return ("not_subject", "")

    # 1) 명시적 보충/전해질/저칼륨 보충 목적 키워드 → 차단(복합 여부 무관, repletion 제품).
    for kw in SUPPLEMENT_KEYWORDS:
        if kw.lower() in low:
            return ("blocked_standalone", f"supplement-keyword:{kw}")

    # 2) 보충형 염 존재? — 주성분 기준 단일/복합 판정.
    supp = [s for s in SUPPLEMENT_SALTS if s in text]
    supp += [s for s in SUPPLEMENT_SALTS_LATIN if s in low]
    if supp:
        comps = split_ingredients(ingredient_name)
        sole_active = len(comps) <= 1  # 단일 주성분 = standalone 보충제
        if sole_active:
            return ("blocked_standalone", f"standalone-supplement-salt:{supp[0]}")
        return ("manual_review", f"supplement-salt-coingredient:{supp[0]}")

    # 3) allowlist 염(짝이온/복합제 부수 성분) → 허용.
    allow = [a for a in ALLOWLIST_SALTS if a in text]
    if allow:
        return ("allowed_saltform", allow[0])

    # 4) 칼륨은 있으나 인식된 염 토큰 없음 → 자동 차단하지 않고 manual_review.
    return ("manual_review", "unrecognized-potassium-token")


def forbidden_fields_present(entry):
    return sorted(FORBIDDEN_POTASSIUM_FIELDS & set(entry.keys()))


def check_potassium_policy(entries):
    """name_only 항목에 정책을 적용. 데이터 무수정. 통계/위반 반환."""
    name_only = [e for e in entries if not e.get("covered_by_relation")]
    item_basis = ing_basis = 0
    allowed, manual, blocked, field_viol = [], [], [], []
    for e in name_only:
        item_name = e.get("item_name") or ""
        ing = e.get("ingredient_name") or ""
        if "칼륨" in item_name:
            item_basis += 1
        if "칼륨" in item_name or "칼륨" in ing:
            ing_basis += 1
        verdict, reason = classify_potassium(item_name, ing)
        if verdict == "not_subject":
            continue
        # 칼륨 검사 대상 → 금지 필드 동시 검사.
        ff = forbidden_fields_present(e)
        if ff:
            field_viol.append((e.get("item_seq"), item_name, ff))
        if verdict == "allowed_saltform":
            allowed.append((e.get("item_seq"), item_name, reason))
        elif verdict == "manual_review":
            manual.append((e.get("item_seq"), item_name, reason))
        elif verdict == "blocked_standalone":
            blocked.append((e.get("item_seq"), item_name, reason))
    return {
        "name_only": len(name_only),
        "item_basis": item_basis,
        "ing_basis": ing_basis,
        "subject": len(allowed) + len(manual) + len(blocked),
        "allowed": allowed,
        "manual_review": manual,
        "blocked": blocked,
        "field_violations": field_viol,
    }


def validate(doc):
    entries = doc.get("entries", [])
    meta = doc.get("meta", {}) or {}
    results = []

    def ck(name, ok, detail=""):
        results.append((bool(ok), name, detail))
        return bool(ok)

    stats = check_potassium_policy(entries)

    ck("구조: entries(list)", isinstance(entries, list) and len(entries) > 0)
    # STOP 가드 — 현재 데이터 규모 sanity.
    ck("full index total == 5,500", len(entries) == 5500, f"total {len(entries)}")
    no = [e for e in entries if not e.get("covered_by_relation")]
    rc = [e for e in entries if e.get("covered_by_relation")]
    ck("name_only == 4,942", len(no) == 4942, f"name_only {len(no)}")
    ck("relation_card == 558", len(rc) == 558, f"relation_card {len(rc)}")

    # 칼륨 검사 대상 카운트(리포트용).
    ck("칼륨 검사 대상 존재(item_name>=1, ingredient>=1)",
       stats["item_basis"] >= 1 and stats["ing_basis"] >= 1,
       f"item {stats['item_basis']} / ingredient {stats['ing_basis']}")

    # 핵심: standalone 칼륨보충제 0건.
    ck("standalone 칼륨보충제 0건(현재 데이터)",
       len(stats["blocked"]) == 0,
       f"blocked {len(stats['blocked'])}: {stats['blocked'][:3]}")

    # 칼륨 name_only 항목에 금지 필드 0.
    ck("칼륨 name_only 금지 필드 0(영양소/보충제/제품/구매/복용/상호작용)",
       len(stats["field_violations"]) == 0,
       f"위반 {stats['field_violations'][:3]}")

    # 모든 검사 대상은 allowed 또는 manual_review(blocked 0 이므로).
    ck("검사 대상 = allowed + manual_review (blocked 0)",
       stats["subject"] == len(stats["allowed"]) + len(stats["manual_review"]),
       f"subject {stats['subject']}")

    return results, stats


def _print(results):
    npass = sum(1 for ok, _, _ in results if ok)
    for ok, name, detail in results:
        tag = "PASS" if ok else "FAIL"
        line = f"[{tag}] {name}"
        if detail and not ok:
            line += f"  → {detail}"
        print(line)
    print("=" * 64)
    ok_all = npass == len(results)
    print(f"RESULT: {'PASS' if ok_all else 'FAIL'}  ({npass}/{len(results)} checks passed)")
    print("=" * 64)
    return ok_all


def run_data(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    results, stats = validate(doc)
    ok = _print(results)
    print(f"[stats] name_only={stats['name_only']} · 칼륨(item_name)={stats['item_basis']} · "
          f"칼륨(ingredient)={stats['ing_basis']} · subject={stats['subject']} · "
          f"allowed={len(stats['allowed'])} · manual_review={len(stats['manual_review'])} · "
          f"blocked={len(stats['blocked'])}")
    if stats["manual_review"]:
        print("[manual-review] (비차단 — 리포트 대상):")
        for seq, nm, reason in stats["manual_review"]:
            print(f"   - {nm}  (seq {seq}; {reason})")
    return ok


def selftest():
    """positive/negative fixture 분류 단위테스트 + 데이터 경로 non-no-op(음성) 검증."""
    print("=== SELFTEST: potassium name_only policy ===")
    with open(FIXTURE, encoding="utf-8") as f:
        fx = json.load(f)
    fails = 0

    def expect(cases, want, kind):
        nonlocal fails
        for c in cases:
            v, reason = classify_potassium(c.get("item_name", ""), c.get("ingredient_name", ""))
            ok = (v == want)
            if not ok:
                fails += 1
            print(f"  [{'OK' if ok else 'XX'}] {kind:<10} expect={want:<18} got={v:<18} "
                  f":: {c.get('item_name','')[:34]}  ({reason})")

    expect(fx.get("positive_saltform", []), "allowed_saltform", "positive")
    expect(fx.get("negative_standalone", []), "blocked_standalone", "negative")
    expect(fx.get("manual_review", []), "manual_review", "manual")

    # 금지 필드 fixture: 항목 자체가 forbidden field 를 가지면 check_potassium_policy 가 잡아야 함.
    ff_cases = fx.get("forbidden_field", [])
    for c in ff_cases:
        entry = {"covered_by_relation": False, "item_seq": "TEST", **c}
        ff = forbidden_fields_present(entry)
        ok = len(ff) >= 1
        if not ok:
            fails += 1
        print(f"  [{'OK' if ok else 'XX'}] field      expect>=1 forbidden  got={ff}  "
              f":: {c.get('item_name','')[:30]}")

    # 음성(non-no-op): standalone 보충제 1건을 합성 인덱스에 주입하면 데이터 검사가 FAIL 해야 함.
    base_no = [{"covered_by_relation": False, "item_seq": "P1",
                "item_name": "국제로잘탄정50밀리그램(로사르탄칼륨)", "ingredient_name": "로사르탄칼륨"}]
    inj = base_no + [{"covered_by_relation": False, "item_seq": "BAD",
                      "item_name": "염화칼륨서방정600밀리그램", "ingredient_name": "염화칼륨"}]
    clean_stats = check_potassium_policy(base_no)
    inj_stats = check_potassium_policy(inj)
    c1 = (len(clean_stats["blocked"]) == 0)
    c2 = (len(inj_stats["blocked"]) == 1)
    if not c1:
        fails += 1
    if not c2:
        fails += 1
    print(f"  [{'OK' if c1 else 'XX'}] non-no-op  clean blocked=0  got={len(clean_stats['blocked'])}")
    print(f"  [{'OK' if c2 else 'XX'}] non-no-op  inject blocked=1  got={len(inj_stats['blocked'])}")

    # 금지 필드 주입 → field_violations 잡힘.
    inj_ff = base_no + [{"covered_by_relation": False, "item_seq": "FF",
                         "item_name": "로사르탄칼륨정", "ingredient_name": "로사르탄칼륨",
                         "nutrient": "칼륨"}]
    c3 = (len(check_potassium_policy(inj_ff)["field_violations"]) == 1)
    if not c3:
        fails += 1
    print(f"  [{'OK' if c3 else 'XX'}] non-no-op  inject forbidden-field violation=1  "
          f"got={len(check_potassium_policy(inj_ff)['field_violations'])}")

    print("=" * 64)
    ok = fails == 0
    print(f"SELFTEST: {'PASS' if ok else 'FAIL'}  ({fails} failures)")
    print("=" * 64)
    return ok


def main(argv):
    if "--selftest" in argv:
        return 0 if selftest() else 1
    args = [a for a in argv[1:] if not a.startswith("--")]
    path = args[0] if args else DEF_INDEX
    return 0 if run_data(path) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
