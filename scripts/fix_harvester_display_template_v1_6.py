#!/usr/bin/env python3
"""
fix_harvester_display_template_v1_6.py
MediStack Factory v1.6 — Phase A: harvester **display-template 결함 입력단 차단**.

문제(PR-1·PR-3 에서 반복 적발): harvest 단계의 draft display copy 생성기
(`relation_factory_bot_v1_4.app_copy`)가 라벨이 직접 말하지 않은 능동형 단정을 박았다.
  - 분리 계열: "...복용 시점을 분리하도록 안내하고 있으니..." (라벨귀속 separation-guidance 단정)
  - depletion 계열: "...{영양소} 수치 변화와 관련된..." / "...수치가 걱정되면..." (수치저하 단정)
이 단정은 매 live-PR 에서 사람이 수동 reframe 해야 했다. v1.6 은 **입력단(템플릿 생성기)** 에서 차단한다.

이 모듈은 **읽기전용·순수함수**(live/protected 무수정). 제공:
  - safe_app_copy(counterpart, action) → (display, management) : live 선례 템플릿만 사용(신규 문구 창작 0).
  - reframe_display(old, action) : 이미 박힌 결함 copy 를 live 선례 형태로 보수(A1/A2).
  - copy_lint(text, source_quote) : 사용자 노출 copy 금칙어/단정/과확장 스캔(vfp 재사용 + v1.6 추가).
  - lint_candidate(cand) : 후보 단위 copy-lint → (ok, violations). 위반 시 auto-reject(A6).
  - quote_truncation_ok(quote) : source quote 잘림 방지(A4).

A1 능동 register 제거 · A2 수치 단정 보수 · A3 fact↔management 분리 · A4 quote 잘림 방지 ·
A5 live 선례 템플릿 고정 · A6 copy-lint 자동 reject.
"""
import importlib.util
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# 권위 금지어 스캐너 재사용(봇/validator 와 동일 — 단일 진실원).
_spec = importlib.util.spec_from_file_location(
    "vfp", os.path.join(HERE, "validate_forbidden_phrases_v1_2.py"))
vfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfp)

# ───────────────────────── A5: live 선례 템플릿(신규 문구 창작 금지) ─────────────────────────
# 분리(absorption/separation) — live 62-85 선례와 동형(label fact + 비지시 tail).
SEP_DISPLAY = ("이 약은 {cp}과(와) 함께 복용하면 흡수가 저하될 수 있다는 "
               "허가사항 문구가 있습니다. 함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요.")
SEP_MGMT = "{cp}과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
# 만성 depletion(monitoring) — live 86-93 선례와 동형(수치 단정 없음·골질환 alarm 없음).
DEPL_DISPLAY = ("이 약을 장기간 복용할 때 {cp}과(와) 관련된 허가사항 주의 문구가 있습니다. "
                "증상이 걱정되면 약사 또는 의사와 상담하세요.")
DEPL_MGMT = "장기 복용 중이라면 정기 진료나 복약 상담 시 해당 영양소 상태 확인이 필요한지 문의해볼 수 있습니다."

# 라벨 fact 종결 마커(reframe 시 head/tail 분리 기준 — PR-1/PR-3 선례와 동일).
_FACT_MARKER_FFACT = "허가사항 문구가 있습니다."      # 분리(흡수저하 fact)
_FACT_MARKER_CAUTION = "허가사항 주의 문구가 있습니다."  # depletion(주의 문구)
_SEP_FACT_TAIL = " 함께 복용하는 경우 복용 시점에 대해 약사 또는 의사와 상담하세요."
_DEPL_FACT_TAIL = " 증상이 걱정되면 약사 또는 의사와 상담하세요."

# ───────────────────────── A6: copy-lint 금지셋 ─────────────────────────
# 사용자 노출 copy 절대 금지(task 명시). vfp.FORBIDDEN 에 더해 v1.6 추가분.
FORBIDDEN_EXTRA = [
    "안전", "문제없다", "복용해도 된다", "검사하세요", "검사를 받으세요",
    "처방을 바꾸세요", "처방을 변경", "영양제를 드세요", "위험합니다", "분리하도록 안내",
    # '효과가 감소'는 source-additive(라벨 원문은 "흡수를 방해/저해"까지만) — display 생성문에만 적용(source_quote 무관).
    "효과가 감소",
    # '반드시'는 명령형 지시(복용/섭취/보충/검사/중단)만 금지 — '반드시 상담/의사' 류는 live 선례(보수 톤)라 허용.
    "반드시 복용", "반드시 드", "반드시 섭취", "반드시 보충", "반드시 검사", "반드시 중단", "반드시 끊",
]
# 과확장(모든 제산제/미네랄/금속이온 등 — 라벨이 특정 성분만 말하는데 전체로 일반화 금지).
OVEREXPANSION = [
    "모든 제산제", "모든 미네랄", "모든 무기질", "모든 금속이온", "모든 양이온",
    "모든 다가양이온", "어떤 제산제", "어떤 미네랄", "전체 제산제", "모든 영양소", "모든 비타민",
]
# 수치 단정(A2). 두 부류:
#  - ALWAYS: app_copy depletion 결함 마커("수치 변화"·"수치가 걱정") — live 선례(PR-2)는 절대 안 씀 → 항상 보수화.
#  - COND : 구체 수치 저하 단정 — 라벨이 농도/수치 저하를 직접 말할 때만 허용.
NUMERIC_CLAIMS_ALWAYS = ["수치 변화", "수치가 걱정"]
NUMERIC_CLAIMS_COND = ["수치가 낮아", "수치가 떨어", "수치가 감소", "수치 저하"]
# source quote 가 농도/수치 저하를 실제로 말하면 COND 표현 허용.
_SRC_NUMERIC_SUPPORT = ["혈중 농도", "농도가 감소", "농도 감소", "수치 감소", "수치가 감소", "혈중 수치"]


