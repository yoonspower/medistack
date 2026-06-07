#!/usr/bin/env python3
"""
validate_medistack_v0_1_export.py
MediStack v0.1 beta export contract validator.

목적: medistack_v0.1_beta_export.json 이 앱 배포 전에 v0.1 봉인 조건을
위반하지 않는지 자동 검출한다. 외부 의존성 없음(표준 라이브러리만).

사용:
    python3 validate_medistack_v0_1_export.py [path/to/medistack_v0.1_beta_export.json]

종료 코드: 0 = PASS, 1 = FAIL  (CI/배포 전 훅에서 사용)
"""
import sys
import json
import re

DEFAULT_PATH = "medistack_v0.1_beta_export.json"

EXPECTED_TOP_KEYS = {"meta", "disclaimers", "relations", "excluded_v0_1"}
EXPECTED_RELATIONS = 19
EXCLUDED_ID = 15
EXCLUDED_INGREDIENT = "에스오메프라졸"
EXCLUDED_NUTRIENT = "비타민B12"
POTASSIUM_NUTRIENT = "칼륨"
POTASSIUM_IDS = {17, 19}
FORBIDDEN_RELATION_FIELDS = ("status", "published", "clinical_reviewed")

# 제품 링크/예시 의심 필드(heuristic). product_link_allowed(플래그)는 제외.
# 스키마 확장 시 이 정규식/예외목록만 손보면 됨.
PRODUCT_FIELD_HINT = re.compile(r"(product|affiliate|shop|buy)", re.IGNORECASE)
PRODUCT_FIELD_SAFE = {"product_link_allowed"}


class Validator:
    def __init__(self):
        self.failures = []  # (no, title, detail)
        self.passes = []    # (no, title)

    def check(self, ok, no, title, detail=""):
        if ok:
            self.passes.append((no, title))
        else:
            self.failures.append((no, title, detail))
        return ok


def rid(obj):
    """relation/excluded 객체에서 id 또는 row_id 추출. 없으면 None."""
    if not isinstance(obj, dict):
        return None
    if "id" in obj:
        return obj["id"]
    if "row_id" in obj:
        return obj["row_id"]
    return None


def nonempty(v):
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    return True  # 숫자/불리언은 '존재'로 간주


