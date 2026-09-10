import mcp.types as types
from mcp.server import Server

app = Server("apollo-memory")

async def handle_list_tools(params: types.PaginatedRequestParams | None = None) -> types.ListToolsResult:
    return types.ListToolsResult(tools=[])

async def handle_call_tool(params: types.CallToolRequestParams) -> types.CallToolResult:
    return types.CallToolResult(content=[])

app.add_request_handler("tools/list", types.PaginatedRequestParams, handle_list_tools)
app.add_request_handler("tools/call", types.CallToolRequestParams, handle_call_tool)

print("Handlers registered successfully!")
