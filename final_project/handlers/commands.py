import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from states.walk_state import WalkState, StartState
from states.user_walks import UserWalksState
from .keyboards import WalkKeyboard, MainKeyboard, UserWalksKeyboard, TaskKeyboard
from services.route_generator import RouteGenerator
from services.statistics import get_stats, get_walks_data, set_stats, set_walks_data
from services.task_generator import TaskGenerator


dp = Dispatcher()

text_router = Router()
command_router = Router()


dp.include_router(text_router)
dp.include_router(command_router)

route_generator = RouteGenerator()
task_generator = TaskGenerator()

@command_router.message(CommandStart())
async def start_cmd_hamdler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я твой помощник для прогулок.\nНачни прогулку или посмотри историю прошлых прогулок.",
        reply_markup=MainKeyboard.start_keyboard
        )
    await state.set_state(StartState.main_menu)


@command_router.message(StartState.main_menu)
async def main_menu_choice_handler(message: Message, state: FSMContext):
    """Обработчик гланого меню:
       user начинает прогулку и выбирает длительность или смотрит историю прогулок"""
    if message.text == "Начать прогулку":
        await message.answer(
            "Сколько времени ты готов потратить на прогулку?",
            reply_markup=WalkKeyboard.duration_keyboard
        )
        await state.set_state(WalkState.choosing_duration)
    elif message.text == "Мои прогулки":
        await message.answer(
            "Что хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
        await state.set_state(StartState.user_walks)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )


@command_router.message(WalkState.choosing_duration)
async def route_generation_choice_handler(message: Message, state: FSMContext):
    """Обработчик после выбора длительности прогулки
       user выбирает сгенерировать ли маршрут"""
    if message.text in ["30 минут", "60 минут", "90 минут"]:
        duration = int(message.text.split()[0])
        await state.update_data(duration=duration)
        await message.answer(
            "Какое у тебя сегодня настроение?",
            reply_markup=WalkKeyboard.mood_keyboard
        )
        await state.set_state(WalkState.choosing_mood)
    elif message.text == "Назад":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )

@command_router.message(WalkState.choosing_mood)
async def choosing_mood_handler(message: Message, state: FSMContext):
    """Обработка выбора настроения"""
    data = await state.get_data()
    if message.text in ["Веселое", "Грустное"]:
        await state.update_data(mood=message.text, waiting_custom_mood=False)
        await message.answer(
            "Какую активность хочешь сегодня?",
            reply_markup=WalkKeyboard.activity_keyboard
        )
        await state.set_state(WalkState.choosing_activity)
    elif message.text == "Другое":
        await state.update_data(waiting_custom_mood=True)
        await message.answer(
            "Напиши свое настроение:",
            reply_markup=ReplyKeyboardRemove()
        )
    elif data.get("waiting_custom_mood"):
        await state.update_data(mood=message.text, waiting_custom_mood=False)
        await message.answer(
            "Какую активность хочешь сегодня?",
            reply_markup=WalkKeyboard.activity_keyboard
        )
        await state.set_state(WalkState.choosing_activity)

    elif message.text == "Назад":
        await message.answer(
            "Сколько времени ты готов потратить на прогулку?",
            reply_markup=WalkKeyboard.duration_keyboard
        )
        await state.set_state(WalkState.choosing_duration)
    elif message.text == "В главное меню":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer("Выбери вариант из предложенных")


@command_router.message(WalkState.choosing_activity)
async def choosing_activity_handler(message: Message, state: FSMContext):
    """Обработка выбора активности"""
    data = await state.get_data()
    if message.text in ["Прогулка", "Спорт", "Еда"]:
        await state.update_data(activity=message.text, waiting_custom_mood=False)
        await message.answer(
            "Сколько человек с тобой гуляет?",
            reply_markup=WalkKeyboard.group_size_keyboard
        )
        await state.set_state(WalkState.choosing_group_size)
    elif message.text == "Другое":
        await state.update_data(waiting_custom_activity=True)
        await message.answer(
            "Какую активность хочешь сегодня?",
            reply_markup=ReplyKeyboardRemove()
        )
    elif data.get("waiting_custom_activity"):
        await state.update_data(activity=message.text, waiting_custom_activity=False)
        await message.answer(
            "Сколько человек с тобой гуляет?",
            reply_markup=WalkKeyboard.group_size_keyboard
        )
        await state.set_state(WalkState.choosing_group_size)

    elif message.text == "Назад":
        await message.answer(
            "Какое у тебя сегодня настроение",
            reply_markup=WalkKeyboard.mood_keyboard
        )
        await state.set_state(WalkState.choosing_mood)
    elif message.text == "В главное меню":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer("Выбери вариант из предложенных")

@command_router.message(WalkState.choosing_group_size)
async def choosing_group_size_handler(message: Message, state: FSMContext):
    """Обработка выбора настроения"""
    if message.text in ["1", "2", "3", "4+"]:
        await state.update_data(group_size=message.text)
        await message.answer(
            "Сгенерировать маршрут?",
            reply_markup=WalkKeyboard.route_generation_keyboard
        )
        await state.set_state(WalkState.route_generation)
    elif message.text == "Назад":
        await message.answer(
            "Какую активность хочешь сегодня?",
            reply_markup=WalkKeyboard.activity_keyboard
        )
        await state.set_state(WalkState.choosing_activity)
    elif message.text == "В главное меню":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer("Выбери вариант из предложенных")


@command_router.message(WalkState.route_generation)
async def route_generation_handler(message: Message, state: FSMContext):
    """Обрабочик состояния перед генерацией маршрута:
       user выбирает отправить ли геопозицию для генерации маршрута
       если user выбрал самостоятельную прогулку, то он ее начинает"""
    if message.text == "Сгенерировать маршрут":
        await message.answer(
            "Отправь геопозицию, чтоб я мог сгенерировать тебе маршрут прогулки",
            reply_markup=WalkKeyboard.send_geoposition_keboard
        )
        await state.set_state(WalkState.waiting_geo)
    elif message.text == "Начать прогулку самостоятельно":
        await state.update_data(route="У тебя нет маршрута")
        await run_walk(message, state)
    elif message.text == "Назад":
        await message.answer(
            "Сколько человек с тобой гуляет?",
            reply_markup=WalkKeyboard.group_size_keyboard
        )
        await state.set_state(WalkState.choosing_group_size)
    elif message.text == "В главное меню":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )

@command_router.message(WalkState.waiting_geo)
async def waiting_geo_handler(message: Message, state: FSMContext):
    """Обработчик команд после отправки пользователем геопозиции:
       вызывается функция генерации маршрута, полученный маршрут отправляется пользователю
       user решает, принять ли маршрут"""
    if message.location:
        data = await state.get_data()
        route = await route_generator.generate(
            latitude=message.location.latitude,
            longitude=message.location.longitude,
            duration=data["duration"],
            mood=data["mood"],
            activity=data["activity"]
        )
        points_text = "\n".join(
            [f"{i + 1}. {p['name']} ({p['walk_time_min']} мин): {p['task'] or 'Нет задания'}"
             for i, p in enumerate(route["points"])]
        )

        await state.update_data(route=route)

        await message.answer(
            f"{route['description']}:\n{points_text}\n\nПонравился маршрут?",
            reply_markup=WalkKeyboard.walk_start_keyboard
        )
        await state.set_state(WalkState.route_accessing)
    elif message.text == "Назад":
        await message.answer(
            "Сгенерировать тебе маршрут?",
            reply_markup=WalkKeyboard.route_generation_keyboard
        )
        await state.set_state(WalkState.route_generation)
    elif message.text == "В главное меню":
        await message.answer(
            "Выбери вариант из предложенных",
            reply_markup=MainKeyboard.start_keyboard
        )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )


@command_router.message(WalkState.route_accessing)
async def route_acsessing_handler(message: Message, state: FSMContext):
    """Обработчик команд после генерации и отправки маршрута:
       user выбирает сгенерировать маршрут заново или начать прогулку"""
    if message.text == "Да, начать прогулку":
        await run_walk(message, state)
    elif message.text == "Сгенерировать другой маршрут":
        await message.answer(
            "Отправь геопозицию, чтоб я мог сгенерировать тебе маршрут прогулки",
            reply_markup=WalkKeyboard.send_geoposition_keboard
        )
        await state.set_state(WalkState.waiting_geo)
    elif message.text == "Назад":
        await message.answer(
            "Сгенерировать тебе маршрут?",
            reply_markup=WalkKeyboard.route_generation_keyboard
        )
        await state.set_state(WalkState.route_generation)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )


