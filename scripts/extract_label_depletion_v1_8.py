#!/usr/bin/env python3
"""
extract_label_depletion_v1_8.py — 식약처 nedrug 라벨에서 **약물→영양소 고갈(depletion)** 을 견고하게 추출.

v1.7 추출기(extract_label_interaction)는 흡수-방향성(separation) 만 캔다. 본 모듈은 그와 **별개 모드**로
이뇨제·스테로이드 등의 **칼륨/마그네슘 고갈**(저칼륨혈증·칼륨손실·칼륨배설 증가 등) 결핍 명시를 추출한다.

설계 불변(이 모듈은 추출만 — 판정/승급/copy/칼륨 safety 플래그는 호출자·가드가):
  - source_quote 는 **항상 라벨 원문 그대로의 완전한 문장**(잘림 0). 강한 표현 합성 0.
  - 결핍 주장은 '이상반응/부작용/일반적 주의/전해질' 섹션에서만 채택(depletion scope).
  - 🔑 B2 가드: **상호작용(약-약), 임부/수유부/임신/태아, 소아, 고령자, 과량/과다투여 섹션은 off-scope**.
    상호작용의 '칼륨방출 증가'(병용약 맥락)·임부의 신생아 저마그네슘혈증은 약물 본연의 depletion 근거 아님 → 배제.
  - 방향성: '이 약'이 **미네랄을 고갈/배설증가**시키는 방향(저↓)만 depletion. 고칼륨혈증(↑·칼륨보존성)은 wrong_direction → reject.
  - 단순 영양-무관 이상반응 열거는 결핍 STATE/방향이 없으면 매칭 안 됨(트리메토프림×엽산 bare-mention 회귀 방지).

공개 API:
  split_sections / split_sentences            (v1.7 추출기 primitive 재사용 — 동일 문장분할 보장)
  is_depletion_scope(section_name) -> bool
  nutrient_depletion(sentence)     -> (nutrient|None, kind)   # kind: deficiency_state|excretion_increase|level_decrease|wrong_direction:..|None
  extract_depletions(raw_html)     -> list[Finding]           # in-scope·비임부·결핍명시 완전문장
  exact_ingredient_match(ingr, target) -> bool
  is_single_oral_depletion(row, target) -> bool               # 단일성분·경구 + 주성분=target 정확매칭
Finding = {section, source_quote, nutrient, evidence_kind, direction, mechanism, action}
"""
from __future__ import annotations

import importlib.util
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# v1.7 추출기의 섹션/문장 분할 primitive 재사용(동일 분할 → GOLD verbatim 정합).
_ix = _load("ix_v17", "extract_label_interaction_v1_7.py")
split_sections = _ix.split_sections
split_sentences = _ix.split_sentences
_norm = _ix._norm

# ───────────────────── depletion scope(섹션) ─────────────────────
# 결핍 주장을 채택하는 in-scope 섹션(정규화 후 부분일치).
_INSCOPE_KEYS = ("이상반응", "부작용", "일반적주의", "일반적인주의", "전해질")
# 🔑 off-scope(강제 배제) — 약-약 상호작용 / 임부·수유 / 소아·고령자 / 과량 / 효능·용법 / 금기·저장.
_OFFSCOPE_KEYS = ("상호작용", "병용투여", "약물상호작용", "임부", "수유부", "임신", "수유",
                  "소아", "고령자", "고령", "노인", "과량투여", "과다투여", "과량", "과다",
                  "효능효과", "용법용량", "금기", "저장", "보관", "신생아", "분만")


def is_depletion_scope(section_name) -> bool:
    n = _norm(section_name)
    if any(_norm(k) in n for k in _OFFSCOPE_KEYS):
        return False
    return any(_norm(k) in n for k in _INSCOPE_KEYS)


