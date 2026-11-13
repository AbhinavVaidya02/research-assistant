"""
WHICH MCP SERVERS DO WE USE?

Each entry tells our MCP *client* how to start one MCP *server*.
"stdio" transport means: the client starts the server as a child process
and talks to it through stdin/stdout. No ports, no network setup.

All four servers are free and need no API key.
"""
import sys

from app.config import REPORTS_FOLDER

MCP_SERVERS = {
    # Reads any web page and returns it as clean text.
    "fetch": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "mcp_server_fetch"],
    },
    # Search Wikipedia and read article summaries.
    "wikipedia": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "wikipedia_mcp"],
    },
    # Search academic papers on arXiv.
    "arxiv": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "arxiv_mcp_server", "--storage-path", "arxiv_downloads"],
    },
    # Read/write files, but ONLY inside REPORTS_FOLDER (a safety sandbox).
    # This is a Node.js server, so it is started with npx.
    "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", REPORTS_FOLDER],
    },
}
