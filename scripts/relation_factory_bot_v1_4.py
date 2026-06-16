#!/usr/bin/env python3
"""
relation_factory_bot_v1_4.py
MediStack Relation Factory Bot v1.4 — 1,000 relation scale-up 을 위한 **대량 후보 공장**(manual tool).

파이프라인(기본 offline·안전): inventory load → family universe → candidate 대량 생성(중복 차단) →
precheck 분류(P0/P1/P2/HOLD/REJECT_PRECHECK) → source-check queue. 선택(`--online-source-check`):
SDK-only 라벨 source-check(직접근거 verbatim quote 만 인정·fail-closed) → source_confirmed_draft batch +
PM review queue.

🔒 절대 불변: live export/full index/aliases/src/.github **무수정** · live relation 추가 **0** · schedule **무관** ·
산출물은 data/review/ 와 data/drafts/ 만. 제품/구매/제휴 UI 0 · 보충 권유 0 · 계열 일반화로 **draft 생성 금지**
(draft 는 SDK 직접근거 verbatim 가 있는 것만). reject/hold/no_domestic 은 재후보화 금지(inventory ledger).

CLI:
  python3 scripts/relation_factory_bot_v1_4.py                       # offline: universe+candidates+precheck+queue emit
  python3 scripts/relation_factory_bot_v1_4.py --emit-universe       # family universe 문서/JSON 만 갱신
  python3 scripts/relation_factory_bot_v1_4.py --online-source-check --max-source-check 120   # P0부터 SDK source-check + draft/PM
  옵션: --p0-only · --families F1,F2 · --max-source-check N
출력만 / live write 0 / export write 0 / src write 0 / no auto integrate.
"""
import argparse
import csv
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data")
REVIEW = os.path.join(DATA, "review")
DRAFTS = os.path.join(DATA, "drafts")
DOCS = os.path.join(REPO, "docs")
INVENTORY = os.path.join(REVIEW, "relation_factory_inventory_v1_4.json")

# 출력 경로 (data/review · data/drafts · docs 만)
OUT_UNIVERSE_JSON = os.path.join(REVIEW, "relation_family_universe_v1_4.json")
OUT_UNIVERSE_MD = os.path.join(DOCS, "MediStack_relation_family_universe_v1_4.md")
OUT_CAND_JSON = os.path.join(REVIEW, "relation_factory_candidates_v1_4.json")
OUT_CAND_CSV = os.path.join(REVIEW, "relation_factory_candidates_v1_4.csv")
OUT_CAND_MD = os.path.join(DOCS, "MediStack_relation_factory_candidates_v1_4.md")
OUT_QUEUE = os.path.join(REVIEW, "relation_factory_source_check_queue_v1_4.json")
OUT_PRECHECK = os.path.join(REVIEW, "relation_factory_precheck_summary_v1_4.json")
OUT_SC_JSON = os.path.join(REVIEW, "relation_factory_source_check_results_v1_4.json")
OUT_SC_CSV = os.path.join(REVIEW, "relation_factory_source_check_results_v1_4.csv")
OUT_DRAFT = os.path.join(DRAFTS, "relation_factory_draft_batch_v1_4.json")
OUT_PM_JSON = os.path.join(REVIEW, "relation_factory_pm_review_queue_v1_4.json")
OUT_PM_MD = os.path.join(REVIEW, "relation_factory_pm_review_queue_v1_4.md")


def _load_mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_invmod = _load_mod("invmod", "build_relation_factory_inventory_v1_4.py")
canon_drug = _invmod.canon_drug
canon_counterpart = _invmod.canon_counterpart
inv_key = _invmod.key

# ───────────────────────── counterpart 사양 ─────────────────────────
# canon → (표시명, type, counterpart_category, mechanism, action, detector, evidence_default)
COUNTERPARTS = {
    "fe": ("철분", "nutrient", None, "absorption", "separation", "mineral_fe", "moderate"),
    "ca": ("칼슘", "nutrient", None, "absorption", "separation", "mineral_ca", "moderate"),
    "mg": ("마그네슘", "nutrient", None, "absorption", "separation", "mineral_mg", "moderate"),
    "zn": ("아연", "nutrient", None, "absorption", "separation", "mineral_zn", "moderate"),
    "al_mg_antacid": ("Al/Mg 함유 제산제(약물)", "drug", "al_mg_antacid", "absorption",
                      "separation", "antacid", "moderate"),
    "folate": ("엽산", "nutrient", None, "depletion", "monitoring", "folate", "moderate"),
    "vitd": ("비타민D", "nutrient", None, "depletion", "monitoring", "vitd", "moderate"),
    "b12": ("비타민B12", "nutrient", None, "depletion", "monitoring", "b12", "moderate"),
    "b6": ("비타민B6", "nutrient", None, "depletion", "monitoring", "b6", "moderate"),
    "fatsol_vit": ("지용성 비타민(A·D·E·K)", "nutrient_group", None, "absorption",
                   "separation", "fatsol", "moderate"),
    "k": ("칼륨", "nutrient", None, "depletion", "monitoring", "k_depletion", "moderate"),
    "na": ("나트륨", "electrolyte", None, "depletion", "monitoring", "na_depletion", "moderate"),
}

