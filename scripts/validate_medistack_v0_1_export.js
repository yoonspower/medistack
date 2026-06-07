#!/usr/bin/env node
/*
 * validate_medistack_v0_1_export.js
 * MediStack v0.1 beta export contract validator (Node, no deps).
 *
 * 사용:
 *   node validate_medistack_v0_1_export.js [path/to/medistack_v0.1_beta_export.json]
 *
 * 종료 코드: 0 = PASS, 1 = FAIL
 */
"use strict";
const fs = require("fs");

const DEFAULT_PATH = "medistack_v0.1_beta_export.json";
const EXPECTED_TOP_KEYS = ["meta", "disclaimers", "relations", "excluded_v0_1"];
const EXPECTED_RELATIONS = 19;
const EXCLUDED_ID = 15;
const EXCLUDED_INGREDIENT = "에스오메프라졸";
const EXCLUDED_NUTRIENT = "비타민B12";
const POTASSIUM_NUTRIENT = "칼륨";
const POTASSIUM_IDS = [17, 19];
const FORBIDDEN_RELATION_FIELDS = ["status", "published", "clinical_reviewed"];
const PRODUCT_FIELD_HINT = /(product|affiliate|shop|buy)/i;
const PRODUCT_FIELD_SAFE = new Set(["product_link_allowed"]);

const passes = [];
const failures = [];
function check(ok, no, title, detail = "") {
  if (ok) passes.push([no, title]);
  else failures.push([no, title, detail]);
  return ok;
}
function rid(o) {
  if (o === null || typeof o !== "object" || Array.isArray(o)) return null;
  if ("id" in o) return o.id;
  if ("row_id" in o) return o.row_id;
  return null;
}
function isPlainObj(o) {
  return o !== null && typeof o === "object" && !Array.isArray(o);
}
function nonempty(v) {
  if (v === null || v === undefined) return false;
  if (typeof v === "string") return v.trim() !== "";
  if (Array.isArray(v)) return v.length > 0;
  if (typeof v === "object") return Object.keys(v).length > 0;
  return true;
}
function setEq(a, b) {
  const A = new Set(a), B = new Set(b);
  if (A.size !== B.size) return false;
  for (const x of A) if (!B.has(x)) return false;
  return true;
}

