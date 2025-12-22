import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.walk_prep import waiting_geo_handler
from handlers.keyboards import WalkKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_waiting_geo_sent_geo(storage, storage_key, latitude, longtitude, state_for_route, route):
    message = AsyncMock()
    message.text = "Сгенерировать маршрут"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    message.location = AsyncMock()
    message.location.latitude = latitude
    message.location.longitude = longtitude
    await state.update_data(state_for_route)
    points_text = points_text = "\n".join([
        f"{i + 1}. {p['name']} ({p['walk_time_min']} мин): {p['task'] or 'Нет задания'}"
        for i, p in enumerate(route["points"])
    ])
    with patch("handlers.walk_prep.route_generator.generate", AsyncMock(return_value=route)):
        await waiting_geo_handler(message, state)
        message.answer.assert_called_with(
            f"{route['description']}:\n{points_text}\n\nПонравился маршрут?",
            reply_markup=WalkKeyboard.walk_start_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.route_accessing
        data = await state.get_data()
        assert data["route"] == route


@pytest.mark.asyncio
async def test_waiting_geo_back(storage, storage_key):
    message = AsyncMock()
    message.text = "Назад"
    message.location = None
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await waiting_geo_handler(message, state)
    message.answer.assert_called_with(
        "Сгенерировать тебе маршрут?",
        reply_markup=WalkKeyboard.route_generation_keyboard
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.route_generation


@pytest.mark.asyncio
async def test_waiting_geo_unexpected_message(storage, storage_key, message_text):
    message = AsyncMock()
    message.text = message_text if message_text not in ["Назад"] else "Any"
    message.location = None
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.set_state(WalkState.waiting_geo)
    await waiting_geo_handler(message, state)
    message.answer.assert_called_with(
        "Выбери вариант из предложенных"
    )
    tmp_state = await state.get_state()
    assert tmp_state == WalkState.waiting_geo
