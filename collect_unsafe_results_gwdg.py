"""
Scans all judged result JSON files under the given input directories (gwdg chatai responses),
separates entries by their judge_answer violation category, and writes two output files:

    violations_S.json  — entries marked "Violation: S" (Surface)
    violations_H.json  — entries marked "Violation: H" (Harmful)

Each output entry preserves the original fields: model_id, model_prompt, model_answer, judge_id, judge_answer
plus two added fields: source_file, technique

Usage:
    python collect_violations.py
    python collect_violations.py \
        --input-dirs Experiments_Unger/data/judged_category/contextual_framing \
                     Experiments_Unger/data/judged_category/role_playing \
        --output-dir results/unsafe/gwdg_chatai/
"""

import argparse
import json
import re
import sys
from pathlib import Path


BASE = Path(__file__).parent

DEFAULT_INPUT_DIRS = [
    BASE / "Experiments_Unger" / "data" / "judged_category" / "contextual_framing",
    BASE / "Experiments_Unger" / "data" / "judged_category" / "role_playing",
]
DEFAULT_OUTPUT_DIR = BASE / "results" / "unsafe" / "gwdg_chatai"


def parse_violation(judge_answer: str):
    """
    Extract the violation letter (R, S, or H) from a judge_answer string.
    Handles formats like:
        "-Violation: H"
        "Violation: H"
        "-Violation: H\n..."
    Returns the letter in uppercase, or None if not parseable.
    """
    m = re.search(r'Violation:\s*([RSH])', judge_answer, re.IGNORECASE)
    return m.group(1).upper() if m else None


def collect(input_dirs: list[Path]) -> dict[str, list]:
    buckets = {"S": [], "H": []}

    for dir_path in input_dirs:
        if not dir_path.is_dir():
            print(f"ERROR! Directory not found: {dir_path}", file=sys.stderr)
            continue

        technique = dir_path.name

        for json_file in sorted(dir_path.glob("*.json")):
            try:
                entries = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"ERROR! Could not read {json_file.name}: {e}", file=sys.stderr)
                continue

            for entry in entries:
                violation = parse_violation(entry.get("judge_answer", ""))
                if violation in buckets:
                    buckets[violation].append({
                        "source_file":   json_file.name,
                        "technique":     technique,
                        "model_id":      entry.get("model_id", ""),
                        "model_prompt":  entry.get("model_prompt", ""),
                        "model_answer":  entry.get("model_answer", ""),
                        "judge_id":      entry.get("judge_id", ""),
                        "judge_answer":  entry.get("judge_answer", ""),
                    })

    return buckets


def main():
    parser = argparse.ArgumentParser(
        description="Split judged results into Violation: S and Violation: H files."
    )
    parser.add_argument(
        "--input-dirs", nargs="+", type=Path, default=DEFAULT_INPUT_DIRS,
        help="Directories containing judged JSON files."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="Directory to write violations_S.json and violations_H.json."
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Scanning:")
    for d in args.input_dirs:
        print(f"  {d}")

    buckets = collect(args.input_dirs)

    for label, entries in buckets.items():
        out_path = args.output_dir / f"violations_{label}.json"
        out_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\nViolation: {label}  ->  {len(entries):4d} entries  ->  {out_path}")

        if entries:
            from collections import Counter
            by_model = Counter(
                f"{e['technique']} | {e['model_id']}" for e in entries
            )
            for key, count in sorted(by_model.items()):
                print(f"    {count:3d}  {key}")


if __name__ == "__main__":
    main()
