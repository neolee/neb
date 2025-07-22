from __future__ import annotations as _annotations
from dataclasses import dataclass

from pathlib import Path
import asyncio

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from util.fs import list_files
# BUG the following line cause the infamous `Overriding of current TracerProvider is not allowed` warning
# cause: `PDFLoader` uses `marker-pdf` and `marker-pdf` uses `transformers`, which uses `opentelemetry` in
#        a wrong way, see https://github.com/huggingface/transformers/issues/39115
# UPDATE: already fixed in `transformers 4.53.3`
from rag.text.pdf_loader import PDFLoader

from embedders import snowflake
from rag.store.base import Section, RAGStore

## easily change vector store backend as below
# pgvector
from rag.store.pgvector import PgVectorStore
kb_store = PgVectorStore(
    embedder=snowflake,
    dsn="postgresql://paradigmx@localhost",
    db="zion",
    table="books"
)
# chromedb
# from rag.store.chroma import ChromaStore
# kb_store = ChromaStore(
#     embedder=snowflake,
#     name="books",
#     path="./local/chromadb"
# )

import logfire
import instrument
instrument.init()
logfire.instrument_openai(snowflake.client)


## rag agent

@dataclass
class Deps:
    store: RAGStore

import models as m
rag_agent = Agent(model=m.default, deps_type=Deps)

@rag_agent.tool
async def retrieve(context: RunContext[Deps], query: str) -> str:
    """Retrieve documentation sections based on a search query.

    args:
        context: the call context.
        query: the search query.
    """
    return await context.deps.store.retrieve(query, 10)

async def run_agent(question: str):
    """Entry point to run the agent and perform RAG based question answering."""
    logfire.info("Asking '{question}'", question=question)

    deps = Deps(store=kb_store)
    answer = await rag_agent.run(question, deps=deps)
    print(answer.output)


## build the search database

async def prepare_book_content(path: Path) -> list[Section]:
    with logfire.span("loading data from file"):
        loader = PDFLoader(str(path))
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

    with logfire.span("Loading local books to knowledge store"):
        for path in paths:
            with logfire.span("working on {file}", file=str(path)):
                sections = await prepare_book_content(path)
                with logfire.span("saving data to knowledge store"):
                    await kb_store.load(sections)


## put all things together

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
