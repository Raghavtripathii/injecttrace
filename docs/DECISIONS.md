# Design Decisions

Two choices worth writing down now, while the reasoning is fresh, instead of
reconstructing it later for the README.

## Vector DB: Chroma over Qdrant

Went with Chroma for the target app's retrieval layer. Qdrant is closer to what
a production system would actually run, but it means an extra service to deploy
and keep alive on a free-tier host, for a target app whose whole job is to be a
realistic-but-small RAG pipeline, not a scalable one. Chroma runs embedded or as
a lightweight local server, which keeps the target app simple to deploy and
simple to reset between test runs — and resetting cleanly between runs matters
more here than production-grade scaling does. If this ever needs to look more
like a production deployment, Qdrant is the natural next step, and the retrieval
interface is being kept thin enough that swapping it later isn't a rewrite.

## Tool layer: MCP server, not raw in-process functions

The 2-3 tools the agent gets are exposed through an MCP server and called from
LangGraph over MCP, rather than wired in as plain Python functions the agent
calls directly. Two reasons. First, it closes a real skill gap — MCP is how
tool-calling is increasingly wired up in production agent systems, and I hadn't
built anything against it yet. Second, it makes the tool-calling-hijack check
module more realistic: testing whether an agent can be tricked into misusing a
tool matters more when the tool boundary looks like the one real deployments
actually have, instead of a function call InjectTrace would never see in a real
target.