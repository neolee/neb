from pydantic_ai import Agent, RunContext
import models as m

import instrument
instrument.init()


roulette_agent = Agent(
    model=m.default,
    deps_type=int,
    output_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
    instrument=True,
)

@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# run the agent
import random
success_number = random.randint(1, 5)
print("winning number: ", success_number)
result = roulette_agent.run_sync('Put my money on square two', deps=success_number)
print(result.output)

result = roulette_agent.run_sync('I bet four is the winner', deps=success_number)
print(result.output)
