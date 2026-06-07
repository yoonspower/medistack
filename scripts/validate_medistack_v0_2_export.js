#!/usr/bin/env node
/*
 * validate_medistack_v0_2_export.js
 * MediStack v0.2 beta export contract validator (Node, no deps). v0.1 검증기와 분리.
 *
 * 사용: node validate_medistack_v0_2_export.js [path/to/medistack_v0.2_beta_export.json]
 * 종료 코드: 0 = PASS, 1 = FAIL
 */
"use strict";
const fs = require("fs");

const DEFAULT_PATH = "medistack_v0.2_beta_export.json";
const EXPECTED_TOP_KEYS = ["meta", "disclaimers", "relations", "excluded_v0_1"];
const MIN_RELATIONS = 19;
const ALLOWED_EVIDENCE = new Set(["high", "moderate"]);
const ALLOWED_ACTION = new Set(["separation", "monitoring"]);
const ALLOWED_MECHANISM = new Set(["absorption", "depletion"]);
const FORBIDDEN_RELATION_FIELDS = ["status", "published", "clinical_reviewed"];
const POTASSIUM_NUTRIENT = "칼륨";
const PRODUCT_FIELD_HINT = /(product|affiliate|shop|buy|store|purchase|cart)/i;
const PRODUCT_FIELD_SAFE = new Set(["product_link_allowed"]);

const passes = [], fails = [];
const check = (ok, no, title, detail = "") => { ok ? passes.push([no, title]) : fails.push([no, title, detail]); return ok; };
const isObj = (o) => o !== null && typeof o === "object" && !Array.isArray(o);
const rid = (o) => (isObj(o) ? (("id" in o) ? o.id : ("row_id" in o ? o.row_id : null)) : null);
const nonempty = (v) => {
  if (v === null || v === undefined) return false;
  if (typeof v === "string") return v.trim() !== "";
  if (Array.isArray(v)) return v.length > 0;
  if (typeof v === "object") return Object.keys(v).length > 0;
  return true;
};

