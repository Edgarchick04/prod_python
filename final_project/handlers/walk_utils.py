import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.statistics import finish_walk as finish_walk_db
from services.statistics import start_walk

from states.walk_state import StartState, WalkState

from .keyboards import MainKeyboard, TaskKeyboard, WalkKeyboard


active_timers = {}


async def run_walk(message: Message, state: FSMContext):
    """Задает поведение бота во время прогулки пользователя"""
    data = await state.get_data()
    route = data["route"]
    duration = data.get("duration", 0)

    if not route or isinstance(route, str):
        route = {"description": route or "У тебя нет маршрута", "points": []}

    await state.update_data({
        "walk_state": "in_walk",
        "task_state": "no_task",
        "current_task": None,
        "tasks_count": 0,
    })

    walk_id = await start_walk(
        user_id=message.from_user.id,
        route=route,
        duration=duration
    )

    await state.update_data(walk_id=walk_id)

    if route["points"]:
        points_text = "\n".join(
            [f"{i + 1}. {p['name']} ({p.get('walk_time_min', '?')} мин): "
             f"{p.get('task', 'Нет задания')}"
             for i, p in enumerate(route["points"])]
        )
        route_message = (f"{route['description']}:\n{points_text}\n"
                         f"Ты можешь получать задания во время прогулки.")
    else:
        route_message = f"{route['description']}\nПросто иди гулять 😊"

    await message.answer(
        f"Твоя прогулка длительностью "
        f"{duration} минут началась.\n{route_message}",
        reply_markup=TaskKeyboard.task_generation_keyboard
    )

    await state.set_state(WalkState.in_walk)

    user_id = message.from_user.id
    timer_task = asyncio.create_task(walk_timer(message, duration, state))
    active_timers[user_id] = timer_task


async def finish_walk(message: Message, state: FSMContext):
    """Дострочное завершение прогулки,
       тут доделаем нормальную проверку времени прогулки,
       добавим сохранение статистики и прочее"""
    user_id = message.from_user.id

    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]

    data = await state.get_data()
    walk_id = data.get("walk_id")

    real_dur = 0

    if walk_id:
        real_dur = await finish_walk_db(walk_id)

    await message.answer(
        f"Прогулка завершена \n"
        f"⏱ Длительность: {real_dur} мин \n"
        f"Выполнено заданий: {data.get('tasks_count', 0)}",
        reply_markup=MainKeyboard.start_keyboard
    )

    await state.clear()
    await state.set_state(StartState.main_menu)


async def walk_timer(message: Message, duration: int, state: FSMContext):
    """Замеряет время и завершает прогулку, в финале поставим duration * 60"""
    try:
        await asyncio.sleep(duration)
        current_state = await state.get_state()
        data = await state.get_data()
        if current_state == WalkState.in_walk:
            data = await state.get_data()
            walk_id = data.get("walk_id")

            if walk_id:
                await finish_walk_db(walk_id)

            await message.answer(
                f"<b>Время вышло!</b>\n"
                f"Твоя прогулка длительностью {duration} минут завершена."
                f"Ты выполнил {data.get('tasks_count', 0)} заданий\n",
                reply_markup=WalkKeyboard.walk_end_keyboard,
            )
            await state.clear()
            await message.answer(
                "Что дальше?",
                reply_markup=MainKeyboard.start_keyboard
            )
            await state.set_state(StartState.main_menu)
    except asyncio.CancelledError:
        pass
    finally:
        user_id = message.from_user.id
        if active_timers.get(user_id) == asyncio.current_task():
            active_timers.pop(user_id, None)
