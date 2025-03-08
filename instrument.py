import logfire
from pydantic_ai import Agent


def init():
    logfire.configure()
    logfire.instrument_asyncpg()
    Agent.instrument_all()
