import asyncio
from .gigachat_client import GigaChatClient
from .prompts import build_task_prompt

class TaskGenerator:
    def __init__(self):
        self.client = GigaChatClient()

    def _generate_sync(self, mood: str, activity: str, group_size: str) -> str:
        prompt = build_task_prompt(mood, activity, group_size)
        return self.client.chat(prompt).strip()

    async def generate(self, mood: str, activity: str, group_size: str) -> str:
        return await asyncio.to_thread(
            self._generate_sync,
            mood,
            activity,
            group_size,
        )
