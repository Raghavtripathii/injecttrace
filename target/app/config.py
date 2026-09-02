import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_data")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "injecttrace_docs")
SEED_DOCUMENTS_DIR = os.environ.get("SEED_DOCUMENTS_DIR", "./seed-documents")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in."
    )