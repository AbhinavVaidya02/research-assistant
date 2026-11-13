"""
AGENT 2: Web Researcher   <-- the agent that actually uses MCP tools
-------------------------------------------------------------------
Job:    Answer the sub-questions by searching and reading sources.
Tools:  MCP tools from 3 servers: wikipedia, arxiv, fetch.
Learns: the tool-calling loop (ReAct):

            LLM thinks -> "I need to call a tool" -> tool runs (via MCP)
                ^                                          |
                +------------ result goes back ------------+
            ...repeats until the LLM has enough, then it writes an answer.

`create_react_agent` from LangGraph gives us exactly this loop for free.
"""
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import create_react_agent

from app.utils import message_to_text

RESEARCHER_INSTRUCTIONS = """You are a careful research assistant.
Use your tools to find facts for each sub-question:
- search_wikipedia / get_summary for background and definitions
- search_papers / get_abstract for academic research
- fetch to read a specific web page URL

Rules:
- Do not answer from memory. Use tools, and keep a source link for every fact.
- Be efficient: at most 2 or 3 tool calls per sub-question.
- Reply with short bullet-point notes grouped by sub-question, each with its source."""


def create_web_researcher_agent(llm, research_tools):
    react_agent = create_react_agent(llm, research_tools, prompt=RESEARCHER_INSTRUCTIONS)

    async def web_researcher_agent(state):
        task = f"Topic: {state['topic']}\nSub-questions:\n"
        task += "\n".join(f"- {question}" for question in state["sub_questions"])

        # Second round? The critic told us what was missing, so focus on that.
        critic_feedback = state.get("critic_feedback")
        if critic_feedback:
            task += f"\n\nA reviewer found these gaps. Research ONLY these:\n{critic_feedback}"

        result = await react_agent.ainvoke(
            {"messages": [("user", task)]},
            config={"recursion_limit": 25},  # safety cap on the tool loop
        )

        new_notes = message_to_text(result["messages"][-1])
        tools_called = [m.name for m in result["messages"] if isinstance(m, ToolMessage)]

        # Keep notes from earlier rounds and add the new ones.
        all_notes = (state.get("research_notes", "") + "\n\n" + new_notes).strip()

        return {
            "research_notes": all_notes,
            "research_round": state.get("research_round", 0) + 1,
            "tools_used": tools_called,
        }

    return web_researcher_agent
