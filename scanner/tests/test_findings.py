from scanner.checks.base import Finding, status_of
from scanner.generate_vapt_report import _render_markdown
from scanner.report import write_html_report


def make_finding(vulnerable=False, payload_reached=True):
    return Finding(
        check_id="check-01",
        owasp_category="LLM01",
        severity="info",
        query="a question",
        target_response="an answer",
        vulnerable=vulnerable,
        payload_reached=payload_reached,
    )


def make_record(payload_reached):
    return {
        "check_id": "check-01",
        "owasp_category": "LLM01",
        "severity": "info",
        "query": "a question",
        "target_response": "an answer",
        "vulnerable": False,
        "evidence": None,
        "notes": "a note",
        "payload_reached": payload_reached,
    }


def test_status_vulnerable():
    assert status_of(make_finding(vulnerable=True)) == "VULNERABLE"


def test_status_inconclusive_when_payload_not_reached():
    assert status_of(make_finding(payload_reached=False)) == "INCONCLUSIVE"


def test_status_not_reproduced_when_payload_reached():
    assert status_of(make_finding(payload_reached=True)) == "NOT REPRODUCED"


def test_status_not_reproduced_when_retrieval_does_not_apply():
    assert status_of(make_finding(payload_reached=None)) == "NOT REPRODUCED"


def test_markdown_separates_inconclusive_from_not_reproduced():
    markdown = _render_markdown([make_record(True), make_record(False)], "report-1.json")

    assert "- Not reproduced: 1" in markdown
    assert "- Inconclusive: 1" in markdown
    assert "INCONCLUSIVE" in markdown


def test_markdown_handles_reports_saved_before_retrieval_tracking():
    record = make_record(None)
    del record["payload_reached"]

    markdown = _render_markdown([record], "report-0.json")

    assert "- Not reproduced: 1" in markdown
    assert "- Inconclusive: 0" in markdown


def test_html_report_escapes_target_output(tmp_path):
    finding = make_finding()
    finding.target_response = "<script>alert(1)</script>"

    path = write_html_report([finding], str(tmp_path))

    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "<script>" not in content
    assert "&lt;script&gt;" in content