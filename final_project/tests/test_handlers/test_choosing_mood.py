import pytest
import random
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from unittest.mock import AsyncMock

from handlers.walk_prep import choosing_mood_handler
from handlers.keyboards import WalkKeyboard, MainKeyboard
from states.walk_state import StartState, WalkState


@pytest.mark.asyncio
async def test_choosing_mood_common(storage, storage_key):
    message = AsyncMock()
    message.text = random.choice(["Веселое", "Грустное"])
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Какую активность хочешь сегодня?",
        reply_markup=WalkKeyboard.activity_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_activity
    data = await state.get_data()
    assert data.get("mood") == message.text
    assert data.get("waiting_custom_mood") == False


@pytest.mark.asyncio
async def test_choosing_mood_other(storage, storage_key):
    message = AsyncMock()
    message.text = "Другое"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.choosing_mood)
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Какое у тебя настроение?",
        reply_markup=ReplyKeyboardRemove()
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_mood
    data = await state.get_data()
    assert data.get("waiting_custom_mood") == True


@pytest.mark.asyncio
async def test_choosing_mood_sent_own(storage, storage_key):
    message = AsyncMock()
    message.text = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(waiting_custom_mood=True, mood=message.text)
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Какую активность хочешь сегодня?",
        reply_markup=WalkKeyboard.activity_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_activity


@pytest.mark.asyncio
async def test_choosing_mood_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Введи желаемую длительность прогулки в минутах (только число):",
        reply_markup=WalkKeyboard.duration_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_duration


@pytest.mark.asyncio
async def test_choosing_mood_go_main_menu(storage, storage_key):
    message = AsyncMock()
    message.text = "В главное меню"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_choosing_mood_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in [
        "Веселое", "Грустное",
        "В главное меню", "Назад"
    ] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await choosing_mood_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
