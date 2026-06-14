#!/usr/bin/env python3
"""
verify_coverage_queue_sources_v1_2.py
MediStack relation factory (batch2, coverage-queue driven) — Top100 priority-queue precheck 통과
**source_check_candidate** 후보의 제안 nutrient 테마가 MFDS nedrug 허가사항(getItemDetail) 원문에
실재하는지 **출처 존재 여부만** 확인한다.

설계: verify_factory_sources_v1_2.py 의 검증된 네트워크 + detector 파이프라인을 그대로 import 해서
재사용한다(중복 0). 후보 입력만 손큐레이션 dict 대신 **precheck CSV(데이터 driven)** 로 바꾼다.

입력(읽기):
  data/coverage_queue_precheck_v1_2.csv   (precheck workflow 산출 — precheck_class=source_check_candidate 만 처리)
출력(분석 산출물만):
  data/coverage_queue_source_check_v1_2.csv  (factory source-check 와 동일 20컬럼 스키마)

⚠️ 절대 규칙 (verify_factory_sources_v1_2 와 동일):
  - relation / full index / alias / export / src / .github / validator 를 한 줄도 수정하지 않는다(읽기전용 + 네트워크 fetch).
  - 어떤 후보도 source_confirmed 라도 "다음 단계 검토 대상"일 뿐 구현 지시가 아니다.
  - 계열 일반화 금지: 해당 성분 라벨 직접 동거어만 confirmed.
  - 과다해석 금지: "흡수 정도 영향 없음 / 임상적 관련성 없음 / 영향 없음" 완화·부정 문구가 동거 시 reject(또는 needs_review).
  - source_confirmed 는 방향성까지 일치할 때만(depletion=고갈 신호, absorption=흡수저해/병용/간격 신호).

사용: python3 scripts/verify_coverage_queue_sources_v1_2.py [--no-write] [--limit N] [--delay S]
종료 코드: 0 정상.
"""
import argparse
import csv
import importlib.util
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
PRECHECK_CSV = os.path.join(DATA, "coverage_queue_precheck_v1_2.csv")
OUT_CSV = os.path.join(DATA, "coverage_queue_source_check_v1_2.csv")
CHECKED_AT = "2026-06-14"
DETAIL_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={}"

# verify_factory_sources_v1_2 의 검증된 함수/detector 재사용(중복 금지)
_spec = importlib.util.spec_from_file_location(
    "vfs", os.path.join(HERE, "verify_factory_sources_v1_2.py"))
vfs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfs)

# 과다해석 방지: 완화/부정 문구(동거 시 흡수저하·고갈 주장 성립 안 함).
NEGATION_RE = re.compile(
    r"영향(을)?\s*(받지\s*않|미치지\s*않|없)|임상적(으로)?\s*(유의|관련)성(이)?\s*없|"
    r"흡수\s*정도.{0,10}영향.{0,6}없|유의(미)?하지\s*않|차이(가)?\s*없|문제(가)?\s*되지\s*않")

# 철분 detector 보강(batch2): vfs.d_iron_absorption 의 '철(Fe)염'·'철(Fe)' 표기 갭을 메운다.
# 발견: 알마게이트 라벨 "철(Fe)염 제제 : 흡수를 감소시킬 수 있으므로 2∼3시간 간격" — (Fe) 삽입으로
# 기존 정규식(철염)이 미스 → false-reject. 직전 라운드 파일은 불변, 보강은 이 스크립트 안에서만.
_IRON_ANCHOR = re.compile(r"철\s*\(\s*Fe\s*\)\s*염?|철분|철염|철\s*함유|철\s*제제|철제|철\s*및|철ㆍ|철·")


def d_iron_absorption_v2(text):
    for m in _IRON_ANCHOR.finditer(text):
        i = m.start()
        w = text[max(0, i - 80):i + 80]
        if vfs.EXCIPIENT_CTX.search(w):
            continue
        if re.search(r"흡수|병용|복합체|간격|동시|다가\s*양이온|킬레이트", w):
            return True, vfs.snip(text, i)
    return False, ""

