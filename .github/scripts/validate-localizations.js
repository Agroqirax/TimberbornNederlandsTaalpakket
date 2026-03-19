#!/usr/bin/env node

/**
 * Localization File Validator
 *
 * Validates all .txt/.csv files anywhere inside a /localizations or
 * /Localizations directory tree (including nested subdirectories).
 *
 *   1. Filename matches: [a-z]{2}[A-Z]{2}(_.*)?\.(txt|csv)
 *   2. Header row is exactly: ID,Text,Comment
 *   3. ID must not be empty (error) and Text must not be empty (warning)
 *   4. At least one file must start with "enUS" (warning)
 *   5. Per locales warning if it's missing IDs present in any other locale
 *
 * Handles multiline values wrapped in double-quotes per RFC 4180.
 *
 * Usage:
 *   node validate-localizations.js [rootDir]
 *
 * rootDir defaults to the current working directory.
 */

const fs = require("fs");
const path = require("path");

// ─── Config ───────────────────────────────────────────────────────────────────

const LOCALIZATION_DIR_NAME_RE = /^[Ll]ocalizations$/;
const FILENAME_RE = /^[a-z]{2}[A-Z]{2}(_.*)?\.(txt|csv)$/;
const REQUIRED_HEADER = ["ID", "Text", "Comment"];

let failed = false;

// ─── File collection ──────────────────────────────────────────────────────────

function collectLocalizationFiles(dir) {
  const results = [];

  function walk(current, insideLocalizationTree) {
    let entries;
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch (err) {
      console.warn(
        `::warning:: Cannot read directory: ${current} — ${err.message}`,
      );
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        const enterTree =
          insideLocalizationTree || LOCALIZATION_DIR_NAME_RE.test(entry.name);
        walk(fullPath, enterTree);
      } else if (entry.isFile() && insideLocalizationTree) {
        results.push(fullPath);
      }
    }
  }

  walk(dir, false);
  return results;
}

// ─── CSV parser ───────────────────────────────────────────────────────────────

function parseCSV(content) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let i = 0;

  // Normalise line endings but keep \n intact — multiline quoted fields rely on
  // \n being preserved inside the loop.
  const text = content.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  while (i < text.length) {
    const ch = text[i];
    const next = text[i + 1];

    if (inQuotes) {
      if (ch === '"' && next === '"') {
        // Escaped double-quote inside a quoted field
        field += '"';
        i += 2;
      } else if (ch === '"') {
        // Closing quote
        inQuotes = false;
        i++;
      } else {
        // Any character inside quotes — including \n — is part of the field
        field += ch;
        i++;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
        i++;
      } else if (ch === ",") {
        row.push(field);
        field = "";
        i++;
      } else if (ch === "\n") {
        // End of a logical row (only when not inside a quoted field)
        row.push(field);
        rows.push(row);
        field = "";
        row = [];
        i++;
      } else {
        field += ch;
        i++;
      }
    }
  }

  // Flush the last field/row (file may not end with \n)
  if (row.length > 0 || field !== "") {
    row.push(field);
    rows.push(row);
  }

  return rows;
}

// ─── Validation ───────────────────────────────────────────────────────────────

/**
 * Validates a single file.
 * Returns the Set of IDs found in the file, or null if the file could not be
 * parsed up to the data rows (so it is excluded from cross-file ID checks).
 *
 * @param {string} filePath
 * @returns {Set<string> | null}
 */