function main(path) {
  let data;
  try { data = JSON.parse(fs.readFileSync(path, "utf-8")); }
  catch (e) { console.log(`[FATAL] 파일 없음/파싱 실패: ${e.message}`); return 1; }
  if (!isObj(data)) { console.log("[FATAL] 최상위가 객체 아님"); return 1; }

  const keys = Object.keys(data);
  const miss = EXPECTED_TOP_KEYS.filter((k) => !keys.includes(k));
  const extra = keys.filter((k) => !EXPECTED_TOP_KEYS.includes(k));
  check(miss.length === 0 && extra.length === 0, 1, "top-level keys",
    (miss.length || extra.length) ? `missing=[${miss}] extra=[${extra}]` : "");

  const meta = data.meta, disc = data.disclaimers, rels = data.relations, excl = data.excluded_v0_1;
  const metaOk = isObj(meta), discOk = isObj(disc), relsOk = Array.isArray(rels), exclOk = Array.isArray(excl);
  const tp = [];
  if (!metaOk) tp.push("meta!=object");
  if (!discOk) tp.push("disclaimers!=object");
  if (!relsOk) tp.push("relations!=array");
  if (!exclOk) tp.push("excluded_v0_1!=array");
  check(tp.length === 0, 0, "JSON 파싱/타입", tp.join("; "));

  if (relsOk) check(rels.length >= MIN_RELATIONS, 2, `relations >= ${MIN_RELATIONS} (baseline)`, `실제 ${rels.length}`);
  if (relsOk && metaOk) check(meta.relation_count === rels.length, 3, "meta.relation_count == len(relations)", `meta=${meta.relation_count} actual=${rels.length}`);
  if (exclOk && metaOk) check(meta.excluded_count === excl.length, 4, "meta.excluded_count == len(excluded_v0_1)", `meta=${meta.excluded_count} actual=${excl.length}`);

  if (metaOk) {
    check(meta.published === false, 5, "meta.published === false", `값=${JSON.stringify(meta.published)}`);
    check(meta.clinical_reviewed === false, 6, "meta.clinical_reviewed === false", `값=${JSON.stringify(meta.clinical_reviewed)}`);
  }

  if (relsOk) {
    const req = ["id", "ingredient", "nutrient", "recommended_action", "display_text_ko"];
    const missRows = [], forb = [], ids = [];
    for (const r of rels) {
      if (!isObj(r)) { missRows.push("non-object"); continue; }
      if (!req.every((k) => nonempty(r[k]))) missRows.push(rid(r));
      const bad = FORBIDDEN_RELATION_FIELDS.filter((k) => k in r);
      if (bad.length) forb.push(`id${rid(r)}:[${bad}]`);
      ids.push(rid(r));
    }
    const dups = [...new Set(ids.filter((i) => ids.filter((x) => x === i).length > 1))].sort();
    check(missRows.length === 0 && forb.length === 0 && dups.length === 0, 7,
      "relation 필수필드/고유id/금지필드 없음", `missing=[${missRows}] forbidden=[${forb}] dup_ids=[${dups}]`);
  }

  if (relsOk && exclOk) {
    const relIds = new Set(rels.filter(isObj).map(rid));
    const leak = excl.filter((e) => relIds.has(rid(e))).map(rid);
    const badE = excl.map((e, i) => (isObj(e) && nonempty(e.ingredient) && nonempty(e.nutrient) && rid(e) !== null ? -1 : i)).filter((i) => i >= 0);
    check(leak.length === 0 && badE.length === 0, 8, "excluded_v0_1 무결성", `leak=[${leak}] malformed_idx=[${badE}]`);
  }

  if (discOk) check(nonempty(disc.common), 9, "disclaimers.common 존재", nonempty(disc.common) ? "" : "없음/빈값");

  if (discOk && relsOk) {
    const hasK = rels.some((r) => isObj(r) && r.potassium_safety_card === true);
    const ok10 = !hasK || nonempty(disc.potassium_notice);
    check(ok10, 10, "disclaimers.potassium_notice (칼륨 행 있으면 필수)", ok10 ? "" : "칼륨 행 있는데 potassium_notice 없음");
  }

  if (relsOk) {
    const prob = [];
    for (const r of rels) {
      if (!isObj(r)) continue;
      const isK = r.nutrient === POTASSIUM_NUTRIENT;
      const card = r.potassium_safety_card === true;
      const linkFalse = r.product_link_allowed === false;
      if (isK && !(linkFalse && card)) prob.push(`id${rid(r)}(칼륨): link_false=${linkFalse} card=${card}`);
      if (card && !linkFalse) prob.push(`id${rid(r)}: card=true인데 link!=false`);
    }
    check(prob.length === 0, 11, "칼륨 일관성", prob.join("; "));
  }

  if (relsOk) {
    const viol = [];
    for (const r of rels) {
      if (!isObj(r)) continue;
      for (const k of Object.keys(r)) {
        if (PRODUCT_FIELD_SAFE.has(k)) continue;
        if (PRODUCT_FIELD_HINT.test(k) && nonempty(r[k])) viol.push(`id${rid(r)} '${k}'`);
      }
    }
    check(viol.length === 0, 12, "제품/제휴 필드 전면 금지(v0.2)", viol.join("; "));
  }

  if (relsOk) {
    const bad = [];
    for (const r of rels) {
      if (!isObj(r)) continue;
      if (r.evidence_level != null && !ALLOWED_EVIDENCE.has(r.evidence_level)) bad.push(`id${rid(r)} evidence=${r.evidence_level}`);
      if (r.recommended_action != null && !ALLOWED_ACTION.has(r.recommended_action)) bad.push(`id${rid(r)} action=${r.recommended_action}`);
      if (r.mechanism != null && !ALLOWED_MECHANISM.has(r.mechanism)) bad.push(`id${rid(r)} mechanism=${r.mechanism}`);
    }
    check(bad.length === 0, 13, "enum 경계(evidence/action/mechanism)", bad.join("; "));
  }

  if (relsOk) {
    const rc = rels.filter((r) => isObj(r) && r.requires_clinical_review === true).map(rid);
    check(rc.length === 0, 14, "requires_clinical_review=true 행 없음", rc.length ? `위반 id=[${rc}]` : "");
  }

  const total = passes.length + fails.length;
  const overall = fails.length === 0 ? "PASS" : "FAIL";
  const bar = "=".repeat(64);
  console.log(bar); console.log(`MediStack v0.2 export 검증: ${path}`); console.log(bar);
  if (fails.length) {
    console.log(`\n[FAIL] ${fails.length}건`);
    fails.sort((a, b) => a[0] - b[0]).forEach(([no, title, detail]) =>
      console.log(`  X #${String(no).padEnd(2)} ${title}` + (detail ? `\n         -> ${detail}` : "")));
  } else {
    console.log("\n모든 검증 통과.");
  }
  console.log(`\nRESULT: ${overall}  (${passes.length}/${total} checks passed)`); console.log(bar);
  return overall === "PASS" ? 0 : 1;
}

process.exit(main(process.argv[2] || DEFAULT_PATH));
