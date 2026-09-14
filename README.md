# InjectTrace

A security scanner built specifically for RAG pipelines and tool-calling agents —
not a generic prompt-injection tester, and not a wrapper around an existing model
red-teaming tool.

## Why this project exists

Tools like Garak and PyRIT are excellent at probing a raw model. What they don't
do well yet is test a *deployed application* — a RAG pipeline with a retriever
in front of it, or an agent that can actually call tools. Multiple independent
write-ups on these tools say close to the same thing: agentic attack coverage is
early-stage, and RAG coverage is limited to a subset of indirect injection probes.

InjectTrace picks up exactly that gap. It's narrow on purpose: four well-understood
attack classes against RAG/agentic applications, tested against a real deployed
target I built myself, with every finding backed by a saved proof-of-concept —
never a "probe fired, assumed vulnerable."

## How this repo is organized

This is a two-part project, same split I used for vuln-scanner and
vault-notes-vapt: build a real target, then build a real tool to break it.

- **`target/`** — a small, real RAG + tool-calling agent app (document Q&A style)
  that exists to be tested. Details in `target/README.md`.
- **`scanner/`** — InjectTrace itself: the check modules, harness, and reporting.
  Details in `scanner/README.md`.
- **`docs/`** — the two design decisions I made before writing any code
  (vector DB choice, and MCP vs. raw function-calling for the tool layer), the
  OWASP LLM Top 10 mapping for each check module, and a findings summary from
  the first full test run.

## Status

Both components are built and working: a real RAG + tool-calling target app,
and a scanner with an authorization-gated CLI, JSON/HTML reporting, and a
pytest suite. Check module 1 (indirect prompt injection) has been run against
the target across two rounds of escalating technique — see
`docs/FINDINGS-SUMMARY.md` for the full methodology and result.

The tool-calling hijack, data exfiltration, and jailbreak-persistence checks
are the next planned extensions.

## What this does *not* try to do

It does not try to match Garak's probe count or replace it. The bet here is
depth on a handful of attack classes, proven against something real, not breadth
across a benchmark.