# ───────────────────────── family universe ─────────────────────────
# 각 family: drugs(완전 목록·live 포함 — dedup 가 분리), counterparts(canon), risk_class,
#            priority_default, source_check, notes. 계열 일반화는 source-check 후보 생성에만.
FAMILY_UNIVERSE = [
    {"id": "F1", "name": "Fluoroquinolone × metal cation (absorption/separation)",
     "drugs": ["시프로플록사신", "레보플록사신", "목시플록사신", "오플록사신", "노르플록사신",
               "페플록사신", "로메플록사신", "발로플록사신", "자보플록사신", "프룰리플록사신",
               "게미플록사신", "스파르플록사신", "가티플록사신", "토수플록사신", "플루메퀸",
               "에녹사신", "플레록사신", "루플록사신", "가레녹사신", "시노플록사신"],
     "counterparts": ["fe", "ca", "mg", "zn", "al_mg_antacid"],
     "risk_class": "known_safe", "priority_default": "P0", "source_check": True,
     "notes": "퀴놀론 다가 양이온 킬레이트 — 라벨에 '2시간 전후/간격' 명시 흔함. live 다수 존재→dedup 분리."},
    {"id": "F2", "name": "Tetracycline × metal cation (absorption/separation)",
     "drugs": ["독시사이클린", "미노사이클린", "테트라사이클린", "옥시테트라사이클린",
               "데메클로사이클린", "메타사이클린", "티게사이클린"],
     "counterparts": ["fe", "ca", "mg", "zn", "al_mg_antacid"],
     "risk_class": "known_safe", "priority_default": "P0", "source_check": True,
     "notes": "테트라사이클린계 양이온 킬레이트. 티게사이클린=주사(경구 완제 없음 가능)."},
    {"id": "F3", "name": "Bisphosphonate × mineral (absorption/separation)",
     "drugs": ["알렌드론산", "리세드론산", "이반드론산", "에티드론산", "클로드론산",
               "파미드론산", "졸레드론산", "미노드론산", "인카드론산"],
     "counterparts": ["ca", "fe", "mg", "al_mg_antacid"],
     "risk_class": "known_safe", "priority_default": "P1", "source_check": True,
     "notes": "다가 양이온·칼슘 함유 식품/제산제가 흡수 저하 → 기상 직후 물. 주사제(파미/졸레)=경구 없음."},
    {"id": "F4", "name": "Thyroid hormone × mineral/antacid (absorption)",
     "drugs": ["레보티록신", "리오티로닌"],
     "counterparts": ["mg", "al_mg_antacid"],
     "risk_class": "known_safe", "priority_default": "P1", "source_check": True,
     "notes": "Fe·Ca 는 이미 live. Mg/제산제 흡수 영향은 라벨 직접근거 확인 필요."},
    {"id": "F5", "name": "Iron-chelator / chelation (non-penicillamine)",
     "drugs": ["트리엔틴", "데페라시록스", "데페리프론", "데페록사민"],
     "counterparts": ["fe", "zn", "ca"],
     "risk_class": "high_risk", "priority_default": "HOLD", "source_check": False,
     "notes": "철 과부하 치료제 — 미네랄 상호작용이 치료 목적과 얽힘. reviewer 전 hold(보충 권유 오인 위험)."},
    {"id": "F6", "name": "Acid-reducer (H2/PPI) × Fe/B12/antacid",
     "drugs": ["파모티딘", "시메티딘", "니자티딘", "라푸티딘", "록사티딘",
               "오메프라졸", "에스오메프라졸", "란소프라졸", "판토프라졸", "라베프라졸"],
     "counterparts": ["fe", "b12"],
     "risk_class": "monitoring", "priority_default": "P1", "source_check": True,
     "notes": "만성 위산 감소 → Fe/B12 흡수 영향(라벨 직접근거 약할 수 있음). 산분비억제제 자신은 pH-흡수의존 아님→antacid counterpart 제외. PPI×Mg/B12 다수 live→dedup."},
    {"id": "F7", "name": "Bile-acid sequestrant × fat-soluble vitamin/folate",
     "drugs": ["콜레세벨람", "콜레스티폴"],
     "counterparts": ["fatsol_vit", "folate"],
     "risk_class": "known_safe", "priority_default": "P1", "source_check": True,
     "notes": "콜레스티라민·오르리스타트는 theme map pending. 콜레세벨람은 결합 선택성↑로 미기재 가능."},
    {"id": "F8", "name": "Electrolyte monitoring (diuretic/steroid/laxative) × K/Mg/Na",
     "drugs": ["아세타졸아미드", "아조세미드", "부메타니드", "에타크린산", "스피로노락톤",
               "덱사메타손", "베타메타손", "센나", "비사코딜", "수산화마그네슘"],
     "counterparts": ["k", "mg", "na"],
     "risk_class": "mixed", "priority_default": "P2", "source_check": False,
     "notes": "loop/탄산탈수효소억제=depletion 가능. K-sparing(스피로노락톤)=상승 방향→depletion 금지(REJECT)."},
    {"id": "F9", "name": "Chronic-use depletion (antiepileptic/sulfasalazine/MTX) × folate/vitD",
     "drugs": ["페니토인", "카르바마제핀", "발프로산", "페노바르비탈", "프리미돈",
               "옥스카르바제핀", "라모트리진", "토피라메이트", "조니사미드",
               "설파살라진", "트리메토프림"],
     "counterparts": ["folate", "vitd", "b12"],
     "risk_class": "mixed", "priority_default": "P2", "source_check": True,
     "notes": "항전간제(효소유도) 만성투여=엽산/비타민D 저하 라벨 가능. MTX/피리메타민=항엽산·종양/면역 고위험→F11 HOLD(여기 제외)."},
    {"id": "F10", "name": "Azole antifungal × antacid (pH-dependent absorption)",
     "drugs": ["케토코나졸", "포사코나졸", "이트라코나졸"],
     "counterparts": ["al_mg_antacid"],
     "risk_class": "known_safe", "priority_default": "P1", "source_check": True,
     "notes": "이트라코나졸×Al/Mg 제산제는 live(id61). 케토/포사코나졸은 라벨 직접근거 확인."},
    {"id": "F11", "name": "Exclusion / high-risk ledger (REJECT_PRECHECK / HOLD)",
     "drugs": ["와파린", "사이클로스포린", "타크로리무스", "메토트렉세이트", "피리메타민",
               "레날리도마이드", "이소니아지드", "레보도파"],
     "counterparts": ["folate", "b6", "k"],
     "risk_class": "high_risk", "priority_default": "HOLD", "source_check": False,
     "notes": "warfarin×vitK(antagonism)·이식/면역억제·항암·임신·정신과 고위험. reviewer 전 제외(계열 일반화 금지)."},
]

