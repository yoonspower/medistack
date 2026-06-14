#!/usr/bin/env python3
"""
analyze_coverage_kpi_v1_2.py
MediStack — relation **숫자 목표(1,000)가 아니라 복용빈도 기반 coverage KPI** 분석(읽기전용).

핵심 아이디어: 실측 검색량/판매량 데이터가 없으므로, **full index(MFDS 실품목 17,580)의 성분별 품목수**
를 "시장 존재감 = 복용빈도 proxy"로 사용한다(많이 유통되는 성분 = 많이 처방/복용될 개연). 이 proxy 로
Top 200~300 후보를 랭킹하고, 현재 relation_card 가 그 Top 후보를 **얼마나 덮는지** KPI 로 측정한다.

⚠️ 한계(문서에 명시): 품목수는 검색량/복용량의 **간접 proxy** 이며 정확 빈도가 아니다(인지도·약가·만성/급성
   사용기간 차이 미반영). 외부 실데이터(처방통계·검색량) 확보 전까지 **내부 index proxy ranking** 만 생성한다.
   coverage 공백 ≠ 전부 relation 대상(상호작용 근거 없는 성분 다수) — 이 분석은 **source-check 우선순위 큐**
   작성 목적이지 relation 자동 생성이 아니다.

⚠️ 보호 데이터(relation/full index/alias/export/src) 한 줄도 수정하지 않는다.
읽기: full index · export(relations) · aliases · popular_drug_seed(인지도 보조).
쓰기(분석 산출물만):
  data/coverage_kpi_top_candidates_v1_2.csv
  docs/MediStack_coverage_kpi_analysis_v1_2.md
사용: python3 scripts/analyze_coverage_kpi_v1_2.py [--top N] [--no-write]
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
DOCS = os.path.join(REPO, "docs")
FULL = os.path.join(DATA, "full_drug_name_index_sample_v1_0.json")
EXPORT = os.path.join(DATA, "medistack_v0.2_beta_export.json")
ALIASES = os.path.join(DATA, "medistack_v0.3_aliases.json")
SEED = os.path.join(DATA, "popular_drug_seed_candidates_v1_1.csv")
OUT_CSV = os.path.join(DATA, "coverage_kpi_top_candidates_v1_2.csv")
OUT_MD = os.path.join(DOCS, "MediStack_coverage_kpi_analysis_v1_2.md")

# 치료군 분류 키워드 맵(성분명 부분일치). 사용자 지정 카테고리 중심 — 미매칭은 '기타'.
# 민감/고위험군(정신건강·항혈전·항암)은 source-check 우선순위 큐에서 hold 로 분리.
CLASS_RULES = [
    ("고혈압/심혈관", ["암로디핀", "로사르탄", "발사르탄", "텔미사르탄", "칸데사르탄", "올메사르탄", "이르베사르탄",
                  "피마사르탄", "카르베딜롤", "비소프롤롤", "네비보롤", "아테놀롤", "딜티아젬", "니페디핀", "라미프릴",
                  "페린도프릴", "에날라프릴", "히드로클로로티아지드", "클로르탈리돈", "인다파미드", "푸로세미드",
                  "토라세미드", "스피로노락톤", "실로스타졸", "사르포그렐레이트", "트리메타지딘", "니세르골린"]),
    ("당뇨", ["메트포르민", "글리메피리드", "글리클라지드", "시타글립틴", "빌다글립틴", "리나글립틴", "삭사글립틴",
            "엠파글리플로진", "다파글리플로진", "글리벤클라미드", "피오글리타존", "글리퀴돈", "보글리보스", "아카르보스",
            "제미글립틴", "테네리글립틴"]),
    ("고지혈증", ["로수바스타틴", "아토르바스타틴", "심바스타틴", "피타바스타틴", "프라바스타틴", "플루바스타틴",
              "에제티미브", "페노피브레이트", "오메가-3", "콜레스티라민"]),
    ("해열진통/소염", ["아세트아미노펜", "이부프로펜", "아세클로페낙", "록소프로펜", "나프록센", "셀레콕시브", "멜록시캄",
                  "디클로페낙", "에토돌락", "트라마돌", "에페리손", "잘토프로펜", "탈니플루메이트", "폴마콕시브"]),
    ("소화/위장", ["오메프라졸", "에스오메프라졸", "라베프라졸", "란소프라졸", "판토프라졸", "덱스란소프라졸", "일라프라졸",
                "모사프리드", "레바미피드", "이토프리드", "라푸티딘", "파모티딘", "니자티딘", "라니티딘", "돔페리돈",
                "메토클로프라미드", "알마게이트", "수크랄페이트", "포스포미돈", "트리메부틴"]),
    ("항생/항균", ["아목시실린", "클라불란산", "세파클러", "세프디니르", "세프포독심", "세프프로질", "세픽심", "세프라딘",
                "세팔렉신", "클래리트로마이신", "아지트로마이신", "레보플록사신", "시프로플록사신", "목시플록사신",
                "독시사이클린", "미노사이클린", "메트로니다졸", "세프카펜", "세프디토렌", "로라카르베프"]),
    ("항진균", ["플루코나졸", "이트라코나졸", "테르비나핀", "케토코나졸"]),
    ("호흡기/알레르기", ["몬테루카스트", "세티리진", "로라타딘", "펙소페나딘", "레보세티리진", "슈도에페드린", "암브록솔",
                   "아세틸시스테인", "레보드로프로피진", "프란루카스트", "바일라스틴", "데스로라타딘"]),
    ("비뇨/전립선", ["탐스로신", "솔리페나신", "두타스테리드", "피나스테리드", "타다라필", "실로도신", "톨테로딘",
                 "미라베그론", "알푸조신"]),
    ("신경/뇌", ["프레가발린", "가바펜틴", "도네페질", "토피라메이트", "레비티라세탐", "발프로산", "라모트리진",
              "메만틴", "콜린알포세레이트", "옥스카르바제핀"]),
    ("갑상선/내분비", ["레보티록신", "리오티로닌", "메티마졸", "프로필티오우라실"]),
    ("골다공증", ["알렌드론산", "리세드론산", "이반드론산", "라록시펜", "바제독시펜"]),
    # --- 민감/고위험군(source-check 큐에서 hold 분리) ---
    ("정신건강(민감)", ["에스시탈로프람", "설트랄린", "쿠에티아핀", "알프라졸람", "졸피뎀", "파록세틴", "둘록세틴",
                   "미르타자핀", "아리피프라졸", "올란자핀", "벤라팍신", "트라조돈", "로라제팜", "클로나제팜"]),
    ("항혈전(민감)", ["클로피도그렐", "와파린", "리바록사반", "아픽사반", "다비가트란", "에독사반"]),
    ("항암/면역(민감)", ["메토트렉세이트", "타목시펜", "이마티닙", "카페시타빈", "타크로무스"]),
]
SENSITIVE_CLASSES = {"정신건강(민감)", "항혈전(민감)", "항암/면역(민감)"}


def classify(ing):
    for cls, kws in CLASS_RULES:
        if any(k in ing for k in kws):
            return cls
    return "기타"


def covered_match(ing, covered_bases):
    """index 성분명(salt/복합 포함)이 relation 보유 성분(base)에 해당하면 covered."""
    for c in covered_bases:
        if c and (c in ing or ing in c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=300)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    full = json.load(open(FULL, encoding="utf-8"))
    exp = json.load(open(EXPORT, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    seeds = list(csv.DictReader(open(SEED, encoding="utf-8")))
    ents = full["entries"]
    counts = full["meta"]["counts"]

    # 성분별 품목수(복용빈도 proxy) + relation_card 품목수
    prod_count = Counter()
    rc_count = Counter()
    for e in ents:
        ing = e.get("ingredient_name")
        if not ing:
            continue
        prod_count[ing] += 1
        if e.get("display_mode") == "relation_card":
            rc_count[ing] += 1

    covered_bases = sorted({r["ingredient"] for r in exp["relations"]})
    seed_names = {s["query_name"].strip() for s in seeds}

    # Top N 성분(품목수 desc)
    ranked = prod_count.most_common()
    topN = ranked[:args.top]

    rows = []
    for rank, (ing, cnt) in enumerate(topN, start=1):
        cls = classify(ing)
        cov_base = covered_match(ing, covered_bases)
        rc = rc_count[ing]
        # covered = relation 보유 성분 매칭 OR 품목 중 relation_card 존재
        covered = bool(cov_base) or rc > 0
        in_seed = any(sn in ing or ing in sn for sn in seed_names)
        rows.append({
            "rank": rank, "ingredient_name": ing, "product_count": cnt,
            "therapeutic_class": cls, "relation_covered": "yes" if covered else "no",
            "relation_card_products": rc, "covered_base_ingredient": cov_base or "",
            "in_popular_seed": "yes" if in_seed else "no",
            "sensitive_hold": "yes" if cls in SENSITIVE_CLASSES else "no",
            "queue_action": ("covered" if covered else
                             ("source_check_hold(sensitive)" if cls in SENSITIVE_CLASSES else
                              "source_check_candidate")),
        })

    # ----- KPI -----
    n = len(rows)
    cov_rows = [r for r in rows if r["relation_covered"] == "yes"]
    top_total_products = sum(r["product_count"] for r in rows)
    cov_products = sum(r["product_count"] for r in cov_rows)
    kpi_ing = len(cov_rows) / n if n else 0
    kpi_weighted = cov_products / top_total_products if top_total_products else 0

    # class coverage
    by_cls = defaultdict(lambda: [0, 0, 0])  # [ing_total, ing_covered, products]
    for r in rows:
        c = by_cls[r["therapeutic_class"]]
        c[0] += 1
        c[1] += 1 if r["relation_covered"] == "yes" else 0
        c[2] += r["product_count"]
    # priority queue: 미커버 · 비민감 · 품목수 desc
    queue = [r for r in rows if r["queue_action"] == "source_check_candidate"]
    queue.sort(key=lambda r: -r["product_count"])

    print(f"=== coverage KPI (Top {n} 성분 by 품목수 proxy) ===")
    print(f"고유 성분 총: {len(prod_count)} | relation 보유 성분(base): {len(covered_bases)}")
    print(f"KPI① Top{n} 성분 coverage: {len(cov_rows)}/{n} = {kpi_ing*100:.1f}%")
    print(f"KPI② Top{n} 품목수가중 coverage: {cov_products}/{top_total_products} = {kpi_weighted*100:.1f}%")
    print(f"source-check 우선순위 큐(미커버·비민감): {len(queue)}")
    print("\nTop 15 우선순위 큐(품목수 proxy desc):")
    for r in queue[:15]:
        print(f"  {r['product_count']:4d}  {r['ingredient_name'][:30]:30s} [{r['therapeutic_class']}]")

    if not args.no_write:
        cols = ["rank", "ingredient_name", "product_count", "therapeutic_class", "relation_covered",
                "relation_card_products", "covered_base_ingredient", "in_popular_seed",
                "sensitive_hold", "queue_action"]
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        write_md(rows, queue, by_cls, n, len(cov_rows), kpi_ing, kpi_weighted,
                 cov_products, top_total_products, len(prod_count), covered_bases, counts, args.top)
        print(f"\n[write] {os.path.relpath(OUT_CSV, REPO)} · {os.path.relpath(OUT_MD, REPO)}")
    else:
        print("\n(--no-write)")
    return 0


def write_md(rows, queue, by_cls, n, ncov, kpi_ing, kpi_w, covp, totp, total_ings, covered_bases, counts, topN):
    def pct(x):
        return f"{x*100:.1f}%"
    L = []
    L.append("# MediStack — 복용빈도(proxy) 기반 coverage KPI 분석 (v1.2)\n")
    L.append("> 작성일: 2026-06-14. **분석 전용 — 데이터/렌더/relation 한 줄도 변경하지 않는다.** "
             "재현: `python3 scripts/analyze_coverage_kpi_v1_2.py`. 산출 CSV: `data/coverage_kpi_top_candidates_v1_2.csv`.")
    L.append("> 목적: relation **개수 목표(1,000)** 가 아니라 **사용자가 실제로 많이 찾는 약을 얼마나 덮는지**를 "
             "KPI 로 보고, source-check **우선순위 큐**를 만든다. 이 분석은 relation 을 생성하지 않는다.\n")
    L.append("---\n")
    L.append("## 0. 방법과 한계 (반드시 같이 읽기)\n")
    L.append("- **복용빈도 proxy = full index(MFDS 실품목 17,580)의 성분별 품목수.** 많이 유통되는 성분일수록 "
             "많이 처방·복용될 개연이 크다는 가정. 실측 검색량/처방통계가 아니다.")
    L.append("- **한계(명시):** ①품목수 ≠ 실제 검색량/복용량(인지도·약가·만성 vs 급성 사용기간·OTC 비중 미반영). "
             "②coverage 공백이 곧 'relation 대상'은 아니다 — **상호작용 근거(허가사항 동거어)가 없는 성분이 다수**다. "
             "③이 인덱스는 확장 중 샘플이라 일부 성분 누락 가능. → 그래서 결과는 **확정 랭킹이 아니라 우선순위 후보 큐**다.")
    L.append("- **외부 실데이터 미확보.** 처방통계(건보공단/심평원)·검색량 확보 시 `data/external_rx_volume_*.csv` 로 "
             "proxy 를 보정하는 것이 다음 단계. 현재는 **내부 index proxy ranking** 만 생성한다(이 한계를 문서에 박제).")
    L.append('- "식약처 승인 / 법적 문제없음 / 약사 검수 완료 / 추천 영양제" 표현 미사용. 참고정보 정체성 유지.\n')
    L.append("---\n")
    L.append("## 1. 기준 수치 (현재 라이브)\n")
    L.append(f"- full index total **{counts.get('total')}** = relation_card **{counts.get('relation_card')}** + "
             f"name_only **{counts.get('name_only')}**. 고유 성분(ingredient_name) **{total_ings}**.")
    L.append(f"- relation 보유 성분(base) **{len(covered_bases)}**: {', '.join(covered_bases)}.\n")
    L.append("---\n")
    L.append(f"## 2. 핵심 KPI (Top {topN} 성분 by 품목수 proxy)\n")
    L.append("| KPI | 값 | 의미 |")
    L.append("|---|---|---|")
    L.append(f"| **KPI① 성분 coverage** | **{ncov}/{n} = {pct(kpi_ing)}** | Top {n} 빈출 성분 중 relation 보유 비율 |")
    L.append(f"| **KPI② 품목수가중 coverage** | **{covp:,}/{totp:,} = {pct(kpi_w)}** | 복용빈도 proxy(품목수)로 가중한 실질 커버리지 |")
    L.append("")
    L.append("> 해석: relation 개수(57)는 작지만, 그 57개가 **고빈도 성분(메트포르민·HCTZ·PPI·갑상선·항생제 등)에 "
             "집중**돼 있어 품목수가중 coverage 가 성분수 coverage 보다 의미 있다. 단, Top 빈출 성분의 큰 부분이 "
             "아직 미커버 — §4 큐가 그 공백을 빈도순으로 정렬한다.\n")
    L.append("---\n")
    L.append("## 3. 치료군별 coverage (사용자 지정 카테고리 중심)\n")
    L.append("| 치료군 | Top내 성분 | 커버 | 미커버 | 품목수합 | 비고 |")
    L.append("|---|---|---|---|---|---|")
    order = sorted(by_cls.items(), key=lambda kv: -kv[1][2])
    for cls, (tot, cov, prod) in order:
        note = "민감군=source-check hold" if cls in SENSITIVE_CLASSES else ""
        L.append(f"| {cls} | {tot} | {cov} | {tot-cov} | {prod:,} | {note} |")
    L.append("")
    L.append("---\n")
    L.append("## 4. source-check 우선순위 큐 (미커버 · 비민감 · 품목수 proxy desc)\n")
    L.append("> **이 표가 본 분석의 핵심 산출물**이다. 빈출(품목수 큰)인데 아직 relation 이 없는 성분 = factory "
             "source-check 다음 타깃 후보. **단, 여기 오른다고 relation 확정이 아니다** — 각 성분은 "
             "`verify_factory_sources_v1_2.py` 로 허가사항 동거어를 확인해 근거 있는 것만 draft 로 승격한다. "
             "민감군(정신건강·항혈전·항암)은 §5 로 분리(hold).\n")
    L.append("| 순위 | 성분 | 품목수(proxy) | 치료군 | seed인지도 |")
    L.append("|---|---|---|---|---|")
    for i, r in enumerate(queue[:50], start=1):
        L.append(f"| {i} | {r['ingredient_name']} | {r['product_count']} | {r['therapeutic_class']} | "
                 f"{'O' if r['in_popular_seed']=='yes' else '-'} |")
    L.append(f"\n→ 우선순위 큐(미커버·비민감) 총 **{len(queue)}건** 중 Top 50 표시. 전체는 CSV.")
    L.append("> 후보군 예: 위장관운동(모사프리드·이토프리드)·점막보호(레바미피드)·비뇨(탐스로신)·항생제 잔여(아목시실린/"
             "클라불란산·클래리트로마이신)·항진균(플루코나졸·테르비나핀)·호흡기(몬테루카스트) 등 — 허가사항에 다가양이온/"
             "흡수/전해질 동거어가 있는지 source-check 로 선별.\n")
    L.append("---\n")
    L.append("## 5. 민감/고위험군 (source-check 큐에서 hold 분리)\n")
    sens = [r for r in rows if r["sensitive_hold"] == "yes"]
    sens.sort(key=lambda r: -r["product_count"])
    L.append("> 정신건강·항혈전·항암군은 빈출이라도 **임상판단·출혈/상호작용 위험**으로 참고정보 베타 범위 밖 → "
             "clinical reviewer 트랙 전까지 hold(factory hold 정책 승계).\n")
    L.append("| 성분 | 품목수 | 치료군 |")
    L.append("|---|---|---|")
    for r in sens[:15]:
        L.append(f"| {r['ingredient_name']} | {r['product_count']} | {r['therapeutic_class']} |")
    L.append(f"\n→ 민감군 hold 총 **{len(sens)}건**(Top 15 표시).\n")
    L.append("---\n")
    L.append("## 6. 다음 단계\n")
    L.append("1. §4 우선순위 큐 Top N 을 `harvest_relation_candidates.py` 입력으로 → `verify_factory_sources_v1_2.py` "
             "source-check → 적대적 검증 → confirmed 만 draft. (relation 개수가 아니라 **빈도 가중 coverage KPI** 를 추적 지표로.)")
    L.append("2. 외부 처방/검색 실데이터 확보 시 proxy 보정(`external_rx_volume_*`) — 품목수 proxy 의 한계(§0) 해소.")
    L.append("3. KPI② 품목수가중 coverage 를 라운드마다 재측정해 **체감 가치 향상**을 정량 추적(개수 목표 대신).\n")
    L.append("---\n")
    L.append("> **안전 원칙(불변):** 품목수는 복용빈도의 proxy일 뿐 실측 아님(한계 명시) / coverage 공백 ≠ relation 대상 "
             "(source-check 로 근거 확인) / 민감·고위험군 hold / 이 분석은 우선순위 큐 작성이지 relation 생성 아님 / "
             "데이터·렌더·relation 무변경 / published·clinical false 유지 / '식약처 승인·추천 영양제' 표현 0.\n")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    import sys
    sys.exit(main())
