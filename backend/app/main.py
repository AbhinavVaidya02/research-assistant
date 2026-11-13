"""
FASTAPI BACKEND: exposes the graph to the React frontend.

    GET /research/stream?topic=...   ->  Server-Sent Events (SSE)

SSE = the server keeps the HTTP connection open and pushes small messages.
We send one message every time an agent finishes, so the UI can show live progress.

Run:  uvicorn app.main:app --reload --port 8000
"""
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.graph.research_graph import build_research_graph
from app.llm import create_llm
from app.mcp_tools.load_mcp_tools import load_all_mcp_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: connect to MCP servers, build the graph.
    print("Connecting to MCP servers (first run can take a minute)...")
    all_mcp_tools = await load_all_mcp_tools()
    print(f"Loaded {len(all_mcp_tools)} MCP tools")
    app.state.research_graph = build_research_graph(create_llm(), all_mcp_tools)
    yield


app = FastAPI(title="Research Assistant", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


def describe_agent_result(agent_name: str, output: dict) -> str:
    """A short human-readable line for the UI timeline."""
    if agent_name == "research_planner_agent":
        return "Planned questions:\n- " + "\n- ".join(output["sub_questions"])
    if agent_name == "web_researcher_agent":
        tools = ", ".join(output["tools_used"]) or "no tools"
        return f"Research round {output['research_round']} done. MCP tools called: {tools}"
    if agent_name == "research_critic_agent":
        if output["research_is_good_enough"]:
            return "Research looks good enough."
        return f"Gaps found: {output['critic_feedback']}"
    if agent_name == "report_writer_agent":
        return f"Report saved to {output['report_file_path']}"
    return ""


def sse(event_name: str, data: dict) -> str:
    """Format one Server-Sent Event."""
    return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/research/stream")
async def research_stream(topic: str):
    async def event_generator():
        try:
            # stream_mode="updates" yields {node_name: what_that_node_returned}
            # every time one agent finishes.
            async for update in app.state.research_graph.astream(
                {"topic": topic}, stream_mode="updates"
            ):
                for agent_name, output in update.items():
                    yield sse("agent_finished", {
                        "agent": agent_name,
                        "message": describe_agent_result(agent_name, output),
                    })
                    if agent_name == "report_writer_agent":
                        yield sse("final_report", {"report": output["final_report"]})
        except Exception as error:  # learning project: just show the error
            yield sse("error", {"message": str(error)})
        yield sse("done", {})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
