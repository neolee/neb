from mal.adapter.pydantic_ai import openai_model


deepseek_flash = openai_model("deepseek/deepseek-v4-flash")
deepseek_pro = openai_model("deepseek/deepseek-v4-pro")

qwen = openai_model("qwen/qwen3.5-plus")

gpt = openai_model("openai")

local = openai_model("local")
omlx = openai_model("omlx")

default = qwen
