import json
import re
import asyncio
import requests
import math
from .gigachat_client import GigaChatClient
from .prompts import build_route_prompt


def calculate_distance(lat1, lon1, lat2, lon2):
    """Вычисляет расстояние в метрах между двумя точками"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return int(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def fetch_nearby_places(lat: float, lon: float, radius: int = 2000) -> str:
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["tourism"](around:{radius},{lat},{lon});
      node["amenity"~"cafe|restaurant|fountain|theatre|place_of_worship"](around:{radius},{lat},{lon});
      way["leisure"~"park|garden|playground"](around:{radius},{lat},{lon});
      node["historic"](around:{radius},{lat},{lon});
      node["natural"="viewpoint"](around:{radius},{lat},{lon});
    );
    out center 20;
    """
    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
        data = response.json()

        places_data = []
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name')
            if not name:
                continue

            p_lat = element.get('lat') or element.get('center', {}).get('lat')
            p_lon = element.get('lon') or element.get('center', {}).get('lon')

            if p_lat and p_lon:
                dist = calculate_distance(lat, lon, p_lat, p_lon)
                places_data.append((name, dist))

        unique_places = {}
        for name, dist in places_data:
            if name not in unique_places or dist < unique_places[name]:
                unique_places[name] = dist

        sorted_places = sorted(unique_places.items(), key=lambda x: x[1])

        result = [f"{name} ({dist}м от тебя)" for name, dist in sorted_places[:15]]

        return ", ".join(result)
    except Exception as e:
        print(f"Overpass error: {e}")
        return "Список мест недоступен"


def calculate_points(duration: int) -> int:
    return max(1, duration // 15)


def extract_json(text: str) -> dict:
    try:
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if not match:
            raise ValueError("JSON not found in model response")

        raw_json = match.group(1)

        raw_json = raw_json.replace("“", '"').replace("”", '"').replace("‘", '"').replace("’", '"')
        raw_json = re.sub(r'[\x00-\x1f]+', ' ', raw_json)

        raw_json = re.sub(r',\s*([\]}])', r'\1', raw_json)

        return json.loads(raw_json)
    except Exception as e:
        print(f"JSON extraction error: {e}")
        return {"points": [{"name": "Интересное место рядом", "walk_time_min": 10, "task": "Наслаждайся видом"}]}


class RouteGenerator:
    def __init__(self):
        self.client = GigaChatClient()

    def _generate_sync(self, latitude: float, longitude: float, duration: int, mood: str, activity: str) -> dict:
        points = calculate_points(duration)
        nearby_places = fetch_nearby_places(latitude, longitude)

        prompt = build_route_prompt(latitude, longitude, duration, mood, activity, points, nearby_places)

        raw = self.client.chat(prompt)
        data = extract_json(raw)

        return {
            "description": f"Маршрут на {duration} минут",
            "total_time_min": duration,
            "points": data.get("points", [])
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