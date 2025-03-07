import os
import rtoml


class Provider:
    def __init__(self, config: dict) -> None:
        self.description = config["description"]
        self.api_key = os.environ.get(config["api_key_name"])
        self.base_url = config["base_url"]
        self.beta_base_url = config["beta_base_url"]
        self.chat_model_id = config["chat_model_id"]
        self.coder_model_id = config["coder_model_id"]
        self.reasoner_model_id = config["reasoner_model_id"]


with open("providers.toml", "r") as f:
    data = rtoml.load(f)

providers = []
for p in data["providers"]:
    config = data["providers"][p]
    providers.append(Provider(config))

default_provider_name: str = data["default"]["provider"]
default_provider_config: dict = data["providers"][default_provider_name]
default_provider = Provider(default_provider_config)

default_model_type: str = data["default"]["model_type"]
