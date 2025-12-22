import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.statistics import set_stats

from states.walk_state import StartState, WalkState

from .keyboards import MainKeyboard, TaskKeyboard, WalkKeyboard


async def run_walk(message: Message, state: FSMContext):
    """Задает поведение бота во время прогулки пользователя"""
    data = await state.get_data()
    route = data["route"]
    duration = data.get("duration")

    if not route or isinstance(route, str):
        route = {"description": route or "У тебя нет маршрута", "points": []}

    await state.update_data({
        "walk_state": "in_walk",
        "task_state": "no_task",
        "current_task": None,
        "tasks_count": 0,
        "duration": data["duration"],
        "route": data["route"]
    })

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
    asyncio.create_task(walk_timer(message, data["duration"], state))
    await set_stats(message.from_user.id)


async def finish_walk(message: Message, state: FSMContext):
    """Дострочное завершение прогулки,
       тут доделаем нормальную проверку времени прогулки,
       добавим сохранение статистики и прочее"""
    data = await state.get_data()
    await message.answer(
        f"Твоя прогулка досрочно завершена\n"
        f"Ты выполнил {data.get('tasks_count', 0)} заданий\n"
        f"Что дальше?",
        reply_markup=MainKeyboard.start_keyboard
    )
    await state.clear()
    await state.set_state(StartState.main_menu)


async def walk_timer(message: Message, duration: int, state: FSMContext):
    """Замеряет время и завершает прогулку, в финале поставим duration * 60"""
    await asyncio.sleep(duration)
    current_state = await state.get_state()
    data = await state.get_data()
    if current_state == WalkState.in_walk.state:
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
