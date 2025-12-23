import pytest
import random
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from unittest.mock import AsyncMock

from handlers.walk_prep import choosing_group_size_handler
from handlers.keyboards import WalkKeyboard, MainKeyboard
from states.walk_state import StartState, WalkState


@pytest.mark.asyncio
async def test_choosing_group_size_common(storage, storage_key):
    message = AsyncMock()
    message.text = random.choice(["1", "2", "3", "4+"])
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_group_size_handler(message, state)
    message.answer.assert_called_with(
        "Сгенерировать маршрут?",
        reply_markup=WalkKeyboard.route_generation_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.route_generation
    data = await state.get_data()
    assert data.get("group_size") == message.text


@pytest.mark.asyncio
async def test_choosing_group_size_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_group_size_handler(message, state)
    message.answer.assert_called_with(
        "Какую активность хочешь сегодня?",
        reply_markup=WalkKeyboard.activity_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_activity


@pytest.mark.asyncio
async def test_choosing_group_size_go_main_menu(storage, storage_key):
    message = AsyncMock()
    message.text = "В главное меню"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_group_size_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_choosing_group_size_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in [
        "1", "2", "3", "4+",
        "В главное меню", "Назад"
    ] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_group_size_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
