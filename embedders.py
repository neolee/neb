from mal.providers import provider_by_alias
from rag.embeddings.embedder import Embedder


_ollama_provider = provider_by_alias("ollama")
_qwen_provider = provider_by_alias("qwen")

nomic = Embedder(_ollama_provider, "nomic-embed-text", 768)
snowflake = Embedder(_ollama_provider, "snowflake-arctic-embed2", 1024)
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
