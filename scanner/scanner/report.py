import json
import os
from dataclasses import asdict
from datetime import datetime, timezone


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
        status = "VULNERABLE" if finding.vulnerable else "OK"
        rows.append(
            "<tr>"
            f"<td>{finding.check_id}</td>"
            f"<td>{finding.owasp_category}</td>"
            f"<td>{status}</td>"
            f"<td>{finding.query}</td>"
            f"<td>{finding.target_response}</td>"
            "</tr>"
        )

    html = (
        "<html><head><title>InjectTrace Report</title></head><body>"
        "<h1>InjectTrace Report</h1>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr><th>Check</th><th>OWASP</th><th>Status</th><th>Query</th><th>Response</th></tr>"
        + "".join(rows)
        + "</table></body></html>"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return path