EXPECTED_SECTIONS = ["약물상호작용", "상호작용", "병용금기", "병용주의", "병용투여", "일반적 주의",
                     "사용상의 주의", "주의사항"]


# ───────────────────────── source-check detectors (SDK·verbatim) ─────────────────────────
MINERAL_PATS = {
    "fe": r"철분|철제제|철\s*함유|황산철|구연산.{0,4}철|경구\s*철|철염|철ㆍ?아연|철·아연",
    "ca": r"칼슘",
    "mg": r"마그네슘",
    "zn": r"아연",
}
DIRECTIONAL = (r"흡수.{0,16}(저하|감소|저해|방해|억제)|(저하|감소|저해|방해|억제).{0,16}흡수|흡수율|"
               r"효과.{0,12}(저하|감소)|생체이용률.{0,12}(저하|감소)|동시\s*투여를?\s*피|병용을?\s*피|"
               r"복용\s*간격|투여\s*간격|간격을\s*두|\d+\s*시간\s*(간격|전후|이상|이내|이후)|"
               r"킬레이트|복합체|착화합물")
ANTACID_CTX = r"제산제|수산화마그네슘|수산화알루미늄"
# 영양소(supplement) 맥락 — 미네랄 nutrient relation 인정 요건. 제산제 맥락이면 영양제 아님.
SUPP_CTX = (r"함유\s*(한|된|하는|하고)?\s*제제|함유\s*제제|보충제|종합비타민|비타민제|미네랄이?\s*첨가|"
            r"제제와|제제,|제제\s*및|보충")
ANTACID_NEAR = r"함유.{0,3}제산제|함유하는\s*제산제|수산화(마그네슘|알루미늄)|또는\s*마그네슘\s*함유"
# 상호작용 부정(흡수 영향 없음) — false positive 차단
NEGATION = (r"흡수.{0,10}(영향을?\s*(받지|주지)|저해되지|감소되지|영향이?\s*없)\s*않|"
            r"영향을?\s*(받지|주지|미치지)\s*않|영향이?\s*없|관련(성|이)?\s*없")
# 흡수상호작용이 아닌 맥락(뼈/치아 복합체·보충 권유·결핍 치료) — 미네랄 nutrient 오인 차단
NON_INTERACTION_CTX = (r"골형성|치아|착색|법랑질|뼈에|골에|골의|복합체를?\s*형성|"
                       r"섭취하도록|충분히\s*(칼슘|미네랄)|보충해야|섭취해야|결핍(을|이)?\s*(치료|보충)")


def _snip(text, i, pad=120):
    """match 주변을 **항목 번호/문장 경계**로 잘라 인접 무관 문장(예: 와파린 절) 혼입 방지."""
    lo = max(0, i - pad)
    mk = list(re.finditer(r"(?:\d\)|[-•])\s|다\.\s", text[lo:i]))  # 앞쪽 가장 가까운 항목/문장 경계
    if mk:
        lo = lo + mk[-1].end()
    hi = i + pad
    tail = re.search(r"다\.\s|\d\)\s|[-•]\s", text[i:hi + 50])     # 다음 항목/문장 끝
    if tail:
        hi = i + tail.start() + (2 if tail.group().startswith("다") else 0)
    return re.sub(r"\s+", " ", text[lo:hi]).strip()


def _section_at(text, i):
    best = ""
    for sec in EXPECTED_SECTIONS:
        j = text.rfind(sec, 0, i)
        if j != -1 and (best == "" or j > best[1]):
            best = (sec, j)
    return best[0] if best else "상호작용/주의"


