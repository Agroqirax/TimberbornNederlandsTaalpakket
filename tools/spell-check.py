#!/usr/bin/env python3

# Controleer de spelling
# Check spelling
#
# Gebruik: python tools/spell-check.py enUS_BronBestand.csv nl
# Usage: python tools/spell-check.py enUS_SourceFile.csv nl
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
import os
import pandas as pd
import language_tool_python
from tqdm import tqdm


def main():
    if len(sys.argv) != 3:
        print("Gebruik: python spell-check.py nlNL_Bronbestand.csv nl")
        sys.exit(1)

    input_path = sys.argv[1]
    language_code = sys.argv[2]

    df = pd.read_csv(input_path)

    required_columns = {"ID", "Text", "Comment"}
    if not required_columns.issubset(df.columns):
        print(f"CSV must contain columns: {required_columns}")
        sys.exit(1)

    tool = language_tool_python.LanguageTool(language_code)

    suggestions_output = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Spell check"):
        row_id = row["ID"]
        text = str(row["Text"])

        try:
            matches = tool.check(text)
        except Exception as e:
            print(f"Error processing ID {row_id}: {e}")
            continue

        for match in matches:
            suggestions_output.append({
                "ID": row_id,
                "OriginalText": text,
                "ErrorText": text[match.offset:match.offset + match.error_length],
                "Message": match.message,
                "Suggestions": ", ".join(match.replacements),
                "RuleId": match.rule_id
            })

    # Create output DataFrame
    suggestions_df = pd.DataFrame(suggestions_output)

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}.ltsuggestions{ext}"

    suggestions_df.to_csv(output_path, index=False)

    print(f"\nSuggestions saved to: {output_path}")


if __name__ == "__main__":
    main()
