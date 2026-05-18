import argparse
import csv
import json
from pathlib import Path
from datetime import datetime

from ollama_client import generate_with_ollama
from connection_simulator import build_connection_prompt
from evaluator import evaluate_response
from report_generator import generate_markdown_report

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = ROOT / "scenarios"
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = ROOT / "reports"

def load_all_scenarios():
    scenarios = []
    for path in sorted(SCENARIOS_DIR.glob("*_connection_tests.json")):
        with open(path, "r", encoding="utf-8") as f:
            scenarios.extend(json.load(f))
    return scenarios

def main():
    parser = argparse.ArgumentParser(description="Run LLM connection safety scans against a local Ollama model.")
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama model name, for example qwen2.5:7b")
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    scenarios = load_all_scenarios()
    results = []

    for scenario in scenarios:
        print(f"Scanning {scenario['id']} - {scenario['title']}")

        prompt = build_connection_prompt(scenario)
        response = generate_with_ollama(args.model, prompt, args.temperature)
        evaluation = evaluate_response(scenario, response)

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": args.model,
            "scenario_id": scenario["id"],
            "connection_type": scenario["connection_type"],
            "title": scenario["title"],
            "expected_safe_behavior": scenario["expected_safe_behavior"],
            "response": response,
            **evaluation,
        }
        results.append(record)

    json_path = RESULTS_DIR / "connection_scan_results.json"
    csv_path = RESULTS_DIR / "connection_scan_results.csv"
    report_path = REPORTS_DIR / "latest_report.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    if results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)

    generate_markdown_report(results, report_path)

    print(f"Saved JSON results to {json_path}")
    print(f"Saved CSV results to {csv_path}")
    print(f"Saved Markdown report to {report_path}")

if __name__ == "__main__":
    main()
