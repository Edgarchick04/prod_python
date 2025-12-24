from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from services.route_generator import RouteGenerator

from states.walk_state import StartState, WalkState

from .keyboards import MainKeyboard, WalkKeyboard
from .walk_utils import run_walk


command_router = Router()
route_generator = RouteGenerator()


@command_router.message(WalkState.choosing_duration)
async def route_generation_choice_handler(message: Message, state: FSMContext):
    """Обработчик после выбора длительности прогулки
       user выбирает сгенерировать ли маршрут"""
    data = await state.get_data()
    if message.text in ["30 минут", "60 минут", "90 минут"]:
        duration = int(message.text.split()[0])
        await state.update_data(duration=duration, waiting_custom_duration=False)
        await message.answer(
            "Какое у тебя сегодня настроение?",
            reply_markup=WalkKeyboard.mood_keyboard
        )
        await state.set_state(WalkState.choosing_mood)
    elif message.text == "Другое":
        await state.update_data(waiting_custom_duration=True)
        await message.answer(
            "Введи желаемую длительность прогулки в минутах (только число):",
            reply_markup=ReplyKeyboardRemove()
        )
    elif data.get("waiting_custom_duration"):
        await state.update_data(duration=int(message.text), waiting_custom_duration=False)
        await message.answer(
            "Какое у тебя настроение?",
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
            "Какое у тебя настроение?",
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
            "Введи желаемую длительность прогулки в минутах (только число):",
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
        await state.update_data(
            activity=message.text,
            waiting_custom_activity=False
        )
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
        await state.update_data(
            activity=message.text,
            waiting_custom_activity=False
        )
        await message.answer(
            "Сколько человек с тобой гуляет?",
            reply_markup=WalkKeyboard.group_size_keyboard
        )
        await state.set_state(WalkState.choosing_group_size)

    elif message.text == "Назад":
        await message.answer(
            "Какое у тебя настроение?",
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
    """Обработка выбора количества человек"""
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
            "Отправь геопозицию, чтоб я мог "
            "сгенерировать тебе маршрут прогулки",
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
       вызывается функция генерации маршрута,
       полученный маршрут отправляется пользователю
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
            [f"{i + 1}. {p['name']} ({p['walk_time_min']} мин): "
             f"{p['task'] or 'Нет задания'}"
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
async def route_accessing_handler(message: Message, state: FSMContext):
    """Обработчик команд после генерации и отправки маршрута:
       user выбирает сгенерировать маршрут заново или начать прогулку"""
    if message.text == "Да, начать прогулку":
        await run_walk(message, state)
    elif message.text == "Сгенерировать другой маршрут":
        await message.answer(
            "Отправь геопозицию, чтоб я мог "
            "сгенерировать тебе маршрут прогулки",
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
