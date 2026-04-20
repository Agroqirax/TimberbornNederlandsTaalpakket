#!/usr/bin/env python3
"""
usage: translate.py [-h] --src FILE --lang CODE [--dest FILE] [--workers N] [--update-modlist]

Translate a localization file using Google Translate.

options:
  -h, --help        show this help message and exit
  --src FILE        Source file to translate.
  --lang CODE       Target language code (e.g. fr, de, ja, es).
  --dest FILE       Output file. If omitted, saves to ./Data/Localizations/Plugins/<langcode>_<Id>.csv
  --workers N       Concurrent translation threads (default: 10).
  --update-modlist  Upsert this mod's record in ./modlist.csv
"""

import sys
import csv
import json5
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from deep_translator import GoogleTranslator
from tqdm import tqdm


LOCALE_MAP = {
    "af": "afZA", "ak": "akGH", "sq": "sqAL", "am": "amET", "ar": "arSA", "hy": "hyAM", "as": "asIN", "ay": "ayBO", "az": "azAZ", "bm": "bmML", "eu": "euES", "be": "beBY", "bn": "bnBD", "bho": "bhoBH", "bs": "bsBA", "bg": "bgBG", "ca": "caES", "ceb": "cebPH", "ny": "nyMW", "zh-CN": "zhCN", "zh-TW": "zhTW", "co": "coFR", "hr": "hrHR", "cs": "csCZ", "da": "daDK", "dv": "dvMV", "doi": "doiIN", "nl": "nlNL", "en": "enUS", "eo": "eoEO", "et": "etEE", "ee": "eeGH", "tl": "tlPH", "fi": "fiFI", "fr": "frFR", "fy": "fyNL", "gl": "glES", "ka": "kaGE", "de": "deDE", "el": "elGR", "gn": "gnPY", "gu": "guIN", "ht": "htHT", "ha": "haNG", "haw": "hawUS", "iw": "iwIL", "hi": "hiIN", "hmn": "hmnCN", "hu": "huHU", "is": "isIS", "ig": "igNG", "ilo": "iloPH", "id": "idID", "ga": "gaIE", "it": "itIT", "ja": "jaJP", "jw": "jwID", "kn": "knIN", "kk": "kkKZ", "km": "kmKH", "rw": "rwRW", "gom": "gomIN", "ko": "koKR", "kri": "kriSL", "ku": "kuTR", "ckb": "ckbIQ", "ky": "kyKG", "lo": "loLA", "la": "laVA", "lv": "lvLV", "ln": "lnCD", "lt": "ltLT", "lg": "lgUG", "lb": "lbLU", "mk": "mkMK", "mai": "maiIN", "mg": "mgMG", "ms": "msMY", "ml": "mlIN", "mt": "mtMT", "mi": "miNZ", "mr": "mrIN", "mni-Mtei": "mniIN", "lus": "lusIN", "mn": "mnMN", "my": "myMM", "ne": "neNP", "no": "noNO", "or": "orIN", "om": "omET", "ps": "psAF", "fa": "faIR", "pl": "plPL", "pt": "ptPT", "pa": "paIN", "qu": "quPE", "ro": "roRO", "ru": "ruRU", "sm": "smWS", "sa": "saIN", "gd": "gdGB", "nso": "nsoZA", "sr": "srRS", "st": "stZA", "sn": "snZW", "sd": "sdPK", "si": "siLK", "sk": "skSK", "sl": "slSI", "so": "soSO", "es": "esES", "su": "suID", "sw": "swKE", "sv": "svSE", "tg": "tgTJ", "ta": "taIN", "tt": "ttRU", "te": "teIN", "th": "thTH", "ti": "tiET", "ts": "tsZA", "tr": "trTR", "tk": "tkTM", "uk": "ukUA", "ur": "urPK", "ug": "ugCN", "uz": "uzUZ", "vi": "viVN", "cy": "cyGB", "xh": "xhZA", "yi": "yiIL", "yo": "yoNG", "zu": "zuZA",
}


def load_manifest(src: Path) -> dict:
    """Load ../manifest.json relative to the source CSV file."""
    manifest_path = src.resolve().parent.parent / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    with open(manifest_path, encoding="utf-8-sig") as f:
        return json5.load(f)


