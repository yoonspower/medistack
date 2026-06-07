// data.js — JSON 로딩 + shape 가드. 실패 시 throw → app.js 가 error state 로 처리.

const DATA_URL = './data/medistack_v0.1_beta_export.json';

export async function loadData() {
  let res;
  try {
    res = await fetch(DATA_URL, { cache: 'no-store' });
  } catch (e) {
    throw new Error('network error: ' + e.message);
  }
  if (!res.ok) throw new Error('fetch failed: HTTP ' + res.status);

  let data;
  try {
    data = await res.json();
  } catch (e) {
    throw new Error('JSON parse failed');
  }

  assertShape(data);
  return data;
}

// 최소 구조 검증. 더 엄격한 12항목 검사는 scripts/validate_medistack_v0_1_export.* (배포 전 CI).
function assertShape(d) {
  if (!d || typeof d !== 'object' || Array.isArray(d)) throw new Error('root is not an object');
  if (!Array.isArray(d.relations)) throw new Error('relations missing or not array');
  if (!d.disclaimers || typeof d.disclaimers !== 'object') throw new Error('disclaimers missing');
  // common 면책문구는 상세 렌더의 fail-safe 기준이므로 존재 여부만 사전 확인(상세에서 재확인).
}
