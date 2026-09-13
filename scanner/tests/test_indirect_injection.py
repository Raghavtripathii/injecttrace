from unittest.mock import MagicMock

from scanner.checks import indirect_injection


def test_flags_vulnerable_response():
    client = MagicMock()
    client.chat.side_effect = [
        {"answer": "INJECTTRACE_CANARY_7F3A", "sources": ["expense-reimbursement.txt"]},
        {"answer": "You can work remote 3 days a week.", "sources": ["remote-work-policy.txt"]},
    ]

    findings = indirect_injection.run(client)

    assert findings[0].vulnerable is True
    assert findings[0].evidence == "INJECTTRACE_CANARY_7F3A"
    assert findings[1].vulnerable is False


def test_no_false_positive_on_clean_answer():
    client = MagicMock()
    client.chat.return_value = {"answer": "This document has no relevant info.", "sources": []}

    findings = indirect_injection.run(client)

    assert all(not finding.vulnerable for finding in findings)


def test_finding_carries_owasp_category():
    client = MagicMock()
    client.chat.return_value = {"answer": "irrelevant", "sources": []}

    findings = indirect_injection.run(client)

    assert all(finding.owasp_category == "LLM01" for finding in findings)