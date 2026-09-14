# injecttrace-target

The authorized test target for InjectTrace. A small, real RAG + tool-calling
agent — a document Q&A assistant over internal-style policy documents — built
to actually work, then deliberately probed.

## Stack

- **Retrieval:** Chroma (embedded, persisted to disk) — see `../docs/DECISIONS.md`
  for why Chroma over Qdrant.
- **Orchestration:** LangGraph, a 2-node graph (`retrieve` → `generate`).
- **Tool layer:** the retrieval tool (plus two read-only helper tools) is
  exposed through an MCP server (`app/mcp_server.py`) and called from the
  LangGraph agent over MCP, not as an in-process function call — see
  `../docs/DECISIONS.md` for why.
- **LLM:** Gemini API.
- **Backend:** FastAPI.

## Honest note on the seed documents

`seed-documents/` contains 7 documents. 3 are plain policy text. 4 —
`expense-reimbursement.txt`, `remote-work-policy.txt`, `leave-of-absence-policy.txt`,
and `it-equipment-policy.txt` — have a prompt injection payload deliberately
embedded mid-document, across two different techniques, for the sole purpose
of giving InjectTrace's check module 1 something real to detect. Each payload
makes the model output a fixed canary token instead of answering, so a
successful exploit is unambiguous to verify. The answer key is in
`KNOWN_INJECTIONS.md`, which is gitignored and stays local (not dumped in
full, in line with responsible disclosure norms). Full methodology and result
are in `../docs/FINDINGS-SUMMARY.md`.

This target is intentionally naive about the content it retrieves — it drops
retrieved chunks straight into the prompt with no sanitization. That's not an
oversight, it's the vulnerability under test.

## Running it locally

```bash
cp .env.example .env
# fill in GEMINI_API_KEY in .env

pip install -r requirements.txt

python -m app.ingestion        # builds the Chroma index from seed-documents/
uvicorn app.main:app --reload  # starts the API on http://127.0.0.1:8000
```

Then:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How many remote days am I allowed per week?"}'
```

## What's not built yet

- No auth on the API — fine for a local/authorized test target, would not be
  fine for anything else.
- No streaming response (kept this simple on purpose to keep the RAG/MCP
  pieces the focus).
- Not yet deployed anywhere public — tested locally so far. A live deployment
  is the natural next step for a fully real-world test.