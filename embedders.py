from mal.providers import provider_by_alias
from mal.openai.embedder import Embedder


_local_provider = provider_by_alias("local")
_qwen_provider = provider_by_alias("qwen")

nomic = Embedder(_local_provider, "nomic", 768)
snowflake = Embedder(_local_provider, "snowflake", 1024)
aliyun = Embedder(_qwen_provider, "text-embedding-v3", 1024)


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
