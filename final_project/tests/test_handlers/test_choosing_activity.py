import pytest
import random
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from unittest.mock import AsyncMock

from handlers.walk_prep import choosing_activity_handler
from handlers.keyboards import WalkKeyboard, MainKeyboard
from states.walk_state import StartState, WalkState


@pytest.mark.asyncio
async def test_choosing_activity_common(storage, storage_key):
    message = AsyncMock()
    message.text = random.choice(["Прогулка", "Спорт", "Еда"])
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Сколько человек с тобой гуляет?",
        reply_markup=WalkKeyboard.group_size_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_group_size
    data = await state.get_data()
    assert data.get("activity") == message.text
    assert data.get("waiting_custom_activity") == False


@pytest.mark.asyncio
async def test_choosing_activity_other(storage, storage_key):
    message = AsyncMock()
    message.text = "Другое"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.choosing_activity)
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Какую активность хочешь сегодня?",
        reply_markup=ReplyKeyboardRemove()
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_activity
    data = await state.get_data()
    assert data.get("waiting_custom_activity") == True


@pytest.mark.asyncio
async def test_choosing_activity_sent_own(storage, storage_key):
    message = AsyncMock()
    message.text = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(waiting_custom_activity=True, activity=message.text)
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Сколько человек с тобой гуляет?",
        reply_markup=WalkKeyboard.group_size_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_group_size


@pytest.mark.asyncio
async def test_choosing_activity_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Какое у тебя сегодня настроение",
        reply_markup=WalkKeyboard.mood_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_mood


@pytest.mark.asyncio
async def test_choosing_activity_go_main_menu(storage, storage_key):
    message = AsyncMock()
    message.text = "В главное меню"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_choosing_activity_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in [
        "Прогулка", "Спорт", "Еда",
        "В главное меню", "Назад"
    ] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_activity_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
