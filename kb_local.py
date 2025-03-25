import asyncio
from rag.store.pgvector import PgVectorStore
import embedders


store = PgVectorStore(
    dsn="postgresql://paradigmx@localhost",
    db="zion",
    table="book",
    embedder=embedders.nomic
)

sections = []
asyncio.run(store.load(sections))
