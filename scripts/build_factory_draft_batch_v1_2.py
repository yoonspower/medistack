#!/usr/bin/env python3
"""
build_factory_draft_batch_v1_2.py
MediStack relation factory — source_confirmed(+적대적 검증 통과) 후보만 **draft batch** 로 생성한다.

입력(읽기):
  data/relation_factory_source_check_v1_2.csv          (verify_factory_sources_v1_2.py 산출, 적대적 reconcile 반영)
  data/relation_factory_adversarial_verify_v1_2.json   (적대적 검증 verdict — itemseq_used·정정 evidence quote)

출력(분석 산출물만 — 라이브 미반영):
  data/relation_factory_draft_batch_v1_2.json          (draft relation, 신규 draft_id DF01..)
  data/relation_factory_draft_batch_preflight_v1_2.csv (승격 전 점검표)

⚠️ 절대 규칙:
  - pass_to_draft=true AND 적대적 verdict=confirm 인 후보만 생성.
  - 모든 draft 행: published=false·clinical_reviewed=false·do_not_implement_yet=true·
    review_required=true·source_required=true·**live_integration_forbidden=true**.
  - 칼륨 nutrient 행: product_link_allowed=false·potassium_safety_card=true(안전정책 승계).
  - display/management 는 참고정보 톤 템플릿(복용지시·추천·치료·예방·구매 어휘 0).
  - 라이브 export / full index / alias / src 무수정. relations 55 그대로.
사용: python3 scripts/build_factory_draft_batch_v1_2.py
종료 코드: 0 정상.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
SRC_CSV = os.path.join(DATA, "relation_factory_source_check_v1_2.csv")
ADV_JSON = os.path.join(DATA, "relation_factory_adversarial_verify_v1_2.json")
OUT_JSON = os.path.join(DATA, "relation_factory_draft_batch_v1_2.json")
OUT_CSV = os.path.join(DATA, "relation_factory_draft_batch_preflight_v1_2.csv")
CHECKED_AT = "2026-06-14"
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

# 적대적 검증에서 확인된 대표 품목명(pointer 표기용) + 라벨 섹션
PRODUCT_HINT = {
    "199800324": "메니솔론정4mg(메틸프레드니솔론)",
    "202203949": "덱사하이정4밀리그램(덱사메타손)",
    "199907231": "플로리네프정(미분화플루드로코르티손아세테이트)",
    "201403403": "아세타졸정(아세타졸아미드)",
    "199001306": "유레틴정(아조세미드)",
    "201503196": "테트로닌정5㎍(리오티로닌나트륨)",
}
SECTION = {  # candidate_id -> 라벨 섹션 표기
    "D-CORT-03": "이상반응(체액ㆍ전해질)", "D-CORT-04": "이상반응(체액ㆍ전해질)",
    "D-CORT-06": "이상반응(체액과 전해질 장애)", "D-CA-01": "이상반응(대사)·일반적 주의",
    "D-LOOP-04": "부작용(대사)·고령자 주의", "D-THY-02": "상호작용", "D-THY-03": "상호작용",
}
# draft_id 부여(라이브 D01-D14 와 분리된 factory 네임스페이스)
DRAFT_ID_ORDER = ["D-CORT-03", "D-CORT-04", "D-CORT-06", "D-CA-01", "D-LOOP-04", "D-THY-02", "D-THY-03"]


def split_copy(safe):
    if " / " in safe:
        disp, mgmt = safe.split(" / ", 1)
        return disp.strip(), mgmt.strip()
    return safe.strip(), ""


def main():
    rows = {r["candidate_id"]: r for r in csv.DictReader(open(SRC_CSV, encoding="utf-8"))}
    adv = {v["candidate_id"]: v for v in json.load(open(ADV_JSON, encoding="utf-8"))["verdicts"]}

    drafts = []
    pre_rows = []
    for i, cid in enumerate(DRAFT_ID_ORDER, start=1):
        r = rows[cid]
        v = adv[cid]
        # 게이트: pass_to_draft=true AND adversarial confirm
        assert r["pass_to_draft"] == "true", f"{cid} pass_to_draft != true"
        assert v["verdict"] == "confirm" and v["recommended_status"] == "source_confirmed", f"{cid} 적대적 미통과"
        seq = (v["itemseq_used"] or r["itemseqs_checked"].split(";")[0]).split(";")[0].strip()
        quote = (v["corrected_evidence_quote"] or r["evidence_snippet"]).strip().strip('"')
        ksafe = r["potassium_safety_card"] == "true"
        mech = r["mechanism"]
        action = r["relation_type"]
        disp, mgmt = split_copy(r["safe_user_copy"])
        draft_id = f"DF{i:02d}"
        pointer = (f"식약처 허가사항(nedrug) / {PRODUCT_HINT.get(seq, r['drug_ingredient'])}, itemSeq {seq} / "
                   f"{SECTION.get(cid, '')} / '{quote}' / 확인일 {CHECKED_AT}")
        d = {
            "draft_id": draft_id,
            "source_batch": "relation_factory_v1_2",
            "source_candidate_id": cid,
            "ingredient": r["drug_ingredient"],
            "nutrient": r["nutrient"],
            "mechanism": mech,
            "recommended_action": action,
            "evidence_level": "high",
            "display_text_ko": disp,
            "management_ko": mgmt,
            "product_link_allowed": (False if ksafe else True),
            "potassium_safety_card": bool(ksafe),
            "requires_clinical_review": False,
            "published": False,
            "clinical_reviewed": False,
            "review_required": True,
            "source_required": True,
            "do_not_implement_yet": True,
            "live_integration_forbidden": True,
            "adversarial_verified": True,
            "note": r["internal_note"],
            "source": {
                "type": "허가사항",
                "url": DETAIL_URL.format(seq),
                "pointer": pointer,
                "checked_at": CHECKED_AT,
            },
        }
        drafts.append(d)
        pre_rows.append({
            "draft_id": draft_id, "source_candidate_id": cid, "ingredient": r["drug_ingredient"],
            "nutrient": r["nutrient"], "mechanism": mech, "action": action,
            "potassium_safety_card": str(ksafe).lower(),
            "product_link_allowed": str(not ksafe).lower(),
            "source_itemseq": seq, "evidence_strength": r["evidence_strength"],
            "adversarial_verdict": v["verdict"], "risk_level": r["risk_level"],
            "published": "false", "clinical_reviewed": "false", "do_not_implement_yet": "true",
            "live_integration_forbidden": "true",
            "pass_to_integrate": "false(PM 승인 별도 단계)",
            "checked_at": CHECKED_AT,
        })

    k_rows = [d for d in drafts if d["nutrient"] == "칼륨"]
    meta = {
        "draft_name": "relation_factory_draft_batch_v1_2",
        "created_at": CHECKED_AT,
        "status": "DRAFT — NOT LIVE",
        "do_not_implement_yet": True,
        "live_integration_forbidden": True,
        "published": False,
        "clinical_reviewed": False,
        "count": len(drafts),
        "note": ("relation factory 후보(75건) 대량 source check + 적대적 검증(독립 agent 라벨 재fetch·4렌즈 반증) "
                 "을 모두 통과한 source_confirmed 후보의 draft relation. 라이브 export(relations 55)에는 "
                 "반영되지 않았고 어떤 것도 구현하지 않는다. 각 행 published=false·clinical_reviewed=false·"
                 "review_required=true·source_required=true·do_not_implement_yet=true·live_integration_forbidden=true. "
                 "실제 채택은 PM 승인 + 검토 통과 후 별도 단계에서만. draft id(DFxx)는 라이브 id 공간 및 D01-D14 와 분리. "
                 "제품/제휴/복용지시/추천/치료/예방/구매 톤 0(참고정보 톤). 칼륨 행은 product_link_allowed=false·"
                 "potassium_safety_card=true 승계."),
        "verification_source": ("scripts/verify_factory_sources_v1_2.py + scripts/factory-source-adversarial-verify "
                                "workflow / data/relation_factory_source_check_v1_2.csv + "
                                "data/relation_factory_adversarial_verify_v1_2.json"),
        "potassium_rows": [d["draft_id"] for d in k_rows],
        "refuted_examples": ("F-FQ-01(목시플록사신×칼슘): 라벨이 '흡수 정도는 영향 받지 않음·임상적 관련성 없음' "
                             "→ 적대적 검증 reject. 세팔로스포린×철 10종: 라벨 미기재 reject. "
                             "레보티록신×Mg/아연: 미기재 reject. 이뇨제/스테로이드 11종: 국내 단일 경구제 미확보 needs_review."),
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "draft_relations": drafts}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    cols = list(pre_rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(pre_rows)

    print(f"draft batch 생성: {len(drafts)}건")
    for d in drafts:
        print(f"  {d['draft_id']} {d['source_candidate_id']:10s} {d['ingredient']}×{d['nutrient']} "
              f"({d['mechanism']}/{d['recommended_action']}, kcard={d['potassium_safety_card']})")
    print(f"칼륨 행: {len(k_rows)} (product_link_allowed=false·potassium_safety_card=true)")
    print(f"[write] {os.path.relpath(OUT_JSON, REPO)}")
    print(f"[write] {os.path.relpath(OUT_CSV, REPO)}")
    print("\n라이브 미반영(live_integration_forbidden=true). relations 55 그대로.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
