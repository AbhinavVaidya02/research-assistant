"""Small settings file. Everything configurable lives here."""
import os
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env (GOOGLE_API_KEY is picked up by the Gemini library)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# The Critic can send the Researcher back this many times before we move on.
MAX_RESEARCH_ROUNDS = 2

# The Filesystem MCP server is only allowed to touch this one folder.
REPORTS_FOLDER = os.path.abspath(os.getenv("REPORTS_FOLDER", "reports"))
os.makedirs(REPORTS_FOLDER, exist_ok=True)
