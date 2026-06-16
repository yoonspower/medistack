#!/usr/bin/env python3
"""
integrate_theme_map_draft_batch_v1_3.py
MediStack — theme map expansion 신규 family **6건**(프롬프트 8 적대검증 완료 · 프롬프트 9 harvester 편입)
live 통합 **준비/드라이런** 스크립트. integrate_antacid_fex_v1_2.py 패턴 승계(단일 → 배치 6건).

대상(seed: data/config/theme_map_seeds_v1_3.json · 단일 진실원 = theme_map_harvest_provider_v1_3.build):
  TM-LIP-01     오르리스타트       × 지용성 비타민(A·D·E·K·베타카로틴)  (separation · fat_soluble_vitamin)
  TM-LIP-02     콜레스티라민       × 지용성 비타민(A·D·K)             (separation · fat_soluble_vitamin)
  TM-CEPH-AC-01 세프포독심프록세틸 × 위산 감소·중화 약물(제산제·H2)   (separation · acid_reducing_drug)
  TM-CEPH-AC-02 세프디토렌피복실   × 제산제·위산 감소 약물(H2·PPI 등) (avoid_concomitant · acid_reducing_drug)
  TM-CHEL-01-FE 페니실라민         × 철분                            (separation · null=일반 영양소)
  TM-CHEL-01-ZN 페니실라민         × 아연                            (separation · null=일반 영양소)

⚠️⚠️ 기본값이 **--dry-run(쓰기 0)** 이다. live export 기록은 **--pm-approved + --reviewer-note PATH** 둘 다 있어야만
수행된다(별도 PM 승인 + clinical reviewer 전까지 절대 금지). 본 세션은 --pm-approved 를 호출하지 않는다.
  --pm-approved 없이 실행 시: 라이브/보호 데이터 **무수정**. 예상 통합 결과(live-shape relation 6건 + 예상 카운트
  60→66 + 각 후보의 현행 v0.2 validator 통과/차단 증거 + live 통합 선행조건)를 **review 산출물**
  data/review/theme_map_live_dryrun_v1_3.json (live 아님)에 기록한다.

  reviewer 노트 인터록(check_reviewer_note) — 6건 전건 + category 결정 + grouping 결정 + 아연 mechanism 결정 +
  verified_reference 동의를 **의미 수준**으로 강제. SAMPLE/placeholder/빈 노트/clinical=true·제품 추천 허용 거부.
  reviewer 노트 템플릿은 docs/MediStack_reviewer_package_theme_map_v1_3.md §reviewer-note 참조.

⚠️ live 통합 선행조건(이번 작업 범위 밖 · 별도 PR):
  1) [validator] scripts/validate_medistack_v0_2_export.py 검사 #15 가 avoid_concomitant 를 al_mg_antacid 로만
     허용 → acid_reducing_drug 채택 시 TM-CEPH-AC-02(avoid_concomitant) 가 차단됨. 해당 검사를
     acid_reducing_drug 포함으로 확장해야 함(또는 reviewer 가 TM-CEPH-AC-02 를 separation 으로 하향 결정).
  2) [src] src/js/guards.js getFacets 가 counterpart_category 있는 relation 을 영양소 facet 에서 일괄 제외 →
     fat_soluble_vitamin(영양소군)은 facet 에 포함하고 drug category(acid_reducing_drug·al_mg_antacid)만 제외하도록
     nutrient_categories vs drug_categories 분기 필요.
  3) [src] src/js/render.js 가 acid_reducing_drug 전용 chip/kicker 미보유(현재 avoid_concomitant chip 은 'Al/Mg 함유
     제산제' 문구 고정) → acid_reducing_drug 용 chip/kicker(제산제·H2/PPI 약물 표기) 필요.
  ※ 본 드라이런은 위 선행조건을 **문서화/증명**만 한다(src/validator/export 무수정).

draft → live 매핑(AT-ITZ/AT-FEX 패턴 준용):
  ingredient = drug_ingredient · nutrient = counterpart · mechanism/recommended_action/evidence_level = draft 값
  display_text_ko = display_text_ko_draft · management_ko = management_copy_draft
  counterpart_category: fat_soluble_vitamin/acid_reducing_drug 는 명시, null(페니실라민 FE/ZN)은 **필드 생략**
    (일반 영양소 relation 과 동일 — 영양소 facet 에 정상 노출).
  product_link_allowed=false · potassium_safety_card=false · requires_clinical_review=false
  source = {type:'허가사항', url, pointer(itemSeq+section+라벨 원문 quote+확인일)}. draft-전용/금지 필드 strip.

사용:
  python3 scripts/integrate_theme_map_draft_batch_v1_3.py                                  # (기본) dry-run — 쓰기 0
  python3 scripts/integrate_theme_map_draft_batch_v1_3.py --pm-approved --reviewer-note X  # live(별도 PM·reviewer 후, 본 세션 금지)
종료코드: 0 DONE/skip/dry, 1 STOP(가드/노트 위반).
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
DRYRUN_ARTIFACT = os.path.join(DATA, "review", "theme_map_live_dryrun_v1_3.json")
V0_2_VALIDATOR = os.path.join(HERE, "validate_medistack_v0_2_export.py")

# 단일 진실원 — provider.build() 가 config+draft+adversarial 을 검증해 confirmed/hold 행을 만든다.
_spec = importlib.util.spec_from_file_location(
    "tmprov", os.path.join(HERE, "theme_map_harvest_provider_v1_3.py"))
tmprov = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tmprov)

BASELINE_RELATIONS = 60   # 현재 라이브(예상 전). AT-FEX/칼륨이 먼저 통합되면 runtime max+1 로 자동 조정.
CONFIRMED_AT = "2026-06-16"   # source-check(round2) + 적대검증 확인일
CONFIRMED_IDS = ["TM-LIP-01", "TM-LIP-02", "TM-CEPH-AC-01", "TM-CEPH-AC-02", "TM-CHEL-01-FE", "TM-CHEL-01-ZN"]
NUTRIENT_CATEGORIES = {"fat_soluble_vitamin", None}     # 영양소(군) — 약물 아님
DRUG_CATEGORIES = {"acid_reducing_drug", "al_mg_antacid"}  # 약물 counterpart
ALLOWED_CATEGORIES = NUTRIENT_CATEGORIES | DRUG_CATEGORIES

# draft-전용/금지 필드 — projected_live_relation 에 누출되면 안 됨(AT-FEX 패턴 + theme map 필드).
DRAFT_ONLY = {"candidate_id", "track", "family", "counterpart", "counterpart_type", "confidence",
              "risk_level", "risk_flags", "source_itemseq", "source_section", "source_quote",
              "source_url", "display_text_ko_draft", "management_copy_draft", "adversarial_verdict",
              "adversarial_verified", "adversarial_next_action", "final_status", "recommended_pm_action",
              "reviewer_needed", "do_not_implement_yet", "live_integration_forbidden", "published",
              "clinical_reviewed", "reviewed_by", "status", "drug_ingredient"}

# ── reviewer 노트 인터록(AT-FEX/칼륨 패턴 + theme map 결정 요건) ──
APPROVAL_TOKENS = ("approved", "승인")
NOTE_SAMPLE_SENTINELS = ("SAMPLE", "샘플", "NOT-VALID", "NOT A REAL APPROVAL",
                         "NOT_FOR_PROMOTION", "TEMPLATE-ONLY", "PLACEHOLDER")
NOTE_PLACEHOLDER_MARKERS = ("____", "YYYY-MM-DD", "<검수자", "<reviewer", "<날짜", "<date")
GROUPING_MARKERS = ("grouping 결정", "그룹 단일", "개별 카드", "비타민별 분리", "묶음 카드")
MECHANISM_MARKERS = ("mechanism", "기전")
NOT_CLINICAL_MARKERS = ("clinical_reviewed=true 아님", "임상검수 승격 아님", "임상 검수 승격 아님",
                        "clinical_reviewed 승격 아님")
NOT_PRODUCT_MARKERS = ("제품·구매·제휴·보충제 추천 없음", "제품 추천 없음", "제품 추천 아님",
                       "상업·보충 권유 없음", "보충 추천 없음")
# 거부: clinical/published=true 승격 '요구' 또는 검수완료 '단정'(부정문 '아님/없음' 직후는 제외)
CLINICAL_PROMO_RE = re.compile(
    r"(clinical_reviewed|published)[ \t]*[=:]?[ \t]*true(?![ \t]*(아님|아닙|없음))"
    r"|((약사|임상)[ \t]*검수[ \t]*완료|식약처[ \t]*승인)(?![ \t]*(아님|아닙|없음))")
# 거부: 제품/보충 추천을 '허용/가능/추가' 하는 문구(부정 '안/불가/금지/없음' 직후는 제외)
PRODUCT_PERMISSION_RE = re.compile(
    r"(제품[ \t]*추천|보충제?[ \t]*추천|구매[ \t]*링크|제휴[ \t]*링크|제품[ \t]*링크)"
    r"[ \t]*(허용|가능|추가|노출[ \t]*승인)(?![ \t]*(안|불가|금지|없))")


def check_reviewer_note(reviewer_note):
    """theme map 6건 live 통합 reviewer 노트 게이트.
    (note_content, violations) 반환 — violations 빈 리스트 = 통과. main() 과 테스트가 공유."""
    bad = []
    note = ""
    if reviewer_note and os.path.exists(reviewer_note):
        with open(reviewer_note, encoding="utf-8") as f:
            note = f.read()
    if not note.strip():
        bad.append(f"노트 비공란 필요(--reviewer-note PATH). 받은 값: {reviewer_note!r}")
        return note, bad
    up, low = note.upper(), note.lower()
    for s in NOTE_SAMPLE_SENTINELS:
        if s.upper() in up:
            bad.append(f"SAMPLE/예시 토큰 감지('{s}') — 템플릿 그대로 승격 거부")
            break
    for m in NOTE_PLACEHOLDER_MARKERS:
        if m in note:
            bad.append(f"미기입 placeholder 감지('{m}') — 검수자/검토일 빈칸 채우기 필요")
            break
    if not any(t in low or t in note for t in APPROVAL_TOKENS):
        bad.append(f"승인 표기({'/'.join(APPROVAL_TOKENS)}) 없음")
    miss = [c for c in CONFIRMED_IDS if c not in note]
    if miss:
        bad.append(f"candidate_id 미명시(6건 전건 필요): {miss}")
    if "acid_reducing_drug" not in note:
        bad.append("category 결정 'acid_reducing_drug' 미명시")
    if "fat_soluble_vitamin" not in note:
        bad.append("category 결정 'fat_soluble_vitamin' 미명시")
    if not any(g in note for g in GROUPING_MARKERS):
        bad.append("grouping 결정 미명시(지용성비타민 group/분리·페니실라민 FE/ZN 묶음/개별)")
    if not any(m in note for m in MECHANISM_MARKERS):
        bad.append("TM-CHEL-01-ZN 아연 mechanism 결정 미명시(absorption vs interaction)")
    if "verified_reference" not in note:
        bad.append("verified_reference 노출 동의 미명시")
    if not any(m in note for m in NOT_CLINICAL_MARKERS):
        bad.append("clinical_reviewed=true 아님 명시 필요(verified_reference 천장)")
    if not any(m in note for m in NOT_PRODUCT_MARKERS):
        bad.append("제품/보충 추천 아님 명시 필요")
    if CLINICAL_PROMO_RE.search(note):
        bad.append("clinical_reviewed/published=true 승격 요구 또는 검수완료 단정 — 금지(verified_reference 천장)")
    if PRODUCT_PERMISSION_RE.search(note):
        bad.append("제품/보충 추천 허용 문구 — 금지")
    return note, bad


def draft_to_live(row, new_id):
    """provider confirmed 행 → live-shape relation(draft-전용 필드 strip)."""
    ing = row["drug_ingredient"]
    seq = str(row["source_itemseq"])
    quote = (row.get("source_quote") or "").strip()
    section = row.get("source_section", "")
    pointer = (f"식약처 nedrug getItemDetail / {ing} / itemSeq {seq} / {section} / "
               f"'{quote}' / 확인일 {CONFIRMED_AT}")
    rel = {
        "id": new_id,
        "ingredient": ing,
        "nutrient": row["counterpart"],
        "mechanism": row["mechanism"],
        "recommended_action": row["recommended_action"],
        "evidence_level": row["evidence_level"],
        "display_text_ko": row["display_text_ko_draft"],
        "management_ko": row.get("management_copy_draft", ""),
        "product_link_allowed": False,
        "potassium_safety_card": False,
        "requires_clinical_review": False,
        "source": {"type": "허가사항", "url": row["source_url"], "pointer": pointer},
    }
    cat = row.get("counterpart_category")
    if cat is not None:   # null(페니실라민 FE/ZN) 은 필드 생략 → 일반 영양소 relation 처럼 facet 노출
        rel["counterpart_category"] = cat
    return rel


def guard_projected(cid, row, rel):
    """projected relation 통합 자격 가드. 위반 메시지 리스트(빈=통과)."""
    bad = []
    cat = rel.get("counterpart_category")  # 생략 시 None
    if cat not in ALLOWED_CATEGORIES:
        bad.append(f"{cid}: counterpart_category 비허용({cat!r})")
    # antacid_drug counterpart 는 약물 category 여야 하고 '약물' 표기 + al_mg_antacid 로 좁히지 않음
    if row.get("counterpart_type") == "antacid_drug":
        if cat not in DRUG_CATEGORIES:
            bad.append(f"{cid}: 약물 counterpart 인데 약물 category 아님({cat!r})")
        if cat == "al_mg_antacid":
            bad.append(f"{cid}: acid-reducer 를 al_mg_antacid 로 축소 금지")
        if "약물" not in rel.get("nutrient", ""):
            bad.append(f"{cid}: 약물 counterpart 표기에 '약물' 없음")
    # 영양소 counterpart 에 약물 category 금지
    if row.get("counterpart_type") in ("nutrient", "nutrient_group") and cat in DRUG_CATEGORIES:
        bad.append(f"{cid}: 영양소 counterpart 에 약물 category({cat})")
    if rel.get("product_link_allowed") is not False:
        bad.append(f"{cid}: product_link_allowed != false")
    if rel.get("potassium_safety_card") is not False:
        bad.append(f"{cid}: potassium_safety_card != false")
    if rel.get("requires_clinical_review") is not False:
        bad.append(f"{cid}: requires_clinical_review != false")
    if "reviewed_by" in rel:
        bad.append(f"{cid}: reviewed_by 누출(미기재 필수)")
    if not re.search(r"itemSeq=\d+", rel.get("source", {}).get("url", "")):
        bad.append(f"{cid}: source itemSeq 없음")
    leaked = DRAFT_ONLY & set(rel.keys())
    if leaked:
        bad.append(f"{cid}: draft-전용/금지 필드 누출 {sorted(leaked)}")
    if rel.get("recommended_action") == "avoid_concomitant" and cat != "acid_reducing_drug" and cat != "al_mg_antacid":
        bad.append(f"{cid}: avoid_concomitant 인데 약물 category 아님({cat!r})")
    return bad


def run_v0_2(sim):
    """임시 파일에 sim export 를 쓰고 v0.2 validator 실행 → (passed, tail)."""
    tmp = tempfile.mkdtemp(prefix="ms_tm_dry_")
    p = os.path.join(tmp, "sim_export.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sim, f, ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, V0_2_VALIDATOR, p], capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        tail = "\n".join(out[-6:])
        return r.returncode == 0, tail
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _sim_with(exp, rels):
    sim = json.loads(json.dumps(exp))
    sim["relations"] = sim["relations"] + rels
    sim["meta"]["relation_count"] = len(sim["relations"])
    return sim


def build_projected(exp):
    """provider 행 → (projected entries, holds, errs). live 무수정."""
    confirmed, holds, errs = tmprov.build()
    if errs:
        return None, holds, errs
    by_id = {r["candidate_id"]: r for r in confirmed}
    max_id = max(r["id"] for r in exp["relations"])
    existing = {(r.get("ingredient"), r.get("nutrient")) for r in exp["relations"]}
    entries, guard_viol = [], []
    nid = max_id
    for cid in CONFIRMED_IDS:
        row = by_id[cid]
        already = (row["drug_ingredient"], row["counterpart"]) in existing
        if already:
            guard_viol.append(f"{cid}: 이미 live 에 존재(드라이런 전제 위반)")
            continue
        nid += 1
        rel = draft_to_live(row, nid)
        guard_viol += guard_projected(cid, row, rel)
        entries.append({
            "candidate_id": cid,
            "projected_id": nid,
            "counterpart_category": rel.get("counterpart_category"),
            "recommended_action": rel["recommended_action"],
            "adversarial_verdict": row.get("adversarial_verdict", ""),
            "projected_live_relation": rel,
        })
    return entries, holds, guard_viol


def main():
    pm_approved = "--pm-approved" in sys.argv
    reviewer_note = None
    if "--reviewer-note" in sys.argv:
        i = sys.argv.index("--reviewer-note")
        if i + 1 < len(sys.argv):
            reviewer_note = sys.argv[i + 1]

    exp = json.load(open(EXPORT, encoding="utf-8"))
    before = len(exp["relations"])
    entries, holds, viol = build_projected(exp)
    if entries is None:
        for e in viol:
            print(f"[STOP] provider 안전 위반: {e}")
        return 1
    if viol:
        for b in viol:
            print(f"[STOP] {b}")
        return 1

    projected = [e["projected_live_relation"] for e in entries]
    after = before + len(projected)
    ids = [e["projected_id"] for e in entries]
    print(f"=== theme map 6건 통합 {'(LIVE)' if pm_approved else '(DRY-RUN)'} ===")
    print(f"baseline relations: {before} (기대 {BASELINE_RELATIONS}) · 예상: {before} → {after} · ids {ids}")
    for e in entries:
        r = e["projected_live_relation"]
        print(f"   id{r['id']} {r['ingredient']} × {r['nutrient']} "
              f"({r['mechanism']}/{r['recommended_action']}, evidence={r['evidence_level']}, "
              f"cat={r.get('counterpart_category')}, link={r['product_link_allowed']}, "
              f"kcard={r['potassium_safety_card']}, clinical={r['requires_clinical_review']})")

    if not pm_approved:
        # ── DRY-RUN: live 무수정. v0.2 validator 증거(5건 separation PASS / 6건 #15 차단) 수집 후 artifact 기록 ──
        import hashlib
        with open(EXPORT, "rb") as f:
            sha_before = hashlib.sha256(f.read()).hexdigest()

        sep5 = [e["projected_live_relation"] for e in entries
                if e["recommended_action"] == "separation"]
        ok5, tail5 = run_v0_2(_sim_with(exp, sep5))
        ok6, tail6 = run_v0_2(_sim_with(exp, projected))

        artifact = {
            "meta": {
                "name": "theme_map_live_dryrun_v1_3",
                "status": "DRY-RUN — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
                "purpose": "theme map 6건 live 통합 예상 산출물(드라이런). 실제 export/full index/aliases/src 무수정. "
                           "validate_theme_map_live_dryrun_v1_3.py 가 이 산출물로 안전·계약을 검증.",
                "baseline_relations": before,
                "baseline_max_id": max(r["id"] for r in exp["relations"]),
                "expected_relation_count_before": before,
                "expected_relation_count_after": after,
                "expected_ids": ids,
                "included_candidate_ids": CONFIRMED_IDS,
                "excluded_hold_ids": [h["candidate_id"] for h in holds],
                "live_write_performed": False,
                "live_promotion": 0,
                "published": False,
                "clinical_reviewed": False,
                "reviewed_by": "",
                "data_url": "v0.2 (불변)",
                "export_sha_before": sha_before,
                "export_sha_after_same": True,
                "guard_checks": {
                    "guard_projected_violations": viol,    # 빈 리스트 = 통합 자격
                    "all_product_link_false": all(r["product_link_allowed"] is False for r in projected),
                    "all_potassium_card_false": all(r["potassium_safety_card"] is False for r in projected),
                    "all_requires_clinical_review_false": all(r["requires_clinical_review"] is False for r in projected),
                    "no_reviewed_by": all("reviewed_by" not in r for r in projected),
                    "no_draft_only_leak": all(not (DRAFT_ONLY & set(r.keys())) for r in projected),
                    "all_source_itemseq": all(bool(re.search(r"itemSeq=\d+", r["source"]["url"])) for r in projected),
                    "ids_disjoint_from_live": not (set(ids) & {r["id"] for r in exp["relations"]}),
                },
                "category_decisions_required": {
                    "acid_reducing_drug": "세팔로 acid-reducer(TM-CEPH-AC-01/02). id61 al_mg_antacid(cation chelation)와 구분. "
                                          "reviewer 채택 확정 필요.",
                    "fat_soluble_vitamin": "지용성 비타민군(TM-LIP-01/02). 영양소군 — 약물 아님·비타민K 항응고 맥락 금지. "
                                           "reviewer 채택 확정 필요.",
                    "null_penicillamine": "페니실라민×철분/아연(TM-CHEL-01-FE/ZN)은 일반 영양소 relation(category 생략).",
                    "zinc_mechanism": "TM-CHEL-01-ZN: 라벨 '효과 감소'(흡수 미명시) → mechanism=absorption 은 추론. "
                                      "reviewer 가 absorption vs interaction 확정(user 카피 영향 없음).",
                    "grouping": "지용성 비타민 group 단일 vs 비타민별 분리 · 페니실라민 FE/ZN 묶음 vs 개별 — reviewer 결정.",
                },
                "reviewer_note_required": True,
                "reviewer_note_interlock": {
                    "required": True,
                    "approval_tokens": list(APPROVAL_TOKENS),
                    "candidate_ids_all_of": CONFIRMED_IDS,
                    "category_decisions": ["acid_reducing_drug", "fat_soluble_vitamin"],
                    "grouping_decision_required": True,
                    "zinc_mechanism_decision_required": True,
                    "verified_reference_consent_required": True,
                    "rejects": "SAMPLE/예시 토큰 · placeholder · 빈 노트 · 토큰/candidate_id/category/grouping/mechanism/"
                               "verified_reference 누락 · clinical_reviewed=true·제품추천 허용 문구",
                    "template": "docs/MediStack_reviewer_package_theme_map_v1_3.md §reviewer-note",
                },
                "v0_2_validator_evidence": {
                    "sim_separation_5_passed": ok5,
                    "sim_separation_5_tail": tail5,
                    "sim_all_6_passed": ok6,
                    "sim_all_6_tail": tail6,
                    "interpretation": "separation 5건은 현행 v0.2 validator PASS(파이프라인 준비됨). 6건 전체는 검사 #15"
                                      "(avoid_concomitant ⇒ al_mg_antacid 한정)에서 TM-CEPH-AC-02 만 차단 → 아래 선행조건 1 로 해소.",
                },
                "live_integration_prerequisites": [
                    "validator: validate_medistack_v0_2_export.py 검사 #15 의 avoid_concomitant 허용 category 에 "
                    "acid_reducing_drug 추가(또는 reviewer 가 TM-CEPH-AC-02 를 separation 으로 하향).",
                    "src: src/js/guards.js getFacets — fat_soluble_vitamin(영양소군) facet 포함, drug category만 제외.",
                    "src: src/js/render.js — acid_reducing_drug 전용 chip/kicker(제산제·H2/PPI 약물 표기) 추가.",
                    "reviewer note(위 인터록 충족) + 별도 PM 승인 + 별도 PR(이번 작업 범위 밖).",
                ],
                "note": "본 산출물은 드라이런 예상치일 뿐 source_confirmed 최종확정·식약처 승인·약사 검수 완료·"
                        "법적 문제 없음 을 의미하지 않는다. live 승격은 --pm-approved + --reviewer-note + 별도 PM "
                        "+ clinical reviewer + 위 선행조건(validator/src) 충족.",
            },
            "projected_entries": entries,
            "hold_excluded": [{"candidate_id": h["candidate_id"], "drug_ingredient": h["drug_ingredient"],
                               "counterpart": h["counterpart"], "hold_reason": h["hold_reason"]} for h in holds],
        }
        os.makedirs(os.path.dirname(DRYRUN_ARTIFACT), exist_ok=True)
        with open(DRYRUN_ARTIFACT, "w", encoding="utf-8") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=1)
            f.write("\n")

        with open(EXPORT, "rb") as f:
            sha_after = hashlib.sha256(f.read()).hexdigest()
        if sha_after != sha_before:
            print("[FATAL] 드라이런인데 live export sha 변경됨 — 중단")
            return 1
        print(f"\n[dry-run] live export sha 불변({sha_before[:8]}). 예상 산출물 기록: "
              f"{os.path.relpath(DRYRUN_ARTIFACT, REPO)}")
        print(f"[dry-run] v0.2 validator: separation 5건 PASS={ok5} · 6건 전체 PASS={ok6}"
              f"(6건 차단=TM-CEPH-AC-02 acid_reducing_drug+avoid_concomitant 검사#15 선행조건).")
        print("[dry-run] live 기록은 --pm-approved + --reviewer-note + 별도 PM/reviewer + validator/src 선행조건 필요.")
        return 0

    # ── LIVE 기록(--pm-approved + --reviewer-note): 본 세션 호출 금지. 테스트는 temp 복사본에서만 호출 ──
    _note, note_bad = check_reviewer_note(reviewer_note)
    if note_bad:
        for b in note_bad:
            print(f"[STOP] reviewer 노트: {b}")
        return 1
    exp["relations"] = exp["relations"] + projected
    exp["meta"]["relation_count"] = len(exp["relations"])
    exp["meta"]["note"] = exp["meta"].get("note", "") + \
        (" | theme map expansion 6건 live 통합: 지용성비타민(오르리스타트·콜레스티라민)·acid_reducing_drug "
         "세팔로(세프포독심·세프디토렌)·페니실라민(철분·아연). relation %d→%d. "
         "published/clinical_reviewed=false·reviewed_by 미기재 유지." % (before, after))
    with open(EXPORT, "w", encoding="utf-8") as f:
        json.dump(exp, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\n[write] export 기록 완료(relations {before}→{after}). INTEGRATE THEME MAP: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
