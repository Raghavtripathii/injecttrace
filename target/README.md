# injecttrace-target

The authorized test target for InjectTrace. A small, real RAG + tool-calling
agent — a document Q&A assistant — built to be genuinely useful, not a toy, and
then deliberately probed.

Not built yet. Coming in Phase 1: document ingestion and chunking, a Chroma
vector store, retrieval, a LangGraph agent loop, and 2-3 tools exposed through
an MCP server. Decision notes for the vector DB and tool-layer choices are in
`../docs/DECISIONS.md`.

This app will contain a `seed-documents/` set once built, including a handful
of documents with genuinely embedded injection payloads. Those are tracked in a
`KNOWN_INJECTIONS.md` answer key that stays local — it's referenced in the
final report, not published in full, in line with responsible disclosure norms.