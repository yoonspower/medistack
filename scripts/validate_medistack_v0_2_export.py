#!/usr/bin/env python3
"""
validate_medistack_v0_2_export.py
MediStack v0.2 beta export contract validator. (v0.1 검증기와 분리)

v0.2 정책을 코드로 강제: verified_reference 천장 유지(published/clinical 봉인),
제품/제휴 필드 전면 금지, antagonism·임상판단 행 차단, 칼륨 안전 처리,
relations 수는 meta.relation_count 와 일치(확장 대응), 최소 baseline 보장.

사용:
    python3 validate_medistack_v0_2_export.py [path/to/medistack_v0.2_beta_export.json]
종료 코드: 0 = PASS, 1 = FAIL
"""
import sys
import json
import re

DEFAULT_PATH = "medistack_v0.2_beta_export.json"

EXPECTED_TOP_KEYS = {"meta", "disclaimers", "relations", "excluded_v0_1"}
MIN_RELATIONS = 19  # v0.1 baseline. v0.2 확장 시 이 이상.
ALLOWED_EVIDENCE = {"high", "moderate"}            # low/antagonism 노출 금지
# avoid_concomitant 는 antacid_interaction(counterpart_category=al_mg_antacid) 전용 — 라벨 병용금지를
# 출처 귀속·비지시로 운반하는 약물×Al/Mg 제산제 트랙에서만 허용한다. 문맥 강제는 #15 가 담당
# (enum 통과 ≠ 무조건 허용). 그 밖 금기/위험판단성 action 은 계속 금지.
ALLOWED_ACTION = {"separation", "monitoring", "avoid_concomitant"}
ALLOWED_MECHANISM = {"absorption", "depletion"}    # antagonism/additive 차단
FORBIDDEN_RELATION_FIELDS = ("status", "published", "clinical_reviewed")
POTASSIUM_NUTRIENT = "칼륨"
# 제품/제휴 의심 필드(v0.2 전면 금지). product_link_allowed(플래그)만 허용.
PRODUCT_FIELD_HINT = re.compile(r"(product|affiliate|shop|buy|store|purchase|cart)", re.IGNORECASE)
PRODUCT_FIELD_SAFE = {"product_link_allowed"}


class V:
    def __init__(self):
        self.fails = []
        self.passes = []
    def check(self, ok, no, title, detail=""):
        (self.passes if ok else self.fails).append((no, title) if ok else (no, title, detail))
        return ok


def rid(o):
    if not isinstance(o, dict):
        return None
    return o.get("id", o.get("row_id"))


def nonempty(v):
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    return True


