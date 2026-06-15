#!/usr/bin/env python3
"""
validate_harvester_schedule_safety_v1_3.py
MediStack — harvester workflow(`.github/workflows/harvest.yml`) **schedule-safety 검증기**(읽기전용·네트워크 0).

목적: schedule(cron)이 **나중에** 켜지더라도 harvester 가 구조적으로 live write/auto-integrate 를 할 수 없음을
      기계적으로 보증한다. 현재 main 에서 schedule 이 비활성인지도 함께 확인한다. **워크플로우 파일을 수정하지 않는다.**

검증 규칙(워크플로우 텍스트에 대해 평가):
  R1 schedule_not_active        : 활성(비주석) `schedule:`/`cron:` 라인이 없다(현 main = 주석 유지).
  R2 has_workflow_dispatch      : `workflow_dispatch:` 트리거가 존재(수동 경로 보존).
  R3 commit_default_false       : `commit` 입력 기본값이 false(또는 입력 자체 없음=artifact-only). true 면 FAIL.
  R4 no_direct_push_to_main     : `git push` 가 main/master/github.ref 로 직접 가지 않는다(전용 브랜치+PR 만).
  R5 write_scope_queue_only     : `git add` 대상이 data/harvest_queue/ 한정 + out-of-scope staged 차단 가드 존재.
  R6 no_live_export_write       : 보호/live 파일(export·full index·alias)에 쓰기 동사(git add/redirect/cp/mv/tee) 없음
                                  (validator 가 read-only 인자로 참조하는 것은 허용 — 쓰기 동사만 위반).
  R7 no_integrate_call          : integrate_*.py(live 승격 스크립트) 호출 없음.
  R8 uses_no_live_write_guard   : guard_no_live_write 가드를 거쳐 봇을 실행.
  R9 artifact_or_queue_only     : upload-artifact(PM 큐) 산출 + deploy/Pages publish 스텝 없음.

실행:
  1) 현재 main 의 harvest.yml 을 평가 → 9규칙 전건 PASS 여야 한다.
  2) 결함 주입(fault injection) — 메모리상 변형본으로만(실파일 무수정):
       cron 활성화 / commit default true / integrate 호출 / export write 경로 / main 직접 push
     각각이 해당 규칙을 **FAIL** 로 뒤집는지 + 정상 워크플로우가 **PASS** 하는지.
종료코드: 0 PASS, 1 FAIL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WORKFLOW = os.path.join(REPO, ".github", "workflows", "harvest.yml")

PROTECTED_HINTS = (
    "medistack_v0.1_beta_export", "medistack_v0.2_beta_export",
    "medistack_v0.3_aliases", "full_drug_name_index",
)
WRITE_VERB_RE = re.compile(r"(\bgit\s+add\b|>>?\s|\bcp\s|\bmv\s|\btee\b)")
DEPLOY_RE = re.compile(
    r"(deploy-pages|upload-pages-artifact|configure-pages|peaceiris/actions-gh-pages|deploy\.yml|pages:\s*write)")

fails = []


def _uncommented(text):
    """첫 비공백 문자가 '#' 이 아닌(=활성) 라인만."""
    return [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def _commit_default(text):
    """commit 입력의 default 값(소문자 문자열) / 'ABSENT'(입력 없음) / None(default 누락)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == "commit:" and not ln.lstrip().startswith("#"):
            indent = len(ln) - len(ln.lstrip())
            for j in range(i + 1, len(lines)):
                l2 = lines[j]
                if not l2.strip():
                    continue
                ind2 = len(l2) - len(l2.lstrip())
                if ind2 <= indent:
                    break
                m = re.match(r"\s*default:\s*(\S+)", l2)
                if m:
                    return m.group(1).strip().strip('"').strip("'").lower()
            return None
    return "ABSENT"


