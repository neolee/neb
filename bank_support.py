from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import mal.pydantic_ai.model as model

import instrument
instrument.init()

from bank_db import BankDBConn


@dataclass
class SupportDependencies:
    account_number: str
    db: BankDBConn


class SupportResult(BaseModel):
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description='Whether to block their card or not')
    risk: int = Field(description='Risk level of query', ge=0, le=10)


support_agent = Agent(
    model.default,
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query. '
        "Reply using the customer's name."
    ),
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(query_id=ctx.deps.account_number)
    return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(ctx: RunContext[SupportDependencies], include_pending: bool) -> str:
    """Returns the customer's current account balance."""
    balance = await ctx.deps.db.customer_balance(
        query_id=ctx.deps.account_number,
        include_pending=include_pending,
    )
    return f'${balance:.2f}'


if __name__ == '__main__':
    deps = SupportDependencies(account_number="101", db=BankDBConn())

    result = support_agent.run_sync('What is my balance?', deps=deps)
    print(result.data)

    result = support_agent.run_sync('I just lost my card!', deps=deps)
    print(result.data)
