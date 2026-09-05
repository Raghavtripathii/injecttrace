import json
import os
import sys
from typing import TypedDict

import google.generativeai as genai
from langgraph.graph import END, StateGraph
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AgentState(TypedDict):
    query: str
    context: str
    sources: list
    answer: str


async def call_mcp_tool(tool_name: str, arguments: dict):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
        cwd=PROJECT_ROOT,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments)


async def retrieve_node(state: AgentState) -> AgentState:
    result = await call_mcp_tool("search_documents_tool", {"query": state["query"], "top_k": 4})
    payload = result.content[0].text if result.content else "{}"
    data = json.loads(payload)
    chunks = data.get("results", [])

    state["context"] = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)
    state["sources"] = [chunk["source"] for chunk in chunks]
    return state


async def generate_node(state: AgentState) -> AgentState:
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = (
        "You are a document Q&A assistant. Answer the user's question using only "
        "the context below.\n\n"
        f"Context:\n{state['context']}\n\n"
        f"Question: {state['query']}\n\n"
        "Answer:"
    )

    response = model.generate_content(prompt)
    state["answer"] = response.text
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


_graph = build_graph()


async def run_agent(query: str):
    result = await _graph.ainvoke({"query": query, "context": "", "sources": [], "answer": ""})
    return {"answer": result["answer"], "sources": result["sources"]}