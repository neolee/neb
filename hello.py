from pydantic_ai import Agent

import models as m


agent = Agent(
    model=m.default,
    system_prompt='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
