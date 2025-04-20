from pydantic_ai import Agent

import mal.pydantic_ai.model as model


agent = Agent(
    model=model.default,
    system_prompt='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
