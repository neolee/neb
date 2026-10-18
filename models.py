from mal.adapter.pydantic_ai import openai_model


deepseek = openai_model("deepseek")

gpt = openai_model("openai")

local = openai_model("local")
omlx = openai_model("omlx")

default = deepseek
