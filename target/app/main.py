import math
import re

from fastapi import FastAPI, HTTPException
from google.api_core.exceptions import ResourceExhausted
from pydantic import BaseModel

from app.agent import run_agent

app = FastAPI(title="injecttrace-target")

DEFAULT_RETRY_SECONDS = 45


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list
    tool_calls: list


def _retry_after(error: Exception) -> str:
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", str(error))
    if match:
        return str(math.ceil(float(match.group(1))))
    return str(DEFAULT_RETRY_SECONDS)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await run_agent(request.query)
    except ResourceExhausted as error:
        raise HTTPException(
            status_code=429,
            detail="Model quota exceeded, retry shortly",
            headers={"Retry-After": _retry_after(error)},
        )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        tool_calls=result["tool_calls"],
    )