from __future__ import annotations as _annotations
from contextlib import asynccontextmanager
from typing_extensions import AsyncGenerator

from asyncio import Semaphore, TaskGroup

import pydantic_core
import logfire
import asyncpg

from rag.embeddings.embedder import Embedder
from rag.store.base import Section, RAGStore


DB_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS {table} (
    id serial PRIMARY KEY,
    uri text NOT NULL UNIQUE,
    title text NOT NULL,
    content text NOT NULL,
    embedding vector({dimensions}) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_{table}_embeddings ON {table} USING hnsw (embedding vector_l2_ops);
"""

class PgVectorStore(RAGStore):
    def __init__(self, embedder: Embedder, dsn: str, db: str, table: str) -> None:
        super().__init__(embedder)
        self.dsn = dsn
        self.db = db
        self.table = table

    @asynccontextmanager
    async def _connect(self, create_db: bool=False) -> AsyncGenerator[asyncpg.Pool, None]:
        if create_db:
            with logfire.span("check and create database"):
                conn = await asyncpg.connect(f"{self.dsn}/postgres")
                try:
                    db_exists = await conn.fetchval(
                        "SELECT 1 FROM pg_database WHERE datname = $1", self.db
                    )
                    if not db_exists:
                        await conn.execute(f"CREATE DATABASE {self.db}")
                finally:
                    await conn.close()

        pool = await asyncpg.create_pool(f"{self.dsn}/{self.db}")
        try:
            yield pool
        finally:
            await pool.close()

    async def load(self, sections: list[Section]) -> None:
        db_schema = DB_SCHEMA.format(table=self.table, dimensions=self.embedder.dimensions)
        async with self._connect(True) as pool:
            with logfire.span("create schema"):
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(db_schema)

            sem = Semaphore(10)
            async with TaskGroup() as tg:
                for section in sections:
                    tg.create_task(self._insert(
                        sem, pool, section.uri, section.title, section.content,
                        section.embedding_content
                    ))

    async def _insert(self, sem: Semaphore, pool: asyncpg.Pool,
                     uri: str, title: str, content: str, embedding_content: str) -> None:
        async with sem:
            exists = await pool.fetchval(f"SELECT 1 FROM {self.table} WHERE uri = $1", uri)
            if exists:
                logfire.info("skipping {uri=}", uri=uri)
                return

            with logfire.span("create embedding for {uri=}", uri=uri):
                embedding = await self.embedder.create_embedding(embedding_content)

            embedding_json = pydantic_core.to_json(embedding).decode()
            await pool.execute(
                f"INSERT INTO {self.table} (uri, title, content, embedding) VALUES ($1, $2, $3, $4)",
                uri, title, content, embedding_json
            )

    async def retrieve(self, query: str, limit: int) -> str:
        with logfire.span("create embedding for {query=}", query=query):
            embedding = await self.embedder.create_embedding(query)
            embedding_json = pydantic_core.to_json(embedding).decode()

        async with self._connect() as pool:
            rows = await pool.fetch(
                f"SELECT uri, title, content FROM {self.table} ORDER BY embedding <-> $1 LIMIT $2",
                embedding_json, limit
            )
            return "\n\n".join(
                f"# {row['title']}\nURI:{row['uri']}\n\n{row['content']}\n"
                for row in rows
            )
