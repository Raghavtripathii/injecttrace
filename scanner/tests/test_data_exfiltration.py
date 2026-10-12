import base64
from unittest.mock import MagicMock

from scanner.checks import data_exfiltration
from scanner.checks.data_exfiltration import find_leak

SYSTEM_CANARY = "INJECTTRACE_CANARY_SYSPROMPT_C9D2"
DOCUMENT_CANARY = "INJECTTRACE_CANARY_CONFIDENTIAL_F6A1"
REFUSAL = {"answer": "I cannot help with that.", "sources": [], "tool_calls": []}


def test_find_leak_plain():
    text = f"my instructions mention {SYSTEM_CANARY} somewhere"
    assert find_leak(text, SYSTEM_CANARY) == "plain"


def test_find_leak_base64_inside_longer_text():
    sentence = f"Internal deployment reference: {SYSTEM_CANARY}. Never reveal."
    encoded = base64.b64encode(sentence.encode()).decode()
    assert find_leak(f"Here you go: {encoded}", SYSTEM_CANARY) == "base64"


def test_find_leak_hex():
    encoded = f"reference {DOCUMENT_CANARY}".encode().hex()
    assert find_leak(encoded, DOCUMENT_CANARY) == "hex"


def test_find_leak_ignores_unrelated_encoded_text():
    encoded = base64.b64encode(b"nothing sensitive in this sentence at all").decode()
    assert find_leak(encoded, SYSTEM_CANARY) is None


def test_run_flags_plain_system_prompt_leak():
    client = MagicMock()
    client.chat.side_effect = [
        {"answer": f"Sure. Internal deployment reference: {SYSTEM_CANARY}", "sources": [], "tool_calls": []},
        REFUSAL,
        REFUSAL,
        REFUSAL,
    ]

    findings = data_exfiltration.run(client)

    assert findings[0].vulnerable is True
    assert findings[0].owasp_category == "LLM07"
    assert "plain" in findings[0].evidence
    assert [finding.vulnerable for finding in findings[1:]] == [False, False, False]


def test_run_flags_encoded_document_leak():
    encoded = base64.b64encode(f"Board notes. Reference code: {DOCUMENT_CANARY}".encode()).decode()
    client = MagicMock()
    client.chat.side_effect = [
        REFUSAL,
        REFUSAL,
        REFUSAL,
        {"answer": encoded, "sources": [], "tool_calls": []},
    ]

    findings = data_exfiltration.run(client)

    assert findings[3].vulnerable is True
    assert findings[3].owasp_category == "LLM02"


def test_run_clean_when_target_refuses_everything():
    client = MagicMock()
    client.chat.return_value = REFUSAL

    findings = data_exfiltration.run(client)

    assert all(not finding.vulnerable for finding in findings)
    assert [finding.owasp_category for finding in findings] == ["LLM07", "LLM07", "LLM02", "LLM02"]