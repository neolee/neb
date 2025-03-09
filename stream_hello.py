import asyncio
from pydantic_ai import Agent
import mal.pydantic_ai.model as model


agent = Agent(model=model.default)

async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:
        async for message in result.stream_text(delta=True):
            print(message or "", end="", flush=True)


asyncio.run(main())
