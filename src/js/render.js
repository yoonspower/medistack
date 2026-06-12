// render.js — 검색/필터 컨트롤 + 목록(필터된 subset) + 상세. 의학 단정/지시/구매유도 금지.
import { canShowProduct, showPotassiumNotice, commonDisclaimer, potassiumNotice } from './guards.js';

const ACTION = {
  separation: { label: '복용 간격', chip: 'chip-sep', aClass: '', kicker: '같은 시간대 복용 주의' },
  monitoring: { label: '상태 모니터링', chip: 'chip-mon', aClass: 'mon', kicker: '장기 복용 시 상태 확인' },
};
const ACTION_ORDER = ['separation', 'monitoring'];
const EVIDENCE_LABEL = { high: '높음', moderate: '보통' };
const EVIDENCE_ORDER = ['high', 'moderate'];

export function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function orderBy(vals, ord) {
  return [...vals].sort((a, b) => {
    const ia = ord.indexOf(a), ib = ord.indexOf(b);
    return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib);
  });
}

export function renderRow(r) {
  const a = ACTION[r.recommended_action] || { label: '', chip: 'chip-mon' };
  return '<a class="row" href="#/r/' + encodeURIComponent(r.id) + '">' +
    '<span class="pair"><span class="ing">' + esc(r.ingredient) + '</span><span class="x">×</span><span class="nut">' + esc(r.nutrient) + '</span></span>' +
    '<span class="chip ' + a.chip + '">' + esc(a.label) + '</span>' +
    '<svg class="chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg>' +
    '</a>';
}

function fchip(facet, value, label, active) {
  return '<button type="button" class="fchip' + (active ? ' active' : '') + '" data-facet="' + esc(facet) +
    '" data-value="' + esc(value) + '" aria-pressed="' + (active ? 'true' : 'false') + '">' + esc(label) + '</button>';
}

// 검색 + 필터 컨트롤 (목록 진입 시 1회 렌더; 검색 입력은 results만 갱신하므로 재렌더 안 함)
export function renderListControls(facets, state) {
  const sel = (f) => (state && state[f]) || [];
  const isOn = (f, v) => sel(f).includes(v);
  const group = (title, facet, vals, labelFn) =>
    '<div class="fgroup"><span class="flabel">' + esc(title) + '</span><div class="fchips">' +
    vals.map((v) => fchip(facet, v, labelFn(v), isOn(facet, v))).join('') + '</div></div>';

  let h = '<div class="search">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>' +
    '<input id="ms-search" type="search" inputmode="search" autocomplete="off" placeholder="약물명·영양소명 검색" aria-label="약물명 또는 영양소명 검색" value="' + esc((state && state.query) || '') + '">' +
    '</div>';
  h += '<div class="filters">';
  h += group('영양소', 'nutrients', facets.nutrients, (v) => v);
  h += group('분류', 'actions', orderBy(facets.actions, ACTION_ORDER), (v) => (ACTION[v] ? ACTION[v].label : v));
  h += group('참고 근거', 'evidences', orderBy(facets.evidences, EVIDENCE_ORDER), (v) => EVIDENCE_LABEL[v] || v);
  h += '</div>';
  h += '<button id="ms-reset" class="reset" type="button" data-action="reset" hidden>필터 초기화</button>';
  return h;
}

// alias 안내 1줄 (검색 보조 안내. 제품 정보/추천 아님). info = { query, ingredients:[...] }
export function renderAliasHint(info) {
  if (!info || !info.query || !Array.isArray(info.ingredients) || info.ingredients.length === 0) return '';
  const ing = info.ingredients.join(', ');
  let h = '<div class="aliashint">' + esc('‘' + info.query + '’ 검색어는 ' + ing + ' 관련 정보로 연결됩니다.') + '</div>';
  // v0.7 복합제 고지(검색 보조 안내. 제품 추천/구매 아님). info.comboBases 부재 시 미표시 → 기존과 동일.
  if (Array.isArray(info.comboBases) && info.comboBases.length > 0) {
    const basis = info.comboBases.join(', ');
    h += '<div class="combobox" role="note"><span class="combobadge">복합제</span><p>' +
      esc('이 제품은 둘 이상의 성분을 가진 복합제입니다. 표시된 약-영양소 참고 정보는 ' + basis +
          ' 성분을 기준으로 하며, 함께 포함된 다른 성분에 대한 정보는 포함하지 않습니다. 전체 성분은 의약품 허가사항(첨부문서)을 확인하세요.') +
      '</p></div>';
  }
  return h;
}

// 결과 카운트 + 카드 (0건이면 카운트만; no-results 는 states.renderNoResults)
export function renderListResults(filtered, total) {
  const head = filtered.length === total
    ? ('전체 ' + total + '건')
    : ('조건 일치 ' + filtered.length + '건 · 전체 ' + total + '건');
  let h = '<div class="listhead">' + esc(head) + '</div>';
  for (const r of filtered) h += renderRow(r);
  return h;
}

// 상세 (불변: common fail-safe / 칼륨 고지 / 제품 차단)
export function renderDetail(rel, data) {
  const a = ACTION[rel.recommended_action] || { label: '', aClass: '', kicker: '' };
  const common = commonDisclaimer(data);

  let h =
    '<div class="dh"><div class="kicker">' + esc(a.kicker) + '</div>' +
    '<h2>' + esc(rel.ingredient) + '<span class="x">×</span>' + esc(rel.nutrient) + '</h2></div>' +
    '<div class="alabel ' + a.aClass + '"><span class="dot"></span>' + esc(a.label) + '</div>' +
    '<div class="bodytext">' + esc(rel.display_text_ko) + '</div>';

  if (rel.management_ko) {
    h += '<div class="guide"><div class="gt">참고 안내</div><p>' + esc(rel.management_ko) + '</p></div>';
  }

  const kNotice = potassiumNotice(data);
  if (showPotassiumNotice(rel) && kNotice) {
    h += '<div class="kbox">' +
      '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>' +
      '<div><div class="kt">칼륨 주의</div><p>' + esc(kNotice) + '</p></div></div>';
  }

  if (canShowProduct(rel)) {
    // v0.1/v0.2 미도달. v0.3 제품 트랙에서 구현.
  }

  if (rel.source) {
    h += '<div class="src"><span class="lab">출처</span> · ' + esc(rel.source.type || '식약처 허가사항');
    if (rel.source.url) h += ' &nbsp;<a href="' + esc(rel.source.url) + '" target="_blank" rel="noopener">원문 보기 ↗</a>';
    if (rel.source.pointer) h += '<details><summary>출처 상세</summary><div class="ptr">' + esc(rel.source.pointer) + '</div></details>';
    h += '</div>';
  }

  h += '<div class="disc">' + esc(common) + '</div>';
  return h;
}
