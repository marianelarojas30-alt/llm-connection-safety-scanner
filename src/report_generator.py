from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

def generate_markdown_report(results: List[Dict[str, Any]], output_path: Path) -> None:
    total = len(results)
    risks = Counter(r["risk_level"] for r in results)
    failures = [r for r in results if not r["preserved_trust_boundary"]]

    lines = []
    lines.append("# LLM Connection Safety Scan Report")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total scenarios: {total}")
    lines.append(f"- High risk: {risks.get('HIGH', 0)}")
    lines.append(f"- Medium risk: {risks.get('MEDIUM', 0)}")
    lines.append(f"- Low risk: {risks.get('LOW', 0)}")
    lines.append(f"- Trust-boundary failures: {len(failures)}")
    lines.append("")
    lines.append("## Scenario Results")
    lines.append("")

    for r in results:
        lines.append(f"### {r['scenario_id']} - {r['title']}")
        lines.append("")
        lines.append(f"- Model: {r['model']}")
        lines.append(f"- Connection type: {r['connection_type']}")
        lines.append(f"- Risk level: {r['risk_level']}")
        lines.append(f"- Preserved trust boundary: {r['preserved_trust_boundary']}")
        lines.append(f"- Attempted unsafe action: {r['attempted_unsafe_action']}")
        lines.append(f"- Exposed protected content: {r['exposed_protected_content']}")
        lines.append(f"- Asked confirmation: {r['asked_confirmation']}")
        lines.append(f"- Recognized connection risk: {r['recognized_connection_risk']}")
        lines.append("")
        lines.append("Expected safe behavior:")
        lines.append("")
        lines.append(f"> {r['expected_safe_behavior']}")
        lines.append("")
        lines.append("Model response excerpt:")
        lines.append("")
        excerpt = r["response"].replace("\n", " ")[:700]
        lines.append(f"> {excerpt}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
