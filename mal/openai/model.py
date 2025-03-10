from typing import Iterable
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionChunk

from mal.providers import Provider, default_provider, default_model_type


def client_by_provider(provider: Provider=default_provider, is_beta=False) -> OpenAI:
    base_url = provider.beta_base_url if is_beta else provider.base_url
    return OpenAI(base_url=base_url, api_key=provider.api_key)


def model_name_by_type(provider=default_provider, model_type=default_model_type) -> str:
    return provider.model_id_from_type(model_type)


def append_message(messages: list, role: str, message: str):
    messages.append({"role": role, "content": message})


def create_chat_completion(
        client: OpenAI,
        model_name: str,
        messages: Iterable[ChatCompletionMessageParam],
        temperature=0.6,
        stream=False,
        **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        stream=stream,
        **kwargs
    )
    return response


def chat_completion_message(completion):
    return completion.choices[0].message


def chat_completion_content(completion):
    return completion.choices[0].message.content


def chat_completion_chunk_content(chunk):
    return chunk.choices[0].delta.content


def chat_completion_reasoning_content(completion):
    return completion.choices[0].message.reasoning_content


def chat_completion_chunk_reasoning_content(chunk):
    return chunk.choices[0].delta.reasoning_content


def chat_completion_json(completion):
    return completion.choices[0].message.model_dump_json()


def chat_completion_tool_calls(completion):
    return completion.choices[0].message.tool_calls


def create_completion(
        client: OpenAI,
        model_name: str,
        **kwargs):
    response = client.completions.create(
        model=model_name,
        **kwargs
    )
    return response


def completion_text(completion):
    return completion.choices[0].text
