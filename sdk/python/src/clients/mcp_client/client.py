from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from mcp import (
    ClientSession,
    StdioServerParameters,
    types,
)
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
    ):
        """
        Initialize the MCP Client

        Args:
            command: Command to execute the MCP server
            args: Optional command arguments
            env: Optional environment variables
        """
        self.server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env or {}
        )

    async def _execute_method(self, method_name, **kwargs):
        """Execute a method on a fresh client session"""
        async with stdio_client(server=self.server_params) as (read, write):
            async with ClientSession(read_stream=read, write_stream=write) as session:
                await session.initialize()
                method = getattr(session, method_name)
                return await method(**kwargs)

    async def list_tools(self) -> types.ListToolsResult:
        """Get a list of available tools from the server"""
        return await self._execute_method("list_tools")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server"""
        return await self._execute_method("call_tool", name=name, arguments=arguments)

    async def list_resources(self) -> List[types.Resource]:
        """Get a list of available resources from the server"""
        return await self._execute_method("list_resources")

    async def read_resource(self, uri: str) -> Tuple[bytes, str]:
        """Read a resource from the MCP server"""
        return await self._execute_method("read_resource", uri=uri)

    async def list_prompts(self) -> List[types.Prompt]:
        """Get a list of available prompts from the server"""
        return await self._execute_method("list_prompts")

    async def get_prompt(
        self, name: str, arguments: Optional[Dict[str, str]] = None
    ) -> types.GetPromptResult:
        """Get a prompt template from the MCP server"""
        return await self._execute_method("get_prompt", name=name, arguments=arguments)