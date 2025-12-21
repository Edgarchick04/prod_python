import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from states.walk_state import WalkState, StartState
from states.user_walks import UserWalksState
from handlers.keyboards import WalkKeyboard, MainKeyboard, UserWalksKeyboard, TaskKeyboard
from services.route_generator import route_generator
from services.statistics import get_stats, get_walks_data, set_stats, set_walks_data
from services.task_generator import task_generator


dp = Dispatcher()

text_router = Router()
command_router = Router()


dp.include_router(text_router)
dp.include_router(command_router)


@command_router.message(CommandStart())
async def start_cmd_handler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я твой помощник для прогулок.\nНачни прогулку или посмотри историю прошлых прогулок.",
        reply_markup=MainKeyboard.start_keyboard
        )
    await state.set_state(StartState.main_menu)


@command_router.message(StartState.main_menu)
async def main_menu_choise_handler(message: Message, state: FSMContext):
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
async def route_generation_choise_handler(message: Message, state: FSMContext):
    """Обработчик после выбора длительности прогулки
       user выбирает сгенерировать ли маршрут"""
    if message.text in ["30 минут", "60 минут", "90 минут"]:
        duration = int(message.text.split()[0])
        await state.update_data(duration=duration)
        await message.answer(
            "Сгенерировать тебе маршрут?",
            reply_markup=WalkKeyboard.route_generation_keyboard
        )
        await state.set_state(WalkState.route_generation)
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
            "Сколько времени ты готов потратить на прогулку?",
            reply_markup=WalkKeyboard.duration_keyboard
        )
        await state.set_state(WalkState.choosing_duration)
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
        route = await route_generator(
            message.location.latitude,
            message.location.longitude,
            duration=data["duration"]
        )
        await state.update_data(route=route)
        await message.answer(
            f"{route['description']}\nПонравился маршрут?",
            reply_markup=WalkKeyboard.walk_start_keyboard
        )
        await state.set_state(WalkState.route_accessing)
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


@command_router.message(WalkState.route_accessing)
async def route_accessing_handler(message: Message, state: FSMContext):
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
    if task_state == "no_task":
        if message.text == "Сгенерировать задание":
            current_task = await task_generator()
            await state.update_data({
                "task_state": "task_generated",
                "current_task": current_task["description"]
            })
            await message.answer(
                f"Твое задание:\n{current_task['description']}\nВыполнишь?",
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
            current_task = await task_generator()
            await state.update_data({
                "current_task": current_task["description"]
            })
            await message.answer(
                f"Твое задание:\n{current_task['description']}\nВыполнишь?",
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
                "Твое задание отменено",
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
    await state.update_data({
        "walk_state": "in_walk",
        "task_state": "no_task",
        "current_task": None,
        "tasks_count": 0,
        "duration": data["duration"],
        "route": data["route"]
    })
    await message.answer(
        f"Твоя прогулка длительностью {data['duration']} минут началась.\n"
        f"{data['route']}\nТы можешь получать задания во время прогулки.",
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
