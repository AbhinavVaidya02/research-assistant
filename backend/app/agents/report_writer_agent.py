"""
AGENT 4: Report Writer
----------------------
Job:    Turn the notes into a markdown report and SAVE it to a file.
Tools:  one MCP tool: `write_file` from the filesystem server.
Learns: calling an MCP tool DIRECTLY from our own code (no LLM deciding).
        When we already know exactly which tool to call, this is simpler
        and more reliable than letting a ReAct agent choose.
"""
import os

from app.config import REPORTS_FOLDER
from app.utils import make_file_name, message_to_text


def create_report_writer_agent(llm, write_file_tool):

    async def report_writer_agent(state):
        reply = await llm.ainvoke(
            "Write a clear markdown research report.\n"
            f"Topic: {state['topic']}\n\n"
            f"Research notes (use only these facts):\n{state['research_notes']}\n\n"
            "Structure: title, short summary, one section per key question, "
            "then a 'Sources' list with links. Do not invent facts or links."
        )
        report_markdown = message_to_text(reply)

        # Call the MCP tool directly: tool.ainvoke({...arguments...})
        file_path = os.path.join(REPORTS_FOLDER, make_file_name(state["topic"]))
        await write_file_tool.ainvoke({"path": file_path, "content": report_markdown})

        return {"final_report": report_markdown, "report_file_path": file_path}

    return report_writer_agent
