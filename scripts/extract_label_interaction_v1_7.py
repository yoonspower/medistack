#!/usr/bin/env python3
"""
extract_label_interaction_v1_7.py — 식약처 nedrug 라벨에서 흡수-방향성 상호작용을 **견고하게** 추출.

v1.6 추출 결함(naive 정규식)을 직접 수정한다:
  (1) 문장 중간 잘림 → 오도성 fragment  ⇒ 한국어 종결('다.'/'것.'/'요.')로 완전한 문장만 산출.
  (2) 방향성 동사 누락(특히 '방해') → 매칭 실패  ⇒ 동사 사전으로 커버리지 확보.
  (3) 이상반응/임부/복약안내 줄을 상호작용으로 오인  ⇒ 섹션 분할 + scope 강제(상호작용/병용투여만 채택).

설계 불변(이 모듈은 추출만 한다 — 판정/승급/copy 생성은 호출자·가드가):
  - source_quote 는 **항상 라벨 원문 그대로의 완전한 문장**(잘림 0). 강한 표현 합성 0.
  - 흡수-방향성 주장은 '상호작용·병용투여' 섹션에서만 채택. 그 외 섹션의 동거어는 reject(off_scope).
  - counterpart 가 '이 약'의 흡수를 낮추는 방향이어야 separation-supporting. 반대/모호 → direction='ambiguous'.

공개 API:
  split_sections(raw_html)            -> list[(section_name, section_text)]   # 문서 순서
  split_sentences(text)               -> list[str]                            # 완전 문장(enumerator 제거)
  is_interaction_scope(section_name)  -> bool
  classify_counterparts(sentence)     -> (category|None, terms:list)
  absorption_direction(sentence)      -> 'this_drug_lowered' | 'other_lowered' | 'ambiguous' | None
  extract_interactions(raw_html)      -> list[Finding]                        # 상호작용 섹션의 흡수-방향성 문장
  is_single_oral_product(row)         -> bool                                 # 단일성분·경구 완제 필터(search row)
Finding = {section, source_quote, counterpart_category, counterpart_terms, verb, direction, mechanism, action}
"""
from __future__ import annotations

import html as _html
import re

# ───────────────────── 섹션 분할 ─────────────────────
# nedrug 상세는 최상위 블록(<h3 class="cont_title2 fl">효능효과/용법용량/사용상의주의...)과
# 그 하위 번호 섹션(<p class="title">N. 상호작용 / N. 이상반응 / N. 임부...)으로 구성된다.
_H3_RE = re.compile(r'<h3[^>]*class="[^"]*cont_title2[^"]*"[^>]*>\s*([^<]+?)\s*<', re.I)
_PTITLE_RE = re.compile(r'<p[^>]*class="title"[^>]*>\s*([^<]+?)\s*</p>', re.I)

# 흡수-방향성 주장을 채택하는 섹션(scope). 정규화(공백 제거) 후 부분일치.
_INTERACTION_KEYS = ("상호작용", "병용투여", "병용투여및약물상호작용", "약물상호작용")
# 명시적 off-scope(상호작용성 동거어가 나와도 reject) — scope 밖 표시용.
_OFFSCOPE_KEYS = ("이상반응", "임부", "수유부", "임신", "소아", "고령자", "용법용량",
                  "효능효과", "일반적주의", "경고", "금기", "저장", "보관")


def _strip(s: str) -> str:
    """태그 제거 + 엔티티 복원 + 공백 정규화(문장 경계는 보존됨 — 공백만 접음)."""
    s = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)</(p|div|li|tr|td|h[1-6])\s*>|<br\s*/?>", "\n", s)  # 블록 경계 → 줄바꿈
    s = re.sub(r"<[^>]+>", " ", s)
    s = _html.unescape(s)
    return re.sub(r"[ \t ]+", " ", s).strip()


def _norm(name: str) -> str:
    return re.sub(r"[\s\.\d]+", "", name or "")


def split_sections(raw_html):
    """문서 순서대로 (섹션명, 섹션텍스트) 리스트. 섹션 경계 = h3/​p.title 마커."""
    marks = []
    for m in _H3_RE.finditer(raw_html):
        marks.append((m.start(), m.end(), _html.unescape(m.group(1)).strip()))
    for m in _PTITLE_RE.finditer(raw_html):
        marks.append((m.start(), m.end(), _html.unescape(m.group(1)).strip()))
    marks.sort()
    out = []
    for i, (s, e, name) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(raw_html)
        out.append((name, _strip(raw_html[e:nxt])))
    return out


def is_interaction_scope(section_name) -> bool:
    n = _norm(section_name)
    if any(k in n for k in _INTERACTION_KEYS):
        return True
    return False


def is_offscope(section_name) -> bool:
    n = _norm(section_name)
    return any(k in n for k in _OFFSCOPE_KEYS) and not is_interaction_scope(section_name)


