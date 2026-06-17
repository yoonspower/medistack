#!/usr/bin/env python3
"""
test_live_pr_reviewer_note_v1_4.py
check_live_pr_reviewer_note_v1_4 회귀 테스트 (읽기전용·네트워크 0·live 무수정).
invalid 전건 거부 + valid 통과 + 모든 wave 의 valid note 통과 확인.
종료코드 0 PASS / 1 FAIL.
"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def _load(modfile):
    spec = importlib.util.spec_from_file_location(modfile[:-3], os.path.join(HERE, modfile))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _note(tmp, text):
    p = os.path.join(tmp, "note.txt")
    open(p, "w", encoding="utf-8").write(text)
    return p


def expect_reject(mod, tmp, label, text, ids, delta, wave, nr, must=None):
    ok, probs = mod.check_reviewer_note(_note(tmp, text), ids, delta, wave, nr)
    good = (not ok) and (must is None or any(must in p for p in probs))
    print(("  PASS " if good else "  FAIL ") + label + ("" if good else f"  [probs={probs}]"))
    if not good:
        fails.append(label)


def expect_accept(mod, tmp, label, text, ids, delta, wave, nr):
    ok, probs = mod.check_reviewer_note(_note(tmp, text), ids, delta, wave, nr)
    print(("  PASS " if ok else "  FAIL ") + label + ("" if ok else f"  [probs={probs}]"))
    if not ok:
        fails.append(label)


def main():
    mod = _load("check_live_pr_reviewer_note_v1_4.py")
    tmp = tempfile.mkdtemp(prefix="ms_livepr_gate_")
    print("=== live PR wave reviewer-note checker 회귀 테스트 (live 무수정) ===")

    wave = "antibiotic23"
    ids, delta, nr = mod.load_wave(wave)
    V = mod.build_valid_note(wave, ids, delta, nr)
    R = lambda label, text, must=None: expect_reject(mod, tmp, label, text, ids, delta, wave, nr, must)

    print(f"--- 게이트 단위 (wave={wave}, candidate {len(ids)} · delta +{delta}) ---")
    R("빈 노트 거부", "", "비공란")
    R("note 파일 없음 거부 (직접)", None) if False else None
    # 파일 없음
    ok, probs = mod.check_reviewer_note(os.path.join(tmp, "nope.txt"), ids, delta, wave, nr)
    print(("  PASS " if (not ok and any("파일 없음" in p for p in probs)) else "  FAIL ") + "note 파일 없음 거부")
    if ok:
        fails.append("note 파일 없음")
    R("승인 토큰 없음에도 다른 필수 결손 거부", V.replace("RPH-LIVEPR-001", "익명"), "식별 토큰")
    R("reviewer 식별자 라벨 없음 거부", V.replace("검수자:", "메모:"), "reviewer 식별자 라벨")
    R("검토일 placeholder 거부", V.replace("2026-07-01", "YYYY-MM-DD"), "placeholder 날짜")
    R("commit 없음 거부", V.replace("commit 56f6ddf", "최신본"), "commit")
    R("version 없음 거부", V.replace("v1.4", "초안"), "version")
    R("scope wave 누락 거부", V.replace(f"scope(wave={wave})", "scope(대상=일부)"), f"wave={wave}")
    R("candidate 일부 누락 거부", V.replace(ids[0], "RF-F1-9999"), "candidate_id 미명시")
    R("needs_review id 포함 거부", V + f"\n추가로 {nr[0]} 도 함께 승인.", "needs_review candidate 포함")
    R("needs_review 제외 문구 없음 거부", V.replace(f"needs_review {', '.join(nr)} 는 본 승인에서 제외 확인.", "기타 항목 없음."), "needs_review 제외")
    R("delta 불일치 거부", V.replace(f"delta: +{delta}", "delta: +99"), "delta 불일치")
    R("expected count 불일치 거부", V.replace(f"60 → {60 + delta}", "60 → 999"), "expected count 불일치")
    R("grouping 승인 없음 거부", V.replace("grouping 승인: 본 wave 단위 한 번에 통합.", "통합 방식 미정."), "grouping 승인 없음")
    R("source fidelity 없음 거부", V.replace("출처(source) fidelity: 식약처 허가사항 인용과 일치 보존 확인.", "출처 메모 생략."), "source fidelity")
    R("management copy 보수성 없음 거부", V.replace("관리 문구(management copy): 참고·상담 톤 보수성 유지 확인(분리복용/정기확인 문의, 지시 아님).", "문구 메모 생략."), "management copy")
    R("published=false 누락 거부", V.replace("published=false 유지 승인. ", ""), "published=false")
    R("clinical=false 누락 거부", V.replace("clinical_reviewed=false 유지 승인. ", ""), "clinical_reviewed=false")
    R("reviewed_by 공란 누락 거부", V.replace("reviewed_by 공란 유지 승인.", "검토자명 기록."), "reviewed_by 공란")
    R("제품/제휴 UI 확인 없음 거부", V.replace("제품·구매·제휴 UI 추가 없음 확인. ", ""), "제품/구매/제휴 UI")
    R("schedule 비활성 확인 없음 거부", V.replace("schedule 비활성(inactive) 유지 확인.", "스케줄 메모 생략."), "schedule 비활성")
    R("rollback 확인 없음 거부", V.replace("rollback 가능(wave 단위 git revert) 확인.", "되돌리기 메모 생략."), "rollback")
    # 금지 요구
    R("clinical=true 승격 요구 거부", V + "\nclinical_reviewed=true 로 승격 승인.", "clinical_reviewed=true 요구")
    R("published=true 요구 거부", V + "\npublished=true 로 전환 승인.", "published=true 요구")
    R("제품 추천 허용 거부", V + "\n관련 제품 추천 허용함.", "제품 추천 허용")
    R("구매 권유 거부", V + "\n영양제 구매 권유 문구 추가.", "구매 권유")
    R("복용해도 된다 거부", V + "\n함께 복용해도 된다고 안내 가능.", "복용 권유 단정")
    R("안전하다 단정 거부", V + "\n병용은 안전하다고 표기.", "안전 단정")
    R("처방 지시 거부", V + "\n처방 용량 조정 지시 포함.", "처방 지시")
    R("면허번호 강제 거부", V + "\nreviewer 면허번호 입력 필수.", "면허번호")
    R("schedule 활성 허용 거부", V + "\nschedule 활성화 허용.", "schedule 활성화 허용")
    R("reviewed_by 입력 요구 거부", V + "\nreviewed_by 입력 요구.", "reviewed_by 입력 요구")
    R("SAMPLE 토큰 거부", V + "\nAPPROVED-SAMPLE-NOT-VALID", "SAMPLE")

    expect_accept(mod, tmp, "valid note(antibiotic23) 통과", V, ids, delta, wave, nr)

    print("--- 전 wave valid note 통과 ---")
    for w in ["f1_nutrient10", "f1_antacid8", "f1_all18", "f2_all5", "f3_single",
              "f9_all7", "f4_f6_small2", "antibiotic23", "chronic8", "all33"]:
        wi, wd, wn = mod.load_wave(w)
        vv = mod.build_valid_note(w, wi, wd, wn)
        expect_accept(mod, tmp, f"valid note({w}) 통과 (n={len(wi)},+{wd})", vv, wi, wd, w, wn)

    print("=" * 60)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — invalid 전건 거부 + valid 통과 + 10 wave valid note 통과 · live 무수정")
    return 0


if __name__ == "__main__":
    sys.exit(main())
