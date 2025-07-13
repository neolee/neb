import logfire
from pydantic_ai import Agent


def init():
    logfire.configure(send_to_logfire='if-token-present')
    logfire.instrument_system_metrics()
    logfire.instrument_asyncpg()
    logfire.instrument_pydantic_ai()
    logfire.instrument_pydantic()
    logfire.instrument_mcp()

    Agent.instrument_all()
