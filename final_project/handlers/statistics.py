from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.statistics import get_stats, get_walks_data

from states.walk_state import StartState

from .keyboards import MainKeyboard, UserWalksKeyboard


command_router = Router()


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
        walks_data = await get_walks_data(message.from_user.id)
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