@command_router.message(StartState.user_walks)
async def statistics_handler(message: Message, state: FSMContext):
    """Обработчик команд для просмотра прошлых прогулок"""
    if message.text == "Статистика":
        stats = await get_stats(message.from_user.id)
        await message.answer(
            f"{stats}\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
    elif message.text == "История маршрутов":
        walks_data =  await get_walks_data(message.from_user.id)
        await message.answer(
            f"{walks_data}\nЧто хочешь посмотреть о своих прогулках?",
            reply_markup=UserWalksKeyboard.user_walks_keyboard
        )
    elif message.text == "Назад":
        await message.answer(
            "Начни прогулку или посмотри историю прошлых прогулок.",
            reply_markup=MainKeyboard.start_keyboard
            )
        await state.set_state(StartState.main_menu)
    else:
        await message.answer(
            "Выбери вариант из предложенных"
        )

@command_router.message(WalkState.in_walk, F.text)
async def in_walk_handler(message: Message, state: FSMContext):
    """Обработчик команд для выполнения заданий во время прогулки"""
    data = await state.get_data()
    task_state = data.get("task_state", "no_task")
    print(f"DEBUG: Получено сообщение: '{message.text}', task_state: '{task_state}'")
    if task_state == "no_task":
        if message.text == "Сгенерировать задание":
            # вот тут надо изменить параметры муд и активити
            current_task = await task_generator.generate(mood=data["mood"], activity=data["activity"], group_size=data["group_size"])
            await state.update_data({
                "task_state": "task_generated",
                "current_task": current_task
            })
            await message.answer(
                f"Твое задание:\n{current_task}\nВыполнишь?",
                reply_markup=TaskKeyboard.task_start_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )
    if task_state == "task_generated":
        if message.text == "Да, принять задание":
            await state.update_data({
                "task_state": "task_in_process"
            })
            await message.answer(
                f"Твое задание:\n{data['current_task']}\nГотов сдать?",
                reply_markup=TaskKeyboard.task_in_process_keyboard
            )
        elif message.text == "Сгенерировать другое задание":
            # вот тут надо изменить параметры муд и активити
            current_task = await task_generator.generate(mood=data["mood"], activity=data["activity"], group_size=data["group_size"])
            await state.update_data({
                "current_task": current_task["description"]
            })
            await message.answer(
                f"Твое задание:\n{current_task}\nВыполнишь?",
                reply_markup=TaskKeyboard.task_start_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )
    if task_state == "task_in_process":
        if message.text == "Cдать задание":
            await state.update_data({
                "task_state": "waiting_proof"
            })
            await message.answer(
                "Отправь фотографию, как подтверждение",
                reply_markup=ReplyKeyboardRemove()
            )
        elif message.text == "Назад":
            await state.update_data({
                "current_task": None,
                "task_state": "no_task"
            })
            await message.answer(
                f"Твое задание отменено",
                reply_markup=TaskKeyboard.task_generation_keyboard
            )
        elif message.text == "Завершить прогулку":
            await finish_walk(message, state)
        else:
            await message.answer(
                "Выбери вариант из предложенных"
            )


@command_router.message(WalkState.in_walk, F.photo)
async def task_photo_proof_handler(message: Message, state: FSMContext):
    """Сохраняет фото-подтверждение выполнения задания"""
    data = await state.get_data()
    if data["task_state"] == "waiting_proof":
        photo_proof = message.photo[-1].file_id
        await state.update_data({
            "walk_state": "in_walk",
            "task_state": "no_task",
            "current_task": None,
            "tasks_count": data.get("tasks_count", 0) + 1,
            "task_photo": photo_proof,
            "duration": data["duration"],
            "route": data["route"]
        })
        await set_walks_data(message.from_user.id)
        await message.answer(
            "Круто, задание выполнено!\nХочешь получить новое?",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )


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
            [f"{i + 1}. {p['name']} ({p.get('walk_time_min', '?')} мин): {p.get('task', 'Нет задания')}"
             for i, p in enumerate(route["points"])]
        )
        route_message = f"{route['description']}:\n{points_text}\nТы можешь получать задания во время прогулки."
    else:
        route_message = f"{route['description']}\nПросто иди гулять 😊"

    await message.answer(
        f"Твоя прогулка длительностью {duration} минут началась.\n{route_message}",
        reply_markup=TaskKeyboard.task_generation_keyboard
    )

    await state.set_state(WalkState.in_walk)
    asyncio.create_task(walk_timer(message, data["duration"], state))
    await set_stats(message.from_user.id)


async def finish_walk(message: Message, state: FSMContext):
    """Дострочное завершение прогулки, тут доделаем нормальную проверку времени прогулки,
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