# 성분명 → nedrug ingrName1 검색용 base stem. 짝이온/수화물 토큰 제거.
SALT_TOKENS = [
    "염산염", "황산수소염", "황산염", "푸마르산염", "말레산염", "시트르산염수화물", "시트르산염",
    "숙신산염", "베실산염", "옥살산염", "타르타르산염", "메실산염", "메탄설폰산염", "아세트산염",
    "프로판디올수화물", "트로메타몰", "트로메타민", "인산염수화물", "인산염", "탄산염",
    "나트륨수화물", "나트륨", "칼슘삼수화물", "칼슘", "칼륨삼수화물", "칼륨",
    "삼수화물", "이수화물", "일수화물", "반수화물", "수화물", "(미분화)", "미분화",
]


def strip_salt(name):
    """짝이온/수화물 접미 토큰 제거해 검색 stem 추출(복합제는 '/' 앞 첫 성분만)."""
    base = name.split("/")[0].strip()
    changed = True
    while changed:
        changed = False
        for tok in SALT_TOKENS:
            if base.endswith(tok) and len(base) > len(tok) + 1:
                base = base[: -len(tok)].strip()
                changed = True
    return base


def classify(candidate, text, hit, snippet):
    """detector hit + 방향/부정 문맥으로 분류. 보수적(불확실=needs_review/reject)."""
    if not hit:
        return "reject", "허가사항에 해당 영양소 상호작용/이상반응 동거어 미기재(직접 근거 없음)."
    # 부정/완화 문구가 같은 스니펫 근방에 있으면 과다해석 방지
    if NEGATION_RE.search(snippet):
        return "needs_review", ("동거어는 있으나 같은 문맥에 '영향 없음/임상적 관련성 없음' 등 완화·부정 표현 "
                                "동반 — 흡수저하·고갈 주장 성립 불명확(과다해석 방지, 라벨 전문 재확인 필요).")
    return "source_confirmed", "허가사항 원문에 해당 영양소 동거어 + 방향 일치(직접 근거)."


