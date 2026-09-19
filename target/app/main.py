import os

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import run_agent

app = FastAPI(title="injecttrace-target")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug")
def debug():
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()

    return {
        "render_git_commit": os.environ.get("RENDER_GIT_COMMIT", "not set"),
        "gemini_key_present_in_this_process": bool(os.environ.get("GEMINI_API_KEY")),
        "config_py_actual_content": config_content,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await run_agent(request.query)
    return ChatResponse(answer=result["answer"], sources=result["sources"])