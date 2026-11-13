"""
THE GRAPH: how the four agents are wired together.

    START
      |
      v
  research_planner_agent
      |
      v
  web_researcher_agent  <---------+
      |                           |
      v                           | (gaps found, and we still have rounds left)
  research_critic_agent ----------+
      |
      | (good enough, or out of rounds)
      v
  report_writer_agent
      |
      v
     END

Node  = an agent (a function: state in -> partial state out)
Edge  = "run this one next"
Conditional edge = "ask a function which one to run next"
"""
from langgraph.graph import END, START, StateGraph

from app.agents.report_writer_agent import create_report_writer_agent
from app.agents.research_critic_agent import create_research_critic_agent
from app.agents.research_planner_agent import create_research_planner_agent
from app.agents.web_researcher_agent import create_web_researcher_agent
from app.config import MAX_RESEARCH_ROUNDS
from app.mcp_tools.load_mcp_tools import pick_tools
from app.state import ResearchState


def decide_what_happens_after_critic(state: ResearchState) -> str:
    """The routing function. Returns the NAME of the next node."""
    if state["research_is_good_enough"]:
        return "report_writer_agent"
    if state["research_round"] >= MAX_RESEARCH_ROUNDS:
        return "report_writer_agent"  # stop looping, write with what we have
    return "web_researcher_agent"     # go back and fill the gaps


def build_research_graph(llm, all_mcp_tools):
    # Each agent receives only the MCP tools it needs.
    researcher_tools = pick_tools(
        all_mcp_tools,
        ["search_wikipedia", "get_summary", "search_papers", "get_abstract", "fetch"],
    )
    write_file_tool = pick_tools(all_mcp_tools, ["write_file"])[0]

    graph = StateGraph(ResearchState)

    # 1) Register the agents as nodes
    graph.add_node("research_planner_agent", create_research_planner_agent(llm))
    graph.add_node("web_researcher_agent", create_web_researcher_agent(llm, researcher_tools))
    graph.add_node("research_critic_agent", create_research_critic_agent(llm))
    graph.add_node("report_writer_agent", create_report_writer_agent(llm, write_file_tool))

    # 2) Fixed edges (always go from A to B)
    graph.add_edge(START, "research_planner_agent")
    graph.add_edge("research_planner_agent", "web_researcher_agent")
    graph.add_edge("web_researcher_agent", "research_critic_agent")
    graph.add_edge("report_writer_agent", END)

    # 3) Conditional edge (a function picks the next node)
    graph.add_conditional_edges(
        "research_critic_agent",
        decide_what_happens_after_critic,
        ["web_researcher_agent", "report_writer_agent"],
    )

    return graph.compile()
