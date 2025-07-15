from mal.providers import local_provider, qwen_provider
from mal.openai.embedder import Embedder


nomic = Embedder(local_provider, "nomic", 768)
snowflake = Embedder(local_provider, "snowflake", 1024)
aliyun = Embedder(qwen_provider, "text-embedding-v3", 1024)


if __name__ == "__main__":
    import asyncio

    async def test_embedder(s: str, embedder: Embedder):
        embedding = await embedder.create_embedding(s)
        print(f"Embeddings: {embedding[:5]}")
        print(f"Dimensions: {len(embedding)}")

    s = "The quick brown fox jumps over the lazy dog."
    asyncio.run(test_embedder(s, nomic))
    asyncio.run(test_embedder(s, snowflake))
    asyncio.run(test_embedder(s, aliyun))
