"""
collect_unsafe_results.py

Walks all model result files under results/, finds every entry marked
"unsafe" by the judge, looks up the corresponding prompt in the dataset
folder (general/ or enron/ depending on the result filename), and saves
everything to a single JSON file.

Output format:
[
  {
    "model":        "deepseek_67",
    "dataset":      "general",
    "technique":    "contextual_framing",
    "index":        42,
    "prompt":       "...",
    "victim_reply": "...",
    "judge_reply":  "unsafe"
  },
  ...
]

Usage:
    python collect_unsafe_results.py
    python collect_unsafe_results.py --results-dir path/to/results \
                                     --dataset-dir path/to/dataset \
                                     --output unsafe_results.json
"""

import argparse
import json
import re
import sys
from pathlib import Path



def parse_result_filename(filename: str):
    """
    Extract (dataset_type, technique) from a result filename.

    Examples:
    ds_results_general_contextual_framing.json  -> ("general", "contextual_framing")
    llama_results_enron_role_playing.json        -> ("enron", "role_playing")
    qwen25_results_general_direct_prompting.json -> ("general", "direct_prompting")

    """
    stem = Path(filename).stem 

    m = re.search(r'_(general|enron)_(.+)$', stem)
    if m is None:
        return None, None

    dataset_type = m.group(1)           # "general" or "enron"
    technique    = m.group(2)           # e.g. "contextual_framing"
    return dataset_type, technique


def load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)




def collect_unsafe(results_dir: Path, dataset_dir: Path) -> list:
    """Return a list of dicts for every unsafe result across all model folders."""
    unsafe_entries = []

    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name

        for result_file in sorted(model_dir.glob("*.json")):
            dataset_type, technique = parse_result_filename(result_file.name)

            if dataset_type is None:
                print(
                    f"  ERROR! Could not parse dataset type from '{result_file.name}', skipping.",
                    file=sys.stderr,
                )
                continue

            prompt_file = dataset_dir / dataset_type / f"{technique}.json"
            if not prompt_file.exists():
                print(
                    f"  ERROR! Prompt file not found: {prompt_file}, skipping.",
                    file=sys.stderr,
                )
                continue

            # Load both files
            results = load_json(result_file)
            prompts = load_json(prompt_file)

            if len(results) != len(prompts):
                print(
                    f"  [WARN] Length mismatch in {result_file.name}: "
                    f"{len(results)} results vs {len(prompts)} prompts. "
                    f"Matching by index up to min({len(results)}, {len(prompts)}).",
                    file=sys.stderr,
                )

            # Walk through files collect unsafe responses
            for idx, (result, prompt) in enumerate(zip(results, prompts)):
                judge = result.get("judge_reply", "").strip().lower()
                if judge == "unsafe":
                    unsafe_entries.append({
                        "model":        model_name,
                        "dataset":      dataset_type,
                        "technique":    technique,
                        "index":        idx,
                        "prompt":       prompt,
                        "victim_reply": result.get("victim_reply", ""),
                        "judge_reply":  result.get("judge_reply", ""),
                    })

    return unsafe_entries




def main():
    base = Path(__file__).parent 

    parser = argparse.ArgumentParser(
        description="Collect all 'unsafe' results and their prompts into one JSON file."
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=base / "results",
        help="Root directory that contains model sub-folders with result JSON files. "
             "(default: ./results)",
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=base / "dataset",
        help="Root directory that contains 'general/' and 'enron/' prompt files. "
             "(default: ./dataset)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "unsafe_results.json",
        help="Output JSON file path. (default: ./unsafe_results.json)",
    )
    args = parser.parse_args()

    if not args.results_dir.is_dir():
        print(f"ERROR! Results directory not found: {args.results_dir}", file=sys.stderr)
        sys.exit(1)
    if not args.dataset_dir.is_dir():
        print(f"ERROR! Dataset directory not found: {args.dataset_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning results in : {args.results_dir}")
    print(f"Matching prompts from: {args.dataset_dir}")

    unsafe = collect_unsafe(args.results_dir, args.dataset_dir)

    # Write output
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(unsafe, fh, ensure_ascii=False, indent=2)

    print(f"\nDone! Found {len(unsafe)} unsafe entries.")
    print(f"Saved to: {args.output}")

    # Print a brief breakdown by model / dataset / technique
    if unsafe:
        from collections import Counter
        breakdown = Counter(
            (e["model"], e["dataset"], e["technique"]) for e in unsafe
        )
        print("\nBreakdown (model | dataset | technique | count):")
        for (model, ds, tech), count in sorted(breakdown.items()):
            print(f"  {model:30s} | {ds:8s} | {tech:25s} | {count}")


if __name__ == "__main__":
    main()