# ───────────────────── 문장 분할(완전 문장 보장) ─────────────────────
# 한국어 평서문 종결 '~다.' / 지시 '~것.' / 존대 '~요.' 뒤 공백을 경계로 분할.
# 종결 직전 글자가 '다/것/요' 여야 하므로 소수점('1.7')·약어에서 잘리지 않는다.
_SENT_SPLIT = re.compile(r"(?<=[다것요]\.)\s+")
# 선두 enumerator 제거: 'N)' '(N)' 'N.' '○' '●' '•' '-' '·' 'ㅇ' '가)' '나)' 등.
_ENUM_LEAD = re.compile(r"^\s*(?:\(?\d+\)|\d+\.|[○●◦•▷▸·\-–—]|[가-힣]\))\s*")


def split_sentences(text):
    """완전 문장 리스트. 블록 경계('\\n') 먼저 분할 → 문장 종결 분할 → enumerator 선두 제거.
    블록 분할이 라벨 전용 줄(종결부호 없음)을 다음 문장과 분리해 글루/잘림을 막는다(예: '2) 칼슘보충제/제산제')."""
    out = []
    for block in re.split(r"\n+", text):          # 블록(=라벨/문장 단위) 경계
        for raw in _SENT_SPLIT.split(block):      # 블록 내 '다.' 종결 경계
            s = _ENUM_LEAD.sub("", raw).strip()
            # 다시 한 번(중첩 enumerator '1) (1)' 방지) — 단, 본문 손실 없이 선두만.
            s = _ENUM_LEAD.sub("", s).strip()
            if not s:
                continue
            # 완전 문장만: 종결부호(다./것./요./.)로 끝나야 한다. 라벨 전용 줄은 종결부호 없어 탈락.
            if not re.search(r"[다것요]\.$|\.$", s):
                continue
            out.append(s)
    return out


# ───────────────────── counterpart 사전 ─────────────────────
# (term, category). 우선순위: 제산제(al_mg_antacid) > 미네랄 보충제 > 단일 양이온.
# category 는 MediStack universe 의 counterpart_category 와 정합.
_CP_RULES = [
    ("알루미늄 함유 제산제", "al_mg_antacid"),
    ("마그네슘 함유 제산제", "al_mg_antacid"),
    ("알루미늄·마그네슘 함유 제산제", "al_mg_antacid"),
    ("제산제", "al_mg_antacid"),
    ("칼슘보충제", "ca"),
    ("칼슘보조제", "ca"),
    ("칼슘 보충제", "ca"),
    ("철분제제", "fe"),
    ("철분", "fe"),
    ("아연", "zn"),
    ("다가 양이온", "polyvalent_cation"),
    ("다가양이온", "polyvalent_cation"),
    ("칼슘", "ca"),
    ("마그네슘", "mg"),
    ("알루미늄", "al"),
]
# category 채택 우선순위(한 문장에 여러 개면 가장 약물-counterpart 다운 것을 대표로).
_CAT_PRIORITY = ["al_mg_antacid", "fe", "ca", "polyvalent_cation", "mg", "zn", "al"]


def antacid_scope_from_quote(quote):
    """quote 가 **명시적으로 명명한** 양이온에 따라 제산제 counterpart 표시명을 정한다.
    일반 '제산제'만 있고 Al/Mg/특정 양이온 명명이 없으면 None — Al/Mg-specific 으로 좁히면 원문보다 강함."""
    has_al = "알루미늄" in quote
    has_mg = "마그네슘" in quote
    if has_al and has_mg:
        return "Al/Mg 함유 제산제(약물)"
    if has_al:
        return "알루미늄 함유 제산제(약물)"
    if has_mg:
        return "마그네슘 함유 제산제(약물)"
    return None


def counterpart_scope_justified(counterpart_str, quote):
    """counterpart 표시명의 양이온 특정성이 source quote 에 의해 뒷받침되는지(원문보다 강하지 않은지).
    예: 'Al/Mg 함유 제산제(약물)'는 quote 에 알루미늄·마그네슘이 모두 명명돼야 한다. 일반 '제산제'면 좁힘 금지."""
    cs = counterpart_str or ""
    if "Al/Mg" in cs:
        return ("알루미늄" in quote) and ("마그네슘" in quote)
    if "알루미늄" in cs:
        return "알루미늄" in quote
    if "마그네슘" in cs:
        return "마그네슘" in quote
    return True


def classify_counterparts(sentence):
    """문장에서 counterpart 용어 추출 → (대표 category, 발견 term 목록). 없으면 (None, [])."""
    terms, cats = [], set()
    for term, cat in _CP_RULES:
        if term in sentence:
            terms.append(term)
            cats.add(cat)
    if not cats:
        return None, []
    # 대표 category: '제산제'가 있으면 al_mg_antacid(약물 counterpart), 아니면 우선순위.
    rep = next((c for c in _CAT_PRIORITY if c in cats), None)
    # polyvalent_cation 단독이고 Al/Mg/Fe 가 함께 열거되면 al_mg_antacid 후보로 승격 가능하나,
    # 여기서는 명시 '제산제' 없으면 polyvalent_cation 으로 보수적 유지(가드/검토가 판단).
    return rep, sorted(set(terms))