function validateFile(filePath) {
  const name = path.basename(filePath);

  // 1. Filename
  if (!FILENAME_RE.test(name)) {
    console.error(
      `::error:: Filename "${name}" does not match required pattern`,
    );
    failed = true;
  }

  // 2. Content
  let raw;
  try {
    raw = fs.readFileSync(filePath, "utf8");
  } catch (err) {
    console.error(`::error:: Cannot read file ${filePath} ${err.message}`);
    failed = true;
    return null;
  }

  const rows = parseCSV(raw);

  // Drop rows that are the artefact of a trailing newline: a single truly-empty
  // cell. Rows like ["", "", ""] (e.g. ",,\n") must be kept so ID/Text checks
  // can flag them.
  const nonEmpty = rows.filter((r) => !(r.length === 1 && r[0] === ""));

  if (nonEmpty.length === 0) {
    console.error(`::error:: ${filePath} file is empty`);
    failed = true;
    return null;
  }

  // Header
  const header = nonEmpty[0].map((h) => h.trim());
  if (
    header.length < REQUIRED_HEADER.length ||
    !REQUIRED_HEADER.every((col, idx) => header[idx] === col)
  ) {
    console.error(
      `::error:: ${filePath}:0 header does not match required pattern`,
    );
    failed = true;
    return null;
  }

  const idIdx = header.indexOf("ID");
  const textIdx = header.indexOf("Text");

  // Data rows
  const ids = new Set();
  for (let r = 1; r < nonEmpty.length; r++) {
    const rowData = nonEmpty[r];
    const rowNumber = r + 1; // 1-based; row 1 is the header

    const id = (rowData[idIdx] ?? "").trim();
    if (id === "") {
      console.error(`::error:: ${filePath}:${rowNumber} ID column is empty`);
      failed = true;
    } else {
      ids.add(id);
    }

    if ((rowData[textIdx] ?? "").trim() === "") {
      console.warn(`::warning:: ${filePath}:${rowNumber} Text column is empty`);
    }
  }

  return ids;
}

// ─── Cross-file ID consistency check ─────────────────────────────────────────

/**
 * Extracts the language code prefix (e.g. "enUS", "frFR") from a filename.
 * Returns null if the filename doesn't match the expected pattern.
 *
 * @param {string} filePath
 * @returns {string | null}
 */
function langCodeFromPath(filePath) {
  const name = path.basename(filePath);
  const m = name.match(/^([a-z]{2}[A-Z]{2})/);
  return m ? m[1] : null;
}

/**
 * Groups { filePath -> Set<id> } by language code, merging IDs across all
 * files that share the same code, then warns about IDs that are present in at
 * least one group but missing from another.
 *
 * Only the count of missing IDs is reported, not the full list.
 *
 * @param {Record<string, Set<string>>} fileIdMap
 */
function checkIdConsistency(fileIdMap) {
  // ── Build per-language-code ID union ──────────────────────────────────────
  /** @type {Map<string, Set<string>>} */
  const groupIds = new Map();

  for (const [filePath, ids] of Object.entries(fileIdMap)) {
    const lang = langCodeFromPath(filePath);
    if (lang === null) continue; // Filename didn't match pattern — already flagged

    if (!groupIds.has(lang)) groupIds.set(lang, new Set());
    const group = groupIds.get(lang);
    for (const id of ids) group.add(id);
  }

  const groups = [...groupIds.entries()]; // [[lang, Set<id>], …]
  if (groups.length < 2) return; // Nothing to compare across

  // ── Union of all IDs across all groups ───────────────────────────────────
  const allIds = new Set();
  for (const [, ids] of groups) {
    for (const id of ids) allIds.add(id);
  }

  // ── Report missing counts per group ──────────────────────────────────────
  for (const [lang, ids] of groups) {
    let missingCount = 0;
    for (const id of allIds) {
      if (!ids.has(id)) missingCount++;
    }
    if (missingCount > 0) {
      console.warn(
        `::warning:: Language "${lang}" is missing ${missingCount} ID(s) present in other locales`,
      );
    }
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

function main() {
  const rootDir = process.argv[2] ?? process.cwd();
  const files = collectLocalizationFiles(path.resolve(rootDir)).filter((f) =>
    [".txt", ".csv"].includes(path.extname(f).toLowerCase()),
  );

  if (files.length === 0) {
    console.warn("::warning:: No localization files found");
    process.exit(0);
  }

  // ── enUS presence check ──────────────────────────────────────────────────
  const hasEnUS = files.some((f) => path.basename(f).startsWith("enUS"));
  if (!hasEnUS) {
    console.warn(
      "::warning:: No english localization file was found. An English (enUS) base locale is strongly recommended",
    );
  }

  // ── Per-file validation ──────────────────────────────────────────────────
  /** @type {Record<string, Set<string>>} */
  const fileIdMap = {};

  for (const filePath of files) {
    const ids = validateFile(filePath);
    if (ids !== null) {
      fileIdMap[filePath] = ids;
    }
  }

  // ── Cross-locale ID consistency ──────────────────────────────────────────
  checkIdConsistency(fileIdMap);

  process.exit(failed ? 1 : 0);
}

main();
