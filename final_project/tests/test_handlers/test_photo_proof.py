import pytest
import random
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.walk_process import task_photo_proof_handler
from handlers.keyboards import TaskKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_photo_proof(storage, storage_key, photo_id, state_update):
    message = AsyncMock()
    message.text = "Сгенерировать маршрут"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    message.photo = [AsyncMock(), AsyncMock()]
    message.photo[-1].file_id = photo_id
    await state.set_state(WalkState.in_walk)
    await state.update_data(state_update)
    data = await state.get_data()
    with patch("handlers.walk_process.add_task_photo", AsyncMock()) as mock_add_task_photo:
        await task_photo_proof_handler(message, state)
        mock_add_task_photo.assert_called_with(
            data.get("walk_id"),
            photo_id
        )
        message.answer.assert_called_with(
            "📸 Принято! Задание выполнено 💪\nХочешь ещё?",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk
        data = await state.get_data()
        assert data["task_state"] == "no_task"
        assert data["current_task"] is None
        assert data["tasks_count"] == state_update.get("tasks_count") + 1
