from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.mcp import MCPServerStreamableHTTP

import models as m
import instrument
instrument.init()


server_stdio = MCPServerStdio('uvx', args=["mcp-run-python", "stdio"], timeout=10)
agent_stdio = Agent(m.default, toolsets=[server_stdio])

# info: https://github.com/pydantic/mcp-run-python
# before running the client code ensure running the server using:
# uvx mcp-run-python --port 3001 streamable-http
server_http = MCPServerStreamableHTTP(url="http://localhost:3001/mcp")
agent_http = Agent(m.default, toolsets=[server_http])

today = datetime.now().strftime("%Y-%m-%d")

async def run(agent):
    async with agent.run_mcp_servers():
        result = await agent.run(f"How many days between 2000-01-01 and {today}?")
    print(result.output)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(run(agent_stdio))
    asyncio.run(run(agent_http))