def detect_mineral(text, canon):
    """미네랄(Fe/Ca/Mg/Zn) **영양소 supplement** 흡수 상호작용 — verbatim quote.
    nutrient 인정 요건: ①흡수저하/시점분리 방향성 + ②supplement 맥락('함유 제제'·종합비타민·미네랄제) +
    제외: ③부정문(흡수 영향 없음) ④제산제 맥락(Mg/Al antacid 오인 금지) ⑤뼈/치아 복합체·보충 권유·결핍 치료."""
    # Mg-nutrient 는 absorption 라벨에서 'Mg 함유 제산제'(antacid) 와 구분이 어려움 → auto 확정 제외
    # (antacid 는 al_mg_antacid counterpart 가 별도 처리). Mg nutrient 신규는 reviewer 수동.
    if canon == "mg":
        return False, "", ""
    pat = MINERAL_PATS.get(canon)
    if not pat:
        return False, "", ""
    for m in re.finditer(pat, text):
        i = m.start()
        w = text[max(0, i - 110):i + 130]
        suffix = text[i:i + 28]                 # 이 미네랄 직후 — 제산제 양이온 vs supplement 판별
        pre = text[max(0, i - 30):i]            # 직전 — '미네랄 첨가 비타민제' 등 supplement 맥락
        if not re.search(DIRECTIONAL, w):
            continue
        if re.search(NEGATION, w):              # 흡수 영향 없음 = 상호작용 아님
            continue
        if re.search(NON_INTERACTION_CTX, w):   # 뼈/치아 복합체·보충권유·결핍치료
            continue
        # 이 미네랄이 '…함유 제산제'의 양이온이면 antacid 트랙(nutrient 아님).
        antacid_self = re.search(r"함유.{0,6}제산제|함유하는\s*제산제|함유된\s*제산제", suffix)
        # supplement 명시: '{mineral} 함유 제제'·'…함유된 종합비타민제제' 또는 직전 '비타민제/미네랄 첨가/보충제'
        supp_self = (re.search(r"함유\s*(한|된|하고\s*있는)?\s*제제|함유된\s*종합비타민|종합비타민제제", suffix)
                     or re.search(r"비타민제|미네랄이?\s*첨가|보충제", pre))
        if antacid_self and not supp_self:      # 제산제 양이온
            continue
        if not supp_self:                       # nutrient 인정엔 supplement 명시 필요(보수적)
            continue
        return True, _snip(text, i), _section_at(text, i)
    return False, "", ""


def detect_antacid(text):
    for m in re.finditer(ANTACID_CTX + r"|H2\s*수용체|위산\s*분비\s*억제|산\s*분비", text):
        i = m.start()
        w = text[max(0, i - 110):i + 130]
        if re.search(NEGATION, w):  # '제산제와 병용으로 흡수가 저해되지 않는다' 등 부정 차단
            continue
        # 이 약 자신의 흡수가 영향받아야(다른 약 케토코나졸/이트라코나졸이 주어면 방향 오류)
        if re.search(r"(케토코나졸|이트라코나졸|아졸|딕|항진균제).{0,20}흡수", w) \
                and not re.search(r"이\s*약.{0,16}흡수", w):
            continue
        if re.search(r"흡수.{0,16}(저하|감소|저해|방해|지연)|생체이용률.{0,12}(저하|감소)|병용.{0,8}(피|주의)|"
                     r"동시\s*투여|간격|복용하지\s*마|위산.{0,8}(필요|의존)", w):
            return True, _snip(text, i), _section_at(text, i)
    return False, "", ""


def detect_generic(text, kw_pat, dir_pat=None):
    dpat = dir_pat or DIRECTIONAL
    for m in re.finditer(kw_pat, text):
        i = m.start()
        w = text[max(0, i - 100):i + 120]
        if re.search(dpat, w):
            return True, _snip(text, i), _section_at(text, i)
    return False, "", ""


def run_detector(detector, text):
    if detector in ("mineral_fe", "mineral_ca", "mineral_mg", "mineral_zn"):
        return detect_mineral(text, detector.split("_")[1])
    if detector == "antacid":
        return detect_antacid(text)
    if detector == "folate":
        # depletion/길항 직접근거만. '엽산 보충 권장'·임신 신경관결손 맥락은 제외(보충 권유 금지).
        for m in re.finditer(r"엽산|폴산|폴린산", text):
            i = m.start()
            w = text[max(0, i - 70):i + 90]
            if re.search(r"엽산\s*보충|폴산\s*보충|보충이|보충을?\s*권|신경관\s*결손|임신\s*전|임신\s*1기", w):
                continue
            if re.search(r"(엽산|폴산|폴린산).{0,10}(저하|감소|결핍|길항)|(저하|감소|결핍|길항).{0,10}(엽산|폴산|폴린산)|"
                         r"엽산\s*흡수.{0,8}(저하|감소)|폴산대사|엽산대사", w):
                return True, _snip(text, i), _section_at(text, i)
        return False, "", ""
    if detector == "vitd":
        # 효소유도 약물의 골연화/구루병 → 비타민D 결핍 monitoring. 단순 보충권유 단독은 제외.
        for m in re.finditer(r"비타민\s*D|비타민D|칼시(트리|페)?올|골연화|구루병", text):
            i = m.start()
            w = text[max(0, i - 80):i + 90]
            if re.search(r"골연화|구루병|골다공|비타민\s*D.{0,10}(저하|결핍|투여|섭취)|"
                         r"칼슘.{0,6}저하|골(밀도|대사).{0,8}(저하|이상)", w):
                return True, _snip(text, i), _section_at(text, i)
        return False, "", ""
    if detector == "b12":
        # B12 흡수저하/결핍 직접근거만. '보충/처치 고려' co-mention 제외.
        for m in re.finditer(r"비타민\s*B\s*12|비타민B12|코발라민|시아노코발라민", text):
            i = m.start()
            w = text[max(0, i - 55):i + 75]
            if re.search(r"보충|처치를?\s*고려|투여를?\s*고려|섭취", w):
                continue
            if re.search(r"(B\s*12|코발라민).{0,14}(흡수.{0,8}(저하|감소)|결핍|저하)|"
                         r"(흡수.{0,8}(저하|감소)|결핍).{0,14}(B\s*12|코발라민)", w):
                return True, _snip(text, i), _section_at(text, i)
        return False, "", ""
    if detector == "b6":
        return detect_generic(text, r"피리독신|비타민\s*B\s*6|비타민B6", r"결핍|소실|저하|길항|보충|신경")
    if detector == "fatsol":
        return detect_generic(text, r"지용성\s*비타민|비타민\s*[ADEK]", r"흡수.{0,14}(저하|감소|저해|방해)|간격|보충")
    if detector == "k_depletion":
        return detect_generic(text, r"칼륨|포타슘|저칼륨", r"저하|소실|배설.{0,8}(증가|촉진)|저칼륨|결핍|보충")
    return False, "", ""


