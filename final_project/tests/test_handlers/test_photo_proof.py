import pytest
import random
from aiogram.fsm.context import FSMContext
from unittest.mock import AsyncMock, patch

from handlers.walk_process import task_photo_proof_handler
from handlers.keyboards import TaskKeyboard
from states.walk_state import WalkState


@pytest.mark.asyncio
async def test_photo_proof(storage, storage_key, user_id, photo_id, state_update):
    message = AsyncMock()
    message.text = "Сгенерировать маршрут"
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    message.photo = [AsyncMock(), AsyncMock()]
    message.photo[-1].file_id = photo_id
    message.from_user.id = user_id
    await state.set_state(WalkState.in_walk)
    await state.update_data(state_update)
    with patch("handlers.walk_process.set_walks_data", AsyncMock()) as mock_set_walks_data:
        await task_photo_proof_handler(message, state)
        mock_set_walks_data.assert_called_with(
            message.from_user.id
        )
        message.answer.assert_called_with(
            "Круто, задание выполнено!\nХочешь получить новое?",
            reply_markup=TaskKeyboard.task_generation_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == WalkState.in_walk
        data = await state.get_data()
        assert data["task_state"] == "no_task"
        assert data["current_task"] is None
        assert data["tasks_count"] == state_update.get("tasks_count") + 1
        assert data["task_photo"] == message.photo[-1].file_id
