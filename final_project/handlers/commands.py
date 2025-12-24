from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.walk_state import StartState, WalkState

from .keyboards import MainKeyboard, UserWalksKeyboard, WalkKeyboard


command_router = Router()


@command_router.message(CommandStart())
async def start_cmd_handler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я твой помощник для прогулок.\nНачни"
        " прогулку или посмотри историю прошлых прогулок.",
        reply_markup=MainKeyboard.start_keyboard
        )
    await state.set_state(StartState.main_menu)


@command_router.message(StartState.main_menu)
async def main_menu_choice_handler(message: Message, state: FSMContext):
    """Обработчик гланого меню:
       user начинает прогулку и выбирает длительность
       или смотрит историю прогулок"""
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
