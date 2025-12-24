import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from aiogram.fsm.context import FSMContext

from handlers.walk_utils import finish_walk, active_timers
from handlers.keyboards import MainKeyboard
from states.walk_state import StartState, WalkState



@pytest.mark.asyncio
async def test_finish_walk_with_timer_and_walk_id(storage, storage_key, user_id):
    message = AsyncMock()
    message.from_user.id = user_id
    state = FSMContext(
        storage=storage,
        key=storage_key
    )
    timer_task = asyncio.create_task(asyncio.sleep(0))
    active_timers[user_id] = timer_task
    await state.update_data(
        walk_id=123,
        tasks_count=3
    )
    await state.set_state(WalkState.in_walk)
    with patch("handlers.walk_utils.finish_walk_db", AsyncMock(return_value=30)) as mock_finish_db:
        await finish_walk(message, state)
        mock_finish_db.assert_called_with(123)
        await asyncio.sleep(0,1)
        assert timer_task.cancelled() is True
        assert user_id not in active_timers
        message.answer.assert_called_with(
            "Прогулка завершена \n"
            "⏱ Длительность: 30 мин \n"
            "Выполнено заданий: 3",
            reply_markup=MainKeyboard.start_keyboard
        )
        tmp_state = await state.get_state()
        assert tmp_state == StartState.main_menu
