from config import gigachat_config

from gigachat import GigaChat


class GigaChatClient:
    def __init__(self):
        self.client = GigaChat(
            credentials=gigachat_config.api_key,
            model=gigachat_config.model,
            verify_ssl_certs=False
        )

    def chat(self, prompt: str) -> str:
        response = self.client.chat(prompt)
        return response.choices[0].message.content
