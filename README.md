# chift-ai-toolkit

chift-ai-toolkit provides examples of how to use Chift MCP server.

## Table of Contents
- [Introduction](#introduction)
- [PydanticAI](#pydanticai)
  - [HTTP SSE Transport](#http-sse-transport)
  - [stdio Transport](#stdio-transport)
- [Copilot MCP Client for VSCode](#copilot-mcp-client-for-vscode)
  - [Process-based Server Configuration](#process-based-server-configuration)
  - [SSE Server Configuration](#sse-server-configuration)
  - [Usage in Copilot Chat](#usage-in-copilot-chat)
- [Vercel AI SDK](#vercel-ai-sdk)
  - [Using SSE Transport](#using-sse-transport)
  - [Using Stdio Transport](#using-stdio-transport)
  - [Next.js Route Handler Example](#nextjs-route-handler-example)
- [Claude for Desktop](#claude-for-desktop)
  - [Configuration](#configuration)
  - [Using with SSE Server](#using-with-sse-server)
  - [After Configuration](#after-configuration)
  - [Example Prompts](#example-prompts)

## Introduction

Useful links:
- [Chift Website](https://www.chift.eu/)
- [Chift Python SDK](https://github.com/chift-oneapi/chift-python-sdk)
- [Chift MCP Server](https://github.com/chift-oneapi/mcp)
- [Chift API Documentation](https://docs.chift.eu/api-reference/overview)

## PydanticAI

PydanticAI allows you to easily integrate Chift API with your AI agents.

Documentation:
- [PydanticAI Website](https://ai.pydantic.dev/)
- [PydanticAI MCP Client Documentation](https://ai.pydantic.dev/mcp/client/)

### HTTP SSE Transport

```bash
# Start the Chift MCP server in SSE mode
export CHIFT_CLIENT_SECRET="your_client_secret"
export CHIFT_CLIENT_ID="your_client_id"
export CHIFT_ACCOUNT_ID="your_account_id"
export CHIFT_CONSUMER_ID="your_consumer_id"
export CHIFT_URL_BASE="https://api.chift.eu"

uvx chift-mcp-server sse
```

```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

# Connect to the Chift MCP server
server = MCPServerHTTP(url='http://localhost:3001/sse')
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('''
        Please list all available Chift consumers and 
        show the connections for the first consumer.
        ''')
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

### stdio Transport

```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Define environment variables for the subprocess
env = {
    "CHIFT_CLIENT_SECRET": "your_client_secret",
    "CHIFT_CLIENT_ID": "your_client_id",
    "CHIFT_ACCOUNT_ID": "your_account_id",
    "CHIFT_CONSUMER_ID": "your_consumer_id",
    "CHIFT_URL_BASE": "https://api.chift.eu"
}

# Create a server that will be run as a subprocess
server = MCPServerStdio('uvx', ['chift-mcp-server', 'stdio'], env=env)
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('''
        Please get details about consumer with ID "consumer123" 
        and list all of its available connections.
        ''')
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Copilot MCP Client for VSCode

Documentation:
- [Copilot MCP Client](https://github.com/VikashLoomba/copilot-mcp)

### Process-based Server Configuration

```json
{
  "mcpManager.servers": [
    {
      "name": "Chift MCP Server",
      "type": "process",
      "command": "uvx chift-mcp-server stdio",
      "enabled": true,
      "env": {
        "CHIFT_CLIENT_SECRET": "your_client_secret",
        "CHIFT_CLIENT_ID": "your_client_id",
        "CHIFT_ACCOUNT_ID": "your_account_id",
        "CHIFT_CONSUMER_ID": "your_consumer_id",
        "CHIFT_URL_BASE": "https://api.chift.eu"
      }
    }
  ]
}
```

### SSE Server Configuration

```json
{
  "mcpManager.servers": [
    {
      "name": "Chift MCP Server (SSE)",
      "type": "sse",
      "url": "http://localhost:8888/events",
      "enabled": true
    }
  ]
}
```

For the SSE configuration, you need to start the Chift MCP server separately with:

```bash
export CHIFT_CLIENT_SECRET="your_client_secret"
export CHIFT_CLIENT_ID="your_client_id"
export CHIFT_ACCOUNT_ID="your_account_id"
export CHIFT_CONSUMER_ID="your_consumer_id"
export CHIFT_URL_BASE="https://api.chift.eu"

uvx chift-mcp-server sse
```

### Usage in Copilot Chat

Once configured, open GitHub Copilot Chat in VSCode and use the `@mcp` participant to access Chift API tools:

```
@mcp Please list all available Chift consumers
```

You can also force a tool call by using the '#' key and selecting the specific Chift API tool you want to use.

## Vercel AI SDK

Documentation:
- [Vercel AI SDK](https://sdk.vercel.ai/docs/introduction)

### Using SSE Transport

```javascript
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

// Start the Chift MCP server with your environment variables first
// uvx chift-mcp-server sse

async function main() {
  // Initialize MCP client with SSE transport
  const mcpClient = await createMCPClient({
    transport: {
      type: 'sse',
      url: 'http://localhost:8888/events',
      // Optional: Add headers if your server requires authentication
      headers: {
        // Authorization: 'Bearer your_auth_token_if_needed',
      },
    },
  });

  try {
    // Get all Chift tools from the MCP server
    const chiftTools = mcpClient.tools();

    // Use the tools with a language model
    const result = await streamText({
      model: openai('gpt-4o'),
      tools: chiftTools,
      prompt: 'List all available Chift consumers and get details for the first one.',
      onFinish: async () => {
        // Make sure to close the client when finished
        await mcpClient.close();
      },
    });

    // Process the streaming response
    for await (const chunk of result) {
      if (chunk.type === 'text-delta') {
        process.stdout.write(chunk.textDelta);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    await mcpClient.close();
  }
}

main();
```

### Using Stdio Transport

```javascript
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { Experimental_StdioMCPTransport as StdioMCPTransport } from 'ai/mcp-stdio';
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

async function main() {
  let mcpClient;
  
  try {
    // Initialize MCP client with stdio transport
    mcpClient = await createMCPClient({
      transport: new StdioMCPTransport({
        command: 'uvx',
        args: ['chift-mcp-server', 'stdio'],
        // Pass Chift environment variables
        env: {
          CHIFT_CLIENT_SECRET: 'your_client_secret',
          CHIFT_CLIENT_ID: 'your_client_id',
          CHIFT_ACCOUNT_ID: 'your_account_id',
          CHIFT_CONSUMER_ID: 'your_consumer_id',
          CHIFT_URL_BASE: 'https://api.chift.eu',
        },
      }),
    });

    // Define specific tool schemas (optional - for better type safety)
    const tools = await mcpClient.tools({
      schemas: {
        'consumers': {
          description: 'Get list of available consumers',
        },
        'get_consumer': {
          description: 'Get specific consumer',
          parameters: z.object({
            consumer_id: z.string().describe('The ID of the consumer to retrieve')
          }),
        },
        'consumer_connections': {
          description: 'Get list of connections for a specific consumer',
          parameters: z.object({
            consumer_id: z.string().describe('The ID of the consumer to get connections for')
          }),
        },
      },
    });

    // Use the tools with a language model
    const { text } = await generateText({
      model: openai('gpt-4o'),
      tools,
      maxSteps: 5, // Allow multiple tool calls in sequence
      prompt: 'Get all available consumers and then show me the connections for the first one.',
    });

    console.log(text);
  } finally {
    // Make sure to close the client
    await mcpClient?.close();
  }
}

main();
```

### Next.js Route Handler Example

```javascript
// app/api/chift/route.js
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { Experimental_StdioMCPTransport as StdioMCPTransport } from 'ai/mcp-stdio';

export async function POST(req) {
  const { prompt } = await req.json();
  
  // Initialize MCP client
  const mcpClient = await createMCPClient({
    transport: new StdioMCPTransport({
      command: 'uvx',
      args: ['chift-mcp-server', 'stdio'],
      env: {
        CHIFT_CLIENT_SECRET: process.env.CHIFT_CLIENT_SECRET,
        CHIFT_CLIENT_ID: process.env.CHIFT_CLIENT_ID,
        CHIFT_ACCOUNT_ID: process.env.CHIFT_ACCOUNT_ID,
        CHIFT_CONSUMER_ID: process.env.CHIFT_CONSUMER_ID,
        CHIFT_URL_BASE: process.env.CHIFT_URL_BASE || 'https://api.chift.eu',
      },
    }),
  });

  try {
    // Get tools from the MCP server
    const tools = mcpClient.tools();
    
    // Stream the response
    const stream = streamText({
      model: openai('gpt-4o'),
      tools,
      maxSteps: 3,
      prompt,
      onFinish: async () => {
        await mcpClient.close();
      },
    });
    
    return new Response(stream);
  } catch (error) {
    await mcpClient.close();
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
```

## Claude for Desktop

### Configuration

Open Claude Desktop settings and edit the configuration file by:
1. Click on the Claude menu on your computer
2. Select "Settings..."
3. Click on "Developer" in the left-hand bar
4. Click on "Edit Config"

Then add the Chift MCP server configuration:

```json
{
  "mcpServers": {
    "chift": {
      "command": "uvx",
      "args": [
        "chift-mcp-server",
        "stdio"
      ],
      "env": {
        "CHIFT_CLIENT_SECRET": "your_client_secret",
        "CHIFT_CLIENT_ID": "your_client_id",
        "CHIFT_ACCOUNT_ID": "your_account_id", 
        "CHIFT_CONSUMER_ID": "your_consumer_id",
        "CHIFT_URL_BASE": "https://api.chift.eu"
      }
    }
  }
}
```

Make sure to replace the environment variables with your actual Chift API credentials.

### Using with SSE Server

If you prefer to use the SSE server instead of stdio, you need to:

1. Start the Chift MCP server separately with your environment variables:

```bash
export CHIFT_CLIENT_SECRET="your_client_secret"
export CHIFT_CLIENT_ID="your_client_id"
export CHIFT_ACCOUNT_ID="your_account_id"
export CHIFT_CONSUMER_ID="your_consumer_id"
export CHIFT_URL_BASE="https://api.chift.eu"

uvx chift-mcp-server sse
```

2. Then configure Claude Desktop to connect to the SSE server:

```json
{
  "mcpServers": {
    "chift": {
      "type": "sse",
      "url": "http://localhost:8888/events"
    }
  }
}
```

### After Configuration

1. Restart Claude for Desktop
2. You should see a hammer icon in the chat input area
3. Click on the hammer to see the available Chift API tools
4. Start chatting with Claude using the Chift tools

### Example Prompts

- "Can you list all available Chift consumers?"
- "Get the details for consumer with ID X"
- "Show me all connections for the first consumer"
