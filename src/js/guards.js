// guards.js — 렌더 규칙 레이어 (순수 함수, DOM/네트워크 의존 없음)
// v0.1 봉인 규칙을 코드로 강제한다. status/published/clinical_reviewed 는 절대 읽지 않는다.

const PRODUCT_FIELDS = ['product_links', 'product_examples', 'products', 'affiliate_links', 'buy_links'];
const REQUIRED_RELATION_FIELDS = ['id', 'ingredient', 'nutrient', 'recommended_action', 'display_text_ko'];

// relations 만 렌더 대상. excluded_v0_1 는 절대 사용하지 않는다.
export function getRenderableRelations(data) {
  const rels = data && Array.isArray(data.relations) ? data.relations : [];
  return rels.filter(isRenderable);
}

// 필수 필드 누락 시 반쪽 의학문장 렌더 금지 → skip
export function isRenderable(rel) {
  return !!rel && typeof rel === 'object' && !Array.isArray(rel) &&
    REQUIRED_RELATION_FIELDS.every(
      (k) => rel[k] !== undefined && rel[k] !== null && String(rel[k]).length > 0
    );
}

export function hasProductData(rel) {
  return PRODUCT_FIELDS.some((k) => (Array.isArray(rel[k]) ? rel[k].length > 0 : !!rel[k]));
}

// 제품 영역: 엄격 === true && 제품데이터 존재 시에만. 칼륨(false)·v0.1(데이터 없음)은 미표시.
export function canShowProduct(rel) {
  return rel.product_link_allowed === true && hasProductData(rel);
}

// 칼륨 고지: 플래그 기준만. nutrient 문자열 매칭 금지(표기/i18n 변동 위험).
export function showPotassiumNotice(rel) {
  return rel.potassium_safety_card === true;
}

// 공통 면책문구: 없으면 상세 렌더 차단(fail-safe).
export function commonDisclaimer(data) {
  const c = data && data.disclaimers && data.disclaimers.common;
  return c && String(c).trim() ? c : null;
}

export function potassiumNotice(data) {
  const n = data && data.disclaimers && data.disclaimers.potassium_notice;
  return n && String(n).trim() ? n : null;
}

// 렌더 가능한 relations 에서만 탐색 → excluded/15행/누락행 id는 못 찾고 상세는 error로 fail-safe.
export function findRelation(data, id) {
  return getRenderableRelations(data).find((r) => r.id === id) || null;
}

// ---- Phase 1: 검색/필터 (순수 함수, relations 소스만) ----
const SEARCH_FIELDS = ['ingredient', 'nutrient'];
// v0.8: HCTZ 복합제 칼륨 반전 고지 basis(ARB 파트너가 칼륨을 반대 방향으로 움직임).
const HCTZ_BASIS = '히드로클로로티아지드';

function norm(s) {
  return String(s == null ? '' : s).normalize('NFC').trim().toLowerCase();
}

// facet 동적 도출 (하드코딩 금지 → 확장 자동 대응)
// '영양소' facet 은 실제 영양소 relation 만 — counterpart_category 가 있는 relation(antacid_interaction 등
// 약물×약물 트랙)은 nutrient 슬롯이 영양소가 아니라 '제산제(약물)' 라서 영양소 facet 에서 제외한다
// (검색 '영양소' 필터에 비-영양소가 끼어 '마그네슘 영양제' 류 오인되는 것 차단). 기존 영양소 relation 은
// counterpart_category 가 없어 영향 없음. action/evidence facet 은 전 relation 공통이라 그대로.
export function getFacets(rels) {
  const uniq = (arr) => [...new Set(arr.filter((v) => v !== undefined && v !== null && String(v).length > 0))];
  return {
    nutrients: uniq(rels.filter((r) => !r.counterpart_category).map((r) => r.nutrient)),
    actions: uniq(rels.map((r) => r.recommended_action)),
    evidences: uniq(rels.map((r) => r.evidence_level)),
  };
}

