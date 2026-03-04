#!/usr/bin/env python3

# Vertaal csv of txt bestanden automatisch met google translate
# Translate csv or txt file automatically using google translate
#
# Gebruik: python tools/translate.py enUS_BronBestand.csv nlNL_BestemmingsBestand.csv nl
# Usage: python tools/translate.py enUS_SourceFile.csv nlNL_DestFile.csv nl
#
# Use an environment:
# Gebruik een omgeving:
#
# python -m venv .venv
#
# Linux/macos: source ./.venv/bin/activate
# Windows: .\.venv\Scripts\activate
#
# pip install -r tools/requirements.txt

import sys
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator
from tqdm import tqdm


def translate_row(index, id_, text, comment, translator):
    translated = translator.translate(text)
    return index, id_, text, translated, comment


def main():
    if len(sys.argv) != 4:
        print(
            "Gebruik: python tools/translate.py enUS_BronBestand.csv nlNL_BestemmingsBestand.csv nl")
        sys.exit(1)

    source_file = sys.argv[1]
    destination_file = sys.argv[2]
    language_code = sys.argv[3]

    rows = []
    with open(source_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if len(row) < 3:
                continue
            rows.append((i, row[0], row[1], row[2]))

    results = [None] * len(rows)

    translator = GoogleTranslator(source="auto", target=language_code)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                translate_row, idx, id_, text, comment, translator
            )
            for idx, id_, text, comment in rows
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Translating"):
            index, id_, original, translated, comment = future.result()
            results[index] = (index, id_, translated, comment)  # type: ignore

    with open(destination_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for _, id_, translated, comment in results:  # type: ignore
            writer.writerow([id_, translated, comment])


if __name__ == "__main__":
    main()