def main(path):
    v = V()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[FATAL] 파일 없음: {path}"); return 1
    except json.JSONDecodeError as e:
        print(f"[FATAL] JSON 파싱 실패: {e}"); return 1
    if not isinstance(data, dict):
        print("[FATAL] 최상위가 객체 아님"); return 1

    keys = set(data.keys())
    miss, extra = EXPECTED_TOP_KEYS - keys, keys - EXPECTED_TOP_KEYS
    v.check(not miss and not extra, 1, "top-level keys",
            f"missing={sorted(miss)} extra={sorted(extra)}" if (miss or extra) else "")

    meta, disc = data.get("meta"), data.get("disclaimers")
    rels, excl = data.get("relations"), data.get("excluded_v0_1")
    meta_ok, disc_ok = isinstance(meta, dict), isinstance(disc, dict)
    rels_ok, excl_ok = isinstance(rels, list), isinstance(excl, list)
    tp = []
    if not meta_ok: tp.append("meta!=dict")
    if not disc_ok: tp.append("disclaimers!=dict")
    if not rels_ok: tp.append("relations!=list")
    if not excl_ok: tp.append("excluded_v0_1!=list")
    v.check(not tp, 0, "JSON 파싱/타입", "; ".join(tp))

    # 2) relations 최소 baseline
    if rels_ok:
        v.check(len(rels) >= MIN_RELATIONS, 2, f"relations >= {MIN_RELATIONS} (baseline)", f"실제 {len(rels)}")

    # 3) meta.relation_count == len(relations)
    if rels_ok and meta_ok:
        v.check(meta.get("relation_count") == len(rels), 3, "meta.relation_count == len(relations)",
                f"meta={meta.get('relation_count')} actual={len(rels)}")
    # 4) meta.excluded_count == len(excluded)
    if excl_ok and meta_ok:
        v.check(meta.get("excluded_count") == len(excl), 4, "meta.excluded_count == len(excluded_v0_1)",
                f"meta={meta.get('excluded_count')} actual={len(excl)}")

    # 5/6) 봉인
    if meta_ok:
        v.check(meta.get("published") is False, 5, "meta.published === false", f"값={meta.get('published')!r}")
        v.check(meta.get("clinical_reviewed") is False, 6, "meta.clinical_reviewed === false", f"값={meta.get('clinical_reviewed')!r}")

    # 7) relation 필수필드 / 고유 id / 금지필드
    if rels_ok:
        req = ("id", "ingredient", "nutrient", "recommended_action", "display_text_ko")
        miss_rows, forb, ids = [], [], []
        for r in rels:
            if not isinstance(r, dict):
                miss_rows.append("non-dict"); continue
            if not all(nonempty(r.get(k)) for k in req):
                miss_rows.append(rid(r))
            bad = [k for k in FORBIDDEN_RELATION_FIELDS if k in r]
            if bad: forb.append((rid(r), bad))
            ids.append(rid(r))
        dups = sorted({i for i in ids if ids.count(i) > 1})
        v.check(not miss_rows and not forb and not dups, 7,
                "relation 필수필드/고유id/금지필드(status·published·clinical_reviewed) 없음",
                f"missing={miss_rows} forbidden={forb} dup_ids={dups}")

    # 8) excluded 무결성 (id가 relations에 없어야)
    if rels_ok and excl_ok:
        rel_ids = {rid(r) for r in rels if isinstance(r, dict)}
        leak = [rid(e) for e in excl if rid(e) in rel_ids]
        bad_e = [i for i, e in enumerate(excl) if not (isinstance(e, dict) and nonempty(e.get("ingredient")) and nonempty(e.get("nutrient")) and rid(e) is not None)]
        v.check(not leak and not bad_e, 8, "excluded_v0_1 무결성(relations에 누출 없음·필드 구비)",
                f"leak={leak} malformed_idx={bad_e}")

    # 9) disclaimers.common
    if disc_ok:
        v.check(nonempty(disc.get("common")), 9, "disclaimers.common 존재", "없음/빈값" if not nonempty(disc.get("common")) else "")

    # 10) potassium_notice (칼륨 행 존재 시 필수)
    if disc_ok and rels_ok:
        has_k = any(isinstance(r, dict) and r.get("potassium_safety_card") is True for r in rels)
        ok10 = (not has_k) or nonempty(disc.get("potassium_notice"))
        v.check(ok10, 10, "disclaimers.potassium_notice (칼륨 행 있으면 필수)",
                "칼륨 행 있는데 potassium_notice 없음" if not ok10 else "")

    # 11) 칼륨 일관성: nutrient 칼륨 ⇒ link=false & card=true; card=true ⇒ link=false
    if rels_ok:
        prob = []
        for r in rels:
            if not isinstance(r, dict):
                continue
            is_k_nutrient = r.get("nutrient") == POTASSIUM_NUTRIENT
            card = r.get("potassium_safety_card") is True
            link_false = r.get("product_link_allowed") is False
            if is_k_nutrient and not (link_false and card):
                prob.append(f"id{rid(r)}(칼륨): link_false={link_false} card={card}")
            if card and not link_false:
                prob.append(f"id{rid(r)}: card=true인데 link!=false")
        v.check(not prob, 11, "칼륨 일관성(칼륨⇒link=false&card=true / card=true⇒link=false)", "; ".join(prob))

    # 12) 제품/제휴 필드 전면 금지 (v0.2 보류)
    if rels_ok:
        viol = []
        for r in rels:
            if not isinstance(r, dict):
                continue
            for k, val in r.items():
                if k in PRODUCT_FIELD_SAFE:
                    continue
                if PRODUCT_FIELD_HINT.search(k) and nonempty(val):
                    viol.append(f"id{rid(r)} '{k}'")
        v.check(not viol, 12, "제품/제휴 필드 전면 금지(v0.2)", "; ".join(viol))

    # 13) enum 경계: evidence∈{high,moderate} / action∈{sep,mon} / mechanism∈{absorption,depletion}
    if rels_ok:
        bad = []
        for r in rels:
            if not isinstance(r, dict):
                continue
            ev, ac, me = r.get("evidence_level"), r.get("recommended_action"), r.get("mechanism")
            if ev is not None and ev not in ALLOWED_EVIDENCE: bad.append(f"id{rid(r)} evidence={ev}")
            if ac is not None and ac not in ALLOWED_ACTION: bad.append(f"id{rid(r)} action={ac}")
            if me is not None and me not in ALLOWED_MECHANISM: bad.append(f"id{rid(r)} mechanism={me}")
        v.check(not bad, 13, "enum 경계(evidence high/moderate · action sep/mon · mechanism absorption/depletion)", "; ".join(bad))

    # 14) requires_clinical_review !== true (임상검수 게이트 행 노출 금지)
    if rels_ok:
        rc = [rid(r) for r in rels if isinstance(r, dict) and r.get("requires_clinical_review") is True]
        v.check(not rc, 14, "requires_clinical_review=true 행 없음", f"위반 id={rc}" if rc else "")

    # 15) avoid_concomitant·antacid(al_mg_antacid) 안전 가드 + reviewed_by 봉인
    #  - recommended_action=avoid_concomitant 는 antacid_interaction 전용: counterpart_category=al_mg_antacid
    #    없으면 fail. 영양소 relation 은 counterpart_category 부재 → avoid_concomitant 사용 시 fail
    #    (라벨 병용금지를 약물×Al/Mg 제산제 트랙 밖으로 확대 금지).
    #  - antacid relation(counterpart_category=al_mg_antacid)은 제품/제휴 금지: product_link_allowed=false 강제
    #    (일반 relation 은 제품 데이터 부재라 flag=true 여도 canShowProduct=false — 그 정책은 불변, antacid 만 추가 잠금).
    #  - reviewed_by 전건 공란(clinical reviewer 미확보 — 검수 완료 오인 차단). 라이브 스키마엔 본래 부재.
    if rels_ok:
        bad = []
        for r in rels:
            if not isinstance(r, dict):
                continue
            ac, cc = r.get("recommended_action"), r.get("counterpart_category")
            if ac == "avoid_concomitant" and cc != "al_mg_antacid":
                bad.append(f"id{rid(r)} avoid_concomitant 인데 counterpart_category!=al_mg_antacid({cc!r})")
            if cc == "al_mg_antacid" and r.get("product_link_allowed") is not False:
                bad.append(f"id{rid(r)} antacid relation product_link_allowed!=false({r.get('product_link_allowed')!r})")
            if nonempty(r.get("reviewed_by")):
                bad.append(f"id{rid(r)} reviewed_by 비공란({r.get('reviewed_by')!r})")
        v.check(not bad, 15,
                "avoid_concomitant=antacid(al_mg_antacid) 전용 · antacid product_link=false · reviewed_by 공란",
                "; ".join(bad))

    total = len(v.passes) + len(v.fails)
    overall = "PASS" if not v.fails else "FAIL"
    bar = "=" * 64
    print(bar); print(f"MediStack v0.2 export 검증: {path}"); print(bar)
    if v.fails:
        print(f"\n[FAIL] {len(v.fails)}건")
        for no, title, detail in sorted(v.fails):
            print(f"  X #{no:<2} {title}" + (f"\n         -> {detail}" if detail else ""))
    else:
        print("\n모든 검증 통과.")
    print(f"\nRESULT: {overall}  ({len(v.passes)}/{total} checks passed)"); print(bar)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH))