def make_client():
    sc = _load_mod("sc", "sourcecheck_theme_map_expansion_v1_3.py")
    return sc.make_online_client()


# ───────────────────────── candidate 생성 / 분류 ─────────────────────────
def load_inventory():
    if not os.path.exists(INVENTORY):
        raise SystemExit(f"[FATAL] inventory 없음 — 먼저 build_relation_factory_inventory_v1_4.py")
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    dedup = set(inv.get("dedup_keys", []))
    reject = {r["key"] for r in inv.get("reject", [])}
    nodom = {r["key"] for r in inv.get("no_domestic_product", [])}
    highrisk = {r["key"] for r in inv.get("high_risk_permanent_hold", [])}
    hold = {r["key"] for r in inv.get("hold", [])}
    live = {p["key"] for p in inv.get("live_pairs", [])}
    return inv, dedup, reject, nodom, highrisk, hold, live


def generate(families_filter=None):
    inv, dedup, reject, nodom, highrisk, hold, live = load_inventory()
    cands = []
    n = 0
    for fam in FAMILY_UNIVERSE:
        if families_filter and fam["id"] not in families_filter:
            continue
        for drug in fam["drugs"]:
            for cp in fam["counterparts"]:
                spec = COUNTERPARTS[cp]
                disp, ctype, ccat, mech, action, detector, evd = spec
                k = inv_key(drug, cp if cp != "al_mg_antacid" else "제산제")
                # 중복/상태 판정
                if k in live:
                    dup, existing, pr = "duplicate_live", "live", "REJECT_PRECHECK"
                elif k in reject:
                    dup, existing, pr = "duplicate_reject", "reject", "REJECT_PRECHECK"
                elif k in nodom:
                    dup, existing, pr = "duplicate_no_domestic", "no_domestic_product", "REJECT_PRECHECK"
                elif k in highrisk:
                    dup, existing, pr = "duplicate_highrisk", "high_risk_permanent_hold", "HOLD"
                elif k in hold:
                    dup, existing, pr = "duplicate_hold", "hold", "HOLD"
                elif k in dedup:
                    dup, existing, pr = "duplicate_pending", "pending", "REJECT_PRECHECK"
                else:
                    dup, existing, pr = "new", "none", fam["priority_default"]
                # family risk 반영
                risk = fam["risk_class"]
                if risk == "high_risk" and pr not in ("REJECT_PRECHECK",):
                    pr = "HOLD"
                # K-sparing × 칼륨 = depletion 금지 안전벨트
                if cp == "k" and drug in ("스피로노락톤", "에플레레논", "아밀로라이드", "트리암테렌"):
                    pr, existing = "REJECT_PRECHECK", "k_raising_not_depletion"
                n += 1
                cands.append({
                    "candidate_id": f"RF-{fam['id']}-{n:04d}",
                    "family": fam["id"], "family_name": fam["name"],
                    "drug_ingredient": drug, "counterpart": disp, "counterpart_canon": cp,
                    "counterpart_type": ctype, "counterpart_category": ccat,
                    "proposed_mechanism": mech, "proposed_action": action,
                    "expected_label_section": "약물상호작용/사용상의 주의",
                    "why_candidate": fam["notes"],
                    "duplicate_status": dup, "existing_status": existing,
                    "risk_class": risk, "priority": pr,
                    "source_check_allowed": bool(fam["source_check"] and pr in ("P0", "P1", "P2")
                                                 and dup == "new"),
                    "high_risk_reason": (fam["notes"] if risk == "high_risk" else ""),
                    "evidence_default": evd, "detector": detector,
                    "live_allowed": False,
                })
    return inv, cands


def precheck_summary(cands):
    from collections import Counter
    byp = Counter(c["priority"] for c in cands)
    byf = Counter(c["family"] for c in cands)
    bydup = Counter(c["duplicate_status"] for c in cands)
    new = [c for c in cands if c["duplicate_status"] == "new"]
    scq = [c for c in cands if c["source_check_allowed"]]
    return {
        "total_raw": len(cands), "new_after_dedup": len(new),
        "source_check_queue": len(scq),
        "by_priority": dict(byp), "by_family": dict(byf), "by_duplicate_status": dict(bydup),
        "p0": sum(1 for c in new if c["priority"] == "P0"),
        "p1": sum(1 for c in new if c["priority"] == "P1"),
        "p2": sum(1 for c in new if c["priority"] == "P2"),
        "hold": sum(1 for c in cands if c["priority"] == "HOLD"),
        "reject_precheck": sum(1 for c in cands if c["priority"] == "REJECT_PRECHECK"),
    }


