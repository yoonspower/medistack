// render.js — list / detail 렌더. guards 의 규칙을 사용. 의학 단정/지시/구매유도 카피 금지.
import { getRenderableRelations, canShowProduct, showPotassiumNotice, commonDisclaimer, potassiumNotice } from './guards.js';

const ACTION = {
  separation: { label: '복용 간격', chip: 'chip-sep', aClass: '', kicker: '같은 시간대 복용 주의' },
  monitoring: { label: '상태 모니터링', chip: 'chip-mon', aClass: 'mon', kicker: '장기 복용 시 상태 확인' },
};

export function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

// 목록: relations 19건만. excluded_v0_1 미사용. published/clinical/evidence 뱃지 없음.
export function renderList(data) {
  const rels = getRenderableRelations(data);
  const footer = data.disclaimers && data.disclaimers.card_footer;
  let h = '<div class="listhead">약-영양소 참고 정보 · ' + rels.length + '건</div>';
  for (const r of rels) {
    const a = ACTION[r.recommended_action] || { label: '', chip: 'chip-mon' };
    h +=
      '<a class="row" href="#/r/' + encodeURIComponent(r.id) + '">' +
      '<span class="pair"><span class="ing">' + esc(r.ingredient) + '</span><span class="x">×</span><span class="nut">' + esc(r.nutrient) + '</span></span>' +
      '<span class="chip ' + a.chip + '">' + esc(a.label) + '</span>' +
      '<svg class="chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg>' +
      '</a>';
  }
  if (footer) h += '<div class="listfooter">' + esc(footer) + '</div>';
  return h;
}

// 상세: rel 은 호출 전 findRelation 으로 확보, common 은 commonDisclaimer 로 확보(둘 중 하나라도 없으면 호출측에서 error).
export function renderDetail(rel, data) {
  const a = ACTION[rel.recommended_action] || { label: '', aClass: '', kicker: '' };
  const common = commonDisclaimer(data);

  let h =
    '<div class="dh"><div class="kicker">' + esc(a.kicker) + '</div>' +
    '<h2>' + esc(rel.ingredient) + '<span class="x">×</span>' + esc(rel.nutrient) + '</h2></div>' +
    '<div class="alabel ' + a.aClass + '"><span class="dot"></span>' + esc(a.label) + '</div>' +
    '<div class="bodytext">' + esc(rel.display_text_ko) + '</div>';

  // 가이드(management_ko) — 상담/확인 톤
  if (rel.management_ko) {
    h += '<div class="guide"><div class="gt">참고 안내</div><p>' + esc(rel.management_ko) + '</p></div>';
  }

  // 칼륨 고지 — potassium_safety_card === true 일 때만
  const kNotice = potassiumNotice(data);
  if (showPotassiumNotice(rel) && kNotice) {
    h +=
      '<div class="kbox">' +
      '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>' +
      '<div><div class="kt">칼륨 주의</div><p>' + esc(kNotice) + '</p></div></div>';
  }

  // 제품 영역 — canShowProduct 시에만(v0.1 미도달). 칼륨은 product_link_allowed=false 로 차단.
  if (canShowProduct(rel)) {
    // v0.1 에서는 여기 진입하지 않음. v0.2 제품 트랙에서 구현.
  }

  // 출처 — 식약처 nedrug 원문 링크(제품 링크 아님)
  if (rel.source) {
    h += '<div class="src"><span class="lab">출처</span> · ' + esc(rel.source.type || '식약처 허가사항');
    if (rel.source.url) h += ' &nbsp;<a href="' + esc(rel.source.url) + '" target="_blank" rel="noopener">원문 보기 ↗</a>';
    if (rel.source.pointer) h += '<details><summary>출처 상세</summary><div class="ptr">' + esc(rel.source.pointer) + '</div></details>';
    h += '</div>';
  }

  // 공통 면책문구 — 모든 상세 하단 고정
  h += '<div class="disc">' + esc(common) + '</div>';
  return h;
}
