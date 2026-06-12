// data.js — JSON 로딩 + shape 가드. 실패 시 throw → app.js 가 error state 로 처리.

const DATA_URL = './data/medistack_v0.2_beta_export.json';
// alias 는 relation 과 독립된 별도 파일. 검색 보조 전용. DATA_URL 과 분리.
const ALIAS_URL = './data/medistack_v0.3_aliases.json';
// full drug name index: relation 없는 약의 '품목명 확인'용 별도 파일. alias 와 동일 fail-soft. DATA_URL/relation 과 분리.
const FULL_INDEX_URL = './data/full_drug_name_index_sample_v1_0.json';

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

// alias 로딩 (fail-soft): 실패/HTTP≠200/파싱오류/shape 불일치 → null 반환(앱은 relation-only 검색 유지).
// relation 로드와 달리 alias 실패는 치명 아님 → throw 하지 않는다.
export async function loadAliases() {
  try {
    const res = await fetch(ALIAS_URL, { cache: 'no-store' });
    if (!res.ok) return null;
    const d = await res.json();
    if (!d || typeof d !== 'object' || Array.isArray(d)) return null;
    if (!Array.isArray(d.ingredient_aliases) && !Array.isArray(d.product_aliases)) return null;
    return d;
  } catch (e) {
    return null;
  }
}

// full drug index 로딩 (fail-soft): 실패/HTTP≠200/파싱오류/shape 불일치 → null(앱은 name_only 미표시로 degrade).
// alias 와 동일하게 치명 아님 → throw 하지 않는다. relation 검색은 영향 없음.
export async function loadFullIndex() {
  try {
    const res = await fetch(FULL_INDEX_URL, { cache: 'no-store' });
    if (!res.ok) return null;
    const d = await res.json();
    if (!d || typeof d !== 'object' || Array.isArray(d)) return null;
    if (!Array.isArray(d.entries)) return null;
    return d;
  } catch (e) {
    return null;
  }
}

// 최소 구조 검증. 더 엄격한 12항목 검사는 scripts/validate_medistack_v0_1_export.* (배포 전 CI).
function assertShape(d) {
  if (!d || typeof d !== 'object' || Array.isArray(d)) throw new Error('root is not an object');
  if (!Array.isArray(d.relations)) throw new Error('relations missing or not array');
  if (!d.disclaimers || typeof d.disclaimers !== 'object') throw new Error('disclaimers missing');
  // common 면책문구는 상세 렌더의 fail-safe 기준이므로 존재 여부만 사전 확인(상세에서 재확인).
}
