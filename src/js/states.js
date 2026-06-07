// states.js — empty / error 화면. 안전 카피만. 의학 단정·복용 지시·안심 문구 금지.
import { esc } from './render.js';

const ERROR_COPY = '정보를 불러오지 못했어요. 네트워크 상태를 확인하고 다시 시도해 주세요.';

// empty: 관계 0건. disclaimers.empty_state 사용.
export function renderEmpty(data) {
  const t = (data && data.disclaimers && data.disclaimers.empty_state) || '등록된 참고 정보가 없습니다.';
  return (
    '<div class="state">' +
    '<svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>' +
    '<p>' + esc(t) + '</p></div>'
  );
}

// error: 로드/파싱 실패, fail-safe. 의학 콘텐츠/이전 데이터 렌더 금지 + 재시도.
export function renderError() {
  return (
    '<div class="state">' +
    '<svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 9v4m0 4h.01"/><circle cx="12" cy="12" r="9"/></svg>' +
    '<p>' + esc(ERROR_COPY) + '</p>' +
    '<button class="retry" onclick="location.reload()">다시 시도</button></div>'
  );
}
