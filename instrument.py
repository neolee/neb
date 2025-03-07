import logfire
from pydantic_ai import Agent


def init():
    logfire.configure()
    Agent.instrument_all()
