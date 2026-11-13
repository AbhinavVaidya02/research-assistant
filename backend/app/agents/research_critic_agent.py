"""
AGENT 3: Research Critic
------------------------
Job:    Judge the notes. Good enough to write a report, or are there gaps?
Tools:  NONE. Pure LLM reasoning.
Learns: an agent whose output decides the *route* the graph takes
        (see `decide_what_happens_after_critic` in graph/research_graph.py).
"""
from pydantic import BaseModel, Field


class CriticVerdict(BaseModel):
    is_good_enough: bool = Field(
        description="True if every sub-question is answered with a cited source"
    )
    feedback: str = Field(
        description="If not good enough: which sub-questions are weak or missing. "
                    "If good enough: leave empty."
    )


def create_research_critic_agent(llm):
    critic_llm = llm.with_structured_output(CriticVerdict)

    async def research_critic_agent(state):
        questions = "\n".join(f"- {q}" for q in state["sub_questions"])
        verdict = await critic_llm.ainvoke(
            "You are a strict but fair research reviewer.\n"
            f"Topic: {state['topic']}\n"
            f"Sub-questions:\n{questions}\n\n"
            f"Research notes:\n{state['research_notes']}\n\n"
            "Is every sub-question answered with a source? Judge the notes."
        )
        return {
            "research_is_good_enough": verdict.is_good_enough,
            "critic_feedback": verdict.feedback,
        }

    return research_critic_agent
