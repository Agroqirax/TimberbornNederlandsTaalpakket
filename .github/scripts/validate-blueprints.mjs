#!/usr/bin/env node

/**
 * Blueprint validator
 *
 *  Validates all .json files in the repo against their matching schemas
 *
 * Uses schemas from https://raw.githubusercontent.com/agroqirax/timberborn-schemas/main/catalog.json
 *
 * Usage:
 *   node validate-blueprintss.js
 */

import { readFileSync, readdirSync, statSync } from "fs";
import { resolve, relative, join } from "path";
import Ajv from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

// ─── Exclusions ───────────────────────────────────────────────────────────────

const EXCLUDED_DIRS = new Set([
  "node_modules",
  ".git",
  ".svn",
  ".hg",
  ".vscode",
  ".idea",
  ".DS_Store",
  "dist",
  "build",
  "out",
  "coverage",
  ".nyc_output",
  ".cache",
  ".turbo",
  ".next",
  ".nuxt",
]);

const EXCLUDED_FILES = new Set([
  "package.json",
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  "npm-shrinkwrap.json",
  "tsconfig.json",
  "jsconfig.json",
  ".eslintrc.json",
  ".prettierrc.json",
  ".babelrc.json",
  "renovate.json",
  ".renovaterc.json",
]);

// ─── Helpers ──────────────────────────────────────────────────────────────────

function walk(dir) {
  const results = [];
  for (const name of readdirSync(dir)) {
    if (EXCLUDED_DIRS.has(name)) continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) {
      results.push(...walk(full));
    } else {
      if (!EXCLUDED_FILES.has(name)) results.push(full);
    }
  }
  return results;
}

/**
 * Convert a catalog fileMatch glob pattern to a RegExp.
 *
 * Supported syntax:
 *   *   → any segment character except /
 *   **  → zero or more path segments (greedy)
 *
 * Paths are matched from the repo root, always starting with /.
 */
function globToRegex(pattern) {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*\*/g, "§GLOBSTAR§")
    .replace(/\*/g, "[^/]*")
    .replace(/§GLOBSTAR§/g, ".*");
  return new RegExp(escaped + "$");
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
  return res.json();
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const ajv = new Ajv({
    strict: false,
    allErrors: true,
    loadSchema: fetchJSON,
  });
  addFormats(ajv);

  const catalogUrl =
    "https://raw.githubusercontent.com/agroqirax/timberborn-schemas/main/catalog.json";
  const catalog = await fetchJSON(catalogUrl);

  const rules = catalog.schemas.flatMap((entry) =>
    (entry.fileMatch ?? []).map((pat) => ({
      regex: globToRegex(pat),
      schemaUrl: entry.url,
      name: entry.name,
    })),
  );

  const root = resolve(process.argv[2] ?? ".");
  const allFiles = walk(root).filter((f) => f.endsWith(".json"));

  if (allFiles.length === 0) {
    console.warn("::warning:: No blueprints found");
    process.exit(0);
  }

  let passed = 0;
  let failed = 0;
  let skipped = 0;

  const validatorCache = new Map();

  for (const absPath of allFiles) {
    const rel = "/" + relative(root, absPath).replace(/\\/g, "/");
    const rule = rules.find((r) => r.regex.test(rel));

    if (!rule) {
      console.log(`::notice:: ${rel} No matching schema`);
      skipped++;
      continue;
    }

    let data;
    try {
      data = JSON.parse(readFileSync(absPath, "utf8"));
    } catch (e) {
      console.error(`::error:: ${rel} Invalid JSON: ${e.message}`);
      failed++;
      continue;
    }

    let validate = validatorCache.get(rule.schemaUrl);
    if (!validate) {
      try {
        const schema = await fetchJSON(rule.schemaUrl);
        validate = await ajv.compileAsync(schema);
        validatorCache.set(rule.schemaUrl, validate);
      } catch (e) {
        console.error(
          `::error:: ${rel} Could not compile schema "${rule.name}": ${e.message}`,
        );
        failed++;
        continue;
      }
    }

    if (validate(data)) {
      passed++;
    } else {
      console.error(`::error:: ${rel} [${rule.name}]`);
      for (const err of validate.errors ?? []) {
        const where = err.instancePath || "(root)";
        console.error(`            ${where}: ${err.message}`);
      }
      failed++;
    }
  }

  if (failed > 0) process.exit(1);
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
