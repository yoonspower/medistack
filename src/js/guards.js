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

function norm(s) {
  return String(s == null ? '' : s).normalize('NFC').trim().toLowerCase();
}

// facet 동적 도출 (하드코딩 금지 → 확장 자동 대응)
export function getFacets(rels) {
  const uniq = (arr) => [...new Set(arr.filter((v) => v !== undefined && v !== null && String(v).length > 0))];
  return {
    nutrients: uniq(rels.map((r) => r.nutrient)),
    actions: uniq(rels.map((r) => r.recommended_action)),
    evidences: uniq(rels.map((r) => r.evidence_level)),
  };
}

// state: { query, nutrients:[], actions:[], evidences:[] }
// facet 내부 OR(includes), facet 간 AND, 검색과도 AND. 입력은 반드시 getRenderableRelations 결과.
export function filterRelations(rels, state) {
  const s = state || {};
  const q = norm(s.query);
  const inSel = (val, sel) => !sel || sel.length === 0 || sel.includes(val);
  return rels.filter((r) => {
    if (!inSel(r.nutrient, s.nutrients)) return false;
    if (!inSel(r.recommended_action, s.actions)) return false;
    if (!inSel(r.evidence_level, s.evidences)) return false;
    if (q && !SEARCH_FIELDS.some((f) => norm(r[f]).includes(q))) return false;
    return true;
  });
}
