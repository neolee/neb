from __future__ import annotations as _annotations
from dataclasses import dataclass

from pathlib import Path
import asyncio

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from util.fs import list_files
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

import mal.pydantic_ai.model as model
rag_agent = Agent(model=model.default, deps_type=Deps)

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

    deps = Deps(kb_store)
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