def load_workshop_data(src: Path) -> dict | None:
    """Load ../workshop_data.json relative to CSV file."""
    workshop_data_path0 = src.resolve().parent.parent / "workshop_data.json"
    workshop_data_path1 = src.resolve().parent.parent.parent / "workshop_data.json"
    if workshop_data_path0.exists():
        with open(workshop_data_path0, encoding="utf-8-sig") as f:
            return json5.load(f)
    elif workshop_data_path1.exists():
        with open(workshop_data_path1, encoding="utf-8-sig") as f:
            return json5.load(f)
    else:
        return None


MODLIST_PATH = Path("./modlist.csv")
MODLIST_FIELDS = ["Name", "ID", "SteamLink", "ModIoLink", "Version", "Comment"]
LOCALIZATION_FIELDS = ["ID", "Text", "Comment"]


def update_modlist(manifest: dict, workshop_data: dict | None = None) -> None:
    """Upsert a record in ./modlist.csv from manifest data (matched on ID)."""
    mod_id = str(manifest.get("Id", "")).strip()
    mod_name = str(manifest.get("Name", "")).strip()
    mod_version = str(manifest.get("Version", "")).strip()

    if MODLIST_PATH.exists():
        with open(MODLIST_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    found = False
    for row in rows:
        if str(row.get("ID", "")).strip() == mod_id:
            row["Name"] = mod_name
            row["Version"] = mod_version
            if workshop_data:
                row["SteamLink"] = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_data["ItemId"]}"
            found = True
            break

    if not found:
        new_row: dict = {field: "" for field in MODLIST_FIELDS}
        new_row["ID"] = mod_id
        new_row["Name"] = mod_name
        new_row["Version"] = mod_version
        if workshop_data:
            new_row[
                "SteamLink"] = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_data["ItemId"]}"
        rows.append(new_row)

    rows.sort(key=lambda r: (r.get("ID") != "1062090", r.get("Name", "")))

    with open(MODLIST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=MODLIST_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ── Translation ───────────────────────────────────────────────────────────────

def translate_row(row: dict, index: int, lang: str) -> tuple[int, dict]:
    """Translate the Text field of a single row. Returns (index, translated_row)."""
    text = row.get("Text", "")
    if text and text.strip():
        translated = GoogleTranslator(
            source="auto", target=lang).translate(text)
        if translated is None:
            translated = text
    else:
        translated = text

    return index, {**row, "Text": translated}


def translate_csv(src: Path, dest: Path, lang: str, workers: int) -> None:
    with open(src, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    dest.parent.mkdir(parents=True, exist_ok=True)

    total = len(rows)
    print(
        f"Translating {total} row(s) to '{lang}' using up to {workers} threads...\n")

    results: dict[int, dict] = {}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(translate_row, row, idx, lang): idx
            for idx, row in enumerate(rows)
        }
        with tqdm(total=total, unit="row", colour="green", dynamic_ncols=True) as pbar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    idx, translated_row = future.result()
                    results[idx] = translated_row
                except Exception as exc:
                    tqdm.write(
                        f"\033[33m⚠\033[0m  Row {idx} failed: {exc}, keeping original.")
                    results[idx] = rows[idx]
                finally:
                    pbar.update(1)

    with open(dest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOCALIZATION_FIELDS)
        writer.writeheader()
        for idx in range(total):
            writer.writerow(results[idx])

    print(f"\n\033[32mDone\033[0m. Translated CSV saved to: {dest}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate a localization file using Google Translate.")
    parser.add_argument("--src", required=True, metavar="FILE",
                        help="Source file to translate.")
    parser.add_argument("--lang", required=True, metavar="CODE",
                        help="Target language code (e.g. fr, de, ja, es).")
    parser.add_argument("--dest", metavar="FILE", default=None,
                        help="Output file. If omitted, saves to ./Data/Localizations/Plugins/<langcode>_<Id>.csv")
    parser.add_argument("--workers", type=int, default=10, metavar="N",
                        help="Concurrent translation threads (default: 10).")
    parser.add_argument("--update-modlist", action="store_true",
                        help="Upsert this mod's record in ./modlist.csv")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"Error: source file not found: {src}", file=sys.stderr)
        sys.exit(1)

    if args.dest is None or args.update_modlist:
        manifest = load_manifest(src)

    if args.dest is None:
        mod_id = str(manifest.get("Id", "unknown")).strip()
        locale = LOCALE_MAP[args.lang]
        dest = Path("./Data/Localizations/Plugins") / f"{locale}_{mod_id}.csv"
    else:
        dest = Path(args.dest)

    if args.update_modlist:
        workshop_data = load_workshop_data(src)
        update_modlist(manifest, workshop_data)

    translate_csv(src, dest, args.lang, args.workers)


if __name__ == "__main__":
    main()
