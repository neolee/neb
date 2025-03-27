from __future__ import annotations as _annotations

import chromadb
import logfire

from rag.embeddings.embedder import Embedder
from rag.store.base import Section, RAGStore


class ChromaStore(RAGStore):
    def __init__(self, embedder: Embedder, name: str="documents", path: str="./chromadb") -> None:
        super().__init__(embedder)
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    async def load(self, sections: list[Section]) -> None:
        with logfire.span("creating embeddings"):
            embeddings = [
                await self.embedder.create_embedding(section.embedding_content)
                for section in sections
            ]
        metadatas = [
            {
                "uri": section.uri,
                "title": section.title,
                "content": section.content
            }
            for section in sections
        ]
        self.collection.add(
            ids=[section.uri for section in sections],
            embeddings=embeddings, # type: ignore
            metadatas=metadatas, # type: ignore
            documents=[section.content for section in sections]
        )

    async def retrieve(self, query: str, limit: int) -> str:
        with logfire.span("create embedding for {query=}", query=query):
            query_embedding = await self.embedder.create_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["metadatas", "documents"] # type: ignore
        )

        return "\n\n".join(
            f"# {meta['title']}\nURI:{meta['uri']}\n\n{doc}\n"
            for meta, doc in zip(results["metadatas"][0], results["documents"][0]) # type: ignore
        )
