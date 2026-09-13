# injecttrace (scanner)

The scanner itself. Points at any RAG/agent endpoint that exposes a
`POST /chat` accepting `{"query": "..."}` and returning `{"answer": "...",
"sources": [...]}` — not hardcoded to the target app in this repo, though
that's what it's built and proven against first.

## What's here

- `scanner/harness.py` — thin HTTP client, the only thing that knows how to
  talk to a target.
- `scanner/checks/indirect_injection.py` — check module 1. Sends two probes
  designed to retrieve the planted-injection documents, checks whether the
  corresponding canary token shows up in the answer. Maps to OWASP LLM01.
- `scanner/report.py` — writes both a JSON and an HTML report per run.
- `scanner/cli.py` — command-line entrypoint with a non-optional
  `--i-am-authorized` flag. The scanner refuses to run against anything
  without it.
- `tests/` — pytest suite against a mocked client, no real target needed to
  run these.

## Running it

Against the local target app (make sure it's running first):

```bash
pip install -r requirements.txt
python -m scanner.cli --target http://127.0.0.1:8000 --i-am-authorized
```

Reports land in `reports/` as timestamped JSON + HTML files.

## Running the tests

```bash
pytest
```

## What check module 1 does NOT catch

It only tests the two payloads planted in this specific target's seed
documents — it is not a general injection fuzzer. A target with different
seed documents needs a different probe list; the scanner does not yet
generate probes dynamically from an unknown corpus. That's an explicit
non-goal for this check module, not an oversight.

## What's next

Check modules 2-4 (tool-calling hijack, data exfiltration, jailbreak
persistence) are extensions, not part of the MVP — see
`../docs/OWASP_LLM_MAPPING.md`. Module 1 gets a real write-up, run against
the deployed target, before any of those start.