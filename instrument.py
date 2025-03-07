import logfire
from pydantic_ai import Agent


logfire.configure()

Agent.instrument_all()
