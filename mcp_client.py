from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from pydantic_ai.mcp import MCPServerStdio

import instrument
instrument.init()

import mal.pydantic_ai.model as model


server_sse = MCPServerHTTP(url='http://localhost:3001/sse')
agent_sse = Agent(model.default, mcp_servers=[server_sse])

server_stdio = MCPServerStdio('npx', ['-y', '@pydantic/mcp-run-python', 'stdio'])
agent_stdio = Agent(model.default, mcp_servers=[server_stdio])

async def run(agent):
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-28?')
    print(result.data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run(agent_sse))
