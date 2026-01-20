from mal.adapter.pydantic_ai import openai_model


deepseek = openai_model("deepseek/deepseek-chat")
deepseek_reasoner = openai_model("deepseek/deepseek-reasoner")

qwen = openai_model("qwen/qwen-plus-latest")
qwen_coder = openai_model("qwen/qwen3-coder-plus")

openrouter_gemini_flash = openai_model("openrouter/google/gemini-3-flash-preview")
openrouter_gemini_pro = openai_model("openrouter/google/gemini-3-pro-preview")

local = openai_model("local")

default = qwen