# ───────────────────── 방향성 동사 + 방향 판정 ─────────────────────
# v1.6 이 '방해'를 놓쳐 비스포스포네이트를 흘렸다 → 동사 사전으로 커버.
_DIR_VERBS = ("저해", "방해", "저하", "지연", "감소", "떨어뜨", "줄어", "줄어듦", "감소될", "저해할")
# '이 약'의 흡수가 낮아지는 방향(separation-supporting).
_THIS_LOWERED = [
    re.compile(r"이 ?약의 흡수(를|가)[^.]*?(저해|방해|저하|지연|감소|떨어뜨|줄어)"),
    re.compile(r"이 ?약의 흡수가[^.]*?(지연|감소|저하)[^.]*?될 수 있"),
]
# '이 약'이 상대(다른 약)의 흡수를 낮추는 방향(opposite — separation 근거 아님).
_OTHER_LOWERED = re.compile(r"이 ?약(은|이|이는)[^.]*?(의|을|를)[^.]*?흡수(를|가)[^.]*?(저해|방해|저하|지연|감소)")


def has_direction_verb(sentence) -> bool:
    return any(v in sentence for v in _DIR_VERBS)


def absorption_direction(sentence):
    """흡수 방향 판정. this_drug_lowered = separation-supporting."""
    if not has_direction_verb(sentence):
        return None
    if any(p.search(sentence) for p in _THIS_LOWERED):
        return "this_drug_lowered"
    if _OTHER_LOWERED.search(sentence):
        return "other_lowered"
    # 흡수+동사는 있으나 주체가 '이 약' 명시 안 됨 → 모호.
    if "흡수" in sentence:
        return "ambiguous"
    return None


# ───────────────────── 추출 메인 ─────────────────────
def extract_interactions(raw_html):
    """상호작용/병용투여 섹션의 흡수-방향성(이 약 흡수 저하) 완전 문장 Finding 목록.

    반환 Finding(완전 인용 + 분류). copy 생성/승급은 하지 않는다(호출자 책임).
    """
    findings = []
    seen = set()
    for name, text in split_sections(raw_html):
        if not is_interaction_scope(name):
            continue
        for sent in split_sentences(text):
            if not has_direction_verb(sent):
                continue
            cat, terms = classify_counterparts(sent)
            if not cat:
                continue
            direction = absorption_direction(sent)
            if sent in seen:
                continue
            seen.add(sent)
            findings.append({
                "section": name,
                "source_quote": sent,             # 완전 문장(잘림 0)
                "counterpart_category": cat,
                "counterpart_terms": terms,
                "verb": next((v for v in _DIR_VERBS if v in sent), None),
                "direction": direction,
                "mechanism": "absorption",
                # separation-supporting 만 separation action; 그 외는 needs_review 신호.
                "action": "separation" if direction == "this_drug_lowered" else "needs_review",
            })
    return findings


# ───────────────────── 단일성분·경구 완제 필터 ─────────────────────
_NON_ORAL = ("주", "주사", "주사제", "외용", "점안", "점이", "연고", "크림", "겔", "패취", "패치",
             "흡입", "분무", "좌제", "시럽주")
_RAW_OR_EXPORT = ("원료", "수출용")
# 복합/결합제 신호(단일 주성분 아님).
_COMBO = ("복합", "/", "외 ", " 외", "+", "configuration")


def is_single_oral_product(row):
    """search row(item_name·ingr_name·finished·status_cancel)가 단일성분·경구 완제·정상인지.

    row: dict 또는 .item_name/.ingr_name/.finished/.status_cancel 속성 보유 객체.
    """
    def g(k):
        return (row.get(k) if isinstance(row, dict) else getattr(row, k, "")) or ""
    name, ingr = g("item_name"), g("ingr_name")
    finished, cancel = g("finished"), g("status_cancel")
    if "정상" not in cancel and cancel:           # 취소/취하 제외
        return False
    if finished and "완제" not in finished:        # 원료 제외
        return False
    if any(k in name for k in _RAW_OR_EXPORT):
        return False
    # 비경구 제형(이름 기반) 제외 — '정'/'캡슐'/'서방정' 우선.
    if not re.search(r"(정|캡슐|캅셀|환|산|과립|구강붕해)", name):
        # 정/캡슐류 표기가 없고 비경구 신호가 있으면 제외
        if any(k in name for k in _NON_ORAL):
            return False
    else:
        # 정/캡슐이라도 '주'가 들어가면(예: '~주정') 비경구 우선 검사는 생략(정 표기 신뢰)
        pass
    # 단일 주성분: ingr_name 에 복합 신호 없어야(콤마/플러스/'외').
    if ingr and any(k in ingr for k in (",", "+", "외 ", " 외")):
        return False
    return True