def main(path):
    v = Validator()

    # 12) JSON 파싱 (실패 시 즉시 FATAL FAIL)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[FATAL] 파일 없음: {path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"[FATAL] JSON 파싱 실패: {e}")
        return 1

    if not isinstance(data, dict):
        print("[FATAL] 최상위가 객체(dict)가 아님")
        return 1

    # 1) top-level keys
    keys = set(data.keys())
    missing = EXPECTED_TOP_KEYS - keys
    extra = keys - EXPECTED_TOP_KEYS
    v.check(not missing and not extra, 1, "top-level keys (meta/disclaimers/relations/excluded_v0_1)",
            f"missing={sorted(missing)} extra={sorted(extra)}" if (missing or extra) else "")

    meta = data.get("meta")
    disc = data.get("disclaimers")
    rels = data.get("relations")
    excl = data.get("excluded_v0_1")

    # 12) 타입 가드
    meta_ok = isinstance(meta, dict)
    disc_ok = isinstance(disc, dict)
    rels_ok = isinstance(rels, list)
    excl_ok = isinstance(excl, list)
    type_problems = []
    if not meta_ok: type_problems.append("meta!=dict")
    if not disc_ok: type_problems.append("disclaimers!=dict")
    if not rels_ok: type_problems.append("relations!=list")
    if not excl_ok: type_problems.append("excluded_v0_1!=list")
    v.check(not type_problems, 12, "JSON 파싱/타입", "; ".join(type_problems) if type_problems else "")

    # 2) relations length = 19
    if rels_ok:
        v.check(len(rels) == EXPECTED_RELATIONS, 2, "relations length = 19", f"실제 {len(rels)}건")

    # 3) excluded_v0_1 = 15행 1건
    if excl_ok:
        e15 = [e for e in excl if rid(e) == EXCLUDED_ID]
        ok3 = (len(excl) == 1 and len(e15) == 1 and isinstance(e15[0], dict)
               and e15[0].get("ingredient") == EXCLUDED_INGREDIENT
               and e15[0].get("nutrient") == EXCLUDED_NUTRIENT)
        v.check(ok3, 3, "excluded_v0_1 = 15행(에스오메프라졸×비타민B12) 1건",
                f"excluded {len(excl)}건 / 15행 매칭 {len(e15)}건" if not ok3 else "")

    # 4) relations에 row_id 15 없음
    if rels_ok:
        leaked = [rid(r) for r in rels if rid(r) == EXCLUDED_ID]
        v.check(not leaked, 4, "relations에 row_id 15 미포함", f"15행 누출 {len(leaked)}건" if leaked else "")

    # 5) meta.published === false
    if meta_ok:
        pub = meta.get("published", "MISSING")
        v.check(pub is False, 5, "meta.published === false", f"값={pub!r}")
        # 6) meta.clinical_reviewed === false
        cr = meta.get("clinical_reviewed", "MISSING")
        v.check(cr is False, 6, "meta.clinical_reviewed === false", f"값={cr!r}")

    # 7) relation에 status/published/clinical_reviewed 필드 없음
    if rels_ok:
        offenders = []
        for r in rels:
            if isinstance(r, dict):
                bad = [k for k in FORBIDDEN_RELATION_FIELDS if k in r]
                if bad:
                    offenders.append((rid(r), bad))
        v.check(not offenders, 7, "relation에 status/published/clinical_reviewed 필드 없음",
                f"위반 {offenders}" if offenders else "")

    # 8) disclaimers.common 존재
    if disc_ok:
        v.check(nonempty(disc.get("common")), 8, "disclaimers.common 존재",
                "비어있거나 없음" if not nonempty(disc.get("common")) else "")
        # 9) disclaimers.potassium_notice 존재
        v.check(nonempty(disc.get("potassium_notice")), 9, "disclaimers.potassium_notice 존재",
                "비어있거나 없음" if not nonempty(disc.get("potassium_notice")) else "")

    # 10) 칼륨 17·19: product_link_allowed=false & potassium_safety_card=true
    if rels_ok:
        k_rels = [r for r in rels if isinstance(r, dict) and r.get("nutrient") == POTASSIUM_NUTRIENT]
        k_ids = {rid(r) for r in k_rels}
        problems = []
        if k_ids != POTASSIUM_IDS:
            problems.append(f"칼륨 id집합={sorted(k_ids)} (기대 {sorted(POTASSIUM_IDS)})")
        for r in k_rels:
            if r.get("product_link_allowed") is not False:
                problems.append(f"id{rid(r)} product_link_allowed={r.get('product_link_allowed')!r}")
            if r.get("potassium_safety_card") is not True:
                problems.append(f"id{rid(r)} potassium_safety_card={r.get('potassium_safety_card')!r}")
        v.check(not problems, 10, "칼륨 17·19 product_link_allowed=false & potassium_safety_card=true",
                "; ".join(problems) if problems else "")

    # 11) product_link_allowed=false 행에 제품링크/예시 필드 없음(+ 칼륨카드 일관성)
    if rels_ok:
        viol = []
        for r in rels:
            if isinstance(r, dict) and r.get("product_link_allowed") is False:
                for k, val in r.items():
                    if k in PRODUCT_FIELD_SAFE:
                        continue
                    if PRODUCT_FIELD_HINT.search(k) and nonempty(val):
                        viol.append(f"id{rid(r)} '{k}'={val!r}")
        inconsist = [rid(r) for r in rels if isinstance(r, dict)
                     and r.get("potassium_safety_card") is True
                     and r.get("product_link_allowed") is not False]
        if inconsist:
            viol.append(f"potassium_safety_card=true인데 link!=false: id{inconsist}")
        v.check(not viol, 11, "product_link_allowed=false 행에 제품링크/예시 필드 없음",
                "; ".join(viol) if viol else "")

    # ---- 결과 출력 ----
    total = len(v.passes) + len(v.failures)
    overall = "PASS" if not v.failures else "FAIL"
    print("=" * 62)
    print(f"MediStack v0.1 export 검증: {path}")
    print("=" * 62)
    if v.failures:
        print(f"\n[FAIL] {len(v.failures)}건")
        for no, title, detail in sorted(v.failures):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print("\n모든 검증 통과.")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)")
    print("=" * 62)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    sys.exit(main(p))
