import pytest
import random
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock

from handlers.walk_prep import route_generation_choice_handler
from handlers.keyboards import WalkKeyboard, MainKeyboard
from states.walk_state import StartState, WalkState


@pytest.mark.asyncio
async def test_route_generation_duration_choise(storage, storage_key):
    message = AsyncMock()
    message.text = random.choice(["30 минут", "60 минут", "90 минут"])
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_generation_choice_handler(message, state)
    message.answer.assert_called_with(
        "Какое у тебя сегодня настроение?",
        reply_markup=WalkKeyboard.mood_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_mood
    data = await state.get_data()
    assert data.get("duration") == int(message.text.split()[0])


@pytest.mark.asyncio
async def test_route_generation_choise_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_generation_choice_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных",
        reply_markup=MainKeyboard.start_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == StartState.main_menu


@pytest.mark.asyncio
async def test_route_generation_choise_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Назад", "30 минут", "60 минут", "90 минут"] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.choosing_duration)
    await route_generation_choice_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_duration