# ───────────────────── 영양소 + 결핍 방향 ─────────────────────
NUTRIENTS = ("칼륨", "마그네슘")
# 결핍 STATE(그 자체로 결핍-양성) — 라벨이 직접 명명한 저하 상태.
_DEFICIENCY_STATE = {
    "칼륨": ["저칼륨혈증", "저칼륨성", "칼륨손실", "칼륨소실", "칼륨 손실", "칼륨 소실", "칼륨결핍", "칼륨 결핍"],
    "마그네슘": ["저마그네슘혈증", "마그네슘손실", "마그네슘소실", "마그네슘 손실", "마그네슘 소실",
              "마그네슘결핍", "마그네슘 결핍"],
}
# 결핍 방향 동사(영양소 인근) — 배설/손실 증가 = 고갈, 저하/감소/고갈.
_LOSS_VERBS = ("배설", "손실", "소실", "고갈", "상실")
_DECREASE_VERBS = ("저하", "감소", "결핍")
# wrong-direction(상승·칼륨보존성) — 고칼륨혈증/혈청칼륨 상승/칼륨저류 → 결핍 아님(reject).
_RISE = {
    "칼륨": ["고칼륨혈증", "칼륨저류", "칼륨 저류", "칼륨보존", "칼륨 보존", "칼륨이 상승", "칼륨의 상승"],
    "마그네슘": ["고마그네슘혈증", "마그네슘 상승", "마그네슘이 상승"],
}
# B2: 문장 자체에 임신/태아/신생아 맥락이 섞이면 결핍 근거로 쓰지 않음(섹션 가드 보강).
_PREG_TOKENS = ("임부", "임산부", "임신", "태아", "수유", "신생아", "분만")


def _rise_only(sent, nut):
    """혈청/혈중 nut 상승·고nut혈증 만 있고 결핍 신호는 없는가(wrong direction)."""
    if any(r in sent for r in _RISE[nut]):
        return True
    if re.search(rf"(혈청|혈중)\s*{nut}[^.]{{0,8}}(증가|상승)", sent):
        return True
    return False


def nutrient_depletion(sentence):
    """문장에서 (영양소, kind) 판정. 결핍 명시 없으면 (None, None). 상승만이면 (None,'wrong_direction:nut')."""
    s = sentence or ""
    for nut in NUTRIENTS:
        state = any(k in s for k in _DEFICIENCY_STATE[nut])
        # 영양소 토큰 인근(±조사) 배설/손실 = 고갈 (예: '칼륨의 배설을 증가', '칼륨 손실')
        excretion = bool(re.search(rf"{nut}(을|를|의|이|\s)*[^.]{{0,6}}(배설|손실|소실)", s)) \
            or any(v in s for v in _LOSS_VERBS) and nut in s and bool(re.search(rf"{nut}[^.]{{0,8}}({'|'.join(_LOSS_VERBS)})", s))
        decrease = bool(re.search(rf"{nut}[^.]{{0,12}}({'|'.join(_DECREASE_VERBS)})", s))
        depl = state or excretion or decrease
        if not (nut in s or state):
            continue
        if depl and not (_rise_only(s, nut) and not state and not excretion and not decrease):
            kind = "deficiency_state" if state else ("excretion_increase" if excretion else "level_decrease")
            return nut, kind
        if _rise_only(s, nut) and not depl:
            return None, "wrong_direction:" + nut
    return None, None


# ───────────────────── 추출 메인 ─────────────────────
def extract_depletions(raw_html):
    """in-scope(이상반응/일반적주의/전해질)·비임부·결핍명시 완전문장 depletion Finding 목록.
    copy 생성/승급/칼륨 플래그는 하지 않는다(호출자·가드 책임)."""
    findings, seen = [], set()
    for name, text in split_sections(raw_html):
        if not is_depletion_scope(name):
            continue
        for sent in split_sentences(text):
            if any(p in sent for p in _PREG_TOKENS):   # B2 문장-레벨(섹션 가드 보강)
                continue
            nut, kind = nutrient_depletion(sent)
            if not nut:
                continue
            if sent in seen:
                continue
            seen.add(sent)
            findings.append({
                "section": name,
                "source_quote": sent,            # 완전 문장(잘림 0)
                "nutrient": nut,
                "evidence_kind": kind,
                "direction": "drug_depletes_nutrient",
                "mechanism": "depletion",
                "action": "monitoring",
            })
    return findings


