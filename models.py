from mal.adapter.pydantic_ai import openai_model


deepseek = openai_model("deepseek/deepseek-chat")
deepseek_reasoner = openai_model("deepseek/deepseek-reasoner")

qwen = openai_model("qwen/qwen3.5-plus")

gpt = openai_model("openai")

local = openai_model("local")
omlx = openai_model("omlx")

default = qwen
