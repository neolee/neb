from __future__ import annotations as _annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod

from mal.openai.embedder import Embedder


@dataclass
class Section:
    uri: str
    title: str
    content: str
    embedding_content: str


class RAGStore(ABC):
    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder

    @abstractmethod
    async def load(self, sections: list[Section]) -> None:
        pass

    @abstractmethod
    async def retrieve(self, query: str, limit: int) -> str:
        pass
