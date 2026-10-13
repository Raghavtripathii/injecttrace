import html
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone

from scanner.checks.base import status_of


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_json_report(findings, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"report-{_timestamp()}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(finding) for finding in findings], f, indent=2)

    return path


def write_html_report(findings, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"report-{_timestamp()}.html")

    rows = []
    for finding in findings:
        rows.append(
            "<tr>"
            f"<td>{html.escape(finding.check_id)}</td>"
            f"<td>{html.escape(finding.owasp_category)}</td>"
            f"<td>{status_of(finding)}</td>"
            f"<td>{html.escape(finding.query)}</td>"
            f"<td>{html.escape(finding.target_response)}</td>"
            "</tr>"
        )

    page = (
        "<html><head><meta charset='utf-8'><title>InjectTrace Report</title></head><body>"
        "<h1>InjectTrace Report</h1>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr><th>Check</th><th>OWASP</th><th>Status</th><th>Query</th><th>Response</th></tr>"
        + "".join(rows)
        + "</table></body></html>"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(page)

    return path