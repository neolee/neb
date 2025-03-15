# Nebuchadnezzar

A project aimed at exploring the true potential of AI agents. It is powered by `MAL` and `pydantic-ai`.

## LLM Abstraction Layer (MAL)

MAL (Language Model Abstraction Layer) is a framework designed to streamline the configuration and integration of applications across various language model services. It includes a service provider configuration framework and adaptation layers tailored for popular agent frameworks.

Note: At present, MAL supports only OpenAI-compatible API service providers.

### Service Provider Configuration

> `providers.toml` `mal/providers.py`

- `providers.toml`: Contains multiple provider configurations that you can access by name or alias, along with other extensible attributes.
- `providers.py`: A Python wrapper for the configuration file, offering easy access to provider settings and additional options.

To use this framework, simply add your OpenAI-compatible service provider as a configuration group as shown below:

``` toml
[providers.deepseek]
description = "DeepSeek Official"
api_key_name = "DEEPSEEK_API_KEY"
base_url = "https://api.deepseek.com"
beta_base_url = "https://api.deepseek.com/beta"
chat_model_id = "deepseek-chat"
coder_model_id = "deepseek-chat"
reasoner_model_id = "deepseek-reasoner"
```

You can define aliases within the `[aliases]` section or modify system default settings in the `[defaults]` section. Afterward, you can import `mal.providers` and utilize the following functions and variables for managing `Provider` objects:

- `provider_by_name`
- `provider_by_alias`
- `providers`
- `default_provider`

Most configuration options are self-explanatory; however, a few additional notes are worth mentioning:
- The group name without the `providers` prefix represents the provider's name (e.g., `deepseek`). You can use this name in the `provider_by_name` function to retrieve the corresponding `Provider` object.
- For security reasons, avoid storing real API keys directly in the configuration file. Instead, store these keys as environment variables and reference them by their names within the configuration file using the `api_key_name` field. The actual key will be accessible through the `Provider` objects when you retrieve them via the framework.
- Fields like `beta_base_url` and any `model_id` other than `chat_model_id` are optional. Use these fields only if your provider supports the corresponding features.

### Model Adapter for PydanticAI

> `mal/pydantic_ai/model.py`

The [PydanticAI framework](https://ai.pydantic.dev/) (`pydantic_ai`) constructs an `OpenAIProvider` object using the parameters `base_url` and `api_key`. This `OpenAIProvider` is then utilized along with `model_name` to create an `OpenAIModel` object, which is essential for constructing agents (via the `model=` parameter).

As a bridge between **MAL** and `pydantic_ai`, the module `mal.pydantic_ai.model` handles all the necessary tasks. Simply import this module and use the following functions:

- `model_by_provider`
- `model_by_alias`
- `ollama_model`

...or any pre-defined model objects such as:

``` python
deepseek = model_by_alias("deepseek")
qwen = model_by_alias("qwen")
ollama = model_by_alias("ollama")
ollama_coder = model_by_alias("ollama", model_type="coder")
ollama_phi4 = ollama_model("phi-4")

default = qwen
```

``` python
from pydantic_ai import Agent
import mal.pydantic_ai.model as model

hello_agent = Agent(
    model=model.default,
    system_prompt="Be concise, reply with one sentence.",
)
```

### Model Adapter for OpenAI

> `mal/openai/model.py`

Simplified interfaces for interacting with the OpenAI RESTful API, designed primarily to achieve separation of concerns.

At present, support is limited to the `OpenAI` client, while the development of the asynchronous `AsyncOpenAI` API is still ongoing.

## Agents

### PydanticAI Samples

The majority of PydanticAI examples are designed for OpenAI models but have been updated to utilize **MAL**, making them agnostic to the specific model provider. This allows you to use these samples across nearly any large language model that supports an OpenAI-compatible API.

#### Dependencies

``` toml
dependencies = [
    "asyncpg>=0.30.0",
    "devtools>=0.12.2",
    "httpx[socks]>=0.28.1",
    "logfire[asyncpg]>=3.7.1",
    "pydantic-ai[logfire]>=0.0.35",
    "rtoml>=0.12.0",
]
```

Additional technical details:

- The `logfire` integration is entirely optional, though highly recommended. To exclude this integration, simply remove the import of the `instrument` module and the call to `instrument.init()`. Additionally, in a few sample files (`rag.py`, `weather.py`), you should also eliminate any references to `logfire`.
- Several samples (`bank_support.py`, `rag.py`, `sql_gen.py`) require a database connection. I utilize my local `postgresql` server and the `asyncpg` library for asynchronous access (in the agent). You can adjust the connection parameters or data source name (DSN) and database name to suit your environment.

For more information on each sample, refer to the *sample list* section below.

#### Sample List
- `hello.py`: A basic "Hello World" example for agents.
- `stream_hello.py`: An asynchronous version of the classic "Hello World."
- `roulette_wheel.py`: A roulette wheel simulator that demonstrates tool calling and context management within agents.
- `pydantic_model.py`: Integrates Pydantic data validation into agent functionalities.
- `stream_markdown.py`: Uses `rich` to display streamed Markdown output from an agent.
- `stream_whales.py`: Utilizes `rich` to stream and display Pydantic objects generated by an agent.
- `weather.py`: An agent that calls multiple third-party RESTful APIs for weather information.
- `bank_support.py` and `bank_db.py`: A customer support agent demonstrating integration with RDBMS/MIS systems.
- `sql_gen.py`: Demonstrates RDBMS integration through a logging analyzer tool.
- `rag.py`: Implements a basic Retrieval-Augmented Generation (RAG) process using a local embedding model and `pgvector`.
- `chat_app.*`: A simple chat application built with FastAPI, storing chat history in a SQLite database.
- `question_graph.py`: Allows asking and evaluating agents through the generation of Mermaid graphs.

### Reusable Agents

*TBD*
