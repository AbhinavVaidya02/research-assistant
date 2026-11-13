"""
THE SHARED STATE (LangGraph's most important idea).

Every agent reads from this dictionary and returns a *partial* update.
LangGraph merges each update into the state and passes it to the next agent.
Agents never call each other directly. They only communicate through this state.
"""
from typing import TypedDict


class ResearchState(TypedDict, total=False):
    # --- input ---
    topic: str                       # what the user wants researched

    # --- written by research_planner_agent ---
    sub_questions: list[str]         # the topic split into smaller questions

    # --- written by web_researcher_agent ---
    research_notes: str              # facts + source links found so far
    research_round: int              # how many times the researcher has run
    tools_used: list[str]            # which MCP tools were called (for the UI)

    # --- written by research_critic_agent ---
    research_is_good_enough: bool    # True = go write the report
    critic_feedback: str             # what is missing (if not good enough)

    # --- written by report_writer_agent ---
    final_report: str                # the finished markdown report
    report_file_path: str            # where the report was saved
