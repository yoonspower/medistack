#!/usr/bin/env python3
"""
collect_full_drug_name_index_sample.py
MediStack v1.0-B Phase 2 — full drug name index 1,000 샘플 수집기.

목적:
  "검색했는데 안 나오는 약" 체감을 줄이기 위한 전체 품목명 인덱스 샘플 생성.
  relation/의학 정보는 확장하지 않는다. relation 없는 약은 name_only("품목명 확인만 가능").

두 트랙:
  relation_card  — 기존 verified relation-covered itemSeq(날조 0, 의학정보 없이 itemSeq/이름만 재사용).
                   covered_by_relation=true · display_mode=relation_card · no_relation_notice_required=false.
  name_only      — nedrug searchDrug 실수집(13 relation 성분·에스오메프라졸·수출·원료·취소 제외).
                   covered_by_relation=false · display_mode=name_only · no_relation_notice_required=true.
                   relation/nutrient/supplement/product/management 필드 일절 없음.

수집 안전:
  - itemSeq/itemName 은 기존 검증 데이터 또는 nedrug 원문에서만(날조 금지).
  - 13 canonical 성분을 포함한 약은 name_only 에서 제외(relation 트랙 대상) → 오연결 방지.
  - 에스오메프라졸/넥시움/forbidden itemSeq 제외.
  - 수집 실패/애매 항목은 제외하고 stats 에 기록.

기존 수집 함수(nedrug_search/parse rows/field/정규식)는 collect_nedrug_alias_candidates 에서 재사용.

사용: python3 scripts/collect_full_drug_name_index_sample.py [--target 1000] [--max-pages 2] [--checked-at YYYY-MM-DD] [--no-network]
출력: data/full_drug_name_index_sample_v1_0.json + .csv
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from collect_nedrug_alias_candidates import (  # noqa: E402  (재사용)
    make_opener, nedrug_search, field, ANCHOR_RE, EXPORT_RE, ESO_HINT_RE, FORBIDDEN_ITEMSEQS,
)

ALIAS_PATH = os.path.join(REPO, "data", "medistack_v0.3_aliases.json")
OUT_JSON = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.json")
OUT_CSV = os.path.join(REPO, "data", "full_drug_name_index_sample_v1_0.csv")

TARGET_TOTAL = 1000
PER_INGREDIENT_CAP = 8
DEFAULT_CHECKED_AT = "2026-06-12"
NAME_ONLY_NOTICE = (
    "이 약은 MediStack의 약-영양소 참고정보 DB에 아직 등록된 항목이 없습니다. "
    "현재는 품목명 확인만 가능합니다. 복용 판단은 약사 또는 의사와 상담하세요."
)

# relation 트랙 13 canonical 성분(name_only 에서 제외 → relation 오연결 방지)
CANONICAL_13 = [
    "독시사이클린", "레보티록신", "레보플록사신", "메트포르민", "목시플록사신",
    "미노사이클린", "시프로플록사신", "알렌드론산", "오메프라졸", "오플록사신",
    "토라세미드", "푸로세미드", "히드로클로로티아지드",
]

# name_only 수집용 다양 성분(13 외, 에스오메프라졸 제외). 검색 다양성(편중 방지) 목적.
DIVERSE_INGREDIENTS = [
    "아세트아미노펜", "이부프로펜", "덱시부프로펜", "나프록센", "아세클로페낙", "디클로페낙",
    "멜록시캄", "셀레콕시브", "록소프로펜", "케토롤락", "트라마돌", "에토돌락",
    "아목시실린", "세파클러", "세푸록심", "세프디니르", "아지트로마이신", "클래리트로마이신",
    "록시트로마이신", "메트로니다졸", "클린다마이신", "세프트리악손", "아시클로비르", "발라시클로비르",
    "플루코나졸", "이트라코나졸", "암로디핀", "텔미사르탄", "발사르탄", "로사르탄",
    "칸데사르탄", "올메사르탄", "이르베사르탄", "비소프롤롤", "카르베딜롤", "네비볼롤",
    "딜티아젬", "라미프릴", "페린도프릴", "클로피도그렐", "실로스타졸", "아스피린",
    "아토르바스타틴", "로수바스타틴", "심바스타틴", "프라바스타틴", "피타바스타틴", "에제티미브",
    "페노피브레이트", "판토프라졸", "란소프라졸", "라베프라졸", "모사프리드", "레바미피드",
    "이토프리드", "돔페리돈", "파모티딘", "글리메피리드", "시타글립틴", "리나글립틴",
    "엠파글리플로진", "다파글리플로진", "글리클라지드", "피오글리타존", "세티리진", "레보세티리진",
    "로라타딘", "펙소페나딘", "베포타스틴", "에바스틴", "몬테루카스트", "암브록솔",
    "아세틸시스테인", "레보드로프로피진", "슈도에페드린", "에스시탈로프람", "설트랄린", "둘록세틴",
    "프레가발린", "가바펜틴", "졸피뎀", "알프라졸람", "라모트리진", "쿠에티아핀",
    "도네페질", "탐스로신", "두타스테리드", "피나스테리드", "솔리페나신", "알로푸리놀",
    "콜키신", "베타히스틴", "실데나필", "타다라필",
]

# v1.0 Phase 4 확장: 검색 "안 나오는 약" 체감 축소용 다양 클래스 상용 경구약 성분.
# 제외 유지(안전): 13 canonical · 에스오메프라졸 · 칼륨/칼륨보존이뇨제 · 와파린 · 비타민/미네랄(relation 얽힘).
DIVERSE_INGREDIENTS_EXT = [
    # 진통·소염·근이완·스테로이드
    "피록시캄", "잘토프로펜", "나부메톤", "펠루비프로펜", "폴마콕시브", "탈니플루메이트",
    "플루르비프로펜", "에페리손", "클로르족사존", "티자니딘", "바클로펜", "데플라자코트",
    "프레드니솔론", "메틸프레드니솔론", "덱사메타손", "트리암시놀론",
    # 항생제(13 canonical 제외)
    "세팔렉신", "세프포독심", "세프카펜피복실", "세프디토렌", "암피실린", "술타미실린",
    "세프록사딘", "세픽심", "플로목세프", "노르플록사신", "세프라딘", "반코마이신",
    "테이코플라닌", "리네졸리드", "포스포마이신", "니트로푸란토인", "테트라사이클린",
    "에리트로마이신", "트리메토프림", "세프타지딤", "클로람페니콜",
    # 항진균·항바이러스
    "테르비나핀", "케토코나졸", "보리코나졸", "그리세오풀빈", "미코나졸", "클로트리마졸",
    "팜시클로버", "오셀타미비르", "엔테카비르", "테노포비르",
    # 심혈관(칼륨/칼륨보존이뇨제·와파린 제외)
    "니페디핀", "펠로디핀", "레르카니디핀", "실니디핀", "바르니디핀", "에날라프릴",
    "리시노프릴", "포시노프릴", "이미다프릴", "아테놀롤", "메토프롤롤", "프로프라놀롤",
    "라베탈롤", "아질사르탄", "피마사르탄", "니카르디핀", "트리메타지딘", "이바브라딘",
    "라놀라진", "니코란딜", "몰시도민", "이소소르비드", "인다파미드", "클로르탈리돈",
    "콜레스티라민", "베자피브레이트", "겜피브로질",
    # 당뇨(메트포르민 제외)
    "보글리보스", "아카보스", "미글리톨", "알로글립틴", "제미글립틴", "테네리글립틴",
    "에보글립틴", "빌다글립틴", "삭사글립틴", "카나글리플로진", "이프라글리플로진",
    "레파글리니드", "나테글리니드", "글리벤클라미드", "글리피지드",
    # 갑상선(레보티록신 제외)
    "메티마졸", "프로필티오우라실",
    # 소화기(에스오메프라졸·오메프라졸 제외)
    "데노프라졸", "일라프라졸", "테고프라잔", "보노프라잔", "알마게이트", "마그알드레이트",
    "수크랄페이트", "트리메부틴", "시메티딘", "니자티딘", "라푸티딘", "로페라미드",
    "디오스멕타이트", "리팍시민", "메베베린", "시메티콘", "우르소데옥시콜산",
    "비페닐디메칠디카르복실레이트", "락툴로오스", "비사코딜", "온단세트론", "메토클로프라미드",
    # 알레르기·항히스타민
    "데슬로라타딘", "빌라스틴", "루파타딘", "올로파타딘", "케토티펜", "클로르페니라민",
    "하이드록시진", "프란루카스트", "자피르루카스트",
    # 호흡기
    "카르보시스테인", "브롬헥신", "구아이페네신", "덱스트로메토르판", "테오필린", "독소필린",
    "밤부테롤", "살부타몰", "포르모테롤", "살메테롤", "인다카테롤", "부데소니드",
    # 정신·신경
    "시탈로프람", "파록세틴", "플루옥세틴", "플루복사민", "벤라팍신", "데스벤라팍신",
    "보티옥세틴", "미르타자핀", "부프로피온", "아미트리프틸린", "노르트립틸린", "이미프라민",
    "트라조돈", "아고멜라틴", "발프로산", "토피라메이트", "레베티라세탐", "옥스카르바제핀",
    "카르바마제핀", "페니토인", "라코사미드", "클로나제팜", "디아제팜", "로라제팜",
    "에티졸람", "부스피론", "리스페리돈", "올란자핀", "아리피프라졸", "팔리페리돈",
    "아미설프리드", "할로페리돌", "멜라토닌", "라멜테온", "트리아졸람", "조피클론",
    # 비뇨·전립선
    "실로도신", "알푸조신", "테라조신", "독사조신", "나프토피딜", "미라베그론", "톨테로딘",
    "페소테로딘", "트로스피움", "옥시부티닌", "프로피베린", "데스모프레신",
    # 통풍·골대사(알렌드론산 제외)
    "페북소스타트", "벤즈브로마론", "리세드론산", "이반드론산", "랄록시펜", "바제독시펜",
    # 인지·치매
    "콜린알포세레이트", "니세르골린", "옥시라세탐", "시티콜린", "메만틴", "리바스티그민", "갈란타민",
    # 항혈전(와파린 제외)
    "리바록사반", "아픽사반", "다비가트란", "에독사반", "티카그렐러", "프라수그렐",
    "사르포그렐레이트", "베라프로스트", "트리플루살",
    # 안과(점안 — 품목명 확인용)
    "라타노프로스트", "브리모니딘", "도르졸아미드", "브린졸아미드", "티몰롤", "트라보프로스트", "비마토프로스트",
    # 기타
    "디멘히드리네이트", "메클리진", "레보카르니틴", "은행엽엑스",
]

# v1.0 Phase 5 확장(5,500 → 10,000): 성분 풀 309 → ~500. 미수록 치료군 상용 성분 보강
# (외용·점안·이비인후/흡입·구강/인후·국소마취·진해거담·소화효소·추가 항생/항결핵/항바이러스·
#  파킨슨·정신·비뇨/부인과·항부정맥·PAH·면역조절·금연/중독·PDE5). 검색 커버리지 확장 목적.
# 제외 유지(안전·Phase 4 동일): 13 canonical · 에스오메프라졸 · 칼륨/칼륨보존이뇨제 ·
# 와파린 · 비타민/미네랄(relation 얽힘). name_only 순도는 검증기가 강제(의학/제품 필드 0).
DIVERSE_INGREDIENTS_EXT2 = [
    # 피부 외용·여드름·건선·습진·항진균 외용
    "부펙사막", "아젤라산", "아다팔렌", "트레티노인", "이소트레티노인", "벤조일퍼옥사이드",
    "무피로신", "푸시드산", "베타메타손", "클로베타솔", "모메타손", "데소나이드", "칼시포트리올",
    "타크로리무스", "피메크로리무스", "이미퀴모드", "살리실산", "시클로피록스", "아모롤핀",
    "부테나핀", "에코나졸", "비포나졸",
    # 점안·안과
    "사이클로스포린", "디쿠아포솔", "플루오로메톨론", "가티플록사신", "토브라마이신", "겐타마이신",
    "네오마이신", "브롬페낙", "네파페낙", "로테프레드놀", "트로피카미드", "아트로핀",
    # 이비인후·비염·흡입
    "베클로메타손", "시클레소니드", "아젤라스틴", "레보카바스틴", "옥시메타졸린", "자일로메타졸린",
    "이프라트로피움", "티오트로피움", "글리코피로늄", "아클리디늄", "우메클리디늄", "크로모글리크산",
    # 구강·인후·국소마취
    "벤지다민", "클로르헥시딘", "포비돈요오드", "세틸피리디늄", "폴리크레줄렌", "티로트리신",
    "벤조카인", "리도카인", "프릴로카인", "테트라카인", "프로카인", "구아이아줄렌", "염화리소짐",
    # 진해·거담·기관지확장·소염효소
    "에르도스테인", "아세브로필린", "소브레롤", "펜톡시베린", "클로페라스틴", "디메모르판",
    "티페피딘", "노스카핀", "벤프로페린", "프로카테롤", "클렌부테롤", "툴로부테롤",
    "세라티오펩티다제", "브로멜라인",
    # 소화효소·완하·진경·점막·IBD
    "판크레아틴", "디메티콘", "비오디아스타제", "옥세타카인", "마크로골", "도큐세이트",
    "센노사이드", "피코설페이트", "라모세트론", "아클라토늄", "폴리카르보필", "메살라진",
    "설파살라진", "발살라지드", "아데메티오닌",
    # 추가 항생·항결핵·항바이러스
    "세프티부텐", "세프프로질", "미데카마이신", "에탐부톨", "이소니아지드", "리팜핀",
    "피라진아미드", "펜시클로버", "답토마이신", "콜리스틴", "날리딕스산", "아즈트레오남",
    # 파킨슨·뇌신경·항전간
    "프라미펙솔", "로피니롤", "로티고틴", "레보도파", "엔타카폰", "셀레길린", "라사길린",
    "아만타딘", "프로사이클리딘", "벤즈트로핀", "페람파넬", "조니사미드", "비가바트린", "에토숙시미드",
    # 정신과 추가
    "설피리드", "레보설피리드", "밀나시프란", "모클로베미드", "클로르프로마진", "페르페나진",
    "조테핀", "클로자핀", "지프라시돈", "블로난세린", "루라시돈", "아세나핀",
    # 비뇨·부인과·내분비
    "비베그론", "다리페나신", "이미다페나신", "플라복세이트", "클로미펜", "레트로졸",
    "아나스트로졸", "타목시펜", "다이드로게스테론", "메드록시프로게스테론", "디에노게스트", "시나칼세트",
    # 항부정맥·항고혈압 추가·PAH
    "메틸도파", "클로니딘", "히드랄라진", "미녹시딜", "디곡신", "아미오다론", "드로네다론",
    "플레카이니드", "프로파페논", "멕실레틴", "소타롤", "보센탄", "암브리센탄", "마시텐탄", "리오시구앗",
    # 항히스타민·면역조절·금연/중독·PDE5·기타
    "클레마스틴", "메퀴타진", "에피나스틴", "아자티오프린", "미코페놀산", "레플루노미드",
    "메토트렉세이트", "하이드록시클로로퀸", "토파시티닙", "바리시티닙", "우파다시티닙", "아프레밀라스트",
    "날록손", "날트렉손", "아캄프로세이트", "바레니클린", "우데나필", "미로데나필", "아바나필",
    "신나리진", "플루나리진", "실리마린", "콜레스티미드",
]
# 중복 제거(순서 보존). ext2(신규 niche) 우선 → 기존(base+ext) 보강.
# 신규 성분을 앞에 둬 미수록 약 우선 충당(다양성·균형) + 기존 깊은 페이지로 잔여 보강.
DIVERSE_INGREDIENTS = list(dict.fromkeys(DIVERSE_INGREDIENTS_EXT2 + DIVERSE_INGREDIENTS + DIVERSE_INGREDIENTS_EXT))


def norm_name(s):
    return " ".join(unicodedata.normalize("NFC", str(s or "")).split()).strip().lower()


def contains_13(ingr):
    n = ingr or ""
    return any(c in n for c in CANONICAL_13)


def parse_full(html_text):
    """searchDrug HTML → [{item_seq, item_name, ingr_name, finished, status_cancel, company}]."""
    out = []
    for chunk in re.split(r"<tr[ >]", html_text):
        if "getItemDetail?itemSeq=" not in chunk:
            continue
        m = ANCHOR_RE.search(chunk)
        if not m:
            continue
        out.append({
            "item_seq": m.group(1),
            "item_name": html.unescape(m.group(2)).strip(),
            "ingr_name": field(chunk, "주성분"),
            "finished": field(chunk, "완제/원료구분"),
            "status_cancel": field(chunk, "취소/취하구분"),
            "company": field(chunk, "업체명"),
        })
    return out


def build_relation_card_seed(checked_at):
    a = json.load(open(ALIAS_PATH, encoding="utf-8"))
    seed = {}  # item_seq -> {item_name, ingredient_name, source_checked_at}
    for ing, lst in (a.get("verified_item_seqs") or {}).items():
        for e in (lst or []):
            s = str(e.get("item_seq") or "").strip()
            nm = (e.get("item_name") or "").strip()
            if s and nm and s not in seed:
                seed[s] = {"item_name": nm, "ingredient_name": ing,
                           "source_checked_at": e.get("verified_at") or checked_at}
    for p in (a.get("product_aliases") or []):
        s = str(p.get("item_seq") or "").strip()
        nm = (p.get("alias") or "").strip()
        if s and nm and s not in seed:
            seed[s] = {"item_name": nm, "ingredient_name": p.get("canonical_ingredient", ""),
                       "source_checked_at": checked_at}
    entries = []
    for s, e in seed.items():
        entries.append({
            "item_seq": s,
            "item_name": e["item_name"],
            "normalized_item_name": norm_name(e["item_name"]),
            "ingredient_name": e["ingredient_name"],
            "company_name": None,
            "covered_by_relation": True,
            "display_mode": "relation_card",
            "no_relation_notice_required": False,
            "source": "MFDS nedrug",
            "source_method": "internal.medistack_v0_3_aliases",
            "source_checked_at": e["source_checked_at"],
        })
    return entries, set(seed.keys())


def load_existing_entries(path):
    """Phase 4 augment: 기존 출력의 entries 를 그대로 보존(원본 itemSeq/이름/날짜 불변)."""
    if not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    ents = d.get("entries")
    if not isinstance(ents, list):
        return None
    return [e for e in ents if isinstance(e, dict)]


def collect_name_only(pre_seen, pool_seqs, cap, per_cap, checked_at, max_pages, timeout, sleep):
    op = make_opener()
    out, seen = [], set(pre_seen) | set(pool_seqs)
    st = {"ingredients_searched": 0, "ing_fail": 0, "rows_seen": 0,
          "excl_export": 0, "excl_raw": 0, "excl_cancel": 0, "excl_eso": 0,
          "excl_13": 0, "excl_dup": 0, "excl_pool": 0, "kept": 0, "fails": []}
    for ing in DIVERSE_INGREDIENTS:
        if len(out) >= cap:
            break
        st["ingredients_searched"] += 1
        got = 0
        for page in range(1, max_pages + 1):
            if len(out) >= cap or got >= per_cap:
                break
            try:
                html_text, _ = nedrug_search(op, ing, page=page, timeout=timeout)
            except Exception as e:
                st["ing_fail"] += 1
                st["fails"].append(f"{ing} p{page}: {type(e).__name__}")
                break
            time.sleep(sleep)
            for r in parse_full(html_text):
                if len(out) >= cap or got >= per_cap:
                    break
                st["rows_seen"] += 1
                seq, name, ingr = str(r["item_seq"]).strip(), r["item_name"].strip(), (r["ingr_name"] or "").strip()
                if not seq or not name:
                    continue
                if EXPORT_RE.search(name):
                    st["excl_export"] += 1; continue
                if "원료" in (r["finished"] or ""):
                    st["excl_raw"] += 1; continue
                if (r["status_cancel"] or "") != "정상":
                    st["excl_cancel"] += 1; continue
                if ESO_HINT_RE.search(name) or ESO_HINT_RE.search(ingr) or seq in FORBIDDEN_ITEMSEQS:
                    st["excl_eso"] += 1; continue
                if seq in seen:
                    st["excl_pool" if seq in pool_seqs else "excl_dup"] += 1; continue
                if contains_13(ingr):
                    st["excl_13"] += 1; continue
                seen.add(seq); got += 1; st["kept"] += 1
                comp = (r.get("company") or "").strip() or None
                out.append({
                    "item_seq": seq,
                    "item_name": name,
                    "normalized_item_name": norm_name(name),
                    "ingredient_name": ingr,
                    "company_name": comp,
                    "covered_by_relation": False,
                    "display_mode": "name_only",
                    "no_relation_notice_required": True,
                    "source": "MFDS nedrug",
                    "source_method": "nedrug.searchDrug",
                    "source_checked_at": checked_at,
                })
    return out, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=TARGET_TOTAL)
    ap.add_argument("--max-pages", type=int, default=2)
    ap.add_argument("--checked-at", default=DEFAULT_CHECKED_AT)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--sleep", type=float, default=0.15)
    ap.add_argument("--per-cap", type=int, default=PER_INGREDIENT_CAP, help="성분별 name_only 상한(편중 방지)")
    ap.add_argument("--no-network", action="store_true", help="relation_card seed 만(name_only 수집 생략)")
    ap.add_argument("--augment", action="store_true",
                    help="기존 출력을 seed로 보존하고 신규 name_only만 추가(Phase 4 확장)")
    args = ap.parse_args()

    rc_seed, pool = build_relation_card_seed(args.checked_at)

    if args.augment:
        existing = load_existing_entries(OUT_JSON)
        if not existing:
            print("[augment] 기존 출력 없음 — 일반 모드로 실행하세요(--augment 제거).", file=sys.stderr)
            return 1
        rc = [e for e in existing if e.get("display_mode") == "relation_card"]
        base_no = [e for e in existing if e.get("display_mode") == "name_only"]
        existing_seqs = {str(e.get("item_seq") or "").strip() for e in existing}
        print(f"[augment] 기존 {len(existing)} 보존 (relation_card {len(rc)} + name_only {len(base_no)})")
        name_cap = max(0, args.target - len(existing))
        if args.no_network:
            new_no, st = [], {"note": "no-network: name_only 신규 수집 생략"}
        else:
            print(f"[name_only] 신규 수집 (cap {name_cap}, per-cap {args.per_cap}, max-pages {args.max_pages}, {len(DIVERSE_INGREDIENTS)} 성분)")
            new_no, st = collect_name_only(existing_seqs, pool, name_cap, args.per_cap,
                                           args.checked_at, args.max_pages, args.timeout, args.sleep)
            print(f"[name_only] 신규 {len(new_no)} 추가 / cap {name_cap} (rows {st.get('rows_seen')})")
        st["augment"] = {"existing": len(existing), "base_name_only": len(base_no), "new_name_only": len(new_no)}
        no = base_no + new_no
        entries = rc + no
    else:
        rc = rc_seed
        print(f"[seed] relation_card(covered_by_relation=true) = {len(rc)}  (relation-covered pool itemSeqs)")
        name_cap = max(0, args.target - len(rc))
        if args.no_network:
            no, st = [], {"note": "no-network: name_only 수집 생략"}
            print("[name_only] --no-network → 생략")
        else:
            print(f"[name_only] 수집 시작 (cap {name_cap}, per-cap {args.per_cap}, max-pages {args.max_pages}, {len(DIVERSE_INGREDIENTS)} 성분)")
            no, st = collect_name_only(set(), pool, name_cap, args.per_cap,
                                       args.checked_at, args.max_pages, args.timeout, args.sleep)
            print(f"[name_only] kept {len(no)} / cap {name_cap}  (ingredients {st['ingredients_searched']}, rows {st['rows_seen']})")
        entries = rc + no
    meta = {
        "name": "full_drug_name_index_sample_v1_0",
        "schema_version": "1.0",
        "purpose": "검색 커버리지 확장용 전체 품목명 인덱스(v1.0-B 설계 · Phase 2 1,000 → Phase 4 확장). relation/alias 와 분리. name_only 는 '품목명 확인만 가능'. 앱 배선됨(Phase 3 name_only UX).",
        "source_basis": "MFDS nedrug (식약처 의약품통합정보)",
        "generated_checked_at": args.checked_at,
        "target_total": args.target,
        "counts": {
            "total": len(entries),
            "relation_card": len(rc),
            "name_only": len(no),
        },
        "name_only_notice": NAME_ONLY_NOTICE,
        "note": "relation_card=기존 verified relation-covered itemSeq(의학정보 없이 itemSeq/이름만). name_only=relation 미연결(13성분·에스오메·수출·원료·취소 제외). 의학적 판단/상호작용/영양소 정보 없음.",
        "collection_stats": st,
    }
    doc = {"meta": meta, "entries": entries}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    csv_fields = ["item_seq", "item_name", "normalized_item_name", "ingredient_name",
                  "company_name", "covered_by_relation", "display_mode",
                  "no_relation_notice_required", "source", "source_method", "source_checked_at"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        w.writeheader()
        for e in entries:
            w.writerow(e)

    print(f"[out] {OUT_JSON}  total={len(entries)} (relation_card {len(rc)} + name_only {len(no)})")
    print("[stats] " + json.dumps(st, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
