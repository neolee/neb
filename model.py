from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from providers import Provider, default_model_type, provider_by_alias


def openai_provider(provider: Provider, is_beta=False) -> OpenAIProvider:
    base_url = provider.beta_base_url if is_beta else provider.base_url
    return OpenAIProvider(base_url=base_url, api_key=provider.api_key)


def model_by_provider(provider: Provider, is_beta=False, model_type=default_model_type) -> OpenAIModel:
    op = openai_provider(provider, is_beta)
    model_name = provider.model_id_from_type(model_type)
    return OpenAIModel(model_name, provider=op)


def model_by_alias(alias: str, is_beta=False, model_type=default_model_type) -> OpenAIModel:
    provider = provider_by_alias(alias)
    return model_by_provider(provider, is_beta, model_type)


def ollama_model(model_name: str) -> OpenAIModel:
    p = provider_by_alias("ollama")
    op = openai_provider(p)
    return OpenAIModel(model_name, provider=op)


deepseek = model_by_alias("deepseek")
deepseek_beta = model_by_alias("deepseek", is_beta=True)
deepseek_reasoner = model_by_alias("deepseek", model_type="reasoner")

qwen = model_by_alias("qwen")
qwen_coder = model_by_alias("qwen", model_type="coder")
qwen_reasoner = model_by_alias("qwen", model_type="reasoner")

lmstudio = model_by_alias("lmstudio")

ollama = model_by_alias("ollama")
ollama_coder = model_by_alias("ollama", model_type="coder")

default = qwen
