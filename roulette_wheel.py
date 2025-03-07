from pydantic_ai import Agent, RunContext
import model


import logfire

logfire.configure()
Agent.instrument_all()


roulette_agent = Agent(
    model=model.default,
    deps_type=int,
    result_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# run the agent
success_number = 18
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.data)

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.data)
