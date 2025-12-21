import os
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
GIGACHAT_MODEL = "GigaChat"

class GigaChatClient:
    def __init__(self):
        self.client = GigaChat(
            credentials=GIGACHAT_API_KEY,
            model=GIGACHAT_MODEL,
            verify_ssl_certs=False
        )

    def chat(self, prompt: str) -> str:
        response = self.client.chat(prompt)
        return response.choices[0].message.content