# ───────────────────────── source-check (online) ─────────────────────────
def _pick_oral_product(client, drug):
    """성분 검색 → 경구 완제 1건(주사/외용 제외·라벨 충분) 선택. (itemSeq, name, label) 또는 (None,..)."""
    try:
        rows = client.search_drug(drug, max_pages=1)
    except Exception as e:
        return None, f"search_error:{type(e).__name__}", ""
    if not rows:
        return None, "no_search_rows", ""
    inj = re.compile(r"주사|주\b|외용|점안|점이|연고|크림|로션|좌제|시럽|현탁|건조시럽|패치")
    best = None
    for r in rows:
        name = getattr(r, "item_name", "") or ""
        if inj.search(name):
            continue
        try:
            d = client.get_item_detail(r.item_seq)
        except Exception:
            continue
        lab = d.label_text or ""
        if len(lab) >= 400:
            return r.item_seq, name, lab
        if best is None and lab:
            best = (r.item_seq, name, lab)
    if best:
        return best
    return None, "no_oral_label", ""


def source_check(cands, max_n, p0_only):
    pool = [c for c in cands if c["source_check_allowed"]]
    if p0_only:
        pool = [c for c in pool if c["priority"] == "P0"]
    pool.sort(key=lambda c: ({"P0": 0, "P1": 1, "P2": 2}.get(c["priority"], 9), c["drug_ingredient"]))
    pool = pool[:max_n]
    client = make_client()
    label_cache = {}  # drug → (itemSeq, name, label)
    results = []
    for c in pool:
        drug = c["drug_ingredient"]
        if drug not in label_cache:
            label_cache[drug] = _pick_oral_product(client, drug)
        seq, name, lab = label_cache[drug]
        rec = dict(c)
        if not seq:
            rec.update(sc_status="no_domestic_product" if name in ("no_search_rows", "no_oral_label")
                       else "label_not_found", itemSeq="", source_section="", source_quote="",
                       sc_note=name)
            results.append(rec)
            continue
        found, quote, section = run_detector(c["detector"], lab)
        if found:
            status = "source_confirmed_draft_candidate"
        else:
            # 라벨은 있으나 직접근거 없음 → direction_mismatch/label_not_found 구분
            cp_pat = MINERAL_PATS.get(c["counterpart_canon"])
            has_term = bool(cp_pat and re.search(cp_pat, lab)) or \
                (c["detector"] == "antacid" and re.search(ANTACID_CTX, lab))
            status = "direction_mismatch" if has_term else "label_not_found"
        rec.update(sc_status=status, itemSeq=str(seq), source_product=name,
                   source_section=section, source_quote=quote, sc_note="")
        results.append(rec)
    try:
        net = client.stats
    except Exception:
        net = {}
    return results, net


# ───────────────────────── draft / PM queue emit ─────────────────────────
def app_copy(drug, counterpart, ctype, action):
    if action == "separation":
        disp = (f"이 약은 {counterpart}과(와) 함께 복용하면 약의 흡수가 줄어 효과가 감소할 수 있다는 "
                f"허가사항 문구가 있습니다. 함께 복용해야 하는 경우 복용 시점을 분리하도록 안내하고 있으니, "
                f"약사 또는 의사와 상담하세요.")
        mng = f"{counterpart}과(와)는 복용 시간을 분리하는 것이 좋을 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
    else:  # monitoring/depletion
        disp = (f"이 약을 장기간 복용할 때 {counterpart} 수치 변화와 관련된 허가사항 문구가 있습니다. "
                f"증상이나 수치가 걱정되면 약사 또는 의사와 상담하세요.")
        mng = f"정기적인 확인이 필요할 수 있습니다. 자세한 사항은 약사 또는 의사와 상담하세요."
    return disp, mng


def emit_drafts(results):
    confirmed = [r for r in results if r["sc_status"] == "source_confirmed_draft_candidate"]
    drafts = []
    for r in confirmed:
        disp, mng = app_copy(r["drug_ingredient"], r["counterpart"], r["counterpart_type"], r["proposed_action"])
        d = {
            "candidate_id": r["candidate_id"], "relation": f'{r["drug_ingredient"]} × {r["counterpart"]}',
            "family": r["family"], "drug_ingredient": r["drug_ingredient"],
            "counterpart": r["counterpart"], "counterpart_type": r["counterpart_type"],
            "counterpart_category": r["counterpart_category"],
            "recommended_action": r["proposed_action"], "mechanism": r["proposed_mechanism"],
            "evidence_level": r["evidence_default"], "confidence": "moderate",
            "risk_level": r["risk_class"], "itemSeq": r["itemSeq"],
            "source_section": r["source_section"], "source_quote": r["source_quote"],
            "display_copy": disp, "management_copy": mng,
            "product_link_allowed": False, "potassium_safety_card": r["counterpart_canon"] == "k",
            "live_integration_forbidden": True, "do_not_implement_yet": True,
            "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "reviewer_needed": True, "pm_approval_required": True,
            "safety_flags": (["potassium_supplement_caution"] if r["counterpart_canon"] == "k" else [])
            + (["mechanism_inferred"] if r["proposed_mechanism"] == "absorption"
               and r["counterpart_canon"] in ("zn",) else []),
            "adversarial_required": True,
        }
        drafts.append(d)
    batch = {
        "meta": {
            "name": "relation_factory_draft_batch_v1_4",
            "status": "DRAFT-ONLY — NOT LIVE / do_not_implement_yet=true / live_integration_forbidden=true",
            "purpose": "Relation Factory v1.4 SDK source-confirmed draft 후보. live 통합·승격 0. "
                       "adversarial 검증 + reviewer package + dry-run integrator 후에만 live 절차(별도).",
            "count": len(drafts), "published": False, "clinical_reviewed": False, "reviewed_by": "",
            "note": "source_confirmed 은 라벨 직접근거 verbatim 확인을 의미하며 식약처 승인·약사 검수 완료·"
                    "법적 문제 없음 을 의미하지 않는다. 계열 일반화로 만든 draft 없음(약물별 라벨 직접 확인).",
        },
        "draft_relations": drafts,
    }
    return batch, confirmed


