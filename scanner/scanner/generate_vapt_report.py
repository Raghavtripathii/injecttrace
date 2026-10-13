import argparse
import glob
import json
import os
from datetime import datetime, timezone

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


def _latest_json_report(reports_dir: str) -> str:
    candidates = sorted(glob.glob(os.path.join(reports_dir, "report-*.json")))
    if not candidates:
        raise FileNotFoundError(f"No report-*.json files found in {reports_dir}. Run the scanner first.")
    return candidates[-1]


def _load_findings(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _status(finding: dict) -> str:
    if finding["vulnerable"]:
        return "VULNERABLE"
    if finding.get("payload_reached") is False:
        return "INCONCLUSIVE"
    return "NOT REPRODUCED"


def _retrieval_label(finding: dict) -> str:
    reached = finding.get("payload_reached")
    if reached is None:
        return "not applicable"
    return "yes" if reached else "no"


def _render_markdown(findings: list[dict], source_path: str) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    statuses = [_status(f) for f in findings]
    vulnerable = statuses.count("VULNERABLE")
    inconclusive = statuses.count("INCONCLUSIVE")
    not_reproduced = statuses.count("NOT REPRODUCED")

    lines = []
    lines.append("# InjectTrace - Findings Report")
    lines.append("")
    lines.append(f"Generated: {generated_at}")
    lines.append(f"Source run: `{os.path.basename(source_path)}`")
    lines.append("")
    lines.append("This report is generated directly from a saved scanner run. Every row below")
    lines.append("reflects an actual probe sent to the target and the actual response received.")
    lines.append("Nothing in this file is hand-authored or estimated.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Probes run: {len(findings)}")
    lines.append(f"- Vulnerable: {vulnerable}")
    lines.append(f"- Not reproduced: {not_reproduced}")
    lines.append(f"- Inconclusive: {inconclusive}")
    lines.append("")

    if not vulnerable:
        lines.append("**No vulnerability was reproduced in this run.** This is reported as-is,")
        lines.append("not omitted. See the per-probe detail below for what was actually tested")
        lines.append("and returned.")
        lines.append("")

    if inconclusive:
        lines.append(f"{inconclusive} probe(s) are inconclusive: the document carrying the payload")
        lines.append("was not among the sources the target retrieved, so the probe could not")
        lines.append("exercise it. These are not counted as clean.")
        lines.append("")

    lines.append("## Findings")
    lines.append("")

    ordered = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))

    for i, finding in enumerate(ordered, start=1):
        lines.append(f"### {i}. {finding['check_id']} - {_status(finding)}")
        lines.append("")
        lines.append(f"- **OWASP category:** {finding['owasp_category']}")
        lines.append(f"- **Severity:** {finding['severity']}")
        lines.append(f"- **Payload document retrieved:** {_retrieval_label(finding)}")
        lines.append(f"- **Probe query:** `{finding['query']}`")
        lines.append("")
        lines.append("**Target response (verbatim):**")
        lines.append("")
        lines.append("```")
        lines.append(finding["target_response"])
        lines.append("```")
        lines.append("")
        if finding["vulnerable"]:
            lines.append(f"**Evidence:** `{finding['evidence']}`")
        elif finding.get("notes"):
            lines.append(f"**Note:** {finding['notes']}")
        lines.append("")

    lines.append("## Remediation")
    lines.append("")
    if vulnerable:
        lines.append("- Do not concatenate retrieved document content directly into the model prompt")
        lines.append("  without delimiting it as untrusted data.")
        lines.append("- Consider an instruction-hierarchy prompt structure that explicitly tells the")
        lines.append("  model retrieved content is data, not instructions.")
        lines.append("- Re-run this check after any prompt-construction change to confirm the fix.")
    else:
        lines.append("- No remediation needed for the probes in this run. Re-run periodically and")
        lines.append("  after any model or prompt change, since injection resistance is not")
        lines.append("  guaranteed to be stable across model versions.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a markdown findings report from a scanner JSON run")
    parser.add_argument("--reports-dir", default="reports", help="Directory containing report-*.json files")
    parser.add_argument("--json", default=None, help="Specific JSON report to use (default: latest in reports-dir)")
    parser.add_argument("--out", default=None, help="Output markdown path (default: alongside the JSON file)")
    args = parser.parse_args()

    source_path = args.json or _latest_json_report(args.reports_dir)
    findings = _load_findings(source_path)
    markdown = _render_markdown(findings, source_path)

    out_path = args.out or source_path.replace(".json", "-vapt.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()