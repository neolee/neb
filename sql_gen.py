import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Union

import asyncpg

import logfire
import instrument
instrument.init()

from annotated_types import MinLen
from devtools import debug
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai import format_as_xml

import models as m


DB_SCHEMA = """
CREATE TABLE records (
    created_at timestamptz,
    start_timestamp timestamptz,
    end_timestamp timestamptz,
    trace_id text,
    span_id text,
    parent_span_id text,
    level log_level,
    span_name text,
    message text,
    attributes_json_schema text,
    attributes jsonb,
    tags text[],
    is_exception boolean,
    otel_status_message text,
    service_name text
);
"""

SQL_EXAMPLES = [
    {
        "request": "show me records where foobar is false",
        "response": "SELECT * FROM records WHERE attributes->>'foobar' = false",
    },
    {
        "request": "show me records where attributes include the key 'foobar'",
        "response": "SELECT * FROM records WHERE attributes ? 'foobar'",
    },
    {
        "request": "show me records from yesterday",
        "response": "SELECT * FROM records WHERE start_timestamp::date > CURRENT_TIMESTAMP - INTERVAL '1 day'",
    },
    {
        "request": "show me error records with the tag 'foobar'",
        "response": "SELECT * FROM records WHERE level = 'error' and 'foobar' = ANY(tags)",
    },
]


@dataclass
class Deps:
    conn: asyncpg.Connection


class Success(BaseModel):
    """Response when SQL could be successfully generated."""

    sql_query: Annotated[str, MinLen(1)]
    explanation: str = Field(
        "", description="Explanation of the SQL query, as markdown"
    )


class InvalidRequest(BaseModel):
    """Response the user input didn"t include enough information to generate SQL."""

    error_message: str


Response: TypeAlias = Union[Success, InvalidRequest]
sql_gen_agent: Agent[Deps, Response] = Agent(
    model=m.default,
    # type ignore while we wait for PEP-0747, nonetheless unions will work fine everywhere else
    output_type=Response, # type: ignore
    deps_type=Deps
)


@sql_gen_agent.system_prompt
async def system_prompt() -> str:
    return f"""\
Given the following PostgreSQL table of records, your job is to
write a SQL query that suits the user's request.

Database schema:

{DB_SCHEMA}

today's date = {date.today()}

{format_as_xml(SQL_EXAMPLES)}
"""


@sql_gen_agent.output_validator
async def validate_result(ctx: RunContext[Deps], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result

    # gemini often adds extraneous backslashes to SQL
    result.sql_query = result.sql_query.replace("\\", "")
    if not result.sql_query.upper().startswith("SELECT"):
        raise ModelRetry("Please create a SELECT query")

    try:
        await ctx.deps.conn.execute(f"EXPLAIN {result.sql_query}")
    except asyncpg.exceptions.PostgresError as e:
        raise ModelRetry(f"Invalid query: {e}") from e
    else:
        return result


async def main():
    if len(sys.argv) == 1:
        prompt = "show me logs from yesterday, with level 'error'"
    else:
        prompt = sys.argv[1]

    async with database_connect("postgresql://paradigmx@localhost", "zion") as conn:
        deps = Deps(conn)
        result = await sql_gen_agent.run(prompt, deps=deps)
    debug(result.output)


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
@asynccontextmanager
async def database_connect(server_dsn: str, database: str) -> AsyncGenerator[Any, None]:
    with logfire.span("check and create DB"):
        conn = await asyncpg.connect(f"{server_dsn}/postgres")
        try:
            db_exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", database
            )
            if not db_exists:
                await conn.execute(f"CREATE DATABASE {database}")
        finally:
            await conn.close()

    conn = await asyncpg.connect(f"{server_dsn}/{database}")
    try:
        with logfire.span("create schema"):
            async with conn.transaction():
                if not db_exists:
                    await conn.execute(
                        "CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical')"
                    )
                    await conn.execute(DB_SCHEMA)
        yield conn
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
