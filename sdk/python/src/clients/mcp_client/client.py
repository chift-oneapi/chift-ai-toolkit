from typing import (
    Any,
)

from loguru import logger
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
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
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
        self.session = None
        self.read_stream = None
        self.write_stream = None
        self.connected = False

    async def connect(self) -> None:
        """Connect to the MCP server"""
        if self.connected:
            return

        try:
            self.read_stream, self.write_stream = stdio_client(server=self.server_params)
            self.session = ClientSession(
                read_stream=self.read_stream,
                write_stream=self.write_stream,
            )
            await self.session.initialize()
            self.connected = True
            logger.info("Successfully connected to the MCP server")
        except Exception as e:
            logger.error(f"Failed to connect to the MCP server: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.close()
            self.connected = False
            logger.info("Disconnected from the MCP server")

    async def __aenter__(self) -> 'MCPClient':
        """Context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        await self.disconnect()

    async def list_tools(self) -> list[types.Tool]:
        """Get a list of available tools from the server"""
        if not self.connected:
            await self.connect()
        return await self.session.list_tools()

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server"""
        if not self.connected:
            await self.connect()
        return await self.session.call_tool(name, arguments)

    async def list_resources(self) -> list[types.Resource]:
        """Get a list of available resources from the server"""
        if not self.connected:
            await self.connect()
        return await self.session.list_resources()

    async def read_resource(self, uri: str) -> tuple[bytes, str]:
        """Read a resource from the MCP server"""
        if not self.connected:
            await self.connect()
        return await self.session.read_resource(uri)

    async def list_prompts(self) -> list[types.Prompt]:
        """Get a list of available prompts from the server"""
        if not self.connected:
            await self.connect()
        return await self.session.list_prompts()

    async def get_prompt(self, name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
        """Get a prompt template from the MCP server"""
        if not self.connected:
            await self.connect()
        return await self.session.get_prompt(name, arguments)


