import logfire


def init():
    logfire.configure()
    logfire.instrument_pydantic_ai()
    logfire.instrument_asyncpg()
    logfire.instrument_mcp()
    # logfire.instrument_pydantic()
    # logfire.instrument_system_metrics()
