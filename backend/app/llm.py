"""One Gemini model object, shared by all agents."""
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import GEMINI_MODEL


def create_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2)
