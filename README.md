# Nebuchadnezzar

A project to seek the real power of AI agents. Powered by `pydantic-ai` and `logfire`.

## LLM Abstraction Layer (MAL)

**MAL**(*Large Language Model Abstraction Layer*) is a framework to simplify configuration and adaptation of applications using different language model services. It consists of a service provider configuration framework and adaptation layer(s) for popular agent frameworks.

NOTE: Currently **MAL** only supports OpenAI compatible API service providers.

### Service Provider Configuration

> `providers.toml` `mal/providers.py`

- `providers.toml`: contains multiple provider configurations that you can access by name and alias, and other extensible attributes.
- `providers.py`: Python wrapper for the configuration file, providing easy access to the provider configurations and other settings. 

To use this framework, just add your OpenAI-compatible service provider as a configuration group as below:

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

You can define aliases in the `[aliases]` group, or change system default settings in the `[defaults]` group. Then you can import `mal.providers` and use the following functions and/or variables for `Provider` object(s) for your provider(s):

> `provider_by_name` `provider_by_alias` `providers` `default_provider`

Most configuration items are self explained, a few more notes:
- The group name without the `providers` prefix is the provider's `name` (`deepseek` in the sample above). You can use it in the `provider_by_name` function to get the corresponding `Provider` object.
- For security concerns real API keys should not be stored in the configuration file. The keys should be stored as environment variables and referenced by name in the configuration file (the `api_key_name` field). The real key will be in the `Provider` objects when you get them by calling the framework.
- Fields `beta_base_url` and any `model_id` other than `chat_model_id` are optional. Use them only when your provider matches related features.

### Model Adapter for PydanticAI

> `mal/pydantic_ai/model.py`

The [PydanticAI framework](https://ai.pydantic.dev/) (`pydantic_ai`) uses `base_url` and `api_key` to build a `OpenAIProvider` object, then use this `OpenAIProvider` object and `model_name` to build a `OpenAIModel` object, which is needed in *agent* construction (using `model=` parameter). 

As bridge between **MAL** and `pydantic_ai`, `mal.pydantic_ai.model` does all the work for you. Just import `mal.pydantic_ai.model` and use the following functions:

> `model_by_provider` `model_by_alias` `ollama_model`

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

Simple wrappers for OpenAI RESTful API. Just for *separation of concerns*.

Currently only the `OpenAI` client is supported, the asynchronous `AsyncOpenAI` API is work in progress. 

## Agents

### PydanticAI Samples

Most of PydanticAI samples are built for OpenAI models. They've been migrated to use **MAL** here, which makes them provider independent. So you can try them on almost any LLM, as long as it provides OpenAI compatible API. 

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
- The `logfire` integration is completely optional (but very amazing indeed). If you wish to omit this integration just remove *import* of `instrument` module and call of `instrument.init()` and, in a few samples (`rag.py` `weather.py`), anything of `logfire` reference.
- Several samples (`bank_support.py` `rag.py` `sql_gen.py`) need database connection. I use my local `postgresql` server and `asyncpg` lib to access it asynchronously (in agent). You can change the connection parameters (or server DSN) and database name to match your environment.

Check the *sample list* section below for more details on all samples.

#### Sample List
- `hello.py`: just the *hello world* in agent world
- `stream_hello.py`: an asynchronous version of *hello world* 
- `roulette_wheel.py`: a roulette wheel simulator demonstrating *tool calling* and *context* mechanism
- `pydantic_model.py`: `pydantic` data validation integrated in *agents*
- `stream_markdown.py`: using `rich` to display streamed Markdown output from *agent*
- `stream_whales.py`: using `rich` to display streamed `pydantic` object output from *agent*
- `weather.py`: multiple *tools calling* 3rd party RESTful API in *agent*
- `bank_support.py` `bank_db.py`: a customer supporting *agent* demonstrating RDBMS/MIS integration
- `sql_gen.py`: a logging analyzer demonstrating RDBMS integration
- `rag.py`: basic RAG build/retrieve/query process using local embedding model and `pgvector`
- `chat_app.*`: a simple chat app with FastAPI, chat history stored in a SQLite DB 
- `question_graph.py`: ask and evaluate agents with generated mermaid graph

### Reusable Agents

*TBD*
