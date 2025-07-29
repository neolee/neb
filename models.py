import mal.providers as mal
from mal.pydantic_ai.client import model_by_provider, model_by_provider_with_model


deepseek = model_by_provider(mal.deepseek_provider)
deepseek_beta = model_by_provider(mal.deepseek_provider, is_beta=True)
deepseek_reasoner = model_by_provider(mal.deepseek_provider, model_type="reasoner")

qwen = model_by_provider(mal.qwen_provider)
qwen_coder = model_by_provider(mal.qwen_provider, model_type="coder")
qwen_reasoner = model_by_provider(mal.qwen_provider, model_type="reasoner")

openrouter = model_by_provider(mal.openrouter_provider)
openrouter_gemini_flash = model_by_provider_with_model(mal.openrouter_provider, model_name="google/gemini-2.5-flash")
openrouter_gemini_pro = model_by_provider_with_model(mal.openrouter_provider, model_name="google/gemini-2.5-pro")

local = model_by_provider(mal.local_provider)
local_qwen = model_by_provider_with_model(mal.local_provider, model_name="qwen3")

lmstudio = model_by_provider(mal.lmstudio_provider)

ollama = model_by_provider(mal.ollama_provider)

default = qwen
