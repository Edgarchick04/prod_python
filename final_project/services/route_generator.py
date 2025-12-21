import json
import re
import asyncio
from .gigachat_client import GigaChatClient
from .prompts import build_route_prompt

def calculate_points(duration: int) -> int:
    if duration <= 44:
        return max(1, duration // 10)
    return max(1, duration//15)


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("JSON not found in model response")

    raw_json = match.group()

    raw_json = raw_json.replace("“", '"').replace("”", '"').replace("\n", " ").replace("\r", "")

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as e:
        raw_json = re.sub(r'[\x00-\x1f]+', '', raw_json)
        return json.loads(raw_json)


class RouteGenerator:
    def __init__(self):
        self.client = GigaChatClient()

    def _generate_sync(self, latitude: float, longitude: float, duration: int, mood: str, activity: str) -> dict:
        points = calculate_points(duration)
        prompt = build_route_prompt(latitude, longitude, duration, mood, activity, points)

        raw = self.client.chat(prompt)

        data = extract_json(raw)

        return {
            "description": f"Маршрут на {duration} минут",
            "total_time_min": duration,
            "points": data["points"]
        }

    async def generate(self, latitude: float, longitude: float, duration: int, mood: str, activity: str) -> dict:
        return await asyncio.to_thread(
            self._generate_sync,
            latitude,
            longitude,
            duration,
            mood,
            activity
        )


