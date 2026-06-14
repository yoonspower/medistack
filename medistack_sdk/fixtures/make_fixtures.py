#!/usr/bin/env python3
"""
make_fixtures.py — NedrugClient offline 모드용 **합성(synthetic) 응답 fixture** 생성기.

⚠️ 여기 fixture 는 실제 nedrug 응답이 아니라, SDK 파서·파이프라인 detector 를 결정론적으로
   구동하기 위한 **테스트 더블**이다(라벨 문구는 검증된 detector 정규식을 트리거하도록 최소 구성).
   실제 PM 런은 `--online` 으로 SDK 가 실응답을 fetch·cache 한다.

파일명 규칙(NedrugClient._get 와 일치): search_<slug>_p<page>.html / detail_<seq>.html
slug = re.sub(r'[^0-9A-Za-z가-힣]+','_', ingredient)

재생성: python3 medistack_sdk/fixtures/make_fixtures.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def slug(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", s.strip()).strip("_")


def search_html(rows):
    """rows: [(seq, name, ingr)] → searchDrug 결과 HTML(파서 _ANCHOR_RE/_field 호환)."""
    trs = []
    for seq, name, ingr in rows:
        trs.append(
            f'<tr class="result">'
            f'<td><a href="/pbp/CCBBB01/getItemDetail?itemSeq={seq}" class="prodName">{name}</a></td>'
            f'<td><span class="s-th">주성분</span>{ingr}</td>'
            f'<td><span class="s-th">완제/원료구분</span>완제</td>'
            f'<td><span class="s-th">취소/취하구분</span>정상</td>'
            f'</tr>'
        )
    return ('<html><body><table class="resultTable"><tbody>'
            + "".join(trs) + '</tbody></table></body></html>')


def detail_html(seq, title, ingr, body):
    """getItemDetail HTML. body = 태그제거 후 detector 가 읽을 라벨 본문 텍스트."""
    return (f'<html><body><h1 class="title">{title}</h1>'
            f'<script>var item = {{"itemSeq":"{seq}","ingrName":"{ingr}"}};</script>'
            f'<div class="section interaction"><p>{body}</p></div>'
            f'</body></html>')


# (ingredient, [(seq,name,ingr)]) — 검색 fixture
SEARCH = {
    "세파클러": [("100003", "세파클러캡슐250밀리그램", "세파클러")],
    "프레드니솔론": [("100001", "프레드니솔론정5밀리그램", "프레드니솔론")],
    "아세타졸아미드": [("100002", "아세타졸아미드정250밀리그램", "아세타졸아미드")],
    "레보티록신": [("100004", "신지로이드정0.1밀리그램", "레보티록신나트륨수화물")],
    "레보플록사신": [("100005", "레보플록사신정250밀리그램", "레보플록사신")],
    "펙소페나딘": [("100006", "펙소페나딘염산염정120밀리그램", "펙소페나딘염산염")],
}

# (seq, title, ingr, body) — 상세 fixture. body 가 detector 트리거를 결정.
DETAIL = [
    # 프레드니솔론 → 칼륨 depletion CONFIRMED(저칼륨혈증), 칼슘 absorption 미언급 → reject
    ("100001", "프레드니솔론정5밀리그램", "프레드니솔론",
     "이 약을 장기간 또는 고용량으로 투여하는 경우 전해질 변화로 저칼륨혈증이 나타날 수 있다. "
     "코르티코스테로이드는 칼륨 배설을 증가시킬 수 있으므로 주의한다."),
    # 아세타졸아미드 → 칼륨 depletion CONFIRMED(저칼륨혈증)
    ("100002", "아세타졸아미드정250밀리그램", "아세타졸아미드",
     "탄산탈수효소 억제에 의한 이뇨작용으로 저칼륨혈증 및 대사성 산증이 나타날 수 있어 칼륨 상태를 모니터링한다."),
    # 세파클러 → 철분 absorption 동거어 없음 → REJECT(라벨 미기재). 일반 항생제 문맥만.
    ("100003", "세파클러캡슐250밀리그램", "세파클러",
     "이 약은 그람양성 및 그람음성균에 항균작용을 나타낸다. 위장관계 이상반응으로 설사가 나타날 수 있다."),
    # 레보티록신 → 아연/마그네슘 상호작용 동거어 없음 → REJECT. 일반 갑상선 문맥만.
    ("100004", "신지로이드정0.1밀리그램", "레보티록신나트륨수화물",
     "이 약은 갑상선호르몬 보충요법에 사용한다. 과량 투여 시 빈맥 등이 나타날 수 있다."),
    # 레보플록사신 → antacid Al/Mg directive CONFIRMED(separation_or_spacing) — 단, 라이브 covered → dedup 데모
    ("100005", "레보플록사신정250밀리그램", "레보플록사신",
     "알루미늄 또는 마그네슘을 함유하는 제산제와 병용 시 이 약의 흡수가 감소될 수 있으므로 "
     "이 약 투여 2시간 전후로 투여 간격을 두고 복용한다."),
    # 펙소페나딘 → antacid Al/Mg directive CONFIRMED(미커버 → draft 후보)
    ("100006", "펙소페나딘염산염정120밀리그램", "펙소페나딘염산염",
     "수산화알루미늄 또는 수산화마그네슘을 함유하는 제산제와 동시에 복용하면 이 약의 흡수가 "
     "저하될 수 있으므로 2시간 간격을 두고 투여한다."),
]


def main():
    written = []
    for ing, rows in SEARCH.items():
        path = os.path.join(HERE, f"search_{slug(ing)}_p1.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(search_html(rows))
        written.append(os.path.basename(path))
    for seq, title, ingr, body in DETAIL:
        path = os.path.join(HERE, f"detail_{seq}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(detail_html(seq, title, ingr, body))
        written.append(os.path.basename(path))

    manifest = {
        "note": "SYNTHETIC test doubles for NedrugClient offline mode — NOT real nedrug responses.",
        "purpose": "결정론적 SDK dry-run/test. 실 PM 런은 --online 으로 실응답 fetch/cache.",
        "search_fixtures": {ing: rows for ing, rows in SEARCH.items()},
        "detail_fixtures": {seq: {"title": t, "expected_signal": _signal(seq)} for seq, t, _, _ in DETAIL},
        "files": sorted(written),
    }
    with open(os.path.join(HERE, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"wrote {len(written)} fixtures + MANIFEST.json")


def _signal(seq):
    return {
        "100001": "potassium=confirmed(저칼륨혈증) / calcium=reject(미언급)",
        "100002": "potassium=confirmed(저칼륨혈증)",
        "100003": "iron_absorption=reject(철 동거어 없음)",
        "100004": "zinc=reject, mg_absorption=reject(상호작용 미언급)",
        "100005": "antacid Al/Mg directive=confirmed(separation_or_spacing) — 단 라이브 covered → dedup",
        "100006": "antacid Al/Mg directive=confirmed(미커버 → draft 후보)",
    }[seq]


if __name__ == "__main__":
    main()
