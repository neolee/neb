from openai import AsyncOpenAI
from mal.providers import Provider


class Embedder:
    def __init__(self, provider: Provider, model_id: str, dimensions: int) -> None:
        self.provider = provider
        self.model_id = model_id
        self.dimensions = dimensions

        self.client = AsyncOpenAI(
            base_url=self.provider.base_url,
            api_key=self.provider.api_key
        )

    async def create_embedding(self, s: str):
        embedding = await self.client.embeddings.create(
            input=s,
            model=self.model_id,
            timeout=10.0
        )
        assert len(embedding.data) == 1, (
            f"expected 1 embedding, got {len(embedding.data)}, doc query: {s!r}"
        )
        return embedding.data[0].embedding
