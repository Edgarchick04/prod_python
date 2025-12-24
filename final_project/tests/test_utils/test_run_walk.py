import pytest
from unittest.mock import AsyncMock, patch

from aiogram.fsm.context import FSMContext

from handlers.walk_utils import run_walk, active_timers
from handlers.keyboards import TaskKeyboard
from states.walk_state import WalkState



@pytest.mark.asyncio
async def test_run_walk_with_route(storage, storage_key, user_id, route):
    message = AsyncMock()
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(route=route, duration=30)
    with patch("handlers.walk_utils.start_walk", AsyncMock(return_value=123)) as mock_start_walk:
        await run_walk(message, state)
        mock_start_walk.assert_called_with(
            user_id=user_id,
            route=route,
            duration=30
        )
        data = await state.get_data()
        assert data["walk_state"] == "in_walk"
        assert data["task_state"] == "no_task"
        assert data["walk_id"] == 123
        message.answer.assert_called_with(
            "Твоя прогулка длительностью 30 минут началась.\n"
            "Any description:\n1. Any name (15 мин): Any task\n"
            "2. Any name 2 (15 мин): Any task 2\n"
            "Ты можешь получать задания во время прогулки.",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )      
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk
        assert user_id in active_timers


@pytest.mark.asyncio
async def test_run_walk_without_route(storage, storage_key, user_id):
    message = AsyncMock()
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    route = "У тебя нет маршрута"
    await state.update_data(route=route, duration=30)
    with patch("handlers.walk_utils.start_walk", AsyncMock(return_value=123)) as mock_start_walk:
        await run_walk(message, state)
        expected_route = {"description": "У тебя нет маршрута", "points": []}
        mock_start_walk.assert_called_with(
            user_id=user_id,
            route=expected_route,
            duration=30
        )
        message.answer.assert_called_with(
            "Твоя прогулка длительностью 30 минут началась.\nУ тебя нет маршрута\nПросто иди гулять 😊",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )        
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk


@pytest.mark.asyncio
async def test_run_walk_with_none_route(storage, storage_key, user_id):
    message = AsyncMock()
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    await state.update_data(route=None, duration=30)
    with patch("handlers.walk_utils.start_walk", AsyncMock(return_value=123)) as mock_start_walk:
        await run_walk(message, state)
        expected_route = {"description": "У тебя нет маршрута", "points": []}
        mock_start_walk.assert_called_with(
            user_id=user_id,
            route=expected_route,
            duration=30
        )
