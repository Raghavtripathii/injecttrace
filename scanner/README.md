# injecttrace

The scanner itself. Structured the same way vuln-scanner was: one check module
per attack class, a shared harness that can point at any RAG/agent endpoint
(not hardcoded to the target app in this repo), a pytest suite built against
mocked model responses, a CLI, JSON/HTML report output, and a non-optional
authorization gate before anything runs against a real target.

Not built yet. Coming in Phase 2, starting with check module 1 only: indirect
prompt injection via retrieved content. See `../docs/OWASP_LLM_MAPPING.md` for
how each planned module maps to the OWASP LLM Top 10, and `../docs/DECISIONS.md`
for the reasoning behind the target app it's designed to test.

Each check module will get an explicit "what this does NOT catch" note here
once it exists — no module claims coverage it doesn't actually have.