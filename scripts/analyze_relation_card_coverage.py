#!/usr/bin/env python3
"""
analyze_relation_card_coverage.py
MediStack relation_card 커버리지 분석 + relation 확장 후보 초안 생성 (읽기 전용 분석 스크립트).

목적:
  full index 17,580 중 실제 참고정보가 붙는 relation_card 558 이 어떤 성분/약품군/관계에
  몰려 있는지 정량 분석하고, **데이터를 한 줄도 바꾸지 않고** 다음 단계 relation 확장의
  "검토 후보(candidate only)" 를 내부 데이터 기준으로 설계한다.

읽기:
  data/medistack_v0.2_beta_export.json   (relation 30)
  data/full_drug_name_index_sample_v1_0.json (17,580 = relation_card 558 + name_only 17,022)

쓰기(분석 산출물만 — 보호 데이터 미변경):
  data/relation_card_coverage_snapshot_v1_1.csv       (relation_card 558 스냅샷)
  data/relation_expansion_candidates_v1_1_draft.csv   (확장 후보 초안 — candidate only)

설계 불변(이 스크립트가 보장):
  - 보호 파일(export / full index / aliases / src) 을 절대 열어서 쓰지 않는다(읽기 전용).
  - 후보는 status=candidate_for_review, confirmed=false, source_required=true,
    review_required=true, clinical_reviewed=false 로만 기록한다(실제 relation 아님).
  - 후보 CSV 의 nutrient 테마는 "가설(미확정)" 로 표기 — 복용지시/의학적 단정 아님.

사용:
  python3 scripts/analyze_relation_card_coverage.py            # 분석 + CSV 2종 생성
  python3 scripts/analyze_relation_card_coverage.py --no-write # 콘솔 리포트만
종료 코드: 0 정상, 1 기준 수치 불일치(STOP 신호)
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
FULL_INDEX = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
SNAPSHOT_CSV = os.path.join(DATA, "relation_card_coverage_snapshot_v1_1.csv")
CANDIDATE_CSV = os.path.join(DATA, "relation_expansion_candidates_v1_1_draft.csv")

# 기준 수치(불변) — 어긋나면 STOP
EXPECT = {"total": 17580, "relation_card": 558, "name_only": 17022, "relations": 30}

# relation_card 성분 → 약품군(보고용 그룹화)
DRUG_CLASS = {
    "레보플록사신": "플루오로퀴놀론계 항생제", "시프로플록사신": "플루오로퀴놀론계 항생제",
    "오플록사신": "플루오로퀴놀론계 항생제", "목시플록사신": "플루오로퀴놀론계 항생제",
    "독시사이클린": "테트라사이클린계 항생제", "미노사이클린": "테트라사이클린계 항생제",
    "알렌드론산": "비스포스포네이트(골다공증)",
    "푸로세미드": "루프이뇨제", "토라세미드": "루프이뇨제",
    "히드로클로로티아지드": "치아지드계 이뇨제",
    "메트포르민": "비구아나이드(당뇨)", "레보티록신": "갑상선호르몬",
    "오메프라졸": "PPI(위산분비억제)", "에스오메프라졸": "PPI(위산분비억제)",
}

# 확장 후보 초안 — 내부 데이터 기준 + 기존 relation 과의 계열 인접성으로 큐레이션.
# 모두 candidate only. nutrient 테마는 "가설(미확정)" 이며 의학적 단정/복용지시 아님.
# name_only_product_count 는 스크립트가 현재 인덱스에서 substring 으로 채운다.
CANDIDATE_FAMILIES = [
    # ingredient(대표),  class,                  related_relation_ingredient, proposed_nutrient_theme(가설·미확정),                rationale
    ("판토프라졸",   "PPI(위산분비억제)",     "오메프라졸",
     "마그네슘·비타민B12 (오메프라졸 관계와 동일 계열 가설·미확정)",
     "기존 오메프라졸 PPI relation 과 동일 약효군, 허가사항 출처 확인 가능성 높음, 만성 복용 흔함"),
    ("란소프라졸",   "PPI(위산분비억제)",     "오메프라졸",
     "마그네슘·비타민B12 (오메프라졸 관계와 동일 계열 가설·미확정)",
     "PPI 동일 계열, name_only 다수 존재, 출처 확인 가능성 높음"),
    ("라베프라졸",   "PPI(위산분비억제)",     "오메프라졸",
     "마그네슘·비타민B12 (오메프라졸 관계와 동일 계열 가설·미확정)",
     "PPI 동일 계열, name_only 최다 PPI, 검색 빈도 높을 것으로 추정"),
    ("클로르탈리돈", "치아지드계 이뇨제",     "히드로클로로티아지드",
     "전해질(칼륨 등) 참고 (HCTZ 관계와 동일 계열 가설·미확정)",
     "HCTZ 와 동일 치아지드 계열, 단 칼륨 안전 정책(product_link 금지·potassium_safety) 승계 필요"),
    ("인다파미드",   "치아지드계(유사) 이뇨제", "히드로클로로티아지드",
     "전해질(칼륨 등) 참고 (HCTZ 관계와 동일 계열 가설·미확정)",
     "치아지드 유사 이뇨제, 칼륨 안전 정책 승계 검토 필요"),
    ("로수바스타틴", "스타틴(고지혈증)",       "(신규 계열)",
     "코엔자임Q10 (문헌 보고 가설·미확정)",
     "name_only 최대 단일군, 대중 인지도 높음. 단 신규 계열→출처/문구 신중 검토 필요"),
    ("아토르바스타틴", "스타틴(고지혈증)",     "(신규 계열)",
     "코엔자임Q10 (문헌 보고 가설·미확정)",
     "name_only 다수, 대중 인지도 높음. 신규 계열→출처/문구 신중 검토 필요"),
]


def load():
    exp = json.load(open(EXPORT, encoding="utf-8"))
    full = json.load(open(FULL_INDEX, encoding="utf-8"))
    return exp, full


def build(exp, full):
    rels = exp["relations"]
    ents = full["entries"]
    rc = [e for e in ents if e.get("display_mode") == "relation_card"]
    no = [e for e in ents if e.get("display_mode") == "name_only"]
    # ingredient → list of relations(id, nutrient, mechanism, source)
    ing2rel = defaultdict(list)
    for r in rels:
        ing2rel[r["ingredient"]].append(r)
    return rels, ents, rc, no, ing2rel


def check_baseline(ents, rc, no, rels):
    actual = {"total": len(ents), "relation_card": len(rc), "name_only": len(no), "relations": len(rels)}
    ok = actual == EXPECT
    print("=== 기준 수치 검증 ===")
    for k in EXPECT:
        flag = "OK" if actual[k] == EXPECT[k] else "MISMATCH"
        print(f"  {k}: {actual[k]} (기대 {EXPECT[k]}) [{flag}]")
    return ok


def report(rels, rc, no, ing2rel):
    n_rc, n_no, n_all = len(rc), len(no), len(rc) + len(no)
    print("\n=== A. relation_card 558 — 성분 분포 ===")
    rc_ing = Counter(e["ingredient_name"] for e in rc)
    for ing, c in rc_ing.most_common():
        print(f"  {c:4d} ({c/n_rc*100:5.1f}%)  {ing}  [{DRUG_CLASS.get(ing,'기타')}]")
    print(f"  distinct 성분: {len(rc_ing)}")

    print("\n=== B. relation_card 558 — 약품군 분포 ===")
    rc_cls = Counter(DRUG_CLASS.get(e["ingredient_name"], "기타") for e in rc)
    for cls, c in rc_cls.most_common():
        print(f"  {c:4d} ({c/n_rc*100:5.1f}%)  {cls}")

    print("\n=== C. relation 30 — 관계별 매핑 품목 수 ===")
    # 카드는 성분 단위 매핑 → 같은 성분의 관계들은 동일 item_seq 집합 공유
    seqs_by_ing = defaultdict(set)
    for e in rc:
        seqs_by_ing[e["ingredient_name"]].add(e["item_seq"])
    rel_rows = []
    for r in rels:
        ing = r["ingredient"]
        cnt = len(seqs_by_ing.get(ing, set()))
        sample = [e["item_name"] for e in rc if e["ingredient_name"] == ing][:6]
        rel_rows.append((r["id"], ing, r["nutrient"], r.get("mechanism", ""), cnt, sample))
    for rid, ing, nut, mech, cnt, sample in sorted(rel_rows, key=lambda x: x[0]):
        print(f"  id{rid:2d}  {ing}×{nut} ({mech})  매핑 {cnt}  예: {', '.join(sample[:3])}")

    print("\n  -- 상위 10 (매핑 품목 수) --")
    for rid, ing, nut, mech, cnt, _ in sorted(rel_rows, key=lambda x: -x[4])[:10]:
        print(f"     {cnt:4d}  id{rid} {ing}×{nut}")
    print("  -- 하위 10 (매핑 품목 수) --")
    for rid, ing, nut, mech, cnt, _ in sorted(rel_rows, key=lambda x: x[4])[:10]:
        print(f"     {cnt:4d}  id{rid} {ing}×{nut}")

    print("\n=== D. 제조사 / 출처 분포 ===")
    comp_null = sum(1 for e in rc if not e.get("company_name"))
    print(f"  company_name null: {comp_null}/{n_rc} (relation_card 는 alias 경로 유래 → 제조사 메타 부재)")
    src = Counter(e.get("source", "") for e in rc)
    print(f"  source: {dict(src)}")
    smethod = Counter(e.get("source_method", "") for e in rc)
    print(f"  source_method: {dict(smethod)}")
    # relation source type (상속 원천)
    rsrc = Counter(r["source"]["type"] for r in rels)
    print(f"  (상속 원천) relation 30 source.type: {dict(rsrc)}")

    print("\n=== E. 사용자 체감 가치 비율 ===")
    print(f"  full index total: {n_all}")
    print(f"  relation_card: {n_rc}  ({n_rc/n_all*100:.2f}%)  ← 검색 시 참고정보 표시")
    print(f"  name_only:     {n_no}  ({n_no/n_all*100:.2f}%)  ← 품목명 확인만")
    print(f"  '정보 표시 확률'(균등가정 상한): {n_rc/n_all*100:.2f}%")
    print("  주: 실제 체감은 인기약 검색분포에 좌우 → 외부 인기약 매칭 필요(다음 단계)")

    print("\n=== F. name_only 상위 성분(확장 후보 맥락) ===")
    no_ing = Counter((e.get("ingredient_name") or "(none)") for e in no)
    for ing, c in no_ing.most_common(15):
        print(f"  {c:4d}  {ing}")
    return no_ing


def write_snapshot(rc, ing2rel):
    rows = []
    for e in sorted(rc, key=lambda x: (x["ingredient_name"], x["item_name"])):
        ing = e["ingredient_name"]
        matched = ing2rel.get(ing, [])
        rel_ids = ";".join(str(r["id"]) for r in matched)
        nutrients = ";".join(r["nutrient"] for r in matched)
        # source 는 relation 30 에서 상속(relation_card 558 → relation 30)
        src_type = matched[0]["source"]["type"] if matched else ""
        src_url = matched[0]["source"]["url"] if matched else ""
        rows.append({
            "item_seq": e["item_seq"],
            "item_name": e["item_name"],
            "normalized_item_name": e["normalized_item_name"],
            "ingredient_name": ing,
            "company_name": e.get("company_name") or "",
            "drug_class": DRUG_CLASS.get(ing, "기타"),
            "relation_ids": rel_ids,
            "relation_count": len(matched),
            "nutrients": nutrients,
            "source_type_inherited": src_type,
            "source_url_inherited": src_url,
            "source_checked_at": e.get("source_checked_at", ""),
            "covered_by_relation": e.get("covered_by_relation", ""),
        })
    cols = ["item_seq", "item_name", "normalized_item_name", "ingredient_name", "company_name",
            "drug_class", "relation_ids", "relation_count", "nutrients",
            "source_type_inherited", "source_url_inherited", "source_checked_at", "covered_by_relation"]
    with open(SNAPSHOT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\n[write] {os.path.relpath(SNAPSHOT_CSV, REPO)}  ({len(rows)} rows)")


def write_candidates(no_ing):
    def name_only_count(sub):
        return sum(c for ing, c in no_ing.items() if sub in ing)
    cols = ["candidate_id", "candidate_ingredient", "drug_class", "related_existing_relation",
            "name_only_product_count", "proposed_nutrient_theme_hypothesis", "rationale",
            "status", "confirmed", "source_required", "review_required", "clinical_reviewed"]
    rows = []
    for i, (ing, cls, rel, theme, rationale) in enumerate(CANDIDATE_FAMILIES, 1):
        rows.append({
            "candidate_id": f"C{i:02d}",
            "candidate_ingredient": ing,
            "drug_class": cls,
            "related_existing_relation": rel,
            "name_only_product_count": name_only_count(ing),
            "proposed_nutrient_theme_hypothesis": theme,
            "rationale": rationale,
            "status": "candidate_for_review",
            "confirmed": "false",
            "source_required": "true",
            "review_required": "true",
            "clinical_reviewed": "false",
        })
    with open(CANDIDATE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"[write] {os.path.relpath(CANDIDATE_CSV, REPO)}  ({len(rows)} rows, candidate only)")
    print("\n=== 확장 후보 초안(candidate only) ===")
    for r in rows:
        print(f"  {r['candidate_id']} {r['candidate_ingredient']:8s} [{r['drug_class']}] "
              f"name_only≈{r['name_only_product_count']:4d}  ←{r['related_existing_relation']}")


def main():
    write = "--no-write" not in sys.argv
    exp, full = load()
    rels, ents, rc, no, ing2rel = build(exp, full)
    ok = check_baseline(ents, rc, no, rels)
    if not ok:
        print("\n[STOP] 기준 수치 불일치 — 데이터가 예상과 다름. 분석 중단.")
        return 1
    no_ing = report(rels, rc, no, ing2rel)
    if write:
        write_snapshot(rc, ing2rel)
        write_candidates(no_ing)
    else:
        print("\n(--no-write: CSV 미생성)")
    print("\nANALYZE RELATION CARD COVERAGE: DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
