"""
AGENT 1: Research Planner
-------------------------
Job:    Break the topic into a few focused sub-questions.
Tools:  NONE. Pure LLM reasoning.
Learns: structured output (the LLM must reply in a fixed shape, not free text).
"""
from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """The exact shape we force the LLM to answer in."""
    sub_questions: list[str] = Field(
        description="3 to 4 specific questions that together cover the topic"
    )


def create_research_planner_agent(llm):
    planner_llm = llm.with_structured_output(ResearchPlan)

    async def research_planner_agent(state):
        plan = await planner_llm.ainvoke(
            f"You are a research planner. Topic: '{state['topic']}'.\n"
            "Split it into 3 to 4 specific sub-questions that a researcher "
            "can answer using Wikipedia, arXiv papers and web pages."
        )
        # Return ONLY what changed. LangGraph merges this into the shared state.
        return {"sub_questions": plan.sub_questions, "research_round": 0}

    return research_planner_agent