# ───────────────────── 단일성분·경구 + 주성분 정확매칭 ─────────────────────
# 검색 부분매칭 오탐(프레드니솔론→메틸프레드니솔론, 미분화플루드로코르티손아세테이트 prefix) 차단.
_SALT_SUFFIX = ("나트륨", "염산염", "황산염", "인산염", "인산나트륨", "인산이나트륨", "수화물", "일수화물",
                "이수화물", "삼수화물", "말레산염", "메실산염", "주석산염", "초산염", "아세테이트",
                "발레로아세테이트", "발레레이트", "프로피온산염", "푸로에이트", "피발레이트",
                "헤미숙시네이트", "숙신산나트륨", "데부티레이트", "디히드로젠")
_COMBO_SIGNALS = ("/", ",", "+", "외 ", " 외")
# 주성분 앞 수식어(제형 한정어) — '미분화플루드로코르티손아세테이트' 의 '미분화' 등. 동일 활성성분이므로 strip 후 매칭.
_QUALIFIER_PREFIX = ("미분화", "미세화", "무수", "건조", "정제")


def exact_ingredient_match(ingr, target):
    """주성분(ingr)이 target 약물과 정확히 일치(선두 수식어·염/에스터 접미사 허용·복합제 제외).
    '메틸프레드니솔론' 은 '프레드니솔론' 으로 시작하지 않으므로 false(부분매칭 오탐 차단)."""
    if any(x in (ingr or "") for x in _COMBO_SIGNALS):
        return False
    n = re.sub(r"[\s\(\)]+", "", ingr or "")
    t = re.sub(r"[\s\(\)]+", "", target or "")
    if not t:
        return False
    for q in _QUALIFIER_PREFIX:                 # 선두 수식어 제거(동일 활성성분)
        if n.startswith(q) and len(n) > len(q):
            n = n[len(q):]
            break
    if n == t:
        return True
    if n.startswith(t):
        rem = n[len(t):]
        return any(rem == sfx or rem.startswith(sfx) for sfx in _SALT_SUFFIX)
    return False


def is_single_oral_depletion(row, target):
    """단일성분·경구 완제 + 주성분=target 정확매칭. v1.7 필터(제형/취소/원료) + '/' 복합 + exact ingr."""
    if not _ix.is_single_oral_product(row):
        return False
    ingr = (row.get("ingr_name") if isinstance(row, dict) else getattr(row, "ingr_name", "")) or ""
    if "/" in ingr:                      # v1.7 필터가 놓치는 '/' 복합제 보강
        return False
    return exact_ingredient_match(ingr, target)


if __name__ == "__main__":
    # 자체 점검(빠른 확인)
    assert nutrient_depletion("저칼륨혈증, 저나트륨혈증이 나타날 수 있다.")[0] == "칼륨"
    assert nutrient_depletion("칼륨의 배설을 증가시킨다.")[0] == "칼륨"
    assert nutrient_depletion("고칼륨혈증이 나타날 수 있다.")[0] is None     # rise → reject
    assert nutrient_depletion("혈청 칼륨이 상승할 수 있다.")[0] is None       # rise → reject
    assert nutrient_depletion("이 약은 위장관 운동을 촉진한다.")[0] is None   # 무관
    assert exact_ingredient_match("메틸프레드니솔론", "프레드니솔론") is False
    assert exact_ingredient_match("미분화플루드로코르티손아세테이트", "플루드로코르티손") is True
    assert is_depletion_scope("3. 이상반응") and is_depletion_scope("4. 일반적주의")
    assert not is_depletion_scope("6. 상호작용") and not is_depletion_scope("7. 임부 및 수유부에 대한 투여")
    print("extract_label_depletion_v1_8 self-check OK")