// ---- v0.3: alias 검색 보조 (순수 함수, relation 풀 확장 안 함) ----
// alias 데이터 → 런타임 인덱스 [{ alias(정규화), canonical(정규화) }]. malformed 엔트리는 skip.
export function buildAliasIndex(aliasData) {
  const out = [];
  if (!aliasData || typeof aliasData !== 'object') return out;
  for (const list of [aliasData.ingredient_aliases, aliasData.product_aliases]) {
    if (!Array.isArray(list)) continue;
    for (const e of list) {
      if (!e || typeof e !== 'object') continue;
      const a = e.alias, ci = e.canonical_ingredient;
      if (typeof a !== 'string' || !a.trim()) continue;
      if (typeof ci !== 'string' || !ci.trim()) continue;
      const rec = { alias: norm(a), canonical: norm(ci) };
      // v0.7 복합제: is_combination=true 항목만 combo 메타 부착(나머지 항목엔 미부착 → 하위호환).
      if (e.is_combination === true) {
        rec.isCombo = true;
        const b = e.combination_basis_ingredient;
        rec.basis = norm(typeof b === 'string' && b.trim() ? b : ci);
        // v1.1 A: 공존 성분 라벨(예: '비타민D'). 있으면 배너가 '다른 성분' 대신 그 라벨을 명시.
        // 부재 시 기존 일반 문구('다른 성분') → 하위호환(기존 combo 불변).
        const ol = e.combination_other_label;
        if (typeof ol === 'string' && ol.trim()) rec.otherLabel = ol.trim();
      }
      out.push(rec);
    }
  }
  return out;
}

// 질의 q 의 alias 해석 → canonical_ingredient(정규화) Set.
// alias 표면형은 prefix(startsWith) 매칭: 짧은 INN이 긴 INN의 접미사로 끼는 약물간 오매칭 차단
// (예: "ofloxacin"이 levo/ciprofloxacin에 substring으로 걸리는 문제). canonical 은 정확일치로 relation 매칭.
export function resolveAliasIngredients(query, aliasIndex) {
  const nq = norm(query);
  const set = new Set();
  if (!nq || !Array.isArray(aliasIndex)) return set;
  for (const e of aliasIndex) if (e.alias.startsWith(nq)) set.add(e.canonical);
  return set;
}

// state: { query, nutrients:[], actions:[], evidences:[] }
// facet 내부 OR(includes), facet 간 AND, 검색과도 AND. 입력은 반드시 getRenderableRelations 결과.
// aliasIndex(옵션): 검색은 직접매칭(ingredient/nutrient substring) OR alias매칭(ingredient 정확일치). 풀은 안 넓힘.
export function filterRelations(rels, state, aliasIndex) {
  const s = state || {};
  const q = norm(s.query);
  const aliasIngs = q ? resolveAliasIngredients(s.query, aliasIndex) : null;
  const inSel = (val, sel) => !sel || sel.length === 0 || sel.includes(val);
  return rels.filter((r) => {
    if (!inSel(r.nutrient, s.nutrients)) return false;
    if (!inSel(r.recommended_action, s.actions)) return false;
    if (!inSel(r.evidence_level, s.evidences)) return false;
    if (q) {
      const direct = SEARCH_FIELDS.some((f) => norm(r[f]).includes(q));
      const viaAlias = !!aliasIngs && aliasIngs.has(norm(r.ingredient));
      if (!direct && !viaAlias) return false;
    }
    return true;
  });
}

// alias 안내 1줄 판정. 직접 성분/영양소 매칭이 결과에 있으면 안내 안 함(PM 규칙).
// 입력 filteredRels = 이미 filterRelations 거친 결과. 반환 null 또는 { query, ingredients:[raw...] }.
export function aliasHint(filteredRels, state, aliasIndex) {
  const s = state || {};
  const q = norm(s.query);
  if (!q || !Array.isArray(filteredRels) || filteredRels.length === 0) return null;
  const directInFiltered = filteredRels.some((r) => SEARCH_FIELDS.some((f) => norm(r[f]).includes(q)));
  if (directInFiltered) return null;
  const aliasIngs = resolveAliasIngredients(s.query, aliasIndex);
  if (!aliasIngs.size) return null;
  const ings = [...new Set(filteredRels.filter((r) => aliasIngs.has(norm(r.ingredient))).map((r) => r.ingredient))];
  if (!ings.length) return null;
  const out = { query: s.query, ingredients: ings };
  // v0.7 복합제: 'combo alias 로만' 도달한 성분은 복합제 고지 대상으로 표시.
  const comboBases = comboBasesFor(q, ings, aliasIndex);
  if (comboBases.length) {
    out.comboBases = comboBases;
    // v1.1 A: 공존 성분 라벨 맵 { basisRaw: label }. 부재 시 미설정 → 배너 일반 문구(하위호환).
    const labels = comboOtherLabelsFor(q, comboBases, aliasIndex);
    if (Object.keys(labels).length) out.comboOtherLabels = labels;
  }
  // v0.8 HCTZ: 복합제 basis 가 히드로클로로티아지드이고 칼륨 행(potassium_safety_card 플래그)이
  // 결과에 있을 때만 칼륨 반전 고지 대상. nutrient 문자열 매칭 금지 원칙 → 플래그로 판정.
  // 라이브엔 HCTZ 복합제 0건 → comboBases 에 HCTZ 부재 → 항상 미설정(기존 동작과 동일).
  const hctzN = norm(HCTZ_BASIS);
  if (comboBases.some((b) => norm(b) === hctzN) &&
      filteredRels.some((r) => norm(r.ingredient) === hctzN && showPotassiumNotice(r))) {
    out.hctzPotassiumNotice = true;
  }
  return out;
}