def emit_pm_queue(precheck, results, batch, scnet):
    from collections import Counter
    byf_yield = {}
    for fam in FAMILY_UNIVERSE:
        fid = fam["id"]
        fam_res = [r for r in results if r["family"] == fid]
        conf = sum(1 for r in fam_res if r["sc_status"] == "source_confirmed_draft_candidate")
        byf_yield[fid] = {"name": fam["name"], "source_checked": len(fam_res), "confirmed": conf,
                          "yield": round(conf / len(fam_res), 3) if fam_res else None}
    sc_counts = dict(Counter(r["sc_status"] for r in results))
    pm = {
        "meta": {
            "name": "relation_factory_pm_review_queue_v1_4",
            "status": "LIVE 아님 · 자동 승격 금지 · reviewer/PM 승인 전 live 금지 · 제품/구매/제휴 없음",
            "source_check_stats": scnet, "sc_status_counts": sc_counts,
            "draft_count": batch["meta"]["count"],
        },
        "family_yield": byf_yield,
        "source_confirmed_drafts": [{"candidate_id": d["candidate_id"], "relation": d["relation"],
                                     "itemSeq": d["itemSeq"], "section": d["source_section"],
                                     "quote": d["source_quote"][:160]} for d in batch["draft_relations"]],
        "needs_review": [{"candidate_id": r["candidate_id"], "relation": f'{r["drug_ingredient"]} × {r["counterpart"]}',
                          "reason": r["sc_status"]} for r in results
                         if r["sc_status"] in ("direction_mismatch", "ambiguous")],
        "label_not_found": [f'{r["drug_ingredient"]} × {r["counterpart"]}' for r in results
                            if r["sc_status"] == "label_not_found"],
        "no_domestic_product": [r["drug_ingredient"] for r in results if r["sc_status"] == "no_domestic_product"],
        "next_actions": ["adversarial verification(refute-by-default)", "reviewer package",
                         "dry-run integrator(별도)", "hold/reject close"],
    }
    return pm


