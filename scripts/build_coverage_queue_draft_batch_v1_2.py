#!/usr/bin/env python3
"""
build_coverage_queue_draft_batch_v1_2.py
MediStack relation factory (batch2, coverage-queue) — source_confirmed(+적대적 검증 통과) 후보만
**draft batch** 로 생성한다. build_factory_draft_batch_v1_2.py 패턴 승계, data-driven(하드코딩 없음).

입력(읽기):
  data/coverage_queue_source_check_v1_2.csv          (pass_to_draft=true 행)
  data/coverage_queue_adversarial_verify_v1_2.json   (final_verdict=confirm 만 통과)
출력(분석 산출물만 — 라이브 미반영):
  data/coverage_queue_draft_batch_v1_2.json
  data/coverage_queue_draft_batch_preflight_v1_2.csv

⚠️ 절대 규칙:
  - pass_to_draft=true AND 적대적 final_verdict=confirm 인 후보만 생성.
  - 모든 draft 행: published=false·clinical_reviewed=false·reviewed_by 공란·do_not_implement_yet=true·
    review_required=true·source_required=true·**live_integration_forbidden=true**·source_confirmed=true.
  - 칼륨 nutrient 행: product_link_allowed=false·potassium_safety_card=true(안전정책 승계).
  - display/management 는 참고정보 톤(복용지시·추천·치료·예방·구매 0).
  - 라이브 export / full index / alias / src 무수정. relations 57 그대로.
  - confirmed 0건이면 빈 batch(count=0)로 생성(정상 — 잘못된 relation 차단이 우선).
사용: python3 scripts/build_coverage_queue_draft_batch_v1_2.py
종료 코드: 0 정상.
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
SRC_CSV = os.path.join(DATA, "coverage_queue_source_check_v1_2.csv")
ADV_JSON = os.path.join(DATA, "coverage_queue_adversarial_verify_v1_2.json")
OUT_JSON = os.path.join(DATA, "coverage_queue_draft_batch_v1_2.json")
OUT_CSV = os.path.join(DATA, "coverage_queue_draft_batch_preflight_v1_2.csv")
CHECKED_AT = "2026-06-14"
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"


def split_copy(safe):
    if " / " in safe:
        disp, mgmt = safe.split(" / ", 1)
        return disp.strip(), mgmt.strip()
    return safe.strip(), ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC_CSV, help="source-check CSV(기본=batch2)")
    ap.add_argument("--adv", default=ADV_JSON, help="adversarial verify JSON(기본=batch2)")
    ap.add_argument("--out-json", default=OUT_JSON, help="draft batch JSON 출력(기본=batch2)")
    ap.add_argument("--out-csv", default=OUT_CSV, help="preflight CSV 출력(기본=batch2)")
    ap.add_argument("--id-start", type=int, default=1, help="draft_id(CQFxx) 시작 번호(batch3 는 CQF01 라이브 승격됨 → 2)")
    ap.add_argument("--batch-name", default="coverage_queue_draft_batch_v1_2", help="meta.draft_name")
    ap.add_argument("--source-batch", default="coverage_queue_factory_v1_2", help="각 draft 의 source_batch 라벨")
    ap.add_argument("--live-relations", type=int, default=57, help="현재 라이브 relations(메타 노트용)")
    args = ap.parse_args()
    src_csv, adv_json, out_json, out_csv = args.src, args.adv, args.out_json, args.out_csv

    rows = {r["candidate_id"]: r for r in csv.DictReader(open(src_csv, encoding="utf-8"))}
    adv = json.load(open(adv_json, encoding="utf-8"))
    # 적대적 통과(final_verdict=confirm) candidate_id 집합 + 정정 인용
    adv_pass = {}
    for v in adv.get("verifications", []):
        if v.get("final_verdict") == "confirm":
            adv_pass[v["candidate_id"]] = v

    confirmed = [cid for cid, r in rows.items()
                 if r["source_status"] == "source_confirmed" and r["pass_to_draft"] == "true"
                 and cid in adv_pass]
    confirmed.sort()

    drafts = []
    pre_rows = []
    for i, cid in enumerate(confirmed, start=args.id_start):
        r = rows[cid]
        v = adv_pass[cid]
        seq = (r["itemseqs_checked"] or "").split(";")[0].strip()
        quote = (v.get("corrected_evidence_quote") or r["evidence_snippet"]).strip().strip('"')
        ksafe = r["potassium_safety_card"] == "true"
        mech = r["mechanism"]
        action = r["relation_type"]
        disp, mgmt = split_copy(r["safe_user_copy"])
        draft_id = f"CQF{i:02d}"  # coverage-queue factory namespace (DF01-07 와 분리)
        pointer = (f"식약처 허가사항(nedrug) / {v.get('product') or r['drug_ingredient']}, itemSeq {seq} / "
                   f"상호작용(병용 신중) / '{quote}' / 확인일 {CHECKED_AT}")
        d = {
            "draft_id": draft_id,
            "source_batch": args.source_batch,
            "source_candidate_id": cid,
            "ingredient": r["drug_ingredient"],
            "nutrient": r["nutrient"],
            "mechanism": mech,
            "recommended_action": action,
            "evidence_level": r["evidence_strength"] or "high",
            "display_text_ko": disp,
            "management_ko": mgmt,
            "product_link_allowed": (False if ksafe else True),
            "potassium_safety_card": bool(ksafe),
            "requires_clinical_review": False,
            "source_confirmed": True,
            "published": False,
            "clinical_reviewed": False,
            "reviewed_by": "",
            "review_required": True,
            "source_required": True,
            "do_not_implement_yet": True,
            "live_integration_forbidden": True,
            "adversarial_verified": True,
            "risk_level": r["risk_level"],
            "note": r["internal_note"],
            "source": {
                "type": "허가사항",
                "url": DETAIL_URL.format(seq) if seq else "",
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
            "adversarial_verdict": v.get("final_verdict"), "risk_level": r["risk_level"],
            "published": "false", "clinical_reviewed": "false", "reviewed_by": "",
            "do_not_implement_yet": "true", "live_integration_forbidden": "true",
            "pass_to_integrate": "false(PM 승인 별도 단계)", "checked_at": CHECKED_AT,
        })

    k_rows = [d for d in drafts if d["nutrient"] == "칼륨"]
    meta = {
        "draft_name": args.batch_name,
        "created_at": CHECKED_AT,
        "status": "DRAFT — NOT LIVE",
        "do_not_implement_yet": True,
        "live_integration_forbidden": True,
        "published": False,
        "clinical_reviewed": False,
        "count": len(drafts),
        "note": ("coverage 우선순위 큐(Top100) precheck → 안전후보 nedrug source check → 적대적 검증(독립 회의론자 "
                 "라벨 재fetch·refute-by-default)을 모두 통과한 source_confirmed 후보의 draft relation. "
                 f"라이브 export(relations {args.live_relations})에는 반영되지 않았고 어떤 것도 구현하지 않는다. 각 행 published=false·"
                 "clinical_reviewed=false·reviewed_by 공란·review_required=true·source_required=true·"
                 "do_not_implement_yet=true·live_integration_forbidden=true. 실제 채택은 PM 승인 + 검토 통과 후 "
                 "별도 단계에서만. draft id(CQFxx)는 라이브 id 공간 및 DF01-07 와 분리. 제품/제휴/복용지시/추천/치료/"
                 "예방/구매 톤 0(참고정보 톤). 칼륨 행은 product_link_allowed=false·potassium_safety_card=true 승계."),
        "verification_source": ("scripts/verify_coverage_queue_sources_v1_2.py + "
                                "medistack-cq-adversarial-verify workflow / "
                                "data/coverage_queue_source_check_v1_2.csv + "
                                "data/coverage_queue_adversarial_verify_v1_2.json"),
        "potassium_rows": [d["draft_id"] for d in k_rows],
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "draft_relations": drafts}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    cols = (list(pre_rows[0].keys()) if pre_rows else
            ["draft_id", "source_candidate_id", "ingredient", "nutrient", "mechanism", "action",
             "potassium_safety_card", "product_link_allowed", "source_itemseq", "evidence_strength",
             "adversarial_verdict", "risk_level", "published", "clinical_reviewed", "reviewed_by",
             "do_not_implement_yet", "live_integration_forbidden", "pass_to_integrate", "checked_at"])
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(pre_rows)

    print(f"draft batch 생성: {len(drafts)}건")
    for d in drafts:
        print(f"  {d['draft_id']} {d['source_candidate_id']:8s} {d['ingredient']}×{d['nutrient']} "
              f"({d['mechanism']}/{d['recommended_action']}, kcard={d['potassium_safety_card']})")
    print(f"칼륨 행: {len(k_rows)}")
    print(f"[write] {os.path.relpath(out_json, REPO)}")
    print(f"[write] {os.path.relpath(out_csv, REPO)}")
    print(f"\n라이브 미반영(live_integration_forbidden=true). relations {args.live_relations} 그대로.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
