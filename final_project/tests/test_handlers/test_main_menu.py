import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock

from handlers.commands import main_menu_choice_handler
from handlers.keyboards import WalkKeyboard, UserWalksKeyboard
from states.walk_state import StartState, WalkState


@pytest.mark.asyncio
async def test_main_menu_start_walk(storage, storage_key):
    message = AsyncMock()
    message.text = "Начать прогулку"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await main_menu_choice_handler(message, state)
    message.answer.assert_called_with(
        "Сколько времени ты готов потратить на прогулку?",
        reply_markup=WalkKeyboard.duration_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_duration


@pytest.mark.asyncio
async def test_main_menu_my_walks(storage, storage_key):
    message = AsyncMock()
    message.text = "Мои прогулки"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await main_menu_choice_handler(message, state)
    message.answer.assert_called_with(
        "Что хочешь посмотреть о своих прогулках?",
        reply_markup=UserWalksKeyboard.user_walks_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.user_walks


@pytest.mark.asyncio
async def test_main_menu_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Мои прогулки", "Начать прогулку"] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(StartState.main_menu)
    await main_menu_choice_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu
