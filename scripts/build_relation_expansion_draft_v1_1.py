#!/usr/bin/env python3
"""
build_relation_expansion_draft_v1_1.py
MediStack — source_confirmed A티어 7후보(E01–E06·E08)의 relation 을 **새 버전 draft 파일**로 작성한다.

⚠️ 라이브 핵심자산(v0.2 export·full index·alias·DATA_URL·src) 을 한 줄도 변경하지 않는다.
   이 스크립트는 v0.2 export 의 기존 relation 30 을 **그대로 복사**하고, 검증된 7후보의 신규 relation 11건만
   덧붙여 별도 draft 파일(data/relation_expansion_draft_v1_1.json) 을 만든다. 라이브 미반영(DATA_URL=v0.2 유지).
   relation draft 는 published/clinical_reviewed=false. 실제 라이브 통합(DATA_URL flip + full index)은 별도 PM 게이트.

근거: docs/MediStack_relation_source_verification_atier.md (허가사항 출처 확인 완료).
신규 relation(11) ids 32–42 — 기존 톤(depletion=오메프라졸 13·14 / absorption=알렌드론산 29) 미러링.
  PPI ×비타민B12(depletion·monitoring·moderate) + ×마그네슘(depletion·monitoring·high): 라베/판토/란소/덱스란소
  경구 비스포스포네이트 ×칼슘(absorption·separation·high): 리세드론산·이반드론산 (알렌드론산 29 패턴)
  세프디니르 ×철분(absorption·separation·high)
missing 3(E07/E09/E10 파모티딘/라푸티딘/니자티딘 H2×B12) 및 에스오메프라졸은 **절대 미포함.**

사용: python3 scripts/build_relation_expansion_draft_v1_1.py [--no-write]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
V02 = os.path.join(DATA, "medistack_v0.2_beta_export.json")
OUT = os.path.join(DATA, "relation_expansion_draft_v1_1.json")

CHECKED = "2026-06-13"
NEDRUG = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

# 참고정보 톤 템플릿 (기존 relation 과 동일 문구 — 복용지시/제품권유 아님)
DEP_TEXT = "{ing}을(를) 장기간 복용하는 경우 {nut} 상태에 영향이 있을 수 있다는 보고가 있어, 상태 확인이 필요할 수 있습니다."
DEP_MGMT = "장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다."
ABS_TEXT = "{ing}{p} {nut}이(가) 함유된 제품을 같은 시간에 복용하면 {ing}의 흡수가 줄어들 수 있습니다."
ABS_MGMT = "같은 시간대 복용은 피하고, 시간 간격을 두는 것이 권장될 수 있습니다. 구체적인 간격은 약사와 상담하세요."


def gwa(word):
    """받침 유무에 따라 자연스러운 과/와 이중형(자연형 먼저). 세프디니르(모음종결)→'와(과)'."""
    last = word[-1]
    if "가" <= last <= "힣":
        return "과(와)" if (ord(last) - 0xAC00) % 28 else "와(과)"
    return "과(와)"


# 노출 문구의 nutrient 표기는 기존 baseline(id12/13)을 미러: nutrient 필드는 '비타민B12'(공백없음, baseline 동일)
# 유지하되 display_text 만 '비타민 B12'(공백)로 렌더. disp_nut 로 분리.
def dep(rid, ing, nut, evidence, seq, item, pointer, disp_nut=None):
    return {
        "id": rid, "ingredient": ing, "nutrient": nut, "mechanism": "depletion",
        "recommended_action": "monitoring", "evidence_level": evidence,
        "display_text_ko": DEP_TEXT.format(ing=ing, nut=disp_nut or nut), "management_ko": DEP_MGMT,
        "product_link_allowed": True, "potassium_safety_card": False, "requires_clinical_review": False,
        "source": {"type": "허가사항", "url": NEDRUG.format(seq),
                   "pointer": f"식약처 허가사항(nedrug) / {item}(itemSeq {seq}) / {pointer} / 확인일 {CHECKED}"},
        "draft_origin": "relation_expansion_priority_candidates_v1_1 (source_confirmed)",
    }


def absn(rid, ing, nut, evidence, seq, item, pointer):
    return {
        "id": rid, "ingredient": ing, "nutrient": nut, "mechanism": "absorption",
        "recommended_action": "separation", "evidence_level": evidence,
        "display_text_ko": ABS_TEXT.format(ing=ing, p=gwa(ing), nut=nut), "management_ko": ABS_MGMT,
        "product_link_allowed": True, "potassium_safety_card": False, "requires_clinical_review": False,
        "source": {"type": "허가사항", "url": NEDRUG.format(seq),
                   "pointer": f"식약처 허가사항(nedrug) / {item}(itemSeq {seq}) / {pointer} / 확인일 {CHECKED}"},
        "draft_origin": "relation_expansion_priority_candidates_v1_1 (source_confirmed)",
    }


def new_relations():
    r = []
    # E01 라베프라졸 (경보라베프라졸정10mg 201405854). B12 nutrient 필드='비타민B12'(baseline 동일), display 공백.
    r.append(dep(32, "라베프라졸", "비타민B12", "moderate", "201405854", "경보라베프라졸정10mg(라베프라졸나트륨)",
                 "사용상의 주의사항 / 장기투여로 저염산증·무위산증에 의한 비타민 B12(시아노코발라민) 흡수장애 가능성", disp_nut="비타민 B12"))
    r.append(dep(33, "라베프라졸", "마그네슘", "moderate", "201405854", "경보라베프라졸정10mg(라베프라졸나트륨)",
                 "이상반응 / 드물게 저마그네슘혈증 보고"))
    # E02 판토프라졸 (이텍스판토프라졸정 202107096)
    r.append(dep(34, "판토프라졸", "비타민B12", "moderate", "202107096", "이텍스판토프라졸정(판토프라졸나트륨세스키히드레이트)",
                 "사용상의 주의사항 / 장기투여 시 저염산증·무위산증에 의한 비타민 B12(cyanocobalamin) 흡수장애 가능성", disp_nut="비타민 B12"))
    r.append(dep(35, "판토프라졸", "마그네슘", "moderate", "202107096", "이텍스판토프라졸정(판토프라졸나트륨세스키히드레이트)",
                 "이상반응(대사 및 영양계) / 저마그네슘혈"))
    # E03 란소프라졸 (뉴란소캡슐15mg 201308978)
    r.append(dep(36, "란소프라졸", "비타민B12", "moderate", "201308978", "뉴란소캡슐15밀리그램(란소프라졸)",
                 "사용상의 주의사항 / 위산억제제 장기(예 3년 이상) 투여 시 시아노코발라민(비타민B12) 흡수장애 가능성", disp_nut="비타민 B12"))
    r.append(dep(37, "란소프라졸", "마그네슘", "moderate", "201308978", "뉴란소캡슐15밀리그램(란소프라졸)",
                 "이상반응(대사 및 영양계) / 저마그네슘혈증"))
    # E05 덱스란소프라졸 (덱시라졸캡슐30mg 201802450)
    r.append(dep(38, "덱스란소프라졸", "비타민B12", "moderate", "201802450", "덱시라졸캡슐30밀리그램(덱스란소프라졸)",
                 "사용상의 주의사항 / 위산억제제 장기 투여 시 시아노코발라민(비타민B12) 흡수장애 가능성", disp_nut="비타민 B12"))
    r.append(dep(39, "덱스란소프라졸", "마그네슘", "moderate", "201802450", "덱시라졸캡슐30밀리그램(덱스란소프라졸)",
                 "이상반응(대사 및 영양 장애) / 저마그네슘혈증"))
    # E04 리세드론산 (건토넬정35mg 201903166) — 알렌드론산 29 패턴(칼슘)
    r.append(absn(40, "리세드론산", "칼슘", "high", "201903166", "건토넬정35밀리그램(무수리세드론산나트륨)",
                  "사용상의 주의사항 / 다가 양이온(칼슘·마그네슘·철·알루미늄) 함유 약물·식품이 이 약 흡수 방해 → 동시 복용 회피(라벨상 칼슘·철·마그네슘 포괄)"))
    # E06 이반드론산 (경보이반드로네이트정 201306285)
    r.append(absn(41, "이반드론산", "칼슘", "high", "201306285", "경보이반드로네이트정(이반드론산나트륨일수화물)",
                  "상호작용 / 우유·음식물·칼슘·다가 양이온(알루미늄·마그네슘·철)이 이 약 흡수 저해 → 경구투여 후 1시간 회피(라벨상 칼슘·철·마그네슘 포괄)"))
    # E08 세프디니르 (세프다나캡슐100mg 200711458)
    r.append(absn(42, "세프디니르", "철분", "high", "200711458", "세프다나캡슐100밀리그램(세프디니르)",
                  "상호작용 / 철분제제와 병용 시 이 약 흡수를 약 1/10까지 저해 → 동시 복용 회피·부득이 시 3시간 이상 간격"))
    return r


# 절대 포함 금지(missing 3 + 에스오메프라졸/15행)
FORBIDDEN_INGREDIENTS = {"파모티딘", "라푸티딘", "니자티딘", "에스오메프라졸"}


def main():
    write = "--no-write" not in sys.argv
    v02 = json.load(open(V02, encoding="utf-8"))
    base = v02["relations"]
    assert len(base) == 30, f"기준 v0.2 relations 30 아님: {len(base)}"
    new = new_relations()

    # 안전 가드: 신규 id 충돌 없음, 금지 성분 없음
    base_ids = {r["id"] for r in base}
    new_ids = {r["id"] for r in new}
    assert not (base_ids & new_ids), "신규 relation id 가 기존과 충돌"
    assert new_ids == set(range(32, 43)), f"신규 id 32-42 아님: {sorted(new_ids)}"
    bad = [r["ingredient"] for r in new if r["ingredient"] in FORBIDDEN_INGREDIENTS]
    assert not bad, f"금지 성분 포함: {bad}"

    relations = base + new  # 기존 30 verbatim + 신규 11
    draft = {
        "meta": {
            "product": "MediStack",
            "version": "0.4-relations-draft",
            "kind": "relation_expansion_draft",
            "generated_at": CHECKED,
            "derived_from": "medistack_v0.2_beta_export.json (relation 30 verbatim)",
            "source_basis": "식약처 의약품통합정보시스템(nedrug) 허가사항 원문",
            "lifecycle_status_included": "verified_reference",
            "relation_count": len(relations),
            "relation_count_base": 30,
            "relation_count_new": len(new),
            "excluded_count": v02["meta"].get("excluded_count", 1),
            "published": False,
            "clinical_reviewed": False,
            "live": False,
            "data_url_unchanged": "./data/medistack_v0.2_beta_export.json",
            "note": ("DRAFT — 라이브 미반영. v0.2 relation 30 verbatim + source_confirmed A티어 7후보 신규 11건"
                     "(ids 32-42). 출처=허가사항(nedrug getItemDetail) 확인 완료(2026-06-13). missing 3"
                     "(파모티딘/라푸티딘/니자티딘 H2×B12)·에스오메프라졸 미포함. 실제 라이브 통합(DATA_URL flip"
                     "+full index relation_card flip+alias pool)은 별도 PM 게이트. published/clinical_reviewed=false."),
        },
        "disclaimers": v02.get("disclaimers", {}),
        "relations": relations,
        "excluded_v0_1": v02.get("excluded_v0_1", []),
    }

    print(f"기존 relation {len(base)} verbatim + 신규 {len(new)} = {len(relations)} (relation_count)")
    print("신규 relation:")
    for r in new:
        print(f"  id{r['id']:2d} {r['ingredient']}×{r['nutrient']} [{r['mechanism']}/{r['recommended_action']}/{r['evidence_level']}]")
    if write:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(draft, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"\n[write] {os.path.relpath(OUT, REPO)}")
    else:
        print("\n(--no-write)")
    print("\nBUILD RELATION EXPANSION DRAFT v1.1: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
