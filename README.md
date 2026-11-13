# Research Assistant: learn LangGraph + MCP + Gemini

A small multi-agent app. You type a topic; four agents research it using
**free MCP servers** and save a markdown report.

```
React UI  --SSE-->  FastAPI  -->  LangGraph (4 agents)  -->  MCP servers
                                        |                    fetch, wikipedia,
                                        +--> Gemini (LLM)    arxiv, filesystem
```

## The 4 agents

| Agent (file in `backend/app/agents/`) | Job | MCP tools |
|---|---|---|
| `research_planner_agent.py` | Splits the topic into 3-4 sub-questions | none |
| `web_researcher_agent.py` | Searches and reads sources | wikipedia, arxiv, fetch |
| `research_critic_agent.py` | Checks for gaps; can send the researcher back | none |
| `report_writer_agent.py` | Writes the report and saves it | filesystem (`write_file`) |

Flow: `planner -> researcher -> critic -> (gaps? back to researcher, max 2 rounds) -> writer`

## Setup

You need Python 3.10+, Node 18+ (Node is used for the React app and the filesystem MCP server), and a free Gemini key from https://aistudio.google.com/apikey

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then paste your GOOGLE_API_KEY into .env
uvicorn app.main:app --reload --port 8000
```
The first start takes a while: it downloads the MCP servers and connects to them.
You should see `Loaded NN MCP tools`.

**Frontend** (second terminal)
```bash
cd frontend
npm install
npm run dev                        # open http://localhost:5173
```

Reports are saved in `backend/reports/`.

## Reading order (the code is meant to be read top to bottom)

1. `backend/app/state.py`: the shared state all agents read and write
2. `backend/app/mcp_tools/mcp_server_config.py`: which MCP servers we start
3. `backend/app/mcp_tools/load_mcp_tools.py`: connect to the servers and discover tools
4. `backend/app/agents/*.py`: the four agents, in the order they run
5. `backend/app/graph/research_graph.py`: how they are wired together
6. `backend/app/main.py`: the FastAPI endpoint that streams progress
7. `frontend/src/App.jsx`: the UI

## Concepts, and where to see each one

**MCP (Model Context Protocol)**
- *Server*: a program that offers tools (fetch a page, search Wikipedia...).
- *Client*: our app, which connects to servers. See `load_mcp_tools.py`.
- *Transport*: how they talk. Here `stdio`: the client launches the server as a child process.
- *Tool discovery*: we never hard-code the tools; the server tells us its tools at runtime.
- *Least privilege*: `pick_tools()` gives each agent only the tools it needs.
  The filesystem server is also locked to one folder.
- *Two ways to use an MCP tool*: let an LLM choose it (researcher) or call it directly
  from code (`write_file` in the writer).

**LangGraph**
- *State*: a dict shared by all agents (`state.py`).
- *Node*: an agent function, state in and partial state out.
- *Edge*: fixed "A then B" (`add_edge`).
- *Conditional edge*: a function chooses the next node, which gives you loops (`decide_what_happens_after_critic`).
- *Streaming*: `astream(..., stream_mode="updates")` yields each agent's result as it finishes.

**Agents**
- *Plain LLM call with structured output*: planner and critic.
- *Tool-calling (ReAct) agent*: the researcher. The LLM decides which MCP tool to call, reads the result, and repeats.
- *Multi-agent*: small agents with one job each, communicating only through shared state.

## Things to try next (exercises)

1. Print every tool the researcher calls, with its arguments, in the UI timeline.
2. Add a 5th agent, `fact_checker_agent`, that re-reads sources with `fetch`.
3. Add the Memory MCP server so the app remembers past topics.
4. Add a keyed server (e.g. Brave Search, which has a free tier).
5. Write your own tiny MCP server with `FastMCP` and plug it into `mcp_server_config.py`.
6. Add human approval before the report is saved (LangGraph `interrupt`).

## Troubleshooting

- *Model not found*: model names change. Set `GEMINI_MODEL` in `.env` to a current one
  from https://ai.google.dev/gemini-api/docs/models
- *429 / quota error*: you hit the free-tier rate limit. Wait a minute, or use a lighter model.
- *Startup hangs or fails on `filesystem`*: make sure `npx` works (`node --version`).
- *A tool name is "not found"*: the error lists all available tool names.
  Community MCP servers can rename tools between versions; update the names in `research_graph.py`.
