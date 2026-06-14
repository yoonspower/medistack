#!/usr/bin/env python3
"""
build_antacid_interaction_draft_v1_2.py
MediStack antacid_interaction 트랙 — 단일 게이트(source_confirm_gate_v1_2.json)가 antacid_draft_confirmed 한
후보만 **antacid 전용 draft batch** 로 생성한다(라이브/일반 relation 미반영, live_integration_forbidden=true).

설계(antacid_interaction_track_v1_2.md §3 레이어 분리):
  - 표면 relation_type = antacid_interaction (중립 참고정보 톤)
  - 내부 label_directive_type = avoid_concomitant | separation (라벨 원문 강도 보존)
  - 내부 counterpart_category = al_mg_antacid (영양소 트랙 아님 — Mg 보충제 오인 차단)
  - label_quote = 허가사항 원문 인용(손실 없이 보존)
  - display copy = §4 PM 승인 템플릿 verbatim(앱 자신의 지시 아님 / 출처 귀속 / 병용 프레이밍 유지 / 상담 종결)
  - product_link_allowed=false, potassium_safety_card=false, published=false, clinical_reviewed=false

⚠️ 보호 데이터 무수정(읽기전용 입력 + draft/candidates 산출물만 write). source_confirmed 판정은 하지 않는다(게이트가 함).
출력:
  data/drafts/antacid_interaction_draft_batch_v1_2.json
  data/candidates/antacid_interaction_candidates_v1_2.csv
사용: python3 scripts/build_antacid_interaction_draft_v1_2.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
GATE = os.path.join(DATA, "review", "source_confirm_gate_v1_2.json")
EVID = os.path.join(DATA, "candidates", "antacid_interaction_evidence_v1_2.json")
OUT_DRAFT = os.path.join(DATA, "drafts", "antacid_interaction_draft_batch_v1_2.json")
OUT_CAND = os.path.join(DATA, "candidates", "antacid_interaction_candidates_v1_2.csv")

# §4 PM 승인 display 템플릿(verbatim). 출처 귀속·병용 프레이밍 유지·상담 종결. 영양소 보충제 오인 차단(상대=제산제 명시).
DISPLAY_TEMPLATE = ("일부 알루미늄·마그네슘 함유 제산제와 함께 사용할 때 약물 흡수에 영향을 줄 수 있다는 "
                    "허가사항 문구가 있습니다. 함께 사용하는 경우에는 약사 또는 의사에게 확인하세요.")
DIRECTIVE_LABEL = {"avoid_concomitant": "avoid_concomitant", "separation_or_spacing": "separation"}


def main():
    gate = json.load(open(GATE, encoding="utf-8"))
    evid = {e["candidate_id"]: e for e in json.load(open(EVID, encoding="utf-8"))["evidence"]}
    at = gate["antacid_track"]

    drafts = []
    for g in at:
        if g["verdict"] != "antacid_draft_confirmed":
            continue
        ev = evid.get(g["candidate_id"], {})
        seqs = ev.get("itemseqs_checked", []) or g.get("itemseqs_checked", [])
        seq_hit = ev.get("seq_hit") or (seqs[0] if seqs else "")
        drafts.append({
            "draft_id": g["candidate_id"],
            "ingredient": g["ingredient"],
            "relation_type": "antacid_interaction",          # 표면(중립)
            "counterpart_category": "al_mg_antacid",          # 내부: 상대=Al/Mg 제산제(영양소 아님)
            "label_directive_type": DIRECTIVE_LABEL.get(g.get("directive_kind"), g.get("directive_kind")),
            "copy_risk_level": g.get("copy_strength", "low"),
            "display_text_ko": DISPLAY_TEMPLATE,
            "management_ko": "",                               # 상담 트리거는 display 종결문에 포함
            "label_quote": ev.get("quote", "")[:400],          # 원문 강도 보존(내부)
            "product_link_allowed": False,
            "potassium_safety_card": False,
            "published": False,
            "clinical_reviewed": False,
            "review_required": True,
            "source_required": True,
            "do_not_implement_yet": True,
            "live_integration_forbidden": True,
            "adversarial_verified": False,                     # 본 라운드 미수행(설계 단계). 승격 전 적대검증 필수.
            "note": ("표면 antacid_interaction(중립)+내부 directive 보존 레이어. 영양소(Mg) relation 아님. "
                     "surface 구현·승격은 PM 결정 + 적대검증(copy 충실성) 후 별도 단계."),
            "source": {
                "type": "허가사항",
                "url": ev.get("url", ""),
                "pointer": f"식약처 nedrug getItemDetail / {g['ingredient']} / itemSeq {seq_hit} / 상호작용·복약정보 Al/Mg 제산제 directive / '{ev.get('quote','')[:160]}' / 확인일 2026-06-14",
                "checked_at": "2026-06-14",
            },
        })

    out = {
        "meta": {
            "draft_name": "antacid_interaction_draft_batch_v1_2", "created_at": "2026-06-14",
            "status": "DRAFT — NOT LIVE / antacid 전용 트랙(영양소 relation 미반영)",
            "track": "antacid_interaction", "do_not_implement_yet": True,
            "live_integration_forbidden": True, "published": False, "clinical_reviewed": False,
            "count": len(drafts),
            "gate": "scripts/source_confirm_gate_v1_2.py / data/review/source_confirm_gate_v1_2.json (단일 fail-closed)",
            "note": ("antacid_interaction 트랙은 '약물 × Al/Mg 제산제(약물 카테고리)'이며 영양소(철/칼슘/Mg/아연/칼륨) "
                     "보충제 relation 과 개념적으로 분리된다. surface=중립 antacid_interaction, 내부=label_directive_type/"
                     "counterpart_category/label_quote 로 라벨 원문 강도 보존. 마그네슘 영양제로 오인되지 않게 상대를 제산제로 명시. "
                     "이번 라운드 live·일반 relation 미반영. reject/needs_review 후보는 candidates CSV 참조."),
        },
        "draft_relations": drafts,
    }
    os.makedirs(os.path.dirname(OUT_DRAFT), exist_ok=True)
    json.dump(out, open(OUT_DRAFT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # candidates CSV: 전체 6후보(게이트 판정 포함)
    cols = ["candidate_id", "ingredient", "verdict", "label_directive_type", "counterpart_category",
            "copy_risk_level", "itemseqs_checked", "draft_eligible", "live_integration_forbidden",
            "gate_reason", "label_quote"]
    with open(OUT_CAND, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for g in at:
            ev = evid.get(g["candidate_id"], {})
            w.writerow({
                "candidate_id": g["candidate_id"], "ingredient": g["ingredient"], "verdict": g["verdict"],
                "label_directive_type": DIRECTIVE_LABEL.get(g.get("directive_kind"), g.get("directive_kind", "")),
                "counterpart_category": "al_mg_antacid",
                "copy_risk_level": g.get("copy_strength", ""),
                "itemseqs_checked": ";".join(ev.get("itemseqs_checked", []) or []),
                "draft_eligible": g["draft_eligible"], "live_integration_forbidden": g["live_integration_forbidden"],
                "gate_reason": g["gate_reason"], "label_quote": ev.get("quote", "")[:200],
            })
    print(f"antacid draft: {len(drafts)}건 / candidates: {len(at)}건")
    for d in drafts:
        print(f"  DRAFT {d['draft_id']} {d['ingredient']} [{d['label_directive_type']}] risk={d['copy_risk_level']} live_forbidden={d['live_integration_forbidden']}")
    print(f"[write] {os.path.relpath(OUT_DRAFT, REPO)}")
    print(f"[write] {os.path.relpath(OUT_CAND, REPO)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
