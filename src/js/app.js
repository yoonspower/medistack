// app.js — entry. 데이터 로드 → 해시 라우팅. 실패/0건/누락 시 안전 state.
import { loadData } from './data.js';
import { getRenderableRelations, findRelation, commonDisclaimer } from './guards.js';
import { renderList, renderDetail } from './render.js';
import { renderEmpty, renderError } from './states.js';

const appbar = () => document.getElementById('appbar');
const body = () => document.getElementById('appbody');

const state = { data: null, error: false };

const BETA_TAG = '<span class="beta">베타 · 참고 정보</span>';
function setAppbar(detail) {
  appbar().innerHTML = detail
    ? '<a class="back" href="#/">‹ 목록</a>' + BETA_TAG
    : '<span class="brand">MediStack</span>' + BETA_TAG;
}

function mountError() {
  setAppbar(false);
  body().innerHTML = renderError();
}
function mountEmpty() {
  setAppbar(false);
  body().innerHTML = renderEmpty(state.data);
}
function mountList() {
  setAppbar(false);
  body().innerHTML = renderList(state.data);
  body().scrollTop = 0;
}
function mountDetail(id) {
  const rel = findRelation(state.data, id);
  // fail-safe: 관계 없음(또는 excluded/15행/누락) 또는 공통 면책문구 없음 → error
  if (!rel || !commonDisclaimer(state.data)) return mountError();
  setAppbar(true);
  body().innerHTML = renderDetail(rel, state.data);
  body().scrollTop = 0;
}

function route() {
  if (state.error || !state.data) return mountError();
  if (getRenderableRelations(state.data).length === 0) return mountEmpty();

  const m = location.hash.match(/^#\/r\/(\d+)$/);
  if (m) return mountDetail(Number(m[1]));
  return mountList();
}

async function init() {
  try {
    state.data = await loadData();
  } catch (e) {
    state.error = true;
    if (window.console) console.error('[MediStack] load failed:', e.message);
  }
  route();
  window.addEventListener('hashchange', route);
}

init();
