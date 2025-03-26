import asyncio

from src.clients.mcp_client.client import MCPClient

client = MCPClient(
      command="/usr/bin/uv", args=[
          "run",
          "--directory",
          "/home/dima/dev/chift/mcp",
          "python",
          "main.py"
      ], env={
          "CHIFT_CLIENT_SECRET": "sdf",
          "CHIFT_CLIENT_ID": "asd",
          "CHIFT_ACCOUNT_ID": "sda",
          "CHIFT_URL_BASE": "http://chift.localhost:8000",
          "CHIFT_CONSUMER_ID": "asd"
      }
      )




async def run():
      res = await client.list_tools()
      tools = res.tools
      for i in tools:
            print(i)
      #print(res)


asyncio.run(run())
