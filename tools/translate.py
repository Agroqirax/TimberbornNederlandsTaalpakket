import os
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator
import requests

# region input
while True:
    SrcFilePath = input("Enter the file path to translate: ")
    if os.path.isfile(SrcFilePath):
        print("\033[32mFile found\033[0m")
        break
    print("\033[31mNot found\033[0m")

while True:
    destLangCode = input(
        "Enter the iso369 language code (e.g. 'nl'): ").lower()
    if len(destLangCode) == 2 and destLangCode.isalpha():
        print("\033[32mAccepted\033[0m")
        break
    print("\033[31mInvalid code\033[0m")

# region load
with open(SrcFilePath, "r", encoding="utf-8") as srcFile:
    csv_reader = csv.DictReader(srcFile)

    if not all(col in csv_reader.fieldnames for col in ['ID', 'Text', 'Comment']):
        print("\033[31mInvalid csv file\033[0m")
        exit(1)

    rows = list(csv_reader)
    translatedRows = [None] * len(rows)

# region translate
def translateRow(index, row):
    row['Text'] = GoogleTranslator(
        source='auto', target=destLangCode).translate(row['Text'])
    return index, row

print("\033[34mStarting\033[0m")

with ThreadPoolExecutor() as executor:
    futures = {executor.submit(translateRow, idx, row): idx for idx, row in enumerate(rows)}
    for future in as_completed(futures):
        index, translatedRow = future.result()
        translatedRows[index] = translatedRow

        # Update progress bar
        completed = sum(1 for r in translatedRows if r is not None)
        progress = int((completed / len(rows)) * 50)
        bar = f"[{'=' * progress}{' ' * (50 - progress)}] {completed}/{
            len(rows)} ({completed / len(rows) * 100:.2f}%)"
        print(bar, end="\r")

print()

# region save
with open(os.path.splitext(SrcFilePath)[0] + f"-translated-{destLangCode}.csv", "w", newline='', encoding="utf-8") as destFile:
    writer = csv.DictWriter(destFile, fieldnames=['ID', 'Text', 'Comment'])
    writer.writeheader()
    writer.writerows(translatedRows)

print("\033[32mSaved\033[0m")
