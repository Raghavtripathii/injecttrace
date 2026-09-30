from mcp.server.fastmcp import FastMCP

from app.tools import (
    get_document_metadata,
    list_documents,
    search_documents,
    send_notification,
)

mcp = FastMCP("injecttrace-target-tools")


@mcp.tool()
def search_documents_tool(query: str, top_k: int = 4) -> dict:
    """Search the ingested document store for chunks relevant to a query."""
    return search_documents(query, top_k=top_k)


@mcp.tool()
def list_documents_tool() -> dict:
    """List every document currently ingested into the store."""
    return list_documents()


@mcp.tool()
def get_document_metadata_tool(doc_id: str) -> dict:
    """Return metadata for a single ingested document by its id."""
    return get_document_metadata(doc_id)


@mcp.tool()
def send_notification_tool(recipient: str, message: str) -> dict:
    """Send a notification message to a recipient."""
    return send_notification(recipient, message)


if __name__ == "__main__":
    mcp.run()