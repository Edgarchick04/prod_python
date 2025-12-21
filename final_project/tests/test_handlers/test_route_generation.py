import pytest
import random
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.commands import route_generation_handler
from handlers.keyboards import WalkKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_route_generation_accept_generation(storage, storage_key):
    message = AsyncMock()
    message.text = "Сгенерировать маршрут"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_generation_handler(message, state)
    message.answer.assert_called_with(
        "Отправь геопозицию, чтоб я мог сгенерировать тебе маршрут прогулки",
        reply_markup=WalkKeyboard.send_geoposition_keboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.waiting_geo


@pytest.mark.asyncio
async def test_route_generation_start_without_route(storage, storage_key):
    message = AsyncMock()
    message.text = "Начать прогулку самостоятельно"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(duration=random.choice([30, 60, 90]))
    with patch("handlers.commands.run_walk", AsyncMock()) as mock_run_walk:
        await route_generation_handler(message, state)
        mock_run_walk.assert_called_with(
            message,
            state
        )
        data = await state.get_data()
        assert data.get("route") == "У тебя нет маршрута"


@pytest.mark.asyncio
async def test_route_generation_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_generation_handler(message, state)
    message.answer.assert_called_with(
        "Сколько времени ты готов потратить на прогулку?",
        reply_markup=WalkKeyboard.duration_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.choosing_duration


@pytest.mark.asyncio
async def test_route_generation_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Назад", "Начать прогулку самостоятельно", "Сгенерировать маршрут"] else "Any"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.route_generation)
    await route_generation_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.route_generation
