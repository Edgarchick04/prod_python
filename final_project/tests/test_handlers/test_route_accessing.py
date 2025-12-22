import pytest
import random
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.walk_prep import route_accessing_handler
from handlers.keyboards import WalkKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_route_accessing_start(storage, storage_key):
    message = AsyncMock()
    message.text = "Да, начать прогулку"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(duration=random.choice([30, 60, 90]), route={"description": "empty"})
    with patch("handlers.walk_prep.run_walk", AsyncMock()) as mock_run_walk:
        await route_accessing_handler(message, state)
        mock_run_walk.assert_called_with(
            message,
            state
        )
        data = await state.get_data()
        assert data.get("route") == {"description": "empty"}


@pytest.mark.asyncio
async def test_route_accessing_another_route(storage, storage_key):
    message = AsyncMock()
    message.text = "Сгенерировать другой маршрут"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_accessing_handler(message, state)
    message.answer.assert_called_with(
        "Отправь геопозицию, чтоб я мог сгенерировать тебе маршрут прогулки",
        reply_markup=WalkKeyboard.send_geoposition_keboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.waiting_geo


@pytest.mark.asyncio
async def test_route_accessing_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await route_accessing_handler(message, state)
    message.answer.assert_called_with(
        "Сгенерировать тебе маршрут?",
        reply_markup=WalkKeyboard.route_generation_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.route_generation


@pytest.mark.asyncio
async def test_route_accessing_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Назад", "Да, начать прогулку", "Сгенерировать другой маршрут"] else "Any"
    message.location = None
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.route_accessing)
    await route_accessing_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.route_accessing
