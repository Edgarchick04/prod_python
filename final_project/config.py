import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class BotConfig:
    token: str = os.getenv("TOKEN")
    username: str = "@gotouchthegrassbot"
    name: str = "Веселые прогулки"


@dataclass
class GigaChatConfig:
    api_key: str = os.getenv("GIGACHAT_API_KEY")
    model: str = "GigaChat"


bot_config = BotConfig()
gigachat_config = GigaChatConfig()