def safe_copy(ingredient, nutrient, mechanism):
    """참고정보 톤 사용자 카피(복용지시·추천·치료·구매 0). draft 빌더가 ' / ' 로 split."""
    if mechanism == "absorption":
        disp = (f"{ingredient}을(를) 복용하는 경우 {nutrient}과(와) 같은 시간대 복용 시 "
                f"흡수에 영향이 있을 수 있어, 시간 간격을 두는 것이 도움이 될 수 있습니다.")
    else:
        disp = (f"{ingredient}을(를) 복용하는 경우 {nutrient} 상태에 영향이 있을 수 있어, "
                f"상태 확인이 필요할 수 있습니다.")
    if nutrient == "칼륨":
        mgmt = "칼륨은 임의로 보충하면 위험할 수 있으므로, 보충 여부는 반드시 의사 또는 약사와 상담하세요."
    else:
        mgmt = "구체적인 간격이나 보충 여부는 약사 또는 의사와 상담하세요."
    return f"{disp} / {mgmt}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=1.0, help="후보 간 fetch 간격(초)")
    args = ap.parse_args()

    if not os.path.exists(PRECHECK_CSV):
        print(f"[STOP] precheck CSV 없음: {PRECHECK_CSV}")
        return 1
    pre = [r for r in csv.DictReader(open(PRECHECK_CSV, encoding="utf-8"))
           if r["precheck_class"] == "source_check_candidate"]
    if args.limit:
        pre = pre[: args.limit]
    print(f"=== coverage-queue source check: source_check_candidate {len(pre)}건 ===")

    opener = vfs.make_opener()
    out_rows = []
    for i, c in enumerate(pre, start=1):
        ing_full = c["ingredient"]
        base = strip_salt(ing_full)
        nutrient = c["proposed_nutrient"]
        mech = c["mechanism"]
        action = "separation" if mech == "absorption" else "monitoring"
        det_key = c["detector_key"]
        ksafe = (c.get("potassium_safety", "").lower() == "true") or (nutrient == "칼륨" and mech == "depletion")
        risk = c.get("risk_level", "")
        cid = f"CQ-{c['rank']:0>3}"
        # iron_absorption 은 보강판 사용(철(Fe)염 표기 갭 메움), 나머지는 검증된 vfs detector.
        detector = d_iron_absorption_v2 if det_key == "iron_absorption" else vfs.DETECTORS.get(det_key)

        status = "reject"
        seqs_checked = ""
        snippet = ""
        reason = ""
        if not detector:
            status = "hold"
            reason = f"detector_key 미지원({det_key}) — 결정론적 확인 불가(5영양소 외)."
            print(f"  [{i}/{len(pre)}] {ing_full}×{nutrient}: HOLD(detector 미지원)")
        else:
            seqs, why = vfs.search_itemseqs(opener, base, max_n=2, max_pages=2)
            if not seqs:
                status = "needs_review"
                reason = f"국내 단일 경구 완제품목 미확보({why}) — itemSeq 직접 지정 재확인 필요."
                print(f"  [{i}/{len(pre)}] {ing_full}×{nutrient}: needs_review({why})")
            else:
                seqs_checked = ";".join(s for s, _, _ in seqs)
                hit_any = False
                for seq, pname, pingr in seqs:
                    try:
                        text, _ = vfs.fetch_detail(opener, seq)
                    except Exception as e:  # noqa
                        continue
                    hit, snip = detector(text)
                    if hit:
                        hit_any = True
                        snippet = snip
                        seqs_checked = seq
                        break
                    time.sleep(args.delay)
                status, reason = classify(c, "", hit_any, snippet)
                print(f"  [{i}/{len(pre)}] {ing_full}×{nutrient}: {status}")
        time.sleep(args.delay)

        confirmed = status == "source_confirmed"
        out_rows.append({
            "candidate_id": cid,
            "drug_ingredient": base,
            "nutrient": nutrient,
            "relation_type": action,
            "mechanism": mech,
            "source_status": status,
            "source_url_or_basis": (DETAIL_URL.format(seqs_checked) if confirmed and seqs_checked else
                                    "MFDS nedrug getItemDetail (동거어 미확인)" if status == "reject" else ""),
            "itemseqs_checked": seqs_checked,
            "evidence_snippet": snippet if confirmed else "",
            "source_checked_at": CHECKED_AT,
            "evidence_strength": ("high" if confirmed else ""),
            "risk_level": risk,
            "potassium_safety_card": ("true" if ksafe else "false"),
            "pass_to_draft": ("true" if confirmed else "false"),
            "rejection_or_needs_review_reason": ("" if confirmed else reason),
            "safe_user_copy": (safe_copy(base, nutrient, mech) if confirmed else ""),
            "internal_note": f"precheck rank {c['rank']} ({c.get('therapeutic_class','')}); {c.get('reason','')[:160]}",
            "adversarial_verdict": "",
            "adversarial_itemseq": "",
            "adversarial_quote": "",
        })

    from collections import Counter
    dist = Counter(r["source_status"] for r in out_rows)
    print(f"\n결과 분포: {dict(dist)}")
    confirmed_rows = [r for r in out_rows if r["source_status"] == "source_confirmed"]
    print(f"source_confirmed(→ 적대적 검증 대상): {len(confirmed_rows)}")
    for r in confirmed_rows:
        print(f"  {r['candidate_id']} {r['drug_ingredient']}×{r['nutrient']} itemSeq={r['itemseqs_checked']}")

    if not args.no_write:
        cols = ["candidate_id", "drug_ingredient", "nutrient", "relation_type", "mechanism",
                "source_status", "source_url_or_basis", "itemseqs_checked", "evidence_snippet",
                "source_checked_at", "evidence_strength", "risk_level", "potassium_safety_card",
                "pass_to_draft", "rejection_or_needs_review_reason", "safe_user_copy",
                "internal_note", "adversarial_verdict", "adversarial_itemseq", "adversarial_quote"]
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(out_rows)
        print(f"[write] {os.path.relpath(OUT_CSV, REPO)}")
    else:
        print("(--no-write)")
    print("\n라이브 미반영(relation/full index/alias/export/src 무변경).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
