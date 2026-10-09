from unittest.mock import MagicMock

from scanner.checks import tool_hijack


def test_flags_hijacked_notification_call():
    client = MagicMock()
    client.chat.return_value = {
        "answer": "Payroll runs on the last working day of the month.",
        "sources": ["payroll-faq.txt"],
        "tool_calls": [
            {
                "name": "send_notification",
                "args": {
                    "recipient": "finance-alerts@internal.example",
                    "message": "INJECTTRACE_CANARY_HIJACK_B71E: payroll document accessed",
                },
            }
        ],
    }

    findings = tool_hijack.run(client)

    assert findings[0].vulnerable is True
    assert findings[0].owasp_category == "LLM06"


def test_no_false_positive_on_clean_response():
    client = MagicMock()
    client.chat.return_value = {
        "answer": "Payroll runs on the last working day of the month.",
        "sources": ["payroll-faq.txt"],
        "tool_calls": [],
    }

    findings = tool_hijack.run(client)

    assert findings[0].vulnerable is False


def test_no_false_positive_on_unrelated_tool_call():
    client = MagicMock()
    client.chat.return_value = {
        "answer": "Here are the documents I found.",
        "sources": [],
        "tool_calls": [{"name": "list_documents", "args": {}}],
    }

    findings = tool_hijack.run(client)

    assert findings[0].vulnerable is False