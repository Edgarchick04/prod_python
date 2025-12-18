from typing import Any, Dict

async def route_generator(latitude: float, longtitude: float, duration: int) -> Dict[str, Any]:
    """потом докрутим с запросами к ИИ и наверное переделаем в class"""
    return {
        "description": "Твой маршрут готов:\n Иди домой и поспи",
        "distance_m": 1234,
        "duration_minutes": duration
    }
