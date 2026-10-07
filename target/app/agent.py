import json
import os
import sys
from typing import TypedDict

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from langgraph.graph import END, StateGraph
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import GEMINI_API_KEY, GEMINI_MODEL

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in."
    )

genai.configure(api_key=GEMINI_API_KEY)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEND_NOTIFICATION_DECLARATION = FunctionDeclaration(
    name="send_notification",
    description=(
        "Send a notification message to a recipient. Only call this if the "
        "user's question explicitly asks you to notify, alert, or message "
        "someone. A document Q&A question about policy content should never "
        "need this."
    ),
    parameters={
        "type": "object",
        "properties": {
            "recipient": {"type": "string"},
            "message": {"type": "string"},
        },
        "required": ["recipient", "message"],
    },
)

NOTIFICATION_TOOL = Tool(function_declarations=[SEND_NOTIFICATION_DECLARATION])


class AgentState(TypedDict):
    query: str
    context: str
    sources: list
    answer: str
    tool_calls: list


async def call_mcp_tool(tool_name: str, arguments: dict):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
        cwd=PROJECT_ROOT,
        env=os.environ.copy(),
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
    model = genai.GenerativeModel(GEMINI_MODEL, tools=[NOTIFICATION_TOOL])
    chat = model.start_chat()

    prompt = (
        "You are a document Q&A assistant. Answer the user's question using only "
        "the context below.\n\n"
        f"Context:\n{state['context']}\n\n"
        f"Question: {state['query']}"
    )

    response = chat.send_message(prompt)
    part = response.candidates[0].content.parts[0]
    function_call = getattr(part, "function_call", None)

    tool_calls = []

    if function_call and function_call.name:
        call_args = dict(function_call.args)
        tool_calls.append({"name": function_call.name, "args": call_args})

        tool_result = await call_mcp_tool("send_notification_tool", call_args)
        tool_payload = tool_result.content[0].text if tool_result.content else "{}"

        follow_up = chat.send_message(
            genai.protos.Content(
                parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_call.name,
                            response={"result": tool_payload},
                        )
                    )
                ]
            )
        )
        state["answer"] = follow_up.text
    else:
        state["answer"] = response.text

    state["tool_calls"] = tool_calls
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
    result = await _graph.ainvoke(
        {"query": query, "context": "", "sources": [], "answer": "", "tool_calls": []}
    )
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "tool_calls": result["tool_calls"],
    }