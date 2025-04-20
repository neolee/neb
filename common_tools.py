from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.common_tools.tavily import tavily_search_tool
import mal.pydantic_ai.model as model


## duckduckgo tool
agent = Agent(
    model=model.default,
    tools=[duckduckgo_search_tool()],
    system_prompt='Search DuckDuckGo for the given query and return the results.',
)

result = agent.run_sync(
    'Can you list the top five highest-grossing animated films of 2025?'
)
print(result.output)


## tavily tool
import os
api_key = os.getenv('TAVILY_API_KEY')
assert api_key is not None

agent = Agent(
    model=model.default,
    tools=[tavily_search_tool(api_key)],
    system_prompt='Search Tavily for the given query and return the results.',
)

result = agent.run_sync('Tell me the top news in the GenAI world, give me links.')
print(result.output)
