from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.common_tools.tavily import tavily_search_tool

import instrument
instrument.init()

import mal.pydantic_ai.model as model
from util.pydantic_ai import stream_markdown


duckduckgo_agent = Agent(
    model=model.default,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search DuckDuckGo for the given query and return the results.",
)

import os
api_key = os.getenv("TAVILY_API_KEY")
assert api_key is not None

tavily_agent = Agent(
    model=model.default,
    tools=[tavily_search_tool(api_key)],
    system_prompt="Search Tavily for the given query and return the results.",
)


if __name__ == "__main__":
    q1 = "Can you list the top five highest-grossing animated films of 2025?"
    q2 = "Google I/O 2025"

    import asyncio

    # asyncio.run(stream_markdown(duckduckgo_agent, q2))
    asyncio.run(stream_markdown(tavily_agent, q2))