# ───────────────────────── universe doc emit ─────────────────────────
def emit_universe():
    uni = {"meta": {"name": "relation_family_universe_v1_4",
                    "purpose": "Relation Factory v1.4 family universe(source-check 후보 생성 전용·draft 생성 아님).",
                    "family_count": len(FAMILY_UNIVERSE),
                    "note": "계열 일반화로 draft/live 생성 금지 — 약물별 라벨 직접 source-check 후에만 draft."},
           "families": FAMILY_UNIVERSE, "counterparts": COUNTERPARTS}
    with open(OUT_UNIVERSE_JSON, "w", encoding="utf-8") as f:
        json.dump(uni, f, ensure_ascii=False, indent=1)
        f.write("\n")
    md = ["# MediStack — Relation Family Universe (v1.4)", "",
          "> 대량 후보 생성용 family 정의. **source-check 후보 생성 전용** — 계열 일반화로 draft/live 만들지 않는다.",
          f"> 정본 JSON `data/review/relation_family_universe_v1_4.json` · family **{len(FAMILY_UNIVERSE)}**개. live 승격 0.", ""]
    for fam in FAMILY_UNIVERSE:
        md += [f"## {fam['id']} — {fam['name']}",
               f"- drugs({len(fam['drugs'])}): {', '.join(fam['drugs'])}",
               f"- counterparts: {', '.join(COUNTERPARTS[c][0] for c in fam['counterparts'])}",
               f"- risk_class: **{fam['risk_class']}** · priority_default: {fam['priority_default']} · "
               f"source_check: {fam['source_check']}",
               f"- note: {fam['notes']}", ""]
    md += ["## 제외/고위험 원칙",
           "- warfarin×비타민K(antagonism)·이식/면역억제·항암·임신·정신과 고위험 = reviewer 전 제외.",
           "- K-sparing(스피로노락톤 등)×칼륨 = 상승 방향 → depletion 카드 절대 금지(REJECT_PRECHECK).",
           "- 세파계×철분·미유통 다이유레틱 = 확정 reject/no_domestic(재후보화 금지).",
           "- 계열 일반화 금지: family 는 후보 생성용일 뿐, draft 는 약물별 라벨 직접근거(verbatim)만."]
    with open(OUT_UNIVERSE_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def emit_candidates(cands, precheck):
    cj = {"meta": {"name": "relation_factory_candidates_v1_4", "total": len(cands),
                   "do_not_implement_yet": True, "live_integration_forbidden": True,
                   "precheck": precheck}, "candidates": cands}
    with open(OUT_CAND_JSON, "w", encoding="utf-8") as f:
        json.dump(cj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    cols = ["candidate_id", "family", "drug_ingredient", "counterpart", "counterpart_type",
            "priority", "duplicate_status", "existing_status", "source_check_allowed", "risk_class"]
    with open(OUT_CAND_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for c in cands:
            w.writerow(c)
    queue = [c for c in cands if c["source_check_allowed"]]
    with open(OUT_QUEUE, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "relation_factory_source_check_queue_v1_4",
                            "count": len(queue), "p0": sum(1 for c in queue if c["priority"] == "P0"),
                            "p1": sum(1 for c in queue if c["priority"] == "P1")},
                   "queue": queue}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(OUT_PRECHECK, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "relation_factory_precheck_summary_v1_4"}, **precheck},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    md = ["# MediStack — Relation Factory v1.4 후보 요약", "",
          f"> raw 후보 **{precheck['total_raw']}** · 중복 제거 후 신규 **{precheck['new_after_dedup']}** · "
          f"source-check queue **{precheck['source_check_queue']}**. draft/live 생성 아님(source-check 후보).",
          "", "## priority 분포", f"```\n{json.dumps(precheck['by_priority'], ensure_ascii=False)}\n```",
          "## family 분포", f"```\n{json.dumps(precheck['by_family'], ensure_ascii=False)}\n```",
          "## duplicate_status 분포", f"```\n{json.dumps(precheck['by_duplicate_status'], ensure_ascii=False)}\n```",
          "", "정본: `data/review/relation_factory_candidates_v1_4.json` · queue `..._source_check_queue_v1_4.json`."]
    with open(OUT_CAND_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def emit_sc_results(results):
    with open(OUT_SC_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": {"name": "relation_factory_source_check_results_v1_4",
                            "count": len(results)}, "results": results}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    cols = ["candidate_id", "family", "drug_ingredient", "counterpart", "priority",
            "sc_status", "itemSeq", "source_section", "source_quote"]
    with open(OUT_SC_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-universe", action="store_true")
    ap.add_argument("--online-source-check", action="store_true")
    ap.add_argument("--max-source-check", type=int, default=120)
    ap.add_argument("--families", default="")
    ap.add_argument("--p0-only", action="store_true")
    args = ap.parse_args()

    fams = [x.strip() for x in args.families.split(",") if x.strip()] or None

    emit_universe()
    if args.emit_universe:
        print(f"[universe] {len(FAMILY_UNIVERSE)} families → {os.path.relpath(OUT_UNIVERSE_JSON, REPO)}")
        return 0

    inv, cands = generate(fams)
    precheck = precheck_summary(cands)
    emit_candidates(cands, precheck)
    print(f"[generate] raw {precheck['total_raw']} · new {precheck['new_after_dedup']} · "
          f"queue {precheck['source_check_queue']} (P0 {precheck['p0']} / P1 {precheck['p1']} / P2 {precheck['p2']}) · "
          f"HOLD {precheck['hold']} · REJECT_PRECHECK {precheck['reject_precheck']}")

    if not args.online_source_check:
        print("[offline] source-check 미실행(--online-source-check 로 SDK source-check + draft/PM).")
        return 0

    results, scnet = source_check(cands, args.max_source_check, args.p0_only)
    emit_sc_results(results)
    batch, confirmed = emit_drafts(results)
    with open(OUT_DRAFT, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=1)
        f.write("\n")
    pm = emit_pm_queue(precheck, results, batch, scnet)
    with open(OUT_PM_JSON, "w", encoding="utf-8") as f:
        json.dump(pm, f, ensure_ascii=False, indent=1)
        f.write("\n")
    # PM md
    md = ["# Relation Factory v1.4 — PM Review Queue", "",
          "> **LIVE 아님 · 자동 승격 금지 · reviewer/PM 승인 전 live 금지 · 제품/구매/제휴 없음**",
          f"> SDK source-check {len(results)}건 · source_confirmed draft **{batch['meta']['count']}** · "
          f"network {scnet.get('network','?')}.", "",
          "## family별 수확률"]
    for fid, y in pm["family_yield"].items():
        if y["source_checked"]:
            md.append(f"- {fid} {y['name']}: checked {y['source_checked']} · confirmed {y['confirmed']} · yield {y['yield']}")
    md += ["", "## source_confirmed drafts"]
    for d in pm["source_confirmed_drafts"]:
        md.append(f"- {d['candidate_id']} **{d['relation']}** (itemSeq {d['itemSeq']}·{d['section']}) — \"{d['quote']}\"")
    md += ["", f"## needs_review {len(pm['needs_review'])} · label_not_found {len(pm['label_not_found'])} · "
           f"no_domestic {len(pm['no_domestic_product'])}",
           "", "## 다음 action", *[f"- {a}" for a in pm["next_actions"]]]
    with open(OUT_PM_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    from collections import Counter
    sc_counts = Counter(r["sc_status"] for r in results)
    print(f"[source-check] processed {len(results)} · network {scnet.get('network','?')} · "
          f"confirmed {sc_counts.get('source_confirmed_draft_candidate',0)} · "
          f"needs_review {sc_counts.get('direction_mismatch',0)} · "
          f"label_not_found {sc_counts.get('label_not_found',0)} · "
          f"no_domestic {sc_counts.get('no_domestic_product',0)}")
    print(f"[draft] {batch['meta']['count']} source_confirmed → {os.path.relpath(OUT_DRAFT, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
