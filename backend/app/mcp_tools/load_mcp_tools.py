"""
STEP 1 OF MCP: connect to the servers and ask "what tools do you have?"

MCP tools are discovered at runtime. We never hard-code what `fetch` can do:
the server tells us (name, description, input schema), and the adapter library
turns each one into a normal LangChain tool that LangGraph agents can call.
"""
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.mcp_tools.mcp_server_config import MCP_SERVERS


async def load_all_mcp_tools() -> dict[str, BaseTool]:
    """Returns {tool_name: tool} for every tool from every MCP server."""
    mcp_client = MultiServerMCPClient(MCP_SERVERS)
    all_tools = await mcp_client.get_tools()  # starts each server and lists its tools
    tool_dict = {tool.name: tool for tool in all_tools}
    print("tool_dict", tool_dict)
    return tool_dict


def pick_tools(all_tools: dict[str, BaseTool], tool_names: list[str]) -> list[BaseTool]:
    """
    Give an agent ONLY the tools it needs (least privilege).
    The Wikipedia server alone exposes ~12 tools. Fewer tools means
    a less confused model and a safer agent.
    """
    missing = [name for name in tool_names if name not in all_tools]
    if missing:
        raise RuntimeError(f"MCP tools not found: {missing}. Found: {sorted(all_tools)}")
    return [all_tools[name] for name in tool_names]