def copy_lint(text, source_quote=None):
    """사용자 노출 copy 위반 목록 반환(빈 리스트면 통과). vfp + v1.6 추가 + 수치단정(조건부) + 과확장."""
    t = text or ""
    v = list(vfp.scan(t))                     # 권위 스캐너(치료/구매/복용지시/승인주장 등)
    for p in FORBIDDEN_EXTRA:
        if p in t:
            v.append(p)
    for p in OVEREXPANSION:
        if p in t:
            v.append("overexpansion:" + p)
    sq = source_quote or ""
    src_supports_numeric = any(s in sq for s in _SRC_NUMERIC_SUPPORT)
    for p in NUMERIC_CLAIMS_ALWAYS:          # 결함 마커 — 항상 보수화
        if p in t:
            v.append("numeric_claim_unsourced:" + p)
    for p in NUMERIC_CLAIMS_COND:            # 구체 단정 — source 직접 지지 시 허용
        if p in t and not src_supports_numeric:
            v.append("numeric_claim_unsourced:" + p)
    return v


def quote_truncation_ok(quote):
    """A4: harvest quote 가 잘리지 않았는지(완전한 라벨 문맥 보존). 잘렸으면 승격 불가."""
    q = (quote or "").strip()
    if len(q) < 12:
        return False
    if q.endswith(("…", "...", "..")):
        return False
    if q.endswith(("및", "또는", "와", "과", ",", "·", "+")):  # 불완전 연결어미로 끝남
        return False
    return True


def safe_app_copy(counterpart, action):
    """A3/A5: live 선례 템플릿만으로 (display=label fact, management=hedged 권고) 생성."""
    cp = counterpart
    if action == "separation":
        return SEP_DISPLAY.format(cp=cp), SEP_MGMT.format(cp=cp)
    # monitoring/depletion (그 외 전부 — 보수적으로 depletion 템플릿)
    return DEPL_DISPLAY.format(cp=cp), DEPL_MGMT


def reframe_display(old, action=None):
    """A1/A2: 이미 박힌 결함 display copy 를 live 선례 형태로 보수(원문귀속 단정 제거)."""
    new = old or ""
    # A2: depletion 수치 단정 제거 → "관련된 허가사항 주의 문구" 형태로.
    new = re.sub(r"(.+?)\s*수치 변화와 관련된 허가사항 문구가 있습니다\.",
                 r"\1과(와) 관련된 허가사항 주의 문구가 있습니다.", new)
    new = new.replace("증상이나 수치가 걱정되면", "증상이 걱정되면")
    new = new.replace("수치가 걱정되면", "증상이 걱정되면")
    # A0: head 효과감소 과확장 제거(source-additive) — SEP_DISPLAY 정정과 동일 기준.
    new = new.replace("약의 흡수가 줄어 효과가 감소할 수 있다는", "흡수가 저하될 수 있다는")
    # A1: 분리 능동 register 제거 — fact 마커 뒤를 비지시 tail 로 치환.
    if "분리하도록 안내" in new:
        marker = _FACT_MARKER_FFACT if _FACT_MARKER_FFACT in new else None
        if marker:
            head = new.split(marker)[0] + marker
            tail = _DEPL_FACT_TAIL if action == "depletion" else _SEP_FACT_TAIL
            new = head + tail
    assert "분리하도록 안내" not in new, "reframe 후에도 라벨귀속 분리-안내 단정 잔존"
    assert "수치 변화" not in new and "수치가 걱정" not in new, "reframe 후에도 수치 단정 잔존"
    assert "효과가 감소" not in new, "reframe 후에도 효과감소 과확장 잔존"
    return new


def lint_candidate(cand):
    """A6: 후보 1건 copy-lint. (ok, violations). 위반 시 호출자가 auto-reject."""
    disp = (cand.get("display_text_ko") or cand.get("display_copy")
            or cand.get("display_text_ko_draft") or "")
    mng = (cand.get("management_ko") or cand.get("management_copy")
           or cand.get("management_copy_draft") or "")
    sq = (cand.get("source_quote") or (cand.get("source") or {}).get("quote") or "")
    v = []
    v += ["display:" + x for x in copy_lint(disp, sq)]
    v += ["management:" + x for x in copy_lint(mng, sq)]
    # source quote 가 있어야 하는 user-copy 후보인데 quote 가 잘렸으면 승격 불가(A4).
    if (disp or mng) and not quote_truncation_ok(sq):
        v.append("source_quote_truncated_or_missing")
    return (len(v) == 0, v)


if __name__ == "__main__":
    # 자체 점검(import 없이 빠른 확인)
    d, m = safe_app_copy("철분", "separation")
    assert copy_lint(d) == [] and copy_lint(m) == [], (copy_lint(d), copy_lint(m))
    d2, m2 = safe_app_copy("엽산", "depletion")
    assert copy_lint(d2) == [] and copy_lint(m2) == []
    bad = ("이 약은 칼슘과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 허가사항 문구가 있습니다. "
           "함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, 약사 또는 의사와 상담하세요.")
    assert "분리하도록 안내" in copy_lint(bad)
    assert "분리하도록 안내" not in reframe_display(bad, "separation")
    print("fix_harvester_display_template_v1_6 self-check OK")
