import asyncio

from pydantic_ai import Agent

from util.pydantic_ai import stream_markdown
import models as m

import instrument
instrument.init()


models = [m.deepseek, m.gpt]
async def main():
    prompt = 'Show me a short example of using Pydantic.'
    for model in models:
        agent = Agent(model=model)
        await stream_markdown(agent, prompt)


if __name__ == '__main__':
    asyncio.run(main())
