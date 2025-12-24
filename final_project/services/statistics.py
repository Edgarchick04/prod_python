import json
from datetime import datetime

from services.db import Photo, Walk, async_session

from sqlalchemy import func, select, update


async def start_walk(user_id: int, route: dict, duration: int) -> int:
    async with async_session() as session:
        new_walk = Walk(
            user_id=user_id,
            date=datetime.now().isoformat(),
            duration=duration,
            tasks_count=0,
            route=json.dumps(route, ensure_ascii=False)
        )
        session.add(new_walk)
        await session.commit()
        await session.refresh(new_walk)
        return new_walk.id


async def add_task_photo(walk_id: int, file_id: str):
    async with async_session() as session:
        new_photo = Photo(walk_id=walk_id, file_id=file_id)
        session.add(new_photo)

        stmt = update(Walk).where(Walk.id == walk_id).values(
            tasks_count=Walk.tasks_count + 1
        )
        await session.execute(stmt)
        await session.commit()


async def finish_walk(walk_id: int):
    async with async_session() as session:
        result = await session.execute(select(Walk).where(Walk.id == walk_id))
        walk = result.scalar_one_or_none()

        if walk:
            start_time = datetime.fromisoformat(walk.date)
            end_time = datetime.now()
            duration_delta = end_time - start_time
            actual_minutes = max(1, int(duration_delta.total_seconds() // 60))

            walk.duration = actual_minutes
            await session.commit()
            return actual_minutes
    return 0


async def get_stats(user_id: int) -> str:
    async with async_session() as session:
        stmt = select(
            func.count(Walk.id),
            func.sum(Walk.duration),
            func.sum(Walk.tasks_count)
        ).where(Walk.user_id == user_id)

        result = await session.execute(stmt)
        walks, total_time, total_tasks = result.fetchone()

    return (
        f"📊 Твоя статистика:\n"
        f"🚶 Прогулок: {walks or 0}\n"
        f"⏱ Времени: {total_time or 0} минут\n"
        f"✅ Заданий выполнено: {total_tasks or 0}"
    )


async def get_walks_data(user_id: int) -> str:
    async with async_session() as session:
        stmt = select(
            Walk
        ).where(
            Walk.user_id == user_id
        ).order_by(
            Walk.date.desc()
        ).limit(20)
        result = await session.execute(stmt)
        rows = result.scalars().all()

    if not rows:
        return "У тебя пока нет прогулок"

    walks_list = list(reversed(rows))
    text = "🗺 История маршрутов:\n\n"

    for i, walk in enumerate(walks_list, 1):
        text += (
            f"{i}. 📅 {walk.date[:10]}\n"
            f"   ⏱ {walk.duration} минут\n"
            f"   ✅ {walk.tasks_count} заданий\n"
        )

        if not walk.route:
            text += "   🚶 Прогулка без маршрута\n\n"
            continue

        try:
            route = json.loads(walk.route)
            points = route.get("points", [])
            if not points:
                text += "   🚶 Прогулка без точек\n\n"
                continue

            text += "   📍 Точки маршрута:\n"
            for idx, point in enumerate(points, 1):
                task = point.get("task")
                text += f"      {idx}. {point.get('name', 'Без названия')}"
                if task:
                    text += f" — задание: {task}"
                text += "\n"
            text += "\n"
        except Exception:
            text += "   ⚠️ Не удалось загрузить маршрут\n\n"

    return text


async def get_walk_photos(walk_id: int) -> list[str]:
    async with async_session() as session:
        stmt = select(Photo.file_id).where(Photo.walk_id == walk_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def get_walks_short(user_id: int) -> dict:
    async with async_session() as session:
        stmt = select(
            Walk.id, Walk.date
        ).where(
            Walk.user_id == user_id
        ).order_by(
            Walk.date.desc()
        ).limit(20)
        result = await session.execute(stmt)
        rows = result.all()

    rows = list(reversed(rows))
    return {i + 1: row.id for i, row in enumerate(rows)}