// 질의 prefix 로 매칭된 alias 중, 해당 성분이 combo alias 로만 도달되면 복합제 고지 대상.
// 같은 성분에 단일성분 alias 도 매칭되면 제외 → 단일 제품 오고지 방지. ings = 표시 성분 raw.
// combo 항목이 전혀 없으면(현 라이브 0건) 항상 [] → 기존 동작과 동일.
function comboBasesFor(nq, ings, aliasIndex) {
  if (!nq || !Array.isArray(aliasIndex)) return [];
  const flag = new Map(); // canonical(norm) -> { combo, single }
  for (const e of aliasIndex) {
    if (!e.alias.startsWith(nq)) continue;
    const rec = flag.get(e.canonical) || { combo: false, single: false };
    if (e.isCombo) rec.combo = true; else rec.single = true;
    flag.set(e.canonical, rec);
  }
  return ings.filter((ing) => {
    const rec = flag.get(norm(ing));
    return !!rec && rec.combo && !rec.single;
  });
}

// v1.1 A: comboBases 각 basis 의 공존 성분 라벨 { basisRaw: label }. 질의 prefix 로 매칭된 combo alias 의
// otherLabel 만 수집(없으면 빈 객체 → 배너 일반 문구). 같은 basis 에 라벨이 여럿이면 첫 값(라이브엔 성분당 단일 라벨).
function comboOtherLabelsFor(nq, comboBases, aliasIndex) {
  const out = {};
  if (!nq || !Array.isArray(aliasIndex) || !Array.isArray(comboBases)) return out;
  const want = new Map(comboBases.map((b) => [norm(b), b]));
  for (const e of aliasIndex) {
    if (!e.isCombo || !e.otherLabel || !e.alias.startsWith(nq)) continue;
    const raw = want.get(e.canonical);
    if (raw && !out[raw]) out[raw] = e.otherLabel;
  }
  return out;
}

// ---- v1.0 Phase 3: full drug name index (relation 없는 약의 '품목명 확인'). 의학정보 미부착 ----
// full index 데이터 → name_only 런타임 인덱스. relation_card 항목은 제외(relation 검색이 이미 커버).
// item_seq/item_name/normalized/company_name 만 복사 → 상호작용/영양소/제품 필드는 구조적으로 미반입(있어도 버려짐).
export function buildNameOnlyIndex(fullData) {
  const out = [];
  if (!fullData || typeof fullData !== 'object' || !Array.isArray(fullData.entries)) return out;
  for (const e of fullData.entries) {
    if (!e || typeof e !== 'object') continue;
    if (e.display_mode !== 'name_only' || e.covered_by_relation === true) continue;
    const name = e.item_name;
    if (typeof name !== 'string' || !name.trim()) continue;
    out.push({
      item_seq: String(e.item_seq == null ? '' : e.item_seq),
      item_name: name,
      normalized: norm(e.normalized_item_name || name),
      company_name: typeof e.company_name === 'string' ? e.company_name : null,
    });
  }
  return out;
}

// 질의 q 의 품목명(정규화) 부분일치 → name_only 항목 리스트(최대 limit). relation 풀과 무관·확장 안 함.
export function searchNameOnly(query, nameOnlyIndex, limit) {
  const nq = norm(query);
  const out = [];
  if (!nq || !Array.isArray(nameOnlyIndex)) return out;
  const cap = typeof limit === 'number' && limit > 0 ? limit : nameOnlyIndex.length;
  for (const e of nameOnlyIndex) {
    if (e.normalized.includes(nq)) {
      out.push(e);
      if (out.length >= cap) break;
    }
  }
  return out;
}
