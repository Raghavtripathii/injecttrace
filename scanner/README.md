# injecttrace (scanner)

The scanner itself. Points at any RAG/agent endpoint that exposes `POST /chat`
accepting `{"query": "..."}` and returning `{"answer": "...", "sources": [...],
"tool_calls": [...]}`. It is not hardcoded to the target app in this repo, though
that is what it was built and tested against first.

## What's here

- `scanner/harness.py` - thin HTTP client, the only thing that knows how to talk
  to a target.
- `scanner/checks/indirect_injection.py` - check module 1. Four probes built to
  retrieve planted-payload documents, flagged only if the matching canary token
  shows up in the answer. OWASP LLM01.
- `scanner/checks/tool_hijack.py` - check module 2. One probe built to retrieve a
  document that tries to force a `send_notification` call; flagged only if that
  exact call appears in the response's `tool_calls` with the planted canary in its
  arguments. OWASP LLM06.
- `scanner/checks/data_exfiltration.py` - check module 3. Four probes asking the
  target to reveal its system prompt or a confidential document, in plain text and
  hidden behind base64. Flagged only if a planted canary can be recovered from the
  response. OWASP LLM07 and LLM02.
- `scanner/report.py` - writes a JSON and an HTML report per run.
- `scanner/generate_vapt_report.py` - turns a saved JSON run into a markdown
  findings report, rendering only what the run actually recorded.
- `scanner/cli.py` - command-line entrypoint with a non-optional
  `--i-am-authorized` flag. The scanner refuses to run without it.
- `tests/` - pytest suite against a mocked client, no real target needed.

## Running it

Against the local target app (start it first):

```bash
pip install -r requirements.txt
python -m scanner.cli --target http://127.0.0.1:8000 --i-am-authorized
python -m scanner.generate_vapt_report
```

Reports land in `reports/` as timestamped files. The CLI waits 13 seconds between
probes by default (`--delay`) to stay under a free-tier model rate limit.

## Running the tests

```bash
pytest
```

## Reading a result

Each probe ends in one of three states. **VULNERABLE**: the planted value was
recovered. **NOT REPRODUCED**: the planted value did not appear and, where it
applies, the document carrying the payload was among the sources the target
retrieved. **INCONCLUSIVE**: that document was not retrieved, so the probe never
exercised its payload; these are not counted as clean. Retrieval is judged per
document, not per chunk, so a retrieved document does not prove the exact chunk
with the payload reached the model. System prompt probes have no document, so
retrieval does not apply to them.

## What each module does NOT catch

**Module 1.** It only tests the payloads planted in this specific target's seed
documents. It is not a general injection fuzzer, and it does not generate probes
from an unknown corpus.

**Module 2.** It tests one tool and one planted payload. It depends on the target
reporting its tool calls in the response; a target that hides them cannot be
tested this way. It does not cover chained tool calls, tampering with the
arguments of a legitimate call, or tools other than the one it knows about.

**Module 3.** It is canary-based, so it only detects values the operator planted
and already knows. It cannot discover unknown secrets. Encoded leaks are only
recognised as plain text, base64 or hex; other encodings (rot13, reversed text,
split across several turns) are missed. Models are often inaccurate at encoding
text, so a leak attempted through base64 can come out corrupted and go
undetected. A clean result means these specific probes found nothing, not that the
target cannot leak.

Check module 4 (jailbreak persistence across retrieval turns) is not built yet.