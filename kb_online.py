from __future__ import annotations as _annotations
from dataclasses import dataclass

import asyncio

import httpx

from pydantic import TypeAdapter
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from embedders import nomic
from rag.store.base import Section, RAGStore

## easily change vector store backend as below
# pgvector
from rag.store.pgvector import PgVectorStore
kb_store = PgVectorStore(
    embedder=nomic,
    dsn="postgresql://paradigmx@localhost",
    db="zion",
    table="logfire_docs"
)
# chromedb
# from rag.store.chroma import ChromaStore
# kb_store = ChromaStore(
#     embedder=nomic,
#     name="logfire_docs",
#     path="./local/chromadb"
# )

import logfire
import instrument
instrument.init()
logfire.instrument_openai(nomic.client)


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


## build the search database (and some utilities)
from util.logfire_docs import doc_json_url, make_doc_uri

# data class for doc json parsing
@dataclass
class DocSection:
    id: int
    parent: int | None
    path: str
    level: int
    title: str
    content: str

    def uri(self) -> str:
        return make_doc_uri(self.title, self.path)

    def embedding_content(self) -> str:
        return "\n\n".join((f"path: {self.path}", f"title: {self.title}", self.content))

async def prepare_content() -> list[Section]:
    sessions_ta = TypeAdapter(list[DocSection])
    async with httpx.AsyncClient() as client:
        response = await client.get(doc_json_url)
        response.raise_for_status()
    doc_sections = sessions_ta.validate_json(response.content)
    return [Section(ds.uri(), ds.title, ds.content, ds.embedding_content())
            for ds in doc_sections]

async def build_search_db():
    """Build the search database."""
    sections = await prepare_content()
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
            q = "How do I configure logfire to work with FastAPI?"
        asyncio.run(run_agent(q))
    else:
        print(
            "uv run kb_online.py build|search",
            file=sys.stderr,
        )
        sys.exit(1)
