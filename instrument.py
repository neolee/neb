import logfire
from pydantic_ai import Agent


def init():
    logfire.configure(send_to_logfire='if-token-present')
    logfire.instrument_asyncpg()
    Agent.instrument_all()
