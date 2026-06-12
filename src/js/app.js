// app.js — entry + 해시 라우터 + 검색/필터(인메모리 state). 실패/0건/누락 시 안전 state.
import { loadData, loadAliases, loadFullIndex } from './data.js';
import { getRenderableRelations, findRelation, commonDisclaimer, getFacets, filterRelations, buildAliasIndex, aliasHint, buildNameOnlyIndex, searchNameOnly } from './guards.js';
import { renderListControls, renderListResults, renderDetail, renderAliasHint, renderNameOnlyResults, esc } from './render.js';
import { renderEmpty, renderError, renderNoResults } from './states.js';

const appbar = () => document.getElementById('appbar');
const body = () => document.getElementById('appbody');

const state = { data: null, error: false };
const filterState = { query: '', nutrients: [], actions: [], evidences: [] };
let aliasIndex = []; // alias 부재/실패 시 빈 배열 → relation-only 검색
let nameOnlyIndex = []; // full index 부재/실패 시 빈 배열 → name_only 미표시(현행 동작 degrade)
let nameOnlyNotice = ''; // full index meta.name_only_notice (render fallback 있음)
const NAME_ONLY_LIMIT = 30; // 품목명 확인 결과 표시 상한

const BETA_TAG = '<span class="beta">베타 · 참고 정보</span>';
function setAppbar(detail) {
  appbar().innerHTML = detail ? '<a class="back" href="#/">‹ 목록</a>' + BETA_TAG : '<span class="brand">MediStack</span>' + BETA_TAG;
}

function resetFilter() { filterState.query = ''; filterState.nutrients = []; filterState.actions = []; filterState.evidences = []; }
function hasActiveFilter() { return !!filterState.query || filterState.nutrients.length > 0 || filterState.actions.length > 0 || filterState.evidences.length > 0; }

function mountError() { setAppbar(false); body().innerHTML = renderError(); }
function mountEmpty() { setAppbar(false); body().innerHTML = renderEmpty(state.data); }
function mountDetail(id) {
  const rel = findRelation(state.data, id);
  if (!rel || !commonDisclaimer(state.data)) return mountError(); // fail-safe
  setAppbar(true); body().innerHTML = renderDetail(rel, state.data); body().scrollTop = 0;
}

function renderResults() {
  const rels = getRenderableRelations(state.data);
  const filtered = filterRelations(rels, filterState, aliasIndex);
  const el = document.getElementById('ms-results');
  if (!el) return;
  let html;
  if (filtered.length > 0) {
    html = renderAliasHint(aliasHint(filtered, filterState, aliasIndex)) + renderListResults(filtered, rels.length);
  } else {
    // relation 무매치 → full index name_only 폴백(텍스트 검색어만 있고 facet 미적용 시). relation 풀 확장 아님.
    const facetsActive = filterState.nutrients.length || filterState.actions.length || filterState.evidences.length;
    const matches = (filterState.query && !facetsActive) ? searchNameOnly(filterState.query, nameOnlyIndex, NAME_ONLY_LIMIT) : [];
    html = matches.length > 0 ? renderNameOnlyResults(matches, nameOnlyNotice) : renderNoResults();
  }
  el.innerHTML = html;
  const reset = document.getElementById('ms-reset');
  if (reset) reset.hidden = !hasActiveFilter();
}

function mountList() {
  setAppbar(false);
  const rels = getRenderableRelations(state.data);
  const facets = getFacets(rels);
  body().innerHTML = '<div id="ms-controls"></div><div id="ms-results"></div><div id="ms-footer"></div>';
  document.getElementById('ms-controls').innerHTML = renderListControls(facets, filterState);
  const cf = state.data.disclaimers && state.data.disclaimers.card_footer;
  if (cf) document.getElementById('ms-footer').innerHTML = '<div class="listfooter">' + esc(cf) + '</div>';
  renderResults();
  body().scrollTop = 0;
}

function route() {
  if (state.error || !state.data) return mountError();
  if (getRenderableRelations(state.data).length === 0) return mountEmpty();
  const m = location.hash.match(/^#\/r\/(\d+)$/);
  if (m) return mountDetail(Number(m[1]));
  return mountList();
}

// ---- 이벤트 (appbody 위임; 검색 debounce / 칩 토글 / 초기화) ----
let searchTimer = null;
function onInput(e) {
  if (e.target && e.target.id === 'ms-search') {
    const val = e.target.value;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { filterState.query = val; renderResults(); }, 180);
  }
}
function toggleChip(el) {
  const facet = el.dataset.facet, value = el.dataset.value;
  if (!filterState[facet]) return;
  const i = filterState[facet].indexOf(value);
  if (i >= 0) filterState[facet].splice(i, 1); else filterState[facet].push(value);
  const on = filterState[facet].includes(value);
  el.classList.toggle('active', on);
  el.setAttribute('aria-pressed', on ? 'true' : 'false');
  renderResults();
}
function doReset() {
  clearTimeout(searchTimer);
  resetFilter();
  const s = document.getElementById('ms-search'); if (s) s.value = '';
  document.querySelectorAll('#ms-controls .fchip.active').forEach((c) => { c.classList.remove('active'); c.setAttribute('aria-pressed', 'false'); });
  renderResults();
}
function onClick(e) {
  const chip = e.target.closest && e.target.closest('[data-facet]');
  if (chip) return toggleChip(chip);
  const reset = e.target.closest && e.target.closest('[data-action="reset"]');
  if (reset) return doReset();
}

async function init() {
  try { state.data = await loadData(); }
  catch (e) { state.error = true; if (window.console) console.error('[MediStack] load failed:', e.message); }
  // alias 는 부가기능: 실패해도 앱 정상(relation-only 검색). 치명 아님.
  try {
    const aliasData = await loadAliases();
    aliasIndex = buildAliasIndex(aliasData);
    if (!aliasData && window.console) console.warn('[MediStack] alias load skipped (search uses relations only)');
  } catch (e) { aliasIndex = []; }
  // full drug index 도 부가기능: 실패해도 앱 정상(name_only 미표시로 degrade). 치명 아님.
  try {
    const fullData = await loadFullIndex();
    nameOnlyIndex = buildNameOnlyIndex(fullData);
    nameOnlyNotice = (fullData && fullData.meta && typeof fullData.meta.name_only_notice === 'string') ? fullData.meta.name_only_notice : '';
    if (!fullData && window.console) console.warn('[MediStack] full index load skipped (name_only disabled)');
  } catch (e) { nameOnlyIndex = []; }
  body().addEventListener('input', onInput);
  body().addEventListener('click', onClick);
  route();
  window.addEventListener('hashchange', route);
}

init();
