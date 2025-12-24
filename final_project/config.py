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


@dataclass
class DataBaseConfig:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")


bot_config = BotConfig()
gigachat_config = GigaChatConfig()
db_config = DataBaseConfig()
