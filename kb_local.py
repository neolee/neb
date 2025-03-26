from __future__ import annotations as _annotations
from dataclasses import dataclass

from pathlib import Path
import asyncio

import asyncpg

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent
from openai import AsyncOpenAI

from util.fs import list_files
from rag.text.pdf_loader import PDFLoader
from embedders import snowflake
from rag.store.pgvector import PgVectorStore, Section

kb_store = PgVectorStore(
    embedder=snowflake,
    dsn="postgresql://paradigmx@localhost",
    db="zion",
    table="books"
)

import logfire
import instrument
instrument.init()
logfire.instrument_openai(snowflake.client)


## rag agent

@dataclass
class Deps:
    client: AsyncOpenAI
    pool: asyncpg.Pool

import mal.pydantic_ai.model as model
rag_agent = Agent(model=model.default, deps_type=Deps)

@rag_agent.tool
async def retrieve(context: RunContext[Deps], query: str) -> str:
    """Retrieve documentation sections based on a search query.

    args:
        context: the call context.
        query: the search query.
    """
    return await kb_store.retrieve(query, context.deps.pool, 10)

async def run_agent(question: str):
    """Entry point to run the agent and perform RAG based question answering."""
    logfire.info("Asking '{question}'", question=question)

    async with kb_store.connect() as pool:
        deps = Deps(client=snowflake.client, pool=pool)
        answer = await rag_agent.run(question, deps=deps)
    print(answer.data)


## biuld the search database

async def prepare_book_content(path: Path) -> list[Section]:
    file_path = str(path)
    with logfire.span("Loading data from {file}", file=file_path):
        loader = PDFLoader(file_path)
        chunks = loader.chunks(batch_size=10)
        sections = []
        for idx, chunk in enumerate(chunks):
            uri = str(path / str(idx))
            title = f"{path.stem} #{idx}"
            content = chunk
            embedding_content = "\n\n".join((f"title: {title}", content))
            sections.append(Section(uri, title, content, embedding_content))
    return sections

async def build_search_db():
    """Build the search database."""
    parent = "./books"
    paths = list_files(parent, ".pdf")

    for path in paths:
        sections = await prepare_book_content(path)
        await kb_store.load(sections)

    
if __name__ == "__main__":
    import sys

    action = sys.argv[1] if len(sys.argv) > 1 else None
    if action == "build":
        asyncio.run(build_search_db())
    elif action == "search":
        if len(sys.argv) == 3:
            q = sys.argv[2]
        else:
            q = "What is CAP theorem in softwar architecture?"
        asyncio.run(run_agent(q))
    else:
        print(
            "uv run kb_local.py build|search",
            file=sys.stderr,
        )
        sys.exit(1)
