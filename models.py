from mal.adapter.pydantic_ai import openai_model


deepseek = openai_model("deepseek/deepseek-chat")
deepseek_reasoner = openai_model("deepseek/deepseek-reasoner")

qwen = openai_model("qwen/qwen-plus-latest")
qwen_coder = openai_model("qwen/qwen3-coder-plus")

openrouter_gemini_flash = openai_model("openrouter/google/gemini-2.5-flash")
openrouter_gemini_pro = openai_model("openrouter/google/gemini-2.5-pro")

local = openai_model("local")

lmstudio = openai_model("lmstudio")

default = qwen
