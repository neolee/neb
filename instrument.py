import logfire


# more fine grained control through a callback, if needed
def scrubbing_callback(match: logfire.ScrubMatch):
    # `my_safe_value` often contains the string 'password' but it's not actually sensitive
    if match.path == ('attributes', 'my_safe_value') and match.pattern_match.group(0) == 'password':
        # return the original value to prevent redaction
        return match.value


def init():
    # logfire.configure(scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback))
    logfire.configure(scrubbing=False)
    logfire.instrument_pydantic_ai()
    logfire.instrument_asyncpg()
    logfire.instrument_mcp()
    # logfire.instrument_pydantic()
    # logfire.instrument_system_metrics()