def evaluate(text):
    """워크플로우 텍스트 → {rule_name: (passed, detail)}."""
    active = _uncommented(text)
    res = {}

    bad = [ln.strip() for ln in active if re.search(r"(^|\s)schedule:", ln) or re.search(r"\bcron:", ln)]
    res["R1_schedule_not_active"] = (not bad, f"활성 schedule/cron: {bad}")

    has_wd = any("workflow_dispatch:" in ln for ln in active)
    res["R2_has_workflow_dispatch"] = (has_wd, "workflow_dispatch 트리거 없음")

    cd = _commit_default(text)
    res["R3_commit_default_false"] = (cd in ("false", "ABSENT"), f"commit default = {cd}")

    push_bad = [ln.strip() for ln in active
                if re.search(r"\bgit\s+push\b", ln) and (re.search(r"\b(main|master)\b", ln) or "github.ref" in ln)]
    res["R4_no_direct_push_to_main"] = (not push_bad, f"main 직접 push: {push_bad}")

    adds = [ln for ln in active if re.search(r"\bgit\s+add\b", ln)]
    bad_adds = [ln.strip() for ln in adds if "data/harvest_queue/" not in ln]
    has_scope_guard = ("OUT_OF_SCOPE" in text) or ("grep -v '^data/harvest_queue/'" in text)
    res["R5_write_scope_queue_only"] = (
        (not bad_adds) and has_scope_guard,
        f"scope밖 git add: {bad_adds} / out-of-scope 가드 존재: {has_scope_guard}")

    proto_write = []
    for ln in active:
        if WRITE_VERB_RE.search(ln) and any(h in ln for h in PROTECTED_HINTS):
            proto_write.append(ln.strip())
    res["R6_no_live_export_write"] = (not proto_write, f"보호파일 쓰기: {proto_write}")

    integ = [ln.strip() for ln in active if re.search(r"integrate_\w+\.py", ln)]
    res["R7_no_integrate_call"] = (not integ, f"integrate 호출: {integ}")

    res["R8_uses_no_live_write_guard"] = (
        any("guard_no_live_write" in ln for ln in active), "no-live-write 가드 미사용")

    has_artifact = any("upload-artifact" in ln for ln in active)
    deploy_bad = [ln.strip() for ln in active if DEPLOY_RE.search(ln)]
    res["R9_artifact_or_queue_only"] = (
        has_artifact and not deploy_bad,
        f"artifact 업로드: {has_artifact} / deploy 스텝: {deploy_bad}")
    return res


def _check(label, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(label)


def main():
    print("=== validate_harvester_schedule_safety_v1_3 ===")
    if not os.path.exists(WORKFLOW):
        print(f"[FATAL] 워크플로우 없음: {WORKFLOW}")
        return 1
    with open(WORKFLOW, encoding="utf-8") as f:
        real = f.read()

    print("--- (1) 현재 main harvest.yml — 9규칙 전건 PASS 기대 ---")
    res = evaluate(real)
    for name, (ok, detail) in res.items():
        _check(name, ok, detail)

    print("--- (2) 결함 주입 — 변형본만(실파일 무수정), 해당 규칙 FAIL 로 뒤집힘 기대 ---")

    # cron 활성화: 주석 해제 → R1 FAIL
    f_cron = real.replace("  # schedule:", "  schedule:").replace("  #   - cron:", "    - cron:")
    _check("결함: cron 활성화 → R1 FAIL", not evaluate(f_cron)["R1_schedule_not_active"][0])

    # commit default true → R3 FAIL
    f_commit = real.replace("default: false", "default: true")
    _check("결함: commit default true → R3 FAIL", not evaluate(f_commit)["R3_commit_default_false"][0])

    # integrate 호출 스텝 삽입 → R7 FAIL
    f_integ = real + (
        "\n      - name: (결함주입) integrate 호출\n"
        "        run: python3 scripts/integrate_potassium_pm_ready_v1_2.py --pm-approved\n")
    _check("결함: integrate 호출 → R7 FAIL", not evaluate(f_integ)["R7_no_integrate_call"][0])

    # 보호 export write 경로 삽입 → R5+R6 FAIL
    f_export = real + (
        "\n      - name: (결함주입) export 직접 write\n"
        "        run: |\n"
        "          git add data/medistack_v0.2_beta_export.json\n")
    e_export = evaluate(f_export)
    _check("결함: export write 경로 → R6 FAIL", not e_export["R6_no_live_export_write"][0])
    _check("결함: export git add → R5 FAIL(scope밖)", not e_export["R5_write_scope_queue_only"][0])

    # main 직접 push → R4 FAIL
    f_push = real.replace('git push origin "$BR"', "git push origin main")
    _check("결함: main 직접 push → R4 FAIL", not evaluate(f_push)["R4_no_direct_push_to_main"][0])

    # 정상 워크플로우는 여전히 PASS(대조군)
    _check("대조군: 정상 워크플로우 9규칙 PASS", all(ok for ok, _ in evaluate(real).values()))

    print("=" * 56)
    if fails:
        print(f"RESULT: FAIL — {len(fails)}건: {fails}")
        return 1
    print("RESULT: PASS — schedule 비활성·workflow_dispatch 보존·commit false·main 직접push 없음·"
          "write-scope 큐한정·보호파일 무쓰기·integrate 미호출·guard 사용·artifact-only / 결함주입 전건 탐지")
    return 0


if __name__ == "__main__":
    sys.exit(main())