function main(path) {
  let raw, data;
  try {
    raw = fs.readFileSync(path, "utf-8");
  } catch (e) {
    console.log(`[FATAL] 파일 없음/읽기 실패: ${path}`);
    return 1;
  }
  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.log(`[FATAL] JSON 파싱 실패: ${e.message}`);
    return 1;
  }
  if (!isPlainObj(data)) {
    console.log("[FATAL] 최상위가 객체가 아님");
    return 1;
  }

  // 1) top-level keys
  const keys = Object.keys(data);
  const missing = EXPECTED_TOP_KEYS.filter((k) => !keys.includes(k));
  const extra = keys.filter((k) => !EXPECTED_TOP_KEYS.includes(k));
  check(missing.length === 0 && extra.length === 0, 1,
    "top-level keys (meta/disclaimers/relations/excluded_v0_1)",
    missing.length || extra.length ? `missing=[${missing}] extra=[${extra}]` : "");

  const meta = data.meta, disc = data.disclaimers, rels = data.relations, excl = data.excluded_v0_1;

  // 12) 타입 가드
  const metaOk = isPlainObj(meta), discOk = isPlainObj(disc),
        relsOk = Array.isArray(rels), exclOk = Array.isArray(excl);
  const tp = [];
  if (!metaOk) tp.push("meta!=object");
  if (!discOk) tp.push("disclaimers!=object");
  if (!relsOk) tp.push("relations!=array");
  if (!exclOk) tp.push("excluded_v0_1!=array");
  check(tp.length === 0, 12, "JSON 파싱/타입", tp.join("; "));

  // 2) relations length = 19
  if (relsOk) check(rels.length === EXPECTED_RELATIONS, 2, "relations length = 19", `실제 ${rels.length}건`);

  // 3) excluded = 15행 1건
  if (exclOk) {
    const e15 = excl.filter((e) => rid(e) === EXCLUDED_ID);
    const ok3 = excl.length === 1 && e15.length === 1 && isPlainObj(e15[0]) &&
      e15[0].ingredient === EXCLUDED_INGREDIENT && e15[0].nutrient === EXCLUDED_NUTRIENT;
    check(ok3, 3, "excluded_v0_1 = 15행(에스오메프라졸×비타민B12) 1건",
      ok3 ? "" : `excluded ${excl.length}건 / 15행 매칭 ${e15.length}건`);
  }

  // 4) relations에 15 없음
  if (relsOk) {
    const leaked = rels.filter((r) => rid(r) === EXCLUDED_ID);
    check(leaked.length === 0, 4, "relations에 row_id 15 미포함", leaked.length ? `15행 누출 ${leaked.length}건` : "");
  }

  // 5/6) meta 봉인
  if (metaOk) {
    check(meta.published === false, 5, "meta.published === false", `값=${JSON.stringify(meta.published)}`);
    check(meta.clinical_reviewed === false, 6, "meta.clinical_reviewed === false", `값=${JSON.stringify(meta.clinical_reviewed)}`);
  }

  // 7) relation 금지 필드 없음
  if (relsOk) {
    const offenders = [];
    for (const r of rels) {
      if (isPlainObj(r)) {
        const bad = FORBIDDEN_RELATION_FIELDS.filter((k) => k in r);
        if (bad.length) offenders.push(`id${rid(r)}:[${bad}]`);
      }
    }
    check(offenders.length === 0, 7, "relation에 status/published/clinical_reviewed 필드 없음",
      offenders.length ? `위반 ${offenders.join(", ")}` : "");
  }

  // 8/9) disclaimers
  if (discOk) {
    check(nonempty(disc.common), 8, "disclaimers.common 존재", nonempty(disc.common) ? "" : "비어있거나 없음");
    check(nonempty(disc.potassium_notice), 9, "disclaimers.potassium_notice 존재", nonempty(disc.potassium_notice) ? "" : "비어있거나 없음");
  }

  // 10) 칼륨 17·19
  if (relsOk) {
    const kRels = rels.filter((r) => isPlainObj(r) && r.nutrient === POTASSIUM_NUTRIENT);
    const kIds = kRels.map(rid);
    const problems = [];
    if (!setEq(kIds, POTASSIUM_IDS)) problems.push(`칼륨 id집합=[${kIds.sort()}] (기대 [${POTASSIUM_IDS}])`);
    for (const r of kRels) {
      if (r.product_link_allowed !== false) problems.push(`id${rid(r)} product_link_allowed=${JSON.stringify(r.product_link_allowed)}`);
      if (r.potassium_safety_card !== true) problems.push(`id${rid(r)} potassium_safety_card=${JSON.stringify(r.potassium_safety_card)}`);
    }
    check(problems.length === 0, 10, "칼륨 17·19 product_link_allowed=false & potassium_safety_card=true", problems.join("; "));
  }

  // 11) blocked 행 제품필드 없음 + 칼륨카드 일관성
  if (relsOk) {
    const viol = [];
    for (const r of rels) {
      if (isPlainObj(r) && r.product_link_allowed === false) {
        for (const k of Object.keys(r)) {
          if (PRODUCT_FIELD_SAFE.has(k)) continue;
          if (PRODUCT_FIELD_HINT.test(k) && nonempty(r[k])) viol.push(`id${rid(r)} '${k}'=${JSON.stringify(r[k])}`);
        }
      }
    }
    const inconsist = rels.filter((r) => isPlainObj(r) && r.potassium_safety_card === true && r.product_link_allowed !== false).map(rid);
    if (inconsist.length) viol.push(`potassium_safety_card=true인데 link!=false: id[${inconsist}]`);
    check(viol.length === 0, 11, "product_link_allowed=false 행에 제품링크/예시 필드 없음", viol.join("; "));
  }

  // ---- 출력 ----
  const total = passes.length + failures.length;
  const overall = failures.length === 0 ? "PASS" : "FAIL";
  const bar = "=".repeat(62);
  console.log(bar);
  console.log(`MediStack v0.1 export 검증: ${path}`);
  console.log(bar);
  if (failures.length) {
    console.log(`\n[FAIL] ${failures.length}건`);
    failures.sort((a, b) => a[0] - b[0]).forEach(([no, title, detail]) => {
      console.log(`  X #${String(no).padEnd(2)} ${title}` + (detail ? `\n         -> ${detail}` : ""));
    });
  } else {
    console.log("\n모든 검증 통과.");
  }
  console.log(`\nRESULT: ${overall}  (${passes.length}/${total} checks passed)`);
  console.log(bar);
  return overall === "PASS" ? 0 : 1;
}

process.exit(main(process.argv[2] || DEFAULT_PATH